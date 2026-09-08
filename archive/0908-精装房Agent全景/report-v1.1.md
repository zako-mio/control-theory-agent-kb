# 任务完成报告 — 控制理论 ⊗ Agent 设计知识库 v1.1「精装房全景」专题

> **归档说明（历史版本）**：本报告为 v1.1 阶段留档；精装度评分口径已于 v2.0 改为「硬门槛 + 8 维加权 + 一票否决」加权模型（见 `../../07-checkpoint/premium-scoring-model.md`），本报告中的单点分值属历史版本口径。
> AI 友好留档版（人类可读版见同目录 `report-v1.1.html`）
> 版本：v1.1.0　完成日期：2026-09-08　负责人：主Agent
> 任务路径：`archive/Mission-file/2026-09/0907-控制理论Agent设计知识库/`

---

## 1. 当时情况

### 1.1 任务背景

在既有「控制理论 ⊗ Agent 设计知识库」（v1.0，6 个技术框架产品版）基础上，用户希望**增加市面「精装房」Agent 产品的案例分析**——即那些主打「开箱即用、预装全套能力」的商用/开源成品（如 Cursor、Devin、Dify、Coze 等）。用户的核心好奇点是：**这些产品到底「精装」到什么程度？**

### 1.2 用户原始需求

- 调研市面主流「精装房」Agent 产品，形成全景分析；
- 核心命题由用户洞察提出：**「声称 ≠ 实际」——源码分析能看出真正的一手还是二手**；
- 交付形态：人类可读的高可读交互 HTML（用户明确只看 HTML），AI 端 MD 为低优先镜像；
- 落点：在**现有知识库内扩展**为 v1.1，而非另起炉灶。

### 1.3 环境状态

- 运行环境：WSL2（Linux），工作目录 `/home/zako-mio/opencode`；
- 网络：默认直连，境外被墙站点按需经宿主机代理网关 `172.29.0.1:7890`；
- **关键环境障碍**：`git clone` 不稳定（大仓库频繁挂起），GitHub API 返回 403（未认证限流）→ 最终改用 **`raw.githubusercontent.com` 源码级逐个文件获取**，绕开 clone/API 限制，完成开源源码级实证。

---

## 2. 制定计划

### 2.1 grill-me 收敛的 13 项决策

| # | 决策 |
|:--:|------|
| 1 | 案例定位 = 跨 4 大类「精装房全景地图」 |
| 2 | 分类骨架 = 按供应方 4 类（第一方成品 / 二次封装 / 低代码平台 / 开源成品化） |
| 3 | 核心命题 = 声称 vs 实际（源码/黑箱实证鉴别一手/二手） |
| 4 | 实证深度 = 开源机制级 + 闭源文档优先 + 黑箱兜底（无密钥授权） |
| 5 | 分析框架 = 五环 + 精装度双维度 |
| 6 | 精装度量化 = 先分析，数据涌现后定评分量表（不预设公式） |
| 7 | 交付形态 = 交互 HTML 全景页 + 案例页 + 新 DAG 图 |
| 8 | 落点 = 现有知识库内扩展 → v1.1 |
| 9 | 双维度覆盖 = 全库统一（现有 6 + 新增） |
| 10 | 开源成品化取舍 = 保留真精装房（OpenHands/gpt-researcher）+ 框架半成品对比 |
| 11 | 坐标系 = 精装度 0-5 主轴 × 一手/二手标签 × 4 大类 × 五环定位 |
| 12 | 维度组织 = 精装度为主轴，一手/二手为标签（非独立轴） |
| 13 | 推进 = 先落盘计划再执行；用户只看高可读 HTML |

> **关键概念澄清（决策 12）**：「一手/二手」与「精装/毛坯」是**正交的两根轴**。精装/毛坯 = 预装了多少；一手/二手 = 供应方是否原创者。毛坯房也可以是二手（开源壳包装发版），精装房也可能是一手（大厂自研成品）。

### 2.2 执行阶段划分

