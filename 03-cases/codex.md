# Codex CLI 控制论画像（OpenAI Codex CLI，Rust 实现）

> **分析对象**：`05-source/codex/`（OpenAI，Rust 实现，BUILD.bazel/MODULE.bazel）
> **结论流派**：Codex 不是单环 Agent，而是 **Rust 实现的"重执行器 + 硬安全阀 + 独立评审器"闭环系统**，五环最突出的 T 环（执行器/安全阀），最薄弱的是 P 环（规划纵深不足，MPC 仅玩具级）。

## 1. 设定值（SP）— 用户意图如何分解为可验证子目标

**承担角色**：设定值不是"预写死目标"，而是**用户意图的轻量包装 + 按岗注入的 AGENTS.md 约束**；正式子目标靠 `goal` 工具显式写入，但默认不主动推断。

**关键机制（源码/文档证据）**：
1. **AGENTS.md / AGENTS.override.md 三档注入**：`codex-rs/codex-home/src/instructions/mod.rs` 定义 `UserInstructionsProvider`，按 `[AGENTS.override.md, AGENTS.md]` 顺序加载。`core/src/context/` 下每个 fragment 实现 `ContextualUserFragment` trait，受 AGENTS.md 硬性约束（无 unbounded items / 无 >10K tokens 项）。
2. **goals 系统（显式目标）**：`codex-rs/ext/goal/src/spec.rs` 定义 `create_goal`/`update_goal`/`get_goal` 工具。description 明确要求"Create a goal only when explicitly requested; do not infer goals from ordinary tasks"——设定值只在显式请求时确立，带 token_budget。
3. **plan 工具（TODO/checklist）**：`core/src/tools/handlers/plan.rs` 的 `update_plan`，在 `ModeKind::Plan` 下被禁用。
4. **orchestrator 角色模板**：`core/templates/agents/orchestrator.md` 要求先给"quick plan with goal, constraints, next steps"。
5. **执行性验证约束**：无独立"子目标验证器"——设定值分解主要靠模型 + 评审器（E 环）事后校验。

**控制论映射**：KT-ctrl-045（规划-执行解耦的契约接口）；设定值对应 KT-ctrl-002（负反馈结构中的 r）。

**强弱项**：强——AGENTS.md 分档注入保证设定值有明确权威来源与硬上限；goal 工具支持带预算的显式目标。弱——目标分解纵深浅（单模型驱动"一条链"，不提供独立高层慢规划器产出里程碑）；默认不推断目标。

---

## 2. 传感器 / 评估（E 环）— 靠什么测"执行达标"

**承担角色**：Codex 在 E 环上有两套独立的"非主模型评审器"——**Guardian 评审器（审批决策）** 与 **Review Task 评审器（代码审查）**，都输出结构化 JSON 含置信度，是真正意义上的独立 Critic 传感器。

**关键机制（源码/文档证据）**：
1. **Guardian 评审器**：`core/src/guardian/mod.rs`——独立评审 session，对 `on-request approval` 自动研判。产出 `GuardianAssessment`（allow/deny + 置信度），"Fail closed on timeout, execution failure, or malformed output"。评审超时 90s，可重试 3 次。
2. **Review Task 评审器（代码审查 Critic）**：`core/src/tasks/review.rs` + `core/templates/review/rubric.md`。评审器输出严格 JSON schema：`findings[]`（含 confidence_score、priority 0-3、code_location）+ `overall_correctness` + `overall_confidence_score`。rubric 详细定义"何时算 bug"判定准则（8 条）与严重度分级（P0-P3）。
3. **工具返回即观测**：`tools/executed_tool_calls.rs` 记录每次工具执行往返。
4. **exec 命令可验证性**：`core/src/exec.rs` 捕获 stdout，超时退出码 124。
5. **Guardian 证据留存**：`core/src/context/guardian_review_evidence.rs` 保留最近 8 条已完成评审（`MAX_RETAINED_REVIEWS = 8`），供反思环复用。

**控制论映射**：KT-ctrl-006（反馈灵敏度/鲁棒性）+ KT-ctrl-012（观测噪声 R）。矛盾点：codex 的 E 环是**安全走廊的 E 环**，而非"任务目标达成度"的 E 环——它测的是"这一步动作是否安全/正确"，而非"整体目标是否达成"。

