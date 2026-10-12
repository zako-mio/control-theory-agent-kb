# dsh 官方 vs dsh-custom 装配层 — 对照分析

> 一句话定位：本文件以官方 dsh v0.2.1-alpha.2「默认内核 + 内置 standard 模式 + 零 MCP」为基线，逐类拆解 `dsh-opencode-port` 装配层的改造及其对 SP/M/P/R/T/E 六环的双层增量，量化精装度 3.6 → **3.9**（Δ**+0.3**）的来源，并单列口径披露以免把「装配层复评」误读为内核跃升。
>
> 版本：**v1.5（2026-10-13）**。**内核零变化，全部增量在装配层**——官方基线仍为 `dsh v0.2.1-alpha.2`（commit `d743267`，2026-10-09），本轮**未升版**；变的是装配层（R 环载体落地、E 环门控通道、模型路由治理、判据 13 → 20 项）。官方 **3.6**（raw 3.63，未变）/ 装配层 **3.9**（raw 3.85，v1.4 为 3.8 / raw 3.75），**Δ+0.3**；两者均过端到端硬门槛、无一票否决，**档位仍为「成品化受限」，未跨档**。分值唯一来源：`09-src-data/dsh_custom_scores.py`（`SCORES` / `RING_SCORES` / `WEIGHTS`），本文件不自行改分。与 `03-cases/deepseek-harness.md`（官方画像）口径一致。
>
> ⚠ 本轮**三条 v1.4 旧结论被推翻**（R 环迁移损失、E 环抑制项、沙箱环境事实）——旧值不删除，见文末「历史块 · v1.4 口径」。

## 1. 基线定义

**基线 = 官方 dsh v0.2.1-alpha.2（2026-10-09，commit `d743267`）默认装配 + 内置 standard 模式**，仅含：

- **官方内核**：cordis 插件装配架构（`bundle/base/cordis.patch.yml`）+ 内置 preset 族（standard / ptc / minimal / cordis）+ 内置 `standard` 工具面 **31** 个工具。
- **官方 P/M/T 机制**：plan-mode（`exit_plan_mode` + plan:policy 段，section 2358 字符）、goal + goal-round-driver、subagent（6 个 provider 后端：spawn/fork/acp/codex/claude-code/dsh-sdk）+ fork + workflow + ralph、事件溯源 session + projection + token-meter + compaction 三插件 + session-format v4 + session-query/FTS5。
- **官方 T 安全面**：tools 三瀑布 + timeout-policy + sandbox 后端族（bwrap/Landlock/Seatbelt/win32 ACL/sandbox-ssh）+ spill + approval + permission presets **3 档**（read-only / workspace-write / danger-full-access，default read-only）。
- **官方模型面**：DeepSeek 直连 + llm-pi-ai 第三方目录 + 自定义 OpenAI Chat/Responses/Anthropic 三协议。
- **明确不含**：自定义 preset / persona 覆盖层 / 派生 skill 库 / 专职 worker 编队 / MCP 配置 / 跨会话学习型长期记忆。
- **版本跨度**：tag 全集跨 `0.1.2-alpha.1 … 0.2.1-alpha.2` 共 **21 个预发布**（本轮基线为其中最新者）。

**装配侧 = `dsh-opencode-port` bundle**（`~/.dsh/presets/opencode/`，包版本 0.1.0）**+ 宿主 profile patch 增量**（`~/.dsh/profiles/web/cordis.patch.yml`）。来源工程：`/home/zako-mio/opencode/archive/Mission-file/2026-10/1011-deepseek harness-提示词迁移工程-从opencode/`。

**v1.5 装配层规模（四项硬读数）**：

| 项 | v1.5 读数 | 说明 |
|---|---|---|
| skill 主根 | **49** | = 派生 **47** + **DSH 原生 2**（`dsh-config` / `dsh-reflection`）；模型可见 **46**；`_overlay` 另 **6** 件不计入主根 |
| `verify_bundle` 判据 | **20 项** | v1.4 为 13 项；新增 14–20 七项（见 §2） |
| persona 字节 | **12066 B**（**15 节不变**） | v1.4 为 15403 B——节数未动，正文容量收敛（机器特定事实外迁至 `dsh-config` skill） |
| 插件面 | 宿主 **1**（`dsh-wsl-desktop-path`）+ bundle **2**（`dsh-opencode-commands`、`dsh-opencode-gate-runner`） | v1.4 记「计数 188 → 191」；v1.5 改为**按归属登记**，不再用单点总数 |

> ⚠ **本轮内核零变化，全部增量在装配层**：官方 `dsh` 侧内核版本、commit、工具面、preset 族、permission 3 档**逐项未变**（官方 3.6 / raw 3.63 亦未变）。因此本文件的一切 Δ 都只能归因于 bundle 与宿主 profile patch，⛔ 不得归因于上游升版。

## 2. 改造清单（v1.5 版）

> v1.4 的 10 类结构保留，逐类刷新为 v1.5 实况；**每条均带证据指针**（路径限定的外部指针见 §证据来源）。

