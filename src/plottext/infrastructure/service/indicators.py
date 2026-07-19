import numpy as np
import pandas as pd
import pandas_ta as ta


# ============================================================
# TECHNICAL INDICATORS
# ============================================================

def add_indicators(df, rsi_len=14, adx_len=14, atr_len=14, bb_len=20, bb_std=2, vol_window=20):
    out = df.copy()

    out["RSI"] = ta.rsi(out["Close"], length=rsi_len)

    macd = ta.macd(out["Close"])
    if macd is not None:
        out = out.join(macd)

    adx_result = ta.adx(high=out["High"], low=out["Low"], close=out["Close"], length=adx_len)
    if adx_result is not None:
        out = out.join(adx_result)

    out["ATR"] = ta.atr(high=out["High"], low=out["Low"], close=out["Close"], length=atr_len)

    bb = ta.bbands(out["Close"], length=bb_len, std=bb_std)
    if bb is not None:
        out = out.join(bb)

    out["VOL_SMA"] = out["Volume"].rolling(vol_window).mean()
    out["VOL_REL"] = out["Volume"] / out["VOL_SMA"]
    out["DOJI"] = ta.cdl_pattern(
        open_=out["Open"],
        high=out["High"],
        low=out["Low"],
        close=out["Close"],
        name="doji"
    )
    return out


# ============================================================
# DONCHIAN CHANNELS
# ============================================================

def add_donchian(df, donchian_n=20):
    out = df.copy()
    out["resistance_level"] = out["High"].rolling(donchian_n).max().shift(1)
    out["breakout"] = out["Close"] > out["resistance_level"]
    return out


def add_donchian_bearish(df, donchian_n=20):
    out = df.copy()
    out["support_level"] = out["Low"].rolling(donchian_n).min().shift(1)
    out["breakdown"] = out["Close"] < out["support_level"]
    return out


def add_donchian_both(df, donchian_n=20):
    out = df.copy()
    out["resistance_level"] = out["High"].rolling(donchian_n).max().shift(1)
    out["breakout"] = out["Close"] > out["resistance_level"]
    out["support_level"] = out["Low"].rolling(donchian_n).min().shift(1)
    out["breakdown"] = out["Close"] < out["support_level"]
    return out


def detect_breakout_events(df_donchian, min_gap_days=15):
    events = df_donchian[df_donchian["breakout"] == True].copy()
    if events.empty:
        return events
    keep = [events.index[0]]
    for d in events.index[1:]:
        if (d - keep[-1]).days >= min_gap_days:
            keep.append(d)
    return events.loc[keep]


def detect_breakdown_events(df_donchian_bear, min_gap_days=15):
    events = df_donchian_bear[df_donchian_bear["breakdown"] == True].copy()
    if events.empty:
        return events
    keep = [events.index[0]]
    for d in events.index[1:]:
        if (d - keep[-1]).days >= min_gap_days:
            keep.append(d)
    return events.loc[keep]


# ============================================================
# BOLLINGER BANDS
# ============================================================

def bbands_upper_df(df, length=20, std=2):
    close = df['Close']
    sma = close.rolling(window=length).mean()
    std_vals = close.rolling(window=length).std()
    return sma + (std_vals * std)


def bbands_lower_df(df, length=20, std=2):
    close = df['Close']
    sma = close.rolling(window=length).mean()
    std_vals = close.rolling(window=length).std()
    return sma - (std_vals * std)


def bbands_width_df(df, length=20, std=2):
    close = df['Close']
    sma = close.rolling(window=length).mean()
    std_vals = close.rolling(window=length).std()
    upper = sma + (std_vals * std)
    lower = sma - (std_vals * std)
    return (upper - lower) / close


def bbands_upper(close, length=20, std=2):
    sma = close.rolling(length).mean()
    std_vals = close.rolling(length).std()
    return sma + (std_vals * std)


def bbands_lower(close, length=20, std=2):
    sma = close.rolling(length).mean()
    std_vals = close.rolling(length).std()
    return sma - (std_vals * std)


def bbands_middle(close, length=20):
    return close.rolling(length).mean()


def bbands_width(close, length=20, std=2):
    bb = ta.bbands(pd.Series(close), length=length, std=std)
    upper, lower = bb.iloc[:, 2], bb.iloc[:, 0]
    return (upper - lower) / pd.Series(close)


def bollinger_breakout_signal(close, length=20, num_std=2):
    sma = close.rolling(length).mean()
    std = close.rolling(length).std()
    upper_band = sma + (std * num_std)
    return close > upper_band


def bollinger_breakout(close, length=20, num_std=2):
    sma = close.rolling(length).mean()
    std = close.rolling(length).std()
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    breakout_signal = close > upper_band
    return breakout_signal, upper_band, lower_band


# ============================================================
# INDICATOR WRAPPERS (compatible with backtesting.py self.I())
# ============================================================

def adx(high, low, close, length=14):
    return ta.adx(pd.Series(high), pd.Series(low), pd.Series(close), length=length).iloc[:, 0]


def resistance(high, n=20):
    return pd.Series(high).rolling(n).max().shift(1)


def support(low, n=20):
    return pd.Series(low).rolling(n).min().shift(1)


def vol_ratio(volume, n=20):
    v = pd.Series(volume)
    return v / v.rolling(n).mean()


def macd_hist(close, fast=12, slow=26, signal=9):
    m = ta.macd(pd.Series(close), fast=fast, slow=slow, signal=signal)
    return m.iloc[:, 1]


def rsi(close, length=14):
    return ta.rsi(pd.Series(close), length=length)


def atr(high, low, close, length=14):
    return ta.atr(pd.Series(high), pd.Series(low), pd.Series(close), length=length)


# ============================================================
# UTILITY
# ============================================================

def _col(df, prefix):
    matches = [c for c in df.columns if c.startswith(prefix)]
    if not matches:
        raise KeyError(
            f"No column found with prefix '{prefix}'. "
            f"Did you run add_indicators() on this DataFrame? "
            f"Available columns: {df.columns.tolist()}"
        )
    return matches[0]
