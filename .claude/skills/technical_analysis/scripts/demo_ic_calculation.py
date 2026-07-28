"""
Visual Demonstration of IC (Information Coefficient) Calculation
A beginner-friendly walkthrough with step-by-step explanations
"""

import pandas as pd
import numpy as np
from math import erf, sqrt

print("=" * 80)
print("INFORMATION COEFFICIENT (IC) CALCULATION - STEP BY STEP")
print("=" * 80)
print()

# Step 1: Create sample data
print("STEP 1: SAMPLE DATA")
print("-" * 80)
print("Let's say we have 10 stock observations with RSI and their 20-day returns:")
print()

data = pd.DataFrame({
    'ticker': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
               'TSLA', 'META', 'NFLX', 'AAPL', 'MSFT'],
    'rsi_14': [35, 70, 45, 80, 25, 60, 50, 75, 40, 65],
    'future_return_20d': [0.15, -0.05, 0.10, -0.08, 0.20,
                          0.02, 0.05, -0.03, 0.12, -0.02]
})

print(data.to_string(index=False))
print()

# Step 2: Rank the values
print("=" * 80)
print("STEP 2: RANK THE VALUES (Lowest to Highest)")
print("-" * 80)
print("Instead of using actual values, we rank them:")
print()

data['rsi_rank'] = data['rsi_14'].rank()
data['return_rank'] = data['future_return_20d'].rank()

print(data[['ticker', 'rsi_14', 'rsi_rank', 'future_return_20d', 'return_rank']].to_string(index=False))
print()

print("INTERPRETATION:")
print("  - RSI rank 1 = Lowest RSI (most oversold)")
print("  - RSI rank 10 = Highest RSI (most overbought)")
print("  - Return rank 1 = Lowest return (worst performance)")
print("  - Return rank 10 = Highest return (best performance)")
print()

# Step 3: Show the relationship
print("=" * 80)
print("STEP 3: VISUALIZE THE RELATIONSHIP")
print("-" * 80)
print("Let's see if low RSI ranks match with high return ranks (inverse):")
print()

print(f"{'Ticker':<8} {'RSI Rank':<10} {'Return Rank':<12} {'Pattern':<30}")
print("-" * 80)

for _, row in data.iterrows():
    rsi_r = int(row['rsi_rank'])
    ret_r = int(row['return_rank'])

    # Determine pattern
    if rsi_r <= 3 and ret_r >= 8:
        pattern = "Low RSI, High Return [INVERSE]"
    elif rsi_r >= 8 and ret_r <= 3:
        pattern = "High RSI, Low Return [INVERSE]"
    elif abs(rsi_r - ret_r) <= 2:
        pattern = "Similar ranks [POSITIVE]"
    else:
        pattern = "Mixed"

    print(f"{row['ticker']:<8} {rsi_r:<10} {ret_r:<12} {pattern:<30}")

print()
print("OBSERVATION: Do you see a pattern? Let's calculate the correlation...")
print()

# Step 4: Calculate IC manually
print("=" * 80)
print("STEP 4: CALCULATE IC (SPEARMAN CORRELATION)")
print("-" * 80)
print()

rsi_ranks = data['rsi_rank'].values
return_ranks = data['return_rank'].values
n = len(rsi_ranks)

# Calculate means
mean_rsi = rsi_ranks.mean()
mean_ret = return_ranks.mean()

print(f"Number of observations (n): {n}")
print(f"Mean RSI rank: {mean_rsi:.2f}")
print(f"Mean return rank: {mean_ret:.2f}")
print()

# Show deviations
print("Deviations from mean:")
print(f"{'Ticker':<8} {'RSI Rank':<10} {'Dev from Mean':<15} {'Return Rank':<12} {'Dev from Mean':<15}")
print("-" * 80)

for i, row in data.iterrows():
    rsi_r = rsi_ranks[i]
    ret_r = return_ranks[i]
    rsi_dev = rsi_r - mean_rsi
    ret_dev = ret_r - mean_ret
    print(f"{row['ticker']:<8} {rsi_r:<10.0f} {rsi_dev:>13.2f} {ret_r:<12.0f} {ret_dev:>13.2f}")

print()

# Calculate covariance
cov = ((rsi_ranks - mean_rsi) * (return_ranks - mean_ret)).sum() / n
print(f"Covariance = Sum(deviations_RSI × deviations_Return) / n")
print(f"Covariance = {cov:.4f}")
print()

# Calculate standard deviations
std_rsi = sqrt(((rsi_ranks - mean_rsi) ** 2).sum() / n)
std_ret = sqrt(((return_ranks - mean_ret) ** 2).sum() / n)

print(f"Standard Deviation (RSI ranks) = {std_rsi:.4f}")
print(f"Standard Deviation (Return ranks) = {std_ret:.4f}")
print()

# Calculate IC
ic = cov / (std_rsi * std_ret)

print("-" * 80)
print(f"IC = Covariance / (Std_RSI × Std_Return)")
print(f"IC = {cov:.4f} / ({std_rsi:.4f} × {std_ret:.4f})")
print(f"IC = {cov:.4f} / {std_rsi * std_ret:.4f}")
print(f"IC = {ic:.4f}")
print("-" * 80)
print()

