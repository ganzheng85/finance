# Position Sizing Guide for Dip Buying

How to determine position size based on conviction, risk tolerance, and portfolio constraints.

---

## Position Sizing Framework

### The Conviction-Based Sizing Model

Position size should reflect:
1. **Conviction** (Bargain Test score)
2. **Portfolio size** (total capital)
3. **Risk tolerance** (max loss you can stomach)
4. **Diversification rules** (concentration limits)

---

## Sizing by Bargain Test Score

| Bargain Test Score | Conviction | Position Size | Max Portfolio % |
|-------------------|------------|---------------|-----------------|
| **5/5** | Very High | 7-10% | 10% |
| **4/5** | High | 4-7% | 7% |
| **3/5** | Medium | 2-4% | 5% |
| **2/5** | Low | 0-1% (avoid) | 2% (if you must) |
| **0-1/5** | None | 0% | 0% |

**Formula**: `Position Size = Base Size × Conviction Multiplier × Risk Adjustment`

---

## Example Calculations

### Scenario 1: High Conviction Dip Buy (4/5 Bargain Test)

**Inputs**:
- Portfolio value: $100,000
- Bargain Test score: 4/5 (High conviction)
- Risk tolerance: Moderate (can tolerate -30% position loss)
- Current positions: 5 stocks (20% per sector max)

**Position Size Calculation**:

**Step 1: Base Size** (from table above)
- Score 4/5 → 4-7% of portfolio
- Target: 5% of $100,000 = **$5,000 total position**

**Step 2: Entry Plan (1/3 - 1/3 - 1/3 rule)**
- Entry 1 (33%): $1,650 (1.65% of portfolio)
- Entry 2 (33%): $1,650 (1.65% of portfolio)
- Entry 3 (33%): $1,700 (1.70% of portfolio)
- **Total**: $5,000 (5% of portfolio)

**Step 3: Risk Check**
- Max loss tolerance: -30% on position = -$1,500
- As % of total portfolio: -$1,500 / $100,000 = **-1.5%**
- Acceptable? YES (less than -2% portfolio rule)

**Step 4: Sector Concentration Check**
- Is this position same sector as existing holdings?
- Current sector exposure + new position < 25%?
- If YES → OK to proceed
- If NO → Reduce size or skip

**Decision**: Buy $5,000 total (5% portfolio), split into 3 tranches of ~$1,650 each.

---

### Scenario 2: Very High Conviction (5/5 Bargain Test)

**Inputs**:
- Portfolio value: $200,000
- Bargain Test score: 5/5 (Meta 2022-style opportunity)
- Risk tolerance: Aggressive (can tolerate -40% position loss)
- Sector exposure: Low (this is only tech stock)

**Position Size Calculation**:

**Step 1: Base Size**
- Score 5/5 → 7-10% of portfolio
- Target: 8% of $200,000 = **$16,000 total position**

**Step 2: Entry Plan (Aggressive Pyramid)**
- Entry 1 (20%): $3,200 at -15% drop (1.6% of portfolio)
- Entry 2 (30%): $4,800 at -25% drop (2.4% of portfolio)
- Entry 3 (50%): $8,000 at -35% drop (4.0% of portfolio)
- **Total**: $16,000 (8% of portfolio)

*Note: Aggressive pyramid inverts sizes - buy MORE as it gets cheaper. Only for 5/5 conviction + fortress balance sheet.*

**Step 3: Risk Check**
- Max loss tolerance: -40% on position = -$6,400
- As % of total portfolio: -$6,400 / $200,000 = **-3.2%**
- Acceptable? YES for aggressive investor (< -5% limit)

**Decision**: Buy $16,000 total (8% portfolio), using aggressive pyramid (20%-30%-50%).

---

### Scenario 3: Medium Conviction (3/5 Bargain Test)

**Inputs**:
- Portfolio value: $50,000
- Bargain Test score: 3/5 (Mixed signals, uncertain)
- Risk tolerance: Conservative (can tolerate -20% position loss)

**Position Size Calculation**:

