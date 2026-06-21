# Stock Analysis Web App - Usage Guide

## Overview

The web application provides two types of reports:

### 1. **Technical Analysis** ✅ Fully Automated
- Click "Technical Analysis" → Get complete chart analysis with indicators
- Includes: RSI, MACD, Bollinger Bands, support/resistance, trends
- **Output**: Fully comprehensive HTML report

### 2. **Fundamental Analysis** ⚠️ Structure Only (Comprehensive Requires Claude Code)

The web app generates a **preliminary report structure** with:
- ✅ Current price and valuation data from Yahoo Finance
- ✅ Proper report sections (Price Level, Moat, Management, etc.)
- ❌ Incomplete analysis - requires research to complete

**Why?** Comprehensive fundamental analysis requires:
- Web research for recent earnings calls, news, SEC filings
- Competitive moat analysis with specific evidence
- Management track record assessment
- Scenario modeling with price targets
- Investment thesis and recommendations

This level of research cannot be automated by a simple web app script.

---

## How to Generate Comprehensive Fundamental Analysis

**Option 1: Use Claude Code (Recommended)**

In Claude Code terminal, type:
```
Generate fundamental analysis for {TICKER}
```

This will:
1. ✅ Research competitive moat with actual scores (e.g., 16/18)
2. ✅ Pull real financial metrics from filings
3. ✅ Assess management quality with track record
4. ✅ Identify specific issues (e.g., "AI Capex: $125-145B")
5. ✅ Build Bull/Base/Bear scenarios with price targets
6. ✅ Provide investment recommendation with position sizing
7. ✅ Generate HTML report (view in browser, print to PDF)

**Example Output**: See `fundamental_analysis_skill/analyses/META/META-2026-06-20.html`

---

**Option 2: Use Web App (Manual Completion Required)**

1. Enter ticker in web app
2. Click "Fundamental Research"
3. Click "Generate Reports"
4. Open the generated report
5. **Manually complete** all research sections:
   - Section 2: Moat Analysis (score each category 0-3)
   - Section 3: Business Quality Metrics (from 10-K/10-Q)
   - Section 4: Management Assessment (track record)
   - Section 5: Issue Identification (earnings calls, news)
   - Section 6-10: All other analytical sections
6. Run validation: `python fundamental_analysis_skill/scripts/validate_report_data.py {TICKER}`
7. Generate HTML: `python utils/md_to_html.py {report_path}`

---

## Recommended Workflow

### For Quick Price Check
→ Use web app for technical analysis

### For Investment Research
→ Use Claude Code for comprehensive fundamental analysis

Example:
```bash
# In Claude Code
> Generate fundamental analysis for AAPL
> Generate fundamental analysis for MSFT  
> Generate fundamental analysis for GOOGL
```

This gives you complete, research-backed reports like:
- [META-2026-06-20.html](../fundamental_analysis_skill/analyses/META/META-2026-06-20.html)
- [MSFT-2026-06-19.html](../fundamental_analysis_skill/analyses/MSFT/MSFT-2026-06-19.html)

---

## Web App Capabilities Summary

| Report Type | Web App Output | Quality Level | Time |
|-------------|----------------|---------------|------|
| **Technical Analysis** | ✅ Complete analysis | Comprehensive | ~30 sec |
| **Fundamental Analysis** | ⚠️ Structure only | Preliminary | ~10 sec |

| Task | Tool to Use |
|------|-------------|
| Get technical indicators & charts | ✅ Web App |
| Get preliminary price/valuation data | ✅ Web App |
| Get comprehensive investment research | ✅ Claude Code |
| Build full scenario analysis | ✅ Claude Code |
| Get investment recommendation | ✅ Claude Code |

---

## Why Not Fully Automate Fundamental Analysis?

**Technical analysis** = Quantitative (formulas, historical data)
- ✅ Can be automated

**Fundamental analysis** = Qualitative + Quantitative (requires judgment)
- Moat analysis → Requires understanding competitive dynamics
- Management assessment → Requires reviewing M&A history, track record
- Issue identification → Requires reading earnings calls, understanding context
- Scenario modeling → Requires business judgment and probability assessment
- Investment thesis → Requires synthesis and strategic insight

The META-2026-06-20 report took ~15 minutes of research:
- Read earnings transcripts
- Researched AI capex announcements
- Analyzed Reality Labs losses
- Compared to Google/TikTok competition
- Built probabilistic scenarios
- Assessed management track record

**This cannot be scripted** - it requires Claude Code's Agent tool with web search and synthesis capabilities.

---

## Future Enhancement

If you want the web app to generate comprehensive reports, you would need to:
1. Set up Anthropic API key
2. Integrate Claude API to call Agent tool
3. Add asynchronous job processing (reports take 5-15 minutes)
4. Add queue system for multiple concurrent requests

For now, use Claude Code directly for best results.
