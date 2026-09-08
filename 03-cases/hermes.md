# Hermes Agent 控制论画像（Nous Research）

> **来源**：`05-source/hermes-agent/`（NousResearch 开源，MIT）
> **性质**：自进化 AI 代理，定位"唯一内置学习闭环的智能代理"——跨会话积累知识、自动创建/改进技能、主动持久化记忆。
> **关键结论**：hermes **有独立的 Critic/验证器体系**（E 环在五环中属"最被认真对待、有专属基础设施"的一环，**不是最薄弱**），与 opencode/dsh 式"E 环全是 prompt 层面、无独立传感器"形成鲜明对比。hermes 最突出的环是 **M 环（记忆/状态估计）**，其次是 **T 环（工具容错/看门狗）**；相对最薄弱的是 **P 环（规划/分层）**。

---

## 1. 设定值（用户意图 → 可验证子目标分解）

**承担角色**：hermes 把"设定值"定义为系统提示词中的**验收契约**——用户意图被分解为带显式"接收标准 + 验证指令"的任务模板，而非抽象目标。主要在提示词层 + 任务列表工具层落地，缺乏独立的形式化目标模型。

**关键机制**：
1. **`TASK_COMPLETION_GUIDANCE`**（`agent/prompt_builder.py:349`）：设定值是"可工作的产物、由真实工具输出背书"，明确禁止写了 stub/计划就停。
2. **`OPENAI_MODEL_EXECUTION_GUIDANCE` → `<verification>` 块**（`agent/prompt_builder.py:433`）：完成标准显式列为 5 条——Correctness/Grounding/Formatting/Safety/Completion；"done" 意味着每个具名验收标准都被验证过。
3. **`<external_state_verification>` 块**（`prompt_builder.py:442`）：对外部写操作追加"读回验证目标后才算达成"的硬性验收。
4. **`tools/todo_tool.py::TodoStore`**：内存版修订化任务列表，支持四态 + `parent` 嵌套子任务，跨越上下文压缩后自动重注入。
5. **`/plan`**（`agent/plan_prompt.py`）：规划模式将目标分解为"bite-sized 任务 + 精确文件路径 + 带预期输出的验证命令 + TDD 循环"。

**控制论映射**：KT-ctrl-002（负反馈闭环，目标/规格=设定值 r）+ KT-ctrl-045（规划-执行解耦）；收敛判据指向 KT-ctrl-025（稳态误差验收）。

**强弱项**：**强**——Completion 验收标准工程化（验证/外部写回读/计数器 hard-assert），是"设定值直接携带验证协议"的优秀范例。**弱**——分解靠 prompt 模板与 todo 工具"人肉续写"，无独立 planner 模型或形式化任务图；验证依赖 LLM 自律（`verify_on_stop` 默认 OFF 且仅覆盖 coding 场景）。

---

## 2. E 环 — 传感器 / 评估（Critic / 验证器 / 反馈信号质量）

**承担角色**：hermes 的 E 环是**最被认真对待的独立基础设施**——它把"验证器/Critic"做成了一整套**运行时的证据台账 + 回合末门控 + 独立评审器**。它确实拥有独立的 Critic 系统，这是与 opencode/dsh 最本质的区别。

**关键机制**：
1. **`agent/verification_evidence.py`**：独立验证证据台账（`verification_evidence.db` 持久化）。被动记录"agent 实际证明了什么"——按 session 记录命令类型（lint/typecheck/build/test）、退出码、输出摘要。Deliberately passive：从不跑测试、从不阻塞完成。
2. **`agent/verification_stop.py`**：回合末验证门控（`verify_on_stop`）。编辑代码后若模型想结束而缺"新验证证据"，注入合成 follow-up 提示。排除 prose-only 避免噪音；`max_attempts=2` 防无限纠缠。
3. **`agent/verify/runner.py` + `recipes.py` + `environment.py`**：`hermes verify` 命令，针对项目 recipe 跑完整验证流水线，产出 `VerifyResult`（逐 phase 的 exit_code/duration/output_tail + readiness HTTP probe）。
4. **`agent/review_engine.py`**：`/review` 独立评审器——spawn 一个 full-privilege 后台 subagent，充当"独立 senior reviewer"，读取最近消息 + 打开 PR/diff/跑测试，产出结构化 review 与 verdict。
5. **`agent/coding_context.py`**：`ProjectFacts` 自动探测 `verify_commands`，把验证命令作为结构化事实暴露。
6. **`agent/file_safety.py` / `file_operations._verify_written_hash`**：写文件后哈希回读验证——工具层的"写后验真"传感器。

