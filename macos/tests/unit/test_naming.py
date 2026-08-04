from decimal import Decimal
from pathlib import Path

import pytest

from audioshifter.models import ProcessingRequest
from audioshifter.naming import allocate_output, build_base_filename


def request(tmp_path: Path, name: str, pitch: int, speed: str) -> ProcessingRequest:
    return ProcessingRequest(tmp_path / name, pitch, Decimal(speed), tmp_path)


@pytest.mark.parametrize(
    ("case_id", "name", "pitch", "speed", "expected"),
    [
        ("NAME-T001", "name.mp3", 3, "20", "name+3+20%.mp3"),
        ("NAME-T002", "name.wav", -3, "-20", "name-3-20%.mp3"),
        ("NAME-T003", "name.flac", 3, "-12.5", "name+3-12.5%.mp3"),
        ("NAME-T004", "name.m4a", -2, "30.25", "name-2+30.25%.mp3"),
        ("NAME-T005", "name.mp3", 0, "0", "name+0+0%.mp3"),
        ("NAME-T006", "name.mp3", 1, "20.0", "name+1+20%.mp3"),
        ("NAME-T007", "name.mp3", 1, "-7.500", "name+1-7.5%.mp3"),
        ("NAME-T008", "song.final.v2.mp3", 0, "0", "song.final.v2+0+0%.mp3"),
        ("NAME-T009", "中文 音频.wav", 3, "-20", "中文 音频+3-20%.mp3"),
    ],
)
def test_filename_contract(
    tmp_path: Path,
    case_id: str,
    name: str,
    pitch: int,
    speed: str,
    expected: str,
) -> None:
    assert build_base_filename(request(tmp_path, name, pitch, speed)) == expected


def test_NAME_T010_uses_free_base_path(tmp_path: Path) -> None:
    allocation = allocate_output(request(tmp_path, "name.mp3", 3, "20"))
    assert allocation.output_path.name == "name+3+20%.mp3"
    assert allocation.had_conflict is False
    assert allocation.sequence == 1


def test_NAME_T011_uses_suffix_2_without_overwrite(tmp_path: Path) -> None:
    existing = tmp_path / "name+3+20%.mp3"
    existing.write_bytes(b"keep")
    allocation = allocate_output(request(tmp_path, "name.mp3", 3, "20"))
    assert allocation.output_path.name == "name+3+20%_2.mp3"
    assert allocation.had_conflict is True
    assert existing.read_bytes() == b"keep"


def test_NAME_T012_uses_suffix_3_without_overwrite(tmp_path: Path) -> None:
    (tmp_path / "name+3+20%.mp3").write_bytes(b"one")
    (tmp_path / "name+3+20%_2.mp3").write_bytes(b"two")
    allocation = allocate_output(request(tmp_path, "name.mp3", 3, "20"))
    assert allocation.output_path.name == "name+3+20%_3.mp3"
    assert allocation.sequence == 3
