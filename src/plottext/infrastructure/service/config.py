import copy

from plottext.infrastructure.service.strategy import DEFAULT_CONDITIONS


def _base() -> dict:
    return copy.deepcopy(DEFAULT_CONDITIONS)


# ============================================================
# CATALOGUE OF STRATEGY CONFIGURATIONS
# ============================================================
# Each entry is a conditions dict ready to pass to
# run_backtest_v4() or run_backtest_all_tickers_current_day().
#
# Naming convention:
#   <resistance_mode>__<direction>__<filters>__<variant>
# ============================================================

CONFIGS: dict[str, dict] = {

    # ── BASELINE ─────────────────────────────────────────────
    # Full strategy, all filters, Donchian channels
    "donchian__both__full": _base(),

    # Full strategy, all filters, Bollinger Bands
    "bollinger__both__full": {
        **_base(),
        "bollinger": {"use_bollinger": True, "bb_length": 20, "bb_std": 2},
    },

    # ── DIRECTION ────────────────────────────────────────────
    # LONG only (Donchian)
    "donchian__long__full": {
        **_base(),
        "enable_short": False,
    },

    # SHORT only (Donchian)
    "donchian__short__full": {
        **_base(),
        "enable_long": False,
    },

    # LONG only (Bollinger)
    "bollinger__long__full": {
        **_base(),
        "enable_short": False,
        "bollinger": {"use_bollinger": True, "bb_length": 20, "bb_std": 2},
    },

    # SHORT only (Bollinger)
    "bollinger__short__full": {
        **_base(),
        "enable_long": False,
        "bollinger": {"use_bollinger": True, "bb_length": 20, "bb_std": 2},
    },

    # ── FILTER ABLATION — remove one filter at a time ────────
    # Useful to detect which filter adds real value.

    # Without MACD filter
    "donchian__both__no_macd": {
        **_base(),
        "long":  {**_base()["long"],  "macd": False},
        "short": {**_base()["short"], "macd": False},
    },

    # Without ADX filter
    "donchian__both__no_adx": {
        **_base(),
        "long":  {**_base()["long"],  "adx": False},
        "short": {**_base()["short"], "adx": False},
    },

    # Without RSI filter
    "donchian__both__no_rsi": {
        **_base(),
        "long":  {**_base()["long"],  "rsi": False},
        "short": {**_base()["short"], "rsi": False},
    },

    # Breakout only — minimum viable strategy (no indicator filters)
    "donchian__both__breakout_only": {
        **_base(),
        "long": {
            "adx": False, "breakout": True, "macd": False,
            "rsi": False, "volume": False, "bb_squeeze": False,
        },
        "short": {
            "adx": False, "breakout": True, "macd": False,
            "rsi": False, "volume": False, "bb_squeeze": False,
        },
    },

    # MACD + breakout only (no ADX, no RSI)
    "donchian__both__macd_breakout": {
        **_base(),
        "long":  {**_base()["long"],  "adx": False, "rsi": False},
        "short": {**_base()["short"], "adx": False, "rsi": False},
    },

    # ADX + breakout only (no MACD, no RSI)
    "donchian__both__adx_breakout": {
        **_base(),
        "long":  {**_base()["long"],  "macd": False, "rsi": False},
        "short": {**_base()["short"], "macd": False, "rsi": False},
    },

    # ── ATR SENSITIVITY ──────────────────────────────────────
    # Tight SL/TP: more trades closed quickly, higher churn
    "donchian__both__atr_1_5": {
        **_base(),
        "thresholds": {**_base()["thresholds"], "atr_mult": 1.5},
    },

    # Default (atr_mult=3 already in DEFAULT_CONDITIONS)
    "donchian__both__atr_3": _base(),

    # Wide SL/TP: fewer but potentially larger wins
    "donchian__both__atr_5": {
        **_base(),
        "thresholds": {**_base()["thresholds"], "atr_mult": 5},
    },

    # ── ADX THRESHOLD SENSITIVITY ────────────────────────────
    # More selective: only strong trends
    "donchian__both__adx_20": {
        **_base(),
        "thresholds": {**_base()["thresholds"], "adx": 20},
    },

    # Less selective: catch earlier trend starts
    "donchian__both__adx_10": {
        **_base(),
        "thresholds": {**_base()["thresholds"], "adx": 10},
    },

    # ── RSI THRESHOLD SENSITIVITY ────────────────────────────
    # Tighter RSI window (avoids overbought/oversold more strictly)
    "donchian__both__rsi_40_70": {
        **_base(),
        "thresholds": {**_base()["thresholds"], "rsi_min": 40, "rsi_max": 70},
    },

    # Wider RSI window (more permissive)
    "donchian__both__rsi_20_85": {
        **_base(),
        "thresholds": {**_base()["thresholds"], "rsi_min": 20, "rsi_max": 85},
    },
}


