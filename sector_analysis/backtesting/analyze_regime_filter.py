"""
Analyze when regime filter triggered and its impact
"""

import yfinance as yf
import pandas as pd
from datetime import datetime

START = '2025-04-05'
END = '2025-09-01'

print("="*80)
print("REGIME FILTER ANALYSIS")
print("="*80)
print(f"Period: {START} to {END}\n")

# Fetch SPY data with extra for MA calculation
spy = yf.Ticker('SPY')
spy_data = spy.history(start='2024-06-01', end=END)

# Calculate 200-day MA
spy_data['MA200'] = spy_data['Close'].rolling(window=200).mean()

# Focus on backtest period
backtest_period = spy_data.loc[START:END].copy()
backtest_period['Below_MA'] = backtest_period['Close'] < backtest_period['MA200']
backtest_period['Return'] = backtest_period['Close'].pct_change()

# Summary
total_days = len(backtest_period)
below_ma_days = backtest_period['Below_MA'].sum()
above_ma_days = total_days - below_ma_days

print(f"Total Trading Days: {total_days}")
print(f"Days SPY < 200-day MA: {below_ma_days} ({below_ma_days/total_days*100:.1f}%)")
print(f"Days SPY > 200-day MA: {above_ma_days} ({above_ma_days/total_days*100:.1f}%)")
print()

# When filter triggered
below_periods = backtest_period[backtest_period['Below_MA']].copy()

if len(below_periods) > 0:
    print("="*80)
    print("WHEN REGIME FILTER TRIGGERED (50% Cash)")
    print("="*80)
    print(f"\n{'Date':<15} {'SPY Price':<12} {'200-day MA':<12} {'Daily Return':<12}")
    print("-"*60)

    for date, row in below_periods.iterrows():
        date_str = date.strftime('%Y-%m-%d')
        price = row['Close']
        ma = row['MA200']
        ret = row['Return'] * 100 if pd.notna(row['Return']) else 0
        print(f"{date_str:<15} ${price:>9.2f} ${ma:>10.2f} {ret:>10.2f}%")

    # Calculate what you missed
    print("\n" + "="*80)
    print("IMPACT OF BEING 50% CASH")
    print("="*80)

    # Returns on days below MA
    below_returns = below_periods['Return'].dropna()
    cumulative_return_below = (1 + below_returns).prod() - 1

    print(f"\nCumulative return during 'below MA' days: {cumulative_return_below*100:+.2f}%")
    print(f"Your exposure: 50% (half in cash)")
    print(f"Actual return captured: {cumulative_return_below*0.5*100:+.2f}%")
    print(f"Opportunity cost: {cumulative_return_below*0.5*100:+.2f}%")

    # If it was a rally during those days
    if cumulative_return_below > 0:
        print(f"\n⚠️  SPY RALLIED during the 'bear market' signal!")
        print(f"   The regime filter forced you to 50% cash during gains")
        print(f"   This is why you underperformed")
    else:
        print(f"\n✅ SPY FELL during the 'bear market' signal")
        print(f"   The regime filter protected you from losses")

else:
    print("✅ SPY was ALWAYS above 200-day MA")
    print("   Regime filter never triggered")

# Overall period performance
overall_return = (backtest_period['Close'].iloc[-1] / backtest_period['Close'].iloc[0] - 1) * 100

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print(f"\nSPY Total Return: {overall_return:.2f}%")
print(f"Regime Filter Days: {below_ma_days}/{total_days}")

if below_ma_days > 0:
    avg_return_below = below_returns.mean() * 100
    print(f"\nAverage daily return when below MA: {avg_return_below:+.2f}%")

    if avg_return_below > 0:
        print(f"\n❌ REGIME FILTER HURT PERFORMANCE")
        print(f"   Market rallied while filter signaled 'bear market'")
        print(f"   Being 50% cash caused you to miss gains")
        print(f"\n   Recommendation: Don't use regime filter in strong bull markets")
    else:
        print(f"\n✅ REGIME FILTER HELPED")
        print(f"   Protected from losses during weak periods")
else:
    print(f"\n⚠️  REGIME FILTER DID NOTHING")
    print(f"   SPY always above 200-day MA = always 100% invested")
    print(f"   Regime strategy = Same as base strategy")

# Show the transition points
print("\n" + "="*80)
print("MA CROSSOVER POINTS")
print("="*80)

# Find where it crosses
backtest_period['Crossed'] = backtest_period['Below_MA'] != backtest_period['Below_MA'].shift(1)
crossovers = backtest_period[backtest_period['Crossed']]

if len(crossovers) > 0:
    print(f"\n{'Date':<15} {'Event':<25} {'SPY Price':<12} {'200-day MA':<12}")
    print("-"*70)
    for date, row in crossovers.iterrows():
        date_str = date.strftime('%Y-%m-%d')
        event = "➡️  Below MA (50% cash)" if row['Below_MA'] else "⬆️  Above MA (100% invested)"
        price = row['Close']
        ma = row['MA200']
        print(f"{date_str:<15} {event:<25} ${price:>9.2f} ${ma:>10.2f}")
else:
    print("\nNo crossovers - SPY stayed on same side of MA entire period")
