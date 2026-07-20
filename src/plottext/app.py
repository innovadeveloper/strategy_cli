
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

from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

table = Table(title="Datos con colores", box=box.ROUNDED)
table.add_column("Ticker", style="cyan")
table.add_column("Precio", justify="right")
table.add_column("Cambio %", justify="right")
table.add_column("Estado", justify="center")

# Agregar filas con estilos específicos
table.add_row("AAPL", "$178.50", "+1.2%", "[green]▲ SUBE[/green]")
table.add_row("GOOGL", "$141.80", "-0.5%", "[red]▼ BAJA[/red]")
table.add_row("MSFT", "$378.90", "+0.8%", "[yellow]● ESTABLE[/yellow]")

# Toda la fila con un estilo
table.add_row("TSLA", "$245.30", "+5.2%", "🚀 SUBE", style="bold green")

console.print(table)

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

def main():
    """Wrapper sincrónico para el entry point"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario")
        sys.exit(0)

if __name__ == "__main__":
    main()
