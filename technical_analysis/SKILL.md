---
name: technical-analysis
description: Technical indicators and market data analysis tool using Yahoo Finance data. Provides technical factor calculations, pattern identification, and data summaries for research purposes.
skill_type: analysis
requires_approval: false
---

# Technical Analysis Research Tool

Fetches Yahoo Finance data, calculates comprehensive technical indicators, and generates analytical reports with pattern observations and data summaries for educational and research purposes.

## Overview

This skill provides comprehensive technical analysis for any stock ticker:
- Fetches historical price data from Yahoo Finance
- Calculates 20+ technical indicators (momentum, RSI, MACD, Bollinger Bands, ADX, Stochastic, etc.)
- Analyzes current trend direction and strength
- Identifies support/resistance levels
- Generates actionable trading signals
- Produces detailed markdown reports with optional PDF output

## Usage

When the user requests technical analysis for a stock, invoke this skill:

```
/technical-analysis TICKER [--days DAYS] [--pdf]
```

### Parameters

- `TICKER` (required): Stock ticker symbol (e.g., AAPL, TSLA, NVDA)
- `--days` (optional): Number of recent days to analyze (default: 30)
- `--pdf` (optional): Generate PDF report in addition to markdown

### Examples

```bash
# Basic analysis (last 30 days)
/technical-analysis AAPL

# Extended analysis (last 60 days)
/technical-analysis TSLA --days 60

# With PDF report
/technical-analysis NVDA --pdf

# Extended analysis with PDF
/technical-analysis META --days 90 --pdf
```

## What It Does

### 1. Data Fetching
- Fetches 365 days of historical data from Yahoo Finance (configurable)
- Includes: open, high, low, close, volume
- Validates ticker and data availability

### 2. Technical Factor Calculation

Calculates comprehensive technical indicators:

**Trend Indicators:**
- Momentum (12-1 month momentum with volatility adjustment)
- Simple Moving Averages (SMA): 20, 50, 200-day
- Distance from SMAs
- SMA crossovers (Golden Cross / Death Cross)

**Momentum Oscillators:**
- RSI (Relative Strength Index): 9, 14, 21-period
- MACD (Moving Average Convergence Divergence)
- Stochastic Oscillator (%K and %D)
- ADX (Average Directional Index)

**Volatility Indicators:**
- Annualized volatility
- Bollinger Bands (width, %B, squeeze detection)

**Volume Indicators:**
- Relative Volume (RVOL)
- Volume Price Trend (VPT)

### 3. Trend Analysis

Analyzes trends using multiple factors:
- **Direction**: Bullish, Bearish, or Neutral
- **Strength**: 0-10 scale based on indicator confluence
- **Key Levels**: Support and resistance from SMAs and recent highs/lows
- **Volatility**: Current volatility level and squeeze conditions
- **Volume**: Participation levels and trends

### 4. Trading Signals

Generates actionable signals:
- Strong trend setups (bullish/bearish)
- Oversold bounce opportunities
- Overbought pullback warnings
- Bollinger squeeze breakouts
- Confidence levels (HIGH, MEDIUM, LOW)

### 5. Report Generation

Creates two outputs:

**Markdown Report** (always generated):
- Executive summary
- Detailed trend analysis
- Technical indicator table
- Support/resistance levels
- Trading signals
- Recent price action table

**PDF Report** (optional):
- Professional formatted version of markdown report
- Requires `--pdf` flag

## Output Files

Files are saved to `technical_analysis/analyses/`:

```
TICKER_Technical_Analysis_YYYYMMDD_HHMMSS.md   # Markdown report
TICKER_Technical_Analysis_YYYYMMDD_HHMMSS.pdf  # PDF report (if --pdf)
TICKER_technical_factors_YYYYMMDD.csv          # Raw data with factors
```

## Technical Requirements

### Dependencies

```python
yfinance>=0.2.0      # Yahoo Finance data
pandas>=2.0.0        # Data manipulation
numpy>=1.24.0        # Numerical operations
```

