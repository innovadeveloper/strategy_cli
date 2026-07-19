```py

# velas japonesas

import plotext as plt
import yfinance as yf

df = yf.download("AAPL", period="2mo", interval="1d")

# FIX MultiIndex si existe
if hasattr(df.columns, "levels"):
    try:
        df.columns = df.columns.droplevel(1)
    except:
        pass

data = {col: df[col].tolist() for col in ["Open", "High", "Low", "Close"]}
x = [d.strftime("%d/%m/%Y") for d in df.index]

def main():
    plt.theme("dark")  # opcional 🔥
    plt.plotsize(120, 30)

    plt.candlestick(x, data)
    plt.title("AAPL Candlestick")
    
    plt.show()

if __name__ == "__main__":
    main()


```

```py
from rich.console import Console
from rich.panel import Panel
from prompt_toolkit import prompt

console = Console()

def pantalla_inicio():
    console.clear()
    console.print(Panel("📊 Sistema de Trading", title="Inicio"))

    console.print("1. Ver datos")
    console.print("2. Ingresar símbolo")
    console.print("3. Salir")

    opcion = prompt("Selecciona opción: ")
    return opcion


def pantalla_input():
    console.clear()
    symbol = prompt("Ingresa símbolo (ej: AAPL): ")
    console.print(f"Elegiste: {symbol}")
    input("Enter para volver...")


def main():
    while True:
        opcion = pantalla_inicio()

        if opcion == "1":
            console.print("Mostrando datos...")
            input("Enter para volver...")

        elif opcion == "2":
            pantalla_input()

        elif opcion == "3":
            break

if __name__ == "__main__":
    main()
```


```py
from rich.console import Console
from rich.panel import Panel
from prompt_toolkit import prompt
import plotext as plt
import yfinance as yf


from rich.table import Table

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
# 🏠 MENU
# ========================
def pantalla_inicio():
    console.clear()
    console.print(Panel("📊 Sistema de Trading", title="Inicio"))

    console.print("1. Ver datos (tabla)")
    console.print("2. Ingresar símbolo")
    console.print("3. Ver gráfico 📈")
    console.print("4. Salir")

    opcion = prompt("Selecciona opción: ")
    return opcion

# ========================
# 🔁 LOOP PRINCIPAL
# ========================
def main():
    while True:
        opcion = pantalla_inicio()

        if opcion == "1":
            pantalla_dataframe()   # 👈 NUEVO

        elif opcion == "2":
            pantalla_input()

        elif opcion == "3":
            pantalla_grafico()

        elif opcion == "4":
            break


if __name__ == "__main__":
    main()
```

```py
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.progress import Progress
from rich.layout import Layout
from rich.columns import Columns
from rich.align import Align
from rich.text import Text
from rich import box
import time

console = Console()

# ========================
# 🎨 TEXTO ESTILIZADO
# ========================
console.print("\n[bold magenta]Rich Demo UI[/bold magenta]\n")

text = Text("Sistema de Trading", style="bold white on blue")
console.print(text)


# ========================
# 📦 PANEL
# ========================
panel = Panel(
    "Bienvenido al sistema\nSelecciona una opción",
    title="Inicio",
    border_style="green"
)
console.print(panel)


# ========================
# 📊 TABLA
# ========================
table = Table(title="Mercado", box=box.ROUNDED)

table.add_column("Símbolo", style="cyan")
table.add_column("Precio", justify="right")
table.add_column("Cambio", justify="right")

table.add_row("AAPL", "190.45", "+1.2%")
table.add_row("BTC", "65,000", "-0.5%")
table.add_row("ETH", "3,200", "+2.1%")

console.print(table)


# ========================
# 🌳 TREE (estructura jerárquica)
# ========================
tree = Tree("📁 Proyecto")
tree.add("📄 main.py")
tree.add("📁 utils").add("📄 helpers.py")
tree.add("📁 data").add("📄 dataset.csv")

console.print(tree)


# ========================
# 📐 COLUMNS
# ========================
col1 = Panel("Panel 1", style="red")
col2 = Panel("Panel 2", style="green")
col3 = Panel("Panel 3", style="blue")

console.print(Columns([col1, col2, col3]))


# ========================
# 📏 ALIGN
# ========================
console.print(Align.center("Texto centrado", vertical="middle"))


# ========================
# 📊 PROGRESS BAR
# ========================
with Progress() as progress:
    task = progress.add_task("[green]Cargando...", total=100)

    for i in range(100):
        time.sleep(0.02)
        progress.update(task, advance=1)


# ========================
# 🌀 SPINNER / STATUS
# ========================
with console.status("[bold yellow]Procesando..."):
    time.sleep(2)


# ========================
# 🧱 LAYOUT (pantalla dividida)
# ========================
layout = Layout()

layout.split(
    Layout(name="header", size=3),
    Layout(name="body"),
    Layout(name="footer", size=3)
)

layout["header"].update(Panel("HEADER"))
layout["body"].update(Panel("Contenido principal"))
layout["footer"].update(Panel("FOOTER"))

console.print(layout)


# ========================
# 🔴 LIVE (actualización en tiempo real)
# ========================
from rich.live import Live

table_live = Table()
table_live.add_column("Tiempo")
table_live.add_column("Valor")

with Live(table_live, refresh_per_second=2):
    for i in range(5):
        table_live.add_row(str(i), str(i * 10))
        time.sleep(1)
```

```py
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

# Lista en memoria
simbolos = ["AAPL", "MSFT", "GOOGL", "BTC-USD", "ETH-USD", "NFLX", "AAPL-EURO", "BTC-EURO"]

completer = WordCompleter(
    simbolos,
    ignore_case=True,     # no importa mayúsculas
    match_middle=True     # permite match parcial
)

symbol = prompt("Símbolo: ", completer=completer)

print(f"Elegiste: {symbol}")
```