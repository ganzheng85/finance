"""
Diagnose why sector rotation underperformed in 2023 H1
"""

import pandas as pd
import yfinance as yf
from datetime import datetime
import numpy as np

START_DATE = '2023-01-01'
END_DATE = '2023-06-30'

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
    'SMH': 'Semiconductors',
    'IGV': 'Software'
}

print("="*80)
print("DIAGNOSING 2023 H1 PERFORMANCE")
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

sectors_only = {k: v for k, v in all_data.items() if k != 'SPY'}
sorted_sectors = sorted(sectors_only.items(), key=lambda x: x[1]['return'], reverse=True)

print(f"\n{'Rank':<6} {'Ticker':<8} {'Sector':<30} {'Return':<12} {'vs SPY':<12}")
print("-"*80)

spy_return = all_data['SPY']['return']

for i, (ticker, data) in enumerate(sorted_sectors, 1):
    vs_spy = data['return'] - spy_return
    beat_spy = "[BEAT SPY]" if vs_spy > 0 else ""
    print(f"{i:<6} {ticker:<8} {data['name']:<30} {data['return']:>10.2f}% {vs_spy:>10.2f}% {beat_spy}")

print("-"*80)
print(f"{'--':<6} {'SPY':<8} {'S&P 500 Benchmark':<30} {spy_return:>10.2f}% {0:>10.2f}%")

# Analyze what the strategy held
print("\n" + "="*80)
print("WHAT DID THE STRATEGY HOLD?")
print("="*80)

from pathlib import Path
results_dir = Path(__file__).parent / 'results'
backtest_files = list(results_dir.glob('backtest_top3_base_*20230101*20230630*.csv'))

if backtest_files:
    backtest_file = sorted(backtest_files)[-1]  # Get most recent
    print(f"\nReading: {backtest_file.name}")

    df = pd.read_csv(backtest_file)

    # Extract holdings over time
    all_holdings = []
    for holdings_str in df['holdings'].dropna():
        if holdings_str:
            tickers = holdings_str.split(',')
            all_holdings.extend(tickers)

    # Count how often each sector was held
    from collections import Counter
    holdings_count = Counter(all_holdings)
    total_weeks = len(df)

    print(f"\nSector Allocation (out of {total_weeks} weeks):")
    print(f"\n{'Ticker':<8} {'Sector':<30} {'Weeks Held':<12} {'% Time':<10} {'Return':<12}")
    print("-"*80)

    for ticker, count in holdings_count.most_common():
        pct_time = (count / total_weeks) * 100
        sector_return = all_data.get(ticker, {}).get('return', 0)
        print(f"{ticker:<8} {SECTOR_ETFS.get(ticker, 'Unknown'):<30} {count:<12} {pct_time:>8.1f}% {sector_return:>10.2f}%")

# Calculate top 3 vs actual holdings
print("\n" + "="*80)
print("TOP 3 PERFORMERS vs STRATEGY HOLDINGS")
print("="*80)

top3_tickers = [sorted_sectors[i][0] for i in range(min(3, len(sorted_sectors)))]
top3_returns = [sorted_sectors[i][1]['return'] for i in range(min(3, len(sorted_sectors)))]
top3_avg = sum(top3_returns) / len(top3_returns)

print(f"\nIf you held TOP 3 performers entire period:")
for i, (ticker, ret) in enumerate(zip(top3_tickers, top3_returns), 1):
    print(f"  {i}. {ticker} ({SECTOR_ETFS[ticker]}): {ret:.2f}%")

print(f"\n  Average (equal weight): {top3_avg:.2f}%")
print(f"  SPY: {spy_return:.2f}%")
print(f"  Outperformance: {top3_avg - spy_return:+.2f}%")

# What did strategy actually hold?
print(f"\nWhat strategy ACTUALLY held:")
print(f"  Most held sectors: {', '.join([f'{t} ({c} weeks)' for t, c in holdings_count.most_common(3)])}")

# Calculate weighted average return
if holdings_count:
    weighted_return = sum(all_data.get(ticker, {}).get('return', 0) * count
                         for ticker, count in holdings_count.items()) / sum(holdings_count.values())
    print(f"  Weighted average return: {weighted_return:.2f}%")
    print(f"  Strategy actual return: 13.12%")  # From backtest
    print(f"  SPY return: {spy_return:.2f}%")

