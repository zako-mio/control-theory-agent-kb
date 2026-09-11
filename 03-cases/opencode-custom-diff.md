# opencode-custom 改造差异（官方基线 vs 自改造）— 五环与精装度对照

> 一句话定位：本文件以官方 opencode「四 agent + 官方内置 skills + 基础 provider」为基线，逐类拆解自改造装配层的 10 类改动及其对 M/P/R/T/E 五环的双层增量，量化精装度从 2.9 到 3.9 的跃升来源。
>
> 版本：v1.3（2026-09-11）。相对 v1.2：改造清单由 8 类扩为 10 类（原第 1/2/3 类的数字与成分刷新，新增「架构判断三层栈」「能力扩展 SOP」两行）；五环与精装度分值维持不变（漂移属能力纵深增长、未跨任何 5 档产品阈值），仅刷新 evidence 与机制叙述。评分口径与 `03-cases/opencode-custom.md`（v1.3 权威画像）一致。

## 1. 基线定义

**基线 = 官方 opencode 默认 + 最小常规装配**（官方内核版本 v1.18.30，相对 v1.2 的 1.18.29 仅版本号标注变化、结构未变），仅含：

- **官方四 agent**：`plan`（慢规划，禁 edit）、`build`（快执行）、`general`（通用多步）、`explore`（快速代码探索）——不含任何自定义专职 worker。
- **官方内置 skills**：opencode 自带工具集与内置能力，无个人 skill 库、无 legacy skill。
- **基础 provider**：官方默认模型接入，多 provider 但需用户自填 key/配置，无个人 provider 预设（opencode-go/deepseek/zhipu）。
- **官方内核执行/记忆机制**：shell 看门狗、输出截断、权限 ask/deny/always、AI-SDK 工具修复、SQLite session、compaction 分层压缩、context-epoch 增量基线。
- **明确不含**：自定义 skills / MCP / instructions 协议层 / Reflection 自演化系统 / 专职 worker / 个人 permission 白名单 / compaction 与 variant 调优。基线口径与 `03-cases/opencode.md` 的官方内核画像一致。

## 2. 改造清单（10 类）

