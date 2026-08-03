# Windows 原始目录盘点（2026-08-02）

本文档是目录重整前的一次性仓库盘点快照，不是 static 或 runtime 文档。

## 1. 扫描信息

- 扫描日期：2026-08-02 21:41:44 MST
- 扫描目录：`/Users/smterpro/Workspace/Tools/AudioShifter/`
- 扫描时 Git 状态：不是 Git 仓库；不存在 `.git`、`.gitmodules`、`.gitattributes`、嵌套仓库或 Git LFS 状态。
- 操作系统与架构：Darwin 27.0.0，arm64
- 隐藏项：无
- 软链接或其他符号链接：无
- 超过 10 MB 的文件：根目录与 `dist/` 内的两个相同 Windows EXE、PyInstaller 的 `MyAudioShifter.pkg`、`ffmpeg.exe`；均判定为不提交内容。
- 扫描方式：仅使用文件系统元数据、文本读取、哈希、归档目录和 PE 元数据静态检查；未执行 Python、EXE 或加载 DLL。

### 原始目录树

```text
AudioShifter/
├── MyAudioShifter.exe
├── MyAudioShifter.spec
├── admin_keygen.py
├── build/
│   └── MyAudioShifter/
│       ├── Analysis-00.toc
│       ├── EXE-00.toc
│       ├── MyAudioShifter.pkg
│       ├── PKG-00.toc
│       ├── PYZ-00.pyz
│       ├── PYZ-00.toc
│       ├── base_library.zip
│       ├── localpycs/
│       │   ├── pyimod01_archive.pyc
│       │   ├── pyimod02_importers.pyc
│       │   ├── pyimod03_ctypes.pyc
│       │   ├── pyimod04_pywin32.pyc
│       │   └── struct.pyc
│       ├── warn-MyAudioShifter.txt
│       └── xref-MyAudioShifter.html
├── dist/
│   ├── MyAudioShifter.exe
│   └── license.dat
├── ffmpeg.exe
├── license.dat
├── log/
├── rubberband.exe
├── shifter_gui _EnglishVersion.py
├── shifter_gui.py
├── sndfile.dll
└── 使用指南.txt
```

## 2. 文件分类表

| 原始路径 | 类型 | 作用 | 建议目标路径 | 是否提交 Git | 原因 |
| ---- | -- | -- | ------ | -------- | -- |
| `shifter_gui.py` | 源代码 | 中文 Tkinter GUI、旧激活校验、FFmpeg/Rubber Band 调用和输出处理 | `windows/src/shifter_gui.py` | 是 | Windows 历史实现与行为参考；废弃激活逻辑另列风险 |
| `shifter_gui _EnglishVersion.py` | 源代码 | 英文版 Tkinter GUI，核心处理与中文版相同 | `windows/src/shifter_gui_english.py` | 是 | 可提交的历史源码；修正文件名多余空格 |
| `MyAudioShifter.spec` | 构建配置 | PyInstaller 配置，原来引用 `shifter_gui.py`、FFmpeg、Rubber Band 和 sndfile | `windows/packaging/MyAudioShifter.spec` | 是 | 可重复构建所需配置；资源路径随目录调整 |
| `使用指南.txt` | 用户文档 | Windows 成品的激活和音频处理使用说明 | `windows/docs/使用指南.txt` | 是 | 历史用户文档；其授权表述需要后续审查 |
| `admin_keygen.py` | 授权或激活相关文件 | 旧机器码激活码生成器，含与 GUI 相同的硬编码激活盐值 | `windows/_local_artifacts/legacy_activation/admin_keygen.py` | 否 | 废弃激活工具，不应公开或扩展 |
| `license.dat` | 本地私有文件 | 生成的本机授权值 | `windows/_local_artifacts/legacy_activation/license.dat` | 否 | 机器/授权相关本地数据 |
| `dist/license.dat` | 本地私有文件 | 与根目录 `license.dat` 哈希相同的副本 | `windows/_local_artifacts/dist/license.dat` | 否 | 生成的授权数据且属于发布产物 |
| `MyAudioShifter.exe` | 构建产物 | PyInstaller Windows GUI 成品，48,650,317 字节 | `windows/_local_artifacts/bin/MyAudioShifter.exe` | 否 | 预编译成品且超过 10 MB；与 `dist` 副本相同 |
| `dist/MyAudioShifter.exe` | 构建产物 | 与根目录 EXE 哈希相同的发布副本 | `windows/_local_artifacts/dist/MyAudioShifter.exe` | 否 | 可重新生成的发布产物 |
| `ffmpeg.exe` | 第三方依赖 | FFmpeg 8.0.1 essentials Windows 可执行文件，99,264,000 字节 | `windows/_local_artifacts/bin/ffmpeg.exe` | 否 | 第三方预编译二进制，来源/构建选项/许可证未完整确认 |
| `rubberband.exe` | 第三方依赖 | Rubber Band Windows 命令行程序，646,496 字节 | `windows/_local_artifacts/bin/rubberband.exe` | 否 | 第三方预编译二进制，来源和许可证材料未确认 |
| `sndfile.dll` | 第三方依赖 | libsndfile 1.2.2 Windows 动态库，2,603,520 字节 | `windows/_local_artifacts/bin/sndfile.dll` | 否 | 第三方预编译动态库，来源和许可证材料未确认 |
| `build/MyAudioShifter/*.toc` | 构建产物 | PyInstaller 分析、EXE、PKG 和 PYZ 清单 | `windows/_local_artifacts/build/MyAudioShifter/` | 否 | 生成文件；包含旧机器绝对路径和用户名痕迹 |
| `build/MyAudioShifter/MyAudioShifter.pkg` | 构建产物 | PyInstaller 内部打包归档，48,310,861 字节 | `windows/_local_artifacts/build/MyAudioShifter/` | 否 | 大型、可重新生成的中间产物 |
| `build/MyAudioShifter/PYZ-00.pyz` | 构建产物 | PyInstaller Python 模块归档 | `windows/_local_artifacts/build/MyAudioShifter/` | 否 | 可重新生成的中间产物 |
| `build/MyAudioShifter/base_library.zip` | 构建产物 | Python 标准库字节码归档，共 155 项 | `windows/_local_artifacts/build/MyAudioShifter/` | 否 | 可重新生成且非项目源码 |
| `build/MyAudioShifter/localpycs/` | 构建产物 | PyInstaller 引导模块字节码 | `windows/_local_artifacts/build/MyAudioShifter/localpycs/` | 否 | Python 缓存/构建产物 |
| `build/MyAudioShifter/warn-MyAudioShifter.txt` | 构建产物 | PyInstaller 缺失模块诊断 | `windows/_local_artifacts/build/MyAudioShifter/` | 否 | 单次构建日志性质的输出 |
| `build/MyAudioShifter/xref-MyAudioShifter.html` | 构建产物 | PyInstaller 模块交叉引用报告 | `windows/_local_artifacts/build/MyAudioShifter/` | 否 | 生成报告且包含旧机器路径 |
| `log/` | 日志 | 空日志目录，权限为全员可写 | `windows/_local_artifacts/log/` | 否 | 本地运行状态，不属于源码；权限也需后续审查 |

