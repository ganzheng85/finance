# Weekly Sector Rotation Trading Checklist

## Every Friday After Market Close (4:00 PM ET)

### Step 1: Check Market Regime
**Determine if you should be 100% invested or 50% cash**

1. Look up SPY current price
2. Look up SPY 200-day moving average (MA200)
   - Use: https://stockcharts.com (enter "SPY")
   - Or your broker's chart (add SMA 200 indicator)

**Decision Rule:**
```
IF SPY > 200-day MA:
  → BULL MARKET MODE
  → You will invest 100% (33.33% per sector)
  
IF SPY < 200-day MA:
  → BEAR MARKET MODE
  → You will invest 50% (16.67% per sector)
  → Hold 50% cash
```

**Current Status (as of June 26, 2026):**
- SPY Price: $728.99
- 200-day MA: $686.84
- **Status: BULL MARKET (100% invested)**

---

### Step 2: Run Sector Analysis
**Identify top 3 ranked sectors**

1. Open terminal/command prompt
2. Run: `sector-analysis`
3. Look at the rankings table
4. Write down top 3 tickers

**Example Output:**
```
Rank 1: SMH (Semiconductors) - Score 88.5
Rank 2: XLI (Industrials) - Score 82.7
Rank 3: XLF (Financials) - Score 75.0
```

**Your Top 3:** ________________, ________________, ________________

---

### Step 3: Calculate Target Allocation

**If BULL MARKET (SPY > 200 MA):**
```
Total Portfolio Value: $__________
÷ 3 sectors = $__________ per sector (33.33% each)
Cash to hold: $0
```

**If BEAR MARKET (SPY < 200 MA):**
```
Total Portfolio Value: $__________
× 50% = $__________ to invest
÷ 3 sectors = $__________ per sector (16.67% each)
Cash to hold: $__________ (50%)
```

---

### Step 4: Compare to Current Holdings
**Do you need to rebalance?**

Check:
- [ ] Are top 3 sectors the same as last week?
- [ ] Did market regime change (bull to bear or vice versa)?

**If YES to either:** Proceed to Step 5 (rebalance on Monday)

**If NO to both:** Nothing to do, keep current positions

---

## Monday Morning (9:35 AM ET)
**Execute rebalancing trades (only if needed)**

### Step 5: Sell All Current Positions
**Liquidate everything to cash first**

Sell 100% of each current holding:
- [ ] Sector 1: Sell all shares
- [ ] Sector 2: Sell all shares
- [ ] Sector 3: Sell all shares

**Total Cash After Sales:** $__________

---

### Step 6: Buy New Top 3 Sectors

**Calculate shares to buy:**

For each sector:
```
Target $ Amount (from Step 3): $__________
÷ Current Share Price: $__________
= Shares to buy: __________
```

Execute buy orders:
- [ ] Sector 1 (______): Buy ______ shares @ $______ = $______
- [ ] Sector 2 (______): Buy ______ shares @ $______ = $______
- [ ] Sector 3 (______): Buy ______ shares @ $______ = $______

**Total Invested:** $__________
**Cash Remaining:** $__________ (should be ~0% in bull, ~50% in bear)

---

## Weekly Log

| Date | Market Regime | Top 3 Sectors | Allocation | Total Value | Notes |
|------|---------------|---------------|------------|-------------|-------|
| 2026-06-27 | BULL (100%) | SMH, XLI, XLF | 33.33% each | $_______ | |
| 2026-07-05 | | | | | |
| 2026-07-12 | | | | | |
| 2026-07-19 | | | | | |

---

## Key Reminders

### ✅ DO:
- Check every Friday without fail
- Execute rebalances on Monday morning
- Keep good records of trades
- Trust the system (no emotions)

### ❌ DON'T:
- Trade intra-week (only weekly rebalances)
- Override the 200-day MA signal
- Skip rebalances when regime changes
- Second-guess the top 3 sector rankings

---

## When Market Regime Changes

### Bull → Bear (SPY crosses below 200 MA):
**Action: Go 50% cash**

Example: You have $100,000 in 3 sectors
1. Sell all current positions → $100,000 cash
2. Buy new top 3 sectors with only $50,000 ($16,667 each)
3. Hold $50,000 cash (protection)

### Bear → Bull (SPY crosses above 200 MA):
**Action: Reinvest cash**

Example: You have $50,000 cash + $50,000 in sectors
1. Sell all current positions → $100,000+ cash
2. Buy new top 3 sectors with $100,000 ($33,333 each)
3. Hold $0 cash (fully invested)

---

## Quick Reference

**Market Regime Check:**
- SPY > 200 MA = 100% invested (33.33% x 3)
- SPY < 200 MA = 50% cash + 50% invested (16.67% x 3)

**Rebalance Frequency:**
- Every week (Friday analysis, Monday execution)

**Transaction Costs:**
- ~0.1% per trade (built into backtest results)

**Expected Performance:**
- Bull markets: ~+20% per 6 months
- Bear markets: ~-1% (vs SPY -15%)
- Crashes: ~-14% (vs SPY -31%)

---

## Questions?

**Q: What if I forget to check one Friday?**
A: Check on Monday before market open. Better late than never.

**Q: What if I can't trade on Monday?**
A: Trade Tuesday morning. One day won't matter much.

**Q: Can I adjust the 200-day MA to 150 or 250?**
A: Stick with 200 - it's battle-tested and widely followed.

**Q: Should I rebalance if only 1 sector changed in top 3?**
A: Yes. Sell all 3, buy new top 3. Full rebalance every time.

---

*Last Updated: June 27, 2026*