| # | 类别 | 改造内容 | 证据 | 对环影响 |
|---|------|---------|------|---------|
| 1 | **preset 编队层** | 新增 3 preset：`opencode-standard`(order 11) / `opencode-creator`(12) / `opencode-ptc`(13)；顶层插件行 **23/24/24**（v1.4 为 21/22/22，各 +2 = `gate-runner` + `opencode-commands`） | `07-checkpoint/dsh-custom-snapshot/bundle__cordis.patch.yml`（行 16/446/877 起三段）；`evidence/verify-bundle-13checks.out.txt`（check 2，v1.4 口径） | SP 主 + P | SP：三档设定值固化；P：模式即编队 |
| 2 | **persona 层** | 15 节 / **12066 B**（v1.4 为 15403 B；≈3084 tokens 的旧估算随正文收敛失效）persona 逐字符进三 preset 的 `@deepseek-ai/dsh-persona` 行；**遮蔽**宿主 `system-prompt.personaPrefix`（**2790 字符 / 8 小节 → 变死配置**）。§八「机器特定环境事实」已外迁，只保留被 check 17 提取的那一条 | `bundle__persona.md`（15 个 `## ` 标题）；`bundle__cordis.patch.yml` 行 16/446/877；`evidence/a12-persona-scope.out.txt`（A12-1b/2a/3b/3c） | SP + E | SP：行为纪律随模式走；E：判据可复算（check 3/4/13/17） |
| 3 | **skill 库** | 主根 **49** = 派生 **47** + **DSH 原生 2**（`dsh-config` / `dsh-reflection`）；模型可见 **46 = 49 − 3 件 `disable-model-invocation: true`**（`opencode-config` / `opencode-capability-audit` / `opencode-capability-extension`）；`_overlay` **6 件** openspec 系叠加（不计入主根） | `07-checkpoint/dsh-custom-snapshot/inventory.json`（`skills_list`：`main_root_list` 49 / `derived` 47 / `dsh_native` 2 / `source_skill_dirs` 47 / `non_skill_dirs_excluded` = `_shared`,`disabled`）；`evidence/skill-catalog-runtime.txt`、`skill-reconcile.out.txt`、`a10-negative-skill-gate.out.txt` | T + E | T：能力密度提升；E：门控 0 问题 |
| 4 | **委派编队** | **7 worker**（general / explore / architect / requirement-discovery / search / reflection / pdf）→ 别名 `subagent` / `oc_explore` / `oc_architect` / `oc_requirement` / `oc_search` / `oc_reflection` / `oc_pdf`；`delegation` 组 **12 子行**；worker 均**省略 maxDepth**，靠 `toolFilter.deny` 阻止再委派。**R-A 生效后 `oc_reflection` 的写入目标已指向 DSH 侧候选目录** | `bundle__cordis.patch.yml`（`id: delegation` 行 220/649/1081）；`inventory.json`（`worker_aliases` 6 个别名）；`verify-bundle-13checks.out.txt`（check 7） | P 主 + T | P：主 Agent 编排 + 专职执行；T：工具面按 worker 隔离 |
| 5 | **权限层** | 宿主 presets 由 **3 档 → 5 档**（+`opencode-plan` / `opencode-build`）；`defaultPreset` 由 `read-only` **改为 `opencode-plan`**（sandbox `read-only` + approval `ask`，展示名 `OC·Plan（只读）`） | `07-checkpoint/dsh-custom-snapshot/profile__web-cordis.patch.yml`（`permission` 行，`defaultPreset: opencode-plan`） | T（安全） | T：审批档增加，非隔离档增加；默认档位收紧到只读 |
| 6 | **模型接入层** | 宿主 **4 provider**（zai / opencode-go / commandcode / opencode-go-tmp）+ deepseek 直连；含 `inputModalities` **视觉声明**。**v1.5 新增模型路由治理**：`reasoningEfforts` 三档（low/high/max，**刻意不声明 `off`**——声明空值会把思考默认关掉）+ `maxTokens` **8192 → 32768**（撤销 2026-10-11「方案 D」自设窄帽）+ `deepseek-v4-flash` **16384 → 32768** | `profile__web-cordis.patch.yml`（行 118-131 / 255-304）；`dsh-config` skill `local/model-routes.md` + `claims.yaml` `M1`–`M4` | T（基建） | T：模型接入面扩大，支撑视觉降级路径；窄帽撤销恢复长输出 |
| 7 | **plan-mode 层** | `plan:policy` section 由内置 **2358 → 2515 字符**，追加 **3 行中文逐题访谈指引**（指向 `grill-me`） | 宿主 profile patch；对照内置 standard 会话 `system/message` | SP + P | SP：计划门附访谈约束 |
| 8 | **工具面分层** | 内置 standard **31**；opencode-standard **37**（v1.4 读数，含 6 个 `oc_*`）/ opencode-creator **40**（v1.4 读数，+`cordis_inspect_*`、`plugin_manager`）/ opencode-ptc **1**（仅 `run_code`，`workflow` 双禁）。**v1.5 机制新增**：三 preset 顶层各 +1 `gate-runner` 行 ⇒ 模型可见窄工具 **`run_gate`**（+1）；`opencode-commands` **不注册工具**（只注册人面向命令，见 #14） | `evidence/session-probe-*.json`（v1.4 读数）；`bundle__cordis.patch.yml`（`id: gate-runner` 行 404/833/1267）；`…1011-迁移适配-E环门控通道与R环纠正/evidence/verify-gate-channel-live.out.txt` | T + E | T：同一内核派生 4 种执行面；E：执行面自带门控通道 |
| 9 | **插件收口** | 宿主插件根 `~/.dsh/plugins/` **仅 1 个**：`dsh-wsl-desktop-path`（systemd 宿主 PATH 不含 `/mnt/c/Windows` ⇒ `explorer.exe` spawn ENOENT 的修复，只追加 PATH，不注册任何工具/服务/remote）；bundle 内插件包 **2 个**：`dsh-opencode-commands`、`dsh-opencode-gate-runner`；`plugin_manager` 在 standard/ptc **硬禁**、creator **条件启用** | `inventory.json`（`plugins`：`host_plugins` / `bundle_plugin_packages`）；`profile__web-cordis.patch.yml`（`insert:` 行）；`evidence/plugin-preset-rows.txt` | T（治理） | T：自省面按模式收口，防越权自改 |
| 10 | **领域门控栈** | architecture-judgment（`_private/gate_architecture.py` ADR schema 门控）+ requirement-discovery（分层定档）+ search-methodology（信源分级）+ criterion-design-validation | `_out/architecture-judgment/`、`_out/requirement-discovery/`、`_out/search-methodology/`、`_out/criterion-design-validation/` | E 主 + P | E：领域级自动评估门；P：领域任务路由固化 |
| 11 | **`run_gate` 门控执行通道**（v1.5 新增） | ADR-010：preset 顶层行 ×3（`id: gate-runner`，本地插件包 `dsh-opencode-gate-runner`）；参数面受限——只收「脚本路径 + argv 数组」（**构造上无 `-c`/`-e` 内联通路**）、解释器按**扩展名白名单**（`.py`/`.js`/`.mjs`/`.sh`）选择、**roots 白名单**（会话工作区 + preset 目录 + skills 目录，**realpath 后**判定）、超时 **120s / 上限 600s**、输出 **16KB 封顶后 spill 至 `~/.dsh/spill/gate-runner/`**。**消解 v1.4 的 E 环抑制项**（子 Agent 无 bash ⇒ 门控脚本无法自跑） | `…1011-迁移适配-E环门控通道与R环纠正/arch/ADR-010.json`（`status: proposed`）+ 同目录 `ADR-010.md`（§四 方案 2 / §五 决策 行 71 的窄通道构造约束）与 `MATRIX-010.md`；`…/evidence/gate-runner-unit-tests.out.txt`、`verify-gate-channel-live.out.txt`；`bundle__cordis.patch.yml`（行 404-420 完整 config） | E 主 + T | E：产出方与验证方重新可分离且可自动执行 |
| 12 | **`dsh-config` 能力包**（v1.5 新增） | ADR-011：本机**分层实况 + 冲突消解 + 漂移门控**索引（**收窄口径**——官方 schema 权威归 DSH 自带面，本包只给指针）。结构：`SKILL.md` + `ref/` **8** + `local/` **11** + `ops/` **4** + `troubleshooting/` **1** + `claims.yaml`（声明账本）+ `conflicts.md`（冲突台账） | `~/.dsh/skills/opencode/dsh-config/`；`…1011-全面适配性迁移分析/arch/ADR-011.json`（`status: proposed`、门控 6/6）；`evidence/r11-final-gates.out.txt` §⑤ `verify_dsh_config.py` PASS + 负向自检 15 用例 | E 主 + SP | E：新增「声明账本漂移」判据（check 18）；SP：persona §八 机器事实外迁至此 |
| 13 | **R-A 记忆载体**（v1.5 新增） | ADR-012：`~/.dsh/MEMORY.md` 落地（**14 个 `§` 段 / 10815 B / 57 行 / 14 条 `[src:]` 签名**）+ `~/.dsh/reflection/candidates/` **15 份候选** + `archive/` **1 份** + `dsh-reflection` skill（零和预算 / 生命周期五件 / 容量口径 `memory_capacity_check.py`）。写入链 = **候选 → 主 Agent 审阅 → 落库**（显式链，⛔ 子 Agent 不得直写） | `inventory.json`（`reflection` 段）；`…1011-全面适配性迁移分析/arch/ADR-012.json`（`status: proposed`、门控 6/6）；`bundle__persona.md` §十 | R 主 + M | R：链路接通（Δ+1.0）；M：跨会话学习型记忆载体首次存在（Δ+1） |
| 14 | **命令注册插件**（v1.5 新增） | `dsh-opencode-commands` 插件注册 **`/arch` `/rd` `/reflection`** 三条命令（**命令级工作流入口**）。注：`@deepseek-ai/dsh-commands` 的 registry 是 `Plugin-owned human-command registry`，命令文本**不自动送进模型** | `~/.dsh/presets/opencode/plugins/dsh-opencode-commands/index.js`（行 40/50/60）；`evidence/r11-final-gates.out.txt` §⑦ `commands: tests 6 / pass 6 / fail 0`；`bundle__cordis.patch.yml`（行 421-422） | P + E | P：工作流入口固化；E：check 20 注册单测 |
| 15 | **判据扩充 13 → 20 项**（v1.5 新增） | `verify_bundle.py` 新增 7 项：**14** 门控执行通道 `run_gate`（结构 P1-P5 + 行为负向）/ **15** 真实挂载审计（真 `runProfile` + 真 Loader + 负向控制）/ **16** 工具 `output.schema` 子集校验 / **17** 会话 PATH 引导（外部 CLI 可达性）/ **18** `dsh-config` 声明账本漂移 / **19** 迁移状态（E3 residue / 陈旧断言 / E7 互斥 / R 环载体）+ 判据自检 / **20** 命令注册插件（E10） | `inventory.json`（`gate.check_count` = 20 + 20 条标题）；`evidence/r11-final-gates.out.txt` §③ `verify_bundle.py（20 项）` PASS | E 主 | E：判据面从「静态装配」扩到「运行时可挂载 + 可执行 + 可漂移检测」 |

