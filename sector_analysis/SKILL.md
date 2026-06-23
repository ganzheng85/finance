---
name: sector-analysis
description: Sector rotation analysis tool for tracking institutional money flow across 13 market sectors. Analyzes relative strength, momentum, and rotation patterns. Use when user asks for sector analysis, sector rotation, market rotation, or wants to see which sectors are leading/lagging.
---

# Sector Rotation Analysis Tool

**Track institutional money flow across 13 market sectors (11 S&P sectors + Semiconductors + Magnificent 7)**

This skill generates comprehensive sector rotation analysis with:
- ✅ Relative Strength (RS) vs SPY benchmark
- ✅ Momentum scoring (3M + 6M returns)
- ✅ Sector rankings by composite score
- ✅ Rotation quadrant mapping (Leading, Weakening, Improving, Lagging)
- ✅ Portfolio allocation recommendations
- ✅ HTML and Markdown reports

## Sectors Analyzed

**11 S&P Sector ETFs:**
- XLK - Technology
- XLV - Healthcare
- XLF - Financials
- XLY - Consumer Discretionary
- XLI - Industrials
- XLP - Consumer Staples
- XLE - Energy
- XLU - Utilities
- XLB - Materials
- XLRE - Real Estate
- XLC - Communication Services

**Special Sectors:**
- MAGS - Magnificent 7 (AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA)
- SMH - Semiconductors

**Benchmark:**
- SPY - S&P 500

## How to Run

### Quick Analysis (Recommended)
```bash
cd sector_analysis
python scripts/generate_sector_report.py
```

This generates:
- Comprehensive markdown report
- HTML report (with print-to-PDF button)
- Saved to `sector_analysis/analyses/`

### Step-by-Step (Manual)

**1. Fetch Sector Data**
```bash
cd sector_analysis
python scripts/fetch_sector_data.py
```
Downloads 365 days of price/volume data for all 14 ETFs.

**2. Calculate Metrics**
```bash
python scripts/calculate_sector_metrics.py
```
Calculates relative strength, momentum, rankings, and rotation quadrants.

**3. Generate Report**
```bash
python scripts/generate_sector_report.py
```

## Output Files

**Location:** `sector_analysis/analyses/`

**Files Created:**
- `Sector_Rotation_Analysis_YYYYMMDD_HHMMSS.md` - Markdown report
- `Sector_Rotation_Analysis_YYYYMMDD_HHMMSS.html` - HTML report (printable)

## Report Sections

### 1. Executive Summary
- Top 3 sectors (overweight)
- Bottom 3 sectors (avoid)
- Market rotation status

### 2. Sector Rankings Table
Ranked by composite score with:
- Relative Strength (20d, 60d) vs SPY
- Momentum (3M+6M)
- Signal (🚀 STRONG BUY, ✅ BUY, 👀 WATCH, ⚠️ WEAKENING, ❌ AVOID)

### 3. Rotation Map (Quadrant Analysis)
**🚀 Leading** - Strong + Accelerating (Overweight)
**⚠️ Weakening** - Strong + Decelerating (Reduce)
**👀 Improving** - Weak + Accelerating (Watch)
**❌ Lagging** - Weak + Decelerating (Avoid)

### 4. Detailed Sector Analysis
Deep dive on each sector with:
- Composite score
- Current price
- Relative strength metrics
- Momentum score
- Specific recommendation

### 5. Portfolio Recommendation
- Suggested allocation (Top 5 sectors)
- Sectors to avoid (Bottom 3)

### 6. Methodology
- Composite scoring formula
- Signal categories explanation

## Composite Score Formula

```
Composite Score = 
  25% × RS Rank (20d)
  + 25% × Momentum Rank
  + 25% × RS Percentile (60d)
  + 25% × Return Percentile (20d)
```

## Signal Categories

- 🚀 **STRONG BUY**: RS 20d > +2%, RS 60d > +3%, Momentum > +10%
- ✅ **BUY**: RS 20d > +1%, RS 60d > +1%
- 👀 **WATCH**: RS 20d positive but RS 60d negative (early rotation)
- ⚠️ **WEAKENING**: RS 20d negative but RS 60d positive (fading strength)
- ❌ **AVOID**: Both RS 20d and RS 60d negative

