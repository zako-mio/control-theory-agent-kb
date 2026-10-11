# 控制理论 ⊗ Agent 设计知识库 — 契约文件 (contract.md)

> 本文件是本知识库的**宪法级硬约束**。所有子Agent 必须以本文件为唯一契约来源，禁止在 prompt 中复制本文件全文（避免长 prompt 截断），只允许引用其短路径 `00-contract/contract.md`。
>
> 版本：`v1.4.0`　创建：2026-09-07　v1.1 扩展：2026-09-08（精装房全景专题）　v1.2 扩展：2026-09-09（自改造 opencode 变体专题）　v1.3 扩展：2026-09-11（自改造 opencode 变体复评）　v1.4 扩展：2026-10-11（dsh 装配层变体专题 + opencode 月度追平）　负责人：主Agent

---

## 1. 任务定位与价值主张

**以 Agent 设计构建为业务核心**（业务需求驱动，非理论全集灌输），控制理论作为**解决 Agent 工程问题的技术工具库**引入。知识库价值主张＝**Agent 系统设计框架**：定义目标函数、状态模型、反馈律；配套大规模实验执行落地。

**定位一句话**：把 Agent 当作一架装了传感器、执行器、逻辑决断器的无人机去建模与控制，拒绝把它当成会聊天的搜索引擎。

---

## 2. 框架覆盖维度（五大核心环）

| 环 | 控制理论对应 | Agent 工程问题 | 本库章节 |
|----|------------|--------------|---------|
| **M — 记忆/状态估计** | 状态估计/观测噪声/卡尔曼滤波 | 长上下文取舍、工作记忆蒸馏、观测噪声过滤 | `ch-memory` |
| **P — 规划/分层控制** | 分层控制/慢-快双速控制器 | 任务分解、里程碑设定、慢规划器+快执行器 | `ch-planning` |
| **R — 反思/反馈闭环** | 反馈闭环/误差收敛/积分环节 | 自我反思、错误回馈、长期偏航补偿 | `ch-reflection` |
| **T — 工具调用/执行器** | 执行器/容错/鲁棒性 | 工具调用失败、冗余仲裁、看门狗限幅 | `ch-tool` |
| **E — 评估/传感器** | 传感器/验证器/信噪比 | Critic 模块、验证器、反馈信号质量 | `ch-eval` |

---

## 2.5 精装房全景专题（v1.1 新增）

本库扩展至**市面主流「精装房」 Agent 产品全景**：跨 4 大类、约 11 个典型产品，并对**全部产品（现有 6 + 新增）进行再分类**。

### 核心命题
> **声称 ≠ 实际**——源码分析能看出真正的一手还是二手。实证鉴别每款产品的真实性质。

### 分析坐标系（四维）
| 维度 | 定义 | 作用 |
|------|------|------|
| **精装度（主轴）** | 0-5 分，预装程度 | 主排序列，标注「毛坯→豪装」谱系位置 |
| **一手/二手（标签）** | 供应方是否原创 | 一手=自研原创；二手=封装/转卖底座 |
| **4 大类（分组）** | 第一方成品/二次封装/低代码平台/开源成品化 | 参考分组 |
| **五环定位** | M/P/R/T/E 控制工程本质 | 控制本质 |

> ⚠️ **关键概念区分**：「一手/二手」与「精装/毛坯」是**正交的两根轴**，不可混。
> - 精装/毛坯 = 预装了多少（精装度）
> - 一手/二手 = 供应方是否原创者
> - 毛坯房也可以是二手（开源壳包装发版）；精装房也可能是一手（大厂自研成品）

### 证据强度分级（实证深度标识）
| 级别 | 定义 | 标注 |
|------|------|------|
| **源码级** | 直接分析源码（依赖/入口/是否包壳/预装能力） | 🧪 源码级 |
| **文档级** | 官方文档/公开架构说明 | 📄 文档级 |
| **行为级** | 实际运行黑箱观察 | ▶ 行为级 |
| **声称级** | 仅官方营销宣称，未实证 | 🗣 声称级 |

---

## 2.6 装配层变体专题约定（v1.2 新增，v1.4 泛化）

本专题分析**官方引擎的衍生变体**（变体：`opencode-custom` / `dsh-custom`，均为个人装配层）——**不重造引擎，仅在配置/协议/skill/MCP/记忆系统五层做定向补强**。

