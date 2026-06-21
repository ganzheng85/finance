#!/usr/bin/env python3
"""
Report Data Validation Script

Validates that financial data used in fundamental analysis reports
matches actual data from Yahoo Finance and other sources.
Helps catch hallucination or data errors.

Usage:
    python validate_report_data.py MSFT
    python validate_report_data.py MSFT --report ../analyses/MSFT/MSFT-2026-06-19.md
    python validate_report_data.py MSFT --report ../analyses/MSFT/MSFT-2026-06-19.md --tolerance 5
"""

import sys
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Tuple

try:
    import yfinance as yf
except ImportError:
    print("Error: yfinance not installed. Install with: pip install yfinance")
    sys.exit(1)


def fetch_actual_data(ticker: str) -> Dict[str, Any]:
    """Fetch actual data from Yahoo Finance"""
    print(f"\nFetching actual data for {ticker} from Yahoo Finance...")

    stock = yf.Ticker(ticker)
    info = stock.info
    history = stock.history(period="1y")

    if history.empty:
        return {"error": f"No data found for ticker {ticker}"}

    # Current price
    current_price = history['Close'].iloc[-1]

    # 52-week range
    week_52_high = history['High'].tail(252).max()
    week_52_low = history['Low'].tail(252).min()

    # 6-month metrics
    six_months_ago_price = history['Close'].tail(126).iloc[0] if len(history) >= 126 else history['Close'].iloc[0]
    six_month_return = ((current_price - six_months_ago_price) / six_months_ago_price) * 100

    # Position in range
    range_position = ((current_price - week_52_low) / (week_52_high - week_52_low)) * 100
    pct_from_high = ((current_price - week_52_high) / week_52_high) * 100
    pct_from_low = ((current_price - week_52_low) / week_52_low) * 100

    # Volume
    avg_volume = history['Volume'].tail(20).mean()
    current_volume = history['Volume'].iloc[-1]

    data = {
        "ticker": ticker.upper(),
        "fetch_date": datetime.now().strftime("%Y-%m-%d"),
        "company_name": info.get('longName', ticker),
        "sector": info.get('sector', 'N/A'),
        "industry": info.get('industry', 'N/A'),

        # Price metrics
        "current_price": round(current_price, 2),
        "week_52_high": round(week_52_high, 2),
        "week_52_low": round(week_52_low, 2),
        "range_position_pct": round(range_position, 1),
        "pct_from_high": round(pct_from_high, 1),
        "pct_from_low": round(pct_from_low, 1),
        "six_month_return": round(six_month_return, 1),

        # Valuation metrics
        "pe_trailing": round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else None,
        "pe_forward": round(info.get('forwardPE', 0), 2) if info.get('forwardPE') else None,
        "ps_ratio": round(info.get('priceToSalesTrailing12Months', 0), 2) if info.get('priceToSalesTrailing12Months') else None,
        "pb_ratio": round(info.get('priceToBook', 0), 2) if info.get('priceToBook') else None,

        # Volume
        "avg_volume_20d": int(avg_volume),
        "current_volume": int(current_volume),

        # Other
        "market_cap": info.get('marketCap', None),
        "beta": info.get('beta', None),
    }

    return data