**Step 1: Base Size**
- Score 3/5 → 2-4% of portfolio
- Target: 2% of $50,000 = **$1,000 total position** (small starter)

**Step 2: Entry Plan (Conservative, 2 tranches only)**
- Entry 1 (50%): $500 at initial entry (1% of portfolio)
- Entry 2 (50%): $500 IF thesis strengthens (score → 4/5)
- Entry 3: SKIP (3/5 doesn't warrant full position)

**Step 3: Risk Check**
- Max loss tolerance: -20% on position = -$200
- As % of total portfolio: -$200 / $50,000 = **-0.4%**
- Acceptable? YES (minimal portfolio impact)

**Decision**: Buy $500 initially (1% portfolio). Add $500 more ONLY if thesis improves (re-run Bargain Test). If thesis weakens, exit at small loss.

---

## Portfolio-Level Position Limits

### Diversification Rules (Hard Limits)

| Limit Type | Max % | Rationale |
|------------|-------|-----------|
| **Single position** | 10% | Avoid concentration risk (one blow-up wipes out 10%+) |
| **Single sector** | 25% | Sector crashes happen (2000 tech, 2008 financials) |
| **Total dip-buying** | 40-50% | Don't put entire portfolio in falling knives |
| **International** | 30% | Currency, geopolitical, accounting risks |
| **Small caps** | 20% | Liquidity, volatility risks |
| **Speculative** | 10-15% | High-risk, high-reward (options, crypto, SPACs) |

**Example**: $100K portfolio
- Max single position: $10K (10%)
- Max tech sector: $25K (25%)
- Max total dip buys: $40-50K (40-50%)
- Keep $20-30K cash (20-30%) for more opportunities

**Why Limits Matter**: 
- GE 2017 at 10% position → lost -8% of portfolio (-80% stock price)
- GE 2017 at 25% position → lost -20% of portfolio (devastating)
- Limits prevent single mistakes from destroying portfolio

---

## Position Sizing Based on Volatility (Kelly Criterion)

**Advanced**: Use Kelly Criterion for mathematically optimal sizing.

**Kelly Formula**:
```
Position Size % = (Win Probability × Avg Win - Loss Probability × Avg Loss) / Avg Win
```

**Example**: Meta 2022 dip buy

**Inputs**:
- Win Probability: 60% (high conviction thesis works)
- Avg Win: +67% (bull case: $90 → $150)
- Loss Probability: 40% (thesis fails)
- Avg Loss: -25% (bear case: $90 → $67)

**Calculation**:
```
Kelly % = (0.60 × 67% - 0.40 × 25%) / 67%
        = (40.2% - 10%) / 67%
        = 30.2% / 67%
        = 45% of portfolio
```

**BUT**: Kelly is aggressive (assumes perfect information). Use **Half Kelly** or **Quarter Kelly**:
- Half Kelly: 45% / 2 = **22.5% position** (still too aggressive for most)
- Quarter Kelly: 45% / 4 = **11.25% position** (reasonable)

**Practical rule**: Kelly gives theoretical max. Cut it by 50-75% for real-world (uncertainty, black swans).

**For Meta 2022**: Kelly says 45%, but prudent investor uses 10-15% (quarter Kelly + diversification).

---

## Position Sizing by Risk Budget

**Alternative Approach**: Allocate based on **max portfolio loss** you'll tolerate.

**Example**: Conservative Investor

**Inputs**:
- Portfolio: $100,000
- Max portfolio loss tolerance: -3% (-$3,000)
- Stock expected volatility: -30% downside if thesis fails

**Calculation**:
```
Position Size = Max Portfolio Loss / Expected Stock Loss
             = $3,000 / 30%
             = $10,000 (10% of portfolio)
```

**Interpretation**: To risk only -3% of portfolio, can invest $10K in this stock (if it falls -30%, portfolio loses -3%).

**Example**: Aggressive Investor

**Inputs**:
- Portfolio: $200,000
- Max portfolio loss tolerance: -5% (-$10,000)
- Stock expected volatility: -40% downside if thesis fails

**Calculation**:
```
Position Size = $10,000 / 40%
             = $25,000 (12.5% of portfolio)
```

**But**: 12.5% exceeds 10% single-position limit. **Cap at $20K (10%)**.

---

## Entry Tranche Sizing (1/3 - 1/3 - 1/3 vs Alternatives)

### Standard: 1/3 - 1/3 - 1/3 (Equal Thirds)

**When to use**: Medium-to-high conviction (3-4/5), normal volatility.

**Example**: $6,000 position
- Entry 1: $2,000 (33%)
- Entry 2: $2,000 (33%)
- Entry 3: $2,000 (33%)

**Pros**: Balanced, reduces timing risk, flexible.
**Cons**: Miss optimal sizing if price only drops once.

---

### Aggressive: Inverted Pyramid (20% - 30% - 50%)

**When to use**: Very high conviction (5/5), fortress balance sheet, can tolerate -50% drop.

**Example**: $10,000 position
- Entry 1: $2,000 (20%) at -15% drop
- Entry 2: $3,000 (30%) at -25% drop
- Entry 3: $5,000 (50%) at -35% drop (if it gets there)

**Pros**: Maximize position at best prices (buy MORE when cheaper).
**Cons**: Risky - if thesis breaks at -40%, you're overexposed.

**Use case**: Meta 2022, NVDA 2018 (conviction thesis validated by later data).

---

### Conservative: Front-Load (50% - 30% - 20%)

**When to use**: Lower conviction (3/5), want exposure but cautious.

**Example**: $5,000 position
- Entry 1: $2,500 (50%) at initial entry
- Entry 2: $1,500 (30%) IF bounces (confirms thesis)
- Entry 3: $1,000 (20%) IF catalyst materializes

**Pros**: Get most exposure early, add only if confidence increases.
**Cons**: If price falls -30%, average cost is higher (bought most at top).

**Use case**: Uncertain thesis, want to "test the waters" with larger initial bet.

---

### Two-Tranche (50% - 50%)

**When to use**: Binary outcome (either thesis works or doesn't), no middle ground.

**Example**: $4,000 position
- Entry 1: $2,000 (50%) at initial drop
- Entry 2: $2,000 (50%) either:
  - **(A)** Bounces +15% (thesis confirmed), add
  - **(B)** Drops another -20% (deep value), add
  - **(C)** Thesis breaks → exit Entry 1 at small loss, skip Entry 2

**Pros**: Simpler than 3 tranches, clear decision points.
**Cons**: Less flexibility than 3 tranches.

**Use case**: Fast-moving situations (activist campaigns, M&A rumors, FDA approvals).

---

## Position Sizing Based on Account Size

### Small Account ($10K - $50K)

**Challenge**: Diversification vs minimum position size (hard to buy 10 stocks with $10K).

**Recommended**:
- **5-7 positions** (not 10-15)
- **Position size**: 10-20% each (larger than 10% rule, but necessary)
- **Focus**: Quality over quantity (3-4 high-conviction dips, not 10 mediocre ones)

**Example**: $25K account
- 5 positions × $5K each (20% each)
- Accept concentration risk (vs over-diversifying into weak ideas)

---

### Medium Account ($50K - $500K)

**Sweet spot**: Enough to diversify (8-12 positions) without over-diversification.

**Recommended**:
- **8-12 positions**
- **Position size**: 5-10% each (stick to 10% max rule)
- **Diversification**: 3-4 sectors, 2-3 geographies

**Example**: $200K account
- 10 positions × $20K each (10% each)
- Or 8 core positions ($15-25K) + 2 small speculative ($5-10K)

---

### Large Account ($500K+)

**Challenge**: Liquidity (hard to deploy $50-100K into small caps without moving price).

**Recommended**:
- **12-20 positions**
- **Position size**: 5-10% each, but favor liquid large caps
- **Diversification**: 5-6 sectors, international exposure

**Example**: $1M account
- 15 positions × $50-80K each (5-8% each)
- Focus on S&P 500 + large international (avoid small caps where $50K order moves price 5%)

---

## Position Sizing Mistakes to Avoid

### Mistake 1: "All-In" on First Dip

**Bad**: Stock drops -20%, you put entire 10% position in at once.

**Why bad**: If it drops another -20%, you're down -20% on 10% position = -2% portfolio loss, AND you have no capital to average down.

**Fix**: 1/3 - 1/3 - 1/3 rule. Enter gradually.

---

### Mistake 2: Over-Sizing on Low Conviction

**Bad**: Bargain Test score 2/5, but you buy 5% position because "it's cheap."

**Why bad**: Low conviction + large position = recipe for panic selling at bottom.

**Fix**: Match size to conviction. 2/5 = 0-1% max (or avoid entirely).

---

### Mistake 3: Ignoring Portfolio-Level Limits

**Bad**: You own 4 tech stocks (25% portfolio). You buy Meta dip (another 8%). Now 33% in tech.

**Why bad**: If tech sector crashes -30% (2022), you lose -10% of portfolio in one sector.

**Fix**: Check sector exposure BEFORE buying. If >25%, skip or trim existing holdings.

---

### Mistake 4: No Position Limits on Winners

**Bad**: Stock rallies +100%, now 18% of portfolio (was 8%). You don't trim.

**Why bad**: If stock crashes -50% from peak, you lose -9% of portfolio in one name.

**Fix**: Rebalance when position exceeds 10-12%. Trim back to 8-10%.

---

### Mistake 5: Averaging Down on Value Traps

**Bad**: GE drops -30%, you add more. Drops another -30%, you add more. Down -60% total.

**Why bad**: Thesis was broken (3+ Bargain Test fails), but you averaged down due to sunk cost fallacy.

**Fix**: Re-run Bargain Test every -10-15% drop. If score falls to 2/5, EXIT (don't add).

---

## Position Sizing Checklist

Before buying, confirm:

- [ ] Bargain Test score ≥ 3/5 (if 2/5, only 0-1% or avoid)
- [ ] Position size = score-appropriate % (5/5 → 7-10%, 4/5 → 4-7%, 3/5 → 2-4%)
- [ ] Single position < 10% of portfolio
- [ ] Sector exposure (existing + new) < 25% of portfolio
- [ ] Total dip-buying allocation < 50% of portfolio
- [ ] Max portfolio loss (if position -30%) < 3-5% acceptable
- [ ] Entry plan defined (1/3-1/3-1/3 or pyramid)
- [ ] Stop-loss set (-40-50% from average cost)
- [ ] Exit plan defined (sell 25% at +30%, 50% at fair value, etc.)

**If all boxes checked → Proceed with buy.**

---

## Position Sizing Calculator (Manual)

**Inputs**:
1. Portfolio value: $______
2. Bargain Test score: ___/5
3. Target position %: ____ % (from table)
4. Entry plan: [ ] Equal thirds [ ] Pyramid [ ] Front-load [ ] Two-tranche

**Calculations**:

**Total Position Size**: $______ = Portfolio Value × Target %

**Entry Tranches** (if using 1/3-1/3-1/3):
- Entry 1 (33%): $______ (___% of portfolio)
- Entry 2 (33%): $______ (___% of portfolio)
- Entry 3 (33%): $______ (___% of portfolio)

**Risk Check**:
- Expected loss if thesis fails: ___% (e.g., -30%)
- Max portfolio loss: $______ = Total Position × Expected Loss
- Max portfolio loss %: ___% = Max $ Loss / Portfolio Value
- Acceptable? [ ] Yes (< 3-5%) [ ] No (reduce size)

**Sector Check**:
- Current sector exposure: ___% of portfolio
- New position size: ___% of portfolio
- **Total sector after buy**: ___% (current + new)
- Within 25% limit? [ ] Yes [ ] No (reduce size or skip)

**Decision**:
- [ ] **BUY** - All checks passed
- [ ] **REDUCE SIZE** - Fails risk or sector check (new target: ___%)
- [ ] **AVOID** - Fails multiple checks or score <3/5

---

**Prepared for**: [Your Name]  
**Date**: [Date]  
**Review**: Re-run this calculator every new dip buy to maintain discipline.
