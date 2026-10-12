# 执行计划 — 控制理论 ⊗ Agent 设计知识库 v1.5「dsh 装配层二次追平」

> 任务：`0907-控制理论Agent设计知识库` v1.4.0 → **v1.5**
> 创建：2026-10-13　负责人：主 Agent
> 留档目录：`Mission-file/2026-10/1011-KB-v1.4-dsh装配与opencode追平/1013-v1.5-dsh装配二次追平/`（用户裁定：沿用上次 dsh 重分析任务留档目录并建子目录区分）
> 计划依据：用户三项裁定（目标 = `zako-mio/control-theory-agent-kb`；范围 = 全量 v1.5；冻结点 = 等迁移线第 10 轮落地后取快照）
> 方法论承载：`version-upgrade-cascade`（级联更新）、`dsh-config`（装配分层实况）

---

## 一、任务定位

n**一句话**：DSH 的「能力装配迁徙」在 KB v1.4 之后又经历了 11 轮调整优化，本轮回填这些事实、复算评分与五环判定，把 KB 的 dsh 部分从 v1.4 快照点追平到冻结点。

**为什么不是「只刷新 evidence」**：v1.4 的三条结论已被现实推翻或需重判（见 §六），按契约 §2.7④「装配层发生能力纵深增长 / 机制新增时触发复评」，本轮属**实质复评**而非维护性刷新。

**与相邻工作线的边界**：
- 本轮回**只读**对待 `~/.dsh/**`——是「分析 DSH」，不是「改 DSH」；
- 迁移线（`1011-deepseek harness-提示词迁移工程-从opencode/`）负责改装配层；本线只消费其结果并留证；
- 两侧**互不阻塞**，但本线 Phase 2 取快照须落在迁移线的静止点（见 §十 风险 1）。

---

## 二、三项已裁决策（用户 2026-10-13 逐项选定）

| # | 决策 | 取值 |
|:--:|---|---|
| D1 | 目标项目 | `zako-mio/control-theory-agent-kb`（本地 `.../0907-控制理论Agent设计知识库/`） |
| D2 | 范围 | **全量 v1.5**：证据层重算 + 评分重算 + 画像/diff/页面/实验/级联/门控 |
| D3 | 冻结点 | 等迁移线第 10 轮（行为验收收尾）落地后再取快照 → **实际状态见 §五 注** |

---

## 三、触发判据与定档

### 3.1 触发判据（契约 §2.7④）

| 判据 | 实例 | 结论 |
|---|---|---|
| 内核升版 | dsh `v0.2.1-alpha.2`（`d743267`，2026-10-09）**未变** | 不触发 |
| 装配层「能力纵深增长 / 机制新增」 | ① `run_gate` 窄通道（新对外工具 + 新插件）② `dsh-config` skill v1.0（新技能层）③ `dsh-context`/R-A 载体（新记忆写入链）④ `dsh-wsl-desktop-path`（新插件）⑤ `verify_bundle` 13→19 项 ⑥ 沙箱由「无后端」变为 `bwrap enforcement=full` | **触发** |

### 3.2 定档

- **复杂度自评 16/20**（影响范围 4 · 逻辑深度 4 · 操作数量 5 · 风险精度 3）→ 高复杂度，按最深推理档执行。
- **架构分档：门控级**。规模三问 Q2（跨 ≥2 模块：数据层/交付层/契约/门控层）、Q3（公开仓已发布，反转成本高于改回配置）命中 ⇒ 三步不得跳过：① 加载 `architecture-judgment` ② 委派 `oc_architect` ③ `gate_architecture.py` PASS 前不得交付。

---

## 四、基线

### 4.1 KB 侧（v1.4.0，2026-10-11）

