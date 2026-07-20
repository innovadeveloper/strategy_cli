# plottext

Add your description here

## Instalacion

```bash
# Instalar desde Artifactory
uv pip install --index-url https://artifactory-service.abexacloud.com/repository/pypi-hosted/simple/ plottext

# O en modo desarrollo
uv pip install -e .
```

## Uso

```bash
# Ejecutar el script
app-cli

# O como modulo
python -m plottext.app
```

## Desarrollo

```bash
# Crear entorno virtual
uv venv --python 3.11
source .venv/bin/activate

# Instalar dependencias
uv pip install -e .

# Ejecutar
app-cli
```

## Estructura del proyecto

```
src/plottext/
├── app.py
├── domain/
│   ├── dto/
│   └── utilities/
├── infrastructure/
│   ├── config/
│   └── service/
└── ui/
    ├── dialogs/
    └── screens/
```

## Publicación e instalación de tools desde artifactory

```
# Instalar desde PyPI
uv tool install ruff

# Instalar desde Artifactory (URL entre comillas)
uv tool install wg-cli --index-url "https://artifactory/simple/"

# Instalar con versión específica
uv tool install wg-cli==0.1.0 --force-reinstall

# Listar herramientas instaladas
uv tool list

# Ejecutar herramienta
wg-cli --help

# o
uv tool run wg-cli

# Desinstalar
uv tool uninstall wg-cli
```

```sh

twine upload --repository artifactory_abexacloud dist/*

uv tool install plottext==0.1.0 --index "https://artifactory-service.abexacloud.com/repository/pypi-hosted/simple/" --force-reinstall
```

## Creación de ficheros de configuración para credenciales de Artifactory

```
# file : ~/.pypirc

[distutils]
index-servers = artifactory_abexacloud

[artifactory_abexacloud]
repository = https://artifactory-service.abexacloud.com/repository/pypi-hosted/
username = sample_user
password = sample_user
```

```

# file : ~/.netrc

machine artifactory-service.abexacloud.com
login admin
password admin
```

## Pyinstaller (empaquetado de ejecutable)

```md
┌───────────────────────────────────────────────────────────────────────────────────────┬────────────────────────────────────────────────────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────┐
│                             Error al ejecutar el binario                              │                                 Causa                                  │                                          Solución                                          │
├───────────────────────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────┤
│ ModuleNotFoundError: No module named 'X'                                              │ Import dinámico que PyInstaller no vio                                 │ agregar 'X' a hiddenimports, o si es un paquete con submódulos con plugins (X.foo,         │
│                                                                                       │                                                                        │ X.bar...) usar collect_submodules('X')                                                     │
├───────────────────────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────┤
│ FileNotFoundError buscando un .json, .ttf, .css, plantilla, etc. dentro de            │ El paquete trae recursos no-Python que PyInstaller no empaqueta por    │ collect_data_files('X')                                                                    │
│ site-packages/X/...                                                                   │ defecto                                                                │                                                                                            │
├───────────────────────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────┤
│ ImportError: DLL load failed (Windows) / Library not loaded (dylib, macOS) / .so:     │ Extensión compilada (C/C++/Rust) o librería nativa que el import       │ collect_dynamic_libs('X')                                                                  │
│ cannot open shared object (Linux)                                                     │ estático no detecta como binario                                       │                                                                                            │
└───────────────────────────────────────────────────────────────────────────────────────┴────────────────────────────────────────────────────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────┘

```

```sh

uv add --dev pyinstaller

uv run pyinstaller --onefile src/plottext/app.py

    # FileNotFoundError: [Errno 2] No such file or directory: '/var/folders/_n 9bdk_rbx6gnbd8cbp720393c0000gn/T/_MEI3TLpsf/backtesting/autoscale_cb.js'

uv run pyinstaller app.spec

```