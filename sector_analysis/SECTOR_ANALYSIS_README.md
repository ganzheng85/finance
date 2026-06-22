# Sector Analysis - Money Flow & Rotation Strategy

## Overview

This sector analysis framework tracks **where institutional money is actually moving** across market sectors. Unlike stock-level analysis, sector rotation provides a macro view of capital flows and helps identify which industries are receiving investment versus being rotated out of.

## Core Philosophy

> **Sector rotation is NOT about predicting the future**  
> **It's about tracking where capital is already moving**

This aligns with quantitative research:
- **Momentum** = follow winners
- **Flows** = confirm real capital allocation
- **Breadth** = validate strength of the move

---

## 1. Relative Strength (RS) - The Foundation

**Definition:**
```
RS = Sector ETF Price / SPY Price
```

**Interpretation:**
- **RS Rising** → Sector outperforming → Money flowing in
- **RS Falling** → Sector underperforming → Money rotating out

### Implementation

Use **two time horizons** for complete picture:

| Horizon | Period | Purpose |
|---------|--------|---------|
| **Short-term** | 20-day return | Catch early rotation signals |
| **Medium-term** | 60-day return | Confirm sustained trends |

### Signal Logic

| Condition | 20-day RS | 60-day RS | Interpretation |
|-----------|-----------|-----------|----------------|
| **Strong Sector** | > 0 | > 0 | Both short and long term outperformance |
| **Early Rotation** | ↑ (positive) | Weak/negative | Fresh money entering, potential new leader |
| **Late Cycle** | ↓ (weakening) | Still strong | Momentum fading, potential rotation out |
| **Weak Sector** | < 0 | < 0 | Underperforming, avoid |

**Example:**
```
Technology (XLK):
  20-day RS: +5.2%  (vs SPY)
  60-day RS: +8.1%  (vs SPY)
  → Signal: STRONG (outperforming on both timeframes)

Energy (XLE):
  20-day RS: +3.1%  (vs SPY)
  60-day RS: -2.4%  (vs SPY)
  → Signal: EARLY ROTATION (fresh strength emerging)
```

---

## 2. Momentum Ranking - Quantitative Alpha

**Core Idea:** Sector leadership persists → Rank and follow winners

### Standard Approach

**Composite Momentum Score:**
```
Momentum Score = 3-month return + 6-month return
```

**Process:**
1. Calculate momentum for all 13 sectors
2. Rank sectors by momentum score
3. **Long top 3-5 sectors**
4. **Avoid bottom 3 sectors**
5. Rebalance monthly

### Academic Version (12-1 Momentum)

**Formula:**
```
12-1 Momentum = 12-month return - 1-month return
```

**Why skip last month?**
- Removes short-term mean reversion noise
- Captures sustained institutional trends
- Better risk-adjusted returns

**Example Ranking:**
```
Rank  Sector              3M Return  6M Return  Total Score
----  -----------------   ---------  ---------  -----------
1.    Technology (XLK)      +12.3%    +18.5%      +30.8%
2.    Healthcare (XLV)      +8.1%     +15.2%      +23.3%
3.    Financials (XLF)      +6.4%     +11.8%      +18.2%
...
9.    Energy (XLE)          -2.1%     +1.3%       -0.8%
10.   Utilities (XLU)       -3.5%     -5.2%       -8.7%
11.   Real Estate (XLRE)    -4.2%     -6.8%      -11.0%

→ Portfolio: Long XLK, XLV, XLF
→ Avoid: XLE, XLU, XLRE
```

---

## 3. ETF Flow Data - Real Money Tracking

**Definition:**
```
Net Flow = Change in Shares Outstanding × NAV
```

**Why it's powerful:**
- Captures **actual allocation decisions** by institutions
- Reflects real capital entering/exiting sectors
- Often **leads price moves** (smart money indicator)

### Interpretation

| Flow Direction | Price Action | Signal |
|----------------|--------------|--------|
| **Positive inflow** | Price rising | ✅ **Strong accumulation** |
| **Positive inflow** | Price flat/down | ⚠️ **Early accumulation** (potential bottom) |
| **Negative outflow** | Price rising | 🚨 **Distribution** (weak rally, avoid) |
| **Negative outflow** | Price falling | ❌ **Capitulation** (strong selling) |

