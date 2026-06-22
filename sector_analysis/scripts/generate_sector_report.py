"""
Generate Sector Rotation Report

Creates markdown and HTML reports for sector analysis.
"""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fetch_sector_data import fetch_sector_etfs, SECTOR_ETFS
from calculate_sector_metrics import (
    calculate_relative_strength,
    calculate_momentum,
    rank_sectors,
    identify_rotation_quadrants
)


def generate_markdown_report(rankings_df, quadrants, full_df):
    """
    Generate comprehensive sector rotation markdown report

    Parameters
    ----------
    rankings_df : pd.DataFrame
        Ranked sector data
    quadrants : dict
        Rotation quadrant assignments
    full_df : pd.DataFrame
        Full historical data

    Returns
    -------
    str
        Markdown formatted report
    """
    md = []

    # Header
    md.append("# Sector Rotation Analysis")
    md.append("")
    md.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md.append(f"**Analysis Date:** {rankings_df.iloc[0]['date'].strftime('%Y-%m-%d')}")
    md.append(f"**Benchmark:** S&P 500 (SPY)")
    md.append("")
    md.append("> **Purpose:** Track institutional money flow across market sectors")
    md.append("")
    md.append("---")
    md.append("")

    # Executive Summary
    md.append("## Executive Summary")
    md.append("")

    top_3 = rankings_df.head(3)
    bottom_3 = rankings_df.tail(3)

    md.append(f"**Top 3 Sectors (Overweight):**")
    for _, row in top_3.iterrows():
        md.append(f"- {row['sector_name']} ({row['ticker']}): Score {row['composite_score']:.1f}")
    md.append("")

    md.append(f"**Bottom 3 Sectors (Avoid):**")
    for _, row in bottom_3.iterrows():
        md.append(f"- {row['sector_name']} ({row['ticker']}): Score {row['composite_score']:.1f}")
    md.append("")

    # Rotation status
    leading_count = len(quadrants['leading'])
    if leading_count >= 4:
        rotation_status = "STRONG MARKET (Many leaders)"
    elif leading_count >= 2:
        rotation_status = "HEALTHY ROTATION (Moderate leadership)"
    else:
        rotation_status = "DEFENSIVE MARKET (Few leaders)"

    md.append(f"**Market Rotation Status:** {rotation_status}")
    md.append("")
    md.append("---")
    md.append("")

    # Sector Rankings Table
    md.append("## Sector Rankings")
    md.append("")
    md.append("| Rank | Sector | Ticker | Score | RS (20d) | RS (60d) | Momentum | Signal |")
    md.append("|------|--------|--------|-------|----------|----------|----------|--------|")

    for _, row in rankings_df.iterrows():
        rank = row['rank']
        sector = row['sector_name']
        ticker = row['ticker']
        score = row['composite_score']
        rs_20 = row['rs_20d'] * 100
        rs_60 = row['rs_60d'] * 100
        momentum = row['momentum_score'] * 100
        signal = row['signal']

        md.append(f"| {rank} | {sector} | {ticker} | {score:.1f} | {rs_20:+.2f}% | {rs_60:+.2f}% | {momentum:+.2f}% | {signal} |")

    md.append("")
    md.append("---")
    md.append("")

    # Rotation Map
    md.append("## Rotation Map (Quadrant Analysis)")
    md.append("")
    md.append("### 🚀 Leading (Strong + Accelerating)")
    if quadrants['leading']:
        for ticker in quadrants['leading']:
            sector_name = SECTOR_ETFS.get(ticker, ticker)
            md.append(f"- **{ticker}** - {sector_name}")
    else:
        md.append("- *None*")
    md.append("")

    md.append("### ⚠️ Weakening (Strong + Decelerating)")
    if quadrants['weakening']:
        for ticker in quadrants['weakening']:
            sector_name = SECTOR_ETFS.get(ticker, ticker)
            md.append(f"- **{ticker}** - {sector_name}")
    else:
        md.append("- *None*")
    md.append("")

    md.append("### 👀 Improving (Weak + Accelerating)")
    if quadrants['improving']:
        for ticker in quadrants['improving']:
            sector_name = SECTOR_ETFS.get(ticker, ticker)
            md.append(f"- **{ticker}** - {sector_name}")
    else:
        md.append("- *None*")
    md.append("")

    md.append("### ❌ Lagging (Weak + Decelerating)")
    if quadrants['lagging']:
        for ticker in quadrants['lagging']:
            sector_name = SECTOR_ETFS.get(ticker, ticker)
            md.append(f"- **{ticker}** - {sector_name}")
    else:
        md.append("- *None*")
    md.append("")
    md.append("---")
    md.append("")

    # Detailed Sector Analysis
    md.append("## Detailed Sector Analysis")
    md.append("")

    for _, row in rankings_df.iterrows():
        rank = row['rank']
        ticker = row['ticker']
        sector = row['sector_name']
        score = row['composite_score']
        rs_20 = row['rs_20d'] * 100
        rs_60 = row['rs_60d'] * 100
        momentum = row['momentum_score'] * 100
        signal = row['signal']
        price = row['adjusted_close']

        md.append(f"### {rank}. {sector} ({ticker}) - {signal}")
        md.append("")
        md.append(f"- **Composite Score:** {score:.1f}")
        md.append(f"- **Current Price:** ${price:.2f}")
        md.append(f"- **Relative Strength (20-day):** {rs_20:+.2f}%")
        md.append(f"- **Relative Strength (60-day):** {rs_60:+.2f}%")
        md.append(f"- **Momentum (3M+6M):** {momentum:+.2f}%")
        md.append("")

        # Signal interpretation
        if '🚀' in signal:
            md.append("**Recommendation:** OVERWEIGHT - Strong outperformance on multiple timeframes")
        elif '✅' in signal:
            md.append("**Recommendation:** OVERWEIGHT - Consistent outperformance")
        elif '👀' in signal:
            md.append("**Recommendation:** WATCH - Early rotation signal, monitor for confirmation")
        elif '⚠️' in signal:
            md.append("**Recommendation:** REDUCE - Momentum fading, consider taking profits")
        else:
            md.append("**Recommendation:** AVOID - Underperforming, capital better deployed elsewhere")

        md.append("")

    md.append("---")
    md.append("")

    # Portfolio Recommendation
    md.append("## Portfolio Recommendation")
    md.append("")

    top_5 = rankings_df.head(5)
    total_score = top_5['composite_score'].sum()

    md.append("### Suggested Allocation (Top 5 Sectors)")
    md.append("")

    for _, row in top_5.iterrows():
        ticker = row['ticker']
        sector = row['sector_name']
        score = row['composite_score']
        allocation = (score / total_score) * 100

        md.append(f"- **{sector} ({ticker}):** {allocation:.1f}%")

    md.append("")

    md.append("### Sectors to Avoid (Bottom 3)")
    md.append("")

    bottom_3 = rankings_df.tail(3)
    for _, row in bottom_3.iterrows():
        ticker = row['ticker']
        sector = row['sector_name']
        md.append(f"- {sector} ({ticker})")

    md.append("")
    md.append("---")
    md.append("")

    # Methodology
    md.append("## Methodology")
    md.append("")
    md.append("**Composite Score Components:**")
    md.append("")
    md.append("- 25% - Relative Strength (20-day) vs SPY")
    md.append("- 25% - Momentum Score (3M + 6M returns)")
    md.append("- 25% - Relative Strength (60-day) vs SPY")
    md.append("- 25% - Recent Performance (20-day return)")
    md.append("")
    md.append("**Signal Categories:**")
    md.append("")
    md.append("- 🚀 **STRONG BUY:** RS 20d > +2%, RS 60d > +3%, Momentum > +10%")
    md.append("- ✅ **BUY:** RS 20d > +1%, RS 60d > +1%")
    md.append("- 👀 **WATCH:** RS 20d positive but RS 60d negative (early rotation)")
    md.append("- ⚠️ **WEAKENING:** RS 20d negative but RS 60d still positive (fading strength)")
    md.append("- ❌ **AVOID:** Both RS 20d and RS 60d negative")
    md.append("")
    md.append("---")
    md.append("")

    # Disclaimer
    md.append("## Important Disclaimer")
    md.append("")
    md.append("**RESEARCH TOOL - NOT INVESTMENT ADVICE**")
    md.append("")
    md.append("This sector rotation analysis is provided as a research tool for tracking capital flows across market sectors. ")
    md.append("It is for educational purposes only and does not constitute investment advice or personalized recommendations.")
    md.append("")
    md.append("**Key Points:**")
    md.append("- This analysis tracks where capital is currently moving, not where it will move")
    md.append("- Past sector performance does not guarantee future results")
    md.append("- Sector rotation strategies carry risk of loss")
    md.append("- Always consult with licensed financial professionals before making investment decisions")
    md.append("")
    md.append(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return "\n".join(md)


def save_report(content, output_dir="analyses"):
    """
    Save markdown report to file

    Returns
    -------
    str
        Path to saved file
    """
    output_path = Path(__file__).parent.parent / output_dir
    output_path.mkdir(exist_ok=True, parents=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"Sector_Rotation_Analysis_{timestamp}.md"
    filepath = output_path / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n[OK] Report saved to: {filepath}")
    return str(filepath)


def main():
    """Main function to generate sector analysis"""
    try:
        print(f"\n{'='*60}")
        print("SECTOR ROTATION ANALYSIS")
        print(f"{'='*60}")

        # Step 1: Fetch sector data
        df = fetch_sector_etfs(lookback_days=365)

        # Step 2: Calculate metrics
        df = calculate_relative_strength(df)
        df = calculate_momentum(df)

        # Step 3: Rank sectors
        rankings = rank_sectors(df)

        # Step 4: Identify rotation quadrants
        quadrants = identify_rotation_quadrants(df)

        # Step 5: Generate report
        print(f"\n{'='*60}")
        print("GENERATING REPORT")
        print(f"{'='*60}")

        md_report = generate_markdown_report(rankings, quadrants, df)
        md_path = save_report(md_report)

        # Step 6: Generate HTML
        print(f"\n{'='*60}")
        print("GENERATING HTML")
        print(f"{'='*60}")
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'utils'))
            from md_to_html import convert_md_to_html

            html_path = md_path.replace('.md', '.html')
            convert_md_to_html(md_path, html_path)
            print(f"[OK] HTML saved to: {html_path}")
        except Exception as e:
            print(f"[WARNING] HTML generation failed: {str(e)}")

        print(f"\n{'='*60}")
        print("[OK] SECTOR ANALYSIS COMPLETE!")
        print(f"{'='*60}")

        # Print summary
        print(f"\nTOP 3 SECTORS:")
        for _, row in rankings.head(3).iterrows():
            print(f"  {row['rank']}. {row['sector_name']} ({row['ticker']}): {row['signal']}")

        print(f"\nBOTTOM 3 SECTORS:")
        for _, row in rankings.tail(3).iterrows():
            print(f"  {row['rank']}. {row['sector_name']} ({row['ticker']}): {row['signal']}")

        return md_path

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