**强弱项**：强——E 环是 codex 最强的设计：Guardian + Review 评审器都是独立模型 + 独立 session，输出带 confidence_score/priority/overall_correctness 的结构化 JSON，是"Critic 即传感器 + 低通滤波"理论的最佳实现。弱——E 环只管"单步正确/安全"（微观），不管"长程目标达标"（宏观）；Review 评审器默认仅在用户显式请求时触发。

---

## 3. 执行器 / 工具（T 环）— 容错机制

**承担角色**：Codex 的 T 环是**全产品最重的一环**——多层 OS 级沙箱 + 审批策略 + 硬限幅 + 超时看门狗 + 并发限流 + 电路断路器，堪称"执行器 + 安全阀 + 仲裁器"的教科书级实现。

**关键机制（源码/文档证据）**：
1. **多平台 OS 级沙箱**：`sandboxing/src/manager.rs` 定义 `SandboxType::{None, MacosSeatbelt, LinuxSeccomp, WindowsRestrictedToken}`；Linux 用 bwrap + Landlock，macOS 用 Seatbelt（.sbpl 策略文件），Windows 用 Restricted Token + WFP。硬安全边际。
2. **exec 超时看门狗**：`core/src/exec.rs`——`DEFAULT_EXEC_COMMAND_TIMEOUT_MS = 10_000`；`ExecExpiration::{Timeout, DefaultTimeout, Cancellation, TimeoutOrCancellation}`；`IO_DRAIN_TIMEOUT_MS = 2_000` 防孙子进程挂死；`EXEC_OUTPUT_MAX_BYTES` 输出硬上限。
3. **审批策略管线（安全阀）**：`core/src/tools/approvals.rs` + `exec_policy/executable_identity.rs` + `tools/network_approval.rs` + `command_canonicalization.rs`。命令先 canonicalize（解析别名/脚本），shell 命令被拆解成内层命令评估。
4. **sandbox violation 检测**：`sandboxing/src/violation.rs` + `denial.rs`——被沙箱拦截的请求作为反馈回灌。
5. **并发受限**：`core/src/agent/control/execution.rs` 的 `AgentExecutionLimiter`/`AgentExecutionGuard`（RAII 持有 max_threads）。
6. **重试/退避**：`core/src/responses_retry.rs`（INITIAL_CONNECTION_RETRY_DELAY = 5s）＋ `util.rs` 的 `backoff()`（指数退避 + 抖动）。
7. **MCP 工具**：`codex-mcp/src/`，受审批与沙箱约束。

**控制论映射**：KT-ctrl-034（饱和/看门狗/anti-windup）+ KT-ctrl-031（鲁棒稳定性）+ KT-ctrl-030（模型不确定性降级路径）。

**强弱项**：强——T 环是全产品最强：OS 级沙箱×审批策略管线×超时看门狗×输出限幅×并发限制×指数退避。弱——单一模型主循环的"容错"主要靠拦截/超时（被动安全），而非异质冗余表决（主动仲裁）——T 环重"安全阀"轻"冗余"。

---

## 4. 记忆 / 状态估计（M 环）— 会话/上下文管理

**承担角色**：Codex 的 M 环是**"增量上下文 + 硬 token 预算 + 分层压缩/远程压缩"的 Kalman 式记忆**，注意力高度放在"什么该进上下文"。

**关键机制（源码/文档证据）**：
1. **上下文 fragment 体系（ContextualUserFragment）**：`core/src/context/mod.rs`——所有注入 model 的片段实现 trait，AGENTS.md 硬约束"everything injected must have bounded size & hard cap / No items > 10K tokens"。按"信息增量"而非"全量"组织。
2. **上下文窗口/压缩触发**：`core/src/session/context_window.rs` 计算 `ContextWindowTokenStatus`；`state/auto_compact_window.rs` 追踪压缩窗口。
3. **分层压缩**：`core/src/compact.rs`（本地）+ `compact_remote.rs`/`compact_remote_v2.rs`（远程）+ `compact_token_budget.rs`；`SUMMARIZATION_PROMPT`，`COMPACT_USER_MESSAGE_MAX_TOKENS = 20_000`。
4. **持久化**：`thread-store/src/local/`（SQLite，rollout_lineage.rs/writer_lock.rs）、`state/src/sqlite.rs`。
5. **会话级共享状态**：`core/src/rollout_budget.rs`（weighted tokens 的 record_usage）+ `state/session.rs`；`context/rollout_budget.rs` 把剩余 token 作为 developer 片段回灌模型。
6. **World State 渲染**：`core/src/context/world_state/`——把当前环境/权限/协作模式渲染成有界上下文片段。

