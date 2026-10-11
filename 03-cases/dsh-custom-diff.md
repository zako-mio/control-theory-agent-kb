# dsh 官方 vs dsh-custom 装配层 — 对照分析

> 一句话定位：本文件以官方 dsh v0.2.1-alpha.2「默认内核 + 内置 standard 模式 + 零 MCP」为基线，逐类拆解 `dsh-opencode-port` 装配层的 10 类改动及其对 SP/M/P/R/T/E 六环的双层增量，量化精装度 3.6 → 3.8（Δ+0.2）的来源，并单列口径披露以免把「首次回填模型分」误读为跃升。
>
> 版本：v1.0（2026-10-11）。**本轮首次**把 dsh 纳入精装度 v2.0 模型（硬门槛 + 8 维加权 + 一票否决）；官方 3.6 / 装配层 3.8，均过端到端硬门槛、无一票否决。分值唯一来源：`09-src-data/dsh_custom_scores.py`（`SCORES` / `RING_SCORES` / `WEIGHTS`），本文件不自行改分。与 `03-cases/deepseek-harness.md`（官方画像，本轮升 0.2.1-alpha.2）口径一致。

## 1. 基线定义

**基线 = 官方 dsh v0.2.1-alpha.2（2026-10-09，commit `d743267`）默认装配 + 内置 standard 模式**，仅含：

- **官方内核**：cordis 插件装配架构（`bundle/base/cordis.patch.yml`）+ 内置 preset 族（standard / ptc / minimal / cordis）+ 内置 `standard` 工具面 **31** 个工具。
- **官方 P/M/T 机制**：plan-mode（`exit_plan_mode` + plan:policy 段，section 2358 字符）、goal + goal-round-driver、subagent（6 个 provider 后端：spawn/fork/acp/codex/claude-code/dsh-sdk）+ fork + workflow + ralph、事件溯源 session + projection + token-meter + compaction 三插件 + session-format v4 + session-query/FTS5。
- **官方 T 安全面**：tools 三瀑布 + timeout-policy + sandbox 后端族（bwrap/Landlock/Seatbelt/win32 ACL/sandbox-ssh）+ spill + approval + permission presets **3 档**（read-only / workspace-write / danger-full-access，default read-only）。
- **官方模型面**：DeepSeek 直连 + llm-pi-ai 第三方目录 + 自定义 OpenAI Chat/Responses/Anthropic 三协议。
- **明确不含**：自定义 preset / persona 覆盖层 / 派生 skill 库 / 专职 worker 编队 / MCP 配置 / 跨会话学习型长期记忆。
- **版本跨度**：tag 全集跨 `0.1.2-alpha.1 … 0.2.1-alpha.2` 共 **21 个预发布**（本轮基线为其中最新者）。

**装配侧 = `dsh-opencode-port` bundle**（`~/.dsh/presets/opencode/`，包版本 0.1.0）**+ 宿主 profile patch 增量**（`~/.dsh/profiles/web/cordis.patch.yml`）。来源工程：`/home/zako-mio/opencode/archive/Mission-file/2026-10/1011-deepseek harness-提示词迁移工程-从opencode/`。

## 2. 改造清单（10 类）

