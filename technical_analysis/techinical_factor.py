from typing import List, Optional

import numpy as np
import pandas as pd


class TechnicalFactors:
    """
    A class for computing technical factors on a long-format stock DataFrame.

    Expected input format:
        - Required columns: ['symbol', 'date', 'adjusted_close', 'volume']
        - Additional columns: ['open', 'high', 'low'] (required for some indicators)
        - Long format with ~500 symbols
        - Date column should be datetime or convertible to datetime

    Usage:
        tf = TechnicalFactors(df)

        # Run individual factors
        df_with_momentum = tf.momentum(period=252, skip_days=21)
        df_with_rsi = tf.rsi(window=14)

        # Run all factors at once
        df_all_factors = tf.run_all()
    """

    def __init__(self, df: pd.DataFrame, price_col: str = "adjusted_close", volume_col: str = "volume"):
        """
        Initialize the TechnicalFactors calculator.

        Parameters
        ----------
        df : pd.DataFrame
            Long-format DataFrame with columns:
            - Required: ['symbol', 'date', 'adjusted_close', 'volume']
            - Optional but recommended: ['open', 'high', 'low']
              (high/low required for ADX and Stochastic indicators)
        price_col : str
            Name of the price column (default: 'adjusted_close')
        volume_col : str
            Name of the volume column (default: 'volume')
        """
        required_cols = ['symbol', 'date', price_col, volume_col]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        self.df = df.copy()
        self.price_col = price_col
        self.volume_col = volume_col

        # Ensure date is datetime
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df = self.df.sort_values(['symbol', 'date']).reset_index(drop=True)

    def volatility(self, window: int = 252) -> pd.DataFrame:
        """Annualized volatility."""
        self.df = calculate_volatility_standalone(self.df, window=window, price_col=self.price_col)
        return self.df

    def momentum(self, period: int = 252, skip_days: int = 21, vol_penalty: bool = True,
                 winsor: Optional[float] = None, zscore: bool = False) -> pd.DataFrame:
        """12-1 momentum factor with optional volatility adjustment."""
        self.df = calculate_momentum_factor(
            self.df, period=period, skip_days=skip_days, vol_penalty=vol_penalty,
            price_col=self.price_col, winsor=winsor, zscore=zscore
        )
        return self.df

    def distance_from_sma(self, window: int = 200) -> pd.DataFrame:
        """Distance from Simple Moving Average."""
        self.df = calculate_distance_from_sma(self.df, window=window)
        return self.df

    def sma_distance(self, short_window: int = 20, long_window: int = 50) -> pd.DataFrame:
        """Distance between two SMAs (e.g., 20-day vs 50-day)."""
        self.df = calculate_sma_distance(self.df, short_window=short_window, long_window=long_window)
        return self.df

    def relative_volume(self, window: int = 30, keep_baseline: bool = False,
                       use_ema: bool = False, by_weekday: bool = False,
                       winsor: Optional[float] = None, zscore: bool = False) -> pd.DataFrame:
        """Relative volume (RVOL) indicator."""
        self.df = calculate_relative_volume(
            self.df, window=window, keep_baseline=keep_baseline, use_ema=use_ema,
            by_weekday=by_weekday, winsor=winsor, zscore=zscore
        )
        return self.df

    def volume_price_trend(self) -> pd.DataFrame:
        """Volume Price Trend (VPT) indicator."""
        self.df = calculate_volume_price_trend(self.df)
        return self.df

    def rsi(self, window: int = 14) -> pd.DataFrame:
        """Wilder's RSI."""
        self.df = calculate_rsi_wilder(self.df, window=window, price_col=self.price_col)
        return self.df

    def bollinger_width(self, window: int = 20, mult: float = 2.0,
                       normalize: str = "sma", keep_components: bool = False) -> pd.DataFrame:
        """Bollinger Band Width."""
        self.df = calculate_bb_width(
            self.df, window=window, price_col=self.price_col, mult=mult,
            normalize=normalize, keep_components=keep_components
        )
        return self.df

    def bollinger_percent_b(self, window: int = 20, mult: float = 2.0) -> pd.DataFrame:
        """Bollinger %B indicator."""
        self.df = calculate_bollinger_percent_b(
            self.df, window=window, price_col=self.price_col, mult=mult
        )
        return self.df

    def bollinger_squeeze(self, window: int = 20, pct: float = 0.1) -> pd.DataFrame:
        """Flag Bollinger squeeze conditions."""
        # Requires bb_width to be computed first
        if 'bb_width' not in self.df.columns:
            self.bollinger_width(window=window)
        self.df = flag_bollinger_squeeze(self.df, window=window, pct=pct)
        return self.df

    def adx(self, window: int = 14) -> pd.DataFrame:
        """Average Directional Index (ADX) - requires 'high' and 'low' columns."""
        if 'high' not in self.df.columns or 'low' not in self.df.columns:
            raise ValueError("ADX requires 'high' and 'low' columns in the DataFrame")
        self.df = calculate_adx(self.df, window=window, price_col=self.price_col)
        return self.df

    def stochastic(self, k_window: int = 14, d_window: int = 3,
                  use_ema: bool = False, keep_components: bool = True) -> pd.DataFrame:
        """Stochastic Oscillator (%K and %D) - requires 'high' and 'low' columns."""
        if 'high' not in self.df.columns or 'low' not in self.df.columns:
            raise ValueError("Stochastic requires 'high' and 'low' columns in the DataFrame")
        self.df = calculate_stochastic(
            self.df, k_window=k_window, d_window=d_window,
            price_col=self.price_col, use_ema=use_ema, keep_components=keep_components
        )
        return self.df

    def macd(self, fast: int = 12, slow: int = 26, signal: int = 9,
             keep_lines: bool = True) -> pd.DataFrame:
        """MACD histogram and signal lines."""
        self.df = calculate_macd(
            self.df, fast=fast, slow=slow, signal=signal,
            price_col=self.price_col, keep_lines=keep_lines
        )
        return self.df

    def run_all(self,
                include_high_low_indicators: bool = True,
                custom_params: Optional[dict] = None) -> pd.DataFrame:
        """
        Calculate all technical factors at once.

        Parameters
        ----------
        include_high_low_indicators : bool
            If True and 'high'/'low' columns exist, compute ADX and Stochastic
        custom_params : dict, optional
            Override default parameters for specific indicators.
            Example: {'momentum': {'period': 126}, 'rsi': {'window': 21}}

        Returns
        -------
        pd.DataFrame
            DataFrame with all computed technical factors
        """
        params = custom_params or {}

        # Price-based indicators
        print("Computing volatility...")
        self.volatility(**params.get('volatility', {}))

        print("Computing momentum...")
        self.momentum(**params.get('momentum', {}))

        print("Computing distance from SMA...")
        self.distance_from_sma(**params.get('distance_from_sma', {}))

        print("Computing SMA distance (20 vs 50)...")
        self.sma_distance(**params.get('sma_distance', {}))

        print("Computing RSI...")
        self.rsi(**params.get('rsi', {}))

        print("Computing Bollinger Bands...")
        self.bollinger_width(**params.get('bollinger_width', {}))
        self.bollinger_percent_b(**params.get('bollinger_percent_b', {}))
        self.bollinger_squeeze(**params.get('bollinger_squeeze', {}))

        print("Computing MACD...")
        self.macd(**params.get('macd', {}))

        # Volume-based indicators
        print("Computing relative volume...")
        self.relative_volume(**params.get('relative_volume', {}))

        print("Computing VPT...")
        self.volume_price_trend()

        # High/Low indicators (optional)
        if include_high_low_indicators and 'high' in self.df.columns and 'low' in self.df.columns:
            print("Computing ADX...")
            self.adx(**params.get('adx', {}))

            print("Computing Stochastic...")
            self.stochastic(**params.get('stochastic', {}))

        print("All factors computed successfully!")
        return self.df

    def get_factor_columns(self) -> List[str]:
        """Return list of all computed factor columns (excludes original data columns)."""
        original_cols = {
            'symbol', 'date', self.price_col, self.volume_col,
            'open', 'high', 'low', 'close', 'adjusted_close', 'volume'
        }
        factor_cols = [col for col in self.df.columns if col not in original_cols]
        return factor_cols

    def reset(self, df: Optional[pd.DataFrame] = None):
        """Reset to original or new DataFrame."""
        if df is not None:
            self.__init__(df, self.price_col, self.volume_col)
        else:
            # This would require storing original df, not implemented
            raise NotImplementedError("Reset without providing df is not supported. Pass the original df.")


