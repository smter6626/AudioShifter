# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Yeming Dai
from __future__ import annotations

import threading
import time
from decimal import Decimal
from pathlib import Path

from audioshifter.controller import ApplicationController
from audioshifter.errors import ErrorCode, app_error
from audioshifter.models import ProcessingResult, ProcessingStage, ProgressEvent


class FakeRoot:
    def __init__(self) -> None:
        self.callbacks: list[callable] = []
        self.destroyed = False

    def after(self, milliseconds: int, callback):
        self.callbacks.append(callback)
        return len(self.callbacks)

    def destroy(self) -> None:
        self.destroyed = True

    def pump_until(self, predicate, timeout: float = 3) -> None:
        deadline = time.monotonic() + timeout
        while not predicate() and time.monotonic() < deadline:
            if self.callbacks:
                callback = self.callbacks.pop(0)
                callback()
            time.sleep(0.005)
        assert predicate()


class FakeView:
    def __init__(self) -> None:
        self.running_states: list[bool] = []
        self.statuses: list[str] = []
        self.successes: list[ProcessingResult] = []
        self.errors = []
        self.cancelled = 0
        self.already_running = 0
        self.conflicts = []
        self.accept_conflict = True
        self.confirm_exit = True
        self.thread_ids: list[int] = []

    def _record(self) -> None:
        self.thread_ids.append(threading.get_ident())

    def set_running(self, running: bool) -> None:
        self._record()
        self.running_states.append(running)

    def set_status(self, message: str) -> None:
        self._record()
        self.statuses.append(message)

    def confirm_output_conflict(self, allocation) -> bool:
        self._record()
        self.conflicts.append(allocation)
        return self.accept_conflict

    def show_success(self, result) -> None:
        self._record()
        self.successes.append(result)

    def show_error(self, error) -> None:
        self._record()
        self.errors.append(error)

    def show_cancelled(self) -> None:
        self._record()
        self.cancelled += 1

    def show_already_running(self) -> None:
        self._record()
        self.already_running += 1

    def confirm_exit_running(self) -> bool:
        self._record()
        return self.confirm_exit


class BlockingPipeline:
    def __init__(self) -> None:
        self.started = threading.Event()
        self.release = threading.Event()
        self.requests = []
        self.allocations = []

    def run(self, request, *, allocation, token, on_stage):
        self.requests.append(request)
        self.allocations.append(allocation)
        on_stage(ProgressEvent(ProcessingStage.DECODING, "正在解码和标准化音频…"))
        self.started.set()
        while not self.release.wait(0.01):
            if token.cancelled:
                raise app_error(ErrorCode.CANCELLED, stage=ProcessingStage.DECODING)
        if token.cancelled:
            raise app_error(ErrorCode.CANCELLED, stage=ProcessingStage.DECODING)
        return ProcessingResult(
            allocation.output_path,
            request.input_path,
            request.pitch_semitones,
            request.speed_change_percent,
            Decimal(1) + request.speed_change_percent / Decimal(100),
            allocation=allocation,
        )


class FailingPipeline:
    def __init__(self, error=None, unexpected: Exception | None = None) -> None:
        self.error = error
        self.unexpected = unexpected

    def run(self, request, *, allocation, token, on_stage):
        if self.unexpected is not None:
            raise self.unexpected
        raise self.error


def _source(tmp_path: Path) -> Path:
    source = tmp_path / "source.wav"
    source.write_bytes(b"audio")
    return source


def test_TASK_T001_T002_duplicate_start_is_rejected_and_request_is_snapshot(tmp_path: Path) -> None:
    root = FakeRoot()
    view = FakeView()
    pipeline = BlockingPipeline()
    main_thread = threading.get_ident()
    controller = ApplicationController(
        root, view, pipeline=pipeline, downloads_path=tmp_path, poll_interval_ms=1
    )
    source = _source(tmp_path)
    assert controller.start(str(source), "+3", "-20") is True
    assert pipeline.started.wait(1)
    assert controller.start(str(source), "0", "0") is False
    assert view.already_running == 1
    pipeline.release.set()
    root.pump_until(lambda: bool(view.successes))
    assert pipeline.requests[0].pitch_semitones == 3
    assert pipeline.requests[0].speed_change_percent == Decimal("-20")
    assert view.running_states == [True, False]
    assert set(view.thread_ids) == {main_thread}


def test_NAME_T013_conflict_confirmation_uses_allocated_suffix(tmp_path: Path) -> None:
    root = FakeRoot()
    view = FakeView()
    pipeline = BlockingPipeline()
    source = _source(tmp_path)
    (tmp_path / "source+0+0%.mp3").write_bytes(b"keep")
    controller = ApplicationController(root, view, pipeline=pipeline, downloads_path=tmp_path)
    assert controller.start(str(source), "0", "0") is True
    assert view.conflicts[0].output_path.name == "source+0+0%_2.mp3"
    pipeline.release.set()
    root.pump_until(lambda: bool(view.successes))


