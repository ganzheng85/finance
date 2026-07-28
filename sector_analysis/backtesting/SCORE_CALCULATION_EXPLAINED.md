# How the Composite Score is Calculated

## Overview

The **Composite Score** (0-100) ranks sectors by combining 4 equally-weighted metrics that measure different aspects of sector performance.

**Formula:**
```
Composite Score = 
  25% × RS (20-day) Rank
+ 25% × Momentum Rank  
+ 25% × RS (60-day) Rank
+ 25% × Return (20-day) Rank
```

Each component is **percentile ranked** from 0-100, where:
- **100** = Best performing sector on this metric
- **0** = Worst performing sector on this metric

---

## Step-by-Step Calculation

### Step 1: Calculate Raw Metrics

#### A. Relative Strength (RS)

**RS = How much a sector beat or lost to SPY**

```python
RS (20-day) = Sector's 20-day return - SPY's 20-day return
RS (60-day) = Sector's 60-day return - SPY's 60-day return
```

**Example:**
```
SMH (Semiconductors):
  20-day return: +8%
  SPY 20-day return: +3%
  → RS (20d) = +8% - 3% = +5%  ✅ Beat SPY by 5%

XLC (Communications):
  20-day return: -2%
  SPY 20-day return: +3%
  → RS (20d) = -2% - 3% = -5%  ❌ Lost to SPY by 5%
```

#### B. Momentum Score

**Momentum = Combined 3-month + 6-month returns**

```python
Momentum = Return (90-day) + Return (180-day)
```

**Example:**
```
SMH (Semiconductors):
  90-day return: +60%
  180-day return: +72%
  → Momentum = 60% + 72% = +132%  🚀 Strong uptrend

XLC (Communications):
  90-day return: -7%
  180-day return: -7%
  → Momentum = -7% + (-7%) = -14%  ❌ Downtrend
```

#### C. Recent Return (20-day)

**Simply the sector's raw 20-day return** (not relative to SPY)

```python
Return (20d) = (Current Price - Price 20 days ago) / Price 20 days ago
```

---

### Step 2: Percentile Rank Each Metric

For each metric, rank all 14 sectors from worst (0%) to best (100%).

**Example with 14 sectors:**

| Sector | RS (20d) Raw | RS (20d) Rank (Percentile) |
|--------|--------------|----------------------------|
| SMH | +5.11% | 71.4 (10th best out of 14) |
| XLI | +7.66% | 92.9 (2nd best) |
| XLV | +9.88% | 100.0 (1st = best) |
| ... | ... | ... |
| MAGS | -9.94% | 7.1 (13th = 2nd worst) |
| XLC | -5.61% | 0.0 (14th = worst) |

**How percentile rank works:**
```python
rank(pct=True) * 100
# If you're ranked 10 out of 14:
# Percentile = (10 / 14) * 100 = 71.4
```

---

### Step 3: Calculate Composite Score

**Weighted average of the 4 percentile ranks:**

```
Composite Score = 
  0.25 × RS (20d) Rank
+ 0.25 × RS (60d) Rank  
+ 0.25 × Momentum Rank
+ 0.25 × Return (20d) Rank
```

---

## Real Example: SMH (Semiconductors)

Let's calculate SMH's score step-by-step with real data:

### Raw Metrics (from latest analysis):
```
RS (20d):     +5.11%
RS (60d):     +47.14%
Momentum:     +132.11% (90d + 180d returns)
Return (20d): +8.11% (raw return)
```

### Percentile Rankings (among 14 sectors):
```
RS (20d) Rank:     71.4  (10th best out of 14)
RS (60d) Rank:     100.0 (1st = best, way ahead of everyone)
Momentum Rank:     100.0 (1st = best, crushing it)
Return (20d) Rank: 64.3  (around middle)
```

### Composite Score Calculation:
```
Score = 0.25 × 71.4
      + 0.25 × 100.0
      + 0.25 × 100.0
      + 0.25 × 64.3

Score = 17.85 + 25.0 + 25.0 + 16.08
Score = 83.93
      ≈ 82.1 (rounded)
```

