---
name: fundamental-analysis
description: Fundamental stock research and company data analysis tool. Use when user asks for stock analysis, fundamental analysis, or company analysis. ALWAYS generates COMPREHENSIVE, fully-researched reports with actual analysis, scores, and recommendations - NOT templates or preliminary reports.
---

# Fundamental Analysis Research Tool

**CRITICAL: This skill generates COMPREHENSIVE, fully-researched fundamental analysis reports.**

When invoked, you MUST produce a complete analysis with:
- ✅ Actual moat scores (0-18) with specific evidence for each category
- ✅ Real financial metrics from SEC filings and earnings reports
- ✅ Management quality assessment with track record analysis
- ✅ Specific issues identified with severity ratings
- ✅ Bull/Base/Bear scenario analysis with price targets
- ✅ Investment thesis and clear recommendation (BUY/HOLD/SELL)

**DO NOT generate template reports or preliminary reports that require "manual completion."**

This tool provides comprehensive analytical research for educational and research purposes, not investment recommendations.

## Reference Sample

**See**: `analyses/MSFT/MSFT-2026-06-19.md` and `analyses/META/META-2026-06-20.md` - Complete, validated fundamental analysis reports. These reports demonstrate the REQUIRED quality standard:
- Comprehensive moat analysis with actual scores (16-17/18) and specific evidence
- Real financial metrics from SEC filings (margins, ROE, revenue growth)
- Management quality assessment with historical track record
- Specific issues identified (e.g., "AI Capex Explosion: $125-145B")
- Bull/Base/Bear scenarios with specific price targets ($650-700, $820-880, $380-420)
- Investment thesis and clear recommendation (QUALIFIED BUY, position sizing guidance)
- Data validated against Yahoo Finance (all metrics passed validation)
- Professional HTML output with print-to-PDF button

**EVERY fundamental analysis report MUST match this quality level - fully researched and complete, not preliminary templates.**

## Workflow

**IMPORTANT: Generate COMPREHENSIVE analysis, not templates. Follow the META-2026-06-20.md or MSFT-2026-06-19.md examples.**

### Smart Update: Same-Day Report Optimization

**Report Naming Convention:**
- Format: `{TICKER}-YYYY-MM-DD-HHMM.md`
- Example: `META-2026-06-21-1154.md` (generated at 11:54 AM)
- **Multiple reports per day allowed** - each gets unique timestamp

