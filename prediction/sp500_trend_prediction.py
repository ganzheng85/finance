"""
S&P 500 Uptrend/Downtrend Prediction using VIX, Volume, and Moving Averages
============================================================================

This module demonstrates how to:
1. Define uptrend/downtrend using technical indicators
2. Build composite signals from VIX, volume, and moving averages
3. Backtest signal accuracy and strategy performance

Author: Finance Analysis
Date: 2025-12-06
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

# ==============================================================================
# SECTION 1: TREND DEFINITION
# ==============================================================================
"""
Uptrend vs Downtrend Definition:

1. PRIMARY SIGNAL (Price vs EMA):
   - Uptrend: Close > EMA_50 (price above short-term average)
   - Downtrend: Close < EMA_50 (price below short-term average)

2. CONFIRMATION SIGNALS:
   a) EMA Slope: Compare EMA_50 vs EMA_200 (or check rate of change)
      - Uptrend: EMA_50 > EMA_200 AND EMA_50 rising
      - Downtrend: EMA_50 < EMA_200 AND EMA_50 falling
   
   b) VIX Regime (Volatility):
      - Low VIX (<20): Calm market, supports uptrend
      - High VIX (>25): Fearful market, supports downtrend
   
   c) Volume Confirmation:
      - Uptrend + High Volume: Strong buying, high confidence
      - Downtrend + High Volume: Strong selling, high confidence
      - Divergence (trend with low volume): Weak signal

3. COMPOSITE SIGNAL STRENGTH (0-10 scale):
   - Base score 5 (neutral)
   - Add +1 for each uptrend confirmation
   - Subtract -1 for each downtrend confirmation
