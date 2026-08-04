# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Yeming Dai
"""Stable output naming and no-overwrite allocation."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from .models import OutputAllocation, ProcessingRequest


def format_pitch(pitch: int) -> str:
    return f"{pitch:+d}"


def format_decimal(value: Decimal) -> str:
    normalized = Decimal(0) if value == 0 else value.normalize()
    return format(normalized, "f")


def format_speed(speed: Decimal) -> str:
    normalized = Decimal(0) if speed == 0 else speed
    prefix = "+" if normalized >= 0 else ""
    return f"{prefix}{format_decimal(normalized)}"


def build_base_filename(request: ProcessingRequest) -> str:
    return (
        f"{request.input_path.stem}"
        f"{format_pitch(request.pitch_semitones)}"
        f"{format_speed(request.speed_change_percent)}%.mp3"
    )


def find_available_output(downloads_path: Path, base_filename: str) -> OutputAllocation:
    base_path = downloads_path / base_filename
    if not base_path.exists():
        return OutputAllocation(base_path, base_path, False, 1)
    sequence = 2
    while True:
        candidate = base_path.with_name(f"{base_path.stem}_{sequence}{base_path.suffix}")
        if not candidate.exists():
            return OutputAllocation(base_path, candidate, True, sequence)
        sequence += 1


def allocate_output(request: ProcessingRequest) -> OutputAllocation:
    return find_available_output(request.downloads_path, build_base_filename(request))


def revalidate_output_allocation(allocation: OutputAllocation) -> OutputAllocation:
    if not allocation.output_path.exists():
        return allocation
    return find_available_output(allocation.base_path.parent, allocation.base_path.name)
