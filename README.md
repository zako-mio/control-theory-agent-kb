# 控制理论 ⊗ Agent 设计知识库

> **版本**：v1.5.0（6 框架 + 14 精装房全景 + 装配层变体 opencode-custom / dsh-custom）｜创建：2026-09-07｜v1.1 扩展：2026-09-08｜v1.2 自改造 opencode 变体专题：2026-09-09｜v1.3 变体复评：2026-09-11｜v1.4 dsh 装配层变体专题 + opencode 月度追平：2026-10-11｜v1.5 dsh 装配层二次追平：2026-10-13
> **定位**：以 Agent 设计构建为业务核心，控制理论作为解决 Agent 工程问题的**技术工具库**引入。
> **核心命题**：把 Agent 当作一架装了传感器、执行器、逻辑决断器的无人机去建模与控制，拒绝把它当成会聊天的搜索引擎。

---

## v1.5 摘要（2026-10-13）— dsh 装配层二次追平

本轮 **v1.4 → v1.5**，单线：把 dsh 侧装配层从 v1.4 快照点（2026-10-11 17:09）**追平**到 v1.5 冻结点（2026-10-13 05:04）。**内核零变化**（dsh `v0.2.1-alpha.2` / commit `d743267` 未变），全部增量在装配层。

### 一、触发判据（契约 §2.7⑥）

装配层命中「能力纵深增长 / 机制新增」六项：① `run_gate` 门控执行通道（ADR-010）；② `dsh-config` 能力包（ADR-011）；③ R 环 R-A 文件载体（ADR-012）；④ `dsh-wsl-desktop-path` / `dsh-opencode-commands` 两个新插件；⑤ `verify_bundle` 判据 **13 → 20 项**；⑥ 沙箱由「本机无可用后端」变为 `bwrap enforcement=full`。

### 二、追平范围：R1–R12 全轮次

| 时点 | 轮次 | 变化 |
|---|---|---|
| 10-11 17:16–18:07 | R1–R2 | 思考档 `reasoningEfforts` + 子 Agent 能力上限；**E 环 `run_gate` 通道（ADR-010）** |
| 10-11 19:46–19:48 | R3 | 重挂 `dsh-wsl-desktop-path`（web + headless） |
| 10-12 08:32–09:31Z | R4–R5 | **`dsh-config` skill v1.0（ADR-011）**；**R 环 R-A 载体（ADR-012）** |
| 10-12 15:46–17:16 | R6–R8 | `verify_bundle` 13 → 19 项；persona 收敛（8018 → 6524 字符）；模型路由治理；R09 收尾 |
| 10-12 17:40–19:13 | R9–R10 | E3 residue 119 → 0；R-A 落库取证；行为验收收尾 |
| 10-13 02:37–03:38 | R11–R12 | caps 台账统一；判据 19 → 20 项；收官轮（重启后验收） |

### 三、评分变动（唯一 8 维变动 + 三环上调）

- **精装度**：官方 dsh 维持 **3.6**；`dsh-custom` **3.8 → 3.9**（raw 3.75 → 3.85，Δ 由 +0.2 变 **+0.3**）；档位仍「成品化受限」，**未跨档**。
- **8 维唯一变动**：`memory` **4 → 5**（权重 10%）。依据＝R-A 载体落地：`~/.dsh/MEMORY.md`（14 个 `§` 段 / 10815 B / 14 条 `[src:]` 签名）+ 候选目录 15 份 + `dsh-reflection` skill。
- **五环双层**：SP +0.5 · **M +0.5** · P +0.5 · **R +1.0** · T 0 · **E +2.0（达反转阈值）**。
- ⚠️ **最弱环结论再次改变**：v1.4 判「最弱环由 E 转移到 R」；v1.5 下 **R 与 E 并列 4.0**，不再存在单一最弱环。

### 四、三条旧结论被推翻 / 更正（本轮实质内容）

