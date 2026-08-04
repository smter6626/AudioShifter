# AudioShifter macOS MVP

AudioShifter 是一个完全在本机运行的中文音频变调与变速工具。当前仓库提供可从 Python 虚拟环境直接启动的 Apple Silicon macOS MVP；尚未打包为 `.app`。

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

## 启动 GUI

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

测试在系统临时目录动态生成合成音频，不使用或提交用户音频。最新证据见 [mvp_test_report.md](mvp_test_report.md)。

## 当前限制

- 当前仅支持 Apple Silicon `arm64` 开发环境；不支持 Intel Mac 或通用二进制。
- 尚未执行 PyInstaller，未生成 `.app` 或 `.dmg`；源码运行仍需要已验证的 Homebrew 工具链和虚拟环境。
- 最低 macOS 版本尚未通过最终打包产物实测，因此不作承诺。
- 不提供批处理、任务队列、自定义输出目录、输出格式选择或元数据保留。
- 状态按处理阶段显示，不提供缺乏依据的精确百分比。
- 正式二进制分发前仍需完成 FFmpeg/Rubber Band 等依赖的许可证材料与分发路线。

## 设计与合同

- [长期静态合同](../docs/macos_rebuild_static.md)
- [执行状态与当前步骤](../docs/macos_rebuild_runtime.md)
- [行为规格](design/behavior_spec.md)
- [架构规划](design/architecture_plan.md)
- [验证矩阵](design/verification_matrix.md)