**控制论映射**：KT-ctrl-035（扰动观测器 DOB）+ KT-ctrl-006（灵敏度/鲁棒性基础）+ KT-ctrl-012（观测噪声 R）+ KT-ctrl-001（开环 vs 闭环）。

**强弱项**：**强（相对最被重视）**——持久化证据台账 + 回合末门控 + 独立 `hermes verify` 强验证器 + 独立 `/review` 评审器 + 工具层写后回读哈希，形成多层传感器。**弱**——①部分默认关闭（`verify_on_stop` 默认 OFF，opt-in）；②`verification_evidence` 是"被动台账"（记账但不裁决）；③`/review` 和 `hermes verify` 是用户/命令触发的离线强验证，不在默认回合循环内自动跑。

---

## 3. T 环 — 执行器 / 工具（工具调用容错）

**承担角色**：hermes 的 T 环是**工程密度极高**的一环——工具执行有完整的并发/超时/授权门控/看门狗/容错状态机，围绕 `agent/tool_executor.py`（84KB）与 `agent/turn_*.py` 组织。

**关键机制**：
1. **`agent/tool_executor.py`**：完整工具执行中间件——并发批处理（`_ConcurrentBatch`）、顺序执行门控（`_StartOrderGate`）、活动心跳（`_run_with_activity_heartbeat`）、超时/取消结果（`_ToolTimeoutResult`/`_ToolCancelledResult`）、授权门（`_ConcurrentToolAuthorizationGate`）。
2. **`agent/iteration_budget.py`**：迭代预算硬限幅——每个 agent（父 500 次、子 50 次）线程安全计数器，超限则停止。
3. **`agent/deadline.py`**：看门狗级 deadline 管理——`run_bounded_sync/async`、`kill_process_tree`、标记 backend suspect、超时诊断 dump。
4. **`agent/turn_tool_validation.py`**：未知工具名（auto-repair + **3-strike partial exit**）与畸形 JSON 参数（retry→recovery），`mixed_invalid_batch` 半错误保留。
5. **`agent/tool_guardrails.py` + `tools/approval.py`**：危险命令审批、self-repo 保护、SSRF 防护。
6. **`agent/moa_loop.py`（Mixture-of-Agents）+ `tools/delegate_tool.py` 并行 fan-out**：多参考模型聚合，best-of-N 异构采样——异质冗余/多数表决实例。

**控制论映射**：KT-ctrl-034（安全边际/硬约束限幅）+ KT-ctrl-033（冗余与仲裁 NMR/TMR）+ KT-ctrl-031/032（鲁棒稳定 vs H∞）+ KT-ctrl-030（模型不确定性）。

**强弱项**：**强（五环中第二强）**——工具层容错工程复杂度罕见：并发/顺序门控、心跳、deadline、空响应预算、3-strike 退出、授权门、guardrails 一应俱全。**弱**——大量容错面向"工具调用/LLM 输出"而非"任务语义"；无显式 worst-case 成本权衡面。

---

## 4. M 环 — 记忆 / 状态估计（会话/上下文管理）

**承担角色**：hermes 自称"唯一内置学习闭环的代理"，M 环是它的**招牌与最强项**——记忆不是单一 context 串，而是**多层记忆架构**（工作记忆/平滑压缩/持久 MEMORY.md/跨会话搜索/外置 memory provider/技能图谱），配合严格的 prompt-caching 不变式。

**关键机制**：
1. **两层压缩**（`agent/compression_facade.py` + `conversation_compression.py` + `turn_context_compaction.py`）：gateway 会话卫生（85% 阈值）+ agent `ContextCompressor`（50% 阈值）。算法先剪旧工具结果（不调 LLM），再选边界，再用 auxiliary 压缩模型生成结构化摘要。
2. **`agent/context_compressor.py`（282KB）**：上下文状态估计核心——带 `MEMORY.md/USER.md always authoritative` 注入、`[SKILL_PRUNED]` 标记、检查点摘要、provider 侧 native 压缩路径。
3. **`agent/memory_manager.py` + `memory_provider.py`**：插件化记忆。内置 provider 恒开 + 最多一个外部 provider，支持多钩子。
4. **`tools/memory_tool.py`**：持久精炼记忆（MEMORY.md=agent 笔记 / USER.md=用户画像），作为会话开始的 FROZEN 快照注入 system prompt；会话中写盘但绝不改 prompt（prefix cache 不变式）。
5. **跨会话记忆**：`session_search`（FTS5 会话搜索）+ `agent/background_review.py`（每轮 fork 一个 agent 问"该存/改哪个 memory/skill?"）+ `curator.py` + `learning_graph.py`（技能自动创建/改进图谱）。
6. **prompt-cache 不变式**（AGENTS.md）：system prompt 字节稳定，唯一允许的 context 变异是 compression。

