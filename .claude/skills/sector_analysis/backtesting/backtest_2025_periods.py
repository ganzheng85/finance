"""
Backtest: Top 3 vs Top 5 vs SPY for 2025 Time Periods

Testing:
1. 2025 H1: January 1 - June 1, 2025
2. 2025 H2: June 1 - December 31, 2025
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from calculate_sector_metrics import (
    calculate_relative_strength,
    calculate_momentum,
    rank_sectors
)

# Configuration
TOP_N_OPTIONS = [3, 5]  # Test Top 3 and Top 5
INITIAL_CAPITAL = 100000
TRANSACTION_COST_PCT = 0.001

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

# Test periods
TEST_PERIODS = {
    '2025_H1': {
        'name': '2025 First Half',
        'start': datetime(2025, 1, 1),
        'end': datetime(2025, 6, 1),
        'description': 'January - June 2025'
    },
    '2025_H2': {
        'name': '2025 Second Half',
        'start': datetime(2025, 6, 1),
        'end': datetime(2025, 12, 31),
        'description': 'June - December 2025'
    }
}


def run_backtest_for_period(period_key, period_config):
    """Run backtest for a specific time period"""

    print("\n" + "="*80)
    print(f"TESTING: {period_config['name']}")
    print("="*80)
    print(f"Period: {period_config['start'].date()} to {period_config['end'].date()}")
    print(f"Description: {period_config['description']}")

    # Fetch data (extra for lookback calculations)
    start_date = period_config['start'] - timedelta(days=365)
    end_date = period_config['end']

    print(f"\nFetching data from {start_date.date()} to {end_date.date()}...")

    all_tickers = list(SECTOR_ETFS.keys()) + ['SPY']
    sector_data = {}

    for ticker in all_tickers:
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date)
            if not data.empty:
                sector_data[ticker] = data['Close']
        except Exception as e:
            print(f"  {ticker}: ERROR - {str(e)}")

    df_prices = pd.DataFrame(sector_data)
    df_prices = df_prices.dropna()
    df_prices.index = df_prices.index.tz_localize(None)

    print(f"[OK] Fetched {len(df_prices)} days of data")

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
    backtest_start = period_config['start']
    all_dates = df_prices.index[df_prices.index >= backtest_start]

    rebal_dates = []
    for date in all_dates:
        week_num = date.isocalendar()[1]
        next_day = date + timedelta(days=1)
        if next_day not in all_dates or next_day.isocalendar()[1] != week_num:
            rebal_dates.append(date)

    if not rebal_dates:
        print("[ERROR] No rebalancing dates found")
        return None

    print(f"[OK] {len(rebal_dates)} weekly rebalancing dates")

    # Initialize portfolios for Top 3, Top 5, and SPY
    portfolios = {}

    for top_n in TOP_N_OPTIONS:
        portfolios[f'Top_{top_n}'] = {
            'cash': INITIAL_CAPITAL,
            'positions': {},
            'value_history': [],
            'date_history': [],
            'trades': []
        }

    spy_benchmark = {
        'shares': INITIAL_CAPITAL / df_prices.loc[rebal_dates[0], 'SPY'],
        'value_history': [],
        'date_history': []
    }

    print("Running backtest...")

    # Suppress verbose output
    import io
    import contextlib

    # Run backtest
    for i, rebal_date in enumerate(rebal_dates):
        # Get historical data
        historical_data = sector_df[sector_df['date'] <= rebal_date].copy()

        # Calculate metrics and rank (suppress print statements)
        with contextlib.redirect_stdout(io.StringIO()):
            historical_data = calculate_relative_strength(historical_data)
            historical_data = calculate_momentum(historical_data)
            sector_only = historical_data[historical_data['ticker'] != 'SPY'].copy()
            rankings = rank_sectors(sector_only)

        # Process each portfolio
        for strategy_name, portfolio in portfolios.items():
            # Determine top N for this strategy
            top_n = int(strategy_name.split('_')[1])
            top_sectors = rankings.head(top_n)['ticker'].tolist()

            # Calculate current portfolio value
            portfolio_value = portfolio['cash']
            for ticker, shares in portfolio['positions'].items():
                if ticker in df_prices.columns:
                    portfolio_value += shares * df_prices.loc[rebal_date, ticker]

            # Record values
            portfolio['value_history'].append(portfolio_value)
            portfolio['date_history'].append(rebal_date)

            # Sell all current positions
            for ticker in list(portfolio['positions'].keys()):
                shares = portfolio['positions'][ticker]
                if shares > 0:
                    price = df_prices.loc[rebal_date, ticker]
                    proceeds = shares * price
                    cost = proceeds * TRANSACTION_COST_PCT
                    portfolio['cash'] += proceeds - cost

            portfolio['positions'] = {}

            # Buy top N sectors with equal weight
            equal_weight = 1.0 / top_n
            target_value_per_sector = portfolio['cash'] * equal_weight

            for ticker in top_sectors:
                price = df_prices.loc[rebal_date, ticker]
                shares_to_buy = target_value_per_sector / price
                portfolio['positions'][ticker] = shares_to_buy

            # Deduct transaction costs
            total_transaction_costs = portfolio['cash'] * TRANSACTION_COST_PCT
            portfolio['cash'] = 0  # All cash invested

        # SPY benchmark
        spy_value = spy_benchmark['shares'] * df_prices.loc[rebal_date, 'SPY']
        spy_benchmark['value_history'].append(spy_value)
        spy_benchmark['date_history'].append(rebal_date)

        # Progress indicator
        if i % 5 == 0 or i == len(rebal_dates) - 1:
            pct = (i + 1) / len(rebal_dates) * 100
            print(f"  Week {i+1}/{len(rebal_dates)} ({pct:.0f}%) - {rebal_date.date()}")

    print("[OK] Backtest complete!")

    # Calculate metrics
    results = {}

    for strategy_name, portfolio in portfolios.items():
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

        results[strategy_name] = {
            'final_value': final_value,
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe': sharpe,
            'max_drawdown': max_drawdown
        }

    # SPY
    spy_returns = pd.Series(spy_benchmark['value_history'], index=spy_benchmark['date_history'])
    spy_final = spy_returns.iloc[-1]
    spy_return = ((spy_final - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
    spy_annual = ((spy_final / INITIAL_CAPITAL) ** (1/years_elapsed) - 1) * 100
    spy_daily = spy_returns.pct_change().dropna()
    spy_vol = spy_daily.std() * np.sqrt(252) * 100
    spy_sharpe = spy_annual / spy_vol if spy_vol > 0 else 0
    spy_cummax = spy_returns.cummax()
    spy_dd = (spy_returns - spy_cummax) / spy_cummax * 100
    spy_max_dd = spy_dd.min()

    results['SPY'] = {
        'final_value': spy_final,
        'total_return': spy_return,
        'annual_return': spy_annual,
        'volatility': spy_vol,
        'sharpe': spy_sharpe,
        'max_drawdown': spy_max_dd
    }

    # Print summary
    print(f"\n{'Strategy':<20} {'Final Value':<15} {'Return':<10} {'Max DD':<10} {'Alpha':<10}")
    print("-"*70)
    for strategy in ['Top_3', 'Top_5', 'SPY']:
        r = results[strategy]
        alpha = r['total_return'] - results['SPY']['total_return'] if strategy != 'SPY' else 0
        name = strategy.replace('_', ' ')
        print(f"{name:<20} ${r['final_value']:>13,.2f} {r['total_return']:>8.2f}% {r['max_drawdown']:>8.2f}% {alpha:>8.2f}%")

    return {
        'period_name': period_config['name'],
        'description': period_config['description'],
        'start_date': period_config['start'],
        'end_date': period_config['end'],
        'results': results
    }


# Main execution
print("="*80)
print("2025 SECTOR ROTATION BACKTEST")
print("="*80)
print("\nTesting Top 3 vs Top 5 vs SPY for 2025 periods")

all_results = {}

for period_key, period_config in TEST_PERIODS.items():
    result = run_backtest_for_period(period_key, period_config)
    if result:
        all_results[period_key] = result

# Generate summary report
print("\n" + "="*80)
print("SUMMARY ACROSS ALL PERIODS")
print("="*80)

for period_key, result in all_results.items():
    print(f"\n{result['period_name']} ({result['description']})")
    print("-"*80)

    results = result['results']
    print(f"\n{'Strategy':<20} {'Return':<12} {'Sharpe':<10} {'Max DD':<12} {'Winner':<10}")
    print("-"*70)

    strategies = ['Top_3', 'Top_5', 'SPY']
    best_return = max(strategies, key=lambda s: results[s]['total_return'])

    for strategy in strategies:
        r = results[strategy]
        winner = "[WIN]" if strategy == best_return else ""
        name = strategy.replace('_', ' ')
        print(f"{name:<20} {r['total_return']:>10.2f}% {r['sharpe']:>8.2f} {r['max_drawdown']:>10.2f}% {winner:<10}")

# Overall winner
print("\n" + "="*80)
print("OVERALL WINNER ANALYSIS")
print("="*80)

strategy_wins = {'Top_3': 0, 'Top_5': 0, 'SPY': 0}
for period_key, result in all_results.items():
    results = result['results']
    best = max(['Top_3', 'Top_5', 'SPY'], key=lambda s: results[s]['total_return'])
    strategy_wins[best] += 1

print(f"\nWins by Strategy:")
for strategy, wins in strategy_wins.items():
    name = strategy.replace('_', ' ')
    print(f"  {name}: {wins}/{len(all_results)} periods")

overall_winner = max(strategy_wins.items(), key=lambda x: x[1])
print(f"\nOverall Winner: {overall_winner[0].replace('_', ' ')} ({overall_winner[1]}/{len(all_results)} periods)")

# Save results
results_dir = Path(__file__).parent / 'results'
results_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

summary_file = results_dir / f'2025_periods_summary_{timestamp}.txt'
with open(summary_file, 'w') as f:
    f.write("2025 SECTOR ROTATION BACKTEST SUMMARY\n")
    f.write("="*80 + "\n\n")

    for period_key, result in all_results.items():
        f.write(f"{result['period_name']} ({result['description']})\n")
        f.write("-"*80 + "\n")

        results = result['results']
        for strategy in ['Top_3', 'Top_5', 'SPY']:
            r = results[strategy]
            name = strategy.replace('_', ' ')
            f.write(f"\n{name}:\n")
            f.write(f"  Final Value: ${r['final_value']:,.2f}\n")
            f.write(f"  Total Return: {r['total_return']:.2f}%\n")
            f.write(f"  Annualized: {r['annual_return']:.2f}%\n")
            f.write(f"  Sharpe Ratio: {r['sharpe']:.2f}\n")
            f.write(f"  Max Drawdown: {r['max_drawdown']:.2f}%\n")
        f.write("\n\n")

    f.write(f"Overall Winner: {overall_winner[0].replace('_', ' ')}\n")

print(f"\n[OK] Summary saved to: {summary_file}")

print("\n" + "="*80)
print("BACKTEST COMPLETE!")
print("="*80)
