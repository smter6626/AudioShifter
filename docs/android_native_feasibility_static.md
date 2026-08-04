# AudioShifter Android 原生音频管线可行性验证：静态合同

> 文档类型：`static.md`
>
> 任务名称：**AudioShifter Android 原生音频管线可行性验证**
>
> 作用：记录 Android 移植 Phase 0 中长期稳定、原则上不随单次实验变化的背景、目标、范围、验收标准和执行约束。
>
> 本文档不记录当前执行步骤、临时命令、排错过程、完成记录或短期计划；这些内容应写入 `docs/android_native_feasibility_runtime.md`。Phase 0 通过后，正式 Android 产品行为、架构和验证矩阵应另行建立，不应把探索性结论直接当作最终产品合同。

## 1. 项目背景

AudioShifter 是一个面向非技术用户的本地音频变调与变速工具。Windows 历史版本和已经完成的 macOS 版本均使用 FFmpeg 与 Rubber Band 完成音频解码、变调、变速和重新编码。

macOS 复刻已经完成源码 MVP、独立应用打包、非开发机人工验收和 GitHub Pre-release 发布。Android 是下一平台，但 Android 与桌面系统在原生依赖、应用生命周期、文件访问、后台执行、CPU ABI、安装包结构和系统安全模型方面存在显著差异，因此不能把桌面实现直接复制为 Android 应用。

用户当前没有 Android 开发经验，但这不得成为限制技术路线、工具链深度或实现方案的理由。Phase 0 应同时作为可复现的工程实践与学习过程：在作出路线选择、引入 Android 专有组件或执行关键步骤时，主动向用户解释相关技术的用途、所在层级、与桌面实现的差异、为什么需要以及存在的主要替代方案。解释应服务于理解真实技术，不得通过隐藏、过度简化或回避 NDK、JNI、Gradle、ABI、Android 生命周期、存储模型等核心概念来换取表面上的低门槛。Codex 仍应优先采用可脚本化、可诊断、可复现的路线，但这是为了工程质量与可重复性，而不是因为用户缺少 Android 经验而缩小可选方案。

Windows 历史实现继续只作为产品行为和音频处理方向的参考。其源码、文档和构建内容不修改、不清理、不重构；旧机器码、激活码、注册码和授权文件机制不得在 Android 重新实现。

## 2. 仓库与平台上下文

- GitHub 仓库：`smter6626/AudioShifter`
- 仓库地址：`https://github.com/smter6626/AudioShifter`
- 默认分支：`main`
- 本地仓库：`/Users/smterpro/Workspace/Tools/AudioShifter`
- Android 开发根目录：`/Users/smterpro/Workspace/Tools/AudioShifter/mobile`
- 开发主机：Apple Silicon Mac
- 目标平台：Android
- Phase 0 首选目标 ABI：`arm64-v8a`
- 首选验证环境：Apple Silicon 上的官方 Android Emulator
- 最终产品仍必须经过真实 Android 设备验证；模拟器不能作为最终真机验收替代品

Phase 0 可以创建 `mobile/android/` 下的最小工程、脚本、原生源码、测试资源生成器和报告，但不得修改 `windows/` 历史内容，不得破坏已完成的 `macos/` 代码、构建和发布状态。

## 3. Phase 0 的核心目标

Phase 0 不是编写完整 Android 应用，而是**找出并证明至少一条可以在 Android 系统中实现 AudioShifter 核心音频处理的具体方案、依赖组合和工程路线**。

“可行路线”不能只停留在文档推测、第三方项目宣传、主机侧编译成功或单个库可以生成 `.so`。最终必须形成一条能够由当前仓库复现的链路，至少明确并验证：

1. Android 工具链与目标 ABI。
2. 使用的 FFmpeg、Rubber Band 或替代依赖及其固定来源、版本或 commit。
3. 原生依赖如何构建、链接并装入 APK 或 Android 测试载体。
4. Kotlin/Java 与原生处理层之间的调用边界，或其他明确可维护的调用方式。
5. 输入音频如何进入处理管线，输出音频如何写回 Android 可访问的位置。
6. 变调、变速、格式转换和最终 MP3 输出如何实现。
7. 处理过程如何报告成功、失败和取消，至少给出可实现且经最小验证的机制。
8. 从干净 checkout 到构建、安装、执行和验证的可重复命令。
9. 依赖许可证、源码提供和分发义务。
10. 该路线为什么适合后续完整 Android 应用，而不只是一次性实验。

