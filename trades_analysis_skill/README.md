# Trades Analysis Skill

A comprehensive skill for analyzing trading performance with focus on:
- **Unrealized P&L** (current holdings performance)
- **Realized P&L** (closed positions using FIFO methodology)
- **Win/loss statistics** and trading patterns
- **Portfolio performance tracking**
- **Best/worst trade identification**

## Quick Start

### 1. Install Dependencies

```bash
# Required for data analysis and price fetching
pip install pandas yfinance

# Optional: For PDF conversion
pip install markdown xhtml2pdf
```

### 2. Prepare Your Trades CSV

Your CSV should have these columns:
- `Date (MM-DD-YYYY)`: Transaction date
- `Transaction Type`: Buy, Sell, Dividend, etc.
- `Stock / ETF Symbol`: Ticker symbol
- `Quantity of Units`: Number of shares
- `Amount per unit`: Price per share
- `Total Amount (before trading fees)`: Total transaction value

Example:
```csv
Date (MM-DD-YYYY),Transaction Type,Stock / ETF Symbol,Quantity of Units,Amount per unit,Total Amount (before trading fees)
02-06-2026,Buy,AAPL,100,150.00,15000.00
03-15-2026,Sell,AAPL,50,155.00,7750.00
04-20-2026,Buy,MSFT,75,300.00,22500.00
```

### 3. Run Unrealized P&L Analysis

Analyzes current holdings vs purchase/sale prices:

```bash
# Basic usage
python scripts/analyze_trades.py trades.csv

# Or let it use default filename
python scripts/analyze_trades.py
```

**What it shows:**
- Current portfolio value and unrealized P&L
- Best/worst buy trades (current holdings)
- Best/worst sell trades (exit timing)
- Ticker-by-ticker holdings breakdown

### 4. Run Realized P&L Analysis

Calculates actual profits/losses from closed positions using FIFO:

```bash
# Basic usage
python scripts/calculate_realized_pnl.py trades.csv

# Or let it use default filename
python scripts/calculate_realized_pnl.py
```

**What it shows:**
- Total realized P&L from closed trades
- Win rate and win/loss ratio
- Best/worst realized trades
- Realized P&L by ticker and by month

### 5. Generate Comprehensive Report

Use Claude Code to generate a full markdown + PDF report:

```
Analyze my trades from trades_20260611.csv and generate a comprehensive report
```

Claude will:
1. Run both analysis scripts
2. Generate a markdown report with all metrics
3. Convert to PDF using the shared `utils/md_to_pdf.py` utility
4. Save to `analyses/Trading-Analysis-YYYY-MM-DD.md` and `.pdf`

### 6. Convert Report to PDF Manually

```bash
# From project root
python utils/md_to_pdf.py "trades_analysis_skill/analyses/Trading-Analysis-2026-06-12.md"

# Or from within trades_analysis_skill directory
cd trades_analysis_skill
python ../utils/md_to_pdf.py "analyses/Trading-Analysis-2026-06-12.md"
```

## Skill Structure

```
trades_analysis_skill/
├── SKILL.md                                    # Main skill definition
├── README.md                                   # This file
├── scripts/
│   ├── analyze_trades.py                       # Unrealized P&L analysis
│   └── calculate_realized_pnl.py               # Realized P&L (FIFO)
├── analyses/
│   ├── Trading-Analysis-YYYY-MM-DD.md          # Analysis reports
│   ├── Trading-Analysis-YYYY-MM-DD.pdf         # PDF versions
│   └── ...                                     # Historical reports
├── trades_for_analysis.csv                     # Sample data (gitignored)
└── trading_analysis_report.md                  # Sample report
```

## Analysis Components

### 1. Unrealized P&L Analysis (Current Holdings)

**Script**: `scripts/analyze_trades.py`

**Purpose**: Analyze performance of positions you still own

