from dataclasses import FrozenInstanceError

import pytest

from audioshifter.errors import AppError, ErrorCode, USER_MESSAGES
from audioshifter.models import ProcessingRequest
from audioshifter.task_guard import SingleTaskGuard, TaskAlreadyRunningError
from audioshifter.workspace import TaskWorkspace


def test_TEMP_T001_workspaces_are_unique_and_temporary() -> None:
    first = TaskWorkspace.create()
    second = TaskWorkspace.create()
    try:
        assert first.path != second.path
        assert first.path.parent == first.temporary_root
        assert second.path.parent == second.temporary_root
    finally:
        first.cleanup()
        second.cleanup()


def test_TEMP_T009_refuses_cleanup_outside_temp_root(tmp_path) -> None:
    workspace = TaskWorkspace.create()
    original = workspace.path
    workspace.path = tmp_path / "unrelated"
    try:
        with pytest.raises(ValueError, match="Refusing unsafe"):
            workspace.cleanup()
    finally:
        workspace.path = original
        workspace.cleanup()


def test_TASK_T002_controller_guard_rejects_second_task() -> None:
    guard = SingleTaskGuard()
    guard.begin()
    with pytest.raises(TaskAlreadyRunningError):
        guard.begin()
    guard.finish()
    guard.begin()
    guard.finish()


def test_request_is_immutable(tmp_path) -> None:
    from decimal import Decimal

    request = ProcessingRequest(tmp_path / "in.mp3", 0, Decimal(0), tmp_path)
    with pytest.raises(FrozenInstanceError):
        request.pitch_semitones = 3  # type: ignore[misc]


@pytest.mark.parametrize("code", list(ErrorCode), ids=lambda code: f"ERR-T001-{code.value}")
def test_ERR_T001_all_stable_error_codes_have_chinese_messages(code: ErrorCode) -> None:
    error = AppError(code)
    assert error.code is code
    assert error.user_message == USER_MESSAGES[code]
    assert any("\u4e00" <= character <= "\u9fff" for character in str(error))