**控制论映射**：KT-ctrl-011（卡尔曼滤波预测-更新）+ KT-ctrl-014（信息滤波/信息降维）+ KT-ctrl-012（Q/R 权重）+ KT-ctrl-013（分离性原理）。记忆带置信度标记（`[SKILL_PRUNED]`、`VERIFIED_DISPLAY`）——符合"记忆必须带 P 协方差"。

**强弱项**：**强（五环中最强，最高密度）**——真正 Kalman 式多层记忆：工作上下文↔持久记忆↔跨会话↔外置 provider↔技能图谱，每层有明确冻结/权威性/置信度标记。**弱**——无显式"不确定性/P 协方差数值"模型（是离散标记而非连续置信度）；记忆增强依赖后台 fork（可能延迟/丢弃）。

---

## 5. P 环 — 规划 / 分层（慢/快双速规划）

**承担角色**：hermes 的 P 环是**混合型**——没有独立"慢 planner 模型"，而是 skill/工具/委派组织成的分层：高层靠 `delegate_task`（orchestrator/leaf）做委派分层，中层靠 skill 时序抽象，低层靠 todo 工具+子代理执行。规划与执行在执行循环内耦合。

**关键机制**：
1. **`tools/delegate_tool.py`（Subagent Architecture）**：委派分层核心。spawn 独立 AIAgent 子代理：leaf 或 orchestrator 角色、`max_spawn_depth`（默认 1）、单任务 & 批量并行模式、`output_schema` 机器校验契约。父代理只见委派调用+摘要——信息隔离分层。
2. **`tools/delegate_tool_toolsets.py`**：子代理能力空间约束（`DELEGATE_BLOCKED_TOOLS` 禁递归 delegation、kanban）。
3. **skills 即 options**（`SKILLS_GUIDANCE`、`agent/curator.py`）：非平凡工作流自动存档为 skill，作为选项/原语供高层复用——KT-ctrl-046 options 时序抽象。
4. **`/plan`（`agent/plan_prompt.py`）**：慢速规划模式，产出 `.hermes/plans/*.md`。但非滚动重规划。
5. **`agent/kanban_stop.py` + kanban 工具**：任务图编排——`kanban_create` 显式 `parents=[...]` 表达依赖、`kanban_request_review` 释放下游 lane、orchestrator 角色专门做"路由而非实现"。

**控制论映射**：KT-ctrl-045（规划-执行解耦）+ KT-ctrl-046（options/SMDP）+ KT-ctrl-041/043（分层控制/时标分离）+ KT-ctrl-042（多层递阶控制）。滚动重规划（MPC KT-ctrl-044）**较弱**——`/plan` 不自动滚动、无"前瞻 N 步只走 1 步"机制。

**强弱项**：**中偏弱（相对自身各环节最弱）**——委派分层强大，但缺乏 MPC 式滚动重规划、无独立 planner 模型、无预测时域 N 概念；默认是 ReAct 式单循环（`conversation_loop.py` 就是 `while api_call_count < max_iterations`）。**若五环有短板，P 环是相对最弱的一环**。

---

## 6. R 环 — 反思 / 反馈闭环（多轮自我纠偏）

**承担角色**：hermes 的 R 环是**多层、非侵入**的——反思通过独立 fork 的后台评审/后台记忆 review 实现，与主循环解耦，避免污染 prefix-cache；同时在 prompt 层建筑了一套"自证/纠错"纪律。

