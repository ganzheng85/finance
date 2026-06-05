---
name: ercot-analysis
description: "ERCOT electricity market daily analysis. Use when analyzing ERCOT grid conditions today including: price spikes, price volatility, generator outages, transmission congestion, wind and solar contribution, battery storage performance, and overall grid health."
---

# ERCOT Market Analysis Skill

Produces a comprehensive daily analysis of the ERCOT (Electric Reliability Council of Texas) wholesale electricity market, covering price dynamics, grid reliability, renewable generation, and battery storage performance.

## Workflow

### 1. Confirm the analysis date
Default to **today** (current date in Central Time). Confirm whether the user wants:
- Real-time/current conditions (last few hours)
- Full-day summary (requires end-of-day data)
- Specific past date

### 2. Fetch ERCOT market data
Run the data fetching script for today's date:
```
python scripts/fetch_ercot_data.py --date TODAY --output data/
```
The script retrieves:
- Real-time settlement point prices (15-min intervals)
- Day-ahead vs real-time price spreads
- Generator outage reports
- Transmission constraint shadow prices
- Generation mix by fuel type (wind, solar, gas, nuclear, coal, hydro, battery)
- Battery storage charge/discharge dispatch

If the script is unavailable, fetch data manually from sources in `references/data-sources.md`.

### 3. Read the analysis framework
Review `references/analysis-framework.md` for classification thresholds, scoring rubrics, and interpretation guidelines.

### 4. Perform the six analyses
Execute each analysis module in order — they are interdependent (e.g., outages drive price spikes):

| # | Module | Key Question |
|---|--------|-------------|
| 1 | Price Spike Analysis | Were there extreme prices today? When and why? |
| 2 | Price Volatility | How wide was the intra-day price range? |
| 3 | Outage Assessment | What capacity was offline? Did it stress the grid? |
| 4 | Congestion Analysis | Which transmission constraints bound? Cost? |
| 5 | Wind & Solar Contribution | What share did renewables provide? Any curtailment? |
| 6 | Battery Storage Performance | How did BESS dispatch? Was it effective? |

### 5. Score overall grid health
Using the scoring rubric in the framework, assign:
- **GREEN** — Normal operations, ample reserves, stable prices
- **YELLOW** — Elevated stress, some constraints or volatility, manageable
- **RED** — Emergency conditions, scarcity pricing, reserve shortfalls

### 6. Produce the analysis report
Use the template in `references/analysis-template.md` to format the output.

### 7. Save the output
Save the report as `analyses/ERCOT-[YYYY-MM-DD].md`.

---

## Analysis Components

### 1. Price Spike Analysis
Identify Real-Time LMP spikes and their causes.

**Spike Thresholds (ERCOT Real-Time Settlement Point Prices)**:
- **Normal**: $0 – $100/MWh
- **Elevated**: $100 – $500/MWh
- **High Spike**: $500 – $2,000/MWh
- **Extreme Spike**: $2,000 – $5,000/MWh (ERCOT High System-Wide Offer Cap = $5,000/MWh)
- **Negative Price**: Below $0/MWh (excess renewable generation or must-run units)

**Key metrics**:
- Number of 15-min intervals above each threshold
- Peak price (time, hub/zone, magnitude)
- Duration of price spikes
- Day-ahead vs real-time spread (positive spread = real-time scarcer than forecast)
- Weighted average real-time price vs day-ahead price

**Root cause classification**:
- **Demand-driven**: Load spike (heat wave, cold snap) exhausted reserves
- **Supply-driven**: Large generator trip or outage during peak
- **Congestion-driven**: Transmission bottleneck isolated a load zone
- **Renewable intermittency**: Wind/solar drop during peak demand
- **Scarcity event**: Operating reserves fell below 2,300 MW (ERCOT triggers EEA)

Output: **NONE / MINOR / SIGNIFICANT / EXTREME** + cause narrative

### 2. Price Volatility Analysis
Assess intra-day and inter-hub price variability.

**Metrics**:
- **Intra-day spread**: Max price – Min price for the day (all hubs)
- **Standard deviation** of 15-min real-time prices (all hubs)
- **Coefficient of variation** (StdDev / Mean) — normalizes for price level
- **Negative price periods**: Number of hours with negative RT prices
- **Price reversal count**: Number of times price crossed $100/MWh threshold

**Volatility Classification**:
- **Low**: StdDev < $20/MWh, spread < $100/MWh
- **Moderate**: StdDev $20–$100/MWh, spread $100–$500/MWh
- **High**: StdDev $100–$500/MWh, spread $500–$2,000/MWh
- **Extreme**: StdDev > $500/MWh, spread > $2,000/MWh

**Hub comparison**: Report prices by hub — HB_NORTH, HB_SOUTH, HB_WEST, HB_HOUSTON — to identify geographic price separation.

Output: **LOW / MODERATE / HIGH / EXTREME** with metrics table

### 3. Outage Assessment
Evaluate forced and planned generator outages and their reserve margin impact.

**Key metrics**:
- **Total forced outages** (MW) — unplanned generator trips
- **Total planned outages** (MW) — scheduled maintenance
- **Available capacity** (MW) — nameplate minus all outages
- **Peak load** (MW) — maximum demand of the day
- **Operating reserve margin** = (Available Capacity – Peak Load) / Peak Load × 100%
- **Largest single forced outage** (unit name, MW, duration)

