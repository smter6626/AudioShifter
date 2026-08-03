# AudioShifter macOS 架构规划

> 文档定位：本文件是 macOS 第一阶段的**实现前架构合同**，用于规定模块职责、依赖方向、数据流、状态流和可测试边界。
>
> 本文件不包含正式业务代码，不替代 `behavior_spec.md` 中的用户可见行为合同，也不记录执行进度。测试覆盖关系见 `verification_matrix.md`，长期项目原则见 `docs/macos_rebuild_static.md`。
>
> 架构优先级：行为合同正确性 > 可测试性 > 错误可诊断性 > 打包可行性 > 代码简洁性。不得为了减少文件数量而重新把 GUI、路径、子进程和业务状态集中到单个脚本。

## 1. 架构目标

第一阶段架构需要满足：

1. 用户界面与音频处理逻辑分离。
2. 参数校验、文件命名、输出冲突、临时目录和错误分类可以脱离 GUI 独立测试。
3. FFmpeg 与 Rubber Band 调用通过适配层封装，不在 GUI 中拼接命令。
4. 外部进程支持取消、超时、stderr 捕获和安全终止。
5. 单任务约束在应用控制层统一执行。
6. Tkinter 控件只在主线程更新。
7. 开发环境和 PyInstaller 打包环境可以使用不同的依赖解析策略，但上层接口一致。
8. Windows 历史源码只作为行为参考，不复制激活模块、固定临时路径和线程违规设计。

## 2. 非目标

本阶段架构规划不包含：

- 正式 GUI 布局和视觉设计
- PyInstaller `.spec` 实现
- 签名、公证或安装器
- Intel Mac 或通用二进制
- Android 代码复用设计
- 云端处理、账户、遥测或自动更新
- 音频元数据保留
- 多任务队列或并发批处理

## 3. 建议目录结构

正式代码阶段建议采用：

```text
macos/
├── src/
│   └── audioshifter/
│       ├── __init__.py
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
│   ├── integration/
│   └── fixtures/
└── design/
    ├── behavior_spec.md
    ├── architecture_plan.md
    └── verification_matrix.md
```

目录只是模块边界建议；后续可以根据实现证据微调文件数量，但不得破坏职责分离和依赖方向。

## 4. 依赖方向

依赖方向固定为：

```text
Tkinter GUI
    ↓
Application Controller
    ↓
Processing Pipeline
    ↓
Validation / Naming / Workspace / Dependency Resolution
    ↓
FFmpeg Adapter / Rubber Band Adapter
    ↓
Process Runner
    ↓
External binaries
```

横向模块不得反向依赖 GUI。

禁止的依赖包括：

- `validation.py` 导入 Tkinter
- `naming.py` 直接启动 FFmpeg
- `process_runner.py` 弹出 messagebox
- `pipeline.py` 直接修改控件
- `gui.py` 自行删除临时目录
- `gui.py` 自行决定输出冲突后缀
- `ffmpeg_adapter.py` 读取输入框文本

## 5. 数据模型

### 5.1 ProcessingRequest

`models.py` 应定义不可变的处理请求，至少包含：

| 字段 | 类型 | 含义 |
|---|---|---|
| `input_path` | `Path` | 已规范化的输入文件路径 |
| `pitch_semitones` | `int` | `-24` 至 `+24` |
| `speed_change_percent` | `Decimal` 或等价精确十进制类型 | `-95` 至 `+400` |
| `downloads_path` | `Path` | 已解析的下载目录 |

请求一旦提交给处理层，不允许 GUI 在处理中修改。

速度值优先使用十进制表示，而不是直接依赖二进制浮点字符串，以确保：

- 文件命名稳定
- 尾随零规范化稳定
- 边界比较明确
- `+12.5` 不被格式化为非预期长小数

传给 Rubber Band 时再转换为稳定的小数字符串。

### 5.2 ProcessingResult

处理成功结果至少包含：

| 字段 | 含义 |
|---|---|
| `output_path` | 最终 MP3 路径 |
| `input_path` | 源文件路径 |
| `pitch_semitones` | 实际变调值 |
| `speed_change_percent` | 实际速度变化值 |
| `tempo_ratio` | 实际 Rubber Band tempo multiplier |
| `warnings` | 例如临时目录清理失败 |
| `diagnostics` | 不直接展示给普通用户的摘要 |

### 5.3 ProcessingStage

建议使用枚举表示稳定阶段：

```text
IDLE
VALIDATING
ALLOCATING_OUTPUT
PREPARING_WORKSPACE
DECODING
PROCESSING
ENCODING
VERIFYING_OUTPUT
CLEANING_UP
SUCCEEDED
CANCELLING
CANCELLED
FAILED
```

