# PRIME 控制论画像 — 五大核心环分析

> 分析对象：`03-cases/source/prime-agent/`（TypeScript monorepo，packages: agent/ai/coding-agent/tui + prime-agent-runtime Python）
> 核心双抽象：**RLM**（Recursive Language Model，context-as-variables + 常驻 Python REPL）+ **Continual Harness**（持久可编辑的 prompts/memories/skills/subagent specs，`/refine` 证据更新，snapshots 回滚）
> 映射基准：`02-framework/framework.md` 五大核心环主控概念

## 0. 设定值：目标分解机制（Goal ≡ 被控量参考 r）

**承担角色**：把用户的高层意图固化为「可跨轮存活、可预算计量、可显式完成」的持久被控参考值 r，并授权子层继续分解。

**关键机制**：
- **`/goal` 持久目标**（`src/core/goals.ts`）：`GoalState` 记录 `objective / tokenBudget / tokensUsed / timeUsedSeconds / continuationsUsed / status(active|paused|budget_limited|complete|error)`。目标由用户或 host 显式创建，状态写入 `thread_goal_state` custom entry，随会话 JSONL 持久化（`_persistGoalState`）。
- **`goal.complete()` 显式收敛信号**：只有 kernel 侧 `goal.complete()` 标记成功；其余状态（paused/budget_limited/error）都是未收敛。
- **`rlm(...)` 子代理 = 目标下钻分解**：子代继承父模型/provider/skills/tools，把单个子目标封装成独立 context 的 `AgentSession`；子代结果只经 `agent_message` 或文件回流。
- **`/heartbeat` + `rlm_heartbeat` + `prime-agent schedule`**：三套定时/调度表面，把"持续被控指令"注入队列，让目标在无人值守时仍被持续跟追。
- **`createGoalContextMessage` 目标续接上下文**（agent-session.ts:1317,2135）：active 目标在普通轮后由 harness 继续 push `goal_context` continuation 消息，直到 `goal.complete()` 或预算到达。

**控制论映射**：KT-ctrl-002（负反馈闭环结构，目标/规格=设定值 r）+ KT-ctrl-041（分层控制结构，根 agent 定高策略目标，`rlm()` 子层分解执行）。

**强弱项**：**强**——目标有显式状态机、可预算（token budget）、可续接（continuation）、可收敛（complete），比多数 agent 的单轮任务闭环更工程化。**弱**——目标分解粒度靠 LLM 主观性，`objective` 上限 4000 字符且无结构化"子目标清单"模板；目标达成与否缺少机器可验证的结构化判据。

## 1. E 环 — 传感器/评估（测量执行达标）

**承担角色**：为闭环生产"执行是否达标"的反馈信号 y，含质量门（quality gates）、`/refine` 的证据评估、autonomous 的硬件限额。

**关键机制**：
- **Autonomous quality gates**（`src/core/autonomous.ts:273-348`）：`refreshAutonomousQualityGates` 跑配置命令（如 `npm run check`），`exit_code==0` 判定 passed；失败返回 bounded output 给 agent 再试。这是真正的**终端验证器/传感器**。
- **Gate 不重跑优化（DOB 式感知偏差补偿）**：抓 git worktree snapshot（`git status + git diff + untrackedHash`），若 workspace 未变则**不重跑同一失败 gate**（autonomous.ts:296-311），防"反复耗尽的空转"。
- **Autonomous 硬件限额即"传感器量程"**：`maxContinuations=3 / maxTurns=12 / maxTokens=80k / timeoutMs=30min`，`shouldAutonomouslyContinue` 根据 gateResult 与 limitReason 决定是否继续。
- **`/refine` 证据评估（在线反思式"评审器"）**：`planRefinement`（refinement.ts:880-948）把 trajectory、当前 harness state、refinement history 打包给 LLM，要求"small evidence-backed edits"，输出 JSON 后按 before/after snapshot 应用，可回滚。
- **`shouldAutonomouslyContinue` 判定偏"诚实"**：`reason="missing_terminal_evidence"`——当没配置 gate 时，用"是否已产出可观察终态证据"作为弱传感器。

**控制论映射**：KT-ctrl-035（扰动观测器 DOB，gate 不重跑=低通滤波+剔除噪声虚耗）+ KT-ctrl-006（灵敏度与鲁棒性基础，gate 通过=高回路增益）+ 交叉 KT-ctrl-001（开环vs闭环）。