- **基线**：
  - `opencode-custom`：官方 opencode 默认 + 最小常规装配（四 agent + 官方内置 skills + 基础 provider），基线口径见 `03-cases/opencode.md`；v1.4 起本机运行时基线为 **1.18.35**（上游最新 release `v1.19.0` 于 2026-10-11 发布，**只登记不追**）。
  - `dsh-custom`：官方 **dsh v0.2.1-alpha.2**（2026-10-09，commit `d743267`，跨 21 个预发布 tag）默认装配作为宿主内核，装配层为 `dsh-opencode-port` bundle。
- **落点**（`dsh-custom`）：`~/.dsh/presets/opencode/`（3 preset：opencode-standard / creator / ptc）+ `~/.dsh/skills/opencode/`（45 派生 skill）+ 宿主 profile patch（4 provider / permission 5 档 / plugin-manager `pnpmCommand`）。
- **评分方法**：五环**双层评分**（内核层 + 装配层增量 Δ）+ 复用精装度 **v2.0**（硬门槛 + 8 维加权 + 一票否决，见 `07-checkpoint/premium-scoring-model.md`）。
- **口径**（已定结论）：
  - `opencode-custom`：官方精装度 2.9 → 自改造 3.9（Δ+1.0）；五环双层 SP 3.5→4.5、M 3.5→4.0、P 4.5→5.0、R 2.0→4.5（反转）、T 4.5→5.0、E 2.0→4.0（反转）。
  - `dsh-custom`：官方精装度 **3.6 → 3.8**（Δ+0.2）；五环双层 SP 4.5→5.0、M 4.0→4.0、P 4.5→5.0、R 3.0→3.0、T 5.0→5.0、E 2.0→3.5。
- **排名约定**：变体（`opencode-custom` / `dsh-custom`）**不参与 14 产品市售精装度排名**（个人装配层无分发渠道，不与市售产品同轴比较）。
- **证据**：
  - `opencode-custom`：脱敏快照 `07-checkpoint/opencode-custom-snapshot/`（opencode.jsonc / instructions / command / inventory.json），评分单一数据源 `09-src-data/opencode_custom_scores.py`。
  - `dsh-custom`：脱敏快照 `07-checkpoint/dsh-custom-snapshot/`（bundle / profile / inventory.json / manifest.json），评分单一数据源 `09-src-data/dsh_custom_scores.py`（与 `opencode_custom_scores.py` **同构**）。

---

## 2.7 变体复评约定（v1.3 新增）

本约定固化 `opencode-custom` / `dsh-custom` 等衍生变体的**后续再评估口径**，防止多次复评间口径漂移。

### ① 排名隔离（硬约束）
变体（`opencode-custom` / `dsh-custom`）为个人装配层，**不参与 14 产品市售精装度排名**；其分值仅用于「官方内核 vs 装配层增量」的内部对照，不得与市售产品同轴比较、不得对外排名。

### ② 复评口径（三段式，缺一不可）
- **证据层全量重算**：脱敏快照 + `inventory.json` + 评分**单一数据源**全量刷新——opencode 侧 = `09-src-data/opencode_custom_scores.py`，dsh 侧 = `09-src-data/dsh_custom_scores.py`（两者同构）；8 维与五环分值由数据涌现定稿，**禁止手改数值**。
- **交付层全量更新**：画像 MD、diff MD、对照页、门户/README/索引/契约全量同步；生成物必须由生成脚本重生成（**禁只改生成物而不改生成脚本**）。
- **实验层只补新机制**：仅对新机制补做实验，**不重跑既有实验**；历史实验结论保留原版本号并加「历史块」标注，新实验另起章节。

### ③ 脱敏红线
`opencode.env` 不拷贝；密钥一律写作 `<REDACTED>`；`MEMORY.md` 不入公开库（`.gitignore` 排除）。实验仅限 `/tmp/opencode` 隔离区，前后对记忆文件做 sha256 校验。对实机配置只读，不修改 `~/.config/opencode/**`。

