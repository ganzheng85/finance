# Report Data Validation

## Overview

The `validate_report_data.py` script helps ensure that fundamental analysis reports use accurate financial data from Yahoo Finance. This is a quality control step to catch:

- **Hallucination errors** - When AI generates plausible but incorrect numbers
- **Outdated data** - When report uses stale data
- **Data entry mistakes** - Manual errors in report creation

## How It Works

1. **Fetches actual data** from Yahoo Finance for the specified ticker
2. **Extracts values** from the markdown report using pattern matching
3. **Compares** report values against actual data with configurable tolerance
4. **Reports** any mismatches or missing values

## Usage

### Basic Validation

```bash
python scripts/validate_report_data.py MSFT --report analyses/MSFT/MSFT-2026-06-19.md
```

### Custom Tolerance

```bash
# Allow up to 5% difference (useful for older reports)
python scripts/validate_report_data.py MSFT --report analyses/MSFT/MSFT-2026-06-19.md --tolerance 5
```

### Just Fetch Data (No Validation)

```bash
# Fetch current Yahoo Finance data without validating a report
python scripts/validate_report_data.py MSFT
```

## What Gets Validated

The script checks these key metrics:

### Price Metrics
- Current Price
- 52-Week High/Low
- Position in 52-Week Range
- % From High/Low
- 6-Month Return %

### Valuation Metrics
- P/E Ratio (Trailing)
- P/E Ratio (Forward)
- P/S Ratio
- P/B Ratio

### Volume Metrics
- Average Volume (20-day)
- Current Volume

## Understanding Results

### Example Output

```
================================================================================
DATA VALIDATION REPORT: MSFT
================================================================================

Fetch Date: 2026-06-20
Company: Microsoft Corporation
Tolerance: ±2.0%

--------------------------------------------------------------------------------
Metric                         Actual          Report          Status              
--------------------------------------------------------------------------------
Current Price                  379.40          379.40          [OK] MATCH          
52-Week High                   551.05          551.05          [OK] MATCH          
P/E (Trailing)                 22.57           22.61           [OK] MATCH          
P/E (Forward)                  19.61           18.50           [X] MISMATCH (5.7% diff)
--------------------------------------------------------------------------------

Summary:
  [OK] Matches:    10
  [X]  Mismatches: 1
  [!]  Missing:    0
  Total Checks: 11
```

### Status Codes

- `[OK] MATCH` - Value matches within tolerance
- `[X] MISMATCH` - Value differs by more than tolerance %
- `[!] MISSING` - Value not found in report or actual data

### Exit Codes

- `0` - All validations passed
- `1` - Mismatches found or error occurred

## Tolerance Guidance

**Default: 2.0%**
- Good for reports created same-day
- Catches significant errors while allowing minor rounding

**Higher tolerance (5-10%)**
- Useful for older reports (stock prices change)
- When comparing against different data sources
- For highly volatile stocks

**Lower tolerance (0.5-1%)**
- For critical precision requirements
- When exact matching is needed

## Workflow Integration

### When Creating New Reports

```bash
# 1. Generate the report
python scripts/price_analysis.py MSFT

# 2. Create full analysis report
# ... (manual or automated)

# 3. Validate the report
python scripts/validate_report_data.py MSFT --report analyses/MSFT/MSFT-2026-06-20.md

# 4. Fix any mismatches before finalizing
```

### Before Publishing Reports

Always run validation as a final quality check:

```bash
python scripts/validate_report_data.py TICKER --report PATH_TO_REPORT
```

If mismatches are found, investigate and correct before publishing.

## Limitations

1. **Yahoo Finance Data Only**
   - Currently validates against Yahoo Finance
   - Does not check SEC filing data (10-K, 10-Q)
   - Market cap, revenue, earnings require separate validation

2. **Pattern Matching**
   - Relies on consistent markdown formatting
   - Custom formatting may not be extracted correctly

3. **Timing Differences**
   - Real-time vs delayed quotes
   - Intraday vs close prices
   - Different calculation methods for ratios

4. **No Fundamental Data**
   - Does not validate revenue, earnings, cash flow
   - Cannot check qualitative assessments
   - Moat scores, management ratings are not validated

## Future Enhancements

Potential additions:
- SEC Edgar data validation for fundamental metrics
- Historical data validation (specific past dates)
- Automated correction suggestions
- Batch validation for multiple reports
- Integration with report generation pipeline

## Troubleshooting

### "No data found for ticker"
- Check ticker symbol is correct
- Verify ticker exists on Yahoo Finance
- Try running with just ticker (no --report) to test data fetch

### "Report file not found"
- Verify file path is correct (relative to current directory)
- Check file name and extension (.md)

### Many MISSING values
- Report may use different formatting
- Update extraction patterns in `extract_report_values()`

### Systematic mismatches for all values
- Data source timing differences
- Check tolerance setting
- Verify report date vs fetch date

## Support

For issues or questions:
1. Check this README
2. Review script source code comments
3. Test with known-good reports
4. Verify Yahoo Finance data availability

---

**Version:** 1.0
**Last Updated:** 2026-06-20
