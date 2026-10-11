# 任务完成报告 — KB v1.4「dsh 装配层立像 + opencode 月度追平」三库分批级联更新

> AI 友好留档版（人类可读版见同目录 `report.html`）
> 版本：v1.4.0　完成日期：2026-10-11　负责人：主Agent
> 复杂度自评：**19/20**（影响范围 5 · 逻辑深度 5 · 操作数量 5 · 风险精度 4）→ 高复杂度
> 架构分档：**咨询级**（三问全不触发——不改任何系统模块/接口，仅更新分析产物，未走门控）
> 留档位置：`Mission-file/2026-10/1011-KB-v1.4-dsh装配与opencode追平/`

---

## 1. 当时情况

### 1.1 用户原始需求

> 「这是一个我的 github 项目的一个分析，现在我们的 dsh 有所装配，然后也经历了大量更新，opencode 也有变动，所以需要将这些部分重新分析，你先了解情况，然后制定计划」

经口径澄清后确定为：**三个库全动、分批执行、顺序由主 Agent 决定**；并追加两条执行纪律——**不需要停顿**、**控制主 Agent 上下文长度**（成熟任务可交子 Agent 并配辅助子 Agent，即深度 2）。

### 1.2 勘查后的三个关键发现（决定了本轮范围）

1. **两库存在「一个月 backlog」**：`control-theory-agent-kb`（下称 KB）与 `opencode-dag-analysis` 都停在 **2026-09-11 23:04**（v1.3）。而 `Mission-file/2026-09/0914-自改造opencode再评估v1.4/report.md` 明确记载「**不更新知识库**（按用户口径）」——即 0914 那次全量复评（11 agent / 43 可加载 skill / 3 cmd / 6 instr / 6 MCP / 4 provider / 16 model / 32 variant / 9 script）**从未入库**；此后还叠加了 0913 前端三层栈（→0916 退役）、0915 vision-worker 退役、0921 需求发现三层栈、0926 通知插件、0927 provider 拆分、1010 MEMORY 生命周期治理。⇒ 本轮不是「点检」，是**补一个月的账**。
2. **dsh 侧跨代**：KB 的 dsh 画像锁 `v0.1.1-rc.2`（2026-08-21，精装度单点分 2.5，最弱 E 环）；当前源码树 `dsh-v0.2.1-alpha.2`（2026-10-09，commit `d743267`），中间跨 **21 个预发布 tag**。
3. **dsh 出现全新维度「装配层」**：`~/.dsh/presets/opencode/`（bundle `dsh-opencode-port`，2026-10-11 安装）把 opencode 的行为纪律 + 45 skill + 7 角色迁为 dsh 的 3 个自定义 preset；`~/.dsh/plugins/` 已空（8 个自装插件 2026-10-10 移出）。KB 对此**零记录**，而 opencode 侧早有对等的 `opencode-custom` 变体专题 ⇒ dsh 侧缺一个同构条目。

### 1.3 环境事实（实测，非推断）

| 事实 | 值 | 影响 |
|---|---|---|
| 三库状态 | KB `main`=83d02b3 / opencode-dag `main`=6e02692 / dsh-plugin-dag `v0.2.1-alpha.2`=af5b963 | 工作区均干净 |
| dsh-plugin-dag 分支 | **已在远端**（`rev-list --left-right` = `0 0`） | 该项收尾已是 no-op，仅需复核 |
| 深度 2 委派 | **不可用**：`subagent depth 2 exceeds maxDepth 1` | 分片改用 `workflow` 预案 |
| 子 Agent 工具面 | 有 read/write/edit/glob/grep，**无 bash** | 脚本执行/门控/git 全部由主 Agent 承担 |
| 视觉能力 | **可用**（`read_image` 成功并正确描述页面） | L4 视觉层由主 Agent 自看，不委派、不交人看 |
| 沙箱后端 | 无 bubblewrap / Landlock | `workspace-write` 档 bash 被 fail-closed；须 `danger-full-access` |
| snap chromium | 容器内缺 `cap_dac_override`，无法启动 | 渲染统一走 playwright 自带 chrome-for-testing |

---

## 2. 制定计划

### 2.1 关键决议（主 Agent 拍板，已在 PLAN 中列明）

