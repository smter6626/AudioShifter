# AudioShifter

AudioShifter 是一个完全在本机运行的音频变调与变速工具。macOS 中文 GUI
已经完成，当前候选版本为 `v0.1.0-alpha.2`；Android 仍处于后续准备阶段。

## macOS 应用

当前 macOS 应用：

- 支持 Apple Silicon `arm64`；
- 支持 MP3、M4A、WAV、FLAC 输入；
- 支持 `-24` 至 `+24` 半音变调；
- 支持相对原速度 `-95%` 至 `+400%` 变速；
- 输出 44.1 kHz、双声道、320 kbps MP3 到 Downloads；
- 同名文件不会覆盖，支持取消，且不修改源文件；
- 已内置 Python、Tcl/Tk、FFmpeg、FFprobe、Rubber Band 及运行库。

该应用仅在 Apple Silicon arm64、macOS 27.0 build 26A5378n 上验证。旧版
macOS 未测试，可能无法运行；不支持 Intel Mac、Rosetta 或 universal2。

二进制只使用 PyInstaller ad-hoc signing，没有 Developer ID、Apple
notarization 或 stapling。完整使用、构建、Gatekeeper 单应用放行和验证说明
见 [macOS README](macos/README.md)。

## 许可证与品牌

Copyright (C) 2026 Yeming Dai

除文件另有说明外，项目所有者拥有版权的 macOS、mobile、相关共享构建
配置和文档代码以 `GPL-3.0-or-later` 提供。GPL 允许依照其条款使用、修改、
再分发和商业使用代码。

以下内容不属于该 GPL 授权：

- `windows/` 下的全部历史内容；
- AudioShifter 名称、Logo、应用图标和官方品牌；
- 第三方软件、源码及许可证材料。

修改版可以使用和商业分发 GPL 代码，但必须使用自己的名称、bundle
identifier、图标和品牌，不得冒充官方 AudioShifter 版本。第三方组件继续
适用各自许可证。

- [LICENSE](LICENSE)：完整 GNU GPL version 3 正文。
- [LICENSING.md](LICENSING.md)：GPL-3.0-or-later 覆盖范围与排除范围。
- [TRADEMARKS.md](TRADEMARKS.md)：名称、图标、官方身份和避免混淆规则。
- [macOS 第三方组件说明](macos/THIRD_PARTY_NOTICES.md)：内置第三方组件、版本和许可证。

## 仓库目录

- `macos/`：已实现的 macOS 源码、测试、构建、打包和 Release 工具。
- `mobile/`：后续 Android 实现工作区。
- `windows/`：只读历史内容，不属于本项目 GPL 授权。
- `docs/`：跨平台设计合同、执行状态和历史盘点。

## 项目文档

- [macOS 使用与开发](macos/README.md)
- [macOS 复刻静态合同](docs/macos_rebuild_static.md)
- [macOS 复刻执行状态](docs/macos_rebuild_runtime.md)
- [Windows 原始目录盘点](docs/map_win_8.2.md)

本 Git 仓库不提交构建后的 `.app`、Release 压缩包或第三方二进制；候选
Release 资产由已提交的可重复构建和源码收集工具生成。
