# DeepSeek Harness (dsh v0.2.1-alpha.2) — 控制论画像

> **对象**：deepseek-harness `v0.2.1-alpha.2`（2026-10-09 发布，commit `d743267`；`package.json` version `0.2.1-alpha.2`）
> **分析基座**：cordis 插件装配架构，三层装配口径 —— ① base bundle `packages/bundle/base/cordis.patch.yml`（**95 条 `- id:` 装配行**）；② web-app bundle `packages/bundle/web-app/cordis.patch.yml` + `presets/*.patch.yml`（standard/minimal/ptc/cordis）；③ profile patch（部署/个人覆盖层）。源码置于 `packages/` 下。
> **控制论角色**：整体是**被控系统 + 强约束执行器 + 事件溯源状态估计器**，而非自评估闭环智能控制器

> **版本跨度**：相对上一轮基线 `v0.1.1-rc.2`（2026-08-21）跨 **21 个预发布 tag**（0.1.2-alpha.1 … 0.2.1-alpha.2）。
> **装配口径修正**：基线曾记「`bundle/base/cordis.patch.yml` 装配 76 核心 + 36 外部 seam」。当前该文件 `- id:` 条目为 95 行，与旧「76 + 36」**口径不同、不可直接相减**（旧口径把 base 与 seam 分列统计，现行文件为单层扁平装配表）。本版统一按上栏三层口径描述。
>
> **v1.5 处置（2026-10-13）**：本轮为「dsh 装配层二次追平」，**内核零变化**（仍 `v0.2.1-alpha.2` / `d743267`），故本画像**不重算分值**——官方精装度维持 **3.6**（raw 3.63）。装配层侧的全部增量（R1–R12 轮次登记、8 维 `memory` 4→5、五环 M/R/E 上调、E 环达反转阈值）见变体画像 `03-cases/dsh-custom.md` 与对照分析 `03-cases/dsh-custom-diff.md`；本轮**未新增**官方侧结论，仅更正一处环境事实（见文末「本机环境事实」栏）。

## 0. 一图总览：dsh 的五环拆解

```
 设定值 r（用户任务 / 直人消息）
      │
      ▼
  P 规划（plan-mode[log-only] + goal[权威校验] + subagent[托管 activations]
      │   + tool-subagent-control[send/interrupt/list] + agent-team[实验:roster+DAG] + todo + ralph）
      │  慢 Planner 出里程碑 / 快 Executor 逐条落地 / 委派立即返回 {kind:'activation'}
      ▼                                                                   │
  T 执行器（tools 三瀑布[native|ptc] + PTC 运行时[跨语言] + timeout-policy    │
      │   + sandbox[bwrap/Landlock/Seatbelt/ACL/ssh, fail-closed] + approval + preset）──► 世界/环境
      │  硬限幅 · 看门狗 · 审批仲裁 · 冗余 · 取消 · 跨语言执行                  │
      │                                                                   │
   实际输出 y ◄───────────────────────────────────────────────────────────┘
      │
      ▼
  M 记忆/状态估计（session 事件溯源 v4 + projection + session-query-sqlite[FTS5]
      │   + compaction[generation 门控重试] + token-meter + skill registry[host+per-scope]）
      │
      └──► E 评估（⭐本轮「部分修正」：auto-review 独立 LLM 审查器 —— 但评的是
      │      「动作可授权性」而非「目标达成度」，且 base bundle 默认未装配）
      │      其余：telemetry 族[资源/性能镜像] · verify-*[开发期门控]
      │            workspace-changes[世界变了什么] · message-feedback[log-only]
      │
      └──► R 反思/反馈（llm-retry[对模型不可见] + goal-round-driver + hooks steer/deny
             + repeat-tool-reminder[只 enrich] + repeat-output-guard[检测→停机，不修复]）
                          ▲
                          ◆ 误差信号来源仍薄弱：无 self-critique、无 e=r−y
```

## 1. 设定值（用户意图 → 可验证子目标）— 维持 ⭐强

**承担角色**：把用户原始意图拆解为「事件溯源的目标对象 + 里程碑 todo + 待批计划 + **定时触发**」，并把「计划/执行」两个时标显式解耦；本轮新增**权威校验**与**时间维度设定值**。

