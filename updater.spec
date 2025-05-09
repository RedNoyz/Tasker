# -*- mode: python ; coding: utf-8 -*-

BUILD_DEBUG = False

a = Analysis(
    ['updater.py'],
    pathex=[],
    binaries=[],
    datas=[('Assets', 'Assets'), ('src', 'src')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['utils/enable_debug.py'] if BUILD_DEBUG else [],
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
    name='updater',
    debug=BUILD_DEBUG,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=BUILD_DEBUG,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Assets/updater.ico',
)
