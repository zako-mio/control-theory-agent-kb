---
description: 审阅 Reflection 系统中待确认的 Memory/Skill 条目（/reflection memory|skill|status|browse 区分子动作）。基于 2026-08-20 完整流程沉淀：三池扫描、统一分析优先逐条兜底、独立性/重复性三分类、容量 A/B/C/D 分层、签名门禁校验、双版本同步。2026-09-14（G-40）新增链路校验：recover-stale 超时回退、validate 字段存在性/双写契约/schema/归档隔离机检、备份轮转与归档隔离门控。2026-09-28 新增步骤 4b「迭代治理」（准入去重 ADD/UPDATE/DELETE/NOOP、退役三态 keep/update/remove|archive、陈旧与悬空引用机检、Coverage/Citation 双机检、减法与结构重构判据）并修订容量口径（硬＝行>200 或 字节>25000 源自官方；软＝字符>5000 为自愿纪律）。2026-10-10 新增生命周期口径（用户定调「条目越多注意力越分散，效用越低」）：常驻注意力视作**零和公共资源** ⇒ 准入增「边际显著性」关、新增**零和预算**（段数不增）、并接结构面机检（单段占比 >50% 软超限；`--soft-segments` 默认关＝须用户裁决项）。
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

### 1b. 链路校验（超时回退 + 字段存在性，2026-09-14 G-40）

扫描前先跑两个只读/自愈命令，保证队列结构自洽；两者都必须凭**命令退出码**判定，不得凭肉眼：

1. **processing 超时回退**（先做，防单点阻塞）：
   `python3 ~/.config/opencode/scripts/pending_io.py recover-stale --timeout-days 7`
   - 判据：`processing` 停留 **> 7 天**判定超时，年龄按 `processing_at`（进入 processing 时自动打点）计算，缺失则回退用 `ts`。
   - 动作：超时条目回退 `waiting` 并写 `recovered_at` + `reflection_note`；无可解析时间戳者**仅报告不回退**；幂等。
   - 验收：退出码 = 0。

2. **schema / 双写契约 / 归档隔离校验**：
   `python3 ~/.config/opencode/scripts/pending_io.py validate`
   - **done 字段存在性判据（硬）**：对每个 `status=done` 的 cycle，断言 `"results" in cycle or "result_path" in cycle` 且非空值。二者皆缺 → 记为 error（命令退出码 1）→ 该 cycle **不得**当作可审阅完成态，须先补齐 `results`/`result_path` 或按未完成状态处理。
   - 附带判据：`meta.{waiting,processing,done}_count` 与实测计数逐项相等；每个 cycle 有 `cycle_id`/合法 `status`/可解析 `ts`；`processing` 不得携带空 `results` 占位。
   - 归档隔离：`memory_pending/` 内出现「已审阅」标记 → error（未审阅/已审阅隔离被破坏）；无对应 cycle 的候选文件 → warning（滞留池孤儿）。
   - 验收：退出码 = 0（无 error）；warning 不阻断但须在概览中提示。

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

### 4b. 迭代治理（2026-09-28 新增：治本于「只加不减」）

**为什么**：MEMORY.md 与 skills 逐轮只加不减 ⇒ 必然触顶。外部权威实践一致指向**写入时门控＋制度化退役**，而非事后反复压缩——有损压缩会丢信息（LongMemEval：以 summary/fact 替代原文损害 QA）、抽象式摘要会幻觉（Maynez ACL2020）、反复自消费有退化风险（Model Collapse/MAD）；且「裸指针」有强实证腐化率（Perma：HLR 2014 >70%、2021 更新 75%；HTTP 200 也靠不住）。调研结论与全部链接见 `~/opencode/archive/Mission-file/2026-09/0928-reflection-review/research/SYNTHESIS-迭代策略结论.md`。