**关键机制**：
1. **dsh-plan-mode**（`docs/subsystems/plan.md:11`）：`plan/mode`（`{active: boolean}`）改为 **log-only、整值替换** 的 session 事件——durable 且可回放、**永不进入模型 transcript**；`plan` 单元折叠已提交模式/命令结算/最近请求头记录的模式，resume/fork/compaction 三者均从日志恢复。计划与执行的硬分离从「提示词约定」升级为「持久化日志事实」。
2. **dsh-tool-goal 权威与阈值硬校验**（`packages/goal/tool-goal/README.md:55`）：工具只在**该活跃 driver 内、有 open turn 的精确调用 agent** 上执行；`create/edit/pause/resume` 额外要求**运行时根 agent 当前轮存在直人消息**——subagent 或非人生产者**无法创建/编辑目标**；`blocked` 调用在配置的连续轮数（`blockedAfterConsecutiveRounds`，默认 3）未满前被**机械拒绝**，模型须在 `blocked_reason` 中描述持续条件。自主轮成功 `complete`/`blocked` 后**同时终止物理轮**。
3. **dsh-tool-schedule 把「时间」变成一等设定值**（`docs/subsystems/schedule.md:265`，`docs/tool-catalog.md:35`）：四只工具 `schedule_create/list/delete/update` 支持 `after_seconds`、绝对 `at`、有界定频 `every_seconds`、显式 **IANA 时区**的 `daily`/`weekly` 本地时刻、以及五字段 `cron`；**委派子会话（depth>0）被工具层拒绝**，到期消息恢复原 Session——设定值从「空间维度（哪个 agent）」扩展到「时间维度（何时）」。
4. **dsh-goal-round-driver**：把 active 目标转为连续 Goal Round（`<goal_round>` 提示排队 + 计轮数），`agent/pre-step` 校验 reservation——持久目标自动续跑。
5. **dsh-tool-todo**（`todo_write`，整表替换语义）：把大目标切成模型自报里程碑清单，`allowParallelInProgress` 无默认值、由部署显式声明（`docs/tool-catalog.md:44`）。
6. **dsh-agent-presets + dsh-agent-instructions**：per-session `agent.cordis.yml` 组合 + `AGENTS.md` 工作区指令链。

**控制论映射**：KT-ctrl-045（规划-执行解耦，plan/mode 的 log-only 化把解耦沉淀为持久事件）；KT-ctrl-002（设定值 r = 用户意图，且本轮以「直人消息」为其**权限来源**）；KT-ctrl-041（分层控制）；KT-ctrl-046（options/SMDP，schedule 的触发器即时间域动作原语）。

**强弱项**：⭐**强**——设定值闭环完整（计划确认门 + 持久目标状态机 + 可勾选里程碑 + 时间触发器），且本轮把「谁能改设定值」从软约定升级为**硬校验**（直人消息权威 + 连续轮数下限）。⚠️**弱**——计划的「成功判据」仍是模型自报文本，无自动校验；目标达标与否依赖模型自述，设定值缺乏独立测量支撑。

## 2. E 环 — 评估 / 传感器（**最薄弱环**；本轮判定：**部分修正**）

**承担角色**：**仍无「目标达成度」的独立测量**。本轮出现了一个真实的独立 LLM 审查器（auto-review），但它评的是**单个动作的可授权性**，不是**任务目标的达成度**；其余传感器仍为工具输出契约、错误信号、资源/性能测量三类间接信号。

**关键机制**：
1. **⭐ dsh-experimental-auto-review（本轮新增，须明确记为「部分修正」）**：`packages/experimental/auto-review/`。`REVIEW_POLICY` 自我定位为「**final authorization reviewer for exactly one pending tool call**」（`src/index.ts:41-62`）：对单个待执行工具调用做 low/medium/high 风险分级并给出 allow/deny，allow 即**替代人工审批**、调用立即以完整主机权限执行。挂载点为 `tools/pre-execute` 瀑布（`src/index.ts:684-714`），仅当 session 的 permission preset 为 `AUTO_PRESET` 时介入（:689），`high` 恒 deny 且不可被人类指令降级。⇒ **这是一个真正的独立 LLM 评估器，但评估对象是「动作可授权性」而非「目标达成度」**；且 **base bundle 未装配**（`packages/bundle/base/cordis.patch.yml` 无 auto-review 条目）——**默认关闭，opt-in**。
2. **telemetry 族（`session-telemetry` / `product-telemetry` / `otel`）**：资源与性能镜像（turn/step 计数、墙钟、token、耗时分布），**不含目标符合度字段**。
3. **`verify-*` 脚本族**：**开发期门控**（仓库自检/构建校验），不是运行时评估器——不计入运行时 E 环。
4. **dsh-workspace-changes**：只记录「**世界变了什么**」（文件/工作区差异），不判「变得对不对」。
5. **dsh-tools canonical tool output 契约**：`pre-execute→execute→post-execute` 三瀑布 + `tools/result` 观察事件；工具结果冻结、快照参数——保证格式可信，不判好坏。
6. **dsh-llm-retry**：把 `request-error` 当作错误信号源，按 `retryableCodes`/`maxRetries`/指数退避重试——用于触发重试而非修正方向；且**对模型不可见**（`packages/llm/llm-retry/README.md:50-58`）。
7. **dsh-message-feedback / command-feedback**：Like/Dislike + 备注，`feedback/record` 仍是 **log-only 事件**——用户反馈被采集但不进入控制闭环。

**控制论映射**：KT-ctrl-001（开环 vs 闭环）——在「效果评估」维度上 dsh 仍接近**开环**（无 y 的独立测量源）；auto-review 是**局部闭环的审批传感器**（KT-ctrl-031 鲁棒稳定 / KT-ctrl-033 仲裁），而非 KT-ctrl-035（DOB）式的目标偏移观测器。对照 KT-ctrl-012（观测噪声 R）：仍缺「测输出 y 与目标差」的 Critic 传感器，也缺低通滤波/信噪比加权。

