# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Yeming Dai
"""Thread-safe application controller connecting a view to the audio pipeline."""

from __future__ import annotations

import queue
import threading
import traceback
from pathlib import Path
from typing import Protocol

from .errors import AppError, ErrorCode, app_error
from .models import OutputAllocation, ProcessingResult, ProgressEvent
from .naming import allocate_output
from .pipeline import AudioPipeline
from .process_runner import CancellationToken
from .task_guard import SingleTaskGuard, TaskAlreadyRunningError
from .validation import build_request


class RootScheduler(Protocol):
    def after(self, milliseconds: int, callback) -> object: ...

    def destroy(self) -> None: ...


class ApplicationView(Protocol):
    def set_running(self, running: bool) -> None: ...

    def set_status(self, message: str) -> None: ...

    def confirm_output_conflict(self, allocation: OutputAllocation) -> bool: ...

    def show_success(self, result: ProcessingResult) -> None: ...

    def show_error(self, error: AppError) -> None: ...

    def show_cancelled(self) -> None: ...

    def show_already_running(self) -> None: ...

    def confirm_exit_running(self) -> bool: ...


class ApplicationController:
    def __init__(
        self,
        root: RootScheduler,
        view: ApplicationView,
        *,
        pipeline: AudioPipeline | None = None,
        downloads_path: Path | None = None,
        poll_interval_ms: int = 50,
    ) -> None:
        self._root = root
        self._view = view
        self._pipeline = pipeline or AudioPipeline()
        self._downloads_path = downloads_path
        self._poll_interval_ms = poll_interval_ms
        self._guard = SingleTaskGuard()
        self._events: queue.Queue[ProgressEvent | ProcessingResult | AppError] = queue.Queue()
        self._token: CancellationToken | None = None
        self._worker: threading.Thread | None = None
        self._exit_after_cancel = False
        self._closed = False
        self._schedule_poll()

    @property
    def active(self) -> bool:
        return self._guard.active

    def start(self, input_text: str, pitch_text: str, speed_text: str) -> bool:
        try:
            self._guard.begin()
        except TaskAlreadyRunningError:
            self._view.show_already_running()
            return False

        try:
            if not input_text.strip():
                raise app_error(
                    ErrorCode.INPUT_NOT_FOUND,
                    user_message="请先选择一个 MP3、M4A、WAV 或 FLAC 音频文件。",
                )
            request = build_request(
                input_text,
                pitch_text,
                speed_text,
                downloads_path=self._downloads_path,
            )
            allocation = allocate_output(request)
            if allocation.had_conflict and not self._view.confirm_output_conflict(allocation):
                self._view.set_status("已取消开始，现有文件未被修改。")
                self._guard.finish()
                return False
        except AppError as exc:
            self._view.show_error(exc)
            self._view.set_status("输入有误，请修改后重试。")
            self._guard.finish()
            return False
        except Exception as exc:
            error = app_error(
                ErrorCode.UNKNOWN_ERROR,
                details={"traceback": traceback.format_exc()},
                cause=exc,
            )
            self._view.show_error(error)
            self._guard.finish()
            return False

        token = CancellationToken()
        self._token = token
        self._view.set_running(True)
        self._view.set_status("正在检查输入和参数…")
        worker = threading.Thread(
            target=self._run_worker,
            args=(request, allocation, token),
            name="AudioShifter-processing",
            daemon=False,
        )
        self._worker = worker
        worker.start()
        return True

    def _run_worker(self, request, allocation, token: CancellationToken) -> None:
        try:
            result = self._pipeline.run(
                request,
                allocation=allocation,
                token=token,
                on_stage=self._events.put,
            )
            self._events.put(result)
        except AppError as exc:
            self._events.put(exc)
        except Exception as exc:
            self._events.put(
                app_error(
                    ErrorCode.UNKNOWN_ERROR,
                    details={"traceback": traceback.format_exc()},
                    cause=exc,
                )
            )

    def cancel(self) -> bool:
        if not self._guard.active or self._token is None:
            return False
        self._view.set_status("正在取消，请稍候…")
        self._token.cancel()
        return True

    def request_close(self) -> None:
        if not self._guard.active:
            self._closed = True
            self._root.destroy()
            return
        if not self._view.confirm_exit_running():
            return
        self._exit_after_cancel = True
        self.cancel()

    def _schedule_poll(self) -> None:
        if not self._closed:
            self._root.after(self._poll_interval_ms, self._poll_events)

    def _poll_events(self) -> None:
        terminal_seen = False
        while True:
            try:
                event = self._events.get_nowait()
            except queue.Empty:
                break
            if isinstance(event, ProgressEvent):
                self._view.set_status(event.message)
            elif isinstance(event, ProcessingResult):
                terminal_seen = True
                self._view.set_status("处理完成。")
                self._view.show_success(event)
                self._finish_task()
            elif isinstance(event, AppError):
                terminal_seen = True
                if event.code is ErrorCode.CANCELLED:
                    self._view.set_status("处理已取消。")
                    if not self._exit_after_cancel:
                        self._view.show_cancelled()
                else:
                    self._view.set_status("处理失败，请根据提示重试。")
                    self._view.show_error(event)
                self._finish_task()
        if terminal_seen and self._exit_after_cancel:
            self._closed = True
            self._root.destroy()
            return
        self._schedule_poll()

    def _finish_task(self) -> None:
        self._guard.finish()
        self._token = None
        self._worker = None
        self._view.set_running(False)