Phase 0 的最终产物是可执行证据和路线决策，不是完整 GUI。

## 4. 需要保持的核心音频语义

Phase 0 应以已经验证的 macOS 行为为音频语义基线，至少评估并尽量验证：

### 4.1 输入范围

- MP3
- M4A
- WAV
- FLAC

底层库理论支持更多格式不代表产品自动承诺更多格式。

### 4.2 变调

- 单位：半音（semitone）
- 整数输入
- 范围：`-24` 至 `+24`
- `0` 表示保持原调

### 4.3 变速

- 用户语义：相对于原速度的变化百分比
- 范围：`-95` 至 `+400`
- 底层换算：

```text
tempo_ratio = 1 + speed_change / 100
```

### 4.4 目标输出

- MP3
- 320 kbps
- 44.1 kHz
- 双声道
- 不修改源文件
- 失败或取消不得留下被误认为成功结果的残缺输出

Phase 0 不要求先实现桌面端全部命名、冲突弹窗、GUI 和 Downloads 产品行为，但所选路线不能从技术上阻止后续实现这些合同。

## 5. 候选技术路线与选择原则

Phase 0 不预先强制唯一实现，但应优先评估以下方向：

1. **FFmpeg 集成 Rubber Band 的单一原生处理栈**：自行从固定源码构建启用 `librubberband` 的 Android FFmpeg，并通过 JNI、稳定封装层或经过审计的调用接口执行一条处理管线。
2. **FFmpeg 与 Rubber Band 分层原生库**：FFmpeg 负责解码和编码，Rubber Band C++ API 负责变调变速，应用通过 JNI 组织 PCM 流或中间文件。
3. **经审计的维护中 Android 封装或构建脚本**：只有在来源、维护状态、许可证、二进制来源、可重复构建和长期风险均明确时才可采用。
4. **其他替代路线**：只有在能够满足核心音频语义、可离线运行、可合法分发并明显降低工程风险时才进入候选。

不得因为某个旧项目曾经支持 Android 就直接采用其预编译二进制。已停止维护、来源不清、只有网盘二进制、无法重建、许可证不完整或需要远程服务的方案不得作为最终 PASS 路线。

路线选择按以下优先级判断：

1. 能在真实 Android 运行环境完成端到端处理。
2. 可从源码重复构建，依赖和版本可以固定。
3. Codex 可通过命令行自动执行和诊断。
4. 可在仓库内形成脚本化流程，不依赖长期 GUI 点击。
5. 许可证和源码分发义务清晰可履行。
6. 后续可以实现取消、进度、错误映射和 Android 生命周期管理。
7. 构建时间、APK 体积、运行性能和维护复杂度合理。
8. 尽量减少自定义 JNI 和脆弱补丁，但不得以不可审计的预编译包换取表面简单。

## 6. Codex 优先的执行模型

Phase 0 默认由 Codex 驱动，流程必须优先选择可脚本化、可检查、可恢复的操作。

### 6.1 优先使用

- `git`
- `gh`
- `curl` 或官方包管理/下载工具
- `sdkmanager`
- `avdmanager`
- `emulator`
- `adb`
- Gradle Wrapper：`./gradlew`
- CMake、Ninja 和 Android NDK 命令行工具
- Shell、Python 或 Kotlin 测试脚本
- 可保存到仓库的环境盘点、构建、安装、运行和验证脚本

### 6.2 Android Studio 的定位

Android Studio 可以安装并作为 SDK、AVD、日志和项目查看工具使用，但正式构建和验证不能只依赖 IDE 内部不可复现的点击操作。Phase 0 必须保留命令行入口，使 Codex 能在不操作 IDE GUI 的情况下完成主要工作。

### 6.3 Computer Use 的边界

Computer Use 只允许作为终极解决方案，且必须满足以下条件之一：

- 官方安装器或系统权限弹窗无法通过命令行继续。
- Android Studio、Device Manager 或系统设置存在一次性 GUI 阻塞，且没有可靠 CLI 替代方案。
- 需要对模拟器中的最终用户可见行为做少量人工式确认。

Computer Use 不得用于：

