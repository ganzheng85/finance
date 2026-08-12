"""
Fetch Sector ETF Data

Downloads price and volume data for 13 sector ETFs (11 S&P sectors + SMH + MAGS) + SPY benchmark.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


# 11 SPDR Sector ETFs + Special Sectors + SPY Benchmark
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
    'IGV': 'Software',
    'SPY': 'S&P 500 Benchmark'
}


def fetch_sector_etfs(lookback_days=365):
    """
    Fetch daily price/volume data for all sector ETFs

    Parameters
    ----------
    lookback_days : int
        Number of days of historical data to fetch

    Returns
    -------
    pd.DataFrame
        Combined dataframe with all sector data
    """
    print(f"\n{'='*60}")
    print("FETCHING SECTOR ETF DATA")
    print(f"{'='*60}")

    all_data = []

    for ticker, name in SECTOR_ETFS.items():
        try:
            print(f"Fetching {ticker} ({name})...")

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)

            # Download data using Ticker object for more reliable structure
            etf = yf.Ticker(ticker)
            df = etf.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d')
            )

            if df.empty:
                print(f"  [WARNING] No data for {ticker}")
                continue

            # Reset index to make date a column
            df = df.reset_index()

            # Standardize column names
            df.columns = [str(col).replace(' ', '_').lower() for col in df.columns]

            # Add ticker and name columns
            df['ticker'] = ticker
            df['sector_name'] = name

            # Ensure we have the right column names
            if 'close' in df.columns and 'adjusted_close' not in df.columns:
                df['adjusted_close'] = df['close']

            all_data.append(df)

            print(f"  [OK] {len(df)} days fetched")

        except Exception as e:
            print(f"  [ERROR] Failed to fetch {ticker} ({name})")
            print(f"          Error: {str(e)}")
            print(f"          This ETF will be skipped, continuing with others...")
            continue

    if not all_data:
        error_msg = "\n" + "="*60 + "\n"
        error_msg += "WARNING: Failed to fetch ANY sector data from Yahoo Finance\n"
        error_msg += "="*60 + "\n"
        error_msg += "Possible causes:\n"
        error_msg += "  - Network connection is down\n"
        error_msg += "  - Yahoo Finance API is temporarily unavailable\n"
        error_msg += "  - Firewall blocking access to Yahoo Finance\n"
        error_msg += "  - Rate limiting (too many requests)\n"
        error_msg += "\nPlease check your internet connection and try again.\n"
        error_msg += "="*60 + "\n"
        print(error_msg)
        raise Exception("No sector data could be fetched - Yahoo Finance connection failed")

    # Combine all dataframes
    combined_df = pd.concat(all_data, ignore_index=True)

    # Ensure date is datetime
    combined_df['date'] = pd.to_datetime(combined_df['date'])

    # Sort by ticker and date
    combined_df = combined_df.sort_values(['ticker', 'date']).reset_index(drop=True)

    sector_count = len([k for k in SECTOR_ETFS.keys() if k != 'SPY'])
    print(f"\n[OK] Fetched data for {len(SECTOR_ETFS)} ETFs ({sector_count} sectors + SPY)")
    print(f"  Total rows: {len(combined_df)}")
    print(f"  Date range: {combined_df['date'].min().date()} to {combined_df['date'].max().date()}")

    return combined_df


if __name__ == "__main__":
    # Test the fetcher
    df = fetch_sector_etfs(lookback_days=180)
    print(f"\nSample data:")
    print(df.head())
    print(f"\nColumns: {df.columns.tolist()}")
