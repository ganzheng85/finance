# Stock Analysis Framework

## Price Level Determination

### Data Points Needed
1. **Current Price**: Real-time or latest close
2. **52-Week Range**: High and low
3. **Historical Valuation**: P/E, P/S, P/B over 3-5 years
4. **Intrinsic Value Estimate**: DCF, comparables, or asset-based

### Classification Logic

**HIGH** - Stock is expensive relative to history and fundamentals
- Price > 90% of 52-week range, OR
- Current P/E > 1.5x historical average P/E, OR
- Price > 1.3x intrinsic value estimate
- **Signal**: Proceed with caution, need exceptional moat or growth

**MEDIUM** - Stock is fairly valued
- Price between 40-90% of 52-week range, AND
- Current P/E within 0.8-1.2x historical average, AND
- Price within 0.8-1.2x intrinsic value
- **Signal**: Fair entry point if fundamentals are solid

**LOW** - Stock is cheap relative to history
- Price < 40% of 52-week range, OR
- Current P/E < 0.7x historical average, OR
- Price < 0.7x intrinsic value
- **Signal**: Investigate WHY it's cheap - opportunity or value trap?

### Important Caveats
- Growth companies may always look "high" on traditional metrics
- Value traps often look "low" but deserve to be
- Sector rotation and macro factors can override individual metrics
- Always ask: "What does the market know that I don't?"

---

## Recent Price Trend Analysis Framework (6 Months)

### Purpose
Understanding WHY a stock moved helps determine whether current price is opportunity or warning sign. Recent price action provides context for valuation and sentiment.

### Data to Gather
1. **Price 6 months ago** (exact date: today minus 6 months)
2. **Highest and lowest prices in past 6 months**
3. **Key earnings reports** in period (usually 2 quarterly reports)
4. **Major news events** (product launches, acquisitions, regulatory, management changes)
5. **Sector/market performance** for comparison (S&P 500, relevant sector ETF)
6. **Volume spikes** indicating institutional activity

### Analysis Process

**Step 1: Calculate the Move**
- 6-month return: (Current Price - Price 6mo ago) / Price 6mo ago
- Compare to: S&P 500, Sector ETF, key competitors
- Characterize: Outperformer (>+10% vs market), Inline (-10% to +10%), Underperformer (<-10%)

**Step 2: Identify Key Events**
Map price movements to specific catalysts:
- **Earnings-related**: Beat/miss, guidance raise/cut, margin expansion/compression
- **Product/Business**: New product launch, customer win/loss, market share data
- **Strategic**: M&A announcement, partnership, restructuring, spin-off
- **Management**: CEO change, insider buying/selling, compensation changes
- **External**: Regulatory approval/denial, lawsuit outcome, tariff impact
- **Macro**: Fed policy, sector rotation, recession fears, commodity price moves

**Step 3: Assess Justification**
For each major move (>10%), determine:
- **Fundamentally justified**: Price moved due to changed business outlook
- **Sentiment-driven**: Price moved on fear/greed without fundamental change
- **Mixed**: Some fundamental change but market overreacted

**Step 4: Trend Characterization**

**Bullish Patterns**:
- Steady uptrend on improving fundamentals (healthy)
- Sharp rally on specific catalyst that remains intact (opportunity if pullback)
- Recovery from oversold levels as concerns prove overblown (turnaround)

**Bearish Patterns**:
- Steady decline on deteriorating fundamentals (avoid or wait)
- Sharp selloff on specific negative catalyst (assess if temporary or permanent)
- Failed rallies and lower highs (distribution, loss of support)

**Neutral/Mixed Patterns**:
- Sideways consolidation in range (uncertainty, waiting for catalyst)
- Volatile swings with no clear trend (conflicting signals)
- Sector-driven moves (company-specific factors less relevant)

**Step 5: Volume Context**
- **High volume moves**: Institutional participation, conviction (more significant)
- **Low volume moves**: Retail/technical, less conviction (can reverse easily)
- **Volume on up days vs down days**: Accumulation (buy) vs Distribution (sell)

**Step 6: Synthesize into Narrative**

Write 2-3 paragraphs answering:
1. **What happened**: "Stock fell 35% over past 6 months from $X to $Y"
2. **Why it happened**: "Driven primarily by [specific catalyst], compounded by [secondary factor]"
3. **Fundamental vs Sentiment**: "The selloff appears [justified/overdone/mixed] because..."
4. **Current implication**: "This creates [opportunity/warning/neutral setup] for investors today"

### Example Narratives

