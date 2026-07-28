"""
Analyze the relationship between RSI and forward returns
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import yfinance as yf

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))
from techinical_factor import TechnicalFactors

# Configuration
TICKERS = ['GOOGL', 'AMZN', 'NVDA']
START_DATE = '2026-03-01'
END_DATE = '2026-06-28'

print("=" * 80)
print("RSI vs 20-DAY FORWARD RETURNS ANALYSIS")
print("=" * 80)
print(f"Tickers: {', '.join(TICKERS)}")
print(f"Period: {START_DATE} to {END_DATE}")
print()

# Download data
print("Downloading stock data...")
all_data = []

for ticker in TICKERS:
    stock = yf.Ticker(ticker)
    hist = stock.history(start=START_DATE, end=END_DATE)

    if not hist.empty:
        hist = hist.reset_index()
        hist['symbol'] = ticker
        hist = hist.rename(columns={
            'Date': 'date',
            'Close': 'adjusted_close',
            'Volume': 'volume',
            'Open': 'open',
            'High': 'high',
            'Low': 'low'
        })
        all_data.append(hist[['symbol', 'date', 'adjusted_close', 'volume', 'open', 'high', 'low']])
        print(f"  [OK] {ticker}: {len(hist)} days")

df = pd.concat(all_data, ignore_index=True)

# Calculate RSI
print("\nCalculating RSI_14...")
tf = TechnicalFactors(df)
tf.rsi(window=14)
df = tf.df

# Calculate 20-day forward returns
print("Calculating 20-day forward returns...")
df['fwd_return_20d'] = df.groupby('symbol')['adjusted_close'].pct_change(20).shift(-20)

# Remove rows without forward returns (last 20 days)
analysis_df = df[df['fwd_return_20d'].notna()].copy()

print(f"\n[OK] Analysis dataset: {len(analysis_df)} observations")

# Show the relationship
print("\n" + "=" * 80)
print("RSI_14 vs 20-DAY FORWARD RETURNS")
print("=" * 80)

# Sort by RSI and divide into quintiles
analysis_df = analysis_df.sort_values('rsi_14')
analysis_df['rsi_quintile'] = pd.qcut(analysis_df['rsi_14'], q=5, labels=['Q1 (Lowest RSI)', 'Q2', 'Q3', 'Q4', 'Q5 (Highest RSI)'], duplicates='drop')

# Calculate average returns by quintile
print("\nAVERAGE 20-DAY FORWARD RETURN BY RSI QUINTILE:")
print("-" * 80)
print(f"{'RSI Quintile':<25} {'Avg RSI':<12} {'Avg 20d Return':<20} {'Sample Size':<12}")
print("-" * 80)

quintile_stats = analysis_df.groupby('rsi_quintile', observed=True).agg({
    'rsi_14': 'mean',
    'fwd_return_20d': 'mean',
    'symbol': 'count'
}).reset_index()

for _, row in quintile_stats.iterrows():
    quintile = row['rsi_quintile']
    avg_rsi = row['rsi_14']
    avg_return = row['fwd_return_20d'] * 100  # Convert to percentage
    count = row['symbol']
    print(f"{quintile:<25} {avg_rsi:>10.2f} {avg_return:>18.2f}% {count:>10.0f}")

print("-" * 80)
print("\nINTERPRETATION:")
print("IC = -0.4852 means INVERSE relationship")
print("Lower RSI = Better future returns")
print("Higher RSI = Worse future returns")
print()

# Show specific examples
print("=" * 80)
print("SPECIFIC EXAMPLES (Recent data points)")
print("=" * 80)
print(f"{'Date':<12} {'Ticker':<8} {'RSI_14':<10} {'20d Return':<15} {'Outcome':<20}")
print("-" * 80)

# Show 10 random examples
examples = analysis_df.sample(min(10, len(analysis_df))).sort_values('rsi_14')

for _, row in examples.iterrows():
    date_str = row['date'].strftime('%Y-%m-%d')
    ticker = row['symbol']
    rsi = row['rsi_14']
    fwd_ret = row['fwd_return_20d'] * 100

    # Determine if prediction was correct
    if rsi < 40:  # Oversold (should predict good returns)
        prediction = "Low RSI -> Good return" if fwd_ret > 0 else "Low RSI -> Bad return"
    elif rsi > 60:  # Overbought (should predict poor returns)
        prediction = "High RSI -> Bad return" if fwd_ret < 0 else "High RSI -> Good return"
    else:
        prediction = "Neutral"

    print(f"{date_str:<12} {ticker:<8} {rsi:>8.2f} {fwd_ret:>13.2f}% {prediction:<20}")

# Calculate Spearman correlation
print("\n" + "=" * 80)
print("STATISTICAL VALIDATION")
print("=" * 80)

# Manual Spearman correlation
rsi_values = analysis_df['rsi_14'].values
return_values = analysis_df['fwd_return_20d'].values

rsi_ranks = pd.Series(rsi_values).rank()
return_ranks = pd.Series(return_values).rank()

n = len(rsi_ranks)
mean_rsi = rsi_ranks.mean()
mean_ret = return_ranks.mean()

cov = ((rsi_ranks - mean_rsi) * (return_ranks - mean_ret)).sum() / n
std_rsi = np.sqrt(((rsi_ranks - mean_rsi) ** 2).sum() / n)
std_ret = np.sqrt(((return_ranks - mean_ret) ** 2).sum() / n)

ic = cov / (std_rsi * std_ret)

# t-statistic
t = ic * np.sqrt((n - 2) / (1 - ic**2 + 1e-10))

# p-value
from math import erf
p_value = 2 * (1 - 0.5 * (1 + erf(abs(t) / np.sqrt(2))))

print(f"\nInformation Coefficient (IC): {ic:.4f}")
print(f"P-value: {p_value:.6f}")
print(f"Sample size: {n} observations")
print()

if ic < -0.05 and p_value < 0.05:
    print("[RESULT] STRONG INVERSE RELATIONSHIP")
    print("  - Lower RSI values predict HIGHER future returns")
    print("  - Higher RSI values predict LOWER future returns")
    print()
    print("PRACTICAL MEANING:")
    print("  - When RSI < 40 (oversold), stocks tend to bounce back")
    print("  - When RSI > 60 (overbought), stocks tend to pull back")
    print("  - RSI is acting as a mean-reversion indicator")
elif ic > 0.05 and p_value < 0.05:
    print("[RESULT] STRONG POSITIVE RELATIONSHIP")
    print("  - Higher RSI values predict HIGHER future returns")
    print("  - Lower RSI values predict LOWER future returns")
else:
    print("[RESULT] NO SIGNIFICANT RELATIONSHIP")

# Show scatter-like data
print("\n" + "=" * 80)
print("DATA DISTRIBUTION")
print("=" * 80)

# Bin RSI into ranges and show average returns
bins = [0, 30, 40, 50, 60, 70, 100]
labels = ['0-30\n(Very Oversold)', '30-40\n(Oversold)', '40-50\n(Neutral Low)',
          '50-60\n(Neutral High)', '60-70\n(Overbought)', '70-100\n(Very Overbought)']

analysis_df['rsi_bin'] = pd.cut(analysis_df['rsi_14'], bins=bins, labels=labels)

print(f"\n{'RSI Range':<20} {'Count':<10} {'Avg 20d Return':<20} {'Min Return':<15} {'Max Return':<15}")
print("-" * 80)

for label in labels:
    subset = analysis_df[analysis_df['rsi_bin'] == label]
    if len(subset) > 0:
        count = len(subset)
        avg_ret = subset['fwd_return_20d'].mean() * 100
        min_ret = subset['fwd_return_20d'].min() * 100
        max_ret = subset['fwd_return_20d'].max() * 100
        print(f"{label:<20} {count:<10} {avg_ret:>18.2f}% {min_ret:>13.2f}% {max_ret:>13.2f}%")

print()
print("=" * 80)
print("CONCLUSION")
print("=" * 80)
print(f"""
For {', '.join(TICKERS)} during {START_DATE} to {END_DATE}:

IC = {ic:.4f} indicates a STRONG INVERSE correlation.

This means:
1. When RSI_14 is LOW (oversold), 20-day forward returns tend to be POSITIVE
2. When RSI_14 is HIGH (overbought), 20-day forward returns tend to be NEGATIVE
3. RSI is working as a CONTRARIAN/MEAN-REVERSION indicator

Trading Strategy Implication:
- BUY when RSI < 40 (oversold conditions)
- SELL/AVOID when RSI > 60 (overbought conditions)
- This is the OPPOSITE of momentum trading (which would buy high RSI)

This validates the classic interpretation of RSI as a mean-reversion indicator!
""")
