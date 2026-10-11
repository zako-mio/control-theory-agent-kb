# opencode-custom（自改造 opencode）— Agent 控制论画像

> 本画像定位为官方 opencode 的衍生变体·个人装配层，基线是官方默认 + 最小常规装配（四 agent + 官方内置 skills + 基础 provider）。证据强度为源码级（配置级），全部结论可回溯至 `07-checkpoint/opencode-custom-snapshot/` 快照原文（`collected_at = 2026-10-11T17:04:12+08:00`；旧版归档为 `inventory-v1.3.json`）。与官方 opencode 的关系是「内核继承 + 装配层增强」：不改动 opencode 引擎源码，仅在配置/协议/skill/MCP/记忆系统五层做定向补强，把官方偏开环的 Plan-and-Execute 内核改造为可自演化的闭环编排平台。当前装配口径为 **9 agent / 45 可加载 skill（顶层 46 目录 + `skills/disabled/` 4 件）/ 4 MCP / 3 command / 6 instructions / 2 plugins / 6 providers**，纵深机制为「**双领域三层栈**（架构判断 + 需求发现）」与「能力扩展 / 能力体检**姊妹 SOP** + 判据方法论」。

## 0. 精装度评估

> 定位：个人装配层（官方 opencode 衍生变体）｜ 精装度：3.9/5 ｜ 分类：个人变体（官方衍生）｜ 一手/二手：一手 ｜ 证据强度：源码级（配置级）

**综合评分**：3.9/5 — 在内核继承官方基线之上，以协议层、专职 worker、skill 库、MCP、Reflection 记忆系统做定向补强，8 维中 6 维较官方提升，精装度从 2.9 跃升至 3.9，但一键部署与完整沙箱仍受个人装配限制。**本轮（v1.4，2026-10-11）维持 3.9**，理由＝**净变化为「能力纵深 + 结构调整 + 2 项损失」的混合，无任一维度跨 5 档阈值**：agent 10→9 与 MCP 6→4 属**结构调整**（退役项与新机制相抵；档位判的是「有无并行/委派编排」与「平台接外部世界的可扩展成本」，非计数）；新增需求发现三层栈、判据方法论、能力体检 SOP 与 2 个治理插件属**能力纵深**；同时**登记 2 项能力损失**（L1 视觉代看机制退役、L2 MCP 工具面收窄，见 §8.3）。封顶因素（一键部署=个人 config 无分发、沙箱=非 VM 隔离）未变。

**预装能力表**：

| 维度 | 预装情况 | 依据 |
|------|---------|------|
| 多Agent编排 | 具备 | **9 agent**（plan/build/general/explore + **5 专职 worker**：pdf / architect / reflection / search / requirement-discovery）+ 委派协议 + 并行 + `subagent_depth=1`；`inventory.agents=9`——drawio-worker 与 vision-worker 已于 0915 退役，新增 requirement-discovery-worker；**agent 数由 10 降至 9 不构成降档**（档位判「有无并行/委派编排」而非 worker 个数），仍无真 DAG 画布（未达 5 档市场级编排） |
| Skill库 | 具备 | **45 个可加载 SKILL.md**（顶层 46 目录 + `skills/disabled/` 4 件停用：amap×3 + model-switcher；另含 `_shared`）+ 单根统一；本轮新增 criterion-design-validation / design-material-library / diagram-lite / opencode-capability-audit / requirement-discovery / version-upgrade-cascade；仍为精选个人库、无市场/分发（未达 5 档） |
| 工作流 | 具备 | GATE/COMPLEXITY 门控 + 契约驱动 + 委派接力 + **双领域三层栈 gated SOP**（架构：`/arch` + architecture-behavior + architecture-judgment + gate_architecture.py；需求发现：`/rd` + requirement-discovery-behavior + requirement-discovery + 分层定档工具）；无通用可视化工作流/DAG 引擎（未达 5 档） |
| 模型接入 | 具备 | **6 provider**（opencode-go / opencode-go-tmp / deepseek / zhipu / commandcode / commandcode-free；0927 按「一 key 一变量名」把 commandcode 拆为付费/免费双 provider）+ deepseek-flash V4.1 原生多模态 + @ai-sdk/openai-compatible 图片链路；仍非「数百模型开箱」（未达 5 档） |
| 一键部署 | 部分 | 个人 config 需手动复制装配层，无一键分发（仍为个人变体定位，无 npm/docker/SaaS 分发） |
| 沙箱 | 部分 | external_directory 白名单 + /tmp/opencode 隔离区，仍非完整沙箱/VM 隔离 |
| MCP生态 | 具备 | **4 MCP**（vscode-mcp-server / amap / pdf-reader / headroom，多传输；**1 enabled=pdf-reader**）；**drawio / drawio-local 已退役**（制图改走 `diagram-lite` skill 档位，损失 L2）。**判据说明**：本维量的是「平台接外部世界的可扩展成本」——**多传输能力未变，server 数与启用数属用户配置选择**，故曾触及 4→3 边界仍**维持 4**（口径已在 `09-src-data/opencode_custom_scores.py` 文件头登记） |
| 记忆 | 具备 | MEMORY.md 跨会话（**13137 B / 15 段**）+ pending.json 结构化状态机 + reflection-worker + compaction 调优；2026-10-10 三轮 `/reflection` **生命周期治理 −46%**（24318 → 13137 B，字符 −41%，tokens 9753 → 5264，**段数零和**）+ 机检 `scripts/memory_capacity_check.py`（满分档） |

**声称 vs 实际**：个人变体不涉营销，配置声称的能力均经快照实证，无失实项；8 维打分依据逐一对应 `07-checkpoint/opencode-custom-snapshot/opencode.jsonc` 与 `inventory.json`，分值由 `09-src-data/opencode_custom_scores.py` 可复算，两者口径一致。本轮另补两条**诚实登记**：

1. **「数量下降 ≠ 能力下降」**：agent 10→9（−drawio-worker −vision-worker，+requirement-discovery-worker）与 MCP 6→4（−drawio −drawio-local）**均属结构调整**，不是能力缩水的自动证据——但**其中确有两项是真损失**（下条），故不把「结构调整」当作免责话术，而是逐项标注去留与补偿路径。
2. **两项能力损失 L1 / L2 已登记**：**L1** vision-worker 于 0915 废除 → E 环少一条「图像是否达标」的降级传感器路径（改为会话模型原生视觉直读，无视觉时**由人终判**）；**L2** drawio / drawio-local 两个 MCP 退役 → 配置 server 数 6→4、启用数 2→1（改为 `diagram-lite` skill 档位出图，不委派制图子 Agent、不装绘图 MCP）。**损失登记不得被增长叙述吞掉**，详见 §8.3。

## 1. 设定值（Setpoint）——用户意图 → 可验证子目标

**承担角色**：由「GATE 强制自评 + COMPLEXITY 复杂度标记 + grill-me/question 目标澄清 + `/arch` 架构任务路由 + `/rd` 需求发现路由 + 契约驱动委派协议」共同承担，把模糊意图先分解为带复杂度标签、带推理深度约束、可接力传递的子目标序列，官方内核的 AGENTS.md/plan 里程碑分解被装配层协议进一步结构化。

