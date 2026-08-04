# AudioShifter v0.1.0-alpha.3 — macOS arm64 preview

AudioShifter 的第三个 Apple Silicon macOS 预览候选版。本版本修正 macOS
bundle 版本字段，并在原生应用菜单中加入完整许可证查看器。

## Changes in alpha.3

- Corrected macOS bundle version metadata.
- Added a native License item to the AudioShifter application menu.
- Added an English, scrollable full GPLv3 licence viewer.
- Clarified that ordinary users do not need to download the corresponding-source archive.
- Clarified permission to reproduce unmodified official builds while requiring forks to use their own branding.

## 功能 / Features

- 完全本地的音频变调与变速，中文 GUI。
- 支持 MP3、M4A、WAV、FLAC 输入。
- 输出固定为 MP3、44.1 kHz、双声道、320 kbps。
- 变调范围：`-24` 至 `+24` 个半音。
- 变速范围：相对原速度 `-95%` 至 `+400%`。
- 同名文件永不覆盖，支持取消且不会修改源文件。

## License menu

To view the complete licence in the application:

```text
AudioShifter menu → License
```

The licence viewer contains the complete English GNU GPL version 3 text. It
loads the bundled `LICENSE` resource locally, is scrollable and read-only, and
does not require a network connection.

## 系统要求 / System requirements

- Apple Silicon `arm64` only.
- 仅在 macOS 27.0 build `26A5378n` 上验证。
- 旧版 macOS 未测试，可能无法运行。
- 不支持 Intel Mac、Rosetta 或 `universal2`。

应用已内置 Python、Tcl/Tk、FFmpeg、FFprobe、Rubber Band 和实际运行所需
的动态库。运行时无需安装 Python、Homebrew 或这些音频工具。

## 重要：Gatekeeper / Important Gatekeeper notice

**此版本仅使用 PyInstaller ad-hoc signing，未使用 Apple Developer ID，
未经 Apple 公证，也没有 stapling。**

首次打开时 macOS 可能显示：

> Apple 无法验证 AudioShifter.app 是否包含恶意软件。

请先尝试打开一次，然后进入：

```text
系统设置 → 隐私与安全性 → 仍要打开
```

只应对从本仓库 Release 下载且 SHA-256 匹配的文件执行该单应用放行。
不要全局关闭 Gatekeeper。

## Downloads

普通用户只需下载：

```text
AudioShifter-v0.1.0-alpha.3-macOS27-arm64.zip
SHA256SUMS.txt
```

只校验 App ZIP：

```bash
grep 'AudioShifter-v0.1.0-alpha.3-macOS27-arm64.zip' SHA256SUMS.txt \
  | tr -d '\r' \
  | shasum -a 256 -c -
```

`tr -d '\r'` 兼容可能带有 CRLF 行尾的 `SHA256SUMS.txt`。

需要审计、修改或重建的人再下载：

```text
AudioShifter-v0.1.0-alpha.3-corresponding-source.tar.gz
```

The corresponding-source archive is provided for licence compliance,
inspection, modification, and rebuilding. It is not required to run the app.

若 App 和对应源码两个归档都已下载，可以运行：

```bash
shasum -a 256 -c SHA256SUMS.txt
```

两个归档均应显示 `OK`。

## License and branding

AudioShifter-owned code covered by this release is licensed under
`GPL-3.0-or-later`, subject to `LICENSING.md`. The complete GPLv3 text is in
`LICENSE`; third-party components retain their respective licences.

The AudioShifter name, logo, icon, and official branding are not licensed under the GPL.
They may be copied only as necessary to reproduce or redistribute an
unmodified official release built from an official AudioShifter tag. Modified
versions must use a different name and icon, bundle identifier, and branding
unless prior written permission is obtained. GPL commercial use and distribution
under another brand remain permitted.

## Source

AudioShifter 自身源码固定在 `v0.1.0-alpha.3` Git tag。该二进制所内置
第三方组件的准确对应源码、构建材料、Homebrew formula/receipt、适用补丁
和许可证位于对应源码附件中。GitHub 自动生成的 tag 源码归档不能替代内置
第三方组件的对应源码附件。

## 已知限制 / Known limitations

- 未使用 Developer ID 正式签名，未经公证，首次启动需要人工单应用放行。
- 旧版 macOS 未测试，可能无法运行。
- 仅支持单文件、单任务处理；无批处理或队列。
- 输出目录固定为当前用户的 Downloads。
- 输出固定为 MP3，不保留源音频元数据。
