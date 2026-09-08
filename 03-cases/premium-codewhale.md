# CodeWhale — 精装房控制论画像

> 定位：自研 Rust 内核的终端 / IDE Agent 运行时（以「Claude Code 平替」为卖点）　｜　厂商：Hmbown　｜　分类：二次封装(实为自研)　｜　审计日期：2026-09-08
> 精装度：4/5　｜　一手/二手：一手(自研 Rust 底层)　｜　证据强度：源码级

## 0. 精装度评估（Premium Score）

**综合评分**：4/5 — 自研 20 个 crate 的 Rust 底层 + FLEET 多 Agent 团队 + MCP/hooks/execpolicy/workflow 预装齐全，属"高度自研的成品化运行时"；扣分在于缺独立 Critic 与完整沙箱隔离，评估环受限。

**预装能力清单**：
| 维度 | 预装情况 | 依据 |
|------|---------|------|
| 多Agent编排 | ✅ | FLEET agent 团队；`crates/agent` + `crates/workflow`（源码级） |
| Skill库 | 部分 | README「Connect MCP servers and skills, configure hooks」——skills 以接入为主（源码级） |
| 工作流编排 | ✅ | 自研 `crates/workflow`（源码级） |
| 模型接入 | ✅ | 多 provider 切换（源码级，`crates/config`） |
| 一键部署 | 部分 | `Cargo.toml` 原生构建安装，非托管云一键（源码级） |
| 沙箱/隔离 | 部分 | `crates/execpolicy` 审批阀门，非完整 VM 沙箱（源码级） |
| MCP生态 | ✅ | 自研 `crates/mcp`（源码级） |
| 记忆 | 部分 | 会话级状态，未见跨会话长期记忆内核（源码级） |

**声称 vs 实际**：官方以「Claude Code 平替 / 替代」营销 → **源码级证实为独立自研 Rust 底层**（`Cargo.toml` 列出 20 个自研 crate，含 `crates/{agent,tools,mcp,hooks,execpolicy,config,tui,workflow}`），并非封装 Claude Code。实证结论：**"平替"标签低估了它，实为自研（比声称更原创）**（源码级）。

---

## 1. 设定值（Setpoint）——用户意图 → FLEET 团队目标分解

**承担角色**：由「`crates/config` 装配的 provider/hooks 约束 + `crates/workflow` 工作流定义 + FLEET 多 Agent 角色分派」共同承担，把用户意图转化为带角色与流程边界的目标序列。

**关键机制**：
- **FLEET 团队角色分派**：`crates/agent` 提供 agent 团队（FLEET）抽象，把单一意图拆给多个带角色的 agent，设定值即"团队任务 + 各角色职责"（源码级）。
- **workflow 工作流即目标模板**：`crates/workflow` 把任务固化为可复用的流程定义，设定值 = 流程节点序列，降低每轮从零描述目标的成本（源码级）。
- **hooks 作为目标前置约束**：README 明确「configure hooks」，在动作前注入规则/校验，使设定值带硬边界（源码级）。
- **config 多 provider 装配**：`crates/config` 统一装配模型 provider 与运行参数，设定值中的"用哪个模型/什么预算"在此固化（源码级）。

**控制论映射**：KT-ctrl-045（规划-执行解耦，意图→流程→执行）/ KT-ctrl-041（分层控制结构，团队角色分层）。

**强弱项**：**强**——workflow 模板 + FLEET 角色使目标结构化、可复用；**弱**——设定值仍以配置/流程文本承载，缺结构化定量目标函数与强制验收门控。

---

## 2. E 环 — 评估/传感器（hooks 事件 + 审批门控）

**承担角色**：由「`crates/hooks` 事件钩子 + `crates/execpolicy` 审批结果 + 工具退出码/错误流」承担。**无独立 Critic 模型**，评估信号偏"规则型/事件型"，信噪比中等。

