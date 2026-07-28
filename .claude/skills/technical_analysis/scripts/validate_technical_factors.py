"""
Validate Technical Factors for Individual Stocks

This script tests whether technical indicators (RSI, MACD, Bollinger, etc.)
are predictive of future stock returns using Information Coefficient (IC) analysis.

Usage:
    python validate_technical_factors.py --tickers AAPL MSFT GOOGL --start 2024-01-01 --end 2024-12-31 --factors rsi_14 macd_hist bb_width momentum_score

Available factors:
    - volatility: Annualized volatility
    - momentum_score: 12-1 momentum with volatility adjustment
    - momentum_raw: Raw momentum without volatility adjustment
    - dist_sma_20, dist_sma_50, dist_sma_200: Distance from SMA
    - sma_dist_20_50: Distance between 20 and 50 day SMA
    - rsi_14: RSI (14-day)
    - bb_width: Bollinger Band Width
    - bb_percent_b: Bollinger %B
    - macd_hist_12_26_9: MACD Histogram
    - relative_volume: Relative Volume
    - vpt: Volume Price Trend
    - adx_14: Average Directional Index (requires high/low data)
    - stoch_k_14, stoch_d_3: Stochastic Oscillator (requires high/low data)
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
import yfinance as yf

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))
from techinical_factor import TechnicalFactors


def calculate_information_coefficient(factor_values, forward_returns):
    """
    Calculate Information Coefficient (Spearman correlation) between factor and returns.

    IC measures how well a factor predicts future returns:
    - IC > 0.05 and p < 0.05: Predictive (higher factor = higher returns)
    - IC < -0.05 and p < 0.05: Inverse (lower factor = higher returns)
    - |IC| < 0.05 or p >= 0.05: Not significant

    Returns:
        (ic, p_value)
    """
    # Remove NaN pairs
    df_clean = pd.DataFrame({
        'factor': factor_values,
        'return': forward_returns
    }).dropna()

    if len(df_clean) < 10:
        return np.nan, np.nan

    clean_factors = df_clean['factor'].values
    clean_returns = df_clean['return'].values

    # Manual Spearman correlation (rank-based)
    factor_ranks = pd.Series(clean_factors).rank()
    return_ranks = pd.Series(clean_returns).rank()

    # Pearson correlation on ranks = Spearman
    n = len(factor_ranks)
    mean_f = factor_ranks.mean()
    mean_r = return_ranks.mean()

    cov = ((factor_ranks - mean_f) * (return_ranks - mean_r)).sum() / n
    std_f = ((factor_ranks - mean_f) ** 2).sum() / n
    std_r = ((return_ranks - mean_r) ** 2).sum() / n
    std_f = np.sqrt(std_f)
    std_r = np.sqrt(std_r)

    if std_f == 0 or std_r == 0:
        return np.nan, np.nan

    ic = cov / (std_f * std_r)

    # Calculate p-value using t-statistic
    t = ic * np.sqrt((n - 2) / (1 - ic**2 + 1e-10))

    # Two-tailed p-value (approximate)
    from math import erf
    p_value = 2 * (1 - 0.5 * (1 + erf(abs(t) / np.sqrt(2))))

    return ic, p_value


def validate_technical_factors(tickers, start_date, end_date, factors_to_test):
    """
    Validate technical factors for given tickers and time period.

    Args:
        tickers: List of stock tickers
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        factors_to_test: List of factor column names to validate

    Returns:
        Dictionary with validation results
    """
    print("=" * 80)
    print("TECHNICAL FACTOR VALIDATION")
    print("=" * 80)
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Period: {start_date} to {end_date}")
    print(f"Factors: {', '.join(factors_to_test)}")
    print()

    # Download stock data
    print("Downloading stock data...")
    all_data = []

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)

            if hist.empty:
                print(f"  [WARNING] No data for {ticker}")
                continue

            # Convert to long format
            hist = hist.reset_index()
            hist['symbol'] = ticker
            hist = hist.rename(columns={
                'Date': 'date',
                'Close': 'adjusted_close',
                'Volume': 'volume',
                'Open': 'open',
                'High': 'high',
                'Low': 'low'
            })

            all_data.append(hist[['symbol', 'date', 'adjusted_close', 'volume', 'open', 'high', 'low']])
            print(f"  [OK] {ticker}: {len(hist)} days")

        except Exception as e:
            print(f"  [ERROR] {ticker}: {e}")

    if not all_data:
        print("\n[ERROR] No data downloaded. Exiting.")
        return None

    # Combine all ticker data
    df = pd.concat(all_data, ignore_index=True)
    print(f"\n[OK] Combined data: {len(df)} rows for {df['symbol'].nunique()} symbols")

    # Calculate technical factors
    print("\nCalculating technical factors...")
    tf = TechnicalFactors(df)

    # Run all factors to ensure dependencies are met
    tf.run_all(include_high_low_indicators=True)
    df = tf.df

    print(f"[OK] Technical factors calculated")
    print(f"Available factor columns: {', '.join(tf.get_factor_columns())}")

    # Calculate forward returns (5, 10, 20 days)
    print("\nCalculating forward returns...")
    for horizon in [5, 10, 20]:
        df[f'fwd_return_{horizon}d'] = df.groupby('symbol')['adjusted_close'].pct_change(horizon).shift(-horizon)

    print("[OK] Forward returns calculated")

    # Validate each factor
    print("\n" + "=" * 80)
    print("FACTOR VALIDATION RESULTS")
    print("=" * 80)

    results = {}

    for factor in factors_to_test:
        if factor not in df.columns:
            print(f"\n[WARNING] Factor '{factor}' not found in data. Skipping.")
            continue

        print(f"\nFactor: {factor}")
        print("-" * 80)

        factor_results = {}

        # Calculate IC for each forward return horizon
        for horizon in [5, 10, 20]:
            fwd_col = f'fwd_return_{horizon}d'

            ic, p_value = calculate_information_coefficient(
                df[factor].values,
                df[fwd_col].values
            )

            # Determine status
            if pd.isna(ic) or pd.isna(p_value):
                status = "INSUFFICIENT DATA"
            elif abs(ic) < 0.05 or p_value >= 0.05:
                status = "NOT SIGNIFICANT"
            elif ic > 0.05:
                status = "PREDICTIVE (higher = better)"
            else:
                status = "INVERSE (lower = better)"

            factor_results[f'{horizon}d'] = {
                'ic': ic,
                'p_value': p_value,
                'status': status
            }

            print(f"  {horizon}-day forward returns:")
            print(f"    IC: {ic:>7.4f}" if not pd.isna(ic) else "    IC:     N/A")
            print(f"    P-value: {p_value:>7.4f}" if not pd.isna(p_value) else "    P-value:     N/A")
            print(f"    Status: {status}")

        results[factor] = factor_results

    # Overall recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    for factor, factor_data in results.items():
        print(f"\n{factor.upper()}:")

        # Use 20-day horizon as primary indicator
        if '20d' in factor_data:
            ic = factor_data['20d']['ic']
            p_value = factor_data['20d']['p_value']
            status = factor_data['20d']['status']

            print(f"  IC (20-day): {ic:.4f} (p={p_value:.4f})" if not pd.isna(ic) else "  IC (20-day): N/A")

            if pd.isna(ic):
                print(f"  -> INSUFFICIENT DATA - Cannot validate")
            elif abs(ic) < 0.05 or p_value >= 0.05:
                print(f"  -> WEAK FACTOR - Not predictive")
            elif ic > 0.05:
                print(f"  -> STRONG FACTOR - Higher values predict better returns")
            else:
                print(f"  -> INVERSE FACTOR - Lower values predict better returns")

    return results


def save_report(results, tickers, start_date, end_date, factors_to_test, output_file):
    """Save validation results to text file."""

    with open(output_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("TECHNICAL FACTOR VALIDATION SUMMARY\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Tickers: {', '.join(tickers)}\n")
        f.write(f"Period: {start_date} to {end_date}\n")
        f.write(f"\n")

        # Results table
        f.write("INFORMATION COEFFICIENT (20-day forward returns)\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Factor':<30} {'IC':<12} {'P-value':<12} {'Status':<30}\n")
        f.write("-" * 80 + "\n")

        for factor, factor_data in results.items():
            if '20d' in factor_data:
                ic = factor_data['20d']['ic']
                p_value = factor_data['20d']['p_value']
                status = factor_data['20d']['status']

                ic_str = f"{ic:.4f}" if not pd.isna(ic) else "N/A"
                p_str = f"{p_value:.4f}" if not pd.isna(p_value) else "N/A"

                f.write(f"{factor:<30} {ic_str:<12} {p_str:<12} {status:<30}\n")

        f.write("\n")
        f.write("INTERPRETATION\n")
        f.write("-" * 80 + "\n")
        f.write("IC > 0.05 and p < 0.05: Predictive (higher factor = higher returns)\n")
        f.write("IC < -0.05 and p < 0.05: Inverse (lower factor = higher returns)\n")
        f.write("|IC| < 0.05 or p >= 0.05: Not significant (factor not working)\n")
        f.write("\n")

        # Detailed recommendations
        f.write("=" * 80 + "\n")
        f.write("RECOMMENDATIONS\n")
        f.write("=" * 80 + "\n")
        f.write("\n")

        for factor, factor_data in results.items():
            if '20d' in factor_data:
                ic = factor_data['20d']['ic']
                p_value = factor_data['20d']['p_value']

                f.write(f"{factor.upper()}:\n")
                f.write(f"  IC: {ic:.4f} (p={p_value:.4f})\n" if not pd.isna(ic) else "  IC: N/A\n")

                if pd.isna(ic):
                    f.write(f"  -> INSUFFICIENT DATA\n")
                elif abs(ic) < 0.05 or p_value >= 0.05:
                    f.write(f"  -> WEAK FACTOR - Consider removing\n")
                elif ic > 0.05:
                    f.write(f"  -> STRONG FACTOR - Keep using!\n")
                    f.write(f"  -> Higher values = Better returns\n")
                else:
                    f.write(f"  -> STRONG FACTOR - Keep using!\n")
                    f.write(f"  -> WARNING: Inverse signal - Lower values = Better returns\n")

                f.write("\n")

        # Multi-horizon analysis
        f.write("=" * 80 + "\n")
        f.write("MULTI-HORIZON ANALYSIS (5, 10, 20 days)\n")
        f.write("=" * 80 + "\n")
        f.write("\n")

        for factor, factor_data in results.items():
            f.write(f"{factor}:\n")
            for horizon in ['5d', '10d', '20d']:
                if horizon in factor_data:
                    ic = factor_data[horizon]['ic']
                    p_value = factor_data[horizon]['p_value']
                    status = factor_data[horizon]['status']

                    ic_str = f"{ic:+.4f}" if not pd.isna(ic) else "  N/A"
                    p_str = f"p={p_value:.4f}" if not pd.isna(p_value) else "p=N/A"

                    f.write(f"  {horizon}: IC={ic_str} ({p_str}) - {status}\n")
            f.write("\n")

        f.write("=" * 80 + "\n")
        f.write("NEXT STEPS\n")
        f.write("=" * 80 + "\n")
        f.write("\n")
        f.write("1. Run this validation monthly to monitor factor health\n")
        f.write("2. If IC is consistently negative, consider inverting the factor in your strategy\n")
        f.write("3. If |IC| < 0.05, remove the factor from your strategy\n")
        f.write("4. Test different factor parameters (e.g., RSI-9 vs RSI-14 vs RSI-21)\n")
        f.write("5. Combine multiple factors with high IC for better predictions\n")
        f.write("\n")

    print(f"\n[OK] Report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Validate technical factors for stock analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate RSI and MACD for AAPL and MSFT
  python validate_technical_factors.py --tickers AAPL MSFT --start 2024-01-01 --end 2024-12-31 --factors rsi_14 macd_hist_12_26_9

  # Validate multiple momentum factors
  python validate_technical_factors.py --tickers GOOGL AMZN --start 2023-01-01 --end 2024-12-31 --factors momentum_score momentum_raw dist_sma_200

  # Validate Bollinger Bands
  python validate_technical_factors.py --tickers SPY QQQ --start 2024-01-01 --end 2024-12-31 --factors bb_width bb_percent_b
        """
    )

    parser.add_argument('--tickers', nargs='+', required=True,
                        help='List of stock tickers to analyze (e.g., AAPL MSFT GOOGL)')
    parser.add_argument('--start', required=True,
                        help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', required=True,
                        help='End date (YYYY-MM-DD)')
    parser.add_argument('--factors', nargs='+', required=True,
                        help='List of technical factors to validate (e.g., rsi_14 macd_hist_12_26_9 bb_width)')

    args = parser.parse_args()

    # Validate dates
    try:
        datetime.strptime(args.start, '%Y-%m-%d')
        datetime.strptime(args.end, '%Y-%m-%d')
    except ValueError:
        print("Error: Dates must be in YYYY-MM-DD format")
        sys.exit(1)

    # Run validation
    results = validate_technical_factors(
        tickers=args.tickers,
        start_date=args.start,
        end_date=args.end,
        factors_to_test=args.factors
    )

    if results is None:
        sys.exit(1)

    # Save report
    results_dir = Path(__file__).parent.parent / 'results'
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    tickers_str = '_'.join(args.tickers[:3])  # Limit filename length
    if len(args.tickers) > 3:
        tickers_str += '_etc'

    output_file = results_dir / f"factor_validation_{tickers_str}_{args.start.replace('-', '')}_{args.end.replace('-', '')}_{timestamp}.txt"

    save_report(results, args.tickers, args.start, args.end, args.factors, output_file)

    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    print(f"Report saved to: {output_file}")


if __name__ == '__main__':
    main()