| # | 类别 | 改造内容 | 证据 | 对环影响 |
|---|------|---------|------|---------|
| 1 | **preset 编队层** | 新增 3 preset：`opencode-standard`(order 11) / `opencode-creator`(12) / `opencode-ptc`(13)；顶层插件行 **21/22/22**、递归展开子行 **34/35/35** | `~/.dsh/presets/opencode/cordis.patch.yml`；`evidence/verify-bundle-13checks.out.txt`（check 2）；`plugin-preset-rows.txt` | SP 主 + P | SP：三档设定值固化；P：模式即编队 |
| 2 | **persona 层** | 15 节 / **8018 字符**（≈3084 tokens）persona 逐字符进三 preset 的 `@deepseek-ai/dsh-persona` 行；**遮蔽**宿主 `system-prompt.personaPrefix`（**2790 字符 / 8 小节 → 变死配置**） | `bundle/persona.md`；`evidence/a12-persona-scope.out.txt`（A12-1b/2a/3b/3c） | SP + E | SP：行为纪律随模式走；E：判据可复算 |
| 3 | **skill 库** | **45 派生目录**（`~/.dsh/skills/opencode/`）单根；模型可见 **42 = 45 − 3 件 `disable-model-invocation`**（opencode-config / opencode-capability-audit / opencode-capability-extension）；`_overlay` **6 件** openspec 系叠加 | `evidence/skill-catalog-runtime.txt`、`skill-reconcile.out.txt`、`a10-negative-skill-gate.out.txt` | T + E | T：能力密度提升；E：门控 0 问题 |
| 4 | **委派编队** | **7 worker**（general / explore / architect / requirement-discovery / search / reflection / pdf）→ 别名 `subagent` / `oc_explore` / `oc_architect` / `oc_requirement` / `oc_search` / `oc_reflection` / `oc_pdf`；`delegation` 组 **12 子行**；worker 均**省略 maxDepth**，靠 `toolFilter.deny` 阻止再委派 | `cordis.patch.yml`（`id: delegation`）；`verify-bundle-13checks.out.txt`（check 7：8 subagent rows = 7 worker + fork） | P 主 + T | P：主 Agent 编排 + 专职执行；T：工具面按 worker 隔离 |
| 5 | **权限层** | 宿主 presets 由 **3 档 → 5 档**（+`opencode-plan` / `opencode-build`），`defaultPreset: read-only` 未变 | `~/.dsh/profiles/web/cordis.patch.yml`；`report.md` §3.5 | T（安全） | T：审批档增加，非隔离档增加 |
| 6 | **模型接入层** | 宿主 **4 provider**（zai / opencode-go / commandcode / opencode-go-tmp）+ deepseek 直连；含 `inputModalities` **视觉声明** | 宿主 profile patch；`report.md` | T（基建） | T：模型接入面扩大，支撑视觉降级路径 |
| 7 | **plan-mode 层** | `plan:policy` section 由内置 **2358 → 2515 字符**，追加 **3 行中文逐题访谈指引**（指向 `grill-me`） | 宿主 profile patch；对照内置 standard 会话 `system/message` | SP + P | SP：计划门附访谈约束 |
| 8 | **工具面分层** | 内置 standard **31** / opencode-standard **37**（含 6 个 `oc_*`）/ opencode-creator **40**（+`cordis_inspect_*`、`plugin_manager`）/ opencode-ptc **1**（仅 `run_code`，`workflow` 双禁） | `evidence/session-probe-*.json`；`report.md` §3.10 | T | T：同一内核派生 4 种执行面 |
| 9 | **插件收口** | `plugin_manager` 计数 **188 → 191**（+3 行 preset）；standard/ptc **硬禁**、creator **条件启用** | `evidence/plugin-preset-rows.txt`；`report.md` §3.3 | T（治理） | T：自省面按模式收口，防越权自改 |
| 10 | **领域门控栈** | architecture-judgment（`_private/gate_architecture.py` ADR schema 门控）+ requirement-discovery（分层定档）+ search-methodology（信源分级）+ criterion-design-validation | `_out/architecture-judgment/`、`_out/requirement-discovery/`、`_out/search-methodology/`、`_out/criterion-design-validation/` | E 主 + P | E：首个领域级自动评估门；P：领域任务路由固化 |

## 3. 五环双层 delta（含 SP）

| 环 | 官方内核 | 装配层增量 | 装配层综合 | 标注 | 关键改造 |
|----|:---:|:---:|:---:|:---:|------|
| **SP 设定值** | 4.5 | +0.5 | **5.0** | 增强 | 3 preset 层固化 persona 15 节（GATE/COMPLEXITY/契约委派/留档 5 段）+ plan-mode section 追加逐题访谈指引 |
| **M 记忆** | 4.0 | 0 | **4.0** | 持平 | 装配层未新增跨会话记忆；persona 的 MEMORY/reflection 段在 dsh 侧**不可用** |
| **P 规划** | 4.5 | +0.5 | **5.0** | 增强 | +7 专职 worker + `oc_*` 别名 + delegation 编队（12 子行）+ 全局控制面（send_message/interrupt_agent/list_agents） |
| **R 反思** | 3.0 | 0 | **3.0** | 持平·迁移损失 | 未新增内源反思；reflection 链路在 dsh 侧断裂（`dsh-reflection` 插件已移出） |
| **T 执行** | 5.0 | 0 | **5.0** | 持平 | permission 5 档 + 工具面按 preset 收敛（31/37/40/1）+ plugin_manager 收口（188→191）；官方 T 环已处上限，装配层无净增 |
| **E 评估** | 2.0 | +1.5 | **3.5** | **增强（非反转）** | `oc_architect` + `gate_architecture.py` / `oc_requirement` + 分层定档 / `oc_search` 证据包 + 信源分级 / criterion-design-validation；但门控脚本依赖 bash 而子 Agent 无 bash，且仍为领域级单点 |