def extract_report_values(report_path: Path) -> Dict[str, Any]:
    """Extract key values from the markdown report"""
    print(f"\nExtracting values from report: {report_path.name}...")

    if not report_path.exists():
        return {"error": f"Report file not found: {report_path}"}

    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    values = {}

    # Extract current price from header
    price_match = re.search(r'\*\*Current Price\*\*:\s*\$?([\d,]+\.?\d*)', content)
    if price_match:
        values['current_price'] = float(price_match.group(1).replace(',', ''))

    # Extract 52-week range
    high_match = re.search(r'\*\*52-Week Range\*\*:\s*\$?([\d,]+\.?\d*)\s*-\s*\$?([\d,]+\.?\d*)', content)
    if high_match:
        values['week_52_low'] = float(high_match.group(1).replace(',', ''))
        values['week_52_high'] = float(high_match.group(2).replace(',', ''))

    # Extract position in range
    pos_match = re.search(r'\*\*Position in Range\*\*:\s*([\d.]+)%', content)
    if pos_match:
        values['range_position_pct'] = float(pos_match.group(1))

    # Extract percent from high
    high_pct_match = re.search(r'\(([-\d.]+)%\s*below high', content, re.IGNORECASE)
    if high_pct_match:
        values['pct_from_high'] = -float(high_pct_match.group(1))
    elif re.search(r'\(([-\d.]+)%\s*from high', content):
        high_pct_match = re.search(r'\(([-\d.]+)%\s*from high', content)
        values['pct_from_high'] = float(high_pct_match.group(1))

    # Extract percent from low
    low_pct_match = re.search(r'([\d.]+)%\s*above low', content, re.IGNORECASE)
    if low_pct_match:
        values['pct_from_low'] = float(low_pct_match.group(1))

    # Extract 6-month return
    six_mo_match = re.search(r'\*\*6-month change:\s*([-\d.]+)%', content)
    if six_mo_match:
        values['six_month_return'] = float(six_mo_match.group(1))

    # Extract P/E ratios from table
    pe_trailing_match = re.search(r'P/E \(Trailing\)\s*\|\s*([\d.]+)', content)
    if pe_trailing_match:
        values['pe_trailing'] = float(pe_trailing_match.group(1))

    pe_forward_match = re.search(r'P/E \(Forward\)\s*\|\s*([\d.]+)', content)
    if pe_forward_match:
        values['pe_forward'] = float(pe_forward_match.group(1))

    ps_match = re.search(r'P/S\s*\|\s*([\d.]+)', content)
    if ps_match:
        values['ps_ratio'] = float(ps_match.group(1))

    pb_match = re.search(r'P/B\s*\|\s*([\d.]+)', content)
    if pb_match:
        values['pb_ratio'] = float(pb_match.group(1))

    # Extract volume
    vol_match = re.search(r'\*\*Trading Volume\*\*:\s*([\d.]+)M\s*\(([\d.]+)x', content)
    if vol_match:
        values['current_volume_m'] = float(vol_match.group(1))
        values['volume_ratio'] = float(vol_match.group(2))

    return values


def compare_values(actual: Dict[str, Any], report: Dict[str, Any], tolerance_pct: float = 2.0) -> List[Tuple[str, Any, Any, bool, str]]:
    """
    Compare actual vs report values

    Returns list of tuples: (field_name, actual_value, report_value, is_match, status)
    """
    comparisons = []

    # Fields to compare with their display names
    fields = {
        'current_price': 'Current Price',
        'week_52_high': '52-Week High',
        'week_52_low': '52-Week Low',
        'range_position_pct': 'Position in Range %',
        'pct_from_high': '% From High',
        'pct_from_low': '% From Low',
        'six_month_return': '6-Month Return %',
        'pe_trailing': 'P/E (Trailing)',
        'pe_forward': 'P/E (Forward)',
        'ps_ratio': 'P/S Ratio',
        'pb_ratio': 'P/B Ratio',
    }

    for field, display_name in fields.items():
        actual_val = actual.get(field)
        report_val = report.get(field)

        if actual_val is None or report_val is None:
            status = '[!] MISSING'
            is_match = False
            comparisons.append((display_name, actual_val, report_val, is_match, status))
            continue

        # Calculate percentage difference
        if actual_val != 0:
            pct_diff = abs((report_val - actual_val) / actual_val) * 100
        else:
            pct_diff = 0 if report_val == 0 else 100

        is_match = pct_diff <= tolerance_pct

        if is_match:
            status = '[OK] MATCH'
        else:
            status = f'[X] MISMATCH ({pct_diff:.1f}% diff)'

        comparisons.append((display_name, actual_val, report_val, is_match, status))

    return comparisons


