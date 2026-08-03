# AudioShifter

AudioShifter 是一个面向非技术用户的本地音频变调与变速工具。现有 Windows 版本使用 Python、Tkinter、FFmpeg 和 Rubber Band；项目当前优先复刻 macOS 版本，完成后再开始 Android 移植。

## 目录

- `windows/`：整理后的 Windows 历史源码、打包配置和用户文档。
- `macos/`：macOS 复刻工作区，当前尚未开始实现。
- `mobile/`：后续 Android 移植工作区。
- `docs/`：跨平台设计合同、执行状态和仓库盘点。

## 项目文档

- [macOS 复刻静态合同](docs/macos_rebuild_static.md)
- [macOS 复刻执行状态](docs/macos_rebuild_runtime.md)
- [Windows 原始目录盘点](docs/map_win_8.2.md)

本仓库不包含预编译的第三方可执行文件或动态库。依赖的实际版本、来源和许可证需要在 macOS 实现前确认。
