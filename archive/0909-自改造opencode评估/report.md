# 任务完成报告 — 控制理论 ⊗ Agent 设计知识库 v1.2「自改造 opencode」变体专题

> AI 友好留档版（人类可读版见同目录 `report.html`）
> 版本：v1.2.0　完成日期：2026-09-09　负责人：主Agent
> 任务路径：`archive/Mission-file/2026-09/0907-控制理论Agent设计知识库/`

---

## 1. 当时情况

### 1.1 任务背景

既有知识库中，`03-cases/opencode.md` 评估的是**官方 opencode v1.18.29 内核**（结论：E/R 环弱、P/T 最强）。而本机 `~/.config/opencode` 已被用户长期改造为一套**重装配层**：9 个 agent（+5 专职 worker）、6 个 MCP、28+11 skills、Reflection 自演化系统、auto-mode/agent-protocol/search-behavior 协议层。用户要求**增量新增对「自改造 opencode」的评估，便于与官方原版区分**。

### 1.2 用户原始需求

- 增量（不推翻既有库），在现有知识库内新增「自改造 opencode」评估；
- 核心诉求：**便于官方原版 opencode 区分**；
- 最终追加要求：留档到 KB 的 `archive/0909-自改造opencode评估/`，并**推送 GitHub + 更新 Pages**。

### 1.3 环境状态

- 运行环境：WSL2（Linux），工作目录 `/home/zako-mio/opencode`；opencode `1.18.29`（`/home/zako-mio/.opencode/bin/opencode`）；
- 配置源：`~/.config/opencode/`（`opencode.jsonc` 用 `{env:XXX}` 引用密钥，无硬编码；`opencode.env` 含真实密钥）；
- 渲染环境：系统 chromium 可用（snap 沙箱无法写 `/tmp`）；playwright Python 模块未装；
- 仓库：`https://github.com/zako-mio/control-theory-agent-kb.git`，分支 `main`；GitHub Pages 源=`main` 根目录（`https://zako-mio.github.io/control-theory-agent-kb/`）。

---

## 2. 制定计划

### 2.1 grill-me 收敛的 14 项决策

| # | 决策 |
|:--:|------|
| 1 | 定位 = 独立案例 + diff 对照 + 交互对照页（全量三产物） |
| 2 | 标尺 = 五环双层评分 + 复用精装度 v2.0 加权模型 |
| 3 | 粒度 = 全量 8 类改造 + 每项五环权重标注 |
| 4 | 基线 = 官方默认 + 最小常规装配（四 agent + 官方内置 skills + 基础 provider） |
| 5 | 核心命题 = 三线并列（主：弱环定向补强；副：精装度跃升；副：编排升级） |
| 6 | 实验 = 完整实机实验组（`/tmp/opencode` 隔离区） |
| 7 | 对照页形态 = 五环雷达图叠加 + 逐环 delta 卡片 |
| 8 | 交付物 = 七件套（案例+diff+两 HTML+实验+实验 HTML+索引） |
| 9 | 整合 = 全量整合 + 变体单独标注（不进 6 框架原生排名） |
| 10 | 证据策略 = 脱敏快照 + 路径引用 |
| 11 | 命名 = `opencode-custom`（自改造），案例 ID `KT-case-007` |
| 12 | 精装度 = 实算分数 + 变体标注不排名 |
| 13 | 门控 = L1-L7 全开 |
| 14 | 实验组配独立人类端 HTML（实为七件） |

> 复杂度门控：`[GATE] 范围=4 深度=4 操作=5 风险=3 → 16 → Deep`（[COMPLEXITY: 16/20]，Deep 推理）。

### 2.2 执行阶段划分