> **2026-10-10 用户定调（口径升级，刚性）**：「memory 写长了写多了意义不大——**条目越多注意力越分散，效用越低**」。
> 推论：常驻注意力是**零和公共资源**，效用对条目数**次可加** ⇒ 既有「必要性＝常驻成本 vs 覆盖价值」中的成本项
> **须计入「注意力稀释」这项公共成本**；判据由「**够不够格留下**（不重复、有价值）」上移为「**值不值得挤掉别人**（边际显著性）」。
> 机检形态：`memory_capacity_check.py` 的结构面判据（单段占比 / 段数 / 零和预算，见其 docstring 二之补）。

每次审阅固定执行**五件**，产出并入步骤 7 的清单：

1. **准入去重（ADD / UPDATE / DELETE / NOOP 式，逐条裁决）**：每条候选先判与既有 MEMORY 段／既有 skill 章节的关系，四选一并在账本留痕。
   **⛔ 过「边际显著性」关（2026-10-10 新增，只对 MEMORY 常驻区施加）**：拟入常驻的条目须同时答**三问**——
   ①高频触发（够常驻税）？②不可重查（配置/文件系统查不到）？③**它比同额预算下可被它挤掉的那条更值吗**？
   三问缺一 ⇒ 一律**下沉 skill（按需加载）**，⛔ 不因「未在他处重复/独一无二」而保留（唯一性不是显著性）。
   细则：
   - `ADD` 无等价条目 ⇒ 采纳；`UPDATE` 为既有条目的增量 ⇒ 并入并标来源；`DELETE` 与既有**矛盾** ⇒ 先裁取代关系（⛔ 不改史：以取代声明列「旧→新」，旧件保留为历史记录）；`NOOP` 已有等价 ⇒ 不写。
   - 机检辅助：`python3 ~/.config/opencode/scripts/prompt_audit.py` —— 其 **W2** 输出 MEMORY 规则句与各 skill 的**近重复对**及 Jaccard（供去重裁决，⚠ 不设阈值、只报告）。
2. **退役三态（keep / update / remove｜archive）**：退役须显式选态并留痕；`remove` **不等于删除** —— 一律先 `archive`（前像 ＋ sha256），再在原处标注「已被 `<新件>` 取代」。⛔ 不得静默删除。
3. **陈旧 / 悬空引用机检**：`python3 ~/.config/opencode/scripts/prompt_audit.py --strict`。
   - 对 **MEMORY.md** 悬空路径引用判 **FAIL**；对 **skill 文件**默认判 WARN（该启发式在 skill 上假阳率高，分诊记录见脚本 docstring：全库 153 项 → 修根后 57 项，抽样均为相对其它目录的引用 / doc 举例 / 设计陈述）。
   - 另报「时间型字面量」清单（**未来日期判 FAIL**）；⚠ 不判「多旧算陈旧」（该阈值无权威依据，须用户裁决，不得由规模直觉设定）。
4. **Coverage / Citation 双机检（任何减法或结构重构后必跑）**：
   - **Citation**＝每条被删/被搬的内容须有**承载位点**（文件 ＋ **逐字**关键词，`grep -F` 须命中）。
   - **Coverage**＝`python3 ~/.config/opencode/scripts/subtraction_coverage_check.py --before <前像> --after <新件> [--after-extra <搬迁文件,逗号分隔>] [--ledger <账本>]`：
     **H1 标题集合不可丢**、**H2 规则句零完全丢失** 为硬判据；W1（加粗/代码跨度逐字覆盖）与 W2（数字细节收缩）只 WARN。
     ⚠ 结构重构档须用 `--after-extra` 把被搬迁文件并入 after 语料（内容「搬走 ≠ 丢失」）。

5. **零和预算（2026-10-10 新增，MEMORY 常驻区专属）**：**新增一条 ⇔ 退役或下沉一条**。
   - 机检：`python3 ~/.config/opencode/scripts/memory_capacity_check.py --baseline <前像> --zero-sum-segments` ⇒ **段数相对前像增长即软超限**（新增一条须伴退役一条）。
   - 配套观测：段数 / 单段最大占比（`seg_share_max`）无条件输出；**单段占比 > 50% 即软超限**（结构性细则倾泻信号）。
   - ⚠ **段数绝对上限属「须用户裁决项」**（`--soft-segments`，默认 None=不启用）：⛔ 不得由规模直觉设定该数（同 `prompt_audit` 不判「多旧算陈旧」的惯例）。