| # | 类别 | 改造内容 | 证据 | 五环权重 | 对环影响 |
|---|------|---------|------|---------|---------|
| 1 | **Agent 扩展** | 装配层 agent 9→10、专职 worker 5→6：新增 pdf-worker / drawio-worker / architect-worker / vision-worker / reflection-worker / search-worker（均 hidden subagent，`subagent_depth=2`） | `opencode.jsonc` `agent.*`；`inventory.json` `agents`（10 项） | P 主 + T | P：双速→分层编排平台；T：工具能力按 worker 隔离授权 |
| 2 | **协议层** | auto-mode.md（GATE/COMPLEXITY/variant/reflection 硬门禁/委派协议/编码安全/留档；原 agent-protocol.md 已并入）、search-behavior.md（外部信息实证）、architecture-behavior.md（架构触发规则/知识分层/openspec design 门控）、browser-management.md、downloads.md | `instructions__auto-mode.md`、`instructions__architecture-behavior.md`、`instructions__search-behavior.md`；`opencode.jsonc` `instructions` 列表（5 项，agent-protocol 已并入 auto-mode） | P/E/R 跨环 | P：目标物化+推理档分层+架构任务路由；E：信源分级+用户确认；R：反思启动即触发 |
| 3 | **Skill 库** | 由 v1.2 的「28 skills + 11 legacy」双根收敛为 **45 个 skill 目录单根统一**（含 `_shared`；41 个可加载 SKILL.md，4 个 `_SKILL.md` 命名不达标未加载），新增 7 个：architecture-judgment / opencode-capability-extension / github-bulk-upload / job-listing-filter / restricted-corpus-acquisition / resumable-content-pipeline / single-source-docs-pipeline | `inventory.json` `skills`（45）；`opencode.jsonc` `skills.paths`（双根已统一，无 `skill/` 引用） | T + E | T：能力密度大幅提升；E：grill-me 收敛 + 方法论 skill 提供评估范式 |
| 4 | **MCP 集成** | 6 个 MCP：vscode-mcp-server / amap / pdf-reader / drawio / drawio-local / headroom（多传输，部分启用） | `opencode.jsonc` `mcp`；`inventory.json` `mcp`（6 项） | T | T：外部工具生态可插拔，pdf/drawio 仅授权对应 worker |
| 5 | **Reflection 自演化系统** | MEMORY.md 跨会话记忆 + pending.json 结构化状态机 + reflection-worker + `/reflection` 命令（三池扫描/签名门禁/容量分层） | `command__reflection.md`；`instructions__auto-mode.md` Reflection 自检与 4 层输入；`inventory.json` `command` | R（核心） | R：半开环→跨会话闭环自演化（核心反转）；M：补齐长期记忆 |
| 6 | **Provider 扩展** | 3 个 provider 预设：opencode-go（Go 套餐）/ deepseek（官方直连）/ zhipu（GLM），含多模型与 Daily/Deep variant | `opencode.jsonc` `provider.*` | T（基建） | T：模型接入面扩大，支撑专职 worker 与视觉降级路径 |
| 7 | **Compaction / variant 调优** | compaction：`tail_turns=4`、`preserve_recent_tokens=16384`、`reserved=10000`、auto/prune；Daily/Deep variant 分档（max_tokens 8192/16384，reasoning_effort high/max） | `opencode.jsonc` `compaction` 与各模型 `variants`；`instructions__auto-mode.md` 决策边界 | M（基建） | M：状态估计更新预算精细可控；P：推理档随复杂度动态分配 |
| 8 | **Permission 规则** | external_directory 白名单（默认 allow，`~/.ssh\|~/.aws\|~/.gnupg` deny）+ read auth.json deny + bash 危险命令 deny/ask + edit 分层授权（仅 build 与写入型子 Agent） | `opencode.jsonc` `permission` 及各 agent `permission` | T（安全） | T：执行器最小授权与越权收口，仍非完整沙箱 |
| 9 | **架构判断三层栈（新机制 A）** | 以「skill（architecture-judgment，内置 167 节点离线方法论 KG）+ worker（architect-worker）+ 行为指令（architecture-behavior.md）+ 命令（/arch）+ 门控（gate_architecture.py --kind adr\|boundary）」五元构成领域级控制回路；门控 FAIL 原样回传修正≤2 轮、不得降级为口头通过 | `skills/architecture-judgment/`（含 `_private/gate_architecture.py`）；`command__arch.md`；`instructions__architecture-behavior.md`；实验7（端到端 12 步，gate 6/6 PASS） | P + E（+T） | P：架构域编排固化为受门控 SOP；E：首个可自动执行的领域级评估门（schema + 图谱机检）；T：产出方 bash deny → 产出/验证天然分离 |
| 10 | **能力扩展 SOP（二阶能力，新机制 B）** | 以 opencode-capability-extension skill 定义「为 opencode 自身新增/补齐能力」的标准流程——诊断孤儿能力 → 统一 skill 双根 → 引用普查防迁移断裂（grep 硬编码）→ 契约先行（交付物 + 结构契约）→ 落地门控与冒烟 → 单一真相源 + 派生对账安装；任何新能力按 Skill + Worker + 行为指令三层栈装配 | `skills/opencode-capability-extension/`；实验8（三层栈闭合 3/3，引用产物 14/14 存在，文档-契约对账 0 问题） | M + P 跨环 | M：单一真相源 + 派生对账保状态一致；P：引用普查为能力迁移提供前置约束；装配层由此获得「为自己系统性新增能力」的二阶元能力 |

## 3. 五环双层 delta

| 环 | 官方内核 | 装配层增量 | 自改造综合 | 标注 | 关键改造 |
|----|:---:|:---:|:---:|:---:|------|
| **M 记忆** | 3.5 | +0.5 | 4.0 | 增强 | MEMORY.md 跨会话 + pending.json 状态机 + compaction 调优（本轮无变化） |
| **P 规划** | 4.5 | +0.5 | 5.0 | 增强 | +6 专职 worker（+architect-worker / 共 6 worker）+ GATE/COMPLEXITY 推理档 + 契约接力 + 架构三层栈 gated SOP（已处 5.0 上限） |
| **R 反思** | 2.0 | +2.5 | 4.5 | **反转** | Reflection 自演化系统 + 【新增弱项】实验10 暴露 MEMORY 硬门禁仅提示词级、权限层 edit allow 覆盖 6/13 agent（含 build），存在制度化旁路 |
| **T 执行** | 4.5 | +0.5 | 5.0 | 增强 | 6 MCP + 权限白名单 + 专职 worker 工具隔离（本轮无变化） |
| **E 评估** | 2.0 | +2.0 | 4.0 | **反转** | search-behavior 信源分级 + search-worker 证据包 + **gate_architecture.py 领域级自动评估门控** + grill-me/question 用户传感器 |