**Example 1: Justified Selloff (Warning Sign)**
"SAP fell 38% over the past 6 months from $308 to $191, primarily driven by management's guidance for cloud revenue growth deceleration in Q2 2026 and warnings of 'slight deceleration in cloud backlog growth over coming quarters.' The selloff accelerated after Q1 earnings despite beating estimates, as investors focused on forward guidance rather than backward results. Additionally, competitive concerns from ServiceNow's AI agent platform strategy and Middle East geopolitical impacts contributed to the decline. The move appears **partially justified** by real deceleration risks but **overdone** given that Q1 cloud revenue still grew 27%, operating margins expanded to 30%, and full-year guidance was maintained (not cut). This creates a **value opportunity** for long-term investors willing to accept near-term uncertainty."

**Example 2: Sentiment-Driven Selloff (Opportunity)**
"Meta fell 34% from October to March, dropping from $550 to $365, despite delivering strong Q3 results with 33% revenue growth and 61% profit growth. The selloff was driven entirely by **investor concerns over AI capex** ($125-145B guidance for 2026) and **fears about ROI timeline**, not deteriorating fundamentals. Reality Labs losses ($4B/quarter) added to skepticism. The move appears **unjustified by fundamentals** - Azure grew 40%, advertising business accelerated, and operating margins expanded. This represents a **high-conviction buying opportunity** as market overreacted to near-term spending fears."

**Example 3: Justified Rally (Chasing Risk)**
"Marvell rallied 375% over 6 months from $59 to $282, driven by explosive AI data center demand, custom silicon design wins (Amazon Trainium, Microsoft Maia, Google TPU), and raised guidance (FY2027 to $11.5B, FY2028 to $16.5B). NVIDIA's $2B equity investment in March validated the strategy. The move appears **fundamentally justified** by real business acceleration (data center revenue +50-55%), but valuation has become **extreme** at 96x P/E and 28x P/S, pricing in perfection. Stock is now at 99% of 52-week range at all-time highs. This creates **elevated risk** of pullback on any disappointment, making it an **avoid at current levels** despite business quality."

### Red Flags in Price Action
- Consistent downtrend despite positive earnings (market knows something)
- Failed rallies on good news (distribution, sellers waiting)
- High volume selloffs that don't bounce (capitulation or structural)
- Divergence from peers (company-specific problem vs sector move)
- Insider selling during price decline (management losing confidence)

### Green Flags in Price Action
- Holding support despite bad news (buyers stepping in, valuation floor)
- Quick recovery from selloffs (strong hands, conviction)
- Outperformance during sector weakness (relative strength)
- Insider buying during price decline (management sees value)
- Low volume selloffs (lack of conviction, technical)

---

## Peer Group Comparison Framework

### Purpose
Understanding relative valuation and performance helps determine if stock is cheap/expensive vs peers and if underperformance is company-specific or sector-wide.

### Peer Selection
Choose 3-5 direct competitors based on:
- Similar business model and revenue streams
- Similar market cap range (within 3x)
- Same industry/sector
- Geographic overlap

**Example Peer Groups**:
- **Microsoft**: SAP, Oracle, Salesforce, ServiceNow
- **Meta**: Alphabet (Google), Snap, Pinterest
- **ServiceNow**: Workday, SAP, Salesforce

### Metrics to Compare

**Valuation Multiples**:
| Metric | Company | Peer 1 | Peer 2 | Peer 3 | Industry Avg |
|--------|---------|--------|--------|--------|--------------|
| P/E    | 26.25   | 19.35  | 28.50  | 35.20  | 27.50       |
| P/S    | 10.3    | 6.02   | 8.5    | 12.1   | 9.2         |
| EV/EBITDA | 18.5 | 15.2   | 20.1   | 22.3   | 19.0       |

**Growth Metrics**:
| Metric | Company | Peer 1 | Peer 2 | Peer 3 |
|--------|---------|--------|--------|--------|
| Revenue Growth (YoY) | 18% | 12% | 25% | 15% |
| Cloud Revenue Growth | 40% | 27% | 35% | N/A |
| EBITDA Margin | 46% | 30% | 38% | 42% |

**Performance (6-month)**:
| Stock | Return | Reason for outperform/underperform |
|-------|--------|-------------------------------------|
| Company | -20% | Copilot adoption concerns |
| Peer 1 | -38% | Cloud deceleration worse |
| Peer 2 | +15% | AI monetization ahead |

### Interpretation
- **Premium valuation justified if**: Higher growth, better margins, stronger moat
- **Discount warranted if**: Company-specific issues, weaker competitive position
- **Relative opportunity if**: Trading at discount despite similar/better fundamentals

---

## Financial Metrics Framework

### Debt & Leverage Metrics

**Debt-to-Equity Ratio** = Total Debt / Total Equity
- **<0.5x**: Conservative (tech, asset-light businesses)
- **0.5-1.5x**: Moderate (most companies)
- **1.5-3x**: Elevated (capital-intensive, utilities)
- **>3x**: High risk (financial distress possible)

