# Technical Analysis Skill

Comprehensive technical analysis tool that fetches Yahoo Finance data and analyzes stock trends using 20+ technical indicators.

## Quick Start

```bash
# Basic analysis (last 30 days)
python scripts/analyze_stock.py AAPL

# Extended analysis (60 days)
python scripts/analyze_stock.py TSLA --days 60

# With PDF report
python scripts/analyze_stock.py NVDA --pdf
```

Or using Claude Code skill:

```
/technical-analysis AAPL
/technical-analysis TSLA --days 60 --pdf
```

## What It Does

This skill provides comprehensive technical analysis including:

✅ **Trend Analysis**: Direction, strength, and momentum  
✅ **20+ Technical Indicators**: RSI, MACD, Bollinger Bands, ADX, Stochastic, SMAs  
✅ **Support/Resistance Levels**: Key price levels from SMAs and recent extremes  
✅ **Trading Signals**: Actionable buy/sell/hold recommendations  
✅ **Volume Analysis**: Relative volume and participation trends  
✅ **Volatility Analysis**: Current volatility and squeeze conditions  
✅ **Detailed Reports**: Markdown and optional PDF output

## Installation

### Dependencies

```bash
pip install yfinance pandas numpy
```

### Optional (for PDF generation)

PDF generation requires the `md_to_pdf.py` utility in the parent `utils/` directory.

## Usage

### Command Line

```bash
# Navigate to technical_analysis directory
cd technical_analysis

# Basic usage
python scripts/analyze_stock.py <TICKER>

# With options
python scripts/analyze_stock.py <TICKER> [--days N] [--lookback N] [--pdf]
```

### Parameters

- **TICKER** (required): Stock ticker symbol (e.g., AAPL, TSLA, MSFT)
- **--days N**: Number of recent trading days to analyze (default: 30)
- **--lookback N**: Days of historical data to fetch (default: 365)
- **--pdf**: Generate PDF report in addition to markdown

### Examples

```bash
# Apple, last 30 days
python scripts/analyze_stock.py AAPL

# Tesla, last 60 days with PDF
python scripts/analyze_stock.py TSLA --days 60 --pdf

# NVIDIA, 90 days, fetch 500 days of history
python scripts/analyze_stock.py NVDA --days 90 --lookback 500
```

## Technical Indicators Calculated

### Trend Indicators
- **Momentum (12-1)**: Classic momentum factor with volatility adjustment
- **SMA (Simple Moving Average)**: 20, 50, 200-day averages
- **Distance from SMA**: How far price is from each SMA
- **SMA Distance**: Crossover signals (Golden Cross / Death Cross)

### Momentum Oscillators
- **RSI (Relative Strength Index)**: 9, 14, 21-period
  - <30 = Oversold, >70 = Overbought
- **MACD**: Moving Average Convergence Divergence
  - Line, Signal, and Histogram
- **Stochastic**: %K and %D oscillators
  - <20 = Oversold, >80 = Overbought
- **ADX (Average Directional Index)**: Trend strength
  - >25 = Strong trend, <20 = Weak trend

### Volatility Indicators
- **Annualized Volatility**: Standard deviation of returns
- **Bollinger Bands**: Width, %B, and squeeze detection
- **Bollinger Squeeze**: Low volatility compression (potential breakout)

### Volume Indicators
- **Relative Volume (RVOL)**: Current volume vs average
  - >2x = Very high, <0.5x = Low
- **Volume Price Trend (VPT)**: Cumulative volume × price change

## Output

### Console Output

The script displays:
1. Data fetching progress
2. Factor calculation progress
3. Summary of key technical indicators
4. Trend direction and strength
5. Trading signals

