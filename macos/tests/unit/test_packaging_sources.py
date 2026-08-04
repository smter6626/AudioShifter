# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Yeming Dai
from __future__ import annotations

from pathlib import Path

from macos.packaging.collect_macho_dependencies import collect_external_binaries


ROOT = Path(__file__).resolve().parents[3]


def test_PKG_T003_recursive_external_dependency_inventory_is_complete() -> None:
    items = collect_external_binaries()
    destinations = {item.destination for item in items}
    assert {"bin/ffmpeg", "bin/ffprobe", "bin/rubberband"} <= destinations
    assert len(destinations) == len(items)
    assert all(item.source.is_file() for item in items)
    assert all(not str(item.source).startswith(("/System/Library/", "/usr/lib/")) for item in items)


def test_PKG_T001_spec_is_arm64_windowed_and_stably_identified() -> None:
    spec = (ROOT / "macos" / "packaging" / "AudioShifter.spec").read_text(encoding="utf-8")
    assert 'console=False' in spec
    assert 'target_arch="arm64"' in spec
    assert 'codesign_identity=None' in spec
    assert 'bundle_identifier="io.github.smter6626.audioshifter"' in spec
    assert "AudioShifter.icns" in spec


def test_PKG_icon_and_license_sources_are_committed_resources() -> None:
    source = ROOT / "macos" / "assets" / "source" / "audioshifter_icon.png"
    icon = ROOT / "macos" / "assets" / "AudioShifter.icns"
    notices = ROOT / "macos" / "THIRD_PARTY_NOTICES.md"
    assert source.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert icon.read_bytes()[:4] == b"icns"
    assert notices.is_file()
    assert any((ROOT / "macos" / "licenses").iterdir())


def test_PKG_project_license_and_brand_sources_are_bundled_by_spec() -> None:
    spec = (ROOT / "macos" / "packaging" / "AudioShifter.spec").read_text(encoding="utf-8")
    for filename in ("LICENSE", "LICENSING.md", "TRADEMARKS.md", "THIRD_PARTY_NOTICES.md"):
        assert filename in spec
    assert '"macos" / "licenses"' in spec
    assert "BUNDLE_SHORT_VERSION" in spec
    assert "BUNDLE_VERSION" in spec
