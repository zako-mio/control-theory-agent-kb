# opencode-custom 改造差异（官方基线 vs 自改造）— 五环与精装度对照

> 一句话定位：本文件以官方 opencode「四 agent + 官方内置 skills + 基础 provider」为基线，逐类拆解自改造装配层的 8 类改动及其对 M/P/R/T/E 五环的双层增量，量化精装度从 2.9 到 3.9 的跃升来源。

## 1. 基线定义

**基线 = 官方 opencode 默认 + 最小常规装配**，仅含：

- **官方四 agent**：`plan`（慢规划，禁 edit）、`build`（快执行）、`general`（通用多步）、`explore`（快速代码探索）——不含任何自定义专职 worker。
- **官方内置 skills**：opencode 自带工具集与内置能力，无个人 skill 库、无 legacy skill。
- **基础 provider**：官方默认模型接入，多 provider 但需用户自填 key/配置，无个人 provider 预设（opencode-go/deepseek/zhipu）。
- **官方内核执行/记忆机制**：shell 看门狗、输出截断、权限 ask/deny/always、AI-SDK 工具修复、SQLite session、compaction 分层压缩、context-epoch 增量基线。
- **明确不含**：自定义 skills / MCP / instructions 协议层 / Reflection 自演化系统 / 专职 worker / 个人 permission 白名单 / compaction 与 variant 调优。基线口径与 `03-cases/opencode.md` 的官方内核画像一致。

## 2. 改造清单（8 类）

| # | 类别 | 改造内容 | 证据 | 五环权重 | 对环影响 |
|---|------|---------|------|---------|---------|
| 1 | **Agent 扩展** | 新增 5 个专职 worker：pdf-worker / drawio-worker / vision-worker / reflection-worker / search-worker（均 hidden subagent，`subagent_depth=2`） | `opencode.jsonc` `agent.*`；`inventory.json` `agents`（9 项） | P 主 + T | P：双速→分层编排平台；T：工具能力按 worker 隔离授权 |
| 2 | **协议层** | auto-mode.md（GATE/COMPLEXITY/variant/reflection 硬门禁/委派协议/编码安全/留档）、search-behavior.md（外部信息实证）、agent-protocol.md（委派/Reflection 自检/MCP 路由）、browser-management.md、downloads.md | `instructions__auto-mode.md`、`instructions__agent-protocol.md`、`instructions__search-behavior.md`；`opencode.jsonc` `instructions` 列表 | P/E/R 跨环 | P：目标物化+推理档分层；E：信源分级+用户确认；R：反思启动即触发 |
| 3 | **Skill 库** | 28 个 skills（cytoscape/kb-construction/openspec 系列/frontend-design/lark-suite 等）+ 11 个 legacy skill（agency-agents/grill-me/opencode-config/resume-builder 等） | `inventory.json` `skills`（28）+ `legacy_skill`（11）；`opencode.jsonc` `skills.paths` | T + E | T：能力密度大幅提升；E：grill-me 收敛 + 方法论 skill 提供评估范式 |
| 4 | **MCP 集成** | 6 个 MCP：vscode-mcp-server / amap / pdf-reader / drawio / drawio-local / headroom（多传输，部分启用） | `opencode.jsonc` `mcp`；`inventory.json` `mcp`（6 项） | T | T：外部工具生态可插拔，pdf/drawio 仅授权对应 worker |
| 5 | **Reflection 自演化系统** | MEMORY.md 跨会话记忆 + pending.json 结构化状态机 + reflection-worker + `/reflection` 命令（三池扫描/签名门禁/容量分层） | `command__reflection.md`；`instructions__agent-protocol.md` Reflection 自检与 4 层输入；`inventory.json` `command` | R（核心） | R：半开环→跨会话闭环自演化（核心反转）；M：补齐长期记忆 |
| 6 | **Provider 扩展** | 3 个 provider 预设：opencode-go（Go 套餐）/ deepseek（官方直连）/ zhipu（GLM），含多模型与 Daily/Deep variant | `opencode.jsonc` `provider.*` | T（基建） | T：模型接入面扩大，支撑专职 worker 与视觉降级路径 |
| 7 | **Compaction / variant 调优** | compaction：`tail_turns=4`、`preserve_recent_tokens=16384`、`reserved=10000`、auto/prune；Daily/Deep variant 分档（max_tokens 8192/16384，reasoning_effort high/max） | `opencode.jsonc` `compaction` 与各模型 `variants`；`instructions__auto-mode.md` 决策边界 | M（基建） | M：状态估计更新预算精细可控；P：推理档随复杂度动态分配 |
| 8 | **Permission 规则** | external_directory 白名单（默认 allow，`~/.ssh|~/.aws|~/.gnupg` deny）+ read auth.json deny + bash 危险命令 deny/ask + edit 分层授权（仅 build 与写入型子 Agent） | `opencode.jsonc` `permission` 及各 agent `permission` | T（安全） | T：执行器最小授权与越权收口，仍非完整沙箱 |

## 3. 五环双层 delta

| 环 | 官方内核 | 装配层增量 | 自改造综合 | 标注 | 关键改造 |
|----|:---:|:---:|:---:|:---:|------|
| **M 记忆** | 3.5 | +0.5 | 4.0 | 增强 | MEMORY.md 跨会话 + pending.json 状态机 + compaction 调优 |
| **P 规划** | 4.5 | +0.5 | 5.0 | 增强 | +5 专职 worker + GATE/COMPLEXITY 推理档 + 契约接力 |
| **R 反思** | 2.0 | +2.5 | 4.5 | **反转** | Reflection 自演化系统（pending.json + reflection-worker + /reflection） |
| **T 执行** | 4.5 | +0.5 | 5.0 | 增强 | 6 MCP + 权限白名单 + 专职 worker 工具隔离 |
| **E 评估** | 2.0 | +2.0 | 4.0 | **反转** | search-behavior 信源分级 + search-worker 证据包 + grill-me/question |

