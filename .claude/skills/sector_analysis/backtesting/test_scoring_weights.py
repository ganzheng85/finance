"""
Test Different Scoring Weights

This script tests multiple weight combinations to find the best one
for your specific period.

Usage:
    python test_scoring_weights.py --start 2025-04-05 --end 2025-09-01
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

from calculate_sector_metrics_weighted import (
    calculate_relative_strength,
    calculate_momentum,
    rank_sectors_weighted
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

# Weight combinations to test
WEIGHT_SCENARIOS = {
    'Equal Weight (Current)': {
        'rs_20d': 0.25,
        'rs_60d': 0.25,
        'momentum': 0.25,
        'return_20d': 0.25
    },
    'Momentum Heavy': {
        'rs_20d': 0.15,
        'rs_60d': 0.25,
        'momentum': 0.50,  # 50% weight on momentum
        'return_20d': 0.10
    },
    'Momentum Dominant': {
        'rs_20d': 0.10,
        'rs_60d': 0.20,
        'momentum': 0.60,  # 60% weight on momentum
        'return_20d': 0.10
    },
    'Recent Strength Focus': {
        'rs_20d': 0.40,  # Focus on short-term
        'rs_60d': 0.20,
        'momentum': 0.30,
        'return_20d': 0.10
    },
    'Balanced RS': {
        'rs_20d': 0.30,
        'rs_60d': 0.30,  # Equal RS focus
        'momentum': 0.30,
        'return_20d': 0.10
    },
    'Long-term Momentum': {
        'rs_20d': 0.10,
        'rs_60d': 0.40,  # Focus on medium-term
        'momentum': 0.40,
        'return_20d': 0.10
    }
}


def run_backtest(weights, weight_name, start_date, end_date, top_n=3):
    """Run backtest with specific weights"""

    # Fetch data (extra for lookback)
    fetch_start = start_date - timedelta(days=365)

    all_tickers = list(SECTOR_ETFS.keys()) + ['SPY']
    sector_data = {}

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

    # Get rebalancing dates (weekly)
    all_dates = df_prices.index[df_prices.index >= start_date]
    rebal_dates = []
    for date in all_dates:
        week_num = date.isocalendar()[1]
        next_day = date + timedelta(days=1)
        if next_day not in all_dates or next_day.isocalendar()[1] != week_num:
            rebal_dates.append(date)

    if not rebal_dates:
        return None

    # Initialize portfolio
    portfolio = {
        'cash': INITIAL_CAPITAL,
        'positions': {},
        'value_history': [],
        'date_history': []
    }

    spy_benchmark = {
        'shares': INITIAL_CAPITAL / df_prices.loc[rebal_dates[0], 'SPY'],
        'value_history': [],
        'date_history': []
    }

    # Run backtest
    for rebal_date in rebal_dates:
        historical_data = sector_df[sector_df['date'] <= rebal_date].copy()

        # Calculate metrics and rank with custom weights (suppress output)
        with contextlib.redirect_stdout(io.StringIO()):
            historical_data = calculate_relative_strength(historical_data)
            historical_data = calculate_momentum(historical_data)
            sector_only = historical_data[historical_data['ticker'] != 'SPY'].copy()
            rankings = rank_sectors_weighted(sector_only, weights=weights, verbose=False)

        top_sectors = rankings.head(top_n)['ticker'].tolist()

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
                cost = proceeds * TRANSACTION_COST_PCT
                portfolio['cash'] += proceeds - cost

        portfolio['positions'] = {}

        # Buy top N sectors
        equal_weight = 1.0 / top_n
        target_value_per_sector = portfolio['cash'] * equal_weight

        for ticker in top_sectors:
            price = df_prices.loc[rebal_date, ticker]
            shares_to_buy = target_value_per_sector / price
            portfolio['positions'][ticker] = shares_to_buy

        portfolio['cash'] = 0

        # SPY benchmark
        spy_value = spy_benchmark['shares'] * df_prices.loc[rebal_date, 'SPY']
        spy_benchmark['value_history'].append(spy_value)
        spy_benchmark['date_history'].append(rebal_date)

    # Calculate metrics
    returns = pd.Series(portfolio['value_history'], index=portfolio['date_history'])
    final_value = returns.iloc[-1]
    total_return = ((final_value - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100

    days_elapsed = (rebal_dates[-1] - rebal_dates[0]).days
    years_elapsed = days_elapsed / 365.25
    annual_return = ((final_value / INITIAL_CAPITAL) ** (1/years_elapsed) - 1) * 100

    daily_returns = returns.pct_change().dropna()
    volatility = daily_returns.std() * np.sqrt(252) * 100
    sharpe = annual_return / volatility if volatility > 0 else 0

    cummax = returns.cummax()
    drawdown = (returns - cummax) / cummax * 100
    max_drawdown = drawdown.min()

    # SPY metrics
    spy_returns = pd.Series(spy_benchmark['value_history'], index=spy_benchmark['date_history'])
    spy_final = spy_returns.iloc[-1]
    spy_return = ((spy_final - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100

    alpha = total_return - spy_return

    return {
        'name': weight_name,
        'weights': weights,
        'final_value': final_value,
        'total_return': total_return,
        'annual_return': annual_return,
        'sharpe': sharpe,
        'max_drawdown': max_drawdown,
        'alpha': alpha,
        'spy_return': spy_return
    }


def main():
    parser = argparse.ArgumentParser(description='Test different scoring weights')
    parser.add_argument('--start', type=str, default='2025-04-05', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, default='2025-09-01', help='End date (YYYY-MM-DD)')
    parser.add_argument('--top', type=int, default=3, choices=[3, 5], help='Top N sectors')
    args = parser.parse_args()

    start_date = datetime.strptime(args.start, '%Y-%m-%d')
    end_date = datetime.strptime(args.end, '%Y-%m-%d')

    print("="*80)
    print("TESTING DIFFERENT SCORING WEIGHTS")
    print("="*80)
    print(f"Period: {args.start} to {args.end}")
    print(f"Top {args.top} sectors")
    print(f"Transaction costs: {TRANSACTION_COST_PCT*100:.2f}%")
    print()

    # Run backtests for each weight scenario
    results = []

    for scenario_name, weights in WEIGHT_SCENARIOS.items():
        print(f"\nTesting: {scenario_name}")
        print(f"  Weights: RS20={weights['rs_20d']*100:.0f}% RS60={weights['rs_60d']*100:.0f}% " +
              f"MOM={weights['momentum']*100:.0f}% RET20={weights['return_20d']*100:.0f}%")

        result = run_backtest(weights, scenario_name, start_date, end_date, args.top)
        if result:
            results.append(result)
            print(f"  Return: {result['total_return']:+.2f}% | Alpha: {result['alpha']:+.2f}% | Sharpe: {result['sharpe']:.2f}")

    # Display results
    print("\n" + "="*80)
    print("RESULTS COMPARISON")
    print("="*80)

    print(f"\n{'Strategy':<30} {'Return':<12} {'Alpha':<12} {'Sharpe':<10} {'Max DD':<10}")
    print("-"*80)

    # Sort by total return
    results.sort(key=lambda x: x['total_return'], reverse=True)

    for result in results:
        print(f"{result['name']:<30} {result['total_return']:>10.2f}% {result['alpha']:>10.2f}% " +
              f"{result['sharpe']:>8.2f} {result['max_drawdown']:>8.2f}%")

    # Best strategy
    if results:
        best = results[0]
        print("\n" + "="*80)
        print("RECOMMENDED WEIGHTS")
        print("="*80)
        print(f"\nBest Strategy: {best['name']}")
        print(f"  Return: {best['total_return']:+.2f}%")
        print(f"  Alpha vs SPY: {best['alpha']:+.2f}%")
        print(f"  SPY Return: {best['spy_return']:.2f}%")
        print(f"\nOptimal Weights:")
        for metric, weight in best['weights'].items():
            print(f"  {metric:<15} {weight*100:>5.1f}%")

        print(f"\nImprovement vs Current (Equal Weight):")
        current = next((r for r in results if r['name'] == 'Equal Weight (Current)'), None)
        if current:
            improvement = best['total_return'] - current['total_return']
            print(f"  Return Improvement: {improvement:+.2f}%")
            print(f"  Alpha Improvement: {(best['alpha'] - current['alpha']):+.2f}%")


if __name__ == "__main__":
    main()
