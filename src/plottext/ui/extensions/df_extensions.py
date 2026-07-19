
import pandas as pd

def dfs_from_dict(data_dict, n_columns=1):
    """
    Crea dos DataFrames a partir del diccionario con 'keep' y 'purge'
    divididos en N columnas
    """
    import math
    
    def split_list_into_columns(lst, n_cols):
        """Divide una lista en N columnas"""
        per_col = math.ceil(len(lst) / n_cols)
        # Crear lista de listas para cada columna
        columns = []
        for i in range(n_cols):
            start = i * per_col
            end = min(start + per_col, len(lst))
            col_data = lst[start:end] + [''] * (per_col - (end - start))
            columns.append(col_data)
        return columns
    
    # Dividir las listas en columnas
    keep_columns = split_list_into_columns(data_dict['keep'], n_columns)
    purge_columns = split_list_into_columns(data_dict['purge'], n_columns)
    
    # Crear DataFrame de 'keep' con múltiples columnas
    keep_data = {}
    for i, col in enumerate(keep_columns):
        keep_data[f'Keep_{i+1}'] = col
    
    # Crear DataFrame de 'purge' con múltiples columnas
    purge_data = {}
    for i, col in enumerate(purge_columns):
        purge_data[f'Purge_{i+1}'] = col
    
    df_keep = pd.DataFrame(keep_data)
    df_purge = pd.DataFrame(purge_data)
    
    return df_keep, df_purge