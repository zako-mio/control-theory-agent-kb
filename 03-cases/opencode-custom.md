# opencode-custom（自改造 opencode）— Agent 控制论画像

> 本画像定位为官方 opencode 的衍生变体·个人装配层，基线是官方默认 + 最小常规装配（四 agent + 官方内置 skills + 基础 provider）。证据强度为源码级（配置级），全部结论可回溯至 `07-checkpoint/opencode-custom-snapshot/` 快照原文。与官方 opencode 的关系是「内核继承 + 装配层增强」：不改动 opencode 引擎源码，仅在配置/协议/skill/MCP/记忆系统五层做定向补强，把官方偏开环的 Plan-and-Execute 内核改造为可自演化的闭环编排平台。

## 0. 精装度评估

> 定位：个人装配层（官方 opencode 衍生变体）｜ 精装度：3.9/5 ｜ 分类：个人变体（官方衍生）｜ 一手/二手：一手 ｜ 证据强度：源码级（配置级）

**综合评分**：3.9/5 — 在内核继承官方基线之上，以协议层、专职 worker、skill 库、MCP、Reflection 记忆系统做定向补强，8 维中 6 维较官方提升，精装度从 2.9 跃升至 3.9，但一键部署与完整沙箱仍受个人装配限制。

**预装能力表**：

| 维度 | 预装情况 | 依据 |
|------|---------|------|
| 多Agent编排 | ✅ | 9 agent（+5 专职 worker：pdf/drawio/vision/reflection/search）+ 委派协议 + 并行 + subagent_depth=2；无真 DAG 画布 |
| Skill库 | ✅ | 28 skills + 11 legacy（精选库，非市场） |
| 工作流 | ✅ | GATE/COMPLEXITY 门控 + 契约驱动 + 委派接力协议 |
| 模型接入 | ✅ | 3 provider（opencode-go/deepseek/zhipu）+ 多模型 + 手动切换 |
| 一键部署 | 部分 | 个人 config 需手动复制装配层，无一键分发 |
| 沙箱 | 部分 | external_directory 白名单 + /tmp/opencode 隔离区，仍非完整沙箱 |
| MCP生态 | ✅ | 6 MCP（vscode/amap/pdf-reader/drawio×2/headroom）多传输 |
| 记忆 | ✅ | MEMORY.md 跨会话 + pending.json 结构化状态 + reflection-worker |

**声称 vs 实际**：个人变体不涉营销，配置声称的能力均经快照实证，无失实项；8 维打分依据逐一对应 `07-checkpoint/opencode-custom-snapshot/opencode.jsonc` 与 `inventory.json`，分值由 `09-src-data/opencode_custom_scores.py` 可复算。

## 1. 设定值（Setpoint）——用户意图 → 可验证子目标

**承担角色**：由「GATE 强制自评 + COMPLEXITY 复杂度标记 + grill-me/question 目标澄清 + 契约驱动委派协议」共同承担，把模糊意图先分解为带复杂度标签、带推理深度约束、可接力传递的子目标序列，官方内核的 AGENTS.md/plan 里程碑分解被装配层协议进一步结构化。

