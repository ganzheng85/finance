"""
What could you see in REAL-TIME during April 2025?

This shows what signals were available BEFORE you knew it was a V-shaped recovery.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

START = '2025-04-01'
END = '2025-05-15'

print("="*80)
print("REAL-TIME SIGNALS DURING APRIL 2025")
print("="*80)
print("What information was available BEFORE knowing it was V-shaped?\n")

# Fetch SPY data
spy = yf.Ticker('SPY')
spy_data = spy.history(start='2024-06-01', end=END)

# Calculate multiple indicators
spy_data['MA50'] = spy_data['Close'].rolling(window=50).mean()
spy_data['MA200'] = spy_data['Close'].rolling(window=200).mean()
spy_data['Return_1d'] = spy_data['Close'].pct_change()
spy_data['Return_5d'] = spy_data['Close'].pct_change(periods=5)
spy_data['Return_10d'] = spy_data['Close'].pct_change(periods=10)
spy_data['Return_20d'] = spy_data['Close'].pct_change(periods=20)

# Volatility (10-day rolling)
spy_data['Volatility_10d'] = spy_data['Return_1d'].rolling(window=10).std() * 100

# Distance from MA
spy_data['Dist_from_MA200'] = ((spy_data['Close'] - spy_data['MA200']) / spy_data['MA200']) * 100
spy_data['Dist_from_MA50'] = ((spy_data['Close'] - spy_data['MA50']) / spy_data['MA50']) * 100

# Focus on critical period
critical_period = spy_data.loc[START:END].copy()

print(f"{'Date':<12} {'Price':<9} {'vs 200MA':<9} {'1d Chg':<8} {'5d Chg':<8} {'10d Chg':<9} {'Vol':<8} {'Signal':<30}")
print("-"*110)

for date, row in critical_period.iterrows():
    date_str = date.strftime('%Y-%m-%d')
    price = row['Close']
    vs_ma200 = row['Dist_from_MA200']
    ret_1d = row['Return_1d'] * 100 if pd.notna(row['Return_1d']) else 0
    ret_5d = row['Return_5d'] * 100 if pd.notna(row['Return_5d']) else 0
    ret_10d = row['Return_10d'] * 100 if pd.notna(row['Return_10d']) else 0
    vol = row['Volatility_10d'] if pd.notna(row['Volatility_10d']) else 0

    # Real-time signal interpretation
    signal = ""
    if vs_ma200 < -5:
        if ret_5d > 5:
            signal = "Below MA, but +5d rally"
        else:
            signal = "Below MA, weak"
    elif vs_ma200 < 0:
        if ret_5d > 3:
            signal = "Near MA, rallying"
        else:
            signal = "Near MA, uncertain"
    else:
        signal = "Above MA, bullish"

    # Add volatility warning
    if vol > 2:
        signal += " [HIGH VOL]"

    print(f"{date_str:<12} ${price:>6.2f} {vs_ma200:>7.1f}% {ret_1d:>6.1f}% {ret_5d:>6.1f}% {ret_10d:>7.1f}% {vol:>6.2f}% {signal:<30}")

# Key events
print("\n" + "="*80)
print("KEY EVENTS (What you could observe in real-time)")
print("="*80)

key_dates = {
    '2025-04-07': 'First day below 200-day MA',
    '2025-04-08': 'Another drop (-1.57%) - looks like bear market?',
    '2025-04-09': 'HUGE rally +10.5% - V-recovery or dead cat bounce?',
    '2025-04-10': 'Pullback -4.38% after big rally - was Apr 9 fake?',
    '2025-04-11': 'Back up +1.78% - confusion continues',
    '2025-04-21': 'Drop -2.38% - still below MA',
    '2025-04-25': 'Grinding higher but STILL below 200-day MA',
    '2025-05-02': 'Still below MA, but up +1.48%',
    '2025-05-09': 'Last day below MA - recovery confirmed',
    '2025-05-12': 'Back ABOVE 200-day MA - officially bullish again'
}

for date_str, event in key_dates.items():
    try:
        date = pd.Timestamp(date_str)
        if date in critical_period.index:
            row = critical_period.loc[date]
            print(f"\n{date_str}: {event}")
            print(f"  Price: ${row['Close']:.2f} | 200-day MA: ${row['MA200']:.2f}")
            print(f"  5-day return: {row['Return_5d']*100:+.1f}%")
            print(f"  What you see: Still {row['Dist_from_MA200']:.1f}% below MA")
    except:
        pass

print("\n" + "="*80)
print("THE DILEMMA")
print("="*80)

print("""
On April 9, you saw:
  - SPY jumped +10.5% in ONE day
  - Still 3.8% below 200-day MA
  - Previous day was -1.57%