### ④ 复评节奏与版本号规则
- **触发条件**：官方基线漂移（opencode / dsh 内核升版）或装配层发生「能力纵深增长 / 机制新增」时触发复评。
- **版本号规则**：复评后知识库版本号递增（如 v1.2 → v1.3），并同步刷新全站版本标识（生成脚本 + 生成物双轨，零残留）。
- **诚实口径**：若复评未跨评分模型 5 档产品阈值，**维持原分值、不虚报跃升**，仅在画像/diff 中刷新 evidence 与机制叙述。

### ⑤ 未入库轮次的补账义务（v1.4 新增）

- **补账义务（硬约束）**：若某轮复评因用户口径「**不入库**」，则**其后一轮复评必须显式补入该轮的实机事实**，并在画像 / diff 中留痕，**不得静默跳过**。
  - **本轮先例**：`2026-09/0914-自改造opencode再评估v1.4` 全量复评明确「**不更新知识库**」→ 本库存在 2026-09-11 → 2026-10-11 的**一个月 backlog**，本轮（v1.4）一次性补入。
- **口径变更须披露（硬约束）**：当某产品从「**单点分**」改为「**8 维模型分**」时，必须**显式声明两者不同源、不可相减**，**禁止呈现为跃升**。
  - **本轮先例**：dsh 旧口径仅「技术框架对照」的**单点分 2.5**（`gen_html.py` `FRAMEWORK_DATA`，**非** 8 维模型输出）；v1.4 首次回填 v2.0 模型得 **3.6**。`3.6` 与 `2.5` **不同源、不可相减**，旧单点分作为历史口径保留（见 `03-cases/dsh-custom-diff.md` §口径披露）。

---

## 3. 目录结构（本知识库全量）

```
0907-控制理论Agent设计知识库/
├── 00-contract/          # 本契约 + 信源分级 + 破坏性范围三清单
│   └── contract.md
├── 01-theory/            # 控制理论证据包（Phase 1，5 分区）
│   ├── 01-closed-loop.md   # 闭环反馈/稳定性
│   ├── 02-state-est.md     # 状态估计/记忆(卡尔曼)
│   ├── 03-pid.md           # PID 与误差收敛
│   ├── 04-robust.md        # 鲁棒控制/不确定性
│   └── 05-hierarchical.md  # 分层控制/慢快双速
├── 02-framework/         # 五大核心环映射框架（Phase 2）
│   └── framework.md
├── 03-cases/             # 产品控制论画像（v1.1 扩展至 ~15 产品；v1.2/v1.4 增装配层变体）
│   ├── prime.md / deepseek-harness.md / opencode.md / hermes.md / claudecode.md / codex.md  # 原 6
│   ├── premium-{product}.md   # v1.1 新增精装房案例（Cursor/Windsurf/... 等）
│   └── {variant}.md / {variant}-diff.md  # v1.2/v1.4 装配层变体画像 + diff（opencode-custom、dsh-custom）
├── 04-interactive/       # 交互 DAG 总览 + 精装房全景页 + 装配层变体页（cytoscape）
│   ├── index.html
│   ├── premium-map.html       # 精装房全景地图
│   ├── premium-{product}.html # 精装房案例页
│   ├── premium-cyto.html      # 精装房 DAG 交互图
│   ├── case-{variant}.html / exp-{variant}.html   # v1.2/v1.4 变体案例页 / 实验页（opencode-custom、dsh-custom）
│   └── compare-opencode.html / compare-dsh.html   # v1.2/v1.4 官方 vs 装配层对照页
├── 05-md/                # AI 友好 MD 镜像 + 索引
│   ├── 00-index.md
│   └── ...
├── 06-experiments/       # 全产品标准实验组记录（Phase 4）
│   ├── README.md
│   └── ...
├── 07-checkpoint/        # 中间产物/生成脚本/门控脚本 + PLAN-v1.1.md
├── 08-drawio/            # draw.io 图表（含精装房全景对照）
├── 09-src-data/          # DAG DATA/KT 详情/生成脚本
├── index.html            # 人类端入口
└── README.md
```

---

## 4. ID 命名规则

- **知识点 ID**：`KT-{type}-{num}`，type ∈ `{ctrl(控制理论), agent(映射/框架), case(产品案例), exp(实验)}`
  - 例：`KT-ctrl-001`（闭环反馈定义）、`KT-case-003`（opencode 控制论画像）、`KT-exp-006`（context 污染实验）
