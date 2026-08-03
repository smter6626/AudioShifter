# macOS

当前状态：Apple Silicon 开发环境已验证，行为合同与实现前架构已经确认，尚未开始正式 GUI 和音频处理核心实现。

## 核心文档

- [长期静态合同](../docs/macos_rebuild_static.md)
- [执行状态与当前步骤](../docs/macos_rebuild_runtime.md)
- [开发环境报告](environment_report.md)
- [行为规格](design/behavior_spec.md)
- [架构规划](design/architecture_plan.md)
- [验证矩阵](design/verification_matrix.md)

## 当前平台边界

- 仅支持 Apple Silicon `arm64`
- 不支持 Intel Mac 或通用二进制
- 不考虑 Developer ID 签名和 Apple 公证
- 不修改或重构 Windows 历史实现

下一阶段将依据已确认合同建立非 GUI 测试框架和最小核心代码骨架。