# ==================== Standalone Functions (for backward compatibility) ====================
def calculate_volatility_standalone(df: pd.DataFrame, window: int = 252, price_col: str = "adjusted_close") -> pd.DataFrame:
    """
    Annualized volatility per row, computed from daily returns over 'window' for each symbol.
    Returns DataFrame with added 'volatility' column.
    """
    # Sort and compute daily returns per symbol
    df = df.copy()
    df = df.sort_values(["symbol", "date"])
    daily_ret = df.groupby("symbol")[price_col].pct_change()

    # Rolling std of daily returns per symbol
    vol_daily = (
        daily_ret.groupby(df["symbol"])
        .rolling(window=window, min_periods=window)
        .std()
        .reset_index(level=0, drop=True)
    )

    # Annualize volatility
    vol_annual = vol_daily * np.sqrt(252)
    df['volatility'] = vol_annual
    return df

def calculate_momentum_factor(df: pd.DataFrame,
                              period: int = 252,
                              skip_days: int = 21,
                              vol_penalty: bool = True,
                              price_col: str = "adjusted_close",
                              winsor: float = None,
                              zscore: bool = False) -> pd.DataFrame:
    """
    Calculates a cross-sectional momentum factor (12-1 style by default) and optional volatility adjustment.

    Args:
        df: long DataFrame with columns ['symbol', 'date', price_col]
        period: lookback window in trading days (e.g., 252 ~ 12 months)
        skip_days: exclude most recent days (e.g., 21 ~ 1 month)
        vol_penalty: if True, divide momentum by annualized volatility
        price_col: price column name
        winsor: if set (e.g., 0.01), winsorize momentum_score at each date
        zscore: if True, z-score momentum_score within date for comparability

    Returns:
        df with columns: ['momentum_raw', 'volatility' (if vol_penalty), 'momentum_score']
    """
    df = df.sort_values(["symbol", "date"]).copy()

    # Geometric total return from t - period to t - skip_days
    # (12-1 momentum when period=252, skip_days=21)
    px_t_minus_skip = df.groupby("symbol")[price_col].shift(skip_days)
    px_t_minus_period = df.groupby("symbol")[price_col].shift(period)

    momentum_raw = (px_t_minus_skip / px_t_minus_period) - 1
    df["momentum_raw"] = momentum_raw

    if vol_penalty:
        df["volatility"] = calculate_volatility_standalone(df, window=period, price_col=price_col)['volatility']

        # Safe division: avoid infs
        denom = df["volatility"].replace(0, np.nan)
        df["momentum_score"] = df["momentum_raw"] / denom
    else:
        df["momentum_score"] = df["momentum_raw"]

    # Optional winsorization per date to reduce extreme outliers
    if winsor is not None and 0 < winsor < 0.5:
        def _winsorize(s: pd.Series, p: float):
            lower = s.quantile(p)
            upper = s.quantile(1 - p)
            return s.clip(lower, upper)

        df["momentum_score"] = (
            df.groupby("date")["momentum_score"]
              .transform(lambda s: _winsorize(s, winsor))
        )

    # Optional z-score per date for cross-sectional comparability
    if zscore:
        def _z(s: pd.Series):
            m = s.mean()
            sd = s.std(ddof=0)
            return (s - m) / sd if sd and not np.isnan(sd) else s*0
        df["momentum_score"] = (
            df.groupby("date")["momentum_score"]
              .transform(_z)
        )

    return df

