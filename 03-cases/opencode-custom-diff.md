# opencode-custom 改造差异（官方基线 vs 自改造）— 五环与精装度对照

> 一句话定位：本文件以官方 opencode「四 agent + 官方内置 skills + 基础 provider」为基线，逐类拆解自改造装配层的 **12 类**改动及其对 SP/M/P/R/T/E 六环的双层增量，量化精装度从 2.9 到 3.9 的跃升来源，并**显式登记两项能力损失**。
>
> 版本：**v1.4（2026-10-11）**。相对 v1.3：① 基线内核版本由 1.18.30 升为 **1.18.35**（本机运行时；上游 v1.19.0 只登记不追）；② 改造清单由 **10 类扩为 12 类**（新增 #11 需求发现三层栈、#12 判据方法论与治理脚本+插件层；已退役项标注「已退役（损失登记）」）；③ 新增 **§5b 两项能力损失登记（L1/L2）**；④ 核心发现由四条扩为六条（+「数量下降 ≠ 能力下降」的诚实登记、+「未入库轮次的补账义务」）；⑤ **五环与精装度分值维持不变**（净变化属「能力纵深 + 结构调整 + 2 项损失」的混合、未跨任何 5 档产品阈值），仅刷新 evidence 与机制叙述。评分口径与 `03-cases/opencode-custom.md`（v1.4 权威画像）一致，分值唯一来源 `09-src-data/opencode_custom_scores.py`。

## 1. 基线定义

**基线 = 官方 opencode 默认 + 最小常规装配**（官方内核版本 **v1.18.35**，2026-10-06 发布，为本机可实证的运行时 `~/.opencode/bin/opencode --version`；相对 v1.3 的 1.18.30 有 5 个 patch 增量、结构未变），仅含：

- **官方四 agent**：`plan`（慢规划，禁 edit）、`build`（快执行）、`general`（通用多步）、`explore`（快速代码探索）——不含任何自定义专职 worker。
- **官方内置 skills**：opencode 自带工具集与内置能力，无个人 skill 库、无 legacy skill。
- **基础 provider**：官方默认模型接入，多 provider 但需用户自填 key/配置，无个人 provider 预设（opencode-go / deepseek / zhipu / commandcode 等）。
- **官方内核执行/记忆机制**：shell 看门狗、输出截断、权限 ask/deny/always、AI-SDK 工具修复、SQLite session、compaction 分层压缩、context-epoch 增量基线。
- **明确不含**：自定义 skills / MCP / instructions 协议层 / Reflection 自演化系统 / 专职 worker / 个人 permission 白名单 / compaction 与 variant 调优 / 插件钩子层。基线口径与 `03-cases/opencode.md` 的官方内核画像一致。

> **上游 v1.19.0 只登记不追**：v1.19.0 于 2026-10-11 发布，release note 明写 `Run opencode upgrade --major to upgrade to OpenCode 2`——性质是**主版本跃迁入口**而非 1.x 功能增量，且本机**未安装**、无本地源码/行为证据。故本轮基线取 **1.18.35**，v1.19.0 仅在 `03-cases/opencode.md` 登记，待 OpenCode 2 落地并取得本地证据后单独立项。**基线取「本机可实证的运行时」而非「上游最新 tag」，是本轮的口径选择。**

## 2. 改造清单（12 类）