**减法判据（两侧分列，⛔ 不得凭手感删）**：

- **MEMORY.md（常驻索引）**：按 A 事实型（可从配置文件/文件系统重查 → 聚合）/ B 协议重复型（已由 `instructions/*.md`、`command/*.md` 等**共载件**承载 → 压为指针）/ C 方法论型（保留但压缩例证）/ D 本轮新增高价值（完整保留）分层。**判据、阈值、结论一律内联自足**；只有**例证、长引文、过程叙述**可剥离或指针化。⛔ 裸外链指针（指向未共载、易腐化的外部对象）。
  - ⚠ **分层只回答「怎么放」，不回答「该不该放」**：该不该放须先过上面的**边际显著性三问**。**「跨域元规则即便未在他处重复」不构成保留理由**（唯一性 ≠ 显著性；每条常驻规则都在摊薄其余规则的注意力）。
  - **本 skill 与 MEMORY 的分工（2026-10-10 明确）**：MEMORY ＝ **常驻索引**（母题一句话 ＋ 指针）；**细则**（含原「批（…）」跨周期元规则记录）＝ skill 的按需 `references/*.md`。判据「细则已下沉」须以 `--after-extra <承载文件>` 经 Coverage 门证「搬走 ≠ 丢失」，⛔ 不得只留裸指针。
- **skill**：四判据 ①同族多实例（同元规则只留 1 条结论＋「域内实例见 X」）②跨文件重复 ③例证压缩（保留判据与结论，具名实例全篇上限 1 条）④结构冗余（导语/自指复述/重复预防性说明）。⛔ 不得以「MEMORY 已载」为由删本件判据（既定方向是「MEMORY 压指针、skill 保真」）；②仅可用于**姊妹 skill 逐字承载**且须 grep 出命中行。
- **每条割舍必须写**「承载位点（文件 ＋ 逐字关键词｜须机检命中）或 判死理由」；二者皆无 ⇒ **不得删**（fail-closed，⛔ 不得以「不在批清单」为由判死）。
- **算前先测**：定减幅预算前须先做**可删面实测**（如括号内容审计 ＋ 判据关键词抽检），⛔ 禁凭规模直觉估预算（实证：首轮估「−1500～−2500」，实测可删面仅 ~−530）。

**结构重构档（超出推荐额度时）**：skill 若超出 Agent Skills 开放标准推荐额度（`SKILL.md` > 5000 tokens 或 > 500 行），**优先拆分重构**为 `SKILL.md`（判据索引 ＋ 四阶段总览 ＋ 交叉指针）＋ **一层深** `references/*.md`，而非行内删削。要求：frontmatter 逐字节不变、标题集合不丢、内部 `§X.Y` 自引改写为显式路径、双根（live ＋ 归档 skill 根）逐字节一致。

### 5. 签名门禁

- 写入 MEMORY.md 的每个 § 段必须带 `[src: <cycle_id>]` 签名，签名取自该条目的来源 cycle id。
- `manual_pending` 签名的段（历史直接写入）在确认后应转正为真实 cycle_id 或删除。
- 合并段内追加内容需标注来源（如 `(2026-08-18 追加 cycle_0818_v4_fix)`），保持可溯源。
- 写入后校验：MEMORY.md 全段都有签名、无裸段（校验脚本：按 `§` 切分，每段首行必须是 `[src: ...]`）。

### 6. 清理队列

