# done

- 2026-08-04：macOS 复刻已完成源码 MVP、PyInstaller 独立应用、许可证与对应源码打包、非开发 Apple Silicon Mac 人工验收，并将 `v0.1.0-alpha.3` 公开为 GitHub Pre-release。
- 2026-08-04：已清理从未公开且被取代的 alpha.1 与 alpha.2 Draft Release，保留三个历史 annotated tags；macOS 当前没有阻塞 Android 调查的已知缺陷。
- 2026-08-04：用户确认进入 Android 任务，但指出三个主要不确定性：没有 Android 开发经验；尚未由本项目证明 FFmpeg、Rubber Band 及其传递依赖能够在 Android 运行；尚未建立可由当前 Apple Silicon Mac 操作的 Android 模拟环境。
- 2026-08-04：决定不直接开发完整 Android GUI，先执行独立 Phase 0，以实际 Android 运行证据选择一条可实现、可维护、可合法分发且 Codex 方便操作的原生音频路线。
- 2026-08-04：创建 `docs/android_native_feasibility_static.md`，固化 Phase 0 目标、候选方向、Codex 优先原则、Computer Use 边界、Android Emulator 要求和实质验收标准。

# active step — Android Phase 0：证明一条可实现的原生音频路线

## 1. 本阶段目标

本阶段只负责回答并以运行证据证明：

> AudioShifter 应使用哪一组 Android 工具链、依赖、构建方法和调用结构，才能在 Android 系统内完成 MP3、M4A、WAV、FLAC 输入的变调、变速和 320 kbps MP3 输出，并为后续完整应用保留取消、进度、错误和生命周期控制能力？

最终必须选定一条主路线，而不是只列出候选方案。路线必须由当前仓库内的代码、脚本和报告复现，并在官方 Android Emulator 中真实运行。

本阶段不开发正式 GUI，不发布 APK，不承诺最低 Android 版本，不处理 Play Store。

## 2. 开始前的 Git 与文档门槛

Codex 开始任何安装、下载或源码修改前必须：

1. 进入：

   ```text
   /Users/smterpro/Workspace/Tools/AudioShifter
   ```

2. 执行并记录：

   ```bash
   git status --short
   git branch -vv
   git fetch origin --tags
   git rev-list --left-right --count origin/main...HEAD
   ```

3. 确认工作区干净、当前分支为 `main`、跟踪 `origin/main`、差异为 `0 0`。
4. 完整读取：

   ```text
   docs/android_native_feasibility_static.md
   docs/android_native_feasibility_runtime.md
   docs/macos_rebuild_static.md
   docs/macos_rebuild_runtime.md
   macos/design/behavior_spec.md
   LICENSING.md
   TRADEMARKS.md
   LICENSE
   ```

5. 检查仓库现有 `mobile/`、`.gitignore`、根 README 和构建约束。
6. 不执行 `reset --hard`、`clean -fd`、自动 stash、force push 或历史重写。
7. 不修改或执行 `windows/` 历史内容；除必要文档链接外，不修改已经发布的 macOS 实现和 release tag。

若工作区不干净或本地领先/落后无法通过普通 fast-forward 解决，停止并报告，不自行覆盖用户修改。

## 3. 第一关：开发主机与 Android 工具链盘点

先盘点，不先安装。

必须检查并记录：

- macOS 版本与主机架构
- Xcode Command Line Tools
- Java/JDK 版本与来源
- Android Studio 是否已安装
- `ANDROID_HOME`、`ANDROID_SDK_ROOT` 和实际 SDK 路径
- `sdkmanager`
- `avdmanager`
- `adb`
- `emulator`
- 已安装 SDK platforms、build-tools、platform-tools
- 已安装 NDK side-by-side 版本
- 已安装 CMake、Ninja、LLDB
- Gradle 与可用 Gradle Wrapper
- 磁盘空间
- 已存在的 AVD 和 system image
- Homebrew 中可能相关的工具，但不得因盘点执行全局升级

创建：

```text
mobile/android/phase0/environment_report.md
```

报告必须区分：

```text
already installed
missing
usable as-is
requires project-local pinning
requires user-approved installation
```

工具链版本优先由正式 Android 项目的 Gradle Wrapper、AGP、SDK、NDK side-by-side 和 CMake配置固定，不依赖开发机全局默认碰巧正确。

### 3.1 安装策略

只有完成盘点后才能安装缺失组件。

优先顺序：

1. 官方 Android Studio / Android SDK 已有安装。
2. `sdkmanager` 安装项目所需的明确版本。
3. Android Studio 官方安装器只用于取得 SDK/IDE 基础设施。
4. 不使用来源不明的整合包。