# ============================================================
# DATE RANGES TO EVALUATE
# ============================================================
# Keys are used as the "period" label in evaluation results.
# Format: (start_date, end_date) as ISO strings.
# ============================================================

DATE_RANGES: dict[str, tuple[str, str]] = {
    # ── Años individuales ──
    "2020": ("2020-01-01", "2020-07-01"),
    "2021": ("2021-01-01", "2021-06-01"),
    "2022": ("2022-01-01", "2022-07-01"),
    "2023": ("2023-01-01", "2023-05-01"),
    "2024": ("2024-01-01", "2024-06-01"),
    "2025": ("2025-01-01", "2025-07-01"),
    "2026": ("2026-01-01", "2026-12-31"),
    # ── Periodos completos ──
    "full": ("2020-01-01", "2025-12-31")
}


DATE_RANGES_2017: dict[str, tuple[str, str]] = {
    # ── Años individuales ──
    "2017": ("2017-01-01", "2017-08-01"),
    "2018": ("2018-01-01", "2018-04-01"),
    "2019": ("2019-01-01", "2019-05-01"),
    "2020": ("2020-01-01", "2020-07-01"),
    "2021": ("2021-01-01", "2021-06-01"),
    "2022": ("2022-01-01", "2022-07-01"),
    "2023": ("2023-01-01", "2023-05-01"),
    "2024": ("2024-01-01", "2024-06-01"),
    "2025": ("2025-01-01", "2025-07-01"),
    "2026": ("2026-01-01", "2026-12-31"),
    # ── Periodos completos ──
    "full": ("2017-01-01", "2025-12-31"),
    "full_2017_2021": ("2017-01-01", "2021-12-31"),  # Pre-pandemia + COVID
    "full_2020_2025": ("2020-01-01", "2025-12-31"),  # Pandemia en adelante
}


DATE_RANGES_JULIO: dict[str, tuple[str, str]] = {
    # ── Años individuales ──
    "2017": ("2017-01-01", "2017-12-31"),
    "2018": ("2018-04-01", "2018-12-31"),
    "2019": ("2019-05-01", "2019-12-31"),
    "2020": ("2020-07-01", "2020-12-31"),
    "2021": ("2021-06-01", "2021-12-31"),
    "2022": ("2022-07-01", "2022-12-31"),
    "2023": ("2023-05-01", "2023-12-31"),
    "2024": ("2024-06-01", "2024-12-31"),
    "2025": ("2025-07-01", "2025-12-31"),
    "2026": ("2026-01-01", "2026-12-31"),
    # ── Periodos completos ──
    "full": ("2017-01-01", "2025-12-31"),
    "full_2017_2021": ("2017-01-01", "2021-12-31"),  # Pre-pandemia + COVID
    "full_2020_2025": ("2020-01-01", "2025-12-31"),  # Pandemia en adelante
}

DATE_RANGES77: dict[str, tuple[str, str]] = {
    # ── Años individuales ──
    "2017": ("2017-01-01", "2017-12-31"),
    "2018": ("2018-01-01", "2018-12-31"),
    "2019": ("2019-01-01", "2019-12-31"),
    "2020": ("2020-01-01", "2020-12-31"),
    "2021": ("2021-01-01", "2021-12-31"),
    "2022": ("2022-01-01", "2022-12-31"),
    "2023": ("2023-01-01", "2023-12-31"),
    "2024": ("2024-01-01", "2024-12-31"),
    "2025": ("2025-01-01", "2025-12-31"),
    "2026": ("2026-01-01", "2026-12-31"),
    # ── Periodos completos ──
    "full": ("2017-01-01", "2025-12-31"),
    "full_2017_2021": ("2017-01-01", "2021-12-31"),  # Pre-pandemia + COVID
    "full_2020_2025": ("2020-01-01", "2025-12-31"),  # Pandemia en adelante
}