**强弱项**：❌**最弱**（判定由「最弱」**部分修正**为「最弱，但已存在一个非同质的独立评估器」）——本轮必须写清 auto-review，以免读者以为漏检：它证明了 dsh 具备构造独立 LLM 评估器的**架构能力**，但它（a）评授权而非评达标，（b）默认关闭，（c）粒度是单次工具调用而非任务。执行达标仍靠三样间接物：工具契约保证**格式**、token-meter 保证**资源不爆**、llm-retry 保证**请求不抛**——三者都不回答「这一步是否达成了目标子目标」。这仍直接掐断 R 环的输入，使纠偏带明显变窄。

## 3. T 环 — 执行器 / 工具（**最突出环**）— 维持 ⭐⭐

**承担角色**：工程化最成熟的执行器——一套带硬限幅、看门狗、审批仲裁、冗余取消、并发分类的工具调用管线；本轮新增**跨语言执行（PTC）**与**多后端 fail-closed 沙箱**。

**关键机制**：
1. **呈现模式收敛为 `native | ptc`**：`export type ToolPresentationMode = 'native' | 'ptc'`（`packages/core/tools/src/index.ts:672`），配置 union 仅接受二者（:812）；`ptc` 模式下原生工具 schema 从请求中**消失**，模型只拿到 `run_code` 与 SDK 说明——`both` 已被拒绝（旧 `native/code/both` 三态不复存在）。
2. **PTC 真运行时（本轮最大 T 环增量）**：`ctx.ptcRuntime` 是正式 seam（`docs/capability-seams.md:672`），实现有两家——
   - `ptc-runtime-node`（`packages/ptc-runtime/ptc-runtime-node/README.md:12`）：执行模型编写的 TypeScript，**每次调用起一个受管 Node 进程**，宿主函数以 async binding 注入；受**同一套平台沙箱策略**约束（与 Bash 同源），带 elapsed deadline、输出上限、V8 heap limit；取消与完成终止整个托管进程组；**请求受限模式而后端不可用时直接失败**。
   - `experimental-ptc-runtime-python`：实验性 Python 路径，走 fd-3 协议，需 `sandbox` + `sandboxPolicy`，受限运行无法建立约束时以 `sandbox-unavailable` 失败（`docs/upgrade-guide/v0.2.1-alpha.1/python-ptc-sandbox/guide.md:12`）。
3. **沙箱后端族 + fail-closed**：`sandbox-local` 按平台选 runner 链——`linux`: `bwrap` → Landlock；`darwin`: Seatbelt；`win32`: ACL restricted-token；另有 `sandbox-ssh`。**"A platform with no chain, or a chain where every probe fails, is unavailable and fails closed at `confine()`"**（`packages/sandbox/sandbox-local/README.md:71`），`enforcement` 分 full/partial，不可用即 `SANDBOX_UNAVAILABLE`。⚠️ **本机事实（v1.5 更正）**：本机 `bwrap` 已安装且 runner 链**选中 bwrap**，`enforcement=full`——read-only / workspace-write 档在 shell + fs 双侧真强制。v1.4 所记「本机 bubblewrap 与 Landlock 均不可用 → 实际走 fail-closed 分支」**已证伪**（属环境事实更正，非内核设计变化，⛔ 不计入分值变动）。
4. **permission preset 打包 sandbox + approval**：`set(session, name)` 解析 preset（未知名抛错），跑 Auto admission，追加 **log-only** `permission/preset` 事件，再分别经 `setSandboxMode`（dsh-sandbox-policy）与 `setApprovalPolicy`（dsh-user-approval）写入两个 knob，且仅在有效值变化时写（`docs/subsystems/permission-presets.md:73`）；可从内置档**派生 custom/Auto**。
5. **dsh-tool-call-timeout-policy**：读每个工具声明的 `timeoutMs` 派生 per-tool deadline，超时替换为 `TOOL_TIMEOUT`——看门狗硬超时。
6. **dsh-spill-policy**：超 `maxInlineBytes` 的纯文本结果 spill 到 Store，替换为有界首尾预览——输出 token 限幅（anti-windup 的 token 侧）；PTC 子派发经 `tools/ptc-dispatch-log` 瀑布复用同一预览策略。
7. **dsh-llm-retry**：指数退避+抖动+`providerRetryAfterMs`——冗余重试（时间域冗余）。
8. **dsh-repeat-tool-reminder**：连续同参调用同一工具达阈值（3/5/8）注入提醒，**只 enrich 不 veto**——死循环预警但不硬停（`packages/guard/repeat-tool-reminder/README.md:91`）。
9. **dsh-session-checkpoint-policy**：`tools/execute` 顶层分发前强制 `sessions.flush()`——执行器副作用前的持久化屏障。

**控制论映射**：KT-ctrl-034（饱和/看门狗/anti-windup）、KT-ctrl-033（冗余与仲裁）、KT-ctrl-031（鲁棒稳定性，read-only fail-safe 默认 + 沙箱 fail-closed）、KT-ctrl-030（模型不确定性，`ptc` 让执行器在语言维度获得鲁棒性）。

