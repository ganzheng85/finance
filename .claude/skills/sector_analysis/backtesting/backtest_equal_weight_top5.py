"""
Backtest: Equal Weight Top 5 Sector Rotation Strategy
Weekly rebalancing to top 5 ranked sectors with 20% allocation each
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
REBALANCE_FREQUENCY = 'weekly'  # Weekly rebalancing
TOP_N_SECTORS = 5  # Top 5 sectors
EQUAL_WEIGHT = 0.20  # 20% each (1/5)
INITIAL_CAPITAL = 100000  # $100,000 starting capital
TRANSACTION_COST_PCT = 0.001  # 0.1% transaction cost (10 basis points)

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
print("SECTOR ROTATION BACKTEST - Equal Weight Top 5 Strategy")
print("="*80)
print(f"\nConfiguration:")
print(f"  Lookback Period: {LOOKBACK_MONTHS} months")
print(f"  Rebalancing: {REBALANCE_FREQUENCY}")
print(f"  Top N Sectors: {TOP_N_SECTORS}")
print(f"  Equal Weight: {EQUAL_WEIGHT*100:.0f}% each")
print(f"  Initial Capital: ${INITIAL_CAPITAL:,.0f}")
print(f"  Transaction Cost: {TRANSACTION_COST_PCT*100:.2f}%")

# Calculate date range
end_date = datetime.now()
start_date = end_date - timedelta(days=LOOKBACK_MONTHS * 30 + 365)  # Extra year for calculations

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

# Remove timezone information for easier comparisons
df_prices.index = df_prices.index.tz_localize(None)

print(f"\n[OK] Fetched {len(df_prices)} days of data for {len(all_tickers)} ETFs")

# Create sector dataframe in format expected by ranking functions
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

print(f"\n[OK] Prepared sector dataframe with {len(sector_df)} rows")

# Get rebalancing dates (weekly)
backtest_start = end_date - timedelta(days=LOOKBACK_MONTHS * 30)
all_dates = df_prices.index[df_prices.index >= backtest_start]

# Get weekly rebalancing dates (every Friday or last trading day of week)
rebal_dates = []
for date in all_dates:
    week_num = date.isocalendar()[1]
    year_num = date.year

    # Check if this is the last trading day of the week
    next_day = date + timedelta(days=1)
    if next_day not in all_dates or next_day.isocalendar()[1] != week_num:
        rebal_dates.append(date)

print(f"\n[OK] Identified {len(rebal_dates)} weekly rebalancing dates")

# Initialize portfolio
portfolio = {
    'cash': INITIAL_CAPITAL,
    'positions': {},  # ticker: shares
    'value_history': [],
    'date_history': [],
    'holdings_history': [],
    'trades': []
}

spy_benchmark = {
    'shares': INITIAL_CAPITAL / df_prices.loc[rebal_dates[0], 'SPY'],
    'value_history': [],
    'date_history': []
}

print(f"\n[OK] Initialized portfolio with ${INITIAL_CAPITAL:,.0f}")
print(f"[OK] SPY benchmark: {spy_benchmark['shares']:.2f} shares at ${df_prices.loc[rebal_dates[0], 'SPY']:.2f}")

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

    # Rank sectors (exclude SPY)
    sector_only = historical_data[historical_data['ticker'] != 'SPY'].copy()
    rankings = rank_sectors(sector_only)

    # Get top N sectors
    top_sectors = rankings.head(TOP_N_SECTORS)['ticker'].tolist()

    # Calculate current portfolio value
    portfolio_value = portfolio['cash']
    for ticker, shares in portfolio['positions'].items():
        if ticker in df_prices.columns:
            portfolio_value += shares * df_prices.loc[rebal_date, ticker]

    # Calculate SPY benchmark value
    spy_value = spy_benchmark['shares'] * df_prices.loc[rebal_date, 'SPY']

    # Record values
    portfolio['value_history'].append(portfolio_value)
    portfolio['date_history'].append(rebal_date)
    portfolio['holdings_history'].append(top_sectors.copy())

    spy_benchmark['value_history'].append(spy_value)
    spy_benchmark['date_history'].append(rebal_date)

    # Rebalance portfolio - liquidate everything to cash first
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

    # Clear all positions
    portfolio['positions'] = {}

    # Now buy top 5 sectors with equal weight
    target_value_per_sector = portfolio['cash'] * EQUAL_WEIGHT

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

    # Deduct all purchase costs from cash
    total_invested = portfolio['cash']
    total_transaction_costs = total_invested * TRANSACTION_COST_PCT
    portfolio['cash'] = 0  # All cash invested

    # Progress update
    if i % 5 == 0 or i == len(rebal_dates) - 1:
        pct_complete = (i + 1) / len(rebal_dates) * 100
        print(f"  Week {i+1}/{len(rebal_dates)} ({pct_complete:.0f}%) - {rebal_date.date()} - Value: ${portfolio_value:,.0f} - Holdings: {', '.join(top_sectors)}")

print("\n[OK] Backtest complete!")

# Calculate performance metrics
portfolio_returns = pd.Series(portfolio['value_history'], index=portfolio['date_history'])
spy_returns = pd.Series(spy_benchmark['value_history'], index=spy_benchmark['date_history'])

final_portfolio_value = portfolio_returns.iloc[-1]
final_spy_value = spy_returns.iloc[-1]

portfolio_return_pct = ((final_portfolio_value - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
spy_return_pct = ((final_spy_value - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
alpha = portfolio_return_pct - spy_return_pct

# Calculate annualized returns
days_elapsed = (rebal_dates[-1] - rebal_dates[0]).days
years_elapsed = days_elapsed / 365.25
portfolio_annual_return = ((final_portfolio_value / INITIAL_CAPITAL) ** (1/years_elapsed) - 1) * 100
spy_annual_return = ((final_spy_value / INITIAL_CAPITAL) ** (1/years_elapsed) - 1) * 100

# Calculate volatility
portfolio_daily_returns = portfolio_returns.pct_change().dropna()
spy_daily_returns = spy_returns.pct_change().dropna()

portfolio_volatility = portfolio_daily_returns.std() * np.sqrt(252) * 100  # Annualized
spy_volatility = spy_daily_returns.std() * np.sqrt(252) * 100

# Calculate Sharpe Ratio (assuming 0% risk-free rate for simplicity)
portfolio_sharpe = portfolio_annual_return / portfolio_volatility if portfolio_volatility > 0 else 0
spy_sharpe = spy_annual_return / spy_volatility if spy_volatility > 0 else 0

# Calculate max drawdown
portfolio_cummax = portfolio_returns.cummax()
portfolio_drawdown = (portfolio_returns - portfolio_cummax) / portfolio_cummax * 100
portfolio_max_drawdown = portfolio_drawdown.min()

spy_cummax = spy_returns.cummax()
spy_drawdown = (spy_returns - spy_cummax) / spy_cummax * 100
spy_max_drawdown = spy_drawdown.min()

# Count trades
total_trades = len(portfolio['trades'])
total_trade_cost = sum(trade['cost'] for trade in portfolio['trades'])

# Print results
print("\n" + "="*80)
print("BACKTEST RESULTS")
print("="*80)

print(f"\nPeriod: {rebal_dates[0].date()} to {rebal_dates[-1].date()} ({days_elapsed} days / {years_elapsed:.2f} years)")
print(f"Rebalancing Events: {len(rebal_dates)}")
print(f"Total Trades: {total_trades}")
print(f"Total Transaction Costs: ${total_trade_cost:,.2f}")

print(f"\n{'='*80}")
print("PERFORMANCE COMPARISON")
print(f"{'='*80}")

print(f"\n{'Metric':<30} {'Sector Rotation':<20} {'SPY Benchmark':<20} {'Difference':<15}")
print("-"*85)
print(f"{'Initial Capital':<30} ${INITIAL_CAPITAL:>18,.2f} ${INITIAL_CAPITAL:>18,.2f} ${0:>13,.2f}")
print(f"{'Final Value':<30} ${final_portfolio_value:>18,.2f} ${final_spy_value:>18,.2f} ${final_portfolio_value - final_spy_value:>13,.2f}")
print(f"{'Total Return':<30} {portfolio_return_pct:>17.2f}% {spy_return_pct:>17.2f}% {alpha:>12.2f}%")
print(f"{'Annualized Return':<30} {portfolio_annual_return:>17.2f}% {spy_annual_return:>17.2f}% {portfolio_annual_return - spy_annual_return:>12.2f}%")
print(f"{'Volatility (Annual)':<30} {portfolio_volatility:>17.2f}% {spy_volatility:>17.2f}% {portfolio_volatility - spy_volatility:>12.2f}%")
print(f"{'Sharpe Ratio':<30} {portfolio_sharpe:>18.2f} {spy_sharpe:>18.2f} {portfolio_sharpe - spy_sharpe:>13.2f}")
print(f"{'Max Drawdown':<30} {portfolio_max_drawdown:>17.2f}% {spy_max_drawdown:>17.2f}% {portfolio_max_drawdown - spy_max_drawdown:>12.2f}%")

if alpha > 0:
    print(f"\n[OUTPERFORMING] Strategy beat SPY by {alpha:.2f}%")
elif alpha < 0:
    print(f"\n[UNDERPERFORMING] Strategy trails SPY by {abs(alpha):.2f}%")
else:
    print(f"\n[MATCHING] Strategy matches SPY")

# Save results
results_dir = Path(__file__).parent / 'results'
results_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
results_file = results_dir / f'backtest_results_{timestamp}.csv'

# Create results dataframe
results_df = pd.DataFrame({
    'date': portfolio['date_history'],
    'portfolio_value': portfolio['value_history'],
    'spy_value': spy_benchmark['value_history'],
    'portfolio_return': [(v - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100 for v in portfolio['value_history']],
    'spy_return': [(v - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100 for v in spy_benchmark['value_history']],
    'alpha': [(pv - sv) / INITIAL_CAPITAL * 100 for pv, sv in zip(portfolio['value_history'], spy_benchmark['value_history'])],
    'holdings': [','.join(h) for h in portfolio['holdings_history']]
})

results_df.to_csv(results_file, index=False)
print(f"\n[OK] Results saved to: {results_file}")

# Save trade log
trades_file = results_dir / f'trade_log_{timestamp}.csv'
trades_df = pd.DataFrame(portfolio['trades'])
trades_df.to_csv(trades_file, index=False)
print(f"[OK] Trade log saved to: {trades_file}")

# Print final holdings
print(f"\n{'='*80}")
print("FINAL PORTFOLIO HOLDINGS")
print(f"{'='*80}")
print(f"\nAs of {rebal_dates[-1].date()}:")
print(f"\n{'Ticker':<10} {'Sector':<30} {'Shares':<15} {'Price':<12} {'Value':<15} {'Weight':<10}")
print("-"*92)

for ticker in sorted(portfolio['positions'].keys()):
    shares = portfolio['positions'][ticker]
    price = df_prices.loc[rebal_dates[-1], ticker]
    value = shares * price
    weight = (value / final_portfolio_value) * 100
    sector_name = SECTOR_ETFS.get(ticker, 'Unknown')
    print(f"{ticker:<10} {sector_name:<30} {shares:>14.2f} ${price:>10.2f} ${value:>13,.2f} {weight:>8.1f}%")

print("-"*92)
print(f"{'TOTAL':<10} {'':<30} {'':<15} {'':<12} ${final_portfolio_value:>13,.2f} {100.0:>8.1f}%")

print(f"\n{'='*80}")
print("BACKTEST COMPLETE!")
print(f"{'='*80}")
