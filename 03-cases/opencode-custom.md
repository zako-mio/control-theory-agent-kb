# opencode-custom（自改造 opencode）— Agent 控制论画像

> 本画像定位为官方 opencode 的衍生变体·个人装配层，基线是官方默认 + 最小常规装配（四 agent + 官方内置 skills + 基础 provider）。证据强度为源码级（配置级），全部结论可回溯至 `07-checkpoint/opencode-custom-snapshot/` 快照原文。与官方 opencode 的关系是「内核继承 + 装配层增强」：不改动 opencode 引擎源码，仅在配置/协议/skill/MCP/记忆系统五层做定向补强，把官方偏开环的 Plan-and-Execute 内核改造为可自演化的闭环编排平台。当前装配口径为 10 agent / 45 skill（单根统一）/ 6 MCP / 2 command / 5 instructions，并新增「架构判断三层栈」与「能力自我扩展 SOP」两项纵深机制。

## 0. 精装度评估

> 定位：个人装配层（官方 opencode 衍生变体）｜ 精装度：3.9/5 ｜ 分类：个人变体（官方衍生）｜ 一手/二手：一手 ｜ 证据强度：源码级（配置级）

**综合评分**：3.9/5 — 在内核继承官方基线之上，以协议层、专职 worker、skill 库、MCP、Reflection 记忆系统做定向补强，8 维中 6 维较官方提升，精装度从 2.9 跃升至 3.9，但一键部署与完整沙箱仍受个人装配限制。本轮回漂移（9→10 agent、28+11 双根→45 单根 skill、1→2 command、新增架构三层栈与能力扩展 SOP）属「能力纵深增长」，未跨评分模型 5 档产品阈值，故维持 3.9；封顶因素（一键部署=个人 config 无分发、沙箱=非 VM 隔离）未变。

**预装能力表**：

| 维度 | 预装情况 | 依据 |
|------|---------|------|
| 多Agent编排 | 具备 | 10 agent（+6 专职 worker：pdf/drawio/architect/vision/reflection/search）+ 委派协议 + 并行 + subagent_depth=2；新增 architect-worker 但无真 DAG 画布（未达 5 档市场级编排） |
| Skill库 | 具备 | 45 skill 目录（+`_shared`；41 个可加载 SKILL.md，4 个 `_SKILL.md` 命名不达标未加载）+ 单根统一；新增 7 个（architecture-judgment/capability-extension 等）；仍为精选个人库、无市场/分发 |
| 工作流 | 具备 | GATE/COMPLEXITY 门控 + 契约驱动 + 委派接力 + 架构三层栈 gated SOP（/arch + architecture-behavior + architecture-judgment + gate_architecture.py）；无通用可视化工作流/DAG 引擎（未达 5 档） |
| 模型接入 | 具备 | 3 provider（opencode-go/deepseek/zhipu）+ deepseek-flash V4.1 原生多模态 + @ai-sdk/openai-compatible 图片链路修复；仍非「数百模型开箱」（未达 5 档） |
| 一键部署 | 部分 | 个人 config 需手动复制装配层，无一键分发（仍为个人变体定位，无 npm/docker/SaaS 分发） |
| 沙箱 | 部分 | external_directory 白名单 + /tmp/opencode 隔离区，仍非完整沙箱/VM 隔离 |
| MCP生态 | 具备 | 6 MCP（vscode-mcp-server/amap/pdf-reader/drawio/drawio-local/headroom，多传输；2 enabled）与上一版同构 |
| 记忆 | 具备 | MEMORY.md 跨会话 + pending.json 结构化状态机 + reflection-worker + compaction 调优（满分档） |

**声称 vs 实际**：个人变体不涉营销，配置声称的能力均经快照实证，无失实项；8 维打分依据逐一对应 `07-checkpoint/opencode-custom-snapshot/opencode.jsonc` 与 `inventory.json`，分值由 `09-src-data/opencode_custom_scores.py` 可复算，两者口径一致。

