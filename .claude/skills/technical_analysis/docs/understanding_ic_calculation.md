# Understanding Information Coefficient (IC) and P-Value

## What is Information Coefficient (IC)?

**Simple Definition:** IC measures how well a factor (like RSI, momentum, etc.) predicts future returns.

Think of it like a correlation score between:
- **What you know today** (the factor value, e.g., RSI = 35)
- **What happens in the future** (the 20-day return, e.g., +15%)

## IC Values and What They Mean

| IC Value | Meaning | Example |
|----------|---------|---------|
| **+0.10** | Strong positive correlation | Higher RSI → Higher future returns (momentum) |
| **+0.05** | Weak positive correlation | Slightly higher RSI → Slightly higher returns |
| **0.00** | No correlation | RSI doesn't predict returns at all |
| **-0.05** | Weak negative correlation | Higher RSI → Slightly lower returns |
| **-0.10** | Strong negative correlation | Higher RSI → Lower future returns (mean-reversion) |

**Our Threshold:**
- If **|IC| > 0.05 AND p-value < 0.05**: Factor is working! ✓
- If **|IC| < 0.05 OR p-value >= 0.05**: Factor is not working ✗

---

## Step-by-Step: How IC is Calculated

### Step 1: Collect Your Data

Let's use a simple example with 10 observations:

| Date | Ticker | RSI_14 | 20-Day Future Return |
|------|--------|--------|---------------------|
| Day 1 | AAPL | 35 | +15% |
| Day 2 | MSFT | 70 | -5% |
| Day 3 | GOOGL | 45 | +10% |
| Day 4 | AMZN | 80 | -8% |
| Day 5 | NVDA | 25 | +20% |
| Day 6 | TSLA | 60 | +2% |
| Day 7 | META | 50 | +5% |
| Day 8 | NFLX | 75 | -3% |
| Day 9 | AAPL | 40 | +12% |
| Day 10 | MSFT | 65 | -2% |

### Step 2: Rank Both Columns

Instead of using the actual values, we **rank** them from lowest to highest.

**Why ranks?** This makes IC a "Spearman correlation" - it measures whether things move in the same direction, not by how much.

**RSI Ranking (lowest to highest):**
| Ticker | RSI Value | Rank |
|--------|-----------|------|
| NVDA | 25 | 1st (lowest) |
| AAPL | 35 | 2nd |
| AAPL | 40 | 3rd |
| GOOGL | 45 | 4th |
| META | 50 | 5th |
| TSLA | 60 | 6th |
| MSFT | 65 | 7th |
| MSFT | 70 | 8th |
| NFLX | 75 | 9th |
| AMZN | 80 | 10th (highest) |

**Future Return Ranking (lowest to highest):**
| Ticker | Return | Rank |
|--------|--------|------|
| AMZN | -8% | 1st (worst) |
| MSFT | -5% | 2nd |
| NFLX | -3% | 3rd |
| MSFT | -2% | 4th |
| TSLA | +2% | 5th |
| META | +5% | 6th |
| GOOGL | +10% | 7th |
| AAPL | +12% | 8th |
| AAPL | +15% | 9th |
| NVDA | +20% | 10th (best) |

### Step 3: Create Rank Pairs

Now we pair up the ranks:

| Ticker | RSI Rank | Return Rank | Moving Together? |
|--------|----------|-------------|------------------|
| AAPL | 2 | 9 | ✗ Low RSI, High return (inverse) |
| MSFT | 8 | 2 | ✓ High RSI, Low return (inverse) |
| GOOGL | 4 | 7 | ✗ Medium RSI, Medium return |
| AMZN | 10 | 1 | ✓ Highest RSI, Lowest return (inverse) |
| NVDA | 1 | 10 | ✓ Lowest RSI, Highest return (inverse) |
| TSLA | 6 | 5 | ✓ Similar ranks |
| META | 5 | 6 | ✓ Similar ranks |
| NFLX | 9 | 3 | ✓ High RSI, Low return (inverse) |
| AAPL | 3 | 8 | ✗ Low RSI, High return (inverse) |
| MSFT | 7 | 4 | ✓ High RSI, Low return (inverse) |

**Pattern:** When RSI rank is LOW, return rank tends to be HIGH (inverse relationship)

### Step 4: Calculate Correlation Between Ranks

This is the **Pearson correlation** but on ranks (which makes it Spearman).

**Formula:**
```
IC = Covariance(RSI_ranks, Return_ranks) / (StdDev(RSI_ranks) × StdDev(Return_ranks))
```

**In simpler terms:**
1. Calculate how much RSI ranks and return ranks vary together (covariance)
2. Divide by how much each varies individually (standard deviations)
3. This gives you a number between -1 and +1

**For our example:**
- RSI ranks: [2, 8, 4, 10, 1, 6, 5, 9, 3, 7]
- Return ranks: [9, 2, 7, 1, 10, 5, 6, 3, 8, 4]