> ⛔ **数值纪律**：本表的 skill 计数、判据项数、persona 字节、插件归属、`run_gate` 参数面均为**权威取值**，⛔ 不得自行推算或替换。工具面一栏的 37/40 标注为 v1.4 读数，v1.5 未重跑 `session-probe` 复算（机制增量已登记为 +1 `run_gate`）。

## 3. 六环双层 delta（含 SP）

| 环 | 官方内核 | 装配层增量 | 装配层综合 | 标注 | 关键改造 |
|----|:---:|:---:|:---:|:---:|------|
| **SP 设定值** | 4.5 | +0.5 | **5.0** | 增强 | 3 preset 层固化 persona 15 节（GATE/COMPLEXITY/契约委派/留档 5 段）+ plan-mode section 追加逐题访谈指引 + 机器事实外迁 `dsh-config` 后正文收敛至 12066 B |
| **M 记忆** | 4.0 | +0.5 | **4.5** | 增强 | 装配层首次落地跨会话学习型记忆载体：`~/.dsh/MEMORY.md`（14 `§` 段 / 10815 B / 57 行 / 14 条 `[src:]` 签名）+ 候选池 + 审阅链（ADR-012） |
| **P 规划** | 4.5 | +0.5 | **5.0** | 增强 | +7 专职 worker + `oc_*` 别名 + delegation 编队（12 子行）+ 全局控制面（send_message/interrupt_agent/list_agents）+ `/arch` `/rd` `/reflection` 三条命令入口 |
| **R 反思** | 3.0 | +1.0 | **4.0** | **增强**（v1.4「迁移损失」**已推翻**） | R-A 文件载体落地（ADR-012，门控 6/6）：候选目录 15 份 + archive 1 份 + `dsh-reflection` skill（零和预算 / 生命周期五件 / 容量口径）+ 写入链「候选 → 主 Agent 审阅 → 落库」；`oc_reflection` 写入目标已转回 DSH 侧 |
| **T 执行** | 5.0 | 0 | **5.0** | 持平（已封顶） | permission 5 档（`defaultPreset: opencode-plan`）+ 工具面按 preset 收敛（31/37/40/1，v1.4 读数）+ 插件面按归属登记（宿主 1 + bundle 2）；官方 T 环已处上限，装配层无净增 |
| **E 评估** | 2.0 | **+2.0** | **4.0** | **反转**（v1.4 的「非反转」**已推翻**） | `run_gate` 窄通道（ADR-010）实机生效：三 preset 各 +1 顶层 `gate-runner` 行，参数面受限（脚本路径 + argv 数组 / roots 与扩展名白名单 / 超时 120s-600s / 输出 16KB 封顶后 spill），负向用例 **18 → 30** 条，`node --test` **57/57**；叠加领域门控栈 + 判据 13 → 20 项 |

