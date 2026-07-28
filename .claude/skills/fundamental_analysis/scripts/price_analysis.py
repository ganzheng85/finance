#!/usr/bin/env python3
"""
Stock Price Analysis Script

Fetches current stock price data and calculates price level metrics.
Requires: yfinance (install with: pip install yfinance)

Usage:
    python price_analysis.py "AAPL"
    python price_analysis.py "MSFT" --period 5y
"""

import sys
import argparse
from datetime import datetime
from typing import Dict, Any

try:
    import yfinance as yf
except ImportError:
    print("Error: yfinance not installed. Install with: pip install yfinance")
    sys.exit(1)


def fetch_stock_data(ticker: str, period: str = "5y") -> Dict[str, Any]:
    """
    Fetch stock data and calculate key metrics.

    Args:
        ticker: Stock ticker symbol
        period: Historical period (1y, 2y, 5y, max)

    Returns:
        Dictionary with price data and metrics
    """
    try:
        stock = yf.Ticker(ticker)

        # Get current info
        info = stock.info
        history = stock.history(period=period)

        if history.empty:
            return {"error": f"No data found for ticker {ticker}"}

        # Current price
        current_price = history['Close'].iloc[-1]

        # 52-week range
        week_52_high = history['High'].tail(252).max()  # ~252 trading days in a year
        week_52_low = history['Low'].tail(252).min()

        # 6-month metrics (~126 trading days)
        six_months_ago_price = history['Close'].tail(126).iloc[0] if len(history) >= 126 else history['Close'].iloc[0]
        six_month_return = ((current_price - six_months_ago_price) / six_months_ago_price) * 100
        six_month_high = history['High'].tail(126).max()
        six_month_low = history['Low'].tail(126).min()

        # Position in 52-week range
        range_position = ((current_price - week_52_low) / (week_52_high - week_52_low)) * 100
        pct_from_high = ((current_price - week_52_high) / week_52_high) * 100
        pct_from_low = ((current_price - week_52_low) / week_52_low) * 100

        # Price level determination
        if range_position > 90 or pct_from_high > -10:
            price_level = "HIGH"
        elif range_position < 40 or pct_from_low < 70:
            price_level = "LOW"
        else:
            price_level = "MEDIUM"

        # Valuation metrics
        pe_ratio = info.get('trailingPE', None)
        forward_pe = info.get('forwardPE', None)
        ps_ratio = info.get('priceToSalesTrailing12Months', None)
        pb_ratio = info.get('priceToBook', None)

        # Volume analysis
        avg_volume = history['Volume'].tail(20).mean()
        current_volume = history['Volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0

        # Compile results
        results = {
            "ticker": ticker.upper(),
            "company_name": info.get('longName', ticker),
            "sector": info.get('sector', 'N/A'),
            "industry": info.get('industry', 'N/A'),
            "current_price": round(current_price, 2),
            "currency": info.get('currency', 'USD'),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

            # Price range data
            "week_52_high": round(week_52_high, 2),
            "week_52_low": round(week_52_low, 2),
            "range_position_pct": round(range_position, 1),
            "pct_from_high": round(pct_from_high, 1),
            "pct_from_low": round(pct_from_low, 1),

            # 6-month metrics
            "six_months_ago_price": round(six_months_ago_price, 2),
            "six_month_return": round(six_month_return, 1),
            "six_month_high": round(six_month_high, 2),
            "six_month_low": round(six_month_low, 2),

            # Price level
            "price_level": price_level,

            # Valuation
            "pe_ratio": round(pe_ratio, 2) if pe_ratio else None,
            "forward_pe": round(forward_pe, 2) if forward_pe else None,
            "ps_ratio": round(ps_ratio, 2) if ps_ratio else None,
            "pb_ratio": round(pb_ratio, 2) if pb_ratio else None,

            # Volume
            "avg_volume_20d": int(avg_volume),
            "current_volume": int(current_volume),
            "volume_vs_avg": round(volume_ratio, 2),

            # Additional info
            "market_cap": info.get('marketCap', None),
            "beta": info.get('beta', None),
        }

        return results

    except Exception as e:
        return {"error": f"Error fetching data for {ticker}: {str(e)}"}


def format_output(data: Dict[str, Any]) -> str:
    """Format the output for display."""

    if "error" in data:
        return f"ERROR: {data['error']}"

    # Format market cap
    market_cap = data.get('market_cap')
    if market_cap:
        if market_cap >= 1e12:
            market_cap_str = f"${market_cap/1e12:.2f}T"
        elif market_cap >= 1e9:
            market_cap_str = f"${market_cap/1e9:.2f}B"
        elif market_cap >= 1e6:
            market_cap_str = f"${market_cap/1e6:.2f}M"
        else:
            market_cap_str = f"${market_cap:,.0f}"
    else:
        market_cap_str = "N/A"

    output = f"""
{'='*70}
STOCK PRICE ANALYSIS: {data['ticker']}
{'='*70}

Company: {data['company_name']}
Sector: {data['sector']} | Industry: {data['industry']}
Market Cap: {market_cap_str}
Analysis Date: {data['timestamp']}

{'='*70}
PRICE LEVEL: {data['price_level']}
{'='*70}

Current Price: {data['currency']} {data['current_price']}
52-Week High:  {data['currency']} {data['week_52_high']} ({data['pct_from_high']:+.1f}%)
52-Week Low:   {data['currency']} {data['week_52_low']} ({data['pct_from_low']:+.1f}%)

Position in 52-Week Range: {data['range_position_pct']:.1f}%

{'='*70}
6-MONTH PERFORMANCE
{'='*70}

Price 6 Months Ago: {data['currency']} {data['six_months_ago_price']}
6-Month Return:     {data['six_month_return']:+.1f}%
6-Month High:       {data['currency']} {data['six_month_high']}
6-Month Low:        {data['currency']} {data['six_month_low']}

{'='*70}
VALUATION METRICS
{'='*70}

P/E Ratio (Trailing): {data['pe_ratio'] if data['pe_ratio'] else 'N/A'}
P/E Ratio (Forward):  {data['forward_pe'] if data['forward_pe'] else 'N/A'}
P/S Ratio:            {data['ps_ratio'] if data['ps_ratio'] else 'N/A'}
P/B Ratio:            {data['pb_ratio'] if data['pb_ratio'] else 'N/A'}

{'='*70}
VOLUME ANALYSIS
{'='*70}

20-Day Avg Volume: {data['avg_volume_20d']:,}
Current Volume:    {data['current_volume']:,}
Volume vs Avg:     {data['volume_vs_avg']:.2f}x

{'='*70}
PRICE LEVEL INTERPRETATION
{'='*70}
"""

    if data['price_level'] == 'HIGH':
        output += """
[!] Stock is trading at HIGH levels

Interpretation:
- Price is near 52-week highs
- Requires strong moat and growth to justify
- Consider waiting for pullback unless exceptional quality
- Good for taking profits if already owned

Action: Proceed with caution, need compelling fundamental reasons
"""
    elif data['price_level'] == 'LOW':
        output += """
[*] Stock is trading at LOW levels

Interpretation:
- Price is near 52-week lows
- INVESTIGATE WHY - opportunity or value trap?
- Check for: business deterioration, industry issues, management problems
- Could be attractive entry if fundamentals intact

Action: Deep dive required - cheap can mean broken
"""
    else:  # MEDIUM
        output += """
[=] Stock is trading at MEDIUM levels

Interpretation:
- Price is in the middle of 52-week range
- Fair entry point if fundamentals are solid
- Neither obviously cheap nor expensive
- Focus on business quality and moat strength

Action: Proceed with standard analysis - price not the primary factor
"""

    output += f"\n{'='*70}\n"

    return output


def main():
    parser = argparse.ArgumentParser(
        description='Analyze stock price levels and key metrics'
    )
    parser.add_argument(
        'ticker',
        type=str,
        help='Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)'
    )
    parser.add_argument(
        '--period',
        type=str,
        default='5y',
        choices=['1y', '2y', '5y', 'max'],
        help='Historical period for analysis (default: 5y)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )

    args = parser.parse_args()

    # Fetch data
    data = fetch_stock_data(args.ticker, args.period)

    # Output
    if args.json:
        import json
        print(json.dumps(data, indent=2))
    else:
        print(format_output(data))


if __name__ == "__main__":
    main()
