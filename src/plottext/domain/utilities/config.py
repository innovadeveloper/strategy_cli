import json
import sys
import os
from pathlib import Path

# Variable global singleton
_CONFIG_DATA = None

def load_config(config_file='config_data.json'):
    """
    Carga el archivo de configuración como diccionario.
    Busca en la raíz del proyecto en desarrollo o junto al ejecutable en producción.
    """
    global _CONFIG_DATA
    
    if _CONFIG_DATA is not None:
        return _CONFIG_DATA
    
    # Determinar la ruta base según el entorno
    if getattr(sys, 'frozen', False):
        # PyInstaller: usar directorio del ejecutable
        base_path = Path(sys.executable).parent
    else:
        # Desarrollo: usar directorio del proyecto (5 niveles arriba de este archivo)
        base_path = Path(__file__).parent.parent.parent.parent.parent
    
    config_path = base_path / config_file
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            _CONFIG_DATA = json.load(f)
        print(f"Configuración cargada desde: {config_path}")
        return _CONFIG_DATA
    except FileNotFoundError:
        print(f"Archivo no encontrado: {config_path}")
        _CONFIG_DATA = {}
        return _CONFIG_DATA
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        _CONFIG_DATA = {}
        return _CONFIG_DATA

# Función de acceso rápido
def config(key=None, default=None):
    """
    Obtiene un valor de configuración.
    Si key es None, devuelve todo el diccionario.
    """
    data = load_config()
    if key is None:
        return data
    return data.get(key, default)

# Uso:
# config_data = load_config()
# valor = config('some_key', 'default_value')
# o directamente:
# api_key = config('api_key')
# all_config = config()