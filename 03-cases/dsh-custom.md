# dsh-custom（dsh v0.2.1-alpha.2 + dsh-opencode-port 装配层）— Agent 控制论画像

> 本画像定位为官方 dsh（DeepSeek Harness）的衍生变体·个人装配层。**内核零改动**：dsh v0.2.1-alpha.2（2026-10-09，commit `d743267`）的源码树一行未动，全部增量落在装配层 `dsh-opencode-port` bundle —— `~/.dsh/presets/opencode/`（bundle 本体）+ `~/.dsh/skills/opencode/`（主根 49 件 skill = 派生 47 + DSH 原生 2）+ `~/.dsh/profiles/web/cordis.patch.yml`（宿主增量）。它把 opencode 侧的行为纪律、skill 库与 7 个角色「化用」为 dsh 的三个自定义 preset（`opencode-standard` / `opencode-creator` / `opencode-ptc`）——v1.5 另以 `run_gate` 窄通道消解 E 环抑制项、以 R-A 记忆载体追平 R 环迁移损失；来源工程见 `Mission-file/2026-10/1011-deepseek harness-提示词迁移工程-从opencode/`。证据强度为源码级（配置级），全部结论可回溯至 bundle 原文与机检产物。与官方 dsh 的关系是「内核继承 + 装配层迁移」：五环中 SP +0.5、M +0.5、P +0.5、R +1.0 为增强，E +2.0（**反转**），T 环持平（已封顶）——v1.4 记的**迁移损失已在 v1.5 二次追平**（R 环 R-A 载体落地、E 环 `run_gate` 通道消解抑制项）。

## 0. 精装度评估

> 定位：个人装配层（官方 dsh 衍生变体）｜ 精装度：3.9/5 ｜ 分类：个人变体（官方衍生）｜ 一手/二手：一手 ｜ 证据强度：源码级（配置级）

**综合评分**：3.9/5 — 在内核继承官方 dsh（3.6/5）之上，以「3 preset 编队 + 7 专职 worker + 主根 49 skill（模型可见 46）+ persona 15 节纪律固化 + 5 档 permission」做定向补强，8 维中 **memory 一维提升（4→5，权重 10% ⇒ +0.10）**，skill 维**维持 4**（主根 45→49 但档位未变），精装度 3.6 → 3.9（Δ+0.3）。**升幅有限是诚实口径**：装配层不是产品化跃迁，而是把既有 opencode 能力搬进 dsh 的 preset 层——multi/deploy/model/workflow/sandbox/mcp 六维全部维持官方值，档位仍为「成品化受限」，**未跨档**。封顶因素（一键部署=不可移植的手动 bundle、MCP=宿主 0 配置）与官方同构，未改善。

> ⚠️ **口径披露（必须与评分单一数据源一致）**：v1.3 之前 dsh 在本库中**只有单点分 2.5**（`gen_html.py` 的 `FRAMEWORK_DATA`，属「技术框架对照」口径，**不是**本 8 维模型输出）。v1.4 **首次**按 v2.0 模型回填 8 维，故 **3.6 与 2.5 不同源、不可直接相减**（2.5 是定性对照分，3.6/3.9 是加权模型分）；旧单点分作为**历史口径保留**，不得用于计算「跃升」。数值唯一来源：`09-src-data/dsh_custom_scores.py`（官方 `raw 3.63→3.6`；装配层 `raw 3.85→3.9`）。
>
> ⚠️ **第二条口径披露（v1.5 新增）**：**沙箱维分值未变（仍 4/4）但证据文本被更正**——v1.4 记「本机无可用沙箱后端（bubblewrap/Landlock 均不可用）→ 实际 fail-closed」，v1.5 实测该断言**已证伪**（bwrap 已装、链选中 bwrap、`enforcement=full`，read-only / workspace-write 在 shell + fs 双侧真强制）。此为**环境事实更正**，⛔ 不是装配层能力增量、⛔ 不计入分值变动、⛔ 不得呈现为装配层收益。

**预装能力表**：

| 维度 | 预装情况 | 依据 |
|------|---------|------|
| 多Agent编排 | 具备 | 3 preset 编队（order 11/12/13）+ 7 专职 worker（general/explore/architect/requirement-discovery/search/reflection/pdf）+ 全局控制面 `send_message`/`interrupt_agent`/`list_agents`；仍无真 DAG/画布（未达 5 档） |
| Skill库 | 具备 | 主根 **49** 件 skill 单根（`~/.dsh/skills/opencode/`）= 派生 47 + **DSH 原生 2**（`dsh-config` / `dsh-reflection`），**模型可见 46** = 49 − 3 件 `disable-model-invocation: true`；`_overlay/` 另 6 件 openspec 系叠加层；精选个人库、无市场/分发（未达 5 档） |
| 工作流 | 具备 | persona 15 节把 GATE/COMPLEXITY 自评、契约驱动委派、留档 5 段模板迁入 preset 层 + plan-mode section 追加 grill-me 逐题访谈指引；无通用可视化画布（未达 5 档） |
| 模型接入 | 具备 | 宿主 profile 4 provider（zai/opencode-go/commandcode/opencode-go-tmp）+ deepseek 直连 + `input: [text, image]` 视觉声明；仍非「千级模型开箱」（未达 5 档） |
| 一键部署 | 部分 | bundle 需手动 `install_bundle` 且**不可移植**（persona 含本机绝对路径、`node_modules` 28 个符号链接指向本机源码树）；无 npm/docker/SaaS 分发 |
| 沙箱 | 部分 | 宿主 permission 5 档（read-only / workspace-write / **opencode-plan** / **opencode-build** / danger-full-access），`defaultPreset` 由 read-only 改为 **opencode-plan**；后两档属**审批档而非隔离档**。⚠️ v1.5 事实更正：本机沙箱后端**已可用且 `enforcement=full`**（bwrap 已装、链选中 bwrap，read-only / workspace-write 在 shell + fs 双侧真强制）——**环境事实更正，非装配层能力增量 ⇒ 维持 4 档** |
| MCP生态 | 部分 | 宿主 **0 个 MCP 配置**（对比 opencode-custom 侧 **4 个**）——迁移相对损失，维持 3 档 |
| 记忆 | 具备 | 事件溯源 session + 投影 + token-meter + compaction（内核继承，未变）；装配层 v1.5 **已落地 R-A 跨会话载体**：`~/.dsh/MEMORY.md`（14 个 `§` 段 / 10815 B / 57 行 / 14 条 `[src:]` 签名）+ `~/.dsh/reflection/candidates/` 15 份候选 + `archive/` 1 份 + `dsh-reflection` skill（零和预算 / 生命周期五件 / 容量口径 `memory_capacity_check.py`）→ 8 维 memory 4→5 |

**声称 vs 实际**（8 条，全部一手取证）：

1. **`plugin_manager` 可用范围**：bundle `README.md` §2 原称「内置 `standard` / `cordis` 会话里可用」→ 实测内置 `standard` 会话 31 个工具**无** `plugin_manager`（仅内置 `cordis` preset 与 `opencode-creator` 模式可用；`web-app` bundle 顶层把 `tool-plugin-manager` 写 `disabled: true`）。README 已加更正记录。
2. **门控结论已过期**：bundle `README.md` §8 与证据文件标「13 项 PASS、门控全绿」→ 第三方新鲜复跑**第 11 项 FAIL**。根因＝宿主 patch 是**活文件**（GUI 改字号/主题/模型都会写回），按整文件 sha256 判漂移会把一次字号调整判成红灯——**假阳性会训练人忽略红灯**；已改为 `scoped_digest` 只对 bundle 实际消费字段（`system-prompt.personaPrefix`）判漂移。（v1.5 判据数已扩至 **20 项**，见 §7.5。）
3. **「45 件 skill」口径**：被当作新模式会话的技能规模 → **v1.5 已改用契约 §2.6 唯一口径**：主根 **49**（派生 47 + DSH 原生 2），**模型可见 46**（49 − 3 件 `disable-model-invocation: true`）。v1.4 的「45 是派生目录口径、模型可见仅 42」已被新口径取代；运行时技能目录三模式均 46，内置 `standard` 为 0。
4. **bundle 被当作可分发迁移包** → **不可移植**：persona 含本机绝对路径，`node_modules` 28 个符号链接指向本机源码树 `/home/zako-mio/dsh/packages/...`。
5. **read-only 档下 bash 仍可跑**：README §4#1 括注「只栅栏写」→ v1.4 记「本机**无可用沙箱后端**（bubblewrap/Landlock 均不可用），`read-only` 与 `workspace-write` 档 `bash` 一律 fail-closed」——**该断言已于 v1.5 证伪**：bwrap 已装、链选中 bwrap、`enforcement=full`，read-only / workspace-write 在 shell + fs 双侧**真强制**（唯一可跑档不再是 `danger-full-access`）。⚠️ 此为**环境事实更正**，⛔ 不计入装配层收益。
6. **`allowed-tools` 惰性键范围**：`ADAPTATION-NOTES.md` 第 14 行称只涉 13 个 openspec 系 skill → 实测派生副本中 **18 件**带该键 = 13 件 openspec 系 + **5 件非 openspec 系**（agency-agents / pdf-ocr / resume-builder / recruit-assist / lark-suite）；`opencode-config` 另带该键，但属 `disable-model-invocation: true` 的 3 件之一，是否计入取决口径。
7. **creator 技能根分支恒不生效**：creator 的 `customSkillDirs` 会用 `!!js` 追加 `dsh-agent-preset/skills` 技能根 → 该目录**实测 ABSENT**，`existsSync` 恒假，该分支永不生效（creator 与 standard 技能根实际相同）。
8. **persona 税与空指向**：每次请求 persona 税（v1.5 为 **6524 字符 / 12066 B**，v1.4 为 8018 字符 / 15403 B；内置 `standard` 仅 54 字符）；**PTC 模式下**工具目录坍缩为单 `run_code`（系统提示 13658 → 53826 字符），而 persona §二 仍写「本模式提供 `subagent`、`oc_explore`…」→ 在 PTC 下是**空指向**（声明了不存在的工具面）。

