#!/usr/bin/env python3
"""
Update Yahoo Finance Data in Existing Report

Updates only the price, volume, and valuation metrics in an existing fundamental
analysis report. Preserves all research, analysis, and recommendations.

Usage:
    python update_report_data.py META
    python update_report_data.py AAPL --report analyses/AAPL/AAPL-2026-06-21.md
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path
import re
from typing import Dict, Any

try:
    import yfinance as yf
except ImportError:
    print("Error: yfinance not installed. Install with: pip install yfinance")
    sys.exit(1)


def fetch_current_data(ticker: str) -> Dict[str, Any]:
    """Fetch current Yahoo Finance data"""
    print(f"Fetching current data for {ticker}...")

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
        "current_volume": int(current_volume),
        "volume_ratio": round(volume_ratio, 2),
    }

    return data


def update_report(report_path: Path, data: Dict[str, Any]) -> bool:
    """Update report with fresh Yahoo Finance data"""

    if not report_path.exists():
        print(f"Error: Report not found at {report_path}")
        return False

    # Read existing report
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update header line with current price
    content = re.sub(
        r'\*\*Current Price\*\*: \$[\d.]+',
        f'**Current Price**: ${data["current_price"]}',
        content
    )

    # Update Executive Summary price
    content = re.sub(
        r'- Current Price: USD \$[\d.]+',
        f'- Current Price: USD ${data["current_price"]}',
        content
    )

    # Update 52-week range
    content = re.sub(
        r'- 52-Week Range: \$[\d.]+ - \$[\d.]+',
        f'- 52-Week Range: ${data["week_52_low"]} - ${data["week_52_high"]}',
        content
    )

    # Update position in range
    content = re.sub(
        r'- \*\*Position in Range\*\*: [\d.]+%',
        f'- **Position in Range**: {data["range_position_pct"]}%',
        content
    )

    # Update pct from high/low
    content = re.sub(
        r'\([+-][\d.]+% from high, [+-][\d.]+% from low\)',
        f'({data["pct_from_high"]:+.1f}% from high, {data["pct_from_low"]:+.1f}% from low)',
        content
    )

    # Update trading volume
    content = re.sub(
        r'- \*\*Trading Volume\*\*: [\d,]+ \([\d.]+x average\)',
        f'- **Trading Volume**: {data["current_volume"]:,} ({data["volume_ratio"]:.2f}x average)',
        content
    )

    # Update P/E ratios in table
    if data['pe_trailing']:
        content = re.sub(
            r'\| P/E \(Trailing\) \| [\d.]+',
            f'| P/E (Trailing) | {data["pe_trailing"]}',
            content
        )

    if data['pe_forward']:
        content = re.sub(
            r'\| P/E \(Forward\) \| [\d.]+',
            f'| P/E (Forward) | {data["pe_forward"]}',
            content
        )

    if data['ps_ratio']:
        content = re.sub(
            r'\| P/S \| [\d.]+',
            f'| P/S | {data["ps_ratio"]}',
            content
        )

    if data['pb_ratio']:
        content = re.sub(
            r'\| P/B \| [\d.]+',
            f'| P/B | {data["pb_ratio"]}',
            content
        )

    # Update 6-month return
    content = re.sub(
        r'- 6-Month Return: [+-][\d.]+%',
        f'- 6-Month Return: {data["six_month_return"]:+.1f}%',
        content
    )

    # Update price level in title
    content = re.sub(
        r'## 1\. Price Level Assessment: (HIGH|MEDIUM|LOW)',
        f'## 1. Price Level Assessment: {data["price_level"]}',
        content
    )

    # Update table of contents
    content = re.sub(
        r'1\. Price Level Assessment: (HIGH|MEDIUM|LOW)',
        f'1. Price Level Assessment: {data["price_level"]}',
        content
    )

    # Add update timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "**Last Data Update**:" in content:
        content = re.sub(
            r'\*\*Last Data Update\*\*: [\d-]+ [\d:]+',
            f'**Last Data Update**: {timestamp}',
            content
        )
    else:
        # Add update timestamp before appendix
        content = re.sub(
            r'(## Appendix:)',
            f'**Last Data Update**: {timestamp}\n\n---\n\n\\1',
            content
        )

    # Write updated report
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[SUCCESS] Report updated: {report_path}")
    print(f"\nUpdated metrics:")
    print(f"  Current Price: ${data['current_price']}")
    print(f"  52-Week Range: ${data['week_52_low']} - ${data['week_52_high']}")
    print(f"  Position: {data['range_position_pct']}% ({data['price_level']})")
    print(f"  P/E (Trailing): {data['pe_trailing']}")
    print(f"  P/E (Forward): {data['pe_forward']}")
    print(f"  Volume: {data['current_volume']:,} ({data['volume_ratio']:.2f}x avg)")

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Update Yahoo Finance data in existing fundamental analysis report'
    )
    parser.add_argument(
        'ticker',
        type=str,
        help='Stock ticker symbol (e.g., AAPL, MSFT, META)'
    )
    parser.add_argument(
        '--report',
        type=str,
        help='Path to report file (default: most recent report for today)'
    )

    args = parser.parse_args()
    ticker = args.ticker.upper()

    # Determine report path
    if args.report:
        report_path = Path(args.report)
    else:
        script_dir = Path(__file__).parent.parent
        today = datetime.now().strftime("%Y-%m-%d")
        analyses_dir = script_dir / 'analyses' / ticker

        # Find most recent report for today (could be multiple with different times)
        if analyses_dir.exists():
            today_reports = list(analyses_dir.glob(f"{ticker}-{today}-*.md"))
            if today_reports:
                # Get the most recent one by modification time
                report_path = max(today_reports, key=lambda p: p.stat().st_mtime)
                print(f"Found today's report: {report_path.name}")
            else:
                print(f"Error: No report found for {ticker} on {today}")
                print(f"Available reports: {[f.name for f in analyses_dir.glob(f'{ticker}-*.md')]}")
                sys.exit(1)
        else:
            print(f"Error: No analyses directory found for {ticker}")
            sys.exit(1)

    # Fetch current data
    data = fetch_current_data(ticker)

    if 'error' in data:
        print(f"Error: {data['error']}")
        sys.exit(1)

    # Update report
    success = update_report(report_path, data)

    if success:
        # Regenerate HTML
        html_path = report_path.with_suffix('.html')
        print(f"\nRegenerating HTML: {html_path}")

        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'utils'))
        from md_to_html import convert_md_to_html

        convert_md_to_html(str(report_path), str(html_path))

        print(f"\n{'='*80}")
        print(f"DATA UPDATE COMPLETE")
        print(f"{'='*80}")
        print(f"\nReport: {report_path}")
        print(f"HTML: {html_path}")
        print(f"\nAll research and analysis preserved.")
        print(f"Only Yahoo Finance data updated (price, volume, ratios).")
        print(f"\n{'='*80}\n")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