**Metrics**:
- Current portfolio value vs cost basis
- Unrealized P&L (paper gains/losses)
- Best buy trades: Biggest unrealized gains
- Worst buy trades: Biggest unrealized losses
- Best sell trades: Sold before price declined (avoided losses)
- Worst sell trades: Sold too early (missed gains)
- Holdings breakdown: Ticker-by-ticker performance

**Example Output**:
```
Current holdings: 43 tickers
Total Cost Basis: $2,256,737.65
Current Value: $2,276,296.31
Unrealized P&L: $+19,558.66 (+0.87%)
```

### 2. Realized P&L Analysis (Closed Positions)

**Script**: `scripts/calculate_realized_pnl.py`

**Purpose**: Calculate actual profits/losses from completed trades

**Methodology**: FIFO (First In First Out)
- Matches oldest buy with each sell chronologically
- Tax-compliant in most jurisdictions
- Tracks actual realized gains/losses

**Metrics**:
- Total realized P&L
- Win rate (percentage of profitable trades)
- Average win vs average loss
- Win/loss ratio
- Best/worst realized trades
- Realized P&L by ticker
- Realized P&L by month

**Example Output**:
```
Total Realized Trades: 138
Winning Trades: 80 (58.0%)
Losing Trades: 58 (42.0%)
Total Realized P&L: $+12,345.67
Win Rate: 58.0%
Win/Loss Ratio: 1.45
```

### 3. Overall Trading Performance

Combines both analyses:
- Overall success rate: Good trades vs bad trades
- Buy trade performance: Currently profitable positions %
- Sell trade performance: Good exit timing %
- Top performers by ticker
- Areas of concern

### 4. Trading Insights

Identifies patterns and lessons:
- Best decisions: What trades worked and why
- Missed opportunities: Sold too early, missed gains
- Timing analysis: Good vs bad entry/exit points
- Sector/ticker patterns: What works, what doesn't
- Risk assessment: Concentration risk, volatility exposure

## Usage Examples

### Example 1: Complete Trading Analysis

```bash
# Run both scripts
python scripts/analyze_trades.py my_trades.csv
python scripts/calculate_realized_pnl.py my_trades.csv
```

Or use Claude Code:
```
Generate a comprehensive trading analysis report from my_trades.csv
```

### Example 2: Quick Portfolio Check

```bash
python scripts/analyze_trades.py my_trades.csv
```

Shows current holdings and unrealized P&L.

### Example 3: Tax Reporting Prep

```bash
python scripts/calculate_realized_pnl.py my_trades.csv
```

Shows realized gains/losses for tax purposes (FIFO method).

### Example 4: Monthly Performance Review

```
Update my trading analysis with latest prices and show monthly P&L trends
```

Claude will re-fetch current prices and generate updated report.

## Key Features

### 1. Dual Analysis Approach
- **Unrealized**: What you currently own (marked-to-market)
- **Realized**: What you've actually gained/lost (closed trades)

### 2. FIFO Methodology
- Tax-compliant matching of buys and sells
- Chronological order processing
- Accurate cost basis tracking

### 3. Comprehensive Metrics
- Win rates and success percentages
- Best/worst trade identification
- Portfolio value tracking
- Monthly performance trends

### 4. Actionable Insights
- Identify repeated mistakes
- Recognize successful patterns
- Understand timing quality
- Assess concentration risk

## Understanding the Metrics

### Good vs Bad Trades

**For Buy Trades (Current Holdings)**:
- **Good**: Current price > Purchase price (unrealized gain)
- **Bad**: Current price < Purchase price (unrealized loss)

**For Sell Trades (Exited Positions)**:
- **Good**: Sell price > Current price (avoided decline or sold high)
- **Bad**: Sell price < Current price (sold too early, missed gains)

**For Realized Trades (Closed Positions)**:
- **Winning**: Sell price > Buy price (actual profit)
- **Losing**: Sell price < Buy price (actual loss)

### Win/Loss Ratio

```
Win/Loss Ratio = Average Winning Trade / Average Losing Trade
```