def calculate_distance_from_sma(df, window=200):
    """
    Calculates how far the current price is from the Simple Moving Average (SMA).
    A positive value means the price is above the SMA.
    """
    df = df.sort_values(['symbol', 'date'])
    sma_col_name = f'sma_{window}'

    # Calculate SMA
    df[sma_col_name] = df.groupby('symbol')['adjusted_close'].transform(
        lambda x: x.rolling(window=window).mean()
    )

    # Calculate the percentage difference
    df[f'dist_sma_{window}'] = (df['adjusted_close'] / df[sma_col_name]) - 1

    # Clean up the intermediate SMA column if desired
    df = df.drop(columns=[sma_col_name])

    return df

def calculate_sma_distance(df: pd.DataFrame,
                          short_window: int = 20,
                          long_window: int = 50,
                          price_col: str = "adjusted_close") -> pd.DataFrame:
    """
    Calculate the distance between two SMAs (e.g., 20-day and 50-day).

    This indicator helps identify:
    - Trend strength: larger distance = stronger trend
    - Golden/Death cross setups: when distance approaches zero
    - Momentum: expanding distance = accelerating trend

    Parameters
    ----------
    df : DataFrame with ['symbol', 'date', price_col]
    short_window : int, shorter SMA period (default 20)
    long_window : int, longer SMA period (default 50)
    price_col : str, price column name

    Returns
    -------
    DataFrame with added column: f'sma_dist_{short_window}_{long_window}'
    Positive value means short SMA is above long SMA (bullish)
    Negative value means short SMA is below long SMA (bearish)
    """
    if short_window >= long_window:
        raise ValueError(f"short_window ({short_window}) must be less than long_window ({long_window})")

    df = df.sort_values(['symbol', 'date']).copy()

    # Calculate both SMAs
    sma_short = df.groupby('symbol')[price_col].transform(
        lambda x: x.rolling(window=short_window, min_periods=short_window).mean()
    )
    sma_long = df.groupby('symbol')[price_col].transform(
        lambda x: x.rolling(window=long_window, min_periods=long_window).mean()
    )

    # Calculate percentage difference
    denom = sma_long.replace(0, np.nan)
    sma_distance = (sma_short / denom) - 1
    sma_distance = sma_distance.replace([np.inf, -np.inf], np.nan)

    df[f'sma_dist_{short_window}_{long_window}'] = sma_distance

    return df