| # | v1.4 旧结论 | v1.5 处置 |
|:--:|---|---|
| C1 | 「本机无可用沙箱后端（bwrap / Landlock 均不可用）」 | **已证伪**（bwrap 已装、`enforcement=full`）⇒ 属**环境事实更正**，⛔ 不计入分值 |
| C2 | 「R 环迁移断裂、最弱环 R = 3.0」 | **已推翻**（R-A 载体落地，ADR-012 门控 6/6）⇒ R 3.0 → 4.0 |
| C3 | 「门控脚本依赖 bash 而子 Agent 无 bash ⇒ E 环只判增强」 | **已消解**（`run_gate` 窄通道）⇒ E 3.5 → 4.0，Δ+2.0 反转 |

### 五、口径唯一化（契约 §2.6 新增）

skill 计数四口径并存（v1.4 时点 45 / README 46 / `reconcile` 47 / 实测主根 49）⇒ 本轮写入契约：**主根 49 = 派生 47 + DSH 原生 2**；**模型可见 46 = 49 − 3**；`_overlay` 6。采集口径的唯一机械承载＝`07-checkpoint/snapshot_dsh_custom.py`。

### 六、本轮新增产物

| 类型 | 产物 |
|------|------|
| 证据 | `07-checkpoint/dsh-custom-snapshot/`（v1.5 新快照，含 `skills_list` / `plugins` / `reflection` / `gate` 四个新取证面）；v1.4 旧快照归档至 `archive/1011-KB-v1.4-dsh装配与opencode追平/dsh-custom-snapshot-v1.4/` |
| 数据源 | `09-src-data/dsh_custom_scores.py`（含 `HISTORY` 机读历史值与口径变更对账） |
| 画像 | `03-cases/dsh-custom.md`（新增 R1–R12 轮次表）、`dsh-custom-diff.md`（双层 delta + 文档 vs 实况冲突） |
| 实验 | `06-experiments/dsh-custom.md` 新增 **实验 15–18**（v1.5 新机制**本库自跑**行为实验：门控通道 57/57 + 23/23 + 10 变异体全判死 / R-A 链 14/14 + 容量 soft / 沙箱三档 `enforcement=full` 真写盘取证 / 账本四查全过 + 15 例负向） |
| 契约 | `00-contract/contract.md` §2.6（口径唯一化）+ §2.7⑥（追平轮登记） |
| 页面 | `04-interactive/{case-dsh-custom,compare-dsh}.html`（由生成脚本全量重生成） |

---

<details>
<summary><b>历史块 · v1.4 摘要（2026-10-11，保留原版本号）</b></summary>

## v1.4 摘要（2026-10-11）— dsh 装配层变体专题 + opencode 月度追平

本轮 **v1.3 → v1.4**，两线并行：① 新增 **dsh 装配层变体专题（`dsh-custom`）**；② **opencode 侧月度追平**，一次性补入 2026-09-11 → 2026-10-11 的一个月 backlog（补账义务，见契约 §2.7⑤）。

### 一、dsh 侧：官方画像升版 + 新增装配层变体

- **官方基线**：`v0.1.1-rc.2` → **`v0.2.1-alpha.2`**（2026-10-09，commit `d743267`，**跨 21 个预发布 tag**）。
- **新增变体 `dsh-custom`** ＝ dsh + `dsh-opencode-port` bundle：**3 preset / 45 派生 skill（模型可见 42）/ 7 worker / permission 5 档 / persona 15 节 8018 字符 / 插件 188→191**；落点 `~/.dsh/presets/opencode/` + `~/.dsh/skills/opencode/`。
- **精装度**：官方 **3.6/5** → `dsh-custom` **3.8/5**（**Δ+0.2**）；五环双层 SP 4.5→5.0、M 4.0→4.0、P 4.5→5.0、R 3.0→3.0、T 5.0→5.0、E 2.0→3.5。
- ⚠️ **口径披露（重要）**：v1.3 之前 dsh 只有「技术框架对照」的**单点分 2.5**（**非** 8 维模型输出）；本轮首次回填 v2.0 模型得 **3.6**。**3.6 与 2.5 不同源、不可相减**，旧单点分作为历史口径保留，**不得呈现为跃升**。

