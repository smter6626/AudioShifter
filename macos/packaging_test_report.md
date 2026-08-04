# AudioShifter macOS standalone packaging test report

## Final status

**PASS** — `AudioShifter.app` was reproducibly built and exercised as a
windowed, ad-hoc-signed, non-notarized, arm64-only application. It launches
from Finder and runs the real audio pipeline without an activated virtual
environment, a Homebrew `PATH`, repository source, or external FFmpeg,
FFprobe, or Rubber Band installations.

This result is deliberately limited to Apple Silicon `arm64` on macOS 27.
Older macOS releases are untested and may not run the application. Intel,
Rosetta, and `universal2` are not supported or claimed.

## Build identity

- Date: 2026-08-04 (America/Phoenix)
- Host: MacBook Pro `Mac16,5`, Apple M4 Max, native `arm64`
- OS: macOS 27.0, build `26A5378n`
- Python: CPython 3.11.15, native arm64
- Tk: 8.6.18, Aqua
- PyInstaller: 6.21.0
- FFmpeg / FFprobe: 8.1.2 (`ffmpeg` bottle revision `8.1.2_1`)
- Rubber Band: 4.0.0
- Spec: `macos/packaging/AudioShifter.spec`
- Build command: `macos/packaging/build_app.sh`
- Application: `macos/dist/AudioShifter.app`
- Exact bundle size: 63,356,035 bytes (about 61 MiB; Finder rounds to 63.4 MB)
- Bundle identifier: `io.github.smter6626.audioshifter`
- Version: `0.1.0` (`CFBundleVersion=1`)

The build uses PyInstaller's `onedir + windowed` bundle structure with
`console=False` and `target_arch="arm64"`. It does not set a speculative
`LSMinimumSystemVersion`.

## Icon and application metadata

The user-provided source
`/Users/smterpro/Downloads/audioshifter_icon.png` was copied without redesign
to `macos/assets/source/audioshifter_icon.png`. It is a readable 1254 × 1254
square RGB PNG. `macos/packaging/build_icon.sh` produces the standard iconset
sizes and `macos/assets/AudioShifter.icns`; `iconutil` reports a valid
1,984,290-byte macOS icon. The spec installs that file as:

```text
AudioShifter.app/Contents/Resources/AudioShifter.icns
```

`Info.plist` contains:

```text
CFBundleDisplayName = AudioShifter
CFBundleExecutable = AudioShifter
CFBundleIdentifier = io.github.smter6626.audioshifter
CFBundleShortVersionString = 0.1.0
CFBundleVersion = 1
CFBundleIconFile = AudioShifter.icns
CFBundlePackageType = APPL
CFBundleDevelopmentRegion = zh_CN
LSApplicationCategoryType = public.app-category.music
NSHighResolutionCapable = true
```

Computer Use confirmed that Finder displays the supplied blue/purple music
icon rather than PyInstaller's default, and that the running app and its alert
dialogs use the application identity.

## Bundle structure and embedded runtime

The required application directories exist:

```text
Contents/Info.plist
Contents/MacOS/AudioShifter
Contents/Frameworks/
Contents/Resources/
Contents/_CodeSignature/
```

The bundle includes the CPython runtime and standard library, Tcl/Tk libraries
and scripts, `_tkinter`, PyInstaller's arm64 windowed bootloader, and these
application-owned tools:

```text
Contents/Frameworks/bin/ffmpeg
Contents/Frameworks/bin/ffprobe
Contents/Frameworks/bin/rubberband
```

The recursive build-time `otool -L` inventory found 27 external CLI roots and
dependencies: the three tools plus 24 dylibs. Major embedded libraries include
FFmpeg's `libav*`, `libsw*`, Rubber Band's libsndfile/libsamplerate chain,
libmp3lame, libFLAC, libogg/libvorbis, mpg123, Opus, libvmaf, libvpx, dav1d,
SVT-AV1, x264, x265, OpenSSL, Tcl/Tk, CPython's `libmpdec`, and `liblzma`.
The generated evidence is `macos/build/external_dependencies.json`.

## Static Mach-O, linkage, and symlink audit

Command:

```bash
macos/packaging/verify_app.sh
```

The verifier recursively runs `file`, `lipo -archs`, `otool -L`, and
`otool -l`, resolves `@loader_path`, `@executable_path`, and `@rpath`, and
checks all bundle symlinks. Final statistics from
`macos/build/app_verification.json`:

```text
Mach-O files:                         75
Architecture:                        arm64-only
Dynamic load references:             324
LC_RPATH commands:                   20
External non-system load commands:   0
Forbidden development load commands: 0
Symlinks:                            44
Broken/external symlinks:             0
```

Every executable, dylib, Python extension, and framework binary is thin
arm64. There is no x86_64-only dependency and no Rosetta requirement. All
non-system load commands resolve within the app; Apple-provided references are
under `/System/Library` or `/usr/lib`. No load command or LC_RPATH points at
`/opt/homebrew`, `macos/.venv`, or the repository. This audit distinguishes
Mach-O load commands from harmless build strings.

`ditto` copy testing retained all symlinks, and `find -L` found no broken link
in the copied bundle.

## Signing and Gatekeeper

No Developer ID identity was supplied. PyInstaller performed the ad-hoc
signing required for the arm64 bundle. Evidence:

```bash
codesign --verify --deep --strict --verbose=4 macos/dist/AudioShifter.app
codesign -dvvv macos/dist/AudioShifter.app
```

Result:

```text
valid on disk
satisfies its Designated Requirement
Format=app bundle with Mach-O thin (arm64)
Signature=adhoc
TeamIdentifier=not set
```

As expected for an app with neither Developer ID signing nor notarization,
`spctl -a -vv -t execute` returned 3 and `rejected`. No certificate was
created, no Keychain or security setting was changed, and no notarization or
stapling was attempted.

## Standalone launch evidence

Three independent launches used the final app executable and verified the
process remained alive long enough to create the Tk window:

1. With `VIRTUAL_ENV` unset: PID 54537 launched successfully.
2. With `PATH=/usr/bin:/bin:/usr/sbin:/sbin` and cwd `/private/tmp`: PID 54547
   launched successfully; `lsof` found no opened `/opt/homebrew`, `.venv`, or
   repository source path.
3. After `ditto` copied the bundle to
   `/private/tmp/AudioShifter-standalone.DyVr7p/AudioShifter.app`: PID 54569
   launched successfully with the same restricted PATH; `lsof` found no
   Homebrew, virtual-environment, or repository access. The known copy was
   removed after the check.

All three test processes were terminated and reaped. A final process query
found no `AudioShifter`, `ffmpeg`, `ffprobe`, or `rubberband` process.

Computer Use then independently operated Finder's exposed “打开” action on
the final `macos/dist/AudioShifter.app`. The Chinese GUI appeared without a
Terminal window. This proves the Finder entry path in addition to direct
executable launch.

## Automated tests

Pre-build and final regression command:

```bash
macos/.venv/bin/python -m pytest
```

Result: **137 passed, 0 failed, 0 skipped** in 6.90 seconds. Collection is 109
unit/failure-injection/packaging-source tests and 28 integration tests. Seven
tests were added above the prior 130-test MVP baseline, covering frozen-state
resource-root selection, resolver factory switching, stable missing packaged
tool errors, packaging source/layout requirements, and icon/focus integration.
No prior test was deleted or skipped.

The build-artifact audit and packaged-pipeline checks are intentionally kept
as executable packaging scripts rather than skipped ordinary pytest cases:

```bash
macos/packaging/verify_app.sh
macos/packaging/verify_packaged_pipeline.sh
```

Both completed successfully on the final bundle.

## Four-format packaged pipeline

`verify_packaged_pipeline.sh` ran with a restricted system-only PATH and
resolved every command from `AudioShifter.app/Contents/Frameworks/bin`.
Inputs were generated under a system temporary directory and removed after
the run.

| Input | Path coverage | Result | Output stream |
|---|---|---|---|
| WAV | Chinese, spaces, parentheses, `&`, uppercase extension | PASS | MP3, 44100 Hz, 2 channels, 320000 bit/s |
| MP3 | multiple-dot stem, uppercase extension | PASS | MP3, 44100 Hz, 2 channels, 320000 bit/s |
| M4A | apostrophe path, uppercase extension | PASS | MP3, 44100 Hz, 2 channels, 320000 bit/s |
| FLAC | space path, uppercase extension | PASS | MP3, 44100 Hz, 2 channels, 320000 bit/s |

All four used pitch `+3` and speed `-20`, and each source SHA-256 was identical
before and after. Representative WAV output:

```text
codec_name=mp3
sample_rate=44100
channels=2
bit_rate=320000
duration=2.500000
size=102444
```

