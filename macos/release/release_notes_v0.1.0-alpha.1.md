# AudioShifter v0.1.0-alpha.1 — macOS arm64 preview

首个 AudioShifter macOS Apple Silicon 公开预览候选版。This is the first
AudioShifter preview candidate for Apple Silicon macOS.

## 功能 / Features

- 完全本地的音频变调与变速，中文 GUI。
- 支持 MP3、M4A、WAV、FLAC 输入。
- 输出固定为 MP3、44.1 kHz、双声道、320 kbps。
- 变调范围：`-24` 至 `+24` 个半音。
- 变速范围：相对原速度 `-95%` 至 `+400%`。
- 同名文件永不覆盖，自动使用 `_2`、`_3` 等名称。
- 单任务后台处理，支持取消且不会修改源文件。

## 系统要求 / System requirements

- Apple Silicon `arm64` only.
- 仅在 macOS 27.0 build `26A5378n` 上验证。
- 旧版 macOS 未测试，可能无法运行。
- 不支持 Intel Mac、Rosetta 或 `universal2`。

应用已内置 Python、Tcl/Tk、FFmpeg、FFprobe、Rubber Band 和实际运行所需
的动态库。运行时无需安装 Python、Homebrew、FFmpeg 或 Rubber Band。

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

## 下载与校验 / Downloads and verification

下载以下三个正式附件：

```text
AudioShifter-v0.1.0-alpha.1-macOS27-arm64.zip
AudioShifter-v0.1.0-alpha.1-corresponding-source.tar.gz
SHA256SUMS.txt
```

在下载目录运行：

```bash
shasum -a 256 -c SHA256SUMS.txt
```

只有两个归档都显示 `OK` 时才继续解压和运行。

## 源码与许可证 / Source and licences

AudioShifter 自身源码固定在 `v0.1.0-alpha.1` Git tag。该二进制所内置
第三方组件的对应源码、构建材料、Homebrew formula/receipt、适用补丁和
许可证位于：

```text
AudioShifter-v0.1.0-alpha.1-corresponding-source.tar.gz
```

GitHub 自动生成的 repository source archives 也必须指向同一个 tag，
但不能替代上述对应源码附件。

## 已知限制 / Known limitations

- 未使用 Developer ID 正式签名，未经公证，首次启动需要人工单应用放行。
- 旧版 macOS 未测试，可能无法运行。
- 仅支持单文件、单任务处理；无批处理或队列。
- 输出目录固定为当前用户的 Downloads。
- 输出固定为 MP3，不保留源音频元数据。
