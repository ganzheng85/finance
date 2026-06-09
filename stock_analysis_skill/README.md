# Stock Analysis Skill

A comprehensive skill for analyzing stocks with focus on:
- Current price levels (HIGH/MEDIUM/LOW)
- Moat strength assessment
- Current business issues identification
- Management problem-solving capability evaluation

## Quick Start

### 1. Install Dependencies

```bash
pip install yfinance
```

### 2. Use the Price Analysis Script

```bash
# Basic usage
python scripts/price_analysis.py "AAPL"

# With different time period
python scripts/price_analysis.py "MSFT" --period 2y

# JSON output for integration
python scripts/price_analysis.py "GOOGL" --json
```

### 3. Fetch Quarterly Financial Data

```bash
# Fetch quarterly financials for any stock
python scripts/fetch_quarterly_data.py META

# Fetch for Microsoft
python scripts/fetch_quarterly_data.py MSFT

# Fetch more quarters (default is 13)
python scripts/fetch_quarterly_data.py AAPL --quarters 8

# Export to CSV files
python scripts/fetch_quarterly_data.py NVDA --export
```

This script pulls **real quarterly data** from Yahoo Finance including:
- Income statement (revenue, operating income, net income, margins)
- Balance sheet (debt, equity, tangible book value)
- Cash flow (free cash flow, capex, buybacks)
- Key metrics (P/E, EPS, market cap)

### 3. Invoke via Claude Code

If this skill is installed in your Claude Code skills directory:

```
I want to analyze NVDA stock
```

Claude will use this skill to perform comprehensive analysis.

## Skill Structure

```
stock_analysis_skill/
├── SKILL.md                                        # Main skill definition
├── README.md                                       # This file
├── references/
│   ├── analysis-framework.md                       # Detailed scoring frameworks
│   ├── analysis-template.md                        # Output template
│   └── strategic-investment-productivity-template.csv  # Template for AI/R&D/capex analysis
├── scripts/
│   ├── price_analysis.py                           # Price data fetching script
│   └── fetch_quarterly_data.py                     # Fetch quarterly financials
├── data/                                           # Raw quarterly data (CSV exports)
│   ├── [ticker]_quarterly_income.csv               # Income statements
│   ├── [ticker]_quarterly_balance.csv              # Balance sheets
│   └── [ticker]_quarterly_cashflow.csv             # Cash flow statements
└── analyses/
    ├── [TICKER]-YYYY-MM-DD.md                      # Stock analysis reports
    ├── [TICKER]-YYYY-MM-DD.pdf                     # PDF versions
    └── [company]-[theme]-YYYY-MM-DD.csv           # Investment productivity analyses
```

## Analysis Components

### 1. Price Level Assessment
Determines if stock is trading at HIGH, MEDIUM, or LOW levels based on:
- Position in 52-week range
- Historical valuation multiples
- Intrinsic value estimates

### 2. Moat Scorecard (0-18 points)
Evaluates competitive advantages across 6 dimensions:
- Brand Power (0-3)
- Network Effects (0-3)
- Cost Advantages (0-3)
- Switching Costs (0-3)
- Regulatory/IP Protection (0-3)
- Data Moat (0-3)

### 3. Current Issues Analysis
Identifies and scores active problems by:
- **Severity**: 1 (minor) to 5 (critical)
- **Urgency**: 1 (long-term) to 5 (immediate)
- **Trend**: Improving / Stable / Worsening

Categories: Revenue, Margin, Operational, Strategic, Financial, External, Management

### 4. Management Assessment
Evaluates whether leadership can solve identified issues:
- **CAN SOLVE**: Proven track record, credible plan, adequate resources
- **UNCERTAIN**: Unproven or mixed signals
- **CANNOT SOLVE**: Inadequate capability or resources

### 5. Investment Recommendation
Final verdict: **BUY** / **WATCH** / **AVOID**

### 6. Strategic Investment Productivity Analysis (NEW)
**When asked to prove whether strategic investments (AI, R&D, capex) are productive:**

Automatically creates **multi-quarter comparison CSV files** with:
- **4-8 quarters of quantitative metrics** (revenue growth, margins, ROIC, user growth, etc.)
- **Good/Bad thresholds** for each metric
- **Quick assessment checklist** (YES/NO questions with weighted scoring)
- **Verdict logic** (PRODUCTIVE (PASS) / UNCERTAIN (CAUTION) / FAILING (FAIL))
- **Data source references** (where to find each metric in earnings reports)

