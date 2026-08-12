"""
Adaptive Regime Filter Strategy

Instead of rigid "stay 50% cash while below 200MA", this uses:
- Fast re-entry on strong bounces
- Multi-timeframe confirmation
- Volatility-based adjustments

This works better for V-shaped recoveries while still protecting downside.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import sys
import argparse
from pathlib import Path
import io
import contextlib

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from calculate_sector_metrics import (
    calculate_relative_strength,
    calculate_momentum,
    rank_sectors
)

# Configuration
INITIAL_CAPITAL = 100000
TRANSACTION_COST_PCT = 0.0

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


def calculate_exposure(spy_data, current_date):
    """
    Calculate portfolio exposure based on adaptive rules

    Returns
    -------
    float
        Portfolio exposure (0.5 = 50% cash, 1.0 = fully invested)
    """
    row = spy_data.loc[current_date]

    # Calculate indicators
    price = row['Close']
    ma200 = row['MA200']
    ma50 = row['MA50']

    # Returns
    ret_5d = row['Return_5d'] * 100 if pd.notna(row['Return_5d']) else 0
    ret_10d = row['Return_10d'] * 100 if pd.notna(row['Return_10d']) else 0

    # Volatility
    vol = row['Volatility_10d'] if pd.notna(row['Volatility_10d']) else 3.0

    # Rules
    below_ma200 = price < ma200
    below_ma50 = price < ma50
    strong_bounce = ret_5d > 5  # +5% in 5 days
    grinding_up = ret_10d > 3  # +3% in 10 days
    low_vol = vol < 2.0

    # Adaptive exposure logic
    if not below_ma200:
        # Above 200-day MA = fully invested
        return 1.0

    # Below 200-day MA, check for recovery signals
    if strong_bounce and not below_ma50:
        # Strong bounce AND above 50-day MA = likely V-recovery
        return 1.0

    if strong_bounce and low_vol:
        # Strong bounce with low volatility = safe to re-enter
        return 0.9

    if grinding_up and not below_ma50:
        # Grinding higher and above 50-day MA
        return 0.8

    if grinding_up:
        # Some upward momentum, cautiously increase
        return 0.7

    # Default: below MA with no clear recovery signals
    return 0.5


def main():
    parser = argparse.ArgumentParser(description='Adaptive regime filter backtest')
    parser.add_argument('--top', type=int, default=3, choices=[3, 5])
    parser.add_argument('--start', type=str, required=True)
    parser.add_argument('--end', type=str, required=True)
    args = parser.parse_args()

    start_date = datetime.strptime(args.start, '%Y-%m-%d')
    end_date = datetime.strptime(args.end, '%Y-%m-%d')

    print("="*80)
    print("ADAPTIVE REGIME FILTER BACKTEST")
    print("="*80)
    print(f"Top {args.top} sectors")
    print(f"Period: {args.start} to {args.end}")
    print()
    print("Rules:")
    print("  - SPY > 200-day MA = 100% invested")
    print("  - SPY < 200-day MA + strong bounce (+5% in 5d) + above 50MA = 100%")
    print("  - SPY < 200-day MA + strong bounce + low vol = 90%")
    print("  - SPY < 200-day MA + grinding up + above 50MA = 80%")
    print("  - SPY < 200-day MA + grinding up = 70%")
    print("  - SPY < 200-day MA + weak = 50%")
    print()

    # Fetch data
    fetch_start = start_date - timedelta(days=365)
    all_tickers = list(SECTOR_ETFS.keys()) + ['SPY']
    sector_data = {}

    print("Fetching data...")
    for ticker in all_tickers:
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=fetch_start, end=end_date)
            if not data.empty:
                sector_data[ticker] = data['Close']
        except:
            pass

    df_prices = pd.DataFrame(sector_data)
    df_prices = df_prices.dropna()
    df_prices.index = df_prices.index.tz_localize(None)

    # Calculate SPY indicators
    spy_indicators = pd.DataFrame(index=df_prices.index)
    spy_indicators['Close'] = df_prices['SPY']
    spy_indicators['MA50'] = spy_indicators['Close'].rolling(window=50).mean()
    spy_indicators['MA200'] = spy_indicators['Close'].rolling(window=200).mean()
    spy_indicators['Return_1d'] = spy_indicators['Close'].pct_change()
    spy_indicators['Return_5d'] = spy_indicators['Close'].pct_change(periods=5)
    spy_indicators['Return_10d'] = spy_indicators['Close'].pct_change(periods=10)
    spy_indicators['Volatility_10d'] = spy_indicators['Return_1d'].rolling(window=10).std() * 100

    # Create sector dataframe
    sector_df = pd.DataFrame()
    for ticker in SECTOR_ETFS.keys():
        if ticker in df_prices.columns:
            temp_df = pd.DataFrame({
                'date': df_prices.index,
                'ticker': ticker,
                'sector_name': SECTOR_ETFS[ticker],
                'adjusted_close': df_prices[ticker].values
            })
            sector_df = pd.concat([sector_df, temp_df], ignore_index=True)

    spy_df = pd.DataFrame({
        'date': df_prices.index,
        'ticker': 'SPY',
        'sector_name': 'S&P 500',
        'adjusted_close': df_prices['SPY'].values
    })
    sector_df = pd.concat([sector_df, spy_df], ignore_index=True)

    # Get rebalancing dates
    all_dates = df_prices.index[df_prices.index >= start_date]
    rebal_dates = []
    for date in all_dates:
        week_num = date.isocalendar()[1]
        next_day = date + timedelta(days=1)
        if next_day not in all_dates or next_day.isocalendar()[1] != week_num:
            rebal_dates.append(date)

    print(f"[OK] {len(rebal_dates)} rebalancing dates")

    # Initialize portfolios
    portfolio = {
        'cash': INITIAL_CAPITAL,
        'positions': {},
        'value_history': [],
        'date_history': [],
        'exposure_history': []
    }

    spy_benchmark = {
        'shares': INITIAL_CAPITAL / df_prices.loc[rebal_dates[0], 'SPY'],
        'value_history': [],
        'date_history': []
    }

    # Run backtest
    print("\nRunning backtest...")
    for i, rebal_date in enumerate(rebal_dates):
        historical_data = sector_df[sector_df['date'] <= rebal_date].copy()

        # Calculate sector rankings
        with contextlib.redirect_stdout(io.StringIO()):
            historical_data = calculate_relative_strength(historical_data)
            historical_data = calculate_momentum(historical_data)
            sector_only = historical_data[historical_data['ticker'] != 'SPY'].copy()
            rankings = rank_sectors(sector_only)

        top_sectors = rankings.head(args.top)['ticker'].tolist()

        # Calculate current exposure based on adaptive rules
        exposure = calculate_exposure(spy_indicators, rebal_date)
        portfolio['exposure_history'].append(exposure)

        # Calculate portfolio value
        portfolio_value = portfolio['cash']
        for ticker, shares in portfolio['positions'].items():
            if ticker in df_prices.columns:
                portfolio_value += shares * df_prices.loc[rebal_date, ticker]

        portfolio['value_history'].append(portfolio_value)
        portfolio['date_history'].append(rebal_date)

        # Sell all positions
        for ticker in list(portfolio['positions'].keys()):
            shares = portfolio['positions'][ticker]
            if shares > 0:
                price = df_prices.loc[rebal_date, ticker]
                proceeds = shares * price
                portfolio['cash'] += proceeds

        portfolio['positions'] = {}

        # Buy top sectors with exposure adjustment
        cash_to_invest = portfolio['cash'] * exposure
        equal_weight = 1.0 / args.top
        target_value_per_sector = cash_to_invest * equal_weight

        for ticker in top_sectors:
            price = df_prices.loc[rebal_date, ticker]
            shares_to_buy = target_value_per_sector / price
            portfolio['positions'][ticker] = shares_to_buy

        # Update cash (keeping uninvested portion)
        portfolio['cash'] = portfolio['cash'] * (1 - exposure)

        # SPY benchmark
        spy_value = spy_benchmark['shares'] * df_prices.loc[rebal_date, 'SPY']
        spy_benchmark['value_history'].append(spy_value)
        spy_benchmark['date_history'].append(rebal_date)

        if i % 5 == 0:
            print(f"  Week {i+1}/{len(rebal_dates)} - {rebal_date.date()} - Exposure: {exposure*100:.0f}%")

    # Calculate metrics
    returns = pd.Series(portfolio['value_history'], index=portfolio['date_history'])
    final_value = returns.iloc[-1]
    total_return = ((final_value - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100

    spy_returns = pd.Series(spy_benchmark['value_history'], index=spy_benchmark['date_history'])
    spy_final = spy_returns.iloc[-1]
    spy_return = ((spy_final - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100

    alpha = total_return - spy_return

    # Results
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    print(f"\nAdaptive Regime:  ${final_value:,.2f} ({total_return:+.2f}%)")
    print(f"SPY Benchmark:    ${spy_final:,.2f} ({spy_return:+.2f}%)")
    print(f"Alpha:            {alpha:+.2f}%")

    # Show exposure changes
    print("\n" + "="*80)
    print("EXPOSURE ADJUSTMENTS")
    print("="*80)

    exposure_series = pd.Series(portfolio['exposure_history'], index=portfolio['date_history'])
    changes = exposure_series[exposure_series != exposure_series.shift(1)]

    print(f"\n{'Date':<15} {'Exposure':<12} {'Reason':<50}")
    print("-"*80)
    for date, exposure in changes.items():
        row = spy_indicators.loc[date]
        reason = ""
        if exposure == 1.0:
            if row['Close'] > row['MA200']:
                reason = "Above 200-day MA"
            else:
                reason = "Strong bounce + above 50MA"
        elif exposure == 0.9:
            reason = "Strong bounce + low volatility"
        elif exposure == 0.8:
            reason = "Grinding up + above 50MA"
        elif exposure == 0.7:
            reason = "Grinding up slowly"
        else:
            reason = "Below MA, no recovery signal"

        print(f"{date.strftime('%Y-%m-%d'):<15} {exposure*100:>4.0f}%        {reason:<50}")

    print("\n" + "="*80)
    print("COMPARISON vs STANDARD REGIME")
    print("="*80)
    print(f"\nStandard Regime (50% when below MA): ~14.69%")
    print(f"Adaptive Regime:                      {total_return:+.2f}%")
    print(f"Improvement:                          {total_return - 14.69:+.2f}%")
    print(f"\nSPY:                                  {spy_return:+.2f}%")
    print(f"Alpha vs SPY:                         {alpha:+.2f}%")


if __name__ == "__main__":
    main()