"""

def calculate_trend_indicators(ticker='SPY', start_date='2015-01-01', end_date='2025-12-06'):
    """
    Download data and compute trend indicators for S&P 500 proxy.
    
    Parameters:
    -----------
    ticker : str
        Ticker symbol (SPY, SPX, or IVV)
    start_date : str
        Start date in YYYY-MM-DD format
    end_date : str
        End date in YYYY-MM-DD format
    
    Returns:
    --------
    pd.DataFrame with columns:
        Close, Volume, EMA_50, EMA_200, EMA_slope_50, VIX, Volume_MA,
        Volume_Ratio, Uptrend_Signal, Downtrend_Signal, Composite_Signal
    """
    print(f"Downloading {ticker} data from {start_date} to {end_date}...")
    
    # Download price and volume data
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)
    data.index = pd.to_datetime(data.index)
    
    # Download VIX (CBOE Volatility Index) for fear gauge
    print("Downloading VIX (Volatility Index)...")
    vix = yf.download('^VIX', start=start_date, end=end_date, progress=False)['Close']
    
    # Ensure VIX index matches data index
    data['VIX'] = vix
    data['VIX'].fillna(method='ffill', inplace=True)
    
    # ========================================================================
    # 1. MOVING AVERAGES (EMA for responsiveness to recent price action)
    # ========================================================================
    data['EMA_50'] = data['Close'].ewm(span=50, adjust=False).mean()
    data['EMA_200'] = data['Close'].ewm(span=200, adjust=False).mean()
    
    # Rate of change of EMA (slope indicator)
    data['EMA_50_prev'] = data['EMA_50'].shift(1)
    data['EMA_50_slope'] = (data['EMA_50'] - data['EMA_50_prev']) / data['EMA_50_prev']
    
    # ========================================================================
    # 2. VOLUME ANALYSIS (confirmation of trends)
    # ========================================================================
    data['Volume_MA'] = data['Volume'].rolling(window=20).mean()
    data['Volume_Ratio'] = data['Volume'] / data['Volume_MA']
    
    # ========================================================================
    # 3. COMPOSITE TREND SIGNAL (0-10 scale)
    # ========================================================================
    # Initialize composite signal
    data['Composite_Signal'] = 5.0  # Neutral baseline
    
    # PRIMARY: Price vs EMA_50
    data['Price_vs_EMA50'] = 0
    data.loc[data['Close'] > data['EMA_50'], 'Price_vs_EMA50'] = 1  # Uptrend
    data.loc[data['Close'] < data['EMA_50'], 'Price_vs_EMA50'] = -1  # Downtrend
    
    # CONFIRMATION 1: EMA_50 vs EMA_200
    data['EMA_trend'] = 0
    data.loc[data['EMA_50'] > data['EMA_200'], 'EMA_trend'] = 1  # Uptrend
    data.loc[data['EMA_50'] < data['EMA_200'], 'EMA_trend'] = -1  # Downtrend
    
    # CONFIRMATION 2: EMA slope (0.05% = 50 bps is the threshold)
    data['EMA_slope_signal'] = 0
    data.loc[data['EMA_50_slope'] > 0.0005, 'EMA_slope_signal'] = 1  # Rising
    data.loc[data['EMA_50_slope'] < -0.0005, 'EMA_slope_signal'] = -1  # Falling
    
    # CONFIRMATION 3: VIX regime (fear gauge)
    data['VIX_signal'] = 0
    data.loc[data['VIX'] < 20, 'VIX_signal'] = 1  # Low VIX = calm, bullish bias
    data.loc[data['VIX'] > 25, 'VIX_signal'] = -1  # High VIX = fearful, bearish bias
    
    # CONFIRMATION 4: Volume confirmation
    data['Volume_signal'] = 0
    data.loc[data['Volume_Ratio'] > 1.2, 'Volume_signal'] = 1  # High volume expansion
    data.loc[data['Volume_Ratio'] < 0.8, 'Volume_signal'] = -1  # Low volume contraction
    
    # COMPOSITE: Combine all signals (weighted)
    # Price vs EMA: 40% weight (most important)
    # EMA trend: 30% weight
    # EMA slope: 15% weight
    # VIX: 10% weight
    # Volume: 5% weight
    data['Composite_Signal'] = (
        5.0 +  # Neutral baseline
        data['Price_vs_EMA50'] * 2.0 +  # 40%
        data['EMA_trend'] * 1.5 +       # 30%
        data['EMA_slope_signal'] * 0.75 +  # 15%
        data['VIX_signal'] * 0.5 +      # 10%
        data['Volume_signal'] * 0.25    # 5%
    )
    
    # ========================================================================
    # 4. BINARY SIGNALS (for classification)
    # ========================================================================
    # Uptrend signal: Composite > 6 (>neutral by at least 1 unit)
    # Downtrend signal: Composite < 4 (<neutral by at least 1 unit)
    data['Signal_Binary'] = 0  # Neutral
    data.loc[data['Composite_Signal'] > 6, 'Signal_Binary'] = 1  # Uptrend
    data.loc[data['Composite_Signal'] < 4, 'Signal_Binary'] = -1  # Downtrend
    
    # ========================================================================
    # 5. ACTUAL NEXT-DAY RETURN (for accuracy testing)
    # ========================================================================
    data['Next_Return'] = data['Close'].pct_change().shift(-1)
    data['Actual_Direction'] = 0
    data.loc[data['Next_Return'] > 0, 'Actual_Direction'] = 1  # Actually went up
    data.loc[data['Next_Return'] < 0, 'Actual_Direction'] = -1  # Actually went down
    
    print(f"Successfully computed {len(data)} trading days of indicators.")
    return data


# ==============================================================================
# SECTION 2: SIGNAL INTERPRETATION GUIDE
# ==============================================================================
"""
COMPOSITE_SIGNAL Interpretation (0-10 scale):
- 0-3: Strong Downtrend (high confidence bearish)
- 3-4: Weak Downtrend (low confidence bearish)
- 4-6: Neutral/Uncertain (no clear direction)
- 6-7: Weak Uptrend (low confidence bullish)
- 7-10: Strong Uptrend (high confidence bullish)

Example Scenarios:
------------------
Scenario 1: Strong Uptrend
  Close > EMA_50 (+2.0)
  EMA_50 > EMA_200 (+1.5)
  EMA_50 rising (+0.75)
  VIX < 20 (+0.5)
  Volume expanding (+0.25)
  -> Composite = 5 + 2 + 1.5 + 0.75 + 0.5 + 0.25 = 10.0 (Very Bullish)