def calculate_relative_volume(
    df: pd.DataFrame,
    window: int = 30,
    keep_baseline: bool = False,
    use_ema: bool = False,
    by_weekday: bool = False,
    winsor: float = None,  # e.g., 0.01 = winsorize 1% tails per date
    zscore: bool = False
) -> pd.DataFrame:
    """
    Relative Volume (RVOL): today's volume / baseline average volume.

    Parameters
    ----------
    df : long DataFrame with columns ['symbol', 'date', 'volume']
          - 'date' should be datetime64[ns]
    window : int, rolling lookback length (e.g., 30 trading days)
    keep_baseline : bool, if True keep the baseline column
    use_ema : bool, if True use exponential average instead of simple mean
    by_weekday : bool, if True baseline is rolling mean of same weekday only
    winsor : float in (0, 0.5), per-date winsorization for RVOL (optional)
    zscore : bool, if True z-score RVOL per date (optional for ranking)

    Returns
    -------
    DataFrame with 'relative_volume' and optionally baseline column.
    """
    df = df.sort_values(['symbol', 'date']).copy()
    vol = df['volume'].astype(float)
    base_col = f"avg_vol_{window}"
    rvol_col = "relative_volume"

    if by_weekday:
        # Compute baseline as rolling average of same weekday volume
        # Create helper key: (symbol, weekday)
        weekday = df['date'].dt.weekday  # Monday=0 ... Sunday=6; trading ~ 0..4
        df['_wd'] = weekday

        # Group by symbol & weekday
        g = df.groupby(['symbol', '_wd'])['volume']

        if use_ema:
            baseline = (
                g.transform(lambda x: x.ewm(span=window, adjust=False).mean())
            )
        else:
            baseline = (
                g.transform(lambda x: x.rolling(window=window, min_periods=window).mean())
            )

        df.drop(columns=['_wd'], inplace=True)
    else:
        # Standard rolling or EMA per symbol
        g = df.groupby('symbol')['volume']
        if use_ema:
            baseline = g.transform(lambda x: x.ewm(span=window, adjust=False).mean())
        else:
            baseline = g.transform(lambda x: x.rolling(window=window, min_periods=window).mean())

    # Safe division
    denom = baseline.replace(0, np.nan)
    rvol = vol / denom
    rvol = rvol.replace([np.inf, -np.inf], np.nan)

    df[rvol_col] = rvol
    if keep_baseline:
        df[base_col] = baseline

    # Optional winsorization per date
    if winsor is not None and 0 < winsor < 0.5:
        def _winsorize(s: pd.Series, p: float):
            lower = s.quantile(p)
            upper = s.quantile(1 - p)
            return s.clip(lower, upper)
        df[rvol_col] = df.groupby('date')[rvol_col].transform(lambda s: _winsorize(s, winsor))

    # Optional z-score per date
    if zscore:
        def _z(s: pd.Series):
            m, sd = s.mean(), s.std(ddof=0)
            return (s - m) / sd if (sd and not np.isnan(sd)) else s*0
        df[f"{rvol_col}_z"] = df.groupby('date')[rvol_col].transform(_z)

    return df

def calculate_volume_price_trend(df):
    """
    Calculates the Volume Price Trend (VPT) indicator.
    A rising VPT indicates stronger volume on up days, confirming an uptrend.
    """
    df = df.sort_values(['symbol', 'date']).copy()

    # Calculate percentage price change per symbol
    price_pct_change = df.groupby('symbol')['adjusted_close'].pct_change()

    # Calculate the change in VPT for each day
    vpt_change = df['volume'] * price_pct_change

    # Cumulative sum per symbol
    df['vpt'] = vpt_change.groupby(df['symbol']).cumsum()

    return df

def calculate_rsi_wilder(df: pd.DataFrame, window: int = 14, price_col: str = "adjusted_close") -> pd.DataFrame:
    """
    Calculate Wilder's RSI per symbol on a long-format DataFrame with columns:
    ['symbol', 'date', price_col].

    Returns the input DataFrame with an added column: f'rsi_{window}'.
    """
    # Ensure proper sort
    df = df.sort_values(["symbol", "date"]).copy()

    # Price changes per symbol
    delta = df.groupby("symbol")[price_col].diff()

    # Separate gains and losses
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)

    # Wilder's smoothing is equivalent to EMA with alpha = 1/window
    # Use min_periods=window to avoid premature values
    avg_gain = (
        gain.groupby(df["symbol"])
            .ewm(alpha=1/window, adjust=False, min_periods=window)
            .mean()
            .reset_index(level=0, drop=True)
    )
    avg_loss = (
        loss.groupby(df["symbol"])
            .ewm(alpha=1/window, adjust=False, min_periods=window)
            .mean()
            .reset_index(level=0, drop=True)
    )

    # RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # If avg_loss == 0, RSI should be 100 (pure uptrend)
    rsi = rsi.where(avg_loss != 0, 100)

    df[f"rsi_{window}"] = rsi

    return df