**Interest Coverage Ratio** = EBIT / Interest Expense
- **>8x**: Excellent (debt easily serviceable)
- **4-8x**: Good (comfortable margin)
- **2-4x**: Adequate (manageable but tight)
- **<2x**: Concerning (risk of financial distress)

**Net Debt/EBITDA** = (Total Debt - Cash) / EBITDA
- **<1x**: Very strong
- **1-3x**: Healthy
- **3-5x**: Elevated
- **>5x**: High risk

### Cash Flow Metrics

**Free Cash Flow** = Operating Cash Flow - Capital Expenditures
- Look for: Positive, growing, predictable
- Red flag: Negative or declining despite revenue growth

**FCF Conversion** = FCF / Net Income
- **>100%**: Excellent (high-quality earnings)
- **80-100%**: Good
- **60-80%**: Adequate
- **<60%**: Concerning (earnings quality questionable)

**FCF Yield** = (FCF / Market Cap) × 100%
- **>8%**: Very attractive
- **5-8%**: Good
- **3-5%**: Fair
- **<3%**: Expensive (unless high growth)

### Capital Allocation Metrics

**ROIC** = NOPAT / Invested Capital
- **>20%**: Exceptional (wide moat)
- **15-20%**: Excellent
- **10-15%**: Good
- **<10%**: Concerning (capital not earning return)

**ROIC vs WACC**:
- **ROIC > WACC + 5%**: Value creation
- **ROIC ≈ WACC**: Breakeven
- **ROIC < WACC**: Value destruction

### Short Interest & Institutional Flows

**Short Interest %** = Shares Shorted / Shares Outstanding
- **<3%**: Low (normal)
- **3-10%**: Moderate (some skepticism)
- **10-20%**: High (significant bearish sentiment)
- **>20%**: Extreme (short squeeze risk or real problems)

**Days to Cover** = Shares Shorted / Average Daily Volume
- **<2 days**: Easy to cover (less squeeze risk)
- **2-5 days**: Moderate
- **>5 days**: High (potential squeeze if positive catalyst)

**Institutional Ownership**:
- **Increasing**: Smart money accumulating (bullish)
- **Stable**: Neutral
- **Decreasing**: Smart money exiting (bearish)

**Insider Transactions**:
- **Insider buying**: Bullish signal (management sees value)
- **Insider selling**: Often neutral (diversification) unless unusual
- **Clustered buying**: Very bullish
- **Clustered selling**: Concerning

---

## Moat Scoring System

### 1. Brand Power (0-3)
- **3**: Dominant brand commanding premium pricing (Apple, Coca-Cola)
- **2**: Strong brand with regional or category leadership
- **1**: Recognized brand but limited pricing power
- **0**: Commodity or no-name brand

### 2. Network Effects (0-3)
- **3**: Product exponentially better with scale (Facebook, Visa)
- **2**: Meaningful benefit from user growth
- **1**: Minor network advantages
- **0**: No network effects

### 3. Cost Advantages (0-3)
- **3**: Structural 20%+ cost advantage vs competitors (Walmart, Costco)
- **2**: 10-20% cost edge from scale or process
- **1**: Minor cost efficiencies
- **0**: No cost advantage or at disadvantage

### 4. Switching Costs (0-3)
- **3**: Extremely high switching costs (enterprise software, banks)
- **2**: Moderate friction to switch (pain but doable)
- **1**: Low switching costs but some stickiness
- **0**: Customers can switch freely

### 5. Regulatory/IP Protection (0-3)
- **3**: Strong patent portfolio or regulatory exclusivity
- **2**: Some IP protection or regulatory barriers
- **1**: Minor regulatory advantages
- **0**: No regulatory or IP moat

### 6. Data Moat (0-3)
- **3**: Proprietary data that compounds and creates insurmountable advantage
- **2**: Meaningful data advantage that improves product
- **1**: Some data collection but limited moat
- **0**: No data advantage

**Total Moat Score Interpretation:**
- **15-18**: Exceptional moat, can justify premium valuation
- **10-14**: Strong moat, durable competitive advantage
- **6-9**: Moderate moat, vulnerable to competition
- **0-5**: Weak/no moat, commodity business

---

## Current Issues Framework

### Issue Categories

#### Revenue Issues
- Growth rate declining
- Customer churn increasing
- Market share loss
- Product obsolescence risk
- Geographic concentration risk

#### Margin Issues
- Input cost inflation
- Pricing pressure from competition
- Operating leverage deteriorating
- Mix shift to lower-margin products

#### Operational Issues
- Supply chain disruption
- Production quality problems
- Service delivery failures
- IT/infrastructure problems

#### Strategic Issues
- Wrong market positioning
- Failed M&A integration
- R&D productivity declining
- Business model under threat

