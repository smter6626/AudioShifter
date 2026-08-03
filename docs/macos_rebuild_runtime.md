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

# active step

- 开展 macOS 复刻的实现前准备，不安装依赖、不编写 GUI、不执行打包：
  1. 确认实际目标 Mac 的架构、最低 macOS 版本和分发对象，并记录是否需要 Intel 支持、通用二进制、Developer ID 签名及公证；未确认项不得写成承诺。
  2. 分别核实 FFmpeg、Rubber Band、libsndfile 的 macOS 来源、版本、构建方式、构建选项、相互依赖和许可证义务；不得直接复用本地 Windows 二进制。
  3. 从静态合同和 Windows 历史源码提取可测试的行为基线：输入格式、半音/速度语义、MP3 输出、文件命名、同名处理、临时资源和错误类别；明确排除机器码、激活码、授权文件及固定下载目录临时文件。
  4. 在以上信息确认后，提出 GUI、音频处理、依赖/路径解析、参数校验和错误表示的 macOS 模块边界，以及对应的验证矩阵；所有待定内容明确标注“待确认”。

# next steps

- 根据已确认的行为基线建立不依赖 GUI 的参数、命名、临时文件和错误处理测试。
- 实现并验证 macOS 音频处理核心后，再接入中文 Tkinter GUI。
- 在目标设备上验证应用包与内置依赖，再决定签名、公证和分发形式。
- macOS 复刻完成后才开始 `mobile/` 下的 Android 移植。
