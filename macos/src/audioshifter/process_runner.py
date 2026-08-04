"""Safe subprocess execution with process-group cancellation and diagnostics."""

from __future__ import annotations

import os
import signal
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .errors import ErrorCode, app_error
from .models import ProcessingStage


@dataclass(frozen=True, slots=True)
class ProcessResult:
    args: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float
    cancelled: bool = False


class CancellationToken:
    def __init__(self) -> None:
        self._event = threading.Event()

    def cancel(self) -> None:
        self._event.set()

    @property
    def cancelled(self) -> bool:
        return self._event.is_set()


def _decode(data: bytes | None) -> str:
    return (data or b"").decode("utf-8", errors="replace")


class ProcessRunner:
    def __init__(self, *, poll_interval: float = 0.05, terminate_grace: float = 1.0) -> None:
        self._poll_interval = poll_interval
        self._terminate_grace = terminate_grace
        self._active_lock = threading.Lock()
        self._active: subprocess.Popen[bytes] | None = None

    @property
    def active_pid(self) -> int | None:
        with self._active_lock:
            return None if self._active is None else self._active.pid

    def run(
        self,
        args: Sequence[str | Path],
        *,
        token: CancellationToken,
        stage: ProcessingStage,
        cwd: Path | None = None,
    ) -> ProcessResult:
        command = tuple(str(argument) for argument in args)
        if token.cancelled:
            raise app_error(ErrorCode.CANCELLED, stage=stage, details={"args": command})
        started = time.monotonic()
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                start_new_session=True,
                close_fds=True,
            )
        except FileNotFoundError as exc:
            raise app_error(
                ErrorCode.DEPENDENCY_MISSING,
                stage=stage,
                details={"executable": command[0], "args": command},
                cause=exc,
            ) from exc
        except PermissionError as exc:
            raise app_error(
                ErrorCode.DEPENDENCY_NOT_EXECUTABLE,
                stage=stage,
                details={"executable": command[0], "args": command},
                cause=exc,
            ) from exc

        with self._active_lock:
            self._active = process
        try:
            while True:
                if token.cancelled:
                    self._terminate_group(process)
                    stdout, stderr = process.communicate()
                    raise app_error(
                        ErrorCode.CANCELLED,
                        stage=stage,
                        details={
                            "args": command,
                            "returncode": process.returncode,
                            "stdout": _decode(stdout),
                            "stderr": _decode(stderr),
                        },
                    )
                try:
                    stdout, stderr = process.communicate(timeout=self._poll_interval)
                    break
                except subprocess.TimeoutExpired:
                    continue
        finally:
            with self._active_lock:
                if self._active is process:
                    self._active = None
        return ProcessResult(
            args=command,
            returncode=process.returncode,
            stdout=_decode(stdout),
            stderr=_decode(stderr),
            duration_seconds=time.monotonic() - started,
        )

    def _terminate_group(self, process: subprocess.Popen[bytes]) -> None:
        if process.poll() is not None:
            return
        group_id = process.pid
        try:
            os.killpg(group_id, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=self._terminate_grace)
        except subprocess.TimeoutExpired:
            pass
        deadline = time.monotonic() + self._terminate_grace
        while time.monotonic() < deadline:
            try:
                os.killpg(group_id, 0)
            except ProcessLookupError:
                return
            time.sleep(min(self._poll_interval, 0.05))
        try:
            os.killpg(group_id, signal.SIGKILL)
        except ProcessLookupError:
            pass
        if process.poll() is None:
            process.wait()