| 项 | 值 |
|---|---|
| 规模 | 6 框架 + 14 精装房 + 2 装配层变体（`opencode-custom` / `dsh-custom`）；`04-interactive` 42 页 |
| 覆盖率期望清单 | `07-checkpoint/coverage-manifest.txt` 112 项 |
| 信源分母 | 24 份画像（6 + 14 + 2×2） |
| 门控 | L1–L7 全开 ALL PASS（6 层，issue 0，warning 3 类） |
| 官方 dsh 画像 | 精装度 **3.6**（raw 3.63）；五环 SP 4.5 / M 4.0 / P 4.5 / R 3.0 / T 5.0 / E 2.0 |
| `dsh-custom` 变体 | 精装度 **3.8**（raw 3.75，Δ+0.2，8 维仅 Skill 3→4）；五环 SP 5.0 / M 4.0 / P 5.0 / R 3.0 / T 5.0 / E 3.5 |
| 关键结论 | 官方最弱环 E(2.0) 升 3.5 后，**最弱环转移到 R(3.0，迁移损失)**；「强内核 + 薄装配层」范式 |
| 口径披露 | 旧单点分 2.5（`gen_html.py` FRAMEWORK_DATA）与新模型分 3.6 **不同源、不可相减** |

### 4.2 快照点（v1.4 证据层基准）

`07-checkpoint/dsh-custom-snapshot/`：`collected_at = 2026-10-11T17:09:09+08:00`，9 件脱敏件 + `inventory.json` + `manifest.json`（逐件 `sha256_16`）。
其中 `inventory.json` 记：presets 3（order 11/12/13）、worker 别名 6、permission 5 档、**skills 主根 45 / overlay 6 / 模型可见估计 42**。

---

## 五、v1.4 快照后的装配层轮次（按磁盘时间戳重建）

> ⚠ 两条编号并行，勿混：**本表 R#** 为按文件时间戳重建的「装配层变更轮」；迁移线自述轮次为 **09 / 10 / 11**（见末列）。

| R# | 时点 | 装配层变化（磁盘实测） | 证据 |
|:--:|---|---|---|
| R1 | 10-11 17:16–17:20 | 思考档 `reasoningEfforts` + 子 Agent 能力上限（subagentcap） | `.bak-thinking-subagentcap-20261011-171649`、`.bak-subagentcap-20261011-172007` |
| R2 | 10-11 18:07 | **E 环门控执行通道 `run_gate`（ADR-010）**：三 preset 各 +1 顶层 `gate-runner` 行（本地插件 `dsh-opencode-gate-runner`） | `.bak-gatechannel-20261011-180758`；`1011-迁移适配-E环门控通道与R环纠正/` |
| R3 | 10-11 19:46–19:48 | 重挂 `dsh-wsl-desktop-path`（web + headless），修 explorer.exe ENOENT | `.bak-wslpath-20261011-194630` / `-194846` |
| R4 | 10-12 08:32–08:41 | **`dsh-config` skill v1.0（ADR-011，门控 6/6）**；机器事实外迁 `local/host-env-facts.md`；服务重启 08:41:06 | `.bak-dshconfig-20261012-083240` |
| R5 | 10-12 09:31Z | **R 环 R-A 文件载体（ADR-012，门控 6/6）**：14 份候选 + `MEMORY.md` 正文 14 段/10815 B + `dsh-reflection` skill | `~/.dsh/reflection/`、`~/.dsh/MEMORY.md` |
| R6 | 10-12 15:46–15:50 | **`verify_bundle` 13 → 19 项**；persona E5 收敛（字符 9034 → 6524） | `.bak-dshconfig-20261012-154654` / `-155059` |
| R7 | 10-12 16:07 | 模型路由：`maxTokens` 8192→32768（撤销「方案 D」）、`reasoningEffort` max→high、`v4-flash` 16384→32768 | `1012-dsh长输出截断根因诊断/` |
| R8 | 10-12 17:16 | R09 收尾：`install.py` 变换表、`_overlay/pdf-ocr` scripts、`run_gate` 负向 18→30、`verify_bundle` 19/19 | `install.py.bak-r09-20261012-171611` |
| R9 | 10-12 17:40–18:11 | E3 residue **119 → 0**；R-A 落库取证；E6 PDF/OCR；E9；审查接 check 19 | `r09-*.out.txt`、`执行E3E4-report.md` |
| R10 | 10-12 18:55–19:13 | 行为验收收尾（5 条请求 × 逐条会话；`search-methodology` 未加载为本轮重测项） | `r10-behavioral.out.txt`（19994 B）、`迁移台账.yaml` 19:13 |
| R11 | **10-13 02:37–（进行中）** | caps 台账统一 + 审查脚本与唯一源单口径控制（1 正控 4 负控全过） | `r11-caps-ledger.out.txt`、`r11-audit-unify.out.txt` |

### 5.1 文件级差量（快照 → 2026-10-13 02:40 实测）

