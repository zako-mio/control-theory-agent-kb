# 实验记录：PRIME（RLM coding agent）— 标准实验组

> 产品：PRIME（`best-radar/bradar-prime-agent`，TypeScript monorepo）
> 实验日期：2026-09-07　实验方式：**源码级可逆故障注入点分析**（不实机破坏）
> 契约约束：仅分析可逆注入点，不改源码，不实机运行破坏实验

## 实验设计框架

PRIME 的核心是 RLM（Recursive Language Model）+ Continual Harness。每个实验场景映射到可逆注入点：环境变量 `RLM_DEPTH`/`RLM_MAX_DEPTH`、gate 配置 `commands:[]`、`/refine` 的 snapshot rollback、autonomous 的 `maxContinuations` 等。

| 场景 | 可逆注入点 | 触发行为 | 控制论环节 | 回滚方式 |
|------|-----------|---------|-----------|---------|
| 正常基线 | 无（默认） | RLM REPL 运行 | 设定值+执行 | — |
| 故障注入 | `RLM_MAX_DEPTH=1`（注入超深递归） | host 拒绝 rlm.run | T 环限幅 | 改回 2 |
| 上下文污染 | 调低 compaction `keepRecentTokens` | 触发压缩 | M 环信息滤波 | 改回 20k |
| 超长循环 | `maxContinuations=1` + 空 gate | bounded continuation | R 环误差回灌 | 改回 3 |

## 各场景源码证据

### 场景1：正常模式（基线）
- 核心：常驻 Python REPL（`packages/agent` + `core/tools/ipython.ts`）+ `/goal` 持久目标 + `rlm()` 递归子代
- 控制论：设定值 r 由 `/goal` 持久化，RLM 执行

### 场景2：故障注入 — 递归深度超限（T 环限幅，**可逆注入点**）
- **注入点**：环境变量 `RLM_DEPTH`/`RLM_MAX_DEPTH`，测试源码 `file-operations.test.ts:163-168` 严格校验非负整数，非法值抛 `"RLM_DEPTH must be a non-negative integer"`。
- **触发行为**：`RLM_DEPTH < RLM_MAX_DEPTH`（默认 2）；超深度 host 拒绝 `rlm.run` 并 raise 到 Python——**执行器硬约束 u_sat**。
- **控制论**：KT-ctrl-034 安全边际/硬约束限幅——深度限幅防递归爆炸。
- **回滚**：改回 `RLM_MAX_DEPTH=2`。

### 场景3：上下文污染（M 环信息滤波，**可逆注入点**）
- **注入点**：compaction `keepRecentTokens=20k`，`contextTokens > contextWindow - reserveTokens` 触发。
- **触发行为**：向后找 cut point 保留近期 token，生成结构化 summary（读/改文件累计跟踪），`CompactionEntry` 含 `firstKeptEntryId`；重复 compaction 从上次边界起算。
- **控制论**：KT-ctrl-011 卡尔曼更新 + KT-ctrl-014 信息降维（只保留增量信息）。
- **回滚**：调回 20k。

### 场景4：超长循环 — Autonomous bounded continuation（R 环误差回灌，**可逆注入点**）
- **注入点**：autonomous `maxContinuations=3/maxTurns=12/maxTokens=80k/timeoutMs=30min` + gate 配置。
- **触发行为**：`shouldAutonomouslyContinue` 根据 gateResult/limitReason 决定；gate 失败时 `buildAutonomousGateFailureContinuation` 将失败命令/输出/bounded 提示注入下一轮（"Fix the failure, then produce terminal evidence"）——**负反馈误差 e 直接回灌执行器**。
- **控制论**：KT-ctrl-044 MPC 滚动时域（前瞻一组、只进一步、根据门重算）。
- **回滚**：改回 maxContinuations=3。

## PRIME 标准实验组结论

| 场景 | 控制论环节 | 可逆注入点 | 行为 | 强弱项 |
|------|-----------|-----------|------|-------|
| 1 正常 | 设定值+执行 | 默认 | RLM REPL 运行 | 基线 |
| 2 超深递归 | T 环限幅 | RLM_DEPTH/MAX_DEPTH | host 拒绝 rlm.run | 强（防爆炸） |
| 3 上下文污染 | M 环信息滤波 | compaction keepRecentTokens | 压力压缩| 强（只留增量） |
| 4 超长循环 | R 环误差回灌 | maxContinuations+gate | gate 失败注入下一轮 | 强（MPC 式） |

**整体控制论结论**：PRIME 的**可逆注入点高度集中在 R 环（/refine + gate + autonomous）与 M 环（continual harness）**——它把「自我改进」做成持久可撤销的状态（snapshot rollback），比 opencode/dsh 更有「自整定」色彩。但 E 环默认 gate 为空（`commands:[]` = 开环），`/refine` 与 auto-refine review 仍是同一 LLM 自评（共模偏置）。印证 phase3 画像：**R 环最强、E 环最弱**。

> ⚠️ 契约遵守确认：本次实验为**纯源码分析**（未实机运行、未修改任何源码/配置文件、无破坏）。可逆注入点为理论定位，实际注入需在隔离环境执行且可回滚。
