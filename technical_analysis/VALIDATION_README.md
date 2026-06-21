# Technical Analysis - Data Validation System

## Overview

The technical analysis system now includes **automatic validation** to prevent hallucination errors and ensure all calculated values in reports are accurate.

## How It Works

### Automatic Validation (During Report Generation)

When you run `python scripts/analyze_stock.py {TICKER}`, the system:

1. ✅ Fetches fresh Yahoo Finance data
2. ✅ Calculates all technical indicators
3. ✅ Generates markdown and HTML reports
4. ✅ **Automatically validates** all values in the report
5. ✅ Displays validation summary

**Example Output:**
```
============================================================
Validating Report Data...
============================================================
[OK] All 9 values validated successfully!
```

**If Mismatches Found:**
```
[WARNING] Validation found 1 mismatch(es):
  - Annualized Volatility %: Report=36.24, Actual=38.56

Run validation script for detailed report:
  python scripts/validate_technical_report.py META --report ...
```

### Manual Validation (Standalone)

You can also manually validate any existing report:

```bash
cd technical_analysis
python scripts/validate_technical_report.py AAPL \
  --report analyses/AAPL_Technical_Analysis_20260621_154759.md \
  --tolerance 0.02
```

## What Gets Validated

| Metric | Description | Tolerance |
|--------|-------------|-----------|
| **Current Price** | Latest closing price | ±2% |
| **RSI(14)** | Relative Strength Index | ±2% |
| **MACD Histogram** | MACD histogram value | ±2% |
| **Stochastic %K** | Stochastic oscillator | ±2% |
| **ADX(14)** | Average Directional Index | ±2% |
| **Bollinger %B** | Position within Bollinger Bands | ±2% |
| **Annualized Volatility** | Historical volatility (annualized) | ±2% |
| **Last Volume** | Trading volume | Exact match |
| **Last Close** | Closing price (verification) | ±2% |

## Validation Results

### ✅ Success Example (AAPL)
```
================================================================================
TECHNICAL ANALYSIS DATA VALIDATION: AAPL
================================================================================

Validation Date: 2026-06-21 16:02:13
Tolerance: ±2.0%

--------------------------------------------------------------------------------
Metric                         Report          Actual          Status
--------------------------------------------------------------------------------
Current Price                  298.01          298.01          [OK] MATCH
RSI(14)                        50.98           50.98           [OK] MATCH
MACD Histogram                 -2.04           -2.04           [OK] MATCH
Stochastic %K                  35.41           35.41           [OK] MATCH
ADX(14)                        27.29           27.29           [OK] MATCH
Bollinger %B                   0.33            0.33            [OK] MATCH
Annualized Volatility %        22.67           22.25           [OK] MATCH
Last Volume                    85962200.00     85962200.00     [OK] MATCH
Last Close                     298.01          298.01          [OK] MATCH
--------------------------------------------------------------------------------

Summary:
  [OK] Matches:    9
  [X]  Mismatches: 0
  [!]  Missing:    0
  Total Checks: 9

[OK] All values validated successfully!
================================================================================
```

### ⚠️ Warning Example (Minor Mismatch)

Small differences in volatility can occur due to:
- Different calculation windows (30 days vs 252 days)
- Rounding differences
- Timestamp differences (intraday updates)

If difference is within acceptable range (e.g., 5-10% for volatility), the report is still usable.

## Validation in Web App

When generating technical analysis through the web app:

1. User clicks "Technical Analysis"
2. System generates report
3. System automatically validates data
4. Validation status included in API response

**API Response:**
```json
{
  "ticker": "AAPL",
  "type": "technical",
  "html_path": "/path/to/report.html",
  "validation_passed": true,
  "validation_output": "..."
}
```

**If Validation Fails:**
```json
{
  "validation_passed": false,
  "warning": "Report validation found data mismatches. Review validation output."
}
```

## Command Line Options

### Basic Validation
```bash
python scripts/validate_technical_report.py AAPL \
  --report analyses/AAPL_Technical_Analysis_20260621_154759.md
```

### Custom Tolerance
```bash
python scripts/validate_technical_report.py META \
  --report analyses/META_Technical_Analysis_20260621_160327.md \
  --tolerance 0.05  # 5% tolerance instead of default 2%
```

### Custom Lookback Period
```bash
python scripts/validate_technical_report.py TSLA \
  --report analyses/TSLA_Technical_Analysis_20260621_120000.md \
  --lookback 730  # Use 2 years of data for validation
```

## Technical Details

### Validation Process

1. **Extract Values from Report**
   - Parses markdown file
   - Extracts all numeric values using regex
   - Stores in dictionary

2. **Calculate Fresh Values**
   - Fetches latest Yahoo Finance data
   - Recalculates all technical indicators
   - Uses same parameters as original report

3. **Compare Values**
   - Compares each metric
   - Calculates percentage difference
   - Flags mismatches exceeding tolerance

4. **Generate Report**
   - Lists all matches
   - Highlights mismatches
   - Identifies missing values

### Column Name Mapping

The validator tries multiple column name variations for each indicator:

**RSI:**
- `rsi_14`, `rsi`, `RSI_14`, `RSI`

**MACD Histogram:**
- `macd_hist_12_26_9`, `macd_hist`, `MACD_Hist`, `macd_histogram`

**Stochastic %K:**
- `stoch_k_14`, `stoch_k_14_3_3`, `stoch_k`, `STOCHk_14_3_3`

**Bollinger %B:**
- `bb_percent_b`, `bb_pct_b_20_2`, `bb_percent`, `BBL_20_2`

**ADX:**
- `adx_14`, `ADX_14`, `adx`, `ADX`

### Volatility Calculation

Volatility is calculated as:
```python
# Use last 30 days
returns = prices.pct_change()
daily_vol = returns.std()
annualized_vol = daily_vol * sqrt(252) * 100
```

## Troubleshooting

### High Volatility Mismatch
- **Cause**: Different calculation windows
- **Solution**: Use `--tolerance 0.10` (10%) for volatility
- **Expected**: Volatility can vary 5-15% based on window

### Missing Values
- **Cause**: Indicator not calculated (insufficient data)
- **Solution**: Increase `--lookback` days
- **Expected**: Need minimum 50-200 days for some indicators

### All Values Missing
- **Cause**: Report format changed or parsing failed
- **Solution**: Check report file format
- **Expected**: Report should match standard template

## Files

| File | Purpose |
|------|---------|
| `scripts/validate_technical_report.py` | Standalone validation script |
| `scripts/analyze_stock.py` | Generates reports with automatic validation |
| `stock_analysis_app/api/technical.py` | Web app integration with validation |

## Summary

✅ **Automatic validation** prevents hallucination errors  
✅ **9 metrics validated** for each report  
✅ **2% default tolerance** (configurable)  
✅ **Integrated with web app** and command line  
✅ **Detailed reports** show all matches/mismatches  

All technical analysis reports are now validated for accuracy!