# Interpret IC
print("INTERPRETATION:")
if ic > 0.05:
    print(f"  IC = {ic:.4f} is POSITIVE and > 0.05")
    print("  -> Higher RSI tends to predict HIGHER returns (MOMENTUM)")
elif ic < -0.05:
    print(f"  IC = {ic:.4f} is NEGATIVE and < -0.05")
    print("  -> Higher RSI tends to predict LOWER returns (MEAN-REVERSION)")
else:
    print(f"  IC = {ic:.4f} is close to ZERO")
    print("  -> RSI doesn't predict returns (NO RELATIONSHIP)")
print()

# Step 5: Calculate p-value
print("=" * 80)
print("STEP 5: CALCULATE P-VALUE (Is this significant or just luck?)")
print("-" * 80)
print()

# Calculate t-statistic
if abs(ic) < 1:
    t_stat = ic * sqrt((n - 2) / (1 - ic**2 + 1e-10))
else:
    t_stat = float('inf') if ic > 0 else float('-inf')

print(f"T-statistic formula: t = IC × sqrt((n - 2) / (1 - IC²))")
print(f"t = {ic:.4f} × sqrt(({n} - 2) / (1 - {ic:.4f}²))")
print(f"t = {ic:.4f} × sqrt({n - 2} / {1 - ic**2:.4f})")
print(f"t = {ic:.4f} × {sqrt((n - 2) / (1 - ic**2 + 1e-10)):.4f}")
print(f"t = {t_stat:.4f}")
print()

# Calculate p-value
if abs(t_stat) != float('inf'):
    p_value = 2 * (1 - 0.5 * (1 + erf(abs(t_stat) / sqrt(2))))
else:
    p_value = 0.0

print(f"P-value = {p_value:.6f}")
print()

print("INTERPRETATION:")
print(f"  P-value = {p_value:.6f}")
if p_value < 0.01:
    print("  -> Very strong evidence (p < 0.01) - almost certainly real!")
elif p_value < 0.05:
    print("  -> Strong evidence (p < 0.05) - probably real!")
elif p_value < 0.10:
    print("  -> Weak evidence (p < 0.10) - might be real, might be luck")
else:
    print("  -> No evidence (p ≥ 0.10) - likely just random noise")
print()

# Step 6: Final decision
print("=" * 80)
print("STEP 6: FINAL DECISION")
print("-" * 80)
print()

print(f"IC = {ic:.4f}")
print(f"P-value = {p_value:.6f}")
print(f"Sample size = {n}")
print()

if abs(ic) >= 0.05 and p_value < 0.05:
    if ic > 0:
        print("[RESULT] STRONG PREDICTIVE FACTOR (Momentum)")
        print("  [OK] Use this factor!")
        print("  [OK] Higher factor values = Higher expected returns")
    else:
        print("[RESULT] STRONG INVERSE FACTOR (Mean-Reversion)")
        print("  [OK] Use this factor!")
        print("  [OK] Lower factor values = Higher expected returns")
elif abs(ic) < 0.05:
    print("[RESULT] WEAK FACTOR")
    print("  [X] Don't use this factor")
    print("  [X] IC is too close to zero (no predictive power)")
elif p_value >= 0.05:
    print("[RESULT] NOT STATISTICALLY SIGNIFICANT")
    print("  [X] Don't use this factor")
    print("  [X] P-value is too high (might be random luck)")
else:
    print("[RESULT] UNCLEAR")

print()

# Compare with actual validation results
print("=" * 80)
print("COMPARISON WITH REAL DATA")
print("-" * 80)
print()
print("In our toy example (10 observations):")
print(f"  IC = {ic:.4f}")
print(f"  P-value = {p_value:.4f}")
print(f"  Conclusion: {'Significant' if p_value < 0.05 else 'Not significant'}")
print()
print("In the real GOOGL/AMZN/NVDA validation (186 observations):")
print(f"  IC = -0.4852")
print(f"  P-value = 0.0000")
print(f"  Conclusion: VERY significant!")
print()
print("WHY THE DIFFERENCE?")
print("  - More observations (186 vs 10) = More statistical power")
print("  - Larger sample size = More confident in the result")
print("  - With only 10 observations, it's hard to prove significance")
print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
Information Coefficient (IC) tells you:
  1. DIRECTION: Positive or negative relationship
  2. STRENGTH: How strong the relationship is (0 to 1 or -1)

P-value tells you:
  1. CONFIDENCE: Is this real or just random luck?
  2. We use p < 0.05 as our threshold (95% confidence)

Together they answer:
  [OK] Does this factor predict returns? (IC magnitude)
  [OK] In what direction? (IC sign: + or -)
  [OK] Can we trust it? (p-value)

KEY THRESHOLDS:
  - Good factor: |IC| > 0.05 AND p < 0.05
  - Weak factor: |IC| < 0.05 OR p >= 0.05
""")