| 文件 | 快照 | 现在 | 变化要点 |
|---|---|---|---|
| bundle `cordis.patch.yml` | 93283 B / 1305 行 | 85501 B / 1299 行 | +`gate-runner`×3；persona prefix 段 −33 行×3 |
| bundle `README.md` | 22168 B / 324 行 | 40812 B / 530 行 | +§3.2/§3.3/§4.2/§10.1；**§4.1「无沙箱后端」结论被推翻** |
| bundle `persona.md` | 15403 B | 12066 B | §八 外迁；§十一~十三 收敛为祈使句/点名式 |
| bundle `ADAPTATION-NOTES.md` | 9108 B | 10913 B | 反思写入链行重写为 ADR-012/R-A |
| bundle `provenance.json` | 11907 B | 12209 B | 生成物，指纹条目 +1 |
| bundle `PROVENANCE.md` | 5692 B | 5994 B | 字节微增（内容差异待复核，见 §十一 未决项 U3） |
| bundle `package.json` | 392 B | 392 B | 逐字未变 |
| profile `cordis.patch.yml` | 17538 B / 282 行 | 25569 B / 372 行 | +`dsh-wsl-desktop-path`(insert)、+`agent-preset-registry`；`defaultPreset` read-only→**opencode-plan**；+`reasoningEfforts` 三档；maxTokens 回调 |
| 派生 skill（主根含 SKILL.md） | 45 | **49** | `+dsh-config`、`+dsh-reflection`、`+browser-harness` 等；`_overlay` 6→7 |
| 门控 | 13 项 | **19 项** | `verify_bundle.py CHECK_TITLES` 19 条；新增 6 个 `verify_*` 引擎 |

### 5.2 注（D3 冻结点实际状态）

用户裁定的冻结条件是「迁移线第 10 轮落地」；**该条件已于 2026-10-12 19:13 满足**，但该线随即进入 **R11（caps 台账统一）**，`~/.dsh/presets/opencode/verify_migration_state.py` 至 **02:48 仍在增长（58080 B）**。
⇒ 取快照前须就「R11 是否已收尾」重新判一次静止点（P0-2）。

---

## 六、必须重判的三条旧结论（本轮实质内容）

| # | v1.4 旧结论 | 现实 | 影响的评分面 |
|:--:|---|---|---|
| C1 | 「**本机无可用沙箱后端**（bubblewrap / Landlock 均不可用）」 | 已被证伪：`bwrap` 已装、链选中 bwrap、`enforcement=full`，read-only / workspace-write 在 shell+fs 双侧真强制 | **沙箱维（权重 10）+ T 环** |
| C2 | 「**R 环迁移断裂**，`dsh-reflection` 插件移出后 persona 记忆段不可用，最弱环 R=3.0」 | R-A 文件载体已落地（ADR-012 6/6）：候选目录 + 落库链 + skill；`MEMORY.md` 正文已落 | **R 环（本轮预期上移）+ 记忆维（权重 10）+「最弱环」结论** |
| C3 | 「子 Agent 无 shell ⇒ 门控脚本无法在子 Agent 内自跑，E 环只判增强不判反转」 | `run_gate` 窄通道（ADR-010）已实机生效（脚本路径 + argv 数组，roots/扩展名白名单，负向 30 条） | **E 环口径 + T 环工具面** |

另需登记（不算重判，但属文档 vs 实况冲突，须在 diff 中显式写出）：
- `README §5` 仍写 `defaultPreset: read-only`，profile 实况已是 `opencode-plan`；
- skill 计数**四套口径并存**：快照 45 / README 46 / `reconcile` 47 / 实测主根 49 ⇒ 见 P0-1。

---

## 七、阶段 P0–P7