**强弱项**：⭐⭐**最突出**——三瀑布解耦（策略/执行/改写）给了安全阀与限幅的清晰落点；超时+沙箱+审批+溢出+重试+取消形成完整「硬限幅+降级+冗余」链条；**本轮再叠加两项结构性升级**：执行器**跨语言化**（PTC 把可执行面从「工具调用」扩展到「程序」）与沙箱**多后端 fail-closed**（不可用即拒绝，而非静默降级为无约束）。⚠️**小弱点**：repeat-tool-reminder 只提醒不否决；无跨工具的统一预算表（token/并发/成本一次性汇总看门狗）。

## 4. M 环 — 记忆 / 状态估计（**次强**，本轮增量最大之一）— 维持 ⭐

**承担角色**：以「事件溯源（append-only 日志）」为唯一真源，经投影（纯函数 fold）派生可读状态；本轮新增**派生检索索引**与**持久格式代际**——记忆从「可回放」升级为「可回放 + 可检索 + 有代际」。

**关键机制**：
1. **⭐ dsh-session-query-sqlite FTS5 派生索引**（`packages/session-query/session-query-sqlite/README.md:61`）：**确定性排序**（先比实际 FTS5 高亮匹配跨度数，再比文档长度，event time/session id/seq 破平），结果携带受 `snippetChars` 约束的**有界 snippet**（Unicode code point 计），无 provider 私有数值分；分页走 **generation-bound opaque cursor**——`SessionSearchCursor` 绑定精确归一化请求，**语料变化即 `SESSION_QUERY_STALE_CURSOR`**（跨会话 cursor 不跨语料变化存活，会话内 cursor 可存活于无关会话变化）。FTS5 语法（引号/`OR`/`NEAR`/`*`）一律当**数据**而非可执行查询。
2. **五只只读检索工具**（`docs/tool-catalog.md:39`）：`session_event_read` / `session_event_search` / `session_event_trace` / `session_search` / `session_trace`；每个结果都以**不可变的调用 agent session** 授权，隐藏 provider cursor；**opt-in**（需显式装配，需要强制 deadline 或有界内联输出时另挂 timeout/spill 策略）。
3. **⭐ `SESSION_FORMAT_VERSION = 4`**（`packages/core/session/src/types.ts:89`）：v3→v4 把 **user 角色的工具结果提升为 tool 角色消息**；相邻代际迁移**不可变**，且**只读 open 不发布后继格式**——持久层首次获得显式代际契约。
4. **skill 注册表 host + per-scope 分层**（`docs/subsystems/skills.md:13`）：注册按调用上下文的 scope 归档，host 行与仓库插件落全局层、agent preset 的 standing composition 所挂插件落该 preset 层；provider 名**按层唯一**而非进程唯一；读取时合并全局层与查看 scope 链（**最近层同名直接胜出**），发现缓存按解析后的 scope 链作键——先验知识库的分层注入。
5. **压缩恢复改「generation 前进才重试」**（`docs/subsystems/compaction.md:101`）：失败请求恢复走 `agent/request-error`，**仅当 surface replacement generation 前进时**才返回 retry 动作（即使后续摘要工作抛错亦然），取消仍优先——重试条件从「时间/次数」改为「状态确实前进了」。
6. **dsh-token-meter + compaction-basic + tool-result-pruner**：回放感知 `measure()` + 压力触发压缩，先裁工具结果再 LLM 摘要（复用 KV 前缀缓存），`CONTEXT_WINDOW_EXCEEDED` 溢出恢复——信息滤波/降维。
7. **dsh-session-projection**：`SessionProjectionRegistry`，每个投影单元 `init/apply/view` 三纯函数，框架订阅一次 `session/event` 驱动所有单元。

**控制论映射**：KT-ctrl-010（状态估计，事件溯源折叠）；KT-ctrl-011（Kalman 预测-更新，投影=update、token-meter 压力=可观测性门）；KT-ctrl-014（信息滤波/降维）；本轮新增 **KT-ctrl-024（状态可观测性/可观测性判据）**——FTS5 索引 + cursor generation 把「我能否可靠地回看过去」变成可判定的工程属性（`STALE_CURSOR` 即观测失效信号）。**缺失**：KT-ctrl-012（观测噪声 R vs 过程噪声 Q，**仍无置信度/协方差**）与 KT-ctrl-013（分离性）。

**强弱项**：⭐**次强**——事件溯源+投影提供极高状态保真度与可回放性；本轮把记忆推进到「**可检索**（FTS5 确定性排序 + 有界 snippet + generation-bound cursor）」与「**有代际**（v4 不可变迁移 + 只读 open）」，并以 scope 分层注册表承载先验。⚠️**弱点**——**仍缺置信度（P 协方差）**：记忆只记事实不记「我有多确定」，P/R 环无法区分「确信」与「猜测」。

## 5. P 环 — 规划 / 分层控制（本轮增量最大之一）— 维持 ⭐强

