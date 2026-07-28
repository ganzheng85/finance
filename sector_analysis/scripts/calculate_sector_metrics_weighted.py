"""
Calculate Sector Metrics with Customizable Weights

This version allows you to adjust the weights of different metrics
to better capture momentum or other market conditions.
"""

import pandas as pd
import numpy as np


def calculate_relative_strength(sector_df):
    """
    Calculate relative strength vs SPY

    Parameters
    ----------
    sector_df : pd.DataFrame
        Combined dataframe with all sectors

    Returns
    -------
    pd.DataFrame
        Sector metrics with RS calculations
    """
    # Get SPY data as benchmark
    spy_df = sector_df[sector_df['ticker'] == 'SPY'][['date', 'adjusted_close']].copy()
    spy_df.columns = ['date', 'spy_close']

    # Get sector data (exclude SPY)
    sectors_df = sector_df[sector_df['ticker'] != 'SPY'].copy()

    # Merge with SPY data
    sectors_df = sectors_df.merge(spy_df, on='date', how='left')

    # Calculate RS = Sector / SPY
    sectors_df['rs_ratio'] = sectors_df['adjusted_close'] / sectors_df['spy_close']

    # Calculate returns over different periods
    for period in [20, 60, 90, 180]:
        sectors_df[f'return_{period}d'] = sectors_df.groupby('ticker')['adjusted_close'].pct_change(periods=period)
        sectors_df[f'spy_return_{period}d'] = sectors_df.groupby('ticker')['spy_close'].pct_change(periods=period)
        sectors_df[f'rs_{period}d'] = sectors_df[f'return_{period}d'] - sectors_df[f'spy_return_{period}d']

    return sectors_df


def calculate_momentum(sector_df):
    """
    Calculate momentum scores

    Parameters
    ----------
    sector_df : pd.DataFrame
        DataFrame with sector data

    Returns
    -------
    pd.DataFrame
        Sector data with momentum scores
    """
    # Calculate returns if not already done
    if 'return_60d' not in sector_df.columns:
        sector_df['return_60d'] = sector_df.groupby('ticker')['adjusted_close'].pct_change(periods=60)
    if 'return_90d' not in sector_df.columns:
        sector_df['return_90d'] = sector_df.groupby('ticker')['adjusted_close'].pct_change(periods=90)
    if 'return_180d' not in sector_df.columns:
        sector_df['return_180d'] = sector_df.groupby('ticker')['adjusted_close'].pct_change(periods=180)

    # Composite momentum = 3M + 6M returns
    sector_df['momentum_score'] = sector_df['return_90d'] + sector_df['return_180d']

    # 12-1 momentum (skip last month)
    sector_df['return_240d'] = sector_df.groupby('ticker')['adjusted_close'].pct_change(periods=240)
    sector_df['return_20d'] = sector_df.groupby('ticker')['adjusted_close'].pct_change(periods=20)
    sector_df['momentum_12_1'] = sector_df['return_240d'] - sector_df['return_20d']

    return sector_df


def rank_sectors_weighted(sector_df, weights=None, verbose=True):
    """
    Rank sectors with customizable metric weights

    Parameters
    ----------
    sector_df : pd.DataFrame
        Sector data with all metrics
    weights : dict, optional
        Custom weights for each metric. Default:
        {
            'rs_20d': 0.25,      # Short-term relative strength
            'rs_60d': 0.25,      # Medium-term relative strength
            'momentum': 0.25,    # Momentum score (3M + 6M)
            'return_20d': 0.25   # Recent return
        }
    verbose : bool
        Whether to print progress

    Returns
    -------
    pd.DataFrame
        Latest rankings for all sectors
    """
    if verbose:
        print(f"\n{'='*60}")
        print("RANKING SECTORS WITH CUSTOM WEIGHTS")
        print(f"{'='*60}")

    # Default equal weights
    if weights is None:
        weights = {
            'rs_20d': 0.25,
            'rs_60d': 0.25,
            'momentum': 0.25,
            'return_20d': 0.25
        }

    # Validate weights sum to 1.0
    total_weight = sum(weights.values())
    if not np.isclose(total_weight, 1.0, atol=0.001):
        raise ValueError(f"Weights must sum to 1.0, got {total_weight}")

    if verbose:
        print(f"\nWeights:")
        for metric, weight in weights.items():
            print(f"  {metric:<15} {weight*100:>5.1f}%")

    # Get most recent data for each ticker
    latest_data = sector_df.loc[sector_df.groupby('ticker')['date'].idxmax()].copy()

    # Calculate percentile ranks for each metric (0-100 scale)
    latest_data['rs_20d_rank'] = latest_data['rs_20d'].rank(pct=True) * 100
    latest_data['rs_60d_rank'] = latest_data['rs_60d'].rank(pct=True) * 100
    latest_data['momentum_rank'] = latest_data['momentum_score'].rank(pct=True) * 100
    latest_data['return_20d_rank'] = latest_data['return_20d'].rank(pct=True) * 100

    # Calculate weighted composite score
    latest_data['composite_score'] = (
        weights['rs_20d'] * latest_data['rs_20d_rank'] +
        weights['rs_60d'] * latest_data['rs_60d_rank'] +
        weights['momentum'] * latest_data['momentum_rank'] +
        weights['return_20d'] * latest_data['return_20d_rank']
    )

    # Filter out sectors with insufficient data (NaN composite scores)
    valid_data = latest_data[latest_data['composite_score'].notna()].copy()

    if len(valid_data) < len(latest_data):
        dropped = len(latest_data) - len(valid_data)
        dropped_tickers = latest_data[latest_data['composite_score'].isna()]['ticker'].tolist()
        if verbose:
            print(f"[WARNING] Dropped {dropped} sectors with insufficient data: {', '.join(dropped_tickers)}")

    # Overall rank
    valid_data['rank'] = valid_data['composite_score'].rank(ascending=False, method='first').astype(int)

    # Sort by rank
    valid_data = valid_data.sort_values('rank')

    # Categorize signal
    valid_data['signal'] = valid_data.apply(categorize_signal, axis=1)

    if verbose:
        print(f"[OK] Ranked {len(valid_data)} sectors")

    return valid_data


def categorize_signal(row):
    """Categorize sector strength based on composite score"""
    score = row.get('composite_score', 0)
    rs_20 = row.get('rs_20d', 0) * 100
    rs_60 = row.get('rs_60d', 0) * 100

    if score >= 75:
        if rs_20 > 1 and rs_60 > 1:
            return 'Very Strong'
        elif rs_20 > 0 and rs_60 < 0:
            return 'Strong (Early Rotation)'
        else:
            return 'Strong'
    elif score >= 60:
        if rs_20 > 0 and rs_60 < 0:
            return 'Medium (Early Rotation)'
        elif rs_20 < 0 and rs_60 > 0:
            return 'Medium (Weakening)'
        else:
            return 'Medium'
    else:
        return 'Weak'
