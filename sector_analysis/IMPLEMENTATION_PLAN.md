# Sector Analysis - Implementation Plan

## Overview

Add sector-level analysis to the web app using a tabbed interface:
- **Tab 1:** Company Analysis (existing)
- **Tab 2:** Sector Analysis (new)

---

## Phase 1: Data Pipeline

### 1.1 Sector ETF Data Fetcher

**File:** `sector_analysis/scripts/fetch_sector_data.py`

**Functionality:**
```python
def fetch_sector_etfs(lookback_days=365):
    """
    Fetch daily price/volume data for all 13 sector ETFs + SPY
    
    Returns:
        DataFrame with columns:
        - date
        - ticker (XLK, XLV, XLF, ...)
        - open, high, low, close, adjusted_close
        - volume
    """
    
    sector_tickers = [
        'XLK',   # Technology
        'XLV',   # Healthcare
        'XLF',   # Financials
        'XLY',   # Consumer Discretionary
        'XLI',   # Industrials
        'XLP',   # Consumer Staples
        'XLE',   # Energy
        'XLU',   # Utilities
        'XLB',   # Materials
        'XLRE',  # Real Estate
        'XLC',   # Communication Services
        'SPY'    # Benchmark
    ]
```

### 1.2 Constituent Stock Data

**File:** `sector_analysis/scripts/fetch_sector_constituents.py`

**Purpose:** For breadth calculations
- Fetch top 10-20 stocks per sector
- Calculate % above 50-day MA
- Track new highs/lows

---

## Phase 2: Calculation Engine

### 2.1 Relative Strength Calculator

**File:** `sector_analysis/lib/relative_strength.py`

```python
def calculate_relative_strength(sector_df, benchmark='SPY'):
    """
    Calculate RS = Sector / SPY
    
    Returns:
        - 20-day RS return
        - 60-day RS return
        - RS percentile rank
    """

def categorize_rs_signal(rs_20d, rs_60d):
    """
    Returns: 'STRONG', 'EARLY_ROTATION', 'LATE_CYCLE', 'WEAK'
    """
```

### 2.2 Momentum Ranker

**File:** `sector_analysis/lib/momentum_ranker.py`

```python
def calculate_momentum(sector_df):
    """
    Calculate:
    - 3-month return
    - 6-month return
    - 12-1 momentum
    
    Returns ranked DataFrame
    """

def rank_sectors_by_momentum(sector_df):
    """
    Rank 1-11 by composite momentum score
    """
```

### 2.3 Flow Analyzer

**File:** `sector_analysis/lib/flow_analyzer.py`

```python
def calculate_etf_flows(ticker, lookback_days=30):
    """
    Calculate net flows = Δ(shares_outstanding) × NAV
    
    Note: Shares outstanding updated quarterly
    Approximation: Use volume × price as proxy
    """

def classify_flow_signal(flow, momentum_rank):
    """
    Returns: 'STRONG_BUY', 'CAUTION', 'WATCH', 'AVOID'
    """
```

### 2.4 Breadth Calculator

**File:** `sector_analysis/lib/breadth_calculator.py`

```python
def calculate_breadth_metrics(constituent_stocks):
    """
    Calculate:
    - % stocks above 50-day MA
    - Advance/Decline line
    - New highs - New lows
    
    Returns breadth score (0-100)
    """
```

### 2.5 Composite Scorer

**File:** `sector_analysis/lib/sector_scorer.py`

```python
def calculate_composite_score(sector_metrics):
    """
    Weighted score:
    - 25% RS rank
    - 25% Momentum rank
    - 20% Flow z-score
    - 15% Breadth score
    - 15% Volume score
    
    Returns: Score 0-100
    """

def generate_rotation_quadrant(sector_df):
    """
    Classify sectors into:
    - Leading, Weakening, Lagging, Improving
    
    Returns quadrant assignments
    """
```

---

## Phase 3: Report Generation

### 3.1 Markdown Report Generator

**File:** `sector_analysis/scripts/generate_sector_report.py`

