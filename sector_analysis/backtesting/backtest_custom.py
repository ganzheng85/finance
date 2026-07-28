"""
Custom Sector Rotation Backtest Script

Usage:
    python backtest_custom.py --top N --strategy STRATEGY --start YYYY-MM-DD --end YYYY-MM-DD

Arguments:
    --top         : Number of top sectors (3 or 5)
    --strategy    : Risk management strategy (base, trailing15, hard25, regime)
    --start       : Start date (YYYY-MM-DD)
    --end         : End date (YYYY-MM-DD)

Examples:
    # Test Top 3 with base strategy for 2025
    python backtest_custom.py --top 3 --strategy base --start 2025-01-01 --end 2025-12-31

    # Test Top 5 with market regime for H1 2025
    python backtest_custom.py --top 5 --strategy regime --start 2025-01-01 --end 2025-06-01
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from calculate_sector_metrics import (
    calculate_relative_strength,
    calculate_momentum,
    rank_sectors
)

# Configuration
INITIAL_CAPITAL = 100000
TRANSACTION_COST_PCT = 0.0  # Set to 0 to ignore transaction costs
TRAILING_STOP_15 = 0.15
TRAILING_STOP_25 = 0.25

SECTOR_ETFS = {
    'XLK': 'Technology',
    'XLV': 'Healthcare',
    'XLF': 'Financials',
    'XLY': 'Consumer Discretionary',
    'XLI': 'Industrials',
    'XLP': 'Consumer Staples',
    'XLE': 'Energy',
    'XLU': 'Utilities',
    'XLB': 'Materials',
    'XLRE': 'Real Estate',
    'XLC': 'Communication Services',
    'MAGS': 'Magnificent 7',
    'SMH': 'Semiconductors',
    'IGV': 'Software'
}


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Custom Sector Rotation Backtest',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Top 3, base strategy, full 2025
  python backtest_custom.py --top 3 --strategy base --start 2025-01-01 --end 2025-12-31

  # Top 5, market regime, H1 2025
  python backtest_custom.py --top 5 --strategy regime --start 2025-01-01 --end 2025-06-01

  # Top 3, trailing 15% stop, custom period
  python backtest_custom.py --top 3 --strategy trailing15 --start 2024-06-01 --end 2025-06-01
        """
    )

    parser.add_argument('--top', type=int, required=True, choices=[3, 5],
                        help='Number of top sectors to invest in (3 or 5)')

    parser.add_argument('--strategy', type=str, required=True,
                        choices=['base', 'trailing15', 'hard25', 'regime'],
                        help='Risk management strategy: base (no stops), trailing15 (15%% stop), hard25 (25%% stop), regime (SPY 200MA)')

    parser.add_argument('--start', type=str, required=True,
                        help='Start date (YYYY-MM-DD)')

    parser.add_argument('--end', type=str, required=True,
                        help='End date (YYYY-MM-DD)')

    return parser.parse_args()