## 1. 设定值（Setpoint）——用户意图 → 可验证子目标

**承担角色**：由「preset 层 persona 15 节 + plan-mode section 覆写 + 三层触发规则（架构/需求/出图）+ 委派契约」共同承担，把 opencode 侧原本靠 instructions 文件承载的目标分解纪律，固化进 dsh 的 preset 声明层——设定值从「提示词约定」升级为「preset 声明」，三模式各自声明完整插件列表（`cordis.patch.yml:9-1305`）。

**关键机制**：
- **persona 15 节固化设定值纪律**：`~/.dsh/presets/opencode/persona.md`（15 节 / **6524 字符 / 12066 B**，v1.4 为 8018 字符 / 15403 B，`:5-150`）把「调度者定位 + 复杂度自评四维表（`:11-22`）」「委派判据（≥2 工具/联网/多步推理）」「子 Agent 只执行不委派（`:44-48`）」「留档 5 段模板（`:85-92`）」写进 preset 的 `persona.prefix`，随模式激活自动注入。
- **复杂度自评（GATE 化用）**：`persona.md:20-22` 保留 opencode 的 ≤12 常规 / ≥13 高档判据，但**删除**字面门控格式与变体切换（dsh 无变体概念，模型与推理档由 profile `route` 声明）——设定值纪律保留、其载体被诚实改写。
- **plan-mode section 覆写**：`cordis.patch.yml:219-235` 把内置 plan-mode section 从 2358 字符扩到 2515 字符，追加 3 行中文**逐题访谈**指引（一次只问一问，能自行探索的分支不反问用户），把 opencode 的 Plan 模式纪律落成 dsh 的 plan-mode 配置。
- **三层触发规则**：架构类任务先答「规模三问」再定档（`cordis.patch.yml:131-148`，门控级须走 skill→worker→gate 三步）；需求发现走**机械定档**（`cordis.patch.yml:152-161`，调 `check_tier_conditions.py`，工具不可用须显式标 FAIL、不得凭感觉选档）；出图/视觉/PDF 各有归位规则（`:163-167`）。
- **委派契约**：`cordis.patch.yml:54-61` 规定子 Agent 必须按固定 JSON 返回（`status/summary/data/files_created/...`），主 Agent 按 `success`/`partial`/`failed` 分派聚合策略——设定值以可解析契约跨 Agent 传递。
- **留档路径门控**：`persona.md:90` 要求保存前校验路径符合 `Mission-file/{YYYY-MM}/{MMDD-任务名}/`，不通过即拒绝保存。

**控制论映射**：KT-ctrl-002（设定值 r = 用户意图）/ KT-ctrl-045（规划-执行解耦，preset 声明即参考序列固化）/ KT-ctrl-041（分层时标，复杂度自评决定推理档）/ KT-ctrl-046（options/SMDP，三层触发规则把意图映射为动作原语）。

**强弱项**：强——设定值纪律从「提示词文件」变成「preset 声明」，模式切换即生效；三层触发规则（架构/需求/出图）把模糊意图先物化为档位再执行；委派契约可解析。弱——设定值仍以 prompt 文本编码为主，复杂度自评是模型自报而非外部测量；persona 含本机绝对路径，设定值与环境强耦合（可移植性差）。

**双层评分**：内核 4.5/5 + 装配层 Δ+0.5 → 综合 5.0/5（增强）

---

## 2. 传感器 / 评估环（E 环）——测"当前执行是否达标"

**承担角色**：在官方 dsh「E 环近开环、无独立 critic」的基线上，装配层迁入 opencode 侧的**领域级评估栈**——`oc_architect`+`architecture-judgment`（含 `_private/gate_architecture.py` ADR schema 门控）、`oc_requirement`+需求分层定档工具、`oc_search` 证据包与信源分级、`criterion-design-validation`。E 环由此从 2.0 升至 **4.0（Δ+2.0，达反转阈值）**——v1.4 的抑制项已被 `run_gate` 窄通道消解。

**关键机制**：
- **架构域自动门控**：`architecture-judgment/_private/gate_architecture.py --kind adr|boundary` 对 `oc_architect` 产出做 schema + 知识图谱机检，PASS 前不得交付、FAIL 原样回传修正≤2 轮、**不得降级为口头通过**（`cordis.patch.yml:143`、`:147`）。
- **需求域定档工具**：`requirement-discovery/_private/local-bindings.json:5` 绑定 `check_tier_conditions.py`，机械定档而非「看难度」裁量；工具不可用必须标 FAIL（`cordis.patch.yml:152-157`）。
- **信源分级传感器**：`persona.md:100-110` 规定依赖外部事实的结论必须先搜索并打开原始页面、区分「已验证事实/基于证据的推断/尚不确定」、重要结论 ≥2 独立来源交叉验证；`oc_search`（`cordis.patch.yml:346-368`，allow `web_search`/`web_fetch`）把「外部信息是否可信」外包给专职 Agent 并输出结构化证据包。
- **判据可信度方法论**：`criterion-design-validation` skill（`~/.dsh/skills/opencode/criterion-design-validation/`）专治假绿/假跑/恒真判据——正是本轮第 11 项 FAIL 的处置依据。
- **验证优先纪律**：`persona.md:59-64` 规定「没有新鲜的验证证据，不得声称完成」；`cordis.patch.yml:160` 进一步规定「门控全绿/产物被验收/流程走完一律不得当作已达成」。
- **门控执行通道（v1.5 新增，ADR-010）**：三 preset 各 +1 顶层 `gate-runner` 行（本地插件 `dsh-opencode-gate-runner`），注册模型可见的**窄工具 `run_gate`**，为**产出方恢复了门控脚本执行能力**；参数面受限（脚本路径 + argv 数组，roots / 扩展名白名单，超时 120s / 600s，输出 16KB 封顶后 spill），负向用例 18→30 条。
- ✅ **v1.4 抑制项已消解**：v1.4 记「门控脚本依赖 `bash`，而 dsh 子 Agent 无 `bash` 工具（各 worker 的 `toolFilter.deny` 整条禁掉 shell，`cordis.patch.yml:318` 等）→ 门控无法在子 Agent 内自跑，只能由主 Agent 串行执行且需 `danger-full-access` 档（`:148`）」——该抑制项**已消解**，E 环达反转阈值。对比 opencode 侧同名栈可自跑门控，**这边 v1.5 亦判反转**。

**控制论映射**：KT-ctrl-006（强校验降低对基座模型误差敏感）/ KT-ctrl-035（DOB 式在线评估外部偏移，`oc_search` 交叉验证）/ KT-ctrl-012（观测噪声 R，信源分级=按可信度加权）/ KT-ctrl-001（E 环是闭环开关）。

**强弱项**：强——补上了官方最弱环的主要缺口：架构产出有 schema 自动门控、需求定档机械化、外部事实有专职核查管线与信源分级、判据本身有可信度方法论；v1.5 的 `run_gate` 窄通道更把「门控能不能在产出侧跑」这一硬缺口补回（含 30 条负向用例）。弱——①覆盖仍是**领域级单点**（架构/需求两域），无通用独立 Critic 对「语义是否达标」做强验证；②门控执行通道虽已恢复，但**独立验证方（critic）未分离**——产出与验证仍在同一 Agent 会话内；③信源分级是准则而非自动门控，执行仍靠自律。

**双层评分**：内核 2.0/5 + 装配层 Δ+2.0 → 综合 4.0/5（**反转**）

---

