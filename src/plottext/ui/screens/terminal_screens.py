
from rich.console import Console
from rich.panel import Panel
from prompt_toolkit import prompt
from datetime import datetime

from rich.table import Table
import yfinance as yf

import asyncio
from py_shared_library.infrastructure.async_file_lock import async_limiter, async_file_lock
from plottext.infrastructure.service.yh_service import download_real_data, get_nasdaq100_data_async, KEEP_PURGED_DATA, filter_nasdaq100_data
from plottext.ui.extensions.df_extensions import dfs_from_dict
from plottext.ui.extensions.rich_extensions import df_to_table_ritch, two_panels_ritch
from plottext.infrastructure.service.backtest_runner import run_backtest_all_tickers_current_day_async
from plottext.infrastructure.service.config import CONFIGS, DATE_RANGES




console = Console()

# ========================
# home_screen
# ========================
async def home_screen():
    console.clear()
    console.print(Panel("TradingExecutor", title="CLI"))

    console.print("1. View stocks (Keep/Purged)")
    console.print("2. Run strategy of day")
    console.print("3. Run backtesting")
    console.print("4. Download stockfiles")
    console.print("5. Load configfiles")
    console.print("6. Exit program")

    option = prompt("Select option: ")
    return option


# async def fetch_data(symbol):
#     # df = yf.download("AAPL", period="2mo", interval="1d")
#     return await asyncio.to_thread(
#         yf.download,
#         symbol,
#         period="2mo",
#         interval="1d"
#     )



# ========================
# keep_purged_stocks_screen
# ========================
async def keep_purged_stocks_screen():
    """
    Vista KEEP/PURGE de stocks
    """
    console.clear()
    keep_df, purge_df = dfs_from_dict(KEEP_PURGED_DATA) # change by file or rest api..
    keep_table = df_to_table_ritch(keep_df)
    purge_table = df_to_table_ritch(purge_df)

    data = list(map(lambda idx, table :  Panel(table, 
                        title="KEEP" if (idx %2 == 0) else "PURGE",
                        border_style="green" if (idx %2 == 0) else "red",
                        expand=False) , 
                        range(len([keep_table, purge_table])), 
                        [keep_table, purge_table]))
    
    # Mostrar lado a lado con Group
    from rich import print
    from rich.columns import Columns
    
    # Usar Columns para mostrar lado a lado
    print(Panel(
        Columns(data, equal=False, expand=False),
        title="ANÁLISIS DE SÍMBOLOS",
        border_style="bright_blue",
        expand=False
    ))

    input("\nEnter para volver...")



# ========================
# run_strategy_of_day_screen
# ========================
async def run_strategy_of_day_screen():
    """
    Vista KEEP/PURGE de stocks
    """
    console.clear()

    current_date = datetime.now().strftime("%Y-%m-%d")
    investment_amount = input("\nIngresa monto a invertir en USD (Ej 200)[Default : 200]  : ") or "200"
    day_operation_revision = input(f"\nIngresa fecha de sondeo de señales (Ej YY-m-d) [Default : {current_date}] : ") or current_date
    # day_operation_revision = "2026-07-17"

    investment_amount = float(investment_amount)

    with console.status("[bold green]Descargando datos..."):
        data_nasdaq100 = await get_nasdaq100_data_async(period="1y", interval="1d", force_download=False, max_age_days=1)
    # data_nasdaq100 = get_nasdaq100_data_async(period="1y", interval="1d", force_download=False, max_age_days=1)
    data_nasdaq100_by_date = filter_nasdaq100_data(data_nasdaq100_dict=data_nasdaq100, start_date="2026-01-01", end_date=day_operation_revision)

    with console.status("[bold green]Ejecutando estrategia por día..."):
        stocks_df = await run_backtest_all_tickers_current_day_async(data_nasdaq100_by_date, conditions=CONFIGS["bollinger__long__full"], investment_amount=investment_amount)
    stocks_df = stocks_df[stocks_df["tipo"] != "NINGUNA"]

    signal_table = df_to_table_ritch(stocks_df[["ticker", "date", "entry_price", "sl", "tp", "sl_amount", "tp_amount", "resistance_type"]])
    console.print(signal_table)
    # console.print(table)

    input("\nEnter para volver...")

