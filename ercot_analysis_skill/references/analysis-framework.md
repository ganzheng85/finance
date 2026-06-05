# ERCOT Market Analysis Framework

## Price Spike Thresholds

ERCOT operates under a nodal market with a High System-Wide Offer Cap (HCAP) of **$5,000/MWh** and a Low Systemwide Offer Cap (LCAP) of **-$500/MWh**.

### Spike Classification
| Level | Price Range | Significance |
|-------|------------|-------------|
| Normal | $0 – $100/MWh | Competitive dispatch, ample supply |
| Elevated | $100 – $500/MWh | Tighter supply, approaching scarcity |
| High Spike | $500 – $2,000/MWh | Scarcity or significant constraint |
| Extreme Spike | $2,000 – $5,000/MWh | Near-emergency, ORDC adder active |
| HCAP | $5,000/MWh | Binding cap, scarcity pricing in effect |
| Negative | Below $0/MWh | Excess supply (wind/nuclear must-run) |
| Deep Negative | Below -$100/MWh | Severe oversupply, high curtailment pressure |

### Operating Reserve Demand Curve (ORDC)
ERCOT adds an adder to real-time prices when operating reserves are scarce:
- Reserves > 3,000 MW: Adder ≈ $0/MWh
- Reserves 2,000–3,000 MW: Adder scales up
- Reserves < 2,000 MW: Adder = $5,000/MWh × VOLL ratio (max adder = $5,000/MWh)

A high ORDC adder is an early warning of grid stress before any EEA is declared.

---

## Outage Severity Framework

### Reserve Margin Calculation
```
Reserve Margin = (Available Capacity − Peak Load) / Peak Load × 100%
Available Capacity = Installed Capacity − Forced Outages − Planned Outages
```

### ERCOT Emergency Event Alerts (EEA)
| Alert Level | Trigger | Action |
|------------|---------|--------|
| EEA Watch | Reserves projected to drop below 2,300 MW | Issue public conservation appeal |
| EEA Warning | Reserves at or below 2,300 MW | Activate non-spinning reserves |
| EEA Level 1 | Reserves at or below 1,750 MW | Conservation voltage reduction (CVR) |
| EEA Level 2 | Reserves at or below 1,000 MW | Interruptible load curtailment |
| EEA Level 3 | Reserves critically low | Rotating outages (controlled blackouts) |

### Outage Classification by Cause
- **Forced (Unplanned)**: Mechanical failure, fuel supply interruption, weather-related trip
- **Planned (Scheduled)**: Routine maintenance, regulatory inspection
- **Weather-Forced**: Extreme temperature causing equipment failure (e.g., Winter Storm Uri 2021)
- **Fuel Shortage**: Gas supply curtailment, coal stockpile depletion

---

## Congestion Analysis Framework

### Price Separation Metrics
Congestion manifests as price differences between hubs and zones:
- **Hub prices**: HB_NORTH, HB_SOUTH, HB_WEST, HB_HOUSTON (4 main hubs)
- **Load zone prices**: LZ_NORTH, LZ_SOUTH, LZ_WEST, LZ_HOUSTON
- **Resource node prices**: Individual generator nodes (used in congestion revenue rights)

### Shadow Price Interpretation
Shadow price = incremental cost of relaxing a transmission constraint by 1 MW.
- A shadow price of $100/MWh means relieving that constraint by 1 MW would save $100/MWh for all load behind it.
- High shadow prices (>$50/MWh) indicate economically significant congestion.

### Common ERCOT Transmission Bottlenecks
| Corridor | Direction | Typical Constraint Period |
|----------|-----------|--------------------------|
| Permian Basin Export | West → Central | High wind days, low load |
| Panhandle Export | North → South | High wind days |
| South Texas Export | South → North | High solar days |
| Houston Import | Multiple → Houston | High heat demand events |
| Oncor Constraints | Dallas-area | Peak summer demand |

---

## Renewable Integration Framework

### Renewable Penetration Levels
```
Renewable Share (%) = (Wind Generation + Solar Generation) / Total System Load × 100%
```

| Level | Instantaneous Penetration | Daily Energy Share |
|-------|--------------------------|-------------------|
| Low | < 30% | < 25% |
| Moderate | 30–60% | 25–45% |
| High | 60–80% | 45–65% |
| Record Territory | > 80% | > 65% |

### Curtailment Identification
**Economic curtailment** occurs when:
- Real-time prices go negative (generators not paid to produce)
- Renewable generators self-curtail to avoid negative price exposure
- ERCOT dispatches baseload below minimum generation

**Proxy for curtailment**:
- Duration of negative price periods × estimated generation at negative price hours
- ERCOT curtailment reports (when published)

### Renewable Ramp Events
Large, rapid changes in wind or solar output that stress dispatchable resources:
- **Significant ramp**: >1,000 MW change in 15 minutes
- **Major ramp**: >2,000 MW change in 15 minutes
- **Critical ramp**: >3,000 MW change in 15 minutes (rare, high stress)

Solar creates predictable morning ramp-up and evening ramp-down ("duck curve").
Wind creates less predictable ramps, especially during weather front passages.

---

## Battery Storage Performance Framework

### Ideal Dispatch Pattern
A well-optimized BESS maximizes the price spread between charge and discharge:
1. **Charge**: During overnight low-demand hours (12 AM – 6 AM) or midday solar surplus (10 AM – 2 PM) when prices are low or negative
2. **Discharge**: During morning peak (7–9 AM), evening peak (6–9 PM), or during price spikes
3. **Ancillary services**: Provide RegUp/RegDown when not fully committed to energy arbitrage

### BESS Metrics Definitions
| Metric | Formula | Good Value |
|--------|---------|-----------|
| Arbitrage Spread | Avg Discharge Price − Avg Charge Price | > $30/MWh |
| Capacity Utilization | Net Discharge / Installed Capacity × 100% | > 50% on peak days |
| Ancillary Share | MW providing ancillary / Total MW | > 20% |
| Round-Trip Efficiency | Energy Out / Energy In | ~85–92% (physical) |

### BESS Grid Role Classification
| Role | Description |
|------|-------------|
| Peak Shaving | Discharges during demand peaks to reduce scarcity |
| Frequency Regulation | Rapid response (seconds) to frequency deviations |
| Renewable Smoothing | Absorbs excess renewable output, releases during lulls |
| Arbitrage | Pure price spread capture, no specific grid service |
| Emergency Reserve | Holds charge as operating reserve, dispatches only in scarcity |

---

## Seasonal Context for ERCOT

### High-Risk Periods
| Season | Primary Risk | Secondary Risk |
|--------|-------------|---------------|
| Summer Peak (Jun–Sep) | Demand spikes (heat waves) | Wind lulls during high heat |
| Winter Peak (Dec–Feb) | Cold snap demand surge + generator freeze | Wind/solar underperformance |
| Spring (Mar–May) | Negative prices (high wind/solar, low load) | Congestion from renewables |
| Fall (Oct–Nov) | Low risk, mild temperatures | Maintenance outage season |

### ERCOT-Specific Context
- **No interconnection**: ERCOT is an electrical island (limited AC ties to neighboring grids)
- **Price responsive load**: Large industrial and demand response resources can reduce demand during scarcity
- **Nodal market**: Prices differ at every generator bus and load zone
- **No capacity market**: ERCOT relies on energy-only market with ORDC to incent investment
