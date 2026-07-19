import pandas as pd
from backtesting import Backtest
import asyncio


from plottext.infrastructure.service.indicators import (
    add_indicators,
    add_donchian_both,
    detect_breakout_events,
    detect_breakdown_events,
    bbands_width,
    adx,
    resistance,
    support,
    vol_ratio,
    macd_hist,
    rsi,
    atr,
    bollinger_breakout,
)

from plottext.infrastructure.service.strategy import (
    EightStepStrategy,
    DEFAULT_CONDITIONS,
)


# ============================================================
# DATA PREPARATION
# ============================================================

# ============================================================
# DATA PREPARATION
# ============================================================

def prepare_donchian_data(data_dict, indicators=True, dropna=True):
    result = {}

    for ticker, df in data_dict.items():
        if indicators:
            df_with_indicators = add_indicators(df)
        else:
            df_with_indicators = df.copy()

        df_donchian = add_donchian_both(df_with_indicators)

        if dropna:
            df_donchian = df_donchian.dropna()

        result[ticker] = df_donchian

    print(f"Data prepared for {len(result)} tickers")

    return result


def process_stats(ticker, ns_df):
    current_df = add_donchian_both(ns_df, donchian_n=20)
    breakdown_events = detect_breakdown_events(current_df, min_gap_days=15)
    breakout_events = detect_breakout_events(current_df, min_gap_days=15)
    return {"ticker": ticker, "breakdown_events": breakdown_events, "breakout_events": breakout_events}


def reorder_columns(df, columns_first):
    if isinstance(columns_first, str):
        columns_first = [columns_first]

    valid_cols = [col for col in columns_first if col in df.columns]
    remaining = [col for col in df.columns if col not in valid_cols]
    return df[valid_cols + remaining]


# ============================================================
# BACKTEST — FULL HISTORY (run_backtest_v4)
# ============================================================