- **> 1.5**: Excellent (winners much larger than losers)
- **1.0 - 1.5**: Good (winners larger than losers)
- **< 1.0**: Poor (losers larger than winners)

### Win Rate

```
Win Rate = Winning Trades / Total Trades × 100%
```

- **> 60%**: Excellent trading accuracy
- **50-60%**: Good trading accuracy
- **< 50%**: Need to improve trade selection

## Best Practices

1. **Regular Updates**: Run analysis monthly or quarterly
2. **Learn from Data**: Study worst trades to avoid patterns
3. **Validate Winners**: Ensure best trades weren't just luck
4. **Monitor Concentration**: Check for over-concentration in tickers
5. **Track Both Metrics**: Don't ignore either realized or unrealized
6. **Consider Context**: Market conditions affect all trades
7. **Tax Planning**: Use realized P&L for tax-loss harvesting

## Installation

To install this skill for use with Claude Code:

### Option 1: Symlink (Recommended for development)

**Linux/Mac:**
```bash
ln -s $(pwd)/trades_analysis_skill ~/.claude/skills/trades-analysis
```

**Windows (PowerShell as Administrator):**
```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\trades-analysis" -Target "$PWD\trades_analysis_skill"
```

### Option 2: Copy

```bash
cp -r trades_analysis_skill ~/.claude/skills/trades-analysis
```

### Verify Installation

```
/skills
```

You should see `trades-analysis` in the list.

## Troubleshooting

### "yfinance not installed"
```bash
pip install yfinance
```

### "No data found for ticker"
- Verify ticker symbol is correct (case-insensitive)
- Check if stock is delisted or suspended
- Ensure internet connection is active

### Script runs but prices seem stale
- Check your internet connection
- Verify Yahoo Finance is accessible
- Consider API rate limiting (wait a minute and retry)

### FIFO calculations seem wrong
- Verify CSV date format is MM-DD-YYYY
- Ensure transactions are chronologically ordered
- Check for duplicate entries

### CSV parsing errors
- Verify column headers match expected format
- Check for commas in numeric values (should be handled)
- Ensure no missing required columns

## Data Privacy

**Important**: Trading data is personal financial information.
- Keep CSV files in `.gitignore` (already configured)
- Don't commit actual trade data to version control
- Use sample/anonymized data for examples
- Be careful when sharing analysis reports

## Customization

### Add Custom Metrics

Edit scripts to add your own analysis:

```python
# In analyze_trades.py or calculate_realized_pnl.py

# Example: Add Sharpe Ratio calculation
def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    # Your calculation here
    pass
```

### Modify Report Format

Create custom templates in `analyses/` folder with your preferred structure.

### Change FIFO to LIFO

Edit `calculate_realized_pnl.py`:

```python
# Change from deque (FIFO)
buy_queue = defaultdict(deque)

# To list with LIFO logic
buy_queue = defaultdict(list)
# And use .pop() instead of .popleft()
```

## Limitations

- **Not financial advice**: For educational/tracking purposes only
- **Price data delayed**: Yahoo Finance is typically 15-20 min delayed
- **Internet required**: Needs connection for current price fetching
- **Tax calculations**: Consult a tax professional for actual tax reporting
- **No transaction fees**: Scripts don't account for trading fees (add manually if needed)

## Future Enhancements

Potential additions:
- Automated email/Slack reports
- Portfolio rebalancing suggestions
- Benchmark comparison (S&P 500, etc.)
- Sector/industry analysis
- Risk-adjusted return metrics (Sharpe, Sortino)
- Monte Carlo simulations
- Tax-loss harvesting optimizer

## Related Skills

- **stock-analysis**: Analyze stocks before buying
- **portfolio-optimizer**: Optimize holdings allocation
- **tax-planner**: Use realized P&L for tax planning

---

**Version**: 1.0.0  
**Last Updated**: 2026-06-12  
**Maintainer**: Claude Code
