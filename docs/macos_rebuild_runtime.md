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
- 2026-08-03：完成 macOS 可运行 MVP 的纯逻辑层，建立正式 `audioshifter` Python 包、不可变请求/结果模型、稳定错误码、参数与路径校验、Decimal 速度换算、固定命名、同名递增、安全临时工作区和控制层单任务保护；提交 `e7312eb`（`test: add macOS core contract tests`）。
- 2026-08-03：完成开发/打包双策略依赖解析接口、参数数组进程执行器、非 UTF-8 诊断、进程组温和/强制取消，以及 FFmpeg 解码标准化、Rubber Band R3/finer/formant 处理、FFmpeg 320 kbps MP3 编码、FFprobe 验证和排他发布管线；提交 `85068d6`（`feat: implement macOS audio processing pipeline`）。
- 2026-08-03：完成中文 Tkinter GUI、系统文件选择器、参数说明、阶段状态、成功/失败/冲突提示、后台线程与主线程事件队列、取消、重复启动保护和运行中关闭确认；固定源码启动入口为 `python -m audioshifter`；提交 `5e050eb`（`feat: add macOS Tkinter MVP`）。
- 2026-08-03：完成 130 项自动化测试，其中单元/文件系统/控制层故障注入 102 项、真实管线/窗口集成 28 项，结果为 130 passed、0 failed、0 skipped；MP3、M4A、WAV、FLAC、大写扩展名、特殊字符路径、参数边界、媒体规格、时长/音高方向、源哈希、不覆盖、依赖/子进程故障、磁盘/权限注入、取消和临时清理均通过。
- 2026-08-03：使用已安装的 computer-use 能力完成真实 UI 自检：中文窗口和系统文件选择器正常；`+3/-20` 完整处理与 Downloads FFprobe 验证通过；同参数第二次运行提示并生成 `_2`，第一份与源文件未被修改；无输入、变调小数/越界、变速含 `%`/越界、重复启动、可靠取消、运行中关闭选择继续及确认取消退出均通过。测试音频和 Downloads 输出均在取证后按明确完整路径删除。
- 2026-08-03：更新 `macos/README.md` 并创建 `macos/mvp_test_report.md`，记录环境恢复、固定启动/测试入口、版本、覆盖矩阵、代表性 FFprobe、UI 证据、限制和最终 `PASS`；提交 `9c29670`（`test: verify macOS MVP end to end`）。
- 2026-08-03：确认本阶段未执行 PyInstaller，未生成 `.app` 或 `.dmg`，未修改或执行 Windows 历史内容，未提交虚拟环境、测试音频、Downloads 输出或第三方二进制。
- 2026-08-03：完成用户人工验收：使用实际 MP3 以及由该文件转换得到的 M4A、48 kHz 单声道 WAV 和 FLAC，四种格式的变调变速均成功，输出可正常播放且主观听感正常；完整测试再次确认为 `130 passed`。
- 2026-08-03：人工确认同名输出提示与 `_2` 自动递增正确，既有文件未被覆盖；输入源文件未被修改；取消后没有残缺输出；GUI 未发现肉眼可见缺陷；任务运行中关闭窗口会正确提示，选择 Yes 后先取消任务、完成清理再退出。
- 2026-08-03：取消完成后人工执行 `pgrep -fl 'ffmpeg|ffprobe|rubberband'`，结果无输出，确认未发现遗留 FFmpeg、FFprobe 或 Rubber Band 进程。结合自动化、computer-use 与用户人工验证，macOS 源码可运行 MVP 验收状态确认为 `PASS`，可以进入 PyInstaller 打包验证阶段。
- 2026-08-04：完成 PyInstaller 独立应用阶段的 Git 与基线门槛；开始时 `main` 干净并跟踪 `origin/main`、差异为 `0 0`，构建前源码基线为 `130 passed`。完整复读静态/运行时合同、设计、验证矩阵、环境、MVP 报告、README、依赖配置和 macOS 源码/测试后未发现合同矛盾；Windows 历史目录始终未修改或执行。
- 2026-08-04：将用户提供的 1254 × 1254 正方形 PNG 原样纳入 `macos/assets/source/audioshifter_icon.png`，通过标准 iconset 生成有效的 `macos/assets/AudioShifter.icns`，并由正式 spec 写入最终应用；Finder 和运行中应用均显示自定义图标而非 PyInstaller 默认图标。
- 2026-08-04：实现冻结运行时资源根和 resolver 工厂，源码态继续使用开发依赖解析，PyInstaller 态只从 `sys._MEIPASS/bin` 解析 FFmpeg、FFprobe 和 Rubber Band；缺失内部工具仍映射为稳定依赖错误。建立 `macos/packaging/AudioShifter.spec`、`build_app.sh`、入口和递归 Mach-O 依赖盘点脚本，一条命令可重复生成 windowed/onedir、纯 arm64 的 `macos/dist/AudioShifter.app`，bundle identifier 固定为 `io.github.smter6626.audioshifter`。
- 2026-08-04：最终应用大小为 63,356,035 字节，内置 CPython 3.11.15、Tcl/Tk 8.6.18、FFmpeg/FFprobe 8.1.2、Rubber Band 4.0.0 及实际传递动态库。递归审计 75 个 Mach-O，全部为 thin arm64；324 条动态引用和 20 个 LC_RPATH 均可解析，外部非系统 load command 为 0，指向 `/opt/homebrew`、`.venv` 或仓库的开发载入项为 0；44 个符号链接均有效且不指向 bundle 外。
- 2026-08-04：PyInstaller 未提供 Developer ID identity，仅执行 Apple Silicon bundle 所需的 ad-hoc signing；`codesign --verify --deep --strict --verbose=4` 通过，`Signature=adhoc`、`TeamIdentifier=not set`。未执行 Developer ID 正式签名、Apple 公证、stapling、sandbox、DMG、GitHub Release 或任何系统安全设置修改；`spctl` 因此按预期返回 rejected，并如实记录而不作为本阶段失败。
- 2026-08-04：使用最终 `.app` 完成无 `VIRTUAL_ENV`、仅系统 PATH 且 cwd 为 `/private/tmp`、以及 `ditto` 复制到仓库外临时目录的三种独立启动验证；限制环境和仓库外进程的 `lsof` 均未发现 `/opt/homebrew`、`.venv` 或仓库源码访问，复制后符号链接有效，测试副本已清理。Computer Use 从 Finder 打开最终应用，中文 windowed GUI 正常出现且没有伴随终端窗口。
- 2026-08-04：`verify_packaged_pipeline.sh` 只使用 `AudioShifter.app/Contents/Frameworks/bin/` 内部工具，在限制 PATH 下完成 WAV、MP3、M4A、FLAC 四格式真实处理；覆盖大写扩展名、中文、空格、括号、`&` 和单引号路径，四份输出均为 MP3、44100 Hz、双声道、320000 bit/s，源 SHA-256 均未变化。同名 `_2`/`_3`、旧输出哈希保护、真实 Rubber Band 取消、零残缺输出、零工作区泄漏和子进程回收均通过。
- 2026-08-04：Computer Use 对最终打包应用执行完整 GUI 自检：系统文件选择器、`+3/-20` 后台处理、响应性、按钮状态、阶段状态、成功 Downloads 路径和 FFprobe 均通过；第二次处理明确提示不覆盖并生成 `_2`，首份输出和源文件哈希未变。长音频处理中捕获的实际子进程为 bundle 内 `Contents/Frameworks/bin/rubberband`；取消后无输出、无任务目录、无子进程且 GUI 可再次使用。运行中关闭选择 No 后任务继续，第二次选择 Yes 后先取消清理再退出，最终无遗留应用或工具进程。所有明确记录的合成输入和 Downloads 输出均已按完整路径删除。
- 2026-08-04：最终自动化回归为 `137 passed, 0 failed, 0 skipped`，其中 109 项单元/故障注入/打包源测试、28 项集成测试；最终构建静态审计和真实打包管线脚本也均通过。完整证据记录于 `macos/packaging_test_report.md`，用户入口更新于 `macos/README.md`，实际内置组件与许可证材料记录于 `macos/THIRD_PARTY_NOTICES.md` 和 `macos/licenses/`。本应用只在 Apple Silicon arm64、macOS 27.0 build `26A5378n` 上构建和验证；旧版 macOS 未测试，可能无法运行，不承诺 Intel、Rosetta 或 universal2。
- 2026-08-04：建立阶段提交 `f0f4dcd`（`build: add standalone macOS app packaging`）、`3a627a4`（`test: verify standalone macOS app`）和 `710677c`（`docs: record macOS packaging results`）；`.app`、build/dist、第三方二进制/动态库、虚拟环境、测试音频和 Downloads 输出均保持未跟踪且未提交。
- 2026-08-04：完成非开发机跨机器人工验证：将未使用 Developer ID 签名、未经 Apple 公证的 `AudioShifter.app` 通过 AirDrop 传输到另一台符合目标范围的 Apple Silicon Mac；首次启动被 Gatekeeper 以“Apple 无法验证是否包含恶意软件”正常拦截。用户在“系统设置 → 隐私与安全性”中对该应用选择“仍要打开”完成单应用放行后，应用可正常启动并完成音频变调处理，界面和处理逻辑符合预期。该结果确认独立 `.app` 可在非开发机上运行，但未改变当前 ad-hoc 签名、未公证及首次启动需人工放行的分发边界。
- 2026-08-04：为首个 macOS 二进制 Pre-release 建立可重复 Release 工具、固定双语 Release notes 和精确忽略目录；提交 `d1f6285`（`release: prepare v0.1.0-alpha.1 assets`）。创建并推送 annotated tag `v0.1.0-alpha.1`，tag 对象 `348e563` 固定到应用/源码 commit `d1f628503d08efd9813433274181a2a9fe5bec27`，未删除、移动或覆盖该 tag。随后提交源码归档二进制过滤修复 `ed39abd` 和验证器误报修复 `c5ec2fc`；最终生成器从 detached tag worktree 构建应用，并在对应源码中单独保存生成器 commit `c5ec2fcbcb5566dabd9ff45cd3ab49e1fe52db98` 及完整脚本。
- 2026-08-04：最终 Release 候选回归为 `144 passed, 0 failed, 0 skipped`。从 tag 重建的 `.app` 为 63,356,565 字节；最终 ZIP 解压副本递归审计 75 个 Mach-O 全部 thin arm64、324 条动态引用、20 个 LC_RPATH、44 个包内有效符号链接，外部非系统及开发环境 load command 均为 0，ad-hoc `codesign --verify --deep --strict` 返回 0。受限系统 PATH、无 `VIRTUAL_ENV` 和系统临时 cwd 启动通过；ZIP 内部工具完成 WAV、MP3、M4A、FLAC 四格式真实处理，输出均为 MP3/44100 Hz/双声道/320000 bit/s，同名、源哈希保护、真实取消、进程回收和零临时泄漏均通过。
- 2026-08-04：生成 `AudioShifter-v0.1.0-alpha.1-macOS27-arm64.zip`（27,736,114 字节，SHA-256 `18b2d96b0802f5afb800b3ee6926e3a31b4bc9fecedbcd06182c266ca130d788`）、`AudioShifter-v0.1.0-alpha.1-corresponding-source.tar.gz`（199,987,644 字节，SHA-256 `a24e83225522dbc193e6a800625ce0f1652f03317693cce2064ada7a272f8340`）和 `SHA256SUMS.txt`（234 字节，SHA-256 `4e7b7b4073b6304a0808dcb608d8b3307d1100277bfffe4ffcb035275d696a84`）。对应源码覆盖 22 个实际内置第三方组件、23 条准确源码记录、22 份历史 Homebrew formula、8 个适用补丁、75/75 Mach-O 映射和 193 个内部哈希；官方归档 SHA 先完成核验，再排除 64 个经 magic header 确认的上游预编译文件，最终源码包第三方编译二进制审计通过。
- 2026-08-04：使用已认证的 GitHub CLI 2.96.0 创建 Draft Pre-release（database ID `364786397`），标题、tag、Pre-release 标志、Release notes 和三个附件均核对通过，附件状态均为 `uploaded`，GitHub 报告的大小和 SHA-256 与本地一致。Draft URL 为 `https://github.com/smter6626/AudioShifter/releases/tag/untagged-35d3672bf3cc1ee4310c`，只供已认证协作者访问；未点击或调用 Publish。GitHub 自动 tag source ZIP/tar.gz 均实际下载，其 89 项文件 manifest 与本地 `git archive v0.1.0-alpha.1` 完全一致。
- 2026-08-04：从 GitHub Draft 重新下载三个附件，逐文件与本地候选 `cmp` 一致，`shasum -a 256 -c SHA256SUMS.txt` 为两个 `OK`；仅针对下载副本再次完成 ZIP 解压、codesign、Mach-O、符号链接、受限 PATH、四格式管线、冲突、取消、MANIFEST、源码/补丁和全部内部哈希验证，最终均 PASS。完整证据位于 `macos/release/release_verification_v0.1.0-alpha.1.md`。
- 2026-08-04：根目录不存在 `LICENSE`、`LICENSE.*`、`COPYING` 或 `COPYING.*`，可见源码和 Windows 历史授权/激活文字也不构成明确项目分发许可；未擅自选择或添加 GPL、MIT、Apache、专有或其他项目许可证。最终状态为 `PARTIAL — Draft Release prepared; public publication blocked by project licence decision`；需要项目所有者作出的单一决定是明确授权一个与内置 GPL 组件兼容、并说明覆盖自有代码范围的根级项目许可证。Android active step 保持不变，未执行 Android 实现，也未修改 Windows 历史文件。
- 2026-08-04：项目所有者 Yeming Dai 明确授权其拥有版权的 `macos/` 源码、测试、构建/打包/Release 工具，当前及后续 `mobile/` 项目源码、测试、构建工具，相关根级共享代码/构建配置和项目文档采用 `GPL-3.0-or-later`；新增未经改写的官方 GPLv3 根级 `LICENSE`（SHA-256 `3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986`）、范围文件 `LICENSING.md` 和品牌政策 `TRADEMARKS.md`。所有 `windows/` 历史内容、AudioShifter 名称/Logo/应用图标/官方品牌和第三方材料明确排除；品牌政策允许 GPL 代码商业 fork，但要求修改版改名、改 bundle identifier、换图标、声明非官方且不得冒充官方来源。
- 2026-08-04：为主要自有源码和脚本加入 SPDX/copyright 标识；`pyproject.toml` 使用 PEP 639 `License-Expression: GPL-3.0-or-later` 语义和许可证文件元数据，实际 wheel 构建报告 Metadata-Version 2.4、版本 `0.1.0a2`。PyInstaller 应用版本更新为 `0.1.0-alpha.2` / build `2`，最终 `.app` 的 Resources 内包含 `LICENSE`、`LICENSING.md`、`TRADEMARKS.md`、`THIRD_PARTY_NOTICES.md` 和第三方 `licenses/`；根 README、`macos/README.md`、third-party notices、Release notes 和工具说明同步完成。提交 `81686f9`（`license: add GPL and brand policy`）与 `64f5b66`（`docs: update project and macOS release documentation`）。
- 2026-08-04：创建并推送 annotated tag `v0.1.0-alpha.2`，固定到 Release/application/tooling commit `64f5b664e8f6aca1fccc3d7f026f311959519120`。从该 tag 的 detached worktree 重新构建最终应用；自动化回归为 `153 passed, 0 failed, 0 skipped`。最终 App ZIP 解压副本大小 63,401,560 字节，75 个 Mach-O 全部 thin arm64，324 条动态引用、20 个 LC_RPATH、47 个有效包内符号链接，外部非系统及开发环境 load command 为 0，ad-hoc codesign 返回 0；受限 PATH、四格式处理、同名不覆盖、源哈希、真实取消、进程回收和零临时泄漏均通过。
- 2026-08-04：生成 `AudioShifter-v0.1.0-alpha.2-macOS27-arm64.zip`（27,753,339 字节，SHA-256 `d01c9a6e4fca0fd2dabfb8c27443d1c601d8c8b8e1f063b73f83ed3372c37525`）、`AudioShifter-v0.1.0-alpha.2-corresponding-source.tar.gz`（200,037,471 字节，SHA-256 `b6ab71d2ee0737329e43e42d4104ad21ad41a03c1d233817c6bceaaa3c598d0f`）和 `SHA256SUMS.txt`（234 字节，SHA-256 `ec7e1bd893ec2ab4c06373984bb0fb9c3be9b08ea6878ba44be8d5c65750b1b2`）。对应源码记录 GPL 范围与品牌/Windows/第三方排除，覆盖 22 个组件、23 条准确源码记录、8 个适用补丁、75/75 Mach-O 映射和 199 个内部哈希；项目许可证、tag 源码、formula/receipt、patch、构建证据和第三方许可证验证通过。
- 2026-08-04：使用已认证 GitHub CLI 2.96.0 创建新的 Draft Pre-release（database ID `364826053`），URL `https://github.com/smter6626/AudioShifter/releases/tag/untagged-92e819bb21db79a10afc`；tag、标题、正文、Draft/Pre-release 标志和三项附件均核对，资产状态均为 uploaded，大小与 GitHub SHA-256 和本地一致，`published_at=null`，未执行 Publish。从 Draft 下载三个附件后，外层哈希两个 OK，并仅针对下载副本再次完成 App 解压、法律资源、codesign、Mach-O、动态路径、符号链接、受限启动、四格式、冲突、取消、对应源码 MANIFEST、patch 和全部内部哈希，最终 PASS。alpha.1 tag、Draft ID `364786397`、三项资产和未发布状态均保持不变；完整证据位于 `macos/release/release_verification_v0.1.0-alpha.2.md`。最终状态为 `PARTIAL — v0.1.0-alpha.2 Draft prepared; awaiting user review and manual non-development-Mac acceptance`，Android active step 未改变，Windows 历史内容未修改。
- 2026-08-04：完成 alpha.3 版本身份修复：Git tag/显示版本为 `v0.1.0-alpha.3`，Python 版本为 `0.1.0a3`；最终 Info.plist 的 `CFBundleShortVersionString=0.1.0`（满足三段数字格式）且 `CFBundleVersion=3`，bundle identifier 保持 `io.github.smter6626.audioshifter`。采用 Aqua Tk 8.6 特殊 `.menubar.apple` 原生映射，在 Apple 图标右侧真实 `AudioShifter` 应用菜单加入严格名为 `License` 的菜单项；未在主 GUI、File 或 Help 菜单设置许可证入口。
- 2026-08-04：实现非阻塞、可调整大小、带垂直滚动条的英文 `AudioShifter License` 单例窗口；正文只读但可选择复制，支持 Command-C/Command-W、关闭后重开和重复调用前置。窗口从源码根或冻结 bundle `Contents/Resources/LICENSE` 读取完整 GPLv3，不依赖 cwd、仓库绝对路径或网络；根级、最终 App 和 Draft 下载 App 的正文 SHA-256 均为 `3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986`。Computer Use 对 tag 构建和 Draft 下载副本均实际确认原生应用菜单、License 项、英文头部、GPL 开头/末尾、单例、Command-W 和重开；未申请或修改 Accessibility/隐私权限，非开发机最终人工视觉验收仍待用户执行。
- 2026-08-04：更新 `TRADEMARKS.md` 与 `LICENSING.md`，窄授权仅允许为官方 tag 的未修改构建或未修改官方 Release 的原样转发而复制名称、图标和其他品牌资产；修改版仍须更换名称、bundle identifier、Logo、图标和来源识别品牌。该政策不把品牌资产改为 GPL，也不限制以其他品牌商业使用、收费、修改或分发 GPL 代码。普通用户下载流程改为只需 App ZIP 和 `SHA256SUMS.txt`，无需约 200 MB 对应源码；实际在不含源码包的独立目录执行 App-only `grep ... | shasum -a 256 -c -` 并得到 `OK`。
- 2026-08-04：提交并推送 `a6174b4`（`release: prepare v0.1.0-alpha.3`），创建并推送 annotated tag `v0.1.0-alpha.3`（tag 对象 `301d4ef`），固定到 Release/application/tooling commit `a6174b45666a586c2920afdd42e600dce7a8bcda`。从该 tag 的 detached worktree重新构建；自动化回归为 `165 passed, 0 failed, 0 skipped`。最终 ZIP 解压 App 大小 63,410,941 字节，75 个 Mach-O 全部 thin arm64，324 条动态引用、20 个 LC_RPATH、47 个有效包内符号链接，外部非系统及开发环境 load command 为 0，ad-hoc codesign 返回 0；受限 PATH、四格式处理、同名不覆盖、四份源哈希、真实取消、进程回收和零临时泄漏全部通过。
- 2026-08-04：生成 `AudioShifter-v0.1.0-alpha.3-macOS27-arm64.zip`（27,764,722 字节，SHA-256 `a7866775734cbcde12d1b3d5186a09f71da71fe380650438d67a8d1f2987711d`）、`AudioShifter-v0.1.0-alpha.3-corresponding-source.tar.gz`（200,051,018 字节，SHA-256 `2936187f84081c322e3d43254ec2a7f829037db84dc9b7e3532fc868dd9546d2`）和 `SHA256SUMS.txt`（234 字节，SHA-256 `611171939727f40a008c514f6664b5d2ddd5d04b17b23827622fc8babb88d9c2`）。对应源码覆盖 22 个实际组件、23 条准确源码记录、22 份 formula/receipt、8 个适用补丁、75/75 Mach-O 映射和 201 个内部哈希；包含 alpha.3 tag 源码、完整项目法律材料、License 窗口实现、Release 工具、第三方源码/许可证和构建证据。
- 2026-08-04：使用已认证 GitHub CLI 创建未公开 alpha.3 Draft Pre-release（database ID `364860803`），URL `https://github.com/smter6626/AudioShifter/releases/tag/untagged-eb4c98469e0200c34d24`；tag、标题、Draft=`true`、Pre-release=`true`、`published_at=null` 与三项 uploaded 附件逐项核对，GitHub 大小/摘要和本地完全一致，未执行 Publish。从 Draft 独立下载三项附件后逐字节一致，两个归档外层哈希均为 OK，并仅针对下载副本再次完成 ZIP/版本/法律资源/原生菜单与窗口、codesign、Mach-O、动态路径、符号链接、受限启动、四格式、冲突、取消、对应源码 MANIFEST、patch 和内部哈希验证。alpha.1/alpha.2 的 tag、Draft、附件和未发布状态均保持不变；完整证据位于 `macos/release/release_verification_v0.1.0-alpha.3.md`。最终状态为 `PARTIAL — v0.1.0-alpha.3 Draft prepared; awaiting user review and manual non-development-Mac acceptance`，Android active step 未改变，Windows 历史内容未修改。
- 2026-08-04：完成 `v0.1.0-alpha.3` 非开发机人工验收：用户在另一台符合目标范围的 Apple Silicon Mac 从 Draft 下载 App ZIP 与 `SHA256SUMS.txt`。原文档中带行尾锚点的筛选命令在该下载环境未输出哈希行；改用不带行尾锚点并通过 `tr -d '\r'` 规范化输入后，`shasum -a 256 -c -` 返回 `AudioShifter-v0.1.0-alpha.3-macOS27-arm64.zip: OK`，随后直接计算 ZIP SHA-256 为 `a7866775734cbcde12d1b3d5186a09f71da71fe380650438d67a8d1f2987711d`，与 Draft 记录一致。ZIP 可正常解压；首次运行被 Gatekeeper 按预期拦截，经“系统设置 → 隐私与安全性 → 仍要打开”单应用放行后，应用可正常启动和使用，当前人工检查未发现明显缺陷。`v0.1.0-alpha.3` 因此推进为 `PASS — manually accepted on a non-development Apple Silicon Mac`；GitHub Release 截至本记录仍为未公开 Draft，尚未执行 Publish。
- 2026-08-04：修正 alpha.3 当前用户说明中的 App-only SHA-256 命令：原带 `$` 行尾锚点的形式在构建验证环境中曾通过，但在非开发目标 Mac 的下载副本上未匹配出可识别的哈希行；统一改为不带行尾锚点，并在 `shasum` 前使用 `tr -d '\r'` 兼容 CRLF。目标 Mac 已使用新命令得到 `OK`，直接计算 ZIP 摘要也与 Draft 完全一致；本地又分别以 LF 和合成 CRLF 的 `SHA256SUMS.txt` 验证新命令。未修改 ZIP、`SHA256SUMS.txt` Release 附件或任何已记录摘要；本条记录时 Release 仍为 Draft。
- 2026-08-04：在非开发 Apple Silicon Mac 人工验收通过后，使用 GitHub CLI 将现有 Draft database ID `364860803` 正式公开为 `v0.1.0-alpha.3` GitHub Pre-release；`isDraft=false`、`isPrerelease=true`，`publishedAt=2026-08-04T13:39:17Z`，公开 URL 为 `https://github.com/smter6626/AudioShifter/releases/tag/v0.1.0-alpha.3`。未重新构建应用，未移动 tag（仍固定到 `a6174b45666a586c2920afdd42e600dce7a8bcda`），未删除、替换或重新上传附件；公开资产名称、asset ID、大小和 SHA-256 与人工验收版本完全一致。使用全新目录从公开 Release 下载三项附件后，可移植 App-only 命令为 `OK`，完整 `SHA256SUMS.txt` 为两个 `OK`，两个归档直接摘要也与固定记录一致；未认证 HTTP 请求返回 200。最终状态为 `PASS — v0.1.0-alpha.3 manually accepted and publicly released as a GitHub Pre-release`。alpha.1/alpha.2 内部 Draft 保持不变，Android active step 未改变，Windows 历史内容未修改。

