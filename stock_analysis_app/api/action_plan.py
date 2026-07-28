"""
Potential Scenario Analysis
Combines fundamental and technical analysis to present potential trading scenarios
for educational purposes only - not personalized investment advice
"""

import sys
from pathlib import Path
from datetime import datetime
import yfinance as yf

# Add parent directories to path
tech_analysis_path = Path(__file__).parent.parent.parent / 'technical_analysis'
sys.path.insert(0, str(tech_analysis_path))
sys.path.insert(0, str(tech_analysis_path / 'scripts'))

# Import PDF converter
utils_path = Path(__file__).parent.parent.parent / 'utils'
sys.path.insert(0, str(utils_path))
from md_to_pdf import convert_md_to_pdf

from lib.techinical_factor import TechnicalFactors
from trend_analyzer import TrendAnalyzer


def generate_action_plan(ticker: str) -> dict:
    """
    Generate next action plan by combining fundamental and technical insights

    Args:
        ticker: Stock ticker symbol

    Returns:
        dict with report path and metadata
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Fetch stock data with error handling
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period='1y')
    except Exception as e:
        error_msg = f"WARNING: Failed to fetch data from Yahoo Finance for {ticker}\n"
        error_msg += f"Error details: {str(e)}\n"
        error_msg += "Possible causes:\n"
        error_msg += "  - Network connection issue\n"
        error_msg += "  - Invalid ticker symbol\n"
        error_msg += "  - Yahoo Finance API temporarily unavailable\n"
        error_msg += f"  - Ticker {ticker} may be delisted or not found\n"
        print(error_msg)
        raise Exception(error_msg)

    if hist.empty:
        error_msg = f"WARNING: No historical data available for {ticker}\n"
        error_msg += "This could mean:\n"
        error_msg += f"  - Ticker symbol '{ticker}' is invalid or not recognized by Yahoo Finance\n"
        error_msg += "  - Stock may be delisted or suspended from trading\n"
        error_msg += "  - IPO is too recent (less than 1 year of data)\n"
        error_msg += "\nPlease verify the ticker symbol and try again.\n"
        print(error_msg)
        raise Exception(error_msg)

    # Get current price
    current_price = hist['Close'].iloc[-1]

    # Calculate technical factors
    import pandas as pd
    df = pd.DataFrame({
        'symbol': ticker,
        'date': hist.index,
        'open': hist['Open'],
        'high': hist['High'],
        'low': hist['Low'],
        'close': hist['Close'],
        'adjusted_close': hist['Close'],
        'volume': hist['Volume']
    })
    df['date'] = pd.to_datetime(df['date'])

    tf = TechnicalFactors(df, price_col='adjusted_close', volume_col='volume')
    df_with_factors = tf.run_all(include_high_low_indicators=True)

    # Analyze trends
    analyzer = TrendAnalyzer(df_with_factors)
    trend = analyzer.analyze_trend_direction()
    volatility = analyzer.analyze_volatility()
    volume = analyzer.analyze_volume()
    signals = analyzer.generate_trading_signals()
    levels = analyzer.identify_key_levels()

    # Generate action plan
    action_plan = generate_action_plan_content(
        ticker, current_price, info, trend, volatility, volume, signals, levels
    )

    # Save to file
    reports_dir = Path(__file__).parent.parent / 'reports'
    reports_dir.mkdir(exist_ok=True)

    filename = f'{ticker}_action_plan_{timestamp}.md'
    filepath = reports_dir / filename

    with open(filepath, 'w') as f:
        f.write(action_plan)

    # Generate PDF
    pdf_filename = f'{ticker}_action_plan_{timestamp}.pdf'
    pdf_filepath = reports_dir / pdf_filename
    convert_md_to_pdf(str(filepath), str(pdf_filepath))

    return {
        'ticker': ticker,
        'type': 'action_plan',
        'path': str(filepath),
        'filename': filename,
        'pdf_path': str(pdf_filepath),
        'pdf_filename': pdf_filename,
        'timestamp': timestamp
    }


def generate_action_plan_content(ticker, current_price, info, trend, volatility, volume, signals, levels):
    """Generate the action plan markdown content"""

    # Get 52-week range
    fifty_two_week_low = info.get('fiftyTwoWeekLow', 'N/A')
    fifty_two_week_high = info.get('fiftyTwoWeekHigh', 'N/A')

    # Calculate position in range
    if fifty_two_week_low != 'N/A' and fifty_two_week_high != 'N/A':
        range_position = ((current_price - fifty_two_week_low) /
                         (fifty_two_week_high - fifty_two_week_low) * 100)
    else:
        range_position = None

    # Determine overall recommendation
    recommendation = determine_recommendation(trend, signals, range_position)

    content = f"""# {ticker} - Potential Scenario Analysis

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Current Price**: ${current_price:.2f}
**Potential Scenario**: **{recommendation['action']}**

> **IMPORTANT NOTE**: This analysis presents potential scenarios based on technical indicators and historical data. These are hypothetical scenarios for educational purposes only and do not constitute personalized investment recommendations. See full disclaimer at the end of this report.

