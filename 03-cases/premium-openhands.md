# OpenHands (All Hands AI) — 精装房控制论画像

> 定位：自托管编码 Agent 控制中心（Agent Canvas UI + 多后端 + 子 Agent 预设 + 沙箱 + 自动化）　｜　厂商：All Hands AI　｜　分类：开源成品化　｜　审计日期：2026-09-08
> 精装度：4.2/5　｜　一手/二手：一手　｜　证据强度：源码级

## 0. 精装度评估（Premium Score）

**综合评分**：4.2/5 — 开源自研的编码 Agent 成品，**`npm install -g @openhands/agent-canvas` 或 `docker run` 一键起**，预装 Agent Canvas UI + 沙箱 + 子 Agent 预设 + 技能/工具集 + 自动化仓库 + 多后端切换，零配置即跑端到端任务。

**预装能力清单**：
| 维度 | 预装情况 | 依据 |
|------|---------|------|
| 多Agent编排 | ✅ | `openhands-tools` 的 `task`（阻塞式子 Agent 委派）+ `delegate`（委托可视化）+ subagent registry（源码级） |
| Skill库 | ✅ | 内置工具集 19 目录（terminal/file_editor/browser_use/glob/grep/apply_patch/task_tracker 等）+ 技能市场/插件注册（源码级） |
| 工作流编排 | ✅ | `tools/workflow`（definition/impl）+ Agent Canvas automations（Slack/GitHub/Linear 触发）（源码级） |
| 模型接入 | ✅ | `pyproject.toml` workspace + LiteLLM 底座，README「Bring your own model / any LLM」（源码级） |
| 一键部署 | ✅ | `package.json` bin=`agent-canvas`；`docker run ghcr.io/openhands/agent-canvas:1.16.0`（源码级） |
| 沙箱/隔离 | ✅ | Docker Sandbox 模式（README Option 2）+ agent-server 后端隔离（源码级） |
| MCP生态 | ✅ | web_researcher 预设内置 `mcp_servers.fetch`（uvx）+ 工具注册表（源码级） |
| 记忆 | 部分 | SDK `context.condenser`（LLMSummarizingCondenser）+ 会话状态；无显式置信度信念状态（源码级） |

**声称 vs 实际**：官方声称「The self-hosted developer control center for coding agents and automations」 → **源码级证实为自研一手成品**：`package.json`（name=`@openhands/agent-canvas` v1.16.0，bin=`agent-canvas`），`software-agent-sdk/pyproject.toml` 明确 4 个 workspace 自研包（`openhands-sdk` / `openhands-tools` / `openhands-workspace` / `openhands-agent-server`）；子 Agent 预设见 `openhands-tools/openhands/tools/preset/subagents/{default,code_explorer,web_researcher,bash_runner}.md`。与 `premium-evidence.md` 一致：**一手 + 精装度 4.2 + 源码级**。

---

## 1. 设定值（Setpoint）——Agent Canvas 把意图固化为可运行会话

**承担角色**：以「Agent Canvas UI + 会话/任务定义 + 自动化触发」把用户意图固化为可运行、可切换后端、可自动触发的 Agent 会话，作为设定值 r。

**关键机制**：
- **Agent Canvas UI**：`package.json` 描述「Agent Canvas UI for OpenHands - run AI coding agents with a visual interface」，可视化创建与管理会话（源码级）。
- **多后端切换**：README 明示可在 local/remote/cloud 后端间切换而不失焦，「Switch between local, remote, and cloud agents」（源码级）。
- **自动化触发**：Agent Canvas automations 支持 Slack/GitHub/Linear 集成 + 定时/webhook 触发，设定值从手动扩展为事件驱动（源码级）。
- **Agent 定义注册**：`openhands.sdk.subagent` 提供 `register_agent` / `load_project_agents` / `load_user_agents` / `discover_agents`，设定值可由项目/用户级 Agent 定义注入（源码级）。
- **TaskOutcome 契约**：`preset/task_outcome.py` 的 `TaskOutcome` / `TaskOutcomeStatus` 为任务设定值提供结构化结果契约（源码级）。

