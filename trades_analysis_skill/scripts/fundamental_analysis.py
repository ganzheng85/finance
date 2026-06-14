import yfinance as yf
import pandas as pd
from datetime import datetime

# List of losing positions with current losses
losing_positions = {
    'fig': {'loss_pct': -25, 'position': 9313},
    'PDD': {'loss_pct': -23, 'position': 8144},
    'ADBE': {'loss_pct': -20, 'position': 20486},
    'ORCL': {'loss_pct': -20, 'position': 31214},
    'CRM': {'loss_pct': -17, 'position': 26546},
    'DPZ': {'loss_pct': -16, 'position': 25707},
    'BABA': {'loss_pct': -14, 'position': 30337},
    'CMG': {'loss_pct': -14, 'position': 20309},
    'gev': {'loss_pct': -12, 'position': 6583},
    'SAP': {'loss_pct': -10, 'position': 36014},
    'META': {'loss_pct': -9, 'position': 180451},
    'STZ': {'loss_pct': -9, 'position': 18783},
    'TXRH': {'loss_pct': -7, 'position': 20666},
    'COIN': {'loss_pct': -6, 'position': 8839},
    'NVDA': {'loss_pct': -6, 'position': 61275},
    'MSFT': {'loss_pct': -5, 'position': 264312},
    'KMI': {'loss_pct': -3, 'position': 28880},
    'etn': {'loss_pct': -3, 'position': 11721},
    'EOG': {'loss_pct': -2, 'position': 13686},
    'AMZN': {'loss_pct': -2, 'position': 161198},
}

print("="*100)
print("FUNDAMENTAL ANALYSIS OF LOSING POSITIONS")
print("="*100)
print()

results = []

