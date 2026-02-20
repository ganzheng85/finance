import pandas as pd
import numpy as np

def calculate_volatility(df, window=252):
    """
    Calculates annualized volatility based on daily log returns.
    """
    # Calculate daily log returns
    df = df.sort_values(['symbol', 'date'])
    df['log_return'] = df.groupby('symbol')['adjusted_close'].transform(
        lambda x: np.log(x / x.shift(1))
    )
    
    # Calculate rolling standard deviation and annualize it
    # 252 is the standard number of trading days in a year
    vol = df.groupby('symbol')['log_return'].transform(
        lambda x: x.rolling(window=window).std() * np.sqrt(252)
    )
    return vol

def calculate_volatility(df: pd.DataFrame, window: int = 252, price_col: str = "adjusted_close") -> pd.Series:
    """
    Annualized volatility per row, computed from daily returns over 'window' for each symbol.
    Returns a Series aligned to df's index.
    """
    # Sort and compute daily returns per symbol
    df = df.sort_values(["symbol", "date"]).copy()
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
    return vol_annual

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
        df["volatility"] = calculate_volatility(df, window=period, price_col=price_col)

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
    df = df.sort_values(['symbol', 'date'])

    def calculate_vpt_for_group(group):
        # Calculate percentage price change
        price_pct_change = group['adjusted_close'].pct_change()
        # Calculate the change in VPT for each day
        vpt_change = group['volume'] * price_pct_change
        # Sum cumulatively to get the indicator value
        return vpt_change.cumsum()

    # Apply the calculation grouped by symbol
    df['vpt'] = df.groupby('symbol').apply(calculate_vpt_for_group).reset_index(level=0, drop=True)
    
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

def calculate_bb_width(df, window=20):
    """Calculates Bollinger Band Width to identify 'squeezes'."""
    df = df.sort_values(['symbol', 'date'])
    sma = df.groupby('symbol')['adjusted_close'].transform(lambda x: x.rolling(window=window).mean())
    std = df.groupby('symbol')['adjusted_close'].transform(lambda x: x.rolling(window=window).std())
    
    upper_band = sma + (2 * std)
    lower_band = sma - (2 * std)
    df['bb_width'] = (upper_band - lower_band) / sma
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