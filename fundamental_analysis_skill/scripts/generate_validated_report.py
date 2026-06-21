#!/usr/bin/env python3
"""
Generate Validated Fundamental Analysis Report

Wrapper script that generates a fundamental analysis report and automatically validates it.
Ensures all reports pass data validation before being considered complete.

Usage:
    python generate_validated_report.py MSFT
    python generate_validated_report.py AAPL --tolerance 5
"""

import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(
        description='Generate and validate fundamental analysis report'
    )
    parser.add_argument(
        'ticker',
        type=str,
        help='Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)'
    )
    parser.add_argument(
        '--tolerance',
        type=float,
        default=2.0,
        help='Validation tolerance percentage (default: 2.0%%)'
    )

    args = parser.parse_args()
    ticker = args.ticker.upper()

    print("="*80)
    print(f"FUNDAMENTAL ANALYSIS REPORT GENERATION: {ticker}")
    print("="*80)

    # Step 1: Run price analysis
    print(f"\n[1/3] Fetching price data for {ticker}...")
    price_script = Path(__file__).parent / 'price_analysis.py'

    result = subprocess.run(
        [sys.executable, str(price_script), ticker],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"[ERROR] Price analysis failed: {result.stderr}")
        sys.exit(1)

    print(result.stdout)
    print("[OK] Price data fetched successfully")

    # Step 2: User creates full report
    print(f"\n[2/3] Report Creation Step")
    print("-"*80)
    print("Next steps:")
    print(f"  1. Review price analysis output above")
    print(f"  2. Create full fundamental analysis report:")
    print(f"     - Use template: references/analysis-template.md")
    print(f"     - Follow framework: references/analysis-framework.md")
    print(f"     - Reference sample: analyses/MSFT/MSFT-2026-06-19.md")
    print(f"  3. Save as: analyses/{ticker}/{ticker}-{datetime.now().strftime('%Y-%m-%d')}.md")
    print(f"  4. Convert to PDF: python ../utils/md_to_pdf.py <report.md>")
    print()

    # Check if report exists
    report_dir = Path(__file__).parent.parent / 'analyses' / ticker
    if not report_dir.exists():
        print(f"[INFO] Creating directory: {report_dir}")
        report_dir.mkdir(parents=True, exist_ok=True)

    # Look for reports to validate
    md_files = list(report_dir.glob(f'{ticker}-*.md'))

    if not md_files:
        print(f"\n[!] No reports found in {report_dir}")
        print(f"    Create report and re-run this script to validate it")
        return

    # Get most recent report
    latest_report = max(md_files, key=lambda p: p.stat().st_mtime)

    print(f"\n[3/3] Validating report: {latest_report.name}")
    print("-"*80)

    # Step 3: Validate report
    validation_script = Path(__file__).parent / 'validate_report_data.py'

    result = subprocess.run(
        [sys.executable, str(validation_script), ticker,
         '--report', str(latest_report),
         '--tolerance', str(args.tolerance)],
        capture_output=False,  # Show output directly
        text=True
    )

    print()
    if result.returncode == 0:
        print("[OK] Report validation PASSED - Report is ready!")
        print(f"\nFiles:")
        print(f"  Report: {latest_report}")
        pdf_path = latest_report.with_suffix('.pdf')
        if pdf_path.exists():
            print(f"  PDF:    {pdf_path}")
    else:
        print("[!] Report validation FAILED - Please fix mismatches")
        print(f"\nAction required:")
        print(f"  1. Review validation errors above")
        print(f"  2. Correct values in: {latest_report}")
        print(f"  3. Re-run: python {Path(__file__).name} {ticker}")
        sys.exit(1)

    print("="*80)


if __name__ == "__main__":
    main()
