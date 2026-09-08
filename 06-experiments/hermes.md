# 实验记录：Hermes Agent — 标准实验组

> 产品：hermes（`05-source/hermes-agent/`，NousResearch，MIT）
> 实验日期：2026-09-07　实验方式：**源码级可逆故障注入点分析**（不实机破坏，符合契约红线「可逆+受控」）

## 实验设计框架

hermes 的容错机制集中在 `agent/tool_executor.py`、`iteration_budget.py`、`deadline.py`、`verification_stop.py`。每个实验场景映射到可逆源码注入点。

| 场景 | 可逆注入点 | 触发行为 | 控制论环节 | 回滚方式 |
|------|-----------|---------|-----------|---------|
| 正常基线 | 默认 | tool_executor 执行 | 设定值+执行 | — |
| 故障注入 | `iteration_budget` 设父=1 | 迭代预算超限停止 | T 环限幅 | 改回 500 |
| 上下文污染 | 调低 gateway 压缩阈值 <85% | 触发两层压缩 | M 环信息滤波 | 改回 85% |
| 超长循环 | `max_verify_nudges=1` | 回合末验证门控限幅 | R 环防 windup | 改回 3 |

## 各场景源码证据

### 场景1：正常模式（基线）
- `agent/tool_executor.py`（84KB）：完整工具执行中间件，并发/顺序门控、心跳、超时/取消、授权门
- M 环两层压缩（`compression_facade.py` gateway 85% + `context_compressor.py` agent 50%）

### 场景2：故障注入 — 迭代预算限幅（T 环，**可逆注入点**）
- **注入点**：`agent/iteration_budget.py`，每个 agent（父 500 次、子 50 次）线程安全计数器，超限停止。
- **触发行为**：迭代预算耗尽 → 停止（输入饱和 KT-ctrl-034）。
- **回滚**：改回父 500/子 50。

### 场景3：上下文污染（M 环信息滤波，**可逆注入点**）
- **注入点**：`agent/compression_facade.py` gateway 会话卫生阈值 85%，agent `ContextCompressor` 50%。
- **触发行为**：超阈值 → 先剪旧工具结果（不调 LLM），再用 auxiliary 压缩模型生成结构化摘要——信息降维。
- **控制论**：KT-ctrl-011 卡尔曼更新 + KT-ctrl-014 信息滤波。
- **回滚**：调回阈值。

### 场景4：超长循环（R 环防 windup，**可逆注入点**）
- **注入点**：`agent/verification_stop.py` `max_verify_nudges=3`、`max_attempts=2`。
- **触发行为**：编辑代码后缺新验证证据时注入"运行验证→读失败→修复→总结"继续指令，nudges 超限停止——防无限纠缠。
- **控制论**：KT-ctrl-022 积分 I / 防 windup（限幅）。
- **回滚**：改回 max_verify_nudges=3。

## hermes 标准实验组结论

| 场景 | 控制论环节 | 可逆注入点 | 行为 | 强弱项 |
|------|-----------|-----------|------|-------|
| 1 正常 | 设定值+执行 | 默认 | tool_executor 执行 | 基线 |
| 2 迭代预算 | T 环限幅 | iteration_budget | 超限停止 | 强 |
| 3 上下文污染 | M 环信息滤波 | gateway/context 压缩 | 两层压缩蒸馏 | 强（带置信度标记） |
| 4 超长循环 | R 环防 windup | max_verify_nudges | 限幅停止 | 中强 |

**整体控制论结论**：hermes 的**可逆注入点集中在 T 环（执行器高密度容错）与 M 环（多层记忆压缩）**，且 E 环拥有真实独立基础设施（verification_evidence 证据台账 + verification_stop 门控 + verify 强验证器 + review 评审器）。R 环靠后台 fork 反思（不污染缓存）。印证画像：**M 环最强、P 环最弱、E 环有专属基础设施（非最弱）**。

> ⚠️ 契约遵守确认：本次实验为**纯源码分析**（未实机运行、未修改任何源码/配置文件、无破坏）。