> **最弱环：R 与 E 并列 4.0**（v1.4 为单一最弱环 R=3.0）。
>
> 判据：`dsh_custom_scores.py::ring_delta` 以 **Δ≥2.0 记「反转」**，否则 Δ>0 记「增强」、Δ=0 记「持平」。E 环 Δ**+2.0 达反转阈值** ⇒ 标注由 v1.4 的「增强（非反转）」改为**反转**；R 环 Δ+1.0 ⇒ 标注由「持平·迁移损失」改为**增强**（迁移损失结论被 ADR-012 的载体落地推翻）。SP 环按 `RING_ORDER` 单列，不计入五环但为五环提供目标参考序列。

## 4. 精装度 8 维对比

> 数值唯一来源：`09-src-data/dsh_custom_scores.py`（`SCORES` / `WEIGHTS`，与 `premium_scores.WEIGHTS` 同源）。官方加权 **3.63 → 3.6**（未变），装配层加权 **3.85 → 3.9**（v1.4 为 3.75 → 3.8），**Δ+0.3**；两者均过端到端硬门槛、无一票否决。

| 维度 | 权重 | 官方 | 装配层 | Δ | 依据 |
|------|:---:|:---:|:---:|:---:|------|
| 多Agent编排 | 16 | 4 | 4 | 0 | 官方 subagent 6 provider 后端 + fork + workflow + Agent Teams（无可视化 DAG）；装配层 +7 worker + `oc_*` 别名 + 3 preset 编队，**仍无 DAG 画布 → 不升 5** |
| Skill库 | 12 | 3 | 4 | **+1** | 官方 skill 注册表 host + per-scope 分层 + 官方 skill 包（非市场）；装配层主根 **49**（= 派生 47 + DSH 原生 2）/ 模型可见 **46** + `_overlay` 6 件。⚠ **数量增长未改变档位**——Δ 维持 +1，仍非「市场级千件 skill 生态」 |
| 工作流 | 13 | 4 | 4 | 0 | 官方 plan/goal/workflow/ralph + jobs + schedule 四工具触发（无通用可视化画布）；装配层把流程纪律迁入 persona 15 节 + plan-mode 追加访谈指引 + 三条命令入口，**未跨画布档** |
| 模型接入 | 14 | 4 | 4 | 0 | 官方 DeepSeek 直连 + pi-ai 目录 + 三协议；装配层 +4 provider + `inputModalities` 视觉声明 + `reasoningEfforts` 三档 + `maxTokens` 窄帽撤销，**仍非「千级模型开箱」** |
| 一键部署 | 15 | 3 | 3 | 0 | 官方 `npx @deepseek-ai/dsh web` 单命令 + 自填 key；装配层 bundle 需手动 `install_bundle` 且**不可移植**（persona 含本机绝对路径、node_modules 28 个符号链接指向本机源码树）→ 维持 3 |
| 沙箱 | 10 | 4 | 4 | 0 | 官方后端族 + enforcement full/partial + fail-closed。⚠ **环境事实更正**：v1.4 记「本机无可用后端（bubblewrap/Landlock 均不可用）→ 实际 fail-closed」**已证伪**——bwrap **已装**、链选中 **bwrap**、**`enforcement=full`**、`read-only` / `workspace-write` 在 **shell + fs 双侧真强制**。但此为**环境事实更正，非装配层能力增量** ⇒ ⛔ 不得写成装配层收益，**分值不变（仍 4/4，Δ0）** |
| MCP生态 | 10 | 3 | 3 | 0 | 官方内置 MCP client + resources 三工具、无 marketplace；**装配层宿主 0 个 MCP 配置**（对比 opencode-custom 侧 4 个）→ 迁移相对损失 |
| 记忆 | 10 | 4 | 5 | **+1** | 官方事件溯源 session + projection + compaction + session-format v4 + session-query/FTS5；**装配层新增跨会话学习型记忆载体**——`~/.dsh/MEMORY.md`（14 `§` 段 / 10815 B / 57 行 / 14 条 `[src:]` 签名）+ `~/.dsh/reflection/candidates/` 15 份候选 + archive 1 份 + 审阅链（ADR-012，门控 6/6）⇒ **v1.5 相对 v1.4 的唯一 8 维变动**（`skill` 4→4 未动，`memory` 4→5） |

