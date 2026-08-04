"""End-to-end processing orchestration with atomic no-overwrite publication."""

from __future__ import annotations

import errno
import os
from dataclasses import replace
from pathlib import Path
from typing import Callable

from .dependencies import DependencyResolver, default_dependency_resolver
from .errors import AppError, ErrorCode, app_error
from .ffmpeg_adapter import FFmpegAdapter
from .models import (
    OutputAllocation,
    ProcessingRequest,
    ProcessingResult,
    ProcessingStage,
    ProgressEvent,
)
from .naming import allocate_output
from .process_runner import CancellationToken, ProcessRunner
from .rubberband_adapter import RubberBandAdapter
from .validation import compute_tempo_ratio, validate_request
from .workspace import TaskWorkspace


StageCallback = Callable[[ProgressEvent], None]


_STAGE_MESSAGES = {
    ProcessingStage.VALIDATING: "正在检查输入和参数…",
    ProcessingStage.ALLOCATING_OUTPUT: "正在分配安全输出文件名…",
    ProcessingStage.PREPARING_WORKSPACE: "正在准备临时工作区…",
    ProcessingStage.DECODING: "正在解码和标准化音频…",
    ProcessingStage.PROCESSING: "正在变调和变速…",
    ProcessingStage.ENCODING: "正在生成 MP3…",
    ProcessingStage.VERIFYING_OUTPUT: "正在验证输出文件…",
    ProcessingStage.CLEANING_UP: "正在清理临时文件…",
    ProcessingStage.SUCCEEDED: "处理完成。",
    ProcessingStage.CANCELLING: "正在取消…",
    ProcessingStage.CANCELLED: "处理已取消。",
    ProcessingStage.FAILED: "处理失败。",
}


