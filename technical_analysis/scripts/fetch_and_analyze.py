"""
Technical Analysis Script - Fetch Yahoo Finance data and compute technical factors.

Usage:
    python fetch_and_analyze.py TICKER [--days DAYS]

Example:
    python fetch_and_analyze.py AAPL
    python fetch_and_analyze.py TSLA --days 60
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta

import yfinance as yf
import pandas as pd
import numpy as np

# Add parent directory to path to import from lib
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.techinical_factor import TechnicalFactors


def fetch_stock_data(ticker: str, lookback_days: int = 365) -> pd.DataFrame:
    """
    Fetch historical stock data from Yahoo Finance.

    Parameters
    ----------
    ticker : str
        Stock ticker symbol (e.g., 'AAPL', 'TSLA')
    lookback_days : int
        Number of days of historical data to fetch (default: 365)
        Note: We need ~300 days to calculate 252-day momentum factor

    Returns
    -------
    pd.DataFrame
        Long-format DataFrame with columns:
        ['symbol', 'date', 'open', 'high', 'low', 'close', 'adjusted_close', 'volume']
    """
    print(f"\n{'='*60}")
    print(f"Fetching data for {ticker.upper()}")
    print(f"{'='*60}")

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)

    print(f"Date range: {start_date.date()} to {end_date.date()}")
    print(f"Fetching from Yahoo Finance...")

    try:
        # Fetch data
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)

        if hist.empty:
            raise ValueError(f"No data found for ticker '{ticker}'. Please check if the ticker is valid.")

        # Reset index to get date as column
        hist = hist.reset_index()

        # Rename columns to match expected format
        df = pd.DataFrame({
            'symbol': ticker.upper(),
            'date': hist['Date'],
            'open': hist['Open'],
            'high': hist['High'],
            'low': hist['Low'],
            'close': hist['Close'],
            'adjusted_close': hist['Close'],  # Yahoo Finance auto-adjusts
            'volume': hist['Volume']
        })

        # Ensure date is datetime
        df['date'] = pd.to_datetime(df['date'])

        print(f"[OK] Fetched {len(df)} trading days")
        print(f"  Latest date: {df['date'].max().date()}")
        print(f"  Price range: ${df['adjusted_close'].min():.2f} - ${df['adjusted_close'].max():.2f}")

        return df

    except Exception as e:
        print(f"[ERROR] Error fetching data: {str(e)}")
        raise


def calculate_all_factors(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all technical factors using TechnicalFactors class.

    Parameters
    ----------
    df : pd.DataFrame
        Stock data with columns ['symbol', 'date', 'adjusted_close', 'volume', 'high', 'low']

    Returns
    -------
    pd.DataFrame
        Original data plus all technical factor columns
    """
    print(f"\n{'='*60}")
    print("Computing Technical Factors")
    print(f"{'='*60}")

    # Initialize TechnicalFactors
    tf = TechnicalFactors(df, price_col='adjusted_close', volume_col='volume')

    # Calculate all factors (run_all includes all indicators)
    result_df = tf.run_all(include_high_low_indicators=True)

    print(f"\n[OK] All factors computed successfully!")
    print(f"  Total columns: {len(result_df.columns)}")
    print(f"  Factor columns: {len(tf.get_factor_columns())}")

    return result_df


