# Windows build script for trading-cli
# Run from PowerShell inside the project root with the venv activated:
#   .\.venv\Scripts\Activate.ps1
#   .\build-windows.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "==> Activating venv..."
.\.venv\Scripts\Activate.ps1

Write-Host "==> Cleaning previous builds..."
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist")  { Remove-Item -Recurse -Force "dist" }

Write-Host "==> Building trading-cli for Windows..."
pyinstaller trading-cli-windows.spec

Write-Host ""
Write-Host "==> Done! Binary at: dist\trading-cli.exe"
