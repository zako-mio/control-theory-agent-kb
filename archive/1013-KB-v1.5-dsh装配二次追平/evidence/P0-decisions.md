# P0 前置门决议 — KB v1.5「dsh 装配层二次追平」

> 依据：`PLAN-v1.5.md` §七 P0
> 采集：2026-10-13　负责人：主 Agent
> 状态：**三项全部收口**（口径唯一 / 静止点登记 / 外部证据指针确认）

---

## P0-1 skill 计数唯一口径

### 采纳口径（唯一权威）

来源 = `07-checkpoint/snapshot_dsh_custom.py` 的实现与内注释（v1.4 已定，本轮沿用不另立）：

| 层 | 定义 | 采集方式 |
|---|---|---|
| **主根** | `<root>/<name>/SKILL.md` **一层**扫描（深度 2） | `listdir(root)` 逐目录查 `SKILL.md` |
| **模型可见** | 主根 − 带 `disable-model-invocation: true` 的件数 | 读每件 `SKILL.md` 前 4000 字符 |
| **叠加层** | `_overlay/<name>/SKILL.md`（深度 3），**不计入主根** | 单独计数 |
| **DSH 原生** | 主根中**无 opencode 源**的件（新增列，本轮引入） | 与 `~/.config/opencode/skills/` 目录集求差 |

### 现读数（`as_of 2026-10-13 05:05`）

| 指标 | 值 | 明细 |
|---|---:|---|
| 主根 | **49** | ＝ 派生 **47** ＋ DSH 原生 **2** |
| DSH 原生件 | 2 | `dsh-config`、`dsh-reflection`（opencode 侧无同名源） |
| `disable-model-invocation: true` | 3 | `opencode-config`、`opencode-capability-audit`、`opencode-capability-extension` |
| **模型可见** | **46** | 49 − 3 |
| 叠加层 `_overlay` | **6** | openspec 系，未变 |
| 源侧真实技能目录 | 47 | `~/.config/opencode/skills/` 下 49 个目录 − `_shared` − `disabled`（二者非技能目录） |

### 四套旧口径的差异归因（须在 P5 级联中刷新或标注）

| 口径 | 值 | 归属 | 处置 |
|---|---:|---|---|
| `07-checkpoint/dsh-custom-snapshot/inventory.json` | 45 | **v1.4 时点值** | 属历史记录，保留；新快照将刷新为 49 |
| bundle `README.md` §1 | 46 | 源侧口径，已过期 | P5 级联刷新 |
| `reconcile.py` 断言 | 47 | 派生件口径（**与现读数一致**） | 无需改；须在画像中说明其与「主根 49」的差 = DSH 原生 2 件 |
| 实测主根 | 49 | 本轮权威读数 | 写入画像与契约 |

> ⚠ 结论：「45 / 46 / 47 / 49」不是同一事实的四个矛盾读数，而是**四个不同口径**（v1.4 时点 / 源侧 / 派生件 / 主根含原生）。契约 §2.6 须显式写明这四者的定义与换算关系，避免后续复评再次混淆。

---

## P0-2 静止点登记

| 项 | 读数 | 证据 |
|---|---|---|
| **冻结点（本轮证据层基准）** | **2026-10-13 05:04:50 +0800** | 本决议采集时刻 |
| 装配层最后一次写入 | 2026-10-13 03:38 | `~/.dsh/state/mount-audit.jsonl`；bundle `README.md` 03:35、`provenance.json`/`PROVENANCE.md` 03:34 |
| 判据脚本停止增长 | 2026-10-13 02:56:51（67146 B） | `verify_migration_state.py` 两次读数间隔 8s **完全一致** |
| `cordis.yml` 05:02:39 写入归因 | 服务重启（非配置变更） | 内容为固定注释 + `[]`；两次读数一致；与 R12 §0.1「须重启 `dsh-web.service`」一致 |
| 迁移线轮次 | R11 收尾（`r11-final-gates.out.txt` 03:38）→ **R12 收官轮**（`12-接续prompt` 03:30） | 迁移线任务目录 |
| 用户侧动作 | 已完成重启（05:02） | 同上 |

**残余风险**：R12 为收官轮，仍含「两条小收口」；若其再次写入装配层，本冻结点失效。
⇒ **P2 取快照前须复验一次**（同一 `stat` 两次读数法），并把 `as_of` 写入 `manifest.json`。

---

## P0-3 外部证据指针（只引用，不复制）

| 指针 | 位置 | 状态 | 用途 |
|---|---|---|---|
| `ADR-010` | `Mission-file/2026-10/1011-迁移适配-E环门控通道与R环纠正/arch/ADR-010.json` | `proposed` | E 环门控通道 `run_gate` 的决策依据 |
| `ADR-011` | `Mission-file/2026-10/1011-deepseek harness-提示词迁移工程-从opencode/1011-全面适配性迁移分析/arch/ADR-011.json` | `proposed`（门控 6/6 PASS） | `dsh-config` 能力包边界 |
| `ADR-012` | 同 ADR-011 目录 | `proposed`（门控 6/6 PASS） | R 环 R-A 载体（零插件零重启） |
| `迁移台账.yaml` | 同 ADR-011 目录 | 43 个任务：**done 36 / partial 2 / not_done 3 / deferred 1** | 迁移完成度的机读单一来源 |
| 收官取证 | 同目录 `evidence/r11-final-gates.out.txt`、`r11-migration-audit.json`、`迁移完成度审查报告-v10.md` | — | 迁移线最终读数 |

**引用纪律**：
1. 所有指针**带路径限定**——`0928-前端设计方法论建设` 线亦存在同名 `ADR-011`（不同域），裸写会指向错件；
2. KB 侧只登记「指针 + 状态 + 用途」，⛔ 不复制 ADR 正文进公开库；
3. ADR 状态均为 `proposed`，KB 引用时须如实标注，⛔ 不得写成「已定稿」。

---

## P0 完成判据核对

| 判据 | 结果 |
|---|---|
| 口径唯一且无二义 | ✅ 四口径差异已归因，权威口径已定义 |
| 静止点有书面结论 | ✅ 05:04:50，附残余风险与复验要求 |
| 外部证据指针可引用 | ✅ 5 类指针，附引用纪律 |