# Analyze market concentration
print("\n" + "="*80)
print("MARKET ANALYSIS")
print("="*80)

# How many sectors beat SPY?
beat_spy_count = sum(1 for _, data in sectors_only.items() if data['return'] > spy_return)
total_sectors = len(sectors_only)

print(f"\nSectors that beat SPY: {beat_spy_count}/{total_sectors} ({beat_spy_count/total_sectors*100:.1f}%)")

if beat_spy_count < total_sectors * 0.3:
    print(f"\n[CONCENTRATED MARKET]")
    print(f"Only {beat_spy_count} sectors beat SPY - this was a concentrated market!")
    print(f"Sector rotation struggles when few sectors drive gains.")
else:
    print(f"\n[BROAD MARKET]")
    print(f"Many sectors beat SPY - sector rotation should work well.")

# Performance spread
returns_list = [data['return'] for _, data in sectors_only.items()]
max_return = max(returns_list)
min_return = min(returns_list)
median_return = sorted(returns_list)[len(returns_list)//2]

print(f"\nReturn Distribution:")
print(f"  Best sector: {max_return:.2f}%")
print(f"  Median sector: {median_return:.2f}%")
print(f"  Worst sector: {min_return:.2f}%")
print(f"  SPY: {spy_return:.2f}%")
print(f"  Spread: {max_return - min_return:.2f}%")

if median_return < spy_return:
    print(f"\n[ISSUE IDENTIFIED]: Median sector ({median_return:.2f}%) < SPY ({spy_return:.2f}%)")
    print(f"This means SPY's returns were driven by a few large-cap stocks,")
    print(f"not broad sector strength. Sector rotation struggles in this environment.")

# Check monthly returns
print("\n" + "="*80)
print("MONTHLY BREAKDOWN")
print("="*80)

spy_ticker = yf.Ticker('SPY')
spy_data = spy_ticker.history(start=START_DATE, end=END_DATE)
spy_data['Month'] = spy_data.index.to_period('M')

monthly_returns = spy_data.groupby('Month').apply(
    lambda x: ((x['Close'].iloc[-1] - x['Close'].iloc[0]) / x['Close'].iloc[0]) * 100
)

print(f"\nSPY Monthly Returns:")
for month, ret in monthly_returns.items():
    print(f"  {month}: {ret:+.2f}%")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)

print(f"""
Strategy Return: 13.12%
SPY Return: {spy_return:.2f}%
Underperformance: {13.12 - spy_return:.2f}%

WHY IT UNDERPERFORMED:
""")

# Check if strategy missed top performers
top3_set = set(top3_tickers)
held_set = set(holdings_count.keys())
missed = top3_set - held_set

if missed:
    print(f"1. MISSED TOP PERFORMERS: {', '.join(missed)}")
    for ticker in missed:
        ret = all_data[ticker]['return']
        print(f"   - {ticker} ({SECTOR_ETFS[ticker]}): {ret:.2f}%")

if median_return < spy_return:
    print(f"\n2. CONCENTRATED MARKET:")
    print(f"   - Only {beat_spy_count}/{total_sectors} sectors beat SPY")
    print(f"   - SPY driven by mega-cap stocks, not sector breadth")
    print(f"   - Equal-weight sector strategy can't capture this")

if holdings_count:
    # Check if strategy held laggards
    worst_held = min(holdings_count.keys(), key=lambda t: all_data.get(t, {}).get('return', 0))
    worst_return = all_data.get(worst_held, {}).get('return', 0)
    if worst_return < median_return:
        print(f"\n3. HELD LAGGARDS:")
        print(f"   - Held {worst_held} ({SECTOR_ETFS[worst_held]}): {worst_return:.2f}%")
        print(f"   - Below median sector return ({median_return:.2f}%)")

print(f"\nRECOMMENDATIONS:")
if median_return < spy_return:
    print("- 2023 H1 was a concentrated market (tech mega-caps)")
    print("- Sector rotation works better in rotational markets")
    print("- Consider market cap weighting vs equal sector weighting")
else:
    print("- Review sector selection algorithm")
    print("- Weekly rebalancing may cause whipsaw")
    print("- Test monthly rebalancing")
