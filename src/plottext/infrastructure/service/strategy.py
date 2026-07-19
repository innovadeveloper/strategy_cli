import pandas as pd
from backtesting import Strategy

from plottext.infrastructure.service.indicators import (
    bbands_upper_df,
    bbands_lower_df,
    bbands_width_df,
    adx,
    resistance,
    support,
    vol_ratio,
    macd_hist,
    rsi,
    atr,
)


# ============================================================
# DEFAULT CONDITIONS
# ============================================================
# All strategy parameters live here. Pass a modified copy to
# run_backtest_v4() / run_backtest_all_tickers_current_day()
# to compare different configurations without touching code.
#
# Structure:
#   "long"       : which conditions to CHECK for LONG entries
#   "short"      : which conditions to CHECK for SHORT entries
#   "thresholds" : numeric values shared by both directions
#   "bollinger"  : Bollinger Band parameters (replaces EightStepBollingerStrategy)
# ============================================================

DEFAULT_CONDITIONS = {
    # --- Enable/disable entire direction ---
    "enable_long": True,
    "enable_short": True,

    # --- LONG entry conditions (set False to skip that filter) ---
    "long": {
        "adx": True,        # ADX > threshold and rising
        "breakout": True,   # Close > resistance (Donchian or BB upper)
        "macd": True,       # MACD histogram > 0 and rising
        "rsi": True,        # RSI within [rsi_min, rsi_max]
        "volume": False,    # Volume ratio > threshold
        "bb_squeeze": False,# Recent Bollinger squeeze
    },

    # --- SHORT entry conditions ---
    "short": {
        "adx": True,        # ADX > threshold and rising
        "breakout": True,   # Close < support (Donchian or BB lower)
        "macd": True,       # MACD histogram < 0 and falling
        "rsi": True,        # RSI within [rsi_min, rsi_max]
        "volume": False,
        "bb_squeeze": False,
    },

    # --- Numeric thresholds (shared by both directions) ---
    "thresholds": {
        "adx": 14,
        "rsi_min": 30,
        "rsi_max": 78,
        "volume": 1.5,
        "bb_squeeze": 0.04,
        "atr_mult": 3,      # SL/TP = entry ± atr_mult * ATR
    },

    # --- Resistance/support mode ---
    # use_bollinger=False  -> Donchian channels (rolling High/Low)
    # use_bollinger=True   -> Bollinger Bands upper/lower
    "bollinger": {
        "use_bollinger": False,
        "bb_length": 20,
        "bb_std": 2,
    },
}


# ============================================================
# SINGLE STRATEGY CLASS
# ============================================================

class EightStepStrategy(Strategy):

    conditions = None

    def __init__(self, broker, data, params=None):
        if params and "conditions" in params:
            self.conditions = params["conditions"]
        if self.conditions is None:
            self.conditions = DEFAULT_CONDITIONS

        super().__init__(broker, data, params)

    def init(self):
        thresholds = self.conditions.get("thresholds", {})
        bollinger_cfg = self.conditions.get("bollinger", {})

        self._adx_threshold = thresholds.get("adx", 14)
        self._rsi_min = thresholds.get("rsi_min", 30)
        self._rsi_max = thresholds.get("rsi_max", 78)
        self._volume_threshold = thresholds.get("volume", 1.5)
        self._bb_squeeze_threshold = thresholds.get("bb_squeeze", 0.04)
        self._atr_mult = thresholds.get("atr_mult", 3)

        self._use_bollinger = bollinger_cfg.get("use_bollinger", False)
        self._bb_length = bollinger_cfg.get("bb_length", 20)
        self._bb_std = bollinger_cfg.get("bb_std", 2)

        df = self.data.df

        if self._use_bollinger:
            self._bb_upper = bbands_upper_df(df, self._bb_length, self._bb_std)
            self._bb_lower = bbands_lower_df(df, self._bb_length, self._bb_std)
            self._bb_width = bbands_width_df(df, self._bb_length, self._bb_std)
            self._resistance = self._bb_upper
            self._support = self._bb_lower
        else:
            self._resistance = self.I(resistance, self.data.High)
            self._support = self.I(support, self.data.Low)

        self._adx = self.I(adx, self.data.High, self.data.Low, self.data.Close)
        self._vol_ratio = self.I(vol_ratio, self.data.Volume)
        self._macd_hist = self.I(macd_hist, self.data.Close)
        self._rsi = self.I(rsi, self.data.Close)
        self._atr = self.I(atr, self.data.High, self.data.Low, self.data.Close)

    def _evaluate_common(self, side_conditions, idx):
        """
        Evaluates filters that are direction-agnostic:
        ADX, RSI, volume, bb_squeeze.
        Returns False if any enabled filter fails.
        """
        if side_conditions.get("adx", True):
            if self._adx[idx] <= self._adx_threshold or self._adx[idx] <= self._adx[idx - 1]:
                return False

        if side_conditions.get("rsi", True):
            if not (self._rsi_min < self._rsi[idx] < self._rsi_max):
                return False

        if side_conditions.get("volume", False):
            if self._vol_ratio[idx] <= self._volume_threshold:
                return False

        if side_conditions.get("bb_squeeze", False):
            if self._use_bollinger:
                if min(self._bb_width.iloc[-10:]) >= self._bb_squeeze_threshold:
                    return False
            else:
                return False

        return True

    def next(self):
        if self.position:
            return
        if len(self.data.Close) < 30:
            return

        idx = len(self.data.Close) - 1

        try:
            if self._use_bollinger:
                if pd.isna(self._bb_upper.iloc[idx]) or pd.isna(self._bb_width.iloc[idx]):
                    return
            else:
                if pd.isna(self._resistance[idx]) or pd.isna(self._support[idx]):
                    return
            if pd.isna(self._adx[idx]) or pd.isna(self._atr[idx]):
                return
        except (IndexError, AttributeError):
            return

        price = self.data.Close[-1]
        cond_long = self.conditions.get("long", {})
        cond_short = self.conditions.get("short", {})
        risk = self._atr_mult * self._atr[idx]

        # ---- LONG ----
        if self.conditions.get("enable_long", True):
            if self._evaluate_common(cond_long, idx):
                breakout_up = price > (
                    self._resistance.iloc[idx] if self._use_bollinger
                    else self._resistance[idx]
                )
                macd_up = self._macd_hist[idx] > 0 and self._macd_hist[idx] > self._macd_hist[idx - 1]

                long_ok = True
                if cond_long.get("breakout", True) and not breakout_up:
                    long_ok = False
                if long_ok and cond_long.get("macd", True) and not macd_up:
                    long_ok = False

                if long_ok:
                    self.buy(sl=price - risk, tp=price + risk)
                    return

        # ---- SHORT ----
        if self.conditions.get("enable_short", True):
            if self._evaluate_common(cond_short, idx):
                breakout_down = price < (
                    self._support.iloc[idx] if self._use_bollinger
                    else self._support[idx]
                )
                macd_down = self._macd_hist[idx] < 0 and self._macd_hist[idx] < self._macd_hist[idx - 1]

                short_ok = True
                if cond_short.get("breakout", True) and not breakout_down:
                    short_ok = False
                if short_ok and cond_short.get("macd", True) and not macd_down:
                    short_ok = False

                if short_ok:
                    self.sell(sl=price + risk, tp=price - risk)
                    return
