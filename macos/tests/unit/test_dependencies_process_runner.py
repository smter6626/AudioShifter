from __future__ import annotations

import os
import signal
import sys
import threading
import time
from pathlib import Path

import pytest

from audioshifter.dependencies import DevelopmentDependencyResolver, validate_executable
from audioshifter.errors import AppError, ErrorCode
from audioshifter.models import ProcessingStage
from audioshifter.process_runner import CancellationToken, ProcessRunner


def test_DEP_T001_missing_dependency_has_stable_error(tmp_path: Path) -> None:
    with pytest.raises(AppError) as caught:
        validate_executable(tmp_path / "missing", "FFmpeg")
    assert caught.value.code is ErrorCode.DEPENDENCY_MISSING


def test_DEP_T003_non_executable_dependency_has_stable_error(tmp_path: Path) -> None:
    executable = tmp_path / "tool"
    executable.write_text("tool")
    executable.chmod(0o644)
    with pytest.raises(AppError) as caught:
        validate_executable(executable, "Rubber Band")
    assert caught.value.code is ErrorCode.DEPENDENCY_NOT_EXECUTABLE


def test_DEP_T009_development_resolver_finds_verified_tools() -> None:
    dependencies = DevelopmentDependencyResolver().resolve()
    assert dependencies.ffmpeg_path.is_file()
    assert dependencies.ffprobe_path.is_file()
    assert dependencies.rubberband_path.is_file()


def test_process_runner_success_and_stderr_capture() -> None:
    runner = ProcessRunner()
    result = runner.run(
        [sys.executable, "-c", "import sys; print('out'); print('err', file=sys.stderr)"],
        token=CancellationToken(),
        stage=ProcessingStage.DECODING,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "out"
    assert result.stderr.strip() == "err"


def test_process_runner_returns_nonzero_diagnostics() -> None:
    result = ProcessRunner().run(
        [sys.executable, "-c", "import sys; print('bad', file=sys.stderr); raise SystemExit(7)"],
        token=CancellationToken(),
        stage=ProcessingStage.PROCESSING,
    )
    assert result.returncode == 7
    assert "bad" in result.stderr


def test_DEP_T008_non_utf8_output_is_replaced_not_crashed() -> None:
    result = ProcessRunner().run(
        [sys.executable, "-c", "import os; os.write(2, bytes([255, 254]))"],
        token=CancellationToken(),
        stage=ProcessingStage.PROCESSING,
    )
    assert result.returncode == 0
    assert "\ufffd" in result.stderr


def test_process_runner_missing_command_maps_error(tmp_path: Path) -> None:
    with pytest.raises(AppError) as caught:
        ProcessRunner().run(
            [tmp_path / "missing-command"],
            token=CancellationToken(),
            stage=ProcessingStage.DECODING,
        )
    assert caught.value.code is ErrorCode.DEPENDENCY_MISSING


def test_process_runner_non_executable_maps_error(tmp_path: Path) -> None:
    command = tmp_path / "not-executable"
    command.write_text("content")
    command.chmod(0o644)
    with pytest.raises(AppError) as caught:
        ProcessRunner().run(
            [command], token=CancellationToken(), stage=ProcessingStage.DECODING
        )
    assert caught.value.code is ErrorCode.DEPENDENCY_NOT_EXECUTABLE


def _pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def test_TASK_T005_cancel_kills_process_group_and_reaps_children(tmp_path: Path) -> None:
    child_pid_file = tmp_path / "child.pid"
    program = (
        "import pathlib, subprocess, sys, time; "
        "child=subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)']); "
        f"pathlib.Path({str(child_pid_file)!r}).write_text(str(child.pid)); "
        "time.sleep(60)"
    )
    runner = ProcessRunner(poll_interval=0.02, terminate_grace=0.2)
    token = CancellationToken()
    caught: list[AppError] = []

    def run() -> None:
        try:
            runner.run(
                [sys.executable, "-c", program],
                token=token,
                stage=ProcessingStage.DECODING,
            )
        except AppError as exc:
            caught.append(exc)

    thread = threading.Thread(target=run)
    thread.start()
    deadline = time.monotonic() + 5
    while not child_pid_file.exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    assert child_pid_file.exists()
    child_pid = int(child_pid_file.read_text())
    token.cancel()
    thread.join(timeout=5)
    assert not thread.is_alive()
    assert caught and caught[0].code is ErrorCode.CANCELLED
    deadline = time.monotonic() + 2
    while _pid_exists(child_pid) and time.monotonic() < deadline:
        time.sleep(0.02)
    assert not _pid_exists(child_pid)
    with pytest.raises(ProcessLookupError):
        os.kill(child_pid, signal.SIGTERM)
