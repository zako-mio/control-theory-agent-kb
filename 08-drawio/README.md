# 08-drawio 说明

本目录包含三张 drawio 静态图：

- `five-ring-loop.drawio` / `five-ring-loop.png`：五环控制回路图（v1.0）
- `ctrl-agent-mapping.drawio` / `ctrl-agent-mapping.png`：控制论 → Agent 映射表（v1.0）
- `premium-overview.drawio` / `premium-overview.png`：**精装房全景图**（v2.0 加权模型分值，14 产品 × 3 分层 × 4 大类 × 一手/二手 × 一票否决）

## 版本说明

- 前两张为 **v1.0 静态图**，保留原貌作为历史资产。
- `premium-overview` 为 **v2.0 新增**（2026-09-08 接续任务补入，audit 遗留项），数据源为 `07-checkpoint/premium-score-recompute.md` 与 `09-src-data/premium_scores.py`。

精装房交付的**交互图形态**仍以 HTML 动态图为准：

- `04-interactive/premium-map.html`：精装度主轴条形谱系 + 4 大类卡片
- `04-interactive/premium-cyto.html`：精装房 DAG 交互图（14 产品节点）

> 静态 drawio 图与动态 HTML 图口径必须一致；新增/改分值后须同步重跑 `gen_premium_cyto.py` 与 `check_premium_consistency.py`。
