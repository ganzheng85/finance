# Technical Factors Code Review

**Review Date:** June 13, 2026  
**File Reviewed:** `techinical_factor.py` (1,105 lines)

---

## 🚨 CRITICAL ISSUES FOUND

### 1. **DUPLICATE FUNCTION DEFINITIONS** (High Priority)

#### Issue A: `calculate_bb_width` defined TWICE

**First definition:** Lines 539-548 (simple version)
```python
def calculate_bb_width(df, window=20):
    """Calculates Bollinger Band Width to identify 'squeezes'."""
    df = df.sort_values(['symbol', 'date'])
    sma = df.groupby('symbol')['adjusted_close'].transform(lambda x: x.rolling(window=window).mean())
    std = df.groupby('symbol')['adjusted_close'].transform(lambda x: x.rolling(window=window).std())
    upper_band = sma + (2 * std)
    lower_band = sma - (2 * std)
    df['bb_width'] = (upper_band - lower_band) / sma
    return df
```

**Second definition:** Lines 550-603 (comprehensive version with normalization)
```python
def calculate_bb_width(
    df: pd.DataFrame,
    window: int = 20,
    price_col: str = "adjusted_close",
    mult: float = 2.0,
    normalize: str = "sma",
    keep_components: bool = False,
    ddof: int = 0
) -> pd.DataFrame:
```

**Impact:** Python will use the SECOND definition (lines 550-603). The first definition (lines 539-548) is **dead code** and will never execute.

**Recommendation:** ✅ **DELETE lines 539-548** (the first definition)

---

#### Issue B: `calculate_macd` defined TWICE

**First definition:** Lines 787-845
**Second definition:** Lines 847-905

**Impact:** The two definitions are **IDENTICAL**. The second one (lines 847-905) will override the first. Lines 787-845 are **dead code**.

**Recommendation:** ✅ **DELETE lines 787-845** (the first definition)

---

### 2. **INEFFICIENT CODE** (Medium Priority)

#### Issue: Momentum function calls `calculate_volatility_standalone` inefficiently

**Location:** Line 290

```python
def calculate_momentum_factor(...):
    ...
    if vol_penalty:
        df["volatility"] = calculate_volatility_standalone(df, window=period, price_col=price_col)['volatility']
```

**Problem:**
- `calculate_volatility_standalone` creates a COPY of the entire dataframe (`df.copy()`)
- Sorts it again (already sorted)
- Returns the entire df just to extract one column

**Impact:** Unnecessary memory allocation and CPU cycles when processing 500 stocks × 1000+ days

**Better approach:**
```python
if vol_penalty:
    # Compute volatility inline without copying df
    daily_ret = df.groupby("symbol")[price_col].pct_change()
    vol_daily = (
        daily_ret.groupby(df["symbol"])
        .rolling(window=period, min_periods=period)
        .std()
        .reset_index(level=0, drop=True)
    )
    df['volatility'] = vol_daily * np.sqrt(252)
```

**Recommendation:** ⚠️ **Refactor for efficiency** (optional, not a bug)

---

## ✅ CORRECTNESS REVIEW

I'll verify each indicator's mathematical correctness:

### 1. **Volatility** (Lines 234-255) - ✅ CORRECT

```python
daily_ret = df.groupby("symbol")[price_col].pct_change()
vol_daily = daily_ret.groupby(df["symbol"]).rolling(window=window, min_periods=window).std()
vol_annual = vol_daily * np.sqrt(252)
```

**Verification:**
- Daily returns: ✅ Correct (`pct_change()`)
- Rolling std: ✅ Correct
- Annualization: ✅ Correct (std × √252)

**Status:** **CORRECT** ✅

---

### 2. **Momentum (12-1)** (Lines 257-321) - ✅ CORRECT

```python
px_t_minus_skip = df.groupby("symbol")[price_col].shift(skip_days)
px_t_minus_period = df.groupby("symbol")[price_col].shift(period)
momentum_raw = (px_t_minus_skip / px_t_minus_period) - 1
```

**Verification:**
- For 12-1 momentum: `period=252` (12 months), `skip_days=21` (1 month)
- Formula: Return from t-252 to t-21
- This measures: Price 21 days ago / Price 252 days ago - 1
- ✅ **Correct** (standard Jegadeesh-Titman 1993 momentum)

**Volatility adjustment:**
```python
df["momentum_score"] = df["momentum_raw"] / denom  # denom = volatility
```
- ✅ **Correct** (risk-adjusted momentum)

