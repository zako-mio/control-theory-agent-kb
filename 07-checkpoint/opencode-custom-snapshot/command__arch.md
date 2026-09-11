---
description: 架构设计与裁决（/arch <任务描述>）。加载 architecture-judgment 工作流并委派 architect-worker，产出 ADR / 多维权衡矩阵 / 边界设计说明 / 评审结论，经 gate_architecture.py 门控后才交付。
agent: build
---

# 架构设计与裁决命令

你在 build 模式下执行架构任务。用户输入 `/arch <任务描述>`（或 `/arch 选型|评审|边界|技术债 …`）时，按以下流程执行，不依赖其他文档。

## 0. 前置路径

```
SKILL   = /home/zako-mio/.config/opencode/skills/architecture-judgment
MROOT   = /home/zako-mio/opencode/archive/Mission-file/2026-09/0910-软件工程架构方法论
GRAPH   = $MROOT/10-dag-data/methodology-dag.json
```

- 执行主流程：`$SKILL/workflow.md`
- 人工检查单：`$SKILL/checklist.md`
- 产出模板：`$SKILL/templates/{adr,matrix,boundary,review,tech-debt}.md`
- 机检契约：`$SKILL/schemas/{adr,boundary}.schema.json`
- 门控脚本：`$SKILL/_private/gate_architecture.py`（`--kind adr|boundary`，schema/graph 自动解析）
- openspec design 集成契约：`$SKILL/integrations/openspec-design.md`

## 1. 判场景 + 定产出类型

读 `$SKILL/routing.md` 的「§0 场景索引（18 个）」，把 `$ARGUMENTS` 归入其中一个场景（先匹配「触发问法」）。无法归类时，声明为「通用架构判断」并在交付中标注不确定性。

据此判定**产出类型**（见 `routing.md` §9）：

| 产出类型 | 适用 | 模板 | 门控 |
|---|---|---|---|
| `adr`（+矩阵） | 方案设计与选型（场景 1–5、10–12） | `templates/adr.md`（+`matrix.md`） | `--kind adr` **必过** |
| `boundary` | 模块/服务边界与粒度（场景 11） | `templates/boundary.md` | `--kind boundary` **必过** |
| `review` | 架构评审/设计裁决（场景 4、8） | `templates/review.md` | 模板级（人工确认） |
| `tech-debt` | 技术债/重构优先级（场景 2、3） | `templates/tech-debt.md` | 模板级（人工确认） |

## 2. 委派 architect-worker

用 `task` 工具委派 `architect-worker`，prompt 必须包含：

```
## ⚠️ Agent Identity — You are a SUBAGENT. Execute ONLY. No delegation. No search-agents.
## Role Activation: 架构判断与设计裁决专家
## Skills to Load: architecture-judgment（本次场景=<场景号>，产出类型=<adr|boundary|review|tech-debt>，按 workflow.md 4 步执行）
## Reference Files (必读): $SKILL/workflow.md / $SKILL/checklist.md / <对应模板> / <对应 schema>
## Task: <具体架构任务> + <命中场景号> + 要求产出：<结构化 ADR(JSON,严格按 schema) / 边界说明(JSON) / 评审结论 / 技术债象限>
## 约束: 方法论层(ESS/MTH)重召回；技术实践层(TEC)仅作「选型标尺」，只能写入 standards_refs，不得出现在 decision/rationale/叙述位
## ⛔ No Self-Assessment
## Return Format: {"status":"success|partial|failed","summary":"...","data":{"artifact_path":"","matrix_path":"","graph_refs":[]},"files_created":[],"files_modified":[],"decisions":[],"warnings":[],"errors":[]}
```

## 3. 门控（不通过不放行）

产出后**必须**跑机检，不得凭子 Agent 自述放行（schema 与 graph 自动解析，也可显式 `--schema`/`--graph`）：

```bash
# 产出类型 = adr
python3 "$SKILL/_private/gate_architecture.py" --kind adr \
  --input <adr.json 路径> \
  --graph "$GRAPH" --schema "$SKILL/schemas/adr.schema.json"

# 产出类型 = boundary
python3 "$SKILL/_private/gate_architecture.py" --kind boundary \
  --input <boundary.json 路径> \
  --graph "$GRAPH" --schema "$SKILL/schemas/boundary.schema.json"
```

- **PASS（退出码 0）** → 交付（`adr`/`boundary`）。
- **FAIL（退出码 1）** → 把门控输出的 `checks`/`errors` 原样回传 `architect-worker` 修正，**最多 2 轮**；仍不过则如实报告失败与原因，**不得降级为"口头通过"**。
- `review`/`tech-debt` 为模板级产出，不走机检门控，但须人工确认后定稿。

## 4. 交付

向用户给出：
1. **主产物**：ADR（人读版 Markdown + 结构化 JSON 路径）/ 边界设计说明 / 评审结论 / 技术债象限。
2. **多维权衡矩阵**（涉选型时）。
3. **门控证据**（gate 输出原文，`adr`/`boundary` 类型）。
4. 命中的图谱场景与支撑节点（供用户复核判断依据）。

## 5. 是否需要架构图（主动询问）

交付后**主动询问**用户：「是否需要生成架构图（drawio）？」
- 是 → 主 Agent 委派 `drawio-worker`，其 prompt **必须精确写入** `drawio-reference: 图表规范与导出验证`（不得弱化表述）。
- 否 → 结束。

## 约束

- 技术实践层节点仅作「选型标尺」：`TEC-*` 只能进 `standards_refs`。
- 方法论层重召回，技术层宁缺毋滥（字面不精确命中就不引）。
- `architect-worker` 不含制图（架构图由主 Agent 另委 `drawio-worker`）。
- 门控未过不得声称完成。
