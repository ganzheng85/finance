# Web App Integration Example - Tabbed Interface

## Overview

Add a tabbed interface to switch between **Company Analysis** and **Sector Analysis**.

---

## HTML Structure (Add to index.html)

### 1. Add Tab Navigation (After Header, Before Main Content)

```html
<!-- Tab Navigation -->
<div class="tab-navigation">
    <button class="tab-button active" onclick="switchTab('company')" id="company-tab-btn">
        <svg width="20" height="20" fill="currentColor" style="margin-right: 8px;">
            <path d="M3 3h18v2H3V3zm0 4h18v2H3V7zm0 4h18v2H3v-2zm0 4h18v2H3v-2z"/>
        </svg>
        Company Analysis
    </button>
    <button class="tab-button" onclick="switchTab('sector')" id="sector-tab-btn">
        <svg width="20" height="20" fill="currentColor" style="margin-right: 8px;">
            <path d="M3 13h8v8H3v-8zm10 0h8v8h-8v-8zM3 3h8v8H3V3zm10 0h8v8h-8V3z"/>
        </svg>
        Sector Rotation
    </button>
</div>
```

### 2. Wrap Existing Content in Company Tab

```html
<!-- Company Analysis Tab Content -->
<div id="company-content" class="tab-content active">
    <!-- ALL EXISTING CONTENT GOES HERE -->
    <!-- Search form, results, etc. -->
</div>
```

### 3. Add Sector Analysis Tab Content

```html
<!-- Sector Analysis Tab Content -->
<div id="sector-content" class="tab-content" style="display: none;">
    <div class="card">
        <h2>Sector Rotation Analysis</h2>
        <p class="subtitle-text">
            Track institutional money flow across market sectors
        </p>

        <!-- Generate Button -->
        <div class="generate-section">
            <button id="generate-sector-btn" class="btn btn-primary">
                <svg width="20" height="20" fill="currentColor" style="margin-right: 8px;">
                    <path d="M13 7h8v2h-8V7zm0 4h8v2h-8v-2zm0 4h8v2h-8v-2zM3 4h6v6H3V4zm0 8h6v6H3v-6z"/>
                </svg>
                Generate Sector Analysis
            </button>
            <p class="help-text">
                Analyzes 13 sectors and ranks by momentum, flows, and breadth
            </p>
        </div>

        <!-- Loading Indicator -->
        <div id="sector-loading" class="loading" style="display: none;">
            <div class="spinner"></div>
            <p>Analyzing sector rotation...</p>
        </div>

        <!-- Results Container -->
        <div id="sector-results" class="results-container" style="display: none;">
            <!-- Sector Rankings Table -->
            <div class="sector-rankings">
                <h3>Sector Rankings</h3>
                <div id="rankings-table"></div>
            </div>

            <!-- Rotation Status -->
            <div class="rotation-status">
                <h3>Rotation Map</h3>
                <div id="rotation-map"></div>
            </div>

            <!-- Portfolio Recommendation -->
            <div class="portfolio-recommendation">
                <h3>Portfolio Recommendation</h3>
                <div id="portfolio-rec"></div>
            </div>

            <!-- View Reports Links -->
            <div class="report-actions">
                <button class="btn btn-secondary" id="view-sector-report">
                    View Full Report
                </button>
                <button class="btn btn-secondary" id="view-sector-charts">
                    View Charts
                </button>
            </div>
        </div>
    </div>
</div>
```

---

## CSS Styles (Add to style.css)

