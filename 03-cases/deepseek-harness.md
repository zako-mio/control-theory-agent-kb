# DeepSeek Harness (dsh v0.1.1-rc.2) — 控制论画像

> **对象**：deepseek-harness `v0.1.1-rc.2`（2026-08-21 发布）
> **分析基座**：cordis 插件装配架构，`bundle/base/cordis.patch.yml` 装配 76 核心 + 36 外部 seam（L1 核心集）；源码置于 `packages/` 下
> **控制论角色**：整体是**被控系统 + 强约束执行器 + 事件溯源状态估计器**，而非自评估闭环智能控制器

## 0. 一图总览：dsh 的五环拆解

```
 设定值 r（用户任务）
      │
      ▼
  P 规划（dsh-plan-mode + dsh-goal + dsh-subagent + dsh-tool-todo）──────┐
      │  慢 Planner 出里程碑 / 快 Executor 逐条落地                       │
      ▼                                                                   │
  T 执行器（dsh-tools 三瀑布 + timeout-policy + sandbox + approval）─────► 世界/环境
      │  硬限幅 · 看门狗 · 审批仲裁 · 冗余 · 取消                         │
      │                                                                   │
   实际输出 y ◄──────────────────────────────────────────────────────────┘
      │
      ▼
  M 记忆/状态估计（dsh-session 事件溯源 + dsh-session-projection + dsh-compaction + dsh-token-meter）
  └────────────────► R 反思/反馈（dsh-llm-retry + goal-round-driver + hooks steer + repeat-reminder）◄┘
                          ▲              ◆ 误差信号来源薄弱：
        （E 环：无独立 critic，靠 dsh-tools 契约 / dsh-llm-retry 错误 / dsh-session-stats 资源测量）
```

## 1. 设定值（用户意图 → 可验证子目标）

**承担角色**：把用户原始意图拆解为「事件溯源的目标对象 + 里程碑 todo + 待批计划的提交动作」，并将「计划/执行」两个时标显式解耦。

**关键机制**：
1. **dsh-plan-mode**：`exit_plan_mode` 工具 + `plan:policy` 系统提示段 + `/plan` 命令。计划模式要求产出「decision-complete 计划」，且 exit_plan_mode 必须是该响应唯一且最后的工具调用——把拟案（r）与执行硬性分离。
2. **dsh-goal 目标域三件套**：`ctx.goals` 提供 `create/edit/pause/resume/complete/block/clear` 动词，事件溯源（`goal/change`），目标与续行权限分离——设定值以可暂停/可恢复/可达标的状态机承载。
3. **dsh-goal-round-driver**：把 active 目标转为连续 Goal Round（`<goal_round>` 提示排队 + 计轮数），`agent/pre-step` 校验 reservation——持久目标自动续跑。
4. **dsh-tool-todo**（`todo_write`，整表替换语义）：把大目标切成模型自报的里程碑清单，`allowParallelInProgress` 允许并行。
5. **dsh-agent-presets + dsh-agent-instructions**：per-session `agent.cordis.yml` 组合 + `AGENTS.md` 工作区指令链。

**控制论映射**：KT-ctrl-045（规划-执行解耦）；`exit_plan_mode` 是「计划作为设定值 r 的提交」；`goal 事件溯源`是设定值的可撤销/可恢复封装。关联 KT-ctrl-041（分层控制）。

**强弱项**：⭐**强**——设定值闭环完整（计划确认门 + 持久目标状态机 + 可勾选里程碑，三者可滚动衔接）。⚠️**弱**——计划的「成功判据」是模型自报文本，无自动校验；目标达标与否依赖模型自述，设定值缺乏独立测量支撑。

## 2. E 环 — 评估 / 传感器（最薄弱环）

**承担角色**：**几乎没有独立的「执行达标」测量环节**；dsh 的「传感器」主要是工具输出契约、错误信号、资源/性能测量三类间接信号，而非「目标符合度」的直接测量。

**关键机制**：
1. **dsh-tools 的 canonical tool output 契约**：`pre-execute→execute→post-execute` 三瀑布 + `tools/result` 观察事件；工具结果冻结、快照参数——保证格式可信，不判好坏。
2. **dsh-llm-retry**：把 `request-error` 当作唯一错误信号源，按 retryableCodes/maxRetries/指数退避重试——错误信号用于触发重试而非修正方向。
3. **dsh-session-stats**：`sessionStats` 投影，fold 出 turn/step 数 + 墙钟 + 输出 token——性能型传感器。
4. **dsh-token-meter**：回放感知 token 计量，测量「上下文压力」——资源型传感器，驱动压缩而非评估达标。
5. **dsh-message-feedback / command-feedback**：Like/Dislike + 备注，`feedback/record` **log-only 事件**——用户反馈被采集但不进入控制闭环。

