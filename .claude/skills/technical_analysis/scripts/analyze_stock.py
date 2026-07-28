"""
Complete Stock Technical Analysis Script

Fetches fresh Yahoo Finance data, calculates technical factors, and generates comprehensive analysis reports in markdown and HTML formats.

Usage:
    python analyze_stock.py TICKER [--days DAYS] [--lookback DAYS]

Example:
    python analyze_stock.py AAPL
    python analyze_stock.py TSLA --days 60 --lookback 365
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd

# Import our modules
from fetch_and_analyze import fetch_stock_data, calculate_all_factors, get_recent_data
from trend_analyzer import TrendAnalyzer
from plot_comprehensive_analysis import create_comprehensive_chart

# Add lib directory to path for translations
sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))
from translations import get_text


def generate_markdown_report(df: pd.DataFrame, ticker: str, analyzer: TrendAnalyzer, lang: str = 'en') -> str:
    """
    Generate a comprehensive markdown report.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with recent data and technical factors
    ticker : str
        Stock ticker
    analyzer : TrendAnalyzer
        TrendAnalyzer instance
    lang : str
        Language code ('en' or 'zh'), default 'en'

    Returns
    -------
    str
        Markdown formatted report
    """
    # Helper function for translation
    def t(key):
        return get_text(key, lang)
    # Get analyses
    trend = analyzer.analyze_trend_direction()
    vol = analyzer.analyze_volatility()
    volume = analyzer.analyze_volume()
    levels = analyzer.identify_key_levels()
    signals = analyzer.generate_trading_signals()

    latest = df.iloc[-1]

    # Build markdown
    md = []
    md.append(f"# {t('technical_analysis')}: {ticker.upper()}")
    md.append("")
    md.append(f"**{t('generated_on')}:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md.append(f"**{t('ticker')}:** {ticker.upper()}")
    md.append(f"**{t('current_price')}:** ${latest['adjusted_close']:.2f}")
    md.append("")
    md.append(f"> **{t('disclaimer')}**")
    md.append("")

    md.append("---")
    md.append("")

    # Executive Summary
    md.append(f"## {t('executive_summary')}")
    md.append("")
    md.append(f"**{t('trend_direction')}:** {trend['direction']} ({t('strength')}: {trend['strength']}/10)")
    md.append(f"**{t('primary_pattern')}:** {signals[0]['action']} ({signals[0]['confidence']} {t('confidence')})")
    md.append(f"**{t('volatility_level')}:** {vol['level']}")
    md.append(f"**{t('volume_level')}:** {volume['level']}")
    md.append("")

    # Trend Analysis
    md.append("---")
    md.append("")
    md.append(f"## 1. {t('trend_analysis')}")
    md.append("")
    md.append(f"### {t('overall_direction')}: **{trend['direction']}**")
    md.append(f"- **{t('strength')}:** {trend['strength']}/10")
    md.append(f"- **{t('technical_score')}:** {trend['score']:+d}")
    md.append(f"- **{t('price_trend')}:** {trend['price_trend']}")
    md.append(f"- **{t('volume_trend')}:** {trend['volume_trend']}")
    md.append("")

    if trend['bullish_signals']:
        md.append(f"### {t('bullish_signals')}")
        for signal in trend['bullish_signals']:
            md.append(f"- [+] {signal}")
        md.append("")

    if trend['bearish_signals']:
        md.append(f"### {t('bearish_signals')}")
        for signal in trend['bearish_signals']:
            md.append(f"- [WARNING] {signal}")
        md.append("")

    # Key Indicators
    md.append("---")
    md.append("")
    md.append(f"## 2. {t('key_indicators')}")
    md.append("")

    # Table of indicators
    md.append(f"| {t('indicator')} | {t('value')} | {t('signal')} |")
    md.append("|-----------|-------|--------|")

    # RSI
    if 'rsi_14' in df.columns and pd.notna(latest['rsi_14']):
        rsi = latest['rsi_14']
        rsi_signal = f"[GREEN] {t('oversold').upper()}" if rsi < 30 else f"[RED] {t('overbought').upper()}" if rsi > 70 else f"[NEUTRAL] {t('neutral').upper()}"
        md.append(f"| {t('rsi')} | {rsi:.2f} | {rsi_signal} |")

    # MACD
    if 'macd_hist_12_26_9' in df.columns and pd.notna(latest['macd_hist_12_26_9']):
        macd = latest['macd_hist_12_26_9']
        macd_signal = f"[GREEN] {t('bullish').upper()}" if macd > 0 else f"[RED] {t('bearish').upper()}"
        md.append(f"| {t('macd_histogram')} | {macd:+.4f} | {macd_signal} |")

    # ATR - Average True Range (volatility measure)
    if 'atr_14' in df.columns and pd.notna(latest['atr_14']):
        atr_val = latest['atr_14']
        atr_pct = (atr_val / latest['adjusted_close']) * 100
        atr_signal = f"[RED] {t('high_volatility').upper()}" if atr_pct > 5 else f"[NEUTRAL] {t('normal').upper()}" if atr_pct > 2 else f"[GREEN] {t('low_volatility').upper()}"
        md.append(f"| {t('atr')} | ${atr_val:.2f} ({atr_pct:.1f}%) | {atr_signal} |")

    # ADX
    if 'adx_14' in df.columns and pd.notna(latest['adx_14']):
        adx = latest['adx_14']
        adx_signal = f"[GREEN] {t('strong_trend').upper()}" if adx > 25 else f"[NEUTRAL] {t('weak_trend').upper()}"
        md.append(f"| {t('adx')} | {adx:.2f} | {adx_signal} |")

    # Distance from SMAs
    if 'dist_sma_200' in df.columns and pd.notna(latest['dist_sma_200']):
        dist = latest['dist_sma_200'] * 100
        dist_signal = f"[GREEN] {t('above').upper()}" if dist > 0 else f"[RED] {t('below').upper()}"
        md.append(f"| {t('price_vs_sma200')} | {dist:+.2f}% | {dist_signal} |")

    # Bollinger %B
    if 'bb_percent_b' in df.columns and pd.notna(latest['bb_percent_b']):
        pct_b = latest['bb_percent_b']
        bb_signal = f"[RED] {t('below_bands').upper()}" if pct_b < 0 else f"[RED] {t('above_bands').upper()}" if pct_b > 1 else f"[NEUTRAL] {t('within_bands').upper()}"
        md.append(f"| {t('bollinger_b')} | {pct_b:.2f} | {bb_signal} |")

    md.append("")

    # Volatility Analysis
    md.append("---")
    md.append("")
    md.append(f"## 3. {t('volatility_analysis')}")
    md.append("")
    md.append(f"**{t('level')}:** {vol['level']}")
    if vol['annualized_pct']:
        md.append(f"- {t('annualized_volatility')}: {vol['annualized_pct']:.2f}%")
    if vol['percentile']:
        md.append(f"- {t('historical_percentile')}: {vol['percentile']:.1f}{t('percentile')}")
    if vol['atr']:
        md.append(f"- **{t('atr')}:** ${vol['atr']:.2f}")
        if vol['atr_pct']:
            md.append(f"  - {t('as_percent_of_price')}: {vol['atr_pct']:.2f}% ({t('atr_description')})")
    yes_text = t('yes').upper()
    no_text = t('no').upper()
    md.append(f"- {t('bollinger_squeeze')}: **{yes_text if vol['squeeze'] else no_text}**")
    md.append("")

    # Volume Analysis
    md.append("---")
    md.append("")
    md.append(f"## 4. {t('volume_analysis')}")
    md.append("")
    if volume['relative']:
        md.append(f"**{t('relative_volume')}:** {volume['relative']:.2f}x ({volume['level']})")
    md.append(f"**{t('volume_trend')}:** {volume['trend']}")
    md.append("")
    if volume['signals']:
        md.append("**Observations:**")
        for sig in volume['signals']:
            md.append(f"- {sig}")
        md.append("")

    # Key Levels
    md.append("---")
    md.append("")
    md.append(f"## 5. {t('support_resistance')}")
    md.append("")
    md.append(f"**{t('current_price')}:** ${levels['current_price']:.2f}")
    md.append("")

    if levels['resistance']:
        md.append(f"### {t('resistance_levels')}")
        md.append(f"| {t('level')} | {t('type')} | {t('distance')} |")
        md.append("|-------|------|----------|")
        for r in levels['resistance'][:5]:
            md.append(f"| ${r['level']:.2f} | {r['type']} | +{r['distance_pct']:.2f}% |")
        md.append("")

    if levels['support']:
        md.append(f"### {t('support_levels')}")
        md.append(f"| {t('level')} | {t('type')} | {t('distance')} |")
        md.append("|-------|------|----------|")
        for s in levels['support'][:5]:
            md.append(f"| ${s['level']:.2f} | {s['type']} | -{s['distance_pct']:.2f}% |")
        md.append("")

    # Trading Zones Analysis
    md.append(f"### {t('trading_zones')}")
    md.append("")

    # Calculate zones based on detected support/resistance levels
    current = levels['current_price']

    # Find support and resistance levels (only swing/period levels, not SMAs)
    support_levels_list = [s['level'] for s in levels['support'][:5]
                          if 'SMA' not in s.get('type', '')] if levels['support'] else []
    resistance_levels_list = [r['level'] for r in levels['resistance'][:5]
                             if 'SMA' not in r.get('type', '')] if levels['resistance'] else []

    # Create support zone (2 lowest support levels)
    if support_levels_list:
        if len(support_levels_list) >= 2:
            support_zone_low = min(support_levels_list[:2])
            support_zone_high = max(support_levels_list[:2])
            md.append(f"**{t('support_zone')}:** {t('roughly')} ${support_zone_low:.0f}-${support_zone_high:.0f}")
        else:
            # Only one support level, create a range
            support_zone_low = support_levels_list[0]
            support_zone_high = support_zone_low * 1.025
            md.append(f"**{t('support_zone')}:** {t('roughly')} ${support_zone_low:.0f}-${support_zone_high:.0f}")

    # Near-term pivot (around current price, +/- 2%)
    pivot_low = current * 0.985
    pivot_high = current * 1.015
    md.append(f"**{t('near_term_pivot')}:** {t('around')} ${pivot_low:.0f}-${pivot_high:.0f}")

    # Resistance zones
    if resistance_levels_list:
        # First resistance zone (nearest resistance levels, within 10% above)
        r1_list = [r for r in resistance_levels_list if current < r < current * 1.10]
        if r1_list:
            r1_low = min(r1_list) * 0.975
            r1_high = min(r1_list)
            md.append(f"**{t('resistance_zone')}:** {t('roughly')} ${r1_low:.0f}-${r1_high:.0f}")

        # Higher resistance zone (above 5%, from earlier period)
        r2_list = [r for r in resistance_levels_list if r > current * 1.05]
        if r2_list:
            # Take the first higher resistance level
            higher_r = sorted(r2_list)[0] if len(r2_list) >= 1 else r2_list[0]
            r2_low = higher_r * 0.98
            r2_high = higher_r * 1.01
            md.append(f"**{t('higher_resistance')}:** {t('around')} ${r2_low:.0f}-${r2_high:.0f}")

    md.append("")

    # Technical Patterns & Setups
    md.append("---")
    md.append("")
    md.append("## 6. Technical Patterns & Setups")
    md.append("")

    for i, signal in enumerate(signals, 1):
        # Determine emoji based on pattern type
        if 'BULLISH' in signal['action'] or 'OVERSOLD' in signal['action']:
            pattern_emoji = "[GREEN]"
        elif 'BEARISH' in signal['action'] or 'OVERBOUGHT' in signal['action']:
            pattern_emoji = "[RED]"
        else:
            pattern_emoji = "[NEUTRAL]"

        md.append(f"### Pattern #{i}: {pattern_emoji} **{signal['action']}**")
        md.append(f"**Confidence Level:** {signal['confidence']}")
        md.append(f"**Observation:** {signal['reason']}")
        if signal['details']:
            md.append("")
            md.append("**Technical Details:**")
            for detail in signal['details']:
                md.append(f"- {detail}")
        md.append("")

    # Recent Price Action
    md.append("---")
    md.append("")
    md.append("## 7. Recent Price Action (Last 10 Days)")
    md.append("")

    recent_10 = df.tail(10)
    md.append("| Date | Close | Volume | RSI | MACD |")
    md.append("|------|-------|--------|-----|------|")

    for _, row in recent_10.iterrows():
        date_str = row['date'].strftime('%Y-%m-%d')
        close = row['adjusted_close']
        volume = row['volume']
        rsi = row.get('rsi_14', float('nan'))
        macd = row.get('macd_hist_12_26_9', float('nan'))

        rsi_str = f"{rsi:.1f}" if pd.notna(rsi) else "N/A"
        macd_str = f"{macd:+.4f}" if pd.notna(macd) else "N/A"

        md.append(f"| {date_str} | ${close:.2f} | {volume:,.0f} | {rsi_str} | {macd_str} |")

    md.append("")

    # Disclaimer
    md.append("---")
    md.append("")
    md.append(f"## {t('disclaimer.title')}")
    md.append("")
    md.append(f"**{t('disclaimer.subtitle')}**")
    md.append("")
    md.append(t('disclaimer.intro1'))
    md.append(t('disclaimer.intro2'))
    md.append("")
    md.append(f"**{t('disclaimer.not.title')}**")
    md.append(f"- {t('disclaimer.not.1')}")
    md.append(f"- {t('disclaimer.not.2')}")
    md.append(f"- {t('disclaimer.not.3')}")
    md.append(f"- {t('disclaimer.not.4')}")
    md.append("")
    md.append(f"**{t('disclaimer.notes.title')}**")
    md.append(f"- {t('disclaimer.notes.1')}")
    md.append(f"- {t('disclaimer.notes.2')}")
    md.append(f"- {t('disclaimer.notes.3')}")
    md.append(f"- {t('disclaimer.notes.4')}")
    md.append("")
    md.append(t('disclaimer.responsibility'))
    md.append("")
    md.append(f"**{t('disclaimer.generated')}** {t('disclaimer.tool')}")
    md.append(f"**{t('disclaimer.timestamp')}** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return "\n".join(md)


def save_report(content: str, ticker: str, output_dir: str = "analyses") -> str:
    """
    Save report to markdown file.

    Parameters
    ----------
    content : str
        Report content
    ticker : str
        Stock ticker
    output_dir : str
        Output directory

    Returns
    -------
    str
        Path to saved file
    """
    output_path = Path(__file__).parent.parent / output_dir
    output_path.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{ticker.upper()}_Technical_Analysis_{timestamp}.md"
    filepath = output_path / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n[OK] Report saved to: {filepath}")
    return str(filepath)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Complete stock technical analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_stock.py AAPL
  python analyze_stock.py TSLA --days 60
  python analyze_stock.py NVDA --lookback 730
        """
    )
    parser.add_argument('ticker', type=str, help='Stock ticker symbol')
    parser.add_argument('--days', type=int, default=30, help='Number of recent days to analyze (default: 30)')
    parser.add_argument('--lookback', type=int, default=500, help='Days of historical data (default: 500, ensures SMA200 coverage)')
    parser.add_argument('--lang', type=str, default='en', choices=['en', 'zh'], help='Report language: en (English) or zh (Chinese), default: en')

    args = parser.parse_args()

    try:
        print(f"\n{'='*60}")
        print(f"TECHNICAL ANALYSIS: {args.ticker.upper()}")
        print(f"{'='*60}")

        # Calculate required lookback to ensure MAs are valid from start
        # MA20 is the longest short-term MA, so we need at least 20 extra days
        max_ma_period = 20
        required_lookback = args.days + max_ma_period + 10  # Add 10 buffer days
        actual_lookback = max(args.lookback, required_lookback)

        if actual_lookback > args.lookback:
            print(f"[INFO] Fetching {actual_lookback} days (instead of {args.lookback}) to ensure MAs are complete")

        # Step 1: Fetch data
        df = fetch_stock_data(args.ticker, lookback_days=actual_lookback)

        # Step 2: Calculate all technical factors
        df_with_factors = calculate_all_factors(df)

        # Step 3: Get recent data
        df_recent = get_recent_data(df_with_factors, days=args.days)

        # Step 4: Analyze trends
        print(f"\n{'='*60}")
        print("Analyzing Trends...")
        print(f"{'='*60}")
        analyzer = TrendAnalyzer(df_recent)

        # Generate text report
        text_report = analyzer.generate_report()
        print("\n" + text_report)

        # Step 5: Generate markdown report
        print(f"\n{'='*60}")
        print("Generating Markdown Report...")
        print(f"{'='*60}")
        md_report = generate_markdown_report(df_recent, args.ticker, analyzer, lang=args.lang)
        md_path = save_report(md_report, args.ticker)

        # Step 6: Generate comprehensive chart
        print(f"\n{'='*60}")
        print("Generating Technical Chart...")
        print(f"{'='*60}")
        try:
            # Prepare data for charting (need extra history for SMA200, volume MA, and S/R detection)
            # Chart ALWAYS displays 91 calendar days (~65 trading days)
            # Need 20 extra days for Volume MA(20) to warm up
            # Need 200 extra days for SMA(200) to warm up
            # Need more history for better support/resistance detection
            # Total: use max(args.days + 200, 250) to ensure SMA200 coverage
            df_sorted_for_chart = df_with_factors.sort_values('date', ascending=False)
            chart_lookback_days = max(args.days + 200, 250)
            chart_data = df_sorted_for_chart.head(chart_lookback_days).sort_values('date', ascending=True)

            # Create chart
            chart_path = create_comprehensive_chart(chart_data, args.ticker, plot_days=args.days)
            print(f"[OK] Chart saved to: {chart_path}")
        except Exception as e:
            print(f"[WARNING] Chart generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            print("   Reports are still available.")

        # Step 7: Generate HTML report (always)
        print(f"\n{'='*60}")
        print("Generating HTML Report...")
        print(f"{'='*60}")
        try:
            # Import HTML converter (utils is at project root, 4 levels up from scripts/)
            sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / 'utils'))
            from md_to_html import convert_md_to_html

            html_path = md_path.replace('.md', '.html')
            convert_md_to_html(md_path, html_path)
            print(f"[OK] HTML saved to: {html_path}")

        except Exception as e:
            print(f"[WARNING] HTML generation failed: {str(e)}")
            print("   Markdown report is still available.")

        # Step 8: Validate report data
        print(f"\n{'='*60}")
        print("Validating Report Data...")
        print(f"{'='*60}")
        try:
            # Import validation module
            from validate_technical_report import extract_report_values, calculate_fresh_values, validate_values

            # Extract and validate
            report_values = extract_report_values(Path(md_path))
            actual_values = calculate_fresh_values(args.ticker, lookback_days=actual_lookback)
            matches, mismatches, missing = validate_values(report_values, actual_values, tolerance=0.02)

            # Print summary
            if mismatches:
                print(f"[WARNING] Validation found {len(mismatches)} mismatch(es):")
                for item in mismatches:
                    print(f"  - {item['metric']}: Report={item['report']:.2f}, Actual={item['actual']:.2f}")
                print(f"\nRun validation script for detailed report:")
                print(f"  python scripts/validate_technical_report.py {args.ticker} --report {md_path}")
            else:
                print(f"[OK] All {len(matches)} values validated successfully!")

        except Exception as e:
            print(f"[WARNING] Validation failed: {str(e)}")
            print("   Report is still available but values not verified.")

        print(f"\n{'='*60}")
        print("[OK] ANALYSIS COMPLETE!")
        print(f"{'='*60}")

    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
