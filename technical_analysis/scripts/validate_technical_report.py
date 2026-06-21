#!/usr/bin/env python3
"""
Validate Technical Analysis Report Data

Compares values in a technical analysis report against freshly calculated
technical indicators to ensure accuracy and prevent hallucination errors.

Usage:
    python validate_technical_report.py AAPL --report analyses/AAPL_Technical_Analysis_20260621_154759.md
    python validate_technical_report.py META --report analyses/META_Technical_Analysis_20260621_120000.md --tolerance 0.05
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import re
from typing import Dict, Any, Tuple

import pandas as pd

# Import technical analysis modules
from fetch_and_analyze import fetch_stock_data, calculate_all_factors, get_recent_data


def extract_report_values(report_path: Path) -> Dict[str, Any]:
    """Extract numeric values from technical analysis report"""

    if not report_path.exists():
        raise FileNotFoundError(f"Report not found: {report_path}")

    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    values = {}

    # Extract current price
    match = re.search(r'\*\*Current Price:\*\* \$([\d.]+)', content)
    if match:
        values['current_price'] = float(match.group(1))

    # Extract RSI
    match = re.search(r'\| RSI\(14\) \| ([\d.]+)', content)
    if match:
        values['rsi_14'] = float(match.group(1))

    # Extract MACD histogram
    match = re.search(r'\| MACD Histogram \| ([+-]?[\d.]+)', content)
    if match:
        values['macd_hist'] = float(match.group(1))

    # Extract Stochastic %K
    match = re.search(r'\| Stochastic %K \| ([\d.]+)', content)
    if match:
        values['stoch_k'] = float(match.group(1))

    # Extract ADX
    match = re.search(r'\| ADX\(14\) \| ([\d.]+)', content)
    if match:
        values['adx_14'] = float(match.group(1))

    # Extract Bollinger %B
    match = re.search(r'\| Bollinger %B \| ([\d.]+)', content)
    if match:
        values['bb_percent'] = float(match.group(1))

    # Extract volatility (annualized)
    match = re.search(r'- Annualized Volatility: ([\d.]+)%', content)
    if match:
        values['volatility_annual'] = float(match.group(1))

    # Extract volume from recent price action table (last row)
    matches = re.findall(r'\| [\d-]+ \| \$([\d.]+) \| ([\d,]+) \|', content)
    if matches:
        last_volume = matches[-1][1].replace(',', '')
        values['last_volume'] = float(last_volume)
        values['last_close'] = float(matches[-1][0])

    return values


def calculate_fresh_values(ticker: str, lookback_days: int = 365) -> Dict[str, Any]:
    """Calculate fresh technical indicator values"""

    # Fetch data
    df = fetch_stock_data(ticker, lookback_days=lookback_days)

    # Calculate all factors
    df_with_factors = calculate_all_factors(df)

    # Get most recent values
    latest = df_with_factors.iloc[-1]

    # Try multiple column name variations for each indicator
    values = {
        'current_price': latest['adjusted_close'],
        'last_volume': latest['volume'],
        'last_close': latest['adjusted_close'],
    }

    # RSI - try multiple column names
    for col in ['rsi_14', 'rsi', 'RSI_14', 'RSI']:
        if col in df_with_factors.columns and pd.notna(latest.get(col)):
            values['rsi_14'] = latest[col]
            break

    # MACD Histogram - try multiple column names
    for col in ['macd_hist_12_26_9', 'macd_hist', 'MACD_Hist', 'macd_histogram']:
        if col in df_with_factors.columns and pd.notna(latest.get(col)):
            values['macd_hist'] = latest[col]
            break

    # Stochastic %K - try multiple column names
    for col in ['stoch_k_14', 'stoch_k_14_3_3', 'stoch_k', 'STOCHk_14_3_3', 'stochastic_k']:
        if col in df_with_factors.columns and pd.notna(latest.get(col)):
            values['stoch_k'] = latest[col]
            break

    # ADX - try multiple column names
    for col in ['adx_14', 'ADX_14', 'adx', 'ADX']:
        if col in df_with_factors.columns and pd.notna(latest.get(col)):
            values['adx_14'] = latest[col]
            break

    # Bollinger %B - try multiple column names
    for col in ['bb_percent_b', 'bb_pct_b_20_2', 'bb_percent', 'BBL_20_2', 'bollinger_pct_b']:
        if col in df_with_factors.columns and pd.notna(latest.get(col)):
            values['bb_percent'] = latest[col]
            break

    # Calculate annualized volatility from daily returns
    # Use last 30 days for volatility calculation
    if len(df_with_factors) >= 30:
        recent_30 = df_with_factors.tail(30)
        if 'adjusted_close' in recent_30.columns:
            returns = recent_30['adjusted_close'].pct_change().dropna()
            if len(returns) > 0:
                daily_vol = returns.std()
                annualized_vol = daily_vol * (252 ** 0.5) * 100  # Annualized as percentage
                values['volatility_annual'] = annualized_vol

    return values


def validate_values(report_values: Dict[str, Any],
                   actual_values: Dict[str, Any],
                   tolerance: float = 0.02) -> Tuple[list, list, list]:
    """
    Compare report values against actual values

    Parameters
    ----------
    report_values : dict
        Values extracted from report
    actual_values : dict
        Freshly calculated values
    tolerance : float
        Acceptable percentage difference (default: 2%)

    Returns
    -------
    tuple of (matches, mismatches, missing)
    """

    matches = []
    mismatches = []
    missing = []

    # Define metric names for display
    metric_names = {
        'current_price': 'Current Price',
        'rsi_14': 'RSI(14)',
        'macd_hist': 'MACD Histogram',
        'stoch_k': 'Stochastic %K',
        'adx_14': 'ADX(14)',
        'bb_percent': 'Bollinger %B',
        'volatility_annual': 'Annualized Volatility %',
        'last_volume': 'Last Volume',
        'last_close': 'Last Close',
    }

    for key, name in metric_names.items():
        report_val = report_values.get(key)
        actual_val = actual_values.get(key)

        if report_val is None and actual_val is None:
            missing.append({
                'metric': name,
                'status': 'both_missing'
            })
        elif report_val is None:
            missing.append({
                'metric': name,
                'report': 'N/A',
                'actual': f'{actual_val:.2f}' if actual_val else 'N/A',
                'status': 'report_missing'
            })
        elif actual_val is None:
            missing.append({
                'metric': name,
                'report': f'{report_val:.2f}',
                'actual': 'N/A',
                'status': 'actual_missing'
            })
        else:
            # Check if values match within tolerance
            if actual_val == 0:
                # Avoid division by zero
                diff = abs(report_val - actual_val)
                match = diff < 0.01
            else:
                pct_diff = abs(report_val - actual_val) / abs(actual_val)
                match = pct_diff <= tolerance

            if match:
                matches.append({
                    'metric': name,
                    'report': report_val,
                    'actual': actual_val,
                    'diff_pct': abs(report_val - actual_val) / abs(actual_val) * 100 if actual_val != 0 else 0
                })
            else:
                mismatches.append({
                    'metric': name,
                    'report': report_val,
                    'actual': actual_val,
                    'diff_pct': abs(report_val - actual_val) / abs(actual_val) * 100 if actual_val != 0 else 0
                })

    return matches, mismatches, missing


def print_validation_report(ticker: str, matches: list, mismatches: list, missing: list, tolerance: float):
    """Print formatted validation report"""

    print(f"\n{'='*80}")
    print(f"TECHNICAL ANALYSIS DATA VALIDATION: {ticker}")
    print(f"{'='*80}")
    print(f"\nValidation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Tolerance: ±{tolerance*100:.1f}%")
    print(f"\n{'-'*80}")
    print(f"{'Metric':<30} {'Report':<15} {'Actual':<15} {'Status':<20}")
    print(f"{'-'*80}")

    # Print matches
    for item in matches:
        print(f"{item['metric']:<30} {item['report']:<15.2f} {item['actual']:<15.2f} [OK] MATCH")

    # Print mismatches
    for item in mismatches:
        diff_pct = item['diff_pct']
        print(f"{item['metric']:<30} {item['report']:<15.2f} {item['actual']:<15.2f} [X] MISMATCH ({diff_pct:.2f}%)")

    # Print missing
    for item in missing:
        if item['status'] != 'both_missing':
            report_str = str(item.get('report', 'N/A'))
            actual_str = str(item.get('actual', 'N/A'))
            print(f"{item['metric']:<30} {report_str:<15} {actual_str:<15} [!] MISSING")

    print(f"{'-'*80}")
    print(f"\nSummary:")
    print(f"  [OK] Matches:    {len(matches)}")
    print(f"  [X]  Mismatches: {len(mismatches)}")
    print(f"  [!]  Missing:    {len([m for m in missing if m['status'] != 'both_missing'])}")
    print(f"  Total Checks: {len(matches) + len(mismatches) + len(missing)}")

    if mismatches:
        print(f"\n[X] VALIDATION FAILED - {len(mismatches)} value(s) do not match!")
        print(f"\nMismatched values:")
        for item in mismatches:
            print(f"  - {item['metric']}: Report={item['report']:.2f}, Actual={item['actual']:.2f} (diff={item['diff_pct']:.2f}%)")
    elif len([m for m in missing if m['status'] != 'both_missing']) > 0:
        print(f"\n[!] NOTE: {len([m for m in missing if m['status'] != 'both_missing'])} value(s) missing from report or actual data.")
    else:
        print(f"\n[OK] All values validated successfully!")

    print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Validate technical analysis report data against fresh calculations'
    )
    parser.add_argument(
        'ticker',
        type=str,
        help='Stock ticker symbol'
    )
    parser.add_argument(
        '--report',
        type=str,
        required=True,
        help='Path to technical analysis report file'
    )
    parser.add_argument(
        '--tolerance',
        type=float,
        default=0.02,
        help='Acceptable percentage difference (default: 0.02 = 2%%)'
    )
    parser.add_argument(
        '--lookback',
        type=int,
        default=365,
        help='Days of historical data for calculations (default: 365)'
    )

    args = parser.parse_args()
    ticker = args.ticker.upper()
    report_path = Path(args.report)

    try:
        # Extract values from report
        print(f"Extracting values from report: {report_path.name}...")
        report_values = extract_report_values(report_path)
        print(f"[OK] Extracted {len(report_values)} values from report")

        # Calculate fresh values
        print(f"\nCalculating fresh technical indicators for {ticker}...")
        actual_values = calculate_fresh_values(ticker, lookback_days=args.lookback)
        print(f"[OK] Calculated {len(actual_values)} fresh values")

        # Validate
        matches, mismatches, missing = validate_values(
            report_values,
            actual_values,
            tolerance=args.tolerance
        )

        # Print report
        print_validation_report(ticker, matches, mismatches, missing, args.tolerance)

        # Exit with error code if validation failed
        if mismatches:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        print(f"\n[ERROR] Validation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