def test_conflict_dialog_can_cancel_before_background_task(tmp_path: Path) -> None:
    root = FakeRoot()
    view = FakeView()
    view.accept_conflict = False
    pipeline = BlockingPipeline()
    source = _source(tmp_path)
    (tmp_path / "source+0+0%.mp3").write_bytes(b"keep")
    controller = ApplicationController(root, view, pipeline=pipeline, downloads_path=tmp_path)
    assert controller.start(str(source), "0", "0") is False
    assert not pipeline.started.is_set()
    assert controller.active is False


def test_TASK_T008_cancel_is_not_reported_as_failure_and_allows_restart(tmp_path: Path) -> None:
    root = FakeRoot()
    view = FakeView()
    first_pipeline = BlockingPipeline()
    controller = ApplicationController(
        root, view, pipeline=first_pipeline, downloads_path=tmp_path, poll_interval_ms=1
    )
    source = _source(tmp_path)
    assert controller.start(str(source), "0", "0")
    assert first_pipeline.started.wait(1)
    assert controller.cancel()
    root.pump_until(lambda: view.cancelled == 1)
    assert not view.errors
    assert controller.active is False
    first_pipeline.release.clear()
    assert controller.start(str(source), "0", "0")
    first_pipeline.release.set()
    root.pump_until(lambda: bool(view.successes))


def test_TASK_T011_close_refusal_keeps_task_running(tmp_path: Path) -> None:
    root = FakeRoot()
    view = FakeView()
    view.confirm_exit = False
    pipeline = BlockingPipeline()
    controller = ApplicationController(root, view, pipeline=pipeline, downloads_path=tmp_path)
    assert controller.start(str(_source(tmp_path)), "0", "0")
    assert pipeline.started.wait(1)
    controller.request_close()
    assert root.destroyed is False
    assert controller.active is True
    pipeline.release.set()
    root.pump_until(lambda: bool(view.successes))


def test_TASK_T012_close_confirmation_cancels_then_destroys(tmp_path: Path) -> None:
    root = FakeRoot()
    view = FakeView()
    pipeline = BlockingPipeline()
    controller = ApplicationController(
        root, view, pipeline=pipeline, downloads_path=tmp_path, poll_interval_ms=1
    )
    assert controller.start(str(_source(tmp_path)), "0", "0")
    assert pipeline.started.wait(1)
    controller.request_close()
    root.pump_until(lambda: root.destroyed)
    assert view.cancelled == 0
    assert controller.active is False


def test_ERR_T002_no_input_and_invalid_parameters_are_actionable(tmp_path: Path) -> None:
    root = FakeRoot()
    view = FakeView()
    controller = ApplicationController(root, view, pipeline=BlockingPipeline(), downloads_path=tmp_path)
    assert controller.start("", "0", "0") is False
    assert view.errors[-1].code is ErrorCode.INPUT_NOT_FOUND
    source = _source(tmp_path)
    assert controller.start(str(source), "1.5", "0") is False
    assert view.errors[-1].code is ErrorCode.INVALID_PITCH
    assert controller.start(str(source), "0", "20%") is False
    assert view.errors[-1].code is ErrorCode.INVALID_SPEED


def test_ERR_T003_missing_downloads_reaches_view_before_worker(tmp_path: Path) -> None:
    root = FakeRoot()
    view = FakeView()
    controller = ApplicationController(
        root,
        view,
        pipeline=BlockingPipeline(),
        downloads_path=tmp_path / "missing-Downloads",
    )
    assert controller.start(str(_source(tmp_path)), "0", "0") is False
    assert view.errors[-1].code is ErrorCode.DOWNLOADS_NOT_FOUND
    assert controller.active is False


def test_ERR_T004_T005_structured_pipeline_errors_reach_view_on_main_thread(tmp_path: Path) -> None:
    for code in (ErrorCode.DISK_FULL, ErrorCode.PROCESS_FAILED):
        root = FakeRoot()
        view = FakeView()
        main_thread = threading.get_ident()
        controller = ApplicationController(
            root,
            view,
            pipeline=FailingPipeline(app_error(code)),
            downloads_path=tmp_path,
            poll_interval_ms=1,
        )
        assert controller.start(str(_source(tmp_path)), "0", "0")
        root.pump_until(lambda: bool(view.errors))
        assert view.errors[-1].code is code
        assert set(view.thread_ids) == {main_thread}


def test_ERR_T009_unexpected_worker_exception_maps_to_unknown_error(tmp_path: Path) -> None:
    root = FakeRoot()
    view = FakeView()
    controller = ApplicationController(
        root,
        view,
        pipeline=FailingPipeline(unexpected=RuntimeError("injected")),
        downloads_path=tmp_path,
        poll_interval_ms=1,
    )
    assert controller.start(str(_source(tmp_path)), "0", "0")
    root.pump_until(lambda: bool(view.errors))
    assert view.errors[-1].code is ErrorCode.UNKNOWN_ERROR
    assert "traceback" in view.errors[-1].details