**关键机制**：
- **hooks 事件传感器**：`crates/hooks` 在关键生命周期点触发钩子，产出结构化事件供外部校验/统计——这是最可编程的 E 信号（源码级）。
- **execpolicy 审批结果作为门控信号**：`crates/execpolicy` 对动作做放行/拦截判定，其结果本身是"该动作是否合规"的评估信号（源码级）。
- **工具退出码/错误流**：`crates/tools` 返回的错误与退出码直接回灌模型，构成 raw 观测（源码级）。
- **MCP 工具返回**：`crates/mcp` 接入的外部工具返回作为环境观测（源码级）。

**控制论映射**：KT-ctrl-012（观测噪声 R，信号可信度决定是否放大）/ KT-ctrl-001（开环 vs 闭环，E 环是闭环开关）。

**强弱项**：🔴 **相对最弱环**——hooks/execpolicy 是规则型传感器，只能测"是否合规/是否报错"，**无法测"语义是否达标"**；缺独立 Critic/verifier，反馈信号质量依赖用户与外部工具。

---

## 3. T 环 — 执行器/工具（tools + execpolicy 审批阀门）

**承担角色**：由「`crates/tools` 工具执行 + `crates/mcp` 外部工具桥接 + `crates/execpolicy` 审批阀门 + hooks 拦截」承担，是**强安全门控的执行器**。

**关键机制**：
- **execpolicy 审批阀门（看门狗式硬门控）**：`crates/execpolicy` 对执行动作做策略审批，越权/高危动作被拦截或需批准——执行器硬约束（源码级）。
- **tools 统一执行层**：`crates/tools` 收敛工具调用入口，便于统一限幅与错误处理（源码级）。
- **mcp 外部工具桥接**：`crates/mcp` 把 MCP server 工具纳入同一执行器，扩展动作空间（源码级）。
- **hooks 动作前后拦截**：`crates/hooks` 在动作前后插入校验/记录，形成"执行—检查"闭环的 T 侧（源码级）。
- **多 provider 降级**：`crates/config` 支持 provider 切换，主通道失败可换道，属外部扰动鲁棒补偿（源码级）。

**控制论映射**：KT-ctrl-034（安全边际/硬约束限幅+看门狗，execpolicy 审批）/ KT-ctrl-033（冗余与仲裁，多 provider 切换）。

**强弱项**：🟢 **强**——execpolicy 审批阀门 + hooks 拦截 + tools 统一入口构成多层执行安全；**弱**——容错以策略规则为主，工具失败时缺模型级自适应重试，且无完整沙箱隔离。

---

## 4. M 环 — 记忆/状态估计（会话状态 + workflow 上下文）

**承担角色**：由「`crates/config` 运行配置 + 会话状态 + `crates/workflow` 流程上下文」承担，维护"当前在哪个流程节点、团队处于何状态"，但**未见跨会话长期记忆内核**。

**关键机制**：
- **workflow 上下文作为状态骨架**：`crates/workflow` 记录流程执行位置，等价于"我现在在流程的哪一步"的状态估计（源码级）。
- **FLEET 团队状态**：`crates/agent` 维护各 agent 的任务/产出状态，构成多主体状态视图（源码级）。
- **config 运行态快照**：`crates/config` 固化 provider/参数，使状态可复现（源码级）。
- **hooks 事件留痕**：`crates/hooks` 记录事件序列，供状态回溯（源码级）。

**控制论映射**：KT-ctrl-011（卡尔曼滤波预测-更新，流程推进为预测、事件为更新）/ KT-ctrl-014（信息滤波/降维，workflow 只保留增量节点状态）。

**强弱项**：🟢 中强——流程/团队状态结构化；**弱**——**无跨会话长期记忆**，会话结束状态即消散，反思产物需外部机制升级。

---

## 5. P 环 — 规划/分层控制（FLEET + workflow 编排）

