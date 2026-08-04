# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Yeming Dai
from __future__ import annotations

import errno
import os
from pathlib import Path

import pytest

from audioshifter.errors import AppError, ErrorCode
from audioshifter.pipeline import AudioPipeline
from audioshifter.process_runner import CancellationToken
from audioshifter.workspace import TaskWorkspace


@pytest.mark.parametrize(
    ("error_number", "expected"),
    [
        (errno.ENOSPC, ErrorCode.DISK_FULL),
        (errno.EACCES, ErrorCode.OUTPUT_PERMISSION_DENIED),
    ],
)
def test_OUT_T006_publish_filesystem_errors_are_actionable_and_leave_no_partial(
    tmp_path: Path, monkeypatch, error_number: int, expected: ErrorCode
) -> None:
    source = tmp_path / "encoded.mp3"
    source.write_bytes(b"complete staged output")
    target = tmp_path / "Downloads" / "result.mp3"
    target.parent.mkdir()

    def fail_open(*args, **kwargs):
        raise OSError(error_number, os.strerror(error_number))

    monkeypatch.setattr(os, "open", fail_open)
    with pytest.raises(AppError) as caught:
        AudioPipeline._publish_exclusive(source, target, CancellationToken())
    assert caught.value.code is expected
    assert not target.exists()


def test_TEMP_T008_cleanup_failure_returns_warning_without_unsafe_retry(monkeypatch) -> None:
    workspace = TaskWorkspace.create()

    def fail_cleanup(path):
        raise PermissionError("injected cleanup failure")

    monkeypatch.setattr("audioshifter.workspace.shutil.rmtree", fail_cleanup)
    warning = workspace.cleanup()
    assert warning is not None
    assert warning.code is ErrorCode.CLEANUP_WARNING
    assert workspace.path.exists()
    monkeypatch.undo()
    assert workspace.cleanup() is None
    assert not workspace.path.exists()