# completed step specification — macOS runnable MVP

- 完成 macOS 第一阶段可运行 MVP：按照已确认的行为合同，依次建立纯逻辑模块、真实 FFmpeg/Rubber Band 音频管线、中文 Tkinter GUI 和端到端自检，使用户可以从现有虚拟环境启动程序并使用真实音频文件测试。本步骤允许编写正式业务代码、自动化测试和 GUI，也允许使用用户已手动确认可用的 computer-use/桌面控制能力执行 UI 自检；不执行 PyInstaller 打包，不生成 `.app` 或 `.dmg`，不处理签名、公证和正式分发。

  ## 1. Git、文档与工具前置检查

  1. 进入本地仓库 `/Users/smterpro/Workspace/Tools/AudioShifter/`，执行：

     ```bash
     git status --short
     git branch -vv
     git pull --ff-only
     ```

     工作区必须干净，`main` 必须正确跟踪 `origin/main`。如存在未提交修改、无法快进、分支分叉或冲突，立即停止并报告；不得执行 `reset`、`stash`、`clean`、强制 checkout 或 force push。

  2. 完整阅读并遵守：

     ```text
     docs/macos_rebuild_static.md
     docs/macos_rebuild_runtime.md
     macos/design/behavior_spec.md
     macos/design/architecture_plan.md
     macos/design/verification_matrix.md
     macos/environment_report.md
     macos/Brewfile
     macos/requirements-dev.txt
     ```

     行为规格优先于实现便利。不得为了让代码或测试通过而修改已确认的参数、输出、命名、不覆盖、取消或错误合同；若文档之间存在无法兼容的冲突，停止并报告。

  3. 不得修改任何 Windows 历史源码、文档、打包配置或 `_local_artifacts`。Windows 代码只作为历史参考，不能复制机器码/激活逻辑、固定 Downloads 临时文件、静默覆盖或 Tkinter 跨线程更新等旧缺陷。

  4. 确认现有环境仍可用，并记录实际版本：

     ```bash
     macos/.venv/bin/python --version
     ffmpeg -version
     ffprobe -version
     rubberband --version
     ```

     不主动升级、重装或清理 Homebrew 公式。只允许在 `macos/.venv/` 中增加当前阶段实际需要的 Python 测试依赖。

  5. computer-use/桌面控制插件由用户在任务开始前手动测试和确认。Codex 可以调用已存在且已授权的能力，但不得自行安装插件、修改插件配置、申请额外系统权限或改变 macOS 安全设置。computer-use 用于最终 UI 交互自检，不能替代单元测试、集成测试、文件系统检查和 FFprobe 验证。

  6. 若 computer-use 在实际执行时不可用或失去授权，核心、真实管线和 GUI 开发仍应继续；不得伪造 UI 自检通过。最终报告将 UI 自动操作标记为待人工执行，并提供不超过 10 步的人工验证流程。

  ## 2. 项目结构与可重复运行入口

  1. 建立正式 Python 包与测试结构，原则上采用：

     ```text
     macos/
     ├── src/
     │   └── audioshifter/
     │       ├── __init__.py
     │       ├── __main__.py
     │       ├── models.py
     │       ├── errors.py
     │       ├── validation.py
     │       ├── naming.py
     │       ├── dependencies.py
     │       ├── workspace.py
     │       ├── process_runner.py
     │       ├── ffmpeg_adapter.py
     │       ├── rubberband_adapter.py
     │       ├── pipeline.py
     │       ├── controller.py
     │       └── gui.py
     ├── tests/
     │   ├── unit/
     │   └── integration/
     └── design/
     ```

     可以根据实现证据少量调整文件数量，但必须保持 `architecture_plan.md` 规定的职责分离和依赖方向。

  2. 配置可重复的包安装和导入方式，不能依赖当前工作目录或手工修改 `PYTHONPATH`。优先使用标准 `pyproject.toml` 与 editable install。

  3. 从源码启动 GUI 的固定入口应为：

     ```bash
     cd /Users/smterpro/Workspace/Tools/AudioShifter
     source macos/.venv/bin/activate
     python -m audioshifter
     ```

     如采用等价入口，必须同样简短、稳定，并写入 `macos/README.md`。

  4. 在 `macos/requirements-dev.txt` 中加入并固定实际使用的测试依赖，优先使用 `pytest`。不得加入未使用的框架或改变已验证的 Python/Tk/FFmpeg/Rubber Band 组合。

  ## 3. 第一关：纯逻辑模块和单元测试

  1. 实现 `models.py`：
     - 不可变 `ProcessingRequest`
     - `ProcessingResult`
     - 输出路径分配结果
     - 稳定处理阶段和终止状态
     - 必要的进度事件数据

  2. 实现 `errors.py`：
     - 结构化 `AppError`
     - `behavior_spec.md` 规定的稳定错误码
     - 面向用户的简洁提示
     - 内部诊断信息与原始异常链

     不得使用任意异常字符串代替合同错误，也不得在底层模块弹出 Tkinter messagebox。

  3. 实现 `validation.py`：
     - MP3、M4A、WAV、FLAC 扩展名校验，大小写不敏感
     - 输入存在、普通文件、非零大小和可读性检查
     - 变调文本解析：只允许整数，范围 `-24` 至 `+24`
     - 变速文本解析：允许有限小数，范围 `-95` 至 `+400`
     - 用户输入不得包含 `%`
     - 使用 `Decimal` 或等价精确十进制类型保存和格式化速度值
     - 计算 `tempo_ratio = 1 + speed_change / 100`
     - Downloads 存在、为目录、可写的基础预检查

     所有无效输入必须在启动任何外部进程前失败并映射到稳定错误码。

  4. 实现 `naming.py`：
     - 固定命名 `<stem><signed_pitch><signed_speed>%.mp3`
     - `0` 统一表示为 `+0`
     - 速度小数去除无意义尾随零
     - 两个参数永远保留
     - 基础名存在时依次选择 `_2`、`_3` 等名称
     - 永不覆盖、删除或重命名已有文件
     - 返回是否需要冲突提示及实际目标路径
     - 支持最终写入前重新检查并安全重新分配路径

  5. 实现 `workspace.py`：
     - 每个任务创建唯一系统临时目录
     - 提供标准化 WAV 和 Rubber Band 输出 WAV 路径
     - 不在 Downloads、输入目录或仓库中创建临时音频
     - 只清理当前对象创建的工作区
     - 拒绝删除临时根之外或来源不明的路径
     - 成功、失败和取消均可调用清理
     - 清理失败形成 warning，不删除已成功输出

  6. 实现最小单任务状态保护：
     - 活动任务存在时拒绝第二次启动
     - 成功、失败或取消结束后释放
     - 请求提交后参数不可被 GUI 修改
     - 不使用零散的全局可变变量维护任务状态

  7. 按 `verification_matrix.md` 编写单元测试，至少覆盖：

     ```text
     PITCH-T001 ～ PITCH-T013
     SPEED-T001 ～ SPEED-T014
     NAME-T001 ～ NAME-T012
     IN-T005 ～ IN-T010
     TEMP-T001
     TEMP-T009
     TASK-T002
     ERR-T001
     ```

     测试名称或参数化 case 必须保留矩阵 ID，以保证合同可追踪。

  8. 第一关只有在选定的 P0 单元测试全部通过后才能进入真实音频管线。不得通过放宽合同让测试迁就实现。

  ## 4. 第二关：依赖解析与外部进程执行层

  1. 实现 `dependencies.py`：
     - 开发环境中解析当前 FFmpeg、FFprobe 和 Rubber Band
     - 为后续 PyInstaller 内置资源保留独立解析策略接口
     - 验证路径存在、是普通文件且可执行
     - 不使用 Windows 二进制
     - 上层模块不得直接依赖 `/opt/homebrew` 固定字符串

  2. 实现 `process_runner.py`：
     - 只使用参数数组，不执行拼接 Shell 字符串
     - 捕获 stdout、stderr 和退出码
     - 保存完整内部诊断，同时生成简洁用户错误
     - 支持取消当前子进程及其相关子进程
     - 处理非 UTF-8 输出
     - 普通取消映射为 `CANCELLED`，不得映射为未知错误
     - 不导入 Tkinter、不调用 messagebox

  3. 为进程执行层建立隔离测试，至少覆盖：
     - 成功命令
     - 非零退出码
     - 命令不存在
     - 命令不可执行
     - stderr 捕获
     - 取消长时间命令
     - 取消后无遗留进程

  ## 5. 第三关：真实音频适配器与非 GUI 管线

  1. 实现 `ffmpeg_adapter.py`：
     - 解码并标准化为 WAV、PCM signed 16-bit little-endian、44.1 kHz、双声道
     - 使用 `libmp3lame` 编码 320 kbps、44.1 kHz、双声道 MP3
     - 使用 FFprobe 检查输入媒体和最终输出
     - 分别映射媒体无效、解码失败、编码失败和输出验证失败
     - 不复制源文件元数据
     - 最终输出不得使用静默覆盖行为

  2. 实现 `rubberband_adapter.py`：
     - 传入整数半音
     - 传入计算后的 tempo multiplier
     - 使用 R3/finer 处理方向
     - 使用 formant preservation
     - 映射退出码、stderr 和取消状态

  3. 实现 `pipeline.py`，正常状态至少为：

     ```text
     VALIDATING
     → PREPARING
     → DECODING
     → PROCESSING
     → ENCODING
     → VERIFYING
     → SUCCEEDED
     ```

     终止状态为 `FAILED` 或 `CANCELLED`。

  4. 管线必须：
     - 在启动外部进程前完成参数和路径校验
     - 保护源文件不被修改、移动、重命名或删除
     - 创建唯一临时工作区
     - 分配 Downloads 输出路径
     - 同名时返回冲突提示信息
     - 编码前再次检查目标路径，防止外部竞态覆盖
     - 三个处理阶段分别报告状态
     - 成功后使用 FFprobe 验证最终 MP3
     - 失败或取消时删除不完整输出
     - 所有终止路径尽可能清理临时资源
     - 清理失败不掩盖已经成功生成的结果

  5. 在系统临时目录动态生成短小合成音频，不提交音频文件。建立集成测试，至少覆盖：
     - MP3、M4A、WAV、FLAC 输入
     - 大写扩展名
     - 中文、空格、括号、`&` 等路径
     - 只变调、只变速、同时变调和变速
     - `pitch = 0`、`speed = 0`
     - 变调边界 `-24`、`+24`
     - 代表性速度值及边界输入可接受性
     - 固定输出命名和同名 `_2`
     - 源文件哈希不变
     - 最终 MP3 编码、码率、采样率、声道和可读性
     - 时长变化方向与速度合同一致
     - 损坏音频与伪装扩展名
     - FFmpeg/Rubber Band 缺失或不可执行
     - 子进程失败
     - 取消与临时资源清理

  6. 本阶段不固定未经测试证明的严格音质阈值或精确时长误差阈值，但必须验证处理方向、输出有效性和合同媒体规格。

  7. 第二、三关全部 P0 测试通过后才能进入 GUI。

  ## 6. 第四关：中文 Tkinter GUI

  1. 实现 `controller.py`：
     - 连接 GUI 与管线
     - 统一执行单任务互斥
     - 在后台线程运行管线
     - 使用线程安全事件队列
     - 通过 `root.after()` 在 Tkinter 主线程处理状态、结果和错误
     - 管理取消和运行中关闭应用
     - GUI 不直接执行子进程或删除临时文件

  2. 实现 `gui.py`，至少提供：
     - 中文窗口标题和中文操作说明
     - 文件选择器
     - 当前输入路径显示
     - 变调输入
     - 变速输入，并明确说明其为相对变化百分比、无需输入 `%`
     - “开始处理”按钮
     - “取消”按钮
     - 当前阶段状态
     - 成功、失败和冲突提示弹窗

  3. 文件选择器只展示 MP3、M4A、WAV 和 FLAC。默认值为：

     ```text
     变调：0
     变速：0
     ```

  4. 处理期间：
     - 禁止再次启动任务
     - 启用取消按钮
     - 界面保持响应
     - 显示解码、处理、编码和验证等状态
     - 已提交请求不可受输入框后续变化影响

  5. 同名输出时，弹窗说明：
     - 原目标已存在
     - 已有文件不会被覆盖
     - 本次实际使用的新文件名或完整路径

     用户确认后继续，不要求手工改名。

  6. Downloads 不存在、不是目录、不可写或磁盘空间不足时，弹窗说明具体原因并终止；不自动切换目录。

  7. 成功后显示完整 Downloads 输出路径，并恢复可再次处理状态。

  8. 用户取消时：
     - 终止当前进程
     - 不启动后续阶段
     - 删除不完整输出
     - 清理临时工作区
     - 恢复就绪状态
     - 不显示“未知错误”或“处理失败”替代取消状态

  9. 运行期间关闭窗口时：
     - 询问是否取消当前任务并退出
     - 用户拒绝时继续处理
     - 用户确认时执行完整取消和清理后退出
     - 不遗留后台进程

  10. GUI 不提供并发、队列、批处理、元数据选项、输出格式选择或自定义输出目录。

  ## 7. 第五关：自动化自检和 computer-use UI 自检

  1. 创建 `macos/mvp_test_report.md`，至少记录：
     - Python、pytest、FFmpeg、FFprobe 和 Rubber Band 版本
     - 单元测试与集成测试数量及结果
     - 失败、跳过和未覆盖项
     - 已覆盖的验证矩阵 ID
     - GUI 启动结果
     - computer-use UI 自检结果
     - 代表性输出媒体信息
     - 未解决问题
     - 最终状态 `PASS`、`PARTIAL` 或 `FAIL`

  2. 运行完整自动化测试：

     ```bash
     macos/.venv/bin/python -m pytest
     ```

     所有 P0 单元测试和真实管线集成测试必须通过，才能开始 UI 自检。

  3. 在系统临时目录生成短合成输入，不使用用户私人音频，不提交测试输入或输出。

  4. computer-use 可用时执行完整 UI 自检：
     - 启动应用并确认中文窗口正常显示
     - 通过系统文件选择器选择合成音频
     - 输入变调 `+3`、变速 `-20`
     - 启动处理并确认界面保持响应、按钮和状态正确变化
     - 等待成功提示
     - 确认输出位于 `~/Downloads/`
     - 确认文件名为 `<stem>+3-20%.mp3`
     - 使用 FFprobe 验证输出规格
     - 再次使用相同输入和参数，确认冲突提示及 `_2` 输出
     - 确认第一份输出未被覆盖，源文件未改变
     - 仅删除有完整记录且确认属于本轮自检的合成输入和输出

  5. UI 自检还应确认：
     - 无输入时提示
     - 变调小数和越界输入被拒绝
     - 变速带 `%` 和越界输入被拒绝
     - 重复点击不会产生并发任务
     - 取消操作恢复界面且无残留进程/临时文件
     - 运行中关闭窗口出现确认

  6. computer-use 的视觉观察只验证交互，不替代文件系统、哈希、进程状态和 FFprobe 检查。

  7. 若 computer-use 实际不可用：
     - 不得伪造 UI PASS
     - 仍需完成核心、真实管线、GUI 和自动化测试
     - 至少程序化验证 Tkinter 窗口可创建、更新和销毁
     - 报告中标记 `PARTIAL — awaiting manual UI interaction check`
     - 提供不超过 10 步的人工验证流程

  ## 8. README 与用户手动测试入口

  1. 更新 `macos/README.md`，至少写明：
     - 环境恢复和依赖安装命令
     - 启动 GUI 命令
     - 运行完整测试命令
     - 支持格式
     - 参数含义与范围
     - 输出位置和命名规则
     - 当前尚未打包为 `.app`
     - 已知限制

  2. 用户醒来后应能按以下最短流程直接测试真实音频：

     ```bash
     cd /Users/smterpro/Workspace/Tools/AudioShifter
     source macos/.venv/bin/activate
     python -m audioshifter
     ```

  ## 9. 提交与阶段检查点

  长期任务必须按通过的阶段建立独立提交，避免数小时工作只形成一个不可恢复的大提交。建议：

  1. 纯逻辑和单元测试：

     ```text
     test: add macOS core contract tests
     ```

  2. 真实音频处理核心：

     ```text
     feat: implement macOS audio processing pipeline
     ```

  3. 中文 GUI：

     ```text
     feat: add macOS Tkinter MVP
     ```

  4. 自检、README 和报告：

     ```text
     test: verify macOS MVP end to end
     ```

  每次提交前运行该阶段对应的测试。不得提交会破坏下一阶段的已知失败中间状态。

  ## 10. Git 范围与禁止提交项

  提交前执行：

  ```bash
  git status --short
  git diff
  git ls-files
  find . -type f -size +10M -not -path './.git/*'
  ```

  只提交 macOS Python 源码、自动化测试、最小测试配置、依赖/包配置、README、测试报告和 runtime 文档。

  不得提交：
  - `macos/.venv/`
  - `__pycache__/`、pytest/coverage 缓存
  - 合成或用户音频
  - Downloads 输出
  - 第三方二进制或 Homebrew 文件
  - `.app`、`.dmg`、build、dist
  - 证书、私钥、令牌或环境秘密
  - 任何 Windows 文件变更

  若产生固定本地测试目录，应在根 `.gitignore` 中加入精确目录规则；不得全局忽略所有 MP3、WAV、M4A 或 FLAC，因为后续可能需要经审查的小型测试夹具。

  ## 11. 中断条件

  以下情况必须停止并报告，不得自行突破：

  1. Git 工作区不干净、无法 fast-forward 或远端出现未知提交。
  2. static、behavior、architecture 或 verification 文档存在无法兼容的合同冲突。
  3. 需要修改已确认参数范围、命名、Downloads 输出、不覆盖、取消或单任务规则才能继续。
  4. 需要修改或执行 Windows 历史文件。
  5. 需要升级、替换或大范围修改 Homebrew 环境。
  6. 当前 FFmpeg 或 Rubber Band 无法实现合同。
  7. 需要使用 Shell 字符串拼接才能处理用户路径。
  8. 安全取消无法避免遗留进程或残缺输出。
  9. 发现任何路径可能覆盖用户已有文件。
  10. 需要删除来源不明确的文件。
  11. 需要管理员权限、修改系统安全设置或安装来源不明的软件。
  12. 测试证明合同内部存在矛盾或关键文件系统语义不可安全实现。
  13. computer-use 要求 Codex 安装插件、修改插件配置或申请新的系统权限。
  14. 推送前远端 `main` 出现新提交或发生分叉。

  computer-use 不可用本身不阻塞核心实现，只影响最终 UI 自检等级。

  ## 12. 完成标准

  本 active step 只有在以下条件满足后才能关闭：

  1. 用户可以从现有 `.venv` 通过固定命令启动中文 GUI。
  2. 纯逻辑 P0 单元测试通过。
  3. FFmpeg/Rubber Band 真实管线 P0 集成测试通过。
  4. MP3、M4A、WAV 和 FLAC 均完成至少一条成功处理路径。
  5. 输出固定为 320 kbps、44.1 kHz、双声道 MP3。
  6. 输出固定进入 Downloads。
  7. 文件命名、零值、速度小数和同名递增符合合同。
  8. 源文件未被修改。
  9. 临时资源在成功、失败和取消后得到处理。
  10. 单任务约束和取消机制有效。
  11. GUI 在处理时保持响应，Tkinter 更新只发生在主线程。
  12. README 提供可直接执行的启动与测试命令。
  13. `macos/mvp_test_report.md` 如实记录自动化和 UI 自检结果。
  14. 未执行 PyInstaller，未生成发布包。
  15. Windows 目录没有任何修改。
  16. 所有提交已推送，工作区干净，本地与远端差异为 `0 0`。

  computer-use UI 自检完整通过时，本阶段最终状态可以标记为 `PASS`。

  核心、集成测试和 GUI 已完成，但 computer-use 不可用或 UI 操作未完成时，最终状态标记为 `PARTIAL — awaiting manual UI interaction check`；程序仍必须达到用户可以立即手动测试的程度。

  ## 13. Runtime 推进

  完成本阶段后，将实现结果、测试数量、UI 自检状态、报告路径和各阶段短 commit hash 追加到 `done`。

  新的 active step 改为：

  ```text
  使用 PyInstaller 构建并验证未签名的纯 arm64 macOS 应用包，收集 Python/Tk、FFmpeg、Rubber Band 及传递动态库，验证脱离 Homebrew 和开发虚拟环境后的独立运行能力；本步骤同时处理应用内依赖路径、Mach-O 架构、动态库重定位、最低 macOS 实测边界和许可证材料，但仍不执行 Developer ID 签名或 Apple 公证。
  ```

