---
name: trades-analysis
description: Comprehensive trading performance analysis. Use when analyzing portfolio trades, calculating realized/unrealized P&L, evaluating trading decisions, and assessing win/loss rates using FIFO methodology.
---

# Trades Analysis Skill

Produces comprehensive trading performance analysis focusing on transaction history, profit/loss metrics, win rates, and portfolio performance. Analyzes both realized gains (closed positions) and unrealized gains (current holdings).

## Workflow

1. **Confirm the data source**
   - Get path to trades CSV file
   - Verify CSV format: Date, Transaction Type (Buy/Sell), Stock/ETF Symbol, Quantity, Amount per unit, Total Amount
   - Check date range coverage

2. **Run the analysis scripts**
   - **Unrealized P&L Analysis**: `python scripts/analyze_trades.py [CSV_FILE]`
     - Fetches current prices from Yahoo Finance
     - Analyzes current holdings vs purchase/sale prices
     - Calculates portfolio value and unrealized P&L
     - Identifies best/worst trading decisions
   
   - **Realized P&L Analysis**: `python scripts/calculate_realized_pnl.py [CSV_FILE]`
     - Uses FIFO (First In First Out) methodology
     - Matches buy-sell pairs chronologically
     - Calculates actual realized gains/losses
     - Provides win/loss statistics and ratios

3. **Generate comprehensive report**
   - Use the analysis template structure
   - Include both realized and unrealized metrics
   - Highlight top performers and worst performers
   - Provide actionable insights

4. **Save outputs**
   - Save markdown report to `analyses/Trading-Analysis-YYYY-MM-DD.md`
   - Convert to PDF using `python ../utils/md_to_pdf.py` (shared utility)
   - Keep CSV data in root for easy re-analysis

## Analysis Components

### 1. Transaction Overview
- Total transactions by type (Buy, Sell, Dividend)
- Number of unique tickers traded
- Date range of trading activity
- Total capital deployed

### 2. Unrealized P&L Analysis (Current Holdings)
**What it measures**: Performance of positions you still own

**Fractional Position Filtering**: Positions with ≤2 shares are automatically filtered out from current holdings analysis to exclude:
- Stock split remnants
- Dividend reinvestment fractional shares
- Data rounding artifacts
These fractional positions are noted but excluded from portfolio calculations.

- **Current portfolio value** vs cost basis
- **Unrealized P&L** (paper gains/losses)
- **Best buy trades**: Biggest unrealized gains
- **Worst buy trades**: Biggest unrealized losses
- **Best sell trades**: Sold before price declined (avoided losses)
- **Worst sell trades**: Sold too early (missed gains)
- **Holdings breakdown**: Ticker-by-ticker performance

**Output**: Portfolio snapshot with current market value

### 3. Realized P&L Analysis (Closed Positions)
**What it measures**: Actual profits/losses from completed trades

Uses **FIFO (First In First Out)** methodology:
- Matches oldest buy with each sell chronologically
- Calculates actual realized gains/losses
- Tracks win/loss statistics
- Analyzes by ticker and by month

**Key Metrics**:
- **Total realized P&L**: Actual money made/lost
- **Win rate**: Percentage of profitable trades
- **Average win** vs **Average loss**
- **Win/Loss ratio**: Quality of wins vs losses
- **Best/Worst realized trades**: Actual closed positions

**Output**: Historical trading performance

### 4. S&P 500 Performance Comparison
**What it measures**: How your portfolio performed vs the S&P 500 benchmark

Compares your portfolio performance against buying and holding SPY (S&P 500 ETF):

- **SPY return**: S&P 500 performance over the analysis period
- **Portfolio return**: Your unrealized P&L percentage
- **Alpha**: Excess return vs benchmark (positive = outperformance)
- **Benchmark value**: What your capital would be worth if invested in SPY
- **Value difference**: Dollar amount gained or lost vs SPY strategy

**Key Metrics**:
- **Outperforming**: Alpha > 0% (beating the market)
- **Underperforming**: Alpha < 0% (trailing the market)
- **Matching**: Alpha ≈ 0% (market performance)

