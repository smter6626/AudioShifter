# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


WINDOWS_DIR = Path(SPECPATH).parent
SOURCE_DIR = WINDOWS_DIR / 'src'
LOCAL_BIN_DIR = WINDOWS_DIR / '_local_artifacts' / 'bin'

a = Analysis(
    [str(SOURCE_DIR / 'shifter_gui.py')],
    pathex=[str(SOURCE_DIR)],
    binaries=[],
    datas=[
        (str(LOCAL_BIN_DIR / 'ffmpeg.exe'), '.'),
        (str(LOCAL_BIN_DIR / 'rubberband.exe'), '.'),
        (str(LOCAL_BIN_DIR / 'sndfile.dll'), '.'),
    ],
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
    name='MyAudioShifter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