**Example queries**:
- "Prove Meta's AI investments are productive"
- "Is Amazon's AWS capex paying off?"
- "Show me if Tesla's Gigafactory investment worked"

**Output**: CSV files saved to `references/[COMPANY]-[THEME]-productivity-metrics.csv`

## Installation

To install this skill for use with Claude Code:

### Option 1: Symlink (Recommended for development)

**Linux/Mac:**
```bash
ln -s $(pwd)/stock_analysis_skill ~/.claude/skills/stock-analysis
```

**Windows (PowerShell as Administrator):**
```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\stock-analysis" -Target "$PWD\stock_analysis_skill"
```

### Option 2: Copy

```bash
cp -r stock_analysis_skill ~/.claude/skills/stock-analysis
```

### Verify Installation

After installation, the skill should appear in Claude Code's available skills. Test with:

```
/skills
```

You should see `stock-analysis` in the list.

## Usage Examples

### Example 1: Quick Price Check
```
What's the current price level of Tesla?
```

Claude will run the price analysis script and provide the HIGH/MEDIUM/LOW verdict.

### Example 2: Full Analysis
```
Analyze MSFT stock - price level, moat, current issues, and management capability
```

Claude will produce a comprehensive analysis using the framework.

### Example 3: Focused Assessment
```
Does Apple have a strong moat? Score it using the moat framework.
```

Claude will focus on the moat scorecard component.

### Example 4: Strategic Investment Productivity (NEW)
```
Prove whether Meta's AI investments are productive using quantitative metrics
```

Claude will:
1. Identify key metrics (revenue growth, operating margin, ARPU, DAU growth, etc.)
2. Pull 8 quarters of data from earnings reports (Q1 2023 - Q4 2024)
3. Create two CSV files:
   - `meta-ai-productivity-metrics.csv` (comprehensive 50+ metrics)
   - `meta-ai-productivity-quick-checklist.csv` (top 15 metrics, YES/NO format)
4. Calculate weighted score and provide verdict:
   - **PRODUCTIVE (PASS)**: If 4-5 CRITICAL metrics improving → AI is working
   - **UNCERTAIN (CAUTION)**: If 3 CRITICAL metrics improving → Need more time
   - **FAILING (FAIL)**: If <3 CRITICAL metrics improving → AI wasting capital

**Use case**: When evaluating whether to buy a stock after a drop, use this to verify if strategic investments justify a premium valuation or if management is burning money.

## Customization

### Add Custom Metrics

Edit `scripts/price_analysis.py` to add your own metrics:

```python
# Example: Add RSI calculation
def calculate_rsi(prices, period=14):
    # Your RSI logic here
    pass
```

### Modify Scoring Criteria

Edit `references/analysis-framework.md` to adjust:
- Price level thresholds
- Moat scoring definitions
- Issue severity scales

### Change Output Format

Modify `references/analysis-template.md` to customize report structure.

## Data Sources

The price analysis script uses **yfinance** which pulls from Yahoo Finance. For production use, consider:

- Premium data providers (Bloomberg, FactSet, Refinitiv)
- Direct API access to exchanges
- SEC EDGAR for filings
- Earnings call transcripts (AlphaSense, Bloomberg)

## Best Practices

1. **Always fetch current data** - Stock situations change rapidly
2. **Distinguish issues from symptoms** - Dig for root causes
3. **Be honest about uncertainty** - State confidence levels
4. **Provide sources** - Link to filings and data
5. **Separate facts from opinions** - Make interpretation clear

## Limitations

- Not financial advice - for educational/informational purposes only
- Price data delayed (Yahoo Finance is typically 15-20 min delayed)
- Requires internet connection for data fetching
- Analysis quality depends on available information

## Troubleshooting

### "yfinance not installed"
```bash
pip install yfinance
```

### "No data found for ticker"
- Verify ticker symbol is correct
- Check if stock is delisted or suspended
- Try a different data source

### Script runs but shows stale data
- Check your internet connection
- Verify Yahoo Finance is accessible
- Consider API rate limiting

## Contributing

To improve this skill:

1. Add new analysis dimensions (e.g., ESG scoring, technical analysis)
2. Integrate additional data sources
3. Build comparison capabilities across multiple stocks
4. Add portfolio-level analysis

## License

MIT License - See main repository LICENSE file

## Related Skills

- `buffett-investment-research`: Long-term value investing framework
- Other analysis skills in the Claude Code ecosystem

---

**Version**: 1.0.0  
**Last Updated**: 2026-06-01  
**Maintainer**: Your Name
