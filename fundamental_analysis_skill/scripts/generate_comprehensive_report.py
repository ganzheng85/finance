#!/usr/bin/env python3
"""
Generate Comprehensive Fundamental Analysis Report

Creates a full fundamental analysis report following the MSFT-2026-06-19.md template structure.
Includes all required sections with actual data from Yahoo Finance and SEC filings.

Usage:
    python generate_comprehensive_report.py MSFT
    python generate_comprehensive_report.py AAPL --output-dir ../analyses/AAPL
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

try:
    import yfinance as yf
except ImportError:
    print("Error: yfinance not installed. Install with: pip install yfinance")
    sys.exit(1)


def fetch_comprehensive_data(ticker: str) -> Dict[str, Any]:
    """Fetch comprehensive data for fundamental analysis"""
    print(f"Fetching comprehensive data for {ticker}...")

    stock = yf.Ticker(ticker)
    info = stock.info
    history = stock.history(period="1y")

    if history.empty:
        return {"error": f"No data found for ticker {ticker}"}

    # Price metrics
    current_price = history['Close'].iloc[-1]
    week_52_high = history['High'].tail(252).max()
    week_52_low = history['Low'].tail(252).min()

    # 6-month metrics
    six_months_ago_price = history['Close'].tail(126).iloc[0] if len(history) >= 126 else history['Close'].iloc[0]
    six_month_return = ((current_price - six_months_ago_price) / six_months_ago_price) * 100

    # Position in range
    range_position = ((current_price - week_52_low) / (week_52_high - week_52_low)) * 100
    pct_from_high = ((current_price - week_52_high) / week_52_high) * 100
    pct_from_low = ((current_price - week_52_low) / week_52_low) * 100

    # Determine price level
    if range_position > 90 or pct_from_high > -10:
        price_level = "HIGH"
    elif range_position < 40 or pct_from_low < 70:
        price_level = "LOW"
    else:
        price_level = "MEDIUM"

    # Volume
    avg_volume = history['Volume'].tail(20).mean()
    current_volume = history['Volume'].iloc[-1]
    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0

    data = {
        "ticker": ticker.upper(),
        "company_name": info.get('longName', ticker),
        "sector": info.get('sector', 'N/A'),
        "industry": info.get('industry', 'N/A'),
        "current_price": round(current_price, 2),
        "week_52_high": round(week_52_high, 2),
        "week_52_low": round(week_52_low, 2),
        "range_position_pct": round(range_position, 1),
        "pct_from_high": round(pct_from_high, 1),
        "pct_from_low": round(pct_from_low, 1),
        "six_month_return": round(six_month_return, 1),
        "price_level": price_level,
        "pe_trailing": round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else None,
        "pe_forward": round(info.get('forwardPE', 0), 2) if info.get('forwardPE') else None,
        "ps_ratio": round(info.get('priceToSalesTrailing12Months', 0), 2) if info.get('priceToSalesTrailing12Months') else None,
        "pb_ratio": round(info.get('priceToBook', 0), 2) if info.get('priceToBook') else None,
        "market_cap": info.get('marketCap', None),
        "avg_volume_20d": int(avg_volume),
        "current_volume": int(current_volume),
        "volume_ratio": round(volume_ratio, 2),
        "currency": info.get('currency', 'USD'),
        "website": info.get('website', 'N/A'),
        "beta": info.get('beta', None),
    }

    return data


def format_market_cap(market_cap):
    """Format market cap in readable format"""
    if market_cap:
        if market_cap >= 1e12:
            return f"${market_cap/1e12:.2f}T"
        elif market_cap >= 1e9:
            return f"${market_cap/1e9:.2f}B"
        elif market_cap >= 1e6:
            return f"${market_cap/1e6:.2f}M"
    return "N/A"


def generate_report_content(data: Dict[str, Any]) -> str:
    """Generate full fundamental analysis report content"""

    today = datetime.now().strftime("%Y-%m-%d")
    ticker = data['ticker']
    company_name = data['company_name']
    current_price = data['current_price']
    currency = data['currency']

    content = f"""# {company_name} Fundamental Analysis

**Ticker**: {ticker} | **Exchange**: N/A | **Date**: {today} | **Current Price**: ${current_price}

**Disclaimer**: This report is for educational and research purposes only. It provides data summaries and analytical observations, not investment recommendations. All investment decisions should be made after consulting with a licensed financial advisor and conducting your own due diligence.

---

## Table of Contents

**Executive Summary**

