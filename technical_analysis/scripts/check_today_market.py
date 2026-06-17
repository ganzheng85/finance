"""
Check today's market movements for specific stocks
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def check_today_movements(tickers):
    """
    Check today's price movements and recent trend
    """
    print(f"\n{'='*80}")
    print(f"MARKET CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    results = []

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)

            # Get recent data (last 5 days to see trend)
            hist = stock.history(period="5d")

            if len(hist) < 2:
                print(f"[ERROR] Insufficient data for {ticker}")
                continue

            # Get today's data
            today = hist.iloc[-1]
            yesterday = hist.iloc[-2]
            week_ago = hist.iloc[0] if len(hist) >= 5 else hist.iloc[0]

            # Calculate changes
            today_change = (today['Close'] - yesterday['Close']) / yesterday['Close'] * 100
            week_change = (today['Close'] - week_ago['Close']) / week_ago['Close'] * 100

            # Intraday change
            intraday_change = (today['Close'] - today['Open']) / today['Open'] * 100

            # Volume comparison
            avg_volume = hist['Volume'][:-1].mean()  # Average of previous days
            today_volume_ratio = today['Volume'] / avg_volume

            results.append({
                'Ticker': ticker,
                'Price': today['Close'],
                'Today %': today_change,
                'Intraday %': intraday_change,
                'Week %': week_change,
                'Volume': today['Volume'],
                'Vol Ratio': today_volume_ratio,
                'High': today['High'],
                'Low': today['Low'],
            })

        except Exception as e:
            print(f"[ERROR] Failed to fetch {ticker}: {str(e)}")

    if not results:
        print("[ERROR] No data retrieved")
        return

    df = pd.DataFrame(results)

    # Separate into categories
    mega_cap = df[df['Ticker'].isin(['MSFT', 'AMZN', 'GOOG', 'META', 'AAPL', 'NVDA'])]
    semi = df[df['Ticker'].isin(['SMH', 'NVDA', 'AMD', 'AVGO'])]
    market = df[df['Ticker'].isin(['SPY', 'QQQ', 'DIA'])]

    print("="*80)
    print("MEGA-CAP TECH (MSFT, AMZN, GOOG, META)")
    print("="*80)
    if len(mega_cap) > 0:
        print(mega_cap.to_string(index=False))
        print(f"\nAverage Today Change: {mega_cap['Today %'].mean():.2f}%")
        print(f"Average Week Change: {mega_cap['Week %'].mean():.2f}%")

    print(f"\n{'='*80}")
    print("SEMICONDUCTOR SECTOR (SMH, NVDA, AMD, AVGO)")
    print("="*80)
    if len(semi) > 0:
        print(semi.to_string(index=False))
        print(f"\nAverage Today Change: {semi['Today %'].mean():.2f}%")
        print(f"Average Week Change: {semi['Week %'].mean():.2f}%")

    print(f"\n{'='*80}")
    print("MARKET INDICES")
    print("="*80)
    if len(market) > 0:
        print(market.to_string(index=False))

    # Analysis
    print(f"\n{'='*80}")
    print("SECTOR DIVERGENCE ANALYSIS")
    print("="*80)

    if len(mega_cap) > 0 and len(semi) > 0:
        mega_avg = mega_cap['Today %'].mean()
        semi_avg = semi['Today %'].mean()
        divergence = semi_avg - mega_avg

        print(f"\nMega-Cap Tech Average: {mega_avg:+.2f}%")
        print(f"Semiconductor Average: {semi_avg:+.2f}%")
        print(f"Divergence: {divergence:+.2f}%")

        if divergence > 1:
            print("\n[ALERT] Strong sector rotation: Money flowing FROM mega-cap TO semiconductors")
        elif divergence < -1:
            print("\n[ALERT] Strong sector rotation: Money flowing FROM semiconductors TO mega-cap")
        else:
            print("\n[INFO] No significant sector rotation")

    # Identify biggest movers
    print(f"\n{'='*80}")
    print("BIGGEST MOVERS TODAY")
    print("="*80)

    df_sorted = df.sort_values('Today %', ascending=False)
    print("\nWinners:")
    print(df_sorted.head(3)[['Ticker', 'Today %', 'Volume', 'Vol Ratio']].to_string(index=False))

    print("\nLosers:")
    print(df_sorted.tail(3)[['Ticker', 'Today %', 'Volume', 'Vol Ratio']].to_string(index=False))

    # Volume analysis
    print(f"\n{'='*80}")
    print("VOLUME ANALYSIS (Higher volume = stronger conviction)")
    print("="*80)

    high_volume = df[df['Vol Ratio'] > 1.5].sort_values('Vol Ratio', ascending=False)
    if len(high_volume) > 0:
        print("\nHigh Volume Stocks (>1.5x average):")
        print(high_volume[['Ticker', 'Today %', 'Vol Ratio']].to_string(index=False))
    else:
        print("\nNo stocks with unusually high volume")

if __name__ == "__main__":
    # Stocks to check
    tickers = [
        # Mega-cap tech
        'MSFT', 'AMZN', 'GOOG', 'META', 'AAPL',
        # Semiconductors
        'SMH', 'NVDA', 'AMD', 'AVGO', 'TSM',
        # Market indices
        'SPY', 'QQQ', 'DIA'
    ]

    check_today_movements(tickers)