**Report Structure:**
```markdown
# Sector Rotation Analysis
**Date:** 2026-06-21
**Benchmark:** SPY

## Executive Summary
- Top 3 Sectors: [XLK, XLV, XLF]
- Bottom 3 Sectors: [XLE, XLU, XLRE]
- Rotation Status: [EARLY_CYCLE / MID_CYCLE / LATE_CYCLE]

## Sector Rankings

| Rank | Sector | Score | RS (20d) | Momentum | Flow | Breadth | Signal |
|------|--------|-------|----------|----------|------|---------|--------|
| 1    | XLK    | 92.3  | +8.2%    | +15.8%   | +2.3B| 82%     | 🚀 BUY |
| 2    | XLV    | 85.7  | +5.1%    | +12.4%   | +1.1B| 75%     | ✅ BUY |
| ...  | ...    | ...   | ...      | ...      | ...  | ...     | ...    |

## Rotation Map

[ASCII visualization or data for chart]

## Detailed Sector Analysis

### Technology (XLK) - 🚀 STRONG BUY
- **Score:** 92.3 (Rank #1)
- **Relative Strength:** +8.2% (20d), +12.5% (60d)
  - Signal: STRONG (outperforming on both timeframes)
- **Momentum:** +15.8% (3M+6M composite)
- **ETF Flows:** +$2.3B (30-day)
- **Breadth:** 82% above 50-day MA
- **Quadrant:** LEADING

**Recommendation:** OVERWEIGHT

[Repeat for each sector]

## Portfolio Recommendation

**Suggested Allocation (Top 5):**
- Technology (XLK): 25%
- Healthcare (XLV): 25%
- Financials (XLF): 20%
- Industrials (XLI): 15%
- Consumer Discretionary (XLY): 15%

**Avoid (Bottom 3):**
- Energy (XLE)
- Utilities (XLU)
- Real Estate (XLRE)
```

### 3.2 Visualization Generator

**File:** `sector_analysis/scripts/plot_sector_rotation.py`

**Charts to Generate:**

1. **Rotation Quadrant Map** (scatter plot)
   - X-axis: Relative Strength
   - Y-axis: RS Momentum
   - Each sector as labeled point

2. **Momentum Ranking Bar Chart**
   - All sectors sorted by momentum
   - Color-coded (green/red)

3. **Flow Analysis Chart**
   - Dual axis: Price vs Flow
   - Show flow divergences

4. **Breadth Heatmap**
   - Show % above MA for each sector over time

---

## Phase 4: Web App Integration

### 4.1 Update Flask Routes

**File:** `stock_analysis_app/app.py`

```python
# Add new route
@app.route('/sector_analysis')
def sector_analysis():
    """Render sector analysis page with tabs"""
    return render_template('sector_analysis.html')

# Add API endpoint
@app.route('/api/sector/generate', methods=['POST'])
def generate_sector_report():
    """
    Generate sector rotation report
    Returns JSON with report path and metrics
    """
    # Call sector analysis script
    # Return report data
```

### 4.2 Add API Handler

**File:** `stock_analysis_app/api/sector.py`

```python
def generate_sector_analysis():
    """
    1. Fetch all sector ETF data
    2. Calculate RS, momentum, flows, breadth
    3. Generate composite scores
    4. Create rotation map
    5. Generate markdown report
    6. Generate charts
    7. Convert to HTML
    8. Return report data
    """
```

### 4.3 Update Frontend Template

**File:** `stock_analysis_app/templates/index.html`

Add tabbed interface:
```html
<div class="tabs">
    <button class="tab-button active" onclick="showTab('company')">
        Company Analysis
    </button>
    <button class="tab-button" onclick="showTab('sector')">
        Sector Rotation
    </button>
</div>

<div id="company-tab" class="tab-content active">
    <!-- Existing company analysis UI -->
</div>

<div id="sector-tab" class="tab-content" style="display:none;">
    <h2>Sector Rotation Analysis</h2>
    
    <button id="generate-sector-btn">Generate Sector Analysis</button>
    
    <div id="sector-results">
        <!-- Sector rankings table -->
        <!-- Rotation quadrant map -->
        <!-- Flow charts -->
        <!-- Recommendations -->
    </div>
</div>

<script>
function showTab(tabName) {
    // Toggle tab visibility
}

document.getElementById('generate-sector-btn').addEventListener('click', () => {
    // Call /api/sector/generate
    // Display results
});
</script>
```

### 4.4 Create Sector Analysis Template

**File:** `stock_analysis_app/templates/sector_analysis.html`

Dedicated page with:
- Sector rankings table
- Rotation map visualization
- Flow analysis charts
- Breadth metrics
- Portfolio recommendations

---

## Phase 5: Testing & Validation

### 5.1 Unit Tests

**File:** `sector_analysis/tests/test_calculations.py`

Test:
- RS calculations
- Momentum ranking
- Flow calculations
- Breadth metrics
- Composite scoring

### 5.2 Integration Tests

**File:** `sector_analysis/tests/test_report_generation.py`

Test:
- End-to-end report generation
- Chart creation
- HTML conversion

### 5.3 Backtesting

**File:** `sector_analysis/backtests/test_rotation_strategy.py`

Backtest:
- Top 3 sector strategy
- Monthly rebalancing
- Compare vs SPY benchmark

---

## Phase 6: Deployment

### 6.1 Data Update Schedule

