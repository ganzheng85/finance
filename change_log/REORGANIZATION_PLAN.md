# Repository Reorganization Plan

**Date:** June 17, 2026  
**Goal:** Organize files into proper directories for better maintainability

---

## Current Issues

1. ❌ **Ad hoc analysis reports scattered in root** (7 files)
2. ❌ **Notebooks in technical_analysis root** (should be in notebooks/)
3. ❌ **Some Python files in technical_analysis root** (techinical_factor.py, utilities.py should be in lib/)
4. ❌ **Trade data files in skill root** (should be in data/ subdirectory)

---

## Proposed Structure

```
finance/
├── adhoc_analyses/           # NEW: All ad hoc analysis reports
│   ├── SP500_strategy_analysis.md
│   ├── VOO_accumulation_strategy.md
│   ├── cash_allocation_strategy.md
│   ├── cash_position_analysis_2M_portfolio.md
│   ├── model_deployment_comparison.md
│   ├── oracle_ai_infrastructure_research_q3_fy26.md
│   └── sector_rotation_analysis_20260617.md
│
├── utils/                    # Shared utilities across skills
│   ├── README.md
│   ├── MIGRATION_NOTES.md
│   └── md_to_pdf.py         # Shared PDF conversion utility
│
├── dip_buying_skill/
│   ├── README.md
│   ├── SKILL.md
│   ├── scripts/
│   │   └── dip_analyzer.py
│   ├── analyses/
│   │   ├── SMH-dip-buying-plan.csv
│   │   └── SMH-dip-buying-plan-with-support-levels.csv
│   └── references/
│       ├── historical-examples.md
│       ├── position-sizing-guide.md
│       └── *.csv (reference data)
│
├── ercot_analysis_skill/
│   ├── README.md
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── fetch_ercot_data.py
│   │   └── fetch_gridstatus_data.py
│   ├── analyses/
│   │   └── ERCOT-2026-06-04.md
│   └── references/
│       ├── analysis-framework.md
│       ├── analysis-template.md
│       └── data-sources.md
│
├── stock_analysis_skill/
│   ├── README.md
│   ├── SKILL.md
│   ├── CHANGELOG.md
│   ├── UPDATE_SUMMARY.md
│   ├── scripts/
│   │   ├── fetch_quarterly_data.py
│   │   ├── price_analysis.py
│   │   ├── sec_company_snapshot.py
│   │   ├── convert_to_pdf.py
│   │   └── md_to_pdf_simple.py
│   ├── analyses/
│   │   ├── AMZN/
│   │   ├── AVGO/
│   │   ├── META/
│   │   ├── MSFT/
│   │   ├── NOW/
│   │   ├── ORCL/
│   │   └── SAP/
│   ├── data/                 # Quarterly financial data
│   │   ├── AMZN/
│   │   ├── AVGO/
│   │   ├── META/
│   │   ├── MSFT/
│   │   ├── NOW/
│   │   ├── ORCL/
│   │   └── SAP/
│   ├── examples/             # Sample analyses
│   │   └── sample-analysis.md
│   └── references/
│       ├── analysis-framework.md
│       ├── analysis-framework-additions.md
│       ├── analysis-template.md
│       └── strategic-investment-productivity-template.csv
│
├── technical_analysis/
│   ├── README.md
│   ├── SKILL.md
│   ├── REVIEW_REPORT.md
│   ├── CLEANUP_SUMMARY.md
│   ├── scripts/
│   │   ├── analyze_stock.py
│   │   ├── analyze_dip_strategy.py
│   │   ├── check_today_market.py
│   │   ├── fetch_and_analyze.py
│   │   └── trend_analyzer.py
│   ├── lib/                  # NEW: Core library code
│   │   ├── __init__.py
│   │   ├── techinical_factor.py
│   │   └── utilities.py
│   ├── notebooks/            # NEW: Jupyter notebooks
│   │   ├── calculate_techinical_factors.ipynb
│   │   ├── compare_returns.ipynb
│   │   ├── eodhd_data.ipynb
│   │   ├── get_historical_sp500_companies.ipynb
│   │   └── model_training.ipynb
│   └── analyses/
│       ├── AAPL_Technical_Analysis_*.md
│       ├── AMZN_Technical_Analysis_*.md
│       ├── FIG_Technical_Analysis_*.md
│       ├── MSFT_Technical_Analysis_*.md
│       └── SMH_Technical_Analysis_*.md
│
├── trades_analysis_skill/
│   ├── README.md
│   ├── SKILL.md
│   ├── OVERVIEW.md
│   ├── QUICKSTART.md
│   ├── CHANGELOG.md
│   ├── scripts/
│   │   ├── analyze_trades.py
│   │   ├── calculate_realized_pnl.py
│   │   └── fundamental_analysis.py
│   ├── analyses/
│   │   ├── README.md
│   │   ├── Deep-Value-Analysis-Should-You-Hold-Losers.md
│   │   ├── Mean-Reversion-Analysis-META-MSFT.md
│   │   ├── SP500-Comparison-Summary.md
│   │   ├── Trading-Analysis-2026-06-11.md
│   │   ├── Trading-Analysis-2026-06-12-*.md
│   │   └── Winner-Reversal-vs-Loser-Recovery-Analysis.md
│   └── data/                 # Trade data (user data + samples)
│       ├── sample_trades.csv
│       ├── trades_cleaned.csv
│       └── trades_for_analysis.csv
│
└── utils/                    # Shared utilities (stays as-is)
    ├── README.md
    ├── MIGRATION_NOTES.md
    └── md_to_pdf.py         # Shared PDF conversion utility
```

