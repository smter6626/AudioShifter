# AudioShifter v0.1.0-alpha.2 Draft verification

## Final status

```text
PARTIAL — v0.1.0-alpha.2 Draft prepared; awaiting user review and manual non-development-Mac acceptance
```

All automated, packaging, corresponding-source, upload, and download-back
checks passed. The GitHub Release remains a Draft and was not published. The
remaining action is the project owner's review and manual acceptance on a
non-development Apple Silicon Mac.

## Project licence and branding

- Copyright holder: Yeming Dai; notice: `Copyright (C) 2026 Yeming Dai`.
- Covered AudioShifter-owned code uses `GPL-3.0-or-later` as scoped by the root
  `LICENSING.md`.
- Root `LICENSE` is the unmodified official GNU GPL version 3 text: 35,149
  bytes, SHA-256
  `3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986`.
- All `windows/` history, the AudioShifter name/logo/application icon/official
  branding, and third-party material are excluded from the project GPL grant.
- `TRADEMARKS.md` allows descriptive references and unmodified official
  redistribution while requiring modified versions to use their own name,
  bundle identifier, icon, and branding. It does not restrict GPL commercial
  use, modification, or distribution under another brand.
- Python wheel metadata built from `pyproject.toml` reported
  `Metadata-Version: 2.4`, `Version: 0.1.0a2`, and
  `License-Expression: GPL-3.0-or-later`, with the project and third-party
  licence files listed as `License-File` entries.

The final application contains `LICENSE`, `LICENSING.md`, `TRADEMARKS.md`,
`THIRD_PARTY_NOTICES.md`, and `licenses/` in `Contents/Resources`. The packaged
GPL text has the same official SHA-256 above.

## Git and GitHub Draft

- Release tag: `v0.1.0-alpha.2`.
- Release/application/tooling commit:
  `64f5b664e8f6aca1fccc3d7f026f311959519120`.
- Draft database ID: `364826053`.
- Draft URL (authenticated collaborators only):
  <https://github.com/smter6626/AudioShifter/releases/tag/untagged-92e819bb21db79a10afc>
- Title: `AudioShifter v0.1.0-alpha.2 — macOS arm64 preview`.
- State: Draft = `true`, Pre-release = `true`, published time = `null`.
- Creation, upload, inspection, and download path: authenticated GitHub CLI
  2.96.0 with repository `ADMIN` permission; computer-use fallback was not
  required.
- The remote annotated tag resolves to the same release commit. The tag was
  used both for the application build and the embedded `git archive` repository
  source snapshot.

The alpha.1 internal candidate remains unchanged: tag commit
`d1f628503d08efd9813433274181a2a9fe5bec27`, Draft database ID `364786397`,
Draft = `true`, Pre-release = `true`, published time = `null`, and its original
three assets and digests remain present.

## Build environment and command

- Date: 2026-08-04.
- Host architecture: Apple Silicon `arm64`.
- macOS: 27.0, build `26A5378n`.
- Python: 3.11.15.
- PyInstaller: 6.21.0.
- FFmpeg / FFprobe: 8.1.2.
- Rubber Band: 4.0.0.
- Reproducible command:

  ```bash
  macos/release/build_release_assets.sh v0.1.0-alpha.2
  ```

The command first ran all tests, created a detached worktree at the annotated
tag, rebuilt and audited the app from that worktree, created the app archive
with `ditto`, collected exact corresponding source, and atomically placed the
three verified assets in the ignored `macos/release-dist/` directory.

## Draft assets and checksums

| Asset | Bytes | SHA-256 |
|---|---:|---|
| `AudioShifter-v0.1.0-alpha.2-macOS27-arm64.zip` | 27,753,339 | `d01c9a6e4fca0fd2dabfb8c27443d1c601d8c8b8e1f063b73f83ed3372c37525` |
| `AudioShifter-v0.1.0-alpha.2-corresponding-source.tar.gz` | 200,037,471 | `b6ab71d2ee0737329e43e42d4104ad21ad41a03c1d233817c6bceaaa3c598d0f` |
| `SHA256SUMS.txt` | 234 | `ec7e1bd893ec2ab4c06373984bb0fb9c3be9b08ea6878ba44be8d5c65750b1b2` |

Exact `SHA256SUMS.txt` content:

```text
d01c9a6e4fca0fd2dabfb8c27443d1c601d8c8b8e1f063b73f83ed3372c37525  AudioShifter-v0.1.0-alpha.2-macOS27-arm64.zip
b6ab71d2ee0737329e43e42d4104ad21ad41a03c1d233817c6bceaaa3c598d0f  AudioShifter-v0.1.0-alpha.2-corresponding-source.tar.gz
```

GitHub reported all three assets as `uploaded` and independently reported the
same byte sizes and SHA-256 digests.

## App ZIP and standalone verification

