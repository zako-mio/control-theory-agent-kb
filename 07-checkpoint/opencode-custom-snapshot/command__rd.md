---
description: 需求发现与澄清（/rd <需求描述>）。加载 requirement-discovery 工作流（定档前置 → 阶段 0–5），委派 requirement-discovery-worker 产出 POV/HMW/product outcome/appetite/最小交接契约，经 gate_requirement_discovery.py 门控后才交付。
agent: build
---

# 需求发现命令

你在 build 模式下执行需求发现任务。用户输入 `/rd <需求描述>` 时，按以下流程执行，不依赖其他文档。
⚠ **`/rd` 一律按复杂档执行**（显式入口优先于自动定档）。

## 0. 前置路径（绑定解析，⛔ 不直写宿主机绝对路径）

```
SKILL = ~/.config/opencode/skills/requirement-discovery      # 能力包根
BIND  = $SKILL/_private/local-bindings.json                  # 绑定文件（由 install 生成）
       → MISSION_ROOT / SOURCE_DIR / TARGET_DIR / TIER_TOOL / GATE_LEDGER
GATE  = $SKILL/_private/gate_requirement_discovery.py
```

## 1. 定档（机械判定，⛔ 不凭感觉）

```bash
python3 "$(python3 -c "import json;print(json.load(open('$SKILL/_private/local-bindings.json'))['TIER_TOOL'])")" --enter "<需求原文>"
```

- 读输出 JSON 的 `hit` / `verdict` / `ev`（**命中证据**）并**在答复中复述**。
- ⚠ **工具不可用 ⇒ 显式报告「定档未执行」（FAIL）**，⛔ **不得**凭感觉选档、⛔ 不得静默降级。

## 2. 判从哪一步进入

读 `$SKILL/routing.md` 的「触发问法 → 进入点」表 与「**不接**清单」；
⚠ 命中「不接」清单 ⇒ **停手并向用户说明应走哪件**（⛔ 不硬做）。

## 3. 委派 requirement-discovery-worker

用 `task` 工具委派 `requirement-discovery-worker`，prompt 必须包含：

```
## ⚠️ Agent Identity — You are a SUBAGENT. Execute ONLY. No delegation. No search-agents.
## Role Activation: 需求发现与澄清专家（需求层·内部意图固化）
## Skills to Load: requirement-discovery（按 workflow.md 从第 <N> 阶段进入）
## Reference Files (必读): $SKILL/workflow.md / $SKILL/checklist.md / <对应模板> / <对应 schema>
## Task: <具体需求任务> + 要求产出：<stage2.json / handoff.json（严格按 schema）>
## 约束: ⛔ 不产 ADR/specs/tasks/代码；需要外部事实时调用 search-methodology（不复制其规则）；
        访谈消费 grill-me 协议（不另造）；每阶段须给「可观察产出」并在「发问点」向用户提问（故事式，不用闭合题）
## ⛔ No Self-Assessment
## Return Format: {"status":"success|partial|failed","summary":"...","data":{"artifact_path":"","kind":"stage2|handoff","tier":"简单档|复杂档","decision_evidence":""},"files_created":[],"files_modified":[],"decisions":[],"warnings":[],"errors":[]}
```

## 4. 门控（**不通过不放行**）

产出后**必须**跑机检，⛔ 不得凭子 Agent 自述放行：

```bash
python3 "$GATE" --kind stage2  --input <stage2.json 路径>
python3 "$GATE" --kind handoff --input <handoff.json 路径>
```

- **执行主体**：`requirement-discovery-worker` 已获放行 `python3 *gate_requirement_discovery.py*`，**门控由产出方自跑**并把输出原文回传；主 Agent 仅做**独立复跑复核**（抽验 1 次）。
- **PASS（退出码 0）** → 交付（⚠ `WARN` 不影响 PASS，但须**原文照列**给用户）。
- **FAIL（退出码 1）** → 用 `task` 工具**带 `task_id` 续跑同一 worker 会话**，附门控 `checks` 原文，做**最小字段补丁**；**最多 2 轮**；仍不过则如实报告失败与原因，⛔ **不得降级为"口头通过"**。
- ⚠ `G-R7` 因 `TIER_TOOL` 不可用而 FAIL ⇒ 属**环境问题**（⛔ 非产出缺陷）⇒ 先修绑定，⛔ **不得**绕过该判据。

## 5. 交付

向用户给出：
1. **主产物**：POV／HMW／product outcome／appetite／四风险（或最小交接契约）；
2. **门控输出原文**（PASS/FAIL ＋ WARN 全文）；
3. **定档判定原文**（含 `ev` 命中证据）；
4. ⚠ **未主张事项**：单用例证据不得定阈值；未实测项标 `UNVERIFIED`。

## 6. 是否需要原型图（主动询问）

交付后**主动询问**用户：「是否需要生成原型/流程图？」是 → 主 Agent 加载 `diagram-lite` skill 按档位出图（默认 T2）；⛔ 不委派制图子 Agent、⛔ 不装绘图 MCP。

## 约束

- ⛔ 不动 `architecture-judgment`／`architect-worker`／`/arch`／`search-methodology`／任一既有 skill。
- ⛔ 不产 ADR／specs／tasks／代码；下游仅**显式交接**（⛔ 不自动接入 `openspec` 链路）。
- ⛔ 不以「门控全绿」「产物被验收」「流程走完」当作「已达成」（`V3` 禁令）。
- 门控未过不得声称完成。
