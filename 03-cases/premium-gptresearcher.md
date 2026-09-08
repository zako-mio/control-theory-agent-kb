# GPT Researcher (assafelovic) — 精装房控制论画像

> 定位：开源深度研究 Agent（Web UI + 8-agent 编排 + 多格式报告生成 + 引用溯源）　｜　厂商：assafelovic　｜　分类：开源成品化　｜　审计日期：2026-09-08
> 精装度：4/5　｜　一手/二手：一手（编排自研，LangChain/LangGraph 底座）　｜　证据强度：源码级

## 0. 精装度评估（Premium Score）

**综合评分**：4/5 — 开源自研的深度研究成品，预装 Web UI（NextJS + FastAPI）+ Docker/Colab 一键 + MD/PDF/docx 多格式报告 + 8-agent 编排（LangGraph）+ 检索工具，开箱可跑端到端研究任务；扣分项在**通用性受限**（聚焦研究场景）、沙箱/隔离弱、编排依赖 LangGraph 底座。

**预装能力清单**：
| 维度 | 预装情况 | 依据 |
|------|---------|------|
| 多Agent编排 | ✅ | `multi_agents/` 8-agent 团队（Human/Chief Editor/Researcher/Editor/Reviewer/Revisor/Writer/Publisher），`multi_agents/agents/editor.py`（源码级） |
| Skill库 | 部分 | `skills/gpt-researcher/SKILL.md`（Codex/Claude Skill）+ 检索/爬取工具集，非独立工具市场（源码级） |
| 工作流编排 | ✅ | LangGraph `StateGraph` 编排（`multi_agents/agents/editor.py`）+ 主 Agent planner-executor 架构（源码级） |
| 模型接入 | ✅ | `config/variables/default.py` 多 LLM 配置（FAST/SMART/STRATEGIC_LLM）+ 多 provider（源码级） |
| 一键部署 | ✅ | `Dockerfile` / `docker-compose.yml` / Colab notebook / `pip install gpt-researcher`（源码级） |
| 沙箱/隔离 | ✖️ | 未见 per-session 沙箱；爬取/执行在宿主环境（源码级） |
| MCP生态 | ✅ | `mcp-server/` + `pyproject.toml` 依赖 `mcp` / `langchain-mcp-adapters`（源码级） |
| 记忆 | 部分 | `gpt_researcher/memory/` + `multi_agents/memory/draft.py`（DraftState）；无显式置信度（源码级） |

**声称 vs 实际**：官方声称「the first open deep research agent designed for both web and local research」 → **源码级证实为自研编排 + 成品化**：`pyproject.toml`（name=`gpt-researcher` v0.15.1）依赖 `langchain` / `langgraph` 作**底座**，但 8-agent 编排与 `multi_agents/` 团队、`gpt_researcher/actions/`（8 个动作模块）、`backend/server/app.py`（16KB FastAPI）、`frontend/nextjs`（`gpt-researcher-ui` v0.1.74）均为自研。与 `premium-evidence.md` 一致：**一手（编排）+ 精装度 4 + 源码级**。**注意**：编排底座为 LangGraph（非完全自研引擎），这是它与 Dify（自研 graphon）的差异。

---

## 1. 设定值（Setpoint）——研究任务配置把意图固化为可执行研究计划

**承担角色**：以「`task.json` 研究任务配置 + 主 Agent planner 分解」把用户意图固化为一份可执行、可约束的研究任务，作为设定值 r。

**关键机制**：
- **`task.json` 任务配置**：`query` / `model` / `max_sections` / `publish_formats` / `guidelines` / `follow_guidelines` 等字段定义研究目标与约束（`multi_agents/README.md`，源码级）。
- **guidelines 硬约束**：用户可指定报告必须遵守的准则（如 APA 格式、语言），构成设定值的显式规格（源码级）。
- **主 Agent planner-executor 架构**：README 明示「utilize 'planner' and 'execution' agents」，planner 生成研究问题、executor 收集信息（源码级）。
- **Editor 规划大纲**：`multi_agents/agents/editor.py` 的 `EditorAgent` 规划报告大纲与结构（源码级）。
- **max_plan_revisions 上限**：`max_plan_revisions` 限定人工计划修订次数，防无限循环（源码级）。