The application ZIP was created by `ditto -c -k --sequesterRsrc --keepParent`.
Every result below was reproduced on a fresh `ditto -x -k` extraction from the
final asset, not only on `macos/dist`:

- Extracted application logical size: 63,401,560 bytes.
- Bundle identifier: `io.github.smter6626.audioshifter`.
- `CFBundleShortVersionString`: `0.1.0-alpha.2`;
  `CFBundleVersion`: `2`.
- Custom `AudioShifter.icns` present and selected.
- 75 Mach-O files, all thin `arm64`.
- 324 dynamic references and 20 `LC_RPATH` commands audited.
- External non-system load commands: 0.
- `/opt/homebrew`, `.venv`, and repository runtime load commands: 0.
- Symlinks: 47; broken or bundle-external links: 0.
- `codesign --verify --deep --strict --verbose=4`: return code 0.
- Signature: ad-hoc; `TeamIdentifier=not set`.
- `spctl`: rejected as expected because there is no Developer ID signature or
  notarization.
- Restricted launch used PATH `/usr/bin:/bin:/usr/sbin:/sbin`, no
  `VIRTUAL_ENV`, and a system temporary working directory; the GUI remained
  alive through the launch probe.

The extracted app used only these internal command executables:

```text
AudioShifter.app/Contents/Frameworks/bin/ffmpeg
AudioShifter.app/Contents/Frameworks/bin/ffprobe
AudioShifter.app/Contents/Frameworks/bin/rubberband
```

## Real pipeline, naming, source protection, and cancellation

The extracted app processed synthetic WAV, MP3, M4A, and FLAC inputs under the
restricted PATH. Every output stream reported:

```text
codec_name=mp3
sample_rate=44100
channels=2
bit_rate=320000
```

Representative WAV output duration was 2.500000 seconds and SHA-256 was
`c9232e4a165f4de240b5a061b6b1ab628e49e7a71748f4b6e10697ec8ac047a9`.
All input hashes remained unchanged. Repeated allocation produced `_2` and
`_3`, and the prior output hash remained unchanged.

A real Rubber Band cancellation observed the bundle-internal process, reaped
it, left zero partial outputs and zero workspace leaks, and preserved the
source SHA-256. The verification temporary directory was removed after the
run.

## Corresponding source

- Project licence status in `MANIFEST.json`:
  `GPL-3.0-or-later for covered AudioShifter-owned code`.
- The manifest separately records branding, `windows/`, and third-party
  exclusions and hashes `LICENSE`, `LICENSING.md`, and `TRADEMARKS.md`.
- Conceptual third-party runtime components: 22.
- Exact source archive records: 23.
- Historical Homebrew formulae and receipts: 22 component formulae.
- Applicable formula patches included and hashed: 8.
- Packaged Mach-O mappings: 75 of 75; unmapped = 0.
- Internal corresponding-source checksum entries: 199.
- AudioShifter source tag and commit: `v0.1.0-alpha.2` /
  `64f5b664e8f6aca1fccc3d7f026f311959519120`.
- Release tooling commit is the same tag commit.

Each source was tied to the installed component version and checked against
the matching Homebrew SBOM/receipt and historical formula checksum. Applicable
patches, formulae, receipts, build evidence, packaged-file mappings, licence
texts, and the exact Release tools are included. The verifier found no missing
component, patch, hash, or unmapped packaged Mach-O and rejected compiled
third-party material from the final source package.

## Draft download-back verification

All three assets were downloaded from Draft ID `364826053` into a fresh ignored
directory using `gh release download`. Their sizes and hashes matched the local
final assets; the downloaded `SHA256SUMS.txt` was byte-for-byte identical and
reported two `OK` results.

The full verifier then ran only against the downloaded copies. App extraction,
project legal resources, codesign, Mach-O, dynamic paths, symlinks, restricted
launch, WAV/MP3/M4A/FLAC processing, conflict protection, cancellation,
corresponding-source MANIFEST, patches, and every internal hash all passed.

## Gatekeeper, compatibility, and remaining manual acceptance

Release notes state prominently that the app uses PyInstaller ad-hoc signing,
has no Developer ID, notarization, or stapling, and may require the
per-application “系统设置 → 隐私与安全性 → 仍要打开” action. They do not
recommend disabling Gatekeeper globally.

The application is built and verified only on Apple Silicon arm64, macOS 27.0
build `26A5378n`. Older macOS releases are untested and may not run. Intel Mac,
Rosetta, and universal2 are unsupported.

Automated result:

```text
153 passed, 0 failed, 0 skipped
```

The Draft must remain unpublished until the project owner reviews its notes,
licensing/branding scope, assets, and checksums and completes manual testing on
a non-development Mac. No Developer ID signing, notarization, stapling, DMG,
public Release publication, alpha.1 mutation, Windows modification, or Android
active-step change occurred.