**Output**: Clear performance comparison showing if active trading beat passive investing

### 5. Overall Trading Performance
Combines unrealized and realized analysis:

- **Overall success rate**: Good trades vs bad trades
- **Buy trade performance**: Currently profitable positions %
- **Sell trade performance**: Good exit timing %
- **Top performers by ticker**: Which stocks worked best
- **Areas of concern**: Repeated losses in specific tickers

### 6. Trading Insights
Identify patterns and lessons:
- **Best decisions**: What trades worked and why
- **Missed opportunities**: Sold too early, missed gains
- **Timing analysis**: Good vs bad entry/exit points
- **Sector/ticker patterns**: What works, what doesn't
- **Risk assessment**: Concentration risk, volatility exposure

## Output Structure

```
trades_analysis_skill/
├── SKILL.md                                    # This file
├── README.md                                   # Documentation
├── scripts/
│   ├── analyze_trades.py                       # Unrealized P&L analysis
│   └── calculate_realized_pnl.py               # Realized P&L (FIFO)
├── analyses/
│   ├── Trading-Analysis-YYYY-MM-DD.md          # Full report (markdown)
│   ├── Trading-Analysis-YYYY-MM-DD.pdf         # Full report (PDF)
│   └── ...                                     # Historical reports
└── [CSV files at root]                         # Trade data files
```

## Output Format

### Comprehensive Trading Analysis Report

```markdown
# Trading Performance Analysis Report

**Report Generated:** [DATE] at [TIME]
**Analysis Period:** [START_DATE] - [END_DATE]

---

## Executive Summary

- **Overall Trading Success Rate:** [X]% good trades
- **Current Portfolio Value:** $[X]
- **Total Unrealized P&L:** $[X] ([±X]%)
- **Total Realized P&L:** $[X] ([±X]%)
- **Number of Current Holdings:** [X] tickers

---

## Summary Statistics

### Transaction Breakdown
[Table showing Buy/Sell/Dividend counts]

### Buy Trades Performance (Currently Held Positions)
[Table with good/bad trade statistics]

### Sell Trades Performance (Exited Positions)
[Table with good/bad exit timing]

### Realized Trades Performance (Closed Positions - FIFO)
[Table with win rate, total realized P&L, average win/loss]

---

## Top 10 Best Buy Trades (Biggest Unrealized Gains)
[Table with ticker, buy price, current price, gain %]

## Top 10 Worst Buy Trades (Biggest Unrealized Losses)
[Table with ticker, buy price, current price, loss %]

## Top 10 Best Sell Trades (Good Exit Timing)
[Table showing avoided losses by selling before decline]

## Top 10 Worst Sell Trades (Sold Too Early)
[Table showing missed gains by selling too early]

---

## Realized Profit/Loss Analysis (FIFO Method)

### Summary
- Total Realized Trades: [X]
- Winning Trades: [X] ([X]%)
- Losing Trades: [X] ([X]%)
- Total Realized P&L: $[X]
- Win Rate: [X]%
- Win/Loss Ratio: [X]

### Top 10 Best Realized Trades
[Table with buy date, sell date, quantity, buy/sell price, realized P&L]

### Top 10 Worst Realized Trades
[Table with buy date, sell date, quantity, buy/sell price, realized loss]

### Realized P&L by Ticker
[Table showing which tickers were most/least profitable]

### Realized P&L by Month
[Table showing monthly trading performance]

---

## Current Portfolio Holdings

[Table with all current positions showing:
- Ticker, Quantity, Avg Cost, Current Price
- Current Value, Unrealized P&L, P&L %]

**TOTAL**: Cost Basis vs Current Value vs Unrealized P&L

---

## Key Insights

### Top Performers (Current Holdings)
[List top 3-5 with returns and $ gains]

### Biggest Losers (Current Holdings)
[List bottom 3-5 with losses and $ losses]

### Trading Insights
- **Best Selling Decisions:** [Examples]
- **Missed Opportunities:** [Examples]
- **Current Winners:** [Patterns]
- **Areas of Concern:** [Problem areas]

### Lessons Learned
- [Key pattern 1]
- [Key pattern 2]
- [Key pattern 3]

---

## Methodology

**Data Source:** Yahoo Finance (yfinance library)
**Analysis Date:** [DATE]
**Realized P&L Method:** FIFO (First In First Out)

**Good Trade Definition:**
- **Buy Trades:** Current price > Purchase price (unrealized gain)
- **Sell Trades:** Sell price > Current price (avoided decline or sold high)
- **Realized Trades:** Sell price > Buy price (actual profit)

**Bad Trade Definition:**
- **Buy Trades:** Current price < Purchase price (unrealized loss)
- **Sell Trades:** Sell price < Current price (sold too early, missed gains)
- **Realized Trades:** Sell price < Buy price (actual loss)

---

*This report is for informational purposes only and does not constitute financial advice.*
```

