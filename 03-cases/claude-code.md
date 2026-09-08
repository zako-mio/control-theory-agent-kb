# claude-code（Claude Code）控制论画像

> **分析对象**：`anthropics/claude-code`（agented coding tool, Node.js 18+）
> **证据来源**：`CHANGELOG.md`、`plugins/`（官方插件集）、`examples/settings/`、`examples/hooks/`、`README.md`
> **对照框架**：`02-framework/framework.md`（五大核心环 × 控制论概念）

## 0. 前置定位：claude-code 是一个「外挂 Critic + 执行器安全限幅」的反馈环路

claude-code 的**内核本身没有常驻 Critic**。它的闭环是「主循环（LLM 自主 ReAct）＋ 事件钩子（hooks）外挂的硬约束/评审」构成的。这一点在分析各环时至关重要——真正的"测量/评估/反思"大多不在核心 CLI 代码里，而在 hooks 与官方插件层。这决定了它的控制论范式。

---

## 1. S 环 — 设定值 / 用户意图分解

**承担角色**：把用户的自然语言目标，通过「分层管理文件（CLAUDE.md 层级）+ 计划模式 + 结构化工作流」分解为可验证的子目标与里程碑序列。

**关键机制（证据）**：
1. **CLAUDE.md 层级上下文**：用户级 `~/.claude/CLAUDE.md` → 项目根 `CLAUDE.md` → 嵌套目录 `CLAUDE.md`，支持 `@import` 拉取；受管 `claudeMd` 设置可注入（CHANGELOG L131）。
2. **Plan mode / 计划模式**：`/plan <描述>` 进入计划模式，产出 plan 文件，经 `ExitPlanMode`＋权限确认弹窗审批后切换实现模式（CHANGELOG L3121/L4081/L4600）。
3. **feature-dev 插件 7 阶段工作流**：Discovery → Codebase Exploration（并行 code-explorer）→ Clarifying Questions（"DO NOT SKIP"）→ Architecture Design（并行 code-architect）→ Implementation（"DO NOT START WITHOUT USER APPROVAL"）→ Quality Review（3 个 code-reviewer）→ Summary。
4. **TodoWrite 里程碑追踪**：`feature-dev.md` 核心原则 "Use TodoWrite: Track all progress throughout"。
5. **System prompt 设计模式**：`plugin-dev/skills/agent-development/references/system-prompt-design.md` 规定每个子代理 system prompt 必须含 "Core Responsibilities / Process / Quality Standards / Output Format"。

**控制论映射**：KT-ctrl-041/044（分层/MPC 的 r 信号）；CLAUDE.md 层级等同于上层对下层施约束的协调变量（KT-ctrl-042 多层递阶）。

**强弱项**：**强**——分层约束体系成熟，plan mode 制度化为独立状态，feature-dev 做真正设定值收敛。**弱**——设定值分解仍强依赖模型自律，内核无硬性"分解校验器"。

---

## 2. E 环 — 评估 / 传感器（★ 最薄弱 / 最有争议）

**承担角色**：没有常驻内置 Critic；"执行达标"的测量**以外挂 hooks/插件**在**特定时点**（PostToolUse、Stop、git commit）触发。

**关键机制（证据）**：
1. **独立 Critic 最佳样例 = security-guidance 插件**（`plugins/security-guidance/`）：三层的真·多阶段验证器——层1 `patterns.py` 正则规则（PostToolUse 对 Edit/Write 即时扫描危险模式）；层2 `llm.py` 的 LLM diff 审阅（Stop 钩子用 `git stash create` 基线，送独立 LLM 分析后退出码 2 强制继续修复）；层3 `review_api.py` 的 agentic commit 审阅（两阶段 investigat→self-refute）。
2. **code-review 插件的置信度加权**：4 个并行代理分别审 CLAUDE.md 合规 + bug 扫描；每个 issue 打 0–100 置信度分，<80 阈值过滤误报；再用独立验证子代理二次确认。
3. **pr-review-toolkit**：设 `silent-failure-hunter.md` + `type-design-analyzer.md`（类型设计 1–10 评分）等 6 个测评 agent。
4. **Stop 钩子强制验收**：`hook-development/references/patterns.md` Pattern 2/6——`Stop` 钩子"Review transcript；若改了代码则验证是否跑了测试；未跑则 block"。**注意：这是钩子模式，不是内置自动触发**。
5. **PreCompact 钩子**：压缩前拦截/保留关键信息。

