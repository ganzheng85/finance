# Technical Analysis Enhancements - July 2026

## Overview

Three major enhancements have been added to provide more practical trading information:

1. ✅ **Support and Resistance Levels** - Horizontal price levels from swing highs/lows and consolidation zones
2. ✅ **ATR (Average True Range)** - Volatility metric for stop-loss and position sizing
3. ✅ **50-day and 200-day SMAs** - Long-term trend context now visible on charts

---

## 1. Support and Resistance Levels

### What Was Added

**Detection Algorithm** ([plot_comprehensive_analysis.py](scripts/plot_comprehensive_analysis.py)):
- Swing high detection: Local price maxima over 10-day windows
- Swing low detection: Local price minima over 10-day windows
- Level clustering: Groups nearby levels within 2% to avoid clutter
- Proximity filtering: Shows only levels within 20% of current price

**Chart Display**:
- Resistance levels (above price): Red dashed horizontal lines with labels
- Support levels (below price): Green dashed horizontal lines with labels
- Labels show: Level number, price, and % distance from current price
- Example: `R1: $313.25 (+3.2%)`

**Text Reports** ([trend_analyzer.py](scripts/trend_analyzer.py)):
- Enhanced `identify_key_levels()` method now includes:
  - SMA-based support/resistance (20, 50, 200-day)
  - 30-day high/low levels
  - Swing high/low pivot points
  - All sorted by proximity to current price

### How to Use

**For Trading**:
- **Support zones**: Potential buy/add zones where price may bounce
- **Resistance zones**: Potential sell/reduce zones or profit targets
- **Breakouts**: Watch for volume spikes when price breaks through levels

**For Stop-Loss Placement**:
- Place stops just below nearest support (for longs)
- Place stops just above nearest resistance (for shorts)
- Use ATR to set stop distance below support for breathing room

**Example Reading**:
```
Support Levels:
  S1: $295.30 (2.8% below) - Swing Low
  S2: $290.15 (5.5% below) - SMA(50)
  S3: $283.40 (9.2% below) - 30-day Low

Resistance Levels:
  R1: $310.50 (2.1% above) - SMA(20)
  R2: $313.25 (3.2% above) - Swing High
  R3: $320.80 (5.4% above) - 30-day High
```

**Interpretation**: Stock has nearby resistance at $310-313 (good profit target for swing trade), with solid support at $295 (good stop-loss level or buy-on-dip zone).

---

## 2. ATR (Average True Range)

### What Was Added

**Calculation** ([techinical_factor.py](lib/techinical_factor.py)):
- New `atr()` method added to TechnicalFactors class
- New `calculate_atr()` standalone function
- Uses Wilder's smoothing (EMA with alpha=1/14)
- Automatically included in `run_all()` for high/low data

**Output Columns**:
- `atr_14`: ATR value in dollars

**Display Locations**:
1. **Chart annotation**: Shows ATR in dollars and as % of price
2. **Volatility section** of reports: 
   - ATR(14) in dollars
   - ATR as % of price (for position sizing)
3. **Trend analysis output**: Included in volatility analysis

### How to Use

**Stop-Loss Distance**:
- Conservative: 2x ATR below entry
- Moderate: 1.5x ATR below entry  
- Aggressive: 1x ATR below entry

Example: If ATR = $8.50 and entry = $305
- Conservative stop: $305 - (2 × $8.50) = $288
- Moderate stop: $305 - (1.5 × $8.50) = $292.25
- Aggressive stop: $305 - $8.50 = $296.50

**Position Sizing**:
- Risk per trade / ATR = number of shares
- Example: $500 risk, $8.50 ATR → 58 shares max

**Volatility Context**:
- ATR increasing = expanding volatility (wider stops needed)
- ATR decreasing = contracting volatility (breakout may be coming)
- High ATR% (>5%) = very volatile stock (reduce position size)
- Low ATR% (<2%) = stable stock (can use tighter stops)

**Comparison**:
| Stock | ATR | Price | ATR% | Interpretation |
|-------|-----|-------|------|----------------|
| AAPL  | $4.50 | $180 | 2.5% | Moderate volatility |
| NVDA  | $18.20 | $450 | 4.0% | High volatility |
| KO    | $1.20 | $60  | 2.0% | Low volatility |

---

## 3. 50-Day and 200-Day SMAs

### What Was Added

**Chart Display** ([plot_comprehensive_analysis.py](scripts/plot_comprehensive_analysis.py)):
- SMA(50): Orange dashed line (medium-term trend)
- SMA(200): Purple solid line (long-term trend)
- Both were already calculated but not displayed - now visible!

