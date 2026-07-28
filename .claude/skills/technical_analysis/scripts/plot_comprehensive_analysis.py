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


def identify_support_resistance(df: pd.DataFrame, window: int = 10, num_levels: int = 3):
    """
    Identify key support and resistance levels from price action.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with price data
    window : int
        Window for identifying local extrema (swing highs/lows)
    num_levels : int
        Number of support/resistance levels to return

    Returns
    -------
    dict with 'support' and 'resistance' lists
    """
    price = df['adjusted_close'].values
    high = df['high'].values if 'high' in df.columns else price
    low = df['low'].values if 'low' in df.columns else price

    # Find swing highs and lows
    swing_highs = []
    swing_lows = []

    for i in range(window, len(price) - window):
        # Swing high: local maximum
        if high[i] == max(high[i-window:i+window+1]):
            swing_highs.append(high[i])
        # Swing low: local minimum
        if low[i] == min(low[i-window:i+window+1]):
            swing_lows.append(low[i])

    # Cluster nearby levels (within 1.5% of each other)
    # Reduced from 2% to keep more distinct levels
    def cluster_levels(levels, tolerance=0.015):
        if not levels:
            return []
        levels = sorted(levels)
        clusters = []
        current_cluster = [levels[0]]

        for level in levels[1:]:
            if (level - current_cluster[-1]) / current_cluster[-1] <= tolerance:
                current_cluster.append(level)
            else:
                clusters.append(np.mean(current_cluster))
                current_cluster = [level]
        clusters.append(np.mean(current_cluster))
        return clusters

    # Get current price
    current_price = price[-1]

    # Cluster swing highs and lows
    resistance_levels = cluster_levels(swing_highs)
    support_levels = cluster_levels(swing_lows)

    # Also add period highs/lows (various timeframes) as they are important levels
    # Use multiple windows to capture different timeframe levels: short-term to long-term
    for period in [20, 40, 50, 60, 80, 100, 120, 150, 180]:
        if len(high) >= period:
            resistance_levels.append(high[-period:].max())
        if len(low) >= period:
            support_levels.append(low[-period:].min())

    # Re-cluster to merge any duplicates from period highs/lows
    resistance_levels = cluster_levels(resistance_levels)
    support_levels = cluster_levels(support_levels)

    # Filter to get levels near current price (within 50% range for more coverage)
    resistance_levels = [r for r in resistance_levels if r > current_price and r < current_price * 1.50]
    support_levels = [s for s in support_levels if s < current_price and s > current_price * 0.50]

    # If we don't have enough resistance levels, add psychological round-number levels
    # Round numbers (like $320, $325, $330) are important psychological levels for traders
    if len(resistance_levels) < num_levels:
        # Determine appropriate round number interval based on price
        if current_price < 20:
            interval = 1  # $1 intervals for low-priced stocks
        elif current_price < 100:
            interval = 5  # $5 intervals
        elif current_price < 500:
            interval = 10  # $10 intervals
        else:
            interval = 25  # $25 intervals for high-priced stocks

        # Add round numbers above current price
        psychological_levels = []
        next_round = (int(current_price / interval) + 1) * interval
        for i in range(5):  # Add up to 5 round number levels
            level = next_round + (i * interval)
            if level < current_price * 1.50:  # Within detection range
                psychological_levels.append(float(level))

        # Add psychological levels and re-cluster
        resistance_levels.extend(psychological_levels)
        resistance_levels = cluster_levels(resistance_levels)
        # Re-filter after adding psychological levels
        resistance_levels = [r for r in resistance_levels if r > current_price and r < current_price * 1.50]

    # Similarly add round numbers for support if needed
    if len(support_levels) < num_levels:
        if current_price < 20:
            interval = 1
        elif current_price < 100:
            interval = 5
        elif current_price < 500:
            interval = 10
        else:
            interval = 25

        psychological_levels = []
        prev_round = (int(current_price / interval)) * interval
        for i in range(5):
            level = prev_round - (i * interval)
            if level > current_price * 0.50 and level > 0:
                psychological_levels.append(float(level))

        support_levels.extend(psychological_levels)
        support_levels = cluster_levels(support_levels)
        support_levels = [s for s in support_levels if s < current_price and s > current_price * 0.50]

    # Sort by proximity to current price and take top N
    resistance_levels = sorted(resistance_levels)[:num_levels]
    support_levels = sorted(support_levels, reverse=True)[:num_levels]

    return {
        'support': support_levels,
        'resistance': resistance_levels
    }