```css
/* Tab Navigation */
.tab-navigation {
    display: flex;
    gap: 1rem;
    margin: 2rem 0;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 0;
}

.tab-button {
    display: flex;
    align-items: center;
    padding: 1rem 1.5rem;
    background: none;
    border: none;
    border-bottom: 3px solid transparent;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 500;
    color: #6b7280;
    transition: all 0.3s ease;
    position: relative;
    bottom: -2px;
}

.tab-button:hover {
    color: #667eea;
    background-color: #f9fafb;
}

.tab-button.active {
    color: #667eea;
    border-bottom-color: #667eea;
    font-weight: 600;
}

.tab-button svg {
    transition: transform 0.3s ease;
}

.tab-button:hover svg {
    transform: scale(1.1);
}

/* Tab Content */
.tab-content {
    animation: fadeIn 0.3s ease-in;
}

.tab-content.active {
    display: block;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Sector Analysis Specific Styles */
.generate-section {
    text-align: center;
    padding: 2rem 0;
}

.btn-primary {
    display: inline-flex;
    align-items: center;
    padding: 0.875rem 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(102, 126, 234, 0.25);
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(102, 126, 234, 0.35);
}

.btn-primary:active {
    transform: translateY(0);
}

.help-text {
    margin-top: 0.75rem;
    color: #6b7280;
    font-size: 0.875rem;
}

/* Sector Rankings Table */
.sector-rankings {
    margin: 2rem 0;
}

.sector-rankings h3 {
    margin-bottom: 1rem;
    color: #1f2937;
}

.rankings-table {
    width: 100%;
    border-collapse: collapse;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.rankings-table th {
    background-color: #f9fafb;
    padding: 0.75rem;
    text-align: left;
    font-weight: 600;
    color: #374151;
    border-bottom: 2px solid #e5e7eb;
}

.rankings-table td {
    padding: 0.75rem;
    border-bottom: 1px solid #e5e7eb;
}

.rankings-table tr:hover {
    background-color: #f9fafb;
}

/* Signal Badges */
.signal-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.875rem;
    font-weight: 600;
}

.signal-strong-buy {
    background-color: #d1fae5;
    color: #065f46;
}

.signal-buy {
    background-color: #dcfce7;
    color: #166534;
}

.signal-watch {
    background-color: #fef3c7;
    color: #92400e;
}

.signal-avoid {
    background-color: #fee2e2;
    color: #991b1b;
}

/* Portfolio Recommendation */
.portfolio-recommendation {
    margin: 2rem 0;
    padding: 1.5rem;
    background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
    border-radius: 8px;
    border-left: 4px solid #667eea;
}

.portfolio-recommendation h3 {
    margin-bottom: 1rem;
    color: #1f2937;
}

/* Report Actions */
.report-actions {
    display: flex;
    gap: 1rem;
    margin-top: 2rem;
}

.btn-secondary {
    padding: 0.75rem 1.5rem;
    background-color: white;
    border: 2px solid #667eea;
    color: #667eea;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-secondary:hover {
    background-color: #667eea;
    color: white;
    transform: translateY(-2px);
}
```

---

## JavaScript (Add to index.html or separate JS file)

```javascript
// Tab Switching
function switchTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.style.display = 'none';
        content.classList.remove('active');
    });

    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName + '-content').style.display = 'block';
    document.getElementById(tabName + '-content').classList.add('active');
    
    // Add active class to clicked button
    document.getElementById(tabName + '-tab-btn').classList.add('active');
}

// Sector Analysis Generation
document.getElementById('generate-sector-btn').addEventListener('click', async () => {
    // Show loading
    document.getElementById('sector-loading').style.display = 'block';
    document.getElementById('sector-results').style.display = 'none';

    try {
        // Call API
        const response = await fetch('/api/sector/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.success) {
            // Hide loading
            document.getElementById('sector-loading').style.display = 'none';
            
            // Display results
            displaySectorResults(data);
            
            // Show results container
            document.getElementById('sector-results').style.display = 'block';
        } else {
            alert('Error generating sector analysis: ' + data.error);
            document.getElementById('sector-loading').style.display = 'none';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to generate sector analysis');
        document.getElementById('sector-loading').style.display = 'none';
    }
});

function displaySectorResults(data) {
    // Display rankings table
    const rankingsHTML = generateRankingsTable(data.rankings);
    document.getElementById('rankings-table').innerHTML = rankingsHTML;

    // Display rotation map
    const rotationHTML = generateRotationMap(data.rotation_map);
    document.getElementById('rotation-map').innerHTML = rotationHTML;

    // Display portfolio recommendation
    const portfolioHTML = generatePortfolioRec(data.portfolio);
    document.getElementById('portfolio-rec').innerHTML = portfolioHTML;

    // Setup report view buttons
    document.getElementById('view-sector-report').onclick = () => {
        window.open(data.report_url, '_blank');
    };

    document.getElementById('view-sector-charts').onclick = () => {
        window.open(data.charts_url, '_blank');
    };
}

function generateRankingsTable(rankings) {
    let html = '<table class="rankings-table">';
    html += '<thead><tr>';
    html += '<th>Rank</th>';
    html += '<th>Sector</th>';
    html += '<th>Score</th>';
    html += '<th>RS (20d)</th>';
    html += '<th>Momentum</th>';
    html += '<th>Signal</th>';
    html += '</tr></thead>';
    html += '<tbody>';

    rankings.forEach(sector => {
        const signalClass = getSignalClass(sector.signal);
        html += '<tr>';
        html += `<td><strong>${sector.rank}</strong></td>`;
        html += `<td>${sector.name} (${sector.ticker})</td>`;
        html += `<td>${sector.score.toFixed(1)}</td>`;
        html += `<td>${sector.rs_20d > 0 ? '+' : ''}${sector.rs_20d.toFixed(2)}%</td>`;
        html += `<td>${sector.momentum > 0 ? '+' : ''}${sector.momentum.toFixed(2)}%</td>`;
        html += `<td><span class="signal-badge ${signalClass}">${sector.signal}</span></td>`;
        html += '</tr>';
    });

    html += '</tbody></table>';
    return html;
}

function getSignalClass(signal) {
    if (signal.includes('STRONG BUY')) return 'signal-strong-buy';
    if (signal.includes('BUY')) return 'signal-buy';
    if (signal.includes('WATCH')) return 'signal-watch';
    return 'signal-avoid';
}

function generateRotationMap(rotation_map) {
    // Simple text-based quadrant display
    let html = '<div class="rotation-quadrants">';
    
    html += '<div class="quadrant leading">';
    html += '<h4>🚀 Leading (Strong + Accelerating)</h4>';
    html += '<ul>';
    rotation_map.leading.forEach(sector => {
        html += `<li>${sector}</li>`;
    });
    html += '</ul></div>';

    html += '<div class="quadrant weakening">';
    html += '<h4>⚠️ Weakening (Strong + Decelerating)</h4>';
    html += '<ul>';
    rotation_map.weakening.forEach(sector => {
        html += `<li>${sector}</li>`;
    });
    html += '</ul></div>';

    html += '<div class="quadrant lagging">';
    html += '<h4>❌ Lagging (Weak + Decelerating)</h4>';
    html += '<ul>';
    rotation_map.lagging.forEach(sector => {
        html += `<li>${sector}</li>`;
    });
    html += '</ul></div>';

    html += '<div class="quadrant improving">';
    html += '<h4>👀 Improving (Weak + Accelerating)</h4>';
    html += '<ul>';
    rotation_map.improving.forEach(sector => {
        html += `<li>${sector}</li>`;
    });
    html += '</ul></div>';

    html += '</div>';
    return html;
}

function generatePortfolioRec(portfolio) {
    let html = '<div class="portfolio-allocations">';
    
    html += '<h4>Recommended Allocation (Top 5):</h4>';
    html += '<ul class="allocation-list">';
    portfolio.top_5.forEach(sector => {
        html += `<li><strong>${sector.name} (${sector.ticker})</strong>: ${sector.allocation}%</li>`;
    });
    html += '</ul>';

    html += '<h4 style="margin-top: 1.5rem;">Avoid (Bottom 3):</h4>';
    html += '<ul class="avoid-list">';
    portfolio.bottom_3.forEach(sector => {
        html += `<li>${sector.name} (${sector.ticker})</li>`;
    });
    html += '</ul>';

    html += '</div>';
    return html;
}
```

