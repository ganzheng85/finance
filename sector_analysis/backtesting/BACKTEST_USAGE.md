# Custom Backtest Script Usage Guide

## Overview

`backtest_custom.py` allows you to test sector rotation strategies with custom parameters:
- **Top N sectors:** 3 or 5
- **Risk management:** Base, Trailing 15%, Hard 25%, or Market Regime
- **Time period:** Any start and end dates

---

## Command Syntax

```bash
python backtest_custom.py --top N --strategy STRATEGY --start YYYY-MM-DD --end YYYY-MM-DD
```

### Parameters

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `--top` | Yes | 3 or 5 | Number of top-ranked sectors to invest in |
| `--strategy` | Yes | base, trailing15, hard25, regime | Risk management strategy |
| `--start` | Yes | YYYY-MM-DD | Backtest start date |
| `--end` | Yes | YYYY-MM-DD | Backtest end date |

---

## Strategies Explained

### 1. **base** (No Risk Management)
- Always 100% invested in top N sectors
- Equal weight allocation
- Weekly rebalancing
- **Best for:** Bull markets with clear trends

### 2. **trailing15** (15% Trailing Stop)
- Go 50% cash if portfolio drops -15% from peak
- Re-invest when recovered to -5% from peak
- **Best for:** Volatile markets, want downside protection

### 3. **hard25** (25% Hard Stop)
- Go 100% cash if portfolio drops -25% from peak
- Re-invest when recovered to -5% from peak
- **Best for:** Maximum crash protection

### 4. **regime** (Market Regime Filter)
- Go 50% cash when SPY < 200-day moving average
- Back to 100% when SPY > 200-day moving average
- **Best for:** Bear market protection with automatic re-entry

---

## Examples

### Example 1: Top 3, Base Strategy, 2025 Full Year
```bash
python backtest_custom.py --top 3 --strategy base --start 2025-01-01 --end 2025-12-31
```

### Example 2: Top 5, Market Regime, 2025 H1
```bash
python backtest_custom.py --top 5 --strategy regime --start 2025-01-01 --end 2025-06-01
```

### Example 3: Top 3, Trailing 15% Stop, Dec 2025 - Jun 2026
```bash
python backtest_custom.py --top 3 --strategy trailing15 --start 2025-12-01 --end 2026-06-30
```

### Example 4: Top 5, Hard 25% Stop, 2022 Bear Market
```bash
python backtest_custom.py --top 5 --strategy hard25 --start 2022-01-01 --end 2022-10-31
```

### Example 5: Top 3, Market Regime, 2020 COVID Crash
```bash
python backtest_custom.py --top 3 --strategy regime --start 2020-01-01 --end 2020-05-31
```

---

## Output

The script generates:

### 1. **Console Output**
```
================================================================================
BACKTEST RESULTS
================================================================================

Period: 2025-01-03 to 2025-12-30 (362 days / 0.99 years)
Rebalancing Events: 52
Total Trades: 312

PERFORMANCE COMPARISON
Metric                    Sector Rotation      SPY Benchmark      Difference
--------------------------------------------------------------------------------
Final Value                    $127,336.62        $115,664.61      +$11,672.01
Total Return                        27.34%             15.66%           +11.68%
Annualized Return                   27.64%             15.82%           +11.82%
Sharpe Ratio                          1.23               0.98             +0.25
Max Drawdown                         -8.45%             -6.23%            -2.22%
```

### 2. **CSV Files (in results/ folder)**

#### `backtest_top3_base_20250101_20251231_TIMESTAMP.csv`
- Date-by-date portfolio values
- Returns and alpha calculations
- Holdings at each rebalance

#### `trades_top3_base_20250101_20251231_TIMESTAMP.csv`
- Detailed trade log
- Every buy/sell transaction
- Transaction costs

---

## Quick Tests (Common Scenarios)

### Test 1: Compare Top 3 vs Top 5 for 2025
```bash
# Top 3
python backtest_custom.py --top 3 --strategy base --start 2025-01-01 --end 2025-12-31

# Top 5
python backtest_custom.py --top 5 --strategy base --start 2025-01-01 --end 2025-12-31
```

