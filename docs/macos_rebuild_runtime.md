# done

- 2026-08-02：完成原始 Windows 目录的只读扫描，确认文件类型、大小、用途、重复副本、绝对路径、敏感内容迹象、链接和 Git 状态。
- 2026-08-02：初始化本地 Git 仓库，接入并跟踪 `origin/main`；远端当时仅包含静态合同。
- 2026-08-02：完整读取 `docs/macos_rebuild_static.md`，确认 macOS 优先、Android 后续以及新版本移除激活机制的长期约束。
- 2026-08-02：生成一次性仓库地图 `docs/map_win_8.2.md`。
- 2026-08-02：完成平台目录分类，建立根级 `.gitignore`；Windows 构建产物、第三方二进制和本地激活文件已保留在被忽略的 `_local_artifacts` 中。

# active step

- 核对目录重整后的暂存范围：只纳管 README、项目文档、Windows 源码、使用指南和 PyInstaller 配置；验证 `_local_artifacts`、EXE、DLL、授权文件、日志及构建目录均未进入索引。完成分批提交后，把提交短哈希追加到本文件。

# next steps

- 建立 macOS 复刻的准备清单：梳理可复用的产品行为与需要移除的 Windows 激活逻辑。
- 待确认 FFmpeg、Rubber Band、libsndfile 的 macOS 获取方式、版本、构建选项和许可证义务。
- 待确认目标 macOS 设备架构、最低系统版本及是否需要签名、公证或通用二进制。
- 在上述准备项确认前，不开始 GUI、打包或依赖安装。