- 大范围浏览网页、复制代码或下载依赖。
- 长时间操作 Android Studio 完成常规编码和构建。
- 代替 `gradlew`、`adb`、`sdkmanager`、`avdmanager` 或测试脚本。
- 反复点击同一流程而不把步骤脚本化。
- 修改系统安全设置来绕过不明来源或不可信二进制。

每次使用 Computer Use 都必须在 runtime 或报告中记录原因、操作范围、结果以及为什么没有采用 CLI。一次性 GUI 阻塞解决后，应立即返回命令行流程。

### 6.4 教学式说明要求

Codex 在执行过程中应主动解释 Android 开发独有或与桌面端显著不同的技术、路线和术语。说明应与当前实际操作绑定，至少回答：

- 该组件或术语位于哪一层，例如 Gradle/AGP、SDK、NDK、CMake、JNI、ABI、APK、AVD 或 Android 生命周期。
- 当前步骤为什么需要它，它解决的具体问题是什么。
- 它与 Windows/macOS 实现方式有何差异。
- 当前选择的路线有哪些主要替代方案，以及为什么暂不选择其他方案。
- 本次命令、配置或代码产生了什么可验证结果。

说明可以分层、逐步展开，但不得为了照顾初学经验而回避真实实现复杂度、替用户作出未经解释的技术取舍，或把关键原理完全封装成不可理解的黑箱。用户是否熟悉 Android 只影响说明方式，不限制可采用的技术深度和工程方案。

## 7. 环境与安全约束

1. 不执行无关的全局升级、清理或重装。
2. 不在未确认影响范围前修改 shell 配置、Java 默认版本或全局 PATH。
3. 优先使用项目固定版本、Gradle Wrapper 和 Android SDK 的 side-by-side NDK/CMake。
4. 不下载或执行来源不明的 APK、`.so`、原生二进制或构建脚本。
5. 第三方源码必须记录上游地址、版本/commit、许可证和本地补丁。
6. 不提交签名私钥、keystore 密码、token、用户音频或机器专属绝对路径。
7. Phase 0 只使用 debug APK 或等价测试载体，不创建正式发布签名。
8. 不上传 Google Play，不发布 APK，不承诺最低 Android 版本。
9. 不把模拟器中的 root、特殊调试权限或主机挂载当作普通 Android 可用性证据。
10. 不能要求最终用户预装 Termux、FFmpeg、Rubber Band、Python 或其他外部运行环境。

## 8. Android 模拟环境要求

Phase 0 应优先建立官方 Android Emulator，并尽量通过 CLI 管理：

- 使用与 Apple Silicon 兼容的 ARM 系统镜像。
- 创建可重复描述的 AVD 配置。
- 记录 API level、system image、设备模板、ABI、磁盘和启动参数。
- 使用 `adb` 安装 APK、推送测试文件、拉取结果和读取日志。
- 能通过命令行冷启动或无快照启动，以验证环境不依赖一次性缓存状态。

模拟器用于证明 Android 平台可运行性，但 Phase 0 的 PASS 路线还必须说明后续真机验证计划。若当前没有真机，可以把真机性能和厂商后台行为列为下一阶段门槛，但不得把模拟器性能直接外推为真机结论。

## 9. Phase 0 实质验收标准

只有以下全部满足，Phase 0 才能报告 `PASS`：

### 9.1 路线决策

- 至少比较两条候选路线，说明淘汰原因。
- 选定一条主路线，并给出依赖图、调用链和后续应用架构位置。
- 固定关键工具和依赖的版本或 commit。
- 明确全部直接与传递许可证及分发义务。
- 不依赖已归档项目提供的不可重建预编译二进制。

### 9.2 可重复构建

- 从当前仓库和已记录的官方/上游源码可以重复构建。
- 构建过程有仓库内脚本或单一明确入口。
- 至少生成 `arm64-v8a` 可运行产物。
- APK 或测试载体中包含运行所需的原生依赖，不要求模拟器预装外部工具。
- 在清理可再生构建目录后重新构建仍成功。

### 9.3 Android 运行证据