**控制论映射**：KT-ctrl-001（开环 vs 闭环）——dsh 在「效果评估」维度上接近**开环**（无 y 的独立测量源）；对照 KT-ctrl-035（扰动观测器 DOB）/ KT-ctrl-012（观测噪声 R）：缺一个「测输出 y 与目标差」的 Critic 传感器，也缺「低通滤波/信噪比加权」。

**强弱项**：❌**最弱**——全库 grep 无 reflexion/critic/validator 独立模块。执行达标靠三样间接物：工具契约保证**格式**、token-meter 保证**资源不爆**、llm-retry 保证**请求不抛**——但三者都不回答「这一步是否达成了目标子目标」。这直接掐断 R 环的输入，使 dsh 的纠偏带明显变窄。

## 3. T 环 — 执行器 / 工具（最突出环）

**承担角色**：工程化最成熟的执行器——一套带硬限幅、看门狗、审批仲裁、冗余取消、并发分类的工具调用管线。

**关键机制**：
1. **dsh-tools 三瀑布执行管线**：`pre-execute`（allow/deny/ask 策略门）→ `execute`（超时/重试/指标包装）→ `post-execute`（接受/替换/阻断）→ `tools/result` 观察；支持并行/独占并发分类与协作式取消（scheduler）。
2. **dsh-tool-call-timeout-policy**：读每个工具声明的 `timeoutMs` 派生 per-tool deadline，超时替换为 `TOOL_TIMEOUT`——看门狗硬超时。
3. **dsh-sandbox-policy**：**read-only 故障安全默认**，`resolve()` 合并 approved-override > 会话事件折叠 > 部署默认——限幅 + 降级路径的单一所有者。
4. **dsh-user-approval + dsh-permission-presets**：`approval.request` key 决策路由（never/ask）；presets 定义 read-only / workspace-write / danger-full-access 三档——手动仲裁器。
5. **dsh-spill-policy**：超 `maxInlineBytes` 的纯文本结果 spill 到 Store，替换为有界首尾预览——执行器输出 token 限幅（anti-windup 的 token 侧）。
6. **dsh-llm-retry**：指数退避+抖动+`providerRetryAfterMs`——冗余重试（时间域冗余）。
7. **dsh-repeat-tool-reminder**：连续同参调用同一工具达阈值（3/5/8）注入提醒，只 enrich 不 veto——死循环预警但不硬停。
8. **dsh-session-checkpoint-policy**：`tools/execute` 顶层分发前强制 `sessions.flush()`——执行器副作用前的持久化屏障。

**控制论映射**：KT-ctrl-034（饱和/看门狗/anti-windup）、KT-ctrl-033（冗余与仲裁）、KT-ctrl-031（鲁棒稳定性，read-only fail-safe 默认）。

**强弱项**：⭐⭐**最突出**——三瀑布解耦（策略/执行/改写）给了安全阀与限幅的清晰落点；超时+沙箱+审批+溢出+重试+取消形成完整「硬限幅+降级+冗余」链条；read-only 默认是教科书式鲁棒稳定设计。⚠️**小弱点**：repeat-tool-reminder 只提醒不否决；无跨工具的统一预算表（token/并发/成本一次性汇总看门狗）。

## 4. M 环 — 记忆 / 状态估计（次强）

**承担角色**：以「事件溯源（append-only 日志）」为唯一真源，经投影（纯函数 fold）派生可读状态，并用回放感知 token 计量 + 压力触发的信息压缩来管理上下文——典型的「预测-更新」式状态估计，但未显式建模置信度。

**关键机制**：
1. **dsh-session + persistence-jsonl/sqlite**：append-only 事件日志持久化，崩溃/恢复/checkpoint（session-checkpoint-policy 三处 flush 屏障）——状态机以日志为基态，天然可重放。
2. **dsh-session-projection**：`SessionProjectionRegistry`，每个投影单元 `init/apply/view` 三个纯函数，框架订阅一次 `session/event` 驱动所有单元——状态估计器（状态由事件流折叠而出）。
3. **dsh-token-meter**：回放感知 `measure()` + `estimateMessage` 启发式，注册 `usage/contextPressure/breakdown` 三投影——K 增益/协方差代理。
4. **dsh-compaction-basic + tool-result-pruner**：token-meter 驱动压力压缩，先裁工具结果，再 LLM 摘要（`summarizeWithLlm` 复用 KV 前缀缓存），`CONTEXT_WINDOW_EXCEEDED` 时溢出恢复——信息滤波/降维。
5. **dsh-agent-instructions**：`AGENTS.md` 指令链 SHA-1 去重、tombstone 删除标记、compaction 重装载——先验注入 + 漂移校正。