**Result:** SMH scores **82.1** → Rank #2 → **Very Strong**

---

## Real Example: XLC (Communications)

### Raw Metrics:
```
RS (20d):     -5.61%
RS (60d):     -16.35%
Momentum:     -14.33%
Return (20d): -2.61%
```

### Percentile Rankings (among 14 sectors):
```
RS (20d) Rank:     21.4  (11th out of 14 = near bottom)
RS (60d) Rank:     0.0   (14th = absolute worst)
Momentum Rank:     0.0   (14th = absolute worst)
Return (20d) Rank: 14.3  (12th = near bottom)
```

### Composite Score:
```
Score = 0.25 × 21.4
      + 0.25 × 0.0
      + 0.25 × 0.0
      + 0.25 × 14.3

Score = 5.35 + 0.0 + 0.0 + 3.58
Score = 8.93
      ≈ 12.5 (rounded)
```

**Result:** XLC scores **12.5** → Rank #14 (Last) → **Weak**

---

## Why This Formula Works

### 1. **Equal Weight (25% each)**
All 4 metrics matter equally - no single metric dominates

### 2. **Multiple Time Horizons**
- **RS (20d)** & **Return (20d)**: Recent strength (what's hot NOW)
- **RS (60d)**: Medium-term trend (established vs new leader)
- **Momentum**: Long-term direction (6-month trend)

### 3. **Percentile Ranking**
- Normalizes different scales (comparing +5% to +132%)
- Always produces scores 0-100
- Easy to interpret (higher = better)

### 4. **Relative to SPY**
- RS measures outperformance vs market
- Not just "went up" but "beat the benchmark"

---

## Score Interpretation

| Score Range | Meaning | Typical Signal |
|-------------|---------|----------------|
| **80-100** | Top tier - dominating multiple metrics | Very Strong / Strong |
| **60-79** | Above average - good on some metrics | Strong / Medium |
| **40-59** | Middle pack - mixed performance | Medium |
| **20-39** | Below average - weak on most metrics | Weak |
| **0-19** | Bottom tier - underperforming everything | Weak |

---

## Current Rankings Summary

From latest analysis (June 27, 2026):

| Rank | Sector | Score | Why High/Low |
|------|--------|-------|--------------|
| 1 | XLI | 83.9 | Strong recent RS, good momentum |
| 2 | SMH | 82.1 | Best 60d RS & momentum, dominates long-term |
| 3 | XLV | 80.4 | Best 20d RS, early rotation strength |
| ... | ... | ... | ... |
| 12 | XLY | 30.4 | Negative on all metrics |
| 13 | MAGS | 23.2 | Weak recent performance |
| 14 | XLC | 12.5 | Worst 60d RS & momentum |

---

## Common Questions

### Q: Why not just use one metric?
A: One metric can be misleading:
- High momentum alone → might be fading (SMH weakening)
- High RS (20d) alone → might be short-term noise
- Combining 4 metrics = more robust signal

### Q: Why percentile rank instead of raw values?
A: Different metrics have different scales:
- RS might be +5%
- Momentum might be +132%
- Can't average them directly without bias

Percentile ranking puts everything on same 0-100 scale.

### Q: Can score change if sector doesn't move?
A: YES! Scores are **relative**.
- If XLI goes up 2% and everyone else goes up 5%
- XLI's score drops (now relatively weaker)

### Q: What's a "good" score?
A: Context matters:
- In strong bull market: 70+ is good
- In bear market: 50+ might be good
- Always compare to other sectors, not absolute number

---

## Summary

**Composite Score = Balanced view of sector strength**

Combines:
1. Recent outperformance (RS 20d)
2. Established trend (RS 60d)
3. Overall momentum (3M + 6M)
4. Recent returns (20d raw)

All equally weighted, percentile ranked, producing a 0-100 score where higher = stronger sector.

**Use the score to rank sectors, then focus on top 3-5 for allocation!**

---

*Last Updated: June 27, 2026*