## CSV File Format

The skill expects a CSV file with these columns:
- `Date (MM-DD-YYYY)`: Transaction date
- `Transaction Type`: Buy, Sell, Dividend, etc.
- `Stock / ETF Symbol`: Ticker symbol
- `Quantity of Units`: Number of shares
- `Amount per unit`: Price per share
- `Total Amount (before trading fees)`: Total transaction value

Example:
```csv
Date (MM-DD-YYYY),Transaction Type,Stock / ETF Symbol,Quantity of Units,Amount per unit,Total Amount (before trading fees)
06-01-2026,Buy,AAPL,100,150.00,15000.00
06-05-2026,Sell,AAPL,50,155.00,7750.00
```

## Dependencies

```bash
pip install pandas yfinance
```

Optional (for PDF conversion):
```bash
pip install markdown xhtml2pdf
```

## Usage Examples

### Example 1: Analyze Recent Trades
```
Analyze my trades from the CSV file trades_20260611.csv
```

Claude will run both analysis scripts and generate a comprehensive report.

### Example 2: Update Existing Analysis
```
Generate an updated trading analysis with current prices
```

Claude will re-fetch current prices and update the analysis.

### Example 3: Focus on Specific Metrics
```
What's my realized P&L and win rate?
```

Claude will run the realized P&L script and provide summary statistics.

### Example 4: Portfolio Performance
```
Show me my current portfolio value and top holdings
```

Claude will run the unrealized P&L analysis and show current positions.

## Best Practices

1. **Keep CSV updated**: Regularly add new transactions
2. **Run analysis monthly**: Track performance over time
3. **Compare periods**: Look at month-over-month changes
4. **Learn from mistakes**: Analyze worst trades to avoid patterns
5. **Validate winners**: Ensure best trades weren't just luck
6. **Monitor concentration**: Check if portfolio is too concentrated

## Rules and Filters

- Always fetch current prices for unrealized P&L (stale data = bad analysis)
- Use FIFO methodology for realized P&L (tax-compliant in most jurisdictions)
- Distinguish between unrealized (paper) and realized (actual) gains
- Account for transaction fees when available
- Exclude non-trade transactions (dividends, transfers) from trade analysis
- **Ticker normalization:** All tickers normalized to UPPERCASE to prevent "SMH" and "smh" being treated as different stocks
- **Stable sort:** Use `kind='stable'` when sorting by date to preserve original CSV order for same-day trades (critical for FIFO accuracy)

## Common Pitfalls to Avoid

- Confusing unrealized gains with realized gains
- Anchoring on purchase price instead of analyzing current opportunity
- Ignoring transaction costs and taxes
- Overweighting recent performance vs long-term track record
- Chasing winners without understanding why they worked
- Repeating losing patterns without learning

## Notes

This skill is for performance tracking and learning, not financial advice. Always:
- Track both realized and unrealized performance
- Learn from both wins and losses
- Understand why trades worked or didn't work
- Adjust strategy based on data, not emotion
- Consider tax implications of trading decisions
- Maintain proper records for tax reporting

## Integration with Other Skills

- **stock-analysis**: Use to evaluate stocks before buying
- **Portfolio optimization**: Use trading data to improve allocation
- **Tax planning**: Use realized P&L for tax-loss harvesting