> **档位结论**：官方 raw 3.63 → 终值 **3.6**、装配层 raw **3.85** → 终值 **3.9**，二者同落 `tier()` 的「**成品化受限**」档（≥3.5 且 <4.5），**均未跨档**。8 维中 **Skill 库 +1** 与 **记忆 +1** 是两处净增；多Agent/工作流/模型接入三维虽机制增多，但**未触及任何 5 档产品阈值**（无 DAG 画布、无通用可视化工作流、非千级模型开箱）；一键部署与沙箱因「无分发渠道 / 非隔离档」封顶未变（沙箱分值不受环境事实更正影响）。**Δ+0.3 的来源 = 记忆维度 +1 × 权重 10% = +0.10，叠加 v1.4 已记的 Skill 维度 +1 × 12% = +0.12，及四舍五入后的显示差**——是「单维小步 + 一处新维净增」，而非「全面跃升」。

## 5. 口径披露（单点分 vs 模型分 + 本轮两条新增披露）

> ⚠️ **本节是防止虚报跃升的必要声明，缺失即等于虚报。**

1. **旧口径（v1.3 及以前）**：dsh 在 KB 里只有「技术框架对照」的**单点分 2.5**，**硬编码在 `09-src-data/gen_html.py` 的 `FRAMEWORK_DATA`**——它**不是** 8 维模型的输出，没有硬门槛、没有权重、没有一票否决。
2. **新口径（v1.4 首次，v1.5 复评）**：v1.4 **首次**把 dsh 纳入 v2.0 精装度模型（硬门槛 + 8 维加权 + 一票否决），得官方 **3.6** / 装配层 **3.8**；v1.5 复评装配层 **3.9**（raw **3.85 → 3.9**），官方 **3.6**（raw **3.63 → 3.6**）**未变**。
3. **不可相减**：**3.6 与 2.5 不同源**（一个是模型加权输出，一个是框架对照单点判定），因此「2.5 → 3.6」这个差**在数学上不成立**，本文件拒绝给出该数字。旧单点分 2.5 作为**历史口径保留并标注**。
4. **同步校正**：v1.4 把 `FRAMEWORK_DATA` 里 opencode 的 **3.0 校正为模型口径 2.9**——原值属**口径漂移**（同一对象在两套口径下被写了两个数），已一并归位。
5. **未重算项**：**同模型下未重算 `0.1.1-rc.2`**（无当时证据可依），故「0.1.1-rc.2 → 0.2.1-alpha.2 的**模型分变化**」**不可得**；只给「**版本跨度 21 个预发布 + 机制增量清单**」，不给分值差。
6. **沙箱证据文本更正（v1.5 新增披露）**：v1.4 在 8 维依据与发现中写入「**本机无可用后端（bubblewrap/Landlock 均不可用）→ 实际 fail-closed**」。v1.5 实测**证伪**该断言：bwrap 已装、链选中 bwrap、`enforcement=full`、read-only / workspace-write 在 shell + fs 双侧真强制。⚠ 这是一次**环境事实更正**——它**不改变沙箱维度分值**（官方 4 / 装配层 4 / Δ0），因为 v1.4 的分值本就不依赖该断言，且该事实属**环境**而非**装配层能力增量**。⛔ 不得把它写成装配层收益，⛔ 不得据此调分。派生层若仍带该断言，属已登记的「陈旧断言」（check 19 覆盖）。
7. **skill 计数四口径（v1.5 新增披露）**：本库对 skill 规模**一律采用「派生目录口径」**，四个数各有定义，⛔ 不得混用、⛔ 不得互相推断：

   | 口径 | 定义 | v1.5 读数 | v1.4 时点值 |
   |------|------|---:|---:|
   | **主根** | `<root>/<name>/SKILL.md` 一层扫描（深度 2） | **49** | 45 |
   | **派生件** | 主根中**有** opencode 源者（`reconcile.py` 断言对象） | **47** | 45 |
   | **DSH 原生** | 主根中**无** opencode 源者（`dsh-config` / `dsh-reflection`） | **2** | 0 |
   | **模型可见** | 主根 − 带 `disable-model-invocation: true` 者（3 件 opencode 域技能） | **46** | 42 |
   | **叠加层** | `_overlay/<name>/SKILL.md`（深度 3），**不计入主根** | **6** | 6 |

   > 换算关系：**主根 = 派生件 + DSH 原生**；**模型可见 = 主根 − 3**。
   > ⚠ 源侧 `~/.config/opencode/skills/` 的目录数含 `_shared` / `disabled` 两个**非技能目录** ⇒「源侧目录数」≠「派生件数」，两者相差 2。
   > ⚠ 采集口径的唯一机械承载 = `07-checkpoint/snapshot_dsh_custom.py`（`inventory.json` 的 `skills_list` 段）；⛔ 任何口径改动必须经由该脚本，不得只在文档里改数字。
   > ⚠ **历史口径**：v1.4 文档通篇写「45 派生 / 42 可见 / 6 叠加」——那组读数的**主根**也是 45（当时主根 = 派生件，DSH 原生为 0）。v1.5 起主根与派生件**不再相等**（差 2 件 DSH 原生），故引用「45」时必须声明它指的是主根还是派生件。

