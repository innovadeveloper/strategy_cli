# Guía: cómo armar y ajustar un `.spec` de PyInstaller

Procedimiento para empaquetar cualquier script de este proyecto (o de otro) sin
copiar un `.spec` genérico a ciegas. La idea central: **no adivines qué necesita
el build — deja que el binario compilado te lo diga con un error, y arregla
solo ese error.**

## 1. Punto de partida: el esqueleto

```bash
pyi-makespec --onefile --console src/plottext/app.py
```

Esto genera un `.spec` mínimo (`datas=[]`, `hiddenimports=[]`, `binaries=[]`).
Constrúyelo tal cual y corre el binario, no el script de Python:

```bash
pyinstaller app.spec
dist/app
```

Casi seguro va a fallar la primera vez si el proyecto tiene dependencias con
recursos no-Python o imports dinámicos. Eso es esperado — el esqueleto es el
punto de partida, no el resultado.

## 2. El ciclo: build → run → leer el error → arreglar solo eso

Repite hasta que la app corra limpio en un uso real (no solo que abra):

```bash
pyinstaller app.spec && dist/app
```

Cada tipo de error te dice exactamente qué falta y qué herramienta usar:

| Error al ejecutar el binario | Causa | Solución |
|---|---|---|
| `ModuleNotFoundError: No module named 'X'` | Import dinámico que PyInstaller no vio al analizar el código estáticamente (p. ej. `importlib.import_module(nombre_calculado)`, sistemas de plugins, o un paquete con muchos submódulos que no se importan todos explícitamente) | Si es un módulo puntual: agrégalo suelto a `hiddenimports += ['X.submodulo']`. Si el paquete completo usa un patrón de plugins (ej. `X.foo`, `X.bar` se cargan dinámicamente): `hiddenimports += collect_submodules('X')` |
| `FileNotFoundError` buscando un `.json`, `.ttf`, `.css`, `.js`, plantilla HTML, etc. dentro de una ruta tipo `site-packages/X/...` | El paquete lee un archivo de datos con una ruta relativa a su propio `__file__` en tiempo de ejecución (`Path(__file__).parent / "archivo.js"`). Esto **nunca** es detectable por análisis estático porque no hay ningún `import` que rastrear — es lectura de archivo, no importación de módulo | `datas += collect_data_files('X')` |
| `ImportError: DLL load failed` (Windows) / `Library not loaded: ...dylib` (macOS) / `... .so: cannot open shared object file` (Linux) | Extensión compilada (C/C++/Rust/Cython) o librería nativa que el paquete carga en tiempo de ejecución y que el análisis de imports no marcó como binario a copiar | `binaries += collect_dynamic_libs('X')` |

Las tres funciones vienen de:

```python
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs
```

## 3. Qué hace cada función, en una frase

- **`collect_data_files('X')`** → copia archivos NO-`.py` que vienen dentro del
  paquete `X` (css, json, plantillas, fuentes, `.js`, `.txt`...) para que estén
  disponibles en la misma ruta relativa dentro del binario empaquetado.
- **`collect_submodules('X')`** → fuerza a incluir *todos* los submódulos de
  `X`, incluso los que el código no importa de forma literal (útil para
  paquetes con arquitectura de plugins/backends).
- **`collect_dynamic_libs('X')`** → copia librerías nativas compiladas
  (`.so` / `.dylib` / `.pyd`) que `X` necesita en tiempo de ejecución.

## 4. Antes de tocar el `.spec`: inspecciona el paquete

No hace falta esperar al error para saber si un paquete va a necesitar
`collect_data_files` o `collect_dynamic_libs` — puedes revisarlo de antemano:

```bash
# ¿Trae archivos de datos (no .py)?
python -c "import backtesting, os; print(os.path.dirname(backtesting.__file__))"
find "$(python -c 'import backtesting,os;print(os.path.dirname(backtesting.__file__))')" \
  -not -name "*.py" -not -name "*.pyc"

# ¿Trae binarios compilados?
find "$(python -c 'import curl_cffi,os;print(os.path.dirname(curl_cffi.__file__))')" \
  -name "*.so" -o -name "*.dylib" -o -name "*.pyd"
```

Si el `find` de datos devuelve algo como `autoscale_cb.js` → vas a necesitar
`collect_data_files`. Si el segundo `find` devuelve binarios → vas a necesitar
`collect_dynamic_libs`.

## 5. Antes de escribir nada a mano: puede que ya exista un hook

PyInstaller trae `pyinstaller-hooks-contrib` instalado como dependencia, que
ya incluye hooks mantenidos para paquetes comunes (`numpy`, `pandas`, `numba`,
`llvmlite`, `curl_cffi`, entre muchos otros) y se aplican automáticamente sin
que el `.spec` tenga que declarar nada. Por eso muchas veces el `.spec`
mínimo ya funciona para paquetes que "suenan complicados" — el trabajo ya
está hecho aguas arriba. Solo interviene manualmente cuando el error real
te dice que hace falta.

## 6. Lo que NO hay que hacer: agregar cosas "por si acaso"

El análisis estático de PyInstaller (`modulegraph`) sigue imports normales
de forma recursiva solo. Si tu código hace `from textual.widgets import
Button`, PyInstaller ya rastrea esa cadena solo — **no hace falta**
`collect_submodules('textual')` a menos que el error real lo pida.

Un `.spec` con `hiddenimports`/`collect_submodules`/`collect_dynamic_libs`
para diez paquetes "por si las dudas" build más lento y un binario más
pesado con código que nunca corre. El spec correcto es el más corto que pasa
el ciclo del punto 2, no el más largo.

## 7. Cobertura: prueba funcionalidades, no solo el arranque

El análisis estático cubre lo que aparece literalmente en el código. Pero un
`importlib.import_module(nombre_calculado)`, una carga de plugin, o un backend
que solo se activa con cierta opción de la app, **solo se revela ejecutando
esa ruta de código específica** dentro del binario ya empaquetado. Que la app
abra no significa que el `.spec` esté completo — ejercita las funcionalidades
menos comunes (no solo el camino feliz) antes de dar el `.spec` por bueno.

## 8. Multiplataforma: no asumas, repite el ciclo en cada SO

`collect_dynamic_libs` resuelve automáticamente `.dylib` vs `.dll` vs `.so`
según el SO en el que corras PyInstaller — pero eso no significa que un
`.spec` validado en mac vaya a funcionar igual en Windows. Diferencias típicas
entre plataformas:

- Módulos exclusivos de un SO que solo se importan ahí (`winreg`, `win32api`,
  `colorama` en Windows; nada equivalente en mac/Linux).
- `icon=` en el bloque `EXE` (Windows usa `.ico`, macOS usa `.icns` vía
  `BUNDLE`, si se genera `.app`).

Corre el ciclo completo build → run → error en cada plataforma objetivo por
separado. No copies un `.spec` de mac a Windows esperando que funcione sin
pasar por el ciclo ahí también.

## 9. Resumen del procedimiento

1. `pyi-makespec --onefile tu_script.py` → esqueleto.
2. `pyinstaller tu_script.spec` y ejecuta **el binario** (`dist/...`), no el
   script.
3. Lee el error, ubícalo en la tabla de la sección 2, agrega solo lo que pide.
4. Repite el paso 2–3 hasta que corra limpio.
5. Ejercita las funcionalidades reales de la app (no solo el arranque) para
   destapar imports dinámicos que solo aparecen en ciertos flujos.
6. Repite el ciclo completo en cada SO objetivo por separado.
7. Recién al final, ajusta lo cosmético: `excludes` (para bajar tamaño
   quitando lo que sabes que no se usa, ej. `tkinter`, `matplotlib`),
   `icon`, `console`, `upx`.