for ticker, info in losing_positions.items():
    print(f"\n{'='*100}")
    print(f"Analyzing: {ticker.upper()} (Loss: {info['loss_pct']}%, Position: ${info['position']:,})")
    print('='*100)

    try:
        stock = yf.Ticker(ticker)
        stock_info = stock.info

        # Basic info
        name = stock_info.get('longName', ticker)
        sector = stock_info.get('sector', 'N/A')
        industry = stock_info.get('industry', 'N/A')

        # Price data
        current_price = stock_info.get('currentPrice', stock_info.get('regularMarketPrice', 0))
        fifty_two_week_high = stock_info.get('fiftyTwoWeekHigh', 0)
        fifty_two_week_low = stock_info.get('fiftyTwoWeekLow', 0)

        # Valuation metrics
        pe_ratio = stock_info.get('trailingPE', None)
        forward_pe = stock_info.get('forwardPE', None)
        peg_ratio = stock_info.get('pegRatio', None)
        price_to_book = stock_info.get('priceToBook', None)
        price_to_sales = stock_info.get('priceToSalesTrailing12Months', None)

        # Growth metrics
        revenue_growth = stock_info.get('revenueGrowth', None)
        earnings_growth = stock_info.get('earningsGrowth', None)

        # Profitability
        profit_margin = stock_info.get('profitMargins', None)
        operating_margin = stock_info.get('operatingMargins', None)
        roe = stock_info.get('returnOnEquity', None)

        # Financial health
        total_cash = stock_info.get('totalCash', 0)
        total_debt = stock_info.get('totalDebt', 0)
        debt_to_equity = stock_info.get('debtToEquity', None)
        current_ratio = stock_info.get('currentRatio', None)
        free_cash_flow = stock_info.get('freeCashflow', 0)

        # Market data
        market_cap = stock_info.get('marketCap', 0)

        # Analyst recommendations
        recommendation = stock_info.get('recommendationKey', 'N/A')
        target_price = stock_info.get('targetMeanPrice', None)

        print(f"\nCompany: {name}")
        print(f"Sector: {sector} | Industry: {industry}")
        print(f"Market Cap: ${market_cap/1e9:.1f}B" if market_cap > 0 else "Market Cap: N/A")

        print(f"\nPrice Analysis:")
        print(f"  Current Price: ${current_price:.2f}")
        print(f"  52-Week High: ${fifty_two_week_high:.2f}" if fifty_two_week_high else "  52-Week High: N/A")
        print(f"  52-Week Low: ${fifty_two_week_low:.2f}" if fifty_two_week_low else "  52-Week Low: N/A")
        if fifty_two_week_high and current_price:
            pct_off_high = ((current_price - fifty_two_week_high) / fifty_two_week_high) * 100
            print(f"  % from 52W High: {pct_off_high:.1f}%")
        if target_price:
            upside = ((target_price - current_price) / current_price) * 100
            print(f"  Analyst Target: ${target_price:.2f} (Upside: {upside:+.1f}%)")

        print(f"\nValuation Metrics:")
        print(f"  P/E Ratio: {pe_ratio:.2f}" if pe_ratio else "  P/E Ratio: N/A (negative earnings or N/A)")
        print(f"  Forward P/E: {forward_pe:.2f}" if forward_pe else "  Forward P/E: N/A")
        print(f"  PEG Ratio: {peg_ratio:.2f}" if peg_ratio else "  PEG Ratio: N/A")
        print(f"  Price/Book: {price_to_book:.2f}" if price_to_book else "  Price/Book: N/A")
        print(f"  Price/Sales: {price_to_sales:.2f}" if price_to_sales else "  Price/Sales: N/A")

        print(f"\nGrowth Metrics:")
        print(f"  Revenue Growth: {revenue_growth*100:+.1f}%" if revenue_growth is not None else "  Revenue Growth: N/A")
        print(f"  Earnings Growth: {earnings_growth*100:+.1f}%" if earnings_growth is not None else "  Earnings Growth: N/A")

        print(f"\nProfitability:")
        print(f"  Profit Margin: {profit_margin*100:.1f}%" if profit_margin else "  Profit Margin: N/A")
        print(f"  Operating Margin: {operating_margin*100:.1f}%" if operating_margin else "  Operating Margin: N/A")
        print(f"  Return on Equity: {roe*100:.1f}%" if roe else "  ROE: N/A")

        print(f"\nFinancial Health:")
        print(f"  Total Cash: ${total_cash/1e9:.1f}B" if total_cash > 0 else "  Total Cash: N/A")
        print(f"  Total Debt: ${total_debt/1e9:.1f}B" if total_debt > 0 else "  Total Debt: N/A")
        print(f"  Debt/Equity: {debt_to_equity:.2f}" if debt_to_equity else "  Debt/Equity: N/A")
        print(f"  Current Ratio: {current_ratio:.2f}" if current_ratio else "  Current Ratio: N/A")
        print(f"  Free Cash Flow: ${free_cash_flow/1e9:.1f}B" if free_cash_flow else "  Free Cash Flow: N/A")

        print(f"\nAnalyst Recommendation: {recommendation.upper() if recommendation != 'N/A' else 'N/A'}")

        # Calculate value score
        value_score = 0
        value_reasons = []
        concerns = []

        # Score based on valuation multiples
        if pe_ratio and pe_ratio < 15:
            value_score += 2
            value_reasons.append(f"Low P/E ({pe_ratio:.1f})")
        elif pe_ratio and pe_ratio > 30:
            concerns.append(f"High P/E ({pe_ratio:.1f})")

        if peg_ratio and peg_ratio < 1:
            value_score += 2
            value_reasons.append(f"PEG < 1 ({peg_ratio:.2f})")
        elif peg_ratio and peg_ratio > 2:
            concerns.append(f"High PEG ({peg_ratio:.2f})")

        if price_to_book and price_to_book < 2:
            value_score += 1
            value_reasons.append(f"Low P/B ({price_to_book:.2f})")

        # Score based on growth
        if revenue_growth and revenue_growth > 0.15:
            value_score += 2
            value_reasons.append(f"Strong revenue growth ({revenue_growth*100:.0f}%)")
        elif revenue_growth and revenue_growth < 0:
            concerns.append(f"Negative revenue growth ({revenue_growth*100:.0f}%)")

        # Score based on profitability
        if profit_margin and profit_margin > 0.20:
            value_score += 2
            value_reasons.append(f"High margins ({profit_margin*100:.0f}%)")
        elif profit_margin and profit_margin < 0:
            concerns.append("Unprofitable")

        # Score based on financial health
        if debt_to_equity and debt_to_equity < 50:
            value_score += 1
            value_reasons.append("Low debt")
        elif debt_to_equity and debt_to_equity > 200:
            concerns.append(f"High debt/equity ({debt_to_equity:.0f})")

        if free_cash_flow and free_cash_flow > 0:
            value_score += 1
            value_reasons.append("Positive FCF")
        elif free_cash_flow and free_cash_flow < 0:
            concerns.append("Negative FCF")

        # Analyst upside
        if target_price and current_price:
            analyst_upside = ((target_price - current_price) / current_price) * 100
            if analyst_upside > 20:
                value_score += 2
                value_reasons.append(f"High analyst upside ({analyst_upside:.0f}%)")
            elif analyst_upside < -10:
                concerns.append(f"Analysts see downside ({analyst_upside:.0f}%)")

        # 52-week positioning
        if fifty_two_week_high and current_price:
            pct_off_high = ((current_price - fifty_two_week_high) / fifty_two_week_high) * 100
            if pct_off_high < -30:
                value_score += 1
                value_reasons.append(f"Down {-pct_off_high:.0f}% from high")

        print(f"\nVALUE ASSESSMENT:")
        print(f"  Value Score: {value_score}/15")
        if value_reasons:
            print(f"  Strengths: {', '.join(value_reasons)}")
        if concerns:
            print(f"  Concerns: {', '.join(concerns)}")

        # Determine verdict
        if value_score >= 10:
            verdict = "[DEEP VALUE] Strong BUY case"
        elif value_score >= 7:
            verdict = "[MODERATE VALUE] Consider holding"
        elif value_score >= 4:
            verdict = "[MIXED] Needs more analysis"
        else:
            verdict = "[NO VALUE] Consider selling"

        print(f"  Verdict: {verdict}")

        results.append({
            'ticker': ticker.upper(),
            'name': name,
            'loss_pct': info['loss_pct'],
            'position': info['position'],
            'value_score': value_score,
            'verdict': verdict,
            'pe_ratio': pe_ratio,
            'forward_pe': forward_pe,
            'peg_ratio': peg_ratio,
            'revenue_growth': revenue_growth,
            'profit_margin': profit_margin,
            'analyst_upside': analyst_upside if target_price and current_price else None,
        })

    except Exception as e:
        print(f"  [ERROR] Error analyzing {ticker}: {str(e)}")
        results.append({
            'ticker': ticker.upper(),
            'name': 'Error',
            'loss_pct': info['loss_pct'],
            'position': info['position'],
            'value_score': 0,
            'verdict': '[ERROR] Error fetching data',
        })