When we calculate the correlation, we get: **IC ≈ -0.60**

**Interpretation:** Negative IC means inverse relationship - when RSI is high, returns are low.

---

## What is P-Value?

**Simple Definition:** P-value tells you if your result is "statistically significant" or just random luck.

### P-Value Interpretation

| P-Value | Meaning |
|---------|---------|
| **p < 0.01** | Very strong evidence - almost certainly real |
| **p < 0.05** | Strong evidence - probably real (this is our threshold) |
| **p < 0.10** | Weak evidence - might be real, might be luck |
| **p ≥ 0.10** | No evidence - likely just random noise |

**Our Rule:** We only trust the IC if **p-value < 0.05** (less than 5% chance it's random)

### How P-Value is Calculated

The p-value comes from a **t-test** on the correlation.

**Formula:**
```
t = IC × sqrt((n - 2) / (1 - IC²))
```

Where:
- `n` = number of observations (10 in our example)
- `IC` = our calculated correlation (-0.60)

**For our example:**
```
t = -0.60 × sqrt((10 - 2) / (1 - 0.60²))
t = -0.60 × sqrt(8 / 0.64)
t = -0.60 × sqrt(12.5)
t = -0.60 × 3.54
t ≈ -2.12
```

Then we convert this t-statistic to a p-value using a **t-distribution table** (or formula).

For `t = -2.12` with `n = 10` observations:
- **p-value ≈ 0.065**

**Interpretation:** There's a 6.5% chance this relationship is random. Since 6.5% > 5%, we'd say this is borderline - probably real but not quite strong enough evidence.

---

## Real Example from Your Validation

From the GOOGL/AMZN/NVDA test (2026-03-01 to 2026-06-28):

**RSI_14 vs 20-day forward returns:**
- **IC = -0.4852**
- **P-value = 0.0000** (actually something like 0.000001)
- **Sample size = 186 observations**

### What This Means

**IC = -0.4852:**
- Strong inverse correlation
- When RSI is high, 20-day returns tend to be low
- When RSI is low, 20-day returns tend to be high

**P-value ≈ 0.000001:**
- There's only a 0.0001% chance this is random luck
- This is EXTREMELY significant
- We can be very confident RSI predicts returns for these stocks

**How we got p-value:**
```
t = -0.4852 × sqrt((186 - 2) / (1 - 0.4852²))
t = -0.4852 × sqrt(184 / 0.7646)
t = -0.4852 × sqrt(240.6)
t = -0.4852 × 15.51
t ≈ -7.52
```

A t-statistic of -7.52 with 184 degrees of freedom gives p ≈ 0.000000001 (essentially zero)

---

## Visual Explanation

### Positive Correlation (IC > 0)

```
Factor Value:     Low  ──────────────► High
Future Return:    Low  ──────────────► High

Example: Momentum
- High momentum → High future returns
- Low momentum → Low future returns
```

### Negative Correlation (IC < 0)

```
Factor Value:     Low  ──────────────► High
Future Return:    High ◄────────────── Low

Example: RSI (Mean-reversion)
- High RSI → Low future returns
- Low RSI → High future returns
```

### No Correlation (IC ≈ 0)

```
Factor Value:     Low  ──────────────► High
Future Return:    ???  (no pattern)   ???

Example: Random factor
- Factor doesn't predict anything
```

---

## Why We Use Ranks (Spearman) Instead of Raw Values (Pearson)

**Example:**

| Stock | RSI | Return |
|-------|-----|--------|
| A | 30 | +15% |
| B | 60 | +5% |
| C | 90 | +1% |

**Using Raw Values (Pearson):**
- Sensitive to outliers
- Assumes linear relationship

**Using Ranks (Spearman):**
- Ranks: RSI [1, 2, 3], Returns [3, 2, 1]
- Only cares about order, not magnitude
- More robust to extreme values
- Better for finance where relationships are often non-linear

---

## Summary for Beginners

1. **IC measures** whether a factor predicts returns
   - IC > 0: Higher factor → Higher returns
   - IC < 0: Higher factor → Lower returns
   - IC ≈ 0: Factor doesn't work

2. **IC is calculated** by:
   - Ranking your factor values (lowest to highest)
   - Ranking future returns (lowest to highest)  
   - Calculating correlation between the two rank lists

3. **P-value tells you** if the IC is real or just luck
   - p < 0.05: Real pattern (we trust it)
   - p ≥ 0.05: Might be random (we don't trust it)

4. **Good factors have**:
   - |IC| > 0.05 (strong relationship)
   - p < 0.05 (statistically significant)

5. **In practice:**
   - IC = -0.48, p = 0.0000 → **Strong factor, use it!**
   - IC = -0.03, p = 0.50 → **Weak factor, ignore it**
   - IC = N/A → **Not enough data**
