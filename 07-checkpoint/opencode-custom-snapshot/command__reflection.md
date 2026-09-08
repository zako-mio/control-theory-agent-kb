---
description: 审阅 Reflection 系统中待确认的 Memory/Skill 条目（/reflection memory|skill|status|browse 区分子动作）。基于 2026-08-20 完整流程沉淀：三池扫描、统一分析优先逐条兜底、独立性/重复性三分类、容量 A/B/C/D 分层、签名门禁校验、双版本同步。
agent: build
---

# Reflection 审阅命令

你在 build 模式下执行 Reflection 系统的交互式审阅。用户输入 `/reflection` 或 `/reflection memory|skill|status|browse`（子参数在 `$ARGUMENTS` 中）时，按以下完整流程执行，不依赖其他文档。

## 数据文件

- 队列：`/home/zako-mio/opencode/archive/Reflection/pending.json`
- 记忆库：`/home/zako-mio/.config/opencode/MEMORY.md`
- Skill 目录：`/home/zako-mio/opencode/archive/Reflection/skills/{category}/{name}/SKILL.md`
- 滞留池：`/home/zako-mio/opencode/archive/Reflection/memory_pending/`（reflection-worker 产出但未入 pending.json results 的条目）
- 方法论框架：`/home/zako-mio/opencode/archive/Reflection/skills/agent-reflection/SKILL.md`（分析分类/合并策略/容量分层详见该文档「方法论」章节）

## 执行步骤

### 1. 读取队列（三池扫描）

读取三池待审条目，确认各池 JSON/Markdown 可解析：

1. **pending.json**：`status=done` 的 cycle 的 `results.memory_entries` 与 `results.skill_entries`
2. **memory_pending/ 滞留池**：目录内 `*.md` 文件（reflection-worker 产出但未入 results；实证：08-13/14/18 周期 14 条滞留，双轨写入断链）
3. **MEMORY.md 内 manual_pending 段**：签名 `[src: manual_pending]` 的历史直接写入段，确认后转正为真实 cycle_id 或删除

> ⚠️ 只扫 pending.json 会漏掉滞留池与 manual_pending 段——三池必须全扫。

### 2. 按子动作过滤（`$ARGUMENTS`）

- 无参数 / `all`：展示全部 `status=done` 的 cycle 及三池全部条目
- `memory`：只展示含 `memory_entries` 的 cycle
- `skill`：只展示含 `skill_entries` / skill_proposals 的 cycle
- `status`：不展示内容，仅输出 meta 计数统计（waiting/processing/done），然后结束
- `browse`：只输出每个 `status=done` cycle 的 id、cycle_type、created_at，不展示条目，然后结束
- 未知子参数：提示可用子参数并结束

### 3. 展示条目

对每个待审条目，标注：来源池（pending.json / memory_pending / manual_pending）、cycle id、分类（category）、内容摘要。用中文展示，不使用 emoji。

### 4. 审阅策略（统一分析优先、逐条兜底）

**统一分析优先**：条目数量 ≥ 3 时，先做整体分类分析再批量确认：

1. **4 层通用性标尺**（决定是否入 MEMORY 常驻）：高频触发 → 跨场景独立 → 不可重查 → 改写行为，四关全过才留常驻；缺任一则走特化路径。
2. **特化矩阵**（决定条目进哪个 skill/特化工具）：承接标尺判定为"特化"的条目，配置特化 → opencode-config skill（按其索引路由进 ref/local/ops 子文件）；领域特化 → coding/ 对应 skill。
3. **独立性/重复性三分类**：
   - **放弃**：已有指针/已有覆盖/协议层已承载 → 不写入
   - **合并**：与现有 MEMORY.md 段同主题 → 并入现有段（段内追加，标注来源），不新增段
   - **独立**：无重复且高价值 → 新增独立 § 段
