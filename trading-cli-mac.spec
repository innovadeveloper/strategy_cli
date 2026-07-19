# -*- mode: python ; coding: utf-8 -*-
# macOS build spec for trading-cli
# Build: pyinstaller trading-cli-mac.spec

import sys
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

block_cipher = None

# ── Data files ────────────────────────────────────────────────────────────────
datas = []
datas += collect_data_files('textual')
datas += collect_data_files('rich')
datas += collect_data_files('plotext')
datas += collect_data_files('pandas_ta')
datas += collect_data_files('backtesting')
datas += collect_data_files('certifi')
datas += collect_data_files('curl_cffi')

# ── Hidden imports ─────────────────────────────────────────────────────────────
hiddenimports = []
hiddenimports += collect_submodules('textual')
hiddenimports += collect_submodules('rich')
hiddenimports += collect_submodules('pandas_ta')
hiddenimports += collect_submodules('backtesting')
hiddenimports += collect_submodules('plotext')
hiddenimports += collect_submodules('yfinance')
hiddenimports += collect_submodules('numba')
hiddenimports += collect_submodules('llvmlite')
hiddenimports += collect_submodules('curl_cffi')
hiddenimports += collect_submodules('py_shared_library')
hiddenimports += [
    'pkg_resources',
    'pkg_resources.extern',
    'pandas._libs.tslibs.np_datetime',
    'pandas._libs.tslibs.nattype',
    'pandas._libs.tslibs.timedeltas',
    'pandas._libs.tslibs.timestamps',
    'pandas._libs.tslibs.offsets',
    'pandas._libs.tslibs.period',
    'pandas._libs.tslibs.parsing',
    'pandas._libs.tslibs.strptime',
    'pandas._libs.tslibs.vectorized',
    'pandas._libs.missing',
    'pandas._libs.hashtable',
    'pandas._libs.index',
    'pandas._libs.lib',
    'pandas._libs.sparse',
    'pandas._libs.writers',
    'pandas._libs.reduction',
    'scipy',
    'scipy.special',
    'scipy.special._cdflib',
    'scipy.optimize',
    'scipy.linalg',
    'questionary',
    'prompt_toolkit',
    'asciichartpy',
    'asyncio',
    'aiohttp',
    'aiofiles',
    'filelock',
    'peewee',
    'bs4',
    'beautifulsoup4',
    'lxml',
    'multitasking',
    'narwhals',
]

# ── Binary libs (macOS) ───────────────────────────────────────────────────────
binaries = []
binaries += collect_dynamic_libs('curl_cffi')
binaries += collect_dynamic_libs('llvmlite')

a = Analysis(
    ['src/plottext/app.py'],
    pathex=['src'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        '_tkinter',
        'IPython',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='trading-cli',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