> 判据：`dsh_custom_scores.py::ring_delta` 以 **Δ≥2.0 记「反转」**，否则 Δ>0 记「增强」、Δ=0 记「持平」。E 环 Δ+1.5 **未达反转阈值**，且迁移损失使它不宜记为反转——这是本轮最关键的口径克制。SP 环按 `RING_ORDER` 单列，不计入五环但为五环提供目标参考序列。

## 4. 精装度 8 维对比

> 数值唯一来源：`09-src-data/dsh_custom_scores.py`（`SCORES` / `WEIGHTS`，与 `premium_scores.WEIGHTS` 同源）。官方加权 **3.63 → 3.6**，装配层加权 **3.75 → 3.8**，**Δ+0.2**；两者均过端到端硬门槛、无一票否决。

| 维度 | 权重 | 官方 | 装配层 | Δ | 依据 |
|------|:---:|:---:|:---:|:---:|------|
| 多Agent编排 | 16 | 4 | 4 | 0 | 官方 subagent 6 provider 后端 + fork + workflow + Agent Teams（无可视化 DAG）；装配层 +7 worker + `oc_*` 别名 + 3 preset 编队，**仍无 DAG 画布 → 不升 5** |
| Skill库 | 12 | 3 | 4 | **+1** | 官方 skill 注册表 host + per-scope 分层 + 官方 skill 包（非市场）；装配层 +45 派生 skill 精选库（模型可见 42）+ `_overlay` 6 件 |
| 工作流 | 13 | 4 | 4 | 0 | 官方 plan/goal/workflow/ralph + jobs + schedule 四工具触发（无通用可视化画布）；装配层把流程纪律迁入 persona 15 节 + plan-mode 追加访谈指引，**未跨画布档** |
| 模型接入 | 14 | 4 | 4 | 0 | 官方 DeepSeek 直连 + pi-ai 目录 + 三协议；装配层 +4 provider + `inputModalities` 视觉声明，**仍非「千级模型开箱」** |
| 一键部署 | 15 | 3 | 3 | 0 | 官方 `npx @deepseek-ai/dsh web` 单命令 + 自填 key；装配层 bundle 需手动 `install_bundle` 且**不可移植**（persona 含本机绝对路径、node_modules 28 个符号链接指向本机源码树）→ 维持 3 |
| 沙箱 | 10 | 4 | 4 | 0 | 官方后端族 + enforcement full/partial + fail-closed（本机无可用后端 → 实际 fail-closed）；装配层 permission 5 档中 `opencode-plan/build` 属**审批档而非隔离档** → **Δ0** |
| MCP生态 | 10 | 3 | 3 | 0 | 官方内置 MCP client + resources 三工具、无 marketplace；**装配层宿主 0 个 MCP 配置**（对比 opencode-custom 侧 4 个）→ 迁移相对损失 |
| 记忆 | 10 | 4 | 4 | 0 | 官方事件溯源 session + projection + compaction + session-format v4 + session-query/FTS5；装配层未新增跨会话学习型记忆 → **Δ0** |

> **档位结论**：官方 raw 3.63 → 终值 **3.6**、装配层 raw 3.75 → 终值 **3.8**，二者同落 `tier()` 的「**成品化受限**」档（≥3.5 且 <4.5），**均未跨档**。8 维中仅 **Skill 库 +1** 是唯一净增；多Agent/工作流/模型接入三维虽机制增多，但**未触及任何 5 档产品阈值**（无 DAG 画布、无通用可视化工作流、非千级模型开箱）；一键部署与沙箱因「无分发渠道 / 非隔离档」封顶未变。**Δ+0.2 的全部来源 = Skill 维度 +1 × 权重 12% = +0.12，叠加四舍五入后的显示差**——这是一次「单维小步」而非「全面跃升」。