### 二、opencode 侧：月度追平（补账轮）

- **官方基线**：`1.18.30` → **`1.18.35`**（本机运行时）；上游最新 release **`v1.19.0`**（2026-10-11）**只登记不追**。
- **装配层漂移**（2026-09-11 → 2026-10-11）：

  | 维度 | v1.3 | v1.4 | Δ |
  |------|:---:|:---:|:---:|
  | agents | 10 | 9（−drawio-worker −vision-worker，+requirement-discovery-worker） | −1 |
  | skills（可加载） | 41 | 45 | +4 |
  | commands | 2 | 3（+rd） | +1 |
  | instructions（注册） | 5 | 6（+requirement-discovery-behavior.md） | +1 |
  | MCP | 6（2 启用） | 4（1 启用） | −2 |
  | plugins | 0 | 2 | +2 |
  | providers | 3 | 6 | +3 |

  `MEMORY.md` 于 2026-10-10 三轮 `/reflection` 深迁移 **−46%**（24318 → 13137 B，15 段零和）+ 机检 `memory_capacity_check.py`。
- **两项能力损失须登记**（不得只报增长）：**L1** 视觉代看机制退役（vision-worker 于 0915 废除 → E 环少一条「图像是否达标」的降级传感路径）；**L2** MCP 工具面收窄（drawio / drawio-local 退役，制图改走 `diagram-lite` skill 档位）。
- **结论**：净变化＝**能力纵深 + 结构调整 + 2 项损失**的混合，**无任一维度跨 5 档阈值**（MCP 曾触及 4→3 边界，判据为「平台多传输能力未变、仅本地 server 数与启用数变化，属用户配置选择」→ 维持 4）→ 官方 2.9 / 自改造 3.9 **维持不变**，仅刷新 evidence 并登记损失。

### 三、变体排名隔离

`dsh-custom` 与 `opencode-custom` 均为**个人装配层**，**不参与 14 产品市售精装度排名**（见契约 §2.6/§2.7①）。

### 四、本轮新增产物

| 类型 | 产物 |
|------|------|
| 画像 | `03-cases/dsh-custom.md`、`03-cases/dsh-custom-diff.md` |
| 页面 | `04-interactive/case-dsh-custom.html`、`compare-dsh.html`、`exp-dsh-custom.html` |
| 实验 | `06-experiments/dsh-custom.md`（实验 11-14，延续 opencode-custom 的 1-10） |
| 数据源 | `09-src-data/dsh_custom_scores.py`（与 `opencode_custom_scores.py` 同构） |
| 证据 | `07-checkpoint/dsh-custom-snapshot/`（bundle / profile / inventory.json / manifest.json） |

</details>

---

<details>
<summary><b>历史块 · v1.3 复评摘要（2026-09-11，保留原版本号）</b></summary>

本轮对「自改造 opencode」变体做复评，**版本 v1.2 → v1.3**，结论：能力纵深增长、评分维持。

**漂移事实**（相对 v1.2 快照 2026-09-09）：

| 维度 | v1.2 | v1.3 | Δ |
|------|:---:|:---:|:---:|
| agents | 9 | 10（+architect-worker） | +1 |
| skills | 28 skills + 11 legacy（双根） | 45 单根统一 | +7 净增、双根合一 |
| commands | 1 | 2（+arch） | +1 |
| instructions | 5（含 agent-protocol.md） | 5（新增 architecture-behavior.md；agent-protocol.md 并入 auto-mode.md） | 成分变更 |
| MCP | 6 | 6 | 0 |

官方基线 1.18.29 → 1.18.30（30 commits，无新增包、包级依赖结构未变）。新增纵深机制：**架构判断三层栈**（architecture-judgment skill + architect-worker + architecture-behavior.md + `/arch` + gate_architecture.py）+ **能力自我扩展 SOP**（opencode-capability-extension）。