**关键机制**：
- **GATE 强制门控作为设定值入口**：`instructions/auto-mode.md` 规定主 Agent 收到任务后第一条消息必须输出 `[GATE] 范围=X 深度=X 操作=X 风险=X → 总分=XX → Daily|Deep`，把「任务该用多大推理深度」显式固化，不可跳过。
- **COMPLEXITY 跨阶段继承**：Plan 阶段收敛摘要必须含 `[COMPLEXITY: X/20]`，Build 阶段检测到该标记必须使用匹配推理深度、不得重新评估——设定值从规划层刚性传递到执行层，避免深度漂移。
- **grill-me 目标澄清协议**：`opencode.jsonc` 中 plan/build 的 prompt 内联 Grill-Me Protocol，要求逐分支访谈、一次一问、每轮以 `question` 工具收尾，直到设计树所有分支收敛；`question` 是结构化传感器而非自由文本。
- **双领域路由入口（本轮扩展）**：`command/arch.md` 定义 `/arch <任务描述>`（架构类意图按 `routing.md` 的 18 场景索引归入命中场景，判定产出类型 adr/boundary/review/tech-debt 后才委派）；`command/rd.md` 定义 `/rd <需求描述>`（需求发现入口，**一律复杂档**，产出 POV/HMW/product outcome/appetite/最小交接契约）——设定值先物化为「场景号 + 产出类型 + 结构化契约」再进入执行。
- **双行为指令触发约束（本轮扩展）**：`instructions/architecture-behavior.md` 规定架构类任务必须加载 `architecture-judgment` skill + 委派 `architect-worker` + 过门控；`instructions/requirement-discovery-behavior.md`（**压紧 ≤22 行**）规定**定档前置**——先跑 K1–K5＋M1 判定器，**简单档不加载/不委派/不产工件**，且 ⛔ 不产 ADR/specs/tasks/代码——把「什么算架构任务 / 什么算需求发现任务、各走哪条设定值路径」固化为刚性触发规则。
- **契约驱动委派**：`instructions/auto-mode.md` 定义子 Agent prompt 契约（Identity/Role/Skills/Task/Model Selection/Return Format），设定值以契约文件与结构化 JSON 回传，跨 Agent 可溯源（原 `agent-protocol.md` 已并入 auto-mode.md；该文件本轮仍**落盘但有意不注册**）。
- **留档路径正则门控**：auto-mode.md 规定留档路径须匹配 `Mission-file\d{4}-\d{2}\d{4}-.*\`，不通过则拒绝保存——设定值附带可验证的落盘约束。

**控制论映射**：KT-ctrl-045（规划-执行解耦，契约即里程碑参考序列）/ KT-ctrl-041（分层时标，GATE 决定慢/快推理档）/ KT-ctrl-002（设定值 r = 用户意图）/ KT-ctrl-046（options/SMDP，`/arch` 与 `/rd` 场景路由即把意图映射为动作原语）。

**强弱项**：强——设定值有强制 GATE 入口、复杂度可跨阶段继承、目标澄清走结构化 question、**架构与需求发现两类意图各有显式路由**、委派走可溯源契约；弱——设定值仍以 prompt 文本编码为主，无机器可验证的定量目标函数，COMPLEXITY 是自评而非外部测量。

**双层评分**：内核 3.5/5 + 装配层 Δ+1.0 → 综合 4.5/5（增强）

---

## 2. 传感器 / 评估环（E 环）——测"当前执行是否达标"

**承担角色**：由「search-behavior 外部信息实证准则 + search-worker 证据包 + gate_architecture.py ADR schema 门控 + 需求发现分层定档工具 + criterion-design-validation 判据方法论 + grill-me/question 用户传感器 + GATE 自评」承担，官方内核缺失的独立 Critic/verifier 被装配层以「外部事实核查管线 + 领域级自动门控 + 判据方法论 + 结构化用户确认」补齐，评估从「只测是否重复/是否改文件」升级为「可测事实是否多源交叉验证、领域产出是否过 schema 机检、判据本身是否可信」。

**关键机制**：
- **search-behavior 信源分级传感器**：`instructions/search-behavior.md` 规定依赖外部事实的结论必须先搜索并打开原始页面、区分「已验证事实/基于证据的推断/尚不确定」、重要结论 ≥2 独立来源交叉验证——把评估标准编码为可执行准则。
- **search-worker 专职证据包**：`opencode.jsonc` 中 search-worker（发现+获取+交叉验证，输出结构化证据包），把「外部信息是否可信」这一语义评估外包给专职 Agent。
- **领域级自动门控（本轮扩为双域）**：`architecture-judgment` 的 `_private/gate_architecture.py --kind adr|boundary` 对 architect-worker 产出的 ADR/边界说明做 schema + 知识图谱机检；需求发现侧由 `_private/gate_requirement_discovery.py --kind stage2|handoff`（G-R1–G-R9 机检 + 11 例正负向自检 + ledger 回报通道）做分层定档机检。两者均退出码 0 才放行、FAIL 原样回传修正（≤2 轮）、不得降级为「口头通过」——E 环由单点门控扩为**双领域门控**（模板级 review/tech-debt 仍走人工确认）。
- **生产者-验证者打通（0916 D-01 范式）**：两个产出方 worker 的 `bash` 白名单**只放行自己的门控脚本**（`python3 *gate_architecture.py*` / `python3 *gate_requirement_discovery.py*`），使产出方能自跑门控并回传输出原文，省去主 Agent 代跑的一轮往返，同时保持产出与验证的动作分离。
- **criterion-design-validation 判据方法论（本轮新增）**：把「判据（门控/机检/评分卡/词表/检查单）」的**构造—实现—验证—维护**四阶段固化为跨域方法论，专治**假绿 / 假跑 / 恒真判据 / 空集 / 阈值无推导**——E 环由此不仅「有门」，还「知道门本身可不可信」。
- **grill-me/question 用户传感器**：plan/build 内联 Grill-Me Protocol 强制每轮以 `question` 工具收尾，用户确认即反馈信号；`[GRILL]` 确认与选项式提问降低观测噪声。
- **GATE 自评作为元评估**：主 Agent 在动手前对范围/深度/操作/风险四维自评，是「该投入多少评估资源」的前置传感器。
- **本轮损失（L1）**：**视觉降级规则已改写**——vision-worker 于 0915 废除，「会话模型无视觉 → 委派 vision-worker 代看」的路径**不再存在**，改为「模型原生视觉直接 Read；模型无视觉 → **由人看**」。E 环因此**少一条可自动执行的「图像是否达标」降级传感器**（见 §8.3）。

**控制论映射**：KT-ctrl-006（强校验降低对基座模型误差敏感）/ KT-ctrl-035（DOB 式在线评估外部偏移，search-worker 交叉验证）/ KT-ctrl-012（观测噪声 R，信源分级=按可信度加权）/ KT-ctrl-001（E 环是闭环开关）。

**强弱项**：强——补上了官方最弱环：外部事实有了专职核查管线与信源分级，**架构与需求发现双域各有 schema 自动门控且产出方可自跑**，判据本身有方法论约束，用户确认结构化；弱——领域级自动门控仍限架构/需求发现两域（非通用独立 Critic 模型对「语义是否达标」做强验证），search-behavior 是准则而非自动门控，**且 L1 后图像达标判定在无视觉会话下退化为人工**，达标判定仍依赖 Agent 自律执行。

**双层评分**：内核 2.0/5 + 装配层 Δ+2.0 → 综合 4.0/5（反转；**有增有损相抵，维持 4.0**）

---

## 3. 执行器 / 工具环（T 环）——工具调用容错与安全约束

**承担角色**：在官方内核「shell 看门狗 + 输出截断 + 权限仲裁 + AI-SDK 修复」之上，装配层以「4 MCP 多传输 + external_directory 白名单 + bash 危险命令 deny + 专职 worker 工具隔离 + **2 个治理插件（插件钩子层）**」扩展执行器边界，形成「内核硬容错 + 装配层工具生态 + 钩子治理」的三层执行器。

**关键机制**：
- **4 MCP 集成（本轮收窄，损失 L2）**：`opencode.jsonc` 配置 vscode-mcp-server / amap / pdf-reader / headroom 四个 MCP（多传输），**仅 pdf-reader 启用**并仅授权 pdf-worker（agent 级 `pdf-reader_*: allow`，全局为 `deny` 兜底）；vscode/amap/headroom 因工具面小或量化亏损禁用。**drawio / drawio-local 已于 0915 随绘图链路重构退役**（原「drawio-worker → MCP 导出 → 视觉核对」三段链路改为 `diagram-lite` skill 档位出图：T0 文本退化 / T1 模板填空 / T2 DSL→SVG 默认 / T3 发布级）——工具面**由 6 收窄至 4、启用由 2 收窄至 1**；同时保留 `vscode-mcp-server_*: deny` 作为「re-enable 前置防御」（死配置但有意保留）。
- **插件钩子层（本轮新增机制层，8 维模型无对应维度）**：`plugins/` 下 2 个 TS 插件——
  - `system-date-transform.ts`：**prefix-cache 日期治理**。剥离 system 提示中的 `Today's date:` 行、并在**最后一条 user 消息**回注日期，使 system 前缀跨日不变、命中 prompt cache（日志 `~/.cache/opencode/plugin-system-date.log`，17277 行）；
  - `notify-on-pause.ts`：**会话暂停桌面通知**（配置单源 `~/.config/opencode/notify.json`，`enabled=true`；fire-and-forget 分离 spawn + fail-open；日志 `~/.cache/opencode/notify-plugin.log` 7045669 行 + `notify-receipts.log`）。
  两插件均为「钩子式执行器治理」：前者改的是**执行前的上下文形态**（成本面），后者改的是**执行后的状态可见性**（可观测面）。**说明**：本层是装配层新增的第六类机制（配置/协议/skill/MCP/记忆之外），8 维精装度模型无对应维度，故不参与打分，仅在本画像登记其存在与作用。
