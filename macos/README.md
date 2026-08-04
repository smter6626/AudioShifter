# AudioShifter for macOS

AudioShifter 是一个完全在本机运行的中文音频变调与变速工具。仓库既保留 Python 源码开发入口，也提供可重复构建的 Apple Silicon `AudioShifter.app`。当前应用只在 Apple Silicon `arm64`、macOS 27 上构建和验证；旧版 macOS 未测试，可能无法运行。不承诺 Intel Mac、Rosetta 或 `universal2`。

## 直接使用 `.app`

本地构建产物位于：

```text
macos/dist/AudioShifter.app
```

在 Finder 中双击 `AudioShifter.app` 即可启动中文 GUI。这个应用包已经内置 CPython、Tcl/Tk、FFmpeg、FFprobe、Rubber Band 和运行所需的非系统动态库；运行时无需安装或激活 Python，无需 Homebrew，也无需单独安装音频工具。

应用采用 PyInstaller `onedir + windowed` 结构。复制时必须保留完整 `.app` bundle 和其中的符号链接，建议使用 Finder 或：

```bash
ditto macos/dist/AudioShifter.app /目标目录/AudioShifter.app
```

当前构建只使用 PyInstaller 为 Apple Silicon 运行所需生成的 ad-hoc signing。它没有使用 Developer ID Application 证书、没有经过 Apple 公证、没有 stapling，也不是 Mac App Store sandbox 应用。因此 Gatekeeper 对来自其他传输渠道的副本可能拒绝评估；本阶段没有修改 Gatekeeper 或系统安全设置。

## 构建 `.app`

先按下文恢复开发环境，再从仓库根目录执行：

```bash
macos/packaging/build_app.sh
```

脚本会从正式 spec `macos/packaging/AudioShifter.spec` 重新生成图标、递归盘点外部工具的 Mach-O 依赖、清理本项目的 `macos/build/` 和 `macos/dist/`，并生成 `macos/dist/AudioShifter.app`。不需要手工修改构建后的应用包。

重新运行打包验收：

```bash
macos/packaging/verify_app.sh
macos/packaging/verify_packaged_pipeline.sh
```

第一条命令审计应用结构、Info.plist、图标、所有 Mach-O 架构、动态载入路径、RPATH、符号链接和 ad-hoc codesign；第二条使用应用包内部工具验证四种输入、输出规格、不覆盖、源哈希、取消和清理。详细证据见 [packaging_test_report.md](packaging_test_report.md)。

## 环境恢复

需要 Homebrew 提供 Python 3.11、Tk 8.6、FFmpeg、FFprobe 和 Rubber Band。恢复已验证环境时，在仓库根目录执行：

```bash
HOMEBREW_NO_AUTO_UPDATE=1 brew bundle --file=macos/Brewfile
/opt/homebrew/opt/python@3.11/bin/python3.11 -m venv macos/.venv
macos/.venv/bin/python -m pip install -r macos/requirements-dev.txt
macos/.venv/bin/python -m pip install -e .
```

若 `macos/.venv` 已存在，只需激活环境并确认当前源码以 editable 模式安装：

```bash
source macos/.venv/bin/activate
python -m pip install -r macos/requirements-dev.txt
python -m pip install -e .
```

不要升级或清理系统 Homebrew 环境来运行本 MVP；已验证版本和依赖事实见 [environment_report.md](environment_report.md)。

## 从源码启动 GUI

从仓库根目录执行：

```bash
cd /Users/smterpro/Workspace/Tools/AudioShifter
source macos/.venv/bin/activate
python -m audioshifter
```

界面会在后台线程处理音频，因此处理时窗口仍可响应。一个应用实例同时只允许一个任务；运行中可以取消，关闭窗口时会先询问是否取消并退出。

## 使用规则

- 支持输入：MP3、M4A、WAV、FLAC，扩展名大小写均可。
- 变调：相对原音频的整数半音，范围 `-24` 至 `+24`；`0` 保持原调。
- 变速：相对原速度的变化百分比，范围 `-95` 至 `+400`。非零值必须写 `+` 或 `-`，无需输入 `%`；例如 `-20` 表示减速 20%。
- 输出：固定保存到当前用户的 `~/Downloads/`。
- 输出媒体：320 kbps、44.1 kHz、双声道 MP3。
- 命名：`<原文件 stem><显式符号变调><显式符号变速>%.mp3`，例如 `song+3-20%.mp3`；零值也保留为 `+0+0%`。
- 已有文件永不覆盖；冲突时提示后采用 `_2`、`_3` 等首个可用名称。
- 源文件不会被修改；每个任务使用独立系统临时目录，成功、失败或取消后清理。
- 第一阶段不复制标题、艺术家、封面、歌词等源音频元数据。

## 运行测试

完整测试入口：

```bash
macos/.venv/bin/python -m pytest
```

也可以分层运行：

```bash
macos/.venv/bin/python -m pytest macos/tests/unit
macos/.venv/bin/python -m pytest macos/tests/integration
```

测试在系统临时目录动态生成合成音频，不使用或提交用户音频。源码 MVP 证据见 [mvp_test_report.md](mvp_test_report.md)，独立应用证据见 [packaging_test_report.md](packaging_test_report.md)。

## 当前限制

- 当前 `.app` 只在 Apple Silicon `arm64`、macOS 27 上构建和验证；旧版 macOS 未测试，可能无法运行。没有 Intel、Rosetta 或 `universal2` 构建。
- 源码运行和重新构建仍需要已验证的 Homebrew 工具链与 `macos/.venv`；已经生成的 `.app` 运行时不需要这些开发依赖。
- 没有 Developer ID 正式签名或 Apple 公证，未生成 `.dmg`，也没有上传 GitHub Release。
- 不提供批处理、任务队列、自定义输出目录、输出格式选择或元数据保留。
- 状态按处理阶段显示，不提供缺乏依据的精确百分比。
- 已记录实际内置依赖及许可证文本，但正式公开分发前仍必须确定 GPL 兼容的应用许可、对应源码交付和 notice 路线；见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 设计与合同

- [长期静态合同](../docs/macos_rebuild_static.md)
- [执行状态与当前步骤](../docs/macos_rebuild_runtime.md)
- [行为规格](design/behavior_spec.md)
- [架构规划](design/architecture_plan.md)
- [验证矩阵](design/verification_matrix.md)