| # | 决议 | 理由 |
|:--:|---|---|
| D1 | KB 版本 = **v1.4.0**；装配层复评轮次独立编号（0911=v1.3 已入库 / 0914=v1.4 **未入库** / 本轮=轮 v1.5 快照） | 避免「库版本号」与「复评轮次号」两条谱系混淆 |
| D2 | dsh 装配层**单独立像 `dsh-custom`**，与 `opencode-custom` 并列，同为不参与市售排名的变体 | 与既有契约 §2.6/§2.7 同构；折叠进官方画像会掩盖「内核 vs 装配层」对照价值 |
| D3 | opencode 官方基线取 **1.18.35（本机运行时）**，上游 `v1.19.0` 只登记不追 | 一贯口径是「本地可实证的运行时」；1.19.0 未安装、无本地证据 |
| D4 | 分批顺序 **B1 dsh(KB) → B2 opencode(KB) → B3 opencode-dag 重建 + 三库推送** | B1 证据最新鲜；B3 依赖 B2 刷新后的 inventory |
| D5 | dsh-plugin-dag **只推版本分支**，`master` 不动 | 该库历史惯例即「每版一支」，且无 Pages workflow |
| D6 | 不重启 `dsh-web.service` | 需 root 且会中断当前会话；仅登记 |
| D7 | 不写任何记忆文件 | DSH 侧无反思写入链；`MEMORY.md` 与 `pending.json` 只读 |

### 2.2 分批与委派设计

| 批次 | 内容 | 委派 |
|---|---|---|
| B0 | 能力探针（深度 2 / 视觉）+ 三库状态核对 + 留档目录 | 主 Agent + 1 探针子 Agent |
| B1 | dsh 侧：证据采集 → 数据层 → 画像 → 页面 → 门控 | 3× `oc_explore`（只读取证）+ 4× `subagent`（内容创作）+ 主 Agent（脚本/门控） |
| B2 | opencode 侧：快照刷新 + 分值口径 + 画像/diff/实验 + 页面 + 门控 | 4× `subagent` + 主 Agent |
| B3 | opencode-dag：官方点检 + 装配层重建 + 三图重生成 + 门控 + 推送 | 1× `oc_explore` + 2× `subagent` + 主 Agent（管线/推送） |
| B4 | 双版本 5 段报告 + 留档 | 主 Agent |

**上下文控制手段**：子 Agent 承担长文本创作与代码编辑（其上下文独立）；主 Agent 只持有结论与指针，并串行执行唯一需要 bash 的部分（生成/门控/git）。

---

## 3. 执行情况

### 3.1 B0 前置（完成）

- 深度 2 探针 → **失败**（`maxDepth 1`）→ 记录并启用 `workflow` 预案（本轮实际未触发，因任务可拆为「子 Agent 写、主 Agent 跑」两层）。
- 视觉探针 → **成功**；三库状态核对 → 全部干净；**修正 D5**：dsh-plugin-dag 分支已在远端。
- 留档目录 + git 基线前像（三库 commit sha 记于 `evidence/baseline-commits.txt`；git 树本身即回滚手段）。

### 3.2 B1 dsh 侧（完成）

**证据采集**（3 个只读子 Agent 并行，全部返回源码级/文档级 `file:line`）：

- **E 环 → 部分修正**：发现 `packages/experimental/auto-review/`——一个**真实存在的独立 LLM 审查器**（`REVIEW_POLICY` 自述「final authorization reviewer for exactly one pending tool call」，挂 `tools/pre-execute`），但它评的是**动作可授权性**而非**目标达成度**，且 base bundle 默认未装配；telemetry 族＝资源/性能镜像，`verify-*` 族＝开发期门控。⇒ 基线「无对目标达成度的独立测量」**实质成立**，但必须显式写出 auto-review 以免读者以为漏检。
- **R 环 → 维持**：新增 `repeat-output-guard`（第三个触发器，首次具备主动 cancel 权限），但 README 明写「**it never rewrites a message, and a trip is stopped, not repaired**」⇒ 仍属「检测—停机」而非「算误差—修正」。
- **SP/T/M/P → 全部维持**，P/M 增量最大：托管式 activations、6 个 subagent provider 后端、全局控制面（`send_message`/`interrupt_agent`/`list_agents`）、Agent Teams（实验）、session-query FTS5、session-format v4、schedule 四工具、permission preset 派生 custom/Auto。
- **装配层快照**：3 preset（order 11/12/13）、persona 15 节/8018 字符（**遮蔽**宿主 2790 字符/8 小节 → 后者成死配置）、skill 主根 45（模型可见 42）、7 worker 别名、permission 5 档、插件 188→191、门控 13 项 + 第 11 项假阳性 FAIL 根因（宿主活文件整文件 sha256 漂移）。**并提炼 8 条「声称 vs 实际」**。