**控制论映射**：KT-ctrl-006（灵敏度/鲁棒性，置信度阈值=回路增益）+ KT-ctrl-012（观测噪声 R，置信度=信噪比）+ KT-ctrl-035（DOB，investigate→refute）。

**强弱项**：**强**——借助插件层实现真正异质、跨上下文、带置信度与自反证的独立 Critic。**弱**——**无内置、非常驻**：核心主循环不自带 test/lint 强制触发，不自带每步 Critic。"跑不跑测试"依赖模型自觉或加 Stop 钩子。**E 环是贴片式的**，不开插件时几乎退化为"开环"。

---

## 3. T 环 — 执行器 / 工具调用容错

**承担角色**：以「Pre/PostToolUse 钩子仲裁 + 权限模式 + 沙箱 + 预算看门狗 + 超时」把工具调用硬限幅、容错地落地。

**关键机制（证据）**：
1. **PreToolUse 钩子仲裁**（`hook-development/SKILL.md` L127-153）：工具执行前可 `approve/deny/ask`（`permissionDecision`），甚至 `updatedInput` 改写工具入参；支持 regex `matcher` 按工具名/参数匹配。
2. **权限/沙箱三层**（`examples/settings/`）：`settings-strict.json` 用 `ask`/`deny`、`disableBypassPermissionsMode`；`settings-bash-sandbox.json` 强制 Bash 进沙箱（`sandbox.enabled`、`network.allowedDomains` 白名单）。
3. **预算看门狗**（CHANGELOG L1208/L1312/L1206）：`--max-budget-usd` 达到上限后"新 spawn 被拒＋运行中后台 agent 被停"；`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`(默认 20) 限制并发；
4. **超时**：钩子配置 `timeout: 30/60/180`；后台子代理不再受一小时时限。
5. **asyncRewake 异步审阅**：后台安全审阅完成后 `rewakeMessage` 唤醒主会话处理，不阻塞主流程。
6. **富余复杂度控制**：subagent 隔离（worktree/isolation）、`maxTurns`、`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` 控制嵌套深度——防递归爆炸。

**控制论映射**：KT-ctrl-034（饱和/看门狗/anti-windup）+ KT-ctrl-033（冗余仲裁）+ KT-ctrl-031/032（鲁棒稳定）。

**强弱项**：**强**——T 环是 claude-code 最发达的一环：hooks 是最丰富的拦截点/安全阀系统，三类执行器、权限确认、沙箱、预算看门狗、超时、异步降级一应俱全。**弱**——钩子体系复杂配置面大；安全强度高度依赖用户是否启用；沙箱仅作用于 Bash 工具（Read/Write/MCP 仍在沙箱外）。

---

## 4. M 环 — 记忆 / 状态估计

**承担角色**：通过「CLAUDE.md 分层上下文 + SessionStart 注入 + 自动压缩(/compact) + 长上下文窗口 + 子代理隔离转录」维护"我在哪、我知道什么"。

**关键机制（证据）**：
1. **CLAUDE.md 层级即上下文树**：多级 + `@import`；`/doctor` 能"检出可裁剪的已提交 CLAUDE.md"——信息降维/蒸馏工具。
2. **SessionStart 钩子装载上下文**：会话开始注入 `additionalContext` 或写入 `$CLAUDE_ENV_FILE`。
3. **Compaction 自动压缩**：auto-compact 在 1M 窗口约 967K tokens 触发，`/compact` 手动，`/context` 显示 token 占用，`PreCompact` 钩子 block/保留关键信息。
4. **长上下文窗口**：1M 上下文（Opus/Fable），`CLAUDE_CODE_DISABLE_1M_CONTEXT` 强制 hold 到 200K。
5. **子代理隔离转录与记忆释放**：subagent 独立 transcript，可 resume/fork；CHANGELOG L679 "subagent 工具结果在离开显示窗口后被释放，修复长会话无界内存增长"——带遗忘的记忆回收。

