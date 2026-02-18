---
name: "superpowers"
description: "集成 Superpowers 工作流。于设计、规划、实现与测试阶段自动触发相关技能，强制 RED-GREEN-REFACTOR 与两阶段评审。"
---

# Superpowers 工作流

此技能在整个工程生命周期内提供基于“Superpowers”的流程化能力，覆盖从需求澄清、设计拆分、计划编写、子代理执行到测试驱动开发与代码评审的完整闭环。它以简化复杂度、系统化方法与可验证结果为核心。

## 触发规则
- 设计前：进入“brainstorming”以澄清目标并形成可审阅的分段设计文档
- 设计批准后：启用“using-git-worktrees”在独立分支与工作区进行实现
- 编写计划时：启用“writing-plans”将任务拆分为可验证的微任务（2–5 分钟）
- 执行实现时：优先“subagent-driven-development”或“executing-plans”批处理并设置检查点
- 测试阶段：强制“test-driven-development”遵循 RED → GREEN → REFACTOR
- 评审流程：在任务边界调用“requesting-code-review”，采用规范核对与质量审查的双阶段评审
- 收尾阶段：使用“finishing-a-development-branch”进行测试验证、合并/PR 决策与清理

## 全局策略
- YAGNI：仅实现当下必需的功能，避免过度设计
- DRY：消除重复，抽象共性
- Evidence over claims：所有结论以测试和验证为依据
- Complexity reduction：首要目标是降低复杂度与认知负担

## 验证约束
- 测试优先：所有代码变更必须先有失败测试，后有最小通过实现，最后重构
- 评审阻断：关键问题（功能不符、测试缺失、接口不一致）将阻断后续任务
- 隔离开发：默认在新分支与独立工作树中实现，保持主分支健康

## 配置
全局配置位于同目录的 `config.yaml`，用于控制启用的工作流、评审阈值与分支策略等。常见字段：

```yaml
enabled: true
workflows:
  brainstorming: true
  using_git_worktrees:
    enabled: true
    branch_prefix: "feat/superpowers-"
  writing_plans:
    enabled: true
    task_granularity_minutes: 5
  executing_plans:
    enabled: true
    mode: "subagent"
  test_driven_development:
    enforce: true
  requesting_code_review:
    enabled: true
    severity_thresholds:
      critical: "block"
      major: "require_fix"
      minor: "record_and_continue"
  finishing_development_branch:
    enabled: true
policy:
  yagni: true
  dry: true
  evidence_over_claims: true
  complexity_reduction: true
```

## 使用指引
- 触发短语示例：  
  - “帮我规划这个功能” → 触发 brainstorming / writing-plans  
  - “开始实现并验证” → 触发 executing-plans / TDD  
  - “先做代码评审” → 触发 requesting-code-review
- 建议在任务开始与结束时，明确“入口/出口条件”，保证每个环节可度量、可回滚、可复查。

