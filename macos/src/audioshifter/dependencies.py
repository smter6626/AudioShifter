"""Resolve external audio tools without leaking development paths upward."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Protocol

from .errors import ErrorCode, app_error


@dataclass(frozen=True, slots=True)
class ResolvedDependencies:
    ffmpeg_path: Path
    ffprobe_path: Path
    rubberband_path: Path


class DependencyResolver(Protocol):
    def resolve(self) -> ResolvedDependencies: ...


def validate_executable(path: str | Path | None, component: str) -> Path:
    if path is None:
        raise app_error(ErrorCode.DEPENDENCY_MISSING, details={"component": component})
    candidate = Path(path).expanduser()
    if not candidate.exists() or not candidate.is_file():
        raise app_error(
            ErrorCode.DEPENDENCY_MISSING,
            details={"component": component, "path": str(candidate)},
        )
    if not os.access(candidate, os.X_OK):
        raise app_error(
            ErrorCode.DEPENDENCY_NOT_EXECUTABLE,
            details={"component": component, "path": str(candidate)},
        )
    return candidate.resolve()


class DevelopmentDependencyResolver:
    """Resolve the verified developer tools from PATH or explicit test overrides."""

    def __init__(self, overrides: Mapping[str, str | Path] | None = None) -> None:
        self._overrides = dict(overrides or {})

    def _find(self, name: str) -> str | Path | None:
        return self._overrides.get(name) or shutil.which(name)

    def resolve(self) -> ResolvedDependencies:
        return ResolvedDependencies(
            ffmpeg_path=validate_executable(self._find("ffmpeg"), "FFmpeg"),
            ffprobe_path=validate_executable(self._find("ffprobe"), "FFprobe"),
            rubberband_path=validate_executable(self._find("rubberband"), "Rubber Band"),
        )


class PackagedDependencyResolver:
    """Future PyInstaller strategy; the packaging step supplies the resource root."""

    def __init__(self, resource_root: Path) -> None:
        self._bin_dir = resource_root / "bin"

    def resolve(self) -> ResolvedDependencies:
        return ResolvedDependencies(
            ffmpeg_path=validate_executable(self._bin_dir / "ffmpeg", "FFmpeg"),
            ffprobe_path=validate_executable(self._bin_dir / "ffprobe", "FFprobe"),
            rubberband_path=validate_executable(self._bin_dir / "rubberband", "Rubber Band"),
        )