**Already Existed** (no calculation changes needed):
- Backend already calculated `sma_50` and `sma_200`
- Already calculated `dist_sma_50` and `dist_sma_200`
- Reports already showed distance percentages

### How to Use

**Trend Context**:
- Price > SMA(200) + SMA(50) rising = **Strong uptrend**
- Price < SMA(200) + SMA(50) falling = **Strong downtrend**  
- Price between 50 and 200 = **Transitional/choppy**

**Golden Cross / Death Cross**:
- **Golden Cross**: SMA(50) crosses above SMA(200) → Bullish
- **Death Cross**: SMA(50) crosses below SMA(200) → Bearish
- These are major trend signals (but can be late)

**Support/Resistance**:
- 50-day SMA: Medium-term support/resistance
  - Price pullbacks to rising 50-SMA often bounce (buy opportunity)
  - Price rallies to falling 50-SMA often fail (resistance)
- 200-day SMA: Major support/resistance
  - "Line in the sand" for long-term trend
  - Breaking above 200-SMA from below = very bullish
  - Breaking below 200-SMA from above = very bearish

**Distance Interpretation**:
- Price >10% above 200-SMA = Extended/overbought (potential pullback)
- Price >5% below 200-SMA = Oversold (potential bounce if trend intact)
- Price within ±5% of 200-SMA = Fair value zone

**Example Reading**:
```
Current Price: $305.20
SMA(50): $295.30 (+3.3% above 50-SMA)
SMA(200): $283.40 (+7.7% above 200-SMA)

Interpretation:
✓ Price above both 50 and 200-day SMAs → Uptrend intact
✓ 50-SMA above 200-SMA → Medium-term trend positive
✓ 7.7% above 200-SMA → Some extension but not extreme
→ CONCLUSION: Healthy uptrend with room to run
```

---

## Files Modified

### Core Library
1. **[lib/techinical_factor.py](lib/techinical_factor.py)**
   - Added `atr()` method (line 125)
   - Added `calculate_atr()` function (line 626)
   - Updated `run_all()` to include ATR calculation (line 209)

### Visualization
2. **[scripts/plot_comprehensive_analysis.py](scripts/plot_comprehensive_analysis.py)**
   - Added `identify_support_resistance()` function (line 31)
   - Enhanced price panel to show SMA(50) and SMA(200) (lines 97-100)
   - Added support/resistance level plotting (lines 181-200)
   - Added ATR annotation (lines 258-270)

### Analysis
3. **[scripts/trend_analyzer.py](scripts/trend_analyzer.py)**
   - Enhanced `analyze_volatility()` to include ATR (lines 162-165, 189-193)
   - Enhanced `identify_key_levels()` with swing high/low detection (lines 311-358)

### Reports
4. **[scripts/analyze_stock.py](scripts/analyze_stock.py)**
   - Updated volatility section to display ATR (lines 156-159)

---

## Testing the Enhancements

### Quick Test

```bash
cd technical_analysis
python scripts/analyze_stock.py AAPL --days 60
```

### What to Look For

**In the Chart** (`analyses/AAPL_Comprehensive_Chart_*.png`):
1. Orange and purple lines for 50 and 200-day SMAs
2. Red dashed lines above price (resistance) with labels
3. Green dashed lines below price (support) with labels
4. Purple box in top-left showing "ATR(14): $X.XX (X.X%)"

**In the Report** (`analyses/AAPL_Technical_Analysis_*.md`):
1. Section 3 (Volatility Analysis) shows ATR value
2. Section 5 (Support/Resistance) shows swing levels
3. All levels sorted by proximity to current price

### Example Output

**Console**:
```
Computing ATR...
Computing ADX...
Computing Stochastic...
All factors computed successfully!

VOLATILITY ANALYSIS
Level: NORMAL
- Annualized Volatility: 28.45%
- ATR(14): $8.50
  - ATR as % of price: 2.8%
- Bollinger Squeeze: NO

SUPPORT LEVELS:
  S1: $295.30 (2.8% below) - Swing Low
  S2: $290.15 (5.5% below) - SMA(50)

RESISTANCE LEVELS:
  R1: $310.50 (2.1% above) - SMA(20)
  R2: $313.25 (3.2% above) - Swing High
```

---

## Trading Workflow Example

### Swing Trade Setup

**Scenario**: Evaluating TXRH for a swing trade entry

1. **Run analysis**:
   ```bash
   python scripts/analyze_stock.py TXRH --days 60
   ```

