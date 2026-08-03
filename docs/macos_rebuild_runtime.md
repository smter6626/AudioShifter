# done

- 2026-08-02：完成原始 Windows 目录的只读扫描，确认文件类型、大小、用途、重复副本、绝对路径、敏感内容迹象、链接和 Git 状态。
- 2026-08-02：初始化本地 Git 仓库，接入并跟踪 `origin/main`；远端当时仅包含静态合同。
- 2026-08-02：完整读取 `docs/macos_rebuild_static.md`，确认 macOS 优先、Android 后续以及新版本移除激活机制的长期约束。
- 2026-08-02：生成一次性仓库地图 `docs/map_win_8.2.md`。
- 2026-08-02：完成平台目录分类，建立根级 `.gitignore`；Windows 构建产物、第三方二进制和本地激活文件已保留在被忽略的 `_local_artifacts` 中。
- 2026-08-02：提交 `d440f78`（`docs: add repository map and project layout`），纳管仓库地图、入口说明、平台占位说明、忽略规则和初始执行状态。
- 2026-08-02：提交 `150394c`（`chore: organize files by platform`），纳管整理后的 Windows 源码、用户指南和路径已适配新目录的 PyInstaller 配置。
- 2026-08-02：复核所有已跟踪和已暂存路径；EXE、DLL、授权文件、旧注册机、构建目录及日志均未进入 Git，原始本地副本仍保留。
- 2026-08-02：提交 `37e826a`（`docs: clarify Windows legacy code scope`），明确 Windows 旧版源码仅作为历史参考原样保留，后续不修改、不清理、不重构；新平台不得复用旧激活机制。
- 2026-08-02：确认 macOS 目标仅为 Apple Silicon（`arm64`），不支持 Intel Mac、不制作通用二进制；产品功能不依赖特定 macOS 版本，实际兼容下限由最终选定的 Python、Tkinter、依赖与打包工具决定；Developer ID 签名和 Apple 公证不在项目范围内。
- 2026-08-02：完成开发机盘点，确认 Mac16,5、macOS 27.0、Homebrew `/opt/homebrew` 以及选定工具均原生运行于 `arm64`，Rosetta 未启用；系统 Python、uv 和 Conda 未用于项目环境。
- 2026-08-02：选定并验证 Homebrew Python 3.11.15、python-tk/Tcl/Tk 8.6.18、FFmpeg 8.1.2、Rubber Band 4.0.0，以及作为 Rubber Band CLI 传递依赖的 libsndfile 1.2.2；相关 Homebrew 公式原已安装且为当前版本，本轮未执行全局更新、升级、清理或重装。
- 2026-08-02：创建被 Git 忽略的 `macos/.venv/`，确认 Python 为原生 `arm64`；仅在该虚拟环境安装并验证 PyInstaller 6.21.0，未执行应用打包。
- 2026-08-02：完成 Tkinter 验证，确认 Tcl/Tk 实际 patchlevel 8.6.18、Aqua 窗口系统和最小窗口初始化均通过。
- 2026-08-02：完成 FFmpeg/Rubber Band 环境验证及系统临时目录冒烟测试；WAV、MP3、M4A、FLAC 均可读取，`libmp3lame` 可编码，三阶段 `FFmpeg → Rubber Band → FFmpeg` 处理成功，最终 MP3 可由 ffprobe 识别，临时音频已清理。
- 2026-08-02：创建 `macos/environment_report.md`、`macos/Brewfile` 和 `macos/requirements-dev.txt`，记录架构、版本、动态链接、许可证、验证证据和可复现步骤；提交 `9f6995f`（`chore: establish macOS development environment`）。

# active step

- 从静态合同和 Windows 历史源码提取 macOS 可测试行为基线，并据此形成正式实现前的行为规格与验证矩阵；本步骤只定义可验证合同，不编写 GUI 或正式业务实现：
  1. 核对输入格式合同，分别记录 MP3、M4A、WAV、FLAC 的接受条件、验证证据和不在首阶段承诺的格式。
  2. 明确半音参数语义，包括零值、正负方向、小数支持和待测试边界；明确速度百分比与 Rubber Band tempo/time ratio 的换算语义，不把环境冒烟参数直接当成产品默认值。
  3. 明确 MP3 输出合同，包括编码结果需要验证的媒体信息、文件名所需参数信息和输出位置的用户可理解性。
  4. 定义同名输出策略，保证不得无感知覆盖；定义每次处理的独立临时资源、成功/失败/取消后的清理要求，并排除固定下载目录临时文件。
  5. 建立面向用户和内部诊断的错误类别，覆盖输入、参数、依赖、子进程、文件权限、空间、输出冲突和清理失败等场景。
  6. 明确排除机器码、激活码、注册机、授权文件及任何访问限制；Windows 激活实现仅作为不应迁移的历史边界。
  7. 基于行为规格提出 GUI、音频处理、依赖/路径解析、参数校验和错误表示的模块边界，但暂不实现模块。
  8. 为每条合同建立验证矩阵，列出前置条件、输入、预期结果、失败表现、证据和待确认项；未经验证的选择不得写成既定事实。

# next steps

- 根据确认后的行为基线建立不依赖 GUI 的参数、命名、同名输出、临时资源和错误处理测试。
- 测试合同稳定后实现非 GUI 的 macOS 音频处理核心。
- 音频处理核心验证通过后接入中文 Tkinter GUI。
- GUI 和核心验证后执行本地未签名的 arm64 应用包验证；Developer ID 签名和 Apple 公证不在项目范围内。
- macOS 复刻完成后才开始 `mobile/` 下的 Android 移植。