不得执行无关的 Android Studio、Homebrew、JDK 或系统全局升级。

安装前如果需要系统管理员密码、许可确认或明显影响现有开发环境，先停止并向用户说明准确操作。

## 4. 第二关：候选路线调查与比较

创建：

```text
mobile/android/phase0/route_evaluation.md
```

至少调查并比较两条路线，优先顺序如下：

### 路线 A：FFmpeg + librubberband 单一原生栈

目标：自行从固定上游源码为 Android 构建 FFmpeg，并启用 Rubber Band 集成，使解码、变调变速和编码尽可能由一条原生处理管线完成。

需要确认：

- 当前 FFmpeg 与 Rubber Band 上游版本或 commit
- Android NDK 兼容性
- Rubber Band 的 FFT、samplerate、sndfile 或其他传递依赖
- FFmpeg `rubberband` filter 的实际构建条件
- MP3 编码器选择及许可证影响
- JNI 或稳定封装入口
- 取消与进度能力
- APK/`.so` 体积

### 路线 B：FFmpeg 与 Rubber Band 分层原生库

目标：FFmpeg 负责解码/编码，Rubber Band C++ API 负责 PCM 变调变速，由 JNI 组织中间 WAV、PCM buffer 或流式处理。

需要确认：

- 是否需要 libsndfile
- 是否使用中间文件或流式 buffer
- JNI 边界复杂度
- 内存占用
- 取消、进度和错误映射
- 与 Android 生命周期的适配性

### 可选路线 C：维护中的第三方 Android 封装

只有在以下全部明确时才可进入最终比较：

- 项目仍维护或至少有可审计的活跃 fork
- 提供完整源码和可重复构建方法
- 不依赖无法取得的预编译二进制
- FFmpeg/Rubber Band/MP3 编码的许可证和源码义务清楚
- 支持目标 ABI 和当前 Android 工具链
- Codex 可以通过 CLI 使用

FFmpegKit、MobileFFmpeg 或其他归档项目可以作为历史架构和构建脚本参考，但不得仅因使用方便直接采用旧预编译包作为 PASS 路线。

### 4.1 调查证据要求

- 技术结论优先引用 Android、FFmpeg、Rubber Band、Gradle、NDK、CMake 和依赖项目的官方文档或上游源码。
- 固定每个候选的上游 URL、版本/commit、许可证、维护状态、构建入口和已知 Android 证据。
- 不把博客、论坛或模型推测作为唯一依据。
- 对未知项明确写 `UNVERIFIED`，随后通过构建或运行实验验证。

### 4.2 选择标准

按以下顺序选择主路线：

1. Android 端到端真实运行成功。
2. 四种输入格式均通过同一主路线。
3. 可从源码重建。
4. 许可证与对应源码分发可履行。
5. Codex 能通过脚本完成构建、安装、运行、下载结果和验证。
6. 可实现取消、进度和错误边界。
7. 不要求最终用户安装外部工具。
8. 维护复杂度、APK 体积和性能合理。

不得为了完成 Phase 0 而预先宣告路线 A 或 B 胜出。

## 5. 第三关：建立命令行优先的最小 Android 工程

在路线调查达到可以开始实验的程度后，创建最小工程，建议路径：

```text
mobile/android/phase0/prototype/
```

工程至少包含：

- Gradle Wrapper
- Kotlin Android 应用或 instrumented test 载体
- 固定 compile SDK / target SDK / min SDK 实验值
- 固定 AGP、Kotlin、NDK 和 CMake 版本
- `arm64-v8a` ABI filter
- 最小 JNI/C++ 加载验证
- 仓库内构建脚本
- 仓库内安装与运行脚本
- 日志和结果拉取脚本
- 测试音频动态生成脚本，或许可证允许且足够小的受控测试资源

正式入口必须能够通过 CLI 执行，例如：

```bash
./gradlew assembleDebug
adb install -r <debug-apk>
adb shell am start ...
```

不允许只有“在 Android Studio 点击 Run”才能构建或执行。

### 5.1 最小 JNI 门槛

在集成 FFmpeg/Rubber Band 前先验证：

1. Android 应用可以安装和启动。
2. `arm64-v8a` 原生 `.so` 被实际打入 APK。
3. Kotlin 能调用一个最小 JNI 函数并收到确定返回值。
4. `adb logcat` 可以看到受控日志。
5. 清理并重新构建后仍通过。

该门槛失败时不得继续堆叠大型原生依赖。

## 6. 第四关：建立官方 Android Emulator

优先通过 `sdkmanager`、`avdmanager`、`emulator` 和 `adb` 完成。

必须：

