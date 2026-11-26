# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

added_files = [
    ('aria2c.exe', '.'),
    ('assets/logo.png', 'assets'),
    ('assets/icon.ico', 'assets'),
    ('assets/banner.png', 'assets'),
]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'aria2p',
        'requests',
        'base58',
        'Crypto',
        'Crypto.Cipher.AES',
        'Crypto.Protocol.KDF',
        'Crypto.Hash.SHA256',
        'urllib.request',
        'json',
        'zlib',
        're',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'pandas', 'IPython', 'playwright'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Produce onedir output directory (for clean Inno Setup packaging without Temp extraction)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FileKeeper-Downloader-FitGirl',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='FileKeeper-Downloader-FitGirl',
)
