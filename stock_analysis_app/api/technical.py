"""
Technical Analysis Report Generation
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import shutil

# Import PDF converter
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'utils'))
from md_to_pdf import convert_md_to_pdf


def generate_technical_report(ticker: str) -> dict:
    """
    Generate technical analysis report for a stock

    Args:
        ticker: Stock ticker symbol

    Returns:
        dict with report path and metadata
    """
    # Path to technical analysis skill
    project_root = Path(__file__).parent.parent.parent
    technical_skill = project_root / 'technical_analysis'
    script_path = technical_skill / 'scripts' / 'analyze_stock.py'

    # Run the analysis script
    result = subprocess.run(
        [sys.executable, str(script_path), ticker],
        cwd=str(technical_skill),
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(f"Technical analysis failed: {result.stderr}")

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

        # Generate PDF
        pdf_filename = f'{ticker}_technical_{timestamp}.pdf'
        pdf_path = reports_dir / pdf_filename
        convert_md_to_pdf(str(dest_path), str(pdf_path))

        report_data['path'] = str(dest_path)
        report_data['filename'] = dest_filename
        report_data['pdf_path'] = str(pdf_path)
        report_data['pdf_filename'] = pdf_filename

    # Copy chart if available
    if chart_files:
        latest_chart = max(chart_files, key=lambda p: p.stat().st_mtime)
        chart_dest_filename = f'{ticker}_technical_chart_{timestamp}.png'
        chart_dest_path = reports_dir / chart_dest_filename
        shutil.copy2(latest_chart, chart_dest_path)

        report_data['chart_path'] = str(chart_dest_path)
        report_data['chart_filename'] = chart_dest_filename

    return report_data
