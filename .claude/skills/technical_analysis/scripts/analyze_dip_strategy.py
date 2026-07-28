"""
Analyze the effectiveness of buying SMH on every 5% dip
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def analyze_dip_buying_strategy(ticker: str, dip_threshold: float = 0.05, lookback_years: int = 2):
    """
    Analyze how often a stock drops by dip_threshold and the recovery patterns

    Args:
        ticker: Stock symbol
        dip_threshold: Percentage drop to trigger buy (default 5% = 0.05)
        lookback_years: Years of historical data to analyze
    """
    print(f"\n{'='*80}")
    print(f"DIP BUYING STRATEGY ANALYSIS: {ticker}")
    print(f"Strategy: Buy every time price drops {dip_threshold*100}% from recent high")
    print(f"{'='*80}\n")

    # Fetch data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_years*365)

    print(f"Fetching {lookback_years} years of data...")
    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=end_date)

    if df.empty:
        print(f"[ERROR] No data found for {ticker}")
        return

    print(f"[OK] Fetched {len(df)} trading days")
    print(f"Date range: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"Price range: ${df['Close'].min():.2f} - ${df['Close'].max():.2f}\n")

    # Calculate rolling high and drawdown from high
    df['rolling_high'] = df['Close'].expanding().max()
    df['drawdown'] = (df['Close'] - df['rolling_high']) / df['rolling_high']

    # Identify buy signals (when drawdown crosses below -threshold)
    df['buy_signal'] = (df['drawdown'] <= -dip_threshold) & (df['drawdown'].shift(1) > -dip_threshold)

    buy_dates = df[df['buy_signal']].index
    num_signals = len(buy_dates)

    print(f"{'='*80}")
    print(f"BUY SIGNAL FREQUENCY")
    print(f"{'='*80}")
    print(f"Total buy signals: {num_signals}")
    print(f"Frequency: {num_signals / (lookback_years * 12):.1f} signals per month")
    print(f"Average days between signals: {len(df) / max(num_signals, 1):.0f} days\n")

    # Analyze recovery patterns
    recovery_stats = []

    for buy_date in buy_dates:
        buy_price = df.loc[buy_date, 'Close']
        buy_high = df.loc[buy_date, 'rolling_high']
        drawdown = df.loc[buy_date, 'drawdown']

        # Find future prices
        future_df = df[df.index > buy_date]

        if len(future_df) == 0:
            continue

        # Calculate returns after 1 day, 5 days, 20 days, 60 days
        returns = {}
        for days in [1, 5, 20, 60]:
            if len(future_df) >= days:
                future_price = future_df.iloc[days-1]['Close']
                returns[f'{days}d'] = (future_price - buy_price) / buy_price
            else:
                returns[f'{days}d'] = None

        # Days to recovery (price back above buy price)
        recovery_days = None
        for i, future_price in enumerate(future_df['Close']):
            if future_price >= buy_high:
                recovery_days = i + 1
                break

        recovery_stats.append({
            'date': buy_date.date(),
            'buy_price': buy_price,
            'drawdown': drawdown,
            '1d_return': returns['1d'],
            '5d_return': returns['5d'],
            '20d_return': returns['20d'],
            '60d_return': returns['60d'],
            'recovery_days': recovery_days
        })

    recovery_df = pd.DataFrame(recovery_stats)

    if len(recovery_df) == 0:
        print("[WARNING] No buy signals found in this period\n")
        return

    print(f"{'='*80}")
    print(f"RETURN ANALYSIS AFTER BUY SIGNALS")
    print(f"{'='*80}\n")

    for period in ['1d', '5d', '20d', '60d']:
        returns_col = f'{period}_return'
        valid_returns = recovery_df[returns_col].dropna()

        if len(valid_returns) == 0:
            continue

        avg_return = valid_returns.mean()
        median_return = valid_returns.median()
        win_rate = (valid_returns > 0).sum() / len(valid_returns)
        best = valid_returns.max()
        worst = valid_returns.min()

        print(f"{period.upper()} Returns:")
        print(f"  Average: {avg_return*100:+.2f}%")
        print(f"  Median:  {median_return*100:+.2f}%")
        print(f"  Win Rate: {win_rate*100:.1f}%")
        print(f"  Best: {best*100:+.2f}%")
        print(f"  Worst: {worst*100:+.2f}%")
        print()

    # Recovery time analysis
    valid_recovery = recovery_df['recovery_days'].dropna()
    if len(valid_recovery) > 0:
        print(f"RECOVERY TIME (back to pre-dip high):")
        print(f"  Average: {valid_recovery.mean():.0f} days")
        print(f"  Median:  {valid_recovery.median():.0f} days")
        print(f"  Recovery rate: {len(valid_recovery)/len(recovery_df)*100:.1f}% ({len(valid_recovery)}/{len(recovery_df)} signals)")
        print(f"  Did not recover: {len(recovery_df) - len(valid_recovery)} signals\n")

    # Recent signals
    print(f"{'='*80}")
    print(f"LAST 5 BUY SIGNALS")
    print(f"{'='*80}\n")

    recent = recovery_df.tail(5)
    for _, row in recent.iterrows():
        print(f"Date: {row['date']}")
        print(f"  Buy Price: ${row['buy_price']:.2f} (drawdown: {row['drawdown']*100:.1f}%)")
        if pd.notna(row['20d_return']):
            print(f"  20-day return: {row['20d_return']*100:+.2f}%")
        if pd.notna(row['recovery_days']):
            print(f"  Recovered in: {row['recovery_days']:.0f} days")
        else:
            print(f"  Recovered: Not yet")
        print()

    # Risk analysis
    print(f"{'='*80}")
    print(f"RISK ANALYSIS")
    print(f"{'='*80}\n")

    # Maximum drawdown after buy signal
    max_drawdown_after_buy = []
    for buy_date in buy_dates:
        buy_price = df.loc[buy_date, 'Close']
        future_df = df[df.index > buy_date].head(60)  # Next 60 days

        if len(future_df) > 0:
            min_price = future_df['Close'].min()
            drawdown = (min_price - buy_price) / buy_price
            max_drawdown_after_buy.append(drawdown)

    if max_drawdown_after_buy:
        print(f"Maximum drawdown AFTER buying the dip (within 60 days):")
        print(f"  Average: {sum(max_drawdown_after_buy)/len(max_drawdown_after_buy)*100:.2f}%")
        print(f"  Worst: {min(max_drawdown_after_buy)*100:.2f}% (catching falling knife risk)")
        print(f"  Best: {max(max_drawdown_after_buy)*100:+.2f}%\n")

    # Current status
    current_price = df['Close'].iloc[-1]
    current_high = df['rolling_high'].iloc[-1]
    current_drawdown = df['drawdown'].iloc[-1]

    print(f"{'='*80}")
    print(f"CURRENT STATUS")
    print(f"{'='*80}\n")
    print(f"Current Price: ${current_price:.2f}")
    print(f"Recent High: ${current_high:.2f}")
    print(f"Current Drawdown: {current_drawdown*100:.2f}%")

    if current_drawdown <= -dip_threshold:
        print(f"\n[SIGNAL] BUY SIGNAL ACTIVE - Price is down {abs(current_drawdown)*100:.1f}% from high")
    else:
        print(f"\n[INFO] No signal - Need {(abs(current_drawdown) - dip_threshold)*100:.2f}% more drop to trigger")

    print(f"\n{'='*80}")
    print(f"CONCLUSION")
    print(f"{'='*80}\n")

    avg_20d = recovery_df['20d_return'].mean()
    win_rate_20d = (recovery_df['20d_return'].dropna() > 0).sum() / len(recovery_df['20d_return'].dropna())

    print(f"Buying {ticker} on every {dip_threshold*100}% dip:")
    print(f"  Frequency: {num_signals / (lookback_years * 12):.1f} signals/month")
    print(f"  20-day average return: {avg_20d*100:+.2f}%")
    print(f"  20-day win rate: {win_rate_20d*100:.1f}%")

    if avg_20d > 0.02 and win_rate_20d > 0.6:
        print(f"\n  [OK] Strategy shows positive returns")
    elif num_signals / lookback_years > 12:
        print(f"\n  [WARNING] TOO FREQUENT - May lead to overconcentration")
    else:
        print(f"\n  [WARNING] Strategy shows mixed results")

if __name__ == "__main__":
    import sys

    ticker = sys.argv[1] if len(sys.argv) > 1 else "SMH"
    dip_pct = float(sys.argv[2]) / 100 if len(sys.argv) > 2 else 0.05
    years = int(sys.argv[3]) if len(sys.argv) > 3 else 2

    analyze_dip_buying_strategy(ticker, dip_pct, years)
