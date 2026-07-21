#!/bin/bash
# create_project.sh - Generador de estructura de proyecto Python

set -e

# ============================================
# CONFIGURACIÓN PARAMETRIZABLE
# ============================================

# Valores por defecto
PROJECT_NAME="${1:-mi-proyecto}"
PROJECT_NAME_UNDERSCORE="${PROJECT_NAME//-/_}"
PROJECT_VERSION="${2:-0.1.0}"
PROJECT_DESCRIPTION="${3:-Add your description here}"
PYTHON_VERSION="${4:-3.11}"
LIBRARY_VERSION="${5:-py-shared-library>=0.1.1}"
ARTIFACTORY_URL="${6:-https://artifactory-service.abexacloud.com/repository/pypi-hosted/simple/}"
SCRIPT_NAME="${7:-app-cli}"

# ============================================
# FUNCIONES
# ============================================

create_directory_structure() {
    local base_path="src/${PROJECT_NAME_UNDERSCORE}"
    
    echo "Creando estructura de directorios..."
    
    mkdir -p "${base_path}"
    mkdir -p "${base_path}/domain/dto"
    mkdir -p "${base_path}/domain/utilities"
    mkdir -p "${base_path}/infrastructure/config"
    mkdir -p "${base_path}/infrastructure/service"
    mkdir -p "${base_path}/ui/dialogs"
    mkdir -p "${base_path}/ui/screens"
    
    mkdir -p ".vscode"
    
    echo "Estructura creada en: ${base_path}"
}

create_pyproject_toml() {
    echo "Creando pyproject.toml..."
    
    cat > pyproject.toml << EOF
[project]
name = "${PROJECT_NAME_UNDERSCORE}"
version = "${PROJECT_VERSION}"
description = "${PROJECT_DESCRIPTION}"
readme = "README.md"
requires-python = ">=${PYTHON_VERSION}"
dependencies = [
    "${LIBRARY_VERSION}",
]

[tool.uv]
index-url = "${ARTIFACTORY_URL}"
extra-index-url = ["https://pypi.org/simple/"]

[project.scripts]
${SCRIPT_NAME} = "${PROJECT_NAME_UNDERSCORE}.app:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
EOF
    
    echo "pyproject.toml creado"
}

create_app_py() {
    local base_path="src/${PROJECT_NAME_UNDERSCORE}"
    
    echo "Creando app.py..."
    
    cat > "${base_path}/app.py" << EOF
"""Main entry point for ${PROJECT_NAME}."""

import sys


def main():
    """Main function."""
    print("Hello from ${PROJECT_NAME}!")
    print(f"Python version: {sys.version}")
    print(f"Arguments: {sys.argv[1:]}")
    
    # TODO: Implementar lógica principal aquí


if __name__ == "__main__":
    main()
EOF
    
    echo "app.py creado"
}

create_init_files() {
    local base_path="src/${PROJECT_NAME_UNDERSCORE}"
    
    echo "Creando archivos __init__.py..."
    
    cat > "${base_path}/__init__.py" << EOF
"""${PROJECT_NAME} - ${PROJECT_DESCRIPTION}"""
__version__ = "${PROJECT_VERSION}"
EOF
    
    cat > "${base_path}/domain/__init__.py" << EOF
"""Domain layer for ${PROJECT_NAME}."""
EOF
    
    cat > "${base_path}/domain/dto/__init__.py" << EOF
"""Data Transfer Objects for ${PROJECT_NAME}."""
EOF
    
    cat > "${base_path}/domain/utilities/__init__.py" << EOF
"""Utilities for ${PROJECT_NAME} domain."""
EOF
    
    cat > "${base_path}/infrastructure/__init__.py" << EOF
"""Infrastructure layer for ${PROJECT_NAME}."""
EOF
    
    cat > "${base_path}/infrastructure/config/__init__.py" << EOF
"""Configuration for ${PROJECT_NAME}."""
EOF
    
    cat > "${base_path}/infrastructure/service/__init__.py" << EOF
"""Services for ${PROJECT_NAME}."""
EOF
    
    cat > "${base_path}/ui/__init__.py" << EOF
"""UI layer for ${PROJECT_NAME}."""
EOF
    
    cat > "${base_path}/ui/dialogs/__init__.py" << EOF
"""Dialogs for ${PROJECT_NAME}."""
EOF
    
    cat > "${base_path}/ui/screens/__init__.py" << EOF
"""Screens for ${PROJECT_NAME}."""
EOF
    
    echo "Archivos __init__.py creados"
}

create_vscode_files() {
    echo "Creando archivos de configuración de VSCode..."
    
    cat > .vscode/launch.json << EOF
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "${PROJECT_NAME_UNDERSCORE} (program)",
            "type": "debugpy",
            "request": "launch",
            "program": "\${workspaceFolder}/src/${PROJECT_NAME_UNDERSCORE}/app.py",
            "console": "integratedTerminal",
            "cwd": "\${workspaceFolder}",
            "env": {
                "PYTHONPATH": "\${workspaceFolder}/src"
            },
            "args": []
        }
    ]
}
EOF
    
    cat > .vscode/settings.json << EOF
{
    "python-envs.defaultEnvManager": "ms-python.python:venv"
}
EOF
    
    echo "Archivos de VSCode creados"
}

