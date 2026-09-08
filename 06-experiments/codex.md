# 实验记录：codex（Codex CLI）— 标准实验组

> 产品：codex（`05-source/codex/`，OpenAI，Rust）
> 实验日期：2026-09-07　实验方式：**源码级可逆故障注入点分析**（不实机破坏）

## 实验设计框架

codex 的容错集中在 sandbox（OS 级多层沙箱）、approvals（审批策略管线）、guardian（评审器 + 电路断路器）、exec。每个实验场景映射到可逆注入点。

| 场景 | 可逆注入点 | 触发行为 | 控制论环节 | 回滚方式 |
|------|-----------|---------|-----------|---------|
| 正常基线 | 默认 | exec 执行 | 设定值+执行 | — |
| 故障注入 | exec 超时 `DEFAULT_EXEC_COMMAND_TIMEOUT_MS=10s` | 超时看门狗 | T 环限幅 | 改回 |
| 上下文污染 | `COMPACT_USER_MESSAGE_MAX_TOKENS=20k` | 触发压缩 | M 环信息滤波 | 改回 |
| 超长循环 | Guardian `MAX_CONSECUTIVE_DENIALS_PER_TURN=3` | 3 次拒绝中断 | R 环电路断路器 | 改回 |

## 各场景源码证据

### 场景1：正常模式（基线）
- `core/src/exec.rs`：exec 命令执行，捕获 stdout。
- M 环：上下文 fragment 体系（bounded/hard-cap）+ 分层压缩。

### 场景2：故障注入 — exec 超时看门狗（T 环，**可逆注入点**）
- **注入点**：`core/src/exec.rs` `DEFAULT_EXEC_COMMAND_TIMEOUT_MS = 10_000`。
- **触发行为**：超时 → `ExecExpiration::Timeout` 终止 + `IO_DRAIN_TIMEOUT_MS = 2_000` 防挂死（KT-ctrl-034 看门狗）。
- **回滚**：改回默认值。

### 场景3：上下文污染（M 环信息滤波，**可逆注入点**）
- **注入点**：`core/src/compact.rs` `COMPACT_USER_MESSAGE_MAX_TOKENS = 20_000` + `context_window.rs`。
- **触发行为**：长上下文 → 本地/远程压缩 + token 预算回灌。
- **控制论**：KT-ctrl-011 卡尔曼更新 + KT-ctrl-014 信息滤波（"No items > 10K tokens + bounded hard cap"）。
- **回滚**：改回 20k。

### 场景4：超长循环 — Guardian 电路断路器（R 环防 windup，**可逆注入点**）
- **注入点**：`core/src/guardian/mod.rs` `MAX_CONSECUTIVE_GUARDIAN_DENIALS_PER_TURN=3`（Cyber 模型 1 次）。
- **触发行为**：连续 3 次拒绝 → `InterruptTurn` 强制中断（anti-windup）；`record_non_denial` 清零计数。
- **控制论**：KT-ctrl-022 积分 I / 防 windup + KT-ctrl-025 防 overshoot。
- **回滚**：改回 3。

## codex 标准实验组结论

| 场景 | 控制论环节 | 可逆注入点 | 行为 | 强弱项 |
|------|-----------|-----------|------|-------|
| 1 正常 | 设定值+执行 | 默认 | exec 执行 | 基线 |
| 2 exec超时 | T 环看门狗 | DEFAULT_EXEC_TIMEOUT | 超时终止 | 强（OS 级沙箱） |
| 3 上下文污染 | M 环信息滤波 | COMPACT 上限 | 压缩提炼 | 强（缺置信度） |
| 4 超长循环 | R 环电路断路器 | MAX_CONSECUTIVE_DENIALS | 3 次中断 | 强（显式 anti-windup） |

**整体控制论结论**：codex 的**可逆注入点集中在 T 环（OS 级沙箱 + 审批管线 + 超时看门狗）与 R 环（Guardian 电路断路器防 windup）**，E 环有 Guardian + Review 双独立评审器（带 confidence_score）。印证画像：**T/E 环强、P 环弱（MPC 玩具级）、M 环缺置信度（事实串而非信念状态）**。

> ⚠️ 契约遵守确认：本次实验为**纯源码分析**（未实机运行、未修改任何源码/配置文件、无破坏）。
