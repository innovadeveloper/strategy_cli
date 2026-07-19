"""
Screener de señales (Donchian breakout/breakdown) sobre el universo Nasdaq-100.

Requiere: yfinance, pandas, numpy, pandas_ta (opcional, solo si usas add_indicators)
"""

import time
import numpy as np
import pandas as pd
import yfinance as yf
import logging
import asyncio

logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# =====================================================================
# 1. LISTA DE TICKERS DEL NASDAQ-100
# =====================================================================
# Fallback fijo por si Wikipedia cambia de formato o no hay internet en el
# momento de correr esto. No es necesariamente 100% actual -- siempre que
# haya internet, la función intenta primero traer la lista en vivo.
_NASDAQ100_FALLBACK = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "COST",
    "NFLX", "AMD", "PEP", "ADBE", "CSCO", "TMUS", "INTC", "QCOM", "AMGN", "INTU",
    "TXN", "CMCSA", "HON", "AMAT", "BKNG", "SBUX", "ISRG", "VRTX", "MDLZ", "GILD",
    "ADI", "REGN", "PANW", "LRCX", "PYPL", "MU", "SNPS", "CDNS", "KLAC", "MELI",
    "ASML", "CSX", "MAR", "ORLY", "PDD", "CTAS", "CRWD", "ABNB", "FTNT", "ADP",
    "NXPI", "WDAY", "ROP", "MNST", "PCAR", "CHTR", "MCHP", "AEP", "DXCM", "PAYX",
    "ODFL", "ROST", "KDP", "EXC", "IDXX", "CPRT", "FAST", "VRSK", "BIIB", "CTSH",
    "XEL", "EA", "CSGP", "GEHC", "DDOG", "TTD", "ON", "ZS", "TEAM",
    "FANG", "BKR", "GFS", "MRVL", "DASH", "CDW", "WBD", "ILMN", "LULU", "KHC",
    # CARTERA 2: Nasdaq + S&P 500 (diversificación EEUU)
    "JPM", "BAC", "V", "JNJ", "UNH", "PFE", "XOM", "CVX", "WMT", "PG", "MCD", "CAT", "GE", "KO", "HD",
    # # CARTERA 3: Nasdaq + S&P + Internacional (diversificación global)
    "NVO", "SAP", "BABA", "TSM", "TM",
]


def get_nasdaq100_tickers(use_live=True):
    """Devuelve la lista de tickers del Nasdaq-100.

    Si use_live=True intenta leer la tabla actual desde Wikipedia; si falla
    por cualquier motivo (sin internet, cambio de formato), cae al fallback.
    """
    if use_live:
        try:
            tablas = pd.read_html("https://en.wikipedia.org/wiki/Nasdaq-100")
            # La tabla de componentes suele ser la que tiene una columna "Ticker"
            tabla_componentes = next(t for t in tablas if "Ticker" in t.columns)
            tickers = tabla_componentes["Ticker"].astype(str).str.strip().tolist()
            tickers = [t.replace(".", "-") for t in tickers]  # ej. BRK.B -> BRK-B
            print(f"Lista Nasdaq-100 obtenida en vivo: {len(tickers)} tickers")
            return sorted(set(tickers))
        except Exception as e:
            print(f"No se pudo obtener la lista en vivo ({e}). Usando fallback fijo.")
    return sorted(set(_NASDAQ100_FALLBACK))


# =====================================================================
# 2. DESCARGA EN LOTE (mismo patrón que tu download_real_data)
# =====================================================================
def download_real_data(tickers, period="3y", interval="1d", pause=0.0, logs=False):
    """Descarga real desde Yahoo Finance, ticker por ticker.
    Requiere acceso a internet. Devuelve dict {ticker: DataFrame}."""
    data = {}
    for t in tickers:
        try:
            df = yf.download(t, period=period, interval=interval, progress=False)
            if df.empty:
                print(f"{t}: sin datos, se omite")
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
            data[t] = df
            if(logs):
                print(f"{t}: {len(df)} filas, desde {df.index.min().date()} hasta {df.index.max().date()}")
        except Exception as e:
            print(f"{t}: error al descargar ({e}), se omite")
        if pause:
            time.sleep(pause)
    return data


def download_nasdaq100_data(period="3y", interval="1d", use_live_list=False, pause=0.0, logs=False):
    """Atajo: obtiene la lista de tickers del Nasdaq-100 y descarga sus datos."""
    tickers = get_nasdaq100_tickers(use_live=use_live_list)
    return download_real_data(tickers, period=period, interval=interval, pause=pause, logs=logs)