**承担角色**：慢规划器（计划模式+目标）+ 快执行器（工具调用）+ 多级委派（subagent）+ 滚动重规划（goal-round-driver + ralph）；本轮委派**统一为托管式 activations**，并新增**全局控制面**与**实验性 Agent Teams 协调回路**。

**关键机制**：
1. **⭐ 委派统一为托管式 activations**（`docs/upgrade-guide/v0.2.1-alpha.1/subagent-activations/guide.md:12`）：`dsh-tool-subagent` **删除** `backgroundMode`/`enableRunInBackground`/模型参数 `run_in_background`；每次委派接受子代理后立即返回 **`{kind: 'activation', subagentId}`**，最终答案经**父级完成通知**投递；foreground 结果与 `{kind:'background', jobId}` 结果**一并移除**，子代理**不再经 `job_output`/`job_kill` 收集或停止**——委派生命周期从「任务收集模型」改为「运行时托管模型」。
2. **provider 契约明确 6 个**（`docs/subsystems/subagent.md:326`）：`spawn` / `fork` / `acp` / `codex` / `claude-code` / `dsh-sdk`。本地 provider（spawn/fork）经 **`prepareContinuable()`** 提供 creation inputs，可续（含结算后、持久化与 session query 可用时）可冷恢复；外部 provider（acp/codex/claude-code/dsh-sdk）只贡献**一个执行句柄**、**不接受后续消息**、不获得多轮。
3. **⭐ 新增全局控制面**（`packages/subagent/tool-subagent-control/README.md:12`）：`send_message`（直系父↔子之间的 steer）、`interrupt_agent`（停止子代理当前轮，**保留其 inbox 与后代**）、`list_agents`（来自可单独加载的 `list-agents` 插件，按 durable id + label 列出可续子代理）。父与可续子**继承同一 `send_message` 定义与排序**，模型通信不引入子专属 schema；**仅直系父子可通信**。
4. **⭐ Agent Teams（实验）**（`docs/subsystems/agent-team.md:58`，`docs/tool-catalog.md:43`）：持久 **roster** + **共享任务 DAG**——每个任务事件存**完整快照**，`revision` 为 **compare-and-set** 值且每次变更 +1，`blockedBy` 边必须指向未删除任务且**保持图无环**，`writeScopes` 是归一化的**咨询性路径前缀而非锁**；配 **直投 inbox**（`agent/inbox/spliced`）。九只工具（`spawn_teammate`/`team_task_*`/`wait_agent` 等）**全部**限定于隐式 Team Lead 与 durable teammate。⚠️ `agent-team-profile` bundle **默认关闭**（shipped base bundle 保持该包 disabled，文档化的 profile patch 才启用它并同时禁用旧的 continuable-child 控制名）。
5. **dsh-plan-mode**（慢 Planner）+ **dsh-goal + goal-round-driver**（滚动重规划，MPC 滚动时域）。
6. **dsh-tool-ralph + workflow**：ralph 为 fresh-agent 多轮迭代（每轮 fresh structured-output 子代理，`maxRounds=64`）；workflow 为 JS 编排脚本驱动子代理序列——options/MDP 时序抽象。

**控制论映射**：KT-ctrl-044（MPC 滚动时域）、KT-ctrl-043（时标分离 ε）、KT-ctrl-042（多层递阶控制，本轮由「父委派子」扩展为「**父—子双向控制面 + Team roster**」）、KT-ctrl-046（options/SMDP）、KT-ctrl-041（分层控制，Team Lead 层显性化）。

**强弱项**：⭐**强**——dsh 同时具备「计划确认门（plan-mode）」「持久目标滚动（goal-round-driver）」「多级频率分离（subagent/workflow）」三层 P 能力；本轮把委派从「一次性后台任务」升级为**有身份、可续、可中断、可通信的托管 activation**，并以 Agent Teams 把**协调回路显性化**（roster + revision-CAS 任务 DAG + 直投 inbox）。⚠️**弱**——**规划时域仍由配置固定**（`maxGoalRounds` / ralph `maxRounds` / subagent **无前瞻度**）；父层仍**无 λ 更新循环**（无持续约束注入与协调变量更新），Agent Teams 的 DAG 无环性由写入时校验保证，但**无自动重规划器**。

## 6. R 环 — 反思 / 反馈闭环（**中弱**）— 维持 ⚠️

**承担角色**：以「事件/错误触发的重试 + 提醒 + hook 强制 steer + 目标续跑 + **输出塌缩停机**」为主的反馈，集中体现为偏 P 项（即时纠偏）；**仍缺独立「误差计算」机构与 I/D 项**。

