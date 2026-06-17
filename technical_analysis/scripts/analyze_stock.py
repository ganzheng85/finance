"""
Complete Stock Technical Analysis Script

Fetches Yahoo Finance data, calculates technical factors, and generates a comprehensive analysis report.

Usage:
    python analyze_stock.py TICKER [--days DAYS] [--pdf]

Example:
    python analyze_stock.py AAPL
    python analyze_stock.py TSLA --days 60 --pdf
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd

# Import our modules
from fetch_and_analyze import fetch_stock_data, calculate_all_factors, get_recent_data
from trend_analyzer import TrendAnalyzer


def generate_markdown_report(df: pd.DataFrame, ticker: str, analyzer: TrendAnalyzer) -> str:
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

    Returns
    -------
    str
        Markdown formatted report
    """
    # Get analyses
    trend = analyzer.analyze_trend_direction()
    vol = analyzer.analyze_volatility()
    volume = analyzer.analyze_volume()
    levels = analyzer.identify_key_levels()
    signals = analyzer.generate_trading_signals()

    latest = df.iloc[-1]

    # Build markdown
    md = []
    md.append(f"# Technical Analysis Report: {ticker.upper()}")
    md.append("")
    md.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md.append(f"**Analysis Period:** {df['date'].min().date()} to {df['date'].max().date()}")
    md.append(f"**Current Price:** ${latest['adjusted_close']:.2f}")
    md.append("")

    md.append("---")
    md.append("")

    # Executive Summary
    md.append("## Executive Summary")
    md.append("")
    md.append(f"**Trend:** {trend['direction']} (Strength: {trend['strength']}/10)")
    md.append(f"**Primary Signal:** {signals[0]['action']} ({signals[0]['confidence']} confidence)")
    md.append(f"**Volatility:** {vol['level']}")
    md.append(f"**Volume:** {volume['level']}")
    md.append("")

    # Trend Analysis
    md.append("---")
    md.append("")
    md.append("## 1. Trend Analysis")
    md.append("")
    md.append(f"### Overall Direction: **{trend['direction']}**")
    md.append(f"- **Strength:** {trend['strength']}/10")
    md.append(f"- **Technical Score:** {trend['score']:+d}")
    md.append("")

    if trend['bullish_signals']:
        md.append("### Bullish Signals")
        for signal in trend['bullish_signals']:
            md.append(f"- [+] {signal}")
        md.append("")

    if trend['bearish_signals']:
        md.append("### Bearish Signals")
        for signal in trend['bearish_signals']:
            md.append(f"- [WARNING] {signal}")
        md.append("")

    # Key Indicators
    md.append("---")
    md.append("")
    md.append("## 2. Key Technical Indicators")
    md.append("")

    # Table of indicators
    md.append("| Indicator | Value | Signal |")
    md.append("|-----------|-------|--------|")

    # RSI
    if 'rsi_14' in df.columns and pd.notna(latest['rsi_14']):
        rsi = latest['rsi_14']
        rsi_signal = "[GREEN] OVERSOLD" if rsi < 30 else "[RED] OVERBOUGHT" if rsi > 70 else "[NEUTRAL] NEUTRAL"
        md.append(f"| RSI(14) | {rsi:.2f} | {rsi_signal} |")

    # MACD
    if 'macd_hist_12_26_9' in df.columns and pd.notna(latest['macd_hist_12_26_9']):
        macd = latest['macd_hist_12_26_9']
        macd_signal = "[GREEN] BULLISH" if macd > 0 else "[RED] BEARISH"
        md.append(f"| MACD Histogram | {macd:+.4f} | {macd_signal} |")

    # Stochastic
    if 'stoch_k_14' in df.columns and pd.notna(latest['stoch_k_14']):
        stoch = latest['stoch_k_14']
        stoch_signal = "[GREEN] OVERSOLD" if stoch < 20 else "[RED] OVERBOUGHT" if stoch > 80 else "[NEUTRAL] NEUTRAL"
        md.append(f"| Stochastic %K | {stoch:.2f} | {stoch_signal} |")

    # ADX
    if 'adx_14' in df.columns and pd.notna(latest['adx_14']):
        adx = latest['adx_14']
        adx_signal = "[GREEN] STRONG TREND" if adx > 25 else "[NEUTRAL] WEAK TREND"
        md.append(f"| ADX(14) | {adx:.2f} | {adx_signal} |")

    # Distance from SMAs
    if 'dist_sma_200' in df.columns and pd.notna(latest['dist_sma_200']):
        dist = latest['dist_sma_200'] * 100
        dist_signal = "[GREEN] ABOVE" if dist > 0 else "[RED] BELOW"
        md.append(f"| Price vs SMA(200) | {dist:+.2f}% | {dist_signal} |")

    # Bollinger %B
    if 'bb_percent_b' in df.columns and pd.notna(latest['bb_percent_b']):
        pct_b = latest['bb_percent_b']
        bb_signal = "[RED] BELOW BANDS" if pct_b < 0 else "[RED] ABOVE BANDS" if pct_b > 1 else "[NEUTRAL] WITHIN BANDS"
        md.append(f"| Bollinger %B | {pct_b:.2f} | {bb_signal} |")

    md.append("")

    # Volatility Analysis
    md.append("---")
    md.append("")
    md.append("## 3. Volatility Analysis")
    md.append("")
    md.append(f"**Level:** {vol['level']}")
    if vol['annualized_pct']:
        md.append(f"- Annualized Volatility: {vol['annualized_pct']:.2f}%")
    if vol['percentile']:
        md.append(f"- Historical Percentile: {vol['percentile']:.1f}th percentile")
    md.append(f"- Bollinger Squeeze: **{'YES [WARNING]' if vol['squeeze'] else 'NO'}**")
    md.append(f"- Volatility Expanding: **{'YES' if vol['expansion'] else 'NO'}**")
    md.append("")

    if vol['squeeze'] and vol['expansion']:
        md.append("> 💡 **Note:** Bollinger squeeze with expanding volatility suggests a potential breakout.")
        md.append("")

    # Volume Analysis
    md.append("---")
    md.append("")
    md.append("## 4. Volume Analysis")
    md.append("")
    if volume['relative']:
        md.append(f"**Relative Volume:** {volume['relative']:.2f}x ({volume['level']})")
    md.append(f"**Volume Trend:** {volume['trend']}")
    md.append("")
    if volume['signals']:
        md.append("**Observations:**")
        for sig in volume['signals']:
            md.append(f"- {sig}")
        md.append("")

    # Key Levels
    md.append("---")
    md.append("")
    md.append("## 5. Key Support & Resistance Levels")
    md.append("")
    md.append(f"**Current Price:** ${levels['current_price']:.2f}")
    md.append("")

    if levels['resistance']:
        md.append("### Resistance Levels (Above Current Price)")
        md.append("| Level | Type | Distance |")
        md.append("|-------|------|----------|")
        for r in levels['resistance'][:5]:
            md.append(f"| ${r['level']:.2f} | {r['type']} | +{r['distance_pct']:.2f}% |")
        md.append("")

    if levels['support']:
        md.append("### Support Levels (Below Current Price)")
        md.append("| Level | Type | Distance |")
        md.append("|-------|------|----------|")
        for s in levels['support'][:5]:
            md.append(f"| ${s['level']:.2f} | {s['type']} | -{s['distance_pct']:.2f}% |")
        md.append("")

    # Trading Signals
    md.append("---")
    md.append("")
    md.append("## 6. Trading Signals")
    md.append("")

    for i, signal in enumerate(signals, 1):
        action_emoji = "[GREEN]" if signal['action'] == 'BUY' else "[RED]" if signal['action'] == 'SELL' else "[NEUTRAL]"
        md.append(f"### Signal #{i}: {action_emoji} **{signal['action']}**")
        md.append(f"**Confidence:** {signal['confidence']}")
        md.append(f"**Reason:** {signal['reason']}")
        if signal['details']:
            md.append("")
            md.append("**Details:**")
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
    md.append("## Disclaimer")
    md.append("")
    md.append("This technical analysis is for informational purposes only and should not be considered financial advice. ")
    md.append("Always conduct your own research and consult with a licensed financial advisor before making investment decisions.")
    md.append("")
    md.append("**Report generated by:** Technical Analysis Skill (Claude Code)")
    md.append(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

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

    with open(filepath, 'w') as f:
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
  python analyze_stock.py NVDA --pdf
        """
    )
    parser.add_argument('ticker', type=str, help='Stock ticker symbol')
    parser.add_argument('--days', type=int, default=30, help='Number of recent days to analyze (default: 30)')
    parser.add_argument('--lookback', type=int, default=365, help='Days of historical data (default: 365)')
    parser.add_argument('--pdf', action='store_true', help='Generate PDF report (requires utils/md_to_pdf.py)')

    args = parser.parse_args()

    try:
        print(f"\n{'='*60}")
        print(f"TECHNICAL ANALYSIS: {args.ticker.upper()}")
        print(f"{'='*60}")

        # Step 1: Fetch data
        df = fetch_stock_data(args.ticker, lookback_days=args.lookback)

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
        md_report = generate_markdown_report(df_recent, args.ticker, analyzer)
        md_path = save_report(md_report, args.ticker)

        # Step 6: Generate PDF if requested
        if args.pdf:
            print(f"\n{'='*60}")
            print("Generating PDF Report...")
            print(f"{'='*60}")
            try:
                # Import PDF converter
                sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'utils'))
                from md_to_pdf import convert_markdown_to_pdf

                pdf_path = md_path.replace('.md', '.pdf')
                convert_markdown_to_pdf(md_path, pdf_path)
                print(f"[OK] PDF saved to: {pdf_path}")

            except Exception as e:
                print(f"[WARNING] PDF generation failed: {str(e)}")
                print("   Markdown report is still available.")

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