create_readme() {
    echo "Creando README.md..."
    
    cat > README.md << EOF
# ${PROJECT_NAME}

${PROJECT_DESCRIPTION}

## Instalacion

\`\`\`bash
# Instalar desde Artifactory
uv pip install --index-url ${ARTIFACTORY_URL} ${PROJECT_NAME_UNDERSCORE}

# O en modo desarrollo
uv pip install -e .
\`\`\`

## Uso

\`\`\`bash
# Ejecutar el script
${SCRIPT_NAME}

# O como modulo
python -m ${PROJECT_NAME_UNDERSCORE}.app
\`\`\`

## Desarrollo

\`\`\`bash
# Crear entorno virtual
uv venv --python ${PYTHON_VERSION}
source .venv/bin/activate

# Instalar dependencias
uv pip install -e .

# Ejecutar
${SCRIPT_NAME}
\`\`\`

## Estructura del proyecto

\`\`\`
src/${PROJECT_NAME_UNDERSCORE}/
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
\`\`\`

## Publicación e instalación de tools desde artifactory

\`\`\`
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
\`\`\`


## Creación de ficheros de configuración para credenciales de Artifactory

\`\`\`
# file : ~/.pypirc

[distutils]
index-servers = artifactory_abexacloud

[artifactory_abexacloud]
repository = https://artifactory-service.abexacloud.com/repository/pypi-hosted/
username = sample_user
password = sample_user
\`\`\`

\`\`\`

# file : ~/.netrc

machine artifactory-service.abexacloud.com
login admin
password admin
\`\`\`

EOF
    
    echo "README.md creado"
}

create_gitignore() {
    echo "Creando .gitignore..."
    
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*.pyc
.venv/
venv/
ENV/
env/
dist/
build/
*.egg-info/
*.egg
*.so
*.pyd

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# UV
uv.lock
EOF
    
    echo ".gitignore creado"
}

setup_environment() {
    echo "Configurando entorno virtual..."
    
    uv venv --python "${PYTHON_VERSION}" || {
        echo "No se pudo crear el entorno con Python ${PYTHON_VERSION}. Intentando con python3..."
        uv venv --python python3
    }
    
    source .venv/bin/activate
    uv pip install -e .
    
    echo "Entorno virtual configurado"
}

show_summary() {
    echo ""
    echo "========================================"
    echo "PROYECTO CREADO EXITOSAMENTE"
    echo "========================================"
    echo ""
    echo "Detalles del proyecto:"
    echo "  Nombre: ${PROJECT_NAME}"
    echo "  Version: ${PROJECT_VERSION}"
    echo "  Python: ${PYTHON_VERSION}"
    echo "  Script: ${SCRIPT_NAME}"
    echo "  Dependencia: ${LIBRARY_VERSION}"
    echo ""
    echo "Comandos utiles:"
    echo "  source .venv/bin/activate      # Activar entorno"
    echo "  ${SCRIPT_NAME}                  # Ejecutar script"
    echo "  uv build                       # Construir paquete"
    echo "  twine upload -r artifactory_abexacloud dist/*  # Publicar"
    echo ""
    echo "Estructura creada:"
    find src/ -type f | sort 2>/dev/null || echo "  src/ (estructura creada)"
    echo ""
    echo "Todo listo para empezar a desarrollar!"
}

# ============================================
# EJECUCION PRINCIPAL
# ============================================

main() {
    echo ""
    echo "Generando proyecto: ${PROJECT_NAME}"
    echo "========================================"
    echo ""
    
    mkdir -p "${PROJECT_NAME}"
    cd "${PROJECT_NAME}"
    
    create_directory_structure
    create_pyproject_toml
    create_app_py
    create_init_files
    create_vscode_files
    create_readme
    create_gitignore
    
    setup_environment
    
    show_summary
}

# ============================================
# USO
# ============================================

if [[ $# -eq 0 ]]; then
    echo "Uso: $0 [nombre-proyecto] [version] [descripcion] [python-version] [dependencia] [artifactory-url] [script-name]"
    echo ""
    echo "Ejemplo:"
    echo "  $0 mi-proyecto 0.1.0 \"Mi proyecto Python\" 3.11 \"py-shared-library>=0.1.1\" \"https://artifactory/simple/\" \"mi-cli\""
    echo ""
    echo "O con valores por defecto:"
    echo "  $0 my-awesome-tool"
    exit 1
fi

main


# # Guardar el script
# chmod +x create_project.sh

# # Ejecutar con todos los parámetros
# ./create_project.sh "mi-herramienta" "0.1.0" "Herramienta CLI" "3.11" "py-shared-library>=0.1.1" "https://artifactory.abexacloud.com/simple/" "mi-herramienta-cli"

# # O solo con el nombre (resto valores por defecto)
# ./create_project.sh mi-herramienta