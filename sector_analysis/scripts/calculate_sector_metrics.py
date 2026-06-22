"""
Calculate Sector Metrics

Computes relative strength, momentum, and composite scores for sector rotation.
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
    print(f"\n{'='*60}")
    print("CALCULATING RELATIVE STRENGTH")
    print(f"{'='*60}")

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

    print(f"[OK] Relative strength calculated for {len(sectors_df['ticker'].unique())} sectors")

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
    print(f"\n{'='*60}")
    print("CALCULATING MOMENTUM")
    print(f"{'='*60}")

    # Calculate 3-month and 6-month returns if not already done
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

    print(f"[OK] Momentum calculated")

    return sector_df


def rank_sectors(sector_df):
    """
    Rank sectors by various metrics

    Parameters
    ----------
    sector_df : pd.DataFrame
        Sector data with all metrics

    Returns
    -------
    pd.DataFrame
        Latest rankings for all sectors
    """
    print(f"\n{'='*60}")
    print("RANKING SECTORS")
    print(f"{'='*60}")

    # Get most recent date
    latest_date = sector_df['date'].max()
    latest_data = sector_df[sector_df['date'] == latest_date].copy()

    # Calculate composite score (simplified for MVP)
    # Score = 40% RS + 40% Momentum + 20% Recent strength
    latest_data['rs_rank'] = latest_data['rs_20d'].rank(pct=True) * 100
    latest_data['momentum_rank'] = latest_data['momentum_score'].rank(pct=True) * 100

    latest_data['composite_score'] = (
        0.25 * latest_data['rs_rank'] +
        0.25 * latest_data['momentum_rank'] +
        0.25 * latest_data['rs_60d'].rank(pct=True) * 100 +
        0.25 * latest_data['return_20d'].rank(pct=True) * 100
    )

    # Overall rank
    latest_data['rank'] = latest_data['composite_score'].rank(ascending=False, method='first').astype(int)

    # Sort by rank
    latest_data = latest_data.sort_values('rank')

    # Categorize signal
    latest_data['signal'] = latest_data.apply(categorize_signal, axis=1)

    print(f"[OK] Ranked {len(latest_data)} sectors")

    return latest_data


def categorize_signal(row):
    """Categorize sector signal based on metrics"""
    rs_20 = row.get('rs_20d', 0) * 100  # Convert to percentage
    rs_60 = row.get('rs_60d', 0) * 100
    momentum = row.get('momentum_score', 0) * 100

    # Strong outperformance
    if rs_20 > 2 and rs_60 > 3 and momentum > 10:
        return '🚀 STRONG BUY'
    elif rs_20 > 1 and rs_60 > 1:
        return '✅ BUY'
    elif rs_20 > 0 and rs_60 < 0:
        return '👀 WATCH (Early Rotation)'
    elif rs_20 < 0 and rs_60 > 0:
        return '⚠️ WEAKENING'
    else:
        return '❌ AVOID'


def identify_rotation_quadrants(sector_df):
    """
    Identify which quadrant each sector is in

    Quadrants:
    - Leading: Strong RS + Accelerating
    - Weakening: Strong RS + Decelerating
    - Lagging: Weak RS + Decelerating
    - Improving: Weak RS + Accelerating
    """
    latest_date = sector_df['date'].max()
    latest_data = sector_df[sector_df['date'] == latest_date].copy()

    # Calculate RS acceleration (change in RS over time)
    # Approximation: compare 20-day RS to 60-day RS
    latest_data['rs_acceleration'] = latest_data['rs_20d'] - latest_data['rs_60d']

    quadrants = {
        'leading': [],
        'weakening': [],
        'lagging': [],
        'improving': []
    }

    for _, row in latest_data.iterrows():
        ticker = row['ticker']
        rs = row['rs_60d']  # Use 60-day as baseline
        acceleration = row['rs_acceleration']

        if rs > 0 and acceleration > 0:
            quadrants['leading'].append(ticker)
        elif rs > 0 and acceleration <= 0:
            quadrants['weakening'].append(ticker)
        elif rs <= 0 and acceleration <= 0:
            quadrants['lagging'].append(ticker)
        else:  # rs <= 0 and acceleration > 0
            quadrants['improving'].append(ticker)

    return quadrants


if __name__ == "__main__":
    # Test with sample data
    from fetch_sector_data import fetch_sector_etfs

    print("Fetching sector data...")
    df = fetch_sector_etfs(lookback_days=365)

    print("\nCalculating metrics...")
    df = calculate_relative_strength(df)
    df = calculate_momentum(df)

    print("\nRanking sectors...")
    rankings = rank_sectors(df)

    print("\n" + "="*60)
    print("SECTOR RANKINGS")
    print("="*60)
    print(rankings[['rank', 'ticker', 'sector_name', 'composite_score', 'rs_20d', 'momentum_score', 'signal']])