**控制论映射**：KT-ctrl-010（状态估计，事件溯源折叠）、KT-ctrl-011（Kalman 预测-更新，投影=update，token-meter 压力=可观测性门）、KT-ctrl-014（信息滤波/降维）。**缺失**：KT-ctrl-012（观测噪声 R vs 过程噪声 Q，无置信度/协方差）与 KT-ctrl-013（分离性）。

**强弱项**：⭐**次强**——事件溯源+投影提供极高状态保真度与可回放性，「我以为我在哪」由事件日志可审计推导；压缩充分运用 KV 缓存前缀复用。⚠️**弱点**——**缺置信度（P 协方差）**：记忆只记事实不记「我有多确定」，P/R 环无法区分「确信」与「猜测」。

## 5. P 环 — 规划 / 分层控制

**承担角色**：实现慢规划器（计划模式+目标）+ 快执行器（工具调用）+ 多级委派（subagent）+ 滚动重规划（goal-round-driver + ralph）——清晰的 MPC 式分层控制器。

**关键机制**：
1. **dsh-plan-mode**（慢 Planner）：计划模式 + `exit_plan_mode` 提交计划，计划与执行时标解耦。
2. **dsh-goal + dsh-goal-round-driver**（滚动重规划）：持久目标 + 自动 Goal Round 续跑——MPC 滚动时域。
3. **dsh-subagent 多级代理**：`ctx.subagents` 委派 + 上下文/token 隔离，`continuable` 可续跑 + `tool-subagent-report` 回汇报 + `tool-subagent-control` 控制——多层递阶控制（父层经子任务分解协调，子层独立求解）。
4. **dsh-tool-ralph + workflow**：ralph 为 fresh-agent 多轮迭代（每轮 fresh structured-output 子代理，maxRounds=64）；workflow 为 JS 编排脚本驱动子代理序列——options/MDP 时序抽象。
5. **dsh-tool-todo**（里程碑清单）+ **dsh-agent-tool-presentation**（native/code/both 模式选择）——executor 的抽象层级选择。

**控制论映射**：KT-ctrl-044（MPC 滚动时域）、KT-ctrl-043（时标分离 ε）、KT-ctrl-042（多层递阶控制）、KT-ctrl-046（options/SMDP）。

**强弱项**：⭐**强**——dsh 同时具备「计划确认门（plan-mode）」「持久目标滚动（goal-round-driver）」「多级频率分离（subagent/workflow）」三层 P 能力。⚠️**弱**——「规划时域 N」由配置固定（ralph maxRounds、subagent 无前瞻度）；下层 subagent 为单次委派，父层缺持续约束注入/协调变量 λ 更新循环。

## 6. R 环 — 反思 / 反馈闭环（中弱）

**承担角色**：以「事件/错误触发的重试 + 提醒 + hook 强制 steer + 目标续跑」为主的反馈，集中体现为偏 P 项（即时纠偏）；缺独立「误差计算」机构与 I/D 项。

**关键机制**：
1. **dsh-llm-retry**：retryableCodes + maxRetries + 指数退避——P 项即时纠偏。
2. **dsh-compaction-basic**：`CONTEXT_WINDOW_EXCEEDED` 溢出恢复——超调后的降级刹车。
3. **dsh-tool-subagent-report**（reportDelivery: next-step）：子代理在最近步骤边界唤醒父任务并注入上下文——反馈回灌（下级→上级）。
4. **dsh-hooks-claude-code / dsh-hooks-codex**：用户 hooks.json 映射到 harness 7 个拦截点，`agent/turn-stopping` 的 `deny` 时 `agent.steer` 强制续跑；`tools/pre-execute` 可 deny 工具——外部规则对执行的阻断+改向。
5. **dsh-repeat-tool-reminder**：同工具同参连续调用达阈值（3/5/8）注入提醒（只 enrich）——趋势预警（软 D 项）。
6. **dsh-goal-round-driver** + **dsh-agent-instructions**：状态变化驱动的迭代反馈。

**控制论映射**：KT-ctrl-002（负反馈闭环，hooks deny→steer = 实际 y 超限时强制校正）、KT-ctrl-020~023（PID，主要为 P + 弱 D）。**缺失**：KT-ctrl-021/I（积分项，无「反复犯同一错误」的累积补偿）、KT-ctrl-004（误差收敛校正律，无独立「算误差 e=r−y」环节）、KT-ctrl-025（稳态误差/超调验收）。

