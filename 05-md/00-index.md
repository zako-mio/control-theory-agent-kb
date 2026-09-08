# AI 索引 — 控制理论 ⊗ Agent 设计知识库 (00-index.md)

> **AI 友好镜像**，检索优先走本目录（`05-md/`）。人类可读版在 `04-interactive/` + `03-cases/`。
> 版本：v1.1.0（6 框架 + 14 精装房全景版）　创建：2026-09-07　v1.1 扩展：2026-09-08

## 知识库定位

以 **Agent 设计构建为业务核心**（业务需求驱动），控制理论作为解决 Agent 工程问题的**技术工具库**引入。价值主张＝**Agent 系统设计框架**：定义目标函数、状态模型、反馈律。

**定位一句话**：把 Agent 当作一架装了传感器、执行器、逻辑决断器的无人机去建模与控制。

## 五大核心环

| 环 | 控制理论对应 | Agent 工程问题 | 章节 |
|----|------------|--------------|------|
| **M 记忆/状态估计** | 状态估计/观测噪声/卡尔曼滤波 | 长上下文取舍、工作记忆蒸馏、观测噪声过滤 | `ch-memory` |
| **P 规划/分层控制** | 分层控制/慢-快双速控制器 | 任务分解、里程碑设定、慢规划器+快执行器 | `ch-planning` |
| **R 反思/反馈闭环** | 反馈闭环/误差收敛/积分环节 | 自我反思、错误回馈、长期偏航补偿 | `ch-reflection` |
| **T 工具调用/执行器** | 执行器/容错/鲁棒性 | 工具调用失败、冗余仲裁、看门狗限幅 | `ch-tool` |
| **E 评估/传感器** | 传感器/验证器/信噪比 | Critic 模块、验证器、反馈信号质量 | `ch-eval` |

> **闭环方向**：E 决定反馈信号质量 → R 决定纠偏量 → P/T 决定轨迹 → M 决定"我以为我在哪"。任一环失效，闭环即破。

## 控制理论证据包（01-theory/，31 知识点）

### 01-闭环反馈/稳定性（KT-ctrl-001~006）
| KT | 概念 |
|----|------|
| KT-ctrl-001 | 开环 vs 闭环控制 |
| KT-ctrl-002 | 负反馈闭环系统结构 |
| KT-ctrl-003 | 稳定性定义（BIBO/渐近/Lyapunov） |
| KT-ctrl-004 | 误差收敛与反馈校正律 |
| KT-ctrl-005 | 经典 LTI 稳定性判据 |
| KT-ctrl-006 | 反馈系统灵敏度与鲁棒性基础 |

### 02-状态估计/记忆（KT-ctrl-010~015）
| KT | 概念 |
|----|------|
| KT-ctrl-010 | 状态估计问题 |
| KT-ctrl-011 | 卡尔曼滤波（预测-更新） |
| KT-ctrl-012 | 观测噪声 R vs 过程噪声 Q |
| KT-ctrl-013 | 状态估计器与现代控制（分离性） |
| KT-ctrl-014 | 信息滤波/信息降维 |
| KT-ctrl-015 | 贝叶斯滤波/HMM |

### 03-PID/误差收敛（KT-ctrl-020~026）
| KT | 概念 |
|----|------|
| KT-ctrl-020 | PID 控制器结构（三环节） |
| KT-ctrl-021 | 比例控制 P（即时纠偏） |
| KT-ctrl-022 | 积分控制 I（累积补偿） |
| KT-ctrl-023 | 微分控制 D（预测性） |
| KT-ctrl-024 | PID 整定/Ziegler-Nichols |
| KT-ctrl-025 | 误差收敛/稳态误差/超调 |
| KT-ctrl-026 | 状态反馈 LQR |