### Files Structure

```
technical_analysis/
├── SKILL.md                           # This file
├── README.md                          # User documentation
├── techinical_factor.py               # Technical factor calculations
├── scripts/
│   ├── fetch_and_analyze.py          # Data fetching and factor calculation
│   ├── trend_analyzer.py             # Trend analysis engine
│   └── analyze_stock.py              # Main analysis script
└── analyses/                          # Output directory
    ├── TICKER_Technical_Analysis_*.md
    ├── TICKER_Technical_Analysis_*.pdf
    └── TICKER_technical_factors_*.csv
```

## Implementation

When invoked, the skill executes:

```bash
cd technical_analysis
python scripts/analyze_stock.py {ticker} {flags}
```

The script:
1. Fetches Yahoo Finance data (365 days default)
2. Calculates all technical factors using `TechnicalFactors` class
3. Extracts recent N days (default 30)
4. Analyzes trends using `TrendAnalyzer`
5. Generates markdown report
6. Optionally converts to PDF
7. Returns report path and summary

## When to Use This Skill

Invoke this skill when the user:
- Asks for technical analysis of a stock
- Wants to know if a stock is bullish or bearish
- Requests technical indicators (RSI, MACD, etc.)
- Asks about support/resistance levels
- Wants trading signals or setup analysis
- Mentions "technical factors", "chart analysis", or similar

Examples of user requests:
- "Analyze AAPL technical factors"
- "Is TSLA bullish or bearish right now?"
- "Show me the RSI and MACD for NVDA"
- "What are the support levels for META?"
- "Give me technical analysis for MSFT for the last 60 days"

## Error Handling

The skill handles:
- Invalid ticker symbols (error message)
- Insufficient data (error message)
- Missing dependencies (installation instructions)
- Data fetch failures (retry with error details)

## Best Practices

1. **Default to 30 days** for recent analysis (good balance of detail and relevance)
2. **Use 60-90 days** for longer-term trend analysis
3. **Always generate markdown** (lightweight, fast)
4. **Generate PDF only when requested** (requires additional processing)
5. **Validate ticker** before extensive processing

## Skill Invocation Examples

### Example 1: Basic Request
**User:** "Analyze AAPL technically"

**Claude should:**
```
I'll run a technical analysis on AAPL for you.
```
Then invoke: `/technical-analysis AAPL`

### Example 2: Extended Analysis
**User:** "Give me a 60-day technical analysis of TSLA with a PDF report"

**Claude should:**
```
I'll analyze TSLA's technical factors for the last 60 days and generate a PDF report.
```
Then invoke: `/technical-analysis TSLA --days 60 --pdf`

### Example 3: Multiple Requests
**User:** "Analyze the technical factors for AAPL, MSFT, and NVDA"

**Claude should:**
```
I'll run technical analysis on all three stocks: AAPL, MSFT, and NVDA.
```
Then invoke:
```
/technical-analysis AAPL
/technical-analysis MSFT
/technical-analysis NVDA
```

## Return Format

The skill returns:
1. **Console output**: Summary of key findings
2. **File paths**: Locations of generated reports
3. **Key metrics**: Trend direction, signals, price levels

Claude should then:
1. Summarize the key findings for the user
2. Highlight the main signals (bullish/bearish)
3. Mention important levels (support/resistance)
4. Provide the report file path
5. Offer to explain any indicators or signals if needed

## Notes

- Historical data fetched: 365 days (ensures enough data for 252-day momentum)
- Analysis period: Last N days (default 30)
- All technical factors are calculated on the full dataset, then filtered to recent period
- This ensures accurate long-term indicators (like SMA(200)) even for recent analysis
- Factors are calculated per-symbol (supports batch processing if extended)

---

**Skill Author:** Claude Code Technical Analysis Module  
**Version:** 1.0  
**Last Updated:** 2026-06-13