| Phase | 内容 | 委派 | 产出 |
|:---:|------|------|------|
| **0** | 脱敏证据快照 + 精装度 8 维评分固化 | 主Agent | `07-checkpoint/opencode-custom-snapshot/` + `09-src-data/opencode_custom_scores.py` |
| **1** | 独立画像 + 官方 vs 自改造 diff | general 子Agent | `03-cases/opencode-custom.md`、`opencode-custom-diff.md` |
| **2** | 隔离区实机实验组（6 实验） | general 子Agent | `06-experiments/opencode-custom.md` |
| **3** | 3 个 HTML 生成 + nav 注册 | general 子Agent | `case/compare/exp-*.html` + `nav_data.py`/`gen_html.py` |
| **4** | 索引/README/契约 v1.2 | general 子Agent | `05-md/00-index.md`、`README.md`、`contract.md` |
| **5** | L1-L7 门控 + L4 视觉 | 主Agent + vision-worker | 门控 7/7 PASS |
| **6** | 留档 + GitHub 推送 + Pages | 主Agent | 本报告 |

### 2.3 红线约束

1. 严禁修改 `~/.config/opencode/MEMORY.md` 与 `Reflection/pending.json`（记忆系统硬门禁）；
2. 实机实验仅 `/tmp/opencode` 隔离区，实验前后校验记忆系统文件 sha256；
3. 证据留档脱敏：`opencode.env` 不拷贝，密钥 `<REDACTED>`；
4. 变体不污染 14 产品市售排名（独立评分文件 `opencode_custom_scores.py`）。

---

## 3. 执行情况

### 3.1 Phase 0 — 证据与评分（主Agent）

- 写 `07-checkpoint/snapshot_opencode_custom.py`：脱敏快照 8 文件（`opencode.jsonc`/`MEMORY.md`/`reflection.md`/5 份 instructions）+ `inventory.json`（9 agents / 6 MCP / 28 skills + 11 legacy / 3 scripts / 1 command）。
- 首版提取正则在嵌套花括号处截断（只得到 1 agent）→ 改为 **JSONC 去注释 + 去尾逗号 + json.loads** 解析，修正为 9 agents / 6 MCP。
- 固化评分 `09-src-data/opencode_custom_scores.py`：官方 **2.88→2.9**、自改造 **3.85→3.9**（Δ+1.0）。

### 3.2 Phase 1-2 — 画像 / diff / 实验（子Agent）

- 画像 MD：6 环（SP/E/T/M/P/R）+ 精装度评估 + 总评 + 总结 + 9 条 SRC 证据；`render_case.py` 解析通过（6 环、3.9/5、8 维表）。
- diff MD：8 类改造清单 + 五环双层 delta + 8 维对比 + 三大发现 + 9 条 SRC。
- 实验 MD：6 个实验（基线 / 专职 worker 委派+嵌套 depth=2 / Reflection 只读 / GATE / MCP 连通 / Skill 加载）；`render_exp.py` 解析通过。

### 3.3 Phase 3-4 — HTML 与整合（子Agent）

- 3 新页：`case-opencode-custom.html`、`compare-opencode.html`（五环雷达 SVG + delta 卡片）、`exp-opencode-custom.html`；`nav_data.py` NAV 39→40 条；`gen_html.py` 注册新页 + 新增 `gen_compare_opencode()`。
- 索引/README/契约升至 **v1.2.0**：新增 §2.6 变体专题约定 + `opencode-custom` ID 规则 + 核心洞察「装配层可定向补齐内核弱环」。

### 3.4 Phase 5 — 门控与问题应对

| 层 | 结果 | 备注 |
|----|:---:|------|
| L1 生成自验证 | PASS | py_compile + 解析器实跑 |
| L2 全量审计 | PASS | quality-gate 0 issue；14 产品一致性 PASS（未污染排名） |
| L3 结构/断链/NAV | PASS | structure 176 / links 1816 / nav 40 |
| L4 视觉层 | PASS | vision-worker 三图质检（雷达 6 辐条+双多边形闭合） |
| L5 渲染层 | PASS | headless chromium 43 项 |
| L6 覆盖度层 | PASS | coverage 7 项（`--require` 新交付物） |
| L7 信源层 | PASS | sources 22 项 |

**遇到的问题与应对**：