2. **Check long-term trend** (50/200 SMAs):
   - Price $190, SMA(50) $185, SMA(200) $175
   - ✓ Price above both → Uptrend confirmed

3. **Identify entry zone** (support levels):
   - S1: $187 (Swing Low)
   - S2: $185 (SMA 50)
   - → **Entry target: $185-187 on pullback**

4. **Set stop-loss** (ATR-based):
   - ATR = $6.50 (3.4% of price)
   - Entry at $186 → Stop at $186 - (1.5 × $6.50) = $176
   - This is below S2 support, giving it room

5. **Set profit target** (resistance levels):
   - R1: $195 (Swing High)
   - R2: $200 (Round number + 30-day high)
   - → **Initial target: $195 (+4.8%)**

6. **Position sizing**:
   - Account size: $100K
   - Risk per trade: 1% = $1,000
   - Risk per share: $186 - $176 = $10
   - Max shares: $1,000 / $10 = **100 shares**

7. **Execution**:
   - Buy 100 shares at $185-187
   - Stop-loss at $176
   - Take 50% off at $195 (partial profit)
   - Trail stop for remaining 50 shares

### Why This Works Better Than Before

**Before enhancements**:
- "TXRH looks bullish" → vague, no actionable levels
- "Set a stop loss" → where exactly?
- "Take profits" → at what price?

**After enhancements**:
- Entry zone: $185-187 (support confluence)
- Stop: $176 (below support + 1.5x ATR)
- Target: $195 (resistance)
- Position size: 100 shares (risk-based on ATR)

---

## Tips for Using Each Enhancement

### Support/Resistance

**Best Used For**:
- Setting entry orders (buy at support, sell at resistance)
- Profit target placement
- Identifying breakout levels to watch

**Limitations**:
- Not always perfect - levels can be "broken" and then reverse
- Works best in ranging markets, less reliable in strong trends
- Psychological levels (round numbers) may not show up

**Pro Tip**: 
- Look for level confluence (e.g., Swing Low + SMA(50) at same price)
- More confluence = stronger level

### ATR

**Best Used For**:
- Stop-loss placement (1-2x ATR)
- Position sizing (risk/ATR = shares)
- Comparing volatility across stocks

**Limitations**:
- Doesn't predict direction, only magnitude
- Can expand after you enter (stops get hit)
- Very low ATR might precede big move (compression)

**Pro Tip**:
- Check ATR trend: if rising, use wider stops
- High ATR stocks → smaller position size
- Use ATR% to compare different price stocks

### 50/200 SMAs

**Best Used For**:
- Identifying long-term trend direction
- Major support/resistance zones
- Spotting golden/death crosses

**Limitations**:
- Lagging indicators (crossovers happen late)
- Choppy in sideways markets
- 200-SMA needs 200 days of data (IPOs don't have this)

**Pro Tip**:
- Don't trade against the 200-SMA trend (low probability)
- Use 50-SMA pullbacks as entries in 200-SMA uptrends
- Distance from 200-SMA shows if stock is stretched

---

## Common Questions

**Q: Why don't all stocks show all support/resistance levels?**

A: The algorithm filters levels to only show those within 20% of current price and clusters nearby levels. A stock in a strong trend may have few nearby levels.

**Q: Which ATR multiple should I use for stops?**

A: Depends on your holding period:
- Day trading: 0.5-1x ATR
- Swing trading: 1.5-2x ATR
- Position trading: 2-3x ATR

**Q: What if price is between 50 and 200 SMAs?**

A: This is a transitional zone. Wait for price to break above 50-SMA (bullish) or below 50-SMA (bearish) with volume before entering.

**Q: Can I customize the support/resistance detection?**

A: Yes! Edit `identify_support_resistance()` in `plot_comprehensive_analysis.py`:
- `window` parameter (default 10): Larger = fewer, stronger levels
- `num_levels` parameter (default 3): How many levels to show

**Q: Why is ATR sometimes missing?**

A: ATR requires 'high' and 'low' columns. If you only have adjusted_close data, ATR cannot be calculated. This usually only happens with very old or incomplete data.

---

## Next Steps

### Immediate Use
1. Run analysis on your current holdings
2. Note support/resistance levels relative to current price
3. Use ATR to recalibrate any existing stop-losses
4. Check 50/200 SMA position for trend context

### Further Enhancements (Future)
- Volume profile at support/resistance levels
- Fibonacci retracement levels
- Pivot points (classic floor trader method)
- Option Greeks integration for hedging
- Correlation with sector ETFs

---

**Last Updated**: 2026-07-11  
**Version**: 2.0  
**Added by**: Claude Code Enhancement Session