## 3. 执行器 / 工具环（T 环）——工具调用容错与安全约束

**承担角色**：在官方内核「三瀑布工具管线 + 超时看门狗 + spill + 审批仲裁」之上，装配层以「permission 5 档 + 工具面按 preset 收敛 + 各 worker `toolFilter` 最小授权」做**收口**——不是扩容，而是把执行器边界按模式与角色重新划分。

**关键机制**：
- **permission 5 档**：`~/.dsh/profiles/web/cordis.patch.yml:240-264` 整表重述，新增 `opencode-plan`（sandbox read-only）与 `opencode-build`（sandbox workspace-write）两档，原有三档逐字保留；`defaultPreset` 由 `read-only` 改为 **`opencode-plan`**；新增两档是**审批档（approval: ask）而非隔离档**。
- **门控执行窄通道（v1.5 新增）**：三 preset 顶层各 +1 `gate-runner` 行，注册受限工具 `run_gate`（脚本路径 + argv 数组、roots/扩展名白名单、超时 120s/600s、输出 16KB 封顶后 spill）——执行器面新增一条**受约束的**脚本执行通道，而非放开 shell。
- **工具面按 preset 收敛**：内置 `standard` 31 工具 / `opencode-standard` 37（含 6 个 `oc_*`）/ creator 40（+`cordis_inspect_*` + `plugin_manager`）/ ptc **1**（仅 `run_code`，PTC 呈现）。
- **`plugin_manager` 三态收口**：standard 硬禁（`cordis.patch.yml:436-438` `disabled: true`）、creator 条件启用（`:867-869` `disabled: !!js "!ctx.get('profileContext')"`）、ptc 硬禁（`:1303-1305`）；插件计数 188 → 191（三 preset 行 `enabled=true`，`fiberPhase=active`）。
- **worker 工具隔离**：7 个 worker 各自 `toolFilter` —— `oc_explore`/`oc_search` 走 allow 白名单（只读 + 检索），其余走 deny（禁 shell / `todo_write` / `ask_user_question`）；平台互斥的 shell deny 用 `!!js` 取字符串（写成数组会触发 `z.array(z.string())` 失败、整 preset 报 broken）。
- **内核继承的执行器护栏**：三瀑布管线（pre/execute/post）、per-tool deadline 看门狗、spill 输出限幅、审批仲裁、协作式取消。
- **迁移相对损失**：opencode 侧的**命令级 bash deny 与 `external_directory` 白名单未迁移**（README §4#1/#5）——只剩档位级 sandbox，执行器精度下降一档。

**控制论映射**：KT-ctrl-034（硬约束限幅+看门狗）/ KT-ctrl-033（冗余与仲裁，permission 档与 worker 白名单分工）/ KT-ctrl-031（鲁棒稳定，默认档 `opencode-plan` + 沙箱 `enforcement=full` 下 read-only/workspace-write 真强制、不可用即 fail-closed）/ KT-ctrl-030（模型不确定性，`approval: ask` 为不确定动作留降级）。

**强弱项**：强——内核执行器本就最强，叠加 5 档 permission 与 worker 级最小授权后边界更清晰；工具面按模式收敛（37/40/1）使模式语义明确；`run_gate` 以「窄参数面 + 负向用例」的方式补回脚本执行通道，未牺牲隔离。弱——①命令级 deny 与 `external_directory` 白名单在迁移中丢失（README §4#1/#5）；②MCP 生态为 0（对比 opencode-custom 侧 **4 个**，是净损失）。✅ **v1.5 事实更正**：v1.4 记「本机无沙箱后端 → read-only/workspace-write 一律 fail-closed、唯一可跑档是 `danger-full-access`」**已证伪**——bwrap 已装、链选中 bwrap、`enforcement=full`，read-only / workspace-write 在 shell + fs 双侧真强制。⚠️ 但这是**环境事实更正，不是装配层新增隔离能力** ⇒ **沙箱维仍 4/4（Δ0）**，⛔ 不得计作装配层收益。

**双层评分**：内核 5.0/5 + 装配层 Δ0 → 综合 5.0/5（持平；已处上限，「收口」不改变分值）

---

## 4. 记忆 / 状态估计环（M 环）——会话记忆与跨会话长期记忆

**承担角色**：继承官方内核的事件溯源记忆栈（append-only session + 投影纯函数折叠 + token-meter + compaction），**并在 v1.5 补上跨会话记忆层**——R 环 R-A 载体落地（ADR-012，门控 6/6）：`~/.dsh/MEMORY.md` 成为 dsh 侧的长期记忆正文载体，`~/.dsh/reflection/candidates/` 成为候选池，`dsh-reflection` skill 承载零和预算 / 生命周期五件 / 容量口径。M 环由此 4.0 → **4.5**（Δ+0.5，增强）。

**关键机制**：
- **内核记忆继承**：事件溯源 session（`session-format v4` 代际迁移）、`SessionProjectionRegistry` 投影折叠、`dsh-token-meter` 回放感知计量、`compaction-basic` + `tool-result-pruner` 压力压缩、`session-query`/FTS5 跨会话检索。
- **装配层的 compaction 配置**：`cordis.patch.yml:236-252` 装配 compaction 组，`tool-result-pruner` 设 `thresholdChars: 8192 / headChars: 4096 / tailChars: 1024`（**与 opencode 侧 3000 字符阈值不同**，persona 第 15 节明确禁止照抄旧阈值）。
- **记忆纪律（v1.5 已改写）**：`persona.md:94-98` 原规定全局记忆库 `~/.config/opencode/MEMORY.md` **只读**、**不常驻上下文**（append-only 变化文件会让系统前缀反复变化、缓存失效，故按需 `read`）——该纪律针对 **opencode 侧**资产，v1.5 下 dsh 侧已有自己的记忆正文 `~/.dsh/MEMORY.md`（只记存在性与容量，正文不入快照、不入公开库，契约 §2.7③）。
- ✅ **R-A 载体落地（v1.5，ADR-012，门控 6/6）**：`~/.dsh/MEMORY.md` 存在（**14 个 `§` 段 / 10815 B / 57 行 / 14 条 `[src:]` 签名**）+ `~/.dsh/reflection/candidates/` **15 份候选** + `archive/` **1 份** + `dsh-reflection` skill 承载零和预算 / 生命周期五件 / 容量口径（`memory_capacity_check.py`）。写入链 = **候选 → 主 Agent 审阅 → 落库**（**显式链，非自动自省**）。⇒ v1.4 的「装配层未新增跨会话记忆」「记忆只能读不能写」**已被推翻**。
- **配置正确性的一次修正**：宿主 `personaPrefix` 原写作 `persona:`（不在 `dsh-system-prompt` 的 config schema 内）→ 等于从未生效；2026-10-10 改为 `personaPrefix:` 并改用会话日志取证验证（`cordis.patch.yml:5-7`）。

**控制论映射**：KT-ctrl-011（卡尔曼式预测-更新，投影=update、token-meter 压力=可观测性门）/ KT-ctrl-014（信息滤波/降维，结构化压缩与 tool-result 裁剪）/ KT-ctrl-010（状态估计，事件溯源折叠）。**仍缺**：KT-ctrl-013（分离性）与**自动自省式**学习（写入为显式人工审阅链，故不取 5.0）。

**强弱项**：强——内核事件溯源提供极高状态保真度与可回放性，压缩参数与 dsh 实际阈值对齐（未照抄 opencode）；v1.5 补上跨会话长期记忆载体（`MEMORY.md` + 候选池 + 退役/归档），使 M 环从「只读单向通道」变为**可写闭环**。弱——⚠️ **机制齐备但内容体量小**（14 段 / 10.8 KB），且**写入为「候选 → 主 Agent 审阅 → 落库」的显式链，非自动自省**；R-A 载体仍处早期，覆盖度与陈旧引用治理依赖机检（`memory_capacity_check.py`）。

**双层评分**：内核 4.0/5 + 装配层 Δ+0.5 → 综合 4.5/5（增强）

---

## 5. 规划 / 分层环（P 环）——慢/快双速 + 专职 worker 编队

**承担角色**：在官方「plan-mode 慢规划 + goal 滚动 + subagent 多级委派 + workflow/ralph」之上，装配层以「+7 专职 worker + `oc_*` 别名 + delegation 编队（12 子行）+ 全局控制面」把通用委派升级为**具名编队**。

