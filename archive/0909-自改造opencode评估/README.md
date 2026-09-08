# 0909 — 自改造 opencode 变体专题（v1.2）留档

> 任务：在控制理论 ⊗ Agent 设计知识库中增量新增「自改造 opencode（`opencode-custom`）」评估，与官方原版区分。
> 完成日期：2026-09-09　版本：v1.2.0

## 本目录文件

| 文件 | 说明 |
|------|------|
| `report.md` | AI 友好留档报告（5 段模板） |
| `report.html` | 人类可读报告 |

## 交付物（在知识库内）

| 类型 | 路径 |
|------|------|
| 画像 | `../../03-cases/opencode-custom.md` |
| diff | `../../03-cases/opencode-custom-diff.md` |
| 案例页 | `../../04-interactive/case-opencode-custom.html` |
| 对照页（雷达+delta） | `../../04-interactive/compare-opencode.html` |
| 实验 MD | `../../06-experiments/opencode-custom.md` |
| 实验页 | `../../04-interactive/exp-opencode-custom.html` |
| 证据快照 | `../../07-checkpoint/opencode-custom-snapshot/`（`MEMORY.md` 仅本地，不公开） |
| 评分单一数据源 | `../../09-src-data/opencode_custom_scores.py` |

## 核心结论

- **弱环反转**：官方内核 E 环 2.0→4.0、R 环 2.0→4.5（装配层定向补齐，不改引擎）。
- **精装度跃升**：官方 2.9 → 自改造 3.9（Δ+1.0），跨档「需装修」→「成品化受限」；变体不参与 14 产品市售排名。
- **编排升级**：单体双速 → 「主 Agent 编排 + 5 专职 worker + Reflection 自演化」三层平台。

## 门控

L1-L7 **7/7 PASS**（含 L4 VLM 视觉 + L5 headless 渲染 + L6 覆盖度 7 项 + L7 信源 22 项）。
