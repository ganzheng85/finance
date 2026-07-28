"""
Backtest: Top 3 Sector Rotation with Risk Management During Crash Periods

Testing:
1. 2020 COVID Crash (Feb-Mar 2020) - SPY dropped -34%
2. 2022 Bear Market (Jan-Oct 2022) - SPY dropped -25%
3. 2025-2026 Bull Period (recent 6 months) - SPY +8.25%
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from calculate_sector_metrics import (
    calculate_momentum,
    calculate_relative_strength,
    rank_sectors,
)

# Configuration
TOP_N_SECTORS = 3
EQUAL_WEIGHT = 1/3
INITIAL_CAPITAL = 100000
TRANSACTION_COST_PCT = 0.001
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
    'SMH': 'Semiconductors'
}

# Test periods
TEST_PERIODS = {
    'COVID_Crash': {
        'name': '2020 COVID Crash',
        'start': datetime(2020, 1, 1),
        'end': datetime(2020, 5, 31),
        'description': 'SPY dropped -34% in 1 month'
    },
    'Bear_2022': {
        'name': '2022 Bear Market',
        'start': datetime(2022, 1, 1),
        'end': datetime(2022, 10, 31),
        'description': 'SPY dropped -25% over 9 months'
    },
    'Recent_Bull': {
        'name': '2025-2026 Bull Period',
        'start': datetime(2025, 12, 1),
        'end': datetime(2026, 6, 30),
        'description': 'Recent 6-month bull market'
    }
}

def run_backtest_for_period(period_key, period_config):
    """Run backtest for a specific time period"""

    print("\n" + "="*80)
    print(f"TESTING: {period_config['name']}")
    print("="*80)
    print(f"Period: {period_config['start'].date()} to {period_config['end'].date()}")
    print(f"Context: {period_config['description']}")

    # Fetch data (extra for lookback calculations)
    start_date = period_config['start'] - timedelta(days=365)
    end_date = period_config['end']

    print(f"\nFetching data from {start_date.date()} to {end_date.date()}...")

    all_tickers = list(SECTOR_ETFS.keys()) + ['SPY']
    sector_data = {}

    for ticker in all_tickers:
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date)
            if not data.empty:
                sector_data[ticker] = data['Close']
        except Exception as e:
            print(f"  {ticker}: ERROR - {str(e)}")

    df_prices = pd.DataFrame(sector_data)
    df_prices = df_prices.dropna()
    df_prices.index = df_prices.index.tz_localize(None)

    print(f"[OK] Fetched {len(df_prices)} days of data")

    # Create sector dataframe
    sector_df = pd.DataFrame()
    for ticker in SECTOR_ETFS.keys():
        if ticker in df_prices.columns:
            temp_df = pd.DataFrame({
                'date': df_prices.index,
                'ticker': ticker,
                'sector_name': SECTOR_ETFS[ticker],
                'adjusted_close': df_prices[ticker].values
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
    backtest_start = period_config['start']
    all_dates = df_prices.index[df_prices.index >= backtest_start]

    rebal_dates = []
    for date in all_dates:
        week_num = date.isocalendar()[1]
        next_day = date + timedelta(days=1)
        if next_day not in all_dates or next_day.isocalendar()[1] != week_num:
            rebal_dates.append(date)

    if not rebal_dates:
        print("[ERROR] No rebalancing dates found")
        return None

    print(f"[OK] {len(rebal_dates)} weekly rebalancing dates")

    # Initialize portfolios
    portfolios = {
        'Base': {
            'cash': INITIAL_CAPITAL,
            'positions': {},
            'value_history': [],
            'date_history': [],
            'peak_value': INITIAL_CAPITAL,
            'cash_pct': 0.0,
            'trades': []
        },
        'Trailing_15': {
            'cash': INITIAL_CAPITAL,
            'positions': {},
            'value_history': [],
            'date_history': [],
            'peak_value': INITIAL_CAPITAL,
            'cash_pct': 0.0,
            'stopped_out': False,
            'trades': []
        },
        'Hard_25': {
            'cash': INITIAL_CAPITAL,
            'positions': {},
            'value_history': [],
            'date_history': [],
            'peak_value': INITIAL_CAPITAL,
            'cash_pct': 0.0,
            'stopped_out': False,
            'trades': []
        },
        'Market_Regime': {
            'cash': INITIAL_CAPITAL,
            'positions': {},
            'value_history': [],
            'date_history': [],
            'peak_value': INITIAL_CAPITAL,
            'cash_pct': 0.0,
            'trades': []
        }
    }

    spy_benchmark = {
        'shares': INITIAL_CAPITAL / df_prices.loc[rebal_dates[0], 'SPY'],
        'value_history': [],
        'date_history': []
    }

    print("Running backtest...")

    # Suppress verbose output from sector calculations
    import contextlib
    import io

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

        # Get top 3 sectors
        top_sectors = rankings.head(TOP_N_SECTORS)['ticker'].tolist()

        # Check market regime
        spy_price = df_prices.loc[rebal_date, 'SPY']
        spy_ma200 = df_prices.loc[rebal_date, 'SPY_MA200']
        bull_market = spy_price > spy_ma200 if not pd.isna(spy_ma200) else True

        # Process each strategy
        for strategy_name, portfolio in portfolios.items():
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
            if strategy_name == 'Base':
                target_cash_pct = 0.0

            elif strategy_name == 'Trailing_15':
                if drawdown <= -TRAILING_STOP_15 and not portfolio['stopped_out']:
                    target_cash_pct = 0.50
                    portfolio['stopped_out'] = True
                elif drawdown >= -0.05:  # Reset when recovered to -5%
                    target_cash_pct = 0.0
                    portfolio['stopped_out'] = False
                else:
                    target_cash_pct = portfolio['cash_pct']

            elif strategy_name == 'Hard_25':
                if drawdown <= -TRAILING_STOP_25 and not portfolio['stopped_out']:
                    target_cash_pct = 1.0
                    portfolio['stopped_out'] = True
                elif drawdown >= -0.05:  # Reset when recovered to -5%
                    target_cash_pct = 0.0
                    portfolio['stopped_out'] = False
                else:
                    target_cash_pct = portfolio['cash_pct']

            elif strategy_name == 'Market_Regime':
                target_cash_pct = 0.50 if not bull_market else 0.0

            portfolio['cash_pct'] = target_cash_pct

            # Record values
            portfolio['value_history'].append(portfolio_value)
            portfolio['date_history'].append(rebal_date)

            # Sell all current positions
            for ticker in list(portfolio['positions'].keys()):
                shares = portfolio['positions'][ticker]
                if shares > 0:
                    price = df_prices.loc[rebal_date, ticker]
                    proceeds = shares * price
                    cost = proceeds * TRANSACTION_COST_PCT
                    portfolio['cash'] += proceeds - cost

            portfolio['positions'] = {}

            # Calculate amount to invest
            cash_to_invest = portfolio['cash'] * (1 - target_cash_pct)

            if cash_to_invest > 100:  # Only invest if meaningful amount
                target_value_per_sector = cash_to_invest * EQUAL_WEIGHT

                for ticker in top_sectors:
                    price = df_prices.loc[rebal_date, ticker]
                    shares_to_buy = target_value_per_sector / price
                    portfolio['positions'][ticker] = shares_to_buy

                total_transaction_costs = cash_to_invest * TRANSACTION_COST_PCT
                portfolio['cash'] = portfolio['cash'] * target_cash_pct

        # SPY benchmark
        spy_value = spy_benchmark['shares'] * df_prices.loc[rebal_date, 'SPY']
        spy_benchmark['value_history'].append(spy_value)
        spy_benchmark['date_history'].append(rebal_date)

        # Progress indicator
        if i % 5 == 0 or i == len(rebal_dates) - 1:
            pct = (i + 1) / len(rebal_dates) * 100
            print(f"  Week {i+1}/{len(rebal_dates)} ({pct:.0f}%) - {rebal_date.date()}")

    print("[OK] Backtest complete!")

    # Calculate metrics
    results = {}

    for strategy_name, portfolio in portfolios.items():
        returns = pd.Series(portfolio['value_history'], index=portfolio['date_history'])
        final_value = returns.iloc[-1]
        total_return = ((final_value - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100

        days_elapsed = (rebal_dates[-1] - rebal_dates[0]).days
        years_elapsed = days_elapsed / 365.25
        annual_return = ((final_value / INITIAL_CAPITAL) ** (1/years_elapsed) - 1) * 100

        daily_returns = returns.pct_change().dropna()
        volatility = daily_returns.std() * np.sqrt(252) * 100
        sharpe = annual_return / volatility if volatility > 0 else 0

        cummax = returns.cummax()
        drawdown = (returns - cummax) / cummax * 100
        max_drawdown = drawdown.min()

        results[strategy_name] = {
            'final_value': final_value,
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe': sharpe,
            'max_drawdown': max_drawdown
        }

    # SPY
    spy_returns = pd.Series(spy_benchmark['value_history'], index=spy_benchmark['date_history'])
    spy_final = spy_returns.iloc[-1]
    spy_return = ((spy_final - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
    spy_annual = ((spy_final / INITIAL_CAPITAL) ** (1/years_elapsed) - 1) * 100
    spy_daily = spy_returns.pct_change().dropna()
    spy_vol = spy_daily.std() * np.sqrt(252) * 100
    spy_sharpe = spy_annual / spy_vol if spy_vol > 0 else 0
    spy_cummax = spy_returns.cummax()
    spy_dd = (spy_returns - spy_cummax) / spy_cummax * 100
    spy_max_dd = spy_dd.min()

    results['SPY'] = {
        'final_value': spy_final,
        'total_return': spy_return,
        'annual_return': spy_annual,
        'volatility': spy_vol,
        'sharpe': spy_sharpe,
        'max_drawdown': spy_max_dd
    }

    # Print summary
    print(f"\n{'Strategy':<20} {'Final Value':<15} {'Return':<10} {'Max DD':<10} {'Alpha':<10}")
    print("-"*70)
    for strategy in ['Base', 'Trailing_15', 'Hard_25', 'Market_Regime', 'SPY']:
        r = results[strategy]
        alpha = r['total_return'] - results['SPY']['total_return'] if strategy != 'SPY' else 0
        name = strategy.replace('_', ' ')
        print(f"{name:<20} ${r['final_value']:>13,.2f} {r['total_return']:>8.2f}% {r['max_drawdown']:>8.2f}% {alpha:>8.2f}%")

    return {
        'period_name': period_config['name'],
        'description': period_config['description'],
        'start_date': period_config['start'],
        'end_date': period_config['end'],
        'results': results,
        'spy_dd_min': spy_max_dd
    }

# Run all test periods
print("="*80)
print("CRASH PERIOD RISK MANAGEMENT ANALYSIS")
print("="*80)
print("\nTesting Top 3 Sector Rotation Strategy with:")
print("  1. Base: Always invested")
print("  2. 15% Trailing Stop: 50% cash if down -15%")
print("  3. 25% Hard Stop: 100% cash if down -25%")
print("  4. Market Regime: 50% cash when SPY < 200-day MA")

all_results = {}

for period_key, period_config in TEST_PERIODS.items():
    result = run_backtest_for_period(period_key, period_config)
    if result:
        all_results[period_key] = result

# Generate HTML report
print("\n" + "="*80)
print("GENERATING HTML REPORT...")
print("="*80)

html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sector Rotation Risk Management Analysis - Crash Periods</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        h3 {{
            color: #555;
            margin-top: 20px;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .period {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .period h3 {{
            color: #2c3e50;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        th {{
            background-color: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .positive {{
            color: #27ae60;
            font-weight: bold;
        }}
        .negative {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .neutral {{
            color: #95a5a6;
        }}
        .winner {{
            background-color: #d5f4e6;
            font-weight: bold;
        }}
        .recommendation {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .key-finding {{
            background: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .metric {{
            display: inline-block;
            margin: 10px 20px 10px 0;
        }}
        .metric-label {{
            font-size: 0.9em;
            color: #7f8c8d;
        }}
        .metric-value {{
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h1>Sector Rotation Risk Management Analysis</h1>
    <p><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <div class="summary">
        <h2>Executive Summary</h2>
        <p>This analysis tests whether stop losses improve Top 3 Sector Rotation strategy performance during market crashes.</p>

        <h3>Strategies Tested</h3>
        <ul>
            <li><strong>Base:</strong> Always invested in top 3 ranked sectors (33.33% each)</li>
            <li><strong>15% Trailing Stop:</strong> Go 50% cash if portfolio drops -15% from peak</li>
            <li><strong>25% Hard Stop:</strong> Go 100% cash if portfolio drops -25% from peak</li>
            <li><strong>Market Regime:</strong> Go 50% cash when SPY below 200-day moving average</li>
        </ul>

        <h3>Test Periods</h3>
        <ul>
"""