**关键机制**：
1. **dsh-llm-retry**：retryPolicy 驱动重跑，且 **"Nothing here is model-visible: no retry event, delay, provider error, or failed partial output reaches the model or derived messages"**（`packages/llm/llm-retry/README.md:50-58`）——重试对模型**完全不可见**，因此不构成学习信号。
2. **dsh-hooks-claude-code / hooks-codex**：用户 `hooks.json` 映射到 harness 拦截点；`agent/turn-stopping` 的 `deny` 经 `agent.steer()` **强制再走一步**，`tools/pre-execute` / `PostToolUse` 的 `deny` **阻断**工具（`packages/experimental/hooks-claude-code/README.md:89`）——外力硬中断 + 方向改道。
3. **dsh-repeat-tool-reminder**：同工具同参连续达阈值（3/5/8）注入提醒，**只 enrich 不 veto**（`packages/guard/repeat-tool-reminder/README.md:91`）——趋势预警（软 D 项）。
4. **⭐ dsh-repeat-output-guard（本轮新增，base bundle 默认启用）**：`packages/guard/repeat-output-guard/`。监视**实时输出流**，当一段短行序列在滑动窗口内重复足够次数即 `agent.cancel({kind:'hook'})`，让运行在塌缩**早期**停止而非烧完输出预算（默认 `mode: cancel`、`windowLines: 400`、`ngram: 5`、`minCount: 8`、`minChars: 2000`，见 `packages/bundle/base/cordis.patch.yml:454-461`）。但 README 明写：**"it never rewrites a message, and a trip is stopped, not repaired"**（`README.md:136`，"Stops, never repairs"）——塌缩前已持久化的退化文本仍在历史中并会被重放进后续请求，清除它需要适配侧重放策略或压缩触发，**本包都不实现**。⇒ 属「**检测—停机**」而非「**算误差—修正**」。
5. **dsh-tool-subagent-report**（reportDelivery: next-step）：子代理在最近步骤边界唤醒父任务并注入上下文——反馈回灌（下级→上级）。
6. **dsh-goal-round-driver** + **dsh-agent-instructions**：状态变化驱动的迭代反馈。
7. **`packages/core/agent-loop/README.md:220`**：**"No built-in turn budget"**——工具调用或 steer 都会延续当前轮，限制失控轮次的策略必须从既有生命周期扩展点（如 `agent/turn-stopping`）自行取消。

**控制论映射**：KT-ctrl-002（负反馈闭环，hooks deny→steer = 实际 y 超限时强制校正）、KT-ctrl-020~023（PID，主要为 P + 弱 D；repeat-output-guard 是**最锐利的 D 项**但只有停机没有修正量）。**缺失**：KT-ctrl-021/I（积分项，无「反复犯同一错误」的累积补偿）、KT-ctrl-004（误差收敛校正律，**无独立「算误差 e=r−y」环节**）、KT-ctrl-025（稳态误差/超调验收）。

**强弱项**：⚠️**中弱**——以事件/外力触发为主（request-error、hook deny、repeat-reminder、repeat-output-guard、goal 变更），**仍无 self-critique、无 e=r−y**。本轮新增的 repeat-output-guard 让「检测」更锐利（默认开启、可中止），但它**只停机不修复**，属**保护性停机**而非反馈校正。其最强点（hooks deny→steer、子代理 reportDelivery、guard cancel）仍是「外力硬中断 + 方向改道」而非「算误差再修正」。由于 E 环无独立 critic，dsh 反馈放大器输入信号质量上限不高——只能对感知到的失败纠偏，难对未感知的偏航闭环。

## 7. dsh 控制论画像总结

**整体范式**（保留并更新）：
> 一个 **MPC 式滚动规划 + 配置化强约束执行器 + 事件溯源状态估计器** 的工程化控制器，但**不是自评估闭环智能控制器**。

**0.2.1 的变化方向**（同一范式内的结构位移，四句话）：**执行器跨语言化**（PTC：`native | ptc` + `ptc-runtime-node`/`ptc-runtime-python`，受管进程按沙箱策略执行可擦除 TS）；**委派托管化**（activations 取代 background job，删 `job_output`/`job_kill` 收集路径）；**协调回路显性化**（全局控制面 `send_message`/`interrupt_agent`/`list_agents` + Agent Teams roster/共享任务 DAG）；**记忆检索化**（session-query FTS5 确定性排序 + generation-bound cursor）；**持久格式代际化**（`SESSION_FORMAT_VERSION=4`，不可变相邻迁移 + 只读 open 不发布后继）。