- 官方 Android Emulator 可由记录的步骤启动。
- 最小 Android 应用或测试载体可通过 `adb install` 安装并启动。
- 原生库实际由 Android 进程加载，不是只在 macOS 主机执行。
- Android 环境中完成至少一次真实端到端处理：读取输入音频、执行非零变调和非零变速、生成 MP3 输出。
- 代表性参数固定为 `pitch = +3`、`speed_change = -20`，除非底层调查证明需要等价测试参数并明确说明。
- 输出可由 Android 播放或由拉回主机后的 FFprobe 验证为可读 MP3、44.1 kHz、双声道、目标 320 kbps 编码设置。
- 输入源文件哈希保持不变。
- 失败不会把残缺文件报告为成功。

### 9.4 格式能力

主路线必须在 Android 环境实际验证：

- MP3 输入
- M4A 输入
- WAV 输入
- FLAC 输入

四种格式都必须进入同一主路线并生成有效 MP3。若只有部分格式通过，最终状态只能是 `PARTIAL`，不能以“底层理论支持”替代实测。

### 9.5 生命周期可实现性

Phase 0 不要求完成正式后台任务框架，但必须：

- 证明处理可以从 Android 应用线程之外运行，或给出已验证的非阻塞调用结构。
- 证明存在可用的取消机制；至少在长任务测试中触发取消并确认原生处理停止、Android 进程未崩溃、残缺输出被清理。
- 说明进度、错误和取消如何跨越 Kotlin/原生边界。
- 说明后续使用前台服务、WorkManager、协程或其他生命周期组件的候选方式，不把具体选择伪装成已完成结论。

### 9.6 证据与报告

至少创建并维护：

```text
mobile/android/phase0/environment_report.md
mobile/android/phase0/route_evaluation.md
mobile/android/phase0/feasibility_report.md
```

报告必须包含：

- 主机、SDK、JDK、Gradle、AGP、NDK、CMake、Emulator、system image 和 ABI 的实际版本。
- 依赖来源、版本、commit、许可证、构建参数和补丁。
- 完整构建、安装、运行和验证命令。
- APK/原生库架构和大小。
- 四格式测试结果、FFprobe 结果、哈希和取消证据。
- 已知限制、失败实验和淘汰路线。
- 最终 `PASS`、`PARTIAL`、`BLOCKED` 或 `FAIL` 结论。

## 10. 状态定义

### PASS

已经选定一条可维护、可重复构建、许可证清晰、Codex 可操作的 Android 路线，并在官方 Android 环境完成四格式端到端处理和最小取消验证，可以进入正式行为合同和应用架构阶段。

### PARTIAL

核心依赖或部分格式可以运行，但主路线尚未完成全部四格式、取消、重复构建或许可证门槛。必须继续 Phase 0，不得开始完整 GUI。

### BLOCKED

存在具体外部阻塞，例如必要工具无法安装、上游源码无法取得、关键依赖与当前 Android 工具链不兼容，且短期内没有合理替代路线。必须记录阻塞证据和解除条件。

### FAIL

经过合理候选比较后，没有找到满足离线处理、核心音频语义、合法分发和可维护性要求的路线。不得通过降低产品合同或采用不可信二进制伪造通过。

## 11. Phase 0 非目标

本阶段不要求：

- 完整 Jetpack Compose GUI
- 最终产品视觉设计
- 完整 Storage Access Framework 行为合同
- 正式后台服务和通知体验
- 多任务队列
- Play Store 上架
- release keystore 和正式签名
- AAB
- `x86_64`、`armeabi-v7a` 或多 ABI 发布
- 最低 Android 版本承诺
- 全面性能、耗电和发热优化
- 厂商 ROM 兼容性
- 最终用户 APK 发布

这些工作只能在主路线通过 Phase 0 后进入正式 Android 设计阶段。

## 12. 仓库与文档原则

- `docs/android_native_feasibility_static.md` 保存稳定合同，不记录临时实验状态。
- `docs/android_native_feasibility_runtime.md` 保存完成记录、当前 active step、具体执行约束和 next steps。
- 探索代码、最小 Android 工程和脚本放在 `mobile/android/phase0/` 或由后续明确架构决定的相邻路径。
- 可再生的 SDK、NDK、Gradle cache、AVD、构建目录、APK 和大型第三方源码归档原则上不提交。
- 必须提交的第三方补丁、构建脚本、许可证清单和小型测试生成器应进入版本控制。
- 运行时文档应采用追加式 done 记录；已经完成的历史事实不得为了简化文档而删除或改写。