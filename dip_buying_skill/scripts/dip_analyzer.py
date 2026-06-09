#!/usr/bin/env python3
"""
Dip Buying Analysis Script

Fetches stock/ETF data and calculates technical indicators to help determine
if a price drop is a buying opportunity.

Usage:
    python dip_analyzer.py SMH
    python dip_analyzer.py NVDA --period 6mo
    python dip_analyzer.py META --export analysis.json

Requirements:
    pip install yfinance pandas numpy ta-lib (or pandas-ta)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import argparse
import sys

def calculate_rsi(prices, period=14):
    """Calculate RSI (Relative Strength Index)"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_moving_averages(df):
    """Calculate key moving averages"""
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    return df

def find_recent_high(df, lookback_days=60):
    """Find recent high within lookback period"""
    recent_data = df.tail(lookback_days)
    high_price = recent_data['High'].max()
    high_date = recent_data['High'].idxmax()
    return high_price, high_date

def analyze_dip(ticker, period='6mo'):
    """
    Main analysis function for dip buying

    Args:
        ticker: Stock/ETF ticker symbol
        period: Data period (1mo, 3mo, 6mo, 1y, 2y, 5y)

    Returns:
        dict: Analysis results
    """

    print(f"\n{'='*60}")
    print(f"DIP BUYING ANALYSIS: {ticker.upper()}")
    print(f"{'='*60}\n")

    # Fetch data
    print(f"Fetching data for {ticker}...")
    stock = yf.Ticker(ticker)

    try:
        # Get historical data
        df = stock.history(period=period)

        if df.empty:
            print(f"Error: No data found for {ticker}")
            return None

        # Get info
        info = stock.info

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

    # Current price and basic info
    current_price = df['Close'].iloc[-1]
    current_date = df.index[-1].strftime('%Y-%m-%d')

    # 52-week high/low
    week_52_high = df['High'].tail(252).max() if len(df) >= 252 else df['High'].max()
    week_52_low = df['Low'].tail(252).min() if len(df) >= 252 else df['Low'].min()
    week_52_range = week_52_high - week_52_low
    position_in_range = ((current_price - week_52_low) / week_52_range * 100) if week_52_range > 0 else 0

    # Drop from 52-week high
    drop_from_52w_high = ((current_price - week_52_high) / week_52_high * 100)

    # Recent high (60 days)
    recent_high_price, recent_high_date = find_recent_high(df, lookback_days=60)
    drop_from_recent_high = ((current_price - recent_high_price) / recent_high_price * 100)
    days_since_high = (df.index[-1] - recent_high_date).days

    # Calculate moving averages
    df = calculate_moving_averages(df)
    sma_20 = df['SMA_20'].iloc[-1]
    sma_50 = df['SMA_50'].iloc[-1]
    sma_200 = df['SMA_200'].iloc[-1]

    # Price vs MAs
    vs_sma_20 = ((current_price - sma_20) / sma_20 * 100) if not pd.isna(sma_20) else None
    vs_sma_50 = ((current_price - sma_50) / sma_50 * 100) if not pd.isna(sma_50) else None
    vs_sma_200 = ((current_price - sma_200) / sma_200 * 100) if not pd.isna(sma_200) else None

    # RSI
    df['RSI'] = calculate_rsi(df['Close'])
    current_rsi = df['RSI'].iloc[-1]

    # Volume analysis
    avg_volume_20d = df['Volume'].tail(20).mean()
    avg_volume_60d = df['Volume'].tail(60).mean()
    recent_volume_5d = df['Volume'].tail(5).mean()
    volume_surge = (recent_volume_5d / avg_volume_60d) if avg_volume_60d > 0 else 1.0

    # Price momentum (recent 5 days, 10 days, 30 days)
    price_5d_ago = df['Close'].iloc[-6] if len(df) >= 6 else df['Close'].iloc[0]
    price_10d_ago = df['Close'].iloc[-11] if len(df) >= 11 else df['Close'].iloc[0]
    price_30d_ago = df['Close'].iloc[-31] if len(df) >= 31 else df['Close'].iloc[0]

    momentum_5d = ((current_price - price_5d_ago) / price_5d_ago * 100)
    momentum_10d = ((current_price - price_10d_ago) / price_10d_ago * 100)
    momentum_30d = ((current_price - price_30d_ago) / price_30d_ago * 100)

    # Support/Resistance levels
    recent_60d = df.tail(60)
    support_level_quartile = recent_60d['Low'].quantile(0.25)  # Lower quartile as support
    resistance_level = recent_60d['High'].quantile(0.75)  # Upper quartile as resistance

    # Find prior swing lows (local minima in last 60 days)
    swing_lows = []
    for i in range(5, len(recent_60d)-5):
        if recent_60d['Low'].iloc[i] == recent_60d['Low'].iloc[i-5:i+6].min():
            swing_lows.append(recent_60d['Low'].iloc[i])

    # Psychological support (round numbers below current price)
    psychological_levels = []
    for level in [10, 25, 50, 75, 100, 125, 150, 175, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800]:
        if level < current_price and level > current_price * 0.5:  # Within 50% below current
            psychological_levels.append(level)

    # Fibonacci retracement levels (from recent high to recent low)
    fib_high = recent_high_price
    fib_low = recent_60d['Low'].min()
    fib_range = fib_high - fib_low
    fib_382 = fib_high - (fib_range * 0.382)
    fib_500 = fib_high - (fib_range * 0.500)
    fib_618 = fib_high - (fib_range * 0.618)

    # Identify strongest support levels
    support_levels = []

    # Add moving averages as support
    if not pd.isna(sma_200) and sma_200 < current_price:
        strength = "STRONG" if current_price > sma_200 * 1.05 else "MODERATE"
        support_levels.append({
            'price': sma_200,
            'type': '200-day MA',
            'strength': strength
        })
    if not pd.isna(sma_50) and sma_50 < current_price:
        strength = "STRONG" if current_price > sma_50 * 1.05 else "MODERATE"
        support_levels.append({
            'price': sma_50,
            'type': '50-day MA',
            'strength': strength
        })
    if not pd.isna(sma_20) and sma_20 < current_price:
        support_levels.append({
            'price': sma_20,
            'type': '20-day MA',
            'strength': 'WEAK'
        })

    # Add psychological levels
    if psychological_levels:
        # Get the 2 closest psychological levels below current price
        closest_psych = sorted(psychological_levels, reverse=True)[:2]
        for level in closest_psych:
            support_levels.append({
                'price': level,
                'type': 'Psychological',
                'strength': 'MODERATE'
            })

    # Add Fibonacci levels (only if below current price)
    if fib_382 < current_price:
        support_levels.append({
            'price': fib_382,
            'type': 'Fib 38.2%',
            'strength': 'MODERATE'
        })
    if fib_500 < current_price:
        support_levels.append({
            'price': fib_500,
            'type': 'Fib 50%',
            'strength': 'STRONG'
        })
    if fib_618 < current_price:
        support_levels.append({
            'price': fib_618,
            'type': 'Fib 61.8%',
            'strength': 'STRONG'
        })

    # Add swing lows
    if swing_lows:
        unique_swings = list(set([round(s, 2) for s in swing_lows if s < current_price]))
        # Get top 2 swing lows
        for swing in sorted(unique_swings, reverse=True)[:2]:
            support_levels.append({
                'price': swing,
                'type': 'Prior swing low',
                'strength': 'MODERATE'
            })

    # Add 52-week low
    support_levels.append({
        'price': week_52_low,
        'type': '52-week low',
        'strength': 'STRONG'
    })

    # Sort by price (descending) and take top 5
    support_levels = sorted(support_levels, key=lambda x: x['price'], reverse=True)[:5]

    # Volatility (20-day standard deviation of returns)
    df['Returns'] = df['Close'].pct_change()
    volatility_20d = df['Returns'].tail(20).std() * np.sqrt(252) * 100  # Annualized

    # Technical signals
    signals = []

    # RSI signals
    if current_rsi < 30:
        signals.append("OVERSOLD (RSI < 30) - Strong buy signal")
    elif current_rsi < 40:
        signals.append("Approaching oversold (RSI < 40) - Potential buy")
    elif current_rsi > 70:
        signals.append("OVERBOUGHT (RSI > 70) - Avoid buying")

    # Moving average signals
    if vs_sma_50 is not None and vs_sma_50 < -10:
        signals.append("Price >10% below 50-day MA - Oversold")
    if vs_sma_200 is not None and vs_sma_200 < -15:
        signals.append("Price >15% below 200-day MA - Deep oversold")

    # Volume signals
    if volume_surge > 1.5:
        signals.append(f"Volume surge {volume_surge:.1f}x average - Panic selling or capitulation")
    elif volume_surge > 1.2:
        signals.append(f"Elevated volume {volume_surge:.1f}x - Increased selling pressure")

    # Momentum signals
    if momentum_5d > 2:
        signals.append("Bouncing (5-day momentum +2%+) - Early reversal sign")
    elif momentum_5d < -5:
        signals.append("Accelerating down (5-day momentum -5%+) - Wait for stabilization")

    # Drop magnitude assessment
    drop_severity = "NONE"
    if drop_from_52w_high < -30:
        drop_severity = "SEVERE (-30%+ from high)"
    elif drop_from_52w_high < -20:
        drop_severity = "MAJOR (-20-30% from high)"
    elif drop_from_52w_high < -10:
        drop_severity = "MODERATE (-10-20% from high)"
    elif drop_from_52w_high < -5:
        drop_severity = "MINOR (-5-10% from high)"
    else:
        drop_severity = "MINIMAL (<5% from high)"

    # Entry timing assessment
    entry_timing = "WAIT"
    if current_rsi < 30 and momentum_5d > 0 and volume_surge < 1.3:
        entry_timing = "BUY NOW - Oversold + stabilizing"
    elif current_rsi < 40 and vs_sma_50 and vs_sma_50 < -8:
        entry_timing = "BUY SOON - Approaching oversold"
    elif drop_from_52w_high < -25 and momentum_5d > -2:
        entry_timing = "CONSIDER - Large drop, but stabilizing"
    elif momentum_5d < -5 or volume_surge > 2.0:
        entry_timing = "WAIT - Still falling or panic selling"
    else:
        entry_timing = "WATCH - Not oversold enough yet"

    # Compile results
    results = {
        'ticker': ticker.upper(),
        'date': current_date,
        'current_price': round(current_price, 2),
        'company_name': info.get('longName', ticker.upper()),

        '52_week_high': round(week_52_high, 2),
        '52_week_low': round(week_52_low, 2),
        'position_in_52w_range_pct': round(position_in_range, 1),
        'drop_from_52w_high_pct': round(drop_from_52w_high, 1),

        'recent_high_60d': round(recent_high_price, 2),
        'recent_high_date': recent_high_date.strftime('%Y-%m-%d'),
        'drop_from_recent_high_pct': round(drop_from_recent_high, 1),
        'days_since_high': days_since_high,

        'sma_20': round(sma_20, 2) if not pd.isna(sma_20) else None,
        'sma_50': round(sma_50, 2) if not pd.isna(sma_50) else None,
        'sma_200': round(sma_200, 2) if not pd.isna(sma_200) else None,

        'vs_sma_20_pct': round(vs_sma_20, 1) if vs_sma_20 is not None else None,
        'vs_sma_50_pct': round(vs_sma_50, 1) if vs_sma_50 is not None else None,
        'vs_sma_200_pct': round(vs_sma_200, 1) if vs_sma_200 is not None else None,

        'rsi_14': round(current_rsi, 1),

        'avg_volume_20d': int(avg_volume_20d),
        'recent_volume_5d': int(recent_volume_5d),
        'volume_surge_ratio': round(volume_surge, 2),

        'momentum_5d_pct': round(momentum_5d, 1),
        'momentum_10d_pct': round(momentum_10d, 1),
        'momentum_30d_pct': round(momentum_30d, 1),

        'support_levels': [{'price': round(s['price'], 2), 'type': s['type'], 'strength': s['strength']} for s in support_levels],
        'resistance_level': round(resistance_level, 2),
        'volatility_20d_annual_pct': round(volatility_20d, 1),

        'drop_severity': drop_severity,
        'entry_timing': entry_timing,
        'technical_signals': signals,
    }

    # Print formatted output
    print_analysis(results)

    return results