| Phase | 内容 | 委派 | 产出 |
|:---:|------|------|------|
| **0** | 契约扩展：精装度定义 + 证据分级 + 四维坐标系 → `contract.md` v1.1 | 主Agent | `00-contract/contract.md` |
| **1** | 开源源码级实证：CodeWhale / CC-Router / Dify / OpenHands / gpt-researcher / 框架半成品 | explore/general 子Agent | 源码证据包 |
| **2** | 闭源文档 + 黑箱实证：Cursor / Windsurf / Copilot / Devin / WorkBuddy / Coze / QCode | search-worker/explore | 文档证据包 |
| **3** | 差量分析：声称精装度 vs 实证精装度 → 涌现精装度评分量表 | 主Agent | 精装度量表 + 差值矩阵 |
| **4** | 五环画像：每产品 `03-cases/premium-*.md`（五环 + 精装度） | general/explore | 14 份画像 MD |
| **5** | 交互交付：精装房全景页 + 案例页 + 精装房 DAG | 主Agent + drawio-worker | `04-interactive/premium-*` |
| **6** | 全库统一双维度：现有 6 产品补精装度字段 + 再分类，更新索引/README → v1.1 | main | 全库 v1.1 |
| **7** | 门控 + 留档：L1-L7 分层门控 + 双版本报告 | 主Agent | 审计 + 留档 |

### 2.3 红线约束

1. 闭源全部**文档优先**，**不申请任何 API 密钥/授权**；
2. **人类可读 HTML 为唯一成果重心**（用户只看 HTML）；AI 端 MD 镜像为低优先配套；
3. 契约红线：仅 `/tmp/opencode` 实机黑箱 + 源码只读；不改记忆系统文件；不做不可逆破坏；
4. 复用既有资产：`render_case.py` / `gen_html.py` / `nav_data.py` / 门控脚本 / `design-tokens.css`；
5. 违约回退：源码能做的做到机制级，做不到的用文档 + 行为分级标注，不强求统一。

---

## 3. 执行情况

### 3.1 Phase 0 — 契约扩展

在 `00-contract/contract.md` 新增 **§2.5 精装房全景专题**：定义四维坐标系、证据强度四级（源码级 🧪 > 文档级 📄 > 行为级 ▶ > 声称级 🗣）、精装房产品 ID 命名规则（`premium-{short}`），并同步目录结构与深链规则。契约仍为唯一硬约束来源，子Agent 只引用短路径、不复制全文。

### 3.2 Phase 1 — 开源源码级实证

通过 `raw.githubusercontent.com` 逐个抓取仓库关键文件（`package.json` / `Cargo.toml` / `pyproject.toml` / README / 入口），做机制级分析：

- **OpenHands**：`package.json` bin=`agent-canvas` 一键启动；software-agent-sdk 4 个自研包；子Agent 预设 `openhands.tools.preset.subagents`；
- **Dify**：`api/pyproject` **无 langchain 依赖**，自研 `graphon` 编排引擎；`api/core/rag` 133 路径 RAG pipeline；
- **CrewAI**：`pyproject` 自研 `crewai-workspace`；`crewai create crew` 脚手架 + crewai-tools 20+ 工具；
- **CodeWhale**：`Cargo.toml` **20 个自研 crate**（agent/tools/mcp/hooks/execpolicy）；
- **Claude Code Router**：`packages/core` 依赖 **`@the-next-ai/ai-gateway`** 第三方网关底座（二手铁证）；
- **OpenClaude**：`@gitlawb/openclaude` v0.30.0，独立 TypeScript 实现；
- **gpt-researcher**：`multi_agents` 8-agent 团队（LangGraph）+ NextJS/FastAPI Web UI。

### 3.3 Phase 2 — 闭源文档级实证

对 Cursor / Windsurf / Copilot / Devin / WorkBuddy / Coze / QCode 采集官方文档与定价机制，标注文档级证据。**不做任何需密钥/授权的黑箱实测**（规避红线），未实证的营销话术一律标为「声称级」。

### 3.4 Phase 3 — 差量分析（核心成果）

对照「声称精装度 vs 实证精装度」，形成差值矩阵并**由数据涌现定稿 0-5 评分量表**（以「用户零配置即可跑端到端任务」为核心锚点）。三大实证发现：

1. **二手被高估**：CC-Router（源码级铁证依赖 `@the-next-ai/ai-gateway` 第三方网关）、QCode（官方明示「官方价×服务倍率」）——声称「平替 Claude Code」，实为封装/中转；
2. **一手被低估**：CodeWhale（自研 Rust 底层 20 crate）、OpenClaude（独立 TS 实现）——声称「平替」，实为独立自研；
3. **声称功能不存在**：Windsurf 无「Flows DAG」多 Agent 编排（多 Agent 并发 = Arena Mode + worktrees + Managed Devins）。

