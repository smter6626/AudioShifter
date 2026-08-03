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

# active step

- 建立并验证 macOS Apple Silicon 开发环境；本步骤允许安装和配置依赖、创建虚拟环境及执行命令行级环境冒烟测试，但不编写应用 GUI、不实现正式业务模块、不执行 PyInstaller 打包：
  1. 进入本地仓库 `/Users/smterpro/Workspace/Tools/AudioShifter/`，先执行 `git status` 确认没有待提交改动，再执行 `git pull --ff-only` 获取远端最新文档。若工作区不干净、无法快进或出现冲突，停止并向用户报告，不得 reset、stash 或覆盖本地修改。
  2. 记录开发机环境，包括 `uname -m`、`sw_vers`、Shell、Homebrew 路径与架构、可用 Python 版本及其来源。目标必须是原生 `arm64`；发现关键工具通过 Rosetta 或为 `x86_64` 时，先查明原因，不得将其作为合格环境。
  3. 根据静态合同和 Windows 历史实现，核实 macOS 环境实际需要的组件。至少审查 Python、Tkinter、FFmpeg、Rubber Band、libsndfile 和后续使用的 PyInstaller；不得预设 libsndfile 一定是项目直接依赖，应区分直接依赖、Rubber Band/包管理器传递依赖和仅用于构建的开发依赖。
  4. 对每个组件查询可信的一手来源和当前可用版本，检查 Apple Silicon 支持、相互兼容性、安装来源、动态链接关系、许可证以及对最终分发的影响。版本选择以兼容、可重复和后续可打包为优先，不要求无条件追逐最新版本；不得复用 `windows/_local_artifacts/` 中的任何 Windows 二进制。
  5. 在 `macos/.venv/` 创建独立 Python 虚拟环境，并确认该目录已被 `.gitignore` 排除。只在虚拟环境中安装 Python 项目/开发依赖。原生工具和库优先使用已存在的原生 Homebrew；可以安装本项目必要的公式，例如 FFmpeg、Rubber Band 和经核实需要的 libsndfile，但不得升级或清理无关软件。若 Homebrew 不存在、安装要求管理员权限、将造成大范围升级，或依赖选择存在重大分歧，停止并向用户提问。
  6. 安装后逐项验证实际命令路径、版本与架构。至少检查 Python 与 Tkinter 可导入、FFmpeg 可读取常见输入且具备 MP3 编码能力、Rubber Band 命令可运行、相关动态库可解析；使用 `which`、`file`、版本命令和必要时的 `otool -L` 记录证据。不得仅凭安装命令成功就判定环境可用。
  7. 在系统临时目录中生成短小的合成测试音频，完成一次“FFmpeg 解码/标准化 → Rubber Band 变调与变速 → FFmpeg 输出 MP3”的命令行冒烟测试，检查退出状态、输出文件存在性和基础媒体信息。测试文件不得提交仓库，结束后清理；本步骤只验证工具链，不据此确定正式代码结构或用户可见行为合同。
  8. 创建 `macos/environment_report.md`。报告至少包含：目标架构与分发边界；开发机环境；项目所需组件及依赖分类；选择的版本与选择理由；来源和安装方式；实际安装版本、路径和架构；虚拟环境位置与 Python 包；动态链接/传递依赖；许可证与分发注意事项；完整验证结果；冒烟测试步骤和结果；可复现安装命令；未解决问题及明确的待确认项。不得把推测写成已验证事实。
  9. 完成报告后复核仓库，只提交文档、必要的可复现环境配置和 `.gitignore` 调整；不得提交 `.venv`、Homebrew 文件、下载缓存、测试音频、生成音频或第三方预编译二进制。提交后将结果和短 commit hash 追加到本文件的 `done`，再把下一阶段移为新的 `active step`。

# next steps

- 环境验证完全通过后，从静态合同和 Windows 历史源码提取可测试的行为基线：输入格式、半音/速度语义、MP3 输出、文件命名、同名处理、临时资源和错误类别；明确排除机器码、激活码、授权文件及固定下载目录临时文件。
- 基于行为基线提出 GUI、音频处理、依赖/路径解析、参数校验和错误表示的 macOS 模块边界，以及对应的验证矩阵；待确认内容不得猜测。
- 根据确认后的行为基线建立不依赖 GUI 的参数、命名、临时文件和错误处理测试，并实现 macOS 音频处理核心。
- 音频处理核心验证通过后接入中文 Tkinter GUI，再验证未签名的本地应用包；Developer ID 签名和 Apple 公证不在项目范围内。
- macOS 复刻完成后才开始 `mobile/` 下的 Android 移植。