---

## Migration Steps

### Phase 1: Create New Directories ✅
```bash
mkdir -p adhoc_analyses
mkdir -p technical_analysis/lib
mkdir -p technical_analysis/notebooks
mkdir -p trades_analysis_skill/data
mkdir -p stock_analysis_skill/examples  # If doesn't exist
```

### Phase 2: Move Ad Hoc Analyses ✅
Move from root to `adhoc_analyses/`:
- SP500_strategy_analysis.md
- VOO_accumulation_strategy.md
- cash_allocation_strategy.md
- cash_position_analysis_2M_portfolio.md
- model_deployment_comparison.md
- oracle_ai_infrastructure_research_q3_fy26.md
- sector_rotation_analysis_20260617.md

### Phase 3: Move Technical Analysis Files ✅
- Move `technical_analysis/techinical_factor.py` → `technical_analysis/lib/`
- Move `technical_analysis/utilities.py` → `technical_analysis/lib/`
- Move `technical_analysis/*.ipynb` → `technical_analysis/notebooks/`

### Phase 4: Reorganize Trades Data ✅
- Move `trades_analysis_skill/trades_cleaned.csv` → `trades_analysis_skill/data/`
- Move `trades_analysis_skill/trades_for_analysis.csv` → `trades_analysis_skill/data/`
- Keep `trades_analysis_skill/sample_trades.csv` → `trades_analysis_skill/data/` (sample data)

### Phase 5: Update Import Statements 🔧
Update scripts that import from moved files:
- `technical_analysis/scripts/*.py` → Update imports for `techinical_factor.py`, `utilities.py`
- Imports remain: `utils/md_to_pdf.py` (no changes needed)

### Phase 6: Update Documentation 📝
- Update README files to reflect new structure
- Update SKILL.md files if they reference file paths
- Add note to root README about organization

---

## Benefits of New Structure

### ✅ Clear Separation of Concerns
- **adhoc_analyses/**: All one-off analysis reports in one place
- **utils/**: Shared utilities across all skills
- **{skill}/lib/**: Skill-specific library code
- **{skill}/scripts/**: Skill-specific executable scripts
- **{skill}/analyses/**: Skill-specific analysis outputs
- **{skill}/data/**: Skill-specific data files (including samples)
- **{skill}/examples/**: Example outputs and templates

### ✅ Easier Navigation
- No more root clutter (7 analysis files → organized in adhoc_analyses/)
- Clear skill boundaries
- Shared code in utils/ folder

### ✅ Better Scalability
- New skills follow same pattern
- Shared utilities available in utils/
- Each skill manages its own data and samples

### ✅ Improved Maintainability
- Import paths are clearer
- Dependencies are obvious
- Easier to find related files

---

## Backwards Compatibility Notes

### Files That Will Need Import Updates:

**technical_analysis/scripts/analyze_stock.py:**
```python
# OLD
from techinical_factor import TechnicalFactors
from utilities import some_function

# NEW
from technical_analysis.lib.techinical_factor import TechnicalFactors
from technical_analysis.lib.utilities import some_function
```

**Imports for utils remain unchanged - no action needed.**

---

## Execution Plan

1. ✅ Create all new directories
2. ✅ Move files in phases (test after each phase)
3. 🔧 Update import statements
4. 🔧 Update documentation
5. ✅ Test each skill to ensure it still works
6. 📝 Update root README with new structure
7. 🗑️ Mark utils/ as deprecated in README

**Estimated time:** 30-45 minutes  
**Risk level:** Low (can be rolled back via git)  
**Testing required:** Yes (run each skill after reorganization)

---

## Rollback Plan

If issues arise:
```bash
git status                    # See what was moved
git checkout -- .             # Restore all files
git clean -fd                 # Remove new directories
```

Or selectively:
```bash
git mv adhoc_analyses/SP500_strategy_analysis.md ./
# Repeat for each moved file
```

---

**Ready to execute? Confirm to proceed with reorganization.**