## 5. 口径披露（单点分 vs 模型分）

> ⚠️ **本节是防止虚报跃升的必要声明，缺失即等于虚报。**

1. **旧口径（v1.3 及以前）**：dsh 在 KB 里只有「技术框架对照」的**单点分 2.5**，**硬编码在 `09-src-data/gen_html.py` 的 `FRAMEWORK_DATA`**——它**不是** 8 维模型的输出，没有硬门槛、没有权重、没有一票否决。
2. **新口径（本轮首次）**：本轮**首次**把 dsh 纳入 v2.0 精装度模型（硬门槛 + 8 维加权 + 一票否决），得到官方 **3.6** / 装配层 **3.8**。
3. **不可相减**：**3.6 与 2.5 不同源**（一个是模型加权输出，一个是框架对照单点判定），因此「2.5 → 3.6」这个差**在数学上不成立**，本文件拒绝给出该数字。旧单点分 2.5 作为**历史口径保留并标注**。
4. **同步校正**：本轮把 `FRAMEWORK_DATA` 里 opencode 的 **3.0 校正为模型口径 2.9**——原值属**口径漂移**（同一对象在两套口径下被写了两个数），一并归位。
5. **未重算项**：**同模型下未重算 `0.1.1-rc.2`**（无当时证据可依），故「0.1.1-rc.2 → 0.2.1-alpha.2 的**模型分变化**」**不可得**；本轮对该跨度只给「**版本跨度 21 个预发布 + 机制增量清单**」，不给分值差。

## 6. 四大核心发现

**发现一：同一装配层跨平台迁移存在「能力损失」——E 环只判增强、不判反转。**
opencode 侧的 `architect-worker` 可**自跑门控脚本**（有 bash）；dsh 侧**子 Agent 无 bash**（仅 read/write/edit/glob/grep）→ `gate_architecture.py` **无法在子 Agent 内自跑**。同一套「skill + worker + 门控脚本」装配，换了宿主就从「产出方与验证方天然分离且可自动执行」退化为「验证动作须由父层代跑」。故 E 环官方 2.0 → 装配层 3.5，Δ+1.5 **只记「增强」不记「反转」**（阈值 Δ≥2.0）。

**发现二：R 环迁移断裂，闭环未接通（Δ0）。**
提供 `reflection_add` / `reflection_mark` 的 `dsh-reflection` 插件已于 **2026-10-10 随批次移出** → persona 中的 **MEMORY / reflection 段在 dsh 侧不可用**。装配层照搬了 opencode 侧的反思纪律文本，却没有承载它的工具面：纪律是死的，链路是断的。这是「提示词可迁移、运行时能力不可迁移」的典型样本，R 环维持 3.0（标注「持平·迁移损失」）。

**发现三：bundle 自家门控曾假阳性 FAIL——判据应绑「被消费字段」而非「整文件指纹」。**
原判据对「活文件」取**整文件 sha256**，脆性极高：GUI 写回一个 `ui-theme.fontSize` 即导致指纹漂移 → 门控 FAIL，而 bundle 实际消费的字段一个都没变。**已改为 `scoped_digest`，只判 bundle 实际消费字段**。教训具有跨域普适性：**门控判据的对象须与被消费的真实形态对齐**，对「既存且会被他方合法改写」的文件取整文件指纹，同时制造**假 FAIL**（无关改动被当回归）与**覆盖错觉**（真回归混入噪音不可分）。

**发现四：persona 税与 PTC 空指向——装配层的两处结构性代价。**
其一，**persona 税**：每请求 **+8018 字符**（≈3084 tokens），而内置 standard 的对应 section 仅 **54 字符**——约 **150 倍**开销，且三 preset 各自完整复制一份。其二，**PTC 空指向**：PTC 模式下工具面坍缩为单 `run_code`（系统提示 13658 → **53826** 字符，多为 PTC 呈现说明），但 persona §二 仍写「本模式提供 `subagent`、`oc_explore`…」→ **指向了不存在的工具**，模型据文本会尝试调用被禁能力。系统提示膨胀 4 倍、有效工具仅 1 个，是本装配层最尖锐的自相矛盾。

