# -*- mode: python ; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Yeming Dai

from pathlib import Path
import sys


PACKAGING_DIR = Path(SPECPATH).resolve()
REPOSITORY_ROOT = PACKAGING_DIR.parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "macos" / "src"
sys.path.insert(0, str(PACKAGING_DIR))
sys.path.insert(0, str(REPOSITORY_ROOT / "macos" / "release"))

from collect_macho_dependencies import pyinstaller_tool_binaries
from release_config import BUNDLE_SHORT_VERSION, BUNDLE_VERSION


analysis = Analysis(
    [str(PACKAGING_DIR / "entrypoint.py")],
    pathex=[str(SOURCE_ROOT)],
    binaries=pyinstaller_tool_binaries(),
    datas=[
        (str(REPOSITORY_ROOT / "LICENSE"), "."),
        (str(REPOSITORY_ROOT / "LICENSING.md"), "."),
        (str(REPOSITORY_ROOT / "TRADEMARKS.md"), "."),
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
    version=BUNDLE_SHORT_VERSION,
    info_plist={
        "CFBundleDevelopmentRegion": "zh_CN",
        "CFBundleVersion": BUNDLE_VERSION,
        "LSApplicationCategoryType": "public.app-category.music",
        "NSHighResolutionCapable": True,
    },
)