**强弱项**：⚠️**中弱**——以事件/外力触发为主（request-error、hook deny、repeat-reminder、goal 变更），缺少模型自评（self-critique）这种内源反馈。其最强点（hooks deny→steer、子代理 reportDelivery）是「外力硬中断 + 方向改道」而非「算误差再修正」。由于 E 环无独立 critic，dsh 反馈放大器输入信号质量上限不高——只能对感知到的失败纠偏，难对未感知的偏航闭环。

## 7. dsh 控制论画像总结

**整体范式**：
> 一个 **MPC 式滚动规划 + 配置化强约束执行器 + 事件溯源状态估计器** 的工程化控制器，但**不是自评估闭环智能控制器**。

套进反馈回路：r（设定值）由 plan-mode/goal/todo 生成且够完整；T（执行器）是三瀑布+看门狗+沙箱+审批，闭环中工程化最强；M（状态估计）用事件溯源+投影+压力压缩做到高保真可回放；P（规划）是清晰的慢/快双速分层；**但 E（评估）近开环**——没有 Kritik 测量「实际输出 vs 目标」，于是 R（反思）放大的是「错误信号」而非「误差信号」，纠偏带窄。

**最突出的环**：**T 环（工具执行器）**——三瀑布解耦 + 超时看门狗 + read-only 故障安全 + 审批仲裁 + 溢出限幅 + 协作取消，构成教科书式「硬限幅 + 降级 + 冗余」。

**最薄弱的环**：**E 环（评估/传感器）**——无独立 critic/validator，执行达标仅靠工具契约（格式）、token-meter（资源）、llm-retry（请求不抛）间接度量，不度量目标符合度；耦合地让 R 环退化为「错误触发的重试/提醒/steer」。

**三大设计启示**（对照框架 §7「工程最常踩的坑」）：
1. **踩中坑「过度依赖 E 却无 E」**——有大量反馈触发器却缺高质量误差信号；应在 E 环补「子目标验证器/测试钩子」，让 R 环放大的是误差而非不确定度。
2. **踩中坑「M 环缺置信度」**——事件溯源很精确但不带 P 协方差；goal/todo 断言靠模型自述，P/R 无法区分确信与猜测。
3. **坑「T 环缺看门狗」上做得最好**——read-only fail-safe + timeout-policy + spill + approval 是硬保证，是五环中可复用的范本（亮点：把看门狗/限幅沉淀为纯 apply 函数 + guard 目录的多插件组合）。

**关键证据索引（源码路径）**：
- 装配：`packages/bundle/base/cordis.patch.yml`（76 核心行）
- T 环：`packages/core/tools/src/index.ts`、`packages/guard/timeout-policy/src/index.ts`、`packages/sandbox/sandbox-policy/src/index.ts`、`packages/spill/spill-policy/src/index.ts`
- M 环：`packages/session/session-projection/src/index.ts`、`packages/llm/token-meter/src/index.ts`、`packages/compaction/compaction-basic/src/index.ts`
- P 环：`packages/plan/plan-mode/src/index.ts`、`packages/goal/goal/src/index.ts`、`packages/subagent/subagent/src/index.ts`、`packages/workflow/tool-ralph/src/index.ts`
- R 环：`packages/llm/llm-retry/src/index.ts`、`packages/hooks/hooks-claude-code/src/index.ts`、`packages/subagent/tool-subagent-report/src/index.ts`
- E 环（现状）：`packages/session/session-stats/src/projection.ts`、`packages/feedback/message-feedback/src/index.ts`（log-only）

---

### 📚 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S4 | 一手源码观察 | `packages/bundle/base/cordis.patch.yml`（76 核心 + 36 外部 seam 装配） | 高 |
| SRC-002 | S4 | 一手源码观察 | T 环：`packages/core/tools/src/index.ts`、`packages/guard/timeout-policy/src/index.ts`、`packages/sandbox/sandbox-policy/src/index.ts`、`packages/spill/spill-policy/src/index.ts` | 高 |
| SRC-003 | S4 | 一手源码观察 | M 环：`packages/session/session-projection/src/index.ts`、`packages/llm/token-meter/src/index.ts`、`packages/compaction/compaction-basic/src/index.ts` | 高 |
| SRC-004 | S4 | 一手源码观察 | P 环：`packages/plan/plan-mode/src/index.ts`、`packages/goal/goal/src/index.ts`、`packages/subagent/subagent/src/index.ts`、`packages/workflow/tool-ralph/src/index.ts` | 高 |
| SRC-005 | S4 | 一手源码观察 | R/E 环：`packages/llm/llm-retry/src/index.ts`、`packages/hooks/hooks-claude-code/src/index.ts`、`packages/session/session-stats/src/projection.ts`、`packages/feedback/message-feedback/src/index.ts`（log-only） | 高 |