---

## Executive Summary

{recommendation['summary']}

---

## Current Market Position

### Price Location
- **Current Price**: ${current_price:.2f}
- **52-Week Range**: ${fifty_two_week_low:.2f} - ${fifty_two_week_high:.2f}
"""

    if range_position is not None:
        content += f"- **Position in Range**: {range_position:.1f}% ({get_range_description(range_position)})\n"

    content += f"""
### Trend Analysis
- **Direction**: {trend['direction']}
- **Strength**: {trend['strength']}/10
- **Score**: {trend['score']:+d}

### Volatility
- **Level**: {volatility['level']}
"""
    if volatility['annualized_pct']:
        content += f"- **Annualized Volatility**: {volatility['annualized_pct']:.2f}%\n"

    content += f"""
### Volume
- **Relative Volume**: {volume['relative']:.2f}x ({volume['level']})
- **Trend**: {volume['trend']}

---

## Key Levels

### Support Levels (Buy Zones)
"""
    if levels['support']:
        for i, s in enumerate(levels['support'][:3], 1):
            content += f"{i}. **${s['level']:.2f}** ({s['type']}) - {s['distance_pct']:.2f}% below current\n"
    else:
        content += "No clear support levels identified\n"

    content += "\n### Resistance Levels (Sell Zones)\n"
    if levels['resistance']:
        for i, r in enumerate(levels['resistance'][:3], 1):
            content += f"{i}. **${r['level']:.2f}** ({r['type']}) - {r['distance_pct']:.2f}% above current\n"
    else:
        content += "No clear resistance levels identified\n"

    content += f"""
---

## Trading Signals

"""
    for i, signal in enumerate(signals, 1):
        content += f"""### Signal #{i}: {signal['action']}
- **Confidence**: {signal['confidence']}
- **Reason**: {signal['reason']}
"""
        if signal['details']:
            content += "- **Details**:\n"
            for detail in signal['details']:
                content += f"  - {detail}\n"
        content += "\n"

    content += f"""---

## Potential Action Scenarios

{recommendation['action_items']}

---

## Risk Management Considerations

### Potential Entry Strategy
{recommendation['entry_strategy']}

### Potential Position Sizing
{recommendation['position_sizing']}

### Potential Stop Loss
{recommendation['stop_loss']}

### Potential Take Profit Targets
{recommendation['take_profit']}

---

## Monitoring Checklist

Daily:
- [ ] Check if price breaks key support/resistance levels
- [ ] Monitor volume for unusual activity
- [ ] Watch for news or earnings announcements

Weekly:
- [ ] Review trend direction changes
- [ ] Reassess technical signals
- [ ] Update support/resistance levels

Monthly:
- [ ] Review fundamental changes
- [ ] Adjust position size based on portfolio allocation
- [ ] Reassess investment thesis

---

## IMPORTANT LEGAL DISCLAIMER

**EDUCATIONAL PURPOSE ONLY**: This report is provided for educational and informational purposes only. It is not intended to provide, and should not be relied upon for, investment, financial, legal, or tax advice.

**NOT PERSONALIZED ADVICE**: This analysis does not take into account your personal financial situation, investment objectives, risk tolerance, or specific needs. It is based solely on publicly available data and standardized technical analysis algorithms.

**NO GUARANTEE OF PERFORMANCE**: Past performance is not indicative of future results. No guarantee, representation, or warranty is made that any analysis, strategy, or recommendation will be profitable, suitable for your situation, or will not result in losses. Historical patterns may not repeat.

**SUBSTANTIAL RISK OF LOSS**: Trading stocks and securities involves substantial risk of loss and is not suitable for all investors. You should only invest money that you can afford to lose entirely. Market conditions can change rapidly and without warning.

**USER RESPONSIBILITY**: You are solely and exclusively responsible for your own investment and trading decisions. This report does not constitute a recommendation to buy, sell, or hold any security. Always conduct your own thorough research and due diligence.

**PROFESSIONAL CONSULTATION REQUIRED**: Before making any investment decision, you should consult with licensed and qualified financial advisors, tax professionals, and/or legal counsel who can provide advice tailored to your specific circumstances.

**NO GUARANTEE OF ACCURACY**: While we strive for accuracy, we make no representations or warranties regarding the accuracy, completeness, or timeliness of the information provided. Data sources may contain errors or be outdated.

**BY USING THIS REPORT, YOU ACKNOWLEDGE AND AGREE**: That you have read, understood, and accept all terms of this disclaimer, and that you will not hold the creators, operators, or distributors of this tool liable for any losses or damages resulting from your use of this information.

---

