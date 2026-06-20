"""
Fundamental Analysis Report Generation
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import shutil

# Import PDF converter
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'utils'))
from md_to_pdf import convert_md_to_pdf


def generate_fundamental_report(ticker: str) -> dict:
    """
    Generate fundamental analysis report for a stock

    Args:
        ticker: Stock ticker symbol

    Returns:
        dict with report path and metadata
    """
    # Path to fundamental analysis skill
    project_root = Path(__file__).parent.parent.parent
    fundamental_skill = project_root / 'fundamental_analysis_skill'
    script_path = fundamental_skill / 'scripts' / 'price_analysis.py'

    # Run the analysis script
    result = subprocess.run(
        [sys.executable, str(script_path), ticker, '--json'],
        cwd=str(fundamental_skill),
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(f"Fundamental analysis failed: {result.stderr}")

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

            # Generate PDF
            pdf_filename = f'{ticker}_fundamental_{timestamp}.pdf'
            pdf_path = reports_dir / pdf_filename
            convert_md_to_pdf(str(dest_path), str(pdf_path))

            return {
                'ticker': ticker,
                'type': 'fundamental',
                'path': str(dest_path),
                'filename': dest_filename,
                'pdf_path': str(pdf_path),
                'pdf_filename': pdf_filename,
                'timestamp': timestamp
            }

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
