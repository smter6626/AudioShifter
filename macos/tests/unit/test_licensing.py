# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Yeming Dai
from __future__ import annotations

import hashlib
import importlib.util
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RELEASE_DIR = ROOT / "macos" / "release"
OFFICIAL_GPL_V3_SHA256 = (
    "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986"
)
SPDX_HEADER = "SPDX-License-Identifier: GPL-3.0-or-later"
COPYRIGHT_HEADER = "Copyright (C) 2026 Yeming Dai"


def load_release_config():
    spec = importlib.util.spec_from_file_location(
        "release_config_licensing_test", RELEASE_DIR / "release_config.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_LIC_T001_root_license_is_unmodified_official_gpl_v3_text() -> None:
    payload = (ROOT / "LICENSE").read_bytes()
    assert len(payload) == 35_149
    assert hashlib.sha256(payload).hexdigest() == OFFICIAL_GPL_V3_SHA256
    assert payload.startswith(b"                    GNU GENERAL PUBLIC LICENSE\n")
    assert b"END OF TERMS AND CONDITIONS" in payload
    assert payload.endswith(b"<https://www.gnu.org/licenses/why-not-lgpl.html>.\n")


def test_LIC_T002_licensing_scope_covers_owned_code_and_exclusions() -> None:
    licensing = (ROOT / "LICENSING.md").read_text(encoding="utf-8")
    required = (
        "GPL-3.0-or-later",
        "Yeming Dai",
        "`macos/`",
        "`mobile/`",
        "`windows/`",
        "AudioShifter name",
        "macos/assets/source/audioshifter_icon.png",
        "macos/assets/AudioShifter.icns",
        "Third-party",
        "commercial",
    )
    assert all(value in licensing for value in required)


def test_LIC_T003_brand_policy_preserves_gpl_fork_rights_without_confusion() -> None:
    policy = (ROOT / "TRADEMARKS.md").read_text(encoding="utf-8")
    required = (
        "not claimed here to be a registered trademark",
        "must not continue to use `AudioShifter` as its product",
        "bundle identifier",
        "This is an unofficial fork based on AudioShifter.",
        "It is not affiliated with, endorsed by, or supported by the AudioShifter project.",
        "Based on AudioShifter",
        "Forked from AudioShifter",
        "Compatible with AudioShifter output",
        "commercially distribute",
        "official Release",
    )
    assert all(value in policy for value in required)
    forbidden = ("No commercial use", "Commercial use is prohibited", "No redistribution")
    assert all(value not in policy for value in forbidden)
    assert "Do not use the\nregistered-trademark symbol `®`" in policy


def test_LIC_T004_pyproject_uses_pep639_license_metadata() -> None:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        metadata = tomllib.load(handle)
    project = metadata["project"]
    assert metadata["build-system"]["requires"] == ["setuptools>=77"]
    assert project["version"] == "0.1.0a2"
    assert project["license"] == "GPL-3.0-or-later"
    assert set(project["license-files"]) == {
        "LICENSE",
        "LICENSING.md",
        "TRADEMARKS.md",
        "macos/THIRD_PARTY_NOTICES.md",
        "macos/licenses/*",
    }
    assert all(not value.startswith("License ::") for value in project["classifiers"])


def test_LIC_T005_release_identity_is_consistent() -> None:
    config = load_release_config()
    assert config.RELEASE_TAG == "v0.1.0-alpha.2"
    assert config.PYTHON_VERSION == "0.1.0a2"
    assert config.BUNDLE_SHORT_VERSION == "0.1.0-alpha.2"
    assert config.BUNDLE_VERSION == "2"
    assert config.app_asset_name() == "AudioShifter-v0.1.0-alpha.2-macOS27-arm64.zip"
    assert config.source_asset_name() == (
        "AudioShifter-v0.1.0-alpha.2-corresponding-source.tar.gz"
    )
    package_version = (ROOT / "macos" / "src" / "audioshifter" / "__init__.py").read_text(
        encoding="utf-8"
    )
    assert '__version__ = "0.1.0a2"' in package_version


def test_LIC_T006_principal_owned_code_and_build_tools_have_spdx_headers() -> None:
    candidates: list[Path] = []
    for directory in (
        ROOT / "macos" / "src",
        ROOT / "macos" / "tests",
        ROOT / "macos" / "packaging",
        ROOT / "macos" / "release",
    ):
        candidates.extend(directory.rglob("*.py"))
        candidates.extend(directory.rglob("*.sh"))
    candidates.append(ROOT / "macos" / "packaging" / "AudioShifter.spec")
    candidates.extend(
        (ROOT / filename)
        for filename in ("pyproject.toml", "macos/Brewfile", "macos/requirements-dev.txt")
    )
    assert candidates
    for candidate in candidates:
        first_lines = candidate.read_text(encoding="utf-8").splitlines()[:5]
        assert any(SPDX_HEADER in line for line in first_lines), candidate
        assert any(COPYRIGHT_HEADER in line for line in first_lines), candidate


def test_LIC_T007_windows_history_is_explicitly_outside_project_license() -> None:
    licensing = (ROOT / "LICENSING.md").read_text(encoding="utf-8")
    assert "All content under `windows/`" in licensing
    assert "is not offered under the project GPL grant" in licensing