**Reserve adequacy thresholds**:
- **Adequate**: Reserve margin ≥ 13.75% (ERCOT planning reserve margin target)
- **Tight**: Reserve margin 10–13.75%
- **Critical**: Reserve margin 5–10%
- **Emergency**: Reserve margin < 5% (EEA Watch/Warning/Emergency)

**Emergency Event Alerts (EEA)**:
- EEA Level 1: Conservation voltage reduction or public appeal
- EEA Level 2: Firm load shedding possible
- EEA Level 3: Rotating outages (controlled blackouts)

Output: **ADEQUATE / TIGHT / CRITICAL / EMERGENCY** + largest outage event

### 4. Congestion Analysis
Identify active transmission constraints and their market cost.

**Key metrics**:
- **Active constraints**: Transmission lines/transformers with binding limits
- **Shadow price** ($/MWh): Value placed on relieving each constraint
- **Constraint duration** (hours): How long each constraint bound
- **Congestion cost** ($): Shadow price × flow × duration (total market cost)
- **Hub-to-hub spread**: Price difference between HB_NORTH and HB_SOUTH/WEST/HOUSTON
- **Load zone premiums**: Zone prices above or below hub prices

**Congestion Classification**:
- **None**: All zones within $5/MWh of hubs
- **Minor**: Zone-hub spread $5–$25/MWh, short duration
- **Moderate**: Zone-hub spread $25–$100/MWh, or multiple constraints active
- **Severe**: Zone-hub spread > $100/MWh, or persistent constraint binding for >4 hours

**Common congestion corridors**:
- West Texas to load centers (wind export constraints)
- Rio Grande Valley to Houston (south Texas renewables)
- Panhandle to Dallas-Fort Worth (north wind export)

Output: **NONE / MINOR / MODERATE / SEVERE** + top constraints table

### 5. Wind & Solar Contribution Analysis
Quantify renewable generation penetration and curtailment.

**Key metrics**:
- **Wind generation** (MWh): Total daily production, peak output, average output
- **Solar generation** (MWh): Total daily production, peak output (typically 12–2 PM CT)
- **Total renewable share** (%): (Wind + Solar) / Total Load × 100%
- **Peak renewable penetration** (%): Maximum 15-min interval renewable share
- **Wind capacity factor** (%): Actual generation / Nameplate capacity
- **Solar capacity factor** (%): Actual generation / Nameplate capacity
- **Curtailment** (MWh): Generation that was available but not used (negative prices as proxy)
- **Ramp events**: Large wind ramps (>1,000 MW/15 min) that stressed dispatchable resources

**Renewable adequacy levels**:
- **Low contribution**: Renewable share < 30% of daily load
- **Moderate contribution**: 30–50%
- **High contribution**: 50–70%
- **Record-level**: > 70% (ERCOT has hit ~85% instantaneous renewable penetration)

**Installed capacity context** (approximate, as of 2025–2026):
- Wind: ~40,000 MW nameplate
- Solar: ~25,000 MW nameplate
- Battery Storage: ~5,000 MW / ~20,000 MWh

Output: Wind: **X,XXX MW avg / XX% share**, Solar: **X,XXX MW avg / XX% share**, Curtailment: **X,XXX MWh**

### 6. Battery Storage Performance Analysis
Assess how Battery Energy Storage Systems (BESS) dispatched and their grid contribution.

**Key metrics**:
- **Total BESS capacity** (MW): Online vs total installed
- **Peak discharge** (MW): Maximum output during day
- **Peak charge** (MW): Maximum absorption during day
- **Net energy discharged** (MWh): Total discharge minus total charge
- **Charge timing**: Did BESS charge during low/negative price hours? (efficiency measure)
- **Discharge timing**: Did BESS discharge during peak price hours? (value capture)
- **Ancillary services**: Share of BESS providing RegUp, RegDown, RRS (Responsive Reserve)
- **Round-trip efficiency proxy**: Compare avg charge price to avg discharge price

**BESS performance scoring**:
- **Excellent**: Charged during negative/low prices (<$20/MWh), discharged during spikes (>$100/MWh), provided ancillary services
- **Good**: Charged during off-peak, discharged near peak, some ancillary participation
- **Fair**: Charged and discharged at similar prices, limited ancillary contribution
- **Poor**: Charged during high prices or discharged during low prices (suboptimal dispatch)

**Grid contribution classification**:
- **Critical**: BESS prevented scarcity event or curtailed spike duration
- **Supportive**: BESS reduced peak prices or smoothed renewable intermittency
- **Marginal**: BESS dispatched but limited grid impact
- **Idle**: BESS largely offline or not dispatching

Output: **Excellent/Good/Fair/Poor** performance + **Critical/Supportive/Marginal/Idle** grid contribution

---

## Overall Grid Health Score

Score each dimension 1–5, then sum for total:

| Dimension | 5 (Best) | 3 (Neutral) | 1 (Worst) |
|-----------|----------|-------------|-----------|
| Price Stability | No spikes, normal prices | Moderate volatility | Extreme spikes |
| Reserve Adequacy | >15% margin | 10–13% margin | <5% margin / EEA |
| Congestion | No constraints | Minor constraints | Severe congestion |
| Renewable Integration | High share, no curtailment | Moderate share | Low share or high curtailment |
| Storage Effectiveness | Excellent BESS dispatch | Fair BESS dispatch | Idle/poor BESS |

**Total Score Interpretation**:
- **21–25**: GREEN — Excellent grid conditions
- **15–20**: GREEN — Normal operations
- **10–14**: YELLOW — Elevated stress
- **5–9**: RED — Significant stress or emergency conditions