**控制论映射**：KT-ctrl-011（Kalman 预测-更新）+ KT-ctrl-014（信息滤波）+ KT-ctrl-010（状态估计）+ KT-ctrl-042（分层递阶）。

**强弱项**：**强**——CLAUDE.md 层级上下文是最突出的记忆设计，被 code-review/feature-dev/security-guidance 三方依赖；压缩体系工程化程度高；子代理转录隔离。**弱**——几乎不显式维护"信念置信度/协方差"；压缩是长度阈值驱动而非"信息增量/信噪比"驱动；分层记忆权重（Q/R）没有显式表达。

---

## 5. P 环 — 规划 / 分层控制

**承担角色**：慢速规划层（plan mode＋架构agent）产出里程碑/方案，快速执行层（实现＋子代理逐条落地），滚动推进。

**关键机制（证据）**：
1. **Plan mode = 慢速上层控制器**：独立状态（plan 文件＋ExitPlanMode＋审批），只允许读/只读 Bash（CHANGELOG L1179/L1712），禁止写文件——时标分离的慢层。
2. **feature-dev 分层规划**：code-explorer（探索）→ 多方案 code-architect（Minimal/Clean/Pragmatic 三方案）→ 用户选型 → 实现 → 多 code-reviewer。
3. **子代理委派 = Options 抽象**：`Task` 工具 + `subagent_type` + agent frontmatter；嵌套深度受限制。多子代理并行即并行规划。
4. **MPC 式滚动**：feature-dev 每阶段"规划→问用户→批准→再走下一步"，plan mode 压缩后不丢状态。
5. **TodoWrite 里程碑序列**贯穿 feature-dev 全 7 阶段。

**控制论映射**：KT-ctrl-041（分层控制时标）+ KT-ctrl-043（时间尺度分离 ε）+ KT-ctrl-044（MPC 滚动重规划）+ KT-ctrl-045（规划-执行解耦）。

**强弱项**：**强**——P 环完整且体系化：plan mode＋多方案架构设计＋审批门＋todo 里程碑，真正"慢规划/快执行"与时标分离。**弱**——规划仍强依赖模型与用户交互；plan 里程碑可验证性未内置校验；MPC 预测时域 N 由工作流硬编码（7 阶段）。

---

## 6. R 环 — 反思 / 反馈闭环

**承担角色**：通过 Stop/SubagentStop 钩子拦截"退出"，把评审/测试结果回灌给主循环，强制"没达标不结束"。

**关键机制（证据）**：
1. **Stop 钩子 = 反馈闭环的闸门**（`hook-development/SKILL.md` L181-209）：主 agent 想停时触发，可返回 `approve` 或 `block`＋reason；block 则拒绝停止、驱动继续迭代。
2. **security-guidance Stop 钩子（纠偏）**：用 `asyncRewake` 把 LLM 审阅发现的漏洞回灌，退出码 2 强制继续修复。
3. **ralph-wiggum = 显式自指迭代环**（`plugins/ralph-wiggum/`）：Stop 钩子反复喂给 Claude 同一个 prompt 直到输出 completion promise；`--max-iterations` 是积分项上限（anti-windup）。
4. **code-review / security-guidance 自反证**：validate 子代理 & `AGENTIC_REFUTE_SYSTEM` 对候选 finding 主动"证伪"——R 环放大前先滤波。
5. **PostToolUse 错误回灌**：code-quality 钩子把 lint 结果 `exit 2` 喂回；`systemMessage` 注入上下文。

**控制论映射**：KT-ctrl-002（负反馈闭环）+ KT-ctrl-020（PID 三环节）+ KT-ctrl-004（误差收敛）+ KT-ctrl-025（稳态误差/超调）。

**强弱项**：**强**——利用 hooks"拦截退出"能力做出真正持续的纠偏闭环；multi-layer findings 回灌 + evidence-base 认定让纠偏有依据；ralph-loop 的 integral 循环与 completion-promise 稳态带是经典控制式设计。**弱**——反思是"事件驱动、事后触发"而非"增益可调的 PID"（无 Kp/Ki/Kd 显式整定）；主循环自反思仍主要靠 prompt 引导（open-loop），显式反馈控制在 Stop 时点而非每步。

---

## 7. claude-code 控制论画像总结

