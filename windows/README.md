# Windows

本目录保存整理后的 Windows 历史实现，作为 AudioShifter 行为和 macOS 复刻的参考。

- `src/`：中文与英文 Tkinter 源码。
- `packaging/`：PyInstaller 打包配置。
- `docs/`：Windows 用户文档。
- `_local_artifacts/`：仅本机保留的构建产物、第三方二进制和旧激活文件；该目录不会提交到 Git。

现有源码包含历史 Windows 版本的机器码和激活逻辑，仅作为旧版实现参考原样保留；后续不对其修改、清理或重构。macOS 和 `mobile/` 下的新实现不得复用该机制。
