# 精装房实证证据汇总（v1.1 专题）

> 审计日期：2026-09-08　证据来源：开源源码级（raw.githubusercontent.com）+ 闭源文档级（官方站/docs.devin.ai）
> 核心命题：**声称 ≠ 实际**——源码/文档实证鉴别一手/二手、真实精装度。

---

## 一、证据强度分级说明

| 级别 | 定义 | 代表 |
|------|------|------|
| 源码级 | 直接分析源码（依赖/入口/是否包壳/预装能力） | OpenHands/gpt-researcher/CrewAI/Dify/CodeWhale/CCR/OpenClaude |
| 文档级 | 官方文档/公开架构说明 | Cursor/Windsurf/Devin/Copilot/WorkBuddy/Coze/QCode |
| 行为级 | 实际运行黑箱观察 | （本次未做，见「待实证」） |
| 声称级 | 仅官方营销宣称，未实证 | （部分产品营销页引用） |

---

## 二、各产品精装度实证结果

### A. 开源成品化组（源码级）

| 产品 | 一手/二手 | 精装度 | 关键预装 | 关键证据 |
|------|:---:|:---:|---------|---------|
| **OpenHands** | 一手 | 5 | Agent Canvas UI + 沙箱 + 子Agent预设(openhands.tools.preset.subagents) + 技能市场 + 自动化仓库 | package.json bin=agent-canvas 一键；software-agent-sdk 4自研包 |
| **gpt-researcher** | 一手(编排) | 4 | Web UI(NextJS+FastAPI) + Docker/Colab一键 + MD/PDF/docx报告 + 8-agent编排(LangGraph) + 检索工具 | multi_agents 8-agent团队；frontend/nextjs v0.1.74 |
| **CrewAI** | 一手 | 3 | 角色编排原语(Crew/Agent/Task/Flows) + crewai-tools 20+工具extras + JSON-first脚手架 + 官方skills仓库 | pyproject 自研crewai-workspace；crewai create crew 脚手架 |
| **Dify** | 一手 | 5 | 可视化画布(reactflow) + 自研graphon编排引擎 + RAG pipeline(133路径) + 插件市场 + 1000+模型 + docker一键 | api/pyproject 无langchain/graphon自研；api/core/rag 133路径 |

### B. 二次封装/发行版组（源码级）

| 产品 | 一手/二手 | 精装度 | 关键预装 | 关键证据 |
|------|:---:|:---:|---------|---------|
| **CodeWhale** | 一手(自研Rust) | 4 | agent团队(FLEET) + MCP + hooks + 审批阀门(execpolicy) + 多provider切换 + TUI/VS Code扩展 + workflow | Cargo.toml 20个自研crate；README'Connect MCP servers and skills, configure hooks' |
| **Claude Code Router** | **二手** | 3 | 多provider预设路由(Kimi等) + 故障转移/密钥轮换 + 仪表盘 + Fusion视觉/web/MCP/ToolHub | packages/core 依赖@the-next-ai/ai-gateway(二手网关底座) |
| **OpenClaude** | 一手 | 5 | 200+模型开箱接入(多provider预设) + agents/tasks + MCP + slash命令 + 文件/web工具 + 引导式provider | package v0.30.0 @gitlawb/openclaude；README'One CLI across cloud APIs and local backends' |

### C. 闭源商用组（文档级）

| 产品 | 一手/二手 | 精装度 | 关键预装 | 关键证据 |
|------|:---:|:---:|---------|---------|
| **Cursor** | 一手 | 4.5 | Cloud Agents并行 + Composer规划 + Rule工程(MCP/skills/automations) + MCP生态 + 语义索引 + 隔离VM | cursor.com/docs 官方文档 |
| **Windsurf/Devin Desktop** | 一手 | 4 | Cascade agent(Code/Chat/规划/checkpoint回滚) + RAG上下文索引 + MCP marketplace + SKILL.md + Workflows/Rules/Memories + Agent Command Center | docs.devin.ai；**无Flows DAG**(多Agent并发=Arena+worktrees+Managed Devins) |
| **Devin** | 一手 | 5 | 每session独立VM沙箱(桌面+浏览器+Computer Use) + 自主规划 + Browser/VCS双向 + Managed Devins并行 + Dynamic Workflows(真DAG) + Devin API/MCP | docs.devin.ai 官方文档 full |
| **GitHub Copilot** | 一手 | 3.75 | Agent mode + Copilot Workspace任务化 + 多模型路由 + MCP + GitHub深集成 | github.com/features/copilot |

### D. 国内第一方/平台组（文档级）

| 产品 | 一手/二手 | 精装度 | 关键预装 | 关键证据 |
|------|:---:|:---:|---------|---------|
| **WorkBuddy(腾讯)** | 一手 | 5 | 多Agent并行 + 100+专家/7万+Skills + 托管底座(Managed Agents) + 企业安全治理(ISO/SOC/等保) + 3交付形态 | cloud.tencent.com/product/workbuddy 官方页 |
| **Coze扣子(字节)** | 一手 | 4.5 | 可视化工作流 + 单/多Agent + 插件商店 + 知识库 + 长期记忆 | docs.coze.cn 官方文档 |
| **QCode(qcode.cc)** | **二手** | 3.5 | 一Key七模型族 + Claude Code一键 + CC Switch多账号 + 成本指南 | qcode.cc 官方页；明示'官方价×服务倍率' |

---

## 三、关键实证发现（洞察）

1. **「一手/二手」与「精装度」正交**：
   - 一手精装高：OpenHands/Dify/Cursor/Devin/WorkBuddy/OpenClaude（自研+预装满）
   - 二手精装中：CCR(3), QCode(3.5)（封装底座中转，预装度中等但非自研）
   - 一手精装中：CrewAI(3)/gpt-researcher(4)（自研但预装受限）

2. **「声称 vs 实际」典型案例**：
   - **CCR 声称是 Claude Code 增强**，实际核心依赖 `@the-next-ai/ai-gateway`（**二手网关底座**）——源码级证实
   - **QCode 声称平替 Claude Code**，实际明示'官方价×服务倍率'（**二手中转**）——文档级证实
   - **Windsurf 声称有 Flows DAG 多Agent编排**，实际**无此功能**（多Agent并发=Arena+worktrees+Managed Devins）——文档检索否定
   - **CodeWhale/OpenClaude 声称是 Claude Code 平替**，实际**独立自研底层**（非CC封装）——源码级证实

3. **精装度分层**：真·开箱即用成品（OpenHands/Devin/WorkBuddy/Dify/OpenClaude 5分）> 成品化受限（Cursor/Windsurf/Coze 4-4.5）> 需配置框架（CrewAI/CCR/QCode 3-3.5）。