The executable evidence contains only these absolute command paths:

```text
.../AudioShifter.app/Contents/Frameworks/bin/ffmpeg
.../AudioShifter.app/Contents/Frameworks/bin/rubberband
.../AudioShifter.app/Contents/Frameworks/bin/ffprobe
```

## Final Computer Use GUI test

Computer Use tested the final rebuilt `.app`, not `python -m audioshifter`:

- Finder showed the custom icon and opened the app; Chinese labels and layout
  rendered correctly and no Terminal window appeared.
- The macOS file chooser opened and selected the synthetic WAV.
- Pitch `+3` and speed `-20` were submitted. While status read
  `正在变调和变速…`, the UI could still be inspected, Start was disabled and
  Cancel was enabled.
- Success reported
  `~/Downloads/UI 打包自检 & nlMA2F+3-20%.mp3`.
- The final output SHA-256 was
  `9032b26cae5e9235d6491df5f98722575b3be0d30ca973b016381db194d25e3e0`;
  FFprobe reported MP3, 44100 Hz, 2 channels, 320000 bit/s, duration 6.25 s.
- A second identical run displayed the explicit “已有文件不会被覆盖” prompt
  and produced `_2`. The original and `_2` hashes were identical, while the
  original file's hash remained unchanged.
- The short source hash remained
  `b82c9e0369fcbe1906e47d83449da7fffd2cdbeed6f8f227e6ccc4e4875d2684`.

During the long-input run, process evidence captured:

```text
/Users/smterpro/Workspace/Tools/AudioShifter/macos/dist/AudioShifter.app/
Contents/Frameworks/bin/rubberband --pitch 0 --tempo 0.05 --fine --formant ...
```

The observed child PID 54716 belonged to the app PID 54652, proving the GUI
used the embedded tool. Cancel displayed `处理已取消，未保留残缺输出。`; the
target output was absent, the exact task workspace was removed, all child
processes were reaped, and the long source hash remained
`b64f7a4c8f8e31bc45fd63fc2396356f58f7b0a670a38eee6cdcba000388d51e`.
The GUI returned to a reusable state.

For running-window close behavior, selecting No kept packaged Rubber Band PID
54744 running. Closing again and selecting Yes cancelled the task, removed its
workspace, left no partial output or packaged child process, and exited the
app. The final count of `AudioShifter-*` task workspaces was zero.

Only the two explicitly named synthetic inputs and the two successful
Downloads outputs were deleted after evidence collection. The cancelled
output never existed. No user or unknown file was removed.

## Conflict, source protection, cancellation, and cleanup

The automated packaged-pipeline run independently allocated `_2` and `_3`,
preserved the earlier output hash, and used an exclusive publish path. Its
real packaged Rubber Band cancellation observed and reaped PID 54097, produced
zero partial outputs, leaked zero workspaces, and preserved the source hash.
The verification root itself was removed. These programmatic results agree
with the Computer Use evidence above.

## Third-party notices and distribution boundary

`macos/THIRD_PARTY_NOTICES.md` records the exact embedded versions, upstream
projects, installed Homebrew/PyPI sources, packaged files, relationships, and
source-acquisition routes. Matching texts are under `macos/licenses/` and are
embedded in the app. The inventory includes FFmpeg, Rubber Band, CPython,
Tcl/Tk, PyInstaller, libsndfile/libsamplerate, actual codec libraries,
OpenSSL, mpdecimal, and XZ/liblzma.

This local personal-use build is not distributed. A future public binary or
GitHub Release must first settle a GPL-compatible application/distribution
route and provide the required notices and corresponding source for the
applicable FFmpeg, Rubber Band, x264/x265, and other components. No commercial
Rubber Band licence is claimed or purchased.

## Known limitations and untested scope

- Only Apple Silicon arm64 on macOS 27.0 build `26A5378n` was tested.
- Older macOS versions are untested and may fail; no minimum older version is
  promised.
- Intel Mac, Rosetta, and `universal2` are not supported.
- The app is ad-hoc signed only and not notarized, so Gatekeeper assessment is
  expected to reject it outside the local build context.
- No `.dmg`, Developer ID signature, notarization, stapling, App Store sandbox,
  GitHub Release, or public binary distribution was performed.
- Functional limitations remain those in `macos/README.md`: one task at a
  time, fixed Downloads destination and MP3 output, no batch queue, and no
  metadata preservation.
