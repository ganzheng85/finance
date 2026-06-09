---
name: stock-analysis
description: Current stock price analysis and tactical company evaluation. Use when analyzing whether a stock is trading at high/medium/low levels, assessing company moats, evaluating current business issues, and judging management's problem-solving capability.
---

# Stock Analysis Skill

Produces tactical stock analysis focusing on current price levels, moat strength, business issues, and management's ability to solve problems. This complements strategic value-investing frameworks by adding real-time situational awareness.

## Workflow

1. **Confirm the target**
   Get the exact ticker, exchange, company name, and current business focus.

2. **Gather current data**
   Always fetch fresh data - prices, recent news, filings, earnings calls:
   - Current stock price and 52-week range
   - **6-month price history and trend analysis**
   - Recent trading volume and volatility
   - Latest earnings report and guidance
   - Recent news and company announcements
   - Key events that moved the stock (earnings, announcements, macro events)
   - Insider transactions if available
   - **Peer group valuation metrics and performance** (compare P/E, P/S, revenue growth to 3-5 key competitors)
   - **Debt-to-equity ratio and interest coverage ratios** (financial leverage and safety)
   - **Short interest percentage and institutional flows** (sentiment and smart money positioning)

3. **Use the analysis script** (if available)
   Run `python scripts/price_analysis.py "TICKER"` to get automated price metrics.

4. **Read the reference framework**
   Review `references/analysis-framework.md` for the scoring system.

5. **Produce the analysis**
   Use the template in `references/analysis-template.md`.

6. **If asked about strategic investment productivity** (AI, R&D, capex effectiveness):
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
│   ├── [TICKER]-YYYY-MM-DD.md          # Stock analysis report (markdown)
│   ├── [TICKER]-YYYY-MM-DD.pdf         # PDF version
│   ├── [ticker]-[theme]-YYYY-MM-DD.csv # Investment productivity analysis
│   └── ...                             # Multiple analyses over time
│
└── Example: META/
    ├── META-2026-06-04.md              # General stock analysis
    ├── META-2026-06-04.pdf
    ├── META-AI-Productivity-2026-06-07.md  # AI investment analysis
    ├── META-AI-Productivity-2026-06-07.pdf
    ├── meta-ai-productivity-analysis-2026-06-07.csv
    └── meta-ai-investment-returns-2026-06-07.csv

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
