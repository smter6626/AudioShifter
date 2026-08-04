"""FFmpeg decoding/encoding and FFprobe media validation."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .dependencies import ResolvedDependencies
from .errors import ErrorCode, app_error
from .models import MediaInfo, ProcessingStage
from .process_runner import CancellationToken, ProcessResult, ProcessRunner


class FFmpegAdapter:
    def __init__(self, dependencies: ResolvedDependencies, runner: ProcessRunner) -> None:
        self._dependencies = dependencies
        self._runner = runner

    @staticmethod
    def _require_success(result: ProcessResult, code: ErrorCode, stage: ProcessingStage) -> None:
        if result.returncode != 0:
            raise app_error(
                code,
                stage=stage,
                details={
                    "args": result.args,
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                },
            )

    def probe(
        self,
        path: Path,
        *,
        token: CancellationToken,
        invalid_code: ErrorCode,
        stage: ProcessingStage,
    ) -> MediaInfo:
        result = self._runner.run(
            [
                self._dependencies.ffprobe_path,
                "-v",
                "error",
                "-select_streams",
                "a:0",
                "-show_entries",
                "stream=codec_name,sample_rate,channels,bit_rate,duration:format=duration,format_name,bit_rate",
                "-of",
                "json",
                path,
            ],
            token=token,
            stage=stage,
        )
        self._require_success(result, invalid_code, stage)
        try:
            payload = json.loads(result.stdout)
            stream = payload["streams"][0]
            media_format = payload.get("format", {})
            duration_text = stream.get("duration") or media_format["duration"]
            bit_rate_text = stream.get("bit_rate") or media_format.get("bit_rate")
            return MediaInfo(
                codec_name=str(stream["codec_name"]),
                sample_rate=int(stream["sample_rate"]),
                channels=int(stream["channels"]),
                duration_seconds=Decimal(str(duration_text)),
                bit_rate=int(bit_rate_text) if bit_rate_text is not None else None,
                format_name=str(media_format.get("format_name", "")),
            )
        except (KeyError, IndexError, TypeError, ValueError, InvalidOperation, json.JSONDecodeError) as exc:
            raise app_error(
                invalid_code,
                stage=stage,
                details={"path": str(path), "probe_output": result.stdout, "stderr": result.stderr},
                cause=exc,
            ) from exc

    def decode(self, source: Path, destination: Path, *, token: CancellationToken) -> None:
        result = self._runner.run(
            [
                self._dependencies.ffmpeg_path,
                "-hide_banner",
                "-loglevel",
                "error",
                "-nostdin",
                "-n",
                "-i",
                source,
                "-map",
                "0:a:0",
                "-vn",
                "-ac",
                "2",
                "-ar",
                "44100",
                "-c:a",
                "pcm_s16le",
                destination,
            ],
            token=token,
            stage=ProcessingStage.DECODING,
        )
        self._require_success(result, ErrorCode.DECODE_FAILED, ProcessingStage.DECODING)
        if not destination.is_file() or destination.stat().st_size == 0:
            raise app_error(
                ErrorCode.DECODE_FAILED,
                stage=ProcessingStage.DECODING,
                details={"destination": str(destination), "reason": "missing_or_empty"},
            )

    def encode_mp3(self, source: Path, destination: Path, *, token: CancellationToken) -> None:
        result = self._runner.run(
            [
                self._dependencies.ffmpeg_path,
                "-hide_banner",
                "-loglevel",
                "error",
                "-nostdin",
                "-n",
                "-i",
                source,
                "-map",
                "0:a:0",
                "-map_metadata",
                "-1",
                "-map_chapters",
                "-1",
                "-vn",
                "-c:a",
                "libmp3lame",
                "-b:a",
                "320k",
                "-ar",
                "44100",
                "-ac",
                "2",
                destination,
            ],
            token=token,
            stage=ProcessingStage.ENCODING,
        )
        self._require_success(result, ErrorCode.ENCODE_FAILED, ProcessingStage.ENCODING)
        if not destination.is_file() or destination.stat().st_size == 0:
            raise app_error(
                ErrorCode.ENCODE_FAILED,
                stage=ProcessingStage.ENCODING,
                details={"destination": str(destination), "reason": "missing_or_empty"},
            )

    @staticmethod
    def validate_output_spec(media: MediaInfo, path: Path) -> None:
        if (
            media.codec_name != "mp3"
            or media.sample_rate != 44100
            or media.channels != 2
            or media.bit_rate != 320000
            or media.duration_seconds <= 0
        ):
            raise app_error(
                ErrorCode.ENCODE_FAILED,
                stage=ProcessingStage.VERIFYING_OUTPUT,
                details={"path": str(path), "media": media},
                user_message="生成的 MP3 未通过规格验证，残缺结果已删除；请重试。",
            )
