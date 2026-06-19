"""
Comprehensive Technical Analysis Visualization

Creates multi-panel charts showing price, volume, and key technical indicators
to visualize trend strength and direction.

Usage:
    python plot_comprehensive_analysis.py TICKER [--days DAYS]
    python plot_comprehensive_analysis.py TICKER1 TICKER2 TICKER3 --days 60

Example:
    python plot_comprehensive_analysis.py NFLX --days 60
    python plot_comprehensive_analysis.py MSFT META NFLX --days 90
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from fetch_and_analyze import fetch_stock_data, calculate_all_factors


def create_comprehensive_chart(df: pd.DataFrame, ticker: str, output_dir: str = "analyses"):
    """
    Create a comprehensive multi-panel technical analysis chart.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with price data and technical indicators
    ticker : str
        Stock ticker symbol
    output_dir : str
        Output directory for saving the chart
    """
    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')

    # Create figure with GridSpec for better control
    fig = plt.figure(figsize=(18, 14))
    gs = GridSpec(6, 1, height_ratios=[3, 1, 1, 1, 1, 1], hspace=0.3)

    # Get data
    dates = df['date']
    price = df['adjusted_close']
    volume = df['volume']

    # Color scheme
    color_up = '#26a69a'  # Green
    color_down = '#ef5350'  # Red
    color_sma20 = '#2962ff'  # Blue
    color_sma50 = '#ff6d00'  # Orange
    color_sma200 = '#aa00ff'  # Purple

    # ============ PANEL 1: Price + SMAs + Bollinger Bands ============
    ax1 = fig.add_subplot(gs[0])

    # Plot price
    ax1.plot(dates, price, linewidth=1.5, color='black', label='Price', zorder=3)

    # Plot SMAs
    if 'sma_20' in df.columns:
        ax1.plot(dates, df['sma_20'], linewidth=1, color=color_sma20,
                label='SMA(20)', alpha=0.8, linestyle='--')
    if 'sma_50' in df.columns:
        ax1.plot(dates, df['sma_50'], linewidth=1, color=color_sma50,
                label='SMA(50)', alpha=0.8, linestyle='--')
    if 'sma_200' in df.columns:
        ax1.plot(dates, df['sma_200'], linewidth=1.5, color=color_sma200,
                label='SMA(200)', alpha=0.9, linestyle='-')

    # Plot Bollinger Bands
    if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
        ax1.fill_between(dates, df['bb_upper'], df['bb_lower'],
                         alpha=0.1, color='gray', label='Bollinger Bands')
        ax1.plot(dates, df['bb_upper'], linewidth=0.5, color='gray', alpha=0.5)
        ax1.plot(dates, df['bb_lower'], linewidth=0.5, color='gray', alpha=0.5)

    # Highlight current price position
    latest = df.iloc[-1]
    current_price = latest['adjusted_close']
    ax1.axhline(y=current_price, color='red', linestyle=':', linewidth=1, alpha=0.5)

    # Add annotations for key levels
    if 'sma_200' in df.columns and pd.notna(latest['sma_200']):
        dist_sma200 = (current_price / latest['sma_200'] - 1) * 100
        ax1.text(0.02, 0.97, f"Price vs SMA(200): {dist_sma200:+.1f}%",
                transform=ax1.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7),
                fontsize=10, fontweight='bold')

    ax1.set_ylabel('Price ($)', fontsize=12, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=8, ncol=2, framealpha=0.95,
              bbox_to_anchor=(0, 1), borderaxespad=0.5)
    ax1.grid(True, alpha=0.3)
    ax1.set_title(f'{ticker.upper()} - Comprehensive Technical Analysis\n'
                  f'Period: {dates.iloc[0].date()} to {dates.iloc[-1].date()} | '
                  f'Current Price: ${current_price:.2f}',
                  fontsize=16, fontweight='bold', pad=20)
    ax1.tick_params(axis='both', labelsize=10)
    ax1.set_xticklabels([])

    # ============ PANEL 2: Volume ============
    ax2 = fig.add_subplot(gs[1], sharex=ax1)

    # Color volume bars based on price change
    colors = [color_up if df.iloc[i]['adjusted_close'] >= df.iloc[i-1]['adjusted_close']
              else color_down for i in range(1, len(df))]
    colors.insert(0, color_up)  # First bar

    ax2.bar(dates, volume, color=colors, alpha=0.6, width=0.8)

    # Add volume moving average
    volume_ma = volume.rolling(window=20).mean()
    ax2.plot(dates, volume_ma, linewidth=1, color='navy', label='Volume MA(20)', alpha=0.8)

    # Add relative volume annotation
    if 'relative_volume' in df.columns and pd.notna(latest['relative_volume']):
        rvol = latest['relative_volume']
        rvol_text = f"Rel Vol: {rvol:.2f}x"
        rvol_color = 'red' if rvol > 1.5 else 'green' if rvol < 0.7 else 'black'
        ax2.text(0.02, 0.90, rvol_text, transform=ax2.transAxes,
                verticalalignment='top', fontsize=10, color=rvol_color,
                fontweight='bold', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax2.set_ylabel('Volume', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper left', fontsize=8, framealpha=0.95)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='both', labelsize=10)
    ax2.set_xticklabels([])
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))

    # ============ PANEL 3: RSI ============
    ax3 = fig.add_subplot(gs[2], sharex=ax1)

    if 'rsi_14' in df.columns:
        rsi = df['rsi_14']
        ax3.plot(dates, rsi, linewidth=1.5, color='purple', label='RSI(14)')

        # Overbought/Oversold zones
        ax3.axhline(y=70, color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax3.axhline(y=30, color='green', linestyle='--', linewidth=1, alpha=0.5)
        ax3.fill_between(dates, 70, 100, alpha=0.1, color='red')
        ax3.fill_between(dates, 0, 30, alpha=0.1, color='green')

        # Current RSI
        current_rsi = latest['rsi_14']
        rsi_status = 'OVERSOLD' if current_rsi < 30 else 'OVERBOUGHT' if current_rsi > 70 else 'NEUTRAL'
        rsi_color = 'green' if current_rsi < 30 else 'red' if current_rsi > 70 else 'black'
        ax3.text(0.02, 0.90, f"RSI: {current_rsi:.1f} ({rsi_status})",
                transform=ax3.transAxes, verticalalignment='top', fontsize=10,
                color=rsi_color, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        ax3.set_ylim([0, 100])
        ax3.set_ylabel('RSI', fontsize=12, fontweight='bold')
        ax3.legend(loc='upper left', fontsize=8, framealpha=0.95)
        ax3.grid(True, alpha=0.3)
        ax3.tick_params(axis='both', labelsize=10)
        ax3.set_xticklabels([])

    # ============ PANEL 4: MACD ============
    ax4 = fig.add_subplot(gs[3], sharex=ax1)

    if 'macd_line_12_26' in df.columns and 'macd_signal_9' in df.columns and 'macd_hist_12_26_9' in df.columns:
        # Use correct column names
        macd = df['macd_line_12_26']
        macd_signal = df['macd_signal_9']
        macd_hist = df['macd_hist_12_26_9']

        # Plot MACD and Signal line
        ax4.plot(dates, macd, linewidth=2, color='blue', label='MACD Line', zorder=3)
        ax4.plot(dates, macd_signal, linewidth=2, color='red', label='Signal Line', alpha=0.8, zorder=2)

        # Plot histogram
        colors_hist = [color_up if pd.notna(x) and x > 0 else color_down for x in macd_hist]
        ax4.bar(dates, macd_hist, color=colors_hist, alpha=0.6, width=1.5, zorder=1, label='Histogram')

        # Zero line
        ax4.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.7)

        # Current MACD
        if pd.notna(latest['macd_hist_12_26_9']):
            current_macd = latest['macd_hist_12_26_9']
            macd_status = 'BULLISH' if current_macd > 0 else 'BEARISH'
            macd_color = 'green' if current_macd > 0 else 'red'
            ax4.text(0.02, 0.90, f"MACD Hist: {current_macd:+.3f} ({macd_status})",
                    transform=ax4.transAxes, verticalalignment='top', fontsize=10,
                    color=macd_color, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    ax4.set_ylabel('MACD', fontsize=12, fontweight='bold')
    ax4.legend(loc='upper left', fontsize=8, framealpha=0.95)
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='both', labelsize=10)
    ax4.set_xticklabels([])

    # ============ PANEL 5: Stochastic ============
    ax5 = fig.add_subplot(gs[4], sharex=ax1)

    if 'stoch_k_14' in df.columns and 'stoch_d_3' in df.columns:
        # Use correct column names
        stoch_k = df['stoch_k_14']
        stoch_d = df['stoch_d_3']

        ax5.plot(dates, stoch_k, linewidth=2.5, color='blue', label='%K (Fast)', zorder=3)
        ax5.plot(dates, stoch_d, linewidth=2, color='red', label='%D (Slow)', alpha=0.8, zorder=2)

        # Overbought/Oversold zones
        ax5.axhline(y=80, color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax5.axhline(y=20, color='green', linestyle='--', linewidth=1, alpha=0.5)
        ax5.fill_between(dates, 80, 100, alpha=0.1, color='red')
        ax5.fill_between(dates, 0, 20, alpha=0.1, color='green')

        # Current Stochastic
        if pd.notna(latest['stoch_k_14']):
            current_stoch = latest['stoch_k_14']
            stoch_status = 'OVERSOLD' if current_stoch < 20 else 'OVERBOUGHT' if current_stoch > 80 else 'NEUTRAL'
            stoch_color = 'green' if current_stoch < 20 else 'red' if current_stoch > 80 else 'black'
            ax5.text(0.02, 0.90, f"Stoch %K: {current_stoch:.1f} ({stoch_status})",
                    transform=ax5.transAxes, verticalalignment='top', fontsize=10,
                    color=stoch_color, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    ax5.set_ylim([0, 100])
    ax5.set_ylabel('Stochastic', fontsize=12, fontweight='bold')
    ax5.legend(loc='upper left', fontsize=8, framealpha=0.95)
    ax5.grid(True, alpha=0.3)
    ax5.tick_params(axis='both', labelsize=10)
    ax5.set_xticklabels([])

    # ============ PANEL 6: ADX (Trend Strength) ============
    ax6 = fig.add_subplot(gs[5], sharex=ax1)

    if 'adx_14' in df.columns:
        adx = df['adx_14']
        ax6.plot(dates, adx, linewidth=1.5, color='black', label='ADX(14)')

        # Trend strength zones
        ax6.axhline(y=25, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Strong Trend (25)')
        ax6.fill_between(dates, 25, 100, alpha=0.1, color='red')
        ax6.fill_between(dates, 0, 25, alpha=0.1, color='gray')

        # Current ADX
        current_adx = latest['adx_14']
        adx_status = 'STRONG TREND' if current_adx > 25 else 'WEAK TREND'
        adx_color = 'red' if current_adx > 25 else 'gray'
        ax6.text(0.02, 0.90, f"ADX: {current_adx:.1f} ({adx_status})",
                transform=ax6.transAxes, verticalalignment='top', fontsize=10,
                color=adx_color, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        ax6.set_ylim([0, max(50, adx.max() * 1.1)])
        ax6.set_ylabel('ADX', fontsize=12, fontweight='bold')
        ax6.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax6.legend(loc='upper left', fontsize=8, framealpha=0.95)
        ax6.grid(True, alpha=0.3)
        ax6.tick_params(axis='both', labelsize=10)

    # Format x-axis for bottom panel
    ax6.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax6.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.setp(ax6.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=10)

    # Adjust layout
    plt.subplots_adjust(left=0.08, right=0.95, top=0.95, bottom=0.08)

    # Save figure
    output_path = Path(__file__).parent.parent / output_dir
    output_path.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{ticker.upper()}_Comprehensive_Chart_{timestamp}.png"
    filepath = output_path / filename

    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    print(f"\n[OK] Chart saved to: {filepath}")

    return str(filepath)


def create_comparison_chart(data_dict: dict, output_dir: str = "analyses"):
    """
    Create a comparison chart for multiple tickers.

    Parameters
    ----------
    data_dict : dict
        Dictionary with ticker: DataFrame pairs
    output_dir : str
        Output directory
    """
    fig, axes = plt.subplots(len(data_dict), 1, figsize=(18, 5*len(data_dict)))

    if len(data_dict) == 1:
        axes = [axes]

    for idx, (ticker, df) in enumerate(data_dict.items()):
        ax = axes[idx]

        dates = df['date']
        price = df['adjusted_close']

        # Normalize price to 100 at start
        price_normalized = (price / price.iloc[0]) * 100

        ax.plot(dates, price_normalized, linewidth=2.5, label=f'{ticker} (Normalized)', color='darkblue')

        # Add SMAs
        if 'sma_20' in df.columns:
            sma20_norm = (df['sma_20'] / price.iloc[0]) * 100
            ax.plot(dates, sma20_norm, linewidth=1.5, linestyle='--', alpha=0.7, label='SMA(20)', color='orange')

        if 'sma_50' in df.columns:
            sma50_norm = (df['sma_50'] / price.iloc[0]) * 100
            ax.plot(dates, sma50_norm, linewidth=1.5, linestyle='--', alpha=0.7, label='SMA(50)', color='red')

        # Add trend info
        latest = df.iloc[-1]
        if 'adx_14' in df.columns and 'rsi_14' in df.columns:
            info_text = f"ADX: {latest['adx_14']:.1f} | RSI: {latest['rsi_14']:.1f}"
            ax.text(0.02, 0.95, info_text, transform=ax.transAxes,
                   verticalalignment='top', fontsize=11, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

        ax.set_ylabel('Price (Base 100)', fontsize=13, fontweight='bold')
        ax.set_title(f'{ticker.upper()} - Trend Analysis', fontsize=14, fontweight='bold', pad=15)
        ax.legend(loc='upper left', fontsize=9, framealpha=0.95, ncol=1)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=100, color='black', linestyle=':', linewidth=1, alpha=0.5)
        ax.tick_params(axis='both', labelsize=11)

    axes[-1].set_xlabel('Date', fontsize=13, fontweight='bold')
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    axes[-1].xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.setp(axes[-1].xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=11)

    plt.subplots_adjust(left=0.08, right=0.95, top=0.96, bottom=0.08, hspace=0.25)

    # Save
    output_path = Path(__file__).parent.parent / output_dir
    output_path.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    tickers_str = '_'.join(data_dict.keys())
    filename = f"{tickers_str}_Comparison_{timestamp}.png"
    filepath = output_path / filename

    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    print(f"\n[OK] Comparison chart saved to: {filepath}")

    return str(filepath)


def main():
    parser = argparse.ArgumentParser(
        description='Create comprehensive technical analysis charts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python plot_comprehensive_analysis.py NFLX --days 60
  python plot_comprehensive_analysis.py MSFT META NFLX --days 90
        """
    )
    parser.add_argument('tickers', nargs='+', help='Stock ticker symbol(s)')
    parser.add_argument('--days', type=int, default=60, help='Number of days to plot (default: 60)')
    parser.add_argument('--lookback', type=int, default=365, help='Days of historical data (default: 365)')
    parser.add_argument('--comparison', action='store_true', help='Create comparison chart')

    args = parser.parse_args()

    try:
        print(f"\n{'='*60}")
        print("CREATING COMPREHENSIVE TECHNICAL CHARTS")
        print(f"{'='*60}")

        data_dict = {}

        for ticker in args.tickers:
            print(f"\nProcessing {ticker.upper()}...")

            # Fetch and calculate
            df = fetch_stock_data(ticker, lookback_days=args.lookback)
            df_with_factors = calculate_all_factors(df)

            # Get recent data
            df_sorted = df_with_factors.sort_values('date', ascending=False)
            df_recent = df_sorted.head(args.days).sort_values('date', ascending=True)

            data_dict[ticker.upper()] = df_recent

            # Create individual chart
            create_comprehensive_chart(df_recent, ticker)

        # Create comparison chart if multiple tickers
        if len(args.tickers) > 1 and args.comparison:
            print(f"\n{'='*60}")
            print("Creating comparison chart...")
            print(f"{'='*60}")
            create_comparison_chart(data_dict)

        print(f"\n{'='*60}")
        print("[OK] ALL CHARTS CREATED!")
        print(f"{'='*60}")

    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
