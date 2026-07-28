# Stock Analysis Web Application

A modern, user-friendly web application for generating comprehensive stock analysis reports.

## Features

- **Beautiful UI**: Modern, gradient-based design with smooth animations
- **Multiple Report Types**:
  - 📊 **Fundamental Analysis**: Company moat, financials, management quality
  - 📈 **Technical Analysis**: Charts, indicators, trends, support/resistance levels
  - 🎯 **Potential Scenario Analysis**: Buy/sell/hold recommendations with entry/exit strategies
- **Real-time Analysis**: Fetch latest market data and generate fresh reports
- **Download Reports**: View HTML reports in browser or download markdown files
- **Chart Visualization**: Interactive technical analysis charts
- **HTML Reports**: Professional, print-ready HTML reports with built-in print-to-PDF button

## Installation

### 1. Install Dependencies

```bash
cd stock_analysis_app
pip install -r requirements.txt
```

### 2. Verify Parent Skills

Make sure the following skills are available in the parent directory:
- `fundamental_analysis_skill/`
- `.claude/skills/technical_analysis/`

## Usage

### Start the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Generate Reports

1. **Enter a stock ticker** (e.g., AAPL, TSLA, MSFT)
2. **Select report types** (one or multiple):
   - **Fundamental Analysis** ⚠️ See workflow below
   - **Technical Analysis** ✅ Fully automated
3. **Click "Generate Reports"**
4. **View or download** the generated reports

---

### ⚠️ Important: Fundamental Analysis Workflow

The web app generates a **preliminary structure** for fundamental analysis. For **comprehensive analysis** (like [META-2026-06-20.html](../fundamental_analysis_skill/analyses/META/META-2026-06-20.html)), follow this workflow:

#### Step 1: Click "Fundamental Research" in Web App
- Generates preliminary report with price/valuation data
- Creates report structure with all sections
- Displays message: "For comprehensive analysis, tell Claude Code: Generate fundamental analysis for {TICKER}"

#### Step 2: Use Claude Code for Comprehensive Analysis
In Claude Code terminal, type:
```
Generate fundamental analysis for AAPL
```

This will:
- ✅ Research competitive moat with actual scores (e.g., 16/18)
- ✅ Pull real financial metrics from SEC filings
- ✅ Assess management quality with track record
- ✅ Identify specific issues (e.g., "AI Capex: $125-145B")
- ✅ Build Bull/Base/Bear scenarios with price targets
- ✅ Provide investment recommendation with position sizing
- ✅ Generate comprehensive HTML report

#### Step 3: View Report
- Report saved to: `fundamental_analysis_skill/analyses/{TICKER}/{TICKER}-YYYY-MM-DD.html`
- Open in browser to view
- Use built-in print button to save as PDF

---

### Why This Workflow?

**Technical Analysis** = Quantitative formulas → Fully automated ✅

**Fundamental Analysis** = Requires research, judgment, synthesis:
- Read earnings transcripts
- Analyze competitive dynamics
- Assess management track record
- Build probabilistic scenarios
- Synthesize investment thesis

This requires Claude Code's Agent tool with web search capabilities. The web app alone cannot perform this level of analysis.

---

### Quick Reference

| Task | Use |
|------|-----|
| Technical analysis with indicators | ✅ Web App (automated) |
| Preliminary price/valuation check | ✅ Web App (automated) |
| Comprehensive fundamental analysis | 💬 Claude Code: `Generate fundamental analysis for {TICKER}` |
| View existing reports | ✅ Web App or file browser |

## Application Structure

```
stock_analysis_app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── api/                  # Backend API modules
│   ├── __init__.py
│   ├── fundamental.py    # Fundamental analysis generator
│   ├── technical.py      # Technical analysis generator
│   └── action_plan.py    # Action plan generator
├── static/               # Frontend assets
│   ├── css/
│   │   └── style.css    # Application styles
│   └── js/
│       └── main.js      # Frontend JavaScript
├── templates/            # HTML templates
│   └── index.html       # Main page
└── reports/             # Generated reports (auto-created)
```

## API Endpoints

### `POST /api/analyze`
Generate analysis reports for a stock

**Request Body**:
```json
{
  "ticker": "AAPL",
  "report_types": ["fundamental", "technical", "action_plan"]
}
```

**Response**:
```json
{
  "ticker": "AAPL",
  "timestamp": "2026-06-19T10:30:00",
  "reports": [
    {
      "type": "fundamental",
      "status": "success",
      "path": "/path/to/report.md",
      "url": "/api/report/AAPL_fundamental_20260619_103000.md"
    }
  ]
}
```

### `GET /api/report/<filename>`
Retrieve a generated report file

### `GET /api/health`
Health check endpoint

## Report Types

### Fundamental Analysis
Comprehensive company evaluation including:
- Price level assessment (HIGH/MEDIUM/LOW)
- Moat scorecard (0-18 points)
- Business issues identification
- Management quality assessment
- Financial resilience analysis
- Investment thesis and catalysts

### Technical Analysis
Chart-based analysis including:
- 20+ technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Trend direction and strength
- Support/resistance levels
- Trading signals
- Volume analysis
- Comprehensive price charts

### Potential Scenario Analysis
Actionable trading plan including:
- Overall recommendation (BUY/SELL/HOLD)
- Entry strategy and timing
- Position sizing guidelines
- Stop loss levels
- Take profit targets
- Risk management checklist
- Daily/weekly/monthly monitoring tasks

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Custom CSS with CSS Grid and Flexbox
- **Data**: Yahoo Finance (yfinance)
- **Analysis**: Custom technical and fundamental analysis modules

## Configuration

The application can be configured via `app.py`:

```python
# Change server port
app.run(debug=True, host='0.0.0.0', port=5000)

# Change reports directory
app.config['REPORTS_DIR'] = Path(__file__).parent / 'reports'
```

## Development

### Adding New Report Types

1. Create a new module in `api/` (e.g., `api/sentiment.py`)
2. Implement the generation function
3. Add endpoint handling in `app.py`
4. Update frontend in `templates/index.html`
5. Add styling in `static/css/style.css`
6. Add JavaScript logic in `static/js/main.js`

### Customizing the UI

- **Colors**: Edit CSS variables in `static/css/style.css`
- **Layout**: Modify `templates/index.html`
- **Animations**: Update CSS animations in `style.css`

## Troubleshooting

### "Module not found" errors
```bash
# Make sure you're in the right directory
cd stock_analysis_app
pip install -r requirements.txt
```

### "No data available" errors
- Check that the ticker symbol is valid
- Verify internet connection
- Check Yahoo Finance availability

### Reports not generating
- Verify parent skill directories exist
- Check that required scripts are executable
- Review terminal output for detailed error messages

## Security Notes

- This application is designed for local use
- Do not expose to the public internet without proper authentication
- Generated reports are stored locally in the `reports/` directory
- No user data is collected or stored

## Future Enhancements

- [x] Export to HTML/PDF (✅ Implemented - HTML reports with print-to-PDF)
- [ ] User authentication
- [ ] Report history and comparison
- [ ] Multiple stocks comparison
- [ ] Portfolio-level analysis
- [ ] Email report delivery
- [ ] Scheduled automated reports
- [ ] Integration with trading platforms

## License

MIT License - See parent repository LICENSE file

---

**Version**: 1.0.0  
**Last Updated**: 2026-06-19  
**Python Version**: 3.9+
