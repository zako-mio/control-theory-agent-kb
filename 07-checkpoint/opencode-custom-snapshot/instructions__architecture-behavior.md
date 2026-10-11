---
name: architecture-behavior
description: 架构判断行为层(触发规则)。触发:任何涉及技术选型/架构风格/模块与服务边界/架构评审/质量属性权衡/技术债治理/演进治理的任务。
---

<!-- BEGIN ARCHITECTURE-BEHAVIOR POLICY -->
## 架构设计能力触发规则（opencode）

### 第 0 步 · 规模三问（先分流，再决定是否走重流程）

命中「架构类任务」后，主 Agent **先答完下列三问**，答案须在答复或 PLAN 中留痕：

| # | 判定问 | 触发条件 |
|---|---|---|
| Q1 | 是否改变**模块/服务边界或对外接口**（接口签名、契约、依赖方向）？ | 改 → 触发 |
| Q2 | 变更是否**跨模块传播**（会连带改到 ≥2 个模块/包/App）？ | 是 → 触发 |
| Q3 | 反转成本是否**高于「改回配置 / 删文件」量级**（涉数据迁移、外部依赖更换、多文件重构）？ | 高于 → 触发 |

- **三问全不触发 → 咨询级**：**不加载 skill、不委派子 Agent、不产 ADR、不过门控**；
  直接给结论与理由，并在答复末尾标注 `[架构分档: 咨询级 · 三问全不触发 · 未走门控]`。
- **命中 ≥1 问 → 按 `architecture-judgment/routing.md` §9 定档**，执行对应介入强度
  （门控级 / 产出级 / 按需级；各档要求见 §9 表）。
- 口径说明：本分档用于修正「小决策被套重流程」——避免选一个库、调一个目录结构也强制产 ADR 并过门控。

### 三步流程（**仅门控级强制**；产出级 / 按需级见 §9）

对**门控级**任务，主 Agent 必须执行以下三步（不得跳过）：

1. 加载 `architecture-judgment` skill；
2. 委派 `architect-worker` 子 Agent（可见子 Agent；用户也可用 `@architect-worker` 直接召唤）；
3. **方案设计与选型**类任务须过 `gate_architecture.py` 门控方可交付，门控未过不得声称完成。

- **产出级 / 按需级**：不必委派，主 Agent 可自行按对应模板产出（人工确认后定稿）。
- **咨询级**：不产工件、不留档，仅给建议。
- 用户显式调用 `/arch` 时**一律按门控级执行**（显式入口优先于自动分档）。

### 架构类任务的特征

技术选型、架构风格、模块边界、服务粒度、架构评审、设计裁决、质量属性权衡、
敏感点/权衡点分析、技术债治理、遗留系统重构优先级、演进式架构防漂移、
可观测性与 SLO、部署与发布策略、测试策略、交付效能度量。

### 知识分层策略（刚性）

- **方法论层（`MTH-*`）与本质层（`ESS-*`）** 是判断依据，可放宽命中（**重召回**）。
- **技术实践层（`TEC-*`）仅作「选型标尺」佐证**：宁可漏引也不错引（字面不精确命中就不引）；
  只能写入 ADR 的 `standards_refs`，**不得出现在 `decision` / `rationale` 等推荐位**。

### 产出契约

- 交付物：ADR、多维权衡矩阵、边界/模块设计说明（`--kind boundary`）、架构图（按 `diagram-lite` 档位出图）。
- 结构契约：skill 的 `schemas/adr.schema.json`（ADR）与 `schemas/boundary.schema.json`（边界说明）；
  人读检查单：`checklist.md`；工作流：`workflow.md`。
- 其余 4 个工程步骤（需求质量属性 / 评审裁决 / 重构技术债 / 交付治理）为**模板级**产出：
  `templates/review.md`、`templates/tech-debt.md`（不加 schema / 门控）。

### openspec `design` 工件门控（刚性）

当任务涉及**生成或修改** openspec 的 `design` 工件时（`design` 为可选工件，其存在即视为架构相关）：

1. 必须先加载 `architecture-judgment` skill，按其 `integrations/openspec-design.md` 执行；
2. 委派 `architect-worker` 产 `ADR`（落 `change/adr/ADR-xxx.{json,md}`）+ 权衡矩阵（涉选型）；
3. `gate_architecture.py --kind adr --input <adr.json>` **PASS 之前不得定稿 `design.md`**；
   FAIL 回传修正最多 2 轮，不得降级为"口头通过"；
4. 任务结束时把 `change/adr/` 复制到任务留档目录（双落）。
   ⛔ 不修改 openspec 包、也不直接改其生成的 `openspec-*` skill（会被 `openspec update` 无条件覆写）。

### 显式入口与边界

- 用户可用 `/arch <任务描述>` 强制走本流程。
- 知识图谱为母库离线资产，**不联网即可用**；Pages 深链仅作公开引用。
- 架构图不由本流程产出，由主 Agent 加载 `diagram-lite` skill 按档位出图（默认 T2：`dot -Tsvg` 出中文 SVG；对外发布级走 T3）。
<!-- END ARCHITECTURE-BEHAVIOR POLICY -->
