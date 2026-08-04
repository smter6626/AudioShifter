# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Yeming Dai
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

from audioshifter.legal import (
    GPL_V3_SHA256,
    LicenseResourceError,
    complete_window_text,
    license_candidates,
    license_intro,
    load_license_document,
    locate_license_file,
)


ROOT = Path(__file__).resolve().parents[3]


def test_LEGAL_T001_source_runtime_locates_root_license_without_cwd(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    path = locate_license_file()
    assert path == ROOT / "LICENSE"


def test_LEGAL_T002_license_is_complete_verified_gpl_text() -> None:
    document = load_license_document()
    expected = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert document.text == expected
    assert document.sha256 == GPL_V3_SHA256
    assert hashlib.sha256(document.text.encode("utf-8")).hexdigest() == GPL_V3_SHA256
    assert all(
        marker in document.text
        for marker in (
            "GNU GENERAL PUBLIC LICENSE",
            "Version 3, 29 June 2007",
            "END OF TERMS AND CONDITIONS",
        )
    )
    assert "[truncated]" not in document.text.lower()
    assert "…" not in document.text


def test_LEGAL_T003_window_text_has_english_intro_and_unmodified_full_body() -> None:
    document = load_license_document()
    rendered = complete_window_text(document)
    assert rendered.startswith("AudioShifter 0.1.0-alpha.3\nCopyright (C) 2026 Yeming Dai")
    assert "The complete GNU GPL version 3 text follows." in rendered
    assert rendered.endswith(document.text)
    assert rendered.removeprefix(f"{license_intro()}\n\n") == document.text


def test_LEGAL_T004_frozen_runtime_prefers_contents_resources(monkeypatch, tmp_path) -> None:
    contents = tmp_path / "AudioShifter.app" / "Contents"
    executable = contents / "MacOS" / "AudioShifter"
    resource_license = contents / "Resources" / "LICENSE"
    executable.parent.mkdir(parents=True)
    resource_license.parent.mkdir(parents=True)
    executable.touch()
    resource_license.write_bytes((ROOT / "LICENSE").read_bytes())
    fallback = tmp_path / "Frameworks"
    fallback.mkdir()
    (fallback / "LICENSE").write_text("not the complete licence", encoding="utf-8")

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(executable))
    monkeypatch.setattr(sys, "_MEIPASS", str(fallback), raising=False)
    assert license_candidates()[0] == resource_license
    assert locate_license_file() == resource_license
    assert load_license_document().sha256 == GPL_V3_SHA256


def test_LEGAL_T005_missing_or_modified_license_fails_without_summary_fallback(tmp_path) -> None:
    missing = tmp_path / "LICENSE"
    with pytest.raises(LicenseResourceError, match="could not be read"):
        load_license_document(missing)
    modified = tmp_path / "modified-LICENSE"
    modified.write_text("GNU GENERAL PUBLIC LICENSE\nsummary only", encoding="utf-8")
    with pytest.raises(LicenseResourceError, match="integrity check"):
        load_license_document(modified)
