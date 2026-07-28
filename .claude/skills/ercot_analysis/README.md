# ERCOT Market Analysis Skill

A VS Code Copilot skill for daily ERCOT electricity market analysis covering price dynamics, grid reliability, renewable generation, and battery storage performance.

## What This Skill Analyzes

| Module | Key Question |
|--------|-------------|
| **Price Spikes** | Were there extreme prices today? When and why? |
| **Price Volatility** | How wide was the intra-day price range? |
| **Outage Assessment** | What capacity was offline? Did it stress the grid? |
| **Congestion Analysis** | Which transmission constraints bound? Cost? |
| **Wind & Solar Contribution** | What share did renewables provide? Any curtailment? |
| **Battery Storage Performance** | How did BESS dispatch? Was it effective? |

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Fetch today's ERCOT data
```bash
python scripts/fetch_ercot_data.py --date today
```

### 3. Invoke the skill in Copilot chat
In VS Code Copilot Chat, type `/ercot-analysis` or describe what you want:
> "Analyze ERCOT grid conditions for today — focus on price spikes and battery storage"

## Data Sources

- **ERCOT Public API** (`https://api.ercot.com`) — primary source, no auth required
- **GridStatus Python library** — fallback for prices and fuel mix
- **ERCOT MIS portal** — manual downloads when API is unavailable

See [references/data-sources.md](references/data-sources.md) for full details and endpoint reference.

## Directory Structure

```
ercot_analysis_skill/
├── SKILL.md                         # Skill definition (loaded by Copilot)
├── README.md                        # This file
├── requirements.txt                 # Python dependencies
├── analyses/                        # Saved daily analysis reports (ERCOT-YYYY-MM-DD.md)
├── data/                            # Raw fetched data (auto-created by script)
├── references/
│   ├── analysis-framework.md        # Thresholds, scoring rubrics, context
│   ├── data-sources.md              # API endpoints and data availability
│   └── analysis-template.md        # Output report template
└── scripts/
    └── fetch_ercot_data.py          # Data fetcher and analysis engine
```

## Script Usage

```
python scripts/fetch_ercot_data.py [OPTIONS]

Options:
  --date DATE        Date to fetch (YYYY-MM-DD or 'today'). Default: today CT
  --output DIR       Output directory. Default: data/
  --format FORMAT    Output format: json or csv. Default: json
  --no-gridstatus    Disable GridStatus fallback
  --no-save          Print summary only, skip saving files
```

**Examples**:
```bash
# Today's data
python scripts/fetch_ercot_data.py

# Specific past date
python scripts/fetch_ercot_data.py --date 2026-06-01

# Quick console summary, no file output
python scripts/fetch_ercot_data.py --date today --no-save
```

## ERCOT Market Background

ERCOT (Electric Reliability Council of Texas) operates the electric grid for ~90% of Texas. It is an **energy-only market** — no capacity market — relying on scarcity pricing and the Operating Reserve Demand Curve (ORDC) to signal investment needs.

Key characteristics:
- **Electrically isolated**: Limited AC interconnection to neighboring grids (limited ability to import/export)
- **Nodal pricing**: Prices differ at every generator bus and load zone
- **Price cap**: $5,000/MWh High System-Wide Offer Cap (HCAP)
- **Price floor**: -$500/MWh Low System-Wide Offer Cap (LCAP)
- **~40 GW wind**: Largest wind market in the US
- **~25 GW solar**: Rapidly growing, especially West Texas and South Texas
- **~5 GW battery storage**: Growing fast post-Winter Storm Uri (2021)

## License

For personal use within this workspace.
