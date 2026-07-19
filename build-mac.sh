#!/bin/bash
set -e

echo "==> Activating venv..."
source .venv/bin/activate

echo "==> Cleaning previous builds..."
rm -rf build/ dist/

echo "==> Building trading-cli for macOS..."
pyinstaller trading-cli-mac.spec

echo ""
echo "==> Done! Binary at: dist/trading-cli"
echo "==> Size: $(du -sh dist/trading-cli | cut -f1)"