**关键机制**：
- **7 worker 与工具别名**：`cordis.patch.yml:253-416`（standard）定义 delegation 组 —— `general`→`subagent`、`explore`→`oc_explore`、`architect-worker`→`oc_architect`、`requirement-discovery-worker`→`oc_requirement`、`search-worker`→`oc_search`、`reflection-worker`→`oc_reflection`、`pdf-worker`→`oc_pdf`；worker persona 单一来源是 `~/.config/opencode/opencode.jsonc` 的 `agent.<name>.description`。
- **全局控制面**：`tool-subagent-control` + `list-agents`（`cordis.patch.yml:259-262`）提供 `send_message` / `interrupt_agent` / `list_agents` —— 父层对子层有持续干预通道（不止「一次性委派」）。
- **深度控制的双实现**：worker 均**省略 `maxDepth`**（省略读 Host 默认 1，可被委派），「不可再往下委派」由各 worker 的 `toolFilter.deny`（含 `subagent_fork` 与 6 个 `oc_*`）承担。旧写法 `maxDepth: 0` 会让 worker「一调用即报错」，已修正并加三条负向用例（`verify_bundle.py:366-398`）。
- **编队规模**：v1.4 报 standard 顶层 21 行 / 展开 34 行，creator 22/35，ptc 22/35；**v1.5 三 preset 各 +1 顶层 `gate-runner` 行**（⇒ 顶层行数各 +1，展开子行数不变，`verify_bundle` 展开后子行校验面仍为 43 行）。v1.5 现跑读数见 `1011-全面适配性迁移分析/evidence/r11-final-gates.out.txt`（⛔ 本画像不自行推算顶层行数）。
- **模式化规划能力**：ptc 模式下 `workflow-ptc` 与 `tool-workflow` **双禁**（`cordis.patch.yml:1278-1285`）——该模式的规划路径被刻意收窄为「单 `run_code` + 直接推理」。
- **内核 P 环继承**：plan-mode（`exit_plan_mode` 提交计划）、goal/goal-round-driver（持久目标滚动）、workflow（JS 编排）、ralph、jobs、schedule。

**控制论映射**：KT-ctrl-042（多层递阶控制，主 Agent 编排 + 7 具名 worker + 全局控制面）/ KT-ctrl-044（MPC 滚动时域，goal-round 续跑 + `send_message` 干预）/ KT-ctrl-043（时间尺度分离 ε，慢 plan / 快 build / worker 编队）/ KT-ctrl-046（options/SMDP，worker 即高层动作原语）。

**强弱项**：强——通用委派升级为**具名编队**（按任务性质选最贴合的 worker），全局控制面提供持续干预而非一次性委派，深度控制由 deny 而非有害的 `maxDepth: 0` 承担（含负向用例）。弱——仍是「一次切换 + 人工介入」，缺 MPC 式自动滚动重规划；编排拓扑靠 YAML 声明而非可视化约束；ptc 模式下编队被整体禁用，编队能力与模式强绑定。

**双层评分**：内核 4.5/5 + 装配层 Δ+0.5 → 综合 5.0/5（增强；已处 5.0 上限）

---

## 6. 反思 / 反馈闭环环（R 环）——R-A 载体落地，闭环已接通

**承担角色**：官方 dsh 的 R 环本已中弱（3.0，以错误重试 / 提醒 / hook steer / 目标续跑为主，缺独立误差计算）。v1.4 记「装配层没有补强它，反而暴露了一处迁移损失（反思写入链在 dsh 侧整体缺席）」。**v1.5 该结论已被推翻**：ADR-012 落地 **R-A 文件载体**（门控 6/6），反思链由「断裂」变为「**可用**」——`oc_reflection` 不再「只能分析、不能落库」，而是「分析 → 产出候选 → 主 Agent 审阅 → 落库」的显式闭环。R 环由此 3.0 → **4.0**（Δ+1.0，增强）。

**关键机制**：
- ✅ **候选 → 审阅 → 落库显式链（v1.5，ADR-012）**：`~/.dsh/reflection/candidates/`（**15 份候选**）+ `archive/`（**1 份**）→ 主 Agent 审阅 → 落库到 `~/.dsh/MEMORY.md`（**14 个 `§` 段 / 10815 B / 57 行 / 14 条 `[src:]` 签名**）。v1.4 记「提供 `reflection_add` / `reflection_mark` 的 `dsh-reflection` 插件已于 2026-10-10 随批次移出 → persona 的 MEMORY/reflection 段在 dsh 侧不可用」——该断链**已由载体层修复**（不再是插件工具面，而是文件载体 + skill 方法论）。
- ✅ **零和预算 + 生命周期五件 + 容量口径**：`dsh-reflection` skill 承载 —— 零和预算（新增必配平退役）、生命周期五件（准入去重 / 退役三态 / 陈旧引用机检 / Coverage-Citation 双机检 / 零和）、容量口径 `memory_capacity_check.py`。
- **写入是显式链，不是自动自省**：落库需主 Agent 审阅裁决（**非**模型自省后自动写入）——这是 R 环判「增强」而非更强的边界所在。
- **`oc_reflection` 的语义**：`cordis.patch.yml:369-386` 定义 `oc_reflection`；v1.4 记其 persona 声明「generates Memory/Skill entries」而实际「不能写记忆」= **声明与能力不一致**——v1.5 下「产出候选」已是链路的第一段（候选目录真实存在），声明与能力的落差**缩小但未归零**（worker 仍不直接落库，落库归主 Agent）。
- **内核 R 环继承（仍可用）**：`llm-retry` 错误重试与退避、`hooks` 的 `agent/turn-stopping` deny→steer 强制续跑、`repeat-tool-reminder` 同参重复提醒（只 enrich）、`goal-round-driver` 状态变化驱动的迭代。
- **局部纠偏（非闭环）**：架构门控 FAIL 回传修正≤2 轮（`cordis.patch.yml:147`）属**单点执行纠偏**，未接入跨会话反思链路。
- **迁移状态机检**：`verify_bundle` 第 19 项把「**R 环载体**」纳入迁移状态判据（E3 residue / 陈旧断言 / E7 互斥 / R 环载体），使「闭环是否真接通」成为可复算判据而非叙述。

**控制论映射**：KT-ctrl-002（负反馈闭环，hooks deny→steer = 实际 y 超限时强制校正）/ KT-ctrl-020~023（PID，仅存 P + 弱 D）。**仍缺**：KT-ctrl-021/I（积分项——无「反复犯同一错误」的**自动**跨会话累积补偿；零和预算提供了配平但非自动积分）/ KT-ctrl-004（独立算误差 e=r−y 环节仍不独立于产出方）/ KT-ctrl-025（稳态误差/超调验收）。

**强弱项**：强——**v1.5 最大的口径反转**：R-A 载体（`MEMORY.md` + 候选池 + 归档）使反思链**从断裂变为接通**，且配了零和预算 / 生命周期五件 / 容量机检，闭环有可复算判据（check 19）；内核侧 steer/retry 仍在。弱——**闭环是「显式人工审阅链」而非自动自省**：落库依赖主 Agent 裁决，无自动积分项；候选池 15 份、`MEMORY.md` 14 段（10.8 KB）体量仍小；`oc_reflection` 仍不直接落库（声明与能力的落差缩小但未归零）。

**双层评分**：内核 3.0/5 + 装配层 Δ+1.0 → 综合 4.0/5（增强；v1.4 的「持平·迁移损失」已推翻）

---

## 7. 装配层机制专章

### 7.1 bundle 结构与三模式分工

`dsh-opencode-port` 是 out-of-tree bundle，`package.json` 声明 `dsh.bundle.patch: ./cordis.patch.yml`；`cordis.patch.yml`（v1.5 为 85729 B，v1.4 为 93283 B；由 `build_bundle.py` 生成）**只 `insert` 自己的 preset 行、不修改任何 host 行**（纯净模式零变化，由 `check_dump_purity.py` 判据守护）。

| 模式 | preset id | order | 定位 | 与 standard 的差异 |
|---|---|---|---|---|
| OpenCode 迁移 · 标准 | `opencode-standard` | 11 | 日常调度 + 化用后的行为纪律 + 主根 49 skill + 7 worker | 基线（`tool-plugin-manager` 硬禁） |
| OpenCode 迁移 · 创造 | `opencode-creator` | 12 | = 标准 + 插件作者能力 | +`tool-cordis`；`tool-plugin-manager` 条件启用（`!!js "!ctx.get('profileContext')"`） |
| OpenCode 迁移 · PTC | `opencode-ptc` | 13 | = 标准 + PTC 呈现 | +`tool-presentation(mode: ptc)`；`workflow-ptc`/`tool-workflow` 双禁；工具面坍缩为单 `run_code` |

**为什么必须自带 `node_modules`**：loader 解析 patch 里插件 `name` 的锚点是**该 patch 文件所在目录**（`vendor/loader/src/config/tree.ts:122` 的 `import(name, ctx.baseUrl)`），而 `~/.dsh/presets/`、`~/.dsh/`、`~` 祖先目录都没有 `@deepseek-ai/*` —— 故用 `link_modules.py` 建 28 个符号链接（`verify_bundle.py` 第 10 项断言 28/28 齐备）。**这正是「不可移植」的根因**。