**控制论映射**：KT-ctrl-045（规划-执行解耦，task.json+大纲=可评审契约）+ KT-ctrl-041（分层控制结构，Chief Editor 顶层/子 Agent 下层）+ KT-ctrl-002（负反馈闭环结构，目标=设定值 r）。

**强弱项**：⭐**强**——设定值有结构化配置（query/guidelines/格式）、规划阶段明确、修订次数有上限。⚠️**弱**——设定值成功判据仍以报告文本承载，缺机器可验证的量化目标函数。

---

## 2. E 环 — 评估/传感器（(E 环) Reviewer Agent + 检索命中 + 引用校验）

**承担角色**：为闭环生产「研究是否达标」的反馈信号，核心是 **Reviewer Agent**（独立评审器）+ 检索相关性 + 引用溯源，是本产品相对突出的评估环。

**关键机制**：
- **Reviewer Agent 独立评审器**：`multi_agents/` 8-agent 团队中的 Reviewer「Validates the correctness of the research results given a set of criteria and provides feedback」（`multi_agents/README.md`，源码级）——这是**独立于执行者的 Critic 传感器**。
- **Revisor Agent 修订**：Reviewer 反馈后由 Revisor 修订直至满意，形成「评审→修订」闭环（源码级）。
- **DraftState 评审状态**：`multi_agents/memory/draft.py` 的 `DraftState` + `draft_review.py` 的 `DEFAULT_MAX_DRAFT_REVISIONS` / `MaxDraftRevisionsExceededError`——评审有状态、有次数上限（源码级）。
- **检索相关性**：`gpt_researcher/retrievers/` 多检索器（默认 `tavily`，`config/variables/default.py`）按相关性召回，构成信息质量信号（源码级）。
- **引用溯源**：报告带 citations，README 明示「produces detailed, factual, and unbiased research reports with citations」——可验证性作为质量信号（源码级）。

**控制论映射**：KT-ctrl-006（反馈灵敏度/鲁棒性基础，Reviewer 独立校验降低对单模型的敏感）+ KT-ctrl-035（扰动观测器 DOB，Reviewer 在线研判草稿质量）+ KT-ctrl-012（观测噪声 R，检索/评审信号可信度）+ KT-ctrl-001（开环 vs 闭环）。

**强弱项**：🟢 **强**（相对同类）——**有独立 Reviewer Agent + Revisor 修订闭环 + 评审次数上限**，是本产品 E 环的亮点，也是精装度 4 中「评估」维度少见的独立性。⚠️**弱**——Reviewer 与执行者用同一 SMART_LLM（README「only the SMART_LLM is used」），存在共模偏置；评审标准靠提示词承载，非结构化硬校验。

---

## 3. T 环 — 执行器/工具（(T 环) 检索器 + 爬取器 + 报告生成器）

**承担角色**：把研究动作以「多检索器 + 网页爬取 + 报告生成/发布」落地，是直接接触外部信息源与产出格式的执行器。

**关键机制**：
- **多检索器**：`gpt_researcher/retrievers/` 支持 Tavily/Google/DuckDuckGo 等多种检索器（`RETRIEVER` 可配），执行动作可换道（源码级）。
- **网页爬取**：`gpt_researcher/scraper/` + `config/variables/default.py` 的 `SCRAPER` / `MAX_SCRAPER_WORKERS=15` / `SCRAPER_RATE_LIMIT_DELAY`——并发与限速限幅（源码级）。
- **报告生成器**：`gpt_researcher/actions/report_generation.py` + `markdown_processing.py` 生成 MD/PDF/docx 多格式（源码级）。
- **Publisher Agent**：`multi_agents/` 的 Publisher「publishes the final report in various formats such as PDF, Docx, Markdown」（源码级）。
- **MCP 工具接入**：`mcp-server/` + `langchain-mcp-adapters` 把外部 MCP 工具纳入执行器（源码级）。
- **FastAPI 后端**：`backend/server/app.py`（16KB）提供执行 API 出口（源码级）。