**承担角色**：由「FLEET 多 Agent 团队 + `crates/workflow` 工作流编排 + `crates/agent` 角色分工」承担，是**典型的多主体分层编排**。

**关键机制**：
- **FLEET 团队分层**：`crates/agent` 的 FLEET 把任务分给多个角色 agent，上层协调、下层执行，构成递阶控制（源码级）。
- **workflow 慢速编排**：`crates/workflow` 定义节点序列，作为"慢规划器"给出里程碑（源码级）。
- **agent 快速执行**：单个 agent 在节点内快速调用工具落地（源码级）。
- **hooks 协调约束**：`crates/hooks` 在节点切换处注入协调规则（源码级）。

**控制论映射**：KT-ctrl-041（分层控制/时标分层）/ KT-ctrl-045（规划-执行解耦）/ KT-ctrl-046（options/SMDP，角色即能力原语）。

**强弱项**：🟢 强——FLEET + workflow 提供显式多 Agent 分层编排，是精装度 4 的核心支撑；**弱**——编排为流程定义式，缺 MPC 式滚动重规划（执行中自动回上层重算）。

---

## 6. R 环 — 反思/反馈闭环（hooks 反馈 + 审批否决）

**承担角色**：由「hooks 反馈事件 + execpolicy 否决 + 工具错误回灌 + 多 provider 重试」承担，是**规则型反馈环**：能拦截与回灌，但无 Reflexion 式元认知自我反思。

**关键机制**：
- **错误回灌**：`crates/tools` 工具错误直接回到模型上下文，下一轮据此修正（源码级）。
- **execpolicy 否决即负反馈**：审批不通过阻断动作，等价于 e = 目标 − 现状 的即时校正（源码级）。
- **hooks 反馈事件**：`crates/hooks` 在动作后触发校验/通知，形成外置反馈通道（源码级）。
- **provider 重试/切换（D 侧抑制）**：失败通道退避/切换，抑制持续失败趋势（源码级）。

**控制论映射**：KT-ctrl-002（负反馈闭环）/ KT-ctrl-021（P 即时纠偏，审批否决）/ KT-ctrl-023（D 预测性，失败趋势提前换道）。

**强弱项**：🟡 中——有错误回灌 + 规则拦截 + 重试；**弱**——**无模型自我反思循环**（"上轮我哪里错了"），R 环依赖 hooks 外置与人工，属半开环。

---

## 精装房画像总结

**整体范式**：**自研内核 + 多 Agent 流程编排 + 强审批门控的"前馈-执行 + 规则反馈"结构**。

**最突出的环**：**T 环（execpolicy 审批阀门 + hooks 拦截 + tools 统一执行）与 P 环（FLEET + workflow 多 Agent 编排）**——执行安全与团队编排是精装度 4 的两大支柱。

**最薄弱的环**：**E 环（评估/传感器）**——hooks/execpolicy 只能测"合规/报错"，缺独立 Critic 测"做对没"，R 环随之偏弱。

**精装房结论**：CodeWhale 是"**被'平替'标签低估的一手精装房**"——源码级证实其 20 个自研 Rust crate 与 FLEET/workflow/MCP/hooks/execpolicy 预装，属真·自研成品化运行时；精装度 4 的短板集中在评估（E）与长期记忆（M），而非底座原创性。它给架构师的启示是：**"XX 平替"的命名与真实一手程度无关，唯有源码依赖分析能鉴别**。

---

### 📚 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S4 | 源码分析 — `Cargo.toml` 20 个自研 crate | Cargo.toml（Hmbown/codewhale） | 高 |
| SRC-002 | S4 | 源码分析 — README「Connect MCP servers and skills, configure hooks」 | README.md（Hmbown/codewhale） | 高 |
| SRC-003 | S4 | 源码分析 — FLEET 多 Agent 团队 + workflow + execpolicy 审批阀门 | 源码仓库（Hmbown/codewhale） | 高 |
