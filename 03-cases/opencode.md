# opencode v1.18.29 — Agent 控制论画像

> 分析基于 `opencode-src-v1.18.29/` 官方源码（monorepo，`packages/opencode` 主应用 + `packages/core` 核心层 + `packages/cli` 命令框架）与已完成装配层分析（`06-md/`）。映射到 `02-framework/framework.md` 的五大核心环（M/P/R/T/E）× KT-ctrl 概念。

## 1. 设定值（Setpoint）——用户意图 → 可验证子目标

**承担角色**：由「装配层规则（AGENTS.md / opencode.jsonc / instructions）+ Agent 角色分派（plan/build/subagent）+ plan 工具产出的 `.opencode/plans/*.md` 里程碑文件」共同承担，把模糊意图分解为带边界的可验证子目标。

**关键机制**：
- **AGENTS.md / CLAUDE.md / CONTEXT.md 层次化注入**：`session/instruction.ts` 用 `findUp`/`globUp` 从工作目录向上查找 `AGENTS.md`，首次匹配即截断（不层层堆叠）。全局 + 项目 + `~/.claude/CLAUDE.md` 构成目标约束前缀。
- **opencode.jsonc 配置装配**：`agent.ts` `Agent.state` 以 `Permission.merge(defaults, fromConfig(cfg.agent), user)` 组装权限与 prompt；`cfg.instructions` 支持本地/远程路径。
- **plan 模式把目标物质化为可验证里程碑**：`//plan/planmode` 用 `plan_exit` 工具把计划写入 plan 文件，plan-mode Phase 4 要求含「critical files to be modified + verification section describing how to test end-to-end」。
- **并行 explore/general 子目标**：plan-mode Phase 1 要求「launch up to 3 explore agents IN PARALLEL」。
- **question 工具作为目标澄清传感器**：`tool/question.ts` + plan-mode 用 question 工具澄清用户请求歧义。

**控制论映射**：KT-ctrl-045（规划-执行解耦）/ KT-ctrl-041（分层时标）。设定值 r = 用户意图，经 AGENTS.md+plan 分解为 milestone 参考序列。

**强弱项**：**强**——装配层使设定值可溯源、可边界化、可从磁盘重新读；**弱**——设定值主要靠 prompt 文本约束编码，无结构化定量目标函数，验证段是「建议」而非强制门控。

---

## 2. 传感器 / 评估环（E 环）——测"当前执行是否达标"

**承担角色**：由「运行时自动验证（snapshot/file-mutation 变更追踪、日志/错误流、usage/cost 读数）+ 用户 question 交互 + 工具返回的退出码/错误」承担，**没有独立 Critic 模型**，评估信号主要来自环境本身与用户，信噪比中等。

**关键机制**：
- **snapshot 变更追踪（最强 E 信号）**：`core/src/snapshot.ts` 定义 `capture/diff/preview/restore`，`processor.ts` 在每个工具步前后捕获文件树，产出结构化 `Snapshot.FileDiff[]`，`summary.ts computeDiff` 计算会话级 add/deletions/files。
- **工具退出码/错误流作为 raw 观测**：`ai-sdk.ts` 把 `tool-result`/`tool-error`/`error` 归一化为 `LLMEvent`，`value.result.type === "error"` 触发 `failToolCall`，失败信号直接回灌模型。
- **doom_loop 重复性检测（防震荡）**：`processor.ts` L360-379 检测「连续 pending 相同工具+相同输入」触发 `permission.ask("doom_loop")`，DOOM_LOOP_THRESHOLD=3——规则型防震荡（上游拦截）。
- **usage/cost/tokens 预算读数**：`step-finish` 记录 `usage.tokens/cost`，overflow 触发 compaction——成本侧传感器。
- **LSP/reference 作为代码语义观测**：`tool/lsp.ts` 提供 `definition/workspaceSymbol`，让模型读取代码语义。

**控制论映射**：KT-ctrl-012（观测噪声 R）/ KT-ctrl-002（负反馈 e=r−y 的 y 侧）；E 环是「闭环与否」的开关（KT-ctrl-001）。

**强弱项**：🔴 **最弱环**——没有独立 Critic/verifier 模型；没有内置 lint/test 自动触发钩子（依赖 agent 自行调用 shell）；`doom_loop` 与 snapshot diff 是规则型/位移型传感器，**无法测"语义是否达标"**（只能测"是否重复/是否改了文件"）。

---

## 3. 执行器 / 工具环（T 环）——工具调用容错

**承担角色**：由「Effect 事件驱动工具系统 + Permission 仲裁安全阀 + shell/网络工具看门狗 + AI SDK 工具修复」承担，容错主要靠**外部规则（超时/限幅/权限/重试）**而非模型自纠，是**强容错、强安全约束**的执行器。

