from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

import pytest

from audioshifter.dependencies import ResolvedDependencies
from audioshifter.errors import AppError, ErrorCode
from audioshifter.models import ProcessingRequest, ProcessingStage
from audioshifter.naming import allocate_output
from audioshifter.pipeline import AudioPipeline
from audioshifter.process_runner import CancellationToken, ProcessResult, ProcessRunner
from audioshifter.workspace import TaskWorkspace


@dataclass
class FixedResolver:
    dependencies: ResolvedDependencies

    def resolve(self) -> ResolvedDependencies:
        return self.dependencies


def _request(source: Path, downloads: Path, pitch: int = 0, speed: str = "0") -> ProcessingRequest:
    downloads.mkdir(exist_ok=True)
    return ProcessingRequest(source, pitch, Decimal(speed), downloads)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _probe(path: Path, dependencies: ResolvedDependencies) -> dict:
    import subprocess

    completed = subprocess.run(
        [
            str(dependencies.ffprobe_path),
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_name,sample_rate,channels,bit_rate:format=duration",
            "-of",
            "json",
            str(path),
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        shell=False,
    )
    return json.loads(completed.stdout)


@pytest.mark.integration
@pytest.mark.parametrize("format_name", ["mp3", "m4a", "wav", "flac"])
def test_IN_T001_T004_four_formats_real_pipeline(
    tmp_path: Path,
    synthetic_sources: dict[str, Path],
    dependencies: ResolvedDependencies,
    format_name: str,
) -> None:
    downloads = tmp_path / "Downloads"
    source = synthetic_sources[format_name]
    source_hash = _sha256(source)
    stages: list[ProcessingStage] = []
    workspaces_before = set(Path(tempfile.gettempdir()).glob("AudioShifter-*"))
    result = AudioPipeline(FixedResolver(dependencies)).run(
        _request(source, downloads), on_stage=lambda event: stages.append(event.stage)
    )
    media = _probe(result.output_path, dependencies)["streams"][0]
    assert result.output_path.parent == downloads.resolve()
    assert result.output_path.name.endswith("+0+0%.mp3")
    assert media == {
        "codec_name": "mp3",
        "sample_rate": "44100",
        "channels": 2,
        "bit_rate": "320000",
    }
    assert _sha256(source) == source_hash
    assert stages.index(ProcessingStage.DECODING) < stages.index(ProcessingStage.PROCESSING)
    assert stages.index(ProcessingStage.PROCESSING) < stages.index(ProcessingStage.ENCODING)
    assert stages[-1] is ProcessingStage.SUCCEEDED
    assert set(Path(tempfile.gettempdir()).glob("AudioShifter-*")) == workspaces_before


@pytest.mark.integration
def test_PIPE_T002_decode_normalizes_48k_mono_to_s16le_stereo(
    synthetic_sources: dict[str, Path], dependencies: ResolvedDependencies
) -> None:
    from audioshifter.ffmpeg_adapter import FFmpegAdapter

    workspace = TaskWorkspace.create()
    try:
        adapter = FFmpegAdapter(dependencies, ProcessRunner())
        token = CancellationToken()
        adapter.decode(synthetic_sources["wav"], workspace.decoded_path, token=token)
        media = adapter.probe(
            workspace.decoded_path,
            token=token,
            invalid_code=ErrorCode.DECODE_FAILED,
            stage=ProcessingStage.DECODING,
        )
        assert media.codec_name == "pcm_s16le"
        assert media.sample_rate == 44100
        assert media.channels == 2
    finally:
        workspace.cleanup()


@pytest.mark.integration
@pytest.mark.parametrize(
    ("pitch", "speed", "name_fragment"),
    [
        (3, "0", "+3+0%"),
        (0, "-20", "+0-20%"),
        (3, "-20", "+3-20%"),
    ],
)
def test_PIPE_T003_T004_pitch_speed_combinations(
    tmp_path: Path,
    synthetic_sources: dict[str, Path],
    dependencies: ResolvedDependencies,
    pitch: int,
    speed: str,
    name_fragment: str,
) -> None:
    result = AudioPipeline(FixedResolver(dependencies)).run(
        _request(synthetic_sources["m4a"], tmp_path / "Downloads", pitch, speed)
    )
    assert name_fragment in result.output_path.name
    assert result.tempo_ratio == Decimal(1) + Decimal(speed) / Decimal(100)


@pytest.mark.integration
@pytest.mark.parametrize(("pitch", "speed"), [(-24, "0"), (24, "0"), (0, "-95"), (0, "+400")])
def test_contract_boundaries_real_pipeline(
    tmp_path: Path,
    synthetic_sources: dict[str, Path],
    dependencies: ResolvedDependencies,
    pitch: int,
    speed: str,
) -> None:
    result = AudioPipeline(FixedResolver(dependencies)).run(
        _request(synthetic_sources["flac"], tmp_path / "Downloads", pitch, speed)
    )
    assert result.output_path.is_file()


@pytest.mark.integration
@pytest.mark.parametrize(("speed", "direction"), [("-20", "longer"), ("+20", "shorter")])
def test_SPEED_T015_T016_duration_direction(
    tmp_path: Path,
    synthetic_sources: dict[str, Path],
    dependencies: ResolvedDependencies,
    speed: str,
    direction: str,
) -> None:
    result = AudioPipeline(FixedResolver(dependencies)).run(
        _request(synthetic_sources["mp3"], tmp_path / "Downloads", 0, speed)
    )
    input_duration = Decimal(result.diagnostics["input_duration"])
    output_duration = Decimal(result.diagnostics["output_duration"])
    assert (output_duration > input_duration) if direction == "longer" else (output_duration < input_duration)


@pytest.mark.integration
def test_NAME_T014_conflict_increments_without_overwrite(
    tmp_path: Path, synthetic_sources: dict[str, Path], dependencies: ResolvedDependencies
) -> None:
    pipeline = AudioPipeline(FixedResolver(dependencies))
    request = _request(synthetic_sources["mp3"], tmp_path / "Downloads", 3, "-20")
    first = pipeline.run(request)
    first_hash = _sha256(first.output_path)
    second = pipeline.run(request)
    assert second.output_path.stem.endswith("_2")
    assert first.output_path != second.output_path
    assert _sha256(first.output_path) == first_hash


@pytest.mark.integration
def test_NAME_T015_external_race_never_overwrites_allocated_target(
    tmp_path: Path, synthetic_sources: dict[str, Path], dependencies: ResolvedDependencies
) -> None:
    request = _request(synthetic_sources["wav"], tmp_path / "Downloads", 2, "+10")
    allocation = allocate_output(request)
    allocation.output_path.write_bytes(b"external file")
    original_hash = _sha256(allocation.output_path)
    with pytest.raises(AppError) as caught:
        AudioPipeline(FixedResolver(dependencies)).run(request, allocation=allocation)
    assert caught.value.code is ErrorCode.OUTPUT_NAME_CONFLICT
    assert _sha256(allocation.output_path) == original_hash


@pytest.mark.integration
@pytest.mark.parametrize("payload", [b"not audio", b"ID3broken"])
def test_IN_T011_T012_invalid_or_disguised_audio_is_rejected(
    tmp_path: Path, dependencies: ResolvedDependencies, payload: bytes
) -> None:
    source = tmp_path / "fake.mp3"
    source.write_bytes(payload)
    before = set(Path(tempfile.gettempdir()).glob("AudioShifter-*"))
    with pytest.raises(AppError) as caught:
        AudioPipeline(FixedResolver(dependencies)).run(_request(source, tmp_path / "Downloads"))
    assert caught.value.code is ErrorCode.INVALID_INPUT_MEDIA
    assert set(Path(tempfile.gettempdir()).glob("AudioShifter-*")) == before


@pytest.mark.integration
def test_DEP_T002_missing_rubberband_fails_before_workspace(
    tmp_path: Path, synthetic_sources: dict[str, Path], dependencies: ResolvedDependencies
) -> None:
    missing = tmp_path / "missing-rubberband"
    resolver = FixedResolver(
        ResolvedDependencies(dependencies.ffmpeg_path, dependencies.ffprobe_path, missing)
    )
    with pytest.raises(AppError) as caught:
        AudioPipeline(resolver).run(_request(synthetic_sources["wav"], tmp_path / "Downloads"))
    assert caught.value.code in {ErrorCode.DEPENDENCY_MISSING, ErrorCode.DEPENDENCY_NOT_EXECUTABLE}


def _make_python_tool(path: Path, body: str) -> Path:
    path.write_text(f"#!{sys.executable}\n{body}\n")
    path.chmod(0o755)
    return path


@pytest.mark.integration
def test_DEP_T005_rubberband_failure_preserves_diagnostics_and_cleans(
    tmp_path: Path, synthetic_sources: dict[str, Path], dependencies: ResolvedDependencies
) -> None:
    failing = _make_python_tool(
        tmp_path / "failing-rubberband",
        "import sys; print('synthetic rubberband failure', file=sys.stderr); raise SystemExit(9)",
    )
    resolver = FixedResolver(
        ResolvedDependencies(dependencies.ffmpeg_path, dependencies.ffprobe_path, failing)
    )
    before = set(Path(tempfile.gettempdir()).glob("AudioShifter-*"))
    with pytest.raises(AppError) as caught:
        AudioPipeline(resolver).run(_request(synthetic_sources["wav"], tmp_path / "Downloads"))
    assert caught.value.code is ErrorCode.PROCESS_FAILED
    assert caught.value.details["returncode"] == 9
    assert "synthetic rubberband failure" in caught.value.details["stderr"]
    assert set(Path(tempfile.gettempdir()).glob("AudioShifter-*")) == before
    assert not list((tmp_path / "Downloads").glob("*.mp3"))


class FailCommandRunner(ProcessRunner):
    def __init__(self, needle: str, code: int) -> None:
        super().__init__()
        self._needle = needle
        self._code = code

    def run(self, args, *, token, stage, cwd=None):
        rendered = tuple(str(value) for value in args)
        if self._needle in rendered:
            return ProcessResult(rendered, self._code, "", f"injected {self._needle} failure", 0.0)
        return super().run(args, token=token, stage=stage, cwd=cwd)


@pytest.mark.integration
@pytest.mark.parametrize(
    ("needle", "expected"),
    [("pcm_s16le", ErrorCode.DECODE_FAILED), ("libmp3lame", ErrorCode.ENCODE_FAILED)],
)
def test_DEP_T004_T006_ffmpeg_failures_clean_without_partial_output(
    tmp_path: Path,
    synthetic_sources: dict[str, Path],
    dependencies: ResolvedDependencies,
    needle: str,
    expected: ErrorCode,
) -> None:
    before = set(Path(tempfile.gettempdir()).glob("AudioShifter-*"))
    downloads = tmp_path / "Downloads"
    with pytest.raises(AppError) as caught:
        AudioPipeline(FixedResolver(dependencies), FailCommandRunner(needle, 8)).run(
            _request(synthetic_sources["wav"], downloads)
        )
    assert caught.value.code is expected
    assert caught.value.details["returncode"] == 8
    assert "injected" in caught.value.details["stderr"]
    assert set(Path(tempfile.gettempdir()).glob("AudioShifter-*")) == before
    assert not list(downloads.glob("*.mp3"))


class FailFinalProbeRunner(ProcessRunner):
    def __init__(self) -> None:
        super().__init__()
        self._probe_count = 0

    def run(self, args, *, token, stage, cwd=None):
        rendered = tuple(str(value) for value in args)
        if Path(rendered[0]).name == "ffprobe":
            self._probe_count += 1
            if self._probe_count == 3:
                return ProcessResult(rendered, 1, "", "injected final probe failure", 0.0)
        return super().run(args, token=token, stage=stage, cwd=cwd)


@pytest.mark.integration
def test_PIPE_T012_final_probe_failure_removes_published_file(
    tmp_path: Path, synthetic_sources: dict[str, Path], dependencies: ResolvedDependencies
) -> None:
    downloads = tmp_path / "Downloads"
    with pytest.raises(AppError) as caught:
        AudioPipeline(FixedResolver(dependencies), FailFinalProbeRunner()).run(
            _request(synthetic_sources["wav"], downloads)
        )
    assert caught.value.code is ErrorCode.ENCODE_FAILED
    assert not list(downloads.glob("*.mp3"))


@pytest.mark.integration
def test_PIPE_T010_source_metadata_is_not_copied(
    tmp_path: Path, synthetic_sources: dict[str, Path], dependencies: ResolvedDependencies
) -> None:
    import subprocess

    tagged = tmp_path / "tagged.mp3"
    subprocess.run(
        [
            str(dependencies.ffmpeg_path),
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-i",
            str(synthetic_sources["wav"]),
            "-metadata",
            "title=Private title",
            "-metadata",
            "artist=Private artist",
            "-c:a",
            "libmp3lame",
            str(tagged),
        ],
        check=True,
        shell=False,
    )
    result = AudioPipeline(FixedResolver(dependencies)).run(
        _request(tagged, tmp_path / "Downloads")
    )
    completed = subprocess.run(
        [
            str(dependencies.ffprobe_path),
            "-v",
            "error",
            "-show_entries",
            "format_tags=title,artist",
            "-of",
            "json",
            str(result.output_path),
        ],
        stdout=subprocess.PIPE,
        check=True,
        shell=False,
    )
    tags = json.loads(completed.stdout).get("format", {}).get("tags", {})
    assert "title" not in {key.lower() for key in tags}
    assert "artist" not in {key.lower() for key in tags}


def _pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


@pytest.mark.integration
def test_TASK_T006_real_process_cancel_cleans_workspace_and_output(
    tmp_path: Path, synthetic_sources: dict[str, Path], dependencies: ResolvedDependencies
) -> None:
    pid_file = tmp_path / "rubberband.pid"
    sleeping = _make_python_tool(
        tmp_path / "sleeping-rubberband",
        f"import os, pathlib, time; pathlib.Path({str(pid_file)!r}).write_text(str(os.getpid())); time.sleep(60)",
    )
    resolver = FixedResolver(
        ResolvedDependencies(dependencies.ffmpeg_path, dependencies.ffprobe_path, sleeping)
    )
    token = CancellationToken()
    caught: list[AppError] = []
    before = set(Path(tempfile.gettempdir()).glob("AudioShifter-*"))

    def execute() -> None:
        try:
            AudioPipeline(resolver, ProcessRunner(poll_interval=0.02, terminate_grace=0.2)).run(
                _request(synthetic_sources["wav"], tmp_path / "Downloads"), token=token
            )
        except AppError as exc:
            caught.append(exc)

    thread = threading.Thread(target=execute)
    thread.start()
    deadline = time.monotonic() + 5
    while not pid_file.exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    assert pid_file.exists()
    process_pid = int(pid_file.read_text())
    token.cancel()
    thread.join(timeout=5)
    assert not thread.is_alive()
    assert caught and caught[0].code is ErrorCode.CANCELLED
    assert not _pid_exists(process_pid)
    assert set(Path(tempfile.gettempdir()).glob("AudioShifter-*")) == before
    assert not list((tmp_path / "Downloads").glob("*.mp3"))