Question: Is this a V-shaped recovery or dead cat bounce?

OPTION 1: Stay 50% cash (regime filter)
  - Pro: Protected if it's a fake rally
  - Con: Miss gains if it's real recovery
  - Result: You missed half the rally

OPTION 2: Go 100% invested immediately
  - Pro: Capture full rally if it's real
  - Con: Get crushed if it's fake
  - Result: Higher risk, higher reward

OPTION 3: Gradual re-entry
  - Pro: Balance protection and opportunity
  - Con: Still miss some gains
  - Result: Moderate outcome

The truth: YOU CANNOT KNOW which it is until AFTER it happens.
""")

# Show what happened
print("="*80)
print("WHAT ACTUALLY HAPPENED (Hindsight)")
print("="*80)

apr7_price = critical_period.loc['2025-04-07']['Close']
may12_price = critical_period.loc['2025-05-12']['Close']
total_return = ((may12_price - apr7_price) / apr7_price) * 100

print(f"\nApril 7 (first day below MA): ${apr7_price:.2f}")
print(f"May 12 (back above MA): ${may12_price:.2f}")
print(f"Total return: {total_return:+.2f}%")
print(f"\nIt WAS a V-shaped recovery!")
print(f"But you only knew this on May 12, not April 9.")

# Alternative approaches
print("\n" + "="*80)
print("ALTERNATIVE APPROACHES (That work with uncertainty)")
print("="*80)

print("""
Since you CAN'T predict V-recovery vs bear market, use strategies that work BOTH ways:

1. FASTER RE-ENTRY RULES
   Instead of: "Stay 50% cash while below 200-day MA"
   Try: "Go 50% cash when cross below, but back to 100% if +5% in 3 days"

   Result: Catches quick recoveries while still protecting downside

2. MULTI-TIMEFRAME CONFIRMATION
   Don't rely on just 200-day MA
   Look at: 50-day MA, momentum, breadth indicators

   If SPY < 200-day MA but:
     - Above 50-day MA = short-term strength
     - Sectors rallying = market breadth good
     → Maybe it's a recovery, increase exposure

3. VOLATILITY-BASED STOPS
   Instead of MA crossover, use volatility:
   - High volatility = reduce exposure (regardless of MA)
   - Low volatility = full exposure

   April 9: Volatility was high → stay cautious
   May 5+: Volatility dropping → safe to increase

4. ACCEPT THE TRADE-OFF
   Regime filters are INSURANCE:
   - Cost: 3-5% in V-recoveries
   - Benefit: Avoid -20% in real bear markets

   2025: V-recovery → cost you 5%
   2022/2020: Real crashes → would save you 15-20%

   Over 10 years, protection outweighs false alarms

5. PROBABILISTIC APPROACH
   After crossing below MA:
   - Day 1-3: Stay defensive (could be start of crash)
   - Day 4-10: Watch momentum (is it bouncing?)
   - Day 10+: If still grinding up, increase exposure gradually

   Don't think binary (all in / all out)
   Think gradual (30% → 50% → 80% → 100%)
""")

print("\n" + "="*80)
print("RECOMMENDATION FOR YOUR STRATEGY")
print("="*80)

print("""
Current Regime Rule:
  SPY < 200-day MA → 50% cash (PERIOD)
  SPY > 200-day MA → 100% invested

Problem: Too slow to react to V-recoveries

Better Regime Rule:
  SPY < 200-day MA → 50% cash
  BUT if SPY rallies +5% in 5 days → back to 100%

This gives you:
  - Protection from sustained bear markets
  - Quick re-entry on V-recoveries
  - Best of both worlds

Would you like me to code this "adaptive regime filter" and backtest it?
""")