def run_backtest_v4(ohlc_df, cash_amount=1_000, commission_amount=0.001, conditions=None):
    """
    Runs backtest for all tickers. All strategy config (Bollinger, thresholds,
    enable_long, enable_short) is controlled via the `conditions` dict.

    Example — Bollinger-only LONG:
        from wg_tool_cli.backtest.strategy import DEFAULT_CONDITIONS
        import copy
        cond = copy.deepcopy(DEFAULT_CONDITIONS)
        cond["bollinger"]["use_bollinger"] = True
        cond["enable_short"] = False
        results = run_backtest_v4(data, conditions=cond)
    """
    import copy
    if conditions is None:
        conditions = copy.deepcopy(DEFAULT_CONDITIONS)

    use_bollinger = conditions.get("bollinger", {}).get("use_bollinger", False)
    strategy_label = "Bollinger" if use_bollinger else "Donchian"

    result_list = []

    for ticker, df in ohlc_df.items():
        try:
            if len(df) < 50:
                print(f"{ticker}: Insufficient data ({len(df)} bars), skipping...")
                continue

            required_cols = ["Open", "High", "Low", "Close", "Volume"]
            if not all(col in df.columns for col in required_cols):
                print(f"{ticker}: Missing columns, skipping...")
                continue

            current_df = df[required_cols].copy().dropna(subset=required_cols)

            if len(current_df) < 50:
                print(f"{ticker}: Insufficient data after cleaning ({len(current_df)} bars), skipping...")
                continue

            captured_conditions = conditions

            class DynamicStrategy(EightStepStrategy):
                def __init__(self, broker, data, params=None):
                    if params is None:
                        params = {}
                    params["conditions"] = captured_conditions
                    super().__init__(broker, data, params)

            DynamicStrategy.__name__ = f"Strategy_{strategy_label}_{ticker}"

            bt = Backtest(current_df, DynamicStrategy, cash=cash_amount, commission=commission_amount)
            stats = bt.run()

            trades = stats['_trades']

            if not trades.empty:
                trades_long = trades[trades["Size"] > 0]
                trades_short = trades[trades["Size"] < 0]
                n_trades_long = len(trades_long)
                n_trades_short = len(trades_short)
                n_trades_total = len(trades)
                win_rate_long = (len(trades_long[trades_long["PnL"] > 0]) / n_trades_long * 100) if n_trades_long > 0 else 0
                win_rate_short = (len(trades_short[trades_short["PnL"] > 0]) / n_trades_short * 100) if n_trades_short > 0 else 0
                pnl_long = trades_long["PnL"].sum() if not trades_long.empty else 0
                pnl_short = trades_short["PnL"].sum() if not trades_short.empty else 0
                pnl_total = trades["PnL"].sum()
                avg_pnl_long = trades_long["PnL"].mean() if n_trades_long > 0 else 0
                avg_pnl_short = trades_short["PnL"].mean() if n_trades_short > 0 else 0
            else:
                n_trades_long = n_trades_short = n_trades_total = 0
                win_rate_long = win_rate_short = 0
                pnl_long = pnl_short = pnl_total = 0
                avg_pnl_long = avg_pnl_short = 0

            result_list.append({
                "Ticker": ticker,
                "Strategy": strategy_label,
                "Start": stats["Start"],
                "End": stats["End"],
                "Duration (days)": (stats["End"] - stats["Start"]).days,
                "Equity Final [$]": stats["Equity Final [$]"],
                "Equity Peak [$]": stats["Equity Peak [$]"],
                "Return [%]": stats["Return [%]"],
                "# Trades": n_trades_total,
                "Win Rate [%]": stats["Win Rate [%]"],
                "# LONG": n_trades_long,
                "Win Rate LONG [%]": win_rate_long,
                "PnL LONG [$]": pnl_long,
                "Avg PnL LONG [$]": avg_pnl_long,
                "# SHORT": n_trades_short,
                "Win Rate SHORT [%]": win_rate_short,
                "PnL SHORT [$]": pnl_short,
                "Avg PnL SHORT [$]": avg_pnl_short,
                "PnL Total [$]": pnl_total,
                "trades": trades,
            })

            print(f"{ticker}: {n_trades_total} trades | Win Rate: {stats['Win Rate [%]']:.1f}% | Return: {stats['Return [%]']:.1f}%")
            if n_trades_long > 0 or n_trades_short > 0:
                print(f"   LONG: {n_trades_long} | SHORT: {n_trades_short}")

        except Exception as e:
            print(f"Error in {ticker}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue

    return result_list


# ============================================================
# BACKTEST — CURRENT DAY SIGNALS (run_backtest_all_tickers_current_day)
# ============================================================

def _signal_age_bars(close: pd.Series, resistance_line: pd.Series) -> int:
    """
    Returns how many consecutive bars (counting back from the last)
    the Close has been above resistance_line.
    0 means it crossed TODAY (fresh breakout).
    1 means it crossed yesterday and is still above today.
    -1 means it is NOT above resistance right now.
    """
    above = close > resistance_line
    if not above.iloc[-1]:
        return -1
    count = 0
    for i in range(len(above) - 1, -1, -1):
        if above.iloc[i]:
            count += 1
        else:
            break
    return count - 1


def _signal_age_bars_short(close: pd.Series, support_line: pd.Series) -> int:
    """Same as _signal_age_bars but for SHORT (close < support)."""
    below = close < support_line
    if not below.iloc[-1]:
        return -1
    count = 0
    for i in range(len(below) - 1, -1, -1):
        if below.iloc[i]:
            count += 1
        else:
            break
    return count - 1


def run_backtest_all_tickers_current_day(data_dict, conditions=None, 
                                         investment_amount=1000,
                                         instrument_type='stock'):
    """
    Evaluates the last bar of each ticker for LONG/SHORT signals.
    All config is driven by `conditions` (same dict as run_backtest_v4).
    
    Signal freshness (options 2 + 3):
    ----------------------------------
    conditions["thresholds"]["max_signal_age_bars"] controls how many bars
    AFTER the actual breakout bar the signal is still considered valid.
    
        0  → only accept the exact breakout bar (mirrors backtest perfectly)
        1  → accept today + 1 bar after breakout
        3  → accept up to 3 bars after breakout (default — small tolerance)
       99  → disabled (legacy behaviour, any bar above resistance is valid)
    
    Additionally, "breakout_fresh" logic (option 2) always checks that
    yesterday the price was BELOW the resistance and today it crossed above.
    When max_signal_age_bars > 0 this is relaxed to the age window.
    
    Added attributes:
    ------------------
    - sl_amount: Stop Loss amount in USD (monetary value)
    - tp_amount: Take Profit amount in USD (monetary value)
    - units: Number of shares/contracts
    - risk_reward_ratio: TP/SL ratio
    
    Example — Bollinger SHORT-only, fresh signals only:
        import copy
        cond = copy.deepcopy(DEFAULT_CONDITIONS)
        cond["bollinger"]["use_bollinger"] = True
        cond["enable_long"] = False
        cond["thresholds"]["rsi_max"] = 70
        cond["thresholds"]["max_signal_age_bars"] = 0   # exact bar only
        df = run_backtest_all_tickers_current_day(data, conditions=cond, 
                                                  investment_amount=5000)
    """
    import copy
    if conditions is None:
        conditions = copy.deepcopy(DEFAULT_CONDITIONS)
    
    cond_long = conditions.get("long", {})
    cond_short = conditions.get("short", {})
    thresholds = conditions.get("thresholds", {})
    bollinger_cfg = conditions.get("bollinger", {})
    
    adx_threshold_local  = thresholds.get("adx", 14)
    rsi_min_local        = thresholds.get("rsi_min", 30)
    rsi_max_local        = thresholds.get("rsi_max", 78)
    vol_threshold        = thresholds.get("volume", 1.5)
    bb_squeeze_threshold = thresholds.get("bb_squeeze", 0.04)
    atr_mult             = thresholds.get("atr_mult", 3)
    max_signal_age       = thresholds.get("max_signal_age_bars", 3)
    
    use_bollinger = bollinger_cfg.get("use_bollinger", False)
    bb_length = bollinger_cfg.get("bb_length", 20)
    bb_std = bollinger_cfg.get("bb_std", 2)
    
    enable_long = conditions.get("enable_long", True)
    enable_short = conditions.get("enable_short", True)
    
    use_volume_long = cond_long.get("volume", False)
    use_volume_short = cond_short.get("volume", False)
    
    results = []
    
    for ticker, df_raw in data_dict.items():
        df = df_raw[["Open", "High", "Low", "Close", "Volume"]].dropna().copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if len(df) < 30:
            continue
        
        bbw = bbands_width(df["Close"])
        adx_ = adx(df["High"], df["Low"], df["Close"])
        volr = vol_ratio(df["Volume"])
        hist = macd_hist(df["Close"])
        rsi_ = rsi(df["Close"])
        atr_ = atr(df["High"], df["Low"], df["Close"])
        
        if use_bollinger:
            _, upper_band, lower_band = bollinger_breakout(
                df["Close"], length=bb_length, num_std=bb_std
            )
            resistance_line = upper_band
            support_line = lower_band
            resistance_type = "Bollinger"
        else:
            resistance_line = resistance(df["High"])
            support_line = support(df["Low"])
            resistance_type = "Donchian"
        
        if pd.isna(adx_.iloc[-1]) or pd.isna(hist.iloc[-1]) or pd.isna(atr_.iloc[-1]):
            continue
        
        price = df["Close"].iloc[-1]
        idx = -1
        
        adx_ok = adx_.iloc[idx] > adx_threshold_local and adx_.iloc[idx] > adx_.iloc[idx - 1]
        rsi_ok = rsi_min_local < rsi_.iloc[idx] < rsi_max_local
        volume_ok = volr.iloc[idx] > vol_threshold
        squeeze_ok = min(bbw[-10:]) < bb_squeeze_threshold
        
        # ── Signal freshness (options 2 + 3) ──────────────────
        age_long  = _signal_age_bars(df["Close"], resistance_line)
        age_short = _signal_age_bars_short(df["Close"], support_line)
        
        # Option 2: price must have crossed resistance TODAY (age == 0)
        # Option 3: relax to max_signal_age bars after crossing
        # age == -1 means not above resistance at all → no signal
        breakout_up_raw   = price > resistance_line.iloc[idx]
        breakout_up_fresh = (age_long  >= 0) and (age_long  <= max_signal_age)
        breakout_up       = breakout_up_raw and breakout_up_fresh
        
        macd_up = hist.iloc[idx] > 0 and hist.iloc[idx] > hist.iloc[idx - 1]
        
        long_conditions = []
        if cond_long.get("adx", True):
            long_conditions.append(adx_ok)
        if cond_long.get("breakout", True):
            long_conditions.append(breakout_up)
        if cond_long.get("macd", True):
            long_conditions.append(macd_up)
        if cond_long.get("rsi", True):
            long_conditions.append(rsi_ok)
        if use_volume_long:
            long_conditions.append(volume_ok)
        if cond_long.get("bb_squeeze", False):
            long_conditions.append(squeeze_ok)
        
        has_signal_long = enable_long and (all(long_conditions) if long_conditions else False)
        
        breakout_down_raw   = price < support_line.iloc[idx]
        breakout_down_fresh = (age_short >= 0) and (age_short <= max_signal_age)
        breakout_down       = breakout_down_raw and breakout_down_fresh
        
        macd_down = hist.iloc[idx] < 0 and hist.iloc[idx] < hist.iloc[idx - 1]
        
        short_conditions = []
        if cond_short.get("adx", True):
            short_conditions.append(adx_ok)
        if cond_short.get("breakout", True):
            short_conditions.append(breakout_down)
        if cond_short.get("macd", True):
            short_conditions.append(macd_down)
        if cond_short.get("rsi", True):
            short_conditions.append(rsi_ok)
        if use_volume_short:
            short_conditions.append(volume_ok)
        if cond_short.get("bb_squeeze", False):
            short_conditions.append(squeeze_ok)
        
        has_signal_short = enable_short and (all(short_conditions) if short_conditions else False)
        
        # Initialize row_data with basic info
        row_data = {
            "ticker": ticker,
            "date": df.index[-1],
            "tipo": "LONG" if has_signal_long else ("SHORT" if has_signal_short else "NINGUNA"),
            "entry_price": None,
            "sl": None,
            "tp": None,
            "sl_amount": None,
            "tp_amount": None,
            "units": None,
            "risk_reward_ratio": None,
            "resistance_type": resistance_type,
            "signal_age_bars": age_long if has_signal_long else (age_short if has_signal_short else None),
            "max_signal_age": max_signal_age,
            "adx": float(adx_.iloc[idx]),
            "rsi": float(rsi_.iloc[idx]),
            "volume_ratio": float(volr.iloc[idx]),
            "macd_hist": float(hist.iloc[idx]),
            "squeeze": float(bbw.iloc[idx]),
            "cond_adx": adx_ok,
            "cond_breakout_up": breakout_up,
            "cond_breakout_down": breakout_down,
            "cond_macd_up": macd_up,
            "cond_macd_down": macd_down,
            "cond_rsi": rsi_ok,
            "cond_volume": volume_ok,
            "cond_squeeze": squeeze_ok,
        }
        
        if has_signal_long or has_signal_short:
            risk = atr_mult * atr_.iloc[idx]
            row_data["entry_price"] = float(price)
            
            if has_signal_long:
                sl_price = price - risk
                tp_price = price + risk
                row_data["sl"] = float(sl_price)
                row_data["tp"] = float(tp_price)
                row_data["potential_gain"] = float(risk)
                
                # Calculate monetary amounts for LONG position
                amounts = _calculate_sl_tp_amounts(
                    entry_price=price,
                    sl_price=sl_price,
                    tp_price=tp_price,
                    investment_amount=investment_amount,
                    instrument_type=instrument_type
                )
                row_data["sl_amount"] = amounts['sl_amount']
                row_data["tp_amount"] = amounts['tp_amount']
                row_data["units"] = amounts['units']
                row_data["risk_reward_ratio"] = amounts['risk_reward_ratio']
                
            else:  # SHORT
                sl_price = price + risk
                tp_price = price - risk
                row_data["sl"] = float(sl_price)
                row_data["tp"] = float(tp_price)
                row_data["potential_gain"] = float(risk)
                
                # Calculate monetary amounts for SHORT position
                amounts = _calculate_sl_tp_amounts(
                    entry_price=price,
                    sl_price=sl_price,
                    tp_price=tp_price,
                    investment_amount=investment_amount,
                    instrument_type=instrument_type,
                    is_short=True
                )
                row_data["sl_amount"] = amounts['sl_amount']
                row_data["tp_amount"] = amounts['tp_amount']
                row_data["units"] = amounts['units']
                row_data["risk_reward_ratio"] = amounts['risk_reward_ratio']
        
        results.append(row_data)
    
    return pd.DataFrame(results)


def _calculate_sl_tp_amounts(entry_price, sl_price, tp_price, investment_amount, 
                            instrument_type='stock', is_short=False):
    """
    Calculates SL and TP in monetary amounts (USD) for brokers like etoro.
    
    Parameters:
    -----------
    entry_price : float
        Entry price of the position
    sl_price : float
        Stop loss price
    tp_price : float
        Take profit price
    investment_amount : float
        Amount to invest in account currency (USD)
    instrument_type : str
        'stock', 'forex', 'crypto', 'cfd' (default: 'stock')
    is_short : bool
        True if position is SHORT, False if LONG
    
    Returns:
    --------
    dict with sl_amount, tp_amount, units, and risk_reward_ratio
    """
    # For stocks, CFDs on stocks, and crypto (standard assets)
    if instrument_type in ['stock', 'crypto', 'cfd']:
        # Calculate number of shares/units
        units = investment_amount / entry_price
        
        # For LONG: SL is below entry, TP is above entry
        # For SHORT: SL is above entry, TP is below entry
        if not is_short:
            sl_amount = units * abs(entry_price - sl_price)
            tp_amount = units * abs(tp_price - entry_price)
        else:
            sl_amount = units * abs(sl_price - entry_price)
            tp_amount = units * abs(entry_price - tp_price)
    
    elif instrument_type == 'forex':
        # For forex pairs (1 standard lot = 100,000 units)
        lot_size = investment_amount / (entry_price * 100000)
        units = lot_size * 100000
        
        sl_amount = lot_size * 100000 * abs(entry_price - sl_price)
        tp_amount = lot_size * 100000 * abs(tp_price - entry_price)
    
    else:
        # Fallback: treat as stock
        units = investment_amount / entry_price
        sl_amount = units * abs(entry_price - sl_price)
        tp_amount = units * abs(tp_price - entry_price)
    
    # Calculate risk/reward ratio
    risk_reward_ratio = tp_amount / sl_amount if sl_amount > 0 else 0
    
    return {
        'sl_amount': round(sl_amount, 2),  # Round to 2 decimals (USD cents)
        'tp_amount': round(tp_amount, 2),
        'units': round(units, 2),  # Round to 2 decimals for shares
        'risk_reward_ratio': round(risk_reward_ratio, 2)
    }



# ============================================================
# STATS & REPORTING
# ============================================================

def show_summarized_stats(backtest_df):
    df_win = backtest_df["Win Rate [%]"] > 50
    df_loss = backtest_df["Win Rate [%]"] <= 50
    df_loss = backtest_df[df_loss].copy()
    df_win = backtest_df[df_win].copy()
    df_win["TYPE"] = "WIN"
    df_loss["TYPE"] = "LOSE"
    df_total = pd.concat([df_win, df_loss], ignore_index=True).round(2)
    df_total = df_total.drop(columns=["trades"])
    return df_total


def show_detailed_stats_v3(backtest_df, arguments=None, is_summarized=True):
    backtest_df_tmp = backtest_df.copy()
    mask = None
    trade_dict = {}

    if arguments is not None:
        if "win_rate_lower" in arguments:
            mask = backtest_df_tmp["Win Rate [%]"] <= arguments["win_rate_lower"]
        elif "win_rate_greater" in arguments:
            mask = backtest_df_tmp["Win Rate [%]"] >= arguments["win_rate_greater"]
        elif "tickers" in arguments:
            mask = backtest_df["Ticker"].isin(arguments["tickers"])

        if mask is not None:
            backtest_df_tmp = backtest_df_tmp[mask]

    for _, row in backtest_df_tmp.iterrows():
        ticker = row["Ticker"]
        trades = row["trades"]

        if trades is None or trades.empty:
            print(f"No trades for {ticker}")
            trade_dict[ticker] = pd.DataFrame()
            continue

        trades = trades.copy()
        trades["Capital"] = trades["Size"] * trades["EntryPrice"]

        all_trades = trades.copy()
        all_trades["Result"] = all_trades["PnL"].apply(lambda x: "WIN" if x > 0 else "LOSE")

        all_trades["Direction"] = all_trades["Size"].apply(
            lambda x: "LONG" if x > 0 else ("SHORT" if x < 0 else "NEUTRAL")
        )

        if is_summarized:
            n_cols = all_trades.shape[1]
            cols_to_select = [28, 29, 7, 0, 1, 2, 3, 4, 5, 6, 8, 10, 11, 12]

            direction_pos = None
            if "Direction" in all_trades.columns:
                direction_pos = all_trades.columns.get_loc("Direction")

            valid_cols = [i for i in cols_to_select if i < n_cols]

            if direction_pos is not None and direction_pos < n_cols:
                valid_cols.append(direction_pos)

            if valid_cols:
                all_trades = all_trades.iloc[:, valid_cols]
            else:
                print(f"Warning: {ticker} only has {n_cols} columns, cannot summarize")
                all_trades = pd.DataFrame()

        trade_dict[ticker] = all_trades

    return trade_dict



# data_dict, conditions=None
async def run_backtest_all_tickers_current_day_async(data_dict, conditions=None, 
                                         investment_amount=1000,
                                         instrument_type='stock'):
    return await asyncio.to_thread(
        run_backtest_all_tickers_current_day,
        data_dict=data_dict,
        conditions=conditions,
        investment_amount=investment_amount,
        instrument_type=instrument_type
    )