## 6. 五大核心发现

**发现一：R 环迁移损失已追平——v1.4「最弱环 R=3.0、迁移损失」结论被推翻。**
v1.4 判定「提供 `reflection_add` / `reflection_mark` 的 `dsh-reflection` 插件随批次移出 ⇒ reflection 链路在 dsh 侧断裂、R 环维持 3.0」。**该结论已被 ADR-012 的 R-A 载体落地推翻**：`~/.dsh/MEMORY.md` 实际存在（**14 个 `§` 段 / 10815 B / 57 行 / 14 条 `[src:]` 签名**），`~/.dsh/reflection/candidates/` **15 份候选** + `archive/` **1 份**，`dsh-reflection` skill 在位（承载零和预算 / 生命周期五件 / 容量口径 `memory_capacity_check.py`），写入链为**显式链**「候选 → 主 Agent 审阅 → 落库」。⇒ R 3.0 → **4.0**，标注由「持平·迁移损失」改为**增强**。证据：`07-checkpoint/dsh-custom-snapshot/inventory.json`（`reflection` 段）；`…1011-全面适配性迁移分析/arch/ADR-012.json`（门控 6/6）；`bundle__persona.md` §十。

**发现二：E 环达反转阈值——v1.4 的抑制项已被 `run_gate` 消解。**
v1.4 的关键口径克制是「E 环 Δ+1.5 **只记增强、不记反转**」，理由是「门控脚本依赖 bash 而子 Agent 无 bash ⇒ 验证动作须由父层代跑」。**该抑制项已被 ADR-010 的窄通道消解**：`run_gate`（本地插件 `dsh-opencode-gate-runner`）实机生效，三 preset 各 +1 顶层 `gate-runner` 行；参数面受限——只收「脚本路径 + argv 数组」（构造上无 `-c`/`-e` 内联通路）、解释器按扩展名白名单（`.py`/`.js`/`.mjs`/`.sh`）、roots 白名单 realpath 后判定、超时 120s（上限 600s）、输出 16KB 封顶后 spill 至 `~/.dsh/spill/gate-runner/`；负向用例 **18 → 30** 条，`node --test` **57/57**。⇒ E 3.5 → **4.0**，Δ 达 **+2.0 反转阈值**，标注改为**反转**。证据：`…1011-迁移适配-E环门控通道与R环纠正/arch/ADR-010.json`（`status: proposed`）+ `ADR-010.md`；`…/evidence/gate-runner-unit-tests.out.txt`、`verify-gate-channel-live.out.txt`；`evidence/r11-final-gates.out.txt` §③ check 14。

**发现三：最弱环结论再次改变——R 与 E 并列 4.0，不再是单一最弱环。**
v1.4 的结论是「最弱环由 E 转移到 R」（R=3.0 独弱）。v1.5 两环同时上行（R +1.0、E +2.0）后**并列 4.0**，装配层综合分最低环**首次不再唯一**。这既是进步（两处结构性欠账同时补上），也是新的口径风险：**并列意味着「下一个瓶颈」需重新定位**——按当前分值，R 与 E 是唯二低于 5.0 的可动环，而 T 已封顶、SP/P 已满。证据：`09-src-data/dsh_custom_scores.py`（`RING_SCORES`）；`inventory.json`（`reflection` / `gate` 两段）。

**发现四：口径漂移是复评的主要风险——三处已实证。**
本轮实测出三处会静默失真的口径面：① **skill 计数四口径**（主根 49 / 派生 47 / 原生 2 / 可见 46；v1.4 时点 45/45/0/42）——v1.5 起主根 ≠ 派生件，引用「45」时不说清指哪个即出错（见 §5.7）；② **沙箱环境事实**——v1.4 写「本机无可用后端 → 实际 fail-closed」，实况是 bwrap `enforcement=full`（见 §5.6）；③ **两条线同名 ADR-011**——`Mission-file/2026-10/0928-前端设计方法论建设` 线与 `Mission-file/2026-10/1011-deepseek harness-提示词迁移工程-从opencode/1011-全面适配性迁移分析` 线**各有一份 ADR-011**（不同域），⛔ 引用一律**带路径限定**，否则必错指。证据：`00-contract/contract.md` §2.6（skill 计数口径唯一化）；`~/.dsh/skills/opencode/dsh-config/local/sandbox.md` + `conflicts.md`；两条线各自的 `arch/ADR-011.json`。