- **权限分层白名单**：全局 `external_directory` 默认 allow、`~/.ssh|~/.aws|~/.gnupg` deny；`read` 追加 auth.json 与 opencode.env deny；`bash` 对 `python -c *`、`rm -rf *`、`git push *` deny，对 Set-Content/Out-File/Remove-Item -Force 与 `opencode debug config*`（会批量输出明文 apiKey）设 ask。
- **edit 分层授权 + MEMORY 全局硬门禁**：`edit` 分层只放 agent.build 与写入型子 Agent（不放全局，避免覆盖 plan/explore 内置 deny），允许 `~/opencode/**`、`tmp/opencode/**`、`~/mnt/d/Opencode_Download/**`，其余 ask；**全局 `edit: MEMORY.md = deny`**（0914 G-01），agent 级末条胜出——**build 保留 allow 作为 `/reflection` 唯一合法写入路径**，其余 agent 命中全局 deny。
- **专职 worker 工具隔离**：pdf-worker 仅 `pdf-reader_*` allow；architect-worker 与 requirement-discovery-worker 各自 `task: {"*":"deny"}`（职责单一不自委派）+ bash 仅放行**自己的门控脚本**；`subagent_depth=1`（**0915 由 2 降回 1**：depth=2 的唯一用途——worker 再委派视觉子 Agent 代看图片——已随 vision-worker 废除而消失，现无任何子 Agent 持有 task 权限）。
- **内核继承的执行器护栏**：沿用官方 shell 超时看门狗、输出截断 anti-windup、权限 ask/deny/always 仲裁、AI-SDK 工具名修复。

**控制论映射**：KT-ctrl-034（硬约束限幅+看门狗，bash deny/ask 白名单）/ KT-ctrl-033（冗余与仲裁，多 MCP 与专职 worker 分工）/ KT-ctrl-031（鲁棒稳定，权限收口防越权）/ KT-ctrl-030（模型不确定性，edit ask 为不确定动作留降级）。

**强弱项**：强——在官方最强环上叠加了 MCP 生态与细粒度权限白名单，工具边界可插拔且最小授权，**MEMORY 写入有了权限层硬门禁**，插件钩子层补上了成本与可观测两个治理面；弱——容错仍以外部规则为主，缺异质冗余多数表决（NMR/TMR）；**MCP 工具面本轮实际收窄（L2）**，绘图能力由「MCP + 专职 worker」降级为「skill 档位」，属**能力换成本**的主动取舍而非免费增长。

**双层评分**：内核 4.5/5 + 装配层 Δ+0.5 → 综合 5.0/5（增强；**收窄与新增相抵，维持 5.0**）

---

## 4. 记忆 / 状态估计环（M 环）——会话记忆与跨会话长期记忆

**承担角色**：在官方「SQLite Session + compaction 分层压缩 + context-epoch 增量基线」的会话级记忆之上，装配层以「MEMORY.md 跨会话长期记忆 + pending.json 结构化状态机 + reflection-worker 异步写入 + compaction 参数调优 + **记忆容量生命周期治理（零和预算 + 边际显著性）**」补齐官方缺失的跨会话记忆层，形成「会话内两级卡尔曼 + 跨会话结构化状态 + 常驻预算零和」的记忆体系。

