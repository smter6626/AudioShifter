# AudioShifter v0.1.0-alpha.1 release verification

## Final status

```text
BLOCKED — project licence decision required before public release
```

All technical release-candidate checks passed and an authenticated GitHub Draft
Pre-release was created with all three required assets. It was not published.
The repository has no root-level `LICENSE`, `LICENSE.*`, `COPYING`, or
`COPYING.*` file. The visible repository and historical Windows activation
language do not grant a project source or binary distribution licence. This is
the owner decision gate defined by the release task, not a technical build
failure and not legal advice.

The single required owner decision is to identify and authorise a root project
licence compatible with the embedded GPL components, including the exact scope
of AudioShifter-owned code it covers. No licence was selected or added by the
release tooling.

## Git and GitHub Draft

- Release tag: `v0.1.0-alpha.1`
- Annotated tag object: `348e563dfcb42168b29866e5abb78cbd00569d37`
- Release/application commit: `d1f628503d08efd9813433274181a2a9fe5bec27`
- Final release-tooling commit used inside corresponding source:
  `c5ec2fcbcb5566dabd9ff45cd3ab49e1fe52db98`
- Draft database ID: `364786397`
- Draft URL (authenticated collaborators only):
  <https://github.com/smter6626/AudioShifter/releases/tag/untagged-35d3672bf3cc1ee4310c>
- Title: `AudioShifter v0.1.0-alpha.1 — macOS arm64 preview`
- State: Draft = `true`, Pre-release = `true`, published time = `null`
- Creation/upload path: GitHub CLI 2.96.0; computer-use was not needed.
- Tag evidence: the annotated tag API object resolves to release commit
  `d1f6285...`.

GitHub's automatic tag source ZIP and tar.gz were both actually downloaded.
Each extracted file manifest contained 89 entries and exactly matched a local
`git archive v0.1.0-alpha.1`, confirming that both automatic archives refer to
the same tag commit. They are not substitutes for the corresponding-source
asset.

## Build environment and command

- Date: 2026-08-04
- Host: Apple Silicon `arm64`
- macOS: 27.0, build `26A5378n`
- Python: 3.11.15
- PyInstaller: 6.21.0
- FFmpeg / FFprobe: 8.1.2
- Rubber Band: 4.0.0
- Reproducible command:

  ```bash
  macos/release/build_release_assets.sh
  ```

The command ran tests from the release-tooling commit, created a detached
worktree at `v0.1.0-alpha.1`, and built the application from that exact tag.
The current development virtual environment was only a build tool. It was not
copied into the application or release archives.

## Assets and checksums

| Asset | Bytes | SHA-256 |
|---|---:|---|
| `AudioShifter-v0.1.0-alpha.1-macOS27-arm64.zip` | 27,736,114 | `18b2d96b0802f5afb800b3ee6926e3a31b4bc9fecedbcd06182c266ca130d788` |
| `AudioShifter-v0.1.0-alpha.1-corresponding-source.tar.gz` | 199,987,644 | `a24e83225522dbc193e6a800625ce0f1652f03317693cce2064ada7a272f8340` |
| `SHA256SUMS.txt` | 234 | `4e7b7b4073b6304a0808dcb608d8b3307d1100277bfffe4ffcb035275d696a84` |

Exact `SHA256SUMS.txt` content:

```text
18b2d96b0802f5afb800b3ee6926e3a31b4bc9fecedbcd06182c266ca130d788  AudioShifter-v0.1.0-alpha.1-macOS27-arm64.zip
a24e83225522dbc193e6a800625ce0f1652f03317693cce2064ada7a272f8340  AudioShifter-v0.1.0-alpha.1-corresponding-source.tar.gz
```

GitHub reported all assets as `uploaded` and independently reported the same
SHA-256 digests and byte sizes.

## App ZIP verification

The application ZIP was created with:

```bash
ditto -c -k --sequesterRsrc --keepParent \
  macos/dist/AudioShifter.app \
  macos/release-dist/AudioShifter-v0.1.0-alpha.1-macOS27-arm64.zip
```

Verification was performed on a fresh `ditto -x -k` extraction, not on the
original `macos/dist` bundle.

- Extracted application logical file size: 63,356,565 bytes.
- Bundle identifier: `io.github.smter6626.audioshifter`.
- Custom `AudioShifter.icns` present and selected by `Info.plist`.
- 75 Mach-O files; every file is thin `arm64`.
- 324 dynamic references and 20 `LC_RPATH` commands audited.
- External non-system load commands: 0.
- `/opt/homebrew`, `.venv`, and repository runtime load commands: 0.
- Symlinks: 44; broken or external links: 0.
- `codesign --verify --deep --strict --verbose=4`: return code 0.
- Signature: ad-hoc; `TeamIdentifier=not set`.
- `spctl`: rejected as expected for a build without Developer ID or
  notarization.