1. 选择 Apple Silicon 可用的 ARM system image。
2. 记录 API level、system image package、设备模板、ABI 和 AVD 名称。
3. 创建可重复的 AVD 创建命令或脚本。
4. 能使用 CLI 启动模拟器。
5. 能通过 `adb wait-for-device` 等待启动完成。
6. 能安装 debug APK。
7. 能推送输入文件、拉取输出文件、读取 logcat。
8. 至少进行一次冷启动或关闭快照后的复验。

不得依赖 root、主机目录特殊挂载或模拟器专属绕过方式完成核心处理。

### 6.1 Computer Use 兜底

仅当 CLI 无法解决以下一次性阻塞时允许使用 Computer Use：

- Android Studio 首次启动向导
- SDK license 或系统权限弹窗
- Device Manager 中无法通过 CLI 复现的初次设置
- 模拟器内少量最终用户可见行为确认

使用前先记录：

```text
blocker
CLI attempts
why CLI is insufficient
exact GUI action required
```

使用后记录结果并立即回到 CLI。不得让 Computer Use 承担项目创建、常规编码、依赖下载、反复构建或大范围网页研究。

## 7. 第五关：构建并加载候选原生依赖

对每条进入实测的候选路线：

1. 固定上游版本/commit。
2. 记录源码校验值或 Git commit。
3. 使用 Android NDK 为 `arm64-v8a` 构建。
4. 保存可重复构建脚本、CMake/toolchain 参数和必要补丁。
5. 检查生成 `.so` 的架构、动态依赖和未解析符号。
6. 检查 APK 中的 native libraries。
7. 在 Android 进程中实际加载。
8. 不以 macOS 主机侧二进制执行代替 Android 证据。

对于失败路线，保留足以诊断的日志摘要、退出码、版本和失败阶段；不要把大型完整构建目录或上游源码副本直接提交。

## 8. 第六关：端到端音频证明

主路线必须在 Android 环境内完成：

```text
输入文件
→ 解码/标准化
→ Rubber Band 或等价高质量变调变速
→ MP3 编码
→ Android 可访问的输出文件
```

### 8.1 代表性处理

固定代表性参数：

```text
pitch = +3 semitones
speed_change = -20
calculated tempo_ratio = 0.8
```

若所选 API 使用不同参数表达，必须在报告中给出精确换算。

### 8.2 四格式门槛

在 Android 中分别处理：

- MP3
- M4A
- WAV
- FLAC

所有输入应由动态生成或可追踪的受控源构造，输出均为有效 MP3。

每项记录：

- 输入路径与大小
- 输入 SHA-256
- 参数
- 开始与结束时间
- 原生路线和实际命令/API
- 返回状态
- 输出路径与大小
- 输出 SHA-256
- FFprobe codec、sample rate、channels、bit rate 和 duration
- 输入处理后 SHA-256 是否保持不变

目标输出：

```text
MP3
44.1 kHz
stereo
320 kbps encoding configuration
```

FFprobe 报告的瞬时或估算码率若因容器/短音频出现差异，应记录实际编码参数和探测结果，不得伪造严格相等。

### 8.3 Android 内运行证据

必须能证明处理发生在 Android 进程或 Android 原生执行环境中，例如：

- 应用 PID 与 logcat
- JNI/native 日志
- APK 内库清单
- Android 输出文件时间与路径
- 从设备拉回的结果

只在主机运行交叉编译产物不算通过。

## 9. 第七关：失败、取消与非阻塞证明

Phase 0 至少实现一个最小任务控制接口，并验证：

1. 音频处理不在 Android 主线程同步阻塞。
2. Kotlin/Java 层能收到成功和失败状态。
3. 传入损坏文件或不支持内容时明确失败。
4. 长任务中可以触发取消。
5. 取消后原生处理停止，应用进程不崩溃。
6. 取消后残缺目标文件被删除或明确隔离，不能被报告为成功。
7. 临时资源得到清理。
8. 后续正式应用可以从该接口增加进度回调、前台服务或其他生命周期管理。

如果主路线只能进行不可取消的长时间阻塞 JNI 调用，不能报告 PASS，必须继续调整接口或选择其他路线。

## 10. 第八关：许可证与分发可行性

创建或更新 Phase 0 报告中的许可证章节，至少包含：

- FFmpeg 配置与实际启用组件
- Rubber Band 版本和许可证
- MP3 编码器
- FFT、samplerate、sndfile 及其他传递依赖
- 每个依赖的上游 URL、版本/commit、许可证文件路径
- APK 中实际包含的库
- 是否触发 GPL、LGPL 或其他源码提供义务
- 后续 APK 发布需要提供的 notices、许可证文本、对应源码、构建脚本和补丁
- 与根 `LICENSE`、`LICENSING.md`、`TRADEMARKS.md` 的一致性