**关键机制**：
- **MEMORY.md 跨会话长期记忆**：`~/.config/opencode/MEMORY.md` 作为 instructions 注入，以 `§` 分段 + `[src: cycle_id]` 签名承载跨会话沉淀的知识，是官方内核所无的持久记忆层。**本轮现状：13137 B / 15 段**。
- **生命周期治理（本轮新增，2026-10-10）**：三轮 `/reflection` 深迁移把 MEMORY.md 由 **24318 B → 13137 B（−46%，字符 −41%，tokens 9753 → 5264，段数零和）**。原则落 `command/reflection.md` §4b（**零和预算** + **边际显著性三问**），细则下沉 `references/`——**从「只增不减」改为「有预算的常驻资产」**。
- **容量机检（本轮新增）**：`scripts/memory_capacity_check.py` 把治理原则变成可执行判据——单段占比 >50% 启用 / 段数默认关、`--baseline` 零和（段数相对前像增长即判 soft）/ 阈值按 Claude Code 与 Agent Skills 官方额度**推导式**给出；selftest **8 → 13 例**。
- **pending.json 结构化状态机**：auto-mode.md 的 Reflection 自检规则规定启动时检查 `pending.json` 的 `meta.waiting_count`，按 waiting→processing→done/expired 状态流转——把「待反思的经验」建模为可恢复的结构化状态。
- **compaction 参数调优**：`opencode.jsonc` 设 `tail_turns=4`、`preserve_recent_tokens=16384`、`reserved=10000`，与 auto-mode.md 的 L1 剪枝/L2 结构化压缩/L3 兜底摘要阶梯配合，控制状态估计的更新预算。
- **reflection-worker 异步写入**：专职子 Agent 分析 Plan+Build 周期并生成 Memory/Skill 条目，写入 `memory_pending/` 滞留池，避免阻塞主流程。
- **官方内核记忆继承**：SQLite session 持久化、compaction 分层压缩、context-epoch 增量基线、revert 快照回滚。

**控制论映射**：KT-ctrl-011（卡尔曼式预测-更新，context-epoch 为预测、compaction 为更新）/ KT-ctrl-014（信息滤波/降维，结构化压缩模板 + 零和预算）/ KT-ctrl-010（状态估计，MEMORY.md 维护跨会话信念）。

**强弱项**：强——补上了官方「无跨会话长期记忆」的短板，MEMORY.md + pending.json + reflection-worker 构成可溯源、可恢复的长期状态层，**且本轮起有零和预算与机检约束，不再是无限膨胀的黑箱**；弱——长期记忆写入虽已加全局 deny 硬门禁（仅 build 保留 allow 作为 `/reflection` 唯一合法写入路径），但**写入仍需经 `/reflection` 人工确认**，容量阈值中「字符 >5000」一项仍属**自愿纪律（无权威依据）**，pending.json 滞留池存在双轨写入断链风险。

**双层评分**：内核 3.5/5 + 装配层 Δ+0.5 → 综合 4.0/5（增强；**治理强化了置信度但未跨档，维持 4.0**）

---

## 5. 规划 / 分层环（P 环）——慢/快双速 + 专职编排平台

**承担角色**：在官方「plan（慢规划）+ build（快执行）+ task 委派 + subagent_depth」的双速结构之上，装配层以「+5 专职 worker + **双领域三层栈 gated SOP** + GATE/COMPLEXITY 推理档分层 + 契约驱动委派接力 + 并行分片规范」把单体双速规划器升级为分层编排平台，慢/快之外新增「专职能力层」。

**关键机制**：
- **专职 worker 能力层（结构重排：6→5）**：pdf-worker / architect-worker / reflection-worker / search-worker / requirement-discovery-worker 五个隐藏子 Agent，各自封装领域能力，主 Agent 只编排不钻细节（options 式技能抽象）；**drawio-worker 与 vision-worker 已随绘图链路重构退役**，**新增 requirement-discovery-worker** 专司需求发现与澄清。**worker 数由 6 降至 5，但领域覆盖由「制图+视觉」换为「需求发现」**——是能力结构的替换而非简单减少。
- **双领域三层栈 gated 编排（本轮由单域扩为双域）**：
  - **架构域**：主 Agent 按固定编排链执行「加载 architecture-judgment → 委派 architect-worker → 跑 gate_architecture.py 门控放行（FAIL 回传≤2 轮）→ 可选按 `diagram-lite` 档位出图」；
  - **需求发现域**：按 `/rd` 入口 → 加载 requirement-discovery → 委派 requirement-discovery-worker → 跑分层定档工具与 `gate_requirement_discovery.py`（stage2/handoff）门控放行。
  两域均把「领域编排」从自由组合固化为受门控的 SOP，且**产出方 worker 已获准自跑自己的门控脚本**（0916 D-01）。
- **GATE/COMPLEXITY 推理档分层**：GATE 自评 ≤12 走 Daily、≥13 走 Deep，COMPLEXITY 标记跨 Plan→Build 继承，慢/快推理资源随任务复杂度动态分配。
- **契约驱动委派接力**：auto-mode.md 规定独立任务并行 Task、依赖任务串行接力（data 传递）、紧密耦合流程交 1 个 Agent，配合结构化 JSON 回传实现编排接力。
- **并行与批处理规范**：auto-mode.md 规定互不依赖的只读操作必须并行发出、相邻同类只读合并批次、不混合读写——把并行度约束编码为协议。
- **深度限制与恢复**：`subagent_depth=1` 限制递归（0915 由 2 降回 1，理由见 T 环），`task_id` 支持恢复同一子会话；沿用官方 plan/build 双速与并行 explore。

**控制论映射**：KT-ctrl-041（分层时标，慢 plan/快 build/专职 worker 三层）/ KT-ctrl-043（时间尺度分离 ε，Daily/Deep 与主/子 Agent 成本频率比）/ KT-ctrl-044（MPC 滚动时域，契约接力与观察回调）/ KT-ctrl-045（规划-执行解耦）/ KT-ctrl-046（options/SMDP，worker 即高层动作原语）。

**强弱项**：强——官方最强环再升级为分层编排平台，专职 worker 提供时序抽象、**双领域任务各有受门控的固定编排链**、推理档动态分配、并行规范可执行；弱——仍是「一次切换 + 人工介入」，缺 MPC 式自动滚动重规划，无真 DAG 画布，编排拓扑靠协议文本而非可视化约束；**且 worker 编队收敛到 5 人，视觉与制图两条专职链已不存在**（转由会话模型原生能力 + skill 档位承接）。

**双层评分**：内核 4.5/5 + 装配层 Δ+0.5 → 综合 5.0/5（增强；已处 5.0 上限，worker 结构重排不改变分值）

---

## 6. 反思 / 反馈闭环环（R 环）——从半开环到自演化闭环

**承担角色**：在官方「错误回灌 + doom_loop + revert + 重试」的弱 R 环之上，装配层以「Reflection 自演化系统（MEMORY.md + pending.json + reflection-worker + `/reflection` 命令）+ **记忆生命周期治理（零和预算 + 边际显著性三问 + 机检）** + 留档 5 段模板 + 经验教训回写」把反思从内核的局部错误回灌升级为跨会话的元认知闭环，实现「开环主导 → 闭环自演化」的反转。