### Best Practice: Combine Price + Flow

**Signal Matrix:**

| Momentum | ETF Flow | Overall Signal |
|----------|----------|----------------|
| High (top 5) | Positive | 🚀 **STRONG BUY** |
| High (top 5) | Negative | ⚠️ **Caution** (potential reversal) |
| Low (bottom 5) | Positive | 👀 **Watch** (early reversal?) |
| Low (bottom 5) | Negative | ❌ **AVOID** |

**Example:**
```
Technology (XLK):
  Momentum Rank: #1
  7-day Flow: +$2.3B
  30-day Flow: +$8.1B
  → Signal: STRONG (high momentum + sustained inflow)

Energy (XLE):
  Momentum Rank: #2
  7-day Flow: -$450M
  30-day Flow: -$1.2B
  → Signal: WEAK RALLY (price up but money exiting = distribution)
```

---

## 4. Breadth Analysis - Quality of the Move

**Purpose:** Distinguish between **broad sector strength** vs **narrow leadership**

### Key Breadth Indicators

| Indicator | Calculation | Strong Signal | Weak Signal |
|-----------|-------------|---------------|-------------|
| **% Above 50-day MA** | (Stocks above MA) / Total | > 70% | < 30% |
| **Advance/Decline** | Advancing stocks - Declining | Positive & rising | Negative or diverging |
| **New Highs - New Lows** | 52-week highs - lows | > 0 and expanding | < 0 or contracting |

### Interpretation

**Strong Sector:**
- Price ↑ + High breadth (70%+ stocks participating)
- Example: Technology rally with most stocks rising

**Weak Leadership (Avoid):**
- Price ↑ + Low breadth (few stocks driving index)
- Example: "Magnificent 7" driving S&P while most stocks lag

**Example:**
```
Technology (XLK):
  Price: +8.2% (1 month)
  % Above 50-day MA: 82%
  A/D Line: Rising
  → Quality: STRONG (broad participation)

Energy (XLE):
  Price: +6.1% (1 month)
  % Above 50-day MA: 38%
  A/D Line: Flat
  → Quality: WEAK (narrow leadership, likely to fail)
```

---

## 5. Volume-Based Money Flow

**Technical proxy for institutional activity**

### Key Indicators

**On-Balance Volume (OBV):**
```
OBV = Cumulative(Volume × Sign(Price Change))
```

**Relative Volume:**
```
Relative Volume = Current Volume / 20-day Average Volume
```

### Signals

| Price | Volume | OBV Trend | Interpretation |
|-------|--------|-----------|----------------|
| ↑ | Above average | Rising | ✅ **Accumulation** (strong buy) |
| ↑ | Below average | Flat/falling | ⚠️ **Weak rally** (likely to reverse) |
| ↓ | Above average | Falling | ❌ **Distribution** (strong sell) |
| ↓ | Below average | Flat | 🔄 **Consolidation** |

---

## 6. Sector Rotation Map - Visual Framework

**Quadrant Model** for tracking rotation trajectory

### Axes
- **X-axis:** Relative Strength (sector vs SPY)
- **Y-axis:** Momentum of RS (is RS accelerating or decelerating?)

### Four Quadrants

```
                     High Momentum
                           ↑
                           |
    Improving      |    Leading
    (Emerging)     |    (Strong)
    ----------------|---------------→ High RS
    Lagging        |    Weakening
    (Avoid)        |    (Rotating Out)
                           |
                     Low Momentum
```

| Quadrant | RS | Momentum | Action |
|----------|-------|----------|--------|
| **Leading** | Strong | Accelerating | 🚀 **OVERWEIGHT** (ride the trend) |
| **Weakening** | Strong | Decelerating | ⚠️ **REDUCE** (take profits) |
| **Lagging** | Weak | Decelerating | ❌ **AVOID** (no capital) |
| **Improving** | Weak | Accelerating | 👀 **WATCH** (early rotation signal) |

**Example Rotation Map:**
```
Leading (Buy):
  - Technology (XLK): RS=+8%, Momentum=+2%/month
  - Healthcare (XLV): RS=+5%, Momentum=+1.5%/month

Weakening (Reduce):
  - Financials (XLF): RS=+3%, Momentum=-0.5%/month
  - Industrials (XLI): RS=+2%, Momentum=-1%/month

Lagging (Avoid):
  - Energy (XLE): RS=-4%, Momentum=-2%/month
  - Utilities (XLU): RS=-6%, Momentum=-1%/month

Improving (Watch):
  - Consumer Discretionary (XLY): RS=-2%, Momentum=+1%/month
```

