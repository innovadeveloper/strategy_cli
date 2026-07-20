
from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
import pandas as pd
from datetime import datetime


from rich.table import Table
from rich.text import Text
from rich.console import Console
import pandas as pd

console = Console()

# def df_to_table_ritch(df, max_rows=None, index_name=None):
#     """Muestra DataFrame con colores según columna 'style'"""
#     table = Table(show_header=True, header_style="bold cyan")
    
#     # Configurar índice
#     idx_label = index_name or df.index.name or "#"
#     table.add_column(idx_label, style="bold cyan")
    
#     # Agregar columnas (excepto 'style' si no quieres mostrarla)
#     for col in df.columns:
#         if col != 'style':  # Ocultar columna 'style'
#             table.add_column(str(col))
    
#     # Procesar filas
#     for i, (idx, row) in enumerate(df.iterrows()):
#         if max_rows and i >= max_rows:
#             break
        
#         # ✅ Obtener el color de la columna 'style'
#         color = row.get('style', 'white')  # Default: white si no existe
        
#         # Crear índice formateado
#         idx_text = Text(str(idx), style=f"bold {color}")
        
#         # Formatear cada celda con el color correspondiente
#         row_cells = []
#         for col in df.columns:
#             if col != 'style':  # No mostrar la columna 'style'
#                 value = row[col]
#                 # ✅ Aplicar el color a toda la celda
#                 row_cells.append(Text(str(value), style=color))
        
#         # ✅ Aplicar el color a toda la fila
#         table.add_row(idx_text, *row_cells, style=color)
    
#     return table


def df_to_table_ritch(df, max_rows=None, precision=2, index_name=None):
    """
    Muestra cualquier DataFrame como tabla Rich
    
    Args:
        df: DataFrame de pandas
        max_rows: límite de filas a mostrar
        precision: decimales para números
        index_name: nombre personalizado para el índice
    """
    table = Table(show_header=True, header_style="bold cyan")
    
    # Configurar índice
    idx_label = index_name or df.index.name or "Item"
    table.add_column(idx_label)
    
    # Agregar columnas
    for col in df.columns:
        # Detectar tipo de columna para estilos
        col_style = "green" if pd.api.types.is_numeric_dtype(df[col]) else "white"
        table.add_column(str(col), style=col_style)
    
    # Procesar filas
    for i, (idx, row) in enumerate(df.iterrows()):
        if max_rows and i >= max_rows:
            break
        color = row.get('style', 'white')  # Default: white si no existe
        
        # Formatear índice
        idx_formatted = _format_value(idx)
        # idx_text = Text(str(idx), style=f"bold {color}")
        
        # Formatear fila
        row_values = []
        for v in row:
            row_values.append(_format_value(v, precision))
        
        table.add_row(idx_formatted, *row_values)
    
    return table

def _format_value(value, precision=2):
    """Formatea cualquier valor para display"""
    if pd.isna(value):
        return "N/A"
    elif isinstance(value, (pd.Timestamp, datetime)):
        return value.strftime("%Y-%m-%d %H:%M" if value.hour > 0 else "%Y-%m-%d")
    elif isinstance(value, float):
        return f"{value:.{precision}f}"
    elif isinstance(value, int):
        return f"{value:,}"  # agrega separadores de miles
    elif isinstance(value, str) and len(value) > 50:
        return value[:47] + "..."
    else:
        return str(value)
    

def two_panels_ritch(df_left, df_right, 
                          left_title="KEEP",
                          right_title="PURGE",
                          max_rows=None):
    """
    Muestra dos DataFrames lado a lado ajustados al contenido
    """
    console = Console()
    
    # Crear las tablas
    table_left = df_to_table_ritch(df_left)
    table_right = df_to_table_ritch(df_right)
    
    # Crear paneles ajustados
    panel_left = Panel(table_left, 
                       title=left_title, 
                       border_style="green",
                       expand=False)  # No expandir
    
    panel_right = Panel(table_right, 
                        title=right_title, 
                        border_style="red",
                        expand=False)  # No expandir
    
    # Mostrar lado a lado con Group
    from rich import print as rprint
    from rich.columns import Columns
    

    return Panel(
        Columns([panel_left, panel_right], equal=False, expand=False),
        title="ANÁLISIS DE SÍMBOLOS",
        border_style="bright_blue",
        expand=False
    )

    # # Usar Columns para mostrar lado a lado
    # rprint(Panel(
    #     Columns([panel_left, panel_right], equal=False, expand=False),
    #     title="ANÁLISIS DE SÍMBOLOS",
    #     border_style="bright_blue",
    #     expand=False
    # ))
    
    # # Mostrar estadísticas
    # console.print(f"\n[bold cyan]📊 Resumen:[/bold cyan]")
    # console.print(f"  [green]Mantener:[/green] {len(df_left)} símbolos")
    # console.print(f"  [red]Eliminar:[/red] {len(df_right)} símbolos")
    # console.print(f"  [yellow]Total:[/yellow] {len(df_left) + len(df_right)} símbolos")