def print_analysis(results):
    """Print formatted analysis results"""

    print(f"Company: {results['company_name']}")
    print(f"Ticker: {results['ticker']}")
    print(f"Date: {results['date']}")
    print(f"\n{'-'*60}")
    print(f"PRICE ANALYSIS")
    print(f"{'-'*60}")
    print(f"Current Price:        ${results['current_price']}")
    print(f"52-Week High:         ${results['52_week_high']} ({results['drop_from_52w_high_pct']:+.1f}%)")
    print(f"52-Week Low:          ${results['52_week_low']}")
    print(f"Position in Range:    {results['position_in_52w_range_pct']:.1f}% (0%=low, 100%=high)")
    print(f"\nRecent High (60d):    ${results['recent_high_60d']} on {results['recent_high_date']}")
    print(f"Drop from Recent:     {results['drop_from_recent_high_pct']:+.1f}% ({results['days_since_high']} days ago)")
    print(f"\nDrop Severity:        {results['drop_severity']}")

    print(f"\n{'-'*60}")
    print(f"MOVING AVERAGES")
    print(f"{'-'*60}")
    if results['sma_20']:
        print(f"20-day MA:            ${results['sma_20']} ({results['vs_sma_20_pct']:+.1f}%)")
    if results['sma_50']:
        print(f"50-day MA:            ${results['sma_50']} ({results['vs_sma_50_pct']:+.1f}%)")
    if results['sma_200']:
        print(f"200-day MA:           ${results['sma_200']} ({results['vs_sma_200_pct']:+.1f}%)")

    print(f"\n{'-'*60}")
    print(f"MOMENTUM & TECHNICAL INDICATORS")
    print(f"{'-'*60}")
    print(f"RSI (14-period):      {results['rsi_14']:.1f}", end="")
    if results['rsi_14'] < 30:
        print(" [OVERSOLD]")
    elif results['rsi_14'] < 40:
        print(" [Approaching oversold]")
    elif results['rsi_14'] > 70:
        print(" [OVERBOUGHT]")
    else:
        print(" [Neutral]")

    print(f"\n5-day momentum:       {results['momentum_5d_pct']:+.1f}%")
    print(f"10-day momentum:      {results['momentum_10d_pct']:+.1f}%")
    print(f"30-day momentum:      {results['momentum_30d_pct']:+.1f}%")

    print(f"\n{'-'*60}")
    print(f"VOLUME ANALYSIS")
    print(f"{'-'*60}")
    print(f"20-day avg volume:    {results['avg_volume_20d']:,}")
    print(f"Recent 5-day avg:     {results['recent_volume_5d']:,}")
    print(f"Volume surge:         {results['volume_surge_ratio']:.2f}x", end="")
    if results['volume_surge_ratio'] > 1.5:
        print(" [ELEVATED - Panic selling]")
    elif results['volume_surge_ratio'] > 1.2:
        print(" [Above average]")
    else:
        print(" [Normal]")

    print(f"\n{'-'*60}")
    print(f"KEY SUPPORT LEVELS (Entry Zones)")
    print(f"{'-'*60}")
    if results['support_levels']:
        for i, support in enumerate(results['support_levels'], 1):
            strength_marker = "[***]" if support['strength'] == "STRONG" else "[**]" if support['strength'] == "MODERATE" else "[*]"
            print(f"{i}. ${support['price']:>7.2f} - {support['type']:<20} {strength_marker} {support['strength']}")
    else:
        print("No clear support levels identified")

    print(f"\nResistance (75th):    ${results['resistance_level']}")
    print(f"Volatility (annual):  {results['volatility_20d_annual_pct']:.1f}%")

    print(f"\n{'='*60}")
    print(f"ENTRY TIMING ASSESSMENT: {results['entry_timing']}")
    print(f"{'='*60}")

    if results['technical_signals']:
        print(f"\nTechnical Signals:")
        for signal in results['technical_signals']:
            print(f"  • {signal}")

    print(f"\n{'-'*60}")
    print(f"RECOMMENDED ENTRY ZONES (Based on Support)")
    print(f"{'-'*60}")
    strong_supports = [s for s in results['support_levels'] if s['strength'] == 'STRONG']
    if strong_supports and len(strong_supports) >= 3:
        print(f"Entry 1 (33%): ${strong_supports[0]['price']:.2f} ({strong_supports[0]['type']})")
        print(f"Entry 2 (33%): ${strong_supports[1]['price']:.2f} ({strong_supports[1]['type']})")
        print(f"Entry 3 (33%): ${strong_supports[2]['price']:.2f} ({strong_supports[2]['type']})")
    elif len(results['support_levels']) >= 3:
        print(f"Entry 1 (33%): ${results['support_levels'][0]['price']:.2f} ({results['support_levels'][0]['type']})")
        print(f"Entry 2 (33%): ${results['support_levels'][1]['price']:.2f} ({results['support_levels'][1]['type']})")
        print(f"Entry 3 (33%): ${results['support_levels'][2]['price']:.2f} ({results['support_levels'][2]['type']})")
    else:
        print("Insufficient support levels identified - use manual analysis")

    print(f"\n{'-'*60}")
    print(f"NEXT STEPS - Run Bargain Test (5-Point Checklist)")
    print(f"{'-'*60}")
    print(f"1. [ ] Business Intact? (Moat, revenue, margins, balance sheet)")
    print(f"2. [ ] Management Credible? (Track record, transparency, plan)")
    print(f"3. [ ] Valuation Compelling? (P/E vs history, 30%+ discount?)")
    print(f"4. [ ] Risk-Reward Favorable? (3:1+ upside/downside?)")
    print(f"5. [ ] Catalyst for Recovery? (Within 3-6 months?)")
    print(f"\nBargain Test Score: __/5")
    print(f"Recommendation: [STRONG BUY/BUY/WATCH/AVOID/SELL]\n")

def main():
    parser = argparse.ArgumentParser(
        description='Dip Buying Analysis - Analyze price drops for buying opportunities'
    )
    parser.add_argument('ticker', type=str, help='Stock/ETF ticker symbol (e.g., SMH, NVDA, META)')
    parser.add_argument('--period', type=str, default='6mo',
                        help='Data period: 1mo, 3mo, 6mo (default), 1y, 2y, 5y')
    parser.add_argument('--export', type=str, help='Export results to JSON file')

    args = parser.parse_args()

    # Run analysis
    results = analyze_dip(args.ticker.upper(), period=args.period)

    if results and args.export:
        with open(args.export, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n[SUCCESS] Results exported to {args.export}")

    return results

if __name__ == '__main__':
    main()