Example:
```
====================================================================================================
TECHNICAL ANALYSIS REPORT - AAPL
====================================================================================================
Generated: 2026-06-13 10:30:45
Analysis Period: 2025-05-15 to 2026-06-13
Current Price: $290.59

====================================================================================================
TREND ANALYSIS
====================================================================================================
Direction: BULLISH
Strength: 8/10
Score: +6

Bullish Signals:
  + Price 12.5% above SMA(200)
  + SMA(20) 3.2% above SMA(50) (Golden Cross)
  + Strong positive momentum (0.68)
  + MACD histogram positive

====================================================================================================
TRADING SIGNALS
====================================================================================================
Signal #1:
  Action: BUY
  Confidence: HIGH
  Reason: Strong bullish trend (score: 6)
  Details:
    - Price 12.5% above SMA(200)
    - SMA(20) 3.2% above SMA(50) (Golden Cross)
    - Strong positive momentum (0.68)
    - MACD histogram positive
```

### File Outputs

Files are saved to `analyses/` directory:

1. **Markdown Report**: `TICKER_Technical_Analysis_YYYYMMDD_HHMMSS.md`
   - Comprehensive analysis with tables and formatting
   - Executive summary
   - Detailed indicator breakdown
   - Support/resistance levels
   - Trading signals

2. **PDF Report** (optional): `TICKER_Technical_Analysis_YYYYMMDD_HHMMSS.pdf`
   - Professional formatted version of markdown
   - Requires `--pdf` flag

3. **CSV Data**: `TICKER_technical_factors_YYYYMMDD.csv`
   - Raw data with all calculated technical factors
   - Useful for further analysis or spreadsheet import

## Understanding the Reports

### Trend Direction

**BULLISH**: Multiple indicators show upward momentum
- Price above SMAs
- Positive momentum
- Golden cross (short SMA > long SMA)
- MACD positive

**BEARISH**: Multiple indicators show downward momentum
- Price below SMAs
- Negative momentum
- Death cross (short SMA < long SMA)
- MACD negative

**NEUTRAL**: Mixed or weak signals
- Price near SMAs
- Conflicting indicators
- Low ADX (weak trend)

### Signal Confidence

**HIGH**: Strong indicator confluence (5+ aligned signals)
**MEDIUM**: Moderate setup (3-4 aligned signals)
**LOW**: Weak or conflicting signals (<3 aligned)

### Key Levels

**Support**: Price levels where buying pressure may increase
- SMAs below current price
- Recent lows
- Psychological levels

**Resistance**: Price levels where selling pressure may increase
- SMAs above current price
- Recent highs
- Psychological levels

## Script Components

### 1. `fetch_and_analyze.py`

Core data fetching and factor calculation:
- Fetches Yahoo Finance data
- Calculates all technical factors
- Displays summary statistics
- Saves CSV output

```bash
python scripts/fetch_and_analyze.py AAPL --days 30
```

### 2. `trend_analyzer.py`

Trend analysis engine (can be imported):

```python
from trend_analyzer import TrendAnalyzer

analyzer = TrendAnalyzer(df)
trend = analyzer.analyze_trend_direction()
signals = analyzer.generate_trading_signals()
report = analyzer.generate_report()
```

### 3. `analyze_stock.py`

Complete analysis pipeline (recommended):
- Combines fetching, calculation, and analysis
- Generates markdown reports
- Optionally creates PDFs

```bash
python scripts/analyze_stock.py AAPL --days 60 --pdf
```

## Technical Factor Details

### Momentum (12-1)

Classic momentum factor:
- **Period**: 252 trading days (~12 months)
- **Skip**: 21 days (~1 month)
- **Formula**: (Price_t-21 / Price_t-252) - 1
- **Adjustment**: Divided by volatility (risk-adjusted)
- **Interpretation**: 
  - Positive = Upward momentum
  - Negative = Downward momentum
  - >0.5 = Strong upward
  - <-0.5 = Strong downward

### RSI (Relative Strength Index)

Measures speed and magnitude of price changes:
- **Calculation**: Wilder's smoothing (EMA of gains/losses)
- **Range**: 0-100
- **Oversold**: <30 (potential bounce)
- **Overbought**: >70 (potential pullback)
- **Neutral**: 30-70

### MACD (Moving Average Convergence Divergence)

Trend-following momentum indicator:
- **MACD Line**: EMA(12) - EMA(26)
- **Signal Line**: EMA(MACD, 9)
- **Histogram**: MACD - Signal
- **Interpretation**:
  - Histogram > 0: Bullish
  - Histogram < 0: Bearish
  - Crossing zero: Trend change