### Test 2: Compare All 4 Strategies for Top 3
```bash
# Base
python backtest_custom.py --top 3 --strategy base --start 2025-01-01 --end 2025-12-31

# Trailing 15%
python backtest_custom.py --top 3 --strategy trailing15 --start 2025-01-01 --end 2025-12-31

# Hard 25%
python backtest_custom.py --top 3 --strategy hard25 --start 2025-01-01 --end 2025-12-31

# Market Regime
python backtest_custom.py --top 3 --strategy regime --start 2025-01-01 --end 2025-12-31
```

### Test 3: Test Your Specific Periods
```bash
# 2025 H1
python backtest_custom.py --top 3 --strategy regime --start 2025-01-01 --end 2025-06-01

# 2025 H2
python backtest_custom.py --top 3 --strategy regime --start 2025-06-01 --end 2025-12-31
```

---

## Tips

### 1. **Minimum Time Period**
- Recommend at least 3 months for meaningful results
- Script needs ~200 days before start date for calculations

### 2. **Strategy Selection**
- **Bull market?** Use `base` (no stops)
- **Volatile market?** Use `trailing15`
- **Crash risk?** Use `regime` or `hard25`

### 3. **Top 3 vs Top 5**
- **Top 3:** More concentrated, higher returns, higher risk
- **Top 5:** More diversified, lower risk, smoother returns

### 4. **Multiple Tests**
Run the script multiple times with different parameters to compare:
```bash
# Save output to files for comparison
python backtest_custom.py --top 3 --strategy base --start 2025-01-01 --end 2025-12-31 > results/top3_base_2025.txt
python backtest_custom.py --top 5 --strategy regime --start 2025-01-01 --end 2025-12-31 > results/top5_regime_2025.txt
```

---

## Troubleshooting

### Error: "Invalid date format"
**Fix:** Use YYYY-MM-DD format
```bash
# Wrong
--start 01/01/2025

# Correct
--start 2025-01-01
```

### Error: "End date must be after start date"
**Fix:** Make sure end date is later than start date
```bash
# Wrong
--start 2025-12-31 --end 2025-01-01

# Correct
--start 2025-01-01 --end 2025-12-31
```

### Error: "No data for ticker"
**Fix:** Date might be too far back or ticker didn't exist yet
- Try more recent dates
- Check if all sector ETFs existed during your period

### No rebalancing dates found
**Fix:** Date range too short or no trading days
- Ensure at least 1-2 weeks in date range
- Avoid holiday-only periods

---

## Advanced: Batch Testing

Create a batch script to test multiple scenarios:

### Windows (batch.bat)
```batch
@echo off
echo Testing multiple strategies...

python backtest_custom.py --top 3 --strategy base --start 2025-01-01 --end 2025-12-31
python backtest_custom.py --top 3 --strategy regime --start 2025-01-01 --end 2025-12-31
python backtest_custom.py --top 5 --strategy base --start 2025-01-01 --end 2025-12-31
python backtest_custom.py --top 5 --strategy regime --start 2025-01-01 --end 2025-12-31

echo Done!
```

### Mac/Linux (batch.sh)
```bash
#!/bin/bash
echo "Testing multiple strategies..."

python backtest_custom.py --top 3 --strategy base --start 2025-01-01 --end 2025-12-31
python backtest_custom.py --top 3 --strategy regime --start 2025-01-01 --end 2025-12-31
python backtest_custom.py --top 5 --strategy base --start 2025-01-01 --end 2025-12-31
python backtest_custom.py --top 5 --strategy regime --start 2025-01-01 --end 2025-12-31

echo "Done!"
```

---

## Quick Reference Card

```
COMMAND:
python backtest_custom.py --top [3|5] --strategy [base|trailing15|hard25|regime] --start YYYY-MM-DD --end YYYY-MM-DD

STRATEGIES:
  base        = Always invested
  trailing15  = 50% cash at -15% drawdown
  hard25      = 100% cash at -25% drawdown
  regime      = 50% cash when SPY < 200 MA

EXAMPLES:
  Top 3, no stops, 2025:
    python backtest_custom.py --top 3 --strategy base --start 2025-01-01 --end 2025-12-31

  Top 5, market regime, H1 2025:
    python backtest_custom.py --top 5 --strategy regime --start 2025-01-01 --end 2025-06-01
```

---

*Last Updated: June 27, 2026*