**Winsorization and Z-score:** ✅ Both implemented correctly

**Status:** **CORRECT** ✅

---

### 3. **Distance from SMA** (Lines 323-342) - ✅ CORRECT

```python
df[sma_col_name] = df.groupby('symbol')['adjusted_close'].transform(
    lambda x: x.rolling(window=window).mean()
)
df[f'dist_sma_{window}'] = (df['adjusted_close'] / df[sma_col_name]) - 1
```

**Verification:**
- SMA calculation: ✅ Correct
- Distance: (Price / SMA) - 1 = % above/below SMA ✅ Correct

**Status:** **CORRECT** ✅

---

### 4. **SMA Distance** (Lines 344-389) - ✅ CORRECT

```python
sma_short = df.groupby('symbol')[price_col].transform(
    lambda x: x.rolling(window=short_window, min_periods=short_window).mean()
)
sma_long = df.groupby('symbol')[price_col].transform(
    lambda x: x.rolling(window=long_window, min_periods=long_window).mean()
)
sma_distance = (sma_short / denom) - 1  # denom = sma_long
```

**Verification:**
- Calculates (SMA_short / SMA_long) - 1 ✅ Correct
- Positive = bullish (short SMA > long SMA) ✅ Correct

**Status:** **CORRECT** ✅

---

### 5. **Relative Volume (RVOL)** (Lines 391-474) - ✅ CORRECT

```python
baseline = g.transform(lambda x: x.rolling(window=window, min_periods=window).mean())
rvol = vol / denom  # denom = baseline
```

**Verification:**
- RVOL = Current volume / Average volume ✅ Correct
- EMA option: ✅ Correct
- Weekday-specific baseline: ✅ Correct (clever feature!)

**Status:** **CORRECT** ✅

---

### 6. **Volume Price Trend (VPT)** (Lines 476-494) - ✅ CORRECT

```python
price_pct_change = group['adjusted_close'].pct_change()
vpt_change = group['volume'] * price_pct_change
return vpt_change.cumsum()
```

**Verification:**
- VPT formula: Cumulative sum of (Volume × Price % Change) ✅ Correct
- This is the standard VPT indicator

**Status:** **CORRECT** ✅

---

### 7. **RSI (Wilder's)** (Lines 496-537) - ⚠️ MOSTLY CORRECT (Minor Note)

```python
gain = delta.clip(lower=0)
loss = (-delta).clip(lower=0)

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

rs = avg_gain / avg_loss
rsi = 100 - (100 / (1 + rs))
```

**Verification:**

**Wilder's RSI formula:**
1. First average: Simple average of first 14 periods
2. Subsequent: Smoothed average using: `(Previous Avg × 13 + Current) / 14`

**Your implementation:**
- Uses `ewm(alpha=1/14)` from the start
- This is equivalent to Wilder's smoothing AFTER the first period

**Technical note:**
- Wilder's original uses SMA for first period, then EWM
- Your code uses EWM from the start with `min_periods=window`
- After convergence (15-20 periods), the values are nearly identical
- This is an acceptable approximation used by many libraries