### 04-鲁棒控制/不确定性（KT-ctrl-030~035）
| KT | 概念 |
|----|------|
| KT-ctrl-030 | 模型不确定性 |
| KT-ctrl-031 | 鲁棒稳定性 vs 标称稳定性 |
| KT-ctrl-032 | 鲁棒控制方法（H∞/μ/滑模） |
| KT-ctrl-033 | 冗余与仲裁（NMR/TMR） |
| KT-ctrl-034 | 安全边际/硬约束限幅（看门狗） |
| KT-ctrl-035 | 干扰抑制/扰动观测器（DOB） |

### 05-分层控制/慢快双速（KT-ctrl-041~046）
| KT | 概念 |
|----|------|
| KT-ctrl-041 | 分层控制结构（时标分层） |
| KT-ctrl-042 | 递阶/多层控制 |
| KT-ctrl-043 | 时间尺度分离 ε |
| KT-ctrl-044 | MPC 滚动时域优化 |
| KT-ctrl-045 | 规划-执行解耦 |
| KT-ctrl-046 | 分层 RL / options / SMDP |

## 五大核心环映射框架（02-framework/framework.md）

- **M 环**：Kalman 式记忆管理；信息增量预算（蒸馏即降维）
- **P 环**：MPC 式滚动规划；Options 式技能抽象（慢/快双速）
- **R 环**：PID 式反思调节；稳态带验收
- **T 环**：执行器硬限幅+看门狗；异质冗余+多数仲裁
- **E 环**：Critic 即传感器+低通滤波；DOB 式偏差补偿

## 产品控制论画像（03-cases/）

| 产品 | 类型 | 整体范式 | 最强环 | 最弱环 | 独立 Critic | 源码 |
|------|------|---------|-------|-------|:---:|:---:|
| **opencode** v1.18.29 | monorepo+装配层 | 前馈-执行+局部反馈（Plan-and-Execute） | P/T | E | ❌ | 本地 |
| **deepseek-harness** v0.1.1-rc.2 | cordis 插件 | MPC 滚动规划+强约束执行器 | T | E | ❌ | 本地 |
| **PRIME** (RLM) | RLM+Continual Harness | 自适应/自整定负反馈 | R | E | ❌(gates空) | clone |
| **hermes** | NousResearch | 鲁棒控制+多传感器+观测器型 | M/T | P | ✅ | clone |
| **claude-code** | anthropics | 外挂 Critic + 执行器限幅 | T | E | ⚠️外挂贴片 | clone |
| **codex** | openai (Rust) | 重执行器+硬安全阀+双评审器 | T/E | P | ✅双评审器 | clone |

## 核心横向洞察（6 框架对比，主 Agent 终裁）

1. **E 环（评估）从样板三产品「一致最弱」分化为两派**——hermes 有独立 Critic 体系（E 环反转强）、codex 有 Guardian+Review 双评审器（E 环强）；opencode/dsh/PRIME/claude-code 仍偏弱。**「E 环最弱」是早期产品的共性，非 Agent 普遍规律**。
2. **T 环（执行器）是 6 框架共同「最强环」**——看门狗/限幅/沙箱是 Agent 工程最成熟环节（无一例外）。
3. **各产品最弱环分化**——opencode/dsh/PRIME/claude-code = E，hermes/codex = P。
4. **M 环普遍缺置信度（P 协方差）**——记忆多记事实不记"我有多确定"（PRIME 带版本/hermes 带离散标记相对最好）。

## 精装房全景专题（v1.1，14 产品）

**核心命题**：声称 ≠ 实际。坐标系：精装度 0-5（主轴）× 一手/二手（标签）× 4 大类 × 五环定位。