### Bollinger Bands

Volatility bands around price:
- **Middle**: SMA(20)
- **Upper**: SMA(20) + 2σ
- **Lower**: SMA(20) - 2σ
- **%B**: Price position within bands
  - 0 = At lower band
  - 0.5 = At middle
  - 1.0 = At upper band
- **Squeeze**: Narrow bands (low volatility, potential breakout)

### ADX (Average Directional Index)

Measures trend strength (not direction):
- **Range**: 0-100
- **<20**: Weak trend (range-bound)
- **20-25**: Developing trend
- **25-50**: Strong trend
- **>50**: Very strong trend
- **+DI and -DI**: Show direction

## Common Use Cases

### 1. Quick Health Check
```bash
python scripts/analyze_stock.py AAPL
```
Get a quick read on whether AAPL is bullish, bearish, or neutral.

### 2. Detailed Pre-Trade Analysis
```bash
python scripts/analyze_stock.py TSLA --days 60 --pdf
```
Comprehensive 60-day analysis with PDF for record-keeping.

### 3. Portfolio Review
```bash
for ticker in AAPL MSFT NVDA META; do
    python scripts/analyze_stock.py $ticker
done
```
Batch analyze multiple holdings.

### 4. Daily Monitoring
```bash
python scripts/analyze_stock.py AAPL --days 10
```
Focus on recent 10-day trend for active trading.

## Limitations

1. **Technical Analysis Only**: Does not consider fundamentals, news, or macroeconomic factors
2. **Historical Data**: Past performance does not guarantee future results
3. **Lagging Indicators**: Most indicators are backward-looking
4. **False Signals**: No indicator is 100% accurate
5. **Market Conditions**: Works best in trending markets, less effective in choppy conditions

## Best Practices

1. **Combine Multiple Signals**: Don't rely on a single indicator
2. **Confirm with Volume**: Strong moves should have volume confirmation
3. **Respect Trends**: Trade with the trend, not against it
4. **Use Stop Losses**: Technical analysis helps set stop levels
5. **Consider Time Frames**: Short-term signals may conflict with long-term trends
6. **Review Regularly**: Market conditions change, update your analysis

## Troubleshooting

### Error: "No data found for ticker"
- Check ticker symbol is correct (use Yahoo Finance format)
- Verify the stock is actively traded
- Try a different ticker to test

### Error: "Module not found"
```bash
pip install yfinance pandas numpy
```

### PDF Generation Fails
- Check that `utils/md_to_pdf.py` exists
- Markdown report is still generated
- PDF is optional, use markdown instead

### Indicators Show "N/A"
- Not enough historical data
- Increase `--lookback` parameter
- Some indicators need 200+ days of data

## Advanced Usage

### Custom Parameters

Edit `techinical_factor.py` to customize indicator parameters:

```python
# Example: Change RSI period to 21 instead of 14
tf.rsi(window=21)

# Example: Use different MACD settings
tf.macd(fast=10, slow=21, signal=7)
```

### Import as Module

```python
import sys
sys.path.append('technical_analysis')

from scripts.fetch_and_analyze import fetch_stock_data, calculate_all_factors
from scripts.trend_analyzer import TrendAnalyzer

# Fetch and analyze
df = fetch_stock_data('AAPL')
df_factors = calculate_all_factors(df)

# Custom analysis
analyzer = TrendAnalyzer(df_factors)
trend = analyzer.analyze_trend_direction()
print(f"Trend: {trend['direction']}, Strength: {trend['strength']}")
```

## Contributing

To add new indicators:

1. Add calculation function to `techinical_factor.py`
2. Add to `TechnicalFactors.run_all()` method
3. Update `TrendAnalyzer` to use the new indicator
4. Document in this README

## License

For educational and personal use.

## Disclaimer

**This tool is for informational purposes only and should not be considered financial advice.**

- Technical analysis does not guarantee profits
- Past performance does not predict future results
- Always do your own research
- Consult a licensed financial advisor before making investment decisions
- Use at your own risk

---

**Created:** June 2026  
**Author:** Claude Code Technical Analysis Module  
**Version:** 1.0