**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Tool**: Stock Analysis Web Application v1.0
**For Educational Purposes Only - Not Financial Advice**
"""

    return content


def determine_recommendation(trend, signals, range_position):
    """Determine overall recommendation based on analysis"""

    # Default recommendation
    rec = {
        'action': 'HOLD',
        'summary': '',
        'action_items': '',
        'entry_strategy': '',
        'position_sizing': '',
        'stop_loss': '',
        'take_profit': ''
    }

    # Check primary signal
    primary_signal = signals[0] if signals else None

    if not primary_signal:
        rec['summary'] = "No clear trading setup identified based on current technical indicators. In this scenario, waiting for better clarity would be prudent."
        rec['action_items'] = "In this uncertain scenario, one might:\n- Monitor for trend development\n- Wait for clearer technical signals\n- Review company fundamentals"
        rec['entry_strategy'] = "In this scenario, remaining on the sidelines until a clearer setup emerges would be a potential approach"
        rec['position_sizing'] = "In this scenario, holding off on position sizing until signals clarify"
        rec['stop_loss'] = "N/A - No active position scenario"
        rec['take_profit'] = "N/A - No active position scenario"
        return rec

    # Buy signals
    if primary_signal['action'] == 'BUY':
        rec['action'] = 'POTENTIAL BUY SCENARIO'
        rec['summary'] = f"Technical indicators suggest: {primary_signal['reason']}. "

        if range_position and range_position < 30:
            rec['summary'] += f"Stock is in the lower third of its 52-week range ({range_position:.1f}%), potentially good entry point."
        elif range_position and range_position > 70:
            rec['summary'] += f"Stock is in the upper third of its 52-week range ({range_position:.1f}%), consider waiting for pullback."

        rec['action_items'] = """In a buy scenario, one might consider:
1. **Position Building** - Potentially start building position at current levels
2. **Entry Monitoring** - Could use support levels for better entry if price dips
3. **Catalyst Awareness** - Be aware of upcoming earnings or events
4. **Alert Setting** - Place price alerts at key support/resistance levels"""

        rec['entry_strategy'] = """Potential approaches in this scenario:
- **Gradual Entry**: Consider entering 30-50% of planned position at current price
- **Scale-in Approach**: Could add remaining 50-70% at next support level if price dips
- **Aggressive Entry**: Full position only if high confidence and strong bullish signals"""

        rec['position_sizing'] = """Example position sizes (for reference only):
- Conservative scenario: 2-3% of portfolio
- Moderate scenario: 3-5% of portfolio
- Aggressive scenario: 5-7% of portfolio (only with strong conviction)"""

        rec['stop_loss'] = "In this scenario, a potential stop loss might be placed 5-8% below entry or below nearest support level"
        rec['take_profit'] = "Potential profit targets might include next resistance level or 10-15% gain, with consideration for trailing stop"

    # Sell signals
    elif primary_signal['action'] == 'SELL':
        rec['action'] = 'POTENTIAL SELL SCENARIO'
        rec['summary'] = f"Technical indicators suggest: {primary_signal['reason']}. "

        if range_position and range_position > 70:
            rec['summary'] += f"Stock is in the upper third of its 52-week range ({range_position:.1f}%), good time to take profits."
        elif range_position and range_position < 30:
            rec['summary'] += f"Stock is in the lower third of its 52-week range ({range_position:.1f}%), exercise caution before selling."

        rec['action_items'] = """In a sell scenario, one might consider:
1. **Exposure Reduction** - Potentially reduce or exit existing position
2. **Profit Protection** - If in profit, consider taking some gains off the table
3. **Stop Tightening** - Could move stop losses closer to current price
4. **Entry Avoidance** - Avoid adding to position at current levels"""

        rec['entry_strategy'] = "In this scenario, one might avoid initiating new positions and wait for trend reversal confirmation."

        rec['position_sizing'] = """Potential position adjustments (for reference):
- If holding: Consider reducing to 1-2% of portfolio or exiting completely
- If not holding: Avoid entering in this scenario"""

        rec['stop_loss'] = "In this scenario, if holding, one might tighten stop to 3-5% below current price"
        rec['take_profit'] = "Could consider profit-taking if currently in gains"

    # Hold signals
    else:
        rec['action'] = 'WAIT & MONITOR SCENARIO'
        rec['summary'] = "Mixed technical signals. No clear directional bias. Potential scenario: wait for confirmation."

        rec['action_items'] = """In this neutral scenario, one might:
1. **Exercise Patience** - Wait for clearer technical setup to emerge
2. **Monitor Developments** - Watch for potential breakout or breakdown
3. **Prepare Multiple Scenarios** - Have plans ready for both bullish and bearish moves
4. **Review Company Fundamentals** - Use this time to deep-dive into company analysis"""

        rec['entry_strategy'] = "In this scenario, waiting for trend clarity would be prudent. Consider setting alerts at key breakout/breakdown levels."

        rec['position_sizing'] = """Potential approach (for reference):
- If holding: Consider maintaining current position
- If not holding: Wait for better entry opportunity to emerge"""

        rec['stop_loss'] = "If holding, one might maintain stop at 7-10% below entry or support level"
        rec['take_profit'] = "If holding, could consider taking partial profits at resistance levels"

    return rec


def get_range_description(position):
    """Get description of position in 52-week range"""
    if position < 20:
        return "Near 52-week low"
    elif position < 40:
        return "Lower third of range"
    elif position < 60:
        return "Middle of range"
    elif position < 80:
        return "Upper third of range"
    else:
        return "Near 52-week high"