### 7.2 persona 遮蔽（shadow）关系

`persona.md`（15 节 / **6524 字符 / 12066 B**，v1.4 为 8018 字符 / 15403 B）是 persona 正文的**唯一手写来源**，由 `build_bundle.py` 逐字展开进三个 preset 的 `persona.prefix`（`cordis.patch.yml:16-179` / `:446-609` / `:877-1040`），`verify_bundle.py` 第 3 项断言三份与 `persona.md` **逐字符一致**。

它与宿主 `~/.dsh/profiles/web/cordis.patch.yml:11-65` 的 `system-prompt.personaPrefix`（2790 字符 / 8 小节）构成**遮蔽（shadow）关系**：同名 section 被 preset 侧覆盖，宿主那份成为**死配置**——由 `verify_persona_scope.py`（check 13 / A12）取证三条命题：① preset 侧承载（逐字符一致）② host 侧从未生效（七段纪律正文与 persona.md 不重叠）③ 运行时作用域（三会话系统提示取证），并含 5/5 负向用例。

**控制论意义**：这是「双层设定值」的典型冲突处置——两套 persona 若同时生效会产生两套阈值（persona 开篇即写「重复会造成两套阈值，反而误导」），遮蔽机制把设定值收敛为单一来源。

### 7.3 skill 面：49 主根 / 46 可见 / 6 叠加

**v1.5 起采用契约 §2.6 的 skill 计数唯一口径**（⛔ 不再使用「45 件派生 skill」这一旧说法）：

| 口径 | 定义 | **v1.5** | v1.4 |
|---|---|---:|---:|
| **主根** | `<root>/<name>/SKILL.md` 一层扫描（深度 2） | **49** | 45 |
| 派生件 | 主根中有 opencode 源者 | **47** | 45 |
| DSH 原生 | 主根中无 opencode 源者（`dsh-config` / `dsh-reflection`） | **2** | 0 |
| **模型可见** | 主根 − 带 `disable-model-invocation: true` 者（3 件） | **46** | 42 |
| 叠加层 | `_overlay/<name>/SKILL.md`，**不计入主根** | **6** | 6 |

**换算**：主根 = 派生 + DSH 原生（49 = 47 + 2）；模型可见 = 主根 − 3（46 = 49 − 3）。源侧目录数含 `_shared` / `disabled` 两个**非技能目录**（故源侧目录数 ≠ 主根数）。

| 口径 | 数量 | 说明 |
|---|---|---|
| 主根 | **49** 件 | `~/.dsh/skills/opencode/` 一层扫描；`reconcile.py` 的断言对象是**派生件 47**（逐字节一致），**不是主根 49** —— 差额 2 件 `dsh-config` / `dsh-reflection` 为 DSH 原生（无 opencode 源可比对，故不入 reconcile 断言面） |
| **模型可见** | **46** | 49 − 3 件带 `disable-model-invocation: true`（opencode-config / opencode-capability-audit / opencode-capability-extension） |
| `_overlay/` | 6 件 | openspec 系叠加层（openspec-explore/sync-specs/archive-change/bulk-archive-change/onboard/release-openspec），**不计入主根** |
| 运行时目录 | 46（三模式均同） | 内置 `standard` 为 **0** —— 技能面完全由装配层提供 |
| 惰性键 | 18 件带 `allowed-tools` | 13 件 openspec 系 + 5 件非 openspec 系；两侧**均不生效**（惰性键），不得据此推断工具受限 |

`customSkillDirs` 是**追加**而非替换（`includeDefaultRoots` 默认 `true`），故新模式目录 = 49 主根 skill **+ 会话 cwd 项目根/用户根自带 skill**（cwd 在 DSH 仓库内时还有 `.agents/skills` 的 16 件）——「49 件」指主根本身，不是新模式会话的目录总数（README §8.2 用户裁决：有意保留）。

**v1.5 的两件新增 skill 均为 DSH 原生**（`dsh-config` / `dsh-reflection`），属装配层自建能力包而非 opencode 派生——这正是「主根 45→49 而派生仅 45→47」的差额来源。

### 7.4 7 worker 编队与工具别名

| opencode agent | dsh toolName | toolFilter 形态 |
|---|---|---|
| `general` | `subagent` | deny `todo_write`/`ask_user_question`/schedule 组 |
| `explore` | `oc_explore` | allow `read`/`glob`/`grep`/`skill` |
| `architect-worker` | `oc_architect` | deny shell/`todo_write`/`ask_user_question` |
| `requirement-discovery-worker` | `oc_requirement` | 同上 |
| `search-worker` | `oc_search` | allow `read`/`glob`/`grep`/`web_search`/`web_fetch`/`skill` |
| `reflection-worker` | `oc_reflection` | deny shell/`ask_user_question` |
| `pdf-worker` | `oc_pdf` | deny shell/`todo_write`/`ask_user_question` |

**两条设计约束**：① **平台互斥的 shell deny** 必须用 `!!js process.platform === 'win32' ? 'pwsh' : 'bash'` 取**字符串**——写成数组会因 loader 的 `interpolate` 对序列只求一个值（`value.map`）而产生嵌套数组，违反 `z.array(z.string())`，使整个 preset 报 `broken`（这正是 2026-10-11 GUI「预设加载失败」的根因，README §10）。② **`deny` 里不能出现 `subagent`**——`restrictableNames` 只装继承来的全局工具（`packages/core/tools/src/index.ts:1201-1203`），scope 自己注册的 `subagent` 不可被 restrict 命名，写了会让整条 toolFilter 抛错、委派直接起不来。

### 7.5 门控、漂移判据与回滚

- **20 项静态门控（v1.5；v1.4 为 13 项）**：`verify_bundle.py`（结构 / persona 一致性 / 禁用字面量 / 插件可解析 / toolFilter 求值 / worker 编队（含负向用例）/ 三模式差异 / 子行 Config schema（`verify_rows.mjs`，43 行）/ node_modules 锚点 / 源指纹 / 生成幂等 / A12 作用域取证）。**当前 20 项 PASS**（`1011-全面适配性迁移分析/evidence/r11-final-gates.out.txt`）。
- **v1.5 新增的 7 项判据（14–20）**：**14** 门控执行通道 `run_gate`（结构 P1–P5 + 行为负向）/ **15** 真实挂载审计（真 `runProfile` + 真 Loader + 负向控制）/ **16** 工具 `output.schema` 子集校验 / **17** 会话 PATH 引导（外部 CLI 可达性）/ **18** `dsh-config` 声明账本漂移（源指针 / 层归属 / 层间冲突 / 台账一致性）/ **19** 迁移状态（E3 residue / 陈旧断言 / E7 互斥 / **R 环载体**）+ 判据自检 / **20** 命令注册插件（E10：`/arch` `/rd` `/reflection`；含注册单测）。
- **判据数演进**：13（v1.4）→ 19（10-12 15:46，`verify_bundle.py.bak-dshconfig-20261012-154654`）→ **20**（10-13 03:38，R11 收官，+命令注册插件 E10）。
- **第 11 项的教训（判据脆性）**：曾 FAIL，根因不是真漂移，而是宿主 patch 是**活文件**（GUI 写回 `ui-theme.fontSize` 导致整文件 sha256 漂移的**假阳性**）。修法＝`scoped_digest` 只对 bundle 实际消费字段（`system-prompt.personaPrefix`）判漂移，整文件变化但被消费字段未变时输出 note「不算漂移，这是活文件的预期形态」。**这条教训本身就是 `criterion-design-validation` 的现场应用**：假阳性会训练人忽略红灯，最终放过真漂移。
- **结论生成化**：README §8 状态表改由 `gen_status_table.py` **从门控输出派生**（来源分级：可复算 / 复算至产物 / 未复算必须显示 ⚠️），消除「结论手写、判据是脚本」的口径漂移源。
- **回滚**：`~/.dsh-backups/opencode-port-20261011/`（含 `cordis.patch.yml` / `package.json` / `cordis.yml`）；顺序为**先 `remove_bundle` 后还原 patch**（还原后 `plugin_manager` 会再次 ENOENT，因备份 patch 早于 `pnpmCommand` 覆盖）。2026-10-11 实测演练一轮：卸载后既有 4 个 preset 区域与安装前基线**逐字节一致**，重装后组合树与首次安装后**逐字节一致**。
- **pnpm 环境修复**：web 服务由 systemd 启动，PATH 不含 nvm 的 node/pnpm，corepack shim 的 `#!/usr/bin/env node` 会 ENOENT（`install_bundle` 实测 exit 127）→ 修法两处：`~/.dsh/bin/pnpm` 包装脚本 + profile patch 覆盖 `plugin-manager.pnpmCommand`（`cordis.patch.yml:266-274`）。

### 7.6 评分未跃升的原因（档位未跨）

