# ERCOT Data Sources Reference

## Primary Data Sources

### 1. ERCOT Public API (Preferred — Machine Readable)
**URL**: `https://api.ercot.com/api/public-reports/`
**Authentication**: None required for public reports
**Format**: JSON
**Documentation**: https://www.ercot.com/mktinfo/data_acess

Key public report endpoints:
| Report | Description | Endpoint Suffix |
|--------|-------------|----------------|
| Real-Time Settlement Point Prices | 15-min RT prices by hub/zone | `NP6-785-CD` |
| Day-Ahead Market Settlement Point Prices | Hourly DA prices | `NP6-905-CD` |
| Real-Time System Conditions | Load, capacity, reserves | `NP3-911-ER` |
| Hourly Resource Outage Capacity | Forced + planned outages by fuel | `NP4-732-CD` |
| Generation Mix by Fuel | Hourly generation by fuel type | `NP4-160-CD` |
| Shadow Prices of Binding Constraints | Real-time congestion prices | `NP6-86-CD` |
| Battery Storage Dispatch | BESS charge/discharge activity | `NP4-188-CD` |
| Wind Power Production | Actual wind generation | `NP4-742-CD` |
| Solar Power Production | Actual solar generation | `NP4-745-CD` |

**Example API call**:
```
GET https://api.ercot.com/api/public-reports/NP6-785-CD?deliveredDateFrom=2026-06-04&deliveredDateTo=2026-06-04
```

---

### 2. GridStatus Python Library (Easiest for Python Scripts)
**Install**: `pip install gridstatus`
**GitHub**: https://github.com/gridstatus/gridstatus
**Coverage**: ERCOT, CAISO, MISO, PJM, NYISO, ISONE, SPP

```python
import gridstatus

iso = gridstatus.Ercot()

# Real-time prices
prices = iso.get_lmp(date="today", market="REAL_TIME_15_MIN")

# Fuel mix
fuel_mix = iso.get_fuel_mix(date="today")

# Load
load = iso.get_load(date="today")

# Outages (if supported)
# Note: Use ERCOT API directly for detailed outage data
```

**Supported markets for ERCOT**:
- `REAL_TIME_15_MIN` — 15-min settlement point prices
- `DAY_AHEAD_HOURLY` — Day-ahead hourly prices
- `REAL_TIME_HOURLY` — Hourly average RT prices

---

### 3. ERCOT Market Information System (MIS) — Web Portal
**URL**: https://www.ercot.com/misapp/
**Authentication**: Free registration required for some reports
**Format**: CSV/Excel downloads

Useful MIS reports:
- **60DAY_NALN** — Generator outage reports (next 60 days)
- **Hourly RTM SPPs** — Real-time settlement point prices
- **Fuel Mix Report** — Generation by fuel type
- **System Lambda** — Real-time marginal cost

---

### 4. EIA (Energy Information Administration)
**URL**: https://api.eia.gov/
**API Key**: Required (free registration at https://www.eia.gov/opendata/)
**Use case**: Fuel prices (natural gas, coal), capacity additions, historical generation data

Key series:
- `EBA.TEX-ALL.D.H` — ERCOT net generation (hourly)
- `NG.RNGWHHD.D` — Henry Hub natural gas spot price
- `EBA.TEX-ALL.NG.H` — ERCOT net generation by fuel type

---

### 5. GreenFacts / GridStatus.io (Web Dashboard)
**URL**: https://gridstatus.io/live?iso=ERCOT
**Use case**: Quick visual verification of grid conditions
**No API** — Web scraping only (use for manual verification)

---

## Data Availability by Analysis Module

| Analysis Module | Primary Source | Backup Source | Lag |
|----------------|---------------|--------------|-----|
| Price Spikes | ERCOT API (`NP6-785-CD`) | GridStatus | ~15 min |
| Price Volatility | ERCOT API (`NP6-785-CD`) | GridStatus | ~15 min |
| Outages | ERCOT API (`NP4-732-CD`) | ERCOT MIS | ~1 hour |
| Congestion | ERCOT API (`NP6-86-CD`) | ERCOT MIS | ~30 min |
| Wind Generation | ERCOT API (`NP4-742-CD`) | GridStatus fuel mix | ~5 min |
| Solar Generation | ERCOT API (`NP4-745-CD`) | GridStatus fuel mix | ~5 min |
| Battery Storage | ERCOT API (`NP4-188-CD`) | GridStatus fuel mix | ~15 min |
| System Load | ERCOT API (`NP3-911-ER`) | GridStatus | ~5 min |

---

## ERCOT Hub and Zone Reference

### Settlement Point Hubs (HB_)
| Hub | Region | Description |
|-----|--------|-------------|
| HB_NORTH | North Texas | Dallas-Fort Worth area load center |
| HB_SOUTH | South Texas | Austin-San Antonio corridor |
| HB_WEST | West Texas | Permian Basin / wind generation area |
| HB_HOUSTON | Houston area | Gulf Coast industrial/petrochemical load |
| HB_HUBAVG | System average | Weighted average of all 4 hubs |

### Load Zones (LZ_)
| Zone | Utility | Notes |
|------|---------|-------|
| LZ_NORTH | Oncor | Largest load zone by volume |
| LZ_SOUTH | AEP Texas | South Texas load |
| LZ_WEST | AEP Texas | West Texas — often diverges from North hub |
| LZ_HOUSTON | CenterPoint | Houston metro area |

### Price Relationships
- `LZ_WEST – HB_WEST`: Often negative (generation surplus in West Texas wind zones)
- `LZ_HOUSTON – HB_HOUSTON`: Usually positive (load zone premium during high demand)
- `HB_NORTH – HB_WEST`: Key congestion indicator for west-to-east transmission

---

## API Rate Limits and Caching

- **ERCOT Public API**: No stated rate limit, but avoid more than 1 request/second
- **GridStatus**: No rate limit for public endpoints, be respectful
- **EIA**: 5,000 requests/day per API key

**Caching recommendation**: Store downloaded data in `data/YYYY-MM-DD/` directories to avoid repeated API calls for the same date. The fetch script handles this automatically.

---

## Useful Reference Links

- ERCOT Market Rules: https://www.ercot.com/mktrules
- ERCOT Grid Conditions (live): https://www.ercot.com/gridinfo
- ERCOT Emergency Alerts: https://www.ercot.com/news/alerts
- ERCOT Annual Report: https://www.ercot.com/about/investors
- Texas PUC (regulator): https://www.puc.texas.gov/
- NERC Standards (reliability): https://www.nerc.com/
