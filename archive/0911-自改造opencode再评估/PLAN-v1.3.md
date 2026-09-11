# PLAN v1.3 — 自改造 opencode 再评估（两库更新）

> 任务：自改造 opencode 架构已大幅演进，重新评估并更新上传 GitHub 原库
> 计划日期：2026-09-11　负责人：主Agent　执行复杂度：[COMPLEXITY: 17/20] → Deep
> 基线：官方 opencode v1.18.30（本地运行时 v1.18.30）
> 目标库：① `control-theory-agent-kb`　② `opencode-dag-analysis`

---

## 1. 背景与动机

v1.2（2026-09-09，`archive/0909-自改造opencode评估/`）曾对 `opencode-custom` 装配层做评估（官方 2.9 → 自改造 3.9）。此后本机 `~/.config/opencode` 装配层继续演进，实测漂移如下：

| 维度 | v1.2 快照（2026-09-09） | 当前（2026-09-11） | Δ |
|------|:---:|:---:|:---:|
| agents | 9 | 10（+`architect-worker`） | +1 |
| skills | 28 skills + 11 legacy（双根） | 45（单根统一 `skills/`） | +7 净增、双根合一 |
| commands | 1（reflection.md） | 2（+`arch.md`） | +1 |
| instructions | 5（含 agent-protocol.md） | 5（新增 architecture-behavior.md；agent-protocol.md 并入 auto-mode.md） | 成分变更 |
| MCP | 6 | 6 | 0 |

**新增能力（三层栈）**：`architecture-judgment` skill + `architect-worker` + `architecture-behavior.md` 指令层 + `/arch` 命令 → 「架构判断」能力三层栈；另有 `opencode-capability-extension`（能力扩展 SOP）、`github-bulk-upload`、`job-listing-filter`、`restricted-corpus-acquisition`、`resumable-content-pipeline`、`single-source-docs-pipeline` 等新 skill。

**官方基线漂移**：1.18.29 → 1.18.30 = 30 commits / 105 文件（+1676/−403），但**无新增包**、包级依赖结构未变；改动集中于 `packages/web`(37)、`console/*`(31)、docs，核心运行时仅 `opencode`(7 文件)、`core`(3)；功能变更 = Astra system prompt 移植、provider SDK 升级（OpenAI 3.0.88 / Azure 3.0.93 / gitlab-ai-provider 6.15.0）、Bedrock-DeepSeek model id 修复。

---

## 2. 执行决策表（grill-me 收敛）

| # | 决策 |
|:--:|------|
| 1 | 目标库 = 两个都更新（KB 变体专题 + opencode DAG 库） |
| 2 | KB 深度 = 证据层+交付层全量更新；实验层只补新机制，不重跑 v1.2 六实验 |
| 3 | 官方基线 = 两库对齐升至 1.18.30 |
| 4 | DAG 库范围 = 装配层全量重建 + 官方侧增量点检 |
| 5 | 新增实验 4 个：① 架构三层栈端到端 ② 能力扩展器冒烟 ③ architecture-judgment KG 离线可用 ④ MEMORY 硬门禁不可绕 |
| 6 | KB 版本/落点 = v1.3 + 双落档（KB `archive/0911-自改造opencode再评估/` ＋ `Mission-file/2026-09/0911-自改造opencode再评估/`） |
| 7 | DAG 库形态 = 原地更新 + 0911 报告（md+html）+ README 版本说明 |
| 8 | KB 官方画像 = 增量点检 + 版本标注 1.18.30，官方五环基线分值保持 |
| 9 | 先落盘 PLAN 再执行 |
| 10 | 推送 = 两库各自 commit + push `main`（Pages 自动重建），完成后回报 commit hash 与链接 |
| 11 | 红线沿用 v1.2：快照脱敏 / 实验仅 `/tmp/opencode` 隔离区 / 前后 sha256 校验 / 变体不参与市售排名 / 对实机配置只读 |
| 12 | 评分口径 = 复用精装度 v2.0（硬门槛 + 8 维加权 + 一票否决），分值数据涌现定稿 |
| 13 | 报告 = 双版本（md + html），5 段 Mission 模板 |