状态变化通过事件传给控制层，由控制层安排 GUI 主线程更新。

## 6. 结构化错误模型

### 6.1 AppError

`errors.py` 应定义统一的结构化应用错误，至少包含：

| 字段 | 含义 |
|---|---|
| `code` | `behavior_spec.md` 中的稳定错误码 |
| `user_message` | 中文、可操作提示 |
| `stage` | 发生阶段 |
| `details` | 内部诊断字典 |
| `cause` | 原始异常，可选 |
| `recoverable` | 用户修正输入后是否可重试 |

### 6.2 错误映射

底层错误必须在模块边界映射：

- 文件系统异常 → 输入、权限、磁盘或输出错误
- `FileNotFoundError` 启动外部程序 → `DEPENDENCY_MISSING`
- `PermissionError` 启动程序 → `DEPENDENCY_NOT_EXECUTABLE`
- FFmpeg 解码非零返回 → `DECODE_FAILED` 或 `INVALID_INPUT_MEDIA`
- Rubber Band 非零返回 → `PROCESS_FAILED`
- FFmpeg 编码非零返回 → `ENCODE_FAILED`
- 用户取消 → `CANCELLED`

GUI 不解析 stderr 来决定错误类型。

## 7. validation.py

### 7.1 职责

负责纯校验和规范化：

- 输入路径存在性、文件类型、可读性、非零大小
- 扩展名白名单
- 变调字符串解析
- 变速字符串解析
- 参数范围
- 下载目录存在性、目录属性和写入能力预检查
- `tempo_ratio` 计算

### 7.2 接口方向

建议提供无 GUI 的纯函数：

```text
parse_pitch(text) -> int
parse_speed_change(text) -> Decimal
validate_input_path(path) -> Path
validate_downloads_path(path) -> Path
compute_tempo_ratio(speed_change) -> Decimal
build_request(...) -> ProcessingRequest
```

### 7.3 约束

- 不弹窗。
- 不运行外部程序。
- 不创建输出文件。
- 不依赖全局 Tkinter 状态。
- 对同一输入始终产生同一结果或同一错误码。

## 8. naming.py

### 8.1 职责

负责：

- 原文件 stem 提取
- 半音字符串规范化
- 速度字符串规范化
- 基础输出文件名生成
- 自动递增候选生成
- 输出路径冲突分配

### 8.2 稳定规则

基础名称：

```text
<stem><signed_pitch><signed_speed>%.mp3
```

冲突后缀：

```text
<base>_2.mp3
<base>_3.mp3
...
```

### 8.3 输出路径分配接口

建议区分：

```text
build_base_filename(request) -> str
find_available_output(downloads_path, base_filename) -> OutputAllocation
revalidate_output_allocation(allocation) -> OutputAllocation
```

`OutputAllocation` 至少包含：

- 基础目标路径
- 实际目标路径
- 是否发生冲突
- 递增序号
- 是否需要 GUI 提示

### 8.4 竞态处理

单应用禁止并发不能消除外部竞态。编码前必须再次校验实际路径。

实现可选择：

1. 使用排他创建占位文件进行保留；或
2. 编码前再次分配，并让 FFmpeg 使用不覆盖模式。

无论采用哪种方式，行为结果必须满足 `NAME-003` 至 `NAME-006`。

## 9. dependencies.py

### 9.1 职责

负责解析和验证：

- FFmpeg
- FFprobe
- Rubber Band

### 9.2 双模式解析

开发环境：

- 可以解析 Homebrew 已验证路径。
- 可以通过配置或明确的可执行路径启动。

打包环境：

- 从应用资源目录解析内置二进制和动态库。
- 不要求最终用户安装 Homebrew或配置 PATH。

两种模式向上层返回相同的数据结构：

```text
ResolvedDependencies
├── ffmpeg_path
├── ffprobe_path
└── rubberband_path
```

### 9.3 验证

至少检查：

- 路径存在
- 是普通文件或可解析链接
- 具有执行权限
- 启动版本命令成功

版本和架构检查在开发/打包验证中执行，不要求每次用户处理都完整重复。

## 10. workspace.py

### 10.1 职责

负责每个任务的独立临时工作区：

```text
<System Temp>/AudioShifter-<random>/
├── decoded.wav
└── processed.wav
```

### 10.2 生命周期

建议通过上下文管理器或明确的生命周期对象控制：

```text
create
→ expose paths
→ cleanup on success/failure/cancel
```

### 10.3 清理语义

- 清理只作用于当前对象创建的目录。
- 删除前验证路径属于系统临时根目录和当前任务。
- 不使用空变量拼接删除命令。
- 不通过 Shell 执行递归删除。
- 清理失败返回 warning，而不是覆盖已成功结果。