**关键机制**：
- **Reflection 自检规则**：auto-mode.md 规定每轮收到用户消息先检查 pending.json 的 waiting_count，有 waiting 则委派 reflection-worker 处理——把反思从「可选」变为「启动即触发」。
- **4 层输入封装**：每个 Plan+Build 周期完成后封装 Layer A（GATE/COMPLEXITY/决策）+ B（子 Agent JSON/聚合摘要）+ C（MEMORY 快照）+ D（留档报告）写入 pending.json，反思输入结构化。
- **/reflection 交互式审阅**：`command/reflection.md` 定义三池扫描（pending.json / memory_pending / manual_pending）、统一分析优先+逐条兜底、独立性/重复性三分类、容量 A/B/C/D 分层、`[src: cycle_id]` 签名门禁、双版本同步；**本轮新增 §4b**：零和预算 + 边际显著性三问——把「这条经验值不值得占常驻预算」变成必答问题。
- **治理强度升级（本轮新增）**：反思产物的**落地端**由「提示词纪律」加装了两道可执行约束——① 权限层全局 `edit: MEMORY.md = deny`（仅 build 保留 allow 作为唯一合法写入路径）；② 机检 `scripts/memory_capacity_check.py`（单段占比 / 段数零和 / 阈值推导）。**R 环的强化不在「闭环性质」而在「治理强度」**：闭环仍需人工确认，但污染与膨胀有了结构性防线。
- **留档 5 段模板**：auto-mode.md 要求报告含当时情况/制定计划/执行情况/完成情况/反思分析建议 5 段，缺段不合格，把反思固化为交付物必选项。
- **官方内核 R 环继承**：工具错误回灌、doom_loop 防震荡、revert 用户纠偏、LLM 重试退避。
- **本轮核对**：双领域门控的 FAIL 回传修正（≤2 轮）属单点执行纠偏，未接入 Reflection 自演化链路；R 环维持 4.5。

**控制论映射**：KT-ctrl-002（负反馈闭环，误差=执行与目标偏差）/ KT-ctrl-020~023（PID 三环节，P=当轮错误回灌、I=跨会话 MEMORY 累积、D=留档反思预判）/ KT-ctrl-004（误差收敛，签名门禁防污染）/ KT-ctrl-025（稳态误差，人工确认作为积分项限幅）。

**强弱项**：强——补上官方最弱的 R 环：反思启动自动触发、输入结构化、审阅有签名门禁与容量分层、**产物落地有零和预算与机检兜底**、经验回写长期记忆，形成跨会话自演化闭环；弱——闭环仍需 `/reflection` 人工确认，反馈有滞后，pending.json 滞留池存在写入断链，反思质量依赖 reflection-worker 单模型；**治理强度提升不等于闭环性质跃迁**，故分值维持。

**双层评分**：内核 2.0/5 + 装配层 Δ+2.5 → 综合 4.5/5（反转）

---

## 7. 双领域三层栈、能力扩展/体检姊妹件与判据方法论

### 7.1 双领域三层栈（架构判断 + 需求发现）

本画像最显著的纵深机制，是把两类领域判断从「提示词约定」升级为可复用、可门控的能力栈。两域同构：前三个元件即「能力三层栈」范式（Skill + Worker + 行为指令），再叠加命令入口与自动门控。

**域一·架构判断（0911 落地，五元结构）**：

| 元件 | 落点 | 作用 |
|------|------|------|
| Skill | `skills/architecture-judgment/`（内置 167 节点方法论知识图谱，离线可用） | 提供判断依据（MTH/ESS 重召回、TEC 仅作选型标尺）与工作流 |
| Worker | `architect-worker`（可见子 Agent） | 专职产出 ADR / 多维权衡矩阵 / 边界说明 / 评审结论 |
| 行为指令 | `instructions/architecture-behavior.md` | 定义架构任务触发规则、知识分层策略、openspec design 门控 |
| 命令 | `command/arch.md`（`/arch <任务描述>`） | 用户显式入口，做 18 场景路由与产出类型判定 |
| 门控 | `architecture-judgment/_private/gate_architecture.py`（`--kind adr|boundary`，schema + 图谱机检） | 产出放行的自动判据，FAIL 回传≤2 轮、不得口头通过 |

**域二·需求发现（0921 落地，同构五元）**：

| 元件 | 落点 | 作用 |
|------|------|------|
| Skill | `skills/requirement-discovery/`（可执行工作流：阶段 0 入口守卫 → 定档 K1–K5＋M1 → 发现 → 定义 → 成型 → 验证 → 交接） | 提供需求认知澄清流程与模板/checklist/routing/schemas |
| Worker | `requirement-discovery-worker`（可见子 Agent，hidden=false） | 专职产出 POV / HMW / product outcome / appetite / 最小交接契约 |
| 行为指令 | `instructions/requirement-discovery-behavior.md`（**压紧 ≤22 行**，全局注入） | 定档前置：简单档不加载/不委派/不产工件；⛔ 不产 ADR/specs/tasks/代码 |
| 命令 | `command/rd.md`（`/rd <需求描述>`） | 用户显式入口，**一律复杂档** |
| 门控 | `_private/gate_requirement_discovery.py`（`--kind stage2|handoff`，G-R1–G-R9 机检 + 11 例正负向自检 + ledger 回报通道）＋ 分层定档工具 `check_tier_conditions.py`（词表**真单源**，⛔ 不复制） | 产出放行的自动判据 |

**控制论意义**：两域栈把「架构判断」与「需求发现」从开环的人工经验，变成带目标路由（`/arch`、`/rd`）、专职执行（architect-worker、requirement-discovery-worker）、结构化契约（schema）、自动测量（gate）与纠偏回传（FAIL 回修）的完整局部闭环——装配层由此从「首个五元齐备的领域级控制回路」（v1.3 口径）演进为「**双领域同构回路**」，是 P/E 两环协同的落点（P 环编排 + E 环门控）。

### 7.2 能力扩展 / 能力体检姊妹件（装配层的「二阶能力」）

- **扩展件 `skills/opencode-capability-extension/`**：定义为 opencode 自身新增/补齐能力的标准流程——诊断孤儿/半成品能力 → 统一 skill 双根 → 引用普查防迁移断裂（grep 硬编码） → 契约先行（交付物 + 结构契约） → 落地门控与冒烟 → 单一真相源 + 派生对账安装。核心是「能力三层栈」范式：任何新能力都按 Skill + Worker + 行为指令三层装配，并按需补命令与门控。
- **体检件 `skills/opencode-capability-audit/`（本轮新增，与扩展件成姊妹件）**：**只读**能力体检/再评估 SOP——回答「现有能力有没有腐烂、有没有僵尸、有没有该退役的」；扩展件管「增」，体检件管「查与减」。二者互补，使装配层的二阶能力从「只会加」变为「**能加、能查、能减**」。

**关键跃迁**：装配层由此具备完整「二阶能力」——不仅拥有若干能力，还拥有一套「为自己系统性地新增、体检、退役能力」的元能力。可复核证据：v1.2 的 skill 双根（28 skills + 11 legacy）在 v1.3 收敛为单根；本轮进一步收敛为 **45 可加载 + 4 停用（`skills/disabled/`）**的显式分层形态，且**退役动作本身有了登记位（`skills/disabled/`）与检查件（体检 SOP）**——「减法」第一次成为可执行、可复核的动作，而非静默消失。

### 7.3 判据方法论（criterion-design-validation）

`skills/criterion-design-validation/` 是跨域通用的**判据工程方法论**：把模糊判据落成可执行物的**构造—实现—验证—维护**四阶段，含模板与负向测试要求。它回答的是 E 环的**二阶问题**：**「门控全绿是否可信？」**