def run_backtest(top_n, strategy, start_date, end_date):
    """
    Run backtest with specified parameters

    Parameters
    ----------
    top_n : int
        Number of top sectors (3 or 5)
    strategy : str
        Risk management strategy
    start_date : datetime
        Backtest start date
    end_date : datetime
        Backtest end date
    """

    print("\n" + "="*80)
    print("CUSTOM SECTOR ROTATION BACKTEST")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Top Sectors: {top_n}")
    print(f"  Strategy: {strategy}")
    print(f"  Period: {start_date.date()} to {end_date.date()}")
    print(f"  Initial Capital: ${INITIAL_CAPITAL:,.0f}")
    print(f"  Transaction Cost: {TRANSACTION_COST_PCT*100:.2f}%")

    # Strategy description
    strategy_desc = {
        'base': 'Always invested (no stops)',
        'trailing15': '50% cash if down -15% from peak',
        'hard25': '100% cash if down -25% from peak',
        'regime': '50% cash when SPY < 200-day MA'
    }
    print(f"  Strategy Detail: {strategy_desc[strategy]}")

    # Fetch data (extra for lookback calculations)
    data_start = start_date - timedelta(days=400)

    print(f"\nFetching data from {data_start.date()} to {end_date.date()}...")

    all_tickers = list(SECTOR_ETFS.keys()) + ['SPY']
    sector_data = {}

    for ticker in all_tickers:
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=data_start, end=end_date)
            if not data.empty:
                sector_data[ticker] = data['Close']
                print(f"  {ticker}: {len(data)} days")
        except Exception as e:
            print(f"  {ticker}: ERROR - {str(e)}")

    df_prices = pd.DataFrame(sector_data)
    df_prices.index = df_prices.index.tz_localize(None)

    # Filter out sectors with insufficient data for the backtest period
    # Require at least 80% data coverage during backtest period
    backtest_range = df_prices[df_prices.index >= start_date]
    min_required_days = int(len(backtest_range) * 0.8)

    valid_sectors = []
    excluded_sectors = []

    for ticker in SECTOR_ETFS.keys():
        if ticker in df_prices.columns:
            # Count non-NaN values in backtest period
            valid_days = backtest_range[ticker].notna().sum()
            if valid_days >= min_required_days:
                valid_sectors.append(ticker)
            else:
                excluded_sectors.append(f"{ticker} ({valid_days}/{len(backtest_range)} days)")

    if excluded_sectors:
        print(f"\n[INFO] Excluding sectors with insufficient data:")
        for sector in excluded_sectors:
            print(f"  - {sector}")
        print(f"\n[OK] Using {len(valid_sectors)} sectors with sufficient data")

    # Keep only valid sectors + SPY
    valid_tickers = valid_sectors + ['SPY']
    df_prices = df_prices[valid_tickers].copy()

    # Now drop rows where SPY is NaN (we need SPY for benchmarking)
    df_prices = df_prices.dropna(subset=['SPY'])

    print(f"\n[OK] Fetched {len(df_prices)} days of data for {len(valid_sectors)} sectors + SPY")

    # Create sector dataframe (only include non-NaN data for each sector)
    sector_df = pd.DataFrame()
    for ticker in valid_sectors:
        if ticker in df_prices.columns:
            # Only include dates where this sector has valid data
            sector_prices = df_prices[ticker].dropna()
            temp_df = pd.DataFrame({
                'date': sector_prices.index,
                'ticker': ticker,
                'sector_name': SECTOR_ETFS[ticker],
                'adjusted_close': sector_prices.values
            })
            sector_df = pd.concat([sector_df, temp_df], ignore_index=True)

    spy_df = pd.DataFrame({
        'date': df_prices.index,
        'ticker': 'SPY',
        'sector_name': 'S&P 500',
        'adjusted_close': df_prices['SPY'].values
    })
    sector_df = pd.concat([sector_df, spy_df], ignore_index=True)

    # Calculate SPY 200-day MA
    df_prices['SPY_MA200'] = df_prices['SPY'].rolling(window=200).mean()

    # Get rebalancing dates (weekly)
    backtest_start = start_date
    all_dates = df_prices.index[df_prices.index >= backtest_start]

    rebal_dates = []
    for date in all_dates:
        week_num = date.isocalendar()[1]
        next_day = date + timedelta(days=1)
        if next_day not in all_dates or next_day.isocalendar()[1] != week_num:
            rebal_dates.append(date)

    print(f"[OK] Identified {len(rebal_dates)} weekly rebalancing dates")

    # Initialize portfolio
    portfolio = {
        'cash': INITIAL_CAPITAL,
        'positions': {},
        'value_history': [],
        'date_history': [],
        'holdings_history': [],
        'peak_value': INITIAL_CAPITAL,
        'cash_pct': 0.0,
        'stopped_out': False,
        'trades': []
    }

    # SPY benchmark
    spy_benchmark = {
        'shares': INITIAL_CAPITAL / df_prices.loc[rebal_dates[0], 'SPY'],
        'value_history': [],
        'date_history': []
    }

    print(f"[OK] Initialized portfolio with ${INITIAL_CAPITAL:,.0f}")
    print(f"[OK] SPY benchmark: {spy_benchmark['shares']:.2f} shares at ${df_prices.loc[rebal_dates[0], 'SPY']:.2f}")

    print("\n" + "="*80)
    print("RUNNING BACKTEST...")
    print("="*80)

    # Suppress verbose output from sector calculations
    import io
    import contextlib

    # Run backtest
    for i, rebal_date in enumerate(rebal_dates):
        # Get historical data
        historical_data = sector_df[sector_df['date'] <= rebal_date].copy()

        # Calculate metrics and rank (suppress print statements)
        with contextlib.redirect_stdout(io.StringIO()):
            historical_data = calculate_relative_strength(historical_data)
            historical_data = calculate_momentum(historical_data)
            sector_only = historical_data[historical_data['ticker'] != 'SPY'].copy()
            rankings = rank_sectors(sector_only)

        # Get top N sectors
        top_sectors = rankings.head(top_n)['ticker'].tolist()

        # Safety check: ensure we have sectors to invest in
        if len(top_sectors) == 0:
            print(f"  [WARNING] No valid sectors available on {rebal_date.date()}, staying in cash")

        # Calculate current portfolio value
        portfolio_value = portfolio['cash']
        for ticker, shares in portfolio['positions'].items():
            if ticker in df_prices.columns:
                portfolio_value += shares * df_prices.loc[rebal_date, ticker]

        # Update peak value
        if portfolio_value > portfolio['peak_value']:
            portfolio['peak_value'] = portfolio_value

        # Calculate drawdown from peak
        drawdown = (portfolio_value - portfolio['peak_value']) / portfolio['peak_value']

        # Determine cash allocation based on strategy
        if strategy == 'base':
            target_cash_pct = 0.0

        elif strategy == 'trailing15':
            if drawdown <= -TRAILING_STOP_15 and not portfolio['stopped_out']:
                target_cash_pct = 0.50
                portfolio['stopped_out'] = True
            elif drawdown >= -0.05:  # Reset when recovered to -5%
                target_cash_pct = 0.0
                portfolio['stopped_out'] = False
            else:
                target_cash_pct = portfolio['cash_pct']

        elif strategy == 'hard25':
            if drawdown <= -TRAILING_STOP_25 and not portfolio['stopped_out']:
                target_cash_pct = 1.0
                portfolio['stopped_out'] = True
            elif drawdown >= -0.05:  # Reset when recovered to -5%
                target_cash_pct = 0.0
                portfolio['stopped_out'] = False
            else:
                target_cash_pct = portfolio['cash_pct']

        elif strategy == 'regime':
            spy_price = df_prices.loc[rebal_date, 'SPY']
            spy_ma200 = df_prices.loc[rebal_date, 'SPY_MA200']
            bull_market = spy_price > spy_ma200 if not pd.isna(spy_ma200) else True
            target_cash_pct = 0.0 if bull_market else 0.50

        portfolio['cash_pct'] = target_cash_pct

        # Calculate SPY benchmark value
        spy_value = spy_benchmark['shares'] * df_prices.loc[rebal_date, 'SPY']

        # Record values
        portfolio['value_history'].append(portfolio_value)
        portfolio['date_history'].append(rebal_date)
        portfolio['holdings_history'].append(top_sectors.copy())

        spy_benchmark['value_history'].append(spy_value)
        spy_benchmark['date_history'].append(rebal_date)

        # Rebalance portfolio - liquidate everything to cash first
        # Sell all current positions
        for ticker in list(portfolio['positions'].keys()):
            shares = portfolio['positions'][ticker]
            if shares > 0:
                price = df_prices.loc[rebal_date, ticker]
                proceeds = shares * price
                cost = proceeds * TRANSACTION_COST_PCT
                portfolio['cash'] += proceeds - cost

                portfolio['trades'].append({
                    'date': rebal_date,
                    'action': 'SELL',
                    'ticker': ticker,
                    'shares': shares,
                    'price': price,
                    'value': proceeds,
                    'cost': cost
                })

        # Clear all positions
        portfolio['positions'] = {}

        # Calculate amount to invest (after keeping target cash %)
        cash_to_invest = portfolio['cash'] * (1 - target_cash_pct)

        if cash_to_invest > 100 and len(top_sectors) > 0:  # Only invest if meaningful amount and have sectors
            # Buy top N sectors with equal weight
            equal_weight = 1.0 / len(top_sectors)  # Use actual number of sectors available
            target_value_per_sector = cash_to_invest * equal_weight

            for ticker in top_sectors:
                price = df_prices.loc[rebal_date, ticker]
                shares_to_buy = target_value_per_sector / price

                portfolio['positions'][ticker] = shares_to_buy

                portfolio['trades'].append({
                    'date': rebal_date,
                    'action': 'BUY',
                    'ticker': ticker,
                    'shares': shares_to_buy,
                    'price': price,
                    'value': target_value_per_sector,
                    'cost': target_value_per_sector * TRANSACTION_COST_PCT
                })

            # Deduct invested amount from cash (not just set to percentage)
            total_transaction_costs = cash_to_invest * TRANSACTION_COST_PCT
            portfolio['cash'] = portfolio['cash'] - cash_to_invest

        # Progress update
        if i % 5 == 0 or i == len(rebal_dates) - 1:
            pct_complete = (i + 1) / len(rebal_dates) * 100
            cash_status = f"({target_cash_pct*100:.0f}% cash)" if target_cash_pct > 0 else ""
            print(f"  Week {i+1}/{len(rebal_dates)} ({pct_complete:.0f}%) - {rebal_date.date()} - ${portfolio_value:,.0f} {cash_status}")

    print("\n[OK] Backtest complete!")

    # Calculate performance metrics
    portfolio_returns = pd.Series(portfolio['value_history'], index=portfolio['date_history'])
    spy_returns = pd.Series(spy_benchmark['value_history'], index=spy_benchmark['date_history'])

    final_portfolio_value = portfolio_returns.iloc[-1]
    final_spy_value = spy_returns.iloc[-1]

    portfolio_return_pct = ((final_portfolio_value - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
    spy_return_pct = ((final_spy_value - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
    alpha = portfolio_return_pct - spy_return_pct

    # Calculate annualized returns
    days_elapsed = (rebal_dates[-1] - rebal_dates[0]).days
    years_elapsed = days_elapsed / 365.25
    portfolio_annual_return = ((final_portfolio_value / INITIAL_CAPITAL) ** (1/years_elapsed) - 1) * 100
    spy_annual_return = ((final_spy_value / INITIAL_CAPITAL) ** (1/years_elapsed) - 1) * 100

    # Calculate volatility
    portfolio_daily_returns = portfolio_returns.pct_change().dropna()
    spy_daily_returns = spy_returns.pct_change().dropna()

    portfolio_volatility = portfolio_daily_returns.std() * np.sqrt(252) * 100
    spy_volatility = spy_daily_returns.std() * np.sqrt(252) * 100

    # Calculate Sharpe Ratio
    portfolio_sharpe = portfolio_annual_return / portfolio_volatility if portfolio_volatility > 0 else 0
    spy_sharpe = spy_annual_return / spy_volatility if spy_volatility > 0 else 0

    # Calculate max drawdown
    portfolio_cummax = portfolio_returns.cummax()
    portfolio_drawdown = (portfolio_returns - portfolio_cummax) / portfolio_cummax * 100
    portfolio_max_drawdown = portfolio_drawdown.min()

    spy_cummax = spy_returns.cummax()
    spy_drawdown = (spy_returns - spy_cummax) / spy_cummax * 100
    spy_max_drawdown = spy_drawdown.min()

    # Count trades
    total_trades = len(portfolio['trades'])
    total_trade_cost = sum(trade['cost'] for trade in portfolio['trades'])

    # Print results
    print("\n" + "="*80)
    print("BACKTEST RESULTS")
    print("="*80)

    print(f"\nPeriod: {rebal_dates[0].date()} to {rebal_dates[-1].date()} ({days_elapsed} days / {years_elapsed:.2f} years)")
    print(f"Rebalancing Events: {len(rebal_dates)}")
    print(f"Total Trades: {total_trades}")
    print(f"Total Transaction Costs: ${total_trade_cost:,.2f}")

    print(f"\n{'='*80}")
    print("PERFORMANCE COMPARISON")
    print(f"{'='*80}")

    print(f"\n{'Metric':<30} {'Sector Rotation':<20} {'SPY Benchmark':<20} {'Difference':<15}")
    print("-"*85)
    print(f"{'Initial Capital':<30} ${INITIAL_CAPITAL:>18,.2f} ${INITIAL_CAPITAL:>18,.2f} ${0:>13,.2f}")
    print(f"{'Final Value':<30} ${final_portfolio_value:>18,.2f} ${final_spy_value:>18,.2f} ${final_portfolio_value - final_spy_value:>13,.2f}")
    print(f"{'Total Return':<30} {portfolio_return_pct:>17.2f}% {spy_return_pct:>17.2f}% {alpha:>12.2f}%")
    print(f"{'Annualized Return':<30} {portfolio_annual_return:>17.2f}% {spy_annual_return:>17.2f}% {portfolio_annual_return - spy_annual_return:>12.2f}%")
    print(f"{'Volatility (Annual)':<30} {portfolio_volatility:>17.2f}% {spy_volatility:>17.2f}% {portfolio_volatility - spy_volatility:>12.2f}%")
    print(f"{'Sharpe Ratio':<30} {portfolio_sharpe:>18.2f} {spy_sharpe:>18.2f} {portfolio_sharpe - spy_sharpe:>13.2f}")
    print(f"{'Max Drawdown':<30} {portfolio_max_drawdown:>17.2f}% {spy_max_drawdown:>17.2f}% {portfolio_max_drawdown - spy_max_drawdown:>12.2f}%")

    if alpha > 0:
        print(f"\n[OUTPERFORMING] Strategy beat SPY by {alpha:.2f}%")
    elif alpha < 0:
        print(f"\n[UNDERPERFORMING] Strategy trails SPY by {abs(alpha):.2f}%")
    else:
        print(f"\n[MATCHING] Strategy matches SPY")

    # Save results
    results_dir = Path(__file__).parent / 'results'
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    strategy_name = f"top{top_n}_{strategy}"
    date_range = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"

    results_file = results_dir / f'backtest_{strategy_name}_{date_range}_{timestamp}.csv'

    # Create results dataframe
    results_df = pd.DataFrame({
        'date': portfolio['date_history'],
        'portfolio_value': portfolio['value_history'],
        'spy_value': spy_benchmark['value_history'],
        'portfolio_return': [(v - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100 for v in portfolio['value_history']],
        'spy_return': [(v - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100 for v in spy_benchmark['value_history']],
        'alpha': [(pv - sv) / INITIAL_CAPITAL * 100 for pv, sv in zip(portfolio['value_history'], spy_benchmark['value_history'])],
        'holdings': [','.join(h) for h in portfolio['holdings_history']]
    })

    results_df.to_csv(results_file, index=False)
    print(f"\n[OK] Results saved to: {results_file}")

    # Save trade log
    trades_file = results_dir / f'trades_{strategy_name}_{date_range}_{timestamp}.csv'
    trades_df = pd.DataFrame(portfolio['trades'])
    trades_df.to_csv(trades_file, index=False)
    print(f"[OK] Trade log saved to: {trades_file}")

    # Print final holdings
    print(f"\n{'='*80}")
    print("FINAL PORTFOLIO HOLDINGS")
    print(f"{'='*80}")
    print(f"\nAs of {rebal_dates[-1].date()}:")

    if portfolio['positions']:
        print(f"\n{'Ticker':<10} {'Sector':<30} {'Shares':<15} {'Price':<12} {'Value':<15} {'Weight':<10}")
        print("-"*92)

        for ticker in sorted(portfolio['positions'].keys()):
            shares = portfolio['positions'][ticker]
            price = df_prices.loc[rebal_dates[-1], ticker]
            value = shares * price
            weight = (value / final_portfolio_value) * 100
            sector_name = SECTOR_ETFS.get(ticker, 'Unknown')
            print(f"{ticker:<10} {sector_name:<30} {shares:>14.2f} ${price:>10.2f} ${value:>13,.2f} {weight:>8.1f}%")

        print("-"*92)
        invested_value = sum(portfolio['positions'][t] * df_prices.loc[rebal_dates[-1], t] for t in portfolio['positions'])
        cash_value = portfolio['cash']
        print(f"{'INVESTED':<10} {'':<30} {'':<15} {'':<12} ${invested_value:>13,.2f} {(invested_value/final_portfolio_value)*100:>8.1f}%")
        print(f"{'CASH':<10} {'':<30} {'':<15} {'':<12} ${cash_value:>13,.2f} {(cash_value/final_portfolio_value)*100:>8.1f}%")
        print(f"{'TOTAL':<10} {'':<30} {'':<15} {'':<12} ${final_portfolio_value:>13,.2f} {100.0:>8.1f}%")
    else:
        print("\n100% CASH (stopped out)")
        print(f"Cash: ${portfolio['cash']:,.2f}")

    print(f"\n{'='*80}")
    print("BACKTEST COMPLETE!")
    print(f"{'='*80}")

    return {
        'final_value': final_portfolio_value,
        'total_return': portfolio_return_pct,
        'annual_return': portfolio_annual_return,
        'volatility': portfolio_volatility,
        'sharpe': portfolio_sharpe,
        'max_drawdown': portfolio_max_drawdown,
        'alpha': alpha,
        'total_trades': total_trades,
        'total_costs': total_trade_cost
    }


def main():
    """Main function"""
    args = parse_args()

    # Parse dates
    try:
        start_date = datetime.strptime(args.start, '%Y-%m-%d')
        end_date = datetime.strptime(args.end, '%Y-%m-%d')
    except ValueError as e:
        print(f"[ERROR] Invalid date format: {e}")
        print("Use YYYY-MM-DD format (e.g., 2025-01-01)")
        sys.exit(1)

    # Validate dates
    if end_date <= start_date:
        print("[ERROR] End date must be after start date")
        sys.exit(1)

    # Run backtest
    try:
        results = run_backtest(args.top, args.strategy, start_date, end_date)
    except Exception as e:
        print(f"\n[ERROR] Backtest failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