装配层带来的是**能力迁移**而非**产品档位跃迁**，故 v1.5 下 8 维**仅 memory 一维提升（4→5）**，档位仍为「成品化受限」，**未跨档**：

- **多Agent编排 / 工作流** 仍处 4 档：7 worker + 编队 + 三层触发规则增强了编排与流程纪律，v1.5 另加 `gate-runner` 顶层行与命令注册（`/arch` `/rd` `/reflection`），但未引入真 DAG 画布或通用可视化工作流引擎，5 档门槛（市场级/画布级）未达。
- **P 环** 已处 5.0 上限，编队加入无可升空间；**T 环** 5.0 封顶，「收口 + `run_gate` 窄通道」不改变分值。
- **E 环** 增量仍是架构/需求两域单点门控；v1.5 的 `run_gate` 消解了「门控不能自跑」这一抑制项，故 **3.5 → 4.0（达反转阈值）**，但覆盖未扩展到通用 Critic，故不取 4.5+。
- **M / R 环** v1.5 各有实质增量：M 4.0 → **4.5**（R-A 载体），R 3.0 → **4.0**（反思链由断裂变可用）。
- **skill 维维持 4**：主根 45 → 49、模型可见 42 → 46，但档位判据是「是否有市场/分发」（未达 5 档），**数量增长不改变档位**。
- **封顶因素未变**：一键部署=不可移植的手动 bundle（3 档）、MCP=宿主 0 配置（3 档）。⚠️ **v1.5 已删除「沙箱=本机无可用后端故 fail-closed」这一封顶因素**——该断言已证伪（环境事实更正，⛔ 非装配层收益，沙箱维仍 4/4）。

### 7.7 v1.4 快照点 → v1.5 冻结点之间的装配层轮次表

**冻结点**：`2026-10-13T05:04:50+08:00`；**v1.4 快照点**：`2026-10-11T17:09:09+08:00`。下表逐轮登记两时点之间装配层的**全部可回溯变化**（R1–R12），是「13 项判据 → 20 项」「45 主根 → 49 主根」「R 环断裂 → 接通」等结论的轮次级凭据。

| R# | 时点 | 变化 | 证据指针 |
|:--:|---|---|---|
| R1 | 10-11 17:16–17:20 | 思考档 `reasoningEfforts` + 子 Agent 能力上限 | bundle `.bak-thinking-subagentcap-20261011-171649`、`.bak-subagentcap-20261011-172007` |
| R2 | 10-11 18:07 | **E 环门控执行通道 `run_gate`（ADR-010）** | `.bak-gatechannel-20261011-180758`；ADR-010 |
| R3 | 10-11 19:46–19:48 | 重挂 `dsh-wsl-desktop-path`（web + headless），修 explorer.exe ENOENT | `.bak-wslpath-20261011-194630` / `-194846` |
| R4 | 10-12 08:32–08:41 | **`dsh-config` skill v1.0（ADR-011）**；机器事实外迁 `local/host-env-facts.md`；服务重启 08:41:06 | ADR-011 |
| R5 | 10-12 09:31Z | **R 环 R-A 文件载体（ADR-012）** | ADR-012；`~/.dsh/reflection/`、`~/.dsh/MEMORY.md` |
| R6 | 10-12 15:46–15:50 | **`verify_bundle` 13 → 19 项**；persona 收敛（字符 9034 → 6524） | `verify_bundle.py.bak-dshconfig-20261012-154654`、`persona.md.bak-dshconfig-20261012-155059` |
| R7 | 10-12 16:07 | 模型路由：`maxTokens` 8192→32768、`reasoningEffort` max→high、`v4-flash` 16384→32768 | `Mission-file/2026-10/1012-dsh长输出截断根因诊断/` |
| R8 | 10-12 17:16 | R09 收尾：`install.py` 变换表、`_overlay/pdf-ocr` scripts、`run_gate` 负向 18→30 | `install.py.bak-r09-20261012-171611` |
| R9 | 10-12 17:40–18:11 | E3 residue **119 → 0**；R-A 落库取证；E6 PDF/OCR；E9；审查接 check 19 | 迁移线 `evidence/r09-*.out.txt`、`执行E3E4-report.md` |
| R10 | 10-12 18:55–19:13 | 行为验收收尾（5 条请求逐条会话） | `evidence/r10-behavioral.out.txt`、`迁移台账.yaml` 19:13 |
| R11 | 10-13 02:37–03:38 | caps 台账统一 + 审查脚本与唯一源单口径控制；**判据 19 → 20**（+命令注册插件 E10） | `evidence/r11-caps-ledger.out.txt`、`r11-audit-unify.out.txt`、`r11-final-gates.out.txt` |
| R12 | 10-13 03:30 起 | 收官轮（重启后验收与残余收口）；用户已完成服务重启 05:02 | `12-接续prompt-重启后验收与残余收口.md` |

**轮次表的读法**：R1/R3/R7 是**参数与环境治理**（不改档位）；R2/R4/R5/R6 是**机制新增**（`run_gate` 通道、`dsh-config` 能力包、R-A 载体、判据扩容）——这正是 v1.5 触发复评的「能力纵深增长 / 机制新增」判据来源；R8–R12 是**收尾与单口径控制**（负向用例扩容、residue 清零、判据 19→20）。⚠️ 表中「判据 13 → 19」（R6）与「19 → 20」（R11）**不是矛盾**：R6 是 `dsh-config` 轮的一次性扩容，R11 再补第 20 项（命令注册插件 E10）。

### 7.8 外部证据指针（只登记，⛔ 不复制正文）

| 指针 | 路径 | 状态 |
|---|---|---|
| ADR-010 | `Mission-file/2026-10/1011-迁移适配-E环门控通道与R环纠正/arch/ADR-010.json` | `proposed` |
| ADR-011 | `Mission-file/2026-10/1011-deepseek harness-提示词迁移工程-从opencode/1011-全面适配性迁移分析/arch/ADR-011.json` | `proposed`（门控 6/6） |
| ADR-012 | 同 ADR-011 目录 | `proposed`（门控 6/6） |
| 迁移台账 | 同 ADR-011 目录 `迁移台账.yaml` | 43 任务：done 36 / partial 2 / not_done 3 / deferred 1 |
| 收官取证 | 同目录 `evidence/r11-final-gates.out.txt`、`r11-migration-audit.json`、`迁移完成度审查报告-v10.md` | — |

⚠️ **同名消歧**：`0928-前端设计方法论建设` 线存在**同名 ADR-011**（不同域）⇒ 本画像对 ADR 的引用**一律带路径限定**，不得裸引「ADR-011」。

## 八大核心环强弱总评

**v1.5 装配层六环值**：SP **5.0** / M **4.5** / P **5.0** / R **4.0** / T **5.0** / E **4.0**（官方 → 装配层：SP 4.5→5.0、M 4.0→4.5、P 4.5→5.0、R 3.0→4.0、T 5.0→5.0、E 2.0→4.0）。按强度重排：**T = P = SP（5.0，封顶）＞ M（4.5）＞ R = E（4.0，并列最弱）**。

| 环 | 承担角色 | 强度 | 主控概念 |
|---|---------|:---:|---------|
| **设定值** | persona 15 节 + plan-mode 逐题访谈 + 三层触发规则 + 委派契约 + 命令注册（`/arch` `/rd` `/reflection`） | 最强（5.0；Δ+0.5 增强，已封顶） | KT-ctrl-045 规划-执行解耦 |
| **E 评估** | `oc_architect`+`gate_architecture.py` / `oc_requirement` 定档 / `oc_search` 证据包 / 信源分级 / **`run_gate` 门控通道** | 中（**4.0；Δ+2.0 反转**；门控已可自跑，但独立 critic 未分离） | KT-ctrl-035 扰动观测器 |
| **T 执行** | permission 5 档（defaultPreset=`opencode-plan`）+ 工具面收敛（37/40/1）+ worker 最小授权 + `run_gate` 窄通道 | 最强（5.0；Δ0 持平，已封顶） | KT-ctrl-034 限幅/看门狗 |
| **M 记忆** | 内核事件溯源 + 投影 + compaction + **R-A 载体**（`~/.dsh/MEMORY.md` 14 段 / 候选池 15 份 / 归档 1 份） | 次强（**4.5；Δ+0.5 增强**） | KT-ctrl-011 卡尔曼式滤波 |
| **P 规划** | plan/goal 双速 + 7 具名 worker + 全局控制面 + 深度 deny | 最强（5.0；Δ+0.5 增强，已封顶） | KT-ctrl-042/044 递阶 + MPC |
| **R 反思** | 内核 steer/retry + **R-A 载体：候选 → 主 Agent 审阅 → 落库**（零和预算 / 生命周期五件 / 容量口径） | 中（**4.0；Δ+1.0 增强**，闭环已接通；写入为显式链非自动自省） | KT-ctrl-002 负反馈闭环（已接通） |