**控制论映射**：KT-ctrl-034（安全边际/硬约束限幅，爬取并发/限速/令牌上限）+ KT-ctrl-033（冗余与仲裁，多检索器可切换）+ KT-ctrl-030（模型不确定性，检索失败需降级）。

**强弱项**：🟢 **强**——多检索器 + 爬取限幅 + 多格式报告 + MCP 工具，执行器聚焦研究场景且开箱可用。⚠️**弱**——**无沙箱/隔离**（爬取在宿主环境），执行器安全性弱于 OpenHands；工具集为研究专用，通用性受限。

---

## 4. M 环 — 记忆/状态估计（(M 环) DraftState + 上下文压缩 + 向量检索）

**承担角色**：以「DraftState 草稿状态 + 上下文管理 + 向量检索」维护「研究进行到哪、已收集哪些证据」，**未显式建模置信度**。

**关键机制**：
- **DraftState 草稿状态**：`multi_agents/memory/draft.py` 维护草稿与研究进度，是结构化的中间状态（源码级）。
- **记忆后端**：`gpt_researcher/memory/` + `config/variables/default.py` 的 `MEMORY_BACKEND="local"`（源码级）。
- **上下文压缩**：`SUMMARY_TOKEN_LIMIT=700` 等 token 上限 + 上下文管理，按预算压缩信息（源码级）。
- **向量检索记忆**：`gpt_researcher/vector_store/` 存检索嵌入，构成外部可检索记忆（源码级）。
- **多 Agent 隔离上下文**：`deep_agents/` 示例「delegates sections to researcher subagents with isolated context, offloads drafts to a filesystem」——子 Agent 上下文隔离（源码级）。

**控制论映射**：KT-ctrl-010（状态估计，DraftState+向量库折叠出研究状态）+ KT-ctrl-011（Kalman 预测-更新，研究推进=预测、检索结果=更新）+ KT-ctrl-014（信息滤波/降维，token 上限 + 子 Agent 隔离）。**缺失**：KT-ctrl-012（观测噪声 R vs 过程噪声 Q，无置信度/协方差）。

**强弱项**：🟢 中强——DraftState + 向量检索 + 子 Agent 上下文隔离提供状态保真。⚠️**弱**——**记忆无置信度（P 协方差）**；DraftState 侧重草稿文本，非概率信念状态。

---

## 5. P 环 — 规划/分层控制（(P 环) planner-executor + Editor 大纲 + LangGraph 编排）

**承担角色**：以「planner-executor 架构 + Editor 大纲 + LangGraph StateGraph + 8-agent 团队」实现慢规划器与快执行器的分层控制，是本产品最突出的环之一。

**关键机制**：
- **planner-executor 双 Agent**：README 明示「utilize 'planner' and 'execution' agents. The planner generates research questions, while the execution agents gather relevant information」（源码级）。
- **Editor 大纲规划**：`EditorAgent` 规划报告大纲与结构，每个大纲主题并行派发子研究（`multi_agents/README.md` Steps，源码级）。
- **LangGraph StateGraph 编排**：`multi_agents/agents/editor.py` 用 `StateGraph` / `END` 定义有状态多 Agent 流程，含条件路由 `route_draft_review`（源码级）。
- **8-agent 分工**：Chief Editor 协调 + Researcher/Editor/Reviewer/Revisor/Writer/Publisher 分工，构成多层递阶控制（源码级）。
- **并行子研究**：「For each outline topic (in parallel): Researcher → Reviewer → Revisor」——并行 + 迭代（源码级）。
- **max_sections 时域限制**：`max_sections` 限定章节数，等价于规划时域 N（源码级）。

**控制论映射**：KT-ctrl-041（分层控制结构）+ KT-ctrl-045（规划-执行解耦）+ KT-ctrl-044（MPC 滚动时域，Reviewer→Revisor 迭代）+ KT-ctrl-042（多层递阶控制，Chief Editor 协调）+ KT-ctrl-046（options/SMDP，子 Agent 角色=能力原语）。