**实验层**：只补新机制、不重跑既有 6 实验，新增 4 个实验（7-10）：① 架构三层栈端到端（gate 6/6 PASS）② 能力扩展器冒烟（三层栈闭合 3/3）③ architecture-judgment KG 离线可用（167 节点/360 边 1:1、零网络）④ MEMORY 硬门禁不可绕（暴露权限层旁路）。

**评分维持 3.9 的原因**：本轮 9→10 agent、28+11 双根→45 单根 skill、1→2 command、三层栈等属**能力纵深增长**，未跨评分模型 5 档产品阈值；封顶因素（一键部署=个人 config 无分发、沙箱=非 VM 隔离）未变，故官方 2.9 → 自改造 3.9（Δ+1.0）**维持不变、不虚报跃升**，仅刷新 evidence 与机制叙述。

</details>

---

## 快速开始

| 想做什么 | 去哪 |
|---------|------|
| **人类可读入口**（推荐从这里看） | [`index.html`](index.html) |
| 官方 vs 自改造对照页（opencode） | [`04-interactive/compare-opencode.html`](04-interactive/compare-opencode.html) |
| 自改造 opencode 画像 | [`04-interactive/case-opencode-custom.html`](04-interactive/case-opencode-custom.html) |
| **dsh 装配层变体画像（v1.4 新增）** | [`04-interactive/case-dsh-custom.html`](04-interactive/case-dsh-custom.html) |
| dsh 官方 vs 装配层对照页 | [`04-interactive/compare-dsh.html`](04-interactive/compare-dsh.html) |
| dsh-custom 实验记录（实验 11-14） | [`06-experiments/dsh-custom.md`](06-experiments/dsh-custom.md) |
| 精装房全景（14 款产品谱系） | [`04-interactive/premium-map.html`](04-interactive/premium-map.html) |
| 精装房交互 DAG | [`04-interactive/premium-cyto.html`](04-interactive/premium-cyto.html) |
| 五环框架总览 | [`04-interactive/framework.html`](04-interactive/framework.html) |
| AI 检索索引 | [`05-md/00-index.md`](05-md/00-index.md) |
| 31 个控制理论知识点 | [`01-theory/`](01-theory/) |
| 契约（命名/信源/门控规范） | [`00-contract/contract.md`](00-contract/contract.md) |
| 门控脚本 | [`07-checkpoint/kb_gate.py`](07-checkpoint/kb_gate.py) |
| 本次任务留档 | [`archive/0908-精装房Agent全景/`](archive/0908-精装房Agent全景/) |

**本地起服务器跨平台访问**：

```bash
cd 04-interactive && python3 -m http.server 8321
# 浏览器访问 http://localhost:8321/index.html
```

---

## 一、知识库是什么

本知识库系统性地把**控制理论核心思想**（负反馈闭环/状态估计/PID/鲁棒控制/分层控制）深度融入 **Agent 设计与开发**，帮助从业者从「调参工程师」进化为「系统架构师」。

### 五大核心环框架

| 环 | 控制理论对应 | Agent 工程问题 | 章节 |
|----|------------|--------------|------|
| **M 记忆/状态估计** | 状态估计/观测噪声/卡尔曼滤波 | 长上下文取舍、工作记忆蒸馏、观测噪声过滤 | `ch-memory` |
| **P 规划/分层控制** | 分层控制/慢-快双速控制器 | 任务分解、里程碑设定、慢规划器+快执行器 | `ch-planning` |
| **R 反思/反馈闭环** | 反馈闭环/误差收敛/积分环节 | 自我反思、错误回馈、长期偏航补偿 | `ch-reflection` |
| **T 工具调用/执行器** | 执行器/容错/鲁棒性 | 工具调用失败、冗余仲裁、看门狗限幅 | `ch-tool` |
| **E 评估/传感器** | 传感器/验证器/信噪比 | Critic 模块、验证器、反馈信号质量 | `ch-eval` |

> **闭环方向**：E 决定反馈信号质量 → R 决定纠偏量 → P/T 决定轨迹 → M 决定「我以为我在哪」。任一环失效，闭环即破。