⚠️ **最弱环结论**：**最弱环为 R 与 E 并列 4.0，不再存在单一最弱环**——v1.4 的「最弱环由 E 转移到 R」**已被推翻**（E 由 3.5 升至 4.0、R 由 3.0 升至 4.0，两者并列）。

## dsh-custom 控制论画像总结

**整体范式：在官方 dsh 的强执行器/强规划内核之上，把 opencode 的行为纪律、skill 库与角色编队整体搬进 preset 声明层，并在 v1.5 用「`run_gate` 门控通道 + R-A 记忆载体 + `dsh-config` 能力包」把 v1.4 的两处掉队追平——SP/P/T 三环处 5.0 上限，E 环达反转（+2.0），M 环 4.5，R 环由「断裂」变为「接通」（4.0），形成「内核继承 + 装配层迁移 + 迁移损失二次追平」的装配控制器。**

- **最突出的环：T 环（执行器安全）与 P 环（具名编队）、SP 环（设定值）**——三者均处 5.0 上限：T 环在官方三瀑布 + 看门狗之上叠加 5 档 permission 与 worker 级最小授权，v1.5 另加 `run_gate` 窄通道（窄参数面 + 30 条负向用例）；P 环把通用委派升级为 7 具名 worker + 全局控制面（`send_message`/`interrupt_agent`/`list_agents`），并以 `toolFilter.deny`（而非有害的 `maxDepth: 0`）承担「不可再委派」；SP 环以 persona 15 节 + 命令注册（`/arch` `/rd` `/reflection`）把设定值入口显式化。
- **最弱环：R 与 E 并列 4.0**——⚠️ v1.4 的「最弱环转移到 R」**已被推翻**：官方最弱环 E（2.0）经领域级门控 + **`run_gate` 执行通道**升到 **4.0（Δ+2.0，反转）**；R 经 **R-A 载体**由 3.0 升到 **4.0（Δ+1.0）**——**不再存在单一最弱环**。与 `opencode-custom`（E/R 双反转）的对照结论也随之修正：**同一装配层迁移到 dsh，v1.5 下 E 与 R 亦双双达反转/增强**。
- **关键增强：SP / M / P / R 四环（Δ+0.5 / +0.5 / +0.5 / +1.0）**——persona 15 节把 GATE/COMPLEXITY 自评、契约驱动委派、留档 5 段模板固化到 preset 层（设定值纪律从「提示词约定」变成「preset 声明」，模式切换即生效）；R-A 载体使 M 环从「只读单向通道」变为**可写闭环**。
- **关键反转：E 环（Δ+2.0）**——迁入架构门控（`gate_architecture.py` ADR schema）、需求分层定档、`oc_search` 证据包与信源分级；v1.5 的 `run_gate` 窄通道（ADR-010）为产出方**恢复了门控脚本执行能力**，消解 v1.4 的抑制项「门控脚本依赖 bash 而子 Agent 无 bash」⇒ **达反转阈值**。仍为领域级覆盖（架构 / 需求两域），且独立 critic 未分离，故不取 4.5+。
- **关键追平：R 环（Δ+1.0，由迁移损失变为已接通）**——ADR-012 落地 R-A 文件载体：`~/.dsh/MEMORY.md`（14 段 / 10815 B / 14 条 `[src:]`）+ `~/.dsh/reflection/candidates/` 15 份候选 + `archive/` 1 份 + `dsh-reflection` skill（零和预算 / 生命周期五件 / 容量口径）。v1.4 的「反思写入链断裂、`oc_reflection` 能分析不能落库」**已推翻**；写入链是**显式链（候选 → 主 Agent 审阅 → 落库），非自动自省**。
- **双层遮蔽的设定值治理**：preset persona（**12066 B / 6524 字符**，v1.4 为 15403 B / 8018 字符）遮蔽宿主 `personaPrefix`（2790 字符），后者成为死配置——由 A12 三条命题 + 5/5 负向用例取证；代价是每次请求的 persona 税，且 PTC 模式下 persona §二 的工具清单成为**空指向**。
- **精装度 3.6 → 3.9（Δ+0.3）**——8 维中 **memory 一维提升（4→5，权重 10% ⇒ +0.10）**，skill 维维持 4（主根 45→49、模型可见 42→46，档位未变），其余六维与官方同值；**口径诚实**：v1.3 前的单点分 2.5 与本轮 8 维分不同源、不可相减；档位仍「成品化受限」，**未跨档**。封顶主因是不可移植的手动 bundle 与宿主 0 MCP 配置。⚠️ **沙箱维分值未变（4/4）**——v1.4 的「本机无沙箱后端」断言已证伪，但那是**环境事实更正、非装配层收益**。

**一句话画像**：dsh-custom 是**「以官方 dsh v0.2.1-alpha.2 内核为底座、以 3 preset / 7 具名 worker / 主根 49 skill（模型可见 46）/ 5 档 permission（defaultPreset=opencode-plan）/ 20 项门控装配，把 opencode 的行为纪律与角色编队搬进 preset 声明层，并在 v1.5 用 `run_gate` 窄通道与 R-A 记忆载体把 E/R 两环的掉队二次追平的个人变体」**——它没有改一行引擎源码，却同时暴露并处置了迁移工程的两个真问题：**门控脚本依赖子 Agent 拿不到的工具（E 环判据与执行面错配 → 已由 `run_gate` 消解）**，以及**判据对着活文件判漂移会产出假阳性（第 11 项 FAIL 的根因 → 已改为 `scoped_digest`）**。

---