| # | 类别 | 改造内容 | 证据 | 五环权重 | 对环影响 |
|---|------|---------|------|---------|---------|
| 1 | **Agent 扩展（结构调整：10→9）** | 装配层 agent 10→**9**：**−drawio-worker −vision-worker（已退役·损失登记 L1/L2）**，**+requirement-discovery-worker**；现存 5 专职 worker = pdf / architect / reflection / search / requirement-discovery（均 subagent；architect 与 requirement-discovery 为 visible，其余 hidden）；`subagent_depth 2→1`（0915，随视觉代看链废除） | `opencode.jsonc` `agent.*`；`inventory.json` `agents`（**9 项**） | P 主 + T | P：worker 编队由「制图+视觉」换为「需求发现」，双域编排成形；T：工具能力按 worker 隔离授权，且**无任何子 Agent 持有 task 权限** |
| 2 | **协议层（注册 5→6）** | auto-mode.md（GATE/COMPLEXITY/variant/reflection 硬门禁/委派协议/编码安全/留档；原 agent-protocol.md 已并入且**落盘但有意不注册**）、search-behavior.md、architecture-behavior.md、**requirement-discovery-behavior.md（新增，压紧 ≤22 行，定档前置 K1–K5＋M1，简单档不加载/不委派/不产工件）**、browser-management.md；`downloads.md` **退役** | `instructions__*.md`；`opencode.jsonc` `instructions` 列表（**6 项**，含 MEMORY.md 注入位） | P/E/R/SP 跨环 | SP：需求发现触发规则入设定值入口；P：目标物化+推理档分层+双域任务路由；E：信源分级+用户确认；R：反思启动即触发 |
| 3 | **Skill 库（41→45 可加载）** | 单根 `skills/` 下 **45 个可加载 SKILL.md**（顶层 46 目录 + `skills/disabled/` **4 件停用**：amap-budget-control / amap-jsapi-skill / amap-lbs-skill / model-switcher；另含 `_shared`）；本轮新增 criterion-design-validation / design-material-library / diagram-lite / opencode-capability-audit / requirement-discovery / version-upgrade-cascade；**退役项第一次有了显式登记位（`disabled/`）而非静默消失** | `inventory.json` `skills`（46 目录）/ `skills_disabled`（4）；`opencode.jsonc` `skills` 单根 | T + E | T：能力密度提升且**「减法」可复核**；E：判据方法论 skill 提供评估范式 |
| 4 | **MCP 集成（6→4，收窄·损失 L2）** | **4 个 MCP**：vscode-mcp-server / amap / pdf-reader / headroom（多传输），**仅 pdf-reader 启用**（agent 级 `pdf-reader_*: allow`，全局 deny 兜底）；**drawio / drawio-local 已退役（0915）**——制图改走 `diagram-lite` skill 档位；保留 `vscode-mcp-server_*: deny` 作 re-enable 前置防御 | `opencode.jsonc` `mcp`；`inventory.json` `mcp`（**4 项**）/ `config.mcp_enabled`（**1 项**） | T | T：工具面收窄（server 6→4、enabled 2→1）；**判据：平台多传输能力未变、server 数与启用数属用户配置选择 → MCP 维维持 4** |
| 5 | **Reflection 自演化系统 + 生命周期治理** | MEMORY.md 跨会话记忆 + pending.json 结构化状态机 + reflection-worker + `/reflection` 命令（三池扫描/签名门禁/容量分层）；**2026-10-10 新增 §4b：零和预算 + 边际显著性三问**，三轮深迁移 **−46%**（24318 → **13137 B / 15 段**，字符 −41%，tokens 9753 → 5264，段数零和） | `command__reflection.md`（含 §4b）；`instructions__auto-mode.md` Reflection 自检与 4 层输入；`inventory.json` `command`（3）/ `manifest.json`（MEMORY.md 13137 B） | R（核心）+ M | R：半开环→跨会话闭环自演化（核心反转）+**治理强度升级**；M：补齐长期记忆并**由「只增不减」改为「有预算的常驻资产」** |
| 6 | **Provider 扩展（3→6）** | **6 个 provider 预设**：opencode-go（Go 套餐）/ opencode-go-tmp / deepseek（官方直连）/ zhipu（GLM）/ **commandcode（0927 拆分：旧 key，9 付费模型）** / **commandcode-free（0927 拆分：新 key，4 免费模型）**——拆分为「**一 key 一变量名 ＋ 一账户一 provider**」范式；含多模型与 Daily/Deep variant | `opencode.jsonc` `provider.*`；`inventory.json` `providers`（6）/ `config.provider_apikey_env_names`（5 个 env 名，⛔ 不打印值） | T（基建） | T：模型接入面扩大；**同源拆 key 防止「装载新 key 静默改变既有 provider 账户归属」** |
| 7 | **Compaction / variant 调优** | compaction：`tail_turns=4`、`preserve_recent_tokens=16384`、`reserved=10000`、auto/prune；Daily/Deep variant 分档（max_tokens 8192/16384，reasoning_effort high/max） | `opencode.jsonc` `compaction` 与各模型 `variants`；`instructions__auto-mode.md` 决策边界 | M（基建） | M：状态估计更新预算精细可控；P：推理档随复杂度动态分配 |
| 8 | **Permission 规则（+MEMORY 硬门禁）** | external_directory 白名单（默认 allow，`~/.ssh\|~/.aws\|~/.gnupg` deny）+ read auth.json 与 opencode.env deny + bash 危险命令 deny/ask（含 `opencode debug config*` ask，防明文 apiKey 批量泄露）+ edit 分层授权（仅 build 与写入型子 Agent）；**新增全局 `edit: MEMORY.md = deny`**（agent 级末条胜出，build 保留 allow 为 `/reflection` 唯一合法写入路径） | `opencode.jsonc` `permission` 及各 agent `permission` | T（安全） | T：执行器最小授权与越权收口，**记忆写入有权限层硬门禁**，仍非完整沙箱 |
| 9 | **架构判断三层栈（0911）** | 以「skill（architecture-judgment，内置 167 节点离线方法论 KG）+ worker（architect-worker）+ 行为指令（architecture-behavior.md）+ 命令（/arch）+ 门控（gate_architecture.py --kind adr\|boundary）」五元构成领域级控制回路；门控 FAIL 原样回传修正≤2 轮、不得降级为口头通过 | `skills/architecture-judgment/`（含 `_private/gate_architecture.py`）；`command__arch.md`；`instructions__architecture-behavior.md` | P + E（+T） | P：架构域编排固化为受门控 SOP；E：领域级自动评估门（schema + 图谱机检）；T：产出方 bash 收口 |
| 10 | **能力扩展 SOP（二阶能力）** | 以 opencode-capability-extension skill 定义「为 opencode 自身新增/补齐能力」的标准流程——诊断孤儿能力 → 统一 skill 双根 → 引用普查防迁移断裂（grep 硬编码）→ 契约先行（交付物 + 结构契约）→ 落地门控与冒烟 → 单一真相源 + 派生对账安装；任何新能力按 Skill + Worker + 行为指令三层栈装配 | `skills/opencode-capability-extension/` | M + P 跨环 | M：单一真相源 + 派生对账保状态一致；P：引用普查为能力迁移提供前置约束；装配层由此获得「为自己系统性新增能力」的二阶元能力 |
| 11 | **需求发现三层栈（0921，新机制 C）** | 与架构栈**同构的第二领域五元**：「skill（requirement-discovery：阶段 0 入口守卫 → 定档 K1–K5＋M1 → 发现 → 定义 → 成型 → 验证 → 交接）+ worker（requirement-discovery-worker，visible）+ 行为指令（requirement-discovery-behavior.md，**≤22 行压紧，定档前置，简单档不加载/不委派/不产工件**）+ 命令（/rd，**一律复杂档**）+ 门控（gate_requirement_discovery.py --kind stage2\|handoff，G-R1–G-R9 + 11 例正负向自检 + ledger 回报通道）+ 分层定档工具 check_tier_conditions.py（词表**真单源**）」；产出＝需求认知（POV/HMW/outcome/appetite/最小交接契约），⛔ 不产 ADR/specs/tasks/代码 | `skills/requirement-discovery/`；`command__rd.md`；`instructions__requirement-discovery-behavior.md`；`…/0916-产品设计方法论/tools/check_tier_conditions.py` | SP + P + E | SP：需求意图有显式路由与定档前置；P：需求域编排固化为受门控 SOP；E：第二个领域级自动门控 + 词表真单源 |
| 12 | **判据方法论 + 治理脚本/插件层（新机制 D）** | ① **criterion-design-validation**：判据「构造—实现—验证—维护」四阶段方法论，治**假绿/假跑/恒真判据/空集/阈值无推导**——E 环的元评估层；② **治理脚本 14 .py + 1 json + 3 .ps1**（pending_io 独占锁原子写 / memory_capacity_check（selftest 8→13 例）/ subtraction_coverage_check / prompt_audit / drift_reconcile / dual_root_check / gate_host_check / capabilities_reconcile / asset_inventory / evidence_freshness / memory_write_path_audit 等）；③ **2 个治理插件（插件钩子层）**：system-date-transform.ts（prefix-cache 日期治理：剥离 system `Today's date:` + 末条 user 消息回注；日志 17277 行）、notify-on-pause.ts（会话暂停桌面通知，notify.json enabled=true；日志 7045669 行） | `skills/criterion-design-validation/`；`~/.config/opencode/scripts/`；`plugins__system-date-transform.ts`、`plugins__notify-on-pause.ts`；`inventory.json` `scripts`/`plugins` | E + T（+M） | E：门控本身的可信度被方法论约束（元评估层）；T：插件钩子层补上**成本面**（prefix-cache）与**可观测面**（暂停通知）两个治理面——**8 维模型无对应维度，不参与打分，仅在画像登记**；M：容量机检使治理原则可执行 |
| — | **（已退役·损失登记）前端领域三层栈** | 0913 落地（frontend-design skill + frontend-worker + frontend-behavior.md 38 行 + `/frontend` + gate_frontend.py）→ **0916 前后退役**（agent/skill/command/instructions 侧下线；`lib/frontend-capability/` 25 文件资产仍在） | `0913-前端能力建设[ABANDONED]/report.md`；`0916-前端技术栈基线/ABANDONED-REGISTER.md` | — | **已退役**；前端能力改由 `frontend-design-methodology` / `design-material-library` 等 skill 承接 |
| — | **（已退役·损失 L1）vision 代看机制** | vision-worker 于 **0915 废除**（连带 `subagent_depth 2→1`、pdf/frontend worker 的 `task→vision-worker` 块删除） | `0915-绘图链路重构执行/报告.md` + `REWRITE-CONTRACT.md`；负向冒烟 `Agent vision-worker not found` | — | **已退役（损失登记 L1）**：E 环少一条「图像是否达标」的降级传感器路径 |
| — | **（已退役·损失 L2）drawio MCP 链** | drawio / drawio-local 两个 MCP 于 **0915 退役**，连同 `drawio-worker` 与 `skills/drawio-reference/` 整包 | 同上；`inventory.json` `mcp`（4 项） | — | **已退役（损失登记 L2）**：制图改走 `diagram-lite` skill 档位，工具面 6→4（启用 2→1） |