**强弱项**：⭐⭐**最突出**——planner-executor + Editor 大纲 + LangGraph 编排 + 8-agent 分工 + 并行子研究，分层规划与角色化编排是精装度 4 的核心支撑。⚠️**弱**——编排底座为 **LangGraph**（非完全自研引擎，依赖外部库）；规划时域 N 由 `max_sections` 固定，无图级滚动重规划。

---

## 6. R 环 — 反思/反馈闭环（(R 环) Reviewer-Revisor 迭代 + 人工反馈 + 错误重试）

**承担角色**：由「Reviewer→Revisor 修订迭代 + 人工反馈 + 错误重试」承担，是本产品**最成熟的环之一**——有显式的评审-修订闭环。

**关键机制**：
- **Reviewer→Revisor 闭环**：Reviewer 校验草稿给反馈，Revisor 据此修订直至满意（`multi_agents/README.md`，源码级）——显式负反馈校正。
- **修订次数上限**：`DEFAULT_MAX_DRAFT_REVISIONS` / `MaxDraftRevisionsExceededError`——防反思无限循环（anti-windup）（源码级）。
- **人工反馈回路**：`include_human_feedback` 开启后用户可给 Agent 反馈，`max_plan_revisions` 限定修订次数（源码级）。
- **错误重试**：`pyproject.toml` 依赖 `backoff`（指数退避重试），检索/请求失败可重试（源码级）。
- **guidelines 合规迭代**：`follow_guidelines` 让报告按准则迭代直至合规（源码级）。

**控制论映射**：KT-ctrl-002（负反馈闭环结构，Reviewer 反馈→Revisor 修订）+ KT-ctrl-004（误差收敛与反馈校正律，迭代修订使草稿收敛）+ KT-ctrl-021（P 即时纠偏）+ KT-ctrl-022（I 累积补偿，guidelines 持续合规）+ KT-ctrl-025（稳态误差/超调，修订次数上限防超调）。

**强弱项**：⭐**强**——**Reviewer→Revisor 显式评审-修订闭环 + 修订上限 + 人工反馈 + 重试**，R 环在同类产品中较成熟（与 E 环呼应）。⚠️**弱**——反思标准靠提示词与准则文本，非结构化量化；Reviewer 与执行者同模型，共模偏置无法排除。

---

## 精装房画像总结

**整体范式**：**LangGraph 底座上的 8-agent 研究流水线——planner-executor 分层编排 + Reviewer-Revisor 评审闭环 + 多格式报告，开箱即用的深度研究工厂**。

**最突出的环**：**P 环（planner-executor + Editor 大纲 + LangGraph 8-agent 编排）与 R 环（Reviewer→Revisor 评审-修订闭环）**——分层编排与显式评审闭环是精装度 4 的两大支柱，也是相对同类的差异点。

**最薄弱的环**：**T 环（执行器/沙箱）**——无 per-session 沙箱，爬取在宿主环境；工具集为研究专用，通用性受限。（注：E 环有独立 Reviewer，是难得的强项。）

**精装房结论**：GPT Researcher 是「**一手（编排自研）、精装度 4、源码级证实的深度研究成品**」——`multi_agents/` 8-agent 团队 + LangGraph `StateGraph` 编排 + `backend/server/app.py` FastAPI + `frontend/nextjs` v0.1.74 Web UI + 多格式报告 + MCP 工具；**其编排底座为 LangGraph（非完全自研引擎）**，这是它与 Dify（自研 graphon）的关键差异，也是它精装度停在 4 而非 5 的原因之一（另有沙箱缺失）。它给架构师的启示是：**「评审-修订闭环」是 E/R 环可复用的优秀范式——独立 Reviewer + 修订上限，比多数产品的「错误重试」更接近真正的误差收敛控制**。

---

### 📚 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S4 | 源码分析 — `multi_agents/` 8-agent 团队（LangGraph 编排） | multi_agents/（assafelovic/gpt-researcher） | 高 |
| SRC-002 | S4 | 源码分析 — `backend/server/app.py` FastAPI | backend/server/app.py（assafelovic/gpt-researcher） | 高 |
| SRC-003 | S4 | 源码分析 — `frontend/nextjs` v0.1.74 Web UI + MD/PDF/docx 报告 | frontend/nextjs（assafelovic/gpt-researcher） | 高 |
