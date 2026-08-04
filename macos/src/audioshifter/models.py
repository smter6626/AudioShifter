"""Immutable data exchanged between the GUI, controller, and pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Mapping


class ProcessingStage(str, Enum):
    IDLE = "idle"
    VALIDATING = "validating"
    ALLOCATING_OUTPUT = "allocating_output"
    PREPARING_WORKSPACE = "preparing_workspace"
    DECODING = "decoding"
    PROCESSING = "processing"
    ENCODING = "encoding"
    VERIFYING_OUTPUT = "verifying_output"
    CLEANING_UP = "cleaning_up"
    SUCCEEDED = "succeeded"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TerminalStatus(str, Enum):
    SUCCEEDED = "succeeded"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class ProcessingRequest:
    input_path: Path
    pitch_semitones: int
    speed_change_percent: Decimal
    downloads_path: Path


@dataclass(frozen=True, slots=True)
class OutputAllocation:
    base_path: Path
    output_path: Path
    had_conflict: bool
    sequence: int

    @property
    def needs_notification(self) -> bool:
        return self.had_conflict


@dataclass(frozen=True, slots=True)
class ProcessingResult:
    output_path: Path
    input_path: Path
    pitch_semitones: int
    speed_change_percent: Decimal
    tempo_ratio: Decimal
    warnings: tuple[str, ...] = ()
    diagnostics: Mapping[str, Any] = field(default_factory=dict)
    allocation: OutputAllocation | None = None


@dataclass(frozen=True, slots=True)
class ProgressEvent:
    stage: ProcessingStage
    message: str


@dataclass(frozen=True, slots=True)
class MediaInfo:
    codec_name: str
    sample_rate: int
    channels: int
    duration_seconds: Decimal
    bit_rate: int | None
    format_name: str
