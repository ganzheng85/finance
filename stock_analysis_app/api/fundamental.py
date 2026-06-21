"""
Fundamental Analysis Report Generation

IMPORTANT: This API generates report STRUCTURE only.
For COMPREHENSIVE analysis, use Claude Code's fundamental-analysis skill directly:
  - Type in Claude Code: "Generate fundamental analysis for {TICKER}"
  - This will invoke the skill with Agent tool for full research

Web app usage: Creates preliminary report structure for manual completion.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import shutil
import json

# Import HTML converter
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'utils'))
from md_to_html import convert_md_to_html


def generate_fundamental_report(ticker: str) -> dict:
    """
    Generate fundamental analysis report structure

    NOTE: This creates a preliminary structure with price data.
    For comprehensive analysis with moat scores, scenarios, and recommendations,
    use Claude Code's fundamental-analysis skill directly.

    Args:
        ticker: Stock ticker symbol

    Returns:
        dict with report path and metadata
    """
    # Path to fundamental analysis skill
    project_root = Path(__file__).parent.parent.parent
    fundamental_skill = project_root / 'fundamental_analysis_skill'

    # Use comprehensive report generator (creates structure)
    script_path = fundamental_skill / 'scripts' / 'generate_comprehensive_report.py'

    # Set output directory to fundamental skill's analyses folder
    analyses_dir = fundamental_skill / 'analyses' / ticker.upper()

    # Run the report structure generator
    result = subprocess.run(
        [sys.executable, str(script_path), ticker.upper(), '--output-dir', str(analyses_dir)],
        cwd=str(fundamental_skill),
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(f"Report generation failed: {result.stderr}")

    # Look for generated report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    analyses_dir = fundamental_skill / 'analyses' / ticker

    # Find the most recent analysis file
    if analyses_dir.exists():
        md_files = list(analyses_dir.glob(f'{ticker}-*.md'))
        if md_files:
            # Get the most recent file
            latest_report = max(md_files, key=lambda p: p.stat().st_mtime)

            # Copy to web app reports directory
            reports_dir = Path(__file__).parent.parent / 'reports'
            reports_dir.mkdir(exist_ok=True)

            dest_filename = f'{ticker}_fundamental_{timestamp}.md'
            dest_path = reports_dir / dest_filename
            shutil.copy2(latest_report, dest_path)

            # Validate report data before generating PDF
            validation_script = fundamental_skill / 'scripts' / 'validate_report_data.py'
            validation_result = subprocess.run(
                [sys.executable, str(validation_script), ticker, '--report', str(latest_report)],
                cwd=str(fundamental_skill),
                capture_output=True,
                text=True
            )

            validation_passed = validation_result.returncode == 0
            validation_output = validation_result.stdout

            # Generate HTML
            html_filename = f'{ticker}_fundamental_{timestamp}.html'
            html_path = reports_dir / html_filename
            convert_md_to_html(str(dest_path), str(html_path))

            result = {
                'ticker': ticker,
                'type': 'fundamental',
                'path': str(dest_path),
                'filename': dest_filename,
                'html_path': str(html_path),
                'html_filename': html_filename,
                'timestamp': timestamp,
                'validation_passed': validation_passed,
                'validation_output': validation_output,
                'note': f'⚠️ PRELIMINARY report structure only. For COMPREHENSIVE analysis with moat scores, scenarios, and recommendations, tell Claude Code: "Generate fundamental analysis for {ticker}"',
                'instruction': f'For complete analysis, type in Claude Code: "Generate fundamental analysis for {ticker}"'
            }

            # If validation failed, add warning
            if not validation_passed:
                result['warning'] = 'Report validation found data mismatches. Review validation output.'

            return result

    # If no existing report, return basic info
    # This means the script ran but didn't generate a full report
    # We can still provide the price data
    return {
        'ticker': ticker,
        'type': 'fundamental',
        'path': None,
        'filename': None,
        'timestamp': timestamp,
        'note': 'Price data fetched but full report not generated'
    }