- 已确认（yes/edit）的 cycle/条目，从 pending.json 的 cycles 中移除（或移除其已确认的 reflections 条目）。未确认（no）的条目一并移除。
- **加锁原子写回（唯一合法路径）**：对 `pending.json` 的任何写入都必须经 `~/.config/opencode/scripts/pending_io.py`，禁止自行 read→edit/write 整文件。该脚本以 `fcntl.flock(LOCK_EX)` 独占锁串行化多写者，用同目录临时文件 + `os.replace` 原子换入，并自动重算 `meta.waiting_count / processing_count / done_count`、写前备份与备份轮转：
  - 移除已审阅 cycle：`python3 ~/.config/opencode/scripts/pending_io.py remove --ids <id1,id2,...>`
  - 状态/结果回写：`python3 ~/.config/opencode/scripts/pending_io.py set-status --id <cycle_id> --status done --results-file <results.json>`（或 `--result-path memory_pending/xxx.json`）
  - **done 硬契约**：`--status done` 必须携带 `--results-file` 或 `--result-path`，否则命令拒绝写入（退出码 2）；`results` 仅允许 done 写入。
  - 追加新 cycle：`python3 ~/.config/opencode/scripts/pending_io.py append --cycle-file <cycle.json>`
  - 超时回退：`python3 ~/.config/opencode/scripts/pending_io.py recover-stale --timeout-days 7`
  - 校验：`python3 ~/.config/opencode/scripts/pending_io.py validate`（写回后再跑一次，退出码 0 方可收尾）
  - 只读统计：`python3 ~/.config/opencode/scripts/pending_io.py status`
- 备份轮转：脚本写前自动备份，保留最近 5 份，超限者 mv 归档到 `.archive/backups/`，不物理删除。
- 滞留池文件：插入"已审阅 YYYY-MM-DD"标记（如 `<!-- 已审阅 2026-08-20 -->`），随后**移入 `.archive/processed/`**（唯一归档目录）；`memory_pending/` 内不得残留已审阅文件。
- **`.cycle.json` 口径（2026-09-28 第三窗口落定）**：`append` 登记后 `.cycle.json` **由 `pending.json` 承载，不要求归档**（历史事实：已登记 cycle 的 `.cycle.json` 已不存在；⛔ 不追改历史，只记口径）。**未登记**的 `.cycle.json`（`cycle_id` 不在 `pending.json.cycles` 中）属**滞留件** ⇒ 处置＝**移入 `.archive/processed/`** ＋ 写**加法式取代声明**（列「旧→新」，⛔ 不改史）；⛔ 不得用 `append` 补登记（内容已落盘者会被**二次审阅**）。机检工具：`0928-reflection-review/evidence/round3-next/apply_cycle_json_archive.py`（**默认 dry-run**，`--apply` 才落盘，含 fail-closed 与逐项日志）。
- **JSON 校验**：脚本内建写前序列化 + 写后复读校验，任一步失败即整体回滚，绝不留下半写状态（无需再手工跑 `python -c` 校验确认合法）。

### 7. 双版本同步

- 若本次审阅修改了 Skill 文件，检查其阅读版/镜像（如 `version-upgrade-cascade.md` 是 `SKILL.md` 的阅读版）并同步修改。
- 新增/修改 skill 后回归：SKILL.md 与阅读版内容一致（diff 校验）。

### 8. 临时清理

- 审阅过程中产生的临时脚本（如 cleanup 脚本）用完后删除。
- 任务末尾检查 `/tmp` 及临时目录残留并清理。

## 门控

- **完整性**：步骤 4 必须走完——统一分析或逐条确认，不能跳过确认直接写入。
- **写入批处理（2026-09-14 C01 接线 · 前缀缓存治理）**：单次 `/reflection` 会话对 `MEMORY.md` **至多一次写回**——先完成全部分类 / 去重 / 签名组装，再合并 `§` 段后**一次性写回**；禁止边审边写、禁止多次追加。理由：`MEMORY.md` 位于常驻 system 前缀中段，一次中段改写即击穿其后全部 prefix-cache（跨天改写命中率 99.4% 被击穿）；批处理把改写频次压到会话级 1 次。
- **容量＋结构（2026-10-10 口径补齐）**：写入 MEMORY.md 前必须运行
  `python3 ~/.config/opencode/scripts/memory_capacity_check.py --baseline <前像> --zero-sum-segments`
  （**结构面**：`--zero-sum-segments` ⇒ 段数相对前像增长即软超限；单段占比 > 50% 恒软超限；两者推导与「不得由规模直觉设定段数上限」的显式声明见脚本 docstring 二之补）。
