#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Yeming Dai
"""Verify final release assets, including freshly extracted app and source."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import tarfile
import tempfile
import time
from pathlib import Path
from typing import Any, Sequence

from release_manifest import COMPONENTS, sha256_file
from release_config import RELEASE_TAG, app_asset_name, source_asset_name


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PYTHON = REPOSITORY_ROOT / "macos/.venv/bin/python"
FORBIDDEN_TEXT = (
    str(Path.home()),
    str(REPOSITORY_ROOT),
    "gh" + "p_",
    "github" + "_pat_",
)
GPL_V3_OFFICIAL_SHA256 = "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986"


def run(
    args: Sequence[str | Path],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(
        [str(value) for value in args],
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        shell=False,
    )
    if completed.returncode:
        raise RuntimeError(
            f"Command failed ({completed.returncode}): {args!r}\n"
            + completed.stdout.decode("utf-8", errors="replace")
            + completed.stderr.decode("utf-8", errors="replace")
        )
    return completed


def verify_checksum_file(root: Path, checksum_file: Path) -> int:
    lines = [line for line in checksum_file.read_text(encoding="utf-8").splitlines() if line]
    if not lines:
        raise RuntimeError(f"Checksum file is empty: {checksum_file}")
    for line in lines:
        digest, separator, relative = line.partition("  ")
        if separator != "  " or not relative or Path(relative).is_absolute():
            raise RuntimeError(f"Invalid SHA256SUMS line: {line!r}")
        target = root / relative
        if not target.is_file():
            raise FileNotFoundError(f"SHA256SUMS target is missing: {target}")
        actual = sha256_file(target)
        if actual != digest:
            raise RuntimeError(f"Checksum mismatch for {relative}: expected {digest}, got {actual}")
    return len(lines)


def launch_restricted(app: Path) -> dict[str, Any]:
    executable = app / "Contents/MacOS/AudioShifter"
    env = {
        "HOME": os.environ["HOME"],
        "LANG": os.environ.get("LANG", "en_US.UTF-8"),
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "TMPDIR": tempfile.gettempdir(),
    }
    process = subprocess.Popen(
        [str(executable)],
        cwd=tempfile.gettempdir(),
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    time.sleep(3)
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        raise RuntimeError(
            f"Extracted app exited during restricted-PATH launch ({process.returncode})\n"
            + stdout.decode("utf-8", errors="replace")
            + stderr.decode("utf-8", errors="replace")
        )
    os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=5)
        raise RuntimeError("Extracted app did not exit after restricted-PATH launch verification")
    return {
        "executable": str(executable),
        "cwd": tempfile.gettempdir(),
        "path": env["PATH"],
        "virtual_env_set": False,
        "remained_running_for_seconds": 3,
        "terminated_for_test": True,
    }


def verify_source(root: Path, tag: str, expected_commit: str) -> dict[str, Any]:
    package = root / f"AudioShifter-{tag}-corresponding-source"
    if not package.is_dir():
        raise FileNotFoundError(f"Corresponding-source root is missing: {package}")
    internal_count = verify_checksum_file(package, package / "SHA256SUMS.txt")
    manifest = json.loads((package / "MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("release") != tag or manifest.get("release_commit") != expected_commit:
        raise RuntimeError("Corresponding-source tag or commit does not match the release")
    expected_project_status = "GPL-3.0-or-later for covered AudioShifter-owned code"
    if manifest.get("project_licence_status") != expected_project_status:
        raise RuntimeError(f"Unexpected project licence status: {manifest.get('project_licence_status')}")
    project_licensing = manifest.get("project_licensing", {})
    if project_licensing.get("spdx_expression") != "GPL-3.0-or-later":
        raise RuntimeError("Corresponding source lacks the GPL-3.0-or-later project grant")
    exclusions = "\n".join(project_licensing.get("excluded", []))
    for required in ("TRADEMARKS.md", "windows/", "third-party"):
        if required not in exclusions:
            raise RuntimeError(f"Corresponding source licence exclusions omit {required}")
    project_files = project_licensing.get("files", {})
    for name in ("LICENSE", "LICENSING.md", "TRADEMARKS.md"):
        record = project_files.get(name, {})
        path = package / record.get("path", "missing")
        if not path.is_file() or sha256_file(path) != record.get("sha256"):
            raise RuntimeError(f"Project licensing material is missing or mismatched: {name}")
    if sha256_file(package / project_files["LICENSE"]["path"]) != GPL_V3_OFFICIAL_SHA256:
        raise RuntimeError("Corresponding-source LICENSE is not official GPLv3 text")
    if manifest.get("component_count") != len(COMPONENTS):
        raise RuntimeError(f"Unexpected component count: {manifest.get('component_count')}")
    components = manifest.get("components", [])
    expected_ids = {component.key for component in COMPONENTS}
    actual_ids = {component.get("id") for component in components}
    if actual_ids != expected_ids:
        raise RuntimeError(f"Component inventory differs: expected={expected_ids}, actual={actual_ids}")
    packaged_files: list[str] = []
    source_archives = 0
    patch_count = 0
    for component in components:
        files = component.get("packaged_files", [])
        if not files:
            raise RuntimeError(f"Component has no packaged file mapping: {component.get('id')}")
        packaged_files.extend(files)
        sources = component.get("sources", [])
        if not sources:
            raise RuntimeError(f"Component has no source record: {component.get('id')}")
        for source in sources:
            source_path = package / source["source_archive"]
            if not source_path.is_file() or sha256_file(source_path) != source["source_sha256"]:
                raise RuntimeError(f"Source archive missing or mismatched: {source_path}")
            if source.get("expected_source_sha256") and source["source_sha256"] != source["expected_source_sha256"]:
                raise RuntimeError(f"Source formula checksum mismatch: {source_path}")
            if (
                source.get("expected_upstream_archive_sha256")
                and source.get("upstream_archive_sha256")
                != source["expected_upstream_archive_sha256"]
            ):
                raise RuntimeError(f"Upstream formula checksum mismatch: {source_path}")
            source_archives += 1
            for field in ("formula_file", "formula_commit_evidence", "receipt", "sbom", "build_options"):
                value = source.get(field)
                if value and not (package / value).is_file():
                    raise RuntimeError(f"Source metadata is missing: {field}={value}")
            for patch in source.get("patches", []):
                if not (package / patch).is_file():
                    raise RuntimeError(f"Formula patch is missing: {patch}")
                patch_count += 1
    if len(packaged_files) != manifest.get("macho_count") or len(set(packaged_files)) != len(packaged_files):
        raise RuntimeError("Mach-O mapping count is incomplete or contains duplicates")
    if manifest.get("unmapped_macho_files"):
        raise RuntimeError(f"Unmapped Mach-O files: {manifest['unmapped_macho_files']}")

    source_record = manifest["audioshifter_source"]
    repository_archive = package / source_record["archive"]
    if sha256_file(repository_archive) != source_record["sha256"]:
        raise RuntimeError("Tagged AudioShifter repository archive checksum differs")
    if (package / "audioshifter/git-tag.txt").read_text(encoding="utf-8").strip() != tag:
        raise RuntimeError("Tagged source records the wrong tag")
    if (package / "audioshifter/git-commit.txt").read_text(encoding="utf-8").strip() != expected_commit:
        raise RuntimeError("Tagged source records the wrong commit")
    with tempfile.TemporaryDirectory(prefix="AudioShifter-tagged-source-audit-") as temporary:
        tagged_source = Path(temporary)
        with tarfile.open(repository_archive, "r:gz") as archive:
            archive.extractall(tagged_source, filter="data")
        for name in ("LICENSE", "LICENSING.md", "TRADEMARKS.md"):
            tagged_path = tagged_source / name
            if not tagged_path.is_file():
                raise RuntimeError(f"Tagged repository source omits project licensing file: {name}")
        if sha256_file(tagged_source / "LICENSE") != GPL_V3_OFFICIAL_SHA256:
            raise RuntimeError("Tagged repository source contains an unexpected LICENSE")
    tooling_commit = (package / "audioshifter/release-tooling-commit.txt").read_text(
        encoding="utf-8"
    ).strip()
    if manifest.get("release_tooling_commit") != tooling_commit:
        raise RuntimeError("Release tooling commit evidence differs from MANIFEST")
    if not (package / "audioshifter/build-scripts/build_release_assets.sh").is_file():
        raise RuntimeError("Exact release build scripts are absent from corresponding source")

    binary_candidate_suffixes = {".dylib", ".so", ".a", ".o", ".exe", ".dll"}
    for archive_path in (package / "third-party").rglob("*"):
        if not archive_path.is_file():
            continue
        bad: list[str] = []
        with tempfile.TemporaryDirectory(prefix="AudioShifter-source-binary-audit-") as temporary:
            with tarfile.open(archive_path, "r:*") as archive:
                candidates = [
                    member
                    for member in archive.getmembers()
                    if member.isfile()
                    and (
                        member.mode & 0o111
                        or Path(member.name).suffix.lower() in binary_candidate_suffixes
                    )
                ]
                for member in candidates:
                    archive.extract(member, temporary, filter="data")
                    extracted = Path(temporary) / member.name
                    description = run(("file", "-b", extracted)).stdout.decode(
                        "utf-8", errors="replace"
                    )
                    if any(kind in description for kind in ("Mach-O", "PE32", "ELF", "current ar archive")):
                        bad.append(member.name)
        if bad:
            raise RuntimeError(f"Third-party source archive contains compiled binary-looking files: {archive_path}: {bad[:10]}")

    for path in package.rglob("*"):
        if not path.is_file() or path.suffix.lower() in {".gz", ".xz", ".bz2", ".tgz"}:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        if any(fragment and fragment in content for fragment in FORBIDDEN_TEXT):
            raise RuntimeError(f"Private path or token prefix appears in corresponding source: {path}")
    return {
        "component_count": len(components),
        "macho_mapping_count": len(packaged_files),
        "unmapped_macho_files": 0,
        "source_archive_records": source_archives,
        "patch_count": patch_count,
        "internal_checksum_count": internal_count,
        "release_commit": expected_commit,
        "release_tooling_commit": tooling_commit,
        "tag": tag,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets-dir", type=Path, required=True)
    parser.add_argument("--tag", default=RELEASE_TAG)
    parser.add_argument("--commit")
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    assets = args.assets_dir.resolve()
    commit = args.commit or run(("git", "rev-parse", f"{args.tag}^{{commit}}"), cwd=REPOSITORY_ROOT).stdout.decode().strip()
    expected_names = {
        app_asset_name(args.tag),
        source_asset_name(args.tag),
        "SHA256SUMS.txt",
    }
    actual_names = {path.name for path in assets.iterdir() if path.is_file()}
    if actual_names != expected_names:
        raise RuntimeError(f"Release asset set differs: expected={expected_names}, actual={actual_names}")
    outer_checksums = verify_checksum_file(assets, assets / "SHA256SUMS.txt")
    if outer_checksums != 2:
        raise RuntimeError(f"Expected two outer checksums, found {outer_checksums}")

    work_parent = (args.work_dir or Path(tempfile.mkdtemp(prefix="AudioShifter-release-verify-"))).resolve()
    own_work_parent = args.work_dir is None
    if not own_work_parent:
        allowed_parent = (REPOSITORY_ROOT / "macos/release-work").resolve()
        if work_parent.parent != allowed_parent or work_parent.name != "verification":
            raise RuntimeError(f"Refusing to reset unsafe verification directory: {work_parent}")
    if work_parent.exists() and not own_work_parent:
        shutil.rmtree(work_parent)
        work_parent.mkdir(parents=True)
    elif not work_parent.exists():
        work_parent.mkdir(parents=True)
    try:
        app_extract = work_parent / "app"
        app_extract.mkdir(parents=True)
        run(("ditto", "-x", "-k", assets / app_asset_name(args.tag), app_extract))
        app = app_extract / "AudioShifter.app"
        app_audit_path = work_parent / "extracted-app-audit.json"
        app_audit = json.loads(
            run(
                (
                    PYTHON,
                    REPOSITORY_ROOT / "macos/packaging/verify_app.py",
                    app,
                    "--json-output",
                    app_audit_path,
                )
            ).stdout.decode("utf-8")
        )
        pipeline_path = work_parent / "extracted-app-pipeline.json"
        pipeline = json.loads(
            run(
                (
                    PYTHON,
                    REPOSITORY_ROOT / "macos/packaging/verify_packaged_pipeline.py",
                    app,
                    "--json-output",
                    pipeline_path,
                )
            ).stdout.decode("utf-8")
        )
        restricted_launch = launch_restricted(app)

        source_extract = work_parent / "source"
        source_extract.mkdir()
        with tarfile.open(assets / source_asset_name(args.tag), "r:gz") as archive:
            archive.extractall(source_extract, filter="data")
        source_audit = verify_source(source_extract, args.tag, commit)
        result = {
            "status": "PASS",
            "assets_dir": str(assets),
            "tag": args.tag,
            "commit": commit,
            "asset_sizes": {name: (assets / name).stat().st_size for name in sorted(expected_names)},
            "asset_sha256": {
                name: sha256_file(assets / name)
                for name in sorted(expected_names)
                if name != "SHA256SUMS.txt"
            },
            "outer_checksum_count": outer_checksums,
            "extracted_app": app_audit,
            "extracted_pipeline": pipeline,
            "restricted_launch": restricted_launch,
            "corresponding_source": source_audit,
        }
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.json_output:
            args.json_output.parent.mkdir(parents=True, exist_ok=True)
            args.json_output.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
    finally:
        if own_work_parent:
            shutil.rmtree(work_parent, ignore_errors=True)


if __name__ == "__main__":
    main()
