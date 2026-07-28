"""
Check current and historical P/E ratios for stocks
"""
import yfinance as yf
import pandas as pd
from datetime import datetime

def check_pe_ratios(tickers):
    """
    Fetch current P/E and compare to historical ranges
    """
    print(f"\n{'='*80}")
    print(f"P/E RATIO ANALYSIS - {datetime.now().strftime('%Y-%m-%d')}")
    print(f"{'='*80}\n")

    for ticker in tickers:
        print(f"\n{'='*80}")
        print(f"{ticker} - P/E ANALYSIS")
        print(f"{'='*80}\n")

        try:
            stock = yf.Ticker(ticker)

            # Get current info
            info = stock.info

            # Current metrics
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
            trailing_pe = info.get('trailingPE', 'N/A')
            forward_pe = info.get('forwardPE', 'N/A')
            peg_ratio = info.get('pegRatio', 'N/A')

            # Earnings data
            eps_trailing = info.get('trailingEps', 'N/A')
            eps_forward = info.get('forwardEps', 'N/A')

            # Growth metrics
            earnings_growth = info.get('earningsQuarterlyGrowth', 'N/A')
            revenue_growth = info.get('revenueGrowth', 'N/A')

            # Valuation metrics
            price_to_book = info.get('priceToBook', 'N/A')
            price_to_sales = info.get('priceToSalesTrailing12Months', 'N/A')

            # Market cap
            market_cap = info.get('marketCap', 'N/A')
            if market_cap != 'N/A':
                market_cap_b = market_cap / 1e9
            else:
                market_cap_b = 'N/A'

            print("CURRENT VALUATION METRICS")
            print("-" * 80)
            print(f"Current Price:        ${current_price:.2f}")
            print(f"Market Cap:           ${market_cap_b:.1f}B")
            print(f"")
            print(f"Trailing P/E:         {trailing_pe:.2f}" if trailing_pe != 'N/A' else "Trailing P/E:         N/A")
            print(f"Forward P/E:          {forward_pe:.2f}" if forward_pe != 'N/A' else "Forward P/E:          N/A")
            print(f"PEG Ratio:            {peg_ratio:.2f}" if peg_ratio != 'N/A' else "PEG Ratio:            N/A")
            print(f"")
            print(f"EPS (Trailing):       ${eps_trailing:.2f}" if eps_trailing != 'N/A' else "EPS (Trailing):       N/A")
            print(f"EPS (Forward):        ${eps_forward:.2f}" if eps_forward != 'N/A' else "EPS (Forward):        N/A")
            print(f"")
            print(f"Earnings Growth:      {earnings_growth*100:.1f}%" if earnings_growth != 'N/A' else "Earnings Growth:      N/A")
            print(f"Revenue Growth:       {revenue_growth*100:.1f}%" if revenue_growth != 'N/A' else "Revenue Growth:       N/A")
            print(f"")
            print(f"Price-to-Book:        {price_to_book:.2f}" if price_to_book != 'N/A' else "Price-to-Book:        N/A")
            print(f"Price-to-Sales:       {price_to_sales:.2f}" if price_to_sales != 'N/A' else "Price-to-Sales:       N/A")

            # Get historical data to calculate historical P/E ranges
            print(f"\n{'='*80}")
            print("HISTORICAL P/E ANALYSIS (Last 5 Years)")
            print("-" * 80)

            # Get 5 years of price data
            hist = stock.history(period="5y")

            if len(hist) > 0:
                # Get quarterly earnings
                try:
                    financials = stock.quarterly_financials
                    if financials is not None and not financials.empty:
                        print(f"Historical data available: {len(hist)} trading days")

                        # Calculate approximate historical P/E using price and current EPS
                        if eps_trailing != 'N/A' and eps_trailing > 0:
                            # Calculate P/E at different points
                            recent_high = hist['Close'].max()
                            recent_low = hist['Close'].min()
                            year_ago = hist['Close'].iloc[-252] if len(hist) >= 252 else hist['Close'].iloc[0]

                            pe_at_high = recent_high / eps_trailing
                            pe_at_low = recent_low / eps_trailing
                            pe_year_ago = year_ago / eps_trailing

                            print(f"\nApproximate P/E Ranges (using current trailing EPS ${eps_trailing:.2f}):")
                            print(f"  P/E at 5-year high (${recent_high:.2f}): {pe_at_high:.1f}x")
                            print(f"  P/E at 5-year low (${recent_low:.2f}):  {pe_at_low:.1f}x")
                            print(f"  P/E 1 year ago (${year_ago:.2f}):       {pe_year_ago:.1f}x")
                            print(f"  P/E today (${current_price:.2f}):       {trailing_pe:.1f}x")

                            # Calculate percentile
                            current_pe = trailing_pe
                            pe_range = pe_at_high - pe_at_low
                            pe_position = (current_pe - pe_at_low) / pe_range * 100 if pe_range > 0 else 50

                            print(f"\nCurrent P/E Position: {pe_position:.0f}th percentile of 5-year range")

                            if pe_position < 25:
                                print("  → CHEAP - In bottom 25% of historical range")
                            elif pe_position < 50:
                                print("  → FAIR - Below median historical valuation")
                            elif pe_position < 75:
                                print("  → FAIR - Above median but not expensive")
                            else:
                                print("  → EXPENSIVE - In top 25% of historical range")

                except Exception as e:
                    print(f"Could not fetch detailed financials: {e}")
            else:
                print("No historical data available")

            # Sector comparison
            print(f"\n{'='*80}")
            print("SECTOR CONTEXT")
            print("-" * 80)

            sector = info.get('sector', 'N/A')
            industry = info.get('industry', 'N/A')

            print(f"Sector:   {sector}")
            print(f"Industry: {industry}")

            # Get some comparables (hardcoded common ranges)
            if sector == 'Technology':
                print(f"\nTech Sector P/E Ranges (typical):")
                print(f"  Mature Tech:  15-25x")
                print(f"  Growth Tech:  25-40x")
                print(f"  High Growth:  40-60x")
                print(f"  Bubble:       >60x")

                if trailing_pe != 'N/A':
                    if trailing_pe < 25:
                        print(f"\n  {ticker} at {trailing_pe:.1f}x = MATURE/VALUE range")
                    elif trailing_pe < 40:
                        print(f"\n  {ticker} at {trailing_pe:.1f}x = GROWTH range")
                    elif trailing_pe < 60:
                        print(f"\n  {ticker} at {trailing_pe:.1f}x = HIGH GROWTH range")
                    else:
                        print(f"\n  {ticker} at {trailing_pe:.1f}x = BUBBLE territory")

        except Exception as e:
            print(f"[ERROR] Failed to fetch data for {ticker}: {str(e)}")

    print(f"\n{'='*80}")
    print("COMPARATIVE SUMMARY")
    print(f"{'='*80}\n")

    # Create summary table
    summary = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            summary.append({
                'Ticker': ticker,
                'Price': info.get('currentPrice', info.get('regularMarketPrice', 'N/A')),
                'Trailing P/E': info.get('trailingPE', 'N/A'),
                'Forward P/E': info.get('forwardPE', 'N/A'),
                'PEG': info.get('pegRatio', 'N/A'),
                'P/S': info.get('priceToSalesTrailing12Months', 'N/A'),
            })
        except:
            pass

    if summary:
        df = pd.DataFrame(summary)
        print(df.to_string(index=False))

        print(f"\nKey Insights:")
        print("-" * 80)

        # Compare P/Es
        pes = [s['Trailing P/E'] for s in summary if s['Trailing P/E'] != 'N/A']
        if len(pes) == 2:
            if pes[0] < pes[1]:
                print(f"{summary[0]['Ticker']} is cheaper on P/E basis ({pes[0]:.1f}x vs {pes[1]:.1f}x)")
            else:
                print(f"{summary[1]['Ticker']} is cheaper on P/E basis ({pes[1]:.1f}x vs {pes[0]:.1f}x)")

        # Check PEG ratios
        pegs = [(s['Ticker'], s['PEG']) for s in summary if s['PEG'] != 'N/A']
        if pegs:
            print(f"\nPEG Ratios (P/E to Growth):")
            for t, peg in pegs:
                if peg < 1:
                    print(f"  {t}: {peg:.2f} - UNDERVALUED (PEG < 1)")
                elif peg < 2:
                    print(f"  {t}: {peg:.2f} - FAIR VALUE (PEG 1-2)")
                else:
                    print(f"  {t}: {peg:.2f} - EXPENSIVE (PEG > 2)")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        tickers = sys.argv[1:]
    else:
        tickers = ['MSFT', 'META']

    check_pe_ratios(tickers)
