# Windows

本目录保存整理后的 Windows 历史实现，作为 AudioShifter 行为和 macOS 复刻的参考。

- `src/`：中文与英文 Tkinter 源码。
- `packaging/`：PyInstaller 打包配置。
- `docs/`：Windows 用户文档。
- `_local_artifacts/`：仅本机保留的构建产物、第三方二进制和旧激活文件；该目录不会提交到 Git。

现有源码仍包含废弃的机器码和激活逻辑。新平台不得复用该机制，后续应按静态合同移除。