def calculate_bb_width(
    df: pd.DataFrame,
    window: int = 20,
    price_col: str = "adjusted_close",
    mult: float = 2.0,
    normalize: str = "sma",  # "sma", "price", or None (raw width)
    keep_components: bool = False,
    ddof: int = 0            # 0 = population-like, 1 = sample (pandas default)
) -> pd.DataFrame:
    """
    Compute Bollinger Band Width (BBW) per symbol.

    Bands:
      middle = SMA(window)
      upper  = middle + mult * rolling_std(window)
      lower  = middle - mult * rolling_std(window)

    Width:
      If normalize == "sma":   (upper - lower) / middle
      If normalize == "price": (upper - lower) / price
      If normalize == None:    (upper - lower)

    Returns df with 'bb_width' (and optional band components).
    """
    df = df.sort_values(["symbol", "date"]).copy()
    g = df.groupby("symbol")

    # Middle band (SMA) and rolling std
    middle = g[price_col].transform(lambda x: x.rolling(window=window, min_periods=window).mean())
    rstd   = g[price_col].transform(lambda x: x.rolling(window=window, min_periods=window).std(ddof=ddof))

    upper = middle + mult * rstd
    lower = middle - mult * rstd

    raw_width = upper - lower  # equals 2 * mult * rstd

    if normalize == "sma":
        denom = middle.replace(0, np.nan)
        bb_width = raw_width / denom
    elif normalize == "price":
        denom = df[price_col].replace(0, np.nan)
        bb_width = raw_width / denom
    else:
        bb_width = raw_width

    bb_width = bb_width.replace([np.inf, -np.inf], np.nan)
    df["bb_width"] = bb_width

    if keep_components:
        df["bb_middle"] = middle
        df["bb_upper"]  = upper
        df["bb_lower"]  = lower

    return df

def calculate_bollinger_percent_b(
    df: pd.DataFrame,
    window: int = 20,
    price_col: str = "adjusted_close",
    mult: float = 2.0,
    ddof: int = 0
) -> pd.DataFrame:
    """Companion indicator: Bollinger %B."""
    df = df.sort_values(["symbol", "date"]).copy()
    g = df.groupby("symbol")
    middle = g[price_col].transform(lambda x: x.rolling(window=window, min_periods=window).mean())
    rstd   = g[price_col].transform(lambda x: x.rolling(window=window, min_periods=window).std(ddof=ddof))
    upper = middle + mult * rstd
    lower = middle - mult * rstd

    denom = (upper - lower).replace(0, np.nan)
    pct_b = (df[price_col] - lower) / denom
    pct_b = pct_b.replace([np.inf, -np.inf], np.nan)

    df["bb_percent_b"] = pct_b
    return df

def flag_bollinger_squeeze(df, window=20, pct=0.1):
    df = df.copy()
    df["bb_width_pctl"] = (
        df.groupby("symbol")["bb_width"].transform(lambda s: s.rank(pct=True))
    )
    df["bb_squeeze"] = (df["bb_width_pctl"] <= pct).astype(int)
    return df

def calculate_adx(
    df: pd.DataFrame,
    window: int = 14,
    price_col: str = "adjusted_close"
) -> pd.DataFrame:
    """
    Calculate Wilder's ADX per symbol on a long-format DataFrame.
    Requires columns: ['symbol', 'date', 'high', 'low', price_col].

    Outputs columns:
      + 'plus_di_{window}' : +DI (Wilder)
      + 'minus_di_{window}': -DI (Wilder)
      + 'adx_{window}'     : ADX (Wilder)
    """
    df = df.sort_values(["symbol", "date"]).copy()

    # Ensure numeric
    for col in ["high", "low", price_col]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Per-symbol shifts
    g = df.groupby("symbol", sort=False)
    prev_close = g[price_col].shift(1)
    prev_high  = g["high"].shift(1)
    prev_low   = g["low"].shift(1)

    # True Range (TR)
    tr1 = df["high"] - df["low"]
    tr2 = (df["high"] - prev_close).abs()
    tr3 = (df["low"]  - prev_close).abs()
    tr  = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Directional Movement
    upMove   = df["high"] - prev_high              # high_t - high_{t-1}
    downMove = prev_low - df["low"]                # low_{t-1} - low_t  (note order)

    plus_dm  = np.where((upMove > downMove) & (upMove > 0), upMove, 0.0)
    minus_dm = np.where((downMove > upMove) & (downMove > 0), downMove, 0.0)

    # Convert to aligned Series
    plus_dm  = pd.Series(plus_dm, index=df.index)
    minus_dm = pd.Series(minus_dm, index=df.index)

    # Wilder's smoothing: EMA with alpha=1/window, adjust=False
    # Use min_periods=window so values start only after full history
    alpha = 1 / window

    atr = g.apply(lambda s: s["TR"] if "TR" in s else None)  # placeholder to attach TR via groupby
    # Better: compute smoothed per symbol using transform
    atr = tr.groupby(df["symbol"]).transform(
        lambda x: x.ewm(alpha=alpha, adjust=False, min_periods=window).mean()
    )
    sm_plus_dm = plus_dm.groupby(df["symbol"]).transform(
        lambda x: x.ewm(alpha=alpha, adjust=False, min_periods=window).mean()
    )
    sm_minus_dm = minus_dm.groupby(df["symbol"]).transform(
        lambda x: x.ewm(alpha=alpha, adjust=False, min_periods=window).mean()
    )

    # Directional Indicators
    # +DI = 100 * smoothed(+DM) / ATR
    # -DI = 100 * smoothed(-DM) / ATR
    denom = atr.replace(0, np.nan)
    plus_di = 100.0 * sm_plus_dm / denom
    minus_di = 100.0 * sm_minus_dm / denom

    # DX = 100 * |+DI - -DI| / (+DI + -DI)
    di_sum = plus_di + minus_di
    di_diff = (plus_di - minus_di).abs()
    dx = 100.0 * di_diff / di_sum
    dx = dx.replace([np.inf, -np.inf], np.nan)

    # ADX = Wilder-smoothed DX
    adx = dx.groupby(df["symbol"]).transform(
        lambda x: x.ewm(alpha=alpha, adjust=False, min_periods=window).mean()
    )

    # Attach outputs
    df[f"plus_di_{window}"]  = plus_di
    df[f"minus_di_{window}"] = minus_di
    df[f"adx_{window}"]      = adx

    return df

