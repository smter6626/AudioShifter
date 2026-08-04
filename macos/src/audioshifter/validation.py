"""Pure validation and normalization for processing requests."""

from __future__ import annotations

import os
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .errors import AppError, ErrorCode, app_error
from .models import ProcessingRequest, ProcessingStage


SUPPORTED_EXTENSIONS = frozenset({".mp3", ".m4a", ".wav", ".flac"})
_INTEGER_RE = re.compile(r"^[+-]?\d+$")
_DECIMAL_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$")


def parse_pitch(text: str) -> int:
    value = text.strip()
    if not value or not _INTEGER_RE.fullmatch(value):
        raise app_error(ErrorCode.INVALID_PITCH, details={"input": text})
    try:
        pitch = int(value, 10)
    except ValueError as exc:  # defensive: the regular expression already narrows this
        raise app_error(ErrorCode.INVALID_PITCH, details={"input": text}, cause=exc) from exc
    if not -24 <= pitch <= 24:
        raise app_error(ErrorCode.INVALID_PITCH, details={"input": text})
    return pitch


def parse_speed_change(text: str) -> Decimal:
    value = text.strip()
    if not value or "%" in value or not _DECIMAL_RE.fullmatch(value):
        raise app_error(ErrorCode.INVALID_SPEED, details={"input": text})
    try:
        speed = Decimal(value)
    except InvalidOperation as exc:
        raise app_error(ErrorCode.INVALID_SPEED, details={"input": text}, cause=exc) from exc
    if not speed.is_finite():
        raise app_error(ErrorCode.INVALID_SPEED, details={"input": text})
    if speed != 0 and value[0] not in "+-":
        raise app_error(ErrorCode.INVALID_SPEED, details={"input": text, "reason": "missing_sign"})
    if not Decimal("-95") <= speed <= Decimal("400"):
        raise app_error(ErrorCode.INVALID_SPEED, details={"input": text})
    return Decimal(0) if speed == 0 else speed


def compute_tempo_ratio(speed_change: Decimal) -> Decimal:
    return Decimal(1) + speed_change / Decimal(100)


def validate_input_path(path: str | Path) -> Path:
    input_path = Path(path).expanduser()
    if not input_path.exists():
        raise app_error(ErrorCode.INPUT_NOT_FOUND, stage=ProcessingStage.VALIDATING, details={"path": str(input_path)})
    if not input_path.is_file():
        raise app_error(ErrorCode.INPUT_NOT_FILE, stage=ProcessingStage.VALIDATING, details={"path": str(input_path)})
    if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise app_error(ErrorCode.UNSUPPORTED_INPUT, stage=ProcessingStage.VALIDATING, details={"extension": input_path.suffix})
    if not os.access(input_path, os.R_OK):
        raise app_error(ErrorCode.INPUT_NOT_READABLE, stage=ProcessingStage.VALIDATING, details={"path": str(input_path)})
    try:
        if input_path.stat().st_size == 0:
            raise app_error(ErrorCode.INVALID_INPUT_MEDIA, stage=ProcessingStage.VALIDATING, details={"path": str(input_path), "reason": "empty"})
    except OSError as exc:
        raise app_error(ErrorCode.INPUT_NOT_READABLE, stage=ProcessingStage.VALIDATING, details={"path": str(input_path)}, cause=exc) from exc
    return input_path.resolve()


def validate_downloads_path(path: str | Path) -> Path:
    downloads = Path(path).expanduser()
    if not downloads.exists():
        raise app_error(ErrorCode.DOWNLOADS_NOT_FOUND, stage=ProcessingStage.VALIDATING, details={"path": str(downloads)})
    if not downloads.is_dir():
        raise app_error(ErrorCode.DOWNLOADS_NOT_DIRECTORY, stage=ProcessingStage.VALIDATING, details={"path": str(downloads)})
    if not os.access(downloads, os.W_OK):
        raise app_error(ErrorCode.OUTPUT_PERMISSION_DENIED, stage=ProcessingStage.VALIDATING, details={"path": str(downloads)})
    return downloads.resolve()


def build_request(
    input_path: str | Path,
    pitch_text: str,
    speed_text: str,
    downloads_path: str | Path | None = None,
) -> ProcessingRequest:
    downloads = Path.home() / "Downloads" if downloads_path is None else Path(downloads_path)
    return ProcessingRequest(
        input_path=validate_input_path(input_path),
        pitch_semitones=parse_pitch(pitch_text),
        speed_change_percent=parse_speed_change(speed_text),
        downloads_path=validate_downloads_path(downloads),
    )