# completed step specification — standalone arm64 macOS application

- 使用 PyInstaller 构建并验证未使用 Developer ID 签名、未经 Apple 公证的纯 `arm64` macOS 应用包；收集 Python/Tk、FFmpeg、FFprobe、Rubber Band 及传递动态库，验证 Finder 双击、脱离 Homebrew PATH、开发虚拟环境和仓库后的独立运行能力；处理应用内依赖路径、Mach-O 架构、动态库重定位、ad-hoc signing、仅 macOS 27 的实测边界和许可证材料，不执行 Developer ID 签名或 Apple 公证。

# active step

- 在不修改 `windows/` 历史内容的前提下，开始 `mobile/` 下的 Android 移植准备阶段：先建立 Android 用户可见行为合同、架构计划、验证矩阵和开发环境事实，再根据已确认的 macOS 合同定义 Android MVP；本步骤开始前不得直接照搬桌面 GUI 或未经确认地改变参数、命名、输出保护和取消语义。

# next steps

- 为 Android 目标确认输入选择、输出位置、存储权限、后台任务、取消、前后台切换和文件分享行为，不将 macOS 的 Downloads/Tkinter 实现细节直接当成 Android 合同。
- 盘点可用 Android 音频工具链、FFmpeg/Rubber Band 构建路线、ABI、许可证和测试设备环境；在合同与环境报告完成前不开始产品实现。
- `v0.1.0-alpha.3` 已完成人工验收并公开为 GitHub Pre-release；alpha.1 和 alpha.2 内部 Draft 保持不变。是否进入 Developer ID 签名与 Apple 公证阶段仍另行决定。