- **容量（2026-09-28 口径修订）**：同一命令的**多口径**判据（`kind=memory` 硬限＝**行数 >200 或 字节 >25000**〔源自 Claude Code 官方 auto-memory 口径「前 200 行或前 25KB」〕，软限＝**字符 >5000**〔**自愿纪律**，无权威依据〕；`kind=skill` 软限＝**行数 >500 或 token >5000**〔源自 Agent Skills 开放标准，推荐级〕）。判据只取该脚本对文件的**实测**；`pending.json.meta.last_review` 的容量记录是历史快照、**不具判据地位**。
  - 口径推导与来源见脚本模块 docstring 第一节；**token 为代理观测**（tiktoken 实测、**取各编码上界**；本机模型 tokenizer 不同源，已在脚本内声明）。
  - `band=hard` → 必须先按下方减法判据精简再写入，不得自动截断；`band=soft` → 提示不阻断。
  - 变更留痕：原「字符硬 6000」判据因**无权威依据**已降级为可选 `--voluntary-chars-hard`（默认不启用，仅供回归对比）。
- **减法 / 重构门控（2026-09-28 新增）**：凡本轮对 `MEMORY.md` 或任何 skill 做减法或结构重构，收尾必须实跑**双机检**并通过：
  - `python3 ~/.config/opencode/scripts/subtraction_coverage_check.py --before <前像> --after <新件> [--after-extra <搬迁文件>] [--ledger <账本>]` ⇒ **H1/H2 不得 FAIL**（判据分层见步骤 4b）。
  - `python3 ~/.config/opencode/scripts/prompt_audit.py --strict` ⇒ MEMORY.md 悬空路径引用须为 0、未来日期须为 0。
- **编码**：所有文件读写用 UTF-8；修改 MEMORY.md 后校验中文完整（无 U+FFFD 替换字符）。
- **写入必须持锁**：所有 pending.json 写入必须经 `~/.config/opencode/scripts/pending_io.py`（`fcntl.flock` 独占锁 + `os.replace` 原子换入），禁止绕过该脚本直写；脚本写前自动备份并轮转备份（并发安全的唯一写入路径）。
- **链路校验门控（2026-09-14 G-40）**：扫描前 `recover-stale` 与 `validate` 均须退出码 0；写入后再跑一次 `validate` 退出码 0 方可收尾。
- **收尾门控（2026-09-14 A06 接线）**：MEMORY.md 写入后必须运行 `python3 ~/.config/opencode/scripts/drift_reconcile.py --check` 做漂移对账，并运行 `python3 ~/.config/opencode/scripts/memory_capacity_check.py --baseline <前像> --zero-sum-segments` 复核容量与结构面（段数零和 / 单段占比）。
  - **基线语义（刚性）**：漂移基线已于 2026-09-14 `V4-B03` 在 Wave A/B 完成点**复冻**，`drift_reconcile.py --check` 期望 **exit 0**；出现非 0 即视为**真实漂移**，须查证并修复（复冻只允许发生在迁移完成点）。在本轮迁移全部收口（`V4-E04`）前，本门控**报告失败但不阻断写入**；`V4-E04` 收口后转 fail-closed。
  - 容量：`band=soft` → 提示不阻断；`band=hard` → 必须先按 A/B/C/D 分层精简再写入，不得自动截断。
  - 登记与死资产对账位点：`capabilities_reconcile.py`（能力登记）、`asset_inventory.py`（死资产清单）与之配套，出现登记/资产漂移时一并报告。
- **done 字段门控**：任何 `status=done` 的 cycle 必须满足 `has(results) OR has(result_path)`；不满足不得视为完成态、不得计入待确认条目（由 `validate` 机检，禁止口头判断）。
- **备份轮转门控**：现役 `pending.json.bak-*` 数量 ≤ keep（默认 5）；超限者须已归档到 `.archive/backups/` 且原文件不物理删除。
- **归档隔离门控**：`memory_pending/` 内出现「已审阅」标记即 FAIL；审阅后文件必须移入唯一归档目录 `.archive/processed/`。
- **路径本地化**：所有路径用 Linux 形式（`/home/zako-mio/...`），禁止残留 Windows 盘符形式路径。