## 3. 五环双层 delta

| 环 | 官方内核 | 装配层增量 | 自改造综合 | 标注 | 关键改造 |
|----|:---:|:---:|:---:|:---:|------|
| **M 记忆** | 3.5 | +0.5 | 4.0 | 增强 | MEMORY.md 跨会话 + pending.json 状态机 + compaction 调优；**2026-10-10 生命周期治理：零和预算 + 边际显著性三问 + 机检 memory_capacity_check.py（单段占比 / 段数零和 / 阈值推导式），−46% 至 13137 B / 15 段** |
| **P 规划** | 4.5 | +0.5 | 5.0 | 增强 | **+5 专职 worker（新增 requirement-discovery-worker；drawio/vision 退役）** + GATE/COMPLEXITY 推理档 + 契约接力 + **双领域三层栈 gated SOP（架构 / 需求发现）**；worker 获准自跑自己的门控脚本（0916 D-01）——**已处 5.0 上限，结构重排不改变分值** |
| **R 反思** | 2.0 | +2.5 | 4.5 | **反转** | Reflection 自演化系统 + **生命周期治理（零和预算 / 边际显著性三问 / 机检）** + 全局 `edit: MEMORY.md=deny` 权限硬门禁；**强化的是治理强度而非闭环性质**（仍需 /reflection 人工确认）→ 维持 4.5 |
| **T 执行** | 4.5 | +0.5 | 5.0 | 增强 | **MCP 收窄至 4（1 启用；drawio/drawio-local 退役 → diagram-lite skill 档位，损失 L2）** + 权限白名单 + **MEMORY 权限硬门禁** + 专职 worker 工具隔离 + **2 个治理插件（prefix-cache 日期治理 / 暂停通知）**——**收窄与新增相抵，维持 5.0** |
| **E 评估** | 2.0 | +2.0 | 4.0 | **反转** | search-behavior 信源分级 + search-worker 证据包 + **双域领域级自动门控（gate_architecture.py + gate_requirement_discovery.py）** + **criterion-design-validation 判据方法论** + grill-me/question 用户传感器；**损失 L1：vision-worker 代看机制退役，少一条图像达标降级传感器**——**有增有损相抵，维持 4.0** |

