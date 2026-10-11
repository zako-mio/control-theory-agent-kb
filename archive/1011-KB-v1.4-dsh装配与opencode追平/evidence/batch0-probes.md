# Batch 0 探针与状态核对（2026-10-11）

## 1. 深度 2 委派探针 —— 不可用
- 探针：由 `subagent`（depth 1）尝试再派一个子 Agent。
- 结果：**失败**。逐字错误：`subagent depth 2 exceeds maxDepth 1`
- 结论：当前 runtime `maxDepth = 1`，深度 2 委派不可用 → 按 PLAN §4 预案，分片改用 `workflow` 工具（其 agent 具备读源码 + 写文件能力，已在 2026-10-11 dsh-plugin-dag 轮次实战验证）。
- 附注：子 Agent 侧工具清单中**没有** `oc_*` 具名 worker，只有 `subagent`；`oc_*` 仅主 Agent 可用。

## 2. 视觉探针 —— 可用
- 探针：`read_image` 读 `07-checkpoint/case-dsh-v3.png`。
- 结果：**成功**，返回 1440x2000 px 图像并可正确描述页面内容（标题「DeepSeek Harness (dsh v0.1.1-rc.2) — 控制论画像」、SP/E/T 环卡片、侧栏 mag 01-20）。
- 结论：L4 视觉层由主 Agent 自看，不委派、不交人看。

## 3. 三库状态核对
| 库 | 分支 | HEAD | 工作区 |
|---|---|---|---|
| control-theory-agent-kb | main | 83d02b3 (v1.3, 2026-09-11 23:04) | 干净 |
| opencode-dag-analysis | main | 6e02692 (2026-09-11 23:04) | 干净 |
| deepseek-harness-plugin-dag | v0.2.1-alpha.2 | af5b963 | 干净 |

- **修正 D5**：`deepseek-harness-plugin-dag` 的 `v0.2.1-alpha.2` 分支**已在远端**（`git rev-list --left-right --count origin/v0.2.1-alpha.2...v0.2.1-alpha.2` = `0 0`；`git ls-remote` 显示远端 `af5b9630…`）。`master` 仍为 `ca92fcb`（RC8，未跟进，符合决议 D5）。
- ⇒ Batch 3 的推送工作仅剩 KB 与 opencode-dag 两库；dsh-plugin-dag 只需收尾复核。

## 4. 前像（git 基线）
见同目录 `baseline-commits.txt`（三库 commit sha 已记录，git 树本身即可回滚，未另做整树拷贝）。