**关键机制**：
- **shell 工具看门狗（硬超时+kill）**：`tool/shell.ts` L540-554 `Effect.raceAll([handle.exitCode, abort, timeout])`，超时后 `handle.kill({forceKillAfter:"3 seconds"})`——执行器强制限幅（KT-ctrl-034 看门狗）。
- **输出截断限幅（anti-windup）**：`tool/truncate.ts` 对超长输出写入 truncation 目录并返回预览+`[truncated]`；compaction 内 `TOOL_OUTPUT_MAX_CHARS=2000`——防超大观测撑爆上下文。
- **AI SDK 工具调用修复**：`session/llm.ts` `experimental_repairToolCall` 重写大小写不符工具名/失败参数为 `invalid` 兜底。
- **权限仲裁安全阀（ask/allow/deny/always）**：`permission/index.ts` 逐条评估 rule，`deny`→返回、`always`→免问、否则→ask 用户——执行器动作受硬门控。
- **重试/降级**：`session/retry.ts` 对 5xx/429/网络错误做指数退避（RETRY_BACKOFF_FACTOR=2，MAX_RETRIES=5），`context overflow` 明确不重试。

**控制论映射**：KT-ctrl-034（安全边际/硬约束限幅+看门狗）/ KT-ctrl-033（冗余与仲裁）。

**强弱项**：🟢 **强**——shell 超时看门狗、输出截断、权限 deny/ask 仲裁、AI-SDK 工具修复四级硬容错；**弱**——容错以外部规则为主，工具返回错误时缺乏模型级自适应重试。

---

## 4. 记忆 / 状态估计环（M 环）——会话记忆与上下文管理

**承担角色**：由「SQLite 持久化 Session + SessionV2 消息/Part 模型 + compaction 分层压缩 + context-epoch 状态快照」承担，是**两级卡尔曼式记忆**：预测（上下文递推）+ 更新（compaction 融合新观测），但**无跨会话长期记忆**。

**关键机制**：
- **compaction 分层压缩（核心状态估计）**：`session/compaction.ts` 定义 `PRUNE_MINIMUM=20000/PRUNE_PROTECT=40000`、`preserve_recent_tokens` 预算；`select()` 按 `tail_turns` 保留近期轮次，`buildPrompt` 把旧轮压缩成摘要——把历史观测压缩为低维状态。
- **工具输出已压缩标记**：`compaction.ts` serialize 时 `[Old tool result content cleared]`——信息降维，只保留增量。
- **context-epoch 基线**：`core/session/context-epoch.ts` 用 `baseline + baselineSeq` 建立上下文快照基线，实现增量上下文——信息滤波式增量累积（KT-ctrl-014）。
- **session 持久化/父子链**：`session/session.ts` 支持 `parentSessionID` 子会话（subagent 上下文隔离）。
- **revert/unrevert + snapshot 恢复**：`session/revert.ts` 存 snapshot、精确回滚文件变更——M 环反向状态更新。

**控制论映射**：KT-ctrl-011（卡尔曼滤波预测-更新，context-epoch 为预测、compaction 为更新）/ KT-ctrl-014（信息滤波/降维）。

**强弱项**：🟢 **强**——真两级状态估计（context-epoch 增量基线 + compaction 分层压缩 + revert 快照回滚），上下文管理精细；**弱**——**无跨会话长期记忆**，LLM 会话结束后状态即消散，R 环反思产物需经外部链路才升级为长期记忆。

---

## 5. 规划 / 分层环（P 环）——慢/快双速规划

**承担角色**：由「plan agent（慢速规划）+ build agent（快速执行）+ task/subagent 委派 + plan_mode 阶段化 + subagent_depth 分层」承担，**典型的 Plan-and-Execute 双速结构**。

**关键机制**：
- **plan/build 双 Agent 分离**：`agent.ts` 内置 `plan`（disallow edit tools、`plan_exit` allow）与 `build`（默认执行者），plan-mode Phase1→5 阶段化，`plan_exit` 切换。
- **task/subagent 委派分层**：`tool/task.ts` 用 `subagent_type` 选择 explore/general/plan，`subagent_depth`（默认1）限制递归深度，`task_id` 支持恢复同一子会话。
- **并行委派**：plan-mode 明确「launch up to 3 explore agents IN PARALLEL」。
- **背景任务/异步子 Agent**：`tool/task.ts` `background:true` 异步运行，结束后自动通知。

**控制论映射**：KT-ctrl-041（分层时标）/ KT-ctrl-044（MPC 滚动时域）/ KT-ctrl-045（规划-执行解耦）。Plan（慢/低频/抽象）≠ build（快/高频/具体）= 时间尺度分离 ε。

**强弱项**：🟢 **最突出、设计最成型的环**——plan/build 显式分离 + 并行 explore/general + task 委派分层 + subagent_depth 递归限制；**弱**——plan→build 是刚性一次切换，缺 MPC 式滚动重规划（执行中发现问题不能自动回 plan 重算，只能用户介入）。

---

## 6. 反思 / 反馈闭环环（R 环）——多轮自我纠偏

**承担角色**：由「工具错误回灌 + doom_loop 规则拦截 + revert 回滚 + LLM 重试策略 + 用户 feedback」承担，是**弱 R 环**：有错误信号回灌与规则型防震荡，但无 Reflexion 式显式自我打分/元认知反思循环。

