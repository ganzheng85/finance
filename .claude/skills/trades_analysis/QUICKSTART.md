# Quick Start Guide - Trades Analysis Skill

Get started analyzing your trading performance in 5 minutes!

## 1️⃣ Install Dependencies (1 minute)

```bash
pip install pandas yfinance
```

## 2️⃣ Prepare Your Data (2 minutes)

**Option A: Use your existing CSV**
- Make sure it has these columns: `Date (MM-DD-YYYY)`, `Transaction Type`, `Stock / ETF Symbol`, `Quantity of Units`, `Amount per unit`, `Total Amount (before trading fees)`
- Place it in the `trades_analysis_skill` folder

**Option B: Use the sample template**
- Copy `sample_trades.csv` and add your trades
- Or export from your broker and reformat

## 3️⃣ Run Analysis (1 minute)

### Quick Portfolio Check (Unrealized P&L)
```bash
cd trades_analysis_skill
python scripts/analyze_trades.py your_trades.csv
```

**What you'll see:**
- Current portfolio value
- Unrealized P&L (paper gains/losses)
- Best/worst current holdings
- Ticker-by-ticker breakdown

### Tax-Ready Report (Realized P&L)
```bash
python scripts/calculate_realized_pnl.py your_trades.csv
```

**What you'll see:**
- Actual realized gains/losses (FIFO method)
- Win rate and win/loss ratio
- Best/worst closed trades
- P&L by ticker and by month

## 4️⃣ Generate Full Report (1 minute)

### Via Claude Code (Recommended)
```
Analyze my trades from your_trades.csv and create a comprehensive report
```

Claude will:
- ✅ Run both analysis scripts
- ✅ Generate markdown report
- ✅ Convert to PDF
- ✅ Save to `analyses/Trading-Analysis-YYYY-MM-DD.md`

### Manually Convert to PDF
```bash
# From project root
python utils/md_to_pdf.py "trades_analysis_skill/analyses/Trading-Analysis-2026-06-12.md"
```

## 🎯 What You Get

### Unrealized P&L Analysis
```
Current holdings: 43 tickers
Total Cost Basis: $2,256,737.65
Current Value: $2,276,296.31
Unrealized P&L: $+19,558.66 (+0.87%)

Top Winners:
1. mrvl: +289.60% ($6,259.80)
2. EOG: +103.79% ($6,953.42)
3. smh: +100.81% ($15,297.36)
```

### Realized P&L Analysis
```
Total Realized Trades: 138
Winning Trades: 80 (58.0%)
Losing Trades: 58 (42.0%)
Total Realized P&L: $+12,345.67
Win Rate: 58.0%
Win/Loss Ratio: 1.45
```

### Complete Report
- 📊 Executive summary with key metrics
- 📈 Transaction statistics
- 🏆 Top 10 best/worst trades
- 💼 Current portfolio holdings
- 💰 Realized P&L breakdown
- 💡 Trading insights and lessons learned

## 🔍 Example Questions to Ask Claude

Once the skill is set up, try these:

1. **"What's my current portfolio value and unrealized P&L?"**
   - Quick check on current holdings

2. **"Show me my realized gains and losses for tax purposes"**
   - FIFO-based calculations ready for tax reporting

3. **"What are my best and worst trading decisions?"**
   - Learn from winners and losers

4. **"Generate a comprehensive trading analysis report"**
   - Full analysis with all metrics

5. **"Which tickers have been most profitable for me?"**
   - Identify your successful patterns

6. **"What's my win rate and how does it compare month-by-month?"**
   - Track performance trends over time

## 📁 File Structure After Setup

```
trades_analysis_skill/
├── README.md              ← Full documentation
├── SKILL.md               ← Skill definition for Claude
├── QUICKSTART.md          ← This file!
├── sample_trades.csv      ← Template (not gitignored)
├── your_trades.csv        ← Your data (gitignored for privacy)
├── scripts/
│   ├── analyze_trades.py         ← Unrealized P&L
│   └── calculate_realized_pnl.py ← Realized P&L (FIFO)
└── analyses/
    ├── Trading-Analysis-2026-06-11.md  ← Sample report
    ├── Trading-Analysis-2026-06-12.md  ← Your reports
    └── *.pdf                           ← PDF versions
```

## ⚠️ Privacy Note

Your trading data is **automatically gitignored** to protect your financial privacy:
- ✅ `*.csv` files (except `sample_trades.csv`)
- ✅ Reports in `analyses/` directory
- ✅ PDF outputs

Only the skill code and templates are version controlled.

## 🚀 Next Steps

1. **Regular Analysis**: Run monthly to track progress
2. **Learn Patterns**: Study your best/worst trades
3. **Optimize**: Use insights to improve future decisions
4. **Tax Planning**: Use realized P&L for tax-loss harvesting
5. **Share**: Export PDF reports for records

## 🆘 Need Help?

- 📖 See [README.md](README.md) for detailed documentation
- 🐛 Check troubleshooting section in README
- 💬 Ask Claude: "Help me analyze my trading data"

---

**Time to first insight: ~5 minutes**  
**Time to full report: ~10 minutes**  

Happy analyzing! 📊💹