## 1. 设定值（Setpoint）——用户意图 → 可验证子目标

**承担角色**：由「GATE 强制自评 + COMPLEXITY 复杂度标记 + grill-me/question 目标澄清 + /arch 架构任务路由 + 契约驱动委派协议」共同承担，把模糊意图先分解为带复杂度标签、带推理深度约束、可接力传递的子目标序列，官方内核的 AGENTS.md/plan 里程碑分解被装配层协议进一步结构化。

**关键机制**：
- **GATE 强制门控作为设定值入口**：`instructions/auto-mode.md` 规定主 Agent 收到任务后第一条消息必须输出 `[GATE] 范围=X 深度=X 操作=X 风险=X → 总分=XX → Daily|Deep`，把「任务该用多大推理深度」显式固化，不可跳过。
- **COMPLEXITY 跨阶段继承**：Plan 阶段收敛摘要必须含 `[COMPLEXITY: X/20]`，Build 阶段检测到该标记必须使用匹配推理深度、不得重新评估——设定值从规划层刚性传递到执行层，避免深度漂移。
- **grill-me 目标澄清协议**：`opencode.jsonc` 中 plan/build 的 prompt 内联 Grill-Me Protocol，要求逐分支访谈、一次一问、每轮以 `question` 工具收尾，直到设计树所有分支收敛；`question` 是结构化传感器而非自由文本。
- **/arch 架构目标路由（新增）**：`command/arch.md` 定义 `/arch <任务描述>`，把架构类模糊意图按 `routing.md` 的 18 场景索引归入命中场景，判定产出类型（adr/boundary/review/tech-debt）后才委派——设定值先物化为「场景号 + 产出类型 + 结构化契约」再进入执行。
- **architecture-behavior 触发约束（新增）**：`instructions/architecture-behavior.md` 规定架构类任务（技术选型/模块边界/架构评审/质量属性权衡/技术债/演进治理等）必须加载 `architecture-judgment` skill + 委派 `architect-worker` + 过门控，把「什么算架构任务、走哪条设定值路径」固化为刚性触发规则。
- **契约驱动委派**：`instructions/auto-mode.md` 定义子 Agent prompt 契约（Identity/Role/Skills/Task/Model Selection/Return Format），设定值以契约文件与结构化 JSON 回传，跨 Agent 可溯源（原 `agent-protocol.md` 已并入 auto-mode.md）。
- **留档路径正则门控**：auto-mode.md 规定留档路径须匹配 `Mission-file\d{4}-\d{2}\d{4}-.*\`，不通过则拒绝保存——设定值附带可验证的落盘约束。

**控制论映射**：KT-ctrl-045（规划-执行解耦，契约即里程碑参考序列）/ KT-ctrl-041（分层时标，GATE 决定慢/快推理档）/ KT-ctrl-002（设定值 r = 用户意图）/ KT-ctrl-046（options/SMDP，/arch 场景路由即把意图映射为动作原语）。

**强弱项**：强——设定值有强制 GATE 入口、复杂度可跨阶段继承、目标澄清走结构化 question、架构意图有显式路由、委派走可溯源契约；弱——设定值仍以 prompt 文本编码为主，无机器可验证的定量目标函数，COMPLEXITY 是自评而非外部测量。

**双层评分**：内核 3.5/5 + 装配层 Δ+1.0 → 综合 4.5/5（增强）

---

## 2. 传感器 / 评估环（E 环）——测"当前执行是否达标"

**承担角色**：由「search-behavior 外部信息实证准则 + search-worker 证据包 + gate_architecture.py ADR schema 门控 + grill-me/question 用户传感器 + 视觉降级规则 + GATE 自评」承担，官方内核缺失的独立 Critic/verifier 被装配层以「外部事实核查管线 + 领域级自动门控 + 结构化用户确认」补齐，评估从「只测是否重复/是否改文件」升级为「可测事实是否多源交叉验证、架构产出是否过 schema 机检」。

**关键机制**：
- **search-behavior 信源分级传感器**：`instructions/search-behavior.md` 规定依赖外部事实的结论必须先搜索并打开原始页面、区分「已验证事实/基于证据的推断/尚不确定」、重要结论 ≥2 独立来源交叉验证——把评估标准编码为可执行准则。
- **search-worker 专职证据包**：`opencode.jsonc` 新增 search-worker（发现+获取+交叉验证，输出结构化证据包），把「外部信息是否可信」这一语义评估外包给专职 Agent。
- **gate_architecture.py ADR schema 门控（新增，领域级自动评估）**：`architecture-judgment` skill 的 `_private/gate_architecture.py --kind adr|boundary` 对 architect-worker 产出的 ADR/边界说明做 schema + 知识图谱自动机检，退出码 0 才放行、FAIL 原样回传修正最多 2 轮、不得降级为「口头通过」——这是 E 环第一个可自动执行的领域级评估门（模板级 review/tech-debt 仍走人工确认）。
- **grill-me/question 用户传感器**：plan/build 内联 Grill-Me Protocol 强制每轮以 `question` 工具收尾，用户确认即反馈信号；`[GRILL]` 确认与选项式提问降低观测噪声。
- **视觉降级规则**：auto-mode.md 规定会话模型无视觉时不得 Read 图片，改委派 vision-worker 代看，失败降级为 PNG 结构校验——为「图像是否达标」提供降级传感器路径。
- **GATE 自评作为元评估**：主 Agent 在动手前对范围/深度/操作/风险四维自评，是「该投入多少评估资源」的前置传感器。

**控制论映射**：KT-ctrl-006（强校验降低对基座模型误差敏感）/ KT-ctrl-035（DOB 式在线评估外部偏移，search-worker 交叉验证）/ KT-ctrl-012（观测噪声 R，信源分级=按可信度加权）/ KT-ctrl-001（E 环是闭环开关）。

**强弱项**：强——补上了官方最弱环：外部事实有了专职核查管线与信源分级，架构产出有了 schema 自动门控，用户确认结构化，视觉有降级路径；弱——领域级自动门控仅覆盖架构域的 adr/boundary（单点），仍无通用独立 Critic 模型对「语义是否达标」做强验证，search-behavior 是准则而非自动门控，达标判定仍依赖 Agent 自律执行。

**双层评分**：内核 2.0/5 + 装配层 Δ+2.0 → 综合 4.0/5（反转）

---

## 3. 执行器 / 工具环（T 环）——工具调用容错与安全约束

**承担角色**：在官方内核「shell 看门狗 + 输出截断 + 权限仲裁 + AI-SDK 修复」之上，装配层以「6 MCP 多传输 + external_directory 白名单 + bash 危险命令 deny + 专职 worker 工具隔离」扩展执行器边界，形成「内核硬容错 + 装配层工具生态」的双层执行器。

**关键机制**：
- **6 MCP 集成**：`opencode.jsonc` 配置 vscode-mcp-server/amap/pdf-reader/drawio/drawio-local/headroom 六个 MCP（多传输），pdf-reader/drawio 启用并仅授权对应 worker，vscode/amap/headroom 因开销或量化亏损禁用——工具接入可插拔且受权限收口。
- **权限分层白名单**：全局 `external_directory` 默认 allow、`~/.ssh|~/.aws|~/.gnupg` deny；`read` 追加 auth.json deny；`bash` 对 `python -c *`、`rm -rf *`、`git push *` deny，对 Set-Content/Out-File/Remove-Item -Force 设 ask。
- **edit 分层授权**：`edit` 分层只放 agent.build 与写入型子 Agent（不放全局，避免覆盖 plan/explore 内置 deny），允许 `~/opencode/**`、`tmp/opencode/**`、`~/mnt/d/Opencode_Download/**`，其余 ask。
- **专职 worker 工具隔离**：pdf-worker 仅 `pdf-reader_*` allow、drawio-worker 仅 `drawio_*` allow，且 task 权限仅放行 vision-worker；`subagent_depth=2` 限制递归深度。
- **内核继承的执行器护栏**：沿用官方 shell 超时看门狗、输出截断 anti-windup、权限 ask/deny/always 仲裁、AI-SDK 工具名修复。
- **本轮核对（T 环无变化）**：新增的 architect-worker 复用 build 默认工具面与 architecture-judgment skill，未新增 MCP、未新增权限白名单条目；6 MCP 与权限规则同上一版，工具面未扩，T 环维持 5.0。

**控制论映射**：KT-ctrl-034（硬约束限幅+看门狗，bash deny/ask 白名单）/ KT-ctrl-033（冗余与仲裁，多 MCP 与专职 worker 分工）/ KT-ctrl-031（鲁棒稳定，权限收口防越权）/ KT-ctrl-030（模型不确定性，edit ask 为不确定动作留降级）。

**强弱项**：强——在官方最强环上叠加了 MCP 生态与细粒度权限白名单，工具边界可插拔且最小授权；弱——容错仍以外部规则为主，缺异质冗余多数表决（NMR/TMR），MCP 有多个处于禁用态（工具面实际收窄）。

**双层评分**：内核 4.5/5 + 装配层 Δ+0.5 → 综合 5.0/5（增强）

---

## 4. 记忆 / 状态估计环（M 环）——会话记忆与跨会话长期记忆

**承担角色**：在官方「SQLite Session + compaction 分层压缩 + context-epoch 增量基线」的会话级记忆之上，装配层以「MEMORY.md 跨会话长期记忆 + pending.json 结构化状态机 + reflection-worker 异步写入 + compaction 参数调优」补齐官方缺失的跨会话记忆层，形成「会话内两级卡尔曼 + 跨会话结构化状态」的记忆体系。

**关键机制**：
- **MEMORY.md 跨会话长期记忆**：`~/.config/opencode/MEMORY.md` 作为 instructions 注入，以 `§` 分段 + `[src: cycle_id]` 签名承载跨会话沉淀的知识，是官方内核所无的持久记忆层。
- **pending.json 结构化状态机**：auto-mode.md 的 Reflection 自检规则规定启动时检查 `pending.json` 的 `meta.waiting_count`，按 waiting→processing→done/expired 状态流转——把「待反思的经验」建模为可恢复的结构化状态。
- **compaction 参数调优**：`opencode.jsonc` 设 `tail_turns=4`、`preserve_recent_tokens=16384`、`reserved=10000`，与 auto-mode.md 的 L1 剪枝/L2 结构化压缩/L3 兜底摘要阶梯配合，控制状态估计的更新预算。
- **reflection-worker 异步写入**：专职子 Agent 分析 Plan+Build 周期并生成 Memory/Skill 条目，写入 `memory_pending/` 滞留池，避免阻塞主流程。
- **官方内核记忆继承**：SQLite session 持久化、compaction 分层压缩、context-epoch 增量基线、revert 快照回滚。
- **本轮核对（M 环无变化）**：architecture-judgment 内置的 167 节点方法论知识图谱属离线 skill 资产（知识/策略注入层），不计入跨会话记忆层；MEMORY.md + pending.json + reflection-worker + compaction 调优同上一版，M 环维持 4.0。

**控制论映射**：KT-ctrl-011（卡尔曼式预测-更新，context-epoch 为预测、compaction 为更新）/ KT-ctrl-014（信息滤波/降维，结构化压缩模板）/ KT-ctrl-010（状态估计，MEMORY.md 维护跨会话信念）。

**强弱项**：强——补上了官方「无跨会话长期记忆」的短板，MEMORY.md + pending.json + reflection-worker 构成可溯源、可恢复的长期状态层；弱——长期记忆写入需经 /reflection 人工确认，容量受 MEMORY.md 约 5000 字符约束，pending.json 存在滞留池双轨写入断链风险。

**双层评分**：内核 3.5/5 + 装配层 Δ+0.5 → 综合 4.0/5（增强）

---

## 5. 规划 / 分层环（P 环）——慢/快双速 + 专职编排平台

**承担角色**：在官方「plan（慢规划）+ build（快执行）+ task 委派 + subagent_depth」的双速结构之上，装配层以「+6 专职 worker + 架构三层栈 gated SOP + GATE/COMPLEXITY 推理档分层 + 契约驱动委派接力 + 并行分片规范」把单体双速规划器升级为分层编排平台，慢/快之外新增「专职能力层」。

**关键机制**：
- **专职 worker 能力层（5→6）**：pdf-worker/drawio-worker/architect-worker/vision-worker/reflection-worker/search-worker 六个隐藏子 Agent，各自封装领域能力，主 Agent 只编排不钻细节（options 式技能抽象）；新增 architect-worker 专司架构判断与设计裁决。
- **架构三层栈 gated 编排（新增）**：架构任务由主 Agent 按固定编排链执行「加载 architecture-judgment → 委派 architect-worker → 跑 gate_architecture.py 门控放行（FAIL 回传≤2 轮）→ 可选另委 drawio-worker 制图」，把架构域编排从自由组合固化为受门控的 SOP。
- **GATE/COMPLEXITY 推理档分层**：GATE 自评 ≤12 走 Daily、≥13 走 Deep，COMPLEXITY 标记跨 Plan→Build 继承，慢/快推理资源随任务复杂度动态分配。
- **契约驱动委派接力**：auto-mode.md 规定独立任务并行 Task、依赖任务串行接力（data 传递）、紧密耦合流程交 1 个 Agent，配合结构化 JSON 回传实现编排接力。
- **并行与批处理规范**：auto-mode.md 规定互不依赖的只读操作必须并行发出、相邻同类只读合并批次、不混合读写——把并行度约束编码为协议。
- **深度限制与恢复**：`subagent_depth=2` 限制递归，`task_id` 支持恢复同一子会话；沿用官方 plan/build 双速与并行 explore。

**控制论映射**：KT-ctrl-041（分层时标，慢 plan/快 build/专职 worker 三层）/ KT-ctrl-043（时间尺度分离 ε，Daily/Deep 与主/子 Agent 成本频率比）/ KT-ctrl-044（MPC 滚动时域，契约接力与观察回调）/ KT-ctrl-045（规划-执行解耦）/ KT-ctrl-046（options/SMDP，worker 即高层动作原语）。

**强弱项**：强——官方最强环再升级为分层编排平台，专职 worker 提供时序抽象、架构任务有受门控的固定编排链、推理档动态分配、并行规范可执行；弱——仍是「一次切换 + 人工介入」，缺 MPC 式自动滚动重规划，无真 DAG 画布，编排拓扑靠协议文本而非可视化约束。

**双层评分**：内核 4.5/5 + 装配层 Δ+0.5 → 综合 5.0/5（增强；已处 5.0 上限，新增 worker 不改变分值）

---

## 6. 反思 / 反馈闭环环（R 环）——从半开环到自演化闭环

**承担角色**：在官方「错误回灌 + doom_loop + revert + 重试」的弱 R 环之上，装配层以「Reflection 自演化系统（MEMORY.md + pending.json + reflection-worker + /reflection 命令）+ 留档 5 段模板 + 经验教训回写」把反思从内核的局部错误回灌升级为跨会话的元认知闭环，实现「开环主导 → 闭环自演化」的反转。

**关键机制**：
- **Reflection 自检规则**：auto-mode.md 规定每轮收到用户消息先检查 pending.json 的 waiting_count，有 waiting 则委派 reflection-worker 处理——把反思从「可选」变为「启动即触发」。
- **4 层输入封装**：每个 Plan+Build 周期完成后封装 Layer A（GATE/COMPLEXITY/决策）+ B（子 Agent JSON/聚合摘要）+ C（MEMORY 快照）+ D（留档报告）写入 pending.json，反思输入结构化。
- **/reflection 交互式审阅**：`command/reflection.md` 定义三池扫描（pending.json / memory_pending / manual_pending）、统一分析优先+逐条兜底、独立性/重复性三分类、容量 A/B/C/D 分层、`[src: cycle_id]` 签名门禁、双版本同步。
- **留档 5 段模板**：auto-mode.md 要求报告含当时情况/制定计划/执行情况/完成情况/反思分析建议 5 段，缺段不合格，把反思固化为交付物必选项。
- **官方内核 R 环继承**：工具错误回灌、doom_loop 防震荡、revert 用户纠偏、LLM 重试退避。
- **本轮核对（R 环无变化）**：架构三层栈的 gate 失败回传修正（≤2 轮）属单点执行纠偏，未接入 Reflection 自演化链路，也未新增跨会话反思机制；R 环维持 4.5。