**强弱项**：**强**——quality gates + git-snapshot 变更检测 + bounded output 回灌，是**真正的硬验证器**而非纯 LLM 自评；gate 失败还记录 `lastGateFailureSnapshot` 供补偿。**弱**——默认 gate 为空（`commands:[]`，即默认跑"无测量开环"）；`/refine` 的评估本质仍是同一 LLM 自评（共模偏置），未做异质多评审器仲裁；E 环信噪比取决于用户是否显式配置 gate。

## 2. T 环 — 执行器/工具（容错执行）

**承担角色**：把规划动作以"常驻控制环境 + 限幅 + 看门狗"的方式容错落地，唯一直接触碰外界的环节。

**关键机制**：
- **常驻 Python REPL 作为唯一内建工具**（core/tools/ipython.ts + rlm/rlm.md）：执行、读改文件、跑项目命令、调 skills、委托 subagent 全部从持久 kernel 开始；Python 状态跨 tool call 与 compaction 存活。
- **`bash()` 异步执行 + 可终止句柄（看门狗）**（prime-agent-runtime/src/rlm/bash.py）：`h=bash('npm test')` 立即返回 handle，`h.tail()/h.output()/h.poll()/h.kill()`；kill() 为 SIGTERM 逐级升级到 SIGKILL——T 环强制终止/降级路径。输出用 `_BoundedBuffer`（head+tail 滚动）防内存爆炸。
- **RLM 深度限幅（执行器硬约束 u_sat）**：`RLM_DEPTH < RLM_MAX_DEPTH`；默认 `RLM_MAX_DEPTH=2`，超深度 host 拒绝 `rlm.run` 并 raise 到 Python。
- **Typed host bridge 错误传播**：`status:"error"` 直接 `raise RuntimeError`，不让错误静默。
- **Skills 作为可导入 Python 包（执行器冗余/组合）**：Python-backed skill 把能力封装成 `await <skill_import>.<fn>(...)`，skill 元数据只在 startup prompt，SKILL.md 按需加载。

**控制论映射**：KT-ctrl-034（安全边际/硬约束限幅+看门狗）+ KT-ctrl-030（模型不确定性）+ 交叉 KT-ctrl-031（鲁棒稳定性）。

**强弱项**：**强**——单一常驻 REPL 控制环境让"工具即代码"，容错路径（kill 升级、depth 拦截、协议错误不崩、snapshot 恢复）密集且工程化。**弱**——缺显式冗余仲裁（NMR/TMR/多数表决）：无多模型/多工具链"异质冗余 vote"机制；安全上明确声明"不是 security sandbox"（trust model），执行器以 worker OS 权限运行，属已知风险敞口。

## 3. M 环 — 记忆/状态估计（上下文与状态）

**承担角色**：在长上下文与跨轮/跨会话中保真维护"我现在的状态与经验"，含 compaction、continual harness 持久态、kernel snapshot 回滚。

**关键机制**：
- **Continual Harness 持久状态（状态观测器）**（rlm/harness.py + refinement.ts）：harness_state.json 把 `prompt/memory/skill/subagent` 四类条目 + `refinements[]` 事件按 local/global 双层作用域持久化；Python 侧 `_sync_from_disk()` 用 mtime 检测 host `/refine` 外部改写，防内存陈旧覆盖。
- **Compaction（信息滤波/蒸馏）**（docs/compaction.md）：`contextTokens > contextWindow - reserveTokens` 触发，向后找 cut point 保留 `keepRecentTokens=20k`；生成结构化 summary（读/改文件累计跟踪），`CompactionEntry` 含 `firstKeptEntryId`。
- **Kernel snapshot/restore（状态回滚）**（rlm/repl.py:607-808）：`dill` 序列化命名空间到 `kernel-state.dill`，可 restore；带 per-variable 与 aggregate size cap、corrupt snapshot 降级为空。
- **Subagent 注册表跨持久化**：`rlm.list_subagents()` 父作用域注册表 survives kernel restart/compaction/parent restore；daemon 子代从 parent artifact registry rehydrate。
- **目标/自动模式状态记账**（goals.ts + autonomous.ts）：`GoalState`（token/time/continuation）与 `AutonomousRuntimeState` 作为硬状态估计量，持久化进会话。

