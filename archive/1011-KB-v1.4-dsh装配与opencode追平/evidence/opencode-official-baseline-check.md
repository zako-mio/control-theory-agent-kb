# opencode 官方基线点检（1.18.29 → 1.18.35，源码级）

取证日：2026-10-11　取证方式：`git fetch --depth=1 origin refs/tags/v1.18.35`（定向代理）+ `git ls-tree` / `git diff --shortstat`
取证仓：`/home/zako-mio/opencode/archive/Mission-file/2026-09/0902-opencode-dag/opencode-src-v1.18.29`（remote `https://github.com/anomalyco/opencode`）

## 1. 包级结构：零变化
| 项 | v1.18.29 | v1.18.35 | 判定 |
|---|---|---|---|
| `packages/*/package.json` 与 `packages/*/*/package.json` 计数 | **36** | **36** | 一致 |
| 包集合（路径排序 diff） | — | — | **完全一致（无新增/无删除）** |
| `packages/` 顶层目录名 | 32 | 32 | 完全一致 |

⇒ **官方包级 DAG 结构与依赖边不变**，1.18.30 → 1.18.35 只需更新**版本标注**，不需要重采包图。

## 2. 文件级变更量（方法自校验）
| 区间 | 变更量 |
|---|---|
| `v1.18.29 → v1.18.30` | **105 files, +1676 / −403** ← 与 KB v1.3 画像记录的「30 commits / 105 文件（+1676/−403）」**逐项吻合**，方法可信 |
| `v1.18.29 → v1.18.35` | **328 files, +17411 / −8779** |
| `v1.18.30 → v1.18.35` | 318 files, +15961 / −8602 |

## 3. 变更分布（29→35，按顶层目录）
```
73 packages/stats      73 packages/console     60 packages/web
39 packages/opencode   20 artifacts/glm52-rise-video
10 packages/core        7 packages/tui          7 .github/workflows
 4 packages/ui          3 packages/app
```
⇒ 改动集中在 **stats（新增 agent-readable 数据格式）/ console / web / opencode 主包**，核心 `core` 仅 10 文件；**未触及包间依赖图**。

## 4. 版本语义（上游 release notes，GitHub API 实测）
- `v1.18.35` = 1.18.x 末线（2026-10-06）
- `v1.19.0`（2026-10-11T01:39Z）= 通往 **OpenCode 2** 的升级入口（release note 明写 `opencode upgrade --major`）
- 本机运行时 = **1.18.35**；上游最新 = **v1.19.0（只登记不追）**

## 5. 对两个库的结论
- **KB**：官方内核五环基线分值**不调整**（包级结构未变、改动未触及五环机制）
- **opencode-dag**：官方侧只需 `official-dag.json` 的版本标注 1.18.30 → 1.18.35（36 包 / 68 边不变）