- **章节 ID**：`ch-{五环缩写}` 见上文 `ch-memory/ch-planning/ch-reflection/ch-tool/ch-eval`
- **信源 ID**：`SRC-{n}` 顺序编号，每库维护一个信源登记表
- **产品 ID**：`agent-{short}` short ∈ `{prime, dsh, opencode, hermes, claudecode, codex}`（原 6）
- **精装房产品 ID**（v1.1 新增）：`premium-{short}` short ∈ `{cursor, windsurf, copilot, devin, workbuddy, codewhale, ccrouter, qcode, dify, coze, openhands, gptresearcher, ...}`
  - 案例页：`04-interactive/premium-{short}.html`；画像 MD：`03-cases/premium-{short}.md`
- **衍生变体产品 ID**（v1.2 新增，v1.4 扩展）：装配层变体（官方引擎的衍生变体，**不参与市售排名**）
  - `opencode-custom`（官方 opencode 的衍生变体，案例 ID `KT-case-007`）：画像 MD `03-cases/opencode-custom.md`；diff MD `03-cases/opencode-custom-diff.md`；案例页 `04-interactive/case-opencode-custom.html`；对照页 `04-interactive/compare-opencode.html`；实验页 `04-interactive/exp-opencode-custom.html`
  - `dsh-custom`（官方 dsh 的衍生变体，案例 ID `KT-case-008`）：画像 MD `03-cases/dsh-custom.md`；diff MD `03-cases/dsh-custom-diff.md`；案例页 `04-interactive/case-dsh-custom.html`；对照页 `04-interactive/compare-dsh.html`；实验页 `04-interactive/exp-dsh-custom.html`

---

## 5. 深链格式（双向回链规则）

- **页深链**：同库内相对路径，统一 `./{目录}/{文件名}.html`(人类端) 或 `./{目录}/{文件名}.md`(AI端)
- **章节锚点**：`#ch-memory` 等，凡 HTML 标题加 `id="{章节id}"` 便于深链
- **双线回链**：
  - 人类端 HTML 章节页 → 文末「AI 参考源」列出对应 MD 镜像路径
  - AI 端 MD 镜像 → 文首「人类可读版」列出对应 HTML 路径
  - 理论知识点 → 回链其证据来源 SRC-id + 置信度
- **DAG 深链**：交互图节点点击 → `?drill=KT-xxx`（query 下钻）或 `#ch-xxx`（hash 锚点），与 `0902-opencode-dag` 交互图规范一致

---

## 6. 信源分级与标注规范（分类型差异化）

**核心原则**：分类型差异化——理论/原理类需多源交叉验证；案例类以一手观察+源码为准。

| 级别 | 定义 | 入库资格 | 标注方式 |
|------|------|---------|---------|
| **S1 权威一手** | 官方文档/官方论文/官方源码/GitHub 官方 repo | 可独立入库 | ✅✅ // 官方 |
| **S2 权威二手** | 顶级机构/权威期刊/官方博客 | 可入库(含转引标注) | ✅ // 权威二手 |
| **S3 社区/转引** | 博客/StackOverflow/社区教程 | 仅作线索，**不单独入库** | ⚠️ // 转引，作线索 |
| **S4 一手观察** | 本任务直接操控 Agent 的实测/源码分析 | 可独立入库(案例类) | 🧪 // 一手观察 |

**交叉验证有效性判定**：
- **理论类**：同一知识点需 **≥2 个独立 S1/S2 源**一致方可入库存；冲突时标注分歧。
- **案例类**：以 S4 一手观察/源码为准，S1-S3 仅补背景，不强制双源。
- **高危险数据**（安全评分/宏观统计/权威数值）：强制回源核对 ≥2 源。

**每知识点末尾 evidence 信源区块**（沿用 0902-opencode-dag 范式）：
```
### 📚 证据来源
| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S1 | 官方文档 | ... | 高 |
| SRC-002 | S2 | 权威二手 | ... | 中 |
```

---

## 7. 最小必要破坏性操作范围（三清单 ⛔ 实验红线）

> **适用范围**：Phase 4 全产品标准实验组，特别是 Windows 侧老旧 opencode（v1.18.16）实验。
> **原则**：可逆 + 受控故障注入。**仅允许可还原操作**，不改记忆系统文件，不扩大影响面。

