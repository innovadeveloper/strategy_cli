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