def create_comprehensive_chart(df: pd.DataFrame, ticker: str, output_dir: str = "analyses", plot_days: int = None):
    """
    Create a comprehensive multi-panel technical analysis chart.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with price data and technical indicators (may include extra history for MA calculations)
    ticker : str
        Stock ticker symbol
    output_dir : str
        Output directory for saving the chart
    plot_days : int, optional
        Number of most recent days to plot (if None, plot all data in df)
    """
    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')

    # Calculate volume MA(20) on the FULL dataset BEFORE any filtering
    # This ensures the MA is complete even at the start of our display window
    df = df.copy()
    df['volume_ma_20'] = df['volume'].rolling(window=20).mean()

    # ALWAYS show 91 CALENDAR days in chart panels (3 months of data)
    # This overrides the plot_days parameter
    # Calculate date 91 calendar days before the latest date
    latest_date = df['date'].max()
    start_date = latest_date - pd.Timedelta(days=91)

    # Keep the full dataframe for support/resistance detection (more context)
    df_full = df.copy()

    # Now filter to only the 91 display days (volume MA is already calculated and complete)
    df = df[df['date'] >= start_date].copy()

    print(f"Chart displaying 91 calendar days: {start_date.strftime('%Y-%m-%d')} to {latest_date.strftime('%Y-%m-%d')}")
    print(f"Volume MA(20) covers full date range (calculated on complete dataset)")

    # Create figure with GridSpec for better control
    # Layout: 6 rows (Price, Volume, ATR, RSI, MACD, ADX) x 2 columns (Charts + Analysis Panel)
    fig = plt.figure(figsize=(20, 16))
    gs = GridSpec(6, 2, height_ratios=[2.5, 0.8, 0.8, 1, 1, 1], width_ratios=[5, 1],
                  hspace=0.3, wspace=0.05)

    # Get data
    dates = df['date']
    price = df['adjusted_close']
    volume = df['volume']

    # IMPROVED Color scheme - High contrast, distinct colors
    color_up = '#00c853'      # Bright Green
    color_down = '#ff1744'    # Bright Red
    color_price = '#000000'   # Black (price line - most important)
    color_sma20 = '#2196f3'   # Blue (short-term)
    color_sma50 = '#ff9800'   # Orange (medium-term)
    color_sma200 = '#9c27b0'  # Purple (long-term)
    color_support = '#00c853' # Green (support)
    color_resistance = '#ff1744'  # Red (resistance)

    # ============ PANEL 1: Price (NO volume - volume is separate panel) ============
    ax1 = fig.add_subplot(gs[0, 0])

    # Plot price on left axis - THICKEST, BLACK, MOST PROMINENT
    ax1.plot(dates, price, linewidth=3, color=color_price, label='Price', zorder=10, alpha=0.9)

    # Plot ONLY SMA(50) and SMA(200) as requested
    if 'sma_50' in df.columns:
        ax1.plot(dates, df['sma_50'], linewidth=2.5, color=color_sma50,
                label='SMA(50)', alpha=0.9, linestyle='-', zorder=2)
    if 'sma_200' in df.columns:
        ax1.plot(dates, df['sma_200'], linewidth=3, color=color_sma200,
                label='SMA(200)', alpha=0.95, linestyle='-', zorder=1)

    # Plot Bollinger Bands - MUCH MORE VISIBLE
    if 'bb_upper' in df.columns and 'bb_lower' in df.columns and 'bb_middle' in df.columns:
        # Fill between bands with higher alpha
        ax1.fill_between(dates, df['bb_upper'], df['bb_lower'],
                         alpha=0.15, color='#2196f3', label='Bollinger Bands', zorder=0)

        # Plot band lines - SOLID and MORE VISIBLE
        ax1.plot(dates, df['bb_upper'], linewidth=1.5, color='#2196f3',
                alpha=0.6, linestyle='--', zorder=2, label='BB Upper')
        ax1.plot(dates, df['bb_middle'], linewidth=1.5, color='#2196f3',
                alpha=0.6, linestyle='-', zorder=2, label='BB Middle (SMA20)')
        ax1.plot(dates, df['bb_lower'], linewidth=1.5, color='#2196f3',
                alpha=0.6, linestyle='--', zorder=2, label='BB Lower')

    # Highlight current price position
    latest = df.iloc[-1]
    current_price = latest['adjusted_close']
    ax1.axhline(y=current_price, color='red', linestyle=':', linewidth=1, alpha=0.5)

    # Identify support/resistance levels using FULL dataset for better detection
    # Use df_full (complete data) instead of df (91-day filtered) to find more levels
    # Use window=5 for more granular swing detection and num_levels=2 (R1/R2, S1/S2)
    sr_levels = identify_support_resistance(df_full, window=5, num_levels=2)

    # Debug: Print detected levels
    print(f"\nDetected S/R levels for chart:")
    print(f"  Current price: ${current_price:.2f}")
    print(f"  Resistance: {len(sr_levels['resistance'])} levels - {[f'${r:.2f}' for r in sr_levels['resistance']]}")
    print(f"  Support: {len(sr_levels['support'])} levels - {[f'${s:.2f}' for s in sr_levels['support']]}")

    # Calculate label position (just inside left edge of chart to avoid covering y-axis)
    # Position at ~3% into the date range
    date_range = (dates.iloc[-1] - dates.iloc[0]).days
    label_x_pos = dates.iloc[0] + pd.Timedelta(days=int(date_range * 0.03))

    # Plot resistance levels (above current price) - IMPROVED STYLING
    for i, resistance in enumerate(sr_levels['resistance'], 1):
        ax1.axhline(y=resistance, color=color_resistance, linestyle='--',
                   linewidth=2, alpha=0.7, zorder=6)
        distance_pct = ((resistance / current_price) - 1) * 100
        # Label inside chart area on the left to avoid covering y-axis
        ax1.text(label_x_pos, resistance, f' R{i}: ${resistance:.2f} (+{distance_pct:.1f}%)',
                verticalalignment='center', horizontalalignment='left',
                fontsize=9, color='white', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=color_resistance,
                         edgecolor='white', linewidth=1.5, alpha=0.9), zorder=20)

    # Plot support levels (below current price) - IMPROVED STYLING
    for i, support in enumerate(sr_levels['support'], 1):
        ax1.axhline(y=support, color=color_support, linestyle='--',
                   linewidth=2, alpha=0.7, zorder=6)
        distance_pct = ((support / current_price) - 1) * 100
        # Label inside chart area on the left to avoid covering y-axis
        ax1.text(label_x_pos, support, f' S{i}: ${support:.2f} ({distance_pct:.1f}%)',
                verticalalignment='center', horizontalalignment='left',
                fontsize=9, color='white', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=color_support,
                         edgecolor='white', linewidth=1.5, alpha=0.9), zorder=20)

    # Volume removed from price panel - now has its own panel below

    # Check MA trend alignment (using SMA 50 and 200 only)
    ma_trend_text = ""
    ma_trend_color = 'gray'

    # Check if we have both SMAs
    if all(col in df.columns for col in ['sma_50', 'sma_200']) and \
       all(pd.notna(latest[col]) for col in ['sma_50', 'sma_200']):

        ma50 = latest['sma_50']
        ma200 = latest['sma_200']
        price_val = latest['adjusted_close']

        # Strong uptrend: Price > MA50 > MA200
        if price_val > ma50 and ma50 > ma200:
            ma_trend_text = "TREND: BULLISH"
            ma_trend_color = '#00c853'  # Bright green

        # Strong downtrend: Price < MA50 < MA200
        elif price_val < ma50 and ma50 < ma200:
            ma_trend_text = "TREND: BEARISH"
            ma_trend_color = '#ff1744'  # Bright red

        # Transitional: Price between SMAs
        else:
            ma_trend_text = "TREND: NEUTRAL"
            ma_trend_color = '#ff9800'  # Orange

    # Info boxes removed - will be shown in right-side analysis panel

    ax1.set_ylabel('Price ($)', fontsize=12, fontweight='bold')

    # Legend - only price panel items (no volume)
    lines1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(lines1, labels1, loc='upper right',
              fontsize=10, ncol=3, framealpha=0.95, edgecolor='gray', fancybox=True)

    ax1.grid(True, alpha=0.25, linestyle=':', linewidth=0.5)

    # IMPROVED: Cleaner title with better formatting
    ax1.set_title(f'{ticker.upper()} - 91-Day Technical Analysis (3 Months)\n'
                  f'Period: {dates.iloc[0].strftime("%Y-%m-%d")} to {dates.iloc[-1].strftime("%Y-%m-%d")} | '
                  f'Current Price: ${current_price:.2f}',
                  fontsize=17, fontweight='bold', pad=20, color='#1a237e')
    ax1.tick_params(axis='both', labelsize=10)
    ax1.set_xticklabels([])

    # ============ PANEL 2: Volume ============
    ax2 = fig.add_subplot(gs[1, 0], sharex=ax1)

    # Color volume bars based on price change
    colors = [color_up if df.iloc[i]['adjusted_close'] >= df.iloc[i-1]['adjusted_close']
              else color_down for i in range(1, len(df))]
    colors.insert(0, color_up)  # First bar

    # Plot volume bars with better visibility
    ax2.bar(dates, volume, color=colors, alpha=0.6, width=0.8, label='Volume', zorder=2)

    # Plot volume moving average if available
    if 'volume_ma_20' in df.columns:
        ax2.plot(dates, df['volume_ma_20'], linewidth=2, color='#1a237e',
                label='Volume MA(20)', alpha=0.8, linestyle='-', zorder=3)

    ax2.set_ylabel('Volume', fontsize=12, fontweight='bold')
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))
    ax2.legend(loc='upper right', fontsize=10, framealpha=0.95, edgecolor='gray')
    ax2.grid(True, alpha=0.25, linestyle=':', linewidth=0.5)
    ax2.tick_params(axis='both', labelsize=10)
    ax2.set_xticklabels([])

    # ============ PANEL 3: ATR - Average True Range ============
    ax3 = fig.add_subplot(gs[2, 0], sharex=ax1)

    if 'atr_14' in df.columns:
        atr = df['atr_14']
        # Plot ATR line
        ax3.plot(dates, atr, linewidth=2.5, color='#ff6f00', label='ATR(14)', zorder=5)

        # Calculate ATR as % of price for reference
        atr_pct = (atr / price) * 100

        # Current ATR with better styling
        current_atr = latest['atr_14']
        current_atr_pct = (current_atr / current_price) * 100

        # Color based on volatility level
        if current_atr_pct > 5:
            atr_status = 'VERY HIGH'
            atr_color = '#d32f2f'  # Dark red
        elif current_atr_pct > 3:
            atr_status = 'HIGH'
            atr_color = '#ff6f00'  # Orange
        elif current_atr_pct < 1.5:
            atr_status = 'LOW'
            atr_color = '#388e3c'  # Green
        else:
            atr_status = 'NORMAL'
            atr_color = '#1976d2'  # Blue

        # ATR status removed - shown in right panel
        pass

        # Add stop-loss reference lines (1x, 1.5x, 2x ATR)
        ax3.axhline(y=current_atr, color=atr_color, linestyle='-', linewidth=1.5, alpha=0.4)
        ax3.axhline(y=current_atr * 1.5, color='#ff9800', linestyle='--', linewidth=1, alpha=0.3, label='1.5x ATR')
        ax3.axhline(y=current_atr * 2, color='#f44336', linestyle='--', linewidth=1, alpha=0.3, label='2x ATR')

        ax3.set_ylabel('ATR ($)', fontsize=12, fontweight='bold')
        ax3.legend(loc='upper right', fontsize=9, framealpha=0.95, edgecolor='gray')
        ax3.grid(True, alpha=0.25, linestyle=':', linewidth=0.5)
        ax3.tick_params(axis='both', labelsize=10)
        ax3.set_xticklabels([])

    # ============ PANEL 4: RSI (IMPROVED) ============
    ax4 = fig.add_subplot(gs[3, 0], sharex=ax1)

    if 'rsi_14' in df.columns:
        rsi = df['rsi_14']
        # Thicker line with better color
        ax4.plot(dates, rsi, linewidth=2.5, color='#9c27b0', label='RSI(14)', zorder=5)

        # Overbought/Oversold zones - more visible
        ax4.axhline(y=70, color=color_resistance, linestyle='--', linewidth=1.5, alpha=0.6)
        ax4.axhline(y=30, color=color_support, linestyle='--', linewidth=1.5, alpha=0.6)
        ax4.fill_between(dates, 70, 100, alpha=0.12, color=color_resistance)
        ax4.fill_between(dates, 0, 30, alpha=0.12, color=color_support)

        # Current RSI with better styling
        current_rsi = latest['rsi_14']
        rsi_status = 'OVERSOLD' if current_rsi < 30 else 'OVERBOUGHT' if current_rsi > 70 else 'NEUTRAL'
        rsi_color = color_support if current_rsi < 30 else color_resistance if current_rsi > 70 else '#ff9800'
        # RSI status removed - shown in right panel
        pass

        ax4.set_ylim([0, 100])
        ax4.set_ylabel('RSI', fontsize=12, fontweight='bold')
        ax4.legend(loc='upper right', fontsize=10, framealpha=0.95, edgecolor='gray')
        ax4.grid(True, alpha=0.25, linestyle=':', linewidth=0.5)
        ax4.tick_params(axis='both', labelsize=10)
        ax4.set_xticklabels([])

    # ============ PANEL 5: MACD (IMPROVED) ============
    ax5 = fig.add_subplot(gs[4, 0], sharex=ax1)

    if 'macd_line_12_26' in df.columns and 'macd_signal_9' in df.columns and 'macd_hist_12_26_9' in df.columns:
        macd = df['macd_line_12_26']
        macd_signal = df['macd_signal_9']
        macd_hist = df['macd_hist_12_26_9']

        # Plot histogram FIRST (background) with better visibility
        colors_hist = [color_up if pd.notna(x) and x > 0 else color_down for x in macd_hist]
        ax5.bar(dates, macd_hist, color=colors_hist, alpha=0.6, width=1.5, zorder=1, label='Histogram')

        # Plot MACD and Signal lines with better colors
        ax5.plot(dates, macd, linewidth=2.5, color='#2196f3', label='MACD', zorder=3)
        ax5.plot(dates, macd_signal, linewidth=2.5, color='#ff9800', label='Signal', alpha=0.9, zorder=2)

        # Zero line - more prominent
        ax5.axhline(y=0, color='black', linestyle='-', linewidth=1.5, alpha=0.5)

        # Current MACD with better styling
        if pd.notna(latest['macd_hist_12_26_9']):
            current_macd = latest['macd_hist_12_26_9']
            macd_status = 'BULLISH' if current_macd > 0 else 'BEARISH'
            macd_color = color_support if current_macd > 0 else color_resistance
            # MACD status removed - shown in right panel
            pass

    ax5.set_ylabel('MACD', fontsize=12, fontweight='bold')
    ax5.legend(loc='upper right', fontsize=10, framealpha=0.95, edgecolor='gray')
    ax5.grid(True, alpha=0.25, linestyle=':', linewidth=0.5)
    ax5.tick_params(axis='both', labelsize=10)
    ax5.set_xticklabels([])

    # ============ PANEL 6: ADX - Trend Strength (IMPROVED) ============
    ax6 = fig.add_subplot(gs[5, 0], sharex=ax1)

    if 'adx_14' in df.columns:
        adx = df['adx_14']
        # Thicker line with better color
        ax6.plot(dates, adx, linewidth=2.5, color='#1a237e', label='ADX(14)', zorder=5)

        # Trend strength zone - more visible
        ax6.axhline(y=25, color='#9c27b0', linestyle='--', linewidth=1.5, alpha=0.6, label='Strong Trend (25)')
        ax6.fill_between(dates, 25, 100, alpha=0.12, color='#9c27b0')
        ax6.fill_between(dates, 0, 25, alpha=0.08, color='gray')

        # Current ADX with better styling
        current_adx = latest['adx_14']
        adx_status = 'STRONG TREND' if current_adx > 25 else 'WEAK TREND'
        adx_color = '#9c27b0' if current_adx > 25 else '#9e9e9e'
        # ADX status removed - shown in right panel
        pass

        ax6.set_ylim([0, max(50, adx.max() * 1.1)])
        ax6.set_ylabel('ADX', fontsize=12, fontweight='bold')
        ax6.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax6.legend(loc='upper right', fontsize=10, framealpha=0.95, edgecolor='gray')
        ax6.grid(True, alpha=0.25, linestyle=':', linewidth=0.5)
        ax6.tick_params(axis='both', labelsize=10)

    # Format x-axis for bottom panel
    ax6.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax6.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.setp(ax6.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=10)

    # ============ RIGHT PANEL: ANALYSIS SUMMARY ============
    # Create right-side analysis panel spanning all rows
    ax_analysis = fig.add_subplot(gs[:, 1])
    ax_analysis.axis('off')  # Hide axes

    # Collect all metrics
    analysis_text = []

    # Header
    analysis_text.append("ANALYSIS PANEL")
    analysis_text.append("=" * 25)
    analysis_text.append("")

    # Trend info
    if ma_trend_text:
        trend_simple = ma_trend_text.replace("TREND: ", "")
        analysis_text.append(f"Trend      : {trend_simple}")

    # Current price
    analysis_text.append(f"Price      : ${current_price:.2f}")

    # SMAs
    if 'sma_20' in df.columns and 'bb_middle' in df.columns and pd.notna(latest['bb_middle']):
        analysis_text.append(f"SMA20      : ${latest['bb_middle']:.2f}")
    if 'sma_50' in df.columns and pd.notna(latest['sma_50']):
        analysis_text.append(f"SMA50      : ${latest['sma_50']:.2f}")
    if 'sma_200' in df.columns and pd.notna(latest['sma_200']):
        analysis_text.append(f"SMA200     : ${latest['sma_200']:.2f}")

    analysis_text.append("")

    # RSI
    if 'rsi_14' in df.columns and pd.notna(latest['rsi_14']):
        current_rsi = latest['rsi_14']
        rsi_status = 'Oversold' if current_rsi < 30 else 'Overbought' if current_rsi > 70 else 'Neutral'
        analysis_text.append(f"RSI        : {current_rsi:.1f} {rsi_status}")

    # MACD
    if 'macd_hist_12_26_9' in df.columns and pd.notna(latest['macd_hist_12_26_9']):
        current_macd = latest['macd_hist_12_26_9']
        macd_status = 'Bullish' if current_macd > 0 else 'Bearish'
        analysis_text.append(f"MACD       : {macd_status}")

    # ADX
    if 'adx_14' in df.columns and pd.notna(latest['adx_14']):
        current_adx = latest['adx_14']
        adx_status = 'Strong' if current_adx > 25 else 'Weak'
        analysis_text.append(f"ADX        : {current_adx:.1f} {adx_status}")

    analysis_text.append("")

    # Support/Resistance from identified levels (reuse from earlier detection)
    # Note: sr_levels was already calculated above using df_full

    # Show Resistance levels (R1, R2)
    if sr_levels['resistance']:
        analysis_text.append("Resistance")
        for i, resistance in enumerate(sr_levels['resistance'], 1):
            r_pct = ((resistance / current_price) - 1) * 100
            analysis_text.append(f"R{i}         : ${resistance:.2f} (+{r_pct:.1f}%)")

    # Show Support levels (S1, S2)
    if sr_levels['support']:
        if sr_levels['resistance']:
            analysis_text.append("")  # Add spacing between resistance and support
        analysis_text.append("Support")
        for i, support in enumerate(sr_levels['support'], 1):
            s_pct = ((support / current_price) - 1) * 100
            analysis_text.append(f"S{i}         : ${support:.2f} ({s_pct:.1f}%)")

    analysis_text.append("")

    # ATR
    if 'atr_14' in df.columns and pd.notna(latest['atr_14']):
        current_atr = latest['atr_14']
        current_atr_pct = (current_atr / current_price) * 100
        analysis_text.append(f"ATR        : ${current_atr:.2f} ({current_atr_pct:.1f}%)")

    # Relative Volume
    if 'relative_volume' in df.columns and pd.notna(latest['relative_volume']):
        rvol = latest['relative_volume']
        analysis_text.append(f"Rel Volume : {rvol:.2f}x")

    # ============ 91-DAY PRICE TREND (3 MONTHS) ============
    analysis_text.append("")
    analysis_text.append("=" * 25)
    analysis_text.append("91-DAY TREND (3 Months)")
    analysis_text.append("=" * 25)

    # Use the already filtered df which contains 91 calendar days
    if len(df) >= 2:
        # df already contains 91 calendar days of data
        price_start = df.iloc[0]['adjusted_close']
        price_end = df.iloc[-1]['adjusted_close']
        price_high = df['adjusted_close'].max()
        price_low = df['adjusted_close'].min()

        # Calculate return over the period
        return_pct = ((price_end / price_start) - 1) * 100

        # Price range
        range_pct = ((price_high - price_low) / price_low) * 100

        analysis_text.append(f"Start      : ${price_start:.2f}")
        analysis_text.append(f"Current    : ${price_end:.2f}")
        analysis_text.append(f"Return     : {return_pct:+.1f}%")
        analysis_text.append("")
        analysis_text.append(f"Period High: ${price_high:.2f}")
        analysis_text.append(f"Period Low : ${price_low:.2f}")
        analysis_text.append(f"Range      : {range_pct:.1f}%")

        # Simple trend direction over the period
        if return_pct > 5:
            trend_period = "Uptrend"
        elif return_pct < -5:
            trend_period = "Downtrend"
        else:
            trend_period = "Sideways"

        analysis_text.append("")
        analysis_text.append(f"Direction  : {trend_period}")

    # Add the text to the panel
    analysis_string = '\n'.join(analysis_text)

    # Determine background color based on trend
    if 'BULLISH' in ma_trend_text:
        bg_color = '#e8f5e9'  # Light green
        text_color = '#1b5e20'  # Dark green
    elif 'BEARISH' in ma_trend_text:
        bg_color = '#ffebee'  # Light red
        text_color = '#b71c1c'  # Dark red
    else:
        bg_color = '#fff3e0'  # Light orange
        text_color = '#e65100'  # Dark orange

    # Add background rectangle
    ax_analysis.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax_analysis.transAxes,
                                        facecolor=bg_color, edgecolor='#424242',
                                        linewidth=2, zorder=0))

    # Add text
    ax_analysis.text(0.05, 0.98, analysis_string,
                    transform=ax_analysis.transAxes, verticalalignment='top',
                    fontfamily='monospace', fontsize=10, fontweight='normal',
                    color=text_color, zorder=10)

    # Adjust layout to accommodate right panel
    plt.subplots_adjust(left=0.05, right=0.98, top=0.95, bottom=0.08)

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

        # Calculate required lookback to ensure MAs are valid from start of plot
        # MA20 is the longest short-term MA we're showing, so we need at least 20 extra days
        max_ma_period = 20
        required_lookback = args.days + max_ma_period + 10  # Add 10 buffer days
        actual_lookback = max(args.lookback, required_lookback)

        if actual_lookback > args.lookback:
            print(f"[INFO] Fetching {actual_lookback} days (instead of {args.lookback}) to ensure MAs are complete")

        data_dict = {}

        for ticker in args.tickers:
            print(f"\nProcessing {ticker.upper()}...")

            # Fetch and calculate with sufficient history
            df = fetch_stock_data(ticker, lookback_days=actual_lookback)
            df_with_factors = calculate_all_factors(df)

            # Get recent data for plotting (keep extra for volume MA calculation)
            # We need plot_days + 20 (for volume MA) to ensure complete data
            df_sorted = df_with_factors.sort_values('date', ascending=False)
            data_with_history = df_sorted.head(args.days + max_ma_period).sort_values('date', ascending=True)

            data_dict[ticker.upper()] = data_with_history

            # Create individual chart (will only plot the requested days but use extra history for MAs)
            create_comprehensive_chart(data_with_history, ticker, plot_days=args.days)

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