### 核心洞察（6 框架对比，主 Agent 终裁）

1. **T 环（执行器）是 6 框架共同的「最强环」**——看门狗/限幅/沙箱是 Agent 工程最成熟环节
2. **E 环（评估）从样板三产品「一致最弱」分化为两派**——hermes/codex 有独立 Critic 体系（E 环强），opencode/dsh/PRIME/claude-code 仍偏弱
3. **各产品最弱环分化**——opencode/dsh/PRIME/claude-code 最弱环=E，hermes/codex 最弱环=P
4. **M 环普遍缺置信度（P 协方差）**——记忆多记事实不记「我有多确定」
5. **装配层可定向补齐内核弱环**——官方 opencode E/R 弱，经自改造（reflection/grill-me/search-worker/门控）E/R 反转，精装度 2.9→3.9（+1.0）；官方 dsh 内核已强（T 5.0 / M 4.0），装配层（`dsh-opencode-port`）只补 SP/P 编队与 E 环领域门控，精装度 3.6→3.8（+0.2）——**「弱内核 + 强装配层」（opencode-custom）与「强内核 + 薄装配层」（dsh-custom）互补**

---

## 二、v1.1 精装房全景专题

**核心命题**：声称 ≠ 实际——源码分析能看出真正的一手还是二手。

**四维坐标系**：精装度 0-5（主轴）× 一手/二手（标签）× 4 大类（分组）× 五环定位（控制本质）

### 精装度谱系（14 产品，v2.0 加权模型）

> 评分模型：**硬门槛前置（端到端可跑，0/1）+ 8 维加权（多Agent16/一键部署15/模型14/工作流13/Skill12/沙箱10/MCP10/记忆10）+ 一票否决（声称失实封顶4.0、纯中转封顶3.5）**。
> 详见 [`07-checkpoint/premium-scoring-model.md`](07-checkpoint/premium-scoring-model.md) 与重算矩阵 [`07-checkpoint/premium-score-recompute.md`](07-checkpoint/premium-score-recompute.md)。

| 分层 | 分值 | 产品 |
|------|:---:|------|
| 真·开箱即用 | ≥4.5 | Devin(5.0) / WorkBuddy(4.6) |
| 成品化受限 | 3.5-4.5 | Cursor(4.4) / Dify(4.3) / OpenHands(4.2) / Coze(4.2) / Copilot(4.1) / Windsurf(4.0) / OpenClaude(3.8) / GPT-Researcher(3.7) / CodeWhale(3.5) |
| 需装修/中转 | <3.5 | CrewAI(3.0) / CC-Router(2.1) / QCode(1.4) |
| 技术框架（对照） | 2.5-3 | opencode / dsh / PRIME / hermes / claude-code / codex |

> ⚠️ **变体不计入本谱系**：`opencode-custom`（3.9）与 `dsh-custom`（3.8）为**个人装配层**，**不参与 14 产品市售精装度排名**（契约 §2.6 / §2.7①）——其分值仅用于「官方内核 vs 装配层增量」的内部对照。
> ⚠️ **dsh 口径变更（不得读作跃升）**：本行 dsh 的旧标注 **2.5 为单点分**（`gen_html.py` `FRAMEWORK_DATA`，**非** 8 维模型输出）；v1.4 首次回填 v2.0 模型得 **官方 3.6 / 装配层 3.8**，v1.5 复评后装配层为 **3.9**（官方维持 3.6）。**3.6 与 2.5 不同源、不可相减**（契约 §2.7⑤）；v1.4 与 v1.5 属不同时点读数，亦不可相减。

### 三大实证发现

1. **二手被高估**：CC-Router（源码级铁证依赖第三方网关 `@the-next-ai/ai-gateway`）、QCode（官方明示「官方价×服务倍率」）
2. **一手被低估**：CodeWhale（自研 20 个 Rust crate）、OpenClaude（独立 TypeScript 实现）
3. **声称功能不存在**：Windsurf 无「Flows DAG」多 Agent 编排