def calculate_stochastic(
    df: pd.DataFrame,
    k_window: int = 14,
    d_window: int = 3,
    price_col: str = "adjusted_close",
    use_ema: bool = False,
    keep_components: bool = True
) -> pd.DataFrame:
    """
    Compute Stochastic Oscillator (%K and %D) per symbol.

    %K = 100 * (close - lowest_low_n) / (highest_high_n - lowest_low_n)
    %D = SMA/EMA of %K over d_window (signal line)

    Parameters
    ----------
    df : DataFrame with columns ['symbol', 'date', 'high', 'low', price_col]
    k_window : lookback for rolling high/low (default 14)
    d_window : smoothing window for %D (default 3)
    price_col : column to use for 'close' (default 'adjusted_close')
    use_ema : if True, use EMA for %D; otherwise SMA
    keep_components : if True, keep rolling extrema in the output

    Returns
    -------
    DataFrame with columns:
      - 'stoch_k_{k_window}'
      - 'stoch_d_{d_window}'
      - (optional) 'stoch_low_{k_window}', 'stoch_high_{k_window}'
    """
    df = df.sort_values(["symbol", "date"]).copy()

    # Rolling extrema per symbol with full-window requirement
    roll_low = df.groupby("symbol")["low"].transform(
        lambda x: x.rolling(window=k_window, min_periods=k_window).min()
    )
    roll_high = df.groupby("symbol")["high"].transform(
        lambda x: x.rolling(window=k_window, min_periods=k_window).max()
    )

    # Denominator safety
    denom = (roll_high - roll_low).replace(0, np.nan)

    # %K
    stoch_k = 100.0 * (df[price_col] - roll_low) / denom
    stoch_k = stoch_k.replace([np.inf, -np.inf], np.nan).clip(0, 100)

    # %D: smooth %K
    if use_ema:
        stoch_d = (
            stoch_k.groupby(df["symbol"])
                    .transform(lambda s: s.ewm(span=d_window, adjust=False, min_periods=d_window).mean())
        )
    else:
        stoch_d = (
            stoch_k.groupby(df["symbol"])
                    .transform(lambda s: s.rolling(window=d_window, min_periods=d_window).mean())
        )

    df[f"stoch_k_{k_window}"] = stoch_k
    df[f"stoch_d_{d_window}"] = stoch_d

    if keep_components:
        df[f"stoch_low_{k_window}"]  = roll_low
        df[f"stoch_high_{k_window}"] = roll_high

    return df