def print_validation_report(ticker: str, actual: Dict[str, Any], report: Dict[str, Any],
                           comparisons: List[Tuple], tolerance_pct: float):
    """Print formatted validation report"""

    print("\n" + "="*80)
    print(f"DATA VALIDATION REPORT: {ticker}")
    print("="*80)

    print(f"\nFetch Date: {actual.get('fetch_date', 'N/A')}")
    print(f"Company: {actual.get('company_name', 'N/A')}")
    print(f"Tolerance: ±{tolerance_pct}%")

    print("\n" + "-"*80)
    print(f"{'Metric':<30} {'Actual':<15} {'Report':<15} {'Status':<20}")
    print("-"*80)

    matches = 0
    mismatches = 0
    missing = 0

    for display_name, actual_val, report_val, is_match, status in comparisons:
        # Format values
        if actual_val is None:
            actual_str = "N/A"
        elif isinstance(actual_val, float):
            actual_str = f"{actual_val:.2f}"
        else:
            actual_str = str(actual_val)

        if report_val is None:
            report_str = "N/A"
        elif isinstance(report_val, float):
            report_str = f"{report_val:.2f}"
        else:
            report_str = str(report_val)

        print(f"{display_name:<30} {actual_str:<15} {report_str:<15} {status:<20}")

        if 'MATCH' in status:
            matches += 1
        elif 'MISMATCH' in status:
            mismatches += 1
        elif 'MISSING' in status:
            missing += 1

    print("-"*80)
    print(f"\nSummary:")
    print(f"  [OK] Matches:    {matches}")
    print(f"  [X]  Mismatches: {mismatches}")
    print(f"  [!]  Missing:    {missing}")
    print(f"  Total Checks: {len(comparisons)}")

    if mismatches > 0:
        print(f"\n[!] WARNING: {mismatches} value(s) do not match actual data!")
        print("    This could indicate hallucination or outdated data in the report.")
    elif missing > 0:
        print(f"\n[!] NOTE: {missing} value(s) missing from report or actual data.")
    else:
        print("\n[OK] All values validated successfully!")

    print("="*80)

    return {
        'matches': matches,
        'mismatches': mismatches,
        'missing': missing,
        'total': len(comparisons)
    }


def main():
    parser = argparse.ArgumentParser(
        description='Validate fundamental analysis report data against actual sources'
    )
    parser.add_argument(
        'ticker',
        type=str,
        help='Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)'
    )
    parser.add_argument(
        '--report',
        type=str,
        help='Path to markdown report file to validate'
    )
    parser.add_argument(
        '--tolerance',
        type=float,
        default=2.0,
        help='Tolerance percentage for matching values (default: 2.0%%)'
    )

    args = parser.parse_args()

    # Fetch actual data
    actual_data = fetch_actual_data(args.ticker)

    if 'error' in actual_data:
        print(f"Error: {actual_data['error']}")
        sys.exit(1)

    print(f"[OK] Successfully fetched data for {args.ticker}")
    print(f"  Current Price: ${actual_data['current_price']}")
    print(f"  52-Week Range: ${actual_data['week_52_low']} - ${actual_data['week_52_high']}")
    print(f"  P/E (Trailing): {actual_data['pe_trailing']}")

    # If report specified, validate it
    if args.report:
        report_path = Path(args.report)
        report_values = extract_report_values(report_path)

        if 'error' in report_values:
            print(f"Error: {report_values['error']}")
            sys.exit(1)

        print(f"[OK] Extracted {len(report_values)} values from report")

        # Compare values
        comparisons = compare_values(actual_data, report_values, args.tolerance)

        # Print validation report
        summary = print_validation_report(
            args.ticker,
            actual_data,
            report_values,
            comparisons,
            args.tolerance
        )

        # Exit with error code if mismatches found
        if summary['mismatches'] > 0:
            sys.exit(1)
    else:
        print("\nNo report specified. Use --report flag to validate a report.")
        print(f"\nExample:")
        print(f"  python validate_report_data.py {args.ticker} --report analyses/{args.ticker}/{args.ticker}-YYYY-MM-DD.md")


if __name__ == "__main__":
    main()