> 补充：设定值（SP）环官方内核约 3.5，装配层以 GATE + COMPLEXITY + grill-me/question + **`/arch` 架构路由 + `/rd` 需求发现路由 + 双行为指令触发约束**补强至约 4.5（增强），不计入五环但为五环提供目标参考序列。

## 4. 精装度 8 维对比

> 数值唯一来源：`09-src-data/opencode_custom_scores.py`（`SCORES` / `WEIGHTS`，**本轮未改动**；v1.4 口径漂移与 L1/L2 已在文件头登记）。官方加权 2.88 → 2.9，自改造加权 3.85 → 3.9，均过端到端硬门槛，无一票否决。

| 维度 | 权重 | 官方 | 自改造 | Δ | 依据（本轮刷新） |
|------|:---:|:---:|:---:|:---:|------|
| 多Agent编排 | 16 | 3 | 4 | +1 | 官方 plan/build/task 委派原语需用户编排；自改造 **9 agent**（+5 专职 worker：pdf/architect/reflection/search/requirement-discovery）+ 委派协议 + 并行；**drawio-worker 与 vision-worker 已退役、新增 requirement-discovery-worker——agent 数 10→9 不构成降档**（档位判「有无并行/委派编排」而非 worker 个数）；`subagent_depth=1`（无真 DAG 画布，未跨 5 档） |
| Skill库 | 12 | 2 | 4 | +2 | 官方仅内置工具集无预装 skill 库；自改造 **45 个可加载 SKILL.md**（顶层 46 目录 + `skills/disabled/` 4 件停用 + `_shared`）单根统一，本轮新增 6 个（criterion-design-validation / design-material-library / diagram-lite / opencode-capability-audit / requirement-discovery / version-upgrade-cascade）；仍为精选个人库、无市场/分发（未跨 5 档） |
| 工作流 | 13 | 3 | 4 | +1 | 官方 plan 模式 + 编排原语需用户搭建；自改造 GATE/COMPLEXITY 门控 + 契约驱动 + 委派接力 + **双领域三层栈 gated SOP**（架构：/arch + architecture-behavior + architecture-judgment + gate_architecture.py；需求发现：/rd + requirement-discovery-behavior + requirement-discovery + 分层定档工具）；无通用可视化工作流/DAG 引擎（未跨 5 档） |
| 模型接入 | 14 | 3 | 4 | +1 | 官方多 provider 需填 key/配置；自改造 **6 provider**（opencode-go / opencode-go-tmp / deepseek / zhipu / commandcode / commandcode-free，0927 按「一 key 一变量名」拆分）+ deepseek-flash V4.1 原生多模态 + @ai-sdk/openai-compatible 图片链路（仍非数百模型开箱，未跨 5 档） |
| 一键部署 | 15 | 3 | 3 | 0 | 官方 npm 安装 + 自填 provider key；自改造个人 config 需手动复制装配层，无一键分发（封顶未变） |
| 沙箱 | 10 | 3 | 3 | 0 | 官方 permission ask/deny + snapshot 回滚；自改造 + external_directory 白名单 + /tmp/opencode 隔离区，仍非完整沙箱/VM 隔离（封顶未变） |
| MCP生态 | 10 | 3 | 4 | +1 | 官方 MCP 接入/工具节点；自改造 **4 MCP（vscode-mcp-server / amap / pdf-reader / headroom）多传输，1 enabled=pdf-reader**；**drawio / drawio-local 退役（损失 L2）**。**判据说明**：本维量的是「平台接外部世界的可扩展成本」——**多传输能力未变，server 数与启用数属用户配置选择** → 曾触及 4→3 边界仍维持 4（口径已登记） |
| 记忆 | 10 | 3 | 5 | +2 | 官方 SQLite session + compaction（会话级）；自改造 MEMORY.md 跨会话（13137 B / 15 段）+ pending.json 结构化状态 + reflection-worker + **生命周期治理与机检**（满分档） |

