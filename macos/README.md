# AudioShifter for macOS

AudioShifter 是一个完全在本机运行的中文音频变调与变速工具。仓库既保留 Python 源码开发入口，也提供可重复构建的 Apple Silicon `AudioShifter.app`。当前应用只在 Apple Silicon `arm64`、macOS 27 上构建和验证；旧版 macOS 未测试，可能无法运行。不承诺 Intel Mac、Rosetta 或 `universal2`。

## v0.1.0-alpha.3 Release candidate

当前预览候选为 `v0.1.0-alpha.3`。已认证协作者可查看未公开的 Draft
Pre-release（database ID `364860803`）：

<https://github.com/smter6626/AudioShifter/releases/tag/untagged-eb4c98469e0200c34d24>

Release 仍包含三个附件，但普通用户只需下载：

```text
AudioShifter-v0.1.0-alpha.3-macOS27-arm64.zip
SHA256SUMS.txt
```

在下载目录只校验 App ZIP：

```bash
grep 'AudioShifter-v0.1.0-alpha.3-macOS27-arm64.zip$' SHA256SUMS.txt \
  | shasum -a 256 -c -
```

需要审计、修改或重建的人再额外下载：

```text
AudioShifter-v0.1.0-alpha.3-corresponding-source.tar.gz
```

对应源码包不是运行应用所必需的。App 和对应源码两个归档均已下载时，可以
运行完整校验：

```bash
shasum -a 256 -c SHA256SUMS.txt
```

两个归档都应显示 `OK`。

当前 Draft 附件的固定校验值为：

| 附件 | 字节数 | SHA-256 |
|---|---:|---|
| `AudioShifter-v0.1.0-alpha.3-macOS27-arm64.zip` | 27,764,722 | `a7866775734cbcde12d1b3d5186a09f71da71fe380650438d67a8d1f2987711d` |
| `AudioShifter-v0.1.0-alpha.3-corresponding-source.tar.gz` | 200,051,018 | `2936187f84081c322e3d43254ec2a7f829037db84dc9b7e3532fc868dd9546d2` |
| `SHA256SUMS.txt` | 234 | `611171939727f40a008c514f6664b5d2ddd5d04b17b23827622fc8babb88d9c2` |

二进制使用 PyInstaller ad-hoc signing，没有 Developer ID、Apple notarization
或 stapling。首次打开可能出现“Apple 无法验证 AudioShifter.app 是否包含
恶意软件”。只应在确认文件来自本仓库 Release 且 SHA-256 匹配后，先尝试
打开一次，再前往“系统设置 → 隐私与安全性 → 仍要打开”对该应用单独放行；
不要全局关闭 Gatekeeper。

对应源码附件包含该 tag 的 AudioShifter 源码、项目许可证和品牌政策，以及
实际内置第三方组件的准确源码、formula/receipt、补丁、构建证据和许可证。
本候选只创建 Draft Pre-release，等待项目所有者审核和非开发机人工验收；
本阶段不会公开 Publish。

## 许可证与品牌

除文件另有说明外，AudioShifter 项目所有者拥有版权、且位于许可范围内的
代码以 `GPL-3.0-or-later` 提供。完整 GPLv3 正文、项目范围和品牌规则见：

- [`../LICENSE`](../LICENSE)
- [`../LICENSING.md`](../LICENSING.md)
- [`../TRADEMARKS.md`](../TRADEMARKS.md)
- [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)

GPL 允许依照其条款使用、修改、再分发和商业使用代码。AudioShifter 名称、
Logo、应用图标和官方品牌不属于 GPL 授权。未经书面许可，修改版必须更换
产品名、bundle identifier、图标和容易造成官方来源混淆的品牌元素，并明确
注明它是基于 AudioShifter 的非官方分支、与官方项目无隶属或认可关系。
品牌政策只防止冒充官方来源，不禁止使用其他名称和品牌发布商业 GPL fork。

品牌政策同时提供一项窄授权：可以按必要范围复制 AudioShifter 名称、图标和
其他品牌资产，以从官方 tag 复现未修改的官方构建，或原样转发官方 Release。
该授权不把品牌资产置于 GPL 下；修改版仍必须更换名称、bundle identifier、
Logo、图标和其他来源识别品牌，除非获得事先书面许可。

`windows/` 历史内容不属于本项目 GPL 授权；第三方组件继续适用各自许可证。

## 直接使用 `.app`

本地构建产物位于：

```text
macos/dist/AudioShifter.app
```

在 Finder 中双击 `AudioShifter.app` 即可启动中文 GUI。这个应用包已经内置 CPython、Tcl/Tk、FFmpeg、FFprobe、Rubber Band 和运行所需的非系统动态库；运行时无需安装或激活 Python，无需 Homebrew，也无需单独安装音频工具。

完整许可证位于 macOS 顶部原生应用菜单：

```text
AudioShifter → License
```

该菜单项打开标题为 `AudioShifter License` 的非阻塞英文窗口，显示应用包内
`Contents/Resources/LICENSE` 的完整 GPLv3 正文；窗口可调整大小、滚动、
选择复制，并支持 Command-C 和 Command-W。主 GUI 中没有 License 按钮，
License 也不在 File 或 Help 菜单。

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

第一条命令审计应用结构、Info.plist、图标、所有 Mach-O 架构、动态载入路径、RPATH、符号链接和 ad-hoc codesign；第二条使用应用包内部工具验证四种输入、输出规格、不覆盖、源哈希、取消和清理。独立打包阶段证据见 [packaging_test_report.md](packaging_test_report.md)，alpha.3 的 tag 构建、Draft 上传、下载回验和 License 菜单证据见 [release_verification_v0.1.0-alpha.3.md](release/release_verification_v0.1.0-alpha.3.md)。

## 构建 alpha.3 Release 资产

正式准备提交已推送并创建 annotated tag 后，从干净的仓库根目录运行：

```bash
macos/release/build_release_assets.sh v0.1.0-alpha.3
```

该命令会重新运行全部测试，从 alpha.3 tag 的 detached worktree 重建并
验收 `.app`，使用 `ditto` 创建 App ZIP，收集准确第三方对应源码、formula、
receipt、patch、构建证据和许可证，并生成及验证 `SHA256SUMS.txt`。输出位于
被精确忽略的 `macos/release-dist/`，不得提交到 Git。工具和操作细节见
[`release/README.md`](release/README.md)。

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
- 没有 Developer ID 正式签名或 Apple 公证，未生成 `.dmg`；alpha.3 只准备 Draft Pre-release，不在本阶段公开发布。
- 不提供批处理、任务队列、自定义输出目录、输出格式选择或元数据保留。
- 状态按处理阶段显示，不提供缺乏依据的精确百分比。
- 已记录实际内置依赖、准确对应源码、补丁和许可证文本；正式公开前仍需项目所有者审核 Draft 并在非开发机完成人工验收。

## 设计与合同

- [长期静态合同](../docs/macos_rebuild_static.md)
- [执行状态与当前步骤](../docs/macos_rebuild_runtime.md)
- [行为规格](design/behavior_spec.md)
- [架构规划](design/architecture_plan.md)
- [验证矩阵](design/verification_matrix.md)