def get_recent_data(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """
    Extract the most recent N days of data.

    Parameters
    ----------
    df : pd.DataFrame
        Full DataFrame with all data
    days : int
        Number of most recent trading days to extract (default: 30)

    Returns
    -------
    pd.DataFrame
        DataFrame with only the most recent N days
    """
    # Sort by date descending and take top N rows
    df_sorted = df.sort_values('date', ascending=False)
    recent = df_sorted.head(days).sort_values('date', ascending=True)

    print(f"\n{'='*60}")
    print(f"Extracting Last {days} Trading Days")
    print(f"{'='*60}")
    print(f"Date range: {recent['date'].min().date()} to {recent['date'].max().date()}")

    return recent


def save_to_csv(df: pd.DataFrame, ticker: str, output_dir: str = "analyses") -> str:
    """
    Save DataFrame to CSV file.

    Parameters
    ----------
    df : pd.DataFrame
        Data to save
    ticker : str
        Stock ticker
    output_dir : str
        Output directory (default: 'analyses')

    Returns
    -------
    str
        Path to saved CSV file
    """
    # Create output directory if it doesn't exist
    output_path = Path(__file__).parent.parent / output_dir
    output_path.mkdir(exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    filename = f"{ticker.upper()}_technical_factors_{timestamp}.csv"
    filepath = output_path / filename

    # Save to CSV
    df.to_csv(filepath, index=False)

    print(f"\n[OK] Data saved to: {filepath}")

    return str(filepath)


def display_summary(df: pd.DataFrame, ticker: str, days: int = 30):
    """
    Display summary of recent technical factors.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with technical factors
    ticker : str
        Stock ticker
    days : int
        Number of days shown (for display purposes)
    """
    print(f"\n{'='*60}")
    print(f"TECHNICAL FACTORS SUMMARY - {ticker.upper()}")
    print(f"Last {days} Trading Days")
    print(f"{'='*60}")

    # Get latest values (most recent day)
    latest = df.iloc[-1]

    print(f"\nDate: {latest['date'].strftime('%Y-%m-%d')}")
    print(f"Price: ${latest['adjusted_close']:.2f}")
    print(f"Volume: {latest['volume']:,.0f}")

    print(f"\n--- Trend Indicators ---")

    # Momentum
    if 'momentum_score' in df.columns and pd.notna(latest['momentum_score']):
        print(f"Momentum (12-1):        {latest['momentum_score']:+.4f}")

    # Distance from SMAs
    if 'dist_sma_200' in df.columns and pd.notna(latest['dist_sma_200']):
        print(f"Distance from SMA(200): {latest['dist_sma_200']*100:+.2f}%")
    if 'dist_sma_50' in df.columns and pd.notna(latest['dist_sma_50']):
        print(f"Distance from SMA(50):  {latest['dist_sma_50']*100:+.2f}%")
    if 'dist_sma_20' in df.columns and pd.notna(latest['dist_sma_20']):
        print(f"Distance from SMA(20):  {latest['dist_sma_20']*100:+.2f}%")

    # SMA distance
    if 'sma_dist_20_50' in df.columns and pd.notna(latest['sma_dist_20_50']):
        print(f"SMA(20) vs SMA(50):     {latest['sma_dist_20_50']*100:+.2f}%")

    print(f"\n--- Momentum Oscillators ---")

    # RSI
    if 'rsi_14' in df.columns and pd.notna(latest['rsi_14']):
        rsi = latest['rsi_14']
        rsi_signal = "OVERSOLD" if rsi < 30 else "OVERBOUGHT" if rsi > 70 else "NEUTRAL"
        print(f"RSI(14):                {rsi:.2f} ({rsi_signal})")

    # Stochastic
    if 'stoch_k_14' in df.columns and pd.notna(latest['stoch_k_14']):
        stoch_k = latest['stoch_k_14']
        stoch_signal = "OVERSOLD" if stoch_k < 20 else "OVERBOUGHT" if stoch_k > 80 else "NEUTRAL"
        print(f"Stochastic %K(14):      {stoch_k:.2f} ({stoch_signal})")

    # MACD
    if 'macd_hist_12_26_9' in df.columns and pd.notna(latest['macd_hist_12_26_9']):
        macd_hist = latest['macd_hist_12_26_9']
        macd_signal = "BULLISH" if macd_hist > 0 else "BEARISH"
        print(f"MACD Histogram:         {macd_hist:+.4f} ({macd_signal})")

    print(f"\n--- Volatility & Volume ---")

    # Volatility
    if 'volatility' in df.columns and pd.notna(latest['volatility']):
        print(f"Annualized Volatility:  {latest['volatility']*100:.2f}%")

    # Bollinger Band Width
    if 'bb_width' in df.columns and pd.notna(latest['bb_width']):
        print(f"Bollinger Width:        {latest['bb_width']:.4f}")

    # Bollinger %B
    if 'bb_percent_b' in df.columns and pd.notna(latest['bb_percent_b']):
        pct_b = latest['bb_percent_b']
        bb_signal = "BELOW LOWER" if pct_b < 0 else "ABOVE UPPER" if pct_b > 1 else "WITHIN BANDS"
        print(f"Bollinger %B:           {pct_b:.2f} ({bb_signal})")

    # Relative Volume
    if 'relative_volume' in df.columns and pd.notna(latest['relative_volume']):
        rvol = latest['relative_volume']
        rvol_signal = "HIGH" if rvol > 2 else "ELEVATED" if rvol > 1.5 else "NORMAL"
        print(f"Relative Volume:        {rvol:.2f}x ({rvol_signal})")

    # ADX
    if 'adx_14' in df.columns and pd.notna(latest['adx_14']):
        adx = latest['adx_14']
        adx_signal = "STRONG TREND" if adx > 25 else "WEAK TREND"
        print(f"ADX(14):                {adx:.2f} ({adx_signal})")

    print(f"\n{'='*60}")


def main():
    """Main function to run the technical analysis."""
    parser = argparse.ArgumentParser(
        description='Fetch stock data and calculate technical factors',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetch_and_analyze.py AAPL
  python fetch_and_analyze.py TSLA --days 60
  python fetch_and_analyze.py NVDA --lookback 500
        """
    )
    parser.add_argument('ticker', type=str, help='Stock ticker symbol (e.g., AAPL, TSLA)')
    parser.add_argument('--days', type=int, default=30, help='Number of recent days to show (default: 30)')
    parser.add_argument('--lookback', type=int, default=365, help='Days of historical data to fetch (default: 365)')
    parser.add_argument('--no-save', action='store_true', help='Do not save CSV file')

    args = parser.parse_args()

    try:
        # Step 1: Fetch data
        df = fetch_stock_data(args.ticker, lookback_days=args.lookback)

        # Step 2: Calculate all technical factors
        df_with_factors = calculate_all_factors(df)

        # Step 3: Get recent data
        df_recent = get_recent_data(df_with_factors, days=args.days)

        # Step 4: Display summary
        display_summary(df_recent, args.ticker, days=args.days)

        # Step 5: Save to CSV
        if not args.no_save:
            csv_path = save_to_csv(df_recent, args.ticker)
            print(f"\n[OK] Analysis complete! CSV saved to: {csv_path}")
        else:
            print(f"\n[OK] Analysis complete! (CSV not saved)")

        return df_recent

    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
