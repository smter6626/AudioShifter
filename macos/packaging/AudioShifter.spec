# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import sys


PACKAGING_DIR = Path(SPECPATH).resolve()
REPOSITORY_ROOT = PACKAGING_DIR.parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "macos" / "src"
sys.path.insert(0, str(PACKAGING_DIR))

from collect_macho_dependencies import pyinstaller_tool_binaries


analysis = Analysis(
    [str(PACKAGING_DIR / "entrypoint.py")],
    pathex=[str(SOURCE_ROOT)],
    binaries=pyinstaller_tool_binaries(),
    datas=[
        (str(REPOSITORY_ROOT / "macos" / "THIRD_PARTY_NOTICES.md"), "."),
        (str(REPOSITORY_ROOT / "macos" / "licenses"), "licenses"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(analysis.pure)

executable = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="AudioShifter",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch="arm64",
    codesign_identity=None,
    entitlements_file=None,
)

collection = COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    name="AudioShifter",
)

application = BUNDLE(
    collection,
    name="AudioShifter.app",
    icon=str(REPOSITORY_ROOT / "macos" / "assets" / "AudioShifter.icns"),
    bundle_identifier="io.github.smter6626.audioshifter",
    version="0.1.0",
    info_plist={
        "CFBundleDevelopmentRegion": "zh_CN",
        "CFBundleVersion": "1",
        "LSApplicationCategoryType": "public.app-category.music",
        "NSHighResolutionCapable": True,
    },
)
