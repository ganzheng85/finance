"""
Backtest: Top 3 Sector Rotation with Risk Management Strategies

Comparing:
1. Base Strategy: Always invested, weekly rotation
2. Portfolio Trailing Stop: -15% and -25% stops from peak
3. Market Regime Filter: SPY above/below 200-day MA
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
LOOKBACK_MONTHS = 6
TOP_N_SECTORS = 3
EQUAL_WEIGHT = 1/3
INITIAL_CAPITAL = 100000
TRANSACTION_COST_PCT = 0.001

# Risk management parameters
TRAILING_STOP_15 = 0.15  # -15% from peak
TRAILING_STOP_25 = 0.25  # -25% from peak

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
print("RISK MANAGEMENT STRATEGY COMPARISON")
print("="*80)
print(f"\nComparing 4 Strategies:")
print(f"  1. Base: Always invested in top 3 sectors")
print(f"  2. 15% Trailing Stop: Go 50% cash if down -15% from peak")
print(f"  3. 25% Hard Stop: Go 100% cash if down -25% from peak")
print(f"  4. Market Regime: 50% cash when SPY < 200-day MA")
print(f"\nInitial Capital: ${INITIAL_CAPITAL:,.0f}")
print(f"Transaction Cost: {TRANSACTION_COST_PCT*100:.2f}%")

# Calculate date range
end_date = datetime.now()
start_date = end_date - timedelta(days=LOOKBACK_MONTHS * 30 + 365)

print(f"\nFetching data from {start_date.date()} to {end_date.date()}...")

# Fetch data
all_tickers = list(SECTOR_ETFS.keys()) + ['SPY']
sector_data = {}

for ticker in all_tickers:
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date)
        if not data.empty:
            sector_data[ticker] = data['Close']
            print(f"  {ticker}: {len(data)} days")
    except Exception as e:
        print(f"  {ticker}: ERROR - {str(e)}")

df_prices = pd.DataFrame(sector_data)
df_prices = df_prices.dropna()
df_prices.index = df_prices.index.tz_localize(None)

print(f"\n[OK] Fetched {len(df_prices)} days of data")

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

# Calculate SPY 200-day MA
df_prices['SPY_MA200'] = df_prices['SPY'].rolling(window=200).mean()

# Get rebalancing dates
backtest_start = end_date - timedelta(days=LOOKBACK_MONTHS * 30)
all_dates = df_prices.index[df_prices.index >= backtest_start]

rebal_dates = []
for date in all_dates:
    week_num = date.isocalendar()[1]
    next_day = date + timedelta(days=1)
    if next_day not in all_dates or next_day.isocalendar()[1] != week_num:
        rebal_dates.append(date)

print(f"[OK] Identified {len(rebal_dates)} weekly rebalancing dates")

# Initialize portfolios for each strategy
portfolios = {
    'Base': {
        'cash': INITIAL_CAPITAL,
        'positions': {},
        'value_history': [],
        'date_history': [],
        'peak_value': INITIAL_CAPITAL,
        'cash_pct': 0.0,  # Always 0% cash
        'trades': []
    },
    'Trailing_15': {
        'cash': INITIAL_CAPITAL,
        'positions': {},
        'value_history': [],
        'date_history': [],
        'peak_value': INITIAL_CAPITAL,
        'cash_pct': 0.0,
        'trades': []
    },
    'Hard_25': {
        'cash': INITIAL_CAPITAL,
        'positions': {},
        'value_history': [],
        'date_history': [],
        'peak_value': INITIAL_CAPITAL,
        'cash_pct': 0.0,
        'trades': []
    },
    'Market_Regime': {
        'cash': INITIAL_CAPITAL,
        'positions': {},
        'value_history': [],
        'date_history': [],
        'peak_value': INITIAL_CAPITAL,
        'cash_pct': 0.0,
        'trades': []
    }
}

spy_benchmark = {
    'shares': INITIAL_CAPITAL / df_prices.loc[rebal_dates[0], 'SPY'],
    'value_history': [],
    'date_history': []
}

print(f"[OK] Initialized 4 portfolios + SPY benchmark\n")

print("="*80)
print("RUNNING BACKTEST...")
print("="*80)

# Run backtest
for i, rebal_date in enumerate(rebal_dates):
    # Get historical data
    historical_data = sector_df[sector_df['date'] <= rebal_date].copy()

    # Calculate metrics and rank
    historical_data = calculate_relative_strength(historical_data)
    historical_data = calculate_momentum(historical_data)
    sector_only = historical_data[historical_data['ticker'] != 'SPY'].copy()
    rankings = rank_sectors(sector_only)

    # Get top 3 sectors
    top_sectors = rankings.head(TOP_N_SECTORS)['ticker'].tolist()

    # Check market regime (SPY vs 200-day MA)
    spy_price = df_prices.loc[rebal_date, 'SPY']
    spy_ma200 = df_prices.loc[rebal_date, 'SPY_MA200']
    bull_market = spy_price > spy_ma200 if not pd.isna(spy_ma200) else True

    # Process each strategy
    for strategy_name, portfolio in portfolios.items():
        # Calculate current portfolio value
        portfolio_value = portfolio['cash']
        for ticker, shares in portfolio['positions'].items():
            if ticker in df_prices.columns:
                portfolio_value += shares * df_prices.loc[rebal_date, ticker]

        # Update peak value
        if portfolio_value > portfolio['peak_value']:
            portfolio['peak_value'] = portfolio_value

        # Calculate drawdown from peak
        drawdown = (portfolio_value - portfolio['peak_value']) / portfolio['peak_value']

        # Determine cash allocation based on strategy
        if strategy_name == 'Base':
            # Always fully invested
            target_cash_pct = 0.0

        elif strategy_name == 'Trailing_15':
            # -15% trailing stop: go 50% cash
            if drawdown <= -TRAILING_STOP_15:
                target_cash_pct = 0.50
            else:
                # Reset to fully invested when recovered to within -10%
                if drawdown >= -0.10:
                    target_cash_pct = 0.0
                else:
                    target_cash_pct = portfolio['cash_pct']  # Maintain current state

        elif strategy_name == 'Hard_25':
            # -25% hard stop: go 100% cash
            if drawdown <= -TRAILING_STOP_25:
                target_cash_pct = 1.0
            else:
                # Reset to fully invested when recovered to within -10%
                if drawdown >= -0.10:
                    target_cash_pct = 0.0
                else:
                    target_cash_pct = portfolio['cash_pct']

        elif strategy_name == 'Market_Regime':
            # 50% cash in bear market (SPY < 200 MA)
            if not bull_market:
                target_cash_pct = 0.50
            else:
                target_cash_pct = 0.0

        portfolio['cash_pct'] = target_cash_pct

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

                portfolio['trades'].append({
                    'date': rebal_date,
                    'action': 'SELL',
                    'ticker': ticker,
                    'shares': shares,
                    'price': price,
                    'value': proceeds,
                    'cost': cost
                })

        portfolio['positions'] = {}

        # Calculate amount to invest (after keeping target cash %)
        cash_to_invest = portfolio['cash'] * (1 - target_cash_pct)

        if cash_to_invest > 0:
            # Buy top 3 sectors with equal weight
            target_value_per_sector = cash_to_invest * EQUAL_WEIGHT

            for ticker in top_sectors:
                price = df_prices.loc[rebal_date, ticker]
                shares_to_buy = target_value_per_sector / price

                portfolio['positions'][ticker] = shares_to_buy

                portfolio['trades'].append({
                    'date': rebal_date,
                    'action': 'BUY',
                    'ticker': ticker,
                    'shares': shares_to_buy,
                    'price': price,
                    'value': target_value_per_sector,
                    'cost': target_value_per_sector * TRANSACTION_COST_PCT
                })

            # Deduct invested amount and transaction costs
            total_transaction_costs = cash_to_invest * TRANSACTION_COST_PCT
            portfolio['cash'] = portfolio['cash'] * target_cash_pct  # Keep target cash %

    # SPY benchmark
    spy_value = spy_benchmark['shares'] * df_prices.loc[rebal_date, 'SPY']
    spy_benchmark['value_history'].append(spy_value)
    spy_benchmark['date_history'].append(rebal_date)

    # Progress update
    if i % 5 == 0 or i == len(rebal_dates) - 1:
        pct_complete = (i + 1) / len(rebal_dates) * 100
        print(f"  Week {i+1}/{len(rebal_dates)} ({pct_complete:.0f}%) - {rebal_date.date()}")
        print(f"    Base: ${portfolios['Base']['value_history'][-1]:,.0f} | "
              f"15% Stop: ${portfolios['Trailing_15']['value_history'][-1]:,.0f} | "
              f"25% Stop: ${portfolios['Hard_25']['value_history'][-1]:,.0f} | "
              f"Regime: ${portfolios['Market_Regime']['value_history'][-1]:,.0f}")
        if strategy_name == 'Market_Regime':
            print(f"    Market: {'BULL' if bull_market else 'BEAR'} (SPY: ${spy_price:.2f}, MA200: ${spy_ma200:.2f})")

print("\n[OK] Backtest complete!")

# Calculate performance metrics
results = {}

for strategy_name, portfolio in portfolios.items():
    returns = pd.Series(portfolio['value_history'], index=portfolio['date_history'])
    final_value = returns.iloc[-1]
    total_return = ((final_value - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100

    # Calculate annualized metrics
    days_elapsed = (rebal_dates[-1] - rebal_dates[0]).days
    years_elapsed = days_elapsed / 365.25
    annual_return = ((final_value / INITIAL_CAPITAL) ** (1/years_elapsed) - 1) * 100

    # Volatility
    daily_returns = returns.pct_change().dropna()
    volatility = daily_returns.std() * np.sqrt(252) * 100

    # Sharpe ratio
    sharpe = annual_return / volatility if volatility > 0 else 0

    # Max drawdown
    cummax = returns.cummax()
    drawdown = (returns - cummax) / cummax * 100
    max_drawdown = drawdown.min()

    # Trade count and costs
    total_trades = len(portfolio['trades'])
    total_costs = sum(trade['cost'] for trade in portfolio['trades'])

    # Time in cash
    avg_cash_pct = np.mean([
        (p['cash'] / p['value_history'][i] if i < len(p['value_history']) else 0)
        for i, p in enumerate([portfolio] * len(portfolio['date_history']))
    ]) * 100

    results[strategy_name] = {
        'final_value': final_value,
        'total_return': total_return,
        'annual_return': annual_return,
        'volatility': volatility,
        'sharpe': sharpe,
        'max_drawdown': max_drawdown,
        'total_trades': total_trades,
        'total_costs': total_costs
    }

# SPY benchmark
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
    'max_drawdown': spy_max_dd,
    'total_trades': 0,
    'total_costs': 0
}

# Print results
print("\n" + "="*80)
print("BACKTEST RESULTS")
print("="*80)

print(f"\nPeriod: {rebal_dates[0].date()} to {rebal_dates[-1].date()} ({days_elapsed} days)")

print(f"\n{'='*80}")
print("PERFORMANCE COMPARISON")
print(f"{'='*80}")

print(f"\n{'Strategy':<20} {'Final Value':<15} {'Return':<10} {'Annual':<10} {'Sharpe':<10} {'Max DD':<10}")
print("-"*85)

for strategy in ['Base', 'Trailing_15', 'Hard_25', 'Market_Regime', 'SPY']:
    r = results[strategy]
    name = strategy.replace('_', ' ')
    print(f"{name:<20} ${r['final_value']:>13,.2f} {r['total_return']:>8.2f}% {r['annual_return']:>8.2f}% {r['sharpe']:>8.2f} {r['max_drawdown']:>8.2f}%")

print(f"\n{'='*80}")
print("RISK METRICS")
print(f"{'='*80}")

print(f"\n{'Strategy':<20} {'Volatility':<12} {'Trades':<10} {'Costs':<12} {'Alpha vs SPY':<12}")
print("-"*85)

for strategy in ['Base', 'Trailing_15', 'Hard_25', 'Market_Regime']:
    r = results[strategy]
    alpha = r['total_return'] - results['SPY']['total_return']
    name = strategy.replace('_', ' ')
    print(f"{name:<20} {r['volatility']:>10.2f}% {r['total_trades']:>8} ${r['total_costs']:>10,.2f} {alpha:>10.2f}%")

print(f"\n{'='*80}")
print("WINNER ANALYSIS")
print(f"{'='*80}")

# Rank by return
strategies_by_return = sorted(
    [(s, results[s]['total_return']) for s in ['Base', 'Trailing_15', 'Hard_25', 'Market_Regime']],
    key=lambda x: x[1],
    reverse=True
)

print(f"\nRanking by Total Return:")
for rank, (strategy, ret) in enumerate(strategies_by_return, 1):
    medal = "[1st]" if rank == 1 else "[2nd]" if rank == 2 else "[3rd]" if rank == 3 else "[4th]"
    name = strategy.replace('_', ' ')
    alpha = ret - results['SPY']['total_return']
    print(f"  {rank}. {medal} {name:<20} {ret:>8.2f}% (Alpha: {alpha:+.2f}%)")

# Rank by Sharpe
strategies_by_sharpe = sorted(
    [(s, results[s]['sharpe']) for s in ['Base', 'Trailing_15', 'Hard_25', 'Market_Regime']],
    key=lambda x: x[1],
    reverse=True
)

print(f"\nRanking by Sharpe Ratio (Risk-Adjusted):")
for rank, (strategy, sharpe) in enumerate(strategies_by_sharpe, 1):
    medal = "[1st]" if rank == 1 else "[2nd]" if rank == 2 else "[3rd]" if rank == 3 else "[4th]"
    name = strategy.replace('_', ' ')
    print(f"  {rank}. {medal} {name:<20} {sharpe:>8.2f}")

# Rank by max drawdown (least negative = best)
strategies_by_dd = sorted(
    [(s, results[s]['max_drawdown']) for s in ['Base', 'Trailing_15', 'Hard_25', 'Market_Regime']],
    key=lambda x: x[1],
    reverse=True
)

print(f"\nRanking by Drawdown Protection (Lower = Better):")
for rank, (strategy, dd) in enumerate(strategies_by_dd, 1):
    medal = "[1st]" if rank == 1 else "[2nd]" if rank == 2 else "[3rd]" if rank == 3 else "[4th]"
    name = strategy.replace('_', ' ')
    print(f"  {rank}. {medal} {name:<20} {dd:>8.2f}%")

print(f"\n{'='*80}")
print("RECOMMENDATION")
print(f"{'='*80}")

best_return_strat = strategies_by_return[0][0].replace('_', ' ')
best_sharpe_strat = strategies_by_sharpe[0][0].replace('_', ' ')
best_dd_strat = strategies_by_dd[0][0].replace('_', ' ')

print(f"\nBest Total Return: {best_return_strat}")
print(f"Best Risk-Adjusted: {best_sharpe_strat}")
print(f"Best Drawdown Protection: {best_dd_strat}")

# Save results
results_dir = Path(__file__).parent / 'results'
results_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Save comparison CSV
comparison_df = pd.DataFrame({
    'date': rebal_dates,
    'base_value': portfolios['Base']['value_history'],
    'trailing_15_value': portfolios['Trailing_15']['value_history'],
    'hard_25_value': portfolios['Hard_25']['value_history'],
    'market_regime_value': portfolios['Market_Regime']['value_history'],
    'spy_value': spy_benchmark['value_history']
})
comparison_file = results_dir / f'risk_mgmt_comparison_{timestamp}.csv'
comparison_df.to_csv(comparison_file, index=False)
print(f"\n[OK] Comparison results saved to: {comparison_file}")

# Save summary
summary_file = results_dir / f'risk_mgmt_summary_{timestamp}.txt'
with open(summary_file, 'w') as f:
    f.write("RISK MANAGEMENT STRATEGY COMPARISON\n")
    f.write("="*80 + "\n\n")
    f.write(f"Period: {rebal_dates[0].date()} to {rebal_dates[-1].date()}\n")
    f.write(f"Duration: {days_elapsed} days\n\n")

    for strategy in ['Base', 'Trailing_15', 'Hard_25', 'Market_Regime', 'SPY']:
        r = results[strategy]
        name = strategy.replace('_', ' ')
        f.write(f"\n{name}:\n")
        f.write(f"  Final Value: ${r['final_value']:,.2f}\n")
        f.write(f"  Total Return: {r['total_return']:.2f}%\n")
        f.write(f"  Annualized: {r['annual_return']:.2f}%\n")
        f.write(f"  Sharpe Ratio: {r['sharpe']:.2f}\n")
        f.write(f"  Max Drawdown: {r['max_drawdown']:.2f}%\n")
        f.write(f"  Volatility: {r['volatility']:.2f}%\n")
        if strategy != 'SPY':
            f.write(f"  Total Trades: {r['total_trades']}\n")
            f.write(f"  Transaction Costs: ${r['total_costs']:,.2f}\n")

print(f"[OK] Summary saved to: {summary_file}")

print(f"\n{'='*80}")
print("BACKTEST COMPLETE!")
print(f"{'='*80}")