### 3.5 Phase 4 — 五环画像

按 `07-checkpoint/PREMIUM-CASE-TEMPLATE.md` 契约模板，为 14 款产品各生成一份 `premium-*.md`：精装度评分 + 预装能力清单 + 声称vs实际 + 五环（SP/E/T/M/P/R）定位。硬性要求：环标题含 `(E 环)` 等标记供渲染器解析，精装度/一手二手结论必须与 `premium-evidence.md` 一致、不得篡改。

### 3.6 Phase 5 — 交互交付

- `premium-map.html`：精装度主轴（0-5 降序）条形谱系 + 4 大类卡片；
- `premium-cyto.html`：精装房 DAG 交互图（14 产品节点，精装度着色 + 一手/二手形状 + 4 大类分组框）；
- 14 个 `premium-{product}.html` 案例页（由扩展后的 `render_case.py` 渲染）；
- 新增生成脚本 `09-src-data/gen_premium_cyto.py`。

### 3.7 Phase 6 — 全库统一双维度

现有 6 个技术框架产品补精装度字段并再分类（2.5-3 分，需装配/定制，纳入对照），更新 `README.md` / `index.html` / `05-md/00-index.md` 至 v1.1。

### 3.8 Phase 7 — 门控 + 留档

分层门控（L1-L7）：结构层脚本 `quality-gate.py`（扩展精装房覆盖度与页面结构校验）+ 视觉层 VLM + 渲染层 headless Chromium + 覆盖度审计。结果为 **ALL PASS（0 issues）**。

### 3.9 遇到的问题及应对

| 问题 | 应对 |
|------|------|
| `git clone` 大仓库挂起 | 改用 `raw.githubusercontent.com` 逐文件获取 |
| GitHub API 403（未认证限流） | 同上，绕开 API，走 raw 内容端点 |
| 闭源产品无法源码级验证 | 文档级优先 + 声称级标注，不申请密钥（守红线） |
| Windsurf 营销声称与实际不符 | 文档检索否定，标为「声称功能不存在」 |
| 多产物互引一致性风险 | 契约先行 + 画像模板统一标记，精装度结论强制对齐证据文件 |

---

## 4. 完成情况

### 4.1 交付物清单

| 类别 | 路径 | 说明 |
|------|------|------|
| 契约扩展 | `00-contract/contract.md` | v1.1，新增 §2.5 精装房专题 |
| 计划文档 | `07-checkpoint/PLAN-v1.1.md` | 13 决策 + 8 Phase |
| 实证证据 | `07-checkpoint/premium-evidence.md` | 14 产品证据汇总 |
| 差量分析 | `07-checkpoint/premium-diff-analysis.md` | 声称 vs 实际 + 评分量表 |
| 画像模板 | `07-checkpoint/PREMIUM-CASE-TEMPLATE.md` | 渲染器契约 |
| 画像 MD ×14 | `03-cases/premium-{cursor,devin,workbuddy,windsurf,copilot,dify,openhands,coze,openclaude,codewhale,gptresearcher,qcode,ccrouter,crewai}.md` | 五环 + 精装度 |
| 全景页 | `04-interactive/premium-map.html` | 精装度主轴谱系 |
| 精装房 DAG | `04-interactive/premium-cyto.html` | 14 节点交互图 |
| 案例页 ×14 | `04-interactive/premium-*.html` | 单产品画像 |
| 生成脚本 | `09-src-data/gen_premium_cyto.py`（新增）；`render_case.py`/`gen_html.py`/`nav_data.py`（扩展） | — |
| 门控 | `07-checkpoint/quality-gate.py`（扩展） | 结果 ALL PASS（0 issue） |
| 更新 | `README.md` / `index.html` / `05-md/00-index.md` | v1.1 |

### 4.2 精装度谱系（14 产品）

| 分层 | 分值 | 产品 |
|------|:---:|------|
| 真·开箱即用 | 5 | OpenHands / Devin / WorkBuddy / Dify / OpenClaude |
| 成品化受限 | 4-4.5 | Cursor / Coze / Windsurf / GPT-Researcher / CodeWhale / Copilot |
| 需配置框架 | 3-3.5 | QCode / CrewAI / CC-Router |
| 技术框架（现有 6 产品对照） | 2.5-3 | opencode / dsh / PRIME / hermes / claude-code / codex（需装配/定制） |

