
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

import ctypes, sys, os

# Nombre de librería según SO
lib_name = 'libmilib.dll' if sys.platform.startswith('win') else 'libmilib.dylib' if sys.platform.startswith('darwin') else 'libmilib.so'

# lib_path = '/Users/mac/Documents/Projects/PythonProjects/strategy_cli/assets/c_language/libmilib.dylib'

# Cargar librería
try:
    # sys.executable => retorna el path del ejecutable si es un binario, o el path del intérprete si es un script
    # getattr(sys, 'frozen', False) => retorna True si es un binario, False si es un script
    # os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__) => retorna el directorio del ejecutable si es un binario, o el directorio del script si es un script
    lib = ctypes.CDLL(os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), lib_name))
except:
    lib = ctypes.CDLL(lib_name)

# Configurar funciones
lib.suma.argtypes = [ctypes.c_int, ctypes.c_int]
lib.suma.restype = ctypes.c_int
lib.version.restype = ctypes.c_char_p

# Probar
print(f"Versión: {lib.version().decode()}")
print(f"10 + 5 = {lib.suma(10, 5)}")
input("Presiona Enter para salir...")


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
    print("Iniciando la aplicación...")
    # pass
    # main()