> **本轮复评数值未变的原因 = 档位未跨**：v1.4 的净变化是**「能力纵深 + 结构调整 + 2 项损失」的混合**——agent 10→9 与 MCP 6→4 属结构调整（且其中 L1/L2 是**真损失**，见 §5b），需求发现三层栈 / 判据方法论 / 能力体检 SOP / 2 插件属能力纵深。二者均**未触及任何 5 档产品阈值**——多Agent/工作流仍未达可视化画布级、skill 仍未达插件市场级、model 仍未达数百模型开箱；封顶因素（一键部署 = 个人 config 无分发、沙箱 = 非 VM 隔离）亦未变。故 8 维分值维持，仅刷新依据并登记损失。

## 5. 六大核心发现

**发现一：弱环反转——官方两大最弱环（E/R）被装配层补齐并反转（仍成立，但本轮有增有损）。**
官方内核 E 环（2.0）几乎只有环境/工具返回作为传感器、无独立 Critic；R 环（2.0）仅有错误回灌 + doom_loop + revert，是半开环。自改造以 search-behavior 信源分级 + search-worker 证据包 + grill-me/question 用户确认把 E 环反转至 4.0，并**扩为双领域自动门控**（gate_architecture.py + gate_requirement_discovery.py，后者含 G-R1–G-R9 与 11 例正负向自检）；以 pending.json 状态机 + reflection-worker + /reflection 签名门禁把 R 环反转至 4.5，本轮再加零和预算与机检治理。补强方式不是改引擎，而是装配层协议 + 专职 worker + 记忆系统。**但 E 环同时损失了视觉代看路径（L1），故本轮是「有增有损相抵」而非继续净增。**

**发现二：精装度 v1.2 已跃升 2.9 → 3.9（Δ+1.0），v1.3/v1.4 复评确认未跨档位（诚实口径）。**
v1.2 完成从 2.9 到 3.9 的档位跃升：8 维中 6 维提升，记忆 +2（会话级 → 跨会话长期记忆，达满分 5）、skill +2（无预装库 → 精选库），多Agent/工作流/模型/MCP 各 +1；仅一键部署与沙箱未提升——个人装配层无分发渠道、无完整沙箱，是精装度封顶 3.9 而非更高的主因。v1.3 的机制增多（架构三层栈、能力扩展 SOP、7 个新 skill）与 v1.4 的机制增多（需求发现三层栈、判据方法论、能力体检 SOP、2 插件）**均未跨评分模型 5 档产品阈值**，故不虚报跃升、维持 3.9，仅刷新 evidence。

**发现三：从单体双速控制器到分层编排平台。**
官方是「plan/build 双速 + task 委派」的单体结构，最突出的 P/T 环已很强；自改造在此之上叠加专职 worker 形成「主 Agent 编排 + 专职 worker 执行 + 双领域门控 + Reflection 自演化」的分层平台，P 环升至 5.0、T 环升至 5.0。代价是编排拓扑仍靠协议文本而非 DAG 画布约束，且闭环反思仍需 /reflection 人工确认。**本轮 worker 编队由 6 收敛为 5，视觉与制图两条专职链退出——平台变「薄」了，但领域覆盖由「制图+视觉」换为「需求发现」，属结构替换而非简单缩编。**