---

## 7. Practical Implementation Framework

### Core Signal Stack

**Primary Signals (70% weight):**
1. **Relative Strength** vs SPY (20-day, 60-day)
2. **Momentum Ranking** (3M, 6M, 12-1)
3. **ETF Fund Flows** (7-day, 30-day)

**Supporting Signals (30% weight):**
4. **Breadth** (% above MA, A/D line)
5. **Volume/OBV** (accumulation/distribution)
6. **Macro Overlay** (rates, inflation regime)

### Composite Scoring Model

```python
Sector Score = 
    0.25 × RS_rank +
    0.25 × Momentum_rank +
    0.20 × Flow_zscore +
    0.15 × Breadth_score +
    0.15 × Volume_score

Where:
  - RS_rank: Percentile rank of relative strength (0-100)
  - Momentum_rank: Percentile rank of momentum (0-100)
  - Flow_zscore: Z-score of net flows vs history
  - Breadth_score: % stocks above 50-day MA
  - Volume_score: OBV trend strength (0-100)
```

### Portfolio Construction

**Simple Rules:**
1. Calculate composite score for all 13 sectors
2. **Long top 3-5 sectors** (equal weight or momentum-weighted)
3. **Avoid bottom 3 sectors** (zero allocation)
4. **Rebalance monthly** (first trading day)
5. **Risk management:** Exit if sector drops below 50-day MA

**Example Portfolio:**
```
Current Date: 2026-06-21

Rank  Sector              Score  Allocation
----  -----------------   -----  ----------
1.    Technology (XLK)    92.3   25%
2.    Healthcare (XLV)    85.7   25%
3.    Financials (XLF)    78.4   20%
4.    Industrials (XLI)   72.1   15%
5.    Cons. Discr. (XLY)  68.5   15%

Bottom 3 (Avoid):
9.    Energy (XLE)        32.1   0%
10.   Utilities (XLU)     28.6   0%
11.   Real Estate (XLRE)  21.4   0%
```

---

## 8. Sector ETF Universe

### Standard S&P Sector ETFs (SPDR)

| Sector | Ticker | Full Name |
|--------|--------|-----------|
| **Technology** | XLK | Technology Select Sector SPDR |
| **Healthcare** | XLV | Health Care Select Sector SPDR |
| **Financials** | XLF | Financial Select Sector SPDR |
| **Consumer Discretionary** | XLY | Consumer Discretionary Select Sector SPDR |
| **Industrials** | XLI | Industrial Select Sector SPDR |
| **Consumer Staples** | XLP | Consumer Staples Select Sector SPDR |
| **Energy** | XLE | Energy Select Sector SPDR |
| **Utilities** | XLU | Utilities Select Sector SPDR |
| **Materials** | XLB | Materials Select Sector SPDR |
| **Real Estate** | XLRE | Real Estate Select Sector SPDR |
| **Communication Services** | XLC | Communication Services Select Sector SPDR |

### Special Sectors

| Sector | Ticker | Full Name |
|--------|--------|-----------|
| **Magnificent 7** | MAGS | Roundhill Magnificent Seven ETF |
| **Semiconductors** | SMH | VanEck Semiconductor ETF |

**Benchmark:**
- **SPY** - S&P 500 ETF (for relative strength calculations)

---

## 9. Data Requirements

### Required Data (Daily)

For each sector ETF:
1. **Price data:** Open, High, Low, Close, Adjusted Close
2. **Volume data:** Daily volume
3. **Shares outstanding:** For flow calculations
4. **Net Asset Value (NAV):** For flow calculations

For constituent stocks (breadth):
5. **Individual stock prices:** 50-day MA calculations
6. **52-week highs/lows:** New high/low tracking

### API/Data Sources

- **Yahoo Finance:** Price, volume (free)
- **SEC EDGAR:** Shares outstanding (free, updated quarterly)
- **ETF.com / ETFdb:** Flow data (may require subscription)
- **FinViz / TradingView:** Breadth data

---

