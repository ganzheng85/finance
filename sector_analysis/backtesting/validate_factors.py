"""
Factor Validation System

Tests whether RS20, RS60, momentum, and return_20d are still predictive.

Key metrics:
1. Information Coefficient (IC): Correlation between factor value and forward returns
2. IC Stability: Is the IC consistent over time?
3. Hit Rate: How often does the highest-ranked sector outperform?
4. Factor Decay: How long does the predictive power last?

Usage:
    python validate_factors.py --start 2023-01-01 --end 2024-12-31
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import sys
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from calculate_sector_metrics import (
    calculate_relative_strength,
    calculate_momentum,
    rank_sectors
)

SECTOR_ETFS = {
    'XLK': 'Technology',
    'XLV': 'Healthcare',
    'XLF': 'Financials',
    'XLY': 'Consumer Discretionary',
    'XLI': 'Industrials',
    'XLP': 'Consumer Staples',
    'XLE': 'Energy',
    'XLU': 'Utilities',
    'XLB': 'Materials',
    'XLRE': 'Real Estate',
    'XLC': 'Communication Services',
    'MAGS': 'Magnificent 7',
    'SMH': 'Semiconductors',
    'IGV': 'Software'
}


def calculate_information_coefficient(factor_values, forward_returns):
    """
    Calculate Information Coefficient (IC)

    IC = correlation between factor values and forward returns

    IC > 0.05: Factor has predictive power
    IC < 0: Factor is negatively predictive (use inverse)
    |IC| < 0.05: Factor has no predictive power
    """
    # Remove NaN values
    valid_mask = ~(pd.isna(factor_values) | pd.isna(forward_returns))
    clean_factors = factor_values[valid_mask]
    clean_returns = forward_returns[valid_mask]

    if len(clean_factors) < 3:
        return np.nan, np.nan

    # Rank correlation (Spearman-like) - manual implementation
    # Convert to ranks
    factor_ranks = pd.Series(clean_factors).rank()
    return_ranks = pd.Series(clean_returns).rank()

    # Pearson correlation on ranks = Spearman correlation
    n = len(factor_ranks)

    mean_f = factor_ranks.mean()
    mean_r = return_ranks.mean()

    cov = ((factor_ranks - mean_f) * (return_ranks - mean_r)).sum()
    std_f = np.sqrt(((factor_ranks - mean_f) ** 2).sum())
    std_r = np.sqrt(((return_ranks - mean_r) ** 2).sum())

    if std_f == 0 or std_r == 0:
        return 0.0, 1.0

    ic = cov / (std_f * std_r)

    # Simple p-value approximation (for large N)
    if n > 3:
        # t-statistic approximation
        t = ic * np.sqrt((n - 2) / (1 - ic**2 + 1e-10))
        # Two-tailed p-value (approximation using normal distribution)
        from math import erf
        p_value = 2 * (1 - 0.5 * (1 + erf(abs(t) / np.sqrt(2))))
    else:
        p_value = 1.0

    return ic, p_value


def validate_factors(start_date, end_date):
    """
    Validate all factors over a time period
    """
    print("="*80)
    print("FACTOR VALIDATION SYSTEM")
    print("="*80)
    print(f"Period: {start_date.date()} to {end_date.date()}")
    print()

    # Fetch data
    fetch_start = start_date - timedelta(days=400)
    print("Fetching data...")

    all_tickers = list(SECTOR_ETFS.keys()) + ['SPY']
    sector_data = {}

    for ticker in all_tickers:
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=fetch_start, end=end_date + timedelta(days=30))
            if not data.empty:
                sector_data[ticker] = data['Close']
        except:
            pass

    df_prices = pd.DataFrame(sector_data)
    df_prices.index = df_prices.index.tz_localize(None)

    # Filter out sectors with insufficient data
    backtest_range = df_prices[df_prices.index >= start_date]
    min_required_days = int(len(backtest_range) * 0.8)

    valid_sectors = []
    for ticker in SECTOR_ETFS.keys():
        if ticker in df_prices.columns:
            valid_days = backtest_range[ticker].notna().sum()
            if valid_days >= min_required_days:
                valid_sectors.append(ticker)

    df_prices = df_prices[valid_sectors + ['SPY']].dropna(subset=['SPY'])

    print(f"[OK] Using {len(valid_sectors)} sectors")

    # Create sector dataframe
    sector_df = pd.DataFrame()
    for ticker in valid_sectors:
        sector_prices = df_prices[ticker].dropna()
        temp_df = pd.DataFrame({
            'date': sector_prices.index,
            'ticker': ticker,
            'sector_name': SECTOR_ETFS[ticker],
            'adjusted_close': sector_prices.values
        })
        sector_df = pd.concat([sector_df, temp_df], ignore_index=True)

    spy_df = pd.DataFrame({
        'date': df_prices.index,
        'ticker': 'SPY',
        'sector_name': 'S&P 500',
        'adjusted_close': df_prices['SPY'].values
    })
    sector_df = pd.concat([sector_df, spy_df], ignore_index=True)

    # Calculate metrics for all dates
    print("Calculating metrics...")
    import io
    import contextlib

    with contextlib.redirect_stdout(io.StringIO()):
        sector_df = calculate_relative_strength(sector_df)
        sector_df = calculate_momentum(sector_df)

    # Get weekly dates
    all_dates = df_prices.index[df_prices.index >= start_date]
    weekly_dates = []
    for date in all_dates:
        week_num = date.isocalendar()[1]
        next_day = date + timedelta(days=1)
        if next_day not in all_dates or next_day.isocalendar()[1] != week_num:
            weekly_dates.append(date)

    print(f"[OK] {len(weekly_dates)} weekly periods")

    # For each week, calculate factor values and forward returns
    factors = ['rs_20d', 'rs_60d', 'momentum_score', 'return_20d']
    forward_periods = [5, 10, 20]  # 1 week, 2 weeks, 1 month

    factor_data = {
        factor: {f'{period}d_fwd': [] for period in forward_periods}
        for factor in factors
    }

    print("\nCalculating forward returns...")

    for i, current_date in enumerate(weekly_dates[:-4]):  # Need future data
        # Get current factor values
        sector_only = sector_df[
            (sector_df['ticker'] != 'SPY') &
            (sector_df['date'] == current_date)
        ].copy()

        for factor in factors:
            factor_values = sector_only[factor].values

            # Calculate forward returns for each period
            for period in forward_periods:
                future_date = current_date + timedelta(days=period)

                # Get closest future date
                future_dates = df_prices.index[df_prices.index >= future_date]
                if len(future_dates) == 0:
                    continue

                actual_future_date = future_dates[0]

                # Calculate forward returns
                forward_returns = []
                for _, row in sector_only.iterrows():
                    ticker = row['ticker']
                    current_price = row['adjusted_close']

                    if ticker in df_prices.columns and actual_future_date in df_prices.index:
                        future_price = df_prices.loc[actual_future_date, ticker]
                        if pd.notna(future_price) and pd.notna(current_price):
                            fwd_ret = (future_price - current_price) / current_price
                            forward_returns.append(fwd_ret)
                        else:
                            forward_returns.append(np.nan)
                    else:
                        forward_returns.append(np.nan)

                # Store factor values and forward returns
                for fv, fr in zip(factor_values, forward_returns):
                    if pd.notna(fv) and pd.notna(fr):
                        factor_data[factor][f'{period}d_fwd'].append({
                            'date': current_date,
                            'factor_value': fv,
                            'forward_return': fr
                        })

        if i % 10 == 0:
            print(f"  Processed {i}/{len(weekly_dates)-4} weeks...")

    # Calculate Information Coefficients
    print("\n" + "="*80)
    print("INFORMATION COEFFICIENT (IC) ANALYSIS")
    print("="*80)
    print("\nIC measures correlation between factor value and forward returns")
    print("IC > 0.05: Predictive | IC < -0.05: Inverse predictive | |IC| < 0.05: Not predictive")
    print()

    ic_results = {}

    for factor in factors:
        ic_results[factor] = {}
        print(f"\n{factor.upper()}")
        print("-" * 60)
        print(f"{'Period':<15} {'IC':<10} {'P-value':<12} {'Status':<30}")
        print("-" * 60)

        for period in forward_periods:
            key = f'{period}d_fwd'
            data = factor_data[factor][key]

            if len(data) > 0:
                df_temp = pd.DataFrame(data)
                ic, p_value = calculate_information_coefficient(
                    df_temp['factor_value'],
                    df_temp['forward_return']
                )

                # Interpret results
                if abs(ic) > 0.05 and p_value < 0.05:
                    if ic > 0:
                        status = "[+] PREDICTIVE (higher = better)"
                    else:
                        status = "[+] INVERSE (lower = better)"
                elif p_value >= 0.05:
                    status = "[X] NOT SIGNIFICANT"
                else:
                    status = "[X] WEAK"

                ic_results[factor][key] = {
                    'ic': ic,
                    'p_value': p_value,
                    'status': status
                }

                print(f"{f'{period} days':<15} {ic:>8.3f} {p_value:>10.4f} {status:<30}")
            else:
                print(f"{f'{period} days':<15} {'N/A':<10} {'N/A':<12} {'Insufficient data':<30}")

    # Rolling IC analysis
    print("\n" + "="*80)
    print("ROLLING IC ANALYSIS (3-month windows)")
    print("="*80)
    print("\nChecks if factor predictiveness is stable over time")
    print()

    # Calculate rolling IC (3-month windows)
    for factor in factors:
        print(f"\n{factor.upper()} - 20-day forward returns:")
        print("-" * 60)

        data = factor_data[factor]['20d_fwd']
        if len(data) == 0:
            print("  Insufficient data")
            continue

        df_temp = pd.DataFrame(data)
        df_temp = df_temp.set_index('date')

        # Calculate rolling IC
        window_days = 60  # ~3 months
        rolling_ics = []
        rolling_dates = []

        for i in range(len(df_temp) - window_days):
            window = df_temp.iloc[i:i+window_days]
            ic, p_val = calculate_information_coefficient(
                window['factor_value'],
                window['forward_return']
            )
            rolling_ics.append(ic)
            rolling_dates.append(window.index[-1])

        if len(rolling_ics) > 0:
            avg_ic = np.mean(rolling_ics)
            std_ic = np.std(rolling_ics)
            min_ic = np.min(rolling_ics)
            max_ic = np.max(rolling_ics)

            print(f"  Average IC: {avg_ic:>8.3f}")
            print(f"  Std Dev IC: {std_ic:>8.3f}")
            print(f"  Min IC:     {min_ic:>8.3f}")
            print(f"  Max IC:     {max_ic:>8.3f}")

            # Check stability
            if std_ic < 0.1:
                print(f"  Status: [OK] STABLE (low variance)")
            elif std_ic < 0.2:
                print(f"  Status: [!] MODERATE (some variance)")
            else:
                print(f"  Status: [X] UNSTABLE (high variance)")

            # Recent trend
            recent_ic = np.mean(rolling_ics[-10:]) if len(rolling_ics) >= 10 else avg_ic
            older_ic = np.mean(rolling_ics[:10]) if len(rolling_ics) >= 10 else avg_ic

            if recent_ic > older_ic + 0.05:
                print(f"  Trend: ^^ IMPROVING (recent IC: {recent_ic:.3f})")
            elif recent_ic < older_ic - 0.05:
                print(f"  Trend: vv DECLINING (recent IC: {recent_ic:.3f})")
            else:
                print(f"  Trend: -> STABLE")

    # Hit rate analysis
    print("\n" + "="*80)
    print("HIT RATE ANALYSIS")
    print("="*80)
    print("\nHow often does the top-ranked sector outperform?")
    print()

    for period in forward_periods:
        print(f"\n{period}-day forward returns:")
        print("-" * 60)

        # For each factor, check how often top-ranked sector beats median
        for factor in factors:
            data = factor_data[factor][f'{period}d_fwd']
            if len(data) == 0:
                continue

            df_temp = pd.DataFrame(data)

            # Group by date, find top-ranked (highest factor value) and median
            hit_count = 0
            total_count = 0

            for date in df_temp['date'].unique():
                date_data = df_temp[df_temp['date'] == date]

                if len(date_data) < 3:
                    continue

                # Top ranked sector
                top_idx = date_data['factor_value'].idxmax()
                top_return = date_data.loc[top_idx, 'forward_return']

                # Median return
                median_return = date_data['forward_return'].median()

                if top_return > median_return:
                    hit_count += 1

                total_count += 1

            if total_count > 0:
                hit_rate = (hit_count / total_count) * 100

                if hit_rate > 55:
                    status = "[OK] GOOD"
                elif hit_rate > 50:
                    status = "[!] OK"
                else:
                    status = "[X] POOR"

                print(f"  {factor:<20} {hit_rate:>5.1f}% ({hit_count}/{total_count}) {status}")

    # Summary and recommendations
    print("\n" + "="*80)
    print("SUMMARY & RECOMMENDATIONS")
    print("="*80)

    print("\nFactor Effectiveness (20-day forward):")
    print("-" * 60)

    for factor in factors:
        if '20d_fwd' in ic_results[factor]:
            result = ic_results[factor]['20d_fwd']
            ic = result['ic']
            p_val = result['p_value']
            status = result['status']

            print(f"\n{factor.upper()}:")
            print(f"  IC: {ic:.3f} (p={p_val:.4f})")
            print(f"  {status}")

            if abs(ic) > 0.10 and p_val < 0.01:
                print(f"  -> STRONG FACTOR - Keep using!")
            elif abs(ic) > 0.05 and p_val < 0.05:
                print(f"  -> MODERATE FACTOR - Use with caution")
            else:
                print(f"  -> WEAK FACTOR - Consider removing")

    print("\n" + "="*80)
    print("RECOMMENDED WEIGHTS")
    print("="*80)

    # Calculate optimal weights based on IC
    total_ic = sum(abs(ic_results[f]['20d_fwd']['ic'])
                   for f in factors
                   if '20d_fwd' in ic_results[f])

    if total_ic > 0:
        print("\nBased on IC values, recommended weights:")
        for factor in factors:
            if '20d_fwd' in ic_results[factor]:
                ic = abs(ic_results[factor]['20d_fwd']['ic'])
                weight = ic / total_ic
                print(f"  {factor:<20} {weight*100:>5.1f}%")

    print(f"\nCurrent weights (equal):")
    for factor in factors:
        print(f"  {factor:<20}  25.0%")

    # Save summary to file
    from pathlib import Path
    results_dir = Path('results')
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')
    summary_file = results_dir / f'factor_validation_{start_str}_{end_str}_{timestamp}.txt'

    with open(summary_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("FACTOR VALIDATION SUMMARY\n")
        f.write("="*80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Period: {start_date.date()} to {end_date.date()}\n")
        f.write("\n")

        f.write("INFORMATION COEFFICIENT (20-day forward returns)\n")
        f.write("-"*80 + "\n")
        f.write(f"{'Factor':<20} {'IC':<10} {'P-value':<12} {'Status':<30}\n")
        f.write("-"*80 + "\n")

        for factor in factors:
            if '20d_fwd' in ic_results[factor]:
                result = ic_results[factor]['20d_fwd']
                ic = result['ic']
                p_val = result['p_value']
                status = result['status']
                f.write(f"{factor:<20} {ic:>8.3f} {p_val:>10.4f} {status:<30}\n")

        f.write("\n")
        f.write("INTERPRETATION\n")
        f.write("-"*80 + "\n")
        f.write("IC > 0.05 and p < 0.05: Predictive (higher factor = higher returns)\n")
        f.write("IC < -0.05 and p < 0.05: Inverse (lower factor = higher returns)\n")
        f.write("|IC| < 0.05 or p >= 0.05: Not significant (factor not working)\n")

        f.write("\n")
        f.write("="*80 + "\n")
        f.write("RECOMMENDATIONS\n")
        f.write("="*80 + "\n")

        for factor in factors:
            if '20d_fwd' in ic_results[factor]:
                result = ic_results[factor]['20d_fwd']
                ic = result['ic']
                p_val = result['p_value']

                f.write(f"\n{factor.upper()}:\n")
                f.write(f"  IC: {ic:.3f} (p={p_val:.4f})\n")

                if abs(ic) > 0.10 and p_val < 0.01:
                    f.write(f"  -> STRONG FACTOR - Keep using!\n")
                    if ic < 0:
                        f.write(f"  -> WARNING: Inverse signal - consider inverting ranking\n")
                elif abs(ic) > 0.05 and p_val < 0.05:
                    f.write(f"  -> MODERATE FACTOR - Use with caution\n")
                    if ic < 0:
                        f.write(f"  -> WARNING: Inverse signal - consider inverting ranking\n")
                else:
                    f.write(f"  -> WEAK FACTOR - Consider removing\n")

        f.write("\n")
        f.write("RECOMMENDED WEIGHTS (based on absolute IC)\n")
        f.write("-"*80 + "\n")

        if total_ic > 0:
            for factor in factors:
                if '20d_fwd' in ic_results[factor]:
                    ic = abs(ic_results[factor]['20d_fwd']['ic'])
                    weight = ic / total_ic
                    f.write(f"  {factor:<20} {weight*100:>5.1f}%\n")
        else:
            f.write("  All factors are weak - no weight recommendations\n")

        f.write("\n")
        f.write("CURRENT WEIGHTS (equal)\n")
        f.write("-"*80 + "\n")
        for factor in factors:
            f.write(f"  {factor:<20}  25.0%\n")

        f.write("\n")
        f.write("="*80 + "\n")
        f.write("NEXT STEPS\n")
        f.write("="*80 + "\n")
        f.write("\n")
        f.write("1. Run this validation monthly to monitor factor health\n")
        f.write("2. If IC becomes negative, consider inverting the factor\n")
        f.write("3. If |IC| < 0.05, remove the factor from your strategy\n")
        f.write("4. Adjust weights based on IC values to optimize performance\n")
        f.write("\n")
        f.write(f"For full details, run:\n")
        f.write(f"  python validate_factors.py --start {start_str[:4]}-{start_str[4:6]}-{start_str[6:]} ")
        f.write(f"--end {end_str[:4]}-{end_str[4:6]}-{end_str[6:]}\n")

    print(f"\n[OK] Summary saved to: {summary_file}")

    return ic_results


def main():
    parser = argparse.ArgumentParser(description='Validate factor effectiveness')
    parser.add_argument('--start', type=str, default='2023-01-01',
                       help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, default='2024-12-31',
                       help='End date (YYYY-MM-DD)')
    args = parser.parse_args()

    start_date = datetime.strptime(args.start, '%Y-%m-%d')
    end_date = datetime.strptime(args.end, '%Y-%m-%d')

    validate_factors(start_date, end_date)


if __name__ == "__main__":
    main()