| Phase | 输入 | 动作 | 产出 | 完成判据 |
|---|---|---|---|---|
| **P0 前置门** | 本计划 §五/§六 | ① **口径统一**：定「skill 计数」唯一口径并说明其余口径差异 ② **重新判静止点**（R11 是否收尾）③ 确认迁移线外部证据指针可引用（ADR-010/011/012、`迁移台账.yaml` 34 条、`r09*.out.txt`/`r10*`/`r11*`） | 口径决议（写入契约 §2.7） | 三项均有书面结论；口径无二义 |
| **P1 契约刷新** | P0 决议 | ① 判定 §2.7④ 触发成立 ② `00-contract/contract.md` §2.6/§2.7 刷新（版本号 v1.4→v1.5、基线、口径）③ **§2.7⑤ 补账义务**：R1–R11 全轮次显式补入 ④ 口径变更披露表（C1–C3 逐条「旧→新 + 证据指针」，不可相减项显式声明） | 契约 v1.5 | §2.6/§2.7 与 §八 级联清单逐条对齐；无「静默跳过」 |
| **P2 证据层全量重算** | 静止点 | ① 重跑 `snapshot_dsh_custom.py`（脱敏）取新快照，旧快照移入 `archive/` 或加历史标注 ② **补 v1.4 缺失的三个取证面**：skill 清单（逐项）、插件面（`~/.dsh/plugins/` + bundle `plugins/`）、R 环载体**存在性与容量**（⛔ 正文不入公开库）③ 收录 `verify_bundle` 19 项 CHECK_TITLES | 新快照 + 证据包 | 快照 `collected_at` 为静止点；`manifest` 逐件 sha256 可复算；脱敏红线 0 违例 |
| **P3 评分层重算** | P2 证据 | 8 维逐维重判（重点 Skill 库 / 沙箱 / 记忆 / MCP / 工作流）+ 硬门槛重验 + 五环双层重判（E、R、T 因 C1–C3） | 新版 `09-src-data/dsh_custom_scores.py` + 口径变更披露表 | 数值全部由脚本涌现（⛔ 禁手改）；未跨档则明写「维持」，跨档须给量化证据 |
| **P4 差量分析** | P3 | ① `03-cases/dsh-custom.md` 增「R1–R11 轮次表」+ 更新五环/8 维 ② `dsh-custom-diff.md` 双层 delta 全量重算 + 「文档 vs 实况冲突」小节 ③ `deepseek-harness.md` **只补指针与历史块**（内核未变，不重算 3.6） | 3 份画像 MD | 画像结论与证据文件强制一致（契约画像模板）；环标题标记齐备 |
| **P5 交付层全量更新** | P4 | ① 数据层 `gen_html.py` / `nav_data.py` / `gen_coverage_manifest.py` / `dsh_custom_scores.py` ② **全量重生成** `04-interactive/*.html` ③ 实验层**只补新机制**（`run_gate` 窄通道 / R-A 落库链 / bwrap full enforcement / `dsh-config` 账本门控），历史实验 11–14 保留原版本号 + 历史块 ④ 门户 README / index / 00-index 三处登记 | 5 页面 + 1 实验 + 索引 | 生成物 100% 由脚本产出（⛔ 禁只改生成物）；实验编号不重跑 |
| **P6 门控 + 级联** | P5 | ① `kb_gate.py` 六层全开 ② **级联 12 项检查表**逐条 ③ 覆盖率清单登记新增项 ④ `check_premium_consistency.py` + 评分复算 ⑤ headless + 视觉 L4/L5 ⑥ **判据锚点复核 + 负向控制**（迁移线教训：锚点错位＝结构性假绿） | 门控报告 | 六层 ALL PASS、issue 0；版本标识残留 **0**；判据「能 FAIL」有正例 |
| **P7 交付 + 推送** | P6 | ① 留档本目录（5 段报告双版本 + 证据）② `git commit` + push → GitHub Pages 生效验证 ③ 归档回 KB `archive/` | 留档 + 远端 | 5 段齐备；Pages 页面可访问且版本标识为 v1.5 |

---

## 八、级联与门控清单

- **级联半径**：`09-src-data/{nav_data, gen_html, dsh_custom_scores, gen_coverage_manifest, snapshot_dsh_custom}.py` → 全量重生成 → `07-checkpoint/{coverage-manifest.txt, kb_gate.py, check_premium_consistency.py}` → `00-contract/contract.md` + `README.md` + `05-md/00-index.md` + `index.html`
- **级联 12 项检查表**：见 `07-checkpoint/audit-report-v1.1.md`（品牌口径 / 页脚版本 / 总览版本与洞察 / 交互图侧边栏 / 框架页页脚 / 门户入口 / 实验组 README / 旧报告历史标注 / audit 报告历史标注 / `05-md/00-index.md` / `premium-cyto` 统一 sidebar+页脚 / `index_cyto` 页脚）
- **评分模型**：`premium-scoring-model.md` v2.0 —— 硬门槛（端到端零配置可跑 0/1，FAIL 封顶 3.0）+ 8 维加权（多Agent 16 / 一键部署 15 / 模型 14 / 工作流 13 / Skill 12 / 沙箱 10 / MCP 10 / 记忆 10）+ 一票否决（声称失实封顶 4.0 / 纯中转封顶 3.5）；`final = round(min(raw, 各封顶), 1)`

