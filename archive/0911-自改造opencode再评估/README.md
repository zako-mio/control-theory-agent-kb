# 0911 — 自改造 opencode 再评估（v1.3）留档

> 任务：v1.2（0909）之后，本机装配层发生「能力纵深增长」、官方 opencode 由 v1.18.29 升到 v1.18.30；对「自改造 opencode」做复评，并同步更新上传两个原库。
> 完成日期：2026-09-11　版本：v1.3.0

## 本目录文件

| 文件 | 说明 |
|------|------|
| `README.md` | 本目录说明（文件清单 + 成果主体位置 + 核心结论速览） |
| `PLAN-v1.3.md` | 执行计划（grill-me 13 项决策 + 两库 Phase 划分 + 复杂度 17/20 → Deep） |
| `report.md` | AI 友好留档报告（5 段 Mission 模板 + 证据来源表） |
| `report.html` | 人类可读报告（自包含 CSS，内容与 report.md 一致） |

## 成果主体位置（两库）

### 一、控制理论 ⊗ Agent 设计知识库（KB，v1.3）

| 类型 | 路径（仓库相对） |
|------|------|
| 画像（权威） | `03-cases/opencode-custom.md` |
| diff | `03-cases/opencode-custom-diff.md` |
| 实验 | `06-experiments/opencode-custom.md`（实验 7-10 为本轮新增） |
| 评分单一数据源 | `09-src-data/opencode_custom_scores.py` |
| 契约 | `00-contract/contract.md`（§2.7 变体复评约定） |
| 门户/索引 | `README.md`、`05-md/00-index.md` |
| 交互 HTML | `04-interactive/`（39 页，含 case/compare/exp-opencode-custom） |
| 门控结果 | `07-checkpoint/quality-gate-result-v1.3.txt` |
| 快照 | `07-checkpoint/opencode-custom-snapshot/`（脱敏证据源） |

### 二、opencode DAG 依赖分析（DAG）

| 类型 | 路径（仓库相对） |
|------|------|
| 三图数据 | `01-dag-data/{official,diff,modified}-dag.json` |
| 节点页 | `02-nodes/`（129 页 + index） |
| 组页 | `03-groups/`（43 组 + index） |
| 交互三图 | `04-interactive/view-{official,diff,modified}.html` |
| drawio | `05-drawio/main/`（3 主图）+ `05-drawio/assembly/`（关键装配） |
| 说明 | `README.md` |
| 执行报告 | `执行报告-0911.md` / `执行报告-0911.html` |

## 核心结论速览

- **评分维持不变（诚实口径）**：官方 opencode 2.9 → 自改造 3.9（Δ+1.0）**维持不变、不虚报跃升**。本轮漂移属「能力纵深增长」，未跨评分模型 5 档产品阈值；封顶因素（一键部署=个人 config 无分发、沙箱=非 VM 隔离）未变。
- **弱环反转仍成立**：E 环 2.0→4.0、R 环 2.0→4.5。架构三层栈新增 `gate_architecture.py` 领域级自动门控（实验7 gate 6/6 PASS），是 E 环首个可自动执行的领域级评估门。
- **装配层漂移**：agents 9→10（+`architect-worker`）；skills 28+11 双根 → 45 单根（42 加载 = 41 装配 + 1 内置，4 个 `_SKILL.md` 不达标未加载）；commands 1→2（+`/arch`）；instructions 5（`architecture-behavior.md` 入、`agent-protocol.md` 并入 `auto-mode.md`）；MCP 6 不变。
- **两项新机制**：架构判断三层栈（`architecture-judgment` 167 节点离线 KG + `architect-worker` + `architecture-behavior.md` + `/arch` + `gate_architecture.py`）；能力自我扩展 SOP（`opencode-capability-extension`）。
- **4 个新实验**：架构三层栈端到端、能力扩展器冒烟（引用 14/14 存在）、KG 离线可用（167 节点/360 边、3/3 读取）、MEMORY 硬门禁核验（提示词级达标 + 权限层旁路披露）。
- **门控**：KB L1-L7 全 PASS（L4 由 vision-worker 整页截图复核），issues=0，14 产品一致性 PASS（变体未污染市售排名）；DAG quality-gate 30/30 PASS，headless zcount 36/46/129。
- **官方基线**：v1.18.29 → v1.18.30，30 commits、无新增包、包级依赖结构未变，官方三图仅升级版本标注。

## 交付边界（如实披露）

- 变体为个人装配层，**不参与 14 产品市售精装度排名**（契约 §2.6 / §2.7 排名隔离硬约束）。
- DAG 库内部结构模块 DAG 沿用 **v1.18.29 基线**（官方 v1.18.30 结构未变，节点页与 README 已显式标注）。
- 实验10 的子Agent 动态拦截探针为**静态验证**（红线禁写 MEMORY/pending，无法在不触碰真实记忆文件前提下可靠复现运行时拦截）。
