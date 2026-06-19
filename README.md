# Finance Analysis Repository

A comprehensive suite of financial analysis tools and skills for stock analysis, technical analysis, trading performance evaluation, and investment decision-making.

## 📁 Repository Structure

```
finance/
├── fundamental_analysis_skill/    # Fundamental stock analysis (moat, management, financials)
├── technical_analysis/            # Technical indicators and chart analysis
├── trades_analysis_skill/         # Portfolio trading performance analysis
├── dip_buying_skill/              # Systematic dip buying framework
├── ercot_analysis_skill/          # ERCOT electricity market analysis
├── utils/                         # Shared utilities (PDF conversion, etc.)
├── adhoc_analyses/                # One-off research and strategy analyses
├── change_log/                    # Repository change history and migration notes
└── requirements.txt               # Python dependencies
```

---

## 🛠️ Skills Overview

### 1. Fundamental Analysis Skill
**Purpose**: Comprehensive fundamental stock analysis and company evaluation

**Key Features**:
- Price level assessment (HIGH/MEDIUM/LOW)
- Moat scorecard (0-18 points across 6 dimensions)
- Current business issues identification and severity scoring
- Management problem-solving capability evaluation
- Financial resilience & capital allocation analysis
- Investment thesis, catalysts, and risk-reward scenarios
- Strategic investment productivity analysis (AI, R&D, capex effectiveness)
- PDF report generation with highlights summary

**Use When**: Analyzing company fundamentals, moat strength, or management quality

**Triggers**: "stock analysis", "fundamental analysis", "company analysis"

**Location**: `fundamental_analysis_skill/`

---

### 2. Technical Analysis Skill
**Purpose**: Technical indicators and chart-based stock analysis

**Key Features**:
- 20+ technical indicators (RSI, MACD, Bollinger Bands, ADX, Stochastic, etc.)
- Trend direction and strength analysis
- Support/resistance level identification
- Trading signal generation
- Momentum and volatility analysis
- Volume analysis and relative volume
- Comprehensive chart visualization
- Markdown and PDF report generation

**Use When**: Evaluating technical setups, trend analysis, or entry/exit timing

**Triggers**: "technical analysis", "chart analysis", "RSI", "MACD"

**Location**: `technical_analysis/`

---

### 3. Trades Analysis Skill
**Purpose**: Trading performance and portfolio analysis

**Key Features**:
- Realized P&L calculation using FIFO methodology
- Unrealized P&L with current market prices
- Win/loss rate statistics
- Best/worst trading decisions identification
- Portfolio performance metrics
- Transaction history analysis

**Use When**: Evaluating trading performance or portfolio positions

**Triggers**: "trades analysis", "portfolio analysis", "P&L analysis"

**Location**: `trades_analysis_skill/`

---

### 4. Dip Buying Skill
**Purpose**: Systematic framework for buying stocks on price drops

**Key Features**:
- Drop severity quantification
- Bargain vs value trap analysis
- Catalyst identification (temporary vs structural)
- Entry timing and position sizing
- Risk/reward assessment
- Exit strategy planning

**Use When**: Analyzing whether a price drop is a buying opportunity

**Triggers**: "dip buying", "price drop analysis", "buying opportunity"

**Location**: `dip_buying_skill/`

---

### 5. ERCOT Analysis Skill
**Purpose**: Daily ERCOT electricity market analysis

**Key Features**:
- Real-time settlement point prices
- Generator outage reports
- Renewable generation mix (wind, solar)
- Battery storage performance
- Transmission congestion analysis
- Price spike detection

**Use When**: Analyzing ERCOT grid conditions and electricity prices

**Triggers**: "ERCOT analysis", "electricity market", "Texas grid"

**Location**: `ercot_analysis_skill/`

---

## 🚀 Quick Start

### Installation

1. **Clone the repository** (if not already done)
   ```bash
   git clone <repository-url>
   cd finance
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Core Dependencies

- **yfinance** - Yahoo Finance data fetching
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computing
- **matplotlib** - Chart visualization
- **beautifulsoup4** - Web scraping
- **requests** - HTTP requests
- **markdown** - Markdown to HTML conversion
- **xhtml2pdf** - PDF generation

---

## 📖 Usage Examples

### Fundamental Analysis
```bash
# Analyze a stock's fundamentals
cd fundamental_analysis_skill
python scripts/price_analysis.py AAPL