**控制论映射**：KT-ctrl-011（卡尔曼滤波 预测-更新，compaction=预测推进、每轮反馈=更新校正）+ KT-ctrl-014（信息滤波/降维，compaction 只保留增量信息）+ 交叉 KT-ctrl-012（观测噪声 R vs 过程噪声 Q，harness 持久态=强先验 Q，工具/gate 反馈=高置信观测 R）。

**强弱项**：**强**——Continual Harness 是**除对话历史外的第二记忆层**，带作用域（local/global）、版本、before/after snapshot、refinement 历史，是可"持续自改进"的记忆基底；compaction + kernel snapshot + subagent registry 三层持久化是其亮点。**弱**——记忆**不显式携带置信度（P 协方差）**：harness 条目只有 version 无"置信度/证据强度"字段，`/refine` 的 evidence 是自由文本非量化；compaction summary 仍是 LLM 生成（可能引入失真），无信息量阈值门控。

## 4. P 环 — 规划/分层控制（慢/快双速 + 递归分解）

**承担角色**：作为"慢大脑"，把长程目标抽象成里程碑序列，并用 RLM 递归子代理 + daemon 后台并发实现快/慢分离的滚动推进。

**关键机制**：
- **RLM 递归子代理 = 规划-执行解耦**（rlm.md + rlm-runtime.md）：父模型保持自身 context 聚焦，Python 持工作状态，子代理只拿到子任务所需 context；`rlm()` 返回 admission handle（立即返回，不回答案）。
- **Daemon-backed 后台代理 = 时标分离（慢变量持宏观状态）**：resident worker 拥有 root session/kernel/schedules/descendants；关闭 terminal 只 detach client 不 stop worker，`prime-agent attach` reattach。慢层规划跨 detach/reattach 存活，快层单轮执行。
- **非阻塞控制循环**（rlm.ts）：`start work → record handle/output location → end turn → later read`；禁止 `time.sleep()` 轮询、禁止长阻塞 await——把"启动"与"等待完成"在时间上解耦。
- **独立并发子代理**（rlm.md:64-71）：`api_review / test_review / integration_audit` 三路独立 spawn 后 end turn，等 `agent_message` 或文件回流——真正的并行/后台编排。
- **`/autonomous` bounded continuation = MPC 式滚动续接**：gate 通过/限额到达才停；每轮注入 continuation prompt 尝试推进，失败 gate 回灌 bounded output 再续——"前瞻一组、只进一步、根据门重算"。

**控制论映射**：KT-ctrl-044（MPC 滚动时域优化）+ KT-ctrl-045（规划-执行解耦）+ KT-ctrl-043（时间尺度分离 ε）。

**强弱项**：**强**——RLM 递归 + daemon + 非阻塞 loop 构成真正的慢/快双速架构，后台并发与 reattach 是少见的"长时间跨会话规划可持续"设计；深度限幅防递归爆炸。**弱**——缺显式"rollout/前瞻树"与"规划时域 N 的显式设定"：不存在独立 planner 实体，规划全依赖单模型每次 `rlm()` 即时判断；子代理间无拓扑调度（无 DAG/依赖先序），并发是"fire-and-forget"式而非按依赖序执行。

## 5. R 环 — 反思/反馈闭环（多轮自我纠偏）

**承担角色**：作为反馈控制器，计算"目标效果 vs 实际输出"的误差并把修正量回灌到持久 harness 状态，PRIME 的**最大亮点**。

**关键机制**：
- **`/refine` 自我改进 harness（核心 R 环实现）**（refinement.ts）：专用 `/refine` 子系统对当前 trajectory 做评审，产出具名 `create/update/delete` edits 到 `prompt/memory/skill/subagent`；`REFINEMENT_SYSTEM_PROMPT` 明示"base system prompt 不可改写，只改 supplemental 状态"。
- **rollback 回滚 = 误差修正的反向撤销**：每次 refine 记录 before/after snapshot，`rollbackOf` 可逆序恢复——负反馈可逆，等于"Kd 式防过度修正的刹车"。
- **Auto-refine review gate（反思触发/滤波）**（refinement.ts:175-185）：内置一台"是否该跑 /refine"的评审器，置于静默边界执行，拒绝一次性噪声/未支持假设/瞬时工具输出（低通滤波 + 防 windup 累积）。触发理由：`turn_interval` / `compact`。
- **执行状态累计纠偏**：`_assistantTurnsSinceAutoRefine` 自上次评审起累计，`_lastAutoRefineReviewAt` 冷却时间戳，防过度反思（PID 的 I 项 windup 防止）。
- **Autonomous gate 失败回灌 = 闭环误差信号注入**：`buildAutonomousGateFailureContinuation` 将失败命令/输出/bounded 提示注入下一轮，"Fix the failure, then produce terminal evidence"——负反馈误差 e 直接回灌执行器。