def calculate_macd(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    price_col: str = "adjusted_close",
    keep_lines: bool = True
) -> pd.DataFrame:
    """
    Compute MACD, Signal, and Histogram per symbol (vectorized).

    MACD line   = EMA(fast) - EMA(slow)
    Signal line = EMA(MACD, signal)
    Histogram   = MACD - Signal

    Parameters
    ----------
    df : DataFrame with ['symbol','date', price_col]
    fast : int, fast EMA span
    slow : int, slow EMA span (must be > fast)
    signal : int, signal EMA span
    price_col : price column (default 'adjusted_close')
    keep_lines : if True, also output macd_line and macd_signal

    Returns
    -------
    DataFrame with:
      - 'macd_hist_{fast}_{slow}_{signal}'
      - optionally 'macd_line_{fast}_{slow}', 'macd_signal_{signal}'
    """
    if not (isinstance(fast, int) and isinstance(slow, int) and isinstance(signal, int)):
        raise ValueError("fast, slow, and signal must be integers.")
    if fast <= 0 or slow <= 0 or signal <= 0:
        raise ValueError("fast, slow, and signal must be positive.")
    if fast >= slow:
        raise ValueError("fast must be less than slow.")

    df = df.sort_values(["symbol", "date"]).copy()
    # Coerce to numeric
    df[price_col] = pd.to_numeric(df[price_col], errors="coerce")

    # Per-symbol EMAs
    g = df.groupby("symbol")
    ema_fast = g[price_col].transform(lambda s: s.ewm(span=fast, adjust=False).mean())
    ema_slow = g[price_col].transform(lambda s: s.ewm(span=slow, adjust=False).mean())

    macd_line = ema_fast - ema_slow
    macd_signal = macd_line.groupby(df["symbol"]).transform(lambda s: s.ewm(span=signal, adjust=False).mean())
    macd_hist = macd_line - macd_signal

    # Attach outputs
    hist_col = f"macd_hist_{fast}_{slow}_{signal}"
    df[hist_col] = macd_hist

    if keep_lines:
        df[f"macd_line_{fast}_{slow}"] = macd_line
        df[f"macd_signal_{signal}"] = macd_signal

    return df


# ==================== Multi-Period Helper Function ====================

def compute_multi_period_factors(df: pd.DataFrame,
                                 price_col: str = "adjusted_close",
                                 volume_col: str = "volume") -> pd.DataFrame:
    """
    Compute technical factors across multiple time periods for comprehensive analysis.

    This creates a rich feature set capturing short, medium, and long-term signals:
    - Short-term (10-20 days): Day trading, swing trading
    - Medium-term (50 days): Position trading
    - Long-term (200 days): Trend following, investment

    Popular multi-period configurations used by professional traders.

    Returns DataFrame with factors across all time horizons.

    Example output columns:
        dist_sma_20, dist_sma_50, dist_sma_200    # Price distance from SMA
        sma_dist_20_50                             # Distance between 20 and 50 SMA
        rsi_9, rsi_14, rsi_21                      # Multiple RSI windows
        bb_width (10/20/30 overwrites)             # Multiple BB widths
        relative_volume (10/20/30 overwrites)      # Multiple volume periods
    """
    tf = TechnicalFactors(df, price_col=price_col, volume_col=volume_col)

    print("=" * 60)
    print("MULTI-PERIOD TECHNICAL FACTORS COMPUTATION")
    print("=" * 60)

    # === Distance from SMA (Popular: 20, 50, 200) ===
    print("\n[1/7] Computing Distance from SMA...")
    print("  - 20-day: Short-term trend")
    tf.distance_from_sma(window=20)
    print("  - 50-day: Medium-term trend")
    tf.distance_from_sma(window=50)
    print("  - 200-day: Long-term trend (institutional standard)")
    tf.distance_from_sma(window=200)
    print("  - SMA Distance (20 vs 50): Trend momentum indicator")
    tf.sma_distance(short_window=20, long_window=50)

    # === RSI (Popular: 9, 14, 21) ===
    print("\n[2/7] Computing RSI...")
    print("  - 9-period: Fast RSI for active trading")
    tf.rsi(window=9)
    print("  - 14-period: Wilder's standard")
    tf.rsi(window=14)
    print("  - 21-period: Smoothed RSI for longer-term")
    tf.rsi(window=21)

    # === Bollinger Bands (Popular: 10, 20, 30) ===
    # Note: bb_width column gets overwritten, only last one persists
    print("\n[3/7] Computing Bollinger Bands...")
    print("  - 10-day: Short-term volatility")
    tf.bollinger_width(window=10, keep_components=False)
    tf.bollinger_percent_b(window=10)
    print("  - 20-day: Bollinger's standard")
    tf.bollinger_width(window=20, keep_components=False)
    tf.bollinger_percent_b(window=20)
    tf.bollinger_squeeze(window=20)
    print("  - 30-day: Extended volatility")
    tf.bollinger_width(window=30, keep_components=False)
    tf.bollinger_percent_b(window=30)

    # === Relative Volume (Popular: 10, 20, 30) ===
    # Note: relative_volume column gets overwritten
    print("\n[4/7] Computing Relative Volume...")
    print("  - 10-day: Short-term volume spikes")
    tf.relative_volume(window=10)
    print("  - 20-day: Medium-term volume trends")
    tf.relative_volume(window=20)
    print("  - 30-day: Longer-term volume baseline")
    tf.relative_volume(window=30)

    # === MACD (Standard: 12/26/9) ===
    print("\n[5/7] Computing MACD...")
    print("  - Standard 12/26/9 configuration")
    tf.macd(fast=12, slow=26, signal=9, keep_lines=True)

    # === Momentum (Popular: 63, 126, 252 days) ===
    # Note: momentum columns get overwritten
    print("\n[6/7] Computing Momentum Factors...")
    print("  - 252-day (12-1): Classic momentum (most popular)")
    tf.momentum(period=252, skip_days=21, vol_penalty=True)

    # === ADX & Stochastic (if high/low available) ===
    if 'high' in tf.df.columns and 'low' in tf.df.columns:
        print("\n[Bonus] Computing ADX and Stochastic...")
        print("  - 14-period ADX: Wilder's standard")
        tf.adx(window=14)
        print("  - 14/3 Stochastic: Standard configuration")
        tf.stochastic(k_window=14, d_window=3, keep_components=True)

    # === VPT ===
    print("\n[Final] Computing Volume Price Trend...")
    tf.volume_price_trend()

    print("\n" + "=" * 60)
    print(f"✓ Computation complete! Total columns: {len(tf.df.columns)}")
    print(f"✓ Factor columns: {len(tf.get_factor_columns())}")
    print("=" * 60)

    return tf.df