**If a report already exists for the same ticker on the same day:**
- ✅ **Finds most recent report** (by modification time)
- ✅ **Update Yahoo Finance data only** (price, volume, P/E ratios - updated hourly)
- ✅ **Reuse all research** (moat analysis, management assessment, competitive analysis, scenarios)
- ❌ **Skip web searches** (fundamental research doesn't change intraday)

**If no report exists for today or it's a different day:**
- ✅ **Full comprehensive analysis** with web research
- ✅ **New report created** with current hour-minute timestamp

This saves time while keeping price data current and preserving historical snapshots.

---

### Step-by-Step Workflow

**Step 1: Check for existing same-day report**
```bash
# Look for: analyses/{TICKER}/{TICKER}-{TODAY}-*.md
# Example: analyses/META/META-2026-06-21-1154.md
# Note: Multiple reports per day allowed - uses most recent
```

**Step 2A: If same-day report EXISTS → Smart Update (Fast Path)**
```bash
python scripts/update_report_data.py {TICKER}
```
- ✅ Updates ONLY Yahoo Finance data (price, volume, ratios)
- ✅ Preserves ALL research (moat, management, scenarios)
- ✅ Regenerates HTML
- ⏱️ Takes ~5-10 seconds
- **Done!** No web research needed.

**Step 2B: If NO same-day report → Full Comprehensive Analysis**

Follow these substeps:

1. **Confirm the target**
   - Get exact ticker, exchange, company name, current business focus

2. **Gather current data**
   Fetch fresh data - prices, recent news, filings, earnings calls:
   - Current stock price and 52-week range
   - 6-month price history and trend analysis
   - Recent trading volume and volatility
   - Latest earnings report and guidance
   - Recent news and company announcements
   - Key events that moved the stock
   - Peer group valuation metrics (compare to 3-5 competitors)
   - Debt-to-equity and interest coverage ratios
   - Short interest and institutional flows

3. **Conduct comprehensive research** (REQUIRED)
   - **Moat Analysis**: Research competitive advantages, assign scores 0-3 for each category with evidence
   - **Financial Analysis**: Pull metrics from 10-K/10-Q (margins, ROE, growth rates)
   - **Management Assessment**: Review track record, capital allocation decisions
   - **Issue Identification**: Research current challenges from earnings calls and news
   - **Competitive Analysis**: Compare positioning vs competitors
   - **Scenario Building**: Develop bull/base/bear cases with specific price targets

4. **Use Agent tool to generate comprehensive analysis**
   **CRITICAL**: Use the Agent tool to conduct full research and generate a complete report:
   - The Agent will web search for recent earnings, filings, news
   - The Agent will analyze competitive moat with scores and evidence
   - The Agent will build scenario analysis with price targets
   - The Agent will write the complete report to the markdown file
   
   **DO NOT** just run `generate_comprehensive_report.py` - it only creates structure, not analysis.
   **DO NOT** generate template reports that say "Requires Manual Analysis" - do the analysis.

5. **Reference format**
   Follow `analyses/MSFT/MSFT-2026-06-19.md` or `analyses/META/META-2026-06-20.md` exactly:
   - Actual moat scores (e.g., 16/18) with specific evidence
   - Real financial metrics from filings
   - Management assessment with track record
   - Specific issues (e.g., "AI Capex: $125-145B")
   - Bull/Base/Bear with price targets ($650-700, $820-880, $380-420)
   - Clear recommendation (QUALIFIED BUY, position sizing)

6. **Generate highlights summary**
   Create a concise highlights version (2-4 pages) containing:
   - Executive Summary with verdict and price targets
   - Key investment thesis points (3-5 bullets)
   - Valuation snapshot (P/E, P/S, DCF fair value)
   - Risk/reward scenario analysis
   - Top catalysts and monitoring metrics
   - Quick reference table
   Save as `[TICKER]-YYYY-MM-DD-Highlights.md`

7. **Convert to HTML**
   Run `python ../utils/md_to_html.py` (shared utility) on both full report and highlights:
   - `analyses/[TICKER]/[TICKER]-YYYY-MM-DD.md` → `.html`
   - `analyses/[TICKER]/[TICKER]-YYYY-MM-DD-Highlights.md` → `.html`
   
   **Note**: The HTML converter generates professional reports viewable in any browser with a built-in print-to-PDF button. No spacing issues like PDF libraries.

8. **Validate Report Data** ⚠️ CRITICAL - ALWAYS RUN
   **MANDATORY**: Run validation after generating every report to catch hallucination errors:
   ```bash
   python scripts/validate_report_data.py TICKER --report analyses/TICKER/TICKER-YYYY-MM-DD.md
   ```
   
   This validates that all financial metrics in the report match actual Yahoo Finance data:
   - Price metrics (current, 52-week high/low, range position)
   - Valuation ratios (P/E, P/S, P/B)
   - Return calculations (6-month performance)
   - Volume data
   
   **Action on Mismatches**:
   - If validation finds mismatches, investigate and correct the report immediately
   - Review which values are incorrect and update them in the markdown
   - Re-run validation until all checks pass (0 mismatches)
   - Never publish or share a report with unresolved validation errors
   
   **Reference Sample** (all validation passed):
   ```bash
   python scripts/validate_report_data.py MSFT --report analyses/MSFT/MSFT-2026-06-19.md
   
   # Output:
   # [OK] All values validated successfully!
   # Summary:
   #   [OK] Matches:    11
   #   [X]  Mismatches: 0
   #   [!]  Missing:    0
   ```
   
   See `scripts/README_VALIDATION.md` for detailed documentation.

8. **If asked about strategic investment productivity** (AI, R&D, capex effectiveness):
   - Create a **multi-quarter comparison CSV file** with quantitative metrics
   - Include 4-8 quarters of historical data (minimum 2 years)
   - Define clear thresholds for success/failure
   - Provide quick assessment checklist
   - Save to `references/[COMPANY]-[THEME]-productivity-metrics.csv`

## Analysis Components

### 1. Price Level Assessment
Determine if the stock is trading at HIGH, MEDIUM, or LOW levels based on:
- Current price vs 52-week high/low
- Current price vs historical valuation multiples (P/E, P/S, P/B)
- Price vs analyst targets (if available)
- Price vs intrinsic value estimates
- Technical support/resistance levels

Output: **HIGH** / **MEDIUM** / **LOW** with percentage metrics

### 1.1 Recent Price Trend Analysis (Past 6 Months)
Analyze and explain the stock's recent price movements:
- **6-month price change**: Calculate percentage change from 6 months ago to current
- **Key inflection points**: Identify major price movements (>10% moves)
- **Catalyst identification**: Link price movements to specific events:
  - Earnings beats/misses and guidance changes
  - Product launches or strategic announcements
  - Management changes or insider transactions
  - Regulatory news or legal developments
  - Macroeconomic events (Fed decisions, sector rotation)
  - Competitive dynamics or industry shifts
- **Trend characterization**: Describe the overall pattern (steady decline, volatile consolidation, strong rally, etc.)
- **Volume analysis**: Were moves on high or low volume? (Conviction vs noise)
- **Comparison to sector/market**: Did stock outperform or underperform broader indices?

Output: **Clear narrative explaining WHY the stock is where it is today**

Key questions to answer:
- What happened 6 months ago and why did price move from there?
- Were the price movements justified by fundamentals or sentiment-driven?
- Is current price a result of temporary factors or structural changes?
- Does the recent trend support or contradict your investment thesis?

### 2. Moat Analysis
Evaluate competitive advantages:
- **Brand Power**: Pricing power, customer loyalty, brand recognition
- **Network Effects**: Does the product get better with more users?
- **Cost Advantages**: Scale, proprietary tech, better processes
- **Switching Costs**: Customer lock-in, integration depth
- **Regulatory/IP Protection**: Patents, licenses, regulatory barriers
- **Data Moat**: Proprietary data that compounds over time

Score each: 0 (none), 1 (weak), 2 (moderate), 3 (strong)
Output: **Total Moat Score: X/18** with breakdown

### 3. Current Issues Identification
Identify and categorize active problems:
- **Revenue Issues**: Growth slowing, customer churn, market share loss
- **Margin Issues**: Cost inflation, pricing pressure, competitive dynamics
- **Operational Issues**: Supply chain, production, service quality
- **Strategic Issues**: Wrong market positioning, failed initiatives
- **Financial Issues**: Debt load, cash burn, liquidity concerns
- **External Issues**: Regulatory, macro, industry disruption
- **Management Issues**: Turnover, scandal, poor execution

For each issue, rate:
- **Severity**: 1 (minor) to 5 (critical)
- **Urgency**: 1 (long-term) to 5 (immediate crisis)
- **Trend**: Improving / Stable / Worsening

### 4. Management Problem-Solving Assessment
Evaluate leadership's capability to address issues:
- **Track Record**: How did management handle past crises?
- **Transparency**: Are they candid about problems?
- **Action Plan**: Do they have a credible solution path?
- **Resource Allocation**: Are they directing capital/talent appropriately?
- **Execution Speed**: How quickly are they moving?
- **Stakeholder Alignment**: Are employees/customers/investors aligned?

Output: **CAN SOLVE** / **UNCERTAIN** / **CANNOT SOLVE**
Provide evidence and confidence level (High/Medium/Low)

### 5. Financial Resilience & Capital Allocation
Assess the company's financial health and capital deployment:

**Balance Sheet Strength**:
- **Debt-to-Equity Ratio**: Total debt / Total equity (compare to industry average)
- **Interest Coverage Ratio**: EBIT / Interest Expense (ability to service debt)
- **Net Debt / EBITDA**: (Total Debt - Cash) / EBITDA (leverage multiple)
- **Current Ratio**: Current Assets / Current Liabilities (short-term liquidity)
- **Cash Position**: Absolute cash levels and burn rate

**Cash Flow Health**:
- **Free Cash Flow**: Operating Cash Flow - Capex
- **FCF Conversion**: FCF / Net Income (quality of earnings)
- **FCF Yield**: FCF / Market Cap (cash generation vs valuation)
- **Working Capital Trend**: Improving or deteriorating?

**Capital Allocation Quality**:
- **Return on Invested Capital (ROIC)**: NOPAT / Invested Capital (>15% excellent, <10% concerning)
- **ROIC vs WACC**: Is company creating value? (ROIC > WACC)
- **Capital Deployment**: Where is cash going? (R&D, M&A, buybacks, dividends, debt paydown)
- **Share Buybacks**: Are they buying at good prices or destroying value?
- **Dividend Policy**: Sustainable? Growing? Payout ratio reasonable?
- **M&A Track Record**: Creating or destroying shareholder value?

**Financial Resilience Score**:
- **Strong** (0-2 concerns): Fortress balance sheet, strong FCF, excellent capital allocation
- **Adequate** (3-4 concerns): Some leverage but manageable, decent FCF, mixed allocation
- **Weak** (5+ concerns): High debt, poor FCF, questionable capital allocation

Output: **Financial Resilience: Strong / Adequate / Weak** with specific metrics and concerns

### 6. Investment Thesis, Catalysts, and Risks
Articulate the complete investment case:

**Investment Thesis** (Why own this stock):
- **Core Thesis**: One clear sentence stating why this is a good/bad investment
- **Supporting Pillars**: 3-5 key reasons supporting the thesis
- **Differentiation**: What makes this opportunity unique or compelling?
- **Time Horizon**: Is this a 6-month trade, 2-year hold, or 10-year compounder?

**Upside Catalysts** (What could drive stock higher):
- **Near-term (0-6 months)**: Earnings beats, product launches, contract wins
- **Medium-term (6-18 months)**: New market entry, margin expansion, strategic shifts
- **Long-term (18+ months)**: TAM expansion, secular trends, market share gains
- **Probability-weighted**: Assign rough probabilities to each catalyst

**Downside Risks** (What could drive stock lower):
- **Company-specific**: Execution failures, competitive losses, management turnover
- **Industry risks**: Regulation, disruption, cyclical downturns
- **Macro risks**: Recession, interest rates, geopolitical events
- **Valuation risk**: Multiple compression if growth disappoints
- **Probability assessment**: Which risks are most likely?

**Key Inflection Points**:
- What specific events would confirm or invalidate the thesis?
- What metrics should you monitor quarterly?
- What would cause you to exit the position (stop-loss triggers)?

**Risk-Reward Framework**:
- **Bull Case Return**: [+XX%] if everything goes right (probability: XX%)
- **Base Case Return**: [+XX%] if likely scenario plays out (probability: XX%)
- **Bear Case Return**: [-XX%] if key risks materialize (probability: XX%)
- **Expected Value**: Probability-weighted return
- **Asymmetry**: Is the risk-reward skewed to upside or downside?

Output: **Clear, actionable investment thesis with defined catalysts, risks, and expected returns**

### 7. Strategic Investment Productivity Analysis (AI, R&D, Capex)

When asked to prove whether strategic investments (AI, R&D, new products, capex) are productive:

**Approach**:
1. **Identify the investment theme**: AI infrastructure, R&D spending, geographic expansion, M&A, etc.
2. **Define quantitative metrics** that would prove productivity:
   - **Revenue metrics**: Growth rate, ARPU, pricing power
   - **Profitability metrics**: Operating margin, FCF margin, ROIC
   - **Efficiency metrics**: Revenue per employee, revenue per $ invested
   - **Product metrics**: User growth, engagement, conversion rates
   - **Return metrics**: Incremental revenue / investment, payback period
3. **Gather historical data**: Pull metrics from last 4-8 quarters (2 years)
4. **Create comparison table**: Show quarter-over-quarter or year-over-year trends
5. **Identify inflection points**: When did metrics start improving after investment?
6. **Calculate ROI**: Quantify investment amount vs benefit generated
7. **Save to CSV**: Create structured table for easy analysis

**Output Requirements**:
- **CSV file** with columns: Metric, Q1 YYYY, Q2 YYYY, Q3 YYYY, Q4 YYYY, ..., Status (PASS/CAUTION/FAIL), Notes
- **Critical metrics section** (top 5-7 most important)
- **Supporting metrics section** (10-15 additional metrics)
- **Quick assessment checklist** (YES/NO questions for rapid evaluation)
- **Thresholds**: Define "good" vs "bad" values for each metric
- **Data sources**: Where to find each metric in earnings reports/filings
- **Verdict logic**: How to combine metrics into overall BUY/WATCH/AVOID decision

**Example Use Cases**:
- "Prove Meta's AI investments are productive" → Compare ARPU, operating margin, revenue growth, DAU growth, Reels engagement across 8 quarters
- "Is Amazon's AWS capex paying off?" → Compare AWS revenue growth, operating margin, revenue/capex ratio across quarters
- "Did Netflix's content spending work?" → Compare subscriber growth, engagement hours, revenue/subscriber, content ROI

**File Naming Convention**:
- `references/[COMPANY]-[INVESTMENT_THEME]-productivity-metrics.csv` (comprehensive)
- `references/[COMPANY]-[INVESTMENT_THEME]-quick-checklist.csv` (rapid assessment)

**Template Structure** (save as CSV):
```
Category,Metric,Formula,What to Look For,Q1 2023,Q2 2023,Q3 2023,Q4 2023,Q1 2024,Q2 2024,Q3 2024,Q4 2024,Good Threshold,Bad Threshold,Where to Find
Revenue,Revenue Growth % Y/Y,...,...,Fill,Fill,Fill,Fill,Fill,Fill,Fill,Fill,>15%,<5%,Income statement
Profitability,Operating Margin %,...,...,Fill,Fill,Fill,Fill,Fill,Fill,Fill,Fill,>30%,<20%,Income statement
...
```

This allows **data-driven analysis** of whether strategic investments are creating value, using concrete numbers from financial reports rather than management promises.

## Output Structure

All analysis outputs are organized by ticker symbol for easy access:

```
analyses/
├── [TICKER]/                           # Folder per stock ticker
│   ├── [TICKER]-YYYY-MM-DD-HHMM.md     # Full stock analysis report (markdown)
│   ├── [TICKER]-YYYY-MM-DD-HHMM.html   # Full report HTML version (view in browser)
│   ├── [TICKER]-YYYY-MM-DD-HHMM-Highlights.md  # Concise highlights summary
│   ├── [TICKER]-YYYY-MM-DD-HHMM-Highlights.html # Highlights HTML version
│   ├── [ticker]-[theme]-YYYY-MM-DD.csv # Investment productivity analysis
│   └── ...                             # Multiple analyses per day allowed
│
└── Example: META/
    ├── META-2026-06-20-2315.md         # Generated at 11:15 PM
    ├── META-2026-06-20-2315.html       # HTML version with print-to-PDF button
    ├── META-2026-06-21-1154.md         # Generated at 11:54 AM (next day)
    ├── META-2026-06-21-1154.html       # Most recent version
    ├── META-2026-06-21-1430.md         # Updated at 2:30 PM (same day)
    ├── META-2026-06-21-1430.html       # Latest intraday update
    ├── META-AI-Investment-Productivity-2026-06-08.md  # AI investment analysis
    ├── META-AI-Investment-Productivity-2026-06-08.html
    ├── meta-ai-productivity-analysis-2026-06-08.csv
    └── meta-ai-quick-checklist-2026-06-08.csv

data/
├── [TICKER]/                           # Raw quarterly data per ticker
│   ├── [ticker]_quarterly_income.csv   # Income statements
│   ├── [ticker]_quarterly_balance.csv  # Balance sheets
│   └── [ticker]_quarterly_cashflow.csv # Cash flow statements
│
└── Example: META/
    ├── meta_quarterly_income.csv
    ├── meta_quarterly_balance.csv
    └── meta_quarterly_cashflow.csv
```

## Output Format

Use the structure in `references/analysis-template.md`:

```markdown
# [COMPANY] Stock Analysis
**Ticker**: [SYMBOL] | **Date**: [DATE] | **Price**: $[PRICE]

## Executive Summary
[2-3 sentence verdict on price level, moat strength, key issues, and management capability]

## 1. Price Level: [HIGH/MEDIUM/LOW]
- Current: $X ([±Y]% from 52-week high/low)
- Valuation metrics vs history
- Assessment rationale

### Recent Price Trend (Past 6 Months)
- 6-month change: [±X]%
- Key events that moved stock
- Trend narrative and catalyst analysis
- Comparison to sector/market performance

## 2. Moat Scorecard: [X/18]
- Brand Power: [0-3]
- Network Effects: [0-3]
- Cost Advantages: [0-3]
- Switching Costs: [0-3]
- Regulatory/IP: [0-3]
- Data Moat: [0-3]

## 3. Current Issues
[List with severity, urgency, trend]

## 4. Management Assessment: [CAN SOLVE / UNCERTAIN / CANNOT SOLVE]
Evidence:
- Track record
- Current actions
- Resource deployment
Confidence: [High/Medium/Low]

## 5. Financial Resilience & Capital Allocation: [Strong / Adequate / Weak]
**Balance Sheet**:
- Debt-to-Equity: [X.XX]x (vs industry [X.XX]x)
- Interest Coverage: [X.XX]x
- Net Debt/EBITDA: [X.XX]x

**Cash Flow**:
- Free Cash Flow: $[X]B ([±X]% YoY)
- FCF Yield: [X.X]%
- FCF/Net Income: [X.X]x

**Capital Allocation**:
- ROIC: [XX]% (vs WACC [XX]%)
- Capital deployment quality
- Key concerns or strengths

## 6. Investment Thesis, Catalysts & Risks
**Core Thesis**: [One sentence investment case]

**Upside Catalysts**:
- Near-term: [List]
- Medium-term: [List]
- Long-term: [List]

**Downside Risks**:
- Company-specific: [List]
- Industry/Macro: [List]
- Valuation: [Assessment]

**Expected Returns**:
- Bull case: [+XX%] (probability: XX%)
- Base case: [+XX%] (probability: XX%)
- Bear case: [-XX%] (probability: XX%)
- Expected value: [+XX%]

## 7. Recommendation
[BUY / WATCH / AVOID] with reasoning

## 8. Strategic Investment Productivity Analysis (Optional)
**If analyzing AI/R&D/Capex effectiveness**:

See separate CSV file: `references/[COMPANY]-[THEME]-productivity-metrics.csv`

**Quick Assessment**:
- Critical metrics improving: [X/5] PASS
- Supporting metrics improving: [X/10] PASS
- Overall verdict: [Investment is PRODUCTIVE (PASS) / UNCERTAIN (CAUTION) / FAILING (FAIL)]
- Key evidence: [1-2 sentence summary]

**Implications for Investment Thesis**:
- If productive → [How this strengthens/weakens the investment case]
- If uncertain → [What to monitor, when to reassess]
- If failing → [Impact on moat, margins, competitive position]

## Sources
[Links to data, filings, news]
```

### Highlights Report Format

**Purpose**: Provide a concise 2-4 page summary for quick decision-making.

**File Naming**: `[TICKER]-YYYY-MM-DD-Highlights.md`

```markdown
# [COMPANY] ([TICKER]) - Investment Highlights

**Date**: [DATE] | **Current Price**: $[PRICE] | **Market Cap**: $[X]B

---

## Executive Summary

**VERDICT: [STRONG BUY / BUY / HOLD / SELL]** - [One-line rationale]

**Price Action**: [Down/Up X% from peak]  
**Valuation**: Trading at [X]x P/S vs historical [X]x ([X]% discount/premium)  
**Target Price**: $[X-Y] (base case), $[X-Y] (bull case)  
**Expected Return**: **[+X%]** over [24] months (~[X]% annualized)

---

## Investment Thesis - Why [VERDICT]?

### 1. [First Key Point - e.g., Extreme Valuation]
[2-3 sentence explanation with key metrics table]

### 2. [Second Key Point - e.g., Sentiment vs Fundamentals]
[2-3 sentence explanation with evidence]

### 3. [Third Key Point - e.g., Best-in-Class Metrics]
[2-3 sentence explanation with peer comparison]

### 4. [Fourth Key Point - e.g., Competitive Moat]
[2-3 sentence explanation with moat score]

### 5. [Fifth Key Point - e.g., Strategic Positioning]
[2-3 sentence explanation with traction metrics]

---

## Risk/Reward Analysis

### Scenario Analysis

| Scenario | Probability | Price Target | Return from $[X] |
|----------|-------------|--------------|------------------|
| **Bull Case** | [X]% | $[X] | +[X]% |
| **Base Case** | [X]% | $[X] | +[X]% |
| **Bear Case** | [X]% | $[X] | -[X]% |
| **Expected Value** | 100% | **$[X]** | **+[X]%** |

**Upside/Downside Ratio: [X]:1**

[Brief paragraph for each scenario explaining key assumptions]

---

## Key Issues and How Management is Solving Them

### Issue #1: [Name]
**Problem**: [1-2 sentence description]  
**Management Solution**: [2-3 sentences]  
**Confidence**: [High/Medium/Low]

### Issue #2: [Name]
[Same structure]

---

## Investment Recommendation

### Rating: **[STRONG BUY / BUY / HOLD / SELL]**

**Position Size**: [X-Y]% of portfolio  
**Time Horizon**: [X] years  
**Confidence Level**: [High/Medium/Low] ([X]/10)

### Entry Strategy
[Aggressive/Moderate/Conservative approaches]

### Sell Discipline
**Take Profits**: [Price levels]  
**Exit Signals**: [List of red flags]

---

## Key Catalysts and Monitoring

### Near-Term Catalysts (Next 3-6 Months)
1. [Event/Metric to watch]
2. [Event/Metric to watch]

### Success Criteria
**By End of [YEAR]**: [List of checkboxes]  
**By End of [YEAR+1]**: [List of checkboxes]

### Warning Signs (Reduce Position)
- [Metric/Event threshold]
- [Metric/Event threshold]

---

## Quick Reference

### Stock Metrics
- **Current Price**: $[X]
- **52-Week Range**: $[X] - $[X]
- **YTD Performance**: [±X]%
- **Market Cap**: $[X]B

### Valuation
- **P/S**: [X]x (vs [X]x historical)
- **Forward P/E**: [X]x
- **PEG Ratio**: [X]
- **EV/Sales**: [X]x

### Fundamentals (Latest Quarter)
- **Revenue**: $[X]B ([±X]% YoY)
- **Operating Margin**: [X]%
- **FCF Margin**: [X]%
- **Rule of 40**: [X]

### Growth Metrics
[3-5 key metrics relevant to company]

---

**Report Date**: [DATE]  
**Next Review**: [Upcoming event/earnings date]  
**Analyst**: Claude Sonnet 4.5

**Disclaimer**: This analysis is for informational purposes only and does not constitute investment advice.
```

## Rules and Filters

- Always fetch current prices - stale data leads to bad decisions
- Distinguish between temporary issues and structural problems
- Don't conflate low price with good value (it might be low for a reason)
- Don't confuse high price with overvaluation (quality often trades at premium)
- Be brutally honest about management capability - hope is not a strategy
- If key data is missing, state it clearly and adjust confidence accordingly

## Hard Filters - Auto-Downgrade to AVOID

- Critical financial distress (bankruptcy risk within 12 months)
- Management fraud or severe ethical violations
- Structural moat collapse with no recovery path
- Business model obsolescence (Blockbuster moment)

## Source Priority

1. Official company filings (10-K, 10-Q, 8-K for US; equivalents elsewhere)
2. Earnings call transcripts and investor presentations
3. Real-time price data from reliable sources
4. Industry reports and competitor filings
5. Credit ratings and analyst reports (use carefully, check assumptions)
6. News and social sentiment (context only, not decision driver)

## Anti-Patterns to Avoid

- Starting from the chart and working backwards to justify it
- Ignoring issues because you like the company
- Overweighting management PR vs actual results
- Confusing correlation with causation in price movements
- Assuming mean reversion without understanding what changed
- Anchoring on your purchase price instead of current reality

## Notes

This skill is for informed decision support, not financial advice. Always:
- State your assumptions clearly
- Show your work
- Admit uncertainty
- Provide sources
- Separate facts from interpretation
