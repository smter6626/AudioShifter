"""Rubber Band pitch and tempo processing adapter."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from .dependencies import ResolvedDependencies
from .errors import ErrorCode, app_error
from .models import ProcessingStage
from .naming import format_decimal
from .process_runner import CancellationToken, ProcessRunner


class RubberBandAdapter:
    def __init__(self, dependencies: ResolvedDependencies, runner: ProcessRunner) -> None:
        self._dependencies = dependencies
        self._runner = runner

    def process(
        self,
        source: Path,
        destination: Path,
        *,
        pitch_semitones: int,
        tempo_ratio: Decimal,
        token: CancellationToken,
    ) -> None:
        result = self._runner.run(
            [
                self._dependencies.rubberband_path,
                "--pitch",
                str(pitch_semitones),
                "--tempo",
                format_decimal(tempo_ratio),
                "--fine",
                "--formant",
                source,
                destination,
            ],
            token=token,
            stage=ProcessingStage.PROCESSING,
        )
        if result.returncode != 0:
            raise app_error(
                ErrorCode.PROCESS_FAILED,
                stage=ProcessingStage.PROCESSING,
                details={
                    "args": result.args,
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                },
            )
        if not destination.is_file() or destination.stat().st_size == 0:
            raise app_error(
                ErrorCode.PROCESS_FAILED,
                stage=ProcessingStage.PROCESSING,
                details={"destination": str(destination), "reason": "missing_or_empty"},
            )
