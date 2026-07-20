# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

# -- binary files
lib = 'libmilib.dll' if sys.platform.startswith('win') else 'libmilib.dylib' if sys.platform.startswith('darwin') else 'libmilib.so'

# ── Data files ────────────────────────────────────────────────────────────────
datas = []
datas += collect_data_files('backtesting')

# ── Binary libs (macOS) ───────────────────────────────────────────────────────
binaries = []
binaries += collect_dynamic_libs('curl_cffi')
#binaries.append((f'/Users/mac/Documents/Projects/PythonProjects/strategy_cli/assets/c_language/{lib}', '.'))
#binaries.append((f'/tmp/strategy_cli/{lib}', '.'))
binaries.append((f'./libmilib.dylib', '.'))


a = Analysis(
    ['src/plottext/app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