- **要治的病**：假绿（判据恒真/空集通过）、假跑（脚本没真正执行）、阈值无推导（拍脑袋定线）、判据变更的连带作废。
- **装配层落点**：`memory_capacity_check.py` 的阈值推导式与 13 例 selftest、`gate_requirement_discovery.py` 的 11 例正负向自检、`subtraction_coverage_check.py` 等治理脚本，均为该方法论在本装配层的实例。

**控制论意义**：E 环的强度不再只由「有多少个门」决定，而由「门本身可不可信」决定——**判据方法论是评估环的元评估层**，也是本轮 E 环「有增有损相抵仍维持 4.0」的重要支撑（增量在质量维度而非数量维度）。

### 7.4 评分未变的原因（档位未跨）

本轮为「能力纵深 + 结构调整 + 2 项损失」的混合，而非「产品档位跃迁」，故精装度与五环分值均维持不变：

- **多Agent编排 / 工作流** 仍处 4 档内生增长：新增需求发现域 worker 与双域 gated SOP 增强了编排与工程流程，但未引入真 DAG 画布或通用可视化工作流引擎，5 档门槛（市场级/画布级）未达；**agent 数由 10 降至 9 亦不触发降档**（档位判机制形态，非计数）。
- **P 环** 已处 5.0 上限，worker 结构重排（−2 +1）与双域 SOP 反映在编排链上，但分值无可升空间。
- **E 环** 有增（+需求发现门控 / +判据方法论 / +生产者自跑门控）也有损（−视觉代看 L1），**相抵后维持 4.0**。
- **T 环** 有增（+2 治理插件 / +MEMORY 权限硬门禁）也有损（−2 MCP，L2），**相抵后维持 5.0**（已处上限）。
- **M 环** 有增（生命周期治理 + 机检），但容量阈值部分仍属自愿纪律、写入仍需人工确认，**置信度提升未跨档，维持 4.0**。
- **R 环** 强化的是**治理强度**而非**闭环性质**（仍需 `/reflection` 人工确认），维持 4.5。
- **封顶因素未变**：一键部署仍为个人 config 无分发（3 档）、沙箱仍非 VM 隔离（3 档）。

结论：官方 2.9、自改造 3.9 维持；本轮仅刷新 evidence 与机制叙述并登记损失，评分单一数据源 `09-src-data/opencode_custom_scores.py` 未改动。

## 8. 未入库轮次的补账（0911 → 1011）

### 8.1 为什么有这段缺口

`archive/Mission-file/2026-09/0914-自改造opencode再评估v1.4/report.md` 那次**全量复评明确「不更新知识库」**（按用户口径），故本库缺 **2026-09-11 → 2026-10-11 的整段记录**。本轮（v1.4）一次性补入，**留痕在此节**，不再散落。

### 8.2 该轮实机口径与时间线（补账）

**0914 复评时点的实机口径**：**11 agents / 43 可加载 skill / 4 停用 / 3 commands / 6 instructions 注册 / 6 MCP / 4 providers / 16 models / 32 variants / 9 scripts**。

| 日期 | 事件 | 对本画像的影响 |
|------|------|---------------|
| 0913 | **前端领域三层栈**落地（`frontend-design` skill + frontend-worker + frontend-behavior.md + `/frontend` + `gate_frontend.py`） | P/E 环短暂出现第三域 |
| **0915** | **绘图链路重构**：drawio 退役 + **vision-worker 废除** + `subagent_depth 2→1` + 新建 `skills/diagram-lite`（8/8 验收判据 PASS，重启后活体冒烟 5/5） | **损失 L1 + L2 同时发生**；T/P 环工具面与 worker 编队重排 |
| **0916** | **前端三层栈退役**（agent/skill/command/instructions 侧下线，`lib/frontend-capability/` 25 文件资产仍在）；同时打通**生产者-验证者**（worker 获准自跑门控脚本，D-01） | 前端域退出；E 环门控链路缩短一轮往返 |
| **0921** | **需求发现三层栈**落地（requirement-discovery skill + requirement-discovery-worker + requirement-discovery-behavior.md + `/rd` + 分层定档工具 `check_tier_conditions.py`） | **新增第二领域**；SP/P/E 三环同步扩展 |
| **0926** | **通知弹窗**：`notify-on-pause` 插件落地 | 新增「插件钩子层」机制（可观测面） |
| **0927** | **provider 拆分**：`commandcode` 拆为付费/免费双 provider、独立 key（一 key 一变量名） | provider 3→6；T 环基建面扩展 |
| **1010** | **MEMORY 生命周期治理**：三轮 `/reflection` 深迁移 −46%（24318 → 13137 B，15 段零和） | M/R 环治理强度升级 |

> 另：0914 复评本身产出的 44 项工单（`evidence/remediation-verify.json`）、治理脚本扩容（3 → **14 个 .py + 1 json + 3 .ps1**）亦属该缺口期内容，本轮一并登记。

### 8.3 两项能力损失登记（L1 / L2）

**必须登记，不得只报增长。**

| 编号 | 损失 | 发生时点 | 具体后果 | 补偿路径（不等价，仅记现状） |
|------|------|---------|---------|--------------------------|
| **L1** | **视觉代看机制退役** | 0915（vision-worker 废除，连带 `subagent_depth 2→1`、pdf/frontend worker 的 `task→vision-worker` 块删除） | **E 环少一条「图像是否达标」的降级传感器路径**：原「父会话无视觉 → 委派 vision-worker 代看 → 失败降级 PNG 结构校验」三段降级链消失，改为「模型原生视觉直接 Read；模型无视觉 → **由人终判**」 | 会话模型原生多模态（deepseek-flash V4.1）+ 人终判；**在无视觉会话下，图像达标判定退化为人工，自动化程度净下降** |
| **L2** | **MCP 工具面收窄** | 0915（drawio / drawio-local 两个 MCP 退役） | 配置 **server 数 6→4、启用数 2→1**（仅 pdf-reader）；原「drawio-worker → MCP 导出 → 视觉核对」制图链整体拆除 | 制图改走 `diagram-lite` skill 档位出图（T0 文本退化 / T1 模板填空 / T2 DSL→SVG 默认 / T3 发布级）；**不委派制图子 Agent、不装绘图 MCP**——出图能力保留但**能力形态由「MCP 生态 + 专职 worker」降为「skill 档位 + 主 Agent 亲自执行」** |

**口径克制声明**：两项损失**均为主动取舍**（成本换能力、复杂度换可维护性，且 0915 重构验收 8/8 PASS + 活体冒烟 5/5），**但「主动」不等于「无代价」**：L1 使无视觉场景的自动化闭环出现人工断点，L2 使平台侧可插拔绘图生态位空缺。故本画像**既不为增长叙事掩盖损失，也不因损失而下调分值**——MCP 一维的判据是「平台多传输能力未变，server 数与启用数属用户配置选择」（维持 4），E 环则按「有增有损相抵」维持 4.0。

## 七大核心环强弱总评