**控制论映射**：KT-ctrl-045（规划-执行解耦，会话/自动化=可评审契约）+ KT-ctrl-041（分层控制结构）+ KT-ctrl-002（负反馈闭环结构，目标=设定值 r）。

**强弱项**：⭐**强**——设定值有可视化 UI、多后端、事件触发、Agent 定义注册、TaskOutcome 契约，闭环入口完整。⚠️**弱**——设定值成功判据仍以 Agent 输出与 TaskOutcome 状态承载，缺机器可验证的量化目标函数。

---

## 2. E 环 — 评估/传感器（(E 环) 工具观测 + TaskOutcome + 委托可视化）

**承担角色**：为闭环生产「执行是否达标」的反馈信号，来源为工具观测（terminal/file_editor/browser）、TaskOutcome 状态、委托可视化，**无独立通用 Critic 模型**（但有 ask_oracle / tom_consult 类顾问工具）。

**关键机制**：
- **工具观测（Observation）**：SDK 统一 `ToolObservation` 契约，如 `TaskTrackerObservation` / `BrowserObservation` / `DelegateObservation`——格式可信、可回灌（源码级）。
- **TaskOutcome 状态**：`TaskOutcomeStatus` 显式标注任务结果状态（成功/失败/部分），是少见的显式结果信号（源码级）。
- **browser_use 观测**：`tools/browser_use/` 提供导航/点击/取内容/取状态等观测动作，测量环境状态（源码级）。
- **ask_oracle / tom_consult 顾问工具**：独立工具调用外部"神谕"做判断，构成评估型传感器（源码级）。
- **委托可视化**：`delegate/visualizer.py` 的 `DelegationVisualizer` 呈现子 Agent 委派过程，供人工观测（源码级）。

**控制论映射**：KT-ctrl-006（反馈灵敏度/鲁棒性基础）+ KT-ctrl-012（观测噪声 R，工具观测可信度）+ KT-ctrl-035（扰动观测器 DOB，ask_oracle 在线研判）+ KT-ctrl-001（开环 vs 闭环）。

**强弱项**：🟢 中强——统一 Observation 契约 + TaskOutcome 状态 + 顾问工具，评估信号比多数产品结构化。🔴 **相对最弱环**——**缺独立、每步强制运行的通用 Critic**；TaskOutcome 依赖 Agent 自报，评估质量仍受限于模型自述。

---

## 3. T 环 — 执行器/工具（(T 环) 19 类工具集 + Docker 沙箱 + 多 Agent 后端）

**承担角色**：把动作以「丰富工具集 + 沙箱隔离 + 多后端执行」落地，是唯一直接接触代码与外部系统的执行器，工程化最成熟。

**关键机制**：
- **19 类内置工具目录**：`apply_patch`、`ask_oracle`、`browser_use`、`delegate`、`file_editor`、`glob`、`grep`、`planning_file_editor`、`task`、`task_tracker`、`terminal`、`tom_consult`、`workflow` 等（`openhands-tools/openhands/tools/`，源码级）。
- **Docker 沙箱模式**：README Option 2 用 `docker run -v PROJECTS_PATH:/projects` 隔离执行，Agent 仅能访问指定目录（源码级）。
- **terminal 执行器**：`tools/terminal/` 提供命令执行，是核心动作出口（源码级）。
- **多 Agent 后端**：README 明示可跑 OpenHands / Claude Code / Codex / Gemini / 任意 ACP 兼容 Agent——执行器可插拔（源码级）。
- **依赖安全护栏**：`software-agent-sdk/pyproject.toml` 的 `exclude-newer = "7 days"` + 多条 CVE 约束，执行环境供应链限幅（源码级）。
- **file_editor / apply_patch**：两种文件编辑执行器，动作粒度可选（源码级）。

