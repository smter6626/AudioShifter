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
- 2026-08-03：完成 macOS 用户可见合同确认：输出固定到 `~/Downloads/`；变调为 `-24` 至 `+24` 的整数半音；变速改为 `-95` 至 `+400` 的相对变化百分比，底层换算为 `1 + speed_change / 100`；输出固定为 320 kbps、44.1 kHz、双声道 MP3。
- 2026-08-03：确认固定双参数命名 `<stem><signed_pitch><signed_speed>%.mp3`，零值不省略；同名文件永不覆盖，弹窗提示后采用 `_2`、`_3` 等自动递增名称；不复制音频元数据。
- 2026-08-03：确认单应用禁止并发任务，处理期间支持取消；任务运行时关闭窗口需要确认，确认退出后终止子进程、清理临时资源并退出；Downloads 不存在、不可写或磁盘空间不足时弹窗并终止，不自动切换目录。
- 2026-08-03：提交 `d5de8ae`（`docs: add macOS behavior specification`），创建中文行为规格 `macos/design/behavior_spec.md`，以合同编号固化输入、参数、管线、输出、命名、临时资源、任务和错误规则。
- 2026-08-03：提交 `c3746ba`（`docs: add macOS architecture plan`），创建中文架构规划 `macos/design/architecture_plan.md`，确定 GUI、控制层、管线、适配器、进程执行、依赖解析、命名、校验和工作区的职责边界。
- 2026-08-03：提交 `d95593c`（`docs: add macOS verification matrix`），创建中文验证矩阵 `macos/design/verification_matrix.md`，将行为合同映射为单元、集成、GUI、故障注入和打包前检查项。
- 2026-08-03：提交 `0bf56f4`（`docs: align static contract with confirmed macOS behavior`），同步更新长期静态合同，替换旧速度语义并加入已确认的平台、参数范围、下载目录、命名、输出、单任务、取消、关闭和元数据边界。
- 2026-08-03：提交 `7cc361e`（`docs: link macOS design contracts`），更新 `macos/README.md`，建立环境报告和三份设计合同的入口索引。

# active step

- 根据已确认的行为规格建立非 GUI 单元测试框架和最小核心代码骨架；本步骤只实现不依赖 Tkinter、FFmpeg 或 Rubber Band 的纯逻辑模块，不执行真实音频处理，不编写 GUI，不运行 PyInstaller：
  1. 进入本地仓库 `/Users/smterpro/Workspace/Tools/AudioShifter/`，确认工作区干净并执行 `git pull --ff-only`。完整阅读 `docs/macos_rebuild_static.md`、`macos/design/behavior_spec.md`、`macos/design/architecture_plan.md`、`macos/design/verification_matrix.md` 和 `macos/environment_report.md`；如本地存在未提交修改、无法快进或文档之间出现冲突，停止并报告，不得 reset、stash 或覆盖。
  2. 在现有 `macos/.venv/` 中增加并固定最小测试依赖，优先使用 `pytest`；更新 `macos/requirements-dev.txt`，不得升级或重装无关 Homebrew 公式，不得改变已验证的 Python、Tkinter、FFmpeg 或 Rubber Band 环境。
  3. 建立最小 Python 包和测试目录，建议创建 `macos/src/audioshifter/`、`macos/tests/unit/` 以及必要的包初始化文件；配置导入路径应可重复，避免依赖开发者当前工作目录或手工修改 `PYTHONPATH`。
  4. 实现 `models.py` 和 `errors.py`：定义不可变的 `ProcessingRequest`、稳定处理阶段、输出分配结果、结构化 `AppError` 及 `behavior_spec.md` 中的错误码。此步骤不实现外部程序适配器，也不添加 Tkinter 类型。
  5. 实现 `validation.py` 的纯函数：输入扩展名和基础文件状态校验、变调文本解析、变速文本解析、范围检查、Decimal 规范化、`tempo_ratio = 1 + speed_change / 100` 换算、Downloads 基础预检。所有无效输入必须映射到稳定错误码，并在启动任何外部进程前失败。
  6. 实现 `naming.py` 的纯函数和文件系统分配逻辑：生成 `<stem><signed_pitch><signed_speed>%.mp3`，零值固定保留；规范化小数尾随零；在目标存在时从 `_2` 开始递增；永不覆盖或删除已有文件；返回是否需要冲突提示及实际路径。通过临时目录测试竞态前的基本分配行为，不接入 GUI 弹窗。
  7. 实现 `workspace.py` 的最小安全工作区抽象：只能在传入或系统临时根目录下创建唯一任务目录，暴露预定中间路径并安全清理；拒绝清理临时根之外或非当前对象创建的路径。当前步骤不运行 FFmpeg，不生成真实音频。
  8. 实现最小单任务状态保护，可放在独立纯逻辑对象或控制层骨架中：活动任务存在时拒绝第二次启动，结束、失败或取消状态后可以释放。不得在本步骤实现后台线程或 Tkinter 控件更新。
  9. 按 `verification_matrix.md` 的 ID 编写自动化单元测试，至少覆盖 `PITCH-T001` 至 `PITCH-T013`、`SPEED-T001` 至 `SPEED-T014`、`NAME-T001` 至 `NAME-T012`、`IN-T005` 至 `IN-T010`、`TEMP-T001`、`TEMP-T009`、`TASK-T002` 和 `ERR-T001`。测试名称或参数 ID 应保留矩阵编号，保证合同可追踪。
  10. 运行完整单元测试并生成简短结果报告，记录 Python/pytest 版本、测试数量、通过/失败/跳过数和尚未实现的矩阵范围。不得为了让测试通过而修改已确认合同；发现合同内部矛盾或无法实现的文件系统语义时停止并向用户说明。
  11. 复核 Git 范围，只提交 Python 源码、测试、最小测试配置、依赖清单和必要文档；不得提交 `.venv`、缓存、覆盖率临时文件、音频、第三方二进制、`.app`、`.dmg` 或 Windows 文件变更。提交后把结果和短 commit hash 追加到本文件的 `done`，再把真实 FFmpeg/Rubber Band 核心管线实现移为下一 active step。

# next steps

- 在纯逻辑测试通过后，实现 `process_runner.py`、`dependencies.py`、`ffmpeg_adapter.py`、`rubberband_adapter.py` 和非 GUI `pipeline.py`，建立真实四格式输入、三阶段处理、取消和清理的集成测试。
- 非 GUI 核心管线全部 P0 测试通过后，接入中文 Tkinter GUI、主线程事件调度、冲突提示、取消按钮和关闭确认。
- GUI 和核心验证后执行本地未签名的纯 `arm64` 应用包验证，并解决内置依赖、动态库路径和最低 macOS 版本测试。
- 正式分发前确定 GPL 兼容或商业许可路线、第三方 notices 和对应源码提供方式。
- macOS 复刻完成后才开始 `mobile/` 下的 Android 移植。
