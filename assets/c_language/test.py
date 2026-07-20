#!/usr/bin/env python3
"""
Script para probar nuestra librería C multiplataforma
"""
import ctypes
import sys
import os
from pathlib import Path

class MiLib:
    """Wrapper para nuestra librería C"""
    
    def __init__(self):
        self.lib = self._cargar_libreria()
        self._configurar_funciones()
    
    def _get_lib_name(self):
        """Obtiene el nombre correcto de la librería según SO"""
        if sys.platform.startswith('win'):
            return 'libmilib.dll'
        elif sys.platform.startswith('darwin'):
            return 'libmilib.dylib'
        else:
            return 'libmilib.so'
    
    def _get_base_dir(self):
        """Obtiene el directorio del ejecutable o script"""
        if getattr(sys, 'frozen', False):
            # Estamos en un ejecutable PyInstaller
            return os.path.dirname(sys.executable)
        else:
            # Estamos en desarrollo
            return os.path.dirname(os.path.abspath(__file__))
    
    def _cargar_libreria(self):
        """Carga la librería desde varias ubicaciones posibles"""
        base_dir = self._get_base_dir()
        lib_name = self._get_lib_name()
        
        # 1. Buscar en el directorio del ejecutable/script
        local_path = os.path.join(base_dir, lib_name)
        if os.path.exists(local_path):
            try:
                print(f"📦 Cargando librería desde: {local_path}")
                return ctypes.CDLL(local_path)
            except OSError as e:
                print(f"⚠️  Error cargando desde local: {e}")
        
        # 2. Buscar en el directorio actual
        if os.path.exists(lib_name):
            try:
                print(f"📦 Cargando librería desde: {lib_name}")
                return ctypes.CDLL(lib_name)
            except OSError:
                pass
        
        # 3. macOS: buscar en Homebrew
        if sys.platform.startswith('darwin'):
            for path in ['/usr/local/lib', '/opt/homebrew/lib']:
                full_path = os.path.join(path, lib_name)
                if os.path.exists(full_path):
                    try:
                        print(f"📦 Cargando librería desde: {full_path}")
                        return ctypes.CDLL(full_path)
                    except OSError:
                        continue
        
        raise FileNotFoundError(f"No se encontró la librería {lib_name}")
    
    def _configurar_funciones(self):
        """Configura los tipos de las funciones C"""
        lib = self.lib
        
        # Operaciones básicas
        lib.suma.argtypes = [ctypes.c_int, ctypes.c_int]
        lib.suma.restype = ctypes.c_int
        
        lib.resta.argtypes = [ctypes.c_int, ctypes.c_int]
        lib.resta.restype = ctypes.c_int
        
        lib.multiplicacion.argtypes = [ctypes.c_int, ctypes.c_int]
        lib.multiplicacion.restype = ctypes.c_int
        
        lib.division.argtypes = [ctypes.c_int, ctypes.c_int]
        lib.division.restype = ctypes.c_double
        
        # Operaciones con arrays
        lib.promedio.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int]
        lib.promedio.restype = ctypes.c_double
        
        lib.desviacion_estandar.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int]
        lib.desviacion_estandar.restype = ctypes.c_double
        
        lib.ordenar_array.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int]
        lib.ordenar_array.restype = None
        
        # Strings
        lib.concatenar.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        lib.concatenar.restype = ctypes.c_char_p
        
        lib.liberar_string.argtypes = [ctypes.c_char_p]
        lib.liberar_string.restype = None
        
        # Versión
        lib.obtener_version.argtypes = []
        lib.obtener_version.restype = ctypes.c_char_p
    
    # ── Métodos Python que envuelven las funciones C ──
    
    def suma(self, a, b):
        return self.lib.suma(a, b)
    
    def resta(self, a, b):
        return self.lib.resta(a, b)
    
    def multiplicacion(self, a, b):
        return self.lib.multiplicacion(a, b)
    
    def division(self, a, b):
        return self.lib.division(a, b)
    
    def promedio(self, arr):
        if not arr:
            return 0.0
        c_arr = (ctypes.c_double * len(arr))(*arr)
        return self.lib.promedio(c_arr, len(arr))
    
    def desviacion_estandar(self, arr):
        if not arr:
            return 0.0
        c_arr = (ctypes.c_double * len(arr))(*arr)
        return self.lib.desviacion_estandar(c_arr, len(arr))
    
    def ordenar(self, arr):
        if not arr:
            return arr
        c_arr = (ctypes.c_double * len(arr))(*arr)
        self.lib.ordenar_array(c_arr, len(arr))
        return list(c_arr)
    
    def concatenar(self, str1, str2):
        if not str1 or not str2:
            return None
        result = self.lib.concatenar(str1.encode('utf-8'), str2.encode('utf-8'))
        if result:
            return result.decode('utf-8')
        return None
    
    def version(self):
        return self.lib.obtener_version().decode('utf-8')

# ── Ejemplo de uso ──────────────────────────────────────────────────
def main():
    print("🚀 Probando MiLib (librería C multiplataforma)")
    print("=" * 50)
    
    try:
        milib = MiLib()
        
        # Mostrar versión
        print(f"📦 Versión: {milib.version()}")
        print()
        
        # Operaciones básicas
        print("➗ Operaciones básicas:")
        print(f"  10 + 5 = {milib.suma(10, 5)}")
        print(f"  10 - 5 = {milib.resta(10, 5)}")
        print(f"  10 * 5 = {milib.multiplicacion(10, 5)}")
        print(f"  10 / 5 = {milib.division(10, 5):.2f}")
        print()
        
        # Operaciones con arrays
        datos = [2.5, 3.7, 1.8, 4.2, 5.1, 3.9, 2.8]
        print(f"📊 Datos: {datos}")
        print(f"  Promedio: {milib.promedio(datos):.2f}")
        print(f"  Desviación estándar: {milib.desviacion_estandar(datos):.2f}")
        
        datos_ordenados = milib.ordenar(datos.copy())
        print(f"  Datos ordenados: {datos_ordenados}")
        print()
        
        # Strings
        result = milib.concatenar("Hola ", "Mundo!")
        print(f"📝 Concatenación: '{result}'")
        print()
        
        print("✅ ¡MiLib funcionando correctamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())