## Rotation Quadrants

**Quadrant Assignment:**
```python
if RS > 0 and Acceleration > 0:
    quadrant = "Leading"      # Overweight
elif RS > 0 and Acceleration <= 0:
    quadrant = "Weakening"    # Reduce
elif RS <= 0 and Acceleration > 0:
    quadrant = "Improving"    # Watch
else:
    quadrant = "Lagging"      # Avoid
```

## Use Cases

**1. Portfolio Rebalancing**
- Identify strongest sectors for overweight positions
- Exit weakening sectors before major declines

**2. Market Regime Detection**
- Leading sectors = risk-on (growth)
- Lagging sectors = risk-off (defensive rotation)

**3. Tactical Allocation**
- Follow institutional money flow
- Rotate into emerging strength early

**4. Risk Management**
- Avoid lagging sectors
- Reduce positions in weakening sectors

## Example Output

```
TOP 3 SECTORS:
  1. Technology (XLK): 🚀 STRONG BUY
  2. Communication Services (XLC): ✅ BUY
  3. Consumer Discretionary (XLY): ✅ BUY

BOTTOM 3 SECTORS:
  11. Energy (XLE): ❌ AVOID
  12. Utilities (XLU): ❌ AVOID
  13. Real Estate (XLRE): ❌ AVOID

MARKET ROTATION STATUS: HEALTHY ROTATION (Moderate leadership)

ROTATION MAP:
🚀 Leading: XLK, XLC
⚠️ Weakening: XLY, XLI
👀 Improving: XLV, XLF, XLP
❌ Lagging: XLE, XLU, XLRE, XLB, SMH
```

## Important Notes

**Data Freshness:**
- Always fetches latest data from Yahoo Finance
- No caching - fresh analysis every run
- Analysis date shown in report header

**Market Hours:**
- Best run after market close for most recent data
- Can run anytime, uses latest available close prices

**Educational Purpose:**
- This is a research tool, NOT investment advice
- For educational and analytical purposes only
- Always consult licensed financial professionals

## Workflow Integration

When user requests sector analysis:

1. **Navigate to sector_analysis directory**
   ```bash
   cd sector_analysis
   ```

2. **Run comprehensive analysis**
   ```bash
   python scripts/generate_sector_report.py
   ```

3. **Report location**
   - Check `sector_analysis/analyses/` for the latest report
   - Filename includes timestamp: `Sector_Rotation_Analysis_YYYYMMDD_HHMMSS.html`

4. **Present results**
   - Share top 3 sectors (overweight)
   - Share bottom 3 sectors (avoid)
   - Share rotation quadrant status
   - Provide link to full HTML report

## Technical Details

**Dependencies:**
- yfinance - Fetch ETF data
- pandas - Data manipulation
- numpy - Calculations

**Data Points:**
- 365 days historical data
- Daily OHLCV (Open, High, Low, Close, Volume)
- Adjusted close prices used for calculations

**Calculation Windows:**
- RS 20-day (short-term strength)
- RS 60-day (medium-term strength)
- RS 90-day, 180-day (long-term context)
- Momentum: 3-month + 6-month combined

**Report Format:**
- Markdown (.md) for version control
- HTML (.html) with styling and print-to-PDF button
- Timestamped filenames for tracking

## Troubleshooting

**Issue:** No data for specific ETF
- **Solution:** Check if ETF ticker is correct, retry fetch

**Issue:** Empty rotation quadrants
- **Solution:** Normal - reflects actual market conditions

**Issue:** Stale data
- **Solution:** Reports always fetch fresh data, check your internet connection

**Issue:** Missing HTML report
- **Solution:** Ensure `utils/md_to_html.py` is accessible

## Quick Reference

**Run Analysis:**
```bash
cd sector_analysis && python scripts/generate_sector_report.py
```

**View Latest Report:**
```bash
# On Windows
start sector_analysis/analyses/Sector_Rotation_Analysis_*.html

# On Mac/Linux
open sector_analysis/analyses/Sector_Rotation_Analysis_*.html
```

---

**Last Updated:** 2026-06-23
**Version:** 1.0
**Author:** Stock Analysis Dashboard