## 10. Update Frequency & Rebalancing

| Metric | Update Frequency | Purpose |
|--------|------------------|---------|
| **Relative Strength** | Daily | Track real-time outperformance |
| **Momentum Ranking** | Weekly | Identify trend changes |
| **ETF Flows** | Daily/Weekly | Spot institutional activity |
| **Breadth** | Daily | Monitor internal strength |
| **Portfolio Rebalance** | Monthly | Reduce trading costs |

**Rebalancing Rules:**
- Standard: First trading day of month
- Emergency exit: If top sector breaks below 50-day MA (risk management)
- Mid-month add: If new sector enters "Improving" quadrant with strong signals

---

## 11. Risk Management

### Position Sizing

**Equal Weight (Simple):**
```
Each sector = 100% / N positions
Example: 5 sectors × 20% = 100%
```

**Momentum Weight (Advanced):**
```
Weight = Sector_Score / Sum(All_Scores)
Higher score → larger allocation
```

### Stop Loss Rules

1. **Individual Sector:** Exit if drops below 50-day MA
2. **Composite Score:** Exit if score drops below 50th percentile
3. **Flow Reversal:** Reduce if large negative flow (>2 std dev)

### Diversification

- **Minimum:** Hold at least 3 sectors
- **Maximum:** Hold at most 6 sectors
- **Sector correlation:** Avoid overweighting correlated sectors

---

## 12. Backtesting & Validation

### Performance Metrics

Track:
- **Sharpe Ratio:** Risk-adjusted returns
- **Max Drawdown:** Worst peak-to-trough decline
- **Win Rate:** % of months outperforming SPY
- **Turnover:** Monthly sector changes

**Benchmark:** SPY (buy and hold)

### Expected Performance

Historical research shows:
- **Annual Return:** SPY + 2-5% (with rotation)
- **Volatility:** Similar to SPY (sector diversification)
- **Sharpe Ratio:** ~0.6-0.9 (vs ~0.5 for SPY)

---

## 13. Macro Overlay (Optional Enhancement)

### Interest Rate Regime

| Rate Environment | Favor Sectors | Avoid Sectors |
|------------------|---------------|---------------|
| **Rising Rates** | Financials, Energy | Utilities, Real Estate |
| **Falling Rates** | Technology, Real Estate | Financials |
| **Stable Rates** | Momentum-based rotation | - |

### Economic Cycle

| Cycle Phase | Favor Sectors |
|-------------|---------------|
| **Early Recovery** | Financials, Technology, Industrials |
| **Mid Expansion** | Technology, Consumer Discretionary |
| **Late Cycle** | Energy, Materials, Industrials |
| **Recession** | Healthcare, Consumer Staples, Utilities |

---

## Summary: The Complete System

### Weekly Workflow

**Monday Morning Routine:**
1. Update all sector ETF prices and flows
2. Calculate RS (20-day, 60-day) for all sectors
3. Calculate momentum ranking (3M, 6M)
4. Check ETF flows (weekly change)
5. Calculate composite scores
6. Generate sector rotation map
7. Identify top 3-5 sectors

**Monthly Rebalancing (First Trading Day):**
1. Review portfolio vs current rankings
2. Exit bottom-ranked sectors
3. Enter top-ranked sectors
4. Adjust weights based on scores
5. Document trades and rationale

### Key Takeaways

✅ **Relative Strength** is the foundation (sector vs SPY)  
✅ **Momentum persists** → Follow winners, avoid losers  
✅ **Flows confirm price** → Trust sectors with inflows  
✅ **Breadth validates strength** → Avoid narrow leadership  
✅ **Rotation maps** → Visualize money movement  

🎯 **This system doesn't predict the future**  
🎯 **It tracks where capital is already moving**  
🎯 **Follow the money, not the narrative**

---

## Next Steps

1. **Build data pipeline:** Fetch daily sector ETF data
2. **Calculate core metrics:** RS, momentum, flows
3. **Create scoring model:** Composite sector score
4. **Build rotation map:** Quadrant visualization
5. **Backtest strategy:** Validate with historical data
6. **Deploy to web app:** Sector analysis tab
7. **Monitor & refine:** Track performance, adjust weights

---

**Last Updated:** 2026-06-21  
**Framework Version:** 1.0  
**Status:** Implementation Ready