| 环 | 承担角色 | 骨架 | KT-id | 强/弱 |
|----|---------|------|-------|:---:|
| **S 设定值** | CLAUDE.md 层级 + plan mode + 工作流分解 | 分层约束 | 041/042/044 | 强 |
| **E 评估** | 外挂独立 Critic（security-guidance/code-review）＋置信度过滤，无内置 | 贴片式传感器 | 006/012/035 | **弱（未内置）** |
| **T 执行器** | hooks 仲裁 + 权限/沙箱 + 预算看门狗 + 超时 | 硬限幅安全阀 | 034/033/031 | **强** |
| **M 记忆** | CLAUDE.md 层级 + auto-compact + 长上下文 + 子代理隔离 | 上下文树+压缩 | 010/011/014 | 强(缺置信度) |
| **P 规划** | plan mode(慢) + 架构agent + 子代理委派(快) | 分层慢/快 | 041/044/045 | 强 |
| **R 反思** | Stop 钩子拦截退出 + findings 回灌 + ralph-loop 积分循环 | 事件驱动纠偏 | 002/020/004/025 | 中 |

### 整体更像哪种控制范式？
claude-code 本质是一个**"外挂 Critic + 执行器硬限幅"的反馈控制系统，而非全系统内建反馈回路**。核心 CLI 主循环是开放的 ReAct 开环基线，真正让系统"闭环"的是 hooks 体系 + 官方插件：它们植入仲裁（PreToolUse=限幅器）、评审（Stop/PostToolUse=传感器+校正）、迭代（Stop block=反馈闸门）。它更接近 **"可插拔的异构冗余传感器 + 执行器饱和限幅" 的鲁棒控制结构**——默认开环，装钩子即闭环。

### 最突出的环
**T 环（工具调用/执行器）**——hooks 是 claude-code 灵魂：三类钩子几乎覆盖控制回路每个拦截点，配合 matcher 正则、权限确认、沙箱网络白名单、`--max-budget-usd` 看门狗、并发/嵌套/预算三组 cap，是"执行器硬限幅 + 看门狗降级"的工程化典范。紧随其后是 P 环（plan mode 慢规划 + 子代理委派快执行 + feature-dev 多架构方案），时标分离最清晰。

### 最薄弱的环
**E 环（评估/传感器）**——没有内置常驻 Critic：核心主循环不自动触发 test/lint，不强制逐轮验证；"达标测量"全部依赖 Stop 钩子 + 插件且多集中在任务结束/提交时点。后果：默认配置下 E 环近乎开环，错误不可及时纠正；即使装 Critic 也多为事后而非过程内。次要短板是 M 环缺显式置信度（压缩按长度阈值而非信息增量）。

### 给知识库的复用要点
- 把 Critic（E）与反思（R）从内核剥离，放进 hooks/插件层，用「置信度阈值 + 两阶段 investigate/refute + 多异质代理」充当带噪传感器的低通滤波与偏差补偿（对应 DOB/KT-ctrl-035）。
- 记忆/状态（M）有优秀的上下文树（CLAUDE.md 层级）与压缩工具，但未做信念置信度——提示"记忆管理"与"状态估计置信度"是独立两层。
- T 环 hooks 是最完整的执行器安全阀参考模板，可作为"限幅器 + 看门狗"的可落地蓝本。

---

### 📚 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S4 | 一手源码观察 | `anthropics/claude-code`（Node.js 18+，`CHANGELOG.md`、`README.md`） | 高 |
| SRC-002 | S4 | 一手源码观察 | `plugins/security-guidance/`（三层多阶段 Critic：`patterns.py` / `llm.py` / `review_api.py`） | 高 |
| SRC-003 | S4 | 一手源码观察 | `plugins/ralph-wiggum/`（Stop 钩子自指迭代环 + `--max-iterations` anti-windup） | 高 |
| SRC-004 | S4 | 一手源码观察 | `examples/hooks/`、`examples/settings/`（hooks 执行器安全阀参考模板） | 高 |
| SRC-005 | S4 | 一手源码观察 | `CHANGELOG.md`（Plan mode、`--max-budget-usd` 预算看门狗、subagent 转录/内存释放等条目） | 高 |