套进反馈回路：r（设定值）由 plan-mode/goal/todo/**schedule** 生成，且本轮获得「谁能改 r」的硬校验；T（执行器）是三瀑布+看门狗+沙箱+审批，并新增跨语言执行面，闭环中工程化最强；M（状态估计）用事件溯源+投影+压力压缩+**FTS5 检索**做到高保真可回放可检索；P（规划）是清晰的慢/快双速分层，本轮把委派托管化并把协调面显性化；**但 E（评估）仍近开环**——auto-review 证明 dsh 能造独立 LLM 评估器，却只评**动作可授权性**且默认关闭，没有 Kritik 测量「实际输出 vs 目标」，于是 R（反思）放大的是「错误信号」而非「误差信号」，纠偏带窄。

**最突出的环**：**T 环（工具执行器）**——三瀑布解耦 + 超时看门狗 + read-only 故障安全 + 审批仲裁 + 溢出限幅 + 协作取消，构成教科书式「硬限幅 + 降级 + 冗余」；本轮再加 PTC 跨语言执行与沙箱多后端 fail-closed，**T 环的领先幅度反而扩大**。

**最薄弱的环**：**E 环（评估/传感器）**——判定记为「**部分修正**」：新增的 `experimental/auto-review` 是真正的独立 LLM 审查器，但（a）审查对象是单个工具调用的**可授权性**而非目标达成度，（b）base bundle **默认未装配**，（c）telemetry 族只是资源/性能镜像，`verify-*` 属开发期门控，`workspace-changes` 只记「世界变了什么」，message-feedback 仍 log-only。⇒ **「无对目标达成度的独立测量」这一实质结论不变**；耦合地让 R 环退化为「错误触发的重试/提醒/steer/停机」。

**三大设计启示**（对照框架 §7「工程最常踩的坑」）：
1. **踩中坑「过度依赖 E 却无 E」**——有大量反馈触发器却缺高质量误差信号；auto-review 的出现说明补 E 的技术路径已具备（独立 LLM 审查器 + 权限预设定点介入），但它被用在**授权**而非**达标**上。启示：应在 E 环补「子目标验证器/测试钩子」，让 R 环放大的是误差而非不确定度。
2. **踩中坑「M 环缺置信度」**——事件溯源 + FTS5 检索已很精确，但**不带 P 协方差**；goal/todo 断言靠模型自述，P/R 无法区分确信与猜测。
3. **坑「T 环缺看门狗」上做得最好**——read-only fail-safe + timeout-policy + spill + approval + **sandbox fail-closed** 是硬保证，是五环中可复用的范本（亮点：把看门狗/限幅沉淀为纯 apply 函数 + guard 目录的多插件组合；且「不可用即拒绝」而非静默降级）。

**关键证据索引（源码路径）**：
- 装配（三层）：`packages/bundle/base/cordis.patch.yml`（95 条 `- id:` 装配行）、`packages/bundle/web-app/cordis.patch.yml` + `packages/bundle/web-app/presets/{standard,minimal,ptc,cordis}.patch.yml`、profile patch 层
- 设定值：`docs/subsystems/plan.md:11`、`packages/goal/tool-goal/README.md:55`、`docs/subsystems/schedule.md:265`
- T 环：`packages/core/tools/src/index.ts:672`（`native|ptc`）、`packages/ptc-runtime/ptc-runtime-node/README.md:12`、`packages/sandbox/sandbox-local/README.md:71`、`docs/subsystems/permission-presets.md:73`、`packages/guard/timeout-policy/src/index.ts`
- M 环：`packages/session-query/session-query-sqlite/README.md:61`、`docs/tool-catalog.md:39`、`packages/core/session/src/types.ts:89`、`docs/subsystems/skills.md:13`、`docs/subsystems/compaction.md:101`
- P 环：`docs/upgrade-guide/v0.2.1-alpha.1/subagent-activations/guide.md:12`、`docs/subsystems/subagent.md:326`、`packages/subagent/tool-subagent-control/README.md:12`、`docs/subsystems/agent-team.md:58`
- E 环：`packages/experimental/auto-review/src/index.ts:41-62`（REVIEW_POLICY）、`:684-714`（`tools/pre-execute` 挂载）；`packages/feedback/message-feedback/src/index.ts`（log-only）
- R 环：`packages/llm/llm-retry/README.md:50-58`、`packages/experimental/hooks-claude-code/README.md:89`、`packages/guard/repeat-tool-reminder/README.md:91`、`packages/guard/repeat-output-guard/README.md:136`、`packages/core/agent-loop/README.md:220`

---

## 附：历史结论（v0.1.1-rc.2 口径，2026-09-07）

> **保留原因**：本节逐字保留上一轮（基线 `v0.1.1-rc.2`，2026-08-21 发布，画像写于 2026-09-07）的核心结论，供跨版本对照；**不得静默删除**。本轮复核后，**E 环判定由「最弱」调整为「部分修正（最弱，但已存在一个非同质的独立评估器）」——实质结论不变**（仍无对目标达成度的独立测量）；T 最突出、整体范式的表述维持。

**旧整体范式（原文）**：
> 一个 **MPC 式滚动规划 + 配置化强约束执行器 + 事件溯源状态估计器** 的工程化控制器，但**不是自评估闭环智能控制器**。

**旧最突出环（原文）**：**T 环（工具执行器）**——三瀑布解耦 + 超时看门狗 + read-only 故障安全 + 审批仲裁 + 溢出限幅 + 协作取消，构成教科书式「硬限幅 + 降级 + 冗余」。

**旧最薄弱环（原文）**：**E 环（评估/传感器）**——无独立 critic/validator，执行达标仅靠工具契约（格式）、token-meter（资源）、llm-retry（请求不抛）间接度量，不度量目标符合度；耦合地让 R 环退化为「错误触发的重试/提醒/steer」。

**旧装配口径（原文）**：`bundle/base/cordis.patch.yml` 装配 **76 核心 + 36 外部 seam**（L1 核心集）——⚠️ 该口径与现行 95 条 `- id:` 扁平装配表**不可直接相减**，本轮已改按三层口径描述。

**旧三大设计启示（原文）**：① 踩中坑「过度依赖 E 却无 E」；② 踩中坑「M 环缺置信度」；③ 坑「T 环缺看门狗」上做得最好，read-only fail-safe + timeout-policy + spill + approval 是可复用范本。

**旧五环强弱（原文速记）**：设定值 ⭐强 / E ❌最弱 / T ⭐⭐最突出 / M ⭐次强 / P ⭐强 / R ⚠️中弱 —— 与本轮判定逐环一致，仅 E 环加注「部分修正」。

---

### 📚 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S1 | 官方源码（版本锚点） | `/home/zako-mio/dsh/package.json:3`（`"version": "0.2.1-alpha.2"`；tag `dsh-v0.2.1-alpha.2`，2026-10-09，commit `d743267`） | 高 |
| SRC-002 | S4 | 一手源码观察（装配三层） | `packages/bundle/base/cordis.patch.yml`（95 条 `- id:` 装配行）、`packages/bundle/web-app/cordis.patch.yml` + `presets/{standard,minimal,ptc,cordis}.patch.yml`、profile patch 层 | 高 |
| SRC-003 | S1 | 官方子系统文档（设定值） | `docs/subsystems/plan.md:11`（plan/mode log-only 整值替换）、`packages/goal/tool-goal/README.md:55`（直人消息权威 + `blockedAfterConsecutiveRounds`）、`docs/subsystems/schedule.md:265`（四工具 + IANA 时区 + 子会话被拒） | 高 |
| SRC-004 | S1 | 官方源码 + 文档（E 环） | `packages/experimental/auto-review/src/index.ts:41-62`（REVIEW_POLICY「final authorization reviewer for exactly one pending tool call」）、`:684-714`（`tools/pre-execute` 挂载）；`packages/bundle/base/cordis.patch.yml` 无 auto-review 条目（默认未装配） | 高 |
| SRC-005 | S1 | 官方源码 + 文档（T 环） | `packages/core/tools/src/index.ts:672,812`（`native \| ptc`，`both` 被拒）、`packages/ptc-runtime/ptc-runtime-node/README.md:12`、`packages/sandbox/sandbox-local/README.md:71`（runner 链 + fail-closed）、`docs/subsystems/permission-presets.md:73` | 高 |
| SRC-006 | S1 | 官方文档 + 源码（M 环） | `packages/session-query/session-query-sqlite/README.md:61`（确定性排序 + 有界 snippet + `SESSION_QUERY_STALE_CURSOR`）、`docs/tool-catalog.md:39`（五只读工具，opt-in）、`packages/core/session/src/types.ts:89`（`SESSION_FORMAT_VERSION = 4`）、`docs/subsystems/skills.md:13`、`docs/subsystems/compaction.md:101` | 高 |
| SRC-007 | S1 | 官方升级指南 + 文档（P 环） | `docs/upgrade-guide/v0.2.1-alpha.1/subagent-activations/guide.md:12`（activations + 删 `job_output`/`job_kill`）、`docs/subsystems/subagent.md:326`（6 provider + `prepareContinuable`）、`packages/subagent/tool-subagent-control/README.md:12`、`docs/subsystems/agent-team.md:58`（revision CAS + blockedBy 无环）、`docs/tool-catalog.md:43`（agent-team 默认 disabled） | 高 |
| SRC-008 | S1 + S4 | 官方源码/文档 + 一手观察（R 环 + 上游生态） | `packages/llm/llm-retry/README.md:50-58`（对模型不可见）、`packages/experimental/hooks-claude-code/README.md:89`（steer/deny）、`packages/guard/repeat-tool-reminder/README.md:91`（只 enrich）、`packages/guard/repeat-output-guard/README.md:136`（"Stops, never repairs"）+ `packages/bundle/base/cordis.patch.yml:454-461`（默认 `mode: cancel`）、`packages/core/agent-loop/README.md:220`（No built-in turn budget）；上游：`https://github.com/deepseek-ai/deepseek-harness`、`https://deepseek-harness.github.io/deepseek-harness/`、`npx @deepseek-ai/dsh web`、`README.md:13`（Public APIs are pre-stable）；生态旁证：`/home/zako-mio/opencode/archive/Mission-file/2026-10/1011-dsh插件生态调研/evidence/compat-check-0.2.1-alpha.2.txt`（35 个外部插件三态：PASS / REFUSED / NO-DSH-PEERS） | 高 |

> ✅ **本机环境事实（v1.5 更正）**：本机 `bwrap` 已安装，`sandbox-local` 的 runner 链**选中 bwrap**，`enforcement=full`（read-only / workspace-write 于 shell + fs 双侧真强制）。v1.4 所记「本机 bubblewrap 与 Landlock 均不可用 → 走 fail-closed 分支（`SANDBOX_UNAVAILABLE`）」**已证伪**。画像对沙箱能力的描述仍以源码/文档契约为准；本机可达性属**环境事实**，⛔ 不计入任何分值变动。
> ⚠️ **口径提示**：`packages/bundle/base/cordis.patch.yml` 的 `- id:` 装配行现计 **95** 条（事实包记为 94，以源码实际计数为准）；旧「76 + 36」为分列口径，**不可与新口径相减**。