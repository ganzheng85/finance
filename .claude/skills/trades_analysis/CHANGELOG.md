# Changelog

All notable changes to the Trades Analysis Skill will be documented in this file.

## [1.0.0] - 2026-06-12

### Added
- Initial release of Trades Analysis Skill
- **SKILL.md**: Main skill definition with comprehensive workflow
- **README.md**: Complete documentation with usage examples
- **analyze_trades.py**: Unrealized P&L analysis script
  - Fetches current prices from Yahoo Finance
  - Analyzes current holdings vs purchase/sale prices
  - Calculates portfolio value and unrealized P&L
  - Identifies best/worst trading decisions
- **calculate_realized_pnl.py**: Realized P&L analysis using FIFO methodology
  - Matches buy-sell pairs chronologically
  - Calculates actual realized gains/losses
  - Provides win/loss statistics and ratios
  - Shows P&L by ticker and by month
- **sample_trades.csv**: Template CSV file for new users
- **analyses/**: Directory for storing generated reports
- **.gitignore**: Protects personal financial data from being committed
- **Trading-Analysis-2026-06-11.md**: Sample analysis report

### Features
- Dual analysis approach (unrealized + realized P&L)
- FIFO-based cost basis calculation (tax-compliant)
- Comprehensive trading metrics:
  - Overall success rate
  - Win/loss rates and ratios
  - Best/worst trade identification
  - Portfolio value tracking
  - Monthly performance trends
- Integration with shared `utils/md_to_pdf.py` for PDF generation
- Privacy-focused with gitignored trade data
- Compatible with Claude Code skill system

### Documentation
- Complete README with installation instructions
- Usage examples for all scripts
- CSV format specification
- Troubleshooting guide
- Best practices for trading analysis

## Roadmap

### Planned Features (Future Versions)
- [ ] Benchmark comparison (S&P 500, sector indices)
- [ ] Risk-adjusted return metrics (Sharpe, Sortino ratios)
- [ ] Sector/industry breakdown analysis
- [ ] Transaction cost modeling
- [ ] Tax-loss harvesting suggestions
- [ ] Automated monthly/quarterly reports
- [ ] Portfolio rebalancing recommendations
- [ ] Monte Carlo simulations for risk assessment
- [ ] Integration with broker APIs for automatic data import
- [ ] Web dashboard for visualization

### Potential Enhancements
- [ ] Support for options and crypto trading analysis
- [ ] Multi-currency support for international portfolios
- [ ] Dividend tracking and analysis
- [ ] Performance attribution analysis
- [ ] Drawdown analysis and recovery tracking
- [ ] Custom date range analysis
- [ ] Comparison across multiple time periods

---

**Note**: This is version 1.0.0 - the initial release. Please report any issues or feature requests through the project repository.