### ✅ 允许清单（可逆）
1. 修改 config/agent 文件但**先备份**可 revert（备份至 `00-contract/backup/` 或 `/tmp/opencode/backup/`）
2. 创建**临时测试夹具**：测试 agent / 测试 skill / 测试 prompt（仅放在 `07-checkpoint/fixtures/` 或 `/tmp/opencode/`，用完即清理）
3. **模拟故障注入**：伪造 API 超时 / 上下文污染 / token 截断 / 工具调用失败（通过 mock 层或环境变量，**不改真实 API 凭据**）
4. 限时**超长循环**（设置 `timeout`，硬上限后可 kill）
5. 在隔离目录 `/tmp/opencode/` 下新建/删除文件（仅限该目录）
6. `opencode run` / `opencode serve` 非交互模式跑实验

### 🚫 禁止清单（绝对红线）
1. `rm -rf` 任何非 `/tmp/opencode/` 路径；严禁删 `.config/opencode/MEMORY.md`、`archive/Reflection/pending.json` 等记忆系统文件
2. 修改 `~/.config/opencode/MEMORY.md` 或 `pending.json`（记忆系统仅走 pending.json→reflection→/reflection 链路）
3. 删除/改写其它 Agent 的会话记录、credentials、真实 API 密钥
4. 杀其它正在运行的进程（`kill` 仅限本实验启动的 `opencode` / `node` 子进程）
5. 扩大故障注入到**非被测产品**（如注入污染污染到其它产品的数据）
6. 任何破坏性、不可逆、无法还原的操作

### ⚠️ 需前置确认（破坏性动作）
1. 任何第一次 `rm`（即使目标在 `/tmp/opencode/`）前需记录目标路径清单并确认
2. 首次**大范围改造** Windows 侧 `opencode.jsonc`（超过单文件改动）前需确认
3. 任何涉及 kill 非本实验进程的操作
4. 任何修改 `MEMORY.md`/`pending.json` 的尝试（直接禁止，此为需审批项）

---

## 8. 分层门控（Phase 6 自审必通）

> 命名统一为 L1-L7（2026-09-08 收敛，解决历史「三层/四层」表述并存问题）。
> 门控脚本：`07-checkpoint/kb_gate.py`（7 层全量）+ `07-checkpoint/quality-gate.py`（结构层补充）。

| 层 | 名称 | 检查项 | 工具 |
|----|------|--------|------|
| **L1** | 生成时自验证 | py_compile / 关键样例实跑 | 子Agent 自测 |
| **L2** | 全量审计 | 字段完整性 / 命名归一 / 跨产物一致 | `quality-gate.py` |
| **L3** | 结构层 | 编码纯净 / HTML 断链 0 / 标签平衡 / 空文件 / NAV 条目齐全 | `kb_gate.py --layers structure,links,nav` |
| **L4** | 视觉层 | 图表无截断 / 中文渲染完整 / 染色排版正确 | VLM（vision-worker） |
| **L5** | 渲染层 | headless Chromium 验证交互 / DAG 无运行态 bug | `kb_gate.py --layers render` |
| **L6** | 覆盖度层 | 全部交付物齐全 + 口径一致 | `kb_gate.py --layers coverage` |
| **L7** | 信源层 | 证据区块完整 / 可溯源率达标 / verified 标注 | `kb_gate.py --layers sources` |

**启用规则**（按项目规模按需启用，全量级建库 L1-L7 全开）：单文件小改 L1+L3；多产物 L1-L3+L6；含动态渲染 +L5；含图片 +L4；含外部事实 +L7。

---

## 9. 实验标准记录模板（Phase 4 每实验必用）

```markdown
# 实验记录：[产品名] - [场景名]
## 1. 实验设计
- 控制组 / 实验组 / 观测指标
- 注入的扰动（故障类型/程度/持续时间）
## 2. 执行数据
- 启动命令 / 环境 / 时间戳 / 日志截断
## 3. 观测结果
- 目标达成度 / 偏差 / 恢复时长 / 收敛性
## 4. 量化指标
- 计划进度偏差(预期步数/实际步数) / 反馈信噪比 / 成本(round/token)
## 5. 控制论解读
- 属于哪一环 / 哪条控制律生效 / 是否暴露稳定性问题
## 6. 链接
- 所属 AC 章 / 关联 KT / 关联案例 / 回链 MD 镜像
```