**数据层与产物**：

- 新增评分单一数据源 `09-src-data/dsh_custom_scores.py`：**官方 3.6（raw 3.63）→ dsh-custom 3.8（raw 3.75）**，Δ+0.2；8 维仅 skill 一维 3→4；五环双层 SP 4.5→5.0 / M 4.0→4.0 / P 4.5→5.0 / R 3.0→3.0 / T 5.0→5.0 / E 2.0→3.5。
- **口径披露（防虚报跃升）**：v1.3 前 dsh 只有「技术框架对照」的**单点分 2.5**（硬编码于 `gen_html.py` 的 `FRAMEWORK_DATA`），本轮**首次**按精装度 v2.0 模型回填 ⇒ **3.6 与 2.5 不同源、不可相减**；同时把 `FRAMEWORK_DATA` 里 opencode 的 3.0 校正为模型口径 2.9（原为口径漂移）。
- 新增 2 画像（`dsh-custom.md` 266 行 / `dsh-custom-diff.md` 114 行）+ 1 实验（114 行）+ 重写 `deepseek-harness.md`（206 行，含**历史块**保留旧结论）+ 更新其实验页（112 行）。
- 生成器改造：`gen_html.py` 新增 3 个生成函数（六环雷达 + 逐环 delta + 8 维表 + 10 类清单，分值全部从单一数据源动态取）、`FRAMEWORK_DATA` 更新、页脚/tag → v1.4、PAGES 23→26；`nav_data.py` NAV 39→42；`fix_cyto.py` / `gen_premium_cyto.py` 页脚对齐。
- **覆盖率清单入库化**：v1.3 的 coverage manifest 是 `/tmp` 临时件（既不入库也不可复现）→ 新增 `07-checkpoint/gen_coverage_manifest.py`，从 `nav_data.NAV` 期望页面 + 显式非页面清单 + `premium_scores` 的 14 产品动态派生 **112 项**，写入 `07-checkpoint/coverage-manifest.txt` 并入库 ⇒ 缺件会**真实判失败**。
- **dsh 侧脱敏快照**：新增 `snapshot_dsh_custom.py` + `07-checkpoint/dsh-custom-snapshot/`（9 件 + inventory + manifest，含 `collected_at`；`.env`/credentials/sessions 一律不采集）。

### 3.3 B2 opencode 侧（完成）

- 快照脚本升级（新增 `collected_at`、plugins/、`rd.md`、`requirement-discovery-behavior.md`、`agent-protocol.md`；去 `downloads.md`；inventory 增 `skills_disabled` / `instructions_registered` / `providers` / `config`），重采 **13/13 件**，旧 inventory 归档为 `inventory-v1.3.json`。
- 分值口径：**官方 2.9 / opencode-custom 3.9 维持**（净变化＝能力纵深 + 结构调整 + **2 项损失**，无维度跨档）；文件头新增 2026-10-11 重算记录与两项损失登记。
- 漂移实测：agents 10→9、可加载 skill 41→45、commands 2→3、instructions 注册 5→6、MCP 6→4、plugins 0→2、providers 3→6、MEMORY.md 深迁移 −46%。
- 画像更新：`opencode.md` 196 行（新增 `1.18.31→1.18.35` 增量点检 + **源码级点检**：36 包集合逐一致、`29→35` = 328 files +17411/−8779、core 仅 10 文件）、`opencode-custom.md` 313 行（新增 §8 补账章节）、`opencode-custom-diff.md` 140 行（清单 10→12 类 + §5b 损失登记 + 六大发现）。
- **交叉发现（本轮最有价值的一条）**：官方 `v1.18.34` release note「发送带命名空间的 session / parent-session 身份 header」**闭合归因**了 DSH 侧 2026-10-10 遇到的网关 `400 MissingSessionID`（当时只能用裸 curl A/B 判定为「网关侧新增契约」，现可定位到同源客户端契约的引入时点）。