**关键机制**：
- **GATE 强制门控作为设定值入口**：`instructions/auto-mode.md` 规定主 Agent 收到任务后第一条消息必须输出 `[GATE] 范围=X 深度=X 操作=X 风险=X → 总分=XX → Daily|Deep`，把「任务该用多大推理深度」显式固化，不可跳过。
- **COMPLEXITY 跨阶段继承**：Plan 阶段收敛摘要必须含 `[COMPLEXITY: X/20]`，Build 阶段检测到该标记必须使用匹配推理深度、不得重新评估——设定值从规划层刚性传递到执行层，避免深度漂移。
- **grill-me 目标澄清协议**：`opencode.jsonc` 中 plan/build 的 prompt 内联 Grill-Me Protocol，要求逐分支访谈、一次一问、每轮以 `question` 工具收尾，直到设计树所有分支收敛；`question` 是结构化传感器而非自由文本。
- **契约驱动委派**：`agent-protocol.md` 第 3 步定义子 Agent prompt 契约（Identity/Role/Skills/Task/Model Selection/Return Format），设定值以契约文件与结构化 JSON 回传，跨 Agent 可溯源。
- **留档路径正则门控**：`agent-protocol.md` 规定留档路径须匹配 `Mission-file\d{4}-\d{2}\d{4}-.*\`，不通过则拒绝保存——设定值附带可验证的落盘约束。

**控制论映射**：KT-ctrl-045（规划-执行解耦，契约即里程碑参考序列）/ KT-ctrl-041（分层时标，GATE 决定慢/快推理档）/ KT-ctrl-002（设定值 r = 用户意图）。

**强弱项**：强——设定值有强制 GATE 入口、复杂度可跨阶段继承、目标澄清走结构化 question、委派走可溯源契约；弱——设定值仍以 prompt 文本编码为主，无机器可验证的定量目标函数，COMPLEXITY 是自评而非外部测量。

**双层评分**：内核 3.5/5 + 装配层 Δ+1.0 → 综合 4.5/5（增强）

---

## 2. 传感器 / 评估环（E 环）——测"当前执行是否达标"

**承担角色**：由「search-behavior 外部信息实证准则 + search-worker 证据包 + grill-me/question 用户传感器 + 视觉降级规则 + GATE 自评」承担，官方内核缺失的独立 Critic/verifier 被装配层以「外部事实核查管线 + 结构化用户确认」补齐，评估从「只测是否重复/是否改文件」升级为「可测事实是否经多源交叉验证」。

**关键机制**：
- **search-behavior 信源分级传感器**：`instructions/search-behavior.md` 规定依赖外部事实的结论必须先搜索并打开原始页面、区分「已验证事实/基于证据的推断/尚不确定」、重要结论 ≥2 独立来源交叉验证——把评估标准编码为可执行准则。
- **search-worker 专职证据包**：`opencode.jsonc` 新增 search-worker（发现+获取+交叉验证，输出结构化证据包），把「外部信息是否可信」这一语义评估外包给专职 Agent。
- **grill-me/question 用户传感器**：plan/build 内联 Grill-Me Protocol 强制每轮以 `question` 工具收尾，用户确认即反馈信号；`[GRILL]` 确认与选项式提问降低观测噪声。
- **视觉降级规则**：`agent-protocol.md` 规定会话模型无视觉时不得 Read 图片，改委派 vision-worker 代看，失败降级为 PNG 结构校验——为「图像是否达标」提供降级传感器路径。
- **GATE 自评作为元评估**：主 Agent 在动手前对范围/深度/操作/风险四维自评，是「该投入多少评估资源」的前置传感器。

**控制论映射**：KT-ctrl-006（强校验降低对基座模型误差敏感）/ KT-ctrl-035（DOB 式在线评估外部偏移，search-worker 交叉验证）/ KT-ctrl-012（观测噪声 R，信源分级=按可信度加权）/ KT-ctrl-001（E 环是闭环开关）。

**强弱项**：强——补上了官方最弱环：外部事实有了专职核查管线与信源分级，用户确认结构化，视觉有降级路径；弱——仍无独立 Critic 模型对「语义是否达标」做强验证，search-behavior 是准则而非自动门控，达标判定仍依赖 Agent 自律执行。

**双层评分**：内核 2.0/5 + 装配层 Δ+2.0 → 综合 4.0/5（反转）

---

## 3. 执行器 / 工具环（T 环）——工具调用容错与安全约束

**承担角色**：在官方内核「shell 看门狗 + 输出截断 + 权限仲裁 + AI-SDK 修复」之上，装配层以「6 MCP 多传输 + external_directory 白名单 + bash 危险命令 deny + 专职 worker 工具隔离」扩展执行器边界，形成「内核硬容错 + 装配层工具生态」的双层执行器。

**关键机制**：
- **6 MCP 集成**：`opencode.jsonc` 配置 vscode-mcp-server/amap/pdf-reader/drawio/drawio-local/headroom 六个 MCP（多传输），pdf-reader/drawio 启用并仅授权对应 worker，vscode/amap/headroom 因开销或量化亏损禁用——工具接入可插拔且受权限收口。
- **权限分层白名单**：全局 `external_directory` 默认 allow、`~/.ssh|~/.aws|~/.gnupg` deny；`read` 追加 auth.json deny；`bash` 对 `python -c *`、`rm -rf *`、`git push *` deny，对 Set-Content/Out-File/Remove-Item -Force 设 ask。
- **edit 分层授权**：`edit` 分层只放 agent.build 与 5 个写入型子 Agent（不放全局，避免覆盖 plan/explore 内置 deny），允许 `~/opencode/**`、`tmp/opencode/**`、`~/mnt/d/Opencode_Download/**`，其余 ask。
- **专职 worker 工具隔离**：pdf-worker 仅 `pdf-reader_*` allow、drawio-worker 仅 `drawio_*` allow，且 task 权限仅放行 vision-worker；`subagent_depth=2` 限制递归深度。
- **内核继承的执行器护栏**：沿用官方 shell 超时看门狗、输出截断 anti-windup、权限 ask/deny/always 仲裁、AI-SDK 工具名修复。

**控制论映射**：KT-ctrl-034（硬约束限幅+看门狗，bash deny/ask 白名单）/ KT-ctrl-033（冗余与仲裁，多 MCP 与专职 worker 分工）/ KT-ctrl-031（鲁棒稳定，权限收口防越权）/ KT-ctrl-030（模型不确定性，edit ask 为不确定动作留降级）。

**强弱项**：强——在官方最强环上叠加了 MCP 生态与细粒度权限白名单，工具边界可插拔且最小授权；弱——容错仍以外部规则为主，缺异质冗余多数表决（NMR/TMR），MCP 有 3 个处于禁用态（工具面实际收窄）。

**双层评分**：内核 4.5/5 + 装配层 Δ+0.5 → 综合 5.0/5（增强）

---

## 4. 记忆 / 状态估计环（M 环）——会话记忆与跨会话长期记忆

**承担角色**：在官方「SQLite Session + compaction 分层压缩 + context-epoch 增量基线」的会话级记忆之上，装配层以「MEMORY.md 跨会话长期记忆 + pending.json 结构化状态机 + reflection-worker 异步写入 + compaction 参数调优」补齐官方缺失的跨会话记忆层，形成「会话内两级卡尔曼 + 跨会话结构化状态」的记忆体系。

**关键机制**：
- **MEMORY.md 跨会话长期记忆**：`~/.config/opencode/MEMORY.md` 作为 instructions 注入，以 `§` 分段 + `[src: cycle_id]` 签名承载跨会话沉淀的知识，是官方内核所无的持久记忆层。
- **pending.json 结构化状态机**：`agent-protocol.md` 的 Reflection 自检规则规定启动时检查 `pending.json` 的 `meta.waiting_count`，按 waiting→processing→done/expired 状态流转——把「待反思的经验」建模为可恢复的结构化状态。
- **compaction 参数调优**：`opencode.jsonc` 设 `tail_turns=4`、`preserve_recent_tokens=16384`、`reserved=10000`，与 auto-mode.md 的 L1 剪枝/L2 结构化压缩/L3 兜底摘要阶梯配合，控制状态估计的更新预算。
- **reflection-worker 异步写入**：专职子 Agent 分析 Plan+Build 周期并生成 Memory/Skill 条目，写入 `memory_pending/` 滞留池，避免阻塞主流程。
- **官方内核记忆继承**：SQLite session 持久化、compaction 分层压缩、context-epoch 增量基线、revert 快照回滚。

**控制论映射**：KT-ctrl-011（卡尔曼式预测-更新，context-epoch 为预测、compaction 为更新）/ KT-ctrl-014（信息滤波/降维，结构化压缩模板）/ KT-ctrl-010（状态估计，MEMORY.md 维护跨会话信念）。

**强弱项**：强——补上了官方「无跨会话长期记忆」的短板，MEMORY.md + pending.json + reflection-worker 构成可溯源、可恢复的长期状态层；弱——长期记忆写入需经 /reflection 人工确认，容量受 MEMORY.md 约 5000 字符约束，pending.json 存在滞留池双轨写入断链风险。

**双层评分**：内核 3.5/5 + 装配层 Δ+0.5 → 综合 4.0/5（增强）

---

## 5. 规划 / 分层环（P 环）——慢/快双速 + 专职编排平台

**承担角色**：在官方「plan（慢规划）+ build（快执行）+ task 委派 + subagent_depth」的双速结构之上，装配层以「+5 专职 worker + GATE/COMPLEXITY 推理档分层 + 契约驱动委派接力 + 并行分片规范」把单体双速规划器升级为分层编排平台，慢/快之外新增「专职能力层」。

**关键机制**：
- **专职 worker 能力层**：pdf-worker/drawio-worker/vision-worker/reflection-worker/search-worker 五个隐藏子 Agent，各自封装领域能力，主 Agent 只编排不钻细节（options 式技能抽象）。
- **GATE/COMPLEXITY 推理档分层**：GATE 自评 ≤12 走 Daily、≥13 走 Deep，COMPLEXITY 标记跨 Plan→Build 继承，慢/快推理资源随任务复杂度动态分配。
- **契约驱动委派接力**：`agent-protocol.md` 规定独立任务并行 Task、依赖任务串行接力（data 传递）、紧密耦合流程交 1 个 Agent，配合结构化 JSON 回传实现编排接力。
- **并行与批处理规范**：auto-mode.md 规定互不依赖的只读操作必须并行发出、相邻同类只读合并批次、不混合读写——把并行度约束编码为协议。
- **深度限制与恢复**：`subagent_depth=2` 限制递归，`task_id` 支持恢复同一子会话；沿用官方 plan/build 双速与并行 explore。

**控制论映射**：KT-ctrl-041（分层时标，慢 plan/快 build/专职 worker 三层）/ KT-ctrl-043（时间尺度分离 ε，Daily/Deep 与主/子 Agent 成本频率比）/ KT-ctrl-044（MPC 滚动时域，契约接力与观察回调）/ KT-ctrl-045（规划-执行解耦）/ KT-ctrl-046（options/SMDP，worker 即高层动作原语）。

**强弱项**：强——官方最强环再升级为分层编排平台，专职 worker 提供时序抽象、推理档动态分配、并行规范可执行；弱——仍是「一次切换 + 人工介入」，缺 MPC 式自动滚动重规划，无真 DAG 画布，编排拓扑靠协议文本而非可视化约束。

**双层评分**：内核 4.5/5 + 装配层 Δ+0.5 → 综合 5.0/5（增强）

---

## 6. 反思 / 反馈闭环环（R 环）——从半开环到自演化闭环

**承担角色**：在官方「错误回灌 + doom_loop + revert + 重试」的弱 R 环之上，装配层以「Reflection 自演化系统（MEMORY.md + pending.json + reflection-worker + /reflection 命令）+ 留档 5 段模板 + 经验教训回写」把反思从内核的局部错误回灌升级为跨会话的元认知闭环，实现「开环主导 → 闭环自演化」的反转。

**关键机制**：
- **Reflection 自检规则**：`agent-protocol.md` 规定每轮收到用户消息先检查 pending.json 的 waiting_count，有 waiting 则委派 reflection-worker 处理——把反思从「可选」变为「启动即触发」。
- **4 层输入封装**：每个 Plan+Build 周期完成后封装 Layer A（GATE/COMPLEXITY/决策）+ B（子 Agent JSON/聚合摘要）+ C（MEMORY 快照）+ D（留档报告）写入 pending.json，反思输入结构化。
- **/reflection 交互式审阅**：`command/reflection.md` 定义三池扫描（pending.json / memory_pending / manual_pending）、统一分析优先+逐条兜底、独立性/重复性三分类、容量 A/B/C/D 分层、`[src: cycle_id]` 签名门禁、双版本同步。
- **留档 5 段模板**：`agent-protocol.md` 要求报告含当时情况/制定计划/执行情况/完成情况/反思分析建议 5 段，缺段不合格，把反思固化为交付物必选项。
- **官方内核 R 环继承**：工具错误回灌、doom_loop 防震荡、revert 用户纠偏、LLM 重试退避。