**发现五：文档 vs 实况冲突（v1.5 新增小节）——生成物仍带已过期的断言。**
本轮在取证中发现 bundle 自家文档与实况两处不符，**均未修**（属「登记不符」而非「回改历史文档」）：
- **`bundle README §5` 仍写 `defaultPreset: read-only`**（该节自述「原有三档与 `defaultPreset: read-only` 逐字保留」），而**实况已是 `opencode-plan`**（`profile__web-cordis.patch.yml` 的 `permission` 行 `defaultPreset: opencode-plan`）。⇒ 该句是 v1.4 时点的正确陈述、v1.5 时点的**过期陈述**。
- **`bundle README §8` 的 A5 / A6 行自标「两个数字都已过期」**——该行原文即承认：「45 件 / 0 件超限为第一轮门控结论；本轮未复算……⚠ 两个数字都已过期：源侧现为 **47 件**……本行只登记『未复算』这一事实」。v1.5 起该行更过期（主根 49 / 派生 47 / 可见 46），且该行未标 v1.5 版本号。

⚠ 这两处的共同成因与 §8.1 自陈的根因同源：**验收结论写死在 markdown 里，而判据是脚本**。处置：本文件只**登记冲突**并给出正确读数，⛔ 不回改 bundle 文档（不在本工程可改范围内）。证据：`07-checkpoint/dsh-custom-snapshot/bundle__README.md` 行 316/320-322 与行 400；`07-checkpoint/dsh-custom-snapshot/profile__web-cordis.patch.yml` 行 315-336；`…1011-迁移适配-E环门控通道与R环纠正/evidence/r11-final-gates.out.txt` §②（README §8 为生成物，20/20 自动跟随）。

## 7. 排名隔离声明

本文件评分的对象是**个人装配层变体**（`dsh-custom` = 官方内核 + `dsh-opencode-port` bundle + 宿主 profile patch），**不是市售产品**。因此：

- `dsh_custom_scores.py` **独立于 `premium_scores.PRODUCTS`**，其分值**不参与 14 产品市售排名**，不得与 `premium-map.html` / `premium-cyto.html` 中的产品分同轴比较；
- 官方 `dsh` 与 `dsh-custom` 构成**同源对照对**（同一内核、同一模型、同一权重），只回答「装配层带来多少增量」，不回答「dsh 在 14 产品中排第几」；
- 与 `opencode-custom` 专题同构：两个装配层变体分属两个宿主，**跨宿主比 Δ 有意义，比绝对值无意义**（基线不同、可用机制不同）。

<details>
<summary><b>历史块 · v1.4 口径（2026-10-11 时点值，保留不改，⛔ 不得与 v1.5 值相减）</b></summary>

> 本块逐条保留 v1.4 的原始读数与原始结论。v1.4 快照时点 = **2026-10-11T17:09:09**；旧快照归档于 `archive/1011-KB-v1.4-dsh装配与opencode追平/dsh-custom-snapshot-v1.4/`。⛔ 与 v1.5 值**不同时点、不可相减**。

**① 精装度**：官方 **3.6**（raw 3.63）/ 装配层 **3.8**（raw **3.75**），**Δ+0.2**；档位「成品化受限」，均未跨档。

**② 8 维（官方 / 装配层 / Δ）**：多Agent编排 16% 4/4/0 · **Skill库 12% 3/4/+1** · 工作流 13% 4/4/0 · 模型接入 14% 4/4/0 · 一键部署 15% 3/3/0 · 沙箱 10% 4/4/0 · MCP生态 10% 3/3/0 · **记忆 10% 4/4/0**。

**③ 五环双层（官方 → 装配层）**：SP 4.5 → **5.0**（+0.5）· M 4.0 → **4.0**（0）· P 4.5 → **5.0**（+0.5）· R 3.0 → **3.0**（0，持平·迁移损失）· T 5.0 → **5.0**（0）· E 2.0 → **3.5**（+1.5，增强**非反转**）。

**④ skill 计数**：**45** 派生（主根）/ 模型可见 **42** / `_overlay` **6**；DSH 原生 **0**。

**⑤ 判据项数**：`verify_bundle.py` **13** 项（`evidence/verify-bundle-13checks.out.txt`）。

**⑥ 规模与结构**：persona **15403 B**（15 节）/ profile patch **17538 B** / bundle README **22168 B**；preset 顶层插件行 **21/22/22**、递归子行 34/35/35；`plugin_manager` 计数 **188 → 191**；`defaultPreset: read-only` 未变。

**⑦ 旧结论（v1.5 已推翻或更正，此处保留原文口径）**：
- **「最弱环转移到 R（迁移损失）」**——R 环 reflection 链路在 dsh 侧断裂，`dsh-reflection` 插件已移出，persona 的 MEMORY/reflection 段不可用；R 维持 3.0。
- **「E 环只判增强、不判反转」**——门控脚本依赖 bash 而子 Agent 无 bash（仅 read/write/edit/glob/grep），`gate_architecture.py` 无法在子 Agent 内自跑，Δ+1.5 未达 Δ≥2.0 阈值。
- **「沙箱本机无可用后端（bubblewrap/Landlock 均不可用）→ 实际 fail-closed」**——v1.5 已证伪（bwrap 已装、`enforcement=full`）。
- **「bundle 自家门控曾假阳性 FAIL」**——原判据对活文件取整文件 sha256，GUI 写回一个 `ui-theme.fontSize` 即指纹漂移 ⇒ 已改为 `scoped_digest`，只判 bundle 实际消费字段。

</details>