**控制论映射**：KT-ctrl-002（负反馈闭环，误差=执行与目标偏差）/ KT-ctrl-020~023（PID 三环节，P=当轮错误回灌、I=跨会话 MEMORY 累积、D=留档反思预判）/ KT-ctrl-004（误差收敛，签名门禁防污染）/ KT-ctrl-025（稳态误差，人工确认作为积分项限幅）。

**强弱项**：强——补上官方最弱的 R 环：反思启动自动触发、输入结构化、审阅有签名门禁与容量分层、产物回写长期记忆，形成跨会话自演化闭环；弱——闭环仍需 /reflection 人工确认，反馈有滞后，pending.json 滞留池存在写入断链，反思质量依赖 reflection-worker 单模型。

**双层评分**：内核 2.0/5 + 装配层 Δ+2.5 → 综合 4.5/5（反转）

---

## 7. 架构判断三层栈与自我扩展能力

### 7.1 架构判断三层栈（五元结构）

本轮最显著的纵深机制，是把「架构判断」从一个提示词约定升级为可复用、可门控的能力栈。它由五个元件构成，前三个即「能力三层栈」范式（Skill + Worker + 行为指令），再叠加命令入口与自动门控：

| 元件 | 落点 | 作用 |
|------|------|------|
| Skill | `skills/architecture-judgment/`（内置 167 节点方法论知识图谱，离线可用） | 提供判断依据（MTH/ESS 重召回、TEC 仅作选型标尺）与工作流 |
| Worker | `architect-worker`（可见子 Agent，第 6 个专职 worker） | 专职产出 ADR / 多维权衡矩阵 / 边界说明 / 评审结论 |
| 行为指令 | `instructions/architecture-behavior.md` | 定义架构任务触发规则、知识分层策略、openspec design 门控 |
| 命令 | `command/arch.md`（`/arch <任务描述>`） | 用户显式入口，做 18 场景路由与产出类型判定 |
| 门控 | `architecture-judgment/_private/gate_architecture.py`（`--kind adr|boundary`，schema + 图谱机检） | 产出放行的自动判据，FAIL 回传≤2 轮、不得口头通过 |