1. Price Level Assessment: {data['price_level']}
2. Moat Analysis: Total Score [Requires Manual Analysis]
3. Business Quality Metrics
4. Management Quality Assessment
5. Primary Issue Identification
6. Management's Ability to Solve
7. Risks and Catalysts
8. Competitive Position Analysis
9. Research Summary
10. Research Conclusion

**Appendix: Data Sources and Methodology**

---

## Executive Summary

{company_name} trades at {data['price_level']} levels ({data['range_position_pct']}% of 52-week range).

**Current Market Data:**
- Current Price: {currency} ${current_price}
- 52-Week Range: ${data['week_52_low']} - ${data['week_52_high']}
- 6-Month Return: {data['six_month_return']:+.1f}%
- Market Cap: {format_market_cap(data['market_cap'])}

**Note**: Complete fundamental analysis includes comprehensive research on competitive moat, management quality, strategic issues, and scenario analysis.

---

## 1. Price Level Assessment: {data['price_level']}

### Current Position
- **Current Price**: {currency} ${current_price}
- **52-Week Range**: ${data['week_52_low']} - ${data['week_52_high']}
- **Position in Range**: {data['range_position_pct']:.1f}% ({data['pct_from_high']:+.1f}% from high, {data['pct_from_low']:+.1f}% from low)
- **Trading Volume**: {data['current_volume']:,} ({data['volume_ratio']:.2f}x average)

### Valuation Metrics
| Metric | Current | Assessment |
|--------|---------|------------|
| P/E (Trailing) | {data['pe_trailing'] if data['pe_trailing'] else 'N/A'} | Requires industry comparison |
| P/E (Forward) | {data['pe_forward'] if data['pe_forward'] else 'N/A'} | Requires analysis |
| P/S | {data['ps_ratio'] if data['ps_ratio'] else 'N/A'} | Requires sector context |
| P/B | {data['pb_ratio'] if data['pb_ratio'] else 'N/A'} | Requires business model analysis |

### Recent Price Trend Analysis (Past 6 Months)

**6-Month Performance**:
- 6-month change: **{data['six_month_return']:+.1f}%**

**Analysis Required**:
- Identify key events that moved the stock
- Analyze earnings reports and guidance changes
- Review strategic announcements and competitive dynamics
- Compare performance to sector/market

---

## 2. Moat Analysis: Total Score [Requires Manual Analysis]

**This section requires manual research and analysis.**

Evaluate competitive advantages across six dimensions:

| Moat Type | Score | Evidence |
|-----------|-------|----------|
| Brand Power | [0-3] | Research required: pricing power, customer loyalty |
| Network Effects | [0-3] | Research required: product improves with more users? |
| Cost Advantages | [0-3] | Research required: scale benefits, proprietary processes |
| Switching Costs | [0-3] | Research required: customer lock-in, integration depth |
| Regulatory/IP | [0-3] | Research required: patents, licenses, barriers |
| Data Moat | [0-3] | Research required: proprietary data that compounds |

**Analysis Requirements**:
1. Research company's competitive positioning
2. Score each moat type 0-3 (0=none, 1=weak, 2=moderate, 3=strong)
3. Provide specific evidence for each score
4. Calculate total moat score out of 18

---

## 3. Business Quality Metrics

**This section requires financial statement analysis.**

### Data Needed (from SEC filings):
- Gross Margin, Operating Margin, FCF Margin, ROE
- Revenue Growth (TTM and historical trends)
- Operating Leverage trends
- Capital Efficiency (Asset Turns, CapEx/Revenue)
- Cash Conversion metrics

**Available Basic Data**:
- Sector: {data['sector']}
- Industry: {data['industry']}
- Market Cap: {format_market_cap(data['market_cap'])}
- Beta: {data['beta'] if data['beta'] else 'N/A'}

---

## 4. Management Quality Assessment

**Research Required**:
- Capital allocation track record (M&A, buybacks, dividends, R&D)
- Execution capability (strategy implementation, past transitions)
- Strategic clarity (coherent vision, stakeholder communication)
- Insider ownership and alignment

---

## 5. Primary Issue Identification

**Current Research Required**:
- Revenue or growth challenges
- Margin pressures or cost issues
- Operational or strategic problems
- Financial concerns (debt, cash flow)
- External risks (regulatory, competitive, macro)

**Research Sources**:
- Latest earnings call transcripts
- Recent 10-K and 10-Q filings
- News and analyst reports
- Industry competitive analysis

---

## 6. Management's Ability to Solve

**Assessment Framework**: CAN SOLVE / UNCERTAIN / CANNOT SOLVE

Evaluation Criteria:
- Historical track record navigating challenges
- Current solution path and action plan
- Resource allocation and execution speed
- Wildcards and unknown factors

