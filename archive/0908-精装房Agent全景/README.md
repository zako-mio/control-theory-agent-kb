# 留档说明 — 精装房 Agent 全景专题（知识库 v1.1）

> 任务：0907-控制理论Agent设计知识库 → v1.1 精装房扩展
> 完成日期：2026-09-08　留档类型：成果同步留档

---

## 一、本目录内容

| 文件 | 说明 |
|------|------|
| `report-v1.1.md` | 留档报告（AI 友好版，5 段完整） |
| `report-v1.1.html` | 留档报告（高可读版） |
| `PLAN-v1.1.md` | 执行计划文档（grill-me 13 项决策） |
| `evidence/premium-evidence.md` | 14 产品实证证据汇总 |
| `evidence/premium-diff-analysis.md` | 差量分析（声称 vs 实际） |
| `evidence/PREMIUM-CASE-TEMPLATE.md` | 精装房画像 MD 模板 |
| `evidence/audit-report-v1.1.md` | v1.1 分层门控（L1-L7）自审报告 |
| `evidence/quality-gate-result.txt` | 门控结果（ALL PASS） |

---

## 二、成果主体位置（知识库内）

本次成果**主体直接落在知识库目录**：
`~/opencode/archive/Mission-file/2026-09/0907-控制理论Agent设计知识库/`

| 类型 | 路径 |
|------|------|
| 精装房画像（14） | `03-cases/premium-*.md` |
| 精装房全景页 | `04-interactive/premium-map.html` |
| 精装房 DAG | `04-interactive/premium-cyto.html` |
| 精装房案例页（14） | `04-interactive/premium-*.html` |
| 契约 v1.1 | `00-contract/contract.md`（§2.5 精装房专题） |
| 生成脚本 | `09-src-data/gen_premium_cyto.py`（新增） |
| 门控脚本 | `07-checkpoint/quality-gate.py`（扩展） |
| 门户入口 | `index.html`（v1.1） |

---

## 三、核心结论速览

**三大实证发现（声称 ≠ 实际）**：
1. **二手被高估**：CC-Router（依赖 `@the-next-ai/ai-gateway`）、QCode（官价×倍率）
2. **一手被低估**：CodeWhale（自研 Rust）、OpenClaude（独立 TS 实现）
3. **声称功能不存在**：Windsurf 无「Flows DAG」多Agent编排

**精装度谱系**：
- 5分：OpenHands / Devin / WorkBuddy / Dify / OpenClaude
- 4-4.5：Cursor / Coze / Windsurf / GPT-Researcher / CodeWhale / Copilot
- 3-3.5：QCode / CrewAI / CC-Router
- 现有6框架对照：2.5-3分（需装配/定制）

**验证**：结构门控 ALL PASS（0 issue）；headless Chromium + VLM 渲染验证 PASS。

---

## 四、级联更新修复记录（重要）

**教训：增量加页 ≠ 级联更新。** 首轮交付误将任务当作"新增页面"，未按 `version-upgrade-cascade` skill 对**整个知识库**做级联更新。经用户指正后，系统性修复了 12 处级联遗漏：

| # | 遗漏点 | 修复 |
|---|--------|------|
| 1 | `nav_data.py` 侧边栏品牌仍"6 产品" | 改"6 框架 + 14 精装房"，全量重生成 |
| 2 | `gen_html.py` 页脚仍"6 产品版" | 改"v1.1 精装房全景版" |
| 3 | 总览页仍"v1.0·6 product"、无精装房 | 纳入精装房专题+入口 |
| 4 | 主交互 DAG 侧边栏无精装房 | 重跑 gen_cyto.py + fix_cyto.py |
| 5 | 框架页页脚 | 级联 |
| 6 | 门户入口"6产品对比" | 改"6框架对比"+精装房专题区 |
| 7 | 实验组 README 口径 | 改"6框架"+精装房实验边界说明 |
| 8 | 旧报告 report.md/html | 加历史版本标注，指向 v1.1 |
| 9 | audit-report.md | 加历史标注，新建 audit-report-v1.1.md |
| 10 | 05-md/00-index.md 口径 | 改"6框架"+精装房索引 |
| 11 | premium-cyto.html 无侧边栏/页脚 | 注入统一 sidebar+页脚 |
| 12 | index_cyto.html 无页脚 | fix_cyto.py 补页脚 |

**修复后一致性**：36/36 页面统一品牌 + v1.1 页脚 + 精装房导航；全站渲染冒烟 0 失败；门控 ALL PASS。
