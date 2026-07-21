
from rich.console import Console
from rich.panel import Panel
from prompt_toolkit import PromptSession
import plotext as plt
import yfinance as yf
from rich.table import Table
import asyncio

import asyncio
import sys

from plottext.ui.screens.terminal_screens import home_screen, keep_purged_stocks_screen, run_strategy_of_day_screen

# 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-kb
    
# ========================
# LOOP PRINCIPAL
# ========================
async def main_async():
    while True:
        opcion = await home_screen()
        if opcion == "1":
            await keep_purged_stocks_screen() 
        elif opcion == "2":
            await run_strategy_of_day_screen()
        elif opcion == "3":
            sys.exit(0)

def main():
    """Wrapper sincrónico para el entry point"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario")
        sys.exit(0)

if __name__ == "__main__":
    main()