**控制论映射**：KT-ctrl-002（负反馈闭环，误差=执行与目标偏差）/ KT-ctrl-020~023（PID 三环节，P=当轮错误回灌、I=跨会话 MEMORY 累积、D=留档反思预判）/ KT-ctrl-004（误差收敛，签名门禁防污染）/ KT-ctrl-025（稳态误差，人工确认作为积分项限幅）。

**强弱项**：强——补上官方最弱的 R 环：反思启动自动触发、输入结构化、审阅有签名门禁与容量分层、产物回写长期记忆，形成跨会话自演化闭环；弱——闭环仍需 /reflection 人工确认，反馈有滞后，pending.json 滞留池存在写入断链，反思质量依赖 reflection-worker 单模型。

**双层评分**：内核 2.0/5 + 装配层 Δ+2.5 → 综合 4.5/5（反转）

---

## 七大核心环强弱总评

| 环 | 承担角色 | 强度 | 主控概念 |
|---|---------|:---:|---------|
| **设定值** | GATE + COMPLEXITY + grill-me/question 目标澄清 | 🟢 强 | KT-ctrl-045 规划-执行解耦 |
| **E 评估** | search-behavior + search-worker + 用户确认 + 视觉降级 | 🟢 强（由最弱反转） | KT-ctrl-035 扰动观测器 |
| **T 执行** | 6 MCP + 权限白名单 + 专职 worker 工具隔离 | 🟢 **最强** | KT-ctrl-034 限幅/看门狗 |
| **M 记忆** | MEMORY.md 跨会话 + pending.json + compaction 调优 | 🟢 强 | KT-ctrl-011 卡尔曼式滤波 |
| **P 规划** | plan/build 双速 + 5 专职 worker + 契约接力 | 🟢 **最强** | KT-ctrl-044/045 MPC + 解耦 |
| **R 反思** | Reflection 自演化系统 + 留档 5 段 + 经验回写 | 🟢 强（由弱反转） | KT-ctrl-002 负反馈闭环 |