# Fetch quarterly financial data
python scripts/fetch_quarterly_data.py MSFT --export

# Convert analysis to PDF
python ../utils/md_to_pdf.py "analyses/AAPL/AAPL-2026-06-18.md"
```

### Technical Analysis
```bash
# Run technical analysis for a stock
cd technical_analysis
python scripts/analyze_stock.py TSLA

# Generate comprehensive chart
python scripts/plot_comprehensive_analysis.py NVDA

# Fetch data and calculate technical factors
python scripts/fetch_and_analyze.py GOOGL --days 60
```

### Trading Performance Analysis
```bash
# Analyze trading history
cd trades_analysis_skill
python scripts/analyze_trades.py ../adhoc_analyses/portfolio.csv

# Calculate realized P&L (FIFO)
python scripts/calculate_realized_pnl.py ../adhoc_analyses/portfolio.csv
```

---

## 📊 Output Files

### Analysis Reports
- **Markdown reports**: `analyses/{TICKER}/{TICKER}-{DATE}.md`
- **PDF reports**: `analyses/{TICKER}/{TICKER}-{DATE}.pdf`
- **Highlights**: `analyses/{TICKER}/{TICKER}-{DATE}-Highlights.md`
- **Charts**: `analyses/{TICKER}_Comprehensive_Chart_{TIMESTAMP}.png`

### Data Files
- **CSV exports**: `data/{TICKER}/{ticker}_quarterly_{statement}.csv`
- **Technical factors**: `analyses/{TICKER}_technical_factors_{DATE}.csv`
- **Trading data**: `data/trades_export_{DATE}.csv`

---

## 🔧 Utilities

### Shared Utilities (`utils/`)

**`md_to_pdf.py`** - Convert Markdown reports to PDF
```bash
python utils/md_to_pdf.py "path/to/report.md"
```

Features:
- Table support
- Code block formatting
- Unicode character handling
- Automatic filename generation

---

## 📝 Adhoc Analyses

The `adhoc_analyses/` folder contains one-off research and strategy analyses:
- Portfolio allocation strategies
- Sector rotation analysis
- Valuation analyses
- Investment strategy comparisons
- Market research reports

---

## 📚 Documentation

Each skill contains comprehensive documentation:
- **SKILL.md** - Skill definition and workflow
- **README.md** - Installation and usage guide
- **references/** - Templates, frameworks, and examples

---

## 🔄 Change Log

Repository evolution and migration notes are tracked in `change_log/`:
- **REORGANIZATION_PLAN.md** - Repository restructuring plan
- **REORGANIZATION_SUMMARY.md** - Summary of organizational changes
- **MIGRATION_NOTES.md** - Migration guides and breaking changes

---

## 🎯 Best Practices

1. **Always fetch fresh data** - Stock markets change rapidly
2. **Use multiple analysis types** - Combine fundamental, technical, and trading analysis
3. **Document assumptions** - State confidence levels and data sources
4. **Version control analyses** - Keep historical analyses for reference
5. **Separate facts from opinions** - Make interpretation clear in reports

---

## 🛡️ Limitations & Disclaimers

- **Not financial advice** - For educational and informational purposes only
- **Data delays** - Yahoo Finance data is typically 15-20 minutes delayed
- **Internet required** - All data fetching requires active connection
- **Analysis quality** - Dependent on available data and market conditions

Always conduct your own research and consult with licensed financial advisors before making investment decisions.

---

## 🤝 Contributing

To add new skills or improve existing ones:
1. Follow the existing skill structure (SKILL.md, README.md, scripts/, analyses/)
2. Update this README with new skill documentation
3. Add shared utilities to `utils/` folder
4. Document all dependencies in `requirements.txt`

---

## 📄 License

MIT License - See LICENSE file for details

---

**Version**: 2.0  
**Last Updated**: 2026-06-19  
**Python Version**: 3.9+