**发现四：装配层具备二阶自我扩展能力与领域化门控（本轮扩为「双域 + 姊妹件 + 判据方法论」）。**
其一，能力扩展 SOP（opencode-capability-extension）使装配层不仅拥有若干能力，还拥有「为自己系统性地新增能力」的元能力；其二，**本轮新增体检件 opencode-capability-audit（只读能力体检/再评估 SOP），与扩展件成姊妹件——二阶能力从「只会加」变为「能加、能查、能减」**，且退役动作有了显式登记位（`skills/disabled/`）；其三，**判据方法论 criterion-design-validation 把 E 环推到「元评估」层**：不仅问「门过没过」，还问「门本身可不可信」（治假绿/假跑/恒真判据/空集/阈值无推导）；其四，架构判断三层栈与**需求发现三层栈（0921）**同构并存，装配层由「首个五元齐备的领域级闭环」演进为「**双领域同构回路**」；其五，治理强度仍呈梯度——运行时硬阻（gate 脚本确定性二值判定）> 半运行时（权限 allow/deny）> 纯提示词（GATE / MEMORY 硬门禁）；本轮 MEMORY 门禁已从提示词层**下沉到权限层**（全局 deny + build 级 allow 唯一写入路径），并配机检兜底。

**发现五：「数量下降 ≠ 能力下降」——但也不等于「没有损失」（诚实登记，新增）。**
本轮 agent 10→9、MCP 6→4，若只看计数会被读成「能力缩水」；若只看机制增量又会被读成「全面增长」。**两种读法都不诚实。**正确口径是三分：① **结构调整**（worker 由「制图+视觉」换为「需求发现」，档位判机制形态而非个数 → 多Agent 维维持 4）；② **真损失**（L1 视觉代看路径消失、L2 绘图 MCP 生态位空缺 → 逐项登记在 §5b）；③ **能力纵深**（需求发现栈 / 判据方法论 / 体检 SOP / 2 插件）。**登记损失的义务不因「取舍是主动的」而免除**：主动取舍仍有代价，代价要写在纸面上。同理，MCP 维「维持 4」也不是「4 个和 6 个一样好」，而是「本维量的是平台可扩展成本，多传输能力未变」——判据说明必须与结论同行。

**发现六：「未入库轮次的补账义务」（新增）。**
`0914-自改造opencode再评估v1.4` 那次全量复评**明确「不更新知识库」**，导致 KB 缺 **2026-09-11 → 2026-10-11 的整段记录**（该期间发生了前端栈建了又退、vision 废除、需求发现落地、通知插件、provider 拆分、MEMORY 生命周期治理六件大事）。**教训**：知识库与实机之间一旦出现「已复评但不入库」的轮次，缺口会**静默累积**——后续读者看到的是一份「看起来连续、实际断档」的画像，且断档期的损失（L1/L2）最容易被漏记。故本轮把缺口期一次性补为一节（`03-cases/opencode-custom.md` §8，含该轮实机口径 11 agents / 43 可加载 skill / 4 停用 / 3 commands / 6 instructions / 6 MCP / 4 providers / 16 models / 32 variants / 9 scripts），**并在本节留下「补账义务」这条可复用教训**：**凡「已复评但按口径不入库」的轮次，必须在下一轮入库时显式补账，且补账节须标注缺口起止与不入库原因。**

## 5b. 两项能力损失登记（L1 / L2）

> ⚠️ **本节是防止「只报增长」的必要声明，缺失即等于选择性披露。**

| 编号 | 损失 | 发生时点 | 具体后果 | 补偿路径（不等价，仅记现状） |
|------|------|---------|---------|--------------------------|
| **L1** | **视觉代看机制退役** | 0915（vision-worker 废除；连带 `subagent_depth 2→1`、pdf/frontend worker 的 `task→vision-worker` 块删除） | **E 环少一条「图像是否达标」的降级传感器路径**：原「父会话无视觉 → 委派 vision-worker 代看 → 失败降级 PNG 结构校验」三段降级链消失；现为「模型原生视觉直接 Read；模型无视觉 → **由人终判**」。**无视觉会话下图像达标判定退化为人工，自动化程度净下降** | 会话模型原生多模态（deepseek-flash V4.1）；判据侧 semi 判据改「人终判」（`gate_frontend.py` 的 semi 判据经核不依赖 vision-worker，无需修改） |
| **L2** | **MCP 工具面收窄** | 0915（drawio / drawio-local 两个 MCP 退役，连同 drawio-worker 与 `skills/drawio-reference/` 整包） | 配置 **server 数 6→4、启用数 2→1**（仅 pdf-reader）；原「drawio-worker → MCP 导出（Puppeteer 冷启）→ vision 核对」制图链整体拆除。**平台侧可插拔绘图生态位空缺** | 制图改走 `diagram-lite` skill 档位出图（T0 文本退化 / T1 模板填空 / T2 DSL→SVG 默认 / T3 发布级）；成本对照：旧链路「委派 worker + 1000+ 行 skill 重放 + Puppeteer 冷启 + 再委派代看」→ 新链路「一行 `dot -Tsvg`（0.1s）+ 一次 Read」——**能力形态由「MCP 生态 + 专职 worker」降为「skill 档位 + 主 Agent 亲自执行」** |