| 环 | 承担角色 | 强度 | 主控概念 |
|---|---------|:---:|---------|
| **设定值** | GATE + COMPLEXITY + grill-me/question + `/arch` 与 `/rd` 双路由 + 双行为指令 | 强 | KT-ctrl-045 规划-执行解耦 |
| **E 评估** | search-behavior + search-worker + 双域门控（architecture / requirement-discovery）+ 判据方法论 + 用户确认 | 强（由最弱反转；**有增有损相抵，维持 4.0**） | KT-ctrl-035 扰动观测器 |
| **T 执行** | 4 MCP（1 启用）+ 权限白名单 + MEMORY 权限硬门禁 + 2 治理插件 | 最强（**工具面收窄 L2，与插件/门禁新增相抵**） | KT-ctrl-034 限幅/看门狗 |
| **M 记忆** | MEMORY.md 跨会话 + pending.json + compaction 调优 + 零和预算与机检 | 强（**治理强化未跨档**） | KT-ctrl-011 卡尔曼式滤波 |
| **P 规划** | plan/build 双速 + 5 专职 worker + 双领域三层栈 + 契约接力 | 最强（**worker 结构重排，分值已处上限**） | KT-ctrl-044/045 MPC + 解耦 |
| **R 反思** | Reflection 自演化系统 + 生命周期治理 + 留档 5 段 + 经验回写 | 强（由弱反转；**治理强度升、闭环性质未变**） | KT-ctrl-002 负反馈闭环 |

## opencode-custom 控制论画像总结

**整体范式：在官方前馈主导内核上做弱环定向补强，把「开环为主 + 局部闭环」改造为「分层编排 + 跨会话自演化闭环 + 双领域可门控判断」的控制器，并进一步获得「为自己新增、体检、退役能力」的二阶能力。**

- **最突出的环：P 环（分层编排）与 T 环（执行器安全）**——官方本就最强的两环被继续加固：P 环从双速升级为「plan/build + 5 专职 worker + 双领域三层栈」编排平台，T 环从内核护栏扩展到「4 MCP + 细粒度权限白名单 + MEMORY 权限硬门禁 + 2 个治理插件」。
- **关键反转：E 环与 R 环（仍成立，但本轮有增有损）**——官方两大最弱环被装配层补齐：E 环以 search-behavior 信源分级 + search-worker 证据包 + 结构化用户确认，并扩为**双领域自动门控**（gate_architecture.py + gate_requirement_discovery.py）实现反转，同时以判据方法论约束门本身的可信度；R 环以 Reflection 自演化系统（pending.json 状态机 + reflection-worker + /reflection 签名门禁）从半开环升级为跨会话闭环，本轮再加零和预算与机检治理。
- **双领域三层栈落地**：架构判断（0911）与需求发现（0921）两域同构，均由「skill + worker + 行为指令 + 命令 + 门控」五元构成——装配层由「首个五元齐备的领域级闭环」演进为「**双领域同构回路**」。
- **能力可自我扩展 + 可自我体检**：opencode-capability-extension（增）与 opencode-capability-audit（查/减）成姊妹件，配合 criterion-design-validation 判据方法论，装配层的二阶能力从「只会加」变为「**能加、能查、能减、且判据可信**」。
- **两项能力损失已登记（L1/L2）**：vision-worker 代看机制退役使 E 环少一条图像达标的降级传感器路径；drawio/drawio-local MCP 退役使工具面 6→4（启用 2→1）、制图能力由 MCP 生态降为 skill 档位。**主动取舍仍有代价，登记不抵消。**
- **精装度维持 3.9（2.9 → 3.9，Δ+1.0）**——8 维中 6 维较官方提升（记忆满分 5），本轮净变化为「能力纵深 + 结构调整 + 2 项损失」的混合、无任一维度跨 5 档阈值，故**维持 3.9、不虚报跃升**；一键部署与完整沙箱仍受个人装配限制未提升，是封顶主因。
- **从单体到分层编排 + 自扩展/自体检平台**：官方是单体双速控制器，自改造后形成「主 Agent 编排 + 专职 worker 执行 + 双领域门控 + Reflection 自演化 + 能力扩展/体检 SOP」的分工平台。

**一句话画像**：opencode-custom 是**「以内核为底座、以 9 agent / 45 可加载 skill（单根统一，另有 4 件显式停用）/ 4 MCP / 2 插件装配，在装配层定向补强 E/R 弱环、落地架构判断与需求发现双领域三层栈、以判据方法论约束门控可信度、并借能力扩展/体检姊妹 SOP 获得二阶自我扩展能力，同时诚实登记视觉代看与绘图 MCP 两项损失，把前馈主导控制器升级为跨会话自演化闭环编排平台」的个人变体**——它没有重造引擎，而是用协议、专职 worker、领域门控与记忆系统把官方最弱的两环反转为强环，代价是闭环仍需人工确认、一键分发与完整沙箱缺席，以及 L1/L2 两项能力形态降级。

---