### 📚 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S4 | 一手配置观察 | `~/.dsh/presets/opencode/cordis.patch.yml`（v1.5 为 85729 B / v1.4 为 93283 B：3 preset / persona 三份 / delegation 12 子行 / permission 相关行 / 各 preset 顶层 `gate-runner` 行）——**官方 dsh 3.6 / 装配层 3.9** 的配置侧凭据 | 高 |
| SRC-002 | S4 | 一手配置观察 | `~/.dsh/presets/opencode/persona.md`（15 节 / **12066 B / 6524 字符**，v1.4 为 15403 B / 8018 字符；persona 正文唯一手写来源） | 高 |
| SRC-003 | S4 | 一手配置观察 | `~/.dsh/profiles/web/cordis.patch.yml`（25704 B，v1.4 为 17538 B；宿主增量：personaPrefix 2790 字符 / 4 provider / permission 5 档且 `defaultPreset: opencode-plan` / plugin-manager pnpmCommand） | 高 |
| SRC-004 | S4 | 一手门控产物 | `~/.dsh/presets/opencode/verify_bundle.py`（**20 项判据本体**，v1.4 为 13 项；含 check 7 负向用例、check 11 源指纹、check 14 `run_gate` 通道、check 19 迁移状态含 R 环载体、check 20 命令注册插件） | 高 |
| SRC-005 | S4 | 一手机检产物 | `Mission-file/2026-10/1011-…-从opencode/1011-全面适配性迁移分析/evidence/r11-final-gates.out.txt`（**20 项 PASS**；persona.md = 12066 B；plugins 数；28 包链接；源指纹） | 高 |
| SRC-006 | S4 | 一手 bundle 文档 | `~/.dsh/presets/opencode/README.md`（42488 B，v1.4 为 22168 B；§2 plugin_manager 更正记录 / §2.1 不可移植 / §4 十项损失 + §4.2 `run_gate` 门控通道 / §5 权限 5 档 / §6 worker 编队 / §7 回滚 / §8 生成式验收状态（**20/20 项**）/ §8.2 技能目录口径 / §10 预设加载失败根因） | 高 |
| SRC-007 | S4 | 一手 bundle 文档 | `~/.dsh/presets/opencode/ADAPTATION-NOTES.md`（11389 B，v1.4 为 9108 B；第 3 层机制处置逐条表；第 14 行 `allowed-tools` 惰性键 13 件 vs 实测 18 件；`run_gate` 越权防护强度未自证 + 负例扩容记录） | 高 |
| SRC-008 | S4 | 一手技能面盘点 | `~/.dsh/skills/opencode/`（**主根 49 = 派生 47 + DSH 原生 2**（`dsh-config` / `dsh-reflection`）+ `_overlay/` 6 件 openspec 系叠加；**模型可见 46**；3 件 `disable-model-invocation: true`；18 件带 `allowed-tools`；源侧含 `_shared`/`disabled` 两个非技能目录） | 高 |
| SRC-009 | S4 | 一手能力包观察 | `~/.dsh/skills/opencode/architecture-judgment/`（`_private/gate_architecture.py` + `schemas/adr.schema.json` + `routing.md`）、`requirement-discovery/_private/local-bindings.json`（`TIER_TOOL` 绑定）、`dsh-config/`、`dsh-reflection/`（零和预算 / 生命周期五件 / `memory_capacity_check.py` 容量口径） | 高 |
| SRC-010 | S4 | 一手工程报告 | `Mission-file/2026-10/1011-…-从opencode/report.md`（A1–A14 验收表：插件 188→191；工具面 37/40/1） | 高 |
| SRC-011 | S1 | 可复算评分 | `09-src-data/dsh_custom_scores.py`（**官方 3.6 / 装配层 3.9**，8 维（skill 4 / memory 5）与五环双层分值（SP 5.0 / M 4.5 / P 5.0 / R 4.0 / T 5.0 / E 4.0）单一数据源；含 2.5 旧单点分不同源与沙箱证据文本更正两条口径披露） | 高 |
| SRC-012 | S1 | 评分模型 | `07-checkpoint/premium-scoring-model.md`（精装度 v2.0：硬门槛 + 8 维加权 + 一票否决；§3.2 记忆列 5 档 =「跨 session 知识库 + 长期记忆 + 结构化状态」） | 高 |
| SRC-013 | S4 | 对照基线 | `03-cases/deepseek-harness.md`（官方 dsh 内核五环结构与结论口径） | 高 |
| SRC-014 | S4 | 对照写法 | `03-cases/opencode-custom.md`、`03-cases/opencode-custom-diff.md`（同名栈在 opencode 侧「可自跑门控 → 判反转」的对照口径） | 高 |
| SRC-015 | S1 | 框架契约 | `02-framework/framework.md`、`00-contract/contract.md`（五环定义与信源分级规范；**§2.6 skill 计数唯一口径**、§2.7 复评触发与快照/脱敏边界） | 高 |
| SRC-016 | S4 | **本库脱敏快照（入库，可离线复核）** | `07-checkpoint/dsh-custom-snapshot/`（由 `07-checkpoint/snapshot_dsh_custom.py` 采集，**`collected_at = 2026-10-13T05:09:43+08:00`**；旧 v1.4 快照归档于 `archive/1011-KB-v1.4-dsh装配与opencode追平/dsh-custom-snapshot-v1.4/`）——含 `bundle__cordis.patch.yml` / `bundle__persona.md` / `profile__web-cordis.patch.yml` / `inventory.json` / `manifest.json`；`.env`、credentials、sessions 一律不采集 | 高 |
| SRC-017 | S4 | 一手快照·**skill 口径段** | `07-checkpoint/dsh-custom-snapshot/inventory.json` → `skills` + `skills_list`（`main_root` 49 / `derived` 47 / `dsh_native` 2 / `model_visible_estimate` 46 / `overlay` 6 / `skill_md_total` 55 / `source_skill_dirs` 47 / `non_skill_dirs_excluded` = `_shared`、`disabled`；契约 §2.6 五口径的机器可读落点） | 高 |
| SRC-018 | S4 | 一手快照·**插件段** | 同上 `inventory.json` → `plugins`（bundle `presets/opencode/plugins/` = `dsh-opencode-commands`（注册 `/arch` `/rd` `/reflection`）+ `dsh-opencode-gate-runner`；宿主 `~/.dsh/plugins/` = `dsh-wsl-desktop-path`） | 高 |
| SRC-019 | S4 | 一手快照·**reflection 段** | 同上 `inventory.json` → `reflection`（`reflection_dir` 存在；`candidates` 15 / `archive` 1；`MEMORY.md` = 10815 B / 57 行 / 14 `§` 段 / 14 条 `[src:]` 签名；`dsh_reflection_skill: true`）——⚠️ 只记存在性与容量，**MEMORY.md 正文不入快照、不入公开库**（契约 §2.7③） | 高 |
| SRC-020 | S4 | 一手快照·**gate 段** | 同上 `inventory.json` → `gate`（`check_count` 20 与 20 项名称全表：1–13 为 v1.4 存量，14 `run_gate` 门控执行通道 / 15 真实挂载审计 / 16 工具 `output.schema` 子集校验 / 17 会话 PATH 引导 / 18 `dsh-config` 声明账本漂移 / 19 迁移状态（E3 residue / 陈旧断言 / E7 互斥 / R 环载体）/ 20 命令注册插件 E10） | 高 |
| SRC-021 | S4 | 一手外部决策指针 | ADR-010 `Mission-file/2026-10/1011-迁移适配-E环门控通道与R环纠正/arch/ADR-010.json`（`proposed`）；ADR-011 / ADR-012 `Mission-file/2026-10/1011-deepseek harness-提示词迁移工程-从opencode/1011-全面适配性迁移分析/arch/`（均 `proposed`，门控 6/6）；迁移台账同目录 `迁移台账.yaml`（43 任务：done 36 / partial 2 / not_done 3 / deferred 1）；收官取证同目录 `evidence/r11-final-gates.out.txt`、`r11-migration-audit.json`、`迁移完成度审查报告-v10.md`。⚠️ `0928-前端设计方法论建设` 线有**同名 ADR-011**（不同域）⇒ 引用一律带路径限定 | 高 |

---

<details>
<summary><b>📦 历史块 · v1.4 口径（2026-10-11T17:09:09+08:00 快照点；⛔ 已被 v1.5 取代，仅作口径对账保留）</b></summary>

> ⚠️ 以下为 **v1.4 时点读数**，⛔ **不得当作当前实况引用**。保留目的是让「口径变更」可逐条对账（`dsh_custom_scores.py` 的 `HISTORY["v1.4"]` 与旧快照 `archive/1011-KB-v1.4-dsh装配与opencode追平/dsh-custom-snapshot-v1.4/` 为凭据）。

| 项 | v1.4 值 |
|---|---|
| 精装度（装配层） | **3.8**（raw 3.75） |
| 精装度（官方 dsh） | 3.6（raw 3.63） |
| Δ（装配层 − 官方） | **+0.2** |
| 档位 | 成品化受限 |
| 8 维（官方 / 装配层） | multi 4/4 · deploy 3/3 · model 4/4 · workflow 4/4 · **skill 3/4** · sandbox 4/4 · mcp 3/3 · **memory 4/4** |
| 五环（官方 → 装配层） | SP 4.5 → 5.0（+0.5 增强）· **M 4.0 → 4.0（0 持平）** · P 4.5 → 5.0（+0.5 增强）· **R 3.0 → 3.0（0 持平·迁移损失）** · T 5.0 → 5.0（0 持平·已封顶）· **E 2.0 → 3.5（+1.5 增强，非反转）** |
| 最弱环 | **R 单一最弱（3.0）**；旧结论「最弱环由 E 转移到 R」（⛔ v1.5 已推翻：R 与 E 并列 4.0） |
| skill 计数 | **45 派生 / 42 可见 / 6 叠加**（主根口径 45 = 派生 45 + DSH 原生 0） |
| `_overlay` | 6 件（v1.5 未变） |
| `verify_bundle` 判据数 | **13 项**（`evidence/verify-bundle-13checks.out.txt`；第 11 项曾 FAIL，根因为活文件假阳性） |
| profile patch 字节 | 17538 B（v1.5 为 25704 B） |
| persona 字节 / 字符 | 15403 B / 8018 字符（15 节；v1.5 为 12066 B / 6524 字符） |
| bundle README 字节 | 22168 B（v1.5 为 42488 B） |
| ADAPTATION-NOTES 字节 | 9108 B（v1.5 为 11389 B） |
| bundle `cordis.patch.yml` | 93283 B（1305 行 / 70672 字符；v1.5 为 85729 B） |
| `defaultPreset` | `read-only`（v1.5 改为 `opencode-plan`） |
| 沙箱事实（**已被证伪**） | 记「本机无可用沙箱后端（bubblewrap/Landlock 均不可用）→ read-only/workspace-write 一律 fail-closed、唯一可跑档 `danger-full-access`」——⛔ v1.5 已证伪（bwrap 已装、链选中 bwrap、`enforcement=full`）；此为**环境事实更正**，沙箱维 v1.4 与 v1.5 均记 4/4 |
| R 环旧结论（**已被推翻**） | 「反思写入链断裂：提供 `reflection_add`/`reflection_mark` 的 `dsh-reflection` 插件 2026-10-10 移出，`oc_reflection` 能分析不能落库，闭环未接通」——⛔ v1.5 已由 R-A 载体（ADR-012）推翻 |
| E 环旧抑制项（**已消解**） | 「门控脚本依赖 `bash` 而 dsh 子 Agent 无 `bash` 工具 ⇒ 门控无法在子 Agent 内自跑」——⛔ v1.5 已由 `run_gate` 窄通道（ADR-010）消解 |
| M 环旧结论（**已被推翻**） | 「装配层未新增跨会话记忆；记忆只读不可写，MEMORY 段是读得到写不进」——⛔ v1.5 已由 R-A 载体推翻 |

</details>