**控制论意义**：该栈把「架构判断」从开环的人工经验，变成一个带目标路由（/arch）、专职执行（architect-worker）、结构化契约（schema）、自动测量（gate）与纠偏回传（FAIL 回修）的完整局部闭环——是装配层中首个「五元齐备」的领域级控制回路，也是 P/E 两环协同的落点（P 环编排 + E 环门控）。

### 7.2 能力扩展 SOP → 装配层的「二阶能力」

`skills/opencode-capability-extension/` 定义了为 opencode 自身新增/补齐能力的标准流程：诊断孤儿/半成品能力 → 统一 skill 双根 → 引用普查防迁移断裂（grep 硬编码） → 契约先行（交付物 + 结构契约） → 落地门控与冒烟 → 单一真相源 + 派生对账安装。其核心是「能力三层栈」范式：任何新能力都按 Skill + Worker + 行为指令三层装配，并按需补命令与门控。

**关键跃迁**：装配层由此具备「二阶能力」——不仅拥有若干能力，还拥有一套「为自己系统性地新增能力」的元能力。可复核证据：上一版 skill 为双根（28 skills + 11 legacy），本轮收敛为单根 `skills/` 45 目录，并新增 7 个 skill（architecture-judgment / github-bulk-upload / job-listing-filter / opencode-capability-extension / restricted-corpus-acquisition / resumable-content-pipeline / single-source-docs-pipeline）；其中「架构判断三层栈」本身即该 SOP 的首个完整范例。