| 产品 | 精装度 | 一手/二手 | 大类 | 证据级 | 画像 |
|------|:---:|:---:|------|:---:|------|
| OpenHands | 5 | 一手 | 开源成品化 | 源码级 | `03-cases/premium-openhands.md` |
| Devin | 5 | 一手 | 第一方成品 | 文档级 | `03-cases/premium-devin.md` |
| WorkBuddy | 5 | 一手 | 第一方成品 | 文档级 | `03-cases/premium-workbuddy.md` |
| Dify | 5 | 一手 | 低代码平台 | 源码级 | `03-cases/premium-dify.md` |
| OpenClaude | 5 | 一手 | 二次封装 | 源码级 | `03-cases/premium-openclaude.md` |
| Cursor | 4.5 | 一手 | 第一方成品 | 文档级 | `03-cases/premium-cursor.md` |
| Coze扣子 | 4.5 | 一手 | 低代码平台 | 文档级 | `03-cases/premium-coze.md` |
| Windsurf | 4 | 一手 | 第一方成品 | 文档级 | `03-cases/premium-windsurf.md` |
| GPT-Researcher | 4 | 一手 | 开源成品化 | 源码级 | `03-cases/premium-gptresearcher.md` |
| CodeWhale | 4 | 一手 | 二次封装 | 源码级 | `03-cases/premium-codewhale.md` |
| GitHub Copilot | 3.75 | 一手 | 第一方成品 | 文档级 | `03-cases/premium-copilot.md` |
| QCode | 3.5 | 二手 | 二次封装 | 文档级 | `03-cases/premium-qcode.md` |
| CrewAI | 3 | 一手 | 开源成品化 | 源码级 | `03-cases/premium-crewai.md`（证据见证据文件） |
| CC-Router | 3 | 二手 | 二次封装 | 源码级 | `03-cases/premium-ccrouter.md` |

**三大实证发现**：
1. **二手被高估**：CC-Router（源码级依赖 `@the-next-ai/ai-gateway`）、QCode（官价×倍率）
2. **一手被低估**：CodeWhale、OpenClaude（声称平替，实为自研底层）
3. **声称功能不存在**：Windsurf 无「Flows DAG」多Agent编排

**证据文件**：`07-checkpoint/premium-evidence.md`（实证证据）+ `07-checkpoint/premium-diff-analysis.md`（差量分析）

## 知识库文件清单

| 目录 | 内容 |
|------|------|
| `00-contract/contract.md` | 契约（命名/信源分级/破坏性范围/门控 + 精装房专题） |
| `01-theory/` | 5 分区理论证据包（31 知识点，≥2 权威源） |
| `02-framework/framework.md` | 五环映射框架 |
| `03-cases/` | 6 框架画像 + 14 精装房画像（premium-*.md） |
| `04-interactive/` | 人类端 36 页（总览/理论/案例/实验/精装房全景+DAG） |
| `06-experiments/` | 6 产品标准实验组记录 |
| `07-checkpoint/` | 中间产物/门控脚本 + 精装房实证证据 |
| `08-drawio/` | drawio 图表 |
| `09-src-data/` | DAG DATA/生成脚本（含 gen_premium_cyto.py） |

## 关联

- 契约：`00-contract/contract.md`
- 人类可读版入口：`04-interactive/index.html`
- 精装房全景入口：`04-interactive/premium-map.html`

## 人类可读页索引（04-interactive/，36 页）

| 分组 | 页面 | 说明 |
|------|------|------|
| 概览 | `index.html` / `index_cyto.html` | 文档总览 / 交互 DAG |
| 核心 | `framework.html` | 五环映射框架 |
| 理论 | `theory-closed-loop.html` / `theory-state-est.html` / `theory-pid.html` / `theory-robust.html` / `theory-hierarchical.html` | 5 分区理论页 |
| 案例 | `case-opencode.html` / `case-dsh.html` / `case-prime.html` / `case-hermes.html` / `case-claude-code.html` / `case-codex.html` | 6 框架画像 |
| 实验 | `exp-opencode.html` / `exp-dsh.html` / `exp-prime.html` / `exp-hermes.html` / `exp-claude-code.html` / `exp-codex.html` | 6 实验组记录 |
| 精装房 | `premium-map.html` / `premium-cyto.html` + 14 个 `premium-{product}.html` | 全景/ DAG / 案例页 |