"""
Filtra la data de nasdaq100 por rango de fechas. Devuelve un dict {ticker: DataFrame} con los datos filtrados.
Util para reducir la cantidad de datos a procesar en el screener, especialmente si se descargó un rango amplio.
Example :
    data_nasdaq100_dict = download_nasdaq100_data(period="5y", interval="1d", use_live_list=True, pause=0.1)
    start_date = "2023-01-01"
    end_date = "2025-12-31"
"""
def filter_nasdaq100_data(data_nasdaq100_dict, start_date=None, end_date=None):
    """Filtra los DataFrames de un dict {ticker: DataFrame} por rango de fechas."""
    # Filtrar cada DataFrame dentro del diccionario usando .loc
    filtered_data = {
        ticker: df.loc[start_date:end_date]
        for ticker, df in data_nasdaq100_dict.items()
    }
    return filtered_data




import os
import pandas as pd
from datetime import datetime
import hashlib
import os
import pandas as pd
from datetime import datetime
import hashlib
import pickle

class YahooFinanceCache:
    def __init__(self, cache_dir="cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_filename(self, period, interval, extension=".pkl"):
        params = f"{period}_{interval}"
        hash_obj = hashlib.md5(params.encode())
        return os.path.join(self.cache_dir, f"nasdaq100_{hash_obj.hexdigest()[:12]}{extension}")
    
    def _is_cache_valid(self, filename, max_age_days=1):
        if not os.path.exists(filename):
            return False
        
        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(filename))
        return file_age.days < max_age_days
    
    def _save_dict_to_cache(self, data_dict, filename):
        with open(filename, 'wb') as f:
            pickle.dump(data_dict, f)
    
    # def _save_dict_to_cache(self, filename, data):
    #     # Guardar en un archivo temporal primero
    #     temp_filename = filename + '.tmp'
    #     with open(temp_filename, 'wb') as f:
    #         pickle.dump(data, f)
    #     # Luego renombrar (operación atómica)
    #     os.replace(temp_filename, filename)

    def _load_dict_from_cache(self, filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    
    def get_data(self, period="2y", interval="1d", force_download=False, max_age_days=1):
        cache_filename = self._get_cache_filename(period, interval)
        
        if not force_download and self._is_cache_valid(cache_filename, max_age_days):
            print(f"Usando cache: {os.path.basename(cache_filename)}")
            return self._load_dict_from_cache(cache_filename)
        
        print(f"Descargando datos frescos para {period} {interval}...")
        try:
            data_dict = download_nasdaq100_data(period=period, interval=interval, logs=False)
            
            self._save_dict_to_cache(data_dict, cache_filename)
            print(f"Datos guardados en cache: {os.path.basename(cache_filename)}")
            
            return data_dict
            
        except Exception as e:
            print(f"Error descargando datos: {e}")
            
            if os.path.exists(cache_filename):
                print(f"Usando cache antiguo como fallback: {os.path.basename(cache_filename)}")
                return self._load_dict_from_cache(cache_filename)
            else:
                raise

cache = YahooFinanceCache()

def get_nasdaq100_data(period="1y", interval="1d", force_download=False, max_age_days=1):
    return cache.get_data(period, interval, force_download, max_age_days)


async def get_nasdaq100_data_async(period="1y", interval="1d", force_download=False, max_age_days=1):
    return await asyncio.to_thread(
        get_nasdaq100_data,
        period=period,
        interval=interval,
        force_download=force_download,
        max_age_days=max_age_days
    )


# Tu diccionario original
KEEP_PURGED_DATA = {
    'keep': ['AAPL', 'AMD', 'AMZN', 'AVGO', 'CAT', 'CSCO', 'CSX', 'IDXX', 
             'JPM', 'KLAC', 'META', 'MNST', 'MU', 'NFLX', 'NVDA', 'PDD', 
             'TMUS', 'TSM', 'VRTX', 'ZS'],
    'purge': ['ADBE', 'ADI', 'ADP', 'AEP', 'AMAT', 'AMGN', 'ASML', 'BABA', 
              'BAC', 'BIIB', 'BKNG', 'BKR', 'CDNS', 'CDW', 'CHTR', 'CMCSA', 
              'COST', 'CPRT', 'CRWD', 'CSGP', 'CTAS', 'CTSH', 'CVX', 'DDOG', 
              'DXCM', 'EA', 'EXC', 'FANG', 'FAST', 'FTNT', 'GE', 'GILD', 
              'GOOG', 'GOOGL', 'HD', 'HON', 'ILMN', 'INTC', 'INTU', 'ISRG', 
              'JNJ', 'KDP', 'KHC', 'KO', 'LRCX', 'LULU', 'MAR', 'MCD', 
              'MCHP', 'MDLZ', 'MELI', 'MRVL', 'MSFT', 'NVO', 'NXPI', 'ODFL', 
              'ON', 'ORLY', 'PANW', 'PAYX', 'PCAR', 'PEP', 'PFE', 'PG', 
              'PYPL', 'QCOM', 'REGN', 'ROP', 'ROST', 'SAP', 'SBUX', 'SNPS', 
              'TEAM', 'TM', 'TSLA', 'TTD', 'TXN', 'UNH', 'V', 'VRSK', 
              'WBD', 'WDAY', 'WMT', 'XEL', 'XOM', 'ABNB', 'DASH', 'GFS', 
              'GEHC']
}