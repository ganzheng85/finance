"""
Run all backtest strategies for specified periods

Usage:
    # Run all combinations for default periods (2025 H1 & H2)
    python run_all_tests.py

    # Run Top 3 only for custom period
    python run_all_tests.py --top 3 --start 2025-01-01 --end 2025-06-01

    # Run Top 5 only for 2025 full year
    python run_all_tests.py --top 5 --start 2025-01-01 --end 2025-12-31

    # Run both Top 3 and 5 for custom period
    python run_all_tests.py --top 3 5 --start 2024-06-01 --end 2025-06-01
"""

import subprocess
import sys
import argparse
from datetime import datetime

STRATEGIES = ['base', 'trailing15', 'hard25', 'regime']

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Run all backtest strategies',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default: Run all combinations for 2025 H1 & H2
  python run_all_tests.py

  # Top 3 only, custom period
  python run_all_tests.py --top 3 --start 2025-01-01 --end 2025-06-01

  # Top 5 only, full 2025
  python run_all_tests.py --top 5 --start 2025-01-01 --end 2025-12-31

  # Both Top 3 and Top 5, custom period
  python run_all_tests.py --top 3 5 --start 2024-01-01 --end 2024-12-31

  # Single strategy only (Top 3, base, custom period)
  python run_all_tests.py --top 3 --strategy base --start 2025-01-01 --end 2025-12-31
        """
    )

    parser.add_argument('--top', type=int, nargs='+', choices=[3, 5],
                        help='Top sectors to test (3, 5, or both). Default: both')

    parser.add_argument('--strategy', type=str, nargs='+',
                        choices=['base', 'trailing15', 'hard25', 'regime'],
                        help='Strategies to test. Default: all 4 strategies')

    parser.add_argument('--start', type=str,
                        help='Start date (YYYY-MM-DD). If not provided, uses 2025 H1 & H2')

    parser.add_argument('--end', type=str,
                        help='End date (YYYY-MM-DD). Required if --start is provided')

    return parser.parse_args()


def run_backtest(top_n, strategy, start, end, period_name):
    """Run a single backtest and capture results"""
    print("\n" + "="*80)
    print(f"RUNNING: Top {top_n} | {strategy.upper()} | {period_name}")
    print("="*80)

    cmd = [
        sys.executable,  # Use same Python interpreter
        'backtest_custom.py',
        '--top', str(top_n),
        '--strategy', strategy,
        '--start', start,
        '--end', end
    ]

    try:
        # Capture output to extract results
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)  # Display output

        # Parse results from output
        output = result.stdout
        results = {
            'top': top_n,
            'strategy': strategy,
            'period': period_name,
            'start': start,
            'end': end,
            'final_value': None,
            'total_return': None,
            'alpha': None,
            'sharpe': None,
            'max_drawdown': None,
            'success': True
        }

        # Also capture SPY benchmark data
        spy_results = {
            'top': 'SPY',
            'strategy': 'Benchmark',
            'period': period_name,
            'start': start,
            'end': end,
            'final_value': None,
            'total_return': None,
            'alpha': 0.0,  # SPY has 0 alpha vs itself
            'sharpe': None,
            'max_drawdown': None,
            'success': True
        }

        # Extract metrics from output - improved parsing
        lines = output.split('\n')

        for i, line in enumerate(lines):
            try:
                # Look for specific metric lines in the output
                if 'Final Value' in line and '$' in line:
                    # Extract values from fixed-width table
                    # Format: "Final Value                    $XXX,XXX.XX        $YYY,YYY.YY      +$ZZZ.ZZ"
                    parts = line.split('$')
                    if len(parts) >= 3:
                        # First dollar amount is sector rotation
                        value_str = parts[1].split()[0].replace(',', '')
                        results['final_value'] = float(value_str)
                        # Second dollar amount is SPY
                        spy_value_str = parts[2].split()[0].replace(',', '')
                        spy_results['final_value'] = float(spy_value_str)

                elif 'Total Return' in line and '%' in line and 'Annualized' not in line:
                    # Format: "Total Return                        27.34%             15.66%           +11.68%"
                    # Extract percentages
                    import re
                    percentages = re.findall(r'[-+]?\d+\.\d+%', line)
                    if len(percentages) >= 3:
                        results['total_return'] = float(percentages[0].replace('%', ''))
                        spy_results['total_return'] = float(percentages[1].replace('%', ''))
                        results['alpha'] = float(percentages[2].replace('%', '').replace('+', ''))

                elif 'Sharpe Ratio' in line and 'Sector Rotation' not in line:
                    # Format: "Sharpe Ratio                          1.23               0.98             +0.25"
                    import re
                    numbers = re.findall(r'[-+]?\d+\.\d+', line)
                    if len(numbers) >= 2:
                        results['sharpe'] = float(numbers[0])
                        spy_results['sharpe'] = float(numbers[1])

                elif 'Max Drawdown' in line and '%' in line:
                    # Format: "Max Drawdown                         -8.45%             -6.23%            -2.22%"
                    import re
                    percentages = re.findall(r'[-+]?\d+\.\d+%', line)
                    if len(percentages) >= 2:
                        results['max_drawdown'] = float(percentages[0].replace('%', ''))
                        spy_results['max_drawdown'] = float(percentages[1].replace('%', ''))
            except Exception as e:
                # Skip lines that don't parse
                pass

        print(f"[SUCCESS] Completed")
        return True, (results, spy_results)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed: {e}")
        return False, ({
            'top': top_n,
            'strategy': strategy,
            'period': period_name,
            'start': start,
            'end': end,
            'success': False
        }, None)


def generate_summary(all_results, periods, top_options, strategies):
    """Generate comprehensive summary of all backtest results"""
    from pathlib import Path

    print("\n" + "="*80)
    print("COMPREHENSIVE SUMMARY")
    print("="*80)

    # Filter successful results
    successful_results = [r for r in all_results if r.get('success', False)]

    if not successful_results:
        print("\n[WARNING] No successful results to summarize")
        return

    # Group results by period
    for period_key, period_config in periods.items():
        period_results = [r for r in successful_results if r['start'] == period_config['start']]

        if not period_results:
            continue

        print(f"\n{period_config['name']} ({period_config['start']} to {period_config['end']})")
        print("-" * 80)

        # Separate SPY from strategies
        spy_result = next((r for r in period_results if r['top'] == 'SPY'), None)
        strategy_results = [r for r in period_results if r['top'] != 'SPY']

        # Create comparison table
        print(f"\n{'Strategy':<25} {'Return':<12} {'Alpha':<12} {'Sharpe':<10} {'Max DD':<12}")
        print("-" * 80)

        # Sort strategies by return (descending)
        strategy_results.sort(key=lambda x: x.get('total_return') if x.get('total_return') is not None else -999, reverse=True)

        # Show strategies
        for result in strategy_results:
            strategy_name = f"Top {result['top']} - {result['strategy']}"
            ret = result.get('total_return')
            alpha = result.get('alpha')
            sharpe = result.get('sharpe')
            dd = result.get('max_drawdown')

            ret_str = f"{ret:+.2f}%" if ret is not None else "N/A"
            alpha_str = f"{alpha:+.2f}%" if alpha is not None else "N/A"
            sharpe_str = f"{sharpe:.2f}" if sharpe is not None else "N/A"
            dd_str = f"{dd:.2f}%" if dd is not None else "N/A"

            print(f"{strategy_name:<25} {ret_str:<12} {alpha_str:<12} {sharpe_str:<10} {dd_str:<12}")

        # Show SPY benchmark
        if spy_result:
            print("-" * 80)
            strategy_name = "SPY (Benchmark)"
            ret = spy_result.get('total_return')
            alpha = spy_result.get('alpha', 0.0)
            sharpe = spy_result.get('sharpe')
            dd = spy_result.get('max_drawdown')

            ret_str = f"{ret:+.2f}%" if ret is not None else "N/A"
            alpha_str = f"{alpha:+.2f}%" if alpha is not None else "N/A"
            sharpe_str = f"{sharpe:.2f}" if sharpe is not None else "N/A"
            dd_str = f"{dd:.2f}%" if dd is not None else "N/A"

            print(f"{strategy_name:<25} {ret_str:<12} {alpha_str:<12} {sharpe_str:<10} {dd_str:<12}")

        # Identify winner (excluding SPY)
        if strategy_results:
            winner = strategy_results[0]
            print(f"\n[WINNER] Top {winner['top']} - {winner['strategy']}")
            ret = winner.get('total_return')
            alpha = winner.get('alpha')
            ret_str = f"{ret:+.2f}%" if ret is not None else "N/A"
            alpha_str = f"{alpha:+.2f}%" if alpha is not None else "N/A"
            print(f"  Return: {ret_str}")
            print(f"  Alpha: {alpha_str}")

    # Overall best strategy analysis (excluding SPY benchmark)
    print("\n" + "="*80)
    print("BEST STRATEGY BY METRIC")
    print("="*80)

    strategy_only_results = [r for r in successful_results if r['top'] != 'SPY']

    if strategy_only_results:
        # Best return
        best_return = max(strategy_only_results, key=lambda x: x.get('total_return') if x.get('total_return') is not None else -999)
        print(f"\nBest Total Return:")
        print(f"  Top {best_return['top']} - {best_return['strategy']} ({best_return['period']})")
        ret_val = best_return.get('total_return')
        ret_str = f"{ret_val:+.2f}%" if ret_val is not None else "N/A"
        print(f"  Return: {ret_str}")

        # Best alpha
        best_alpha = max(strategy_only_results, key=lambda x: x.get('alpha') if x.get('alpha') is not None else -999)
        print(f"\nBest Alpha vs SPY:")
        print(f"  Top {best_alpha['top']} - {best_alpha['strategy']} ({best_alpha['period']})")
        alpha_val = best_alpha.get('alpha')
        alpha_str = f"{alpha_val:+.2f}%" if alpha_val is not None else "N/A"
        print(f"  Alpha: {alpha_str}")

        # Best Sharpe
        best_sharpe = max(strategy_only_results, key=lambda x: x.get('sharpe') if x.get('sharpe') is not None else -999)
        print(f"\nBest Sharpe Ratio:")
        print(f"  Top {best_sharpe['top']} - {best_sharpe['strategy']} ({best_sharpe['period']})")
        sharpe_val = best_sharpe.get('sharpe')
        sharpe_str = f"{sharpe_val:.2f}" if sharpe_val is not None else "N/A"
        print(f"  Sharpe: {sharpe_str}")

        # Best (least negative) max drawdown
        best_dd = max(strategy_only_results, key=lambda x: x.get('max_drawdown') if x.get('max_drawdown') is not None else -999)
        print(f"\nBest Max Drawdown:")
        print(f"  Top {best_dd['top']} - {best_dd['strategy']} ({best_dd['period']})")
        dd_val = best_dd.get('max_drawdown')
        dd_str = f"{dd_val:.2f}%" if dd_val is not None else "N/A"
        print(f"  Max DD: {dd_str}")

    # Strategy win count (excluding SPY)
    print("\n" + "="*80)
    print("STRATEGY WIN COUNT (by Total Return)")
    print("="*80)

    strategy_wins = {}
    for period_key, period_config in periods.items():
        period_results = [r for r in successful_results if r['start'] == period_config['start'] and r['top'] != 'SPY']
        if period_results:
            winner = max(period_results, key=lambda x: x.get('total_return') if x.get('total_return') is not None else -999)
            key = f"Top {winner['top']} - {winner['strategy']}"
            strategy_wins[key] = strategy_wins.get(key, 0) + 1

    if strategy_wins:
        print(f"\n{'Strategy':<25} {'Wins':<10}")
        print("-" * 40)
        for strategy, wins in sorted(strategy_wins.items(), key=lambda x: x[1], reverse=True):
            print(f"{strategy:<25} {wins}/{len(periods)}")

    # Save summary to file
    results_dir = Path('results')
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    summary_file = results_dir / f'summary_all_tests_{timestamp}.txt'

    with open(summary_file, 'w') as f:
        f.write("SECTOR ROTATION BACKTEST SUMMARY\n")
        f.write("="*80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Write period summaries
        for period_key, period_config in periods.items():
            period_results = [r for r in successful_results if r['start'] == period_config['start']]

            if not period_results:
                continue

            f.write(f"\n{period_config['name']} ({period_config['start']} to {period_config['end']})\n")
            f.write("-" * 80 + "\n")
            f.write(f"\n{'Strategy':<25} {'Return':<12} {'Alpha':<12} {'Sharpe':<10} {'Max DD':<12}\n")
            f.write("-" * 80 + "\n")

            # Separate SPY from strategies
            spy_result = next((r for r in period_results if r['top'] == 'SPY'), None)
            strategy_results = [r for r in period_results if r['top'] != 'SPY']

            strategy_results.sort(key=lambda x: x.get('total_return') if x.get('total_return') is not None else -999, reverse=True)

            # Write strategies
            for result in strategy_results:
                strategy_name = f"Top {result['top']} - {result['strategy']}"
                ret = result.get('total_return')
                alpha = result.get('alpha')
                sharpe = result.get('sharpe')
                dd = result.get('max_drawdown')

                ret_str = f"{ret:+.2f}%" if ret is not None else "N/A"
                alpha_str = f"{alpha:+.2f}%" if alpha is not None else "N/A"
                sharpe_str = f"{sharpe:.2f}" if sharpe is not None else "N/A"
                dd_str = f"{dd:.2f}%" if dd is not None else "N/A"

                f.write(f"{strategy_name:<25} {ret_str:<12} {alpha_str:<12} {sharpe_str:<10} {dd_str:<12}\n")

            # Write SPY benchmark
            if spy_result:
                f.write("-" * 80 + "\n")
                strategy_name = "SPY (Benchmark)"
                ret = spy_result.get('total_return')
                alpha = spy_result.get('alpha', 0.0)
                sharpe = spy_result.get('sharpe')
                dd = spy_result.get('max_drawdown')

                ret_str = f"{ret:+.2f}%" if ret is not None else "N/A"
                alpha_str = f"{alpha:+.2f}%" if alpha is not None else "N/A"
                sharpe_str = f"{sharpe:.2f}" if sharpe is not None else "N/A"
                dd_str = f"{dd:.2f}%" if dd is not None else "N/A"

                f.write(f"{strategy_name:<25} {ret_str:<12} {alpha_str:<12} {sharpe_str:<10} {dd_str:<12}\n")

            if strategy_results:
                winner = strategy_results[0]
                f.write(f"\n[WINNER] Top {winner['top']} - {winner['strategy']}\n")
                ret = winner.get('total_return')
                alpha = winner.get('alpha')
                ret_str = f"{ret:+.2f}%" if ret is not None else "N/A"
                alpha_str = f"{alpha:+.2f}%" if alpha is not None else "N/A"
                f.write(f"  Return: {ret_str}\n")
                f.write(f"  Alpha: {alpha_str}\n")

        # Write overall best (excluding SPY)
        f.write("\n" + "="*80 + "\n")
        f.write("BEST STRATEGY BY METRIC\n")
        f.write("="*80 + "\n")

        strategy_only_results = [r for r in successful_results if r['top'] != 'SPY']

        if strategy_only_results:
            best_return = max(strategy_only_results, key=lambda x: x.get('total_return') if x.get('total_return') is not None else -999)
            f.write(f"\nBest Total Return:\n")
            f.write(f"  Top {best_return['top']} - {best_return['strategy']} ({best_return['period']})\n")
            ret_val = best_return.get('total_return')
            ret_str = f"{ret_val:+.2f}%" if ret_val is not None else "N/A"
            f.write(f"  Return: {ret_str}\n")

            best_alpha = max(strategy_only_results, key=lambda x: x.get('alpha') if x.get('alpha') is not None else -999)
            f.write(f"\nBest Alpha vs SPY:\n")
            f.write(f"  Top {best_alpha['top']} - {best_alpha['strategy']} ({best_alpha['period']})\n")
            alpha_val = best_alpha.get('alpha')
            alpha_str = f"{alpha_val:+.2f}%" if alpha_val is not None else "N/A"
            f.write(f"  Alpha: {alpha_str}\n")

            best_sharpe = max(strategy_only_results, key=lambda x: x.get('sharpe') if x.get('sharpe') is not None else -999)
            f.write(f"\nBest Sharpe Ratio:\n")
            f.write(f"  Top {best_sharpe['top']} - {best_sharpe['strategy']} ({best_sharpe['period']})\n")
            sharpe_val = best_sharpe.get('sharpe')
            sharpe_str = f"{sharpe_val:.2f}" if sharpe_val is not None else "N/A"
            f.write(f"  Sharpe: {sharpe_str}\n")

        # Write strategy wins
        f.write("\n" + "="*80 + "\n")
        f.write("STRATEGY WIN COUNT (by Total Return)\n")
        f.write("="*80 + "\n\n")

        if strategy_wins:
            f.write(f"{'Strategy':<25} {'Wins':<10}\n")
            f.write("-" * 40 + "\n")
            for strategy, wins in sorted(strategy_wins.items(), key=lambda x: x[1], reverse=True):
                f.write(f"{strategy:<25} {wins}/{len(periods)}\n")

    print(f"\n[OK] Summary saved to: {summary_file}")


def main():
    """Run all combinations"""
    args = parse_args()

    print("="*80)
    print("RUNNING ALL BACKTEST COMBINATIONS")
    print("="*80)

    # Determine which top options to test
    if args.top:
        top_options = args.top
    else:
        top_options = [3, 5]

    # Determine which strategies to test
    if args.strategy:
        strategies = args.strategy
    else:
        strategies = STRATEGIES

    # Determine periods to test
    if args.start and args.end:
        # Custom single period
        try:
            start_date = datetime.strptime(args.start, '%Y-%m-%d')
            end_date = datetime.strptime(args.end, '%Y-%m-%d')
        except ValueError as e:
            print(f"[ERROR] Invalid date format: {e}")
            print("Use YYYY-MM-DD format (e.g., 2025-01-01)")
            sys.exit(1)

        if end_date <= start_date:
            print("[ERROR] End date must be after start date")
            sys.exit(1)

        periods = {
            'custom': {
                'start': args.start,
                'end': args.end,
                'name': f"{args.start} to {args.end}"
            }
        }
    elif args.start or args.end:
        print("[ERROR] Both --start and --end must be provided together")
        sys.exit(1)
    else:
        # Default: 2025 H1 & H2
        periods = {
            '2025_H1': {
                'start': '2025-01-01',
                'end': '2025-06-01',
                'name': '2025 First Half'
            },
            '2025_H2': {
                'start': '2025-06-01',
                'end': '2025-12-31',
                'name': '2025 Second Half'
            }
        }

    total_tests = len(periods) * len(top_options) * len(strategies)
    print(f"\nTotal tests to run: {total_tests}")
    print(f"Periods: {len(periods)} ({', '.join([p['name'] for p in periods.values()])})")
    print(f"Top options: {top_options}")
    print(f"Strategies: {strategies}")
    print()

    # Ask for confirmation
    response = input("Press Enter to start, or 'q' to quit: ")
    if response.lower() == 'q':
        print("Cancelled.")
        return

    start_time = datetime.now()
    completed = 0
    failed = 0
    all_results = []
    spy_results_by_period = {}  # Store SPY results once per period

    for period_key, period_config in periods.items():
        print(f"\n{'='*80}")
        print(f"PERIOD: {period_config['name']}")
        print(f"{'='*80}")

        for top_n in top_options:
            for strategy in strategies:
                success, result_tuple = run_backtest(
                    top_n,
                    strategy,
                    period_config['start'],
                    period_config['end'],
                    period_config['name']
                )

                if result_tuple:
                    result_data, spy_data = result_tuple
                    all_results.append(result_data)

                    # Store SPY data once per period
                    if spy_data and period_key not in spy_results_by_period:
                        spy_results_by_period[period_key] = spy_data

                if success:
                    completed += 1
                else:
                    failed += 1

                progress = ((completed + failed) / total_tests) * 100
                print(f"\nProgress: {completed + failed}/{total_tests} ({progress:.1f}%)")

    # Add SPY results to all_results for summary generation
    for spy_result in spy_results_by_period.values():
        if spy_result:
            all_results.append(spy_result)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "="*80)
    print("ALL TESTS COMPLETE!")
    print("="*80)
    print(f"Completed: {completed}/{total_tests}")
    print(f"Failed: {failed}/{total_tests}")
    print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")

    # Generate summary
    generate_summary(all_results, periods, top_options, strategies)

    print(f"\nAll results saved in: results/")


if __name__ == "__main__":
    main()