**关键机制**：
- **错误回灌**：`ai-sdk.ts` `tool-error` → `failToolCall` 把 `[Tool error]: msg` 写回 assistant 消息，模型下一轮看到错误直接修正。
- **doom_loop 防死循环（D 环节超前抑制）**：`processor.ts` 连续相同工具+输入≥3 次触发 `permission.ask("doom_loop")`，阻断无限循环。
- **revert 用户纠偏**：`session/revert.ts` 用户可回滚到任意历史消息并恢复 snapshot——用户作为外部校正器。
- **LLM 重试策略**：`session/retry.ts` 指数退避 + `retry-after` 尊重 + ProviderError 分类——对扰动（外部干扰）的鲁棒补偿。
- **装配层 Reflection 系统**：`mech-reflection-check`（reflection-worker、pending.json 状态机、/reflection 确认）把每轮经验升级为 MEMORY.md/skills——外部化的 R 环。

**控制论映射**：KT-ctrl-002（负反馈闭环）/ KT-ctrl-021/022/023（PID 三档）/ KT-ctrl-003（误差遗忘）。

**强弱项**：🔴 **弱**——内核 R 环是**开环内隐含的**：只有错误回灌 + 规则型 doom_loop + revert 用户校正，**没有模型自我反思（Reflexion 式"上轮我哪里错了"）**；真正多轮自我纠偏机制（reflection-worker）在装配层而非内核，且须经用户 /reflection 确认——反馈回路是**半开环、依赖外部/人工校验**。

---

## 七大核心环强弱总评

| 环 | 承担角色 | 强度 | 主控概念 |
|---|---------|:---:|---------|
| **设定值** | 装配层规则 + plan 里程碑分解 | 🟡 中强 | KT-ctrl-045 Plan-and-Execute |
| **E 评估** | snapshot 变更追踪 + 工具错误流 + 用户 | 🔴 **最弱** | KT-ctrl-012 观测噪声 R |
| **T 执行** | 工具看门狗 + 权限仲裁 + 输出截断 | 🟢 **最强** | KT-ctrl-034 限幅/看门狗 |
| **M 记忆** | context-epoch + compaction 分层 + revert | 🟢 强 | KT-ctrl-011 卡尔曼式滤波 |
| **P 规划** | plan/build 双速 + task 委派分层 | 🟢 **最强** | KT-ctrl-044/045 MPC + 解耦 |
| **R 反思** | 错误回灌 + doom_loop + revert | 🔴 弱 | KT-ctrl-002 负反馈闭环 |

## opencode 控制论画像总结

**整体范式：经典「前馈-执行 + 部分反馈」的 Plan-and-Execute 控制结构，偏"开环为主 + 局部闭环"。**

- **最突出的环：P 环（规划/分层）+ T 环（执行器安全）**——慢/快双速分层（plan→build→task 委派并行）与执行安全（shell 超时看门狗、权限 ask/deny 仲裁、输出截断防 windup）。像一台装配精度高、安全边界严的"前馈控制器"。
- **最薄弱的环：E 环（评估/传感器）**——几乎只有环境/工具返回作为传感器，缺乏独立 Critic/verifier。这直接导致整个系统偏向开环主导：snapshot diff 只能测"改了哪些文件"，doom_loop 只能测"是否重复"，没有"做对了没"的语义判据。
- **R 环局限**：多轮自我纠偏主要靠错误回灌（局部）+ 外部装配层 reflection 系统（滞后、需人工确认），内核无 Reflexion 式元认知反思循环。

**一句话画像**：opencode 是**「规划与执行解耦、执行器高度安全化、但评估与反思依赖外部/人工」的前馈主导控制器**——擅长"把活干得可控、按计划走"，而"判断干得对不对"与"主动重规划"恰是短板，需由装配层（grill-me 收敛、question 用户传感器、reflection 元认知）补全。

---

### 📚 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S4 | 一手源码观察 | `opencode-src-v1.18.29/`（官方 monorepo：`packages/opencode` 主应用 + `packages/core` 核心层 + `packages/cli` 命令框架） | 高 |
| SRC-002 | S4 | 一手源码观察 | `session/instruction.ts`、`agent.ts`（AGENTS.md 层次化注入 + 权限/prompt 装配） | 高 |
| SRC-003 | S4 | 一手源码观察 | `core/src/snapshot.ts`、`processor.ts`、`summary.ts`（snapshot 变更追踪 E 信号 + doom_loop 检测） | 高 |
| SRC-004 | S4 | 一手源码观察 | `tool/shell.ts`、`tool/truncate.ts`、`permission/index.ts`、`session/retry.ts`（执行器看门狗/限幅/仲裁/重试） | 高 |
| SRC-005 | S4 | 一手源码观察 | `session/compaction.ts`、`core/session/context-epoch.ts`、`tool/task.ts`（M/P 环状态估计与分层委派） | 高 |
