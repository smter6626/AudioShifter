from __future__ import annotations

import os
from decimal import Decimal

import pytest

from audioshifter.errors import AppError, ErrorCode
from audioshifter.validation import (
    compute_tempo_ratio,
    parse_pitch,
    parse_speed_change,
    validate_downloads_path,
    validate_input_path,
)


@pytest.mark.parametrize(
    ("case_id", "text", "expected"),
    [
        ("PITCH-T001", "0", 0),
        ("PITCH-T002", "3", 3),
        ("PITCH-T003", "+3", 3),
        ("PITCH-T004", "-3", -3),
        ("PITCH-T005", "  +3  ", 3),
        ("PITCH-T010", "-24", -24),
        ("PITCH-T011", "+24", 24),
    ],
    ids=lambda value: value if isinstance(value, str) and "PITCH-T" in value else None,
)
def test_pitch_contract_accepts(case_id: str, text: str, expected: int) -> None:
    assert parse_pitch(text) == expected


@pytest.mark.parametrize(
    ("case_id", "text"),
    [
        ("PITCH-T006", "1.5"),
        ("PITCH-T007", ""),
        ("PITCH-T008", "abc"),
        ("PITCH-T009-NaN", "NaN"),
        ("PITCH-T009-Infinity", "Infinity"),
        ("PITCH-T012", "-25"),
        ("PITCH-T013", "+25"),
    ],
)
def test_pitch_contract_rejects(case_id: str, text: str) -> None:
    with pytest.raises(AppError) as caught:
        parse_pitch(text)
    assert caught.value.code is ErrorCode.INVALID_PITCH


@pytest.mark.parametrize(
    ("case_id", "text", "expected", "ratio"),
    [
        ("SPEED-T001", "0", Decimal("0"), Decimal("1")),
        ("SPEED-T002", "+20", Decimal("20"), Decimal("1.2")),
        ("SPEED-T003", "-20", Decimal("-20"), Decimal("0.8")),
        ("SPEED-T004", "+12.5", Decimal("12.5"), Decimal("1.125")),
        ("SPEED-T005", "-7.500", Decimal("-7.500"), Decimal("0.925")),
        ("SPEED-T006-plus", "+0", Decimal("0"), Decimal("1")),
        ("SPEED-T006-minus", "-0", Decimal("0"), Decimal("1")),
        ("SPEED-T011", "-95", Decimal("-95"), Decimal("0.05")),
        ("SPEED-T012", "+400", Decimal("400"), Decimal("5")),
    ],
)
def test_speed_contract_accepts(
    case_id: str, text: str, expected: Decimal, ratio: Decimal
) -> None:
    parsed = parse_speed_change(text)
    assert parsed == expected
    assert compute_tempo_ratio(parsed) == ratio


@pytest.mark.parametrize(
    ("case_id", "text"),
    [
        ("SPEED-T007", "20%"),
        ("SPEED-T008", "20"),
        ("SPEED-T009-empty", ""),
        ("SPEED-T009-text", "abc"),
        ("SPEED-T009-sign", "+"),
        ("SPEED-T010-NaN", "NaN"),
        ("SPEED-T010-Infinity", "Infinity"),
        ("SPEED-T013", "-95.01"),
        ("SPEED-T014", "+400.01"),
    ],
)
def test_speed_contract_rejects(case_id: str, text: str) -> None:
    with pytest.raises(AppError) as caught:
        parse_speed_change(text)
    assert caught.value.code is ErrorCode.INVALID_SPEED


@pytest.mark.parametrize("extension", [".MP3", ".M4A", ".WAV", ".FLAC"])
def test_IN_T005_uppercase_extensions(tmp_path, extension: str) -> None:
    source = tmp_path / f"audio{extension}"
    source.write_bytes(b"not-empty")
    assert validate_input_path(source) == source.resolve()


def test_IN_T006_unpromised_extension_is_rejected(tmp_path) -> None:
    source = tmp_path / "audio.aac"
    source.write_bytes(b"not-empty")
    with pytest.raises(AppError) as caught:
        validate_input_path(source)
    assert caught.value.code is ErrorCode.UNSUPPORTED_INPUT


def test_IN_T007_missing_path(tmp_path) -> None:
    with pytest.raises(AppError) as caught:
        validate_input_path(tmp_path / "missing.mp3")
    assert caught.value.code is ErrorCode.INPUT_NOT_FOUND


def test_IN_T008_directory_is_rejected(tmp_path) -> None:
    with pytest.raises(AppError) as caught:
        validate_input_path(tmp_path)
    assert caught.value.code is ErrorCode.INPUT_NOT_FILE


def test_IN_T009_unreadable_file(tmp_path, monkeypatch) -> None:
    source = tmp_path / "audio.mp3"
    source.write_bytes(b"content")
    real_access = os.access

    def fake_access(path, mode):
        if os.fspath(path) == os.fspath(source) and mode == os.R_OK:
            return False
        return real_access(path, mode)

    monkeypatch.setattr(os, "access", fake_access)
    with pytest.raises(AppError) as caught:
        validate_input_path(source)
    assert caught.value.code is ErrorCode.INPUT_NOT_READABLE


def test_IN_T010_zero_byte_file_is_rejected(tmp_path) -> None:
    source = tmp_path / "empty.flac"
    source.touch()
    with pytest.raises(AppError) as caught:
        validate_input_path(source)
    assert caught.value.code is ErrorCode.INVALID_INPUT_MEDIA


def test_OUT_T003_missing_downloads_is_rejected(tmp_path) -> None:
    with pytest.raises(AppError) as caught:
        validate_downloads_path(tmp_path / "Downloads")
    assert caught.value.code is ErrorCode.DOWNLOADS_NOT_FOUND


def test_OUT_T004_downloads_file_is_rejected(tmp_path) -> None:
    downloads = tmp_path / "Downloads"
    downloads.write_text("not a directory")
    with pytest.raises(AppError) as caught:
        validate_downloads_path(downloads)
    assert caught.value.code is ErrorCode.DOWNLOADS_NOT_DIRECTORY


def test_OUT_T005_unwritable_downloads_is_rejected(tmp_path, monkeypatch) -> None:
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    real_access = os.access

    def fake_access(path, mode):
        if os.fspath(path) == os.fspath(downloads) and mode == os.W_OK:
            return False
        return real_access(path, mode)

    monkeypatch.setattr(os, "access", fake_access)
    with pytest.raises(AppError) as caught:
        validate_downloads_path(downloads)
    assert caught.value.code is ErrorCode.OUTPUT_PERMISSION_DENIED