Scenario 2: Weak Downtrend
  Close < EMA_50 (-2.0)
  EMA_50 < EMA_200 (-1.5)
  EMA_50 still rising (+0.75)  <- Divergence!
  VIX > 25 (-0.5)
  Volume low (-0.25)
  -> Composite = 5 - 2 - 1.5 + 0.75 - 0.5 - 0.25 = 1.0 (Weak Bearish)

Scenario 3: Bullish Divergence
  Close < EMA_50 (-2.0)
  EMA_50 < EMA_200 (-1.5)
  EMA_50 rising strongly (+0.75)  <- Key signal of reversal
  VIX dropping (-0.5)
  Volume expanding (+0.25)
  -> Composite = 5 - 2 - 1.5 + 0.75 - 0.5 + 0.25 = 2.0 (Weak Bearish, but watch for reversal)
"""


# ==============================================================================
# SECTION 3: BACKTEST & ACCURACY METRICS
# ==============================================================================

def backtest_trend_signal(data, signal_column='Signal_Binary', actual_column='Actual_Direction'):
    """
    Backtest the trend prediction signal and compute accuracy metrics.
    
    Parameters:
    -----------
    data : pd.DataFrame
        Output from calculate_trend_indicators()
    signal_column : str
        Column containing predicted signals (-1, 0, 1)
    actual_column : str
        Column containing actual next-day direction
    
    Returns:
    --------
    dict with accuracy metrics
    """
    # Remove rows with NaN (early days before indicators stabilize)
    valid_data = data.dropna(subset=[signal_column, actual_column])
    
    if len(valid_data) == 0:
        print("No valid data for backtesting.")
        return {}
    
    y_pred = valid_data[signal_column].values
    y_true = valid_data[actual_column].values
    
    # ========================================================================
    # METRIC 1: DIRECTIONAL ACCURACY (for signals != 0 only)
    # ========================================================================
    directional_mask = y_pred != 0
    if directional_mask.sum() > 0:
        y_pred_dir = y_pred[directional_mask]
        y_true_dir = y_true[directional_mask]
        
        # Correct predictions: sign matches (both positive or both negative)
        correct_signals = (np.sign(y_pred_dir) == np.sign(y_true_dir)).sum()
        directional_accuracy = correct_signals / len(y_pred_dir)
    else:
        directional_accuracy = 0.0
    
    # ========================================================================
    # METRIC 2: UPTREND PREDICTION ACCURACY
    # ========================================================================
    uptrend_signals = (y_pred == 1)
    if uptrend_signals.sum() > 0:
        uptrend_correct = ((y_pred == 1) & (y_true == 1)).sum()
        uptrend_accuracy = uptrend_correct / uptrend_signals.sum()
        uptrend_recall = uptrend_correct / (y_true == 1).sum() if (y_true == 1).sum() > 0 else 0
    else:
        uptrend_accuracy = 0.0
        uptrend_recall = 0.0
    
    # ========================================================================
    # METRIC 3: DOWNTREND PREDICTION ACCURACY
    # ========================================================================
    downtrend_signals = (y_pred == -1)
    if downtrend_signals.sum() > 0:
        downtrend_correct = ((y_pred == -1) & (y_true == -1)).sum()
        downtrend_accuracy = downtrend_correct / downtrend_signals.sum()
        downtrend_recall = downtrend_correct / (y_true == -1).sum() if (y_true == -1).sum() > 0 else 0
    else:
        downtrend_accuracy = 0.0
        downtrend_recall = 0.0
    
    # ========================================================================
    # METRIC 4: OVERALL STATISTICS
    # ========================================================================
    total_signals = len(y_pred)
    uptrend_count = (y_pred == 1).sum()
    downtrend_count = (y_pred == -1).sum()
    neutral_count = (y_pred == 0).sum()
    
    actual_uptrends = (y_true == 1).sum()
    actual_downtrends = (y_true == -1).sum()
    
    metrics = {
        'total_trading_days': total_signals,
        'signal_uptrend_days': uptrend_count,
        'signal_downtrend_days': downtrend_count,
        'signal_neutral_days': neutral_count,
        'actual_uptrend_days': actual_uptrends,
        'actual_downtrend_days': actual_downtrends,
        'directional_accuracy': directional_accuracy,
        'uptrend_precision': uptrend_accuracy,
        'uptrend_recall': uptrend_recall,
        'downtrend_precision': downtrend_accuracy,
        'downtrend_recall': downtrend_recall,
    }
    
    return metrics, valid_data


def print_backtest_results(metrics, valid_data=None):
    """Print formatted backtest results."""
    if not metrics:
        print("No metrics to display.")
        return
    
    print("\n" + "="*70)
    print("BACKTEST RESULTS: S&P 500 TREND PREDICTION")
    print("="*70)
    
    print(f"\n[SIGNAL DISTRIBUTION]")
    print(f"  Total Trading Days: {metrics['total_trading_days']}")
    print(f"  Uptrend Signals (Buy): {metrics['signal_uptrend_days']} ({100*metrics['signal_uptrend_days']/metrics['total_trading_days']:.1f}%)")
    print(f"  Downtrend Signals (Sell): {metrics['signal_downtrend_days']} ({100*metrics['signal_downtrend_days']/metrics['total_trading_days']:.1f}%)")
    print(f"  Neutral Signals: {metrics['signal_neutral_days']} ({100*metrics['signal_neutral_days']/metrics['total_trading_days']:.1f}%)")
    
    print(f"\n[ACTUAL MARKET BEHAVIOR (Next Day)]")
    print(f"  Days with Uptrend (↑): {metrics['actual_uptrend_days']} ({100*metrics['actual_uptrend_days']/metrics['total_trading_days']:.1f}%)")
    print(f"  Days with Downtrend (↓): {metrics['actual_downtrend_days']} ({100*metrics['actual_downtrend_days']/metrics['total_trading_days']:.1f}%)")
    
    print(f"\n[DIRECTIONAL ACCURACY]")
    print(f"  When Signal Issued: {100*metrics['directional_accuracy']:.2f}% correct direction")
    
    print(f"\n[UPTREND (BUY) SIGNAL PERFORMANCE]")
    print(f"  Precision (correct uptrend calls / total uptrend signals): {100*metrics['uptrend_precision']:.2f}%")
    print(f"  Recall (uptrends caught / actual uptrends): {100*metrics['uptrend_recall']:.2f}%")
    
    print(f"\n[DOWNTREND (SELL) SIGNAL PERFORMANCE]")
    print(f"  Precision (correct downtrend calls / total downtrend signals): {100*metrics['downtrend_precision']:.2f}%")
    print(f"  Recall (downtrends caught / actual downtrends): {100*metrics['downtrend_recall']:.2f}%")
    
    print("\n" + "="*70)
    print("INTERPRETATION GUIDE:")
    print("="*70)
    print("  Precision: 'If signal says UP, how often is UP correct?'")
    print("  Recall: 'Of all actual UPs, how many did we catch?'")
    print("  High Precision = Few False Alarms")
    print("  High Recall = Don't miss trends")
    print("  Ideal: Precision ~70%+, Recall ~60%+")
    print("="*70 + "\n")


def plot_trend_signals(data, start_date=None, end_date=None):
    """
    Plot price, indicators, composite signal, and actual direction.
    """
    plot_data = data.copy()
    if start_date and end_date:
        plot_data = plot_data.loc[start_date:end_date]
    
    fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
    
    # Subplot 1: Price and EMAs
    ax0 = axes[0]
    ax0.plot(plot_data.index, plot_data['Close'], label='Close', color='blue', linewidth=1.5)
    ax0.plot(plot_data.index, plot_data['EMA_50'], label='EMA 50', color='orange', linewidth=1)
    ax0.plot(plot_data.index, plot_data['EMA_200'], label='EMA 200', color='red', linewidth=1)
    ax0.set_ylabel('Price ($)')
    ax0.legend(loc='upper left')
    ax0.grid(True, alpha=0.3)
    ax0.set_title('S&P 500 Price and Moving Averages')
    
    # Subplot 2: VIX and Volume Ratio
    ax1 = axes[1]
    ax1.plot(plot_data.index, plot_data['VIX'], label='VIX', color='purple', linewidth=1.5)
    ax1_twin = ax1.twinx()
    ax1_twin.plot(plot_data.index, plot_data['Volume_Ratio'], label='Volume Ratio', color='green', linewidth=1, alpha=0.6)
    ax1.axhline(y=20, color='purple', linestyle='--', alpha=0.5, label='VIX 20')
    ax1.axhline(y=25, color='red', linestyle='--', alpha=0.5, label='VIX 25')
    ax1.set_ylabel('VIX')
    ax1_twin.set_ylabel('Volume Ratio')
    ax1.legend(loc='upper left')
    ax1_twin.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_title('Volatility (VIX) and Volume Confirmation')
    
    # Subplot 3: Composite Signal
    ax2 = axes[2]
    colors = ['red' if x < 4 else 'yellow' if x < 6 else 'green' for x in plot_data['Composite_Signal']]
    ax2.bar(plot_data.index, plot_data['Composite_Signal'], color=colors, alpha=0.6, width=1)
    ax2.axhline(y=5, color='black', linestyle='-', alpha=0.3, label='Neutral')
    ax2.axhline(y=6, color='green', linestyle='--', alpha=0.3)
    ax2.axhline(y=4, color='red', linestyle='--', alpha=0.3)
    ax2.set_ylabel('Signal Strength (0-10)')
    ax2.set_ylim([0, 10])
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    ax2.set_title('Composite Trend Signal (Red=Bearish, Yellow=Neutral, Green=Bullish)')
    
    # Subplot 4: Next Day Actual Direction vs Prediction
    ax3 = axes[3]
    ax3.plot(plot_data.index, plot_data['Next_Return'] * 100, label='Actual Next Return (%)', color='black', linewidth=1, alpha=0.7)
    
    # Color predictions
    uptrend_mask = plot_data['Signal_Binary'] == 1
    downtrend_mask = plot_data['Signal_Binary'] == -1
    
    ax3.scatter(plot_data.index[uptrend_mask], plot_data.loc[uptrend_mask, 'Next_Return'] * 100, 
               color='green', marker='^', s=50, alpha=0.6, label='Predicted Uptrend')
    ax3.scatter(plot_data.index[downtrend_mask], plot_data.loc[downtrend_mask, 'Next_Return'] * 100, 
               color='red', marker='v', s=50, alpha=0.6, label='Predicted Downtrend')
    
    ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax3.set_ylabel('Next Day Return (%)')
    ax3.set_xlabel('Date')
    ax3.legend(loc='upper left')
    ax3.grid(True, alpha=0.3)
    ax3.set_title('Prediction Accuracy: Signal vs Actual Next-Day Return')
    
    plt.tight_layout()
    plt.savefig('sp500_trend_prediction.png', dpi=150, bbox_inches='tight')
    print("Plot saved as 'sp500_trend_prediction.png'")
    plt.show()


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == '__main__':
    # Download and compute indicators
    data = calculate_trend_indicators(ticker='SPY', start_date='2015-01-01', end_date='2025-12-06')
    
    # Backtest
    metrics, valid_data = backtest_trend_signal(data)
    
    # Print results
    print_backtest_results(metrics, valid_data)
    
    # Plot
    plot_trend_signals(data, start_date='2023-01-01')
    
    # Save results to CSV
    output_file = 'sp500_trend_signals.csv'
    data.to_csv(output_file)
    print(f"Full results saved to '{output_file}'")
    
    print("\n✓ Analysis complete!")
    print(f"\nNext Steps:")
    print(f"  1. Analyze precision/recall trade-offs")
    print(f"  2. Optimize signal thresholds (currently Composite > 6 for uptrend)")
    print(f"  3. Test different lookback periods for next-day returns (1-day, 2-day, 5-day)")
    print(f"  4. Add risk management (position sizing based on signal strength)")
    print(f"  5. Evaluate with walk-forward backtesting (2015-2022 train, 2023-2025 test)")