## opencode-custom 控制论画像总结

**整体范式：在官方前馈主导内核上做弱环定向补强，把「开环为主 + 局部闭环」改造为「分层编排 + 跨会话自演化闭环」的闭环控制器。**

- **最突出的环：P 环（分层编排）与 T 环（执行器安全）**——官方本就最强的两环被继续加固：P 环从双速升级为「plan/build/专职 worker」三层编排平台，T 环从内核护栏扩展到 6 MCP + 细粒度权限白名单。
- **关键反转：E 环与 R 环**——官方两大最弱环被装配层补齐：E 环以 search-behavior 信源分级 + search-worker 证据包 + 结构化用户确认反转；R 环以 Reflection 自演化系统（pending.json 状态机 + reflection-worker + /reflection 签名门禁）从半开环升级为跨会话闭环。
- **精装度跃升：2.9 → 3.9（Δ+1.0）**——8 维中 6 维提升，记忆维达满分 5，模型/工作流/skill/MCP 均 +1 至 +2，仅一键部署与完整沙箱受个人装配限制未提升。
- **从单体到分层编排平台**：官方是单体双速控制器，自改造后形成「主 Agent 编排 + 专职 worker 执行 + Reflection 自演化」的三层分工平台。

**一句话画像**：opencode-custom 是**「以内核为底座、在装配层定向补强 E/R 弱环、把前馈主导控制器升级为跨会话自演化闭环编排平台」的个人变体**——它没有重造引擎，而是用协议、专职 worker 与记忆系统把官方最弱的两环反转为强环，代价是闭环仍需人工确认、一键分发与完整沙箱缺席。