**控制论映射**：KT-ctrl-034（安全边际/硬约束限幅，Docker 沙箱 + 依赖护栏）+ KT-ctrl-033（冗余与仲裁，多 Agent 后端可切换）+ KT-ctrl-031（鲁棒稳定性，沙箱隔离防污染主机）+ KT-ctrl-030（模型不确定性，多后端降级）。

**强弱项**：⭐⭐**最突出**——工具集最丰富（19 类目录）、Docker 沙箱 + 多后端 + 依赖护栏构成完整「限幅 + 隔离 + 冗余」，是精装度 4.2 的支柱。⚠️**弱**——Option 1「Without a Sandbox」默认直跑主机文件系统（README 明确警告），沙箱需用户主动选 Docker。

---

## 4. M 环 — 记忆/状态估计（(M 环) 会话状态 + Condenser + 项目/用户 Agent 记忆）

**承担角色**：以「会话状态 + context condenser + 项目/用户级 Agent 定义」维护「当前做到哪、该按谁的定义做」，通过 LLM 摘要压缩上下文，**未显式建模置信度**。

**关键机制**：
- **LLMSummarizingCondenser**：`preset/planning.py` 与 `openhands.sdk.context.condenser` 用 LLM 摘要压缩历史，是典型的信息滤波/降维（源码级）。
- **会话状态（LocalConversation）**：`task/impl.py` 引用 `LocalConversation`，会话维护 Agent 执行状态（源码级）。
- **项目/用户级 Agent 记忆**：`load_project_agents` / `load_user_agents` 从目录发现 Agent 定义，构成跨会话的持久配置记忆（源码级）。
- **规划文件**：`planning_file_editor` 把计划落到文件，作为可持久化的状态载体（源码级）。
- **task_tracker**：`TaskTrackerTool` 跟踪任务状态，构成任务级状态估计（源码级）。

**控制论映射**：KT-ctrl-010（状态估计，会话+跟踪折叠出任务状态）+ KT-ctrl-011（Kalman 预测-更新，会话推进=预测、工具观测=更新）+ KT-ctrl-014（信息滤波/降维，Condenser 摘要）。**缺失**：KT-ctrl-012（观测噪声 R vs 过程噪声 Q，无置信度/协方差）。

**强弱项**：🟢 中强——Condenser + task_tracker + 项目/用户 Agent 定义提供状态保真与跨会话配置记忆。⚠️**弱**——**记忆无置信度（P 协方差）**，P/R 环无法区分确信与猜测。

---

## 5. P 环 — 规划/分层控制（(P 环) planning 预设 + task/delegate 多级委派）

**承担角色**：以「planning Agent 预设 + task/delegate 多级子 Agent 委派 + workflow 编排」实现慢规划器与快执行器的分层控制。

**关键机制**：
- **planning Agent 预设**：`preset/planning.py` 定义 `PLAN_STRUCTURE`（OBJECTIVE / CONTEXT SUMMARY / APPROACH OVERVIEW 等固定章节），慢规划器产出结构化计划（源码级）。
- **task 工具（阻塞式委派）**：`tools/task/impl.py` 的 `TaskExecutor` 把 TaskAction 转为阻塞式子 Agent 执行，返回 TaskObservation——多层递阶控制（源码级）。
- **delegate 工具（委托可视化）**：`tools/delegate/` 提供 `DelegateAction` / `DelegateExecutor` / `DelegationVisualizer`，子 Agent 委派可观测（源码级）。
- **workflow 工具**：`tools/workflow/`（definition/impl）以脚本/定义驱动 Agent 序列，实现 options 式时序抽象（源码级）。
- **子 Agent 预设**：`preset/subagents/{default,code_explorer,web_researcher,bash_runner}.md` 提供开箱角色，父层选预设=选 options（源码级）。
- **task_tracker 里程碑**：跟踪任务/子任务进展，支撑滚动推进（源码级）。

**控制论映射**：KT-ctrl-041（分层控制结构）+ KT-ctrl-045（规划-执行解耦）+ KT-ctrl-042（多层递阶控制，父 Agent 经 task/delegate 协调子 Agent）+ KT-ctrl-046（options/SMDP，子 Agent 预设=能力原语）+ KT-ctrl-044（MPC 滚动时域，planning 预设滚动）。