**口径克制声明**：两项损失**均为主动取舍**（0915 重构 8/8 验收判据 PASS + 重启后活体冒烟 5/5 + 负向冒烟 `Agent vision-worker not found` 已验），**但「主动」不等于「无代价」**。故：**既不为增长叙事掩盖损失，也不因损失而下调分值**——MCP 维判据是「平台多传输能力未变，server 数与启用数属用户配置选择」（维持 4），E 环按「有增有损相抵」维持 4.0。**若未来出现「无视觉会话 + 高图像达标要求」的场景组合，L1 将成为真实瓶颈**，届时应重新评估 E 环。

## 6. 排名隔离声明

本文件评分的对象是**个人装配层变体**（`opencode-custom` = 官方 opencode 内核 + 个人 config 装配层），**不是市售产品**。因此：

- `opencode_custom_scores.py` **独立于 `premium_scores.PRODUCTS`**，其分值**不参与 14 产品市售排名**，不得与 `premium-map.html` / `premium-cyto.html` 中的产品分同轴比较；
- 官方 `opencode` 与 `opencode-custom` 构成**同源对照对**（同一内核、同一模型、同一权重），只回答「装配层带来多少增量」，不回答「opencode-custom 在 14 产品中排第几」；
- 与 `dsh-custom` 专题同构：两个装配层变体分属两个宿主（opencode / dsh），**跨宿主比 Δ 有意义，比绝对值无意义**（基线不同、可用机制不同、L1/L2 类损失各侧不同）——参见 `03-cases/dsh-custom-diff.md`（只读参考，不参与本专题分值）。