### 4.3 验证结果

- **结构门控**：ALL PASS（0 issues，覆盖度 32 文件全在、导航无死链、14 页面结构完整）；
- **渲染验证**：headless Chromium + VLM 验证全景页 / DAG / Cursor 案例页 / QCode 案例页，均 PASS；
- **环境问题记录**：`git clone` 挂起、GitHub API 403 → 改用 `raw.githubusercontent.com` 源码级获取。

### 4.4 改动明细

新增交付物约 40+ 文件（契约扩展 + 计划 + 2 份证据/分析 + 模板 + 14 画像 MD + 全景/DAG + 14 案例 HTML + 生成脚本）；修改 `contract.md` / `quality-gate.py` / `render_case.py` / `gen_html.py` / `nav_data.py` / `README.md` / `index.html` / `05-md/00-index.md`。**未修改任何记忆系统文件，无不可逆破坏。**

---

## 5. 反思 / 分析 / 建议

### 5.1 过程反思

- **「声称 ≠ 实际」方法论被实证验证**：市场命名（「XX 平替 / XX 增强」）极易误导。只有**源码依赖分析**（如 `@the-next-ai/ai-gateway`）或**定价机制**（官价×倍率）能揭示一手/二手真相。这一命题在本批 14 产品上成立了 4 个反直觉案例。
- **契约先行的价值再次验证**：先落盘计划 + 模板 + 证据文件，使 14 份画像与全景/DAG/案例页在精装度、一手二手结论上强制一致，零返工。
- **环境受阻时的降级路径**：`git clone`/GitHub API 不可用时，`raw.githubusercontent.com` 是可靠的源码级替代，无需放弃实证深度。

### 5.2 收获认知

1. **精装度与一手/二手正交**：二手也可以精装（CCR 3 分、QCode 3.5 分），一手也可能不精装（CrewAI 3 分）。做全景时必须**分开标注**，不能互相推断。
2. **证据分级是可信度防线**：源码级 > 文档级 > 行为级 > 声称级。闭源产品文档级标注 + 未实证标声称级，避免把营销话术当事实。
3. **五环框架可迁移到商用成品**：把精装房也纳入 M/P/R/T/E 五环定位，使「预装程度」与「控制论本质」两个视角互补。

### 5.3 未来改进建议

1. **补黑箱行为级实证**：当前闭源产品止于文档级；未来若有免费额度/无需密钥的测试路径，可补行为级验证（严守不申请密钥红线）；
2. **精装度评分可量化加权**：当前量表由数据涌现定稿，后续可将 8 项预装能力维度（多Agent/ Skill库/ 工作流/ 模型接入/ 一键部署/ 沙箱/ MCP/ 记忆）显式加权，提升可复现性；
3. **产品谱系持续跟踪**：精装房市场迭代快（Cursor/Devin/Windsurf 更新频繁），建议定期回归证据文件与评分；
4. **「声称功能不存在」类发现应单独建索引**：Windsurf Flows DAG 案例价值高，可沉淀为「营销话术勘误」子库。

### 5.4 契约遵守确认

全程遵守最小必要破坏性操作范围（可逆 + 受控故障注入），**未修改记忆系统文件**，未做不可逆破坏；未申请任何 API 密钥/授权；闭源实证严守文档级 + 声称级标注。

---

### 📚 证据来源

| SRC | 级别 | 信源 | 路径/URL | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S4 | 一手源码观察 | `raw.githubusercontent.com`（OpenHands/Dify/CodeWhale/CCR/OpenClaude 等） | 高 |
| SRC-002 | S1 | 官方文档 | cursor.com/docs、docs.devin.ai、docs.coze.cn、cloud.tencent.com/product/workbuddy | 高 |
| SRC-003 | S1 | 官方定价页 | qcode.cc（「官方价×服务倍率」） | 高 |
| SRC-004 | S4 | 本库实证汇总 | `07-checkpoint/premium-evidence.md` | 高 |
| SRC-005 | S4 | 本库差量分析 | `07-checkpoint/premium-diff-analysis.md` | 高 |
| SRC-006 | S4 | 结构门控结果 | `07-checkpoint/quality-gate-result.txt`（ISSUES=0） | 高 |