class AudioPipeline:
    def __init__(
        self,
        resolver: DependencyResolver | None = None,
        runner: ProcessRunner | None = None,
    ) -> None:
        self._resolver = resolver or default_dependency_resolver()
        self._runner = runner or ProcessRunner()

    @staticmethod
    def _emit(callback: StageCallback | None, stage: ProcessingStage) -> None:
        if callback is not None:
            callback(ProgressEvent(stage, _STAGE_MESSAGES[stage]))

    @staticmethod
    def _remove_owned_output(path: Path | None) -> None:
        if path is None:
            return
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass

    @staticmethod
    def _publish_exclusive(source: Path, target: Path, token: CancellationToken) -> None:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        descriptor: int | None = None
        created = False
        completed = False
        try:
            descriptor = os.open(target, flags, 0o644)
            created = True
            with source.open("rb") as reader, os.fdopen(descriptor, "wb", closefd=True) as writer:
                descriptor = None
                while True:
                    if token.cancelled:
                        raise app_error(ErrorCode.CANCELLED, stage=ProcessingStage.ENCODING)
                    chunk = reader.read(1024 * 1024)
                    if not chunk:
                        break
                    writer.write(chunk)
                writer.flush()
                os.fsync(writer.fileno())
                completed = True
        except FileExistsError as exc:
            raise app_error(
                ErrorCode.OUTPUT_NAME_CONFLICT,
                stage=ProcessingStage.ENCODING,
                details={"path": str(target)},
                cause=exc,
            ) from exc
        except OSError as exc:
            if exc.errno == errno.ENOSPC:
                code = ErrorCode.DISK_FULL
            elif exc.errno in {errno.EACCES, errno.EPERM, errno.EROFS}:
                code = ErrorCode.OUTPUT_PERMISSION_DENIED
            else:
                code = ErrorCode.ENCODE_FAILED
            raise app_error(code, stage=ProcessingStage.ENCODING, details={"path": str(target)}, cause=exc) from exc
        finally:
            if descriptor is not None:
                os.close(descriptor)
            if created and not completed:
                AudioPipeline._remove_owned_output(target)

    def run(
        self,
        request: ProcessingRequest,
        *,
        allocation: OutputAllocation | None = None,
        token: CancellationToken | None = None,
        on_stage: StageCallback | None = None,
    ) -> ProcessingResult:
        token = token or CancellationToken()
        workspace: TaskWorkspace | None = None
        published_path: Path | None = None
        result: ProcessingResult | None = None
        pending_error: AppError | None = None
        cleanup_warning: AppError | None = None
        try:
            self._emit(on_stage, ProcessingStage.VALIDATING)
            checked_request = validate_request(request)
            if token.cancelled:
                raise app_error(ErrorCode.CANCELLED, stage=ProcessingStage.VALIDATING)
            dependencies = self._resolver.resolve()

            self._emit(on_stage, ProcessingStage.ALLOCATING_OUTPUT)
            chosen = allocation or allocate_output(checked_request)
            if chosen.output_path.exists():
                raise app_error(
                    ErrorCode.OUTPUT_NAME_CONFLICT,
                    stage=ProcessingStage.ALLOCATING_OUTPUT,
                    details={"path": str(chosen.output_path)},
                )

            self._emit(on_stage, ProcessingStage.PREPARING_WORKSPACE)
            workspace = TaskWorkspace.create()
            ffmpeg = FFmpegAdapter(dependencies, self._runner)
            rubberband = RubberBandAdapter(dependencies, self._runner)

            self._emit(on_stage, ProcessingStage.DECODING)
            input_media = ffmpeg.probe(
                checked_request.input_path,
                token=token,
                invalid_code=ErrorCode.INVALID_INPUT_MEDIA,
                stage=ProcessingStage.DECODING,
            )
            ffmpeg.decode(checked_request.input_path, workspace.decoded_path, token=token)

            self._emit(on_stage, ProcessingStage.PROCESSING)
            tempo_ratio = compute_tempo_ratio(checked_request.speed_change_percent)
            rubberband.process(
                workspace.decoded_path,
                workspace.processed_path,
                pitch_semitones=checked_request.pitch_semitones,
                tempo_ratio=tempo_ratio,
                token=token,
            )

            self._emit(on_stage, ProcessingStage.ENCODING)
            if chosen.output_path.exists():
                raise app_error(
                    ErrorCode.OUTPUT_NAME_CONFLICT,
                    stage=ProcessingStage.ENCODING,
                    details={"path": str(chosen.output_path)},
                )
            ffmpeg.encode_mp3(workspace.processed_path, workspace.encoded_path, token=token)

            self._emit(on_stage, ProcessingStage.VERIFYING_OUTPUT)
            staged_media = ffmpeg.probe(
                workspace.encoded_path,
                token=token,
                invalid_code=ErrorCode.ENCODE_FAILED,
                stage=ProcessingStage.VERIFYING_OUTPUT,
            )
            ffmpeg.validate_output_spec(staged_media, workspace.encoded_path)
            self._publish_exclusive(workspace.encoded_path, chosen.output_path, token)
            published_path = chosen.output_path
            final_media = ffmpeg.probe(
                published_path,
                token=token,
                invalid_code=ErrorCode.ENCODE_FAILED,
                stage=ProcessingStage.VERIFYING_OUTPUT,
            )
            ffmpeg.validate_output_spec(final_media, published_path)
            if token.cancelled:
                raise app_error(ErrorCode.CANCELLED, stage=ProcessingStage.VERIFYING_OUTPUT)
            result = ProcessingResult(
                output_path=published_path,
                input_path=checked_request.input_path,
                pitch_semitones=checked_request.pitch_semitones,
                speed_change_percent=checked_request.speed_change_percent,
                tempo_ratio=tempo_ratio,
                diagnostics={
                    "input_duration": str(input_media.duration_seconds),
                    "output_duration": str(final_media.duration_seconds),
                    "codec": final_media.codec_name,
                    "sample_rate": final_media.sample_rate,
                    "channels": final_media.channels,
                    "bit_rate": final_media.bit_rate,
                },
                allocation=chosen,
            )
        except AppError as exc:
            pending_error = exc
            self._remove_owned_output(published_path)
        except Exception as exc:
            pending_error = app_error(
                ErrorCode.UNKNOWN_ERROR,
                stage=ProcessingStage.FAILED,
                details={"exception_type": type(exc).__name__},
                cause=exc,
            )
            self._remove_owned_output(published_path)
        finally:
            if workspace is not None:
                self._emit(on_stage, ProcessingStage.CLEANING_UP)
                cleanup_warning = workspace.cleanup()

        if pending_error is not None:
            terminal = ProcessingStage.CANCELLED if pending_error.code is ErrorCode.CANCELLED else ProcessingStage.FAILED
            self._emit(on_stage, terminal)
            raise pending_error
        assert result is not None
        if cleanup_warning is not None:
            result = replace(result, warnings=(str(cleanup_warning),))
        self._emit(on_stage, ProcessingStage.SUCCEEDED)
        return result