### 📚 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S4 | 一手配置观察 | `07-checkpoint/opencode-custom-snapshot/opencode.jsonc`（agent/provider/mcp/permission/compaction 原文；`subagent_depth=1`、全局 `edit: MEMORY.md=deny`、build 级 allow、`pdf-reader_*` 全局 deny / agent 级 allow） | 高 |
| SRC-002 | S4 | 一手协议观察 | `07-checkpoint/opencode-custom-snapshot/instructions__auto-mode.md`（GATE/COMPLEXITY/variant/子Agent规则/委派/Reflection自检/压缩模板；原 agent-protocol.md 已并入） | 高 |
| SRC-003 | S4 | 一手协议观察 | `07-checkpoint/opencode-custom-snapshot/instructions__architecture-behavior.md`（架构触发规则/知识分层/openspec design 门控） | 高 |
| SRC-004 | S4 | 一手协议观察（新） | `07-checkpoint/opencode-custom-snapshot/instructions__requirement-discovery-behavior.md`（0921 需求发现行为层；≤22 行压紧；定档前置 K1–K5＋M1；简单档不加载/不委派/不产工件） | 高 |
| SRC-005 | S4 | 一手协议观察 | `07-checkpoint/opencode-custom-snapshot/instructions__search-behavior.md`（外部信息实证/时效准则/信源分级） | 高 |
| SRC-006 | S4 | 一手命令观察 | `07-checkpoint/opencode-custom-snapshot/command__reflection.md`（三池扫描/签名门禁/容量分层/双版本同步；**§4b 零和预算 + 边际显著性三问**） | 高 |
| SRC-007 | S4 | 一手命令观察 | `07-checkpoint/opencode-custom-snapshot/command__arch.md`（/arch 场景路由 / architect-worker 委派 / gate_architecture.py 门控流程） | 高 |
| SRC-008 | S4 | 一手命令观察（新） | `07-checkpoint/opencode-custom-snapshot/command__rd.md`（/rd 需求发现入口，一律复杂档） | 高 |
| SRC-009 | S4 | 一手盘点（新快照） | `07-checkpoint/opencode-custom-snapshot/inventory.json`（`collected_at=2026-10-11T17:04:12+08:00`；**9 agents / 4 MCP（1 enabled）/ 45 skills + `_shared` + `disabled` 4 件 / 6 instructions / 3 commands / 2 plugins / 6 providers / 14 .py + 1 json + 3 .ps1 脚本**）；旧版归档 `inventory-v1.3.json` | 高 |
| SRC-010 | S4 | 一手快照清单 | `07-checkpoint/opencode-custom-snapshot/manifest.json`（13 文件 sha256_16 + 字节数；MEMORY.md **13137 B**；`collected_at` 同上） | 高 |
| SRC-011 | S4 | 一手插件观察（新） | `07-checkpoint/opencode-custom-snapshot/plugins__system-date-transform.ts`（prefix-cache 日期治理：剥离 system `Today's date:` + 末条 user 消息回注；日志 `~/.cache/opencode/plugin-system-date.log` 17277 行） | 高 |
| SRC-012 | S4 | 一手插件观察（新） | `07-checkpoint/opencode-custom-snapshot/plugins__notify-on-pause.ts`（会话暂停桌面通知；配置单源 `~/.config/opencode/notify.json` enabled=true；日志 `notify-plugin.log` 7045669 行 + `notify-receipts.log`） | 高 |
| SRC-013 | S4 | 一手机检脚本（新） | `~/.config/opencode/scripts/memory_capacity_check.py`（单段占比 >50% / `--baseline` 段数零和 / 阈值推导式；selftest **8 → 13 例**） | 高 |
| SRC-014 | S4 | 一手治理脚本集（新） | `~/.config/opencode/scripts/`（**14 .py + 1 json + 3 .ps1**：pending_io（独占锁原子写）/ memory_capacity_check / subtraction_coverage_check / prompt_audit / drift_reconcile / dual_root_check / gate_host_check / capabilities_reconcile / asset_inventory / evidence_freshness / memory_write_path_audit 等） | 高 |
| SRC-015 | S4 | 一手能力包观察 | `skills/architecture-judgment/`（SKILL.md + 内置 167 节点方法论图谱 + schemas + `_private/gate_architecture.py`） | 高 |
| SRC-016 | S4 | 一手能力包观察（新） | `skills/requirement-discovery/`（0921 三层栈：workflow/checklist/routing/templates/schemas + `_private/gate_requirement_discovery.py` + `_private/CRITERIA.md`；词表真单源 `check_tier_conditions.py`） | 高 |
| SRC-017 | S4 | 一手能力包观察 | `skills/opencode-capability-extension/`（能力扩展 SOP：三层栈/统一双根/引用普查/契约+门控+冒烟） | 高 |
| SRC-018 | S4 | 一手能力包观察（新） | `skills/opencode-capability-audit/`（只读能力体检/再评估 SOP，与扩展件成**姊妹件**） | 高 |
| SRC-019 | S4 | 一手能力包观察（新） | `skills/criterion-design-validation/`（判据构造—实现—验证—维护四阶段方法论；治假绿/假跑/恒真判据/空集/阈值无推导） | 高 |
| SRC-020 | S4 | 一手留档（0914 缺口轮） | `Mission-file/2026-09/0914-自改造opencode再评估v1.4/report.md`（**明确「不更新知识库」**，故 KB 缺 0911→1011；该轮口径 11 agents / 43 可加载 skill / 4 停用 / 3 commands / 6 instructions / 6 MCP / 4 providers / 16 models / 32 variants / 9 scripts）+ `evidence/inventory-v1.4.json`、`evidence/remediation-verify.json`（44 工单） | 高 |
| SRC-021 | S4 | 一手留档（L1/L2 发生轮） | `Mission-file/2026-09/0915-绘图链路重构执行/报告.md` + `REWRITE-CONTRACT.md`（drawio 退役 + vision-worker 废除 + `subagent_depth 2→1` + `diagram-lite` 新建；8/8 判据 PASS、活体冒烟 5/5、负向冒烟 `Agent vision-worker not found`）；规划侧 `Mission-file/2026-09/0915-绘图链路重构与drawio退役/PLAN.md` | 高 |
| SRC-022 | S4 | 一手留档（前端栈 0913 建 / 0916 退役） | `Mission-file/2026-09/0913-前端能力建设[ABANDONED]/report.md`（frontend-worker + frontend-behavior.md 38 行 + /frontend + gate_frontend.py）；`Mission-file/2026-09/0916-前端技术栈基线/ABANDONED-REGISTER.md`（退役登记） | 高 |
| SRC-023 | S4 | 一手留档（需求发现 0921） | `Mission-file/2026-09/0916-产品设计方法论/20-agent-skill/`（SKILL.md + `_config/command/rd.md` + `_config/instructions/requirement-discovery-behavior.md` + `_private/gate_requirement_discovery.py` + schemas）；分层定档工具 `…/0916-产品设计方法论/tools/check_tier_conditions.py` | 高 |
| SRC-024 | S4 | 一手留档（通知插件 0926） | `Mission-file/2026-09/0926-通知弹窗需求发现/report.md` + `adr/ADR-001-notify-mechanism.json`（notify-on-pause 机制裁决） | 高 |
| SRC-025 | S4 | 一手留档（provider 拆分 0927） | `Mission-file/2026-09/0927-cmdcode免费模型双harness接入/report.md`（commandcode 拆为付费 9 + 免费 4；`COMMANDCODE_API_KEY` / `COMMANDCODE_FREE_API_KEY` 一 key 一变量名） | 高 |
| SRC-026 | S4 | 一手留档（MEMORY 生命周期 1010） | `Mission-file/2026-10/1010-reflection-review/report.md` + `report-round2.md` + `report-round3-lifecycle.md` + `evidence/ledger-1010*.md`（三轮深迁移 −46%、零和、机检落地） | 高 |
| SRC-027 | S4 | 一手留档（生产者-验证者 D-01） | `07-checkpoint/opencode-custom-snapshot/opencode.jsonc` 内嵌注释（0916 D-01：只放行门控脚本本身 `python3 *gate_architecture.py*` / `python3 *gate_requirement_discovery.py*`） | 高 |
| SRC-028 | S1 | 可复算评分 | `09-src-data/opencode_custom_scores.py`（官方 2.9 / 自改造 3.9，8 维与六环分值单一数据源；**本轮 v1.4 口径已在文件头登记漂移与 L1/L2，分值未改动**） | 高 |
| SRC-029 | S1 | 评分模型 | `07-checkpoint/premium-scoring-model.md`（精装度 v2.0：硬门槛 + 8 维加权 + 一票否决） | 高 |
| SRC-030 | S4 | 对照基线 | `03-cases/opencode.md`（官方 opencode 内核五环结构与结论口径；本机运行时 **1.18.35**，上游 v1.19.0 只登记不追） | 高 |
| SRC-031 | S1 | 框架契约 | `02-framework/framework.md`、`00-contract/contract.md`（五环定义与信源分级规范） | 高 |
| SRC-032 | S4 | 对照参考（同轮姊妹件） | `03-cases/dsh-custom-diff.md`（另一宿主的装配层对照写法，**只读参考**，不参与本专题分值） | 高 |