---

## Flask API Endpoint (Add to app.py)

```python
from flask import Flask, request, jsonify
from stock_analysis_app.api import sector

@app.route('/api/sector/generate', methods=['POST'])
def generate_sector_analysis():
    """Generate sector rotation analysis"""
    try:
        # Call sector analysis module
        result = sector.generate_sector_analysis()
        
        return jsonify({
            'success': True,
            'rankings': result['rankings'],
            'rotation_map': result['rotation_map'],
            'portfolio': result['portfolio'],
            'report_url': result['report_path'],
            'charts_url': result['charts_path']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

---

## Example API Response

```json
{
  "success": true,
  "rankings": [
    {
      "rank": 1,
      "name": "Technology",
      "ticker": "XLK",
      "score": 92.3,
      "rs_20d": 8.2,
      "momentum": 15.8,
      "signal": "🚀 STRONG BUY"
    },
    {
      "rank": 2,
      "name": "Healthcare",
      "ticker": "XLV",
      "score": 85.7,
      "rs_20d": 5.1,
      "momentum": 12.4,
      "signal": "✅ BUY"
    }
  ],
  "rotation_map": {
    "leading": ["XLK", "XLV"],
    "weakening": ["XLF"],
    "lagging": ["XLE", "XLU", "XLRE"],
    "improving": ["XLY"]
  },
  "portfolio": {
    "top_5": [
      {"name": "Technology", "ticker": "XLK", "allocation": 25},
      {"name": "Healthcare", "ticker": "XLV", "allocation": 25}
    ],
    "bottom_3": [
      {"name": "Energy", "ticker": "XLE"},
      {"name": "Utilities", "ticker": "XLU"}
    ]
  },
  "report_url": "/reports/Sector_Rotation_20260621.html",
  "charts_url": "/reports/charts/rotation_map_20260621.png"
}
```

---

## Summary

**Implementation steps:**
1. ✅ Add tab navigation HTML
2. ✅ Wrap existing content in company-content div
3. ✅ Add sector-content div with UI
4. ✅ Add CSS styles for tabs and sector UI
5. ✅ Add JavaScript for tab switching and API calls
6. ✅ Add Flask API endpoint
7. ✅ Implement sector analysis backend (see IMPLEMENTATION_PLAN.md)

**Result:** Tabbed interface switching between Company and Sector analysis!