for period_key, result in all_results.items():
    html_content += f"            <li><strong>{result['period_name']}:</strong> {result['description']}</li>\n"

html_content += """        </ul>
    </div>
"""

# Add results for each period
for period_key, result in all_results.items():
    results = result['results']

    html_content += f"""
    <div class="period">
        <h3>{result['period_name']}</h3>
        <p><strong>Period:</strong> {result['start_date'].strftime('%Y-%m-%d')} to {result['end_date'].strftime('%Y-%m-%d')}</p>
        <p><strong>Context:</strong> {result['description']}</p>

        <table>
            <thead>
                <tr>
                    <th>Strategy</th>
                    <th>Final Value</th>
                    <th>Total Return</th>
                    <th>Max Drawdown</th>
                    <th>Alpha vs SPY</th>
                    <th>Sharpe Ratio</th>
                </tr>
            </thead>
            <tbody>
"""

    # Find winner
    strategies = ['Base', 'Trailing_15', 'Hard_25', 'Market_Regime']
    best_return_strat = max(strategies, key=lambda s: results[s]['total_return'])

    for strategy in strategies + ['SPY']:
        r = results[strategy]
        alpha = r['total_return'] - results['SPY']['total_return'] if strategy != 'SPY' else 0
        name = strategy.replace('_', ' ')

        winner_class = 'winner' if strategy == best_return_strat else ''
        return_class = 'positive' if r['total_return'] > 0 else 'negative'
        alpha_class = 'positive' if alpha > 0 else 'negative' if alpha < 0 else 'neutral'

        html_content += f"""
                <tr class="{winner_class}">
                    <td>{name}</td>
                    <td>${r['final_value']:,.2f}</td>
                    <td class="{return_class}">{r['total_return']:+.2f}%</td>
                    <td class="negative">{r['max_drawdown']:.2f}%</td>
                    <td class="{alpha_class}">{alpha:+.2f}%</td>
                    <td>{r['sharpe']:.2f}</td>
                </tr>
"""

    html_content += """
            </tbody>
        </table>
"""

    # Key findings for this period
    base_return = results['Base']['total_return']
    trailing15_return = results['Trailing_15']['total_return']
    hard25_return = results['Hard_25']['total_return']
    regime_return = results['Market_Regime']['total_return']
    spy_return = results['SPY']['total_return']

    best_strat = max(
        [('Base', base_return), ('15% Trailing Stop', trailing15_return),
         ('25% Hard Stop', hard25_return), ('Market Regime', regime_return)],
        key=lambda x: x[1]
    )

    html_content += f"""
        <div class="key-finding">
            <strong>Key Finding:</strong> {best_strat[0]} performed best with {best_strat[1]:+.2f}% return vs SPY's {spy_return:+.2f}%
        </div>
    </div>
"""