### 3.4 B3 opencode-dag 库（完成）

- 官方点检：`git fetch --depth=1` 拉入 v1.18.35 → **包级结构零变化**（36 包 / 32 顶层目录，包集合 diff 完全一致）⇒ 只需版本标注。
- 装配层重建：活体采集 68 组件 → 合并机制后 **87 组件**（83 → 87）。
- 管线改造：版本串与黄金值更新（6 个脚本 + README），并把 `quality-gate.py` 的 9 类期望值**改为从 `modified-dag.json` 的 `stats` 动态读取**（黄金值仅兜底 + `# GOLDEN:` 注释）+ 新增「不得为 0」非空断言。
- 数据与产物：modified **133 节点 / 177 边 / 42 组**（129/190/43），diff-list 94（90），节点页 133、组页 42；删除 7 陈旧节点页 + 1 陈旧组页。
- 门控：`quality-gate.py` **33/33 ALL PASS**；`headless-final` **ALL OK**（zcount 36/46/133、三图截图 255–276 KB、节点页 h2=6）。
- **环境限制代码化**：`headless-final-v11829.py` 原先写死 `CHROME="chromium-browser"`（本机该名是 snap 包装、容器内缺 `cap_dac_override` 无法启动）→ 改为 `detect_browser()` **自动探测**（优先 playwright 自带 chrome-for-testing，其次系统 chromium，最后回退旧名）。

### 3.5 过程中遇到的问题及应对（如实记录）

| # | 问题 | 根因 | 应对 |
|:--:|---|---|---|
| 1 | 一次委派因 prompt 为空而启动 | 主 Agent 批量发委派时漏填参数 | 立即 `interrupt_agent` 并重新委派（该空 prompt 会话未产出任何文件） |
| 2 | dsh 快照 skill 计数两次出错（39 → 45） | 第一版把 `_overlay` 当深度 1 条目重复相减 | 用 `find -mindepth 2 -maxdepth 2` 实测澄清口径（**主根 45 / overlay 6 / 合计 51 / 模型可见 42**），修正脚本后重跑；42 与运行时技能目录实测一致 |
| 3 | 生成器「幂等性检查」报 DRIFT | 主 Agent 在两次重跑之间改过 `dsh-custom.md`（补最弱环 + SRC-016） | 复跑第二次 → **零漂移**，确认为内容变更而非生成器非确定性 |
| 4 | 覆盖率清单生成器路径全错（44 项 MISSING） | 误把 NAV 元组的**标签**当文件名（元组形状是「标签/文件名/分组」） | 修正为 `item[1]` → 112 项、0 缺失 |
| 5 | DAG headless 全 FAIL（zcount=None、截图 0 字节） | 脚本写死 snap chromium | 改为浏览器自动探测（见 3.4），重跑 ALL OK |
| 6 | 子 Agent 报告「`scoped_digest` 未在源码中定位到」 | 该子 Agent 只 grep 了整文件 sha 那一行 | 主 Agent 亲自复核 `build_provenance.py:89-96 / :151-153 / :263-293` → **确实存在**，事实包正确，未据此改写结论 |
| 7 | 实机在会话期内漂移 | opencode 侧 skill 数 17:04 快照为 45，17:2x 复测为 46（新增 `frontend-design-methodology`） | **以快照 `collected_at` 为准（45）**并在门控结果 §六 E4 登记该漂移——这正是本轮为快照补时间戳的用途 |
| 8 | 子 Agent 的「当前标注残留」自检不可信 | 无 bash，只能静态 grep | 全部残留检查由主 Agent 用精确模式复跑（结果：**0 命中**） |
| 9 | DAG 报告子 Agent 在我提交后仍扩写报告 | 时序：我先提交、它后完成 | 复核后确认工作区已无未提交变更（其自述的字节数为估算），并把其发现的 3 处口径不一致**另行提交校准**（`53a07be`） |

---

## 4. 完成情况

### 4.1 交付物清单