### 7.3 评分未变的原因（档位未跨）

本轮为「能力纵深增长」而非「产品档位跃迁」，故精装度与五环分值均维持不变：

- **多Agent编排 / 工作流** 仍处 4 档内生增长：新增 worker 与 gated SOP 增强了编排与工程流程，但未引入真 DAG 画布或通用可视化工作流引擎，5 档门槛（市场级/画布级）未达。
- **P 环** 已处 5.0 上限，architect-worker 的加入反映在 worker 数量与编排链上，但分值无可升空间。
- **E 环** 的增量是架构域单点门控（adr/boundary），不足以支撑整环 +0.5，维持 4.0。
- **R 环** 无新增反思机制，gate 回修属局部纠偏，维持 4.5。
- **封顶因素未变**：一键部署仍为个人 config 无分发（3 档）、沙箱仍非 VM 隔离（3 档）。

结论：官方 2.9、自改造 3.9 维持；本轮仅刷新 evidence 与机制叙述，评分单一数据源 `09-src-data/opencode_custom_scores.py` 未改动。

## 七大核心环强弱总评

| 环 | 承担角色 | 强度 | 主控概念 |
|---|---------|:---:|---------|
| **设定值** | GATE + COMPLEXITY + grill-me/question + /arch 路由 + architecture-behavior | 强 | KT-ctrl-045 规划-执行解耦 |
| **E 评估** | search-behavior + search-worker + gate_architecture.py 门控 + 用户确认 + 视觉降级 | 强（由最弱反转） | KT-ctrl-035 扰动观测器 |
| **T 执行** | 6 MCP + 权限白名单 + 专职 worker 工具隔离 | 最强（本轮无变化） | KT-ctrl-034 限幅/看门狗 |
| **M 记忆** | MEMORY.md 跨会话 + pending.json + compaction 调优 | 强（本轮无变化） | KT-ctrl-011 卡尔曼式滤波 |
| **P 规划** | plan/build 双速 + 6 专职 worker + 架构三层栈 + 契约接力 | 最强 | KT-ctrl-044/045 MPC + 解耦 |
| **R 反思** | Reflection 自演化系统 + 留档 5 段 + 经验回写 | 强（由弱反转，本轮无变化） | KT-ctrl-002 负反馈闭环 |