**Cron job or scheduler:**
```bash
# Daily at 4:30 PM ET (after market close)
30 16 * * 1-5 python sector_analysis/scripts/update_sector_data.py

# Weekly on Sunday (prepare for Monday rebalance)
0 10 * * 0 python sector_analysis/scripts/calculate_sector_rankings.py
```

### 6.2 Report Storage

**Directory structure:**
```
sector_analysis/
├── analyses/
│   ├── Sector_Rotation_20260621.md
│   ├── Sector_Rotation_20260621.html
│   └── charts/
│       ├── rotation_map_20260621.png
│       ├── momentum_ranking_20260621.png
│       └── flow_analysis_20260621.png
```

---

## Implementation Checklist

### Week 1: Data & Calculations
- [ ] Create sector_analysis directory structure
- [ ] Implement fetch_sector_data.py
- [ ] Implement relative_strength.py
- [ ] Implement momentum_ranker.py
- [ ] Test calculations with historical data

### Week 2: Scoring & Visualization
- [ ] Implement flow_analyzer.py
- [ ] Implement breadth_calculator.py
- [ ] Implement sector_scorer.py
- [ ] Create rotation quadrant map chart
- [ ] Create momentum ranking chart

### Week 3: Report Generation
- [ ] Implement generate_sector_report.py
- [ ] Create markdown template
- [ ] Implement HTML conversion
- [ ] Test report generation

### Week 4: Web App Integration
- [ ] Create sector.py API handler
- [ ] Add Flask routes
- [ ] Update index.html with tabs
- [ ] Create sector_analysis.html template
- [ ] Add JavaScript for tab switching
- [ ] Test web app integration

### Week 5: Testing & Refinement
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Backtest rotation strategy
- [ ] Refine scoring weights
- [ ] Performance optimization

### Week 6: Deployment
- [ ] Set up data update scheduler
- [ ] Deploy to web server
- [ ] User acceptance testing
- [ ] Documentation finalization

---

## Quick Start (Minimal Viable Product)

**For fastest implementation, start with:**

1. **Core calculations only** (no flows, simplified breadth)
   - RS vs SPY (20-day, 60-day)
   - Momentum ranking (3M + 6M)
   - Simple composite score

2. **Basic report**
   - Sector rankings table
   - Top 3 / Bottom 3 recommendations
   - Simple rotation status

3. **Web integration**
   - Add "Sector Analysis" tab
   - Single "Generate Report" button
   - Display rankings table

**Estimate:** 2-3 days for MVP

Then incrementally add:
- Flow analysis
- Breadth metrics
- Advanced visualizations
- Backtesting

---

## Dependencies

**Python packages:**
```
yfinance          # Fetch ETF data
pandas            # Data manipulation
numpy             # Calculations
matplotlib        # Charts
seaborn           # Advanced visualizations
scipy             # Statistical functions
```

**Optional:**
```
plotly            # Interactive charts
beautifulsoup4    # Web scraping (for flows)
requests          # API calls
```

---

## Expected Output Example

**Sector Rankings (June 21, 2026):**

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    SECTOR ROTATION ANALYSIS                           ║
║                      Date: 2026-06-21                                 ║
╠═══════════════════════════════════════════════════════════════════════╣
║ Rank │ Sector         │ Score │ RS(20d) │ Momentum │ Signal          ║
╠══════╪════════════════╪═══════╪═════════╪══════════╪═════════════════╣
║  1   │ Technology     │ 92.3  │  +8.2%  │  +15.8%  │ 🚀 STRONG BUY  ║
║  2   │ Healthcare     │ 85.7  │  +5.1%  │  +12.4%  │ ✅ BUY         ║
║  3   │ Financials     │ 78.4  │  +3.2%  │   +9.8%  │ ✅ BUY         ║
║  4   │ Industrials    │ 72.1  │  +1.8%  │   +7.2%  │ 👀 WATCH       ║
║  5   │ Cons. Discr.   │ 68.5  │  +0.9%  │   +5.1%  │ 👀 WATCH       ║
║ ...  │ ...            │  ...  │   ...   │    ...   │ ...            ║
║  9   │ Energy         │ 32.1  │  -4.2%  │   -6.8%  │ ❌ AVOID       ║
║ 10   │ Utilities      │ 28.6  │  -5.8%  │   -9.2%  │ ❌ AVOID       ║
║ 11   │ Real Estate    │ 21.4  │  -7.1%  │  -11.5%  │ ❌ AVOID       ║
╚══════╧════════════════╧═══════╧═════════╧══════════╧═════════════════╝

💼 PORTFOLIO RECOMMENDATION
   Overweight: XLK (25%), XLV (25%), XLF (20%)
   Avoid: XLE, XLU, XLRE
```

---

**Next Step:** Begin Phase 1 implementation - Data Pipeline