| 库 | 交付 | 验证 |
|---|---|---|
| **control-theory-agent-kb** | 版本 v1.3.0 → **v1.4.0**；新增 3 页（`case-dsh-custom` / `compare-dsh` / `exp-dsh-custom`）；新增 2 画像 + 2 diff + 2 实验；重写 dsh 官方画像；更新 opencode 两画像 + diff；`dsh_custom_scores.py`；`snapshot_dsh_custom.py` + 脱敏快照；`gen_coverage_manifest.py` + 入库清单；契约 §2.6/§2.7 泛化 + 新增 ⑤ 补账义务；README / 00-index / 根 index.html 全站 v1.4 | **L1-L7 全开 ALL PASS（issue 0）** + 一致性 PASS + 评分复算 PASS + 残留 0 |
| **opencode-dag-analysis** | 官方标注 v1.18.30 → **v1.18.35**；装配层 83 → **87 组件**；DAG 129 → **133 节点** / 190 → **177 边** / 43 → **42 组**；diff-list 90 → 94；`执行报告-1011.md/html`；3 处口径校准 | **quality-gate 33/33 ALL PASS** + **headless ALL OK** |
| **deepseek-harness-plugin-dag** | 复核：分支 `v0.2.1-alpha.2` 已在远端（`af5b963`），`master` 按决议不动 | `rev-list` 0/0；`ls-remote` 一致 |

### 4.2 关键数字

| 指标 | 值 |
|---|---|
| KB 页面数 | 04-interactive 39 → **42**（+根门户 + report = 45 交付 HTML） |
| KB nav 条目 | 39 → **42**（+portal = 43 页） |
| KB 覆盖率期望清单 | 112 项（入库；v1.3 为 /tmp 临时 79 项） |
| KB 门控 | L1-L7 **7/7 PASS**，issue 0，warning 3 类（均非交付缺失） |
| dsh 精装度 | 官方 **3.6** → dsh-custom **3.8**（Δ+0.2） |
| opencode 精装度 | 官方 **2.9** → opencode-custom **3.9**（维持，Δ+1.0） |
| DAG 组件 | 83 → **87** |
| DAG 节点/边/组 | 129/190/43 → **133/177/42** |

### 4.3 推送结果

| 库 | commit | 远端 |
|---|---|---|
| control-theory-agent-kb | `ba3ecec` | `83d02b3..ba3ecec  main -> main`（已复核 local == remote） |
| opencode-dag-analysis | `7332dbc` + `53a07be` | `6e02692..7332dbc` → `7332dbc..53a07be  main -> main`（触发 Pages workflow） |
| deepseek-harness-plugin-dag | `af5b963` | 分支 `v0.2.1-alpha.2` 已在远端（本分支无 Pages workflow） |

### 4.4 未做项（如实登记）

1. **dsh-plugin-dag 的 `master` 未跟进**（按决议 D5）；如需 Pages/默认分支可见性，需另立一轮。
2. **`dsh-web.service` 未重启**（需 root、会断会话）⇒ dsh 侧视觉能力生效仍待人工。
3. **opencode-dag 的 2 个新插件未入图**（pipeline 无 `plugin` kind）；`05-drawio/` 图未重生成（无生成脚本）；内部 import 数据仍用 v1.18.29 基线。
4. **上游追新未做**：opencode `v1.19.0`（OpenCode 2 入口）与 dsh 后续 tag 只登记不追。
5. **未写任何记忆文件**（D7）；本轮教训以本报告与门控结果文件形式留档。

---

## 5. 反思 / 分析 / 建议

### 5.1 方法论层面的三条收获

1. **「数量下降 ≠ 能力下降」需要显式登记**。本轮 opencode-custom 的 agent 10→9、MCP 6→4 都是**结构调整**（drawio/vision 退役、制图改走 skill 档位），若只报增长就是选择性叙述；本轮把 **L1 视觉代看退役 / L2 MCP 工具面收窄** 两项损失写进画像、diff、门控结果与报告四处。⇒ **复评必须同时登记「增」与「损」**，否则「维持分值」会显得像没查。
2. **同一装配层跨宿主迁移会出现「能力掉队」，且掉队点是可定位的**。opencode 侧 `architecture-judgment` 门控栈判「E 环反转」（子 Agent 有 bash 可自跑门控）；迁到 dsh 后子 Agent **无 bash** ⇒ 门控无法在产出方自跑，E 环只判「增强」；R 环更因 `dsh-reflection` 插件移出而**完全断裂**。⇒ 迁移工程的验收判据不能只看「组件是否齐」，必须看**每个组件的运行时前提是否满足**。
3. **判据要绑「被消费字段」而非「整文件指纹」**。bundle 自家门控第 11 项曾因宿主 patch 是**活文件**（GUI 写回字号即漂移）而假阳性 FAIL——假阳性会训练人忽略红灯，比漏报更隐蔽。⇒ 判据的作用域必须与「实际会被消费的面」对齐（与既有的「公式层比数值层更深一层」同源）。

