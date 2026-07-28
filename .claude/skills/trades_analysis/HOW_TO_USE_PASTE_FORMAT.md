# How to Analyze Trades by Pasting (Quick Method)

This is the fastest way to get comprehensive trade analysis without preparing CSV files.

## 📋 Method 1: Direct Paste (What You've Been Doing)

**Just ask Claude:**

```
Help analyze my [TICKER] trades:

date	action	ticker	quantity	price
05-07-2026	Buy	MSFT	200.00	548.80
05-07-2026	Sell	MSFT	100.00	538.83
...
```

**Claude will automatically:**
1. ✅ Use Agent tool to run FIFO analysis
2. ✅ Fetch current prices from Yahoo Finance
3. ✅ Calculate realized P&L (closed trades)
4. ✅ Calculate unrealized P&L (current holdings)
5. ✅ Show best/worst trades
6. ✅ Provide recommendations (hold/sell/add)

**Output:**
- Comprehensive analysis in ~30 seconds
- No CSV file needed
- No manual scripting

---

## 📊 Method 2: Use the Skill Directly (For Regular Analysis)

### Step 1: Prepare CSV File

Save your trades as CSV:

```csv
date,action,ticker,quantity,price
2026-05-07,Buy,MSFT,200.00,548.80
2026-05-07,Sell,MSFT,100.00,538.83
2026-05-08,Buy,MSFT,100.00,556.99
```

Place in: `.claude/skills/trades_analysis/data/my_trades.csv`

### Step 2: Run Analysis

**Quick Portfolio Check:**
```bash
cd .claude/skills/trades_analysis
python scripts/analyze_trades.py data/my_trades.csv
```

**Realized P&L (FIFO):**
```bash
python scripts/calculate_realized_pnl.py data/my_trades.csv
```

**Full Report via Claude:**
```
Analyze my trades from .claude/skills/trades_analysis/data/my_trades.csv
```

---

## 🎯 What Analysis Includes

### Realized P&L (Closed Trades)
- Total realized profit/loss
- Win rate (% of profitable trades)
- Average win vs average loss
- Best/worst closed trades
- P&L by ticker and by month

### Unrealized P&L (Current Holdings)
- Current position value
- Cost basis vs current price
- Paper gains/losses
- Best/worst current holdings
- Breakeven prices needed

### Trading Insights
- Which stocks you trade well
- Which stocks you should avoid
- Sell timing analysis (sold too early?)
- Buy timing analysis (bought too high?)
- Position sizing recommendations

---

## 💡 Example: Your SMH Analysis

**What you paste:**
```
date	action	ticker	quantity	price
05-07-2026	Buy	smh	200.00	548.80
05-07-2026	Sell	smh	100.00	538.83
06-22-2026	Buy	smh	100.00	665.19
07-17-2026	Buy	smh	50.00	545.53
```

**What you get:**
```
SMH Trade Analysis
==================

Current Position:
- Shares: 617.16 @ $615.27 avg
- Current Price: $584.18
- Unrealized P&L: -$20,741 (-5.05%)

Realized P&L:
- Total Realized: +$19,132
- Win Rate: 54.5%
- Best Trade: Jun 3 (+$6,819)
- Worst Trade: Jun 25 (-$4,045)

Recommendations:
1. Hold until $615 (breakeven)
2. Set limit sell: 25% @ $640
3. Consider adding if dips to $565
```

---

## 🚀 Quick Commands

### Analyze Any Stock
```
Analyze my [TICKER] trades:
[paste trades here]
```

### Compare Multiple Stocks
```
Compare my trading performance on MSFT vs SMH vs META
```

### Get Specific Metrics
```
What's my realized P&L and win rate on SMH?
```

### Get Recommendations
```
Should I hold or sell my SMH position?
```

---

## 📁 File Format Reference

### Your Format (Tab-separated)
```
date	action	ticker	quantity	price	value	market_price
05-07-2026	Buy	smh	200.00	548.80	109,760.00	584.18
```

**✅ This works!** Claude will parse it automatically.

### Standard CSV Format
```csv
date,action,ticker,quantity,price
2026-05-07,Buy,SMH,200.00,548.80
```

**✅ This also works!**

### Broker Export Format
```csv
Date (MM-DD-YYYY),Transaction Type,Stock / ETF Symbol,Quantity of Units,Amount per unit
05-07-2026,Buy,SMH,200.00,548.80
```

**✅ This works too!**

**Claude is flexible - just paste your trades and ask for analysis!**

---

## 🎯 Pro Tips

1. **Include current price** if you know it:
   ```
   Analyze SMH trades (current price: $584.18):
   [paste trades]
   ```

2. **Ask specific questions**:
   ```
   Did I sell SMH too early? Show me what I missed.
   ```

3. **Request scenarios**:
   ```
   If SMH goes to $650, what's my profit? Should I add more now?
   ```

4. **Get comparisons**:
   ```
   Compare my SMH vs MSFT trading - which am I better at?
   ```

---

## 📊 Sample Output

```markdown
# SMH Trade Analysis

## Position Summary
- **Shares**: 667.16 @ $615.27 avg
- **Current**: $584.18
- **Value**: $389,742
- **P&L**: -$20,741 (-5.05%)

## Realized Trades
- **Profit**: +$19,132
- **Trades**: 22 (12 wins, 10 losses)
- **Win Rate**: 54.5%
- **Best**: Jun 3 sell (+$6,819)

## Current Holdings
- **Profitable Lots**: 165 shares (+$3,253)
  - Jul 17 @ $545.53: +7.1%
  - Jul 7 @ $571.75: +2.2%
- **Underwater Lots**: 502 shares (-$23,994)
  - Jun 22 @ $665.19: -12.2%

## Recommendations
1. ✅ Hold to $615 (breakeven)
2. 📈 Set limit sell 25% @ $640
3. 💰 Consider adding @ $565 if dips
4. 🚫 Don't panic sell (already recovered from $552)
```

---

## 🆘 Troubleshooting

**Q: Claude says "file not found"**
- A: Just paste trades directly, no file needed

**Q: Wrong current price**
- A: Specify: "current price is $XXX" in your request

**Q: Want to save analysis**
- A: Claude auto-saves to `.claude/skills/trades_analysis/analyses/`

**Q: Need PDF version**
- A: Ask: "Convert this to PDF"

---

**That's it! Just paste and ask. Claude handles the rest.** 🚀
