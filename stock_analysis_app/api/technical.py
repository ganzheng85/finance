"""
Technical Analysis Report Generation
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import shutil

# Import HTML converter
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'utils'))
from md_to_html import convert_md_to_html


def generate_technical_report(ticker: str, lang: str = 'en') -> dict:
    """
    Generate technical analysis report for a stock

    Args:
        ticker: Stock ticker symbol
        lang: Language code ('en' or 'zh'), default 'en'

    Returns:
        dict with report path and metadata
    """
    # Path to technical analysis skill
    project_root = Path(__file__).parent.parent.parent
    technical_skill = project_root / '.claude' / 'skills' / 'technical_analysis'
    script_path = technical_skill / 'scripts' / 'analyze_stock.py'

    # Run the analysis script
    try:
        # Build command with language parameter
        cmd = [sys.executable, str(script_path), ticker, '--lang', lang]
        result = subprocess.run(
            cmd,
            cwd=str(technical_skill),
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            error_msg = f"WARNING: Technical analysis failed for {ticker}\n"

            # Check if it's a Yahoo Finance data fetch error
            if 'No data found' in result.stderr or 'No data available' in result.stderr:
                error_msg += f"\nYahoo Finance data fetch failed for ticker '{ticker}'.\n"
                error_msg += "Possible causes:\n"
                error_msg += "  - Invalid ticker symbol\n"
                error_msg += "  - Stock may be delisted or suspended\n"
                error_msg += "  - Network connection issue\n"
                error_msg += "  - Yahoo Finance API temporarily unavailable\n"
            else:
                error_msg += f"\nError details: {result.stderr}\n"

            print(error_msg)
            raise Exception(error_msg)
    except subprocess.SubprocessError as e:
        error_msg = f"WARNING: Failed to run technical analysis script\n"
        error_msg += f"Error: {str(e)}\n"
        print(error_msg)
        raise Exception(error_msg)

    # Look for generated report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    analyses_dir = technical_skill / 'analyses'

    # Find the most recent analysis files
    md_files = list(analyses_dir.glob(f'{ticker}_Technical_Analysis_*.md'))
    chart_files = list(analyses_dir.glob(f'{ticker}_Comprehensive_Chart_*.png'))

    report_data = {
        'ticker': ticker,
        'type': 'technical',
        'timestamp': timestamp
    }

    # Copy report to web app reports directory
    reports_dir = Path(__file__).parent.parent / 'reports'
    reports_dir.mkdir(exist_ok=True)

    if md_files:
        latest_report = max(md_files, key=lambda p: p.stat().st_mtime)
        dest_filename = f'{ticker}_technical_{timestamp}.md'
        dest_path = reports_dir / dest_filename
        shutil.copy2(latest_report, dest_path)

        # Copy or generate HTML
        html_filename = f'{ticker}_technical_{timestamp}.html'
        html_path = reports_dir / html_filename

        # Check if HTML already exists in source directory
        source_html = latest_report.with_suffix('.html')
        if source_html.exists():
            # Copy existing HTML
            shutil.copy2(source_html, html_path)
        else:
            # Generate HTML from markdown
            convert_md_to_html(str(dest_path), str(html_path))

        # Validate report data
        validation_script = technical_skill / 'scripts' / 'validate_technical_report.py'
        validation_result = subprocess.run(
            [sys.executable, str(validation_script), ticker, '--report', str(latest_report)],
            cwd=str(technical_skill),
            capture_output=True,
            text=True
        )

        validation_passed = validation_result.returncode == 0
        validation_output = validation_result.stdout

        report_data['path'] = str(dest_path)
        report_data['filename'] = dest_filename
        report_data['html_path'] = str(html_path)
        report_data['html_filename'] = html_filename
        report_data['validation_passed'] = validation_passed
        report_data['validation_output'] = validation_output

        # Add warning if validation failed
        if not validation_passed:
            report_data['warning'] = 'Report validation found data mismatches. Review validation output.'

    # Copy chart if available
    if chart_files:
        latest_chart = max(chart_files, key=lambda p: p.stat().st_mtime)
        chart_dest_filename = f'{ticker}_technical_chart_{timestamp}.png'
        chart_dest_path = reports_dir / chart_dest_filename
        shutil.copy2(latest_chart, chart_dest_path)

        report_data['chart_path'] = str(chart_dest_path)
        report_data['chart_filename'] = chart_dest_filename

    return report_data