## 7. 排名隔离声明

本文件评分的对象是**个人装配层变体**（`dsh-custom` = 官方内核 + `dsh-opencode-port` bundle + 宿主 profile patch），**不是市售产品**。因此：

- `dsh_custom_scores.py` **独立于 `premium_scores.PRODUCTS`**，其分值**不参与 14 产品市售排名**，不得与 `premium-map.html` / `premium-cyto.html` 中的产品分同轴比较；
- 官方 `dsh` 与 `dsh-custom` 构成**同源对照对**（同一内核、同一模型、同一权重），只回答「装配层带来多少增量」，不回答「dsh 在 14 产品中排第几」；
- 与 `opencode-custom` 专题同构：两个装配层变体分属两个宿主，**跨宿主比 Δ 有意义，比绝对值无意义**（基线不同、可用机制不同）。

### 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S1 | 可复算评分（单一数据源） | `09-src-data/dsh_custom_scores.py`（官方 3.6 / 装配层 3.8，8 维 + 五环 + SP 分值权威来源） | 高 |
| SRC-002 | S1 | 评分模型 | `07-checkpoint/premium-scoring-model.md`（精装度 v2.0：硬门槛 + 8 维加权 + 一票否决） | 高 |
| SRC-003 | S4 | 一手装配观察 | `~/.dsh/presets/opencode/cordis.patch.yml`（3 preset / persona 行 / delegation 组 12 子行 / toolFilter.deny） | 高 |
| SRC-004 | S4 | 一手 persona 观察 | `~/.dsh/presets/opencode/persona.md`（15 节 / 8018 字符单一来源） | 高 |
| SRC-005 | S4 | 一手宿主 patch 观察 | `~/.dsh/profiles/web/cordis.patch.yml`（permission 5 档 + 4 provider + plugin-manager.pnpmCommand + plan:policy 2515 字符） | 高 |
| SRC-006 | S4 | 一手静态校验 | `…1011-deepseek harness-提示词迁移工程-从opencode/evidence/verify-bundle-13checks.out.txt`（13 项：顶层 21/22/22、persona 一致性、worker 编队、28 node_modules 锚点） | 高 |
| SRC-007 | S4 | 一手运行时探针 | `…/evidence/session-probe-{builtin-standard,opencode-standard,opencode-creator,opencode-ptc}.json`（工具数 31/37/40/1、系统提示字符数） | 高 |
| SRC-008 | S4 | 一手 skill 取证 | `…/evidence/skill-catalog-runtime.txt`、`skill-reconcile.out.txt`、`a10-negative-skill-gate.out.txt`（45 派生 / 模型可见 42 / 门控 0 问题） | 高 |
| SRC-009 | S4 | 一手作用域取证 | `…/evidence/a12-persona-scope.out.txt`（persona 8018 遮蔽 host personaPrefix 2790/8 小节；含 5 条负向用例） | 高 |
| SRC-010 | S4 | 一手插件计数 | `…/evidence/plugin-preset-rows.txt`（三行 `enabled=true`/`active`；插件总数 188 → 191） | 高 |
| SRC-011 | S4 | 一手迁移报告 | `…1011-…-从opencode/report.md`（§3.5 权限 5 档 / §3.10 运行时验收 / §3.8 加载失败事故与门控加固） | 高 |
| SRC-012 | S4 | 对照基线 | `03-cases/deepseek-harness.md`（官方 dsh 五环结构与结论口径，本轮升 v0.2.1-alpha.2） | 高 |
| SRC-013 | S1 | 口径历史值 | `09-src-data/gen_html.py` `FRAMEWORK_DATA`（dsh 旧单点分 2.5、opencode 校正 3.0 → 2.9；**与模型分不同源**） | 高 |
| SRC-014 | S4 | **本库脱敏快照（入库）** | `07-checkpoint/dsh-custom-snapshot/inventory.json` + `manifest.json`（`collected_at` = 2026-10-11；presets / worker 别名 / permission 档位 / skill 计数与 sha256 均可离线复核） | 高 |
