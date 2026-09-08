# 实验记录：DeepSeek Harness (dsh v0.1.1-rc.2) — 标准实验组

> 产品：deepseek-harness `v0.1.1-rc.2`（cordis 插件装配）
> 实验日期：2026-09-07　实验方式：**源码级可逆故障注入点分析**（不实机破坏，符合契约红线「可逆+受控」）
> 契约约束：仅分析可逆注入点，不改源码文件，不实机运行破坏实验

## 实验设计框架

dsh 是 cordis 插件，每个实验场景映射到可逆的源码注入点（guard 目录的插件/投影），通过「修改 guard 配置 → 观察行为 → 回滚」实现。以下为各场景的**可逆注入点分析**（指出改哪里、会触发什么行为、如何回滚）。

| 场景 | 可逆注入点 | 触发行为 | 控制论环节 | 回滚方式 |
|------|-----------|---------|-----------|---------|
| 正常基线 | 无（默认装配） | 三瀑布执行 | 设定值+执行 | — |
| 故障注入 | `guard/timeout-policy` 设 `timeoutMs=0` | 工具超时→`TOOL_TIMEOUT` | T 环看门狗 | 改回 timeoutMs |
| 上下文污染 | `compaction-basic` / `token-meter` 调高压力阈值 | 触发压缩 | M 环信息滤波 | 改回阈值 |
| 超长循环 | `guard/repeat-tool-reminder` 阈值改 1 | 同工具同参达阈值→提醒 | R 环（软 D 项） | 改回阈值 3/5/8 |

## 各场景源码证据

### 场景1：正常模式（基线）
- 装配：`packages/bundle/base/cordis.patch.yml`（76 核心插件）
- 执行：`packages/core/tools` 的 pre-execute→execute→post-execute 三瀑布
- 控制论：设定值 r 由 plan-mode/goal/todo 生成，T 环三瀑布执行

### 场景2：故障注入 — 工具超时（T 环看门狗，**可逆注入点**）
- **注入点**：`packages/guard/timeout-policy/src/index.ts` 工具声明 `timeoutMs`，接 `exec.signal`，超时映射为 `TOOL_TIMEOUT`。
- **源码证据**：
  ```
  /**
   * Cooperative tool-call timeout enforcer. A tool declares `timeoutMs` and
   * promises to honor `exec.signal`; this wrapper arms that deadline and maps its
   * own expiry to `TOOL_TIMEOUT` without racing or abandoning the tool promise.
   */
  export const TOOL_TIMEOUT = 'TOOL_TIMEOUT'
  ```
- **触发行为**：工具超时 → 返回 `TOOL_TIMEOUT` 结构化结果（不是抛错）→ 回灌模型（R 环纠偏）。
- **控制论**：KT-ctrl-034 饱和/看门狗——协作式超时，非竞速硬杀。
- **回滚**：延长 `timeoutMs` 即恢复。

### 场景3：上下文污染（M 环信息滤波，**可逆注入点**）
- **注入点**：`packages/llm/token-meter`（回放感知 token 计量）+ `packages/compaction/compaction-basic`（压力压缩）+ `tool-result-pruner`（裁剪）。
- **触发行为**：token 压力超阈值 → `agent/pre-step` 触发压缩 → 先裁工具结果，再 LLM 摘要（复用 KV 前缀缓存），`CONTEXT_WINDOW_EXCEEDED` 时溢出恢复。
- **控制论**：KT-ctrl-011 卡尔曼更新 + KT-ctrl-014 信息降维——只保留增量信息。
- **回滚**：调低压力阈值即恢复。

### 场景4：超长循环（R 环软 D 项，**可逆注入点**）
- **注入点**：`packages/guard/repeat-tool-reminder`，阈值 3/5/8（连续同参调用同一工具），只 enrich 注入提醒，**不 veto**（软 D）。
- **触发行为**：同工具同参连续超阈值 → 注入提醒到提示词（趋势预警）。
- **控制论**：KT-ctrl-023 微分 D（趋势预判）——但只提醒不硬停。
- **回滚**：改回阈值或移除插件。

## dsh 标准实验组结论

| 场景 | 控制论环节 | 可逆注入点 | 行为 | 强弱项 |
|------|-----------|-----------|------|-------|
| 1 正常 | 设定值+执行 | 默认装配 | 三瀑布执行 | 基线 |
| 2 超时故障 | T 环看门狗 | timeout-policy | TOOL_TIMEOUT 回灌 | 强（协作式超时） |
| 3 上下文污染 | M 环信息滤波 | token-meter+compaction | 压力压缩 | 强（只留增量） |
| 4 超长循环 | R 环软 D | repeat-tool-reminder | 注入提醒 | 弱（只提醒不否决） |

**整体控制论结论**：dsh 的**可逆注入点设计优秀**——把看门狗/限幅/压缩/提醒全部沉淀为 guard 目录的独立插件，实现"改插件配置即注入扰动、回滚即恢复"。这体现了**模块化的容错性**。但 E 环无独立 validator（全库 grep 无 critic），R 环只能对「感知到的失败」纠偏，放大的是错误信号而非误差信号。印证 phase3 画像：T 环最强、E 环最弱。

> ⚠️ 契约遵守确认：本次实验为**纯源码分析**（未实机运行、未修改任何源码/配置文件、无破坏）。可逆注入点为理论定位，实际注入需在隔离环境执行且可回滚。
