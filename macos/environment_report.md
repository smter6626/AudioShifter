# AudioShifter macOS Environment Report

## 1. Report scope and date

- Report date: 2026-08-02 (MST)
- Repository: `/Users/smterpro/Workspace/Tools/AudioShifter/`
- Baseline commit before environment work: `e51e00d`
- Scope: establish and verify the Apple Silicon development toolchain only. No GUI, application business module, formal test suite, PyInstaller build, or distributable application was created.
- Evidence policy: statements marked **verified** come from commands executed on this machine; upstream/version statements link to first-party project or Homebrew sources; unresolved packaging and compatibility claims are marked **pending**.

## 2. Target platform and distribution boundary

- Target: Apple Silicon `arm64` only.
- Excluded: Intel Mac, `x86_64` execution, Rosetta, universal application output, Developer ID signing, Apple notarization, and Mac App Store distribution.
- No minimum macOS version is claimed. The development machine and current dependencies are recorded, but the eventual compatibility floor can only be established with packaging and testing on the intended oldest system.
- PyInstaller is not a cross-compiler and its documentation says macOS output compatibility depends on the build system. This report does not turn the current development OS into a product support promise.

## 3. Development machine

| Item | Verified value |
| -- | -- |
| Model identifier | `Mac16,5` |
| Operating system | macOS 27.0, build `26A5378n` |
| Kernel | Darwin 27.0.0, `RELEASE_ARM64_T6041` |
| Machine architecture | `uname -m`: `arm64`; `arch`: `arm64`; `hw.optional.arm64`: `1` |
| Rosetta translation | `sysctl.proc_translated`: `0`; Homebrew: `Rosetta 2: false` |
| Shell | `/bin/zsh` |
| Homebrew | 6.0.12, `/opt/homebrew`, CPU `arm_brava`, macOS `27.0-arm64` |
| Homebrew runtime | portable Ruby 4.0.6, Mach-O `arm64` |
| Free disk before setup | 456 GiB |

**Verified conclusion:** the host, shell session, Homebrew runtime, and selected project tools run natively on Apple Silicon. No Intel Homebrew was found under `/usr/local` and PATH resolves `/opt/homebrew` first.

## 4. Pre-existing environment

- The repository was clean, on `main`, tracking SSH `origin/main`, and `git pull --ff-only` reported it was already current.
- Project-related Homebrew formulae already present before this work:
  - `python@3.11 3.11.15_4`
  - `python-tk@3.11 3.11.15`
  - `tcl-tk@8 8.6.18` (dependency)
  - `ffmpeg 8.1.2_1`
  - `rubberband 4.0.0` (installed as a dependency before this task)
  - `libsndfile 1.2.2_1` (dependency)
- `brew outdated` returned no selected formula. `brew install --dry-run` reported all four direct formulae already installed and current, so no Homebrew installation, upgrade, update, cleanup, or reinstall was performed.
- `/usr/bin/python3` is Apple Command Line Tools Python 3.9.6. It is a universal binary and executed as arm64, but was rejected for the project because its lifecycle and Tk/build ownership are controlled by the OS/CLT rather than the repository setup.
- Homebrew `uv 0.11.28` and `conda 26.3.2` exist, but neither was used or modified. No `pyenv` was found.
- A separate `ffmpeg@7` is installed on the machine, but it was not selected, linked, upgraded, or modified; `/opt/homebrew/bin/ffmpeg` resolves to FFmpeg 8.1.2.

## 5. Dependency classification

- **Direct runtime dependencies:** Python 3.11, Python Tkinter support, FFmpeg CLI, and Rubber Band CLI. The future application must carry the required runtime components rather than requiring end users to install Homebrew.
- **Python development dependency:** PyInstaller's pip-managed support packages are transitive development dependencies.
- **Later packaging dependency:** PyInstaller 6.21.0.
- **Transitive dependencies:** Tcl/Tk 8 through `python-tk@3.11`; libsndfile and libsamplerate through the Rubber Band CLI; FFmpeg formula libraries such as LAME through FFmpeg.
- **System-provided components:** macOS frameworks and system libraries reported by `otool`, including Accelerate, AppKit/Cocoa, AudioToolbox, CoreAudio, Foundation, and `libSystem`.
- **Currently not needed as a direct dependency:** libsndfile. The project does not call it directly in the selected command-line design, so it is intentionally absent from `Brewfile`.