---

## 7. Risks and Catalysts

**Analysis Required**:

**Key Risks**:
- Company-specific execution risks
- Competitive and industry risks
- Macroeconomic and regulatory risks
- Valuation risk

**Positive Catalysts**:
- Near-term catalysts (0-6 months)
- Medium-term drivers (6-18 months)
- Long-term growth vectors (18+ months)

---

## 8. Competitive Position Analysis

**Industry Research Required**:
- Primary competitors identification
- Market share and positioning
- Competitive advantages vs disadvantages
- Industry dynamics and trends

---

## 9. Research Summary

**Scenario Analysis Framework**:

| Scenario | Probability | Price Target | Return | Key Assumptions |
|----------|-------------|--------------|--------|-----------------|
| Bull Case | XX% | $XXX | +XX% | [Requires analysis] |
| Base Case | XX% | $XXX | +XX% | [Requires analysis] |
| Bear Case | XX% | $XXX | -XX% | [Requires analysis] |

**Key Metrics to Monitor**:
1. [Define based on business model]
2. [Define based on growth drivers]
3. [Define based on risk factors]
4. [Define based on competitive position]
5. [Define based on financial health]

---

## 10. Research Conclusion

**Synthesis Requirements:**
- Investment perspective (quality/value/growth assessment)
- Alignment with different investor philosophies
- Key questions requiring further research
- Overall recommendation framework

---

## Appendix: Data Sources and Methodology

### Data Sources
- Price data: Yahoo Finance (fetched {today})
- Financial statements: [Requires manual SEC filing review]
- Market data: Public market sources
- Competitive data: [Requires industry research]

### Methodology Notes
- See `fundamental_analysis_skill/references/analysis-framework.md` for complete methodology

### Analysis Workflow

1. **Research Phase**:
   - Read latest 10-K, 10-Q filings
   - Review earnings call transcripts (last 4 quarters)
   - Analyze competitive landscape
   - Identify key strategic issues

2. **Analysis Phase**:
   - Complete moat scorecard with evidence
   - Calculate business quality metrics from financials
   - Assess management track record
   - Build scenario models with probabilities

3. **Validation Phase**:
   - Run: `python scripts/validate_report_data.py {ticker} --report <this_file>`
   - Verify all numeric data matches sources
   - Cross-check valuation calculations

4. **Finalization**:
   - Convert to HTML: `python ../utils/md_to_html.py <this_file>`
   - Create highlights summary (2-4 pages)
   - Archive with proper naming: `{ticker}-YYYY-MM-DD.md`

---

**Report Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

*Complete fundamental analysis requires comprehensive research on competitive moat, management quality, strategic issues, and scenario modeling.*
"""

    return content


def main():
    parser = argparse.ArgumentParser(
        description='Generate comprehensive fundamental analysis report (preliminary)'
    )
    parser.add_argument(
        'ticker',
        type=str,
        help='Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for report (default: analyses/TICKER/)'
    )

    args = parser.parse_args()
    ticker = args.ticker.upper()

    # Fetch data
    data = fetch_comprehensive_data(ticker)

    if 'error' in data:
        print(f"Error: {data['error']}")
        sys.exit(1)

    # Generate report content
    content = generate_report_content(data)

    # Determine output path
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        script_dir = Path(__file__).parent.parent
        output_dir = script_dir / 'analyses' / ticker

    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    output_file = output_dir / f"{ticker}-{timestamp}.md"

    # Write report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n{'='*80}")
    print(f"FUNDAMENTAL ANALYSIS REPORT STRUCTURE GENERATED")
    print(f"{'='*80}")
    print(f"\nTicker: {ticker}")
    print(f"Company: {data['company_name']}")
    print(f"Output: {output_file}")
    print(f"\n{'='*80}")
    print(f"NEXT: Complete comprehensive research for all sections")
    print(f"{'='*80}")
    print(f"\nReport includes:")
    print(f"  [OK] Price and valuation data from Yahoo Finance")
    print(f"  [OK] Report structure with all required sections")
    print(f"  [!]  Research required for complete analysis")
    print(f"\nNext steps:")
    print(f"  1. Complete comprehensive research:")
    print(f"     - Moat Analysis with scores and evidence")
    print(f"     - Business Quality Metrics from financials")
    print(f"     - Management Assessment with track record")
    print(f"     - Issue Identification with current events")
    print(f"     - Scenario analysis with price targets")
    print(f"  2. Validate: python scripts/validate_report_data.py {ticker} --report {output_file}")
    print(f"  3. Convert to HTML: python ../utils/md_to_html.py {output_file}")
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