# Overall recommendation
html_content += """
    <div class="summary">
        <h2>Overall Recommendation</h2>
"""

# Analyze which strategy won most often
strategy_wins = {'Base': 0, 'Trailing_15': 0, 'Hard_25': 0, 'Market_Regime': 0}
for period_key, result in all_results.items():
    results = result['results']
    best = max(['Base', 'Trailing_15', 'Hard_25', 'Market_Regime'],
               key=lambda s: results[s]['total_return'])
    strategy_wins[best] += 1

overall_winner = max(strategy_wins.items(), key=lambda x: x[1])

html_content += f"""
        <div class="recommendation">
            <h3>Winner: {overall_winner[0].replace('_', ' ')}</h3>
            <p>Won in {overall_winner[1]} out of {len(all_results)} test periods.</p>
        </div>

        <h3>Summary by Period</h3>
        <ul>
"""

for period_key, result in all_results.items():
    results = result['results']
    strategies = ['Base', 'Trailing_15', 'Hard_25', 'Market_Regime']
    best_strat = max(strategies, key=lambda s: results[s]['total_return'])
    best_return = results[best_strat]['total_return']
    spy_return = results['SPY']['total_return']

    html_content += f"""
            <li><strong>{result['period_name']}:</strong> {best_strat.replace('_', ' ')} won with {best_return:+.2f}% (SPY: {spy_return:+.2f}%)</li>
"""

html_content += """
        </ul>

        <h3>Final Verdict</h3>
        <p>Based on these crash period tests, the recommendation is:</p>
        <ul>
            <li>If stops helped during crashes: Use them</li>
            <li>If stops hurt performance: Skip them and stay fully invested</li>
            <li>Consider risk tolerance: stops reduce drawdowns but may sacrifice returns</li>
        </ul>
    </div>

    <div class="footer">
        <p><strong>Disclaimer:</strong> Past performance does not guarantee future results. This analysis is for educational purposes only.</p>
        <p>Report generated on """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
    </div>
</body>
</html>
"""

# Save HTML report
results_dir = Path(__file__).parent / 'results'
results_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
html_file = results_dir / f'crash_period_analysis_{timestamp}.html'

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"[OK] HTML report saved to: {html_file}")

print("\n" + "="*80)
print("ANALYSIS COMPLETE!")
print("="*80)