许可证不清楚、依赖来源无法追踪或无法满足源码分发要求时，路线不得 PASS。

## 11. 第九关：可重复性和 Codex 操作性复验

在主路线首次成功后，必须进行一次从可再生状态的复验：

1. 删除项目内可再生 build 输出，不删除用户环境或全局缓存。
2. 使用仓库脚本重新构建。
3. 重新安装 debug APK。
4. 重启或冷启动模拟器。
5. 重新执行至少一个压缩输入和一个无损输入。
6. 拉回输出并重新验证。

最终路线必须提供少量、稳定、顺序明确的命令入口。若每次都需要在 Android Studio 中手工修改路径、点击多个面板或修复随机状态，路线只能为 PARTIAL。

## 12. 必须生成的 Phase 0 报告

至少维护：

```text
mobile/android/phase0/environment_report.md
mobile/android/phase0/route_evaluation.md
mobile/android/phase0/feasibility_report.md
```

`feasibility_report.md` 必须给出：

- 最终状态：PASS / PARTIAL / BLOCKED / FAIL
- 选定主路线
- 被淘汰路线及原因
- 工具链版本
- 上游依赖版本/commit
- 构建入口
- APK 与 `.so` 架构和大小
- 模拟器配置
- 四格式结果
- 代表性 FFprobe
- 取消和清理证据
- 许可证结论
- Codex 能否在无 IDE GUI 主流程下复现
- Computer Use 使用次数、原因和范围；没有使用时也明确记录
- 已知限制
- 真机验证计划
- 是否允许进入正式 Android 行为合同与架构设计

## 13. 提交与状态更新规则

建议按可独立回滚和审阅的里程碑提交，例如：

```text
docs: record Android toolchain inventory
docs: compare Android audio pipeline routes
chore: add Android native prototype scaffold
build: integrate Android native audio dependencies
test: verify Android audio pipeline on emulator
docs: record Android native feasibility result
```

要求：

- 每个提交前执行对应构建或文档检查。
- 不提交 SDK、NDK、AVD、Gradle cache、完整上游源码镜像、大型 build 目录或用户音频。
- 不创建 release、不打 tag、不上传 APK。
- 每完成一个可靠事实，在本文件 `# done` 追加日期和证据；不得删除历史 done。
- active step 只保留当前仍在执行的详细规格；阶段完成后可以把整段重命名为 completed step specification，并建立新的 active step。
- 每次推送后确认 `origin/main...HEAD` 为 `0 0`，工作区干净。

## 14. Phase 0 结束判定

只有 `docs/android_native_feasibility_static.md` 中全部 PASS 门槛满足，才可以写：

```text
PASS — one reproducible Android-native AudioShifter route proven end to end
```

以下情况只能写 `PARTIAL`：

- 只完成 JNI hello world。
- 只在主机编译成功。
- 只有 FFmpeg 或只有 Rubber Band 单独运行。
- 只有 WAV 通过，压缩格式未经 Android 实测。
- 依赖预编译二进制但无法从源码重建。
- 只能通过 Android Studio 大量手工点击运行。
- 无法取消长任务。
- 许可证或对应源码义务未确认。

## 15. 本轮明确禁止事项

- 不直接开发完整 Android GUI。
- 不复制 Tkinter 或桌面路径模型。
- 不恢复激活机制。
- 不使用远程音频处理服务。
- 不使用来源不明的预编译 FFmpeg/Rubber Band APK、AAR 或 `.so`。
- 不把归档项目当作维护中依赖而不说明风险。
- 不用 root 模拟器能力作为普通 Android 路线前提。
- 不大范围使用 Computer Use。
- 不修改 macOS release 资产、tag 或历史 Windows 内容。
- 不为了宣告 PASS 降低四格式、Android 实际运行、取消、重建和许可证门槛。

# next steps

- Phase 0 PASS 后，建立正式 Android 行为合同，确定 Storage Access Framework、输出位置、命名冲突、分享、错误提示、后台处理、通知、返回键和应用被系统回收时的语义。
- 建立正式 Android 架构规划，确定 Jetpack Compose、协程、前台服务/WorkManager、JNI/native 模块、依赖打包、日志和测试边界。
- 建立 Android 验证矩阵，再开始完整 MVP；不得直接把 Phase 0 prototype 当作产品代码扩张而不先整理模块和合同。
- 在 Emulator MVP 通过后使用至少一台真实 Android 手机验证安装、处理性能、内存、发热、耗电、文件访问和厂商后台限制。
- 正式 APK/AAB、release signing、GitHub Release 或 Play Store 分发必须作为后续独立阶段处理。