**强弱项**：⭐**强**——planning 预设 + task/delegate 多级委派 + 子 Agent 预设 + workflow，分层规划能力完整且开箱可用。⚠️**弱**——父层对子 Agent 的持续约束注入/协调变量 λ 更新循环有限；规划时域 N 未显式参数化。

---

## 6. R 环 — 反思/反馈闭环（(R 环) 委派回灌 + Condenser 纠偏 + 自动化重试）

**承担角色**：由「子 Agent 委派回灌 + Condenser 上下文纠偏 + 工具错误回灌 + 自动化重试」承担，是**工程化反馈环**，无独立 Reflexion 元认知模块（但 planning 预设与顾问工具提供弱反思）。

**关键机制**：
- **委派结果回灌**：`TaskObservation` / `DelegateObservation` 把子 Agent 结果回灌父会话，驱动下一步（源码级）。
- **Condenser 纠偏**：上下文压缩时保留关键状态，抑制信息漂移（源码级）。
- **工具错误回灌**：工具执行失败以 Observation 形式回到 Agent，下一轮修正（源码级）。
- **自动化重试**：automations 可按事件重跑，失败任务可再触发（源码级）。
- **ask_oracle / tom_consult**：调用外部顾问做判断，提供弱反思信号（源码级）。

**控制论映射**：KT-ctrl-002（负反馈闭环结构）+ KT-ctrl-021（P 即时纠偏）+ KT-ctrl-023（D 预测性，Condenser 抑制漂移）+ KT-ctrl-025（稳态误差/超调，靠 TaskOutcome 验收）。

**强弱项**：🟡 中——委派回灌 + 错误回灌 + Condenser 纠偏 + 自动化重试形成反馈链。⚠️**弱**——**无独立自反思/self-critique 循环**；R 环偏外部工具错误与子 Agent 回报，属半开环。

---

## 精装房画像总结

**整体范式**：**自研 SDK 驱动的自托管编码 Agent 控制中心——丰富工具执行器 + Docker 沙箱 + 多级子 Agent 委派 + 多后端/自动化，开箱即用的 Agent 工厂**。

**最突出的环**：**T 环（19 类工具 + Docker 沙箱 + 多 Agent 后端）与 P 环（planning 预设 + task/delegate 多级委派 + 子 Agent 预设）**——执行器丰富度与分层委派是精装度 4.2 的两大支柱。

**最薄弱的环**：**E 环（评估/传感器）**——统一 Observation + TaskOutcome 已较结构化，但缺每步强制的独立 Critic；评估质量仍受限于 Agent 自报。

**精装房结论**：OpenHands 是「**一手高精装房（4.2），源码级铁证齐全**」——`package.json`（`@openhands/agent-canvas` v1.16.0，bin 一键）+ `software-agent-sdk` 4 自研 workspace 包 + 19 类工具 + 子 Agent 预设 4 角色 + Docker 沙箱 + 依赖安全护栏（`exclude-newer=7days` + 多条 CVE 约束）。它给架构师的启示是：**「成品化」的硬指标是「一键可跑 + 预装工具/沙箱/多 Agent + 自研底层包」，OpenHands 四项全中**；短板在评估（E）独立性与沙箱默认关闭（Option 1 无沙箱需用户主动选 Docker）。

---

### 📚 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S4 | 源码分析 — `package.json` `@openhands/agent-canvas` v1.16.0（bin 一键） | package.json（All-Hands-AI/OpenHands） | 高 |
| SRC-002 | S4 | 源码分析 — `software-agent-sdk` 4 自研 workspace 包 | software-agent-sdk（All-Hands-AI/OpenHands） | 高 |
| SRC-003 | S4 | 源码分析 — 子 Agent 预设 `openhands.tools.preset.subagents` + 技能市场 + Docker 沙箱 | 源码仓库（All-Hands-AI/OpenHands） | 高 |