---

## 三、目录结构

```
0907-控制理论Agent设计知识库/
├── 00-contract/          # 契约（命名/信源分级/L1-L7 门控/装配层变体专题约定）
├── 01-theory/            # 5 分区理论证据包（31 知识点，≥2 权威源交叉验证）
├── 02-framework/         # 五大核心环映射框架
├── 03-cases/             # 6 框架画像 + 2 装配层变体（opencode-custom* / dsh-custom*）+ 14 精装房画像（premium-*.md，含证据来源区块）
├── 04-interactive/       # 人类端交互 HTML 集群（42 页）
├── 05-md/                # AI 友好 MD 镜像 + 索引
├── 06-experiments/       # 6 框架标准实验组记录 + 装配层变体实验（opencode-custom 1-10 / dsh-custom 11-14）
├── 07-checkpoint/        # 门控脚本 + 实证证据 + 审计报告 + 变体脱敏快照
├── 08-drawio/            # 五环控制回路图 + 控制概念映射表
├── 09-src-data/          # DAG DATA / KT 详情 / 生成脚本 / 变体评分单一数据源
├── archive/              # 任务留档（0908 精装房专题 / 0911 v1.3 / 1011 v1.4 报告 + v1.4 历史快照 / 1013 v1.5 报告）
├── index.html            # 人类入口
└── README.md             # 本文件
```

> **注**：`05-source/`（第三方源码留档）与 `07-checkpoint/tmp-evidence/`（外部抓取快照）未纳入仓库（体积 475M），见 `.gitignore`；如需可经官方仓库获取。

---

## 四、质量门控（L1-L7）

| 层 | 名称 | 工具 | v1.3 结果（v1.4 复跑见下注） |
|----|------|------|:---:|
| L1 | 生成时自验证 | py_compile + 样例实跑 | PASS |
| L2 | 全量审计 | `quality-gate.py` | PASS（issues=0） |
| L3 | 结构层 | `kb_gate.py --layers structure,links,nav` | PASS（164 / 1814 / 40 项） |
| L4 | 视觉层 | VLM（vision-worker） | SKIPPED（本执行者无 VLM 通道，以 headless 截图 + DOM 真值替代） |
| L5 | 渲染层 | `kb_gate.py --layers render` | PASS（40 页冒烟，canvas 正常） |
| L6 | 覆盖度层 | `kb_gate.py --layers coverage` | PASS（79 项显式 manifest） |
| L7 | 信源层 | `kb_gate.py --layers sources` | PASS（22/22 画像含证据区块） |

> ⚠️ **口径说明**：上表为 **v1.3（2026-09-11）** 全量门控**实测值**，明细见 `07-checkpoint/quality-gate-result-v1.3.txt`。**v1.5 轮次的复跑结果见 `07-checkpoint/quality-gate-result-v1.5.txt`**（L1–L7 全 PASS、issue 0；另记一处「空集假绿」的发现与修复），以该文件为准——本表**不预先改写数值**（禁止未跑先报）。
> v1.4/v1.5 新增或改动的页面（`case-dsh-custom.html` / `compare-dsh.html` / `exp-dsh-custom.html` / `case-dsh.html`）与画像（`dsh-custom.md` / `dsh-custom-diff.md` / `deepseek-harness.md`）已纳入 L3/L6/L7 检查面：**04-interactive 页面 39 → 42**，**L7 信源层分母 22 → 24**，**L3 结构层 181 → 183**。
> ⚠️ **复现命令修正（v1.5）**：下方命令原**漏了 `--manifest`**，导致 coverage 层「检查项=0 却 PASS」（空集假绿）。**必须带** `--manifest 07-checkpoint/coverage-manifest.txt`。

复现命令：