# Summary ranking
print("\n\n" + "="*100)
print("SUMMARY RANKING - SHOULD YOU HOLD THESE LOSERS?")
print("="*100)

df_results = pd.DataFrame(results)
df_results = df_results.sort_values('value_score', ascending=False)

print(f"\n{'Rank':<6} {'Ticker':<8} {'Loss':<8} {'Position':<12} {'Score':<8} {'Verdict':<40}")
print("-"*100)

for i, row in df_results.iterrows():
    print(f"{df_results.index.get_loc(i)+1:<6} {row['ticker']:<8} {row['loss_pct']:>+6.0f}% ${row['position']:>10,} {row['value_score']:>7}/15 {row['verdict']:<40}")

print("\n" + "="*100)
print("FINAL RECOMMENDATIONS")
print("="*100)

deep_value = df_results[df_results['value_score'] >= 10]
moderate_value = df_results[(df_results['value_score'] >= 7) & (df_results['value_score'] < 10)]
no_value = df_results[df_results['value_score'] < 4]

print(f"\n[DEEP VALUE] HOLD/ADD (Score >= 10):")
if not deep_value.empty:
    for _, row in deep_value.iterrows():
        print(f"  * {row['ticker']}: Score {row['value_score']}/15, Down {row['loss_pct']}%")
        print(f"    Position: ${row['position']:,}")
else:
    print("  * NONE - No positions show deep value characteristics")

print(f"\n[MODERATE VALUE] HOLD WITH STOPS (Score 7-9):")
if not moderate_value.empty:
    for _, row in moderate_value.iterrows():
        print(f"  * {row['ticker']}: Score {row['value_score']}/15, Down {row['loss_pct']}%")
        print(f"    Position: ${row['position']:,}")
        print(f"    Recommendation: Hold but set -10% stop-loss")
else:
    print("  * NONE")

print(f"\n[NO VALUE] SELL NOW (Score < 4):")
if not no_value.empty:
    total_to_exit = no_value['position'].sum()
    for _, row in no_value.iterrows():
        print(f"  * {row['ticker']}: Score {row['value_score']}/15, Down {row['loss_pct']}%")
        print(f"    Position: ${row['position']:,}")
    print(f"\n  Total to exit: ${total_to_exit:,}")
else:
    print("  * NONE")

print("\n" + "="*100)
print(f"Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*100)