# ==================== Usage Example ====================

if __name__ == '__main__':
    """
    Example usage of the TechnicalFactors class.
    """
    # Sample data creation (replace with your actual data loading)
    print('Creating sample data...')
    dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')
    symbols = [f'SYMBOL_{i}' for i in range(1, 11)]  # 10 symbols

    data = []
    np.random.seed(42)
    for symbol in symbols:
        for date in dates:
            data.append({
                'symbol': symbol,
                'date': date,
                'adjusted_close': 100 + np.random.randn() * 10 + np.random.randn()*0.5,
                'volume': int(1000000 + np.random.randn() * 100000),
                'high': 105 + np.random.randn() * 10,
                'low': 95 + np.random.randn() * 10
            })

    sample_df = pd.DataFrame(data)

    # Method 1: Calculate individual factors
    print('\n=== Method 1: Individual Factors ===')
    tf = TechnicalFactors(sample_df)

    # Run specific factors
    tf.momentum(period=252, skip_days=21)
    tf.rsi(window=14)
    tf.relative_volume(window=30)

    print(f'Columns after individual calculations: {tf.get_factor_columns()}')
    print(tf.df[['symbol', 'date', 'momentum_score', 'rsi_14', 'relative_volume']].head(300))

    # Method 2: Calculate all factors at once
    print('\n=== Method 2: Run All Factors ===')
    tf2 = TechnicalFactors(sample_df)
    result_df = tf2.run_all(include_high_low_indicators=True)

    print(f'\nAll factor columns: {tf2.get_factor_columns()}')
    print(f'Result shape: {result_df.shape}')
    print(result_df[['symbol', 'date'] + tf2.get_factor_columns()[:5]].head())

    # Method 3: Custom parameters - Industry standard
    print('\n=== Method 3: Industry Standard Parameters ===')
    tf3 = TechnicalFactors(sample_df)
    industry_standard_params = {
        'momentum': {'period': 252, 'skip_days': 21, 'vol_penalty': True},  # Classic 12-1
        'rsi': {'window': 14},                                               # Wilder's standard
        'bollinger_width': {'window': 20},                                   # Bollinger's standard
        'distance_from_sma': {'window': 200},                                # 200-day MA standard
    }
    result_df_standard = tf3.run_all(custom_params=industry_standard_params)
    print(f'Computed with industry standard params. Shape: {result_df_standard.shape}')

    # Method 4: Multi-period factors for different time horizons
    print('\n=== Method 4: Multi-Period Factors ===')
    tf4 = TechnicalFactors(sample_df)

    # Compute short-term factors (20-day)
    print("Computing short-term factors (20-day)...")
    tf4.distance_from_sma(window=20)
    tf4.rsi(window=9)
    tf4.bollinger_width(window=10)
    tf4.relative_volume(window=10)

    # Compute medium-term factors (50-day)
    print("Computing medium-term factors (50-day)...")
    tf4.distance_from_sma(window=50)
    tf4.rsi(window=14)
    tf4.bollinger_width(window=20)
    tf4.relative_volume(window=20)

    # Compute long-term factors (200-day)
    print("Computing long-term factors (200-day)...")
    tf4.distance_from_sma(window=200)
    tf4.rsi(window=21)
    tf4.bollinger_width(window=30)
    tf4.relative_volume(window=30)

    # Multiple momentum periods
    print("Computing multi-period momentum...")
    tf4.momentum(period=63, skip_days=5, vol_penalty=True)   # 3-month (will create momentum_raw, momentum_score)
    # Note: momentum creates same column names, so we compute only once or need to rename

    print(f'Multi-period factors computed. Shape: {tf4.df.shape}')
    print(f'Factor columns: {tf4.get_factor_columns()}')

    print('\n✓ Example completed successfully!')