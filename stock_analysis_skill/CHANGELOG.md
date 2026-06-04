# Stock Analysis Skill - Changelog

## Version 1.1 - 2026-06-03

### ✨ New Feature: 6-Month Price Trend Analysis

Added comprehensive recent price trend analysis to help understand WHY stocks are trading at current levels.

### What's New

#### 1. **Enhanced Price Analysis Script**
- **File**: `scripts/price_analysis.py`
- **Added Metrics**:
  - `six_months_ago_price`: Price exactly 6 months ago
  - `six_month_return`: Percentage change over 6 months
  - `six_month_high`: Highest price in past 6 months
  - `six_month_low`: Lowest price in past 6 months

**Example Output**:
```
======================================================================
6-MONTH PERFORMANCE
======================================================================

Price 6 Months Ago: USD 487.83
6-Month Return:     -12.4%
6-Month High:       USD 491.31
6-Month Low:        USD 355.51
```

#### 2. **Updated Skill Documentation**
- **File**: `SKILL.md`
- **Section 1.1**: New "Recent Price Trend Analysis (Past 6 Months)" component
- **Workflow Step 2**: Added requirement to gather 6-month price history and key events

**Key Requirements**:
- Calculate 6-month percentage change
- Identify major price movements (>10% moves)
- Link price movements to specific catalysts (earnings, announcements, macro events)
- Characterize overall trend pattern
- Analyze volume on major moves
- Compare to sector/market performance
- **Provide narrative explaining WHY stock is where it is today**

#### 3. **Enhanced Analysis Framework**
- **File**: `references/analysis-framework.md`
- **New Section**: "Recent Price Trend Analysis Framework (6 Months)"

**Analysis Process**:
1. **Calculate the Move**: 6-month return vs S&P 500 and sector
2. **Identify Key Events**: Map price to catalysts (earnings, M&A, regulatory, etc.)
3. **Assess Justification**: Fundamentally justified vs sentiment-driven
4. **Trend Characterization**: Bullish/bearish/neutral patterns
5. **Volume Context**: High vs low conviction moves
6. **Synthesize Narrative**: 2-3 paragraphs explaining what happened and why

**Red Flags**:
- Consistent downtrend despite positive earnings
- Failed rallies on good news
- High volume selloffs without bounce
- Divergence from peers
- Insider selling during decline

**Green Flags**:
- Holding support despite bad news
- Quick recovery from selloffs
- Outperformance during sector weakness
- Insider buying during decline
- Low volume selloffs

#### 4. **Updated Analysis Template**
- **File**: `references/analysis-template.md`
- **New Section**: "Recent Price Trend Analysis (Past 6 Months)"

**Template Structure**:
```markdown
### Recent Price Trend Analysis (Past 6 Months)

**6-Month Performance**:
- Price 6 months ago: $[X.XX] (date: [YYYY-MM-DD])
- Current price: $[X.XX]
- **6-month change: [±XX]%**
- S&P 500 change (same period): [±XX]%
- Sector ETF change: [±XX]%
- **Relative performance: [Outperformed/Inline/Underperformed]**

**Key Events Timeline**:
1. **[Date]** - [Event description] → Stock [+/-X]% on [volume]
2. **[Date]** - [Event description] → Stock [+/-X]% on [volume]

**Trend Narrative**:
[2-3 paragraphs explaining what happened and why]

**Volume Analysis**:
[High/Normal/Low volume on major moves]

**Key Takeaway**: [One sentence summary]
```

### Why This Matters

**Before**: Analysis showed stock was at LOW/MEDIUM/HIGH level but didn't explain HOW it got there.

**After**: Analysis now explains:
- What price movements occurred over past 6 months
- What specific events caused those movements
- Whether movements were justified or sentiment-driven
- What this means for investors today (opportunity vs warning)

### Example Use Cases

**Example 1: SAP** (from recent analysis)
- 6-month return: -38% (from $308 to $191)
- **Catalyst**: Cloud growth deceleration guidance in Q2
- **Assessment**: Partially justified by real risks but overdone given Q1 still +27% cloud growth
- **Implication**: Value opportunity for long-term investors

**Example 2: Microsoft** (from recent analysis)  
- 6-month return: -12.4% (from $487.83 to $427.34)
- **Catalyst**: Copilot adoption concerns, $190B capex fears
- **Assessment**: Sentiment-driven, fundamentals strong (Azure +40%, AI revenue $37B)
- **Implication**: Quality at temporary discount

**Example 3: Marvell** (from recent analysis)
- 6-month return: +375% (from $59 to $282)
- **Catalyst**: AI data center design wins, NVIDIA $2B investment
- **Assessment**: Fundamentally justified but valuation now extreme (96x P/E)
- **Implication**: Avoid at current levels despite quality

### Benefits

1. **Context**: Understand whether current price is opportunity or warning
2. **Catalyst Tracking**: Know what specific events moved stock
3. **Justification Assessment**: Distinguish fundamental changes from sentiment
4. **Relative Performance**: See if company-specific or sector-wide
5. **Better Decisions**: Make informed judgments on entry/exit timing

### Backward Compatibility

✅ All existing analyses remain valid
✅ New section is additive, doesn't break old format
✅ Script outputs both JSON (for programmatic use) and text (for reading)

### Usage

**Run price analysis script**:
```bash
python scripts/price_analysis.py "TICKER"
```

**Get JSON output** (includes 6-month metrics):
```bash
python scripts/price_analysis.py "TICKER" --json
```

**In analysis reports**, add the new "Recent Price Trend Analysis" section after "Price Level Assessment".

---

## Version 1.0 - 2026-06-01

Initial release with:
- Price level assessment (HIGH/MEDIUM/LOW)
- Moat scorecard (0-18 points)
- Current issues identification
- Management problem-solving assessment
- Investment recommendation (BUY/WATCH/AVOID)
