# Trading Analysis Reports

This directory stores your generated trading analysis reports.

## File Naming Convention

- **Full reports**: `Trading-Analysis-YYYY-MM-DD.md`
- **PDF versions**: `Trading-Analysis-YYYY-MM-DD.pdf`

## Report Contents

Each report typically includes:

1. **Executive Summary**
   - Overall trading success rate
   - Current portfolio value
   - Total unrealized and realized P&L
   - Number of holdings

2. **Transaction Statistics**
   - Buy/Sell/Dividend breakdown
   - Trade performance metrics
   - Win/loss rates

3. **Top Performers & Losers**
   - Best/worst buy trades (unrealized)
   - Best/worst sell trades (timing)
   - Best/worst realized trades (closed positions)

4. **Current Portfolio Holdings**
   - All current positions
   - Cost basis vs current value
   - Unrealized P&L by ticker

5. **Realized P&L Analysis**
   - FIFO-based closed position analysis
   - Win rate and average win/loss
   - Realized P&L by ticker and month

6. **Key Insights**
   - Trading patterns
   - Lessons learned
   - Areas for improvement

## Privacy Note

⚠️ **Reports in this directory are gitignored by default** to protect your personal financial information. Only commit anonymized or sample reports if needed for examples.

## Generating Reports

### Via Claude Code
```
Generate a comprehensive trading analysis from my trades CSV file
```

### Via Scripts
```bash
# From trades_analysis_skill directory
python scripts/analyze_trades.py trades.csv
python scripts/calculate_realized_pnl.py trades.csv
```

### Convert to PDF
```bash
# From project root
python utils/md_to_pdf.py "trades_analysis_skill/analyses/Trading-Analysis-2026-06-12.md"
```

## Sample Report Structure

```markdown
# Trading Performance Analysis Report

**Report Generated:** June 12, 2026 at 2:30 PM
**Analysis Period:** January 1, 2026 - June 12, 2026

---

## Executive Summary
...

## Summary Statistics
...

## Top 10 Best/Worst Trades
...

## Realized P&L Analysis
...

## Current Portfolio Holdings
...

## Key Insights
...
```