1. **快照正则截断** → 改 JSONC 解析（见 3.1）。
2. **snap chromium 无法写 `/tmp`** → 截图输出改到项目 `07-checkpoint/`。
3. **VLM 标签幻觉**：vision-worker 将 `R 反思` 读作“D 部署”、编造“排名17-3” → 用 DOM/源码真值复核（`RING_ORDER=['SP','M','P','R','T','E']`）校正，确认渲染无误。
4. **并发写 pending.json**：实验子Agent 与 reflection-worker 并行，导致实验窗口内 `pending.json` sha256 变化 → 日志归因确认为 reflection-worker 写入（非实验行为），`MEMORY.md` sha256 全程不变，实验记录如实标注。
5. **页脚版本漂移**：3 个非 `gen_html` 产物（`index_cyto`/`premium-cyto`/门户 `index.html`）仍 v1.1 → 双轨修正（生成脚本 + 生成物）至 v1.2。

---

## 4. 完成情况

### 4.1 交付物清单（七件套 + 支撑）

| 类型 | 文件 |
|------|------|
| 画像 | `03-cases/opencode-custom.md` |
| diff | `03-cases/opencode-custom-diff.md` |
| 案例页 | `04-interactive/case-opencode-custom.html` |
| 对照页 | `04-interactive/compare-opencode.html` |
| 实验 MD | `06-experiments/opencode-custom.md` |
| 实验页 | `04-interactive/exp-opencode-custom.html` |
| 索引整合 | `05-md/00-index.md`、`README.md`、`00-contract/contract.md`(v1.2)、`09-src-data/nav_data.py`、`gen_html.py` |
| 证据/评分 | `07-checkpoint/opencode-custom-snapshot/`、`07-checkpoint/snapshot_opencode_custom.py`、`09-src-data/opencode_custom_scores.py` |

### 4.2 核心结论

- **弱环反转**：官方内核 E 环 2.0→4.0、R 环 2.0→4.5；装配层以 search-behavior+search-worker+grill-me 补 E、以 pending.json+reflection-worker+/reflection 补 R。
- **精装度跃升**：官方 2.9（需装修档）→ 自改造 3.9（成品化受限档），Δ+1.0；主要来自记忆（3→5）与 Skill 库（2→4）。
- **编排升级**：从「plan/build 双速 + task 委派」单体，升级为「主 Agent 编排 + 5 专职 worker + Reflection 自演化」三层平台。
- **封顶因素**：一键部署（3）与沙箱（3）未提升——个人配置无分发渠道、无完整沙箱，是精装度未达 4.5 的主因。

### 4.3 门控与推送

- L1-L7 **7/7 PASS**；L2 审计 0 issue；14 产品市售排名一致性 PASS（变体未污染）。
- GitHub：提交并推送 `main`；GitHub Pages 源=`main` 根目录，推送后自动重建。

---

## 5. 反思 / 分析 / 建议

### 5.1 过程反思

- **装配层是「定向补环」而非「换引擎」**：自改造的控制论价值在于，不改 opencode 内核，仅通过协议 + 专职 worker + 记忆系统，就把内核最弱的两环（E/R）反转。这为「框架如何低成本升级为可用系统」提供了可复制范式。
- **VLM 不可全信**：深底密小字区域转写易幻读，须以 DOM/源码真值兜底（与库内既有经验一致）。
- **并行共享状态需哈希门控**：多子Agent 并行时，凡涉及共享状态文件（pending.json），必须前后哈希 + 日志归因，否则误判实验污染。

### 5.2 收获认知

- 精装度 v2.0 模型可迁移到「个人变体」评估，但须标注「不参与市售排名」，否则口径混淆。
- 门控 coverage 层需显式 `--require` 才有意义，否则静默跳过。

### 5.3 未来建议

1. 若要提升自改造精装度上限：方向是**装配层可分发化**（一键安装脚本）与**沙箱化**；
2. Reflection 闭环仍依赖 `/reflection` 人工确认，可考虑半自动门控（低风险条目自动入池）；
3. 建议为「变体类」条目在契约中固化「不排名」标注规则，避免后续维护漂移。

> ⚠️ 契约遵守确认：证据快照已脱敏（`opencode.env` 未拷贝、密钥 `<REDACTED>`）；实验仅在 `/tmp/opencode` 隔离区，`MEMORY.md` sha256 全程不变；变体未进入 14 产品市售排名。