---

## 3. Phase 划分

### KB 侧（`control-theory-agent-kb` → v1.3）

| Phase | 内容 | 委派 | 产出 |
|:---:|------|------|------|
| **K0** | 计划落盘 | 主Agent | 本文件（双落档） |
| **K1** | 脱敏快照刷新（脚本更新：单根 skills、architecture-behavior.md、去 agent-protocol）+ inventory 重算 + 8 维/五环评分重算 | general | `07-checkpoint/opencode-custom-snapshot/`、`snapshot_opencode_custom.py`、`opencode_custom_scores.py` |
| **K2** | 官方画像增量点检（1.18.30 差异 + 版本标注） | general | `03-cases/opencode.md` |
| **K3** | 画像更新 `opencode-custom.md`（10 agent / 45 skills / 三层栈 / 新机制） | general | 画像 MD |
| **K4** | diff 更新 `opencode-custom-diff.md`（8 类→9+ 类改造、五环 delta、8 维对比） | general | diff MD |
| **K5** | 4 个新实验（/tmp/opencode 隔离） | general | `06-experiments/opencode-custom.md` |
| **K6** | HTML 重生成 + 整合：case/compare/exp 三页 + nav_data/gen_html 版本 v1.3 + 索引/README/契约 v1.3 | general | `04-interactive/*`、`09-src-data/*`、`05-md/00-index.md`、`README.md`、`00-contract/contract.md` |
| **K7** | L1-L7 门控（含 HTML 双交付门控） | 主Agent + vision-worker | 门控结果 |
| **K8** | 双版本报告 + 双落档 | 主Agent | `report.md` / `report.html` |

### DAG 侧（`opencode-dag-analysis`）

| Phase | 内容 | 委派 | 产出 |
|:---:|------|------|------|
| **D1** | 官方侧增量点检（1.18.30，确认包级 DAG 无结构变化） | general | 点检记录 |
| **D2** | 装配层全量重建（45 skills / 10 agents / 6 mcp / 5 instructions / 2 commands / 1 config / N mechanisms） | general | 装配组件清单 + 节点数据 |
| **D3** | 三图 + 节点页（why/how）+ 分组 + drawio 重生成 | general + drawio-worker | `01-dag-data/*`、`02-nodes/*`、`03-groups/*`、`05-drawio/*` |
| **D4** | 门控 + README 版本说明 + 0911 报告（md+html） | 主Agent | 报告 |

### 收尾

| Phase | 内容 |
|:---:|------|
| **F1** | 双版本 Mission 报告（5 段模板）+ 双落档一致性校验 |
| **F2** | 两库 commit + push `main` + 回报 hash/链接 |

---

## 4. 红线约束

1. **只读实机配置**：`~/.config/opencode` 仅采集脱敏快照，绝不修改源文件；
2. **脱敏**：`opencode.env` 不拷贝，密钥 `<REDACTED>`；`MEMORY.md` 不入公开库（KB `.gitignore` 已排除）；
3. **实验隔离**：仅 `/tmp/opencode` 隔离区（XDG_CONFIG_HOME/XDG_DATA_HOME/XDG_STATE_HOME/XDG_CACHE_HOME 全指向隔离区）；实验前后 `MEMORY.md` sha256 校验；
4. **不排名**：`opencode-custom` 为个人变体，不参与 14 产品市售排名；
5. **记忆系统硬门禁**：严禁直接修改 `~/.config/opencode/MEMORY.md` 与 `Reflection/pending.json`；
6. **公开库**：不推含密钥/隐私内容；符号链接与临时产物不入库。

---

## 5. 验收标准

- KB：L1-L7 门控全 PASS；nav 覆盖新页；版本号全站一致 v1.3；变体未污染市售排名一致性校验。
- DAG：装配组件数与实机一致；三图节点/边数对账；节点页七段完整；drawio 导出非截断。
- 报告：双版本（md+html）5 段完整；HTML 双交付门控通过。
- 推送：两库 `git status` 干净、推送到 `main`、回报 commit hash。
