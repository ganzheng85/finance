# Trades Analysis Skill - Overview

## 🎯 What This Skill Does

Analyzes your trading performance using two complementary approaches:

### 1. **Unrealized P&L Analysis** (Current Holdings)
What you own right now and how it's performing
- Current portfolio value vs cost basis
- Paper gains/losses on each position
- Best/worst current holdings
- Positions that would profit if sold today

### 2. **Realized P&L Analysis** (Closed Positions)
What you actually made or lost on completed trades
- FIFO (First In First Out) methodology
- Actual gains/losses after selling
- Win rate and win/loss ratio
- Trading performance by ticker and month

## 📊 Key Features

✅ **Comprehensive Metrics**
- Overall trading success rate
- Win/loss rates and ratios
- Portfolio value tracking
- Monthly performance trends

✅ **Actionable Insights**
- Best/worst trade identification
- Pattern recognition (what works, what doesn't)
- Timing analysis (good vs bad exits)
- Concentration risk assessment

✅ **Tax-Ready Reports**
- FIFO-based calculations
- Realized gains/losses for tax reporting
- Transaction-level detail
- Monthly P&L breakdown

✅ **Privacy Protected**
- All trade data gitignored by default
- No sensitive information committed
- Local-only analysis
- Secure and private

## 🚀 Quick Usage

### Run Analysis Scripts

```bash
# Check current portfolio (unrealized P&L)
python scripts/analyze_trades.py your_trades.csv

# Calculate realized gains/losses (FIFO)
python scripts/calculate_realized_pnl.py your_trades.csv
```

### Generate Full Report via Claude

```
Analyze my trades from trades_for_analysis.csv and create a comprehensive report
```

### Convert to PDF

```bash
python ../utils/md_to_pdf.py "analyses/Trading-Analysis-2026-06-12.md"
```

## 📈 Sample Output

### Unrealized P&L Summary
```
Current Portfolio Value: $2,276,296.31
Total Cost Basis: $2,256,737.65
Unrealized P&L: $+19,558.66 (+0.87%)
Number of Holdings: 43 tickers

Top Performers:
- mrvl: +289.60% ($6,259.80 gain)
- EOG: +103.79% ($6,953.42 gain)
- smh: +100.81% ($15,297.36 gain)

Biggest Losers:
- CQQQ: -30.73% ($-8,437.33 loss)
- WB: -27.95% ($-2,963.22 loss)
```

### Realized P&L Summary
```
Total Realized Trades: 138
Winning Trades: 80 (58.0%)
Losing Trades: 58 (42.0%)

Total Realized P&L: $+12,345.67
Average Winning Trade: $+245.50
Average Losing Trade: $-123.25
Win/Loss Ratio: 1.99

Best Trade: VIXY sold for +43.83% ($2,500 gain)
Worst Trade: SNOW sold too early, missed 37.09% gain
```

## 🛠️ What Was Created

### Core Files (4)
1. **SKILL.md** (300+ lines)
   - Skill definition for Claude Code
   - Detailed workflow and analysis components
   - Output format specifications

2. **README.md** (400+ lines)
   - Complete documentation
   - Installation instructions
   - Usage examples and troubleshooting

3. **QUICKSTART.md** (200+ lines)
   - 5-minute getting started guide
   - Example questions for Claude
   - Quick reference

4. **CHANGELOG.md** (100+ lines)
   - Version history
   - Feature roadmap
   - Planned enhancements

### Analysis Scripts (2)
1. **scripts/analyze_trades.py**
   - Fetches current prices from Yahoo Finance
   - Calculates unrealized P&L
   - Identifies best/worst trades
   - Generates portfolio holdings report

2. **scripts/calculate_realized_pnl.py**
   - FIFO methodology for cost basis
   - Matches buy-sell pairs chronologically
   - Calculates realized gains/losses
   - Provides win/loss statistics

### Supporting Files
- **.gitignore**: Protects your financial data
- **sample_trades.csv**: Template for new users
- **analyses/README.md**: Report directory guide
- **analyses/.gitkeep**: Maintains directory structure

### Sample Data
- **trades_for_analysis.csv**: Your existing trade data (365 transactions)
- **Trading-Analysis-2026-06-11.md**: Sample analysis report

## 📚 Documentation Pages

| File | Purpose | Lines | Key Content |
|------|---------|-------|-------------|
| SKILL.md | Claude integration | 317 | Workflow, components, output format |
| README.md | User guide | 404 | Installation, usage, troubleshooting |
| QUICKSTART.md | Quick start | 180 | 5-min setup, example questions |
| CHANGELOG.md | Version history | 79 | Features, roadmap, future plans |
| OVERVIEW.md | This file | ~200 | High-level summary |

**Total**: 1,437 lines of code and documentation

## 🎓 Learning from Your Trades

### Questions This Skill Answers

**Performance Tracking:**
- What's my current portfolio value?
- Am I making money overall?
- What's my win rate?

**Trade Analysis:**
- Which were my best/worst trades?
- Am I selling too early or too late?
- Which stocks work best for my strategy?

**Pattern Recognition:**
- Do I have repeated mistakes?
- What sectors perform well for me?
- Am I improving over time?

**Tax Planning:**
- What are my realized gains/losses?
- Which trades do I report this year?
- Should I harvest losses?

## 🔄 Integration with Other Skills

### Works Well With:
- **stock-analysis**: Research before buying
- **portfolio-optimizer**: Optimize allocation
- **tax-planner**: Plan tax-loss harvesting

### Workflow:
1. Use **stock-analysis** to evaluate potential buys
2. Execute trades and record in CSV
3. Use **trades-analysis** to track performance
4. Use insights to refine strategy
5. Repeat and improve

## 🛡️ Privacy & Security

Your financial data is protected:

✅ **Auto-gitignored**
- All `*.csv` files (except sample)
- All reports in `analyses/`
- All PDF outputs

✅ **Local Processing**
- Analysis runs on your machine
- No data sent to external services (except Yahoo Finance for prices)
- Full control over your data

✅ **Selective Sharing**
- Only share sanitized/anonymized reports if needed
- Keep sensitive data local
- Use sample data for examples

## 🎯 Next Steps

### Immediate (Today):
1. ✅ Review [QUICKSTART.md](QUICKSTART.md) (5 min)
2. ✅ Run test analysis on existing data
3. ✅ Generate your first report

### Short-term (This Week):
1. Ensure all recent trades are in CSV
2. Run monthly analysis
3. Review best/worst trades
4. Identify patterns to improve

### Long-term (Ongoing):
1. Run analysis quarterly
2. Track performance trends
3. Refine trading strategy
4. Consider adding custom metrics

## 📞 Getting Help

- 📖 See [README.md](README.md) for detailed docs
- 🚀 See [QUICKSTART.md](QUICKSTART.md) for quick start
- 🐛 Check troubleshooting section in README
- 💬 Ask Claude: "Help me analyze my trading performance"

## 🎉 Summary

**You now have a complete trading analysis skill that:**
- ✅ Tracks both unrealized and realized P&L
- ✅ Uses tax-compliant FIFO methodology
- ✅ Provides actionable insights
- ✅ Protects your financial privacy
- ✅ Integrates with Claude Code
- ✅ Exports to professional PDF reports

**Total build:**
- 📁 10+ files created
- 🐍 2 Python analysis scripts
- 📄 1,437 lines of code + docs
- ⏱️ Ready to use in 5 minutes

---

**Version**: 1.0.0  
**Created**: 2026-06-12  
**Based on**: trading_analysis_report.md and existing scripts  
**Compatible with**: Claude Code, stock-analysis skill, utils/md_to_pdf.py