**控制论映射**：KT-ctrl-002（负反馈闭环结构）+ KT-ctrl-020/023（PID 三环节，P=gate 即时纠偏、I=auto-refine 累积记忆纠偏、D=snapshot 回滚防过度修正）+ KT-ctrl-004（误差收敛）+ 交叉 KT-ctrl-022（积分 I/防 windup）。

**强弱项**：**强（PRIME 最突出环）**——`/refine` + auto-refine review gate + snapshot rollback + 持久 harness 是**业界罕见的"harness 自身可持续改进"闭环**：不重写 immutabble system prompt，只调整 supplement 状态，且带版本/作用域/回滚，实现"反思→固化经验→下次复用"的自我训练机制。**弱**——误差信号仍依赖 LLM 自评（`/refine` 和 auto-refine review 都是同一模型体系），存在共模偏差；`/refine` 的 edits 应用前有 baseline 冲突检测，但未与 gate 的硬测量联动；误差收敛的"稳态带 |e|≤ε_des 验收标准"未显式定义——只靠 gate 二值判定。

## PRIME 控制论画像总结

**整体控制范式**：一个**以"常驻被控环境 + 持久可改进状态"为核心的 自适应/自整定 负反馈控制系统**。它把"模型"当作被控对象，"Python REPL"当作可编程的常驻执行环境（过程），"continual harness"当作可调参的控制器状态（供校正律回灌），"quality gates"当作硬传感器。其精髓是 **R 环（自改进 harness）与 M 环（双层持久记忆）深度耦合，驱动整个闭环"自我整定"**——接近"自适应控制 + 内模控制"的混合体。

**最突出的环**：
- **R 环（反思/反馈闭环）——真正亮点**。`/refine` 子系统（evidence-backed 小步更新 + auto-refine review gate 滤波 + snapshot 可逆回滚 + local/global 作用域）是唯一能把"学习"落到持久且可撤销状态上的机制；配合 M 环 harness 持久层，实现"一次踩坑→固化 lessons→下次复用"。
- **M 环（记忆/状态估计）并列突出**：Continual Harness + compaction（信息蒸馏）+ kernel snapshot + subagent registry 三层持久化，是 R 环自改进的承载体。

**最薄弱的环**：
- **E 环（评估/传感器）** ——软肋。默认 autonomous 无 gate（开环）；`/refine` 与 auto-refine review 的"评估"仍是同一 LLM 自评（共模偏置，无异质评审器/独立验证器仲裁）；gate 是二值 pass/fail，量化误差信号缺失；`/refine` 的 evidence 是自由文本而非可量化度量。即框架强调的"E 环信噪比决定闭环能走多远"，在 PRIME 里正是**最依赖用户显式配置、且无多源交叉验证**的一环。从业者应知：PRIME 把"自我改进"做得很强（R/M），但"自我验证"（E）相对薄弱，**强 R 环放大的是一个信噪比有限的误差信号**——正对应框架 §7 警示"过度依赖 E、信号质量差时 R 环放大的全是不确定度"。

---

### 📚 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S4 | 一手源码观察 | `03-cases/source/prime-agent/`（TypeScript monorepo：packages agent/ai/coding-agent/tui + prime-agent-runtime Python） | 高 |
| SRC-002 | S4 | 一手源码观察 | `src/core/goals.ts`、`agent-session.ts`（`/goal` 持久目标状态机与 goal_context 续接） | 高 |
| SRC-003 | S4 | 一手源码观察 | `src/core/autonomous.ts`（quality gates 硬验证器 + 硬件限额 + gate 不重跑优化） | 高 |
| SRC-004 | S4 | 一手源码观察 | `refinement.ts`、`rlm/harness.py`（`/refine` 证据更新 + Continual Harness 持久态 + snapshot 回滚） | 高 |
| SRC-005 | S4 | 一手源码观察 | `prime-agent-runtime/src/rlm/bash.py`、`rlm/repl.py`（异步 bash 看门狗 + kernel snapshot/restore） | 高 |
