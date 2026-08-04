"""Stable application errors and Chinese user-facing guidance."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from .models import ProcessingStage


class ErrorCode(str, Enum):
    INPUT_NOT_FOUND = "INPUT_NOT_FOUND"
    INPUT_NOT_FILE = "INPUT_NOT_FILE"
    INPUT_NOT_READABLE = "INPUT_NOT_READABLE"
    UNSUPPORTED_INPUT = "UNSUPPORTED_INPUT"
    INVALID_INPUT_MEDIA = "INVALID_INPUT_MEDIA"
    INVALID_PITCH = "INVALID_PITCH"
    INVALID_SPEED = "INVALID_SPEED"
    DOWNLOADS_NOT_FOUND = "DOWNLOADS_NOT_FOUND"
    DOWNLOADS_NOT_DIRECTORY = "DOWNLOADS_NOT_DIRECTORY"
    OUTPUT_PERMISSION_DENIED = "OUTPUT_PERMISSION_DENIED"
    DISK_FULL = "DISK_FULL"
    DEPENDENCY_MISSING = "DEPENDENCY_MISSING"
    DEPENDENCY_NOT_EXECUTABLE = "DEPENDENCY_NOT_EXECUTABLE"
    DECODE_FAILED = "DECODE_FAILED"
    PROCESS_FAILED = "PROCESS_FAILED"
    ENCODE_FAILED = "ENCODE_FAILED"
    OUTPUT_NAME_CONFLICT = "OUTPUT_NAME_CONFLICT"
    CANCELLED = "CANCELLED"
    CLEANUP_WARNING = "CLEANUP_WARNING"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


USER_MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.INPUT_NOT_FOUND: "找不到所选文件，请重新选择一个现有音频文件。",
    ErrorCode.INPUT_NOT_FILE: "所选路径不是普通文件，请重新选择音频文件。",
    ErrorCode.INPUT_NOT_READABLE: "无法读取所选文件，请检查文件权限后重试。",
    ErrorCode.UNSUPPORTED_INPUT: "当前仅支持 MP3、M4A、WAV 和 FLAC 文件。",
    ErrorCode.INVALID_INPUT_MEDIA: "文件为空、已损坏或不是有效音频，请选择可正常播放的文件。",
    ErrorCode.INVALID_PITCH: "变调必须是 -24 到 +24 之间的整数半音。",
    ErrorCode.INVALID_SPEED: "变速必须是 -95 到 +400 之间、显式带正负号的相对变化值（零除外），且不要输入 %。",
    ErrorCode.DOWNLOADS_NOT_FOUND: "下载目录不存在，请恢复当前用户的 Downloads 目录后重试。",
    ErrorCode.DOWNLOADS_NOT_DIRECTORY: "Downloads 路径不是目录，请修复该路径后重试。",
    ErrorCode.OUTPUT_PERMISSION_DENIED: "无法写入下载目录，请检查目录权限后重试。",
    ErrorCode.DISK_FULL: "磁盘空间不足，无法保存到下载目录；请释放空间后重试。",
    ErrorCode.DEPENDENCY_MISSING: "音频处理组件缺失，请恢复应用环境后重试。",
    ErrorCode.DEPENDENCY_NOT_EXECUTABLE: "音频处理组件无法启动，请检查应用环境后重试。",
    ErrorCode.DECODE_FAILED: "无法读取或标准化源音频，请确认文件可以正常播放。",
    ErrorCode.PROCESS_FAILED: "变调或变速处理失败，请尝试其他有效音频文件或参数。",
    ErrorCode.ENCODE_FAILED: "无法生成 MP3，请检查下载目录权限和磁盘空间。",
    ErrorCode.OUTPUT_NAME_CONFLICT: "无法安全分配输出文件名；已有文件不会被覆盖，请稍后重试。",
    ErrorCode.CANCELLED: "处理已取消。",
    ErrorCode.CLEANUP_WARNING: "结果已生成，但部分临时文件未能清理。",
    ErrorCode.UNKNOWN_ERROR: "出现未预期问题，请重试；若问题持续，请查看本机诊断信息。",
}


@dataclass(slots=True)
class AppError(Exception):
    code: ErrorCode
    user_message: str | None = None
    stage: ProcessingStage | None = None
    details: Mapping[str, Any] = field(default_factory=dict)
    cause: BaseException | None = None
    recoverable: bool = True

    def __post_init__(self) -> None:
        if self.user_message is None:
            self.user_message = USER_MESSAGES[self.code]
        Exception.__init__(self, self.user_message)

    def __str__(self) -> str:
        return self.user_message or USER_MESSAGES[self.code]


def app_error(
    code: ErrorCode,
    *,
    stage: ProcessingStage | None = None,
    details: Mapping[str, Any] | None = None,
    cause: BaseException | None = None,
    user_message: str | None = None,
) -> AppError:
    return AppError(
        code=code,
        user_message=user_message,
        stage=stage,
        details=details or {},
        cause=cause,
    )