## 11. process_runner.py

### 11.1 职责

统一执行外部程序：

- 参数数组
- `shell=False`
- 捕获 stdout/stderr
- 返回码
- 进程句柄
- 取消
- 超时基础设施
- 安全终止

### 11.2 ProcessResult

至少包含：

| 字段 | 含义 |
|---|---|
| `args` | 实际参数数组 |
| `returncode` | 返回码 |
| `stdout` | 解码后的输出摘要 |
| `stderr` | 解码后的错误摘要 |
| `duration` | 执行耗时 |
| `cancelled` | 是否因用户取消终止 |

### 11.3 取消策略

控制层发出取消后：

1. 设置取消令牌。
2. 当前进程收到温和终止请求。
3. 在有限等待后仍未结束时执行强制终止。
4. 等待进程回收，避免僵尸进程。
5. 不启动后续阶段。

具体等待秒数在实现测试阶段确定。

### 11.4 输出解码

stderr 可能包含非 UTF-8 字节。实现应使用明确编码和替换策略，确保诊断本身不会导致新的异常。

## 12. ffmpeg_adapter.py

### 12.1 解码接口

职责：构造并执行输入标准化命令。

目标规格固定为：

- PCM signed 16-bit little-endian
- 44.1 kHz
- 双声道 WAV

适配器接收已验证路径和工作区，不读取 GUI 输入。

### 12.2 编码接口

职责：构造并执行 MP3 编码命令。

输出规格固定为：

- `libmp3lame`
- 320 kbps
- 44.1 kHz
- 双声道

不得使用静默覆盖最终输出的行为。

### 12.3 媒体验证接口

通过 FFprobe 验证：

- 文件存在和非空
- 编码类型
- 采样率
- 声道
- 时长

## 13. rubberband_adapter.py

### 13.1 职责

构造并执行 Rubber Band 处理命令，传入：

- 整数半音
- `tempo_ratio`
- R3/finer
- formant preservation
- 输入工作 WAV
- 输出工作 WAV

### 13.2 参数来源

所有参数必须来自已验证、不可变的 `ProcessingRequest`，不得在适配器内部重新解析用户文本。

### 13.3 失败映射

Rubber Band 非零返回统一映射为 `PROCESS_FAILED`，内部保留命令、返回码和 stderr。

## 14. pipeline.py

### 14.1 职责

编排完整状态机：

```text
validate request
→ resolve dependencies
→ allocate output
→ prepare workspace
→ decode
→ process
→ revalidate output path
→ encode
→ verify output
→ cleanup
→ return result
```

### 14.2 原子成功语义

只有在最终 MP3 通过验证后才进入 `SUCCEEDED`。

失败或取消时：

- 删除残缺最终文件。
- 清理临时工作区。
- 保留源文件。
- 返回结构化错误或取消结果。

### 14.3 冲突提示边界

管线负责识别冲突并返回 `OutputAllocation` 信息；是否弹窗由控制层和 GUI 处理。

为了在用户确认后继续，可将流程分成：

1. 预检和输出分配；
2. 若冲突，等待 GUI 确认；
3. 正式执行。

GUI 不自行重算文件名。

## 15. controller.py

### 15.1 职责

控制层连接 GUI 和管线：

- 接收用户提交
- 防止并发任务
- 调用纯校验
- 处理输出冲突提示流程
- 启动后台任务
- 接收状态事件
- 把 UI 更新调度回 Tkinter 主线程
- 处理取消
- 处理窗口关闭请求

### 15.2 单任务锁

控制层维护唯一活动任务引用。

- 活动任务存在时拒绝第二次启动。
- 任务完成、失败或取消后释放。
- GUI 按钮状态不是唯一保护；控制层本身也必须拒绝并发。

### 15.3 Tkinter 主线程

后台线程不得直接操作控件。控制层通过：

- `root.after(...)`
- 线程安全队列
- 等价的主线程调度机制

传递状态和结果。

## 16. gui.py

### 16.1 职责

GUI 只负责：

- 选择输入文件
- 收集变调和变速文本
- 展示范围和单位说明
- 提交请求
- 显示阶段状态
- 显示冲突提示
- 显示成功路径
- 显示结构化用户错误
- 提供取消
- 处理关闭确认

### 16.2 禁止职责

GUI 不负责：

- 拼接 FFmpeg/Rubber Band 命令
- 计算 tempo ratio
- 生成输出文件名
- 判断递增后缀
- 创建或删除临时文件
- 解析底层 stderr
- 直接处理许可证或依赖打包