4. **容积分层**（MEMORY.md 超 5000 时的精简框架）：
   - **A 事实型**（配置镜像，可从 opencode.jsonc/文件系统重查）→ 合并为聚合段
   - **B 协议重复型**（内容已由 auto-mode.md/命令文件承载）→ 压为指针
   - **C 方法论型**（真正记忆价值）→ 保留，仅压缩例证细节
   - **D 新增高价值**（本次采纳条目）→ 完整保留
5. **特化 skill 去重审计**（落盘 skill 前必做，防功能冲突/重复/弱化）：
   - 先 grep 该 skill 是否已有等价条目 → 命中即合并（补 `[src: <cycle_id>]`），不新增段
   - 无覆盖 → 挂靠进既有结构章节，不堆在文件尾部
   - 对照 agent-reflection §B+「原流程 4 盲区」自检：覆盖判定须延伸至 skill 文件本身 / 只定位"写去哪"不算完成 / grep 为必做前置 / 须检查三伤害（冲突/重复/弱化）
6. **分组批量确认**：按采纳策略分组（如 A 组/B 组/特化组/转正组），用 `question` 工具多选确认，一组一组来；用户可自定义分组策略。

**逐条兜底**：条目数量少或用户明确要求时，对每条用 `question` 工具确认 yes/no/edit：
- **yes**：采纳。Memory → 写入 MEMORY.md（`§` 分段格式，追加新段落，**必须带 `[src: <cycle_id>]` 签名行**）；Skill → 写入 `/home/zako-mio/opencode/archive/Reflection/skills/{category}/{name}/SKILL.md`（含 frontmatter：name / description）。
- **no**：拒绝。该条不写入。
- **edit**：展示原文，用户修改后按修改后内容写入（同样带签名）。
一次只审阅一条，等待用户确认后再处理下一条。

### 5. 签名门禁

- 写入 MEMORY.md 的每个 § 段必须带 `[src: <cycle_id>]` 签名，签名取自该条目的来源 cycle id。
- `manual_pending` 签名的段（历史直接写入）在确认后应转正为真实 cycle_id 或删除。
- 合并段内追加内容需标注来源（如 `(2026-08-18 追加 cycle_0818_v4_fix)`），保持可溯源。
- 写入后校验：MEMORY.md 全段都有签名、无裸段（校验脚本：按 `§` 切分，每段首行必须是 `[src: ...]`）。

### 6. 清理队列

- 已确认（yes/edit）的 cycle/条目，从 pending.json 的 cycles 中移除（或移除其已确认的 reflections 条目）；同步更新 `meta.waiting_count / processing_count / done_count`。未确认（no）的条目一并移除。
- 滞留池文件：插入"已审阅 YYYY-MM-DD"标记（如 `<!-- 已审阅 2026-08-20 -->`），保留文件按需查阅，不物理删除。
- **原子写回**：先备份到同目录（如 `pending.json.bak-YYYYMMDD`），再写。
- **JSON 校验**：写回后必须 `python3 -c "import json; json.load(open('<path>'))"` 确认合法。

### 7. 双版本同步

- 若本次审阅修改了 Skill 文件，检查其阅读版/镜像（如 `version-upgrade-cascade.md` 是 `SKILL.md` 的阅读版）并同步修改。
- 新增/修改 skill 后回归：SKILL.md 与阅读版内容一致（diff 校验）。

### 8. 临时清理

- 审阅过程中产生的临时脚本（如 cleanup 脚本）用完后删除。
- 任务末尾检查 `/tmp` 及临时目录残留并清理。

## 门控

- **完整性**：步骤 4 必须走完——统一分析或逐条确认，不能跳过确认直接写入。
- **容量**：MEMORY.md 超 5000 字符时，提示用户手动整理，不得自动截断；按 A/B/C/D 分层框架提出精简方案供用户选择。
- **编码**：所有文件读写用 UTF-8；修改 MEMORY.md 后校验中文完整（无 U+FFFD 替换字符）。
- **备份**：写回 pending.json 前先备份到同目录（如 `pending.json.bak-YYYYMMDD`）。
- **路径本地化**：所有路径用 Linux 形式（`/home/zako-mio/...`），禁止残留 Windows 盘符形式路径。