## 6. Version selection decisions

### Python and Tcl/Tk

- Upstream Python 3.11 is in security-fixes-only maintenance through October 2027. The selected release is Python 3.11.15, released on 2026-03-03. Sources: [Python version status](https://devguide.python.org/versions/) and [Python 3.11.15 release](https://www.python.org/downloads/release/python-31115/).
- Homebrew supplies an Apple Silicon bottle for Python 3.11.15 and lists deprecation on 2027-11-01 and disablement on 2028-11-01: [Homebrew python@3.11](https://formulae.brew.sh/formula/python%403.11).
- Python 3.11 was chosen over 3.12/3.13/3.14 because the required 3.11 + Tk 8.6 pair was already installed, current, native arm64, and compatible with stable PyInstaller. Current newer Homebrew `python-tk` formulae depend on the unversioned Tcl/Tk line rather than `tcl-tk@8`, which would introduce a Tcl/Tk major-version change without a present project requirement.
- Tk 8.6.18 is deliberately retained for this environment. Tcl/Tk 9 is newer, but selecting it solely for recency would add avoidable packaging risk. This is an environment choice, not a future product compatibility promise.

### FFmpeg and Rubber Band

- FFmpeg upstream and Homebrew both identify 8.1.2 as current stable; the standard Homebrew formula already provides the required formats and `libmp3lame`. A custom or `ffmpeg-full` build is unnecessary. Sources: [FFmpeg downloads](https://ffmpeg.org/download.html) and [Homebrew ffmpeg](https://formulae.brew.sh/formula/ffmpeg).
- Rubber Band upstream and Homebrew both identify 4.0.0 as current. Its CLI and required options are present, so no custom build is needed. Sources: [Rubber Band official site](https://www.breakfastquay.com/rubberband/) and [Homebrew rubberband](https://formulae.brew.sh/formula/rubberband.html).
- libsndfile 1.2.2 is current upstream and is required by the Rubber Band command-line tool, not directly by AudioShifter. Sources: [libsndfile releases](https://github.com/libsndfile/libsndfile/releases/) and [Homebrew libsndfile](https://formulae.brew.sh/formula/libsndfile).

### PyInstaller

- Selected/current: PyInstaller 6.21.0. It supports Python 3.8+ and is tested on macOS. Its macOS requirements include arm64 output support. Sources: [PyInstaller manual](https://pyinstaller.org/en/stable/) and [macOS requirements](https://pyinstaller.org/en/stable/requirements.html).
- The installed wheel contains universal2 bootloader inputs with an arm64 slice. The `pyinstaller` command itself is a script executed by the native arm64 virtual-environment Python. No bootloader was run and no package was built in this task. A future build must explicitly verify that the produced application is arm64-only.

## 7. Installation actions

1. Set `HOMEBREW_NO_AUTO_UPDATE=1` for assessment commands. No global `brew update`, `upgrade`, or `cleanup` was run.
2. Confirmed by dry-run that `python@3.11`, `python-tk@3.11`, `ffmpeg`, and `rubberband` were already installed and current; no system formula changed.
3. A diagnostic `brew linkage` query automatically enabled Homebrew developer mode. It was immediately restored with `brew developer off`; subsequent `brew config` showed no developer-mode entry.
4. Created `macos/.venv/` with `/opt/homebrew/opt/python@3.11/bin/python3.11 -m venv macos/.venv`.
5. Initial virtual-environment tools were pip 26.1.2 and setuptools 83.0.0. Neither was upgraded; the later pip 26.2 notice was intentionally not acted on.
6. Installed `PyInstaller==6.21.0` in the virtual environment. No global or system pip was used.

## 8. Installed component inventory

| Component | Classification | Selected version | Actual version | Source | Path | Architecture | Status |
| -- | -- | ---: | ---: | -- | -- | -- | -- |
| CPython | Direct runtime dependency | 3.11.15 | 3.11.15 (`3.11.15_4` formula) | Homebrew | `/opt/homebrew/opt/python@3.11/bin/python3.11` | arm64 | PASS |
| `_tkinter` | Direct runtime dependency | 3.11.15 / Tk 8.6 | 3.11.15 | Homebrew `python-tk@3.11` | `/opt/homebrew/opt/python-tk@3.11/libexec/_tkinter.cpython-311-darwin.so` | arm64 | PASS |
| Tcl/Tk | Transitive dependency | 8.6.18 | 8.6.18 | Homebrew `tcl-tk@8` | `/opt/homebrew/opt/tcl-tk@8/` | arm64 | PASS |
| FFmpeg / ffprobe | Direct runtime dependency | 8.1.2 | 8.1.2 (`8.1.2_1` formula) | Homebrew | `/opt/homebrew/bin/ffmpeg`, `/opt/homebrew/bin/ffprobe` | arm64 | PASS |
| Rubber Band CLI | Direct runtime dependency | 4.0.0 | 4.0.0 | Homebrew | `/opt/homebrew/bin/rubberband` | arm64 | PASS |
| libsndfile | Transitive dependency | 1.2.2 | 1.2.2 (`1.2.2_1` formula) | Homebrew via Rubber Band | `/opt/homebrew/opt/libsndfile/lib/libsndfile.1.dylib` | arm64 | PASS |
| libsamplerate | Transitive dependency | Homebrew formula | 0.2.2 | Homebrew via Rubber Band | `/opt/homebrew/opt/libsamplerate/lib/libsamplerate.0.dylib` | arm64 | PASS |
| PyInstaller | Later packaging dependency | 6.21.0 | 6.21.0 | PyPI in `.venv` | `macos/.venv/bin/pyinstaller` | arm64 Python process; bootloader inputs include arm64 | PASS (install/import only) |
| macOS frameworks | System-provided components | Current OS | macOS 27.0 | Apple | `/System/Library/Frameworks/`, `/usr/lib/` | arm64 system | PASS |

## 9. Python virtual environment

- Location: `macos/.venv/`
- Git exclusion: `.gitignore` line 6, `.venv/`; both the directory and `macos/.venv/bin/python` were confirmed ignored.
- Python executable: `/Users/smterpro/Workspace/Tools/AudioShifter/macos/.venv/bin/python`
- Python: 3.11.15, `platform.machine() == "arm64"`
- pip: 26.1.2; setuptools: 83.0.0; no baseline tool upgrade was performed.
- Installed pip packages after setup:

| Package | Actual version | Dependency role |
| -- | --: | -- |
| PyInstaller | 6.21.0 | Direct development/packaging dependency |
| altgraph | 0.17.5 | PyInstaller transitive dependency |
| macholib | 1.16.4 | PyInstaller transitive dependency |
| packaging | 26.2 | PyInstaller transitive dependency |
| pyinstaller-hooks-contrib | 2026.6 | PyInstaller transitive dependency |

PyInstaller includes standard `_tkinter` analysis and runtime hooks. Extra project hooks are not currently justified; actual packaging may reveal additional requirements and remains pending.

## 10. Tkinter and Tcl/Tk verification

- `import tkinter`: PASS
- Python API versions: `TkVersion == 8.6`, `TclVersion == 8.6`
- Runtime patchlevels: Tcl 8.6.18, Tk 8.6.18
- Windowing system: `aqua`
- Minimal test: created `tk.Tk()`, withdrew the window, ran `update_idletasks()`, and destroyed it successfully.
- Result: `Tkinter window initialization: PASS`
- Dynamic source: `_tkinter` links `/opt/homebrew/opt/tcl-tk@8/lib/libtcl8.6.dylib` and `libtk8.6.dylib`; both resolved to arm64 Homebrew dylibs.

## 11. FFmpeg capability verification

- Executable: `/opt/homebrew/Cellar/ffmpeg/8.1.2_1/bin/ffmpeg`, Mach-O arm64.
- `ffmpeg -version` and `ffprobe -version`: PASS, version 8.1.2.
- Relevant build flags: `--enable-shared`, `--enable-version3`, `--enable-gpl`, `--enable-libmp3lame`, `--enable-libx264`, `--enable-libx265`, `--enable-audiotoolbox`, and `--enable-neon`.
- MP3 encoder: `libmp3lame` present; `libavcodec` dynamically resolves `libmp3lame.0.dylib` as arm64.
- Decoder/format listings confirm MP3, AAC/M4A, PCM WAV, and FLAC support.

Synthetic 4.0-second, 44.1 kHz stereo input results:

| File | Codec | Detected format | Sample rate | Channels | FFmpeg full-read result |
| -- | -- | -- | --: | --: | -- |
| WAV | `pcm_s16le` | `wav` | 44100 | 2 | PASS |
| MP3 | `mp3` | `mp3` | 44100 | 2 | PASS |
| M4A | `aac` | `mov,mp4,m4a,3gp,3g2,mj2` | 44100 | 2 | PASS |
| FLAC | `flac` | `flac` | 44100 | 2 | PASS |

These checks establish tool capability only and do not expand or finalize the product input contract.

## 12. Rubber Band verification

- Executable: `/opt/homebrew/Cellar/rubberband/4.0.0/bin/rubberband`, Mach-O arm64.
- `rubberband --version`: 4.0.0.
- Homebrew formula includes the CLI and links it to libsamplerate and libsndfile.
- Actual help confirms:
  - `-p` / `--pitch`: semitone pitch offset.
  - `-T` / `--tempo`: tempo multiplier; `0.9` means time ratio `1 / 0.9`.
  - `-3` / `--fine`: R3 finer engine.
  - `-F` / `--formant`: formant preservation.
- The smoke run reported `Using R3 (finer) engine`, time ratio 1.11111, frequency ratio 1.12246 for +2 semitones, and zero frame-count error.

## 13. Dynamic linking and transitive dependencies

- `_tkinter` → Homebrew Tcl 8.6 and Tk 8.6 dylibs, both arm64.
- FFmpeg executable → Homebrew FFmpeg shared libraries and formula dependencies. Direct and inspected linked Homebrew libraries resolved as arm64; the completed decode/encode tests found no loader failure.
- `libavcodec` → `libmp3lame`, confirming the selected MP3 encoding path.
- Rubber Band CLI → Accelerate (system), libsamplerate (Homebrew), libsndfile (Homebrew), libc++ and libSystem. Both Homebrew dylibs are arm64.
- libsndfile itself resolves FLAC, Ogg/Vorbis, Opus, mpg123, and LAME libraries. It is a Rubber Band CLI/Homebrew transitive dependency and is not a project direct dependency.

## 14. Command-line smoke test

The test used a unique `mktemp` directory under the system temporary root, never the repository. Representative three-stage commands were:

```bash
ffmpeg -hide_banner -loglevel error -y -i "$TEST_DIR/source.m4a" \
  -ac 2 -ar 44100 -codec:a pcm_s16le "$TEST_DIR/normalized.wav"

rubberband --pitch 2 --tempo 0.9 --fine --formant \
  "$TEST_DIR/normalized.wav" "$TEST_DIR/processed.wav"

ffmpeg -hide_banner -loglevel error -y -i "$TEST_DIR/processed.wav" \
  -codec:a libmp3lame -b:a 320k "$TEST_DIR/output.mp3"
```

Verified results:

- All three commands exited 0; all intermediate and final files existed and were non-empty.
- Normalized WAV: PCM s16le, 44.1 kHz, 2 channels, 4.017052 seconds.
- Rubber Band WAV: PCM s16le, 44.1 kHz, 2 channels, 4.463401 seconds.
- Final output: MP3, 44.1 kHz, stereo, 4.463401 seconds, 180,811 bytes; `ffprobe` read it successfully.
- Observed duration ratio: 1.111114; expected for tempo 0.9: 1.111111. This is a toolchain sanity check, not a formal product tolerance.
- The safety layer rejected an initial script containing `rm -rf` before that script started, so it created no data. The executed test used a validated temporary path and safe per-entry deletion followed by `rmdir`; cleanup verification returned PASS.

## 15. Reproducible setup

Committed configuration:

- `macos/Brewfile`: direct Homebrew formulae only. It intentionally omits Homebrew-installed transitive dependencies such as libsndfile.
- `macos/requirements-dev.txt`: direct pip development dependency pinned to PyInstaller 6.21.0.

Reproduction sequence:

```bash
HOMEBREW_NO_AUTO_UPDATE=1 brew bundle --file=macos/Brewfile
/opt/homebrew/opt/python@3.11/bin/python3.11 -m venv macos/.venv
macos/.venv/bin/python -m pip install -r macos/requirements-dev.txt
```

Verification entry points:

```bash
macos/.venv/bin/python -c 'import sys, platform, tkinter; print(sys.version, platform.machine(), tkinter.TkVersion)'
macos/.venv/bin/pyinstaller --version
ffmpeg -version
ffprobe -version
rubberband --version
```

Homebrew Brewfiles pin formula names/major lines, not exact bottle revisions. The exact verified revisions are recorded in this report; a future update may change them and requires re-running environment verification.

## 16. License and distribution notes

| Component | Verified license path | Distribution significance |
| -- | -- | -- |
| Python 3.11 | PSF/Python license | Preserve applicable notices when redistributing Python. [Python license](https://docs.python.org/3/license.html) |
| Tcl/Tk 8.6 | BSD-style Tcl/Tk license | Permissive, but applicable notices still need inclusion. [Tcl/Tk licensing](https://www.tcl-lang.org/about/support.html) |
| Homebrew FFmpeg 8.1.2 | Formula declares GPL-3.0-or-later; actual config enables GPL and version 3 components | This installed binary is on a GPL path, not a plain-LGPL build. Future bundling must satisfy the corresponding source, notice, and license obligations. [Homebrew formula](https://formulae.brew.sh/formula/ffmpeg), [FFmpeg legal guidance](https://ffmpeg.org/legal.html) |
| Rubber Band 4.0.0 | GPL-2.0-or-later or separate commercial license | GPL-compatible source distribution or a commercial license must be selected before distributing an application that uses it. App Store distribution is already out of scope. [Official license statement](https://github.com/breakfastquay/rubberband) |
| libsndfile 1.2.2 | LGPL-2.1-or-later | Transitive dynamic dependency of the CLI; notices, license, relinking/source obligations need review when bundling. [Homebrew formula](https://formulae.brew.sh/formula/libsndfile) |
| PyInstaller 6.21.0 | GPL-2.0 with bootloader exception; limited files under Apache-2.0 | PyInstaller permits bundling commercial applications, but output licensing remains constrained by bundled dependencies. [PyInstaller license](https://pyinstaller.org/en/stable/license.html) |

This is a factual inventory, not legal advice. The repository has no confirmed distribution-license decision in this report. FFmpeg and Rubber Band compliance must be resolved before distributing binaries.

## 17. Unresolved issues and pending decisions

- **Pending:** repository/application license and the GPL-compatible versus commercial Rubber Band distribution path.
- **Pending:** final FFmpeg/Rubber Band/lib sources, notices, and corresponding-source delivery method for a distributable package.
- **Pending:** minimum supported macOS. It must be established using the final dependency set and a package built/tested on the intended oldest system.
- **Pending:** PyInstaller collection and relocation of Homebrew Tcl/Tk, FFmpeg, Rubber Band, and transitive dylibs. Standard Tk hooks are installed, but no package was built in this task.
- **Pending:** verify a future PyInstaller output is arm64-only. The installed wheel's bootloader inputs are universal2, even though the running Python and target are arm64.
- **Pending:** exact dependency versions may advance when Homebrew resolves the Brewfile; any changed environment must repeat this report's checks.
- No blocking architecture, loader, Tkinter, codec, CLI, or smoke-test failure remains for environment setup.

## 18. Final environment status

**PASS — macOS Apple Silicon development environment established and verified.**

- Native Apple Silicon host and selected tools: PASS
- Isolated Python virtual environment: PASS
- Python/Tkinter import and real window initialization: PASS
- FFmpeg execution, MP3 encoding, and WAV/MP3/M4A/FLAC reading: PASS
- Rubber Band CLI and required parameter semantics: PASS
- Dynamic dependency resolution: PASS
- Three-stage synthetic-audio smoke test and MP3 probe: PASS
- Reproducible Homebrew and pip configuration: PASS
- Windows binary reuse: none
- Repository contamination by `.venv` or temporary audio: none

This PASS applies to the development environment and command-line toolchain only. Application implementation, packaging, minimum-OS validation, and distribution-license completion remain outside this report and are not implicitly approved.
