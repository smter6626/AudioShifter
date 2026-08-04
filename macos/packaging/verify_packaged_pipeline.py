#!/usr/bin/env python3
"""Exercise the real audio pipeline using only executables inside the built app."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from decimal import Decimal
from pathlib import Path
from typing import Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT / "macos" / "src"))

from audioshifter.dependencies import PackagedDependencyResolver, ResolvedDependencies
from audioshifter.errors import AppError, ErrorCode
from audioshifter.models import ProcessingRequest, ProcessingStage
from audioshifter.pipeline import AudioPipeline
from audioshifter.process_runner import CancellationToken, ProcessRunner


def run(args: Sequence[str | Path]) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(
        [str(value) for value in args],
        env={
            "HOME": os.environ["HOME"],
            "LANG": os.environ.get("LANG", "en_US.UTF-8"),
            "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
            "TMPDIR": tempfile.gettempdir(),
        },
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        shell=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.decode("utf-8", errors="replace"))
    return completed


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe(path: Path, dependencies: ResolvedDependencies) -> dict[str, object]:
    completed = run(
        (
            dependencies.ffprobe_path,
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_name,sample_rate,channels,bit_rate:format=duration,size,bit_rate",
            "-of",
            "json",
            path,
        )
    )
    return json.loads(completed.stdout)


class RecordingRunner(ProcessRunner):
    def __init__(self) -> None:
        super().__init__(poll_interval=0.02, terminate_grace=0.5)
        self.commands: list[tuple[str, ...]] = []

    def run(self, args, *, token, stage, cwd=None):
        rendered = tuple(str(value) for value in args)
        self.commands.append(rendered)
        return super().run(rendered, token=token, stage=stage, cwd=cwd)


def create_sources(root: Path, dependencies: ResolvedDependencies) -> dict[str, Path]:
    source_wav = root / "中文 打包测试 (space) & source.WAV"
    run(
        (
            dependencies.ffmpeg_path,
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:sample_rate=48000:duration=2",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            "-f",
            "wav",
            source_wav,
        )
    )
    sources = {
        "wav": source_wav,
        "mp3": root / "song.final.packaged.MP3",
        "m4a": root / "quote'packaged.M4A",
        "flac": root / "packaged audio.FLAC",
    }
    encoders = {
        "mp3": ("-c:a", "libmp3lame", "-b:a", "192k", "-f", "mp3"),
        "m4a": ("-c:a", "aac", "-f", "ipod"),
        "flac": ("-c:a", "flac", "-f", "flac"),
    }
    for name, arguments in encoders.items():
        run(
            (
                dependencies.ffmpeg_path,
                "-hide_banner",
                "-loglevel",
                "error",
                "-nostdin",
                "-i",
                source_wav,
                *arguments,
                sources[name],
            )
        )
    return sources


def verify_four_formats(
    root: Path,
    resolver: PackagedDependencyResolver,
    dependencies: ResolvedDependencies,
) -> tuple[list[dict[str, object]], RecordingRunner, dict[str, object]]:
    sources = create_sources(root, dependencies)
    downloads = root / "Downloads"
    downloads.mkdir()
    runner = RecordingRunner()
    pipeline = AudioPipeline(resolver, runner)
    workspace_before = {str(path) for path in Path(tempfile.gettempdir()).glob("AudioShifter-*")}
    results: list[dict[str, object]] = []
    first_result = None
    first_hash = None
    for format_name, source in sources.items():
        source_before = sha256(source)
        result = pipeline.run(ProcessingRequest(source, 3, Decimal("-20"), downloads))
        media = probe(result.output_path, dependencies)
        stream = media["streams"][0]
        if stream != {
            "codec_name": "mp3",
            "sample_rate": "44100",
            "channels": 2,
            "bit_rate": "320000",
        }:
            raise RuntimeError(f"Unexpected packaged output media for {format_name}: {media}")
        if result.output_path.name != f"{source.stem}+3-20%.mp3":
            raise RuntimeError(f"Unexpected packaged output name: {result.output_path.name}")
        if sha256(source) != source_before:
            raise RuntimeError(f"Source was modified: {source}")
        output_hash = sha256(result.output_path)
        if first_result is None:
            first_result = result
            first_hash = output_hash
        results.append(
            {
                "format": format_name,
                "input": str(source),
                "input_sha256_before_after": source_before,
                "output": str(result.output_path),
                "output_sha256": output_hash,
                "media": media,
            }
        )

    assert first_result is not None and first_hash is not None
    conflict_source = sources["wav"]
    conflict_request = ProcessingRequest(conflict_source, 3, Decimal("-20"), downloads)
    conflict_first = pipeline.run(conflict_request)
    conflict_first_hash = sha256(conflict_first.output_path)
    conflict_second = pipeline.run(conflict_request)
    if not conflict_second.output_path.stem.endswith("_3"):
        raise RuntimeError(f"Expected sequential no-overwrite suffix: {conflict_second.output_path}")
    if sha256(conflict_first.output_path) != conflict_first_hash:
        raise RuntimeError("Existing conflict output was overwritten")

    workspace_after = {str(path) for path in Path(tempfile.gettempdir()).glob("AudioShifter-*")}
    if workspace_after != workspace_before:
        raise RuntimeError(f"Packaged pipeline leaked workspaces: {workspace_after - workspace_before}")
    conflict = {
        "first": str(conflict_first.output_path),
        "second": str(conflict_second.output_path),
        "first_sha256_before_after": conflict_first_hash,
        "existing_output_preserved": True,
    }
    return results, runner, conflict


def verify_cancellation(
    root: Path,
    resolver: PackagedDependencyResolver,
    dependencies: ResolvedDependencies,
) -> dict[str, object]:
    source = root / "packaged cancellation 120s.WAV"
    run(
        (
            dependencies.ffmpeg_path,
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=330:sample_rate=44100:duration=120",
            "-ac",
            "2",
            "-c:a",
            "pcm_s16le",
            "-f",
            "wav",
            source,
        )
    )
    source_hash = sha256(source)
    downloads = root / "CancelDownloads"
    downloads.mkdir()
    runner = RecordingRunner()
    token = CancellationToken()
    processing_started = threading.Event()
    errors: list[AppError] = []
    workspace_before = {str(path) for path in Path(tempfile.gettempdir()).glob("AudioShifter-*")}

    def stage_callback(event) -> None:
        if event.stage is ProcessingStage.PROCESSING:
            processing_started.set()

    def execute() -> None:
        try:
            AudioPipeline(resolver, runner).run(
                ProcessingRequest(source, 0, Decimal("-95"), downloads),
                token=token,
                on_stage=stage_callback,
            )
        except AppError as exc:
            errors.append(exc)

    thread = threading.Thread(target=execute, name="packaged-cancel-verification")
    thread.start()
    if not processing_started.wait(20):
        raise RuntimeError("Packaged cancellation did not reach Rubber Band stage")
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if runner.active_pid is not None and runner.commands and Path(runner.commands[-1][0]).name == "rubberband":
            break
        time.sleep(0.01)
    active_pid = runner.active_pid
    if active_pid is None or Path(runner.commands[-1][0]).name != "rubberband":
        raise RuntimeError("Could not observe packaged Rubber Band process for cancellation")
    rubberband_command = runner.commands[-1][0]
    token.cancel()
    thread.join(timeout=20)
    if thread.is_alive() or not errors or errors[0].code is not ErrorCode.CANCELLED:
        raise RuntimeError(f"Packaged cancellation failed: alive={thread.is_alive()} errors={errors}")
    try:
        os.kill(active_pid, 0)
    except ProcessLookupError:
        process_reaped = True
    else:
        process_reaped = False
    workspace_after = {str(path) for path in Path(tempfile.gettempdir()).glob("AudioShifter-*")}
    output_files = tuple(downloads.glob("*.mp3"))
    if not process_reaped or output_files or workspace_after != workspace_before or sha256(source) != source_hash:
        raise RuntimeError(
            "Packaged cancellation leaked a process, output, workspace, or changed source: "
            f"reaped={process_reaped} outputs={output_files} workspaces={workspace_after - workspace_before}"
        )
    return {
        "rubberband_path": rubberband_command,
        "observed_pid": active_pid,
        "process_reaped": process_reaped,
        "partial_outputs": 0,
        "workspace_leaks": 0,
        "source_sha256_before_after": source_hash,
    }


def verify(app: Path) -> dict[str, object]:
    app = app.resolve()
    resource_root = app / "Contents" / "Frameworks"
    resolver = PackagedDependencyResolver(resource_root)
    dependencies = resolver.resolve()
    for path in (dependencies.ffmpeg_path, dependencies.ffprobe_path, dependencies.rubberband_path):
        path.relative_to(app)
    with tempfile.TemporaryDirectory(prefix="AudioShifter-packaged-verification-") as directory:
        root = Path(directory)
        format_results, runner, conflict = verify_four_formats(root, resolver, dependencies)
        cancellation = verify_cancellation(root, resolver, dependencies)
    command_executables = sorted({command[0] for command in runner.commands})
    if any(not str(path).startswith(str(app) + os.sep) for path in map(Path, command_executables)):
        raise RuntimeError(f"Pipeline used a non-bundle executable: {command_executables}")
    return {
        "app": str(app),
        "dependency_paths": {
            "ffmpeg": str(dependencies.ffmpeg_path),
            "ffprobe": str(dependencies.ffprobe_path),
            "rubberband": str(dependencies.rubberband_path),
        },
        "restricted_path": "/usr/bin:/bin:/usr/sbin:/sbin",
        "formats": format_results,
        "command_executables": command_executables,
        "conflict": conflict,
        "cancellation": cancellation,
        "temporary_verification_directory_removed": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "app",
        nargs="?",
        type=Path,
        default=REPOSITORY_ROOT / "macos" / "dist" / "AudioShifter.app",
    )
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    payload = verify(args.app)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