> 补充：设定值（SP）环官方内核约 3.5，装配层以 GATE + COMPLEXITY + grill-me/question + **/arch 架构任务路由 + architecture-behavior 触发约束**补强至约 4.5（增强），不计入五环但为五环提供目标参考序列。

## 4. 精装度 8 维对比

> 数值唯一来源：`09-src-data/opencode_custom_scores.py`（`SCORES` / `WEIGHTS`，本轮未改动）。官方加权 2.88 → 2.9，自改造加权 3.85 → 3.9，均过端到端硬门槛，无一票否决。

| 维度 | 权重 | 官方 | 自改造 | Δ | 依据 |
|------|:---:|:---:|:---:|:---:|------|
| 多Agent编排 | 16 | 3 | 4 | +1 | 官方 plan/build/task 委派原语需用户编排；自改造 10 agent（+6 专职 worker，含 architect-worker）+ 委派协议 + 并行 + subagent_depth=2（无真 DAG 画布，未跨 5 档） |
| Skill库 | 12 | 2 | 4 | +2 | 官方仅内置工具集无预装 skill 库；自改造 45 skill 目录单根统一（41 可加载）+ 新增 7 个（仍为精选个人库、无市场/分发，未跨 5 档） |
| 工作流 | 13 | 3 | 4 | +1 | 官方 plan 模式 + 编排原语需用户搭建；自改造 GATE/COMPLEXITY 门控 + 契约驱动 + 委派接力 + 架构三层栈 gated SOP（无通用可视化工作流/DAG 引擎，未跨 5 档） |
| 模型接入 | 14 | 3 | 4 | +1 | 官方多 provider 需填 key/配置；自改造 3 provider（opencode-go/deepseek/zhipu）+ deepseek-flash V4.1 原生多模态 + @ai-sdk/openai-compatible 图片链路修复（仍非数百模型开箱，未跨 5 档） |
| 一键部署 | 15 | 3 | 3 | 0 | 官方 npm 安装 + 自填 provider key；自改造个人 config 需手动复制装配层，无一键分发 |
| 沙箱 | 10 | 3 | 3 | 0 | 官方 permission ask/deny + snapshot 回滚；自改造 + external_directory 白名单 + /tmp/opencode 隔离区，仍非完整沙箱/VM 隔离 |
| MCP生态 | 10 | 3 | 4 | +1 | 官方 MCP 接入/工具节点；自改造 6 MCP（vscode/amap/pdf-reader/drawio×2/headroom）多传输，2 enabled |
| 记忆 | 10 | 3 | 5 | +2 | 官方 SQLite session + compaction（会话级）；自改造 MEMORY.md 跨会话 + pending.json 结构化状态 + reflection-worker |

> **本轮复评数值未变的原因 = 档位未跨**：v1.3 的漂移（agent 9→10、skill 双根 28+11→单根 45、command 1→2、新增架构三层栈与能力扩展 SOP）属「能力纵深增长」，未触及任何 5 档产品阈值——多Agent/工作流仍未达可视化画布级、skill 仍未达插件市场级、model 仍未达数百模型开箱；封顶因素（一键部署 = 个人 config 无分发、沙箱 = 非 VM 隔离）亦未变。故 8 维分值维持，仅刷新依据。

## 5. 四大核心发现

**发现一：弱环反转——官方两大最弱环（E/R）被装配层补齐并反转（仍成立）。**
官方内核 E 环（2.0）几乎只有环境/工具返回作为传感器、无独立 Critic；R 环（2.0）仅有错误回灌 + doom_loop + revert，是半开环。自改造以 search-behavior 信源分级 + search-worker 证据包 + grill-me/question 用户确认把 E 环反转至 4.0，并新增 gate_architecture.py 领域级自动门控（实验7 gate 6/6 PASS）；以 pending.json 状态机 + reflection-worker + /reflection 签名门禁把 R 环反转至 4.5。补强方式不是改引擎，而是装配层协议 + 专职 worker + 记忆系统。

**发现二：精装度 v1.2 已跃升 2.9 → 3.9（Δ+1.0），v1.3 复评确认能力纵深增长未跨档位（诚实口径）。**
v1.2 完成从 2.9 到 3.9 的档位跃升：8 维中 6 维提升，记忆 +2（会话级 → 跨会话长期记忆，达满分 5）、skill +2（无预装库 → 精选库），多Agent/工作流/模型/MCP 各 +1；仅一键部署与沙箱未提升——个人装配层无分发渠道、无完整沙箱，是精装度封顶 3.9 而非更高的主因。v1.3 的机制增多（架构三层栈、能力扩展 SOP、7 个新 skill）未跨评分模型 5 档产品阈值，故不虚报跃升、维持 3.9，仅刷新 evidence。

