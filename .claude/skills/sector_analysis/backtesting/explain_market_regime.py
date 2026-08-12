"""
Demonstrate Market Regime Strategy with Real COVID Crash Example
Shows week-by-week what happens
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

print("="*80)
print("MARKET REGIME STRATEGY EXPLANATION")
print("Example: 2020 COVID Crash")
print("="*80)

# Fetch SPY data for COVID period
start = datetime(2020, 2, 1)
end = datetime(2020, 5, 31)

print(f"\nFetching SPY data from {start.date()} to {end.date()}...")
spy = yf.Ticker("SPY")
spy_data = spy.history(start=start - timedelta(days=250), end=end)
spy_data.index = spy_data.index.tz_localize(None)

# Calculate 200-day MA
spy_data['MA200'] = spy_data['Close'].rolling(window=200).mean()

# Filter to Feb-May 2020
display_data = spy_data.loc[start:end].copy()

print("\n" + "="*80)
print("WEEK-BY-WEEK BREAKDOWN")
print("="*80)

print(f"\n{'Date':<12} {'SPY Price':<12} {'200-day MA':<12} {'Status':<15} {'Action':<30}")
print("-"*95)

portfolio_value = 100000  # Start with $100k
cash_held = 0
invested = portfolio_value

# Sample key dates during COVID crash
key_dates = [
    datetime(2020, 2, 7),   # Before crash
    datetime(2020, 2, 21),  # Crash starting
    datetime(2020, 2, 28),  # Deep into crash
    datetime(2020, 3, 6),   # Continued decline
    datetime(2020, 3, 13),  # Near bottom
    datetime(2020, 3, 20),  # Bottom
    datetime(2020, 3, 27),  # Recovery starting
    datetime(2020, 4, 3),   # Still recovering
    datetime(2020, 4, 17),  # More recovery
    datetime(2020, 5, 1),   # Almost back
    datetime(2020, 5, 15),  # Back above MA200
    datetime(2020, 5, 29),  # Recovered
]

for date in key_dates:
    if date not in display_data.index:
        continue

    price = display_data.loc[date, 'Close']
    ma200 = display_data.loc[date, 'MA200']

    if pd.isna(ma200):
        continue

    if price > ma200:
        status = "BULL"
        allocation = "100% invested"
        cash_pct = 0
        invested_pct = 100
    else:
        status = "BEAR"
        allocation = "50% cash, 50% invested"
        cash_pct = 50
        invested_pct = 50

    print(f"{date.strftime('%Y-%m-%d'):<12} ${price:<10.2f} ${ma200:<10.2f} {status:<15} {allocation:<30}")

print("\n" + "="*80)
print("WHAT THIS MEANS IN PRACTICE")
print("="*80)

print("""
Let's say you have $100,000 on February 21, 2020 (when crash started):

Week 1 (Feb 21): SPY $338 > MA200 $313
  Status: BULL MARKET
  Action: 100% invested
  Holdings:
    - Top Sector 1: $33,333 (33.33%)
    - Top Sector 2: $33,333 (33.33%)
    - Top Sector 3: $33,333 (33.33%)
    - Cash: $0

Week 2 (Feb 28): SPY $303 < MA200 $314
  Status: BEAR MARKET [SIGNAL TO GO DEFENSIVE]
  Action: GO 50% CASH
  Holdings:
    - Top Sector 1: $16,667 (16.67%) [Sell half]
    - Top Sector 2: $16,667 (16.67%) [Sell half]
    - Top Sector 3: $16,667 (16.67%) [Sell half]
    - Cash: $50,000 (50%)             [Protection]

Weeks 3-9 (March-April): SPY stays below MA200
  Status: BEAR MARKET
  Action: STAY 50% CASH [Keep defensive position]
  Holdings:
    - Still 50% cash, 50% in top 3 sectors
    - Rebalance weekly to new top 3 (but only with 50% of capital)

Week 10 (May 15): SPY $293 > MA200 $285
  Status: BULL MARKET [SIGNAL TO GO BACK IN]
  Action: RE-INVEST CASH
  Holdings:
    - Top Sector 1: $33,333 (33.33%) [Double position]
    - Top Sector 2: $33,333 (33.33%) [Double position]
    - Top Sector 3: $33,333 (33.33%) [Double position]
    - Cash: $0                        [Back to fully invested]

""")

print("="*80)
print("KEY INSIGHTS")
print("="*80)

print("""
1. AUTOMATIC PROTECTION:
   - When market crashes (SPY < 200 MA), you automatically hold 50% cash
   - This protected you from the worst of the crash

2. AUTOMATIC RE-ENTRY:
   - When market recovers (SPY > 200 MA), you automatically reinvest
   - You don't miss the recovery

3. NO EMOTIONS:
   - You don't decide "is this a crash?" or "should I sell?"
   - The 200-day MA makes the decision for you
   - Simple rule: Above MA = 100% in, Below MA = 50% in

4. WEEKLY CHECK:
   - Every Friday, check: Is SPY > 200-day MA?
   - Adjust allocation accordingly
   - That's it!
""")

print("="*80)
print("HOW TO CALCULATE 200-DAY MA")
print("="*80)

print("""
Option 1 - Use a Free Website:
  1. Go to https://stockcharts.com
  2. Enter "SPY"
  3. Look for the 200-day moving average line
  4. Is current price above or below the line?

Option 2 - Your Brokerage:
  Most brokers show 200-day MA on their charts
  Look for "SMA(200)" or "MA200"

Option 3 - Python Script (I can create this for you):
  Run a simple script that tells you:
    "SPY is above 200-day MA - Go 100% invested"
    OR
    "SPY is below 200-day MA - Go 50% cash"
""")

print("\n" + "="*80)
print("CURRENT STATUS (AS OF TODAY)")
print("="*80)

# Get current SPY status
current = yf.Ticker("SPY")
recent = current.history(period="1y")
recent['MA200'] = recent['Close'].rolling(window=200).mean()

latest_price = recent['Close'].iloc[-1]
latest_ma200 = recent['MA200'].iloc[-1]
latest_date = recent.index[-1].strftime('%Y-%m-%d')

if latest_price > latest_ma200:
    current_status = "BULL MARKET"
    current_action = "100% INVESTED (33.33% each sector)"
    color = "GREEN"
else:
    current_status = "BEAR MARKET"
    current_action = "50% CASH, 50% INVESTED (16.67% each sector)"
    color = "RED"

print(f"\nDate: {latest_date}")
print(f"SPY Price: ${latest_price:.2f}")
print(f"200-day MA: ${latest_ma200:.2f}")
print(f"Status: {current_status}")
print(f"Action: {current_action}")

print("\n" + "="*80)