## opencode-custom 控制论画像总结

**整体范式：在官方前馈主导内核上做弱环定向补强，把「开环为主 + 局部闭环」改造为「分层编排 + 跨会话自演化闭环 + 架构域可门控判断」的控制器，并进一步获得「为自己新增能力」的二阶能力。**

- **最突出的环：P 环（分层编排）与 T 环（执行器安全）**——官方本就最强的两环被继续加固：P 环从双速升级为「plan/build + 6 专职 worker + 架构三层栈」编排平台，T 环从内核护栏扩展到 6 MCP + 细粒度权限白名单。
- **关键反转：E 环与 R 环（仍成立）**——官方两大最弱环被装配层补齐：E 环以 search-behavior 信源分级 + search-worker 证据包 + 结构化用户确认，并新增 gate_architecture.py 领域级自动门控实现反转；R 环以 Reflection 自演化系统（pending.json 状态机 + reflection-worker + /reflection 签名门禁）从半开环升级为跨会话闭环。
- **架构三层栈落地**：架构判断由「skill（167 节点离线图谱）+ worker（architect-worker）+ 行为指令（architecture-behavior）+ 命令（/arch）+ 门控（gate_architecture.py）」五元构成，装配层出现首个五元齐备的领域级闭环。
- **能力可自我扩展**：opencode-capability-extension SOP 使装配层具备二阶能力，能按「Skill + Worker + 行为指令」三层栈系统性地为自己新增能力；本轮 skill 由双根 28+11 收敛为单根 45 目录、新增 7 skill 即为佐证。
- **精装度维持 3.9（2.9 → 3.9，Δ+1.0）**——8 维中 6 维较官方提升（记忆满分 5），本轮回漂移属能力纵深增长、未跨 5 档阈值，故维持；一键部署与完整沙箱仍受个人装配限制未提升，是封顶主因。
- **从单体到分层编排 + 自扩展平台**：官方是单体双速控制器，自改造后形成「主 Agent 编排 + 专职 worker 执行 + Reflection 自演化 + 能力扩展 SOP」的分工平台。