**控制论映射**：KT-ctrl-010/011（状态估计/Kalman 预测-更新）+ KT-ctrl-014（信息滤波）+ KT-ctrl-012（Q/R 权重）。"No items > 10K tokens + bounded hard cap" 是信息增量预算的直接落地。

**强弱项**：强——上下文信息增量预算纪律严格（bounded/hard-cap/trait 化）；分层压缩 + 远程压缩 + token 预算配套齐全；记忆有 SQLite 持久化。弱——**M 环缺显式"置信度/P 协方差"**：guardian_review_evidence 保留了 confidence_score，但主对话上下文不维护"我对某事实多确信"的状态分布；记忆是"事实串"而非"带不确定度的信念状态"。

---

## 5. 规划 / 分层（P 环）— 慢/快双速规划

**承担角色**：Codex 的 P 环是**"单一模型主循环 + plan 工具轻规划 + 多 Agent 委派"的扁平架构**，不是严格意义上的 MPC 滚动重规划。

**关键机制（源码/文档证据）**：
1. **plan 工具（TODO/checklist）**：`core/src/tools/handlers/plan.rs` 的 `update_plan`，输出 `PlanUpdate` 事件。orchestrator 模板指示"Use the plan tool to explain... Only use it for more complex tasks"——计划是前瞻性清单，非滚动重规划。
2. **多 Agent 委派（V1/V2）**：`core/src/agent/control/*`（spawn.rs/residency.rs）+ `tools/handlers/multi_agents_v2/*`。提供 `spawn_agent`/`send_input`/`wait_agent`/`interrupt_agent`/`followup_task` 等工具。
3. **agent 分层/角色**：`core/src/agent/role.rs` + `agent_graph_store/src/`（记录 agent 树）。`MultiAgentMode::{ExplicitRequestOnly, Proactive}`。有 thread spawn depth 限制。
4. **Agent 执行限制**：`agent/control/execution.rs`、`residency.rs`。
5. **skills 抽象（options）**：`ext/skills/`（SkillMetadata/SkillPolicy/SkillInterface，selection.rs 动态选择）。

**控制论映射**：KT-ctrl-045（规划-执行解耦，这层是真的：高层 Planner 产 milestone + 低层 Executor 单步执行）+ KT-ctrl-046（options/skill 时序抽象）。但**不是 KT-ctrl-044（MPC 滚动）的实现**——codex 没有"前瞻 N 步、只走 1 步、重解"的显式滚动优化器，plan 是一次性 checklist。

**强弱项**：强——多 Agent 委派是 P 环亮点（父 Agent 协调、子 Agent 独立求解，spawn/wait/interrupt/followup 一应俱全，有 depth limit + execution limiter 防失控）。弱——P 环缺 MPC 式滚动重规划；update_plan 是 TODO 清单，模型填一份计划后自行推进；规划时域 N≈整任务；成本/频率 ε 意识弱。

---

## 6. 反思 / 反馈闭环（R 环）— 多轮自我纠偏

**承担角色**：Codex 的 R 环是**"评审结果回灌 + 拒绝电路断路器（anti-windup）+ 重试"的纠偏机制**，偏向"安全纠偏"而非"任务收敛纠偏"。

**关键机制（源码/文档证据）**：
1. **Guardian 拒绝回灌**：`core/src/guardian/review.rs`——评审 deny 后注入 `GUARDIAN_REJECTION_INSTRUCTIONS`："agent must not attempt to achieve the same outcome via workaround, indirect execution, or policy circumvention"——明确禁止策略性绕过（anti-windup）。
2. **Guardian 电路断路器**：`core/src/guardian/mod.rs` 的 `GuardianRejectionCircuitBreaker`——标准策略 3 次连续拒绝即 `InterruptTurn`，Cyber 模型 1 次即中断；`record_denial`/`record_non_denial` 维护连续拒绝计数。防"反复申请同被拒动作"的 windup 限幅。
3. **评审失败反馈（离线）**：`core/src/guardian/feedback.rs`——`record_failed_review` 把失败评审作为 json feedback 落盘。
4. **超时重试指令**：`GUARDIAN_TIMEOUT_INSTRUCTIONS`：超时"not assume unsafe based on timeout alone; you may retry once, or ask for guidance"。
5. **执行失败反馈**：`response_debug-context` + `feedback_tags!` 宏。