---

### 📚 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S4 | 一手配置观察 | `07-checkpoint/opencode-custom-snapshot/opencode.jsonc`（agent/provider/mcp/permission/compaction 原文） | 高 |
| SRC-002 | S4 | 一手协议观察 | `07-checkpoint/opencode-custom-snapshot/instructions__auto-mode.md`（GATE/COMPLEXITY/variant/子Agent规则/压缩模板） | 高 |
| SRC-003 | S4 | 一手协议观察 | `07-checkpoint/opencode-custom-snapshot/instructions__agent-protocol.md`（委派/Reflection自检/MCP路由/编码安全/留档） | 高 |
| SRC-004 | S4 | 一手协议观察 | `07-checkpoint/opencode-custom-snapshot/instructions__search-behavior.md`（外部信息实证/时效准则/信源分级） | 高 |
| SRC-005 | S4 | 一手命令观察 | `07-checkpoint/opencode-custom-snapshot/command__reflection.md`（三池扫描/签名门禁/容量分层/双版本同步） | 高 |
| SRC-006 | S4 | 一手盘点 | `07-checkpoint/opencode-custom-snapshot/inventory.json`（9 agents / 6 MCP / 28 skills + 11 legacy） | 高 |
| SRC-007 | S1 | 可复算评分 | `09-src-data/opencode_custom_scores.py`（官方 2.9 / 自改造 3.9，8 维分值单一数据源） | 高 |
| SRC-008 | S1 | 评分模型 | `07-checkpoint/premium-scoring-model.md`（精装度 v2.0：硬门槛 + 8 维加权 + 一票否决） | 高 |
| SRC-009 | S4 | 对照基线 | `03-cases/opencode.md`（官方 opencode 内核五环结构与结论口径） | 高 |
| SRC-010 | S1 | 框架契约 | `02-framework/framework.md`、`00-contract/contract.md`（五环定义与信源分级规范） | 高 |
