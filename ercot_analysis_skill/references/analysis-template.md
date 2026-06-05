# ERCOT Market Analysis Template

Use this template for every daily ERCOT market analysis report.

---

# ERCOT Market Analysis — [YYYY-MM-DD]

**Analysis Date**: [YYYY-MM-DD] | **Prepared**: [Timestamp CT] | **Grid Health**: 🟢 GREEN / 🟡 YELLOW / 🔴 RED

---

## Executive Summary

[2–4 sentences capturing the day's most important story. Cover:]
- Overall grid health verdict and why
- Most notable event (biggest spike, major outage, renewable record, etc.)
- Renewable performance highlight
- Battery storage headline

**Example**: "ERCOT experienced YELLOW grid conditions on [date] as a heat dome drove afternoon load to 78,000 MW with a 12% reserve margin. Real-time prices spiked to $2,400/MWh at HB_NORTH for 45 minutes at 4:30 PM CT due to a 900 MW forced outage at a gas unit coinciding with peak demand. Wind contributed 28% of daily energy while battery storage discharged 4,200 MW during the spike, reducing its duration."

---

## 1. Price Spike Analysis — [NONE / MINOR / SIGNIFICANT / EXTREME]

### Daily Price Summary
| Hub | DA Avg ($/MWh) | RT Avg ($/MWh) | DA-RT Spread | RT Peak | RT Peak Time | Negative Hours |
|-----|---------------|----------------|-------------|---------|-------------|----------------|
| HB_NORTH | | | | | | |
| HB_SOUTH | | | | | | |
| HB_WEST | | | | | | |
| HB_HOUSTON | | | | | | |

### Price Spike Events
| Time (CT) | Hub/Zone | Price ($/MWh) | Duration | Cause |
|-----------|---------|--------------|----------|-------|
| | | | | |

### Negative Price Events
| Time Window (CT) | Hub/Zone | Avg Price ($/MWh) | Duration | Driver |
|-----------------|---------|------------------|----------|--------|
| | | | | |

### Price Spike Narrative
[Explain the day's price dynamics. Why were prices where they were? What drove spikes or negative prices?]

---

## 2. Price Volatility — [LOW / MODERATE / HIGH / EXTREME]

### Volatility Metrics
| Hub | Min Price ($/MWh) | Max Price ($/MWh) | Intra-Day Spread | Std Dev | CV (%) |
|-----|------------------|------------------|-----------------|---------|--------|
| HB_NORTH | | | | | |
| HB_SOUTH | | | | | |
| HB_WEST | | | | | |
| HB_HOUSTON | | | | | |

### Hub Divergence (Price Separation)
- **HB_NORTH – HB_WEST spread**: [$/MWh avg] — [interpretation]
- **HB_HOUSTON – HB_NORTH spread**: [$/MWh avg] — [interpretation]
- **Maximum hub divergence**: [$/MWh] at [time] between [Hub A] and [Hub B]

### Volatility Narrative
[Was volatility driven by demand uncertainty, renewable intermittency, outages, or congestion? What was the most volatile period?]

---

## 3. Outage Assessment — [ADEQUATE / TIGHT / CRITICAL / EMERGENCY]

### Capacity & Reserve Summary
| Metric | Value |
|--------|-------|
| Installed Capacity | MW |
| Forced Outages | MW |
| Planned Outages | MW |
| Available Capacity | MW |
| Peak Load | MW (time: ) |
| Operating Reserve Margin | % |
| Minimum Reserve | MW (time: ) |
| EEA Issued? | Yes / No |

### Major Outage Events
| Unit / Plant | Fuel Type | Capacity (MW) | Outage Type | Duration | Impact |
|-------------|----------|--------------|------------|---------|--------|
| | | | | | |

### Outage Narrative
[Were outages expected (planned) or did any forced trips occur at a critical time? Did any outage drive price spikes or reduce the reserve margin below comfortable levels?]

---

## 4. Congestion Analysis — [NONE / MINOR / MODERATE / SEVERE]

### Active Transmission Constraints
| Constraint Name | Shadow Price ($/MWh) | Duration (hrs) | Est. Congestion Cost ($) | Direction |
|----------------|---------------------|----------------|------------------------|-----------|
| | | | | |

### Hub-Zone Price Spreads
| Zone | Hub | Avg Spread ($/MWh) | Max Spread ($/MWh) | Congestion Direction |
|------|-----|------------------|------------------|---------------------|
| LZ_WEST | HB_WEST | | | |
| LZ_NORTH | HB_NORTH | | | |
| LZ_HOUSTON | HB_HOUSTON | | | |
| LZ_SOUTH | HB_SOUTH | | | |

### Congestion Narrative
[Which corridors were constrained? West Texas export bottleneck? Houston import limitation? What drove the constraint — high renewable output, high demand, or maintenance outage on a key line?]

---

## 5. Wind & Solar Contribution — [LOW / MODERATE / HIGH / RECORD]

### Renewable Generation Summary
| Source | Peak Output (MW) | Peak Time | Daily Energy (MWh) | Daily Share (%) | Capacity Factor (%) |
|--------|-----------------|----------|--------------------|----------------|---------------------|
| Wind | | | | | |
| Solar | | | | | |
| **Combined** | | | | | |

### Renewable Context
- **Installed Wind Capacity**: ~40,000 MW
- **Installed Solar Capacity**: ~25,000 MW
- **Today's Wind CF**: [X]% (vs typical ~30–35% for ERCOT)
- **Today's Solar CF**: [X]% (vs typical ~18–22% for ERCOT)
- **Peak Renewable Penetration**: [X]% at [time]

### Curtailment Estimate
| Period | Estimated Curtailment (MWh) | Negative Price Trigger | Notes |
|--------|---------------------------|----------------------|-------|
| | | | |

### Key Ramp Events
| Time (CT) | Direction | Magnitude (MW) | Rate (MW/15min) | Stress Impact |
|-----------|-----------|---------------|----------------|--------------|
| | | | | |

### Renewable Narrative
[Did wind blow strongly or weakly? Was solar at expected levels? Were there significant ramps? Did excess renewables cause negative prices or curtailment? How did renewables compare to system needs?]

---

## 6. Battery Storage Performance — [EXCELLENT / GOOD / FAIR / POOR]

### BESS Dispatch Summary
| Metric | Value |
|--------|-------|
| Total BESS Capacity Online | MW |
| Peak Discharge | MW (time: ) |
| Peak Charge | MW (time: ) |
| Total Energy Discharged | MWh |
| Total Energy Charged | MWh |
| Net Energy Discharged | MWh |
| Avg Charge Price | $/MWh |
| Avg Discharge Price | $/MWh |
| Arbitrage Spread | $/MWh |

### BESS Dispatch Timeline
| Period | Mode | MW | Avg Price ($/MWh) | Rationale |
|--------|------|----|--------------------|-----------|
| | Charging | | | |
| | Discharging | | | |
| | Standby | | | |

### Ancillary Services Contribution
| Service | BESS MW | % of Total Requirement | Notes |
|---------|---------|----------------------|-------|
| RegUp | | | |
| RegDown | | | |
| RRS (Responsive Reserve) | | | |

### Storage Narrative
[Did BESS charge during cheap/negative hours? Did it discharge during price spikes? Did it provide ancillary services? Was its grid contribution critical, supportive, or marginal? Compare to an ideal dispatch day.]

---

## 7. Overall Grid Health Assessment

### Scorecard
| Dimension | Score (1–5) | Assessment | Key Evidence |
|-----------|------------|------------|-------------|
| Price Stability | | | |
| Reserve Adequacy | | | |
| Congestion | | | |
| Renewable Integration | | | |
| Storage Effectiveness | | | |
| **TOTAL** | **/25** | | |

### Grid Health: 🟢 GREEN / 🟡 YELLOW / 🔴 RED

### Key Findings
1. [Most important finding]
2. [Second most important finding]
3. [Third most important finding]

### Risks & Watch Items for Tomorrow
- [Any scheduled maintenance outages that could reduce capacity]
- [Weather forecast — will it drive higher/lower load?]
- [Any transmission work that could increase congestion?]
- [Renewable generation outlook — wind and solar forecast]

---

*Data sources: ERCOT Public API, GridStatus.io | Analysis timezone: Central Time (CT)*