**一句话画像**：opencode-custom 是**「以内核为底座、以 10 agent / 45 skill（单根统一）/ 6 MCP 装配，在装配层定向补强 E/R 弱环、落地架构判断三层栈、并借能力扩展 SOP 获得二阶自我扩展能力，把前馈主导控制器升级为跨会话自演化闭环编排平台」的个人变体**——它没有重造引擎，而是用协议、专职 worker、领域门控与记忆系统把官方最弱的两环反转为强环，代价是闭环仍需人工确认、一键分发与完整沙箱缺席。

---

### 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S4 | 一手配置观察 | `07-checkpoint/opencode-custom-snapshot/opencode.jsonc`（agent/provider/mcp/permission/compaction 原文） | 高 |
| SRC-002 | S4 | 一手协议观察 | `07-checkpoint/opencode-custom-snapshot/instructions__auto-mode.md`（GATE/COMPLEXITY/variant/子Agent规则/委派/Reflection自检/压缩模板；原 agent-protocol.md 已并入） | 高 |
| SRC-003 | S4 | 一手协议观察 | `07-checkpoint/opencode-custom-snapshot/instructions__architecture-behavior.md`（架构触发规则/知识分层/openspec design 门控） | 高 |
| SRC-004 | S4 | 一手协议观察 | `07-checkpoint/opencode-custom-snapshot/instructions__search-behavior.md`（外部信息实证/时效准则/信源分级） | 高 |
| SRC-005 | S4 | 一手命令观察 | `07-checkpoint/opencode-custom-snapshot/command__arch.md`（/arch 场景路由 / architect-worker 委派 / gate_architecture.py 门控流程） | 高 |
| SRC-006 | S4 | 一手命令观察 | `07-checkpoint/opencode-custom-snapshot/command__reflection.md`（三池扫描/签名门禁/容量分层/双版本同步） | 高 |
| SRC-007 | S4 | 一手盘点 | `07-checkpoint/opencode-custom-snapshot/inventory.json`（10 agents / 6 MCP / 45 skills + `_shared` 单根 / 5 instructions / 2 commands） | 高 |
| SRC-008 | S4 | 一手能力包观察 | `skills/architecture-judgment/`（SKILL.md + 内置 167 节点方法论图谱 + schemas + `_private/gate_architecture.py`） | 高 |
| SRC-009 | S4 | 一手能力包观察 | `skills/opencode-capability-extension/`（能力扩展 SOP：三层栈/统一双根/引用普查/契约+门控+冒烟） | 高 |
| SRC-010 | S1 | 可复算评分 | `09-src-data/opencode_custom_scores.py`（官方 2.9 / 自改造 3.9，8 维与五环分值单一数据源） | 高 |
| SRC-011 | S1 | 评分模型 | `07-checkpoint/premium-scoring-model.md`（精装度 v2.0：硬门槛 + 8 维加权 + 一票否决） | 高 |
| SRC-012 | S4 | 对照基线 | `03-cases/opencode.md`（官方 opencode 内核五环结构与结论口径，已升 1.18.30） | 高 |
| SRC-013 | S1 | 框架契约 | `02-framework/framework.md`、`00-contract/contract.md`（五环定义与信源分级规范） | 高 |