### 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S1 | 可复算评分（单一数据源） | `09-src-data/dsh_custom_scores.py`（官方 **3.6** / 装配层 **3.9**，8 维 + 五环 + SP 分值权威来源） | 高 |
| SRC-002 | S1 | 评分模型 | `07-checkpoint/premium-scoring-model.md`（精装度 v2.0：硬门槛 + 8 维加权 + 一票否决） | 高 |
| SRC-003 | S4 | 一手装配观察 | `~/.dsh/presets/opencode/cordis.patch.yml`（3 preset / persona 行 / delegation 组 12 子行 / `toolFilter.deny` / 顶层行 23/24/24） | 高 |
| SRC-004 | S4 | 一手 persona 观察 | `~/.dsh/presets/opencode/persona.md`（15 节 / **12066 B** 单一来源） | 高 |
| SRC-005 | S4 | 一手宿主 patch 观察 | `~/.dsh/profiles/web/cordis.patch.yml`（permission 5 档 + **`defaultPreset: opencode-plan`** + 4 provider + `reasoningEfforts` 三档 + `maxTokens` 32768 + plugin-manager `pnpmCommand` + plan:policy 2515 字符） | 高 |
| SRC-006 | S4 | 一手静态校验 | `…1011-deepseek harness-提示词迁移工程-从opencode/evidence/verify-bundle-13checks.out.txt`（v1.4 口径 13 项）；**v1.5 现行为 20 项**，见 SRC-014 与 SRC-019 | 高 |
| SRC-007 | S4 | 一手运行时探针 | `…/evidence/session-probe-{builtin-standard,opencode-standard,opencode-creator,opencode-ptc}.json`（工具数 31/37/40/1、系统提示字符数；**v1.4 读数，v1.5 未复算**） | 高 |
| SRC-008 | S4 | 一手 skill 取证 | `…/evidence/skill-catalog-runtime.txt`、`skill-reconcile.out.txt`、`a10-negative-skill-gate.out.txt`（v1.4：45 派生 / 可见 42 / 门控 0 问题） | 高 |
| SRC-009 | S4 | 一手作用域取证 | `…/evidence/a12-persona-scope.out.txt`（persona 遮蔽 host personaPrefix 2790/8 小节；含 5 条负向用例） | 高 |
| SRC-010 | S4 | 一手插件计数 | `…/evidence/plugin-preset-rows.txt`（三行 `enabled=true`/`active`；v1.4 口径插件总数 188 → 191） | 高 |
| SRC-011 | S4 | 一手迁移报告 | `…1011-…-从opencode/report.md`（§3.5 权限 5 档 / §3.10 运行时验收 / §3.8 加载失败事故与门控加固） | 高 |
| SRC-012 | S4 | 对照基线 | `03-cases/deepseek-harness.md`（官方 dsh 五环结构与结论口径，基线 v0.2.1-alpha.2） | 高 |
| SRC-013 | S1 | 口径历史值 | `09-src-data/gen_html.py` `FRAMEWORK_DATA`（dsh 旧单点分 2.5、opencode 校正 3.0 → 2.9；**与模型分不同源**） | 高 |
| SRC-014 | S4 | **本库脱敏快照（入库，v1.5 新快照）** | `07-checkpoint/dsh-custom-snapshot/inventory.json` + `manifest.json`（`collected_at` = **2026-10-13T05:09:43+08:00**；含 `skills_list` / `plugins` / `reflection` / `gate` 四段——主根 49 = 派生 47 + 原生 2 / 可见 46 / 宿主插件 1 + bundle 插件 2 / MEMORY.md 14 段 10815 B 57 行 / `check_count` 20。旧快照归档于 `archive/1011-KB-v1.4-dsh装配与opencode追平/dsh-custom-snapshot-v1.4/`） | 高 |
| SRC-015 | S4 | 一手 ADR（E 环门控通道） | `Mission-file/2026-10/1011-迁移适配-E环门控通道与R环纠正/arch/ADR-010.json`（`status: proposed`；`run_gate` 窄通道）+ 同目录 `ADR-010.md` / `evidence/gate-runner-unit-tests.out.txt` / `verify-gate-channel-live.out.txt` | 高 |
| SRC-016 | S4 | 一手 ADR（`dsh-config` 能力包） | `Mission-file/2026-10/1011-deepseek harness-提示词迁移工程-从opencode/1011-全面适配性迁移分析/arch/ADR-011.json`（`status: proposed`、门控 6/6）。⚠ **路径限定必带**：`Mission-file/2026-10/0928-前端设计方法论建设` 线有**同名 ADR-011**（不同域） | 高 |
| SRC-017 | S4 | 一手 ADR（R-A 记忆载体） | `Mission-file/2026-10/1011-deepseek harness-提示词迁移工程-从opencode/1011-全面适配性迁移分析/arch/ADR-012.json`（`status: proposed`、门控 6/6） | 高 |
| SRC-018 | S4 | 一手迁移台账 | `Mission-file/2026-10/1011-deepseek harness-提示词迁移工程-从opencode/1011-全面适配性迁移分析/迁移台账.yaml`（**43 任务：done 36 / partial 2 / not_done 3 / deferred 1**） | 高 |
| SRC-019 | S4 | 一手收官取证 | `Mission-file/2026-10/1011-deepseek harness-提示词迁移工程-从opencode/1011-全面适配性迁移分析/evidence/r11-final-gates.out.txt`（`verify_bundle.py` **20 项**全过；`verify_dsh_config.py` PASS + 负向 15 用例；`reconcile.py` PASS；`gate-runner` 单测 57/57、`commands` 单测 6/6）、`evidence/r11-migration-audit.json`、`迁移完成度审查报告-v10.md` | 高 |
