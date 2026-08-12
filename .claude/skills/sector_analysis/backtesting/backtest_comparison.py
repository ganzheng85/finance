"""
Backtest Comparison: Top 3 vs Top 5 vs SPY
Compare sector rotation strategies with different concentration levels
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path to import sector analysis modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from calculate_sector_metrics import (
    calculate_relative_strength,
    calculate_momentum,
    rank_sectors
)

# Configuration
LOOKBACK_MONTHS = 6
REBALANCE_FREQUENCY = 'weekly'
INITIAL_CAPITAL = 100000
TRANSACTION_COST_PCT = 0.001  # 0.1%

# Sector ETFs
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
    'SMH': 'Semiconductors'
}

print("="*80)
print("SECTOR ROTATION COMPARISON BACKTEST")
print("="*80)
print(f"\nComparing 3 Strategies:")
print(f"  1. Top 3 Sectors (33.33% each)")
print(f"  2. Top 5 Sectors (20.00% each)")
print(f"  3. SPY Buy & Hold")
print(f"\nConfiguration:")
print(f"  Lookback Period: {LOOKBACK_MONTHS} months")
print(f"  Rebalancing: {REBALANCE_FREQUENCY}")
print(f"  Initial Capital: ${INITIAL_CAPITAL:,.0f}")
print(f"  Transaction Cost: {TRANSACTION_COST_PCT*100:.2f}%")

# Calculate date range
end_date = datetime.now()
start_date = end_date - timedelta(days=LOOKBACK_MONTHS * 30 + 365)

print(f"\nFetching data from {start_date.date()} to {end_date.date()}...")

# Fetch sector ETF data
all_tickers = list(SECTOR_ETFS.keys()) + ['SPY']
sector_data = {}

for ticker in all_tickers:
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date)
        if not data.empty:
            sector_data[ticker] = data['Close']
            print(f"  {ticker}: {len(data)} days")
        else:
            print(f"  {ticker}: NO DATA")
    except Exception as e:
        print(f"  {ticker}: ERROR - {str(e)}")

# Create DataFrame with all sector prices
df_prices = pd.DataFrame(sector_data)
df_prices = df_prices.dropna()
df_prices.index = df_prices.index.tz_localize(None)

print(f"\n[OK] Fetched {len(df_prices)} days of data for {len(all_tickers)} ETFs")

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

# Add SPY benchmark
spy_df = pd.DataFrame({
    'date': df_prices.index,
    'ticker': 'SPY',
    'sector_name': 'S&P 500',
    'adjusted_close': df_prices['SPY'].values
})
sector_df = pd.concat([sector_df, spy_df], ignore_index=True)

# Get rebalancing dates (weekly)
backtest_start = end_date - timedelta(days=LOOKBACK_MONTHS * 30)
all_dates = df_prices.index[df_prices.index >= backtest_start]

rebal_dates = []
for date in all_dates:
    week_num = date.isocalendar()[1]
    next_day = date + timedelta(days=1)
    if next_day not in all_dates or next_day.isocalendar()[1] != week_num:
        rebal_dates.append(date)

print(f"\n[OK] Identified {len(rebal_dates)} weekly rebalancing dates")

# Initialize portfolios
portfolios = {
    'Top 3': {
        'n_sectors': 3,
        'weight': 1/3,
        'cash': INITIAL_CAPITAL,
        'positions': {},
        'value_history': [],
        'date_history': [],
        'holdings_history': [],
        'trades': []
    },
    'Top 5': {
        'n_sectors': 5,
        'weight': 1/5,
        'cash': INITIAL_CAPITAL,
        'positions': {},
        'value_history': [],
        'date_history': [],
        'holdings_history': [],
        'trades': []
    },
    'SPY': {
        'shares': INITIAL_CAPITAL / df_prices.loc[rebal_dates[0], 'SPY'],
        'value_history': [],
        'date_history': []
    }
}

print(f"\n[OK] Initialized 3 portfolios with ${INITIAL_CAPITAL:,.0f} each")

print("\n" + "="*80)
print("RUNNING BACKTEST...")
print("="*80)

# Run backtest
for i, rebal_date in enumerate(rebal_dates):
    # Get data up to this date
    historical_data = sector_df[sector_df['date'] <= rebal_date].copy()

    # Calculate metrics
    historical_data = calculate_relative_strength(historical_data)
    historical_data = calculate_momentum(historical_data)

    # Rank sectors
    sector_only = historical_data[historical_data['ticker'] != 'SPY'].copy()
    rankings = rank_sectors(sector_only)

    # Process each sector rotation portfolio
    for strategy_name in ['Top 3', 'Top 5']:
        portfolio = portfolios[strategy_name]
        n_sectors = portfolio['n_sectors']
        weight = portfolio['weight']

        # Get top N sectors
        top_sectors = rankings.head(n_sectors)['ticker'].tolist()

        # Calculate current portfolio value
        portfolio_value = portfolio['cash']
        for ticker, shares in portfolio['positions'].items():
            if ticker in df_prices.columns:
                portfolio_value += shares * df_prices.loc[rebal_date, ticker]

        # Record values
        portfolio['value_history'].append(portfolio_value)
        portfolio['date_history'].append(rebal_date)
        portfolio['holdings_history'].append(top_sectors.copy())

        # Rebalance - liquidate everything to cash first
        for ticker in list(portfolio['positions'].keys()):
            shares = portfolio['positions'][ticker]
            if shares > 0:
                price = df_prices.loc[rebal_date, ticker]
                proceeds = shares * price
                cost = proceeds * TRANSACTION_COST_PCT
                portfolio['cash'] += proceeds - cost

                portfolio['trades'].append({
                    'date': rebal_date,
                    'action': 'SELL',
                    'ticker': ticker,
                    'shares': shares,
                    'price': price,
                    'value': proceeds,
                    'cost': cost
                })

        # Clear all positions
        portfolio['positions'] = {}

        # Buy top N sectors with equal weight
        target_value_per_sector = portfolio['cash'] * weight

        for ticker in top_sectors:
            price = df_prices.loc[rebal_date, ticker]
            shares_to_buy = target_value_per_sector / price
            cost_to_buy = target_value_per_sector
            transaction_cost = cost_to_buy * TRANSACTION_COST_PCT

            portfolio['positions'][ticker] = shares_to_buy

            portfolio['trades'].append({
                'date': rebal_date,
                'action': 'BUY',
                'ticker': ticker,
                'shares': shares_to_buy,
                'price': price,
                'value': cost_to_buy,
                'cost': transaction_cost
            })

        # Reset cash
        portfolio['cash'] = 0

    # SPY benchmark
    spy_value = portfolios['SPY']['shares'] * df_prices.loc[rebal_date, 'SPY']
    portfolios['SPY']['value_history'].append(spy_value)
    portfolios['SPY']['date_history'].append(rebal_date)

    # Progress update
    if i % 5 == 0 or i == len(rebal_dates) - 1:
        pct_complete = (i + 1) / len(rebal_dates) * 100
        top3_val = portfolios['Top 3']['value_history'][-1]
        top5_val = portfolios['Top 5']['value_history'][-1]
        print(f"  Week {i+1}/{len(rebal_dates)} ({pct_complete:.0f}%) - {rebal_date.date()}")
        print(f"    Top 3: ${top3_val:,.0f} | Top 5: ${top5_val:,.0f} | SPY: ${spy_value:,.0f}")

print("\n[OK] Backtest complete!")

# Calculate performance metrics
def calculate_metrics(values, dates, initial_capital):
    returns_series = pd.Series(values, index=dates)
    final_value = values[-1]
    total_return = ((final_value - initial_capital) / initial_capital) * 100

    days_elapsed = (dates[-1] - dates[0]).days
    years_elapsed = days_elapsed / 365.25
    annual_return = ((final_value / initial_capital) ** (1/years_elapsed) - 1) * 100

    daily_returns = returns_series.pct_change().dropna()
    volatility = daily_returns.std() * np.sqrt(252) * 100
    sharpe = annual_return / volatility if volatility > 0 else 0

    cummax = returns_series.cummax()
    drawdown = (returns_series - cummax) / cummax * 100
    max_drawdown = drawdown.min()

    return {
        'final_value': final_value,
        'total_return': total_return,
        'annual_return': annual_return,
        'volatility': volatility,
        'sharpe': sharpe,
        'max_drawdown': max_drawdown
    }

# Calculate metrics for all strategies
results = {}
for strategy in ['Top 3', 'Top 5', 'SPY']:
    portfolio = portfolios[strategy]
    values = portfolio['value_history']
    dates = portfolio['date_history']
    results[strategy] = calculate_metrics(values, dates, INITIAL_CAPITAL)

    if strategy != 'SPY':
        results[strategy]['total_trades'] = len(portfolio['trades'])
        results[strategy]['total_costs'] = sum(t['cost'] for t in portfolio['trades'])

# Print results
print("\n" + "="*80)
print("BACKTEST RESULTS")
print("="*80)

print(f"\nPeriod: {rebal_dates[0].date()} to {rebal_dates[-1].date()}")
print(f"Duration: {(rebal_dates[-1] - rebal_dates[0]).days} days ({(rebal_dates[-1] - rebal_dates[0]).days/365.25:.2f} years)")
print(f"Rebalancing Events: {len(rebal_dates)}")

print(f"\n{'='*80}")
print("PERFORMANCE COMPARISON")
print(f"{'='*80}")

print(f"\n{'Metric':<25} {'Top 3 Sectors':<18} {'Top 5 Sectors':<18} {'SPY Buy&Hold':<18}")
print("-"*80)

metrics_display = [
    ('Initial Capital', 'N/A', f"${INITIAL_CAPITAL:,.2f}"),
    ('Final Value', 'final_value', "${:,.2f}"),
    ('Total Return', 'total_return', "{:.2f}%"),
    ('Annualized Return', 'annual_return', "{:.2f}%"),
    ('Volatility (Annual)', 'volatility', "{:.2f}%"),
    ('Sharpe Ratio', 'sharpe', "{:.2f}"),
    ('Max Drawdown', 'max_drawdown', "{:.2f}%"),
]

# Print initial capital
print(f"{'Initial Capital':<25} ${INITIAL_CAPITAL:>16,.2f} ${INITIAL_CAPITAL:>16,.2f} ${INITIAL_CAPITAL:>16,.2f}")

# Print metrics
for label, metric_key, fmt in metrics_display[1:]:
    top3_val = results['Top 3'][metric_key]
    top5_val = results['Top 5'][metric_key]
    spy_val = results['SPY'][metric_key]

    print(f"{label:<25} {fmt.format(top3_val):>18} {fmt.format(top5_val):>18} {fmt.format(spy_val):>18}")

# Trading activity
print(f"\n{'Trading Activity':<25} {'Top 3 Sectors':<18} {'Top 5 Sectors':<18} {'SPY Buy&Hold':<18}")
print("-"*80)
print(f"{'Total Trades':<25} {results['Top 3']['total_trades']:>18} {results['Top 5']['total_trades']:>18} {'0':>18}")
print(f"{'Transaction Costs':<25} ${results['Top 3']['total_costs']:>16,.2f} ${results['Top 5']['total_costs']:>16,.2f} {'$0.00':>18}")

# Winner analysis
print(f"\n{'='*80}")
print("WINNER ANALYSIS")
print(f"{'='*80}")

strategies_ranked = sorted(
    [(name, results[name]['total_return']) for name in ['Top 3', 'Top 5', 'SPY']],
    key=lambda x: x[1],
    reverse=True
)

print(f"\nRanking by Total Return:")
for rank, (strategy, ret) in enumerate(strategies_ranked, 1):
    medal = "[1st]" if rank == 1 else "[2nd]" if rank == 2 else "[3rd]"
    print(f"  {rank}. {medal} {strategy:<15} {ret:>8.2f}%")

# Alpha calculations
top3_alpha = results['Top 3']['total_return'] - results['SPY']['total_return']
top5_alpha = results['Top 5']['total_return'] - results['SPY']['total_return']

print(f"\nAlpha vs SPY:")
print(f"  Top 3: {top3_alpha:+.2f}%")
print(f"  Top 5: {top5_alpha:+.2f}%")

# Risk-adjusted comparison
print(f"\nRisk-Adjusted Returns (Sharpe Ratio):")
for strategy in ['Top 3', 'Top 5', 'SPY']:
    sharpe = results[strategy]['sharpe']
    print(f"  {strategy:<15} {sharpe:.2f}")

# Best choice
best_return = strategies_ranked[0][0]
best_sharpe = max(['Top 3', 'Top 5', 'SPY'], key=lambda x: results[x]['sharpe'])
best_risk = max(['Top 3', 'Top 5', 'SPY'], key=lambda x: -results[x]['max_drawdown'])

print(f"\n{'='*80}")
print("RECOMMENDATION")
print(f"{'='*80}")

print(f"\nBest Total Return: {best_return} ({results[best_return]['total_return']:.2f}%)")
print(f"Best Risk-Adjusted: {best_sharpe} (Sharpe: {results[best_sharpe]['sharpe']:.2f})")
print(f"Best Risk Control: {best_risk} (Max DD: {results[best_risk]['max_drawdown']:.2f}%)")

# Save results
results_dir = Path(__file__).parent / 'results'
results_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
comparison_file = results_dir / f'comparison_results_{timestamp}.csv'

# Create comparison dataframe
comparison_df = pd.DataFrame({
    'date': portfolios['Top 3']['date_history'],
    'top3_value': portfolios['Top 3']['value_history'],
    'top5_value': portfolios['Top 5']['value_history'],
    'spy_value': portfolios['SPY']['value_history'],
    'top3_return': [(v - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100 for v in portfolios['Top 3']['value_history']],
    'top5_return': [(v - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100 for v in portfolios['Top 5']['value_history']],
    'spy_return': [(v - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100 for v in portfolios['SPY']['value_history']],
    'top3_alpha': [(t3 - spy) / INITIAL_CAPITAL * 100 for t3, spy in zip(portfolios['Top 3']['value_history'], portfolios['SPY']['value_history'])],
    'top5_alpha': [(t5 - spy) / INITIAL_CAPITAL * 100 for t5, spy in zip(portfolios['Top 5']['value_history'], portfolios['SPY']['value_history'])],
    'top3_holdings': [','.join(h) for h in portfolios['Top 3']['holdings_history']],
    'top5_holdings': [','.join(h) for h in portfolios['Top 5']['holdings_history']],
})

comparison_df.to_csv(comparison_file, index=False)
print(f"\n[OK] Comparison results saved to: {comparison_file}")

# Save summary
summary_file = results_dir / f'summary_{timestamp}.txt'
with open(summary_file, 'w') as f:
    f.write("SECTOR ROTATION STRATEGY COMPARISON\n")
    f.write("="*80 + "\n\n")
    f.write(f"Period: {rebal_dates[0].date()} to {rebal_dates[-1].date()}\n")
    f.write(f"Duration: {(rebal_dates[-1] - rebal_dates[0]).days} days\n\n")

    for strategy in ['Top 3', 'Top 5', 'SPY']:
        f.write(f"\n{strategy}:\n")
        f.write(f"  Final Value: ${results[strategy]['final_value']:,.2f}\n")
        f.write(f"  Total Return: {results[strategy]['total_return']:.2f}%\n")
        f.write(f"  Annualized: {results[strategy]['annual_return']:.2f}%\n")
        f.write(f"  Sharpe Ratio: {results[strategy]['sharpe']:.2f}\n")
        f.write(f"  Max Drawdown: {results[strategy]['max_drawdown']:.2f}%\n")
        if strategy != 'SPY':
            f.write(f"  Total Trades: {results[strategy]['total_trades']}\n")
            f.write(f"  Transaction Costs: ${results[strategy]['total_costs']:,.2f}\n")

print(f"[OK] Summary saved to: {summary_file}")

print(f"\n{'='*80}")
print("COMPARISON BACKTEST COMPLETE!")
print(f"{'='*80}")
