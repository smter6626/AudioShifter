"""Controller-level single-task protection independent of button state."""

from __future__ import annotations

from threading import Lock


class TaskAlreadyRunningError(RuntimeError):
    pass


class SingleTaskGuard:
    def __init__(self) -> None:
        self._lock = Lock()
        self._active = False

    @property
    def active(self) -> bool:
        with self._lock:
            return self._active

    def begin(self) -> None:
        with self._lock:
            if self._active:
                raise TaskAlreadyRunningError("A processing task is already running")
            self._active = True

    def finish(self) -> None:
        with self._lock:
            self._active = False
