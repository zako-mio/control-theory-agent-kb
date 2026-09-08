# 实验记录：claude-code — 标准实验组

> 产品：claude-code（`05-source/claude-code/`，Anthropic，Node.js 18+）
> 实验日期：2026-09-07　实验方式：**源码级可逆故障注入点分析**（不实机破坏）

## 实验设计框架

claude-code 的容错集中在 hooks 体系（PreToolUse/PostToolUse/Stop/SessionStart/PreCompact）+ 官方插件（security-guidance/code-review/feature-dev/ralph-wiggum）。每个实验场景映射到可逆注入点。

| 场景 | 可逆注入点 | 触发行为 | 控制论环节 | 回滚方式 |
|------|-----------|---------|-----------|---------|
| 正常基线 | 默认 | ReAct 主循环 | 设定值+执行 | — |
| 故障注入 | PreToolUse `permissionDecision=deny` | 工具执行前拦截 | T 环限幅 | 改回 allow/ask |
| 上下文污染 | `CLAUDE_CODE_DISABLE_1M_CONTEXT` | 强制 hold 到 200K | M 环信息滤波 | 移除 disable |
| 超长循环 | ralph-wiggum `--max-iterations` | 积分项上限 | R 环防 windup | 改回默认 |

## 各场景源码证据

### 场景1：正常模式（基线）
- 核心 CLI 主循环：开放 ReAct 开环基线（模型自主产出、自主决定是否测）
- M 环：CLAUDE.md 层级上下文 + auto-compact（967K tokens 触发）

### 场景2：故障注入 — PreToolUse 仲裁（T 环，**可逆注入点**）
- **注入点**：`hook-development/SKILL.md` L127-153，PreToolUse 钩子可 `approve/deny/ask`（`permissionDecision`），支持 regex matcher。
- **触发行为**：工具执行前 `deny` → 拦截（硬约束限幅 KT-ctrl-034）。可 `updatedInput` 改写工具入参。
- **回滚**：改回 allow/ask。

### 场景3：上下文污染（M 环信息滤波，**可逆注入点**）
- **注入点**：`CLAUDE_CODE_DISABLE_1M_CONTEXT`（CHANGELOG L1046）+ auto-compact 阈值。
- **触发行为**：长上下文 → auto-compact 触发压缩（提炼增量信息）或强制 hold 到 200K。
- **控制论**：KT-ctrl-011 卡尔曼更新 + KT-ctrl-014 信息滤波。
- **回滚**：移除 disable，恢复 1M 上下文。

### 场景4：超长循环 — ralph-wiggum 自指迭代（R 环防 windup，**可逆注入点**）
- **注入点**：`plugins/ralph-wiggum/` Stop 钩子反复喂同一 prompt 直到输出 completion promise，`--max-iterations` 是积分项上限。
- **触发行为**：反复自指迭代直到收敛，max-iterations 超限停止（anti-windup）。
- **控制论**：KT-ctrl-020 PID 三环节（I 累积）+ KT-ctrl-025 稳态带验收（completion-promise）。
- **回滚**：改回默认 max-iterations。

## claude-code 标准实验组结论

| 场景 | 控制论环节 | 可逆注入点 | 行为 | 强弱项 |
|------|-----------|-----------|------|-------|
| 1 正常 | 设定值+执行 | 默认 | ReAct 主循环 | 基线 |
| 2 PreToolUse | T 环限幅 | permissionDecision | 拦截/改写 | 强（hooks 最丰富） |
| 3 上下文污染 | M 环信息滤波 | auto-compact | 压缩提炼 | 强（缺置信度） |
| 4 超长循环 | R 环防 windup | ralph-loop max-iterations | 积分上限 | 中 |

**整体控制论结论**：claude-code 的**可逆注入点集中在 hooks 体系**——PreToolUse（限幅器）、Stop/PostToolUse（传感器+校正）、Stop block（反馈闸门）。E 环靠外挂插件（security-guidance 三层验证 + code-review 置信度过滤），无内置常驻 Critic —— 印证画像：**T 环最强、E 环未内置（贴片式）、M 环缺置信度**。

> ⚠️ 契约遵守确认：本次实验为**纯源码分析**（未实机运行、未修改任何源码/配置文件、无破坏）。