### 5.2 环境与流程层面的建议

1. **「环境限制应转成可复现的代码，而非一次性绕过」**：DAG 的 headless 脚本原先写死 snap chromium；本轮改为 `detect_browser()` 自动探测后，两种环境都能跑。建议把该模式推广到所有依赖外部可执行文件的脚本。
2. **子 Agent 无 bash 是当前架构的硬约束**，由此形成稳定的分工范式：**子 Agent 写（内容/代码）、主 Agent 跑（脚本/门控/git）**。建议把该范式写进 `opencode-capability-extension` 的委派章节，避免后续轮次重复试错。
3. **覆盖率清单必须入库**：v1.3 的 79 项清单落在 `/tmp`，本轮已改为入库的 112 项显式期望清单 + 派生脚本。建议后续轮次**只改清单、不改门控逻辑**。
4. **快照必须自带时间戳**：本轮实测到「同一会话内 skill 数 45→46」的实机漂移；`collected_at` 让「口径以哪一刻为准」可判定，而不是靠事后推断。
5. **跨库交叉验证有额外收益**：本轮把 dsh 侧 1010 遗留的「网关 `MissingSessionID` 未归因」与 opencode `v1.18.34` 的 release note 对上，闭合了一条悬了一个月的证据链。建议在复评流程里固定一步「**跨库悬案回填**」。

### 5.3 下一轮建议（按优先级）

1. **dsh 侧 E/R 环的补强是明确的高价值缺口**：给 dsh 子 Agent 一条可用的门控执行通道（或把门控改成主 Agent 可代跑的两段式），并决定 reflection 链路是重建插件还是改用 dsh 原生机制。
2. **opencode `v1.19.0` / OpenCode 2 立项**：待其正式落地并取得本地源码/行为证据后单独立像（本轮已登记）。
3. **opencode-dag 补齐 `plugin` kind**：把 2 个治理插件（prefix-cache 日期治理 / 暂停通知）纳入装配层图，并顺手清理 `build-dag.py` 中已退役组件的旧规则。
4. **dsh-plugin-dag 的 `master` 跟进决策**：若希望默认分支即最新版，需一次 fast-forward 或 PR。

---

### 📚 证据来源

| SRC | 级别 | 信源 | 路径/URL | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S4 | 一手实测 | `evidence/batch0-probes.md`（深度 2 不可用 / 视觉可用 / 三库状态） | 高 |
| SRC-002 | S4 | 一手实测 | `evidence/opencode-official-baseline-check.md`（36 包集合逐一致；105/328/318 files） | 高 |
| SRC-003 | S4 | 一手取证 | `evidence/dsh-five-rings-verdicts.md`（五环判定 + `file:line`） | 高 |
| SRC-004 | S4 | 一手门控 | `evidence/kb-gate-result-v1.4.txt`（L1-L7 全 PASS） | 高 |
| SRC-005 | S4 | 一手重建 | `evidence/dag-rebuild-summary.md`（87 组件 / 133-177-42 / 33-33 PASS） | 高 |
| SRC-006 | S4 | 一手提交 | KB `ba3ecec`；opencode-dag `7332dbc` + `53a07be`；dsh-plugin-dag `af5b963` | 高 |
| SRC-007 | S1 | 官方 release | GitHub API `anomalyco/opencode` releases（v1.18.30–v1.19.0，2026-10-11 实测） | 高 |
| SRC-008 | S1 | 官方源码 | `/home/zako-mio/dsh`（tag `dsh-v0.2.1-alpha.2`，commit `d743267`） | 高 |