扫描未发现无法归类的唯一源数据。根 EXE、`dist` EXE 以及两份授权文件分别为相同哈希副本，但本轮仍全部保留，没有以“重复”为由删除。

## 3. 已发现风险

- 两份 GUI 源码和旧注册机包含同一硬编码激活盐值；本文不记录该值。静态合同要求新版本完全移除机器码、注册码和授权文件校验。
- 旧实现读取 Windows `MachineGuid`，备选调用 WMIC，并在本地写入 `license.dat`。这些逻辑不得移植到 macOS 或 Android。
- 生成的授权文件属于本机/授权相关数据，已排除。
- PyInstaller 的 TOC 和 xref 文件包含旧 Windows 绝对路径及用户名痕迹，已随整个构建目录排除。
- 第三方 EXE/DLL 没有配套的来源记录、完整许可证文本或构建选项；不能仅凭二进制内版本字符串判断分发义务。
- 原目录被 `build/`、`dist/`、成品与依赖二进制污染，不适合整体纳管。
- 英文源码原名 `shifter_gui _EnglishVersion.py` 含多余空格；目标名规范为 `shifter_gui_english.py`。
- 旧源码在用户 `Downloads` 中使用固定临时文件名，且工作线程直接更新 Tkinter 控件；均与静态合同的临时资源和线程安全要求存在差距，留待复刻阶段处理。
- 旧使用指南用“禁止商业用途”概括分发限制，不能替代 FFmpeg、Rubber Band、libsndfile 的实际许可证判断。
- `log/` 原权限为全员可写；目录为空且被排除，后续若引入日志应重新设计位置、权限和隐私边界。

未发现 API Token、GitHub Token、私钥、签名密钥、Android keystore、软链接、子模块或嵌套 Git 仓库。已识别的激活盐值属于明确标注为废弃的历史机制，未作为新功能使用。

## 4. 推荐目标结构

```text
AudioShifter/
├── .gitignore
├── README.md
├── docs/
│   ├── macos_rebuild_static.md
│   ├── macos_rebuild_runtime.md
│   └── map_win_8.2.md
├── windows/
│   ├── README.md
│   ├── src/
│   │   ├── shifter_gui.py
│   │   └── shifter_gui_english.py
│   ├── packaging/
│   │   └── MyAudioShifter.spec
│   ├── docs/
│   │   └── 使用指南.txt
│   └── _local_artifacts/        # 整个目录仅本地保留并忽略
│       ├── bin/
│       ├── build/
│       ├── dist/
│       ├── legacy_activation/
│       └── log/
├── macos/
│   └── README.md
└── mobile/
    └── README.md
```

## 5. 明确排除项

- `windows/_local_artifacts/build/`：PyInstaller 中间产物、缓存、日志和包含本机绝对路径的报告。
- `windows/_local_artifacts/dist/`：Windows 发布成品和生成的授权文件。
- `windows/_local_artifacts/bin/*.exe`、`*.dll`：项目成品及来源/许可证状态未完整确认的第三方二进制。
- `windows/_local_artifacts/legacy_activation/admin_keygen.py`：废弃注册机。
- `windows/_local_artifacts/legacy_activation/license.dat`：生成的本地授权值。
- `windows/_local_artifacts/log/`：本地日志目录。
- 后续所有 `build/`、`dist/`、Python 缓存、虚拟环境、日志、打包应用、移动端包、keystore、签名密钥、环境秘密和用户音频。

以上内容均保留在本机；本轮不删除任何原始副本。

## 6. 待后续处理项

- 按静态合同在新 macOS 实现中移除而非复刻全部激活和机器绑定逻辑。
- 将 GUI、音频处理、依赖/路径解析、参数校验和错误表示拆分为可测试模块。
- 设计唯一临时目录、同名输出处理、取消/失败清理和 Tkinter 主线程更新机制。
- 确认 FFmpeg、Rubber Band、libsndfile 的 macOS 版本、来源、构建方式、构建选项、许可证文本和分发义务。
- 确认目标 Mac 架构、最低系统版本、签名、公证和通用二进制需求。
- 通过测试确定输入格式、参数边界、输出命名和错误类别，不提前扩大产品承诺。
- macOS 复刻完成后再开始 `mobile/` 下的 Android 移植。