## 17. 线程和事件模型

建议事件类型：

```text
StageChanged(stage)
ProgressMessage(text)
OutputConflict(base_path, allocated_path)
Succeeded(result)
Cancelled()
Failed(app_error)
Warning(message, details)
```

事件从工作线程产生，经线程安全队列送至主线程。

第一阶段不要求精确百分比进度。若 FFmpeg/Rubber Band 未提供稳定进度，不得用虚假百分比误导用户；阶段状态足以满足合同。

## 18. 输出冲突交互流程

建议固定流程：

1. 校验输入和参数。
2. 解析 `~/Downloads/`。
3. 生成基础文件名。
4. 查找第一个安全递增名称。
5. 若基础名称不存在，直接继续。
6. 若基础名称已存在，控制层要求 GUI 弹出信息提示。
7. 用户确认后继续使用已分配名称。
8. 编码前再次确认路径安全。
9. 若外部竞态产生新冲突，重新分配并再次提示，或以 `OUTPUT_NAME_CONFLICT` 终止。

永不提供“覆盖已有文件”选项。

## 19. 下载目录错误流程

`~/Downloads/` 是固定产品合同，不提供备用目录。

预检错误：

- 不存在 → `DOWNLOADS_NOT_FOUND`
- 不是目录 → `DOWNLOADS_NOT_DIRECTORY`
- 无写权限 → `OUTPUT_PERMISSION_DENIED`

处理期间写入失败：

- 空间不足 → `DISK_FULL`
- 权限变化 → `OUTPUT_PERMISSION_DENIED`
- 其他写入异常 → 映射为适当输出或编码错误

所有情况均弹窗、终止并清理，不自动改写到桌面或输入目录。

## 20. 取消与关闭流程

### 20.1 用户点击取消

```text
GUI cancel
→ controller marks cancelling
→ process runner terminates active process
→ pipeline removes incomplete output
→ workspace cleanup
→ controller emits Cancelled
→ GUI returns to ready
```

### 20.2 用户关闭窗口

无活动任务：直接退出。

有活动任务：

```text
close request
→ confirmation dialog
├── continue processing → keep window and task
└── cancel and exit → normal cancellation flow → exit
```

## 21. 测试分层

### 21.1 单元测试

不启动外部工具，覆盖：

- 参数解析和范围
- Decimal 规范化
- 文件名生成
- 冲突递增
- 错误映射辅助函数
- 状态转换
- 下载目录预检的模拟场景
- 工作区路径安全逻辑

### 21.2 集成测试

使用已验证本机依赖，覆盖：

- 四种输入格式
- FFmpeg 解码
- Rubber Band 处理
- MP3 编码和 FFprobe 验证
- 真实取消
- 真实临时目录清理
- 输入路径特殊字符

### 21.3 GUI 测试

后续覆盖：

- 按钮禁用和恢复
- 冲突提示
- 错误提示
- 取消按钮
- 关闭确认
- 主线程更新

## 22. 打包边界

开发阶段依赖可以来自 Homebrew，但最终 `.app` 必须携带运行组件。

架构必须避免在业务层硬编码 `/opt/homebrew`。只有 `dependencies.py` 的开发解析策略可以知道 Homebrew 路径；打包解析策略使用应用资源目录。

打包阶段需要单独验证：

- FFmpeg、FFprobe、Rubber Band 路径
- Tcl/Tk
- 所有传递 dylib
- `arm64` 架构
- 运行时加载路径
- 许可证与 notices

## 23. 许可证边界

许可证路线尚未最终决定，但架构应保持第三方组件边界清晰：

- FFmpeg/Rubber Band 作为外部可执行组件调用。
- 组件版本和路径可以独立记录。
- 打包清单可以独立列出第三方文件。
- notices 和对应源码提供方式可以在打包层处理。

不得在业务模块中复制第三方源码或把许可证判断散落到 GUI。

## 24. 架构验收标准

后续实现只有满足以下条件才符合本规划：

1. 纯参数和命名逻辑可在无 Tkinter 环境中测试。
2. GUI 不直接调用 `subprocess`。
3. 所有外部调用使用参数数组和 `shell=False`。
4. 单任务约束同时存在于 GUI 和控制层。
5. 后台线程不直接更新 Tkinter 控件。
6. 取消可以终止当前子进程并阻止后续阶段。
7. 输出冲突逻辑集中且永不覆盖。
8. 临时工作区每任务独立。
9. 错误码稳定，用户提示与内部诊断分离。
10. 开发路径与打包路径解析隔离。
11. Windows 激活逻辑没有进入任何 macOS 模块。
12. 行为实现可以逐条映射到 `verification_matrix.md`。