---

## 九、红线

1. **对 `~/.dsh/**` 绝对只读**——本轮是「分析 DSH」，不是「改 DSH」；
2. **不触碰 `/home/zako-mio/dsh`**（该检出已有 18 项未提交改动，属他线）；
3. **不触碰迁移线的任务目录**（`1011-deepseek harness-提示词迁移工程-从opencode/**`）——只读引用；
4. 契约 §2.7③ 脱敏：密钥一律 `<REDACTED>`；`MEMORY.md` 正文**不入公开库**（`.gitignore` 排除）；
5. 评分数值必须由 `dsh_custom_scores.py` 涌现，**禁手改**；生成物必须由生成脚本重生成；
6. `dsh-custom` 维持**排名隔离**，不参与 14 产品市售精装度排名；
7. 不可逆操作（`rm` 非 `/tmp`、改记忆系统文件）一律先问。

---

## 十、风险与对策

| # | 风险 | 等级 | 对策 |
|:--:|---|:--:|---|
| 1 | **动目标**：迁移线 R11 仍在改写装配层（`verify_migration_state.py` 02:48 仍增长） | 高 | P0-2 重新判静止点；必要时以 `as_of` 取快照并在 KB 内显式登记「他线可能并发变更」 |
| 2 | **口径漂移**：skill 计数四套（45/46/47/49）、两条线各有一个 `ADR-011` | 中 | P0-1 定唯一口径写入契约；KB 深链一律带路径限定 |
| 3 | **门控假绿**：判据锚点错位（迁移线已两次实证） | 中 | P6 增设「判据锚点复核 + 负向控制」，⛔ 不接受「只跑绿」 |
| 4 | **跨线编号混淆**：本表 R# 与迁移线 09/10/11 双轨 | 低 | 所有引用带时点；报告内统一以「时点 + 留档路径」定位 |
| 5 | **沙箱结论反转的连带**：C1 若引起 T 环与沙箱维上调，可能跨档 | 中 | 按 §2.7④ 诚实口径：跨档须给量化证据，不虚报跃升 |

---

## 十一、未决项（待 P0 收口或用户裁定）

- **U1** skill 计数唯一口径（目录数 / 含 `_overlay` / 模型可见数）——建议以「模型可见技能数」为对外口径并附全量清单；
- **U2** 「最弱环」结论是否随 C2 一并改写（R 环由 3.0 上移后，最弱环可能回到 E 或其他）；
- **U3** bundle `PROVENANCE.md` 字节微增但被初判「逐行同文」——须复核实测差异；
- **U4** P4 中 `deepseek-harness.md`（官方画像）边界：内核未变，是否允许「只补指针」而不重算 3.6；
- **U5** 是否把迁移线 `迁移台账.yaml`（34 条）登记为 KB 的外部证据源（引用而不复制）。

---

## 十二、预计产物

| 类别 | 产物 |
|---|---|
| 契约 | `00-contract/contract.md` v1.5（§2.6/§2.7 刷新） |
| 证据 | 新 `dsh-custom-snapshot/`（含 inventory/manifest）、插件面与 skill 面取证件、R 环容量取证件 |
| 评分 | 新版 `09-src-data/dsh_custom_scores.py` + 口径变更披露表 |
| 画像 | `03-cases/dsh-custom.md`、`dsh-custom-diff.md` 更新；`deepseek-harness.md` 补指针 |
| 页面 | `case-dsh-custom.html`、`compare-dsh.html`、`exp-dsh-custom.html`（+ `case-dsh.html` 如官方侧指针变） |
| 实验 | `06-experiments/dsh-custom.md` 新机制章节（不重跑 11–14） |
| 索引 | `README.md`、`index.html`、`05-md/00-index.md` |
| 门控 | 六层结果 + 级联 12 项 + 渲染/视觉验证 |
| 留档 | 本目录 `report.md` / `report.html` + 证据 |