**Improvement (if you want exact Wilder's):**
```python
# First, calculate SMA for first window
first_avg_gain = gain.groupby(df["symbol"]).transform(
    lambda x: x.rolling(window=window).mean()
)
first_avg_loss = loss.groupby(df["symbol"]).transform(
    lambda x: x.rolling(window=window).mean()
)

# Then apply EWM starting from window+1
avg_gain = gain.groupby(df["symbol"]).transform(
    lambda x: x.ewm(alpha=1/window, adjust=False).mean()
)
# Initialize first window with SMA
avg_gain = avg_gain.where(df.groupby("symbol").cumcount() >= window, first_avg_gain)
```

**Status:** **MOSTLY CORRECT** ⚠️ (Works in practice, slight deviation from Wilder's original)

---

### 8. **Bollinger Band Width** (Lines 550-603) - ✅ CORRECT

```python
middle = g[price_col].transform(lambda x: x.rolling(window=window, min_periods=window).mean())
rstd   = g[price_col].transform(lambda x: x.rolling(window=window, min_periods=window).std(ddof=ddof))

upper = middle + mult * rstd
lower = middle - mult * rstd

raw_width = upper - lower  # equals 2 * mult * rstd

if normalize == "sma":
    bb_width = raw_width / denom  # denom = middle
```

**Verification:**
- Upper band: SMA + (2 × σ) ✅ Correct
- Lower band: SMA - (2 × σ) ✅ Correct
- Width: (Upper - Lower) / SMA ✅ Correct
- Normalization options: ✅ Correct

**Status:** **CORRECT** ✅

---

### 9. **Bollinger %B** (Lines 605-625) - ✅ CORRECT

```python
pct_b = (df[price_col] - lower) / denom  # denom = (upper - lower)
```

**Verification:**
- %B = (Price - Lower) / (Upper - Lower) ✅ Correct
- Values: 0 = at lower band, 0.5 = at middle, 1.0 = at upper band ✅ Correct

**Status:** **CORRECT** ✅

---

### 10. **Bollinger Squeeze** (Lines 627-633) - ✅ CORRECT

```python
df["bb_width_pctl"] = (
    df.groupby("symbol")["bb_width"].transform(lambda s: s.rank(pct=True))
)
df["bb_squeeze"] = (df["bb_width_pctl"] <= pct).astype(int)
```

**Verification:**
- Uses percentile rank to identify when BBW is in bottom 10% ✅ Correct
- This correctly identifies low volatility "squeeze" conditions

**Status:** **CORRECT** ✅

---

### 11. **ADX (Average Directional Index)** (Lines 635-717) - ✅ CORRECT

This is the most complex indicator. Let me verify step by step:

**True Range:**
```python
tr1 = df["high"] - df["low"]
tr2 = (df["high"] - prev_close).abs()
tr3 = (df["low"]  - prev_close).abs()
tr  = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
```
✅ **CORRECT** (Standard TR formula)

**Directional Movement:**
```python
upMove   = df["high"] - prev_high
downMove = prev_low - df["low"]

plus_dm  = np.where((upMove > downMove) & (upMove > 0), upMove, 0.0)
minus_dm = np.where((downMove > upMove) & (downMove > 0), downMove, 0.0)
```
✅ **CORRECT** 
- +DM: Upward movement when high increases more than low decreases
- -DM: Downward movement when low decreases more than high increases

**Wilder Smoothing:**
```python
alpha = 1 / window
atr = tr.groupby(df["symbol"]).transform(
    lambda x: x.ewm(alpha=alpha, adjust=False, min_periods=window).mean()
)
```
✅ **CORRECT** (Wilder's smoothing with α=1/14)

**Directional Indicators:**
```python
plus_di = 100.0 * sm_plus_dm / denom   # denom = atr
minus_di = 100.0 * sm_minus_dm / denom
```
✅ **CORRECT**

**DX and ADX:**
```python
dx = 100.0 * di_diff / di_sum  # di_diff = |+DI - -DI|, di_sum = +DI + -DI
adx = dx.groupby(df["symbol"]).transform(
    lambda x: x.ewm(alpha=alpha, adjust=False, min_periods=window).mean()
)
```
✅ **CORRECT** (ADX is smoothed DX)

**Status:** **CORRECT** ✅

---

### 12. **Stochastic Oscillator** (Lines 719-785) - ✅ CORRECT

```python
roll_low = df.groupby("symbol")["low"].transform(
    lambda x: x.rolling(window=k_window, min_periods=k_window).min()
)
roll_high = df.groupby("symbol")["high"].transform(
    lambda x: x.rolling(window=k_window, min_periods=k_window).max()
)

stoch_k = 100.0 * (df[price_col] - roll_low) / denom  # denom = (roll_high - roll_low)
```

**Verification:**
- %K = 100 × (Close - Low_14) / (High_14 - Low_14) ✅ Correct
- Clipping to [0, 100]: ✅ Correct
- %D smoothing (SMA or EMA of %K): ✅ Correct

**Status:** **CORRECT** ✅

---

### 13. **MACD** (Lines 847-905) - ✅ CORRECT

```python
ema_fast = g[price_col].transform(lambda s: s.ewm(span=fast, adjust=False).mean())
ema_slow = g[price_col].transform(lambda s: s.ewm(span=slow, adjust=False).mean())

macd_line = ema_fast - ema_slow
macd_signal = macd_line.groupby(df["symbol"]).transform(lambda s: s.ewm(span=signal, adjust=False).mean())
macd_hist = macd_line - macd_signal
```

**Verification:**
- MACD line = EMA(12) - EMA(26) ✅ Correct
- Signal line = EMA(MACD, 9) ✅ Correct  
- Histogram = MACD - Signal ✅ Correct

**Status:** **CORRECT** ✅

---

## 📊 SUMMARY

### Critical Issues (Must Fix)
1. ❌ **Delete duplicate `calculate_bb_width`** (lines 539-548)
2. ❌ **Delete duplicate `calculate_macd`** (lines 787-845)

### Correctness Results
| Indicator | Status | Notes |
|-----------|--------|-------|
| Volatility | ✅ CORRECT | Annualized volatility formula correct |
| Momentum (12-1) | ✅ CORRECT | Jegadeesh-Titman implementation |
| Distance from SMA | ✅ CORRECT | Standard formula |
| SMA Distance | ✅ CORRECT | Correct cross-SMA calculation |
| Relative Volume | ✅ CORRECT | Includes clever weekday option |
| VPT | ✅ CORRECT | Standard VPT formula |
| RSI | ⚠️ MOSTLY CORRECT | Uses EWM from start (acceptable approx) |
| Bollinger Width | ✅ CORRECT | Standard BB formula |
| Bollinger %B | ✅ CORRECT | Correct position in bands |
| Bollinger Squeeze | ✅ CORRECT | Percentile-based squeeze detection |
| ADX | ✅ CORRECT | Complex but correct Wilder's ADX |
| Stochastic | ✅ CORRECT | Standard %K and %D |
| MACD | ✅ CORRECT | Standard MACD histogram |

### Performance Issues (Optional)
- ⚠️ Momentum function calls `calculate_volatility_standalone` inefficiently (creates copy)
- Consider refactoring for large datasets (500+ stocks, 1000+ days)

---

## 🔧 RECOMMENDED FIXES

### Fix 1: Remove Duplicate Functions

**Delete lines 539-548** (first `calculate_bb_width` definition):
```python
# DELETE THIS (lines 539-548)
def calculate_bb_width(df, window=20):
    """Calculates Bollinger Band Width to identify 'squeezes'."""
    df = df.sort_values(['symbol', 'date'])
    sma = df.groupby('symbol')['adjusted_close'].transform(lambda x: x.rolling(window=window).mean())
    std = df.groupby('symbol')['adjusted_close'].transform(lambda x: x.rolling(window=window).std())
    upper_band = sma + (2 * std)
    lower_band = sma - (2 * std)
    df['bb_width'] = (upper_band - lower_band) / sma
    return df
```

**Delete lines 787-845** (first `calculate_macd` definition):
```python
# DELETE THIS (lines 787-845)
def calculate_macd(
    df: pd.DataFrame,
    fast: int = 12,
    ...
    return df
```

### Fix 2: Improve RSI (Optional - for exact Wilder's formula)

If you want the exact Wilder's RSI (SMA for first period, then EWM):

```python
def calculate_rsi_wilder_exact(df: pd.DataFrame, window: int = 14, price_col: str = "adjusted_close") -> pd.DataFrame:
    df = df.sort_values(["symbol", "date"]).copy()
    
    delta = df.groupby("symbol")[price_col].diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    
    # Calculate initial SMA
    def wilder_smooth(x, window):
        # First value is SMA of first 'window' periods
        sma = x.rolling(window=window).mean()
        # Then apply Wilder smoothing for rest
        result = x.copy()
        for i in range(window, len(x)):
            result.iloc[i] = (result.iloc[i-1] * (window - 1) + x.iloc[i]) / window
        # Use SMA for first window periods, Wilder for rest
        return result.where(result.index >= window - 1, sma)
    
    avg_gain = gain.groupby(df["symbol"]).transform(lambda x: wilder_smooth(x, window))
    avg_loss = loss.groupby(df["symbol"]).transform(lambda x: wilder_smooth(x, window))
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.where(avg_loss != 0, 100)
    
    df[f"rsi_{window}"] = rsi
    return df
```

**However**, your current EWM implementation is acceptable and matches most libraries (TA-Lib, pandas-ta).

---

## ✅ OVERALL VERDICT

**Your technical factors are MATHEMATICALLY CORRECT!** ✅

The only issues are:
1. **Code duplication** (2 functions defined twice) - Easy fix, delete dead code
2. **Minor RSI deviation** - Acceptable approximation, works in practice
3. **Performance issue** - Optional optimization for large datasets

**Grade: A- (would be A+ after removing duplicates)**

---

**Next Steps:**
1. Delete lines 539-548 (first `calculate_bb_width`)
2. Delete lines 787-845 (first `calculate_macd`)
3. Test with real data to verify output ranges are sensible
4. (Optional) Profile performance on 500 stocks × 1000 days

---

**Reviewed by:** Claude Sonnet 4.5  
**Date:** June 13, 2026