**控制论映射**：KT-ctrl-002（负反馈结构）+ KT-ctrl-020~023（PID）+ 尤其 KT-ctrl-022（I 累积 + anti-windup）+ KT-ctrl-025（超调——断路器强制中断 = 防 overshoot）。

**强弱项**：强——R 环有显式 anti-windup 设计（连续拒绝计数 + 中断 + 禁止绕过指令）；评审 error 回灌完善；"重试但最多 3 次/1 次"是有界纠偏。弱——反思偏向"安全纠偏"而非"任务质量纠偏"——主回路没有"任务目标达成度误差 e"的显式计算与回收；不含"随时间累积偏航补偿（I）"意义上的长期任务反思。

---

## Codex 控制论画像总结

**整体控制范式**：Codex 是**"重执行器 + 硬安全阀 + 独立双评审器"的鲁棒闭环系统**，而非典型 MPC 或 PID 型规划 Agent。闭环的"负反馈主信号"来自 Guardian/Review 两个独立评审器（E 环），但这两把尺测的是单步动作的安全/正确性，不是长程目标达成度——因此 Codex 的闭环在**微观（单步正确性）很强**，在**宏观（目标收敛）偏开环**。

**最突出的环**：**T 环（执行器/安全阀）**——OS 级三层沙箱（macOS Seatbelt / Linux bwrap+Landlock / Windows RestrictedToken+WFP）+ 审批策略管线（shell 命令 canonicalize 拆解）+ 超时看门狗 + 输出限幅 + 并发限流 + 指数退避重试，把"执行器硬限幅 + 看门狗"做到了全产品最成熟。

**E 环也是亮点**：Guardian + Review 双独立评审器均输出带 confidence_score 的结构化 JSON，是"Critic 即传感器"的最佳落地（唯一稍弱的是只管单步、非任务整体）。

**最薄弱的环**：**P 环（规划/分层）**——update_plan 是 TODO 清单不是 MPC 滚动重规划；无独立高层慢规划器；多 Agent 委派虽是真分层，但规划时域 N≈整任务、快慢速 ε 意识弱。若按 framework 标准，codex 只做到"慢 Planner 出里程碑"，MPC 是玩具级。

**M 环次弱**：上下文管理纪律极严（bounded/hard-cap/信息增量预算/远程压缩），但缺显式置信度/P 协方差——记忆是"事实串"而非"带不确定度的信念状态"。

**一句话收束**：Codex = **"执行/安全极强、评估（单步）很强、规划与状态估计偏弱"的鲁棒闭环**；被控系统视角看，它是"执行器与安全阀做了冗余强化、但控制器（P）和观测器（M 置信度）相对朴素"的工业级产品——符合 OpenAI 对安全优先、可靠性优先的定位。

---

### 📚 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S4 | 一手源码观察 | `05-source/codex/`（OpenAI，Rust 实现，BUILD.bazel/MODULE.bazel） | 高 |
| SRC-002 | S4 | 一手源码观察 | `core/src/guardian/mod.rs`、`core/src/tasks/review.rs`、`core/templates/review/rubric.md`（Guardian/Review 独立评审器） | 高 |
| SRC-003 | S4 | 一手源码观察 | `sandboxing/src/manager.rs`、`core/src/exec.rs`、`core/src/tools/approvals.rs`（OS 级沙箱 + exec 看门狗 + 审批管线） | 高 |
| SRC-004 | S4 | 一手源码观察 | `core/src/context/mod.rs`、`core/src/session/context_window.rs`、`core/src/compact.rs`、`compact_remote.rs`（上下文 fragment + 分层压缩） | 高 |
| SRC-005 | S4 | 一手源码观察 | `core/src/tools/handlers/plan.rs`、`core/src/agent/control/*`、`agent/role.rs`（plan 工具 + 多 Agent 委派分层） | 高 |
