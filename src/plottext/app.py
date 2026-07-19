
from rich.console import Console
from rich.panel import Panel
from prompt_toolkit import prompt
import plotext as plt
import yfinance as yf
from rich.table import Table
import asyncio

from plottext.ui.screens.terminal_screens import home_screen, keep_purged_stocks_screen, run_strategy_of_day_screen


console = Console()

def pantalla_dataframe():
    console.clear()
    console.print(Panel("📊 DataFrame (AAPL)", title="Datos"))

    df = yf.download("AAPL", period="2mo", interval="1d")

    # Fix MultiIndex
    if hasattr(df.columns, "levels"):
        try:
            df.columns = df.columns.droplevel(1)
        except:
            pass

    table = Table(show_header=True, header_style="bold magenta")

    # Columnas
    table.add_column("Fecha")
    for col in df.columns:
        table.add_column(col)

    # Filas (puedes limitar para no saturar)
    for i, (idx, row) in enumerate(df.iterrows()):
        if i >= 15:  # 👈 limita filas
            break

        table.add_row(
            idx.strftime("%d/%m/%Y"),
            *[f"{v:.2f}" for v in row]
        )

    console.print(table)

    input("\nEnter para volver...")
    
# ========================
# 📊 GRAFICO CANDLESTICK
# ========================
def pantalla_grafico():
    console.clear()
    
    symbol = prompt("Ingresa símbolo (ej: AAPL): ")
    
    console.print(Panel(f"Gráfico de Velas {symbol}", title="Trading"))

    df = yf.download(symbol, period="2mo", interval="1d")

    # Fix MultiIndex (por si acaso)
    if hasattr(df.columns, "levels"):
        try:
            df.columns = df.columns.droplevel(1)
        except:
            pass

    data = {col: df[col].tolist() for col in ["Open", "High", "Low", "Close"]}
    x = [d.strftime("%d/%m/%Y") for d in df.index]

    plt.clear_data()
    plt.clear_figure()

    plt.theme("dark")
    plt.plotsize(120, 30)

    plt.candlestick(x, data)
    plt.title(f"{symbol} Candlestick")

    plt.show()

    input("\nEnter para volver al menú...")


# ========================
# 🧾 INPUT
# ========================
def pantalla_input():
    console.clear()
    symbol = prompt("Ingresa símbolo (ej: AAPL): ")
    console.print(f"Elegiste: {symbol}")
    input("Enter para volver...")
    return symbol


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