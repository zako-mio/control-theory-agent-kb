---
name: requirement-discovery-behavior
description: 需求发现行为层(触发规则)。触发:需求表述模糊/多走法/可行性未知/需按产品设计复杂度走一遍时。
---

<!-- BEGIN REQUIREMENT-DISCOVERY-BEHAVIOR POLICY -->
## 需求发现触发规则（opencode）

1. **定档前置（机械，⛔ 不以"看难度"裁量）**：命中需求发现类表述后先跑
   `python3 "$TIER_TOOL" --enter "<需求原文>"`（`$TIER_TOOL` 见 `skills/requirement-discovery/_private/local-bindings.json`）。
   **简单档** ⇒ ⛔ 不加载 skill／不委派／不产工件；走三步（意图一句 → 做第一个可跑产物 → 拿反馈即停），末尾标 `[需求分档: 简单档]`。
   **复杂档** ⇒ 加载 `requirement-discovery` skill 按 `workflow.md` 阶段 0–5 执行；涉真实需求时委派 `requirement-discovery-worker`。
   ⚠ 工具不可用 ⇒ 显式标 `FAIL`，⛔ 不得凭感觉选档。
2. **边界（⛔ 防抢词）**：⛔ 不产 ADR／选型矩阵／质量属性权衡（→ `architecture-judgment`）；⛔ 不产 proposal/specs/tasks（→ `openspec-propose`，**仅显式交接**）；⛔ 不写代码／不做 TDD。
3. **外部事实与访谈**：需要外部事实时**调用** `search-methodology`，⛔ 不自建检索/验证；访谈**消费** `grill-me` 协议，⛔ 不另造访谈引擎。
4. **⚠ 验证优先（`V1`–`V4`）**：门控全绿／产物被验收／流程走完**一律不得**当作「已达成」（`V3` 禁令）；达成 ＝ **消费证据**（真实触发实例 ＋ 每次落产物，经门控 ledger）。
   ⛔ 阈值不得由规模直觉推导（实证：「列表 ≤5 项」不可由理论推导）；引用外部理论须**显式标注人群与情境边界**。
5. **显式入口**：`/rd <需求描述>` —— 一律按**复杂档**执行（显式入口优先于自动定档）。
<!-- END REQUIREMENT-DISCOVERY-BEHAVIOR POLICY -->