#### Financial Issues
- High debt levels
- Covenant pressures
- Cash burn unsustainable
- Working capital deterioration

#### External Issues
- Regulatory investigation/changes
- Macroeconomic headwinds
- Industry disruption
- ESG controversies

#### Management Issues
- CEO/CFO turnover
- Executive scandals
- Board conflicts
- Succession uncertainty

### Issue Scoring

**Severity (1-5)**
- **5**: Existential threat to business
- **4**: Major profit/value destruction
- **3**: Significant impact, 10-20% EBIT hit
- **2**: Noticeable but manageable
- **1**: Minor irritant

**Urgency (1-5)**
- **5**: Crisis mode, immediate action required
- **4**: Quarterly horizon
- **3**: Annual horizon
- **2**: 2-3 year horizon
- **1**: Long-term watch item

**Trend**
- **Worsening**: Problem accelerating, no solution in sight
- **Stable**: Problem contained but not resolved
- **Improving**: Problem being addressed, early signs of fix

### Red Flags
Issues with Severity 4-5 + Urgency 4-5 + Worsening trend = **Critical situation**

---

## Management Problem-Solving Assessment

### Evidence to Examine

#### 1. Historical Track Record
- How did they handle the last crisis?
- Do they tend to overpromise and underdeliver?
- Have they successfully executed turnarounds?
- What's their batting average on strategic initiatives?

#### 2. Transparency and Candor
- Do they acknowledge problems honestly?
- Do they blame external factors vs owning issues?
- Are they transparent about metrics and setbacks?
- Do they pull guidance or sandbag?

#### 3. Action Plan Quality
- Is there a specific, credible plan?
- Are milestones and metrics defined?
- Does the plan address root causes vs symptoms?
- Are resources allocated appropriately?

#### 4. Speed of Execution
- How quickly did they recognize the problem?
- How fast are they implementing solutions?
- Are they decisively cutting losses or hoping?
- Is the organization mobilized?

#### 5. Capital Allocation During Stress
- Are they protecting the moat or cutting muscle?
- Are they making opportunistic investments?
- How are they managing cash and liquidity?
- Are insider incentives aligned?

#### 6. Stakeholder Management
- Do employees believe in the plan?
- Are customers staying or fleeing?
- Do suppliers trust them?
- Are investors aligned or activist?

### Management Verdict

**CAN SOLVE** (High Confidence)
- Proven track record with similar problems
- Candid about issues, specific action plan
- Adequate resources and moving quickly
- Early evidence plan is working

**CAN SOLVE** (Medium Confidence)
- Some track record but untested in this scenario
- Reasonable plan but execution uncertain
- Resources adequate but speed questionable

**UNCERTAIN**
- New management with no track record
- Problem acknowledged but plan unclear
- Conflicting signals on execution
- Need more time to assess

**CANNOT SOLVE** (Medium Confidence)
- Management denying or downplaying obvious issues
- Past failures addressing similar problems
- Inadequate resources or moving too slowly
- Fundamental capability gap

**CANNOT SOLVE** (High Confidence)
- Repeated failures and broken promises
- Problem beyond management's capability
- Insufficient resources and time running out
- Structural issue requiring board/ownership change

### Confidence Adjusters

**Increase Confidence When:**
- Multiple data points point same direction
- Management has "been here before"
- Insider buying during crisis
- Early KPI improvements visible

**Decrease Confidence When:**
- Limited information or transparency
- New/untested leadership team
- Complex, multi-factor problems
- External factors dominant vs controllable factors

---

## Synthesis: From Analysis to Recommendation

### BUY
- Price Level: LOW to MEDIUM
- Moat Score: 10+
- Current Issues: Severity < 4 OR proven management can solve
- Management: CAN SOLVE (high confidence)

**Thesis**: Quality business, temporary issues, capable management, attractive price

### WATCH
- Price Level: Any, but HIGH requires exceptional quality
- Moat Score: 6+
- Current Issues: Being addressed but outcome uncertain
- Management: CAN SOLVE (medium confidence) or UNCERTAIN

**Thesis**: Interesting business, need to see proof of execution before committing

### AVOID
- Price Level: Any (even LOW can be a trap)
- Moat Score: < 6, OR
- Current Issues: Severity 5, OR
- Management: CANNOT SOLVE, OR
- Multiple red flags across categories

**Thesis**: Too much risk, better opportunities elsewhere

### Override Scenarios

A single critical factor can override the framework:
- **Fraud/Ethics**: Automatic AVOID regardless of price/moat
- **Bankruptcy Risk**: Automatic AVOID unless recovery play with asymmetric upside
- **Moat Collapse**: Even cheap price doesn't justify if competitive advantage gone
- **Exceptional Opportunity**: Very cheap + strong moat + solvable issue = BUY even if management track record mixed
