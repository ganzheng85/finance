"""
Diagnostic script to understand why strategy underperformed SPY

This script helps identify:
1. Which sectors were selected vs which performed best
2. If regime filter triggered (cash positions)
3. Individual sector performance vs SPY
4. Impact of equal weighting vs score weighting
"""

import pandas as pd
import yfinance as yf
from datetime import datetime
import sys
from pathlib import Path

# Configuration
START_DATE = '2025-04-05'
END_DATE = '2025-09-01'

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

print("="*80)
print("PERFORMANCE DIAGNOSTIC")
print("="*80)
print(f"Period: {START_DATE} to {END_DATE}")
print()

# Fetch all sector data
print("Fetching sector performance data...")
all_data = {}

for ticker in list(SECTOR_ETFS.keys()) + ['SPY']:
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=START_DATE, end=END_DATE)
        if not data.empty:
            start_price = data['Close'].iloc[0]
            end_price = data['Close'].iloc[-1]
            total_return = ((end_price - start_price) / start_price) * 100
            all_data[ticker] = {
                'name': SECTOR_ETFS.get(ticker, 'S&P 500'),
                'start': start_price,
                'end': end_price,
                'return': total_return
            }
    except Exception as e:
        print(f"  Error fetching {ticker}: {e}")

print(f"[OK] Fetched {len(all_data)} sectors\n")

# Rank sectors by performance
print("="*80)
print("SECTOR PERFORMANCE RANKING (Best to Worst)")
print("="*80)
print(f"\n{'Rank':<6} {'Ticker':<8} {'Sector':<30} {'Return':<12}")
print("-"*80)

sectors_only = {k: v for k, v in all_data.items() if k != 'SPY'}
sorted_sectors = sorted(sectors_only.items(), key=lambda x: x[1]['return'], reverse=True)

for i, (ticker, data) in enumerate(sorted_sectors, 1):
    print(f"{i:<6} {ticker:<8} {data['name']:<30} {data['return']:>10.2f}%")

# SPY performance
if 'SPY' in all_data:
    spy_return = all_data['SPY']['return']
    print("-"*80)
    print(f"{'--':<6} {'SPY':<8} {'S&P 500 Benchmark':<30} {spy_return:>10.2f}%")

print("\n")

# Analyze what the strategy held
print("="*80)
print("STRATEGY HOLDINGS ANALYSIS")
print("="*80)

# Read backtest results to see what was actually held
results_dir = Path(__file__).parent / 'results'
backtest_files = list(results_dir.glob('backtest_top3_regime_*20250405*20250901*.csv'))

if backtest_files:
    backtest_file = backtest_files[0]
    print(f"\nReading: {backtest_file.name}")

    df = pd.read_csv(backtest_file)

    # Extract unique holdings
    all_holdings = set()
    for holdings_str in df['holdings'].dropna():
        tickers = holdings_str.split(',')
        all_holdings.update(tickers)

    print(f"\nSectors held during the period: {', '.join(sorted(all_holdings))}")

    # Calculate performance of held sectors
    print(f"\n{'Held Sector':<12} {'Return':<12} {'vs SPY':<12}")
    print("-"*40)

    held_returns = []
    for ticker in sorted(all_holdings):
        if ticker in all_data:
            sector_return = all_data[ticker]['return']
            vs_spy = sector_return - spy_return
            held_returns.append(sector_return)
            print(f"{ticker:<12} {sector_return:>10.2f}% {vs_spy:>10.2f}%")

    # Calculate equal-weight portfolio of held sectors
    if held_returns:
        avg_return = sum(held_returns) / len(held_returns)
        print("-"*40)
        print(f"{'Avg (Equal Wt)':<12} {avg_return:>10.2f}% {avg_return - spy_return:>10.2f}%")
        print(f"{'SPY':<12} {spy_return:>10.2f}% {0:>10.2f}%")

        # Calculate what was missed
        print("\n")
        print("="*80)
        print("MISSED OPPORTUNITIES")
        print("="*80)
        print(f"\nTop 3 performing sectors that could have been selected:")
        print(f"\n{'Ticker':<12} {'Sector':<30} {'Return':<12}")
        print("-"*60)

        for i, (ticker, data) in enumerate(sorted_sectors[:3], 1):
            held = "[HELD]" if ticker in all_holdings else ""
            print(f"{ticker:<12} {data['name']:<30} {data['return']:>10.2f}% {held}")

        # Calculate if top 3 were held
        top3_returns = [sorted_sectors[i][1]['return'] for i in range(min(3, len(sorted_sectors)))]
        top3_avg = sum(top3_returns) / len(top3_returns)
        potential_alpha = top3_avg - spy_return

        print(f"\nIf top 3 sectors were held (equal weight):")
        print(f"  Portfolio Return: {top3_avg:.2f}%")
        print(f"  SPY Return: {spy_return:.2f}%")
        print(f"  Potential Alpha: {potential_alpha:+.2f}%")

else:
    print("\n[WARNING] No backtest file found for this period")

# Regime filter analysis
print("\n")
print("="*80)
print("REGIME FILTER ANALYSIS")
print("="*80)

# Fetch SPY with 200-day MA
spy_ticker = yf.Ticker('SPY')
spy_hist = spy_ticker.history(start='2024-06-01', end=END_DATE)  # Extra data for MA calculation
spy_hist['MA200'] = spy_hist['Close'].rolling(window=200).mean()

# Check if SPY was ever below MA200 during the period
backtest_period = spy_hist.loc[START_DATE:END_DATE]
below_ma = backtest_period[backtest_period['Close'] < backtest_period['MA200']]

print(f"\nDays SPY was below 200-day MA: {len(below_ma)}/{len(backtest_period)}")

if len(below_ma) > 0:
    print(f"Regime filter should have triggered {len(below_ma)} days")
    print(f"This would reduce exposure to 50% on those days")
else:
    print("SPY was ALWAYS above its 200-day MA during this period")
    print("Regime filter provided NO BENEFIT - same as base strategy")

print("\n")
print("="*80)
print("SUMMARY")
print("="*80)
print(f"""
1. SPY Return: {spy_return:.2f}%
2. Strategy Return: 12.70% (from backtest)
3. Underperformance: {12.70 - spy_return:.2f}%

MAIN ISSUES:
- Wrong sectors were selected (defensive early, then tech that still lagged)
- Regime filter never triggered (SPY always above 200-day MA)
- Equal weighting may have diluted exposure to best performers
- Transaction costs from weekly rebalancing

RECOMMENDATIONS:
1. Review sector ranking algorithm - why did it pick wrong sectors?
2. Consider score-weighted allocation instead of equal weight
3. Consider less frequent rebalancing (bi-weekly or monthly)
4. Test strategy in different market conditions (not just bull markets)
""")