- Restricted launch used PATH `/usr/bin:/bin:/usr/sbin:/sbin`, no
  `VIRTUAL_ENV`, and a system temporary working directory; the GUI remained
  alive for the three-second launch probe.

The extracted app's internal tools were the only process executables used:

```text
AudioShifter.app/Contents/Frameworks/bin/ffmpeg
AudioShifter.app/Contents/Frameworks/bin/ffprobe
AudioShifter.app/Contents/Frameworks/bin/rubberband
```

## Real pipeline and cancellation

The final extracted ZIP copy processed synthetic WAV, MP3, M4A, and FLAC input
under the restricted PATH. Every output stream had:

```text
codec_name=mp3
sample_rate=44100
channels=2
bit_rate=320000
```

Representative WAV output duration was 2.500000 seconds and output SHA-256 was
`c9232e4a165f4de240b5a061b6b1ab628e49e7a71748f4b6e10697ec8ac047a9`.
All input hashes remained unchanged. Repeated output allocation produced `_2`
and `_3`; the earlier output hash remained unchanged. A real Rubber Band
cancellation observed the bundle-internal process, reaped it, left zero partial
outputs and zero temporary workspace leaks, and preserved the source hash.

## Corresponding source and licences

- Conceptual third-party runtime components: 22.
- Exact source records: 23 (Tcl/Tk also records Python Tk integration source).
- Packaged Mach-O mappings: 75 of 75; unmapped = 0.
- Historical Homebrew formulae: 22.
- Applicable formula patches included and hashed: 8.
- Internal corresponding-source checksum entries: 193.
- AudioShifter repository archive tag/commit: `v0.1.0-alpha.1` /
  `d1f6285...`.
- The exact asset-generation scripts and tooling commit are separately included
  under `audioshifter/build-scripts/`.

Every formula source download was checked against the installed Cellar SPDX
SBOM and matching historical formula SHA-256. Installed versions, rather than
newer current formula versions, were used for dav1d 1.5.3, SVT-AV1 4.1.0, and
mpg123 1.33.6. Sources cover CPython, mpdecimal, XZ, Tcl/Tk, PyInstaller,
FFmpeg/FFprobe, Rubber Band, libvmaf, OpenSSL, libvpx, dav1d, LAME, Opus,
SVT-AV1, x264, x265, libsamplerate, libsndfile, mpg123, libogg, libvorbis,
and FLAC.

Official upstream source archives contained 64 precompiled files (10
PyInstaller bootloaders, 43 libvmaf MATLAB MEX/Windows helpers, and 11 Python/Tk
platform helpers). The collector first verified and recorded each official
archive checksum, then removed only magic-header-confirmed compiled files from
the attached source-only derivatives. Complete relevant source and build scripts
remain, and every excluded path is in `MANIFEST.json`. The final source package
binary audit passed.

Third-party licence texts and notices are included. The package does not claim
that compliance materials resolve the missing AudioShifter project licence.

## Draft download-back verification

All three assets were downloaded from the GitHub Draft into a fresh ignored
directory using `gh release download`. The downloaded files were byte-for-byte
identical to the local final assets, `shasum -a 256 -c SHA256SUMS.txt` returned
two `OK` results, and the full release verifier was rerun against only those
downloaded copies. ZIP extraction, codesign, Mach-O, symlink, restricted launch,
four-format processing, conflict, cancellation, source MANIFEST, patches, and
all internal hashes passed again.

## Gatekeeper and compatibility boundary

Release notes prominently state that this build uses PyInstaller ad-hoc signing,
has no Developer ID, notarization, or stapling, and may require a per-application
“系统设置 → 隐私与安全性 → 仍要打开” override after the first launch attempt.
They do not recommend globally disabling Gatekeeper.

The application is built and verified only on Apple Silicon arm64, macOS 27.0
build `26A5378n`. Older macOS versions are untested and may not run. Intel Mac,
Rosetta, and universal2 are unsupported.

## Test result and remaining action

```text
144 passed, 0 failed, 0 skipped
```

No Developer ID signing, notarization, stapling, public Release publication,
DMG creation, GitHub asset deletion/replacement, Windows modification, or tag
movement occurred. The Draft must remain unpublished until the project owner
makes the single licence decision described at the top of this report.