```bash
python3 07-checkpoint/kb_gate.py \
  --root . \
  --layers structure,links,nav,cascade,coverage,sources,render \
  --nav-source 09-src-data/nav_data.py \
  --exclude tmp-evidence --exclude 05-source --exclude 03-cases/source --exclude archive \
  --exclude 07-checkpoint/opencode-custom-snapshot --exclude 07-checkpoint/dsh-custom-snapshot \
  --nav-exempt 07-checkpoint/report-v1.1.html \
  --manifest 07-checkpoint/coverage-manifest.txt \
  --content-glob "03-cases/*.md" \
  --render-glob "04-interactive/*.html" --render-glob index.html \
  --json-out 07-checkpoint/gate-result.json
# 评分复算（变体，单一数据源）
(cd 09-src-data && python3 opencode_custom_scores.py && python3 dsh_custom_scores.py)
# 14 产品一致性
python3 07-checkpoint/check_premium_consistency.py
```

> ⚠️ **v1.4 门控前置**：`nav` 层以 `09-src-data/nav_data.py` 的 `NAV` 为期望条目源，逐页比对侧边栏。本轮新增 3 页后 **NAV 应为 43 条（00-42）**——`nav_data.py` 与全部 42 页 HTML 侧边栏须同步再生，否则 nav 层会报条目缺失（非交付缺失，属再生未完成）。

---

## 五、信源与证据

- **分级体系**：S1 权威一手（官方文档/源码）> S2 权威二手 > S3 社区转引（仅作线索）> S4 一手观察（本库实测）
- **交叉验证**：理论类 ≥2 独立 S1/S2 源；案例类以 S1/S4 为准
- **证据区块**：**22 份画像**（6 框架 + 14 精装房 + **2 装配层变体** opencode-custom / dsh-custom）均含 `📚 证据来源` 表（SRC 编号 + 级别 + 置信度）
- **实证证据汇总**：`07-checkpoint/premium-evidence.md`、`07-checkpoint/premium-diff-analysis.md`
- **变体证据快照**（脱敏，非内容交付物）：`07-checkpoint/opencode-custom-snapshot/`、`07-checkpoint/dsh-custom-snapshot/`

---

## 六、方法论沉淀

本知识库的建设过程沉淀为一套可复用 skill 集合（`kb-construction`，五类谱系分流 + 公共主干 + L1-L7 门控），已内化至本机 opencode 环境：

- 主入口：`~/.config/opencode/skills/kb-construction/SKILL.md`
- 参考资产：6 个 `reference/*.md`（含 86 个 GitHub 权威仓库实测清单）
- 可执行脚本：5 个 `scripts/*.py`（分块/索引/混合检索/评测/门控）

---

## 七、实验红线（最小必要破坏性范围）

- **原则**：可逆 + 受控故障注入；仅 `/tmp/opencode` 隔离区实机实验 + 源码只读分析
- **禁止**：`rm -rf` 非 `/tmp/opencode` 路径；修改记忆系统文件（MEMORY.md / pending.json）；改真实 API 密钥
- **需前置确认**：首次 `rm`、大范围改造配置、kill 非本实验进程
- 完整三清单见 [`00-contract/contract.md`](00-contract/contract.md) §7

---

## 八、维护与更新

- 本库为长期维护库，随上游产品更新持续维护
- 更新遵循契约 `00-contract/contract.md` 与级联更新方法论（12 项检查表）
- 新增/修改节点后必须回归：生成脚本 + 交互图 DATA + 门控全量验证
- 门控口径统一为 **L1-L7**（见 `07-checkpoint/kb_gate.py`）

---

## 九、许可与引用

本知识库为个人研究成果，欢迎参考。引用实证结论时请保留信源标注（SRC 编号）。

> ⚠️ 14 产品精装度评分基于 2026-09-08 的公开信息与源码分析；装配层变体（`opencode-custom` / `dsh-custom`）评分基于 **2026-10-11** 的实机装配取证（官方基线：opencode `1.18.35` / dsh `v0.2.1-alpha.2`）。产品迭代快，建议定期回归。
> ⚠️ **口径提醒**：dsh 的 **3.6** 为 v2.0 八维模型输出，与 v1.3 前的**单点分 2.5 不同源、不可相减**（见契约 §2.7⑤）。
