"""Per-task temporary workspace with guarded cleanup."""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .errors import AppError, ErrorCode, app_error
from .models import ProcessingStage


_PREFIX = "AudioShifter-"


@dataclass(slots=True)
class TaskWorkspace:
    path: Path
    temporary_root: Path

    @classmethod
    def create(cls) -> "TaskWorkspace":
        root = Path(tempfile.gettempdir()).resolve()
        path = Path(tempfile.mkdtemp(prefix=_PREFIX, dir=root))
        return cls(path=path, temporary_root=root)

    @property
    def decoded_path(self) -> Path:
        return self.path / "decoded.wav"

    @property
    def processed_path(self) -> Path:
        return self.path / "processed.wav"

    def _is_safe(self) -> bool:
        try:
            resolved = self.path.resolve(strict=False)
            return (
                resolved.parent == self.temporary_root.resolve()
                and resolved.name.startswith(_PREFIX)
                and resolved != self.temporary_root.resolve()
            )
        except OSError:
            return False

    def cleanup(self) -> AppError | None:
        if not self._is_safe():
            raise ValueError(f"Refusing unsafe workspace cleanup: {self.path}")
        if not self.path.exists():
            return None
        try:
            shutil.rmtree(self.path)
        except OSError as exc:
            return app_error(
                ErrorCode.CLEANUP_WARNING,
                stage=ProcessingStage.CLEANING_UP,
                details={"workspace": str(self.path)},
                cause=exc,
            )
        return None

    def __enter__(self) -> "TaskWorkspace":
        return self

    def __exit__(self, *_: object) -> None:
        self.cleanup()
