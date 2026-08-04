# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Yeming Dai
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
RELEASE_DIR = REPOSITORY_ROOT / "macos" / "release"


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, RELEASE_DIR / filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_release_inventory_has_22_unique_runtime_components(monkeypatch) -> None:
    monkeypatch.syspath_prepend(str(RELEASE_DIR))
    manifest = load_module("release_manifest_test", "release_manifest.py")
    assert len(manifest.COMPONENTS) == 22
    assert len({component.key for component in manifest.COMPONENTS}) == 22
    assert all(component.patterns for component in manifest.COMPONENTS)


def test_release_inventory_tracks_exact_homebrew_formula_set(monkeypatch) -> None:
    monkeypatch.syspath_prepend(str(RELEASE_DIR))
    manifest = load_module("release_manifest_formula_test", "release_manifest.py")
    assert set(manifest.FORMULAE) == {
        "python@3.11",
        "python-tk@3.11",
        "tcl-tk@8",
        "mpdecimal",
        "xz",
        "ffmpeg",
        "rubberband",
        "libvmaf",
        "openssl@3",
        "libvpx",
        "dav1d",
        "lame",
        "opus",
        "svt-av1",
        "x264",
        "x265",
        "libsamplerate",
        "libsndfile",
        "mpg123",
        "libogg",
        "libvorbis",
        "flac",
    }


def test_formula_patch_parsing_captures_local_and_verified_remote(monkeypatch) -> None:
    monkeypatch.syspath_prepend(str(RELEASE_DIR))
    collector = load_module("release_collector_test", "collect_corresponding_source.py")
    formula = '''
    patch do
      url "https://example.test/fix.patch"
      sha256 "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    end
    def install
      patch :DATA
      system "cp", Formula["python"].opt_prefix/"Patches/python/fix.diff", buildpath
      resource("x").stage { cp Formula["x"].path/"Patches/python/other.patch", buildpath }
    end
    '''
    assert collector.formula_patch_blocks(formula) == (
        (
            "https://example.test/fix.patch",
            "a" * 64,
        ),
    )
    assert collector.local_formula_patches(formula) == (
        "Patches/python/fix.diff",
        "Patches/python/other.patch",
    )


def test_source_filter_recognises_compiled_formats(monkeypatch) -> None:
    monkeypatch.syspath_prepend(str(RELEASE_DIR))
    collector = load_module("release_binary_filter_test", "collect_corresponding_source.py")
    assert collector.is_compiled_magic(b"\x7fELF\x02\x01\x01\x00")
    assert collector.is_compiled_magic(b"\xcf\xfa\xed\xfe\x0c\x00\x00\x01")
    assert collector.is_compiled_magic(b"MZ\x90\x00\x03\x00\x00\x00")
    assert collector.is_compiled_magic(b"!<arch>\n")
    assert not collector.is_compiled_magic(b"#!/bin/sh")


def test_release_notes_include_platform_gatekeeper_and_three_assets() -> None:
    notes = (RELEASE_DIR / "release_notes_v0.1.0-alpha.3.md").read_text(encoding="utf-8")
    required = (
        "macOS 27.0 build `26A5378n`",
        "Apple Silicon `arm64` only",
        "ad-hoc signing",
        "未使用 Apple Developer ID",
        "系统设置 → 隐私与安全性 → 仍要打开",
        "AudioShifter-v0.1.0-alpha.3-macOS27-arm64.zip",
        "AudioShifter-v0.1.0-alpha.3-corresponding-source.tar.gz",
        "SHA256SUMS.txt",
        "shasum -a 256 -c SHA256SUMS.txt",
        "GPL-3.0-or-later",
        "not licensed under the GPL",
        "commercial use and distribution",
        "different name and icon",
        "Corrected macOS bundle version metadata.",
        "AudioShifter menu → License",
        "complete English GNU GPL version 3 text",
        "ordinary users do not need to download",
        "It is not required to run the app.",
        "official AudioShifter tag",
        "grep 'AudioShifter-v0.1.0-alpha.3-macOS27-arm64.zip$' SHA256SUMS.txt",
    )
    assert all(value in notes for value in required)


def test_release_docs_do_not_require_ordinary_users_to_download_source() -> None:
    current_documents = (
        REPOSITORY_ROOT / "README.md",
        REPOSITORY_ROOT / "macos" / "README.md",
        RELEASE_DIR / "README.md",
        RELEASE_DIR / "release_notes_v0.1.0-alpha.3.md",
    )
    for path in current_documents:
        text = path.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        assert "普通用户" in normalized or "Ordinary users" in normalized
        assert "AudioShifter-v0.1.0-alpha.3-macOS27-arm64.zip" in normalized
        assert "corresponding-source" in normalized
        assert "not required to run the app" in normalized or "不是运行应用所必需" in normalized
        assert "下载三个文件" not in normalized


def test_release_configuration_is_the_single_alpha3_identity_source(monkeypatch) -> None:
    monkeypatch.syspath_prepend(str(RELEASE_DIR))
    config = load_module("release_config_test", "release_config.py")
    assert config.RELEASE_TAG == "v0.1.0-alpha.3"
    assert config.RELEASE_TITLE == "AudioShifter v0.1.0-alpha.3 — macOS arm64 preview"
    assert config.app_asset_name() == "AudioShifter-v0.1.0-alpha.3-macOS27-arm64.zip"
    assert config.source_asset_name() == (
        "AudioShifter-v0.1.0-alpha.3-corresponding-source.tar.gz"
    )


def test_release_build_uses_ditto_and_atomic_staging() -> None:
    script = (RELEASE_DIR / "build_release_assets.sh").read_text(encoding="utf-8")
    assert "ditto -c -k --sequesterRsrc --keepParent" in script
    assert "zip -r" not in script
    assert "release-work/staging" not in script  # built from anchored variables
    assert "git status --porcelain" in script
    assert "git worktree add --detach" in script
    assert "verify_release_assets.py" in script
    assert "release_config.py" in script
    assert 'TAG="${1:-}"' in script


def test_release_ignore_rules_are_precise() -> None:
    ignores = (REPOSITORY_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "/macos/release-work/" in ignores
    assert "/macos/release-dist/" in ignores
    assert "*.zip" not in ignores
    assert "*.tar.gz" not in ignores