## 7. 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S4 | 一手配置观察 | `07-checkpoint/opencode-custom-snapshot/opencode.jsonc`（agent/provider/mcp/permission/compaction 原文；`subagent_depth=1`；全局 `edit: MEMORY.md=deny` + build 级 allow；`pdf-reader_*` 全局 deny / agent 级 allow；0916 D-01 门控脚本放行注释） | 高 |
| SRC-002 | S4 | 一手盘点（新快照） | `07-checkpoint/opencode-custom-snapshot/inventory.json`（**9 agents / 4 MCP（1 enabled）/ 45 可加载 skill + `_shared` + `disabled` 4 件 / 6 instructions / 3 commands / 2 plugins / 6 providers**；`collected_at=2026-10-11T17:04:12+08:00`）；旧版归档 `inventory-v1.3.json` | 高 |
| SRC-003 | S4 | 一手快照清单 | `07-checkpoint/opencode-custom-snapshot/manifest.json`（13 文件 sha256_16 + 字节数；MEMORY.md **13137 B**） | 高 |
| SRC-004 | S4 | 一手协议观察 | `07-checkpoint/opencode-custom-snapshot/instructions__auto-mode.md`（GATE/COMPLEXITY/variant/子Agent规则/委派/Reflection自检/压缩模板；原 agent-protocol.md 已并入且落盘但不注册） | 高 |
| SRC-005 | S4 | 一手协议观察 | `07-checkpoint/opencode-custom-snapshot/instructions__architecture-behavior.md`（架构触发规则/知识分层/openspec design 门控） | 高 |
| SRC-006 | S4 | 一手协议观察（新） | `07-checkpoint/opencode-custom-snapshot/instructions__requirement-discovery-behavior.md`（0921 需求发现行为层；≤22 行压紧；定档前置 K1–K5＋M1；简单档不加载/不委派/不产工件） | 高 |
| SRC-007 | S4 | 一手协议观察 | `07-checkpoint/opencode-custom-snapshot/instructions__search-behavior.md`（外部信息实证/时效准则/信源分级） | 高 |
| SRC-008 | S4 | 一手命令观察 | `07-checkpoint/opencode-custom-snapshot/command__reflection.md`（三池扫描/签名门禁/容量分层/双版本同步；**§4b 零和预算 + 边际显著性三问**） | 高 |
| SRC-009 | S4 | 一手命令观察 | `07-checkpoint/opencode-custom-snapshot/command__arch.md`（/arch 场景路由 / architect-worker 委派 / gate_architecture.py 门控流程） | 高 |
| SRC-010 | S4 | 一手命令观察（新） | `07-checkpoint/opencode-custom-snapshot/command__rd.md`（/rd 需求发现入口，一律复杂档） | 高 |
| SRC-011 | S4 | 一手插件观察（新） | `07-checkpoint/opencode-custom-snapshot/plugins__system-date-transform.ts`（prefix-cache 日期治理；日志 `~/.cache/opencode/plugin-system-date.log` 17277 行） | 高 |
| SRC-012 | S4 | 一手插件观察（新） | `07-checkpoint/opencode-custom-snapshot/plugins__notify-on-pause.ts`（会话暂停桌面通知；`notify.json` enabled=true；日志 7045669 行 + `notify-receipts.log`） | 高 |
| SRC-013 | S4 | 一手机检脚本（新） | `~/.config/opencode/scripts/memory_capacity_check.py`（单段占比 >50% / `--baseline` 段数零和 / 阈值推导式；selftest **8 → 13 例**） | 高 |
| SRC-014 | S4 | 一手治理脚本集（新） | `~/.config/opencode/scripts/`（**14 .py + 1 json + 3 .ps1**：pending_io / memory_capacity_check / subtraction_coverage_check / prompt_audit / drift_reconcile / dual_root_check / gate_host_check / capabilities_reconcile / asset_inventory / evidence_freshness / memory_write_path_audit 等） | 高 |
| SRC-015 | S4 | 一手能力包观察 | `skills/architecture-judgment/`（SKILL.md + 167 节点方法论图谱 + schemas + `_private/gate_architecture.py`） | 高 |
| SRC-016 | S4 | 一手能力包观察（新） | `skills/requirement-discovery/`（0921 三层栈：workflow/checklist/routing/templates/schemas + `_private/gate_requirement_discovery.py` + `_private/CRITERIA.md`；词表真单源 `check_tier_conditions.py`） | 高 |
| SRC-017 | S4 | 一手能力包观察 | `skills/opencode-capability-extension/`（能力扩展 SOP：三层栈 / 统一双根 / 引用普查 / 契约+门控+冒烟） | 高 |
| SRC-018 | S4 | 一手能力包观察（新） | `skills/opencode-capability-audit/`（只读能力体检/再评估 SOP，与扩展件成**姊妹件**） | 高 |
| SRC-019 | S4 | 一手能力包观察（新） | `skills/criterion-design-validation/`（判据构造—实现—验证—维护四阶段方法论） | 高 |
| SRC-020 | S4 | 一手留档（0914 缺口轮） | `Mission-file/2026-09/0914-自改造opencode再评估v1.4/report.md`（**明确「不更新知识库」**；该轮口径 11 agents / 43 可加载 skill / 4 停用 / 3 commands / 6 instructions / 6 MCP / 4 providers / 16 models / 32 variants / 9 scripts）+ `evidence/inventory-v1.4.json` + `evidence/remediation-verify.json`（44 工单） | 高 |
| SRC-021 | S4 | 一手留档（L1/L2 发生轮） | `Mission-file/2026-09/0915-绘图链路重构执行/报告.md` + `REWRITE-CONTRACT.md`（drawio 退役 + vision-worker 废除 + `subagent_depth 2→1` + `diagram-lite` 新建；8/8 PASS、活体冒烟 5/5、负向冒烟 `Agent vision-worker not found`）；规划侧 `…/0915-绘图链路重构与drawio退役/PLAN.md` | 高 |
| SRC-022 | S4 | 一手留档（前端栈建/退） | `Mission-file/2026-09/0913-前端能力建设[ABANDONED]/report.md`（frontend-worker + frontend-behavior.md 38 行 + /frontend + gate_frontend.py）；`Mission-file/2026-09/0916-前端技术栈基线/ABANDONED-REGISTER.md`（退役登记） | 高 |
| SRC-023 | S4 | 一手留档（需求发现 0921） | `Mission-file/2026-09/0916-产品设计方法论/20-agent-skill/`（SKILL.md + `_config/command/rd.md` + `_config/instructions/requirement-discovery-behavior.md` + `_private/gate_requirement_discovery.py` + schemas）；分层定档工具 `…/0916-产品设计方法论/tools/check_tier_conditions.py` | 高 |
| SRC-024 | S4 | 一手留档（通知插件 0926） | `Mission-file/2026-09/0926-通知弹窗需求发现/report.md` + `adr/ADR-001-notify-mechanism.json` | 高 |
| SRC-025 | S4 | 一手留档（provider 拆分 0927） | `Mission-file/2026-09/0927-cmdcode免费模型双harness接入/report.md`（commandcode 拆为付费 9 + 免费 4；一 key 一变量名） | 高 |
| SRC-026 | S4 | 一手留档（MEMORY 生命周期 1010） | `Mission-file/2026-10/1010-reflection-review/report.md` + `report-round2.md` + `report-round3-lifecycle.md` + `evidence/ledger-1010*.md`（三轮深迁移 −46%、零和、机检落地） | 高 |
| SRC-027 | S1 | 可复算评分 | `09-src-data/opencode_custom_scores.py`（官方 2.9 / 自改造 3.9，8 维与六环分值单一数据源；**本轮 v1.4 口径已在文件头登记漂移与 L1/L2，分值未改动**） | 高 |
| SRC-028 | S1 | 评分模型 | `07-checkpoint/premium-scoring-model.md`（精装度 v2.0：硬门槛 + 8 维加权 + 一票否决） | 高 |
| SRC-029 | S4 | 对照基线 | `03-cases/opencode.md`（官方 opencode 内核五环结构与结论口径；本机运行时 **1.18.35**，上游 v1.19.0 只登记不追） | 高 |
| SRC-030 | S4 | 对照参考（同轮姊妹件） | `03-cases/dsh-custom-diff.md`（另一宿主的装配层对照写法，**只读参考**，不参与本专题分值） | 高 |
