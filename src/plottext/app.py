
from rich.console import Console
from rich.panel import Panel
from prompt_toolkit import PromptSession
import plotext as plt
import yfinance as yf
from rich.table import Table
import asyncio

from plottext.ui.screens.terminal_screens import home_screen, keep_purged_stocks_screen, run_strategy_of_day_screen


# ========================
# 🔁 LOOP PRINCIPAL
# ========================
async def main():
    while True:
        opcion = await home_screen()

        if opcion == "1":
            await keep_purged_stocks_screen() 

        elif opcion == "2":
            await run_strategy_of_day_screen()

if __name__ == "__main__":
    asyncio.run(main())

    # Crear los DataFrames
    # df_keep, df_purge = create_dataframes_from_dict(data)

    # # Mostrar lado a lado (sin límite)
    # show_dfs_side_by_side(df_keep, df_purge)