> 补充：设定值（SP）环官方内核约 3.5，装配层以 GATE + COMPLEXITY + grill-me/question 目标澄清 + 契约驱动委派补强至约 4.5（增强），不计入五环但为五环提供目标参考序列。

## 4. 精装度 8 维对比

> 数值唯一来源：`09-src-data/opencode_custom_scores.py`（`SCORES` / `WEIGHTS`）。官方加权 2.88 → 2.9，自改造加权 3.85 → 3.9，均过端到端硬门槛，无一票否决。

| 维度 | 权重 | 官方 | 自改造 | Δ | 依据 |
|------|:---:|:---:|:---:|:---:|------|
| 多Agent编排 | 16 | 3 | 4 | +1 | 官方 plan/build/task 委派原语需用户编排；自改造 +5 专职 worker + 委派协议 + 并行 + subagent_depth=2（无真 DAG 画布） |
| Skill库 | 12 | 2 | 4 | +2 | 官方仅内置工具集无预装 skill 库；自改造 28 skills + 11 legacy（精选库，非市场） |
| 工作流 | 13 | 3 | 4 | +1 | 官方 plan 模式 + 编排原语需用户搭建；自改造 + GATE/COMPLEXITY 门控 + 契约驱动 + 委派接力协议 |
| 模型接入 | 14 | 3 | 4 | +1 | 官方多 provider 需填 key/配置；自改造 3 provider（opencode-go/deepseek/zhipu）+ 多模型 + 手动切换 |
| 一键部署 | 15 | 3 | 3 | 0 | 官方 npm 安装 + 自填 provider key；自改造个人 config 需手动复制装配层，无一键分发 |
| 沙箱 | 10 | 3 | 3 | 0 | 官方 permission ask/deny + snapshot 回滚；自改造 + external_directory 白名单 + /tmp/opencode 隔离区，仍非完整沙箱 |
| MCP生态 | 10 | 3 | 4 | +1 | 官方 MCP 接入/工具节点；自改造 6 MCP（vscode/amap/pdf-reader/drawio×2/headroom）多传输 |
| 记忆 | 10 | 3 | 5 | +2 | 官方 SQLite session + compaction（会话级）；自改造 MEMORY.md 跨会话 + pending.json 结构化状态 + reflection-worker |

## 5. 三大核心发现

**发现一：弱环反转——官方两大最弱环（E/R）被装配层补齐并反转。**
官方内核 E 环（2.0）几乎只有环境/工具返回作为传感器、无独立 Critic；R 环（2.0）仅有错误回灌 + doom_loop + revert，是半开环。自改造以 search-behavior 信源分级 + search-worker 证据包 + grill-me/question 用户确认把 E 环反转至 4.0；以 pending.json 状态机 + reflection-worker + /reflection 签名门禁把 R 环反转至 4.5。补强方式不是改引擎，而是装配层协议 + 专职 worker + 记忆系统。

**发现二：精装度跃升 2.9 → 3.9（Δ+1.0），主要来自记忆与 skill 两维。**
8 维中 6 维提升：记忆 +2（会话级 → 跨会话长期记忆，达满分 5）、skill +2（无预装库 → 28+11 精选库），多Agent/工作流/模型/MCP 各 +1；仅一键部署与沙箱未提升——个人装配层无分发渠道、无完整沙箱，是精装度封顶 3.9 而非更高的主因。

**发现三：从单体双速控制器到分层编排平台。**
官方是「plan/build 双速 + task 委派」的单体结构，最突出的 P/T 环已很强；自改造在此之上叠加 5 个专职 worker 形成「主 Agent 编排 + 专职 worker 执行 + Reflection 自演化」三层平台，P 环升至 5.0、T 环升至 5.0。代价是编排拓扑仍靠协议文本而非 DAG 画布约束，且闭环反思仍需 /reflection 人工确认。

## 6. 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S4 | 一手配置观察 | `07-checkpoint/opencode-custom-snapshot/opencode.jsonc`（agent/provider/mcp/permission/compaction 原文） | 高 |
| SRC-002 | S4 | 一手盘点 | `07-checkpoint/opencode-custom-snapshot/inventory.json`（9 agents / 6 MCP / 28 skills + 11 legacy / 5 instructions / 1 command） | 高 |
| SRC-003 | S4 | 一手协议观察 | `07-checkpoint/opencode-custom-snapshot/instructions__auto-mode.md`（GATE/COMPLEXITY/variant/子Agent规则/压缩模板） | 高 |
| SRC-004 | S4 | 一手协议观察 | `07-checkpoint/opencode-custom-snapshot/instructions__agent-protocol.md`（委派/Reflection自检/MCP路由/编码安全/留档） | 高 |
| SRC-005 | S4 | 一手协议观察 | `07-checkpoint/opencode-custom-snapshot/instructions__search-behavior.md`（外部信息实证/时效准则/信源分级） | 高 |
| SRC-006 | S4 | 一手命令观察 | `07-checkpoint/opencode-custom-snapshot/command__reflection.md`（三池扫描/签名门禁/容量分层/双版本同步） | 高 |
| SRC-007 | S1 | 可复算评分 | `09-src-data/opencode_custom_scores.py`（官方 2.9 / 自改造 3.9，8 维分值单一数据源） | 高 |
| SRC-008 | S1 | 评分模型 | `07-checkpoint/premium-scoring-model.md`（精装度 v2.0：硬门槛 + 8 维加权 + 一票否决） | 高 |
| SRC-009 | S4 | 对照基线 | `03-cases/opencode.md`（官方 opencode 内核五环结构与结论口径） | 高 |