**发现三：从单体双速控制器到分层编排平台。**
官方是「plan/build 双速 + task 委派」的单体结构，最突出的 P/T 环已很强；自改造在此之上叠加 6 个专职 worker 形成「主 Agent 编排 + 专职 worker 执行 + Reflection 自演化 + 架构三层栈门控」的分层平台，P 环升至 5.0、T 环升至 5.0。代价是编排拓扑仍靠协议文本而非 DAG 画布约束，且闭环反思仍需 /reflection 人工确认。

**发现四：装配层具备二阶自我扩展能力与领域化门控（新增）。**
其一，能力扩展 SOP（opencode-capability-extension）使装配层不仅拥有若干能力，还拥有「为自己系统性地新增能力」的元能力——实验8 实测三层栈闭合 3/3、引用产物 14/14 存在、契约对账 0 问题；skill 由双根收敛为单根 45 目录即为佐证。其二，架构判断三层栈（实验7：skill→worker→ADR→gate 端到端 12 步、gate 6/6 PASS）是首个「五元齐备」的领域级闭环，把架构判断从开环人工经验变为「目标路由 + 专职执行 + 结构化契约 + 自动测量 + 纠偏回传」的局部闭环。其三，实验10 同时暴露治理强度呈梯度——运行时硬阻（gate 脚本确定性二值判定）> 半运行时（权限 allow/deny）> 纯提示词（GATE / MEMORY 硬门禁）；MEMORY 门禁虽是双条款硬规则，但权限层 edit allow 覆盖 6/13 agent（含 build），存在制度化旁路，关键门禁仍待从提示词层下沉到 runtime/权限层。

## 6. 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S4 | 一手配置观察 | `07-checkpoint/opencode-custom-snapshot/opencode.jsonc`（agent/provider/mcp/permission/compaction 原文） | 高 |
| SRC-002 | S4 | 一手盘点 | `07-checkpoint/opencode-custom-snapshot/inventory.json`（**10 agents / 6 MCP / 45 skills 单根** / 5 instructions / 2 commands） | 高 |
| SRC-003 | S4 | 一手协议观察（新快照） | `07-checkpoint/opencode-custom-snapshot/instructions__auto-mode.md`（GATE/COMPLEXITY/variant/子Agent规则/委派/Reflection自检/压缩模板；原 agent-protocol.md 已并入） | 高 |
| SRC-004 | S4 | 一手协议观察（新快照） | `07-checkpoint/opencode-custom-snapshot/instructions__architecture-behavior.md`（架构触发规则/知识分层/openspec design 门控） | 高 |
| SRC-005 | S4 | 一手协议观察 | `07-checkpoint/opencode-custom-snapshot/instructions__search-behavior.md`（外部信息实证/时效准则/信源分级） | 高 |
| SRC-006 | S4 | 一手命令观察 | `07-checkpoint/opencode-custom-snapshot/command__reflection.md`（三池扫描/签名门禁/容量分层/双版本同步） | 高 |
| SRC-007 | S4 | 一手命令观察（新快照） | `07-checkpoint/opencode-custom-snapshot/command__arch.md`（/arch 场景路由 / architect-worker 委派 / gate_architecture.py 门控流程） | 高 |
| SRC-008 | S4 | 一手能力包观察 | `skills/architecture-judgment/`（SKILL.md + 内置 167 节点方法论知识图谱 + schemas + `_private/gate_architecture.py`） | 高 |
| SRC-009 | S4 | 一手能力包观察 | `skills/opencode-capability-extension/`（能力扩展 SOP：三层栈 / 统一双根 / 引用普查 / 契约+门控+冒烟） | 高 |
| SRC-010 | S4 | 一手实验观察 | `06-experiments/opencode-custom.md` 实验7-10（架构三层栈端到端 gate 6/6 PASS / 能力扩展引用 14/14 / KG 167 节点离线 / MEMORY 权限层旁路） | 高 |
| SRC-011 | S1 | 可复算评分 | `09-src-data/opencode_custom_scores.py`（官方 2.9 / 自改造 3.9，8 维与五环分值单一数据源，本轮未改） | 高 |
| SRC-012 | S1 | 评分模型 | `07-checkpoint/premium-scoring-model.md`（精装度 v2.0：硬门槛 + 8 维加权 + 一票否决） | 高 |
| SRC-013 | S4 | 对照基线 | `03-cases/opencode.md`（官方 opencode 内核五环结构与结论口径，已升 1.18.30） | 高 |