**关键机制**：
1. **`agent/background_review.py`**：每轮 fork 后评估反思——`AIAgent.run_conversation` 每轮可能 spawn daemon 线程，重放快照问"应保存/更新哪个 skill/memory?"。写直达 memory+skill store，主对话与 prompt cache 从不动。
2. **`agent/review_engine.py` + `review_idle_queue.py`**：`/review` 独立评审（用户触发）——spawn 独立 full-privilege subagent 对最近工作做"独立 senior reviewer"结构化审查。
3. **`agent/verification_stop.py` + `verify_hooks.py`**：回合末纠偏反馈——编辑代码后缺新验证证据时，注入"运行验证→读失败→修复→总结"的继续指令，`max_verify_nudges=3` 限幅。
4. **prompt 层纠错纪律**（`prompt_builder.py`）：`<verification>` 逐条自检、`<external_state_verification>` 写后回读、`<literal_preservation>` 不"修复"畸形 token、`<missing_context>` 不猜。
5. **`agent/curator.py` + `learning_graph.py`**：技能自改进——curator 对 skill 做 LLM review，改进技能内容（I 项累积纠偏）。

**控制论映射**：KT-ctrl-020（PID 三环节：P=即时纠偏、I=background review 累积补偏、D=verification 预判超调）+ KT-ctrl-004（误差收敛）+ KT-ctrl-022（积分 I/防 windup）+ KT-ctrl-025（稳态误差/超调）。

**强弱项**：**中强**——背景评审"fork 不污染缓存 + 不动主循环"设计优雅；PID 三环节影子齐全。**弱**——反思主要是异步/后台/用户触发（background_review 有 2s 取消窗口、/review 需手动、verify_on_stop 默认 OFF），主循环内缺"每步算误差→调 prompt"的显式校正步；反思依赖 LLM 自我认知而非确定性误差信号。

---

## Hermes 控制论画像总结

**整体范式**：hermes 是一个**「强状态估计（M）× 强传感器（E）× 强执行容错（T）的鲁棒闭环」**，控制哲学是"工程化传感器 + 多层记忆 + 不破坏缓存的异步反思"。整体更接近 **「 Kalman 式状态估计 + DOB 式感知偏差补偿 + 看门狗限幅」的鲁棒控制范式**，而非 MPC 式滚动规划范式。

**最突出的环**：**M 环（记忆/状态估计）**——"唯一内置学习闭环的代理"卖点与最密实现：两层压缩 + 持久 MEMORY.md/USER.md + 跨会话搜索 + 外置 provider + 技能图谱 + prompt-cache 恒等。

**最薄弱的环**：**P 环（规划/分层）**——委派分层虽完整，但缺 MPC 滚动重规划、缺独立慢 planner、缺预测时域 N；规划"边做边想"，不"前瞻几步只走一步"。

**关于 E 环的关键对比结论**：与 opencode/dsh 式"E 环最弱、几乎全是 prompt 层面、无独立传感器"**截然不同**——hermes 拥有真实的、独立的 E 环基础设施（verification_evidence 持久化验证台账 / verification_stop 回合末门控 / verify 全套 / review_engine 独立评审 / 工具层写后哈希回读）。但注意：多为用户/命令/编辑场景触发、默认关闭或后台异步，且 verification_evidence 自述"被动记账、不阻塞完成"——**它的 Critic 记账但不裁决**，真正裁决仍依赖 LLM 自觉。所以 hermes 的 E 环是**「基础设施强、半开放半闭环」**——传感器硬件齐备，但多数默认不接入自动回路。

> **一句话**：hermes 是**鲁棒控制 + 多传感器 + 观测器型**Agent，M/T/E 三环工程密度远超同行；若与 opencode/dsh 对比，**E 环由"最弱"反转为"有专属基础设施"**，而相对短板落在了 P 环（滚动规划缺失）。

---

### 📚 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S4 | 一手源码观察 | `05-source/hermes-agent/`（NousResearch 开源，MIT） | 高 |
| SRC-002 | S4 | 一手源码观察 | `agent/prompt_builder.py`（`TASK_COMPLETION_GUIDANCE` / `<verification>` / `<external_state_verification>` 验收契约） | 高 |
| SRC-003 | S4 | 一手源码观察 | `agent/verification_evidence.py`、`agent/verification_stop.py`（证据台账 + 回合末验证门控） | 高 |
| SRC-004 | S4 | 一手源码观察 | `agent/verify/runner.py`、`recipes.py`、`environment.py`、`agent/review_engine.py`（独立验证流水线 + `/review` 评审器） | 高 |
| SRC-005 | S4 | 一手源码观察 | `agent/context_compressor.py`、`agent/file_safety.py`、`file_operations._verify_written_hash`（上下文压缩 + 写后哈希回读） | 高 |
