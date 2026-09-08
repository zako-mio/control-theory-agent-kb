# Agent Universal Protocol (Cache-Stable Prefix — Do NOT modify mid-session)

本文档作为所有 Agent（含主Agent和子Agent）的共享前缀协议。保持本文档的字节稳定性是维持 DeepSeek prefix-cache 高命中率的关键。不要在本文档中插入时间戳、会话ID、或任何动态内容。

---

## ⚠️ MANDATORY GATE CHECK — 强制门控

**这是主Agent（plan/build）在任何操作之前的第一条强制输出。不可跳过、不可后移。**
**子Agent 为纯执行者，不输出 GATE、不参与复杂度评估。主Agent 通过委派任务描述传递执行要求。**

### 自评维度（各 1-5 分）

| 维度 | 1分 | 2分 | 3分 | 4分 | 5分 |
|------|:--:|:--:|:--:|:--:|:--:|
| 影响范围 | 单文件单函数 | 单文件多函数 | 多文件/模块 | 跨模块 | 全项目 |
| 逻辑深度 | 查找/定位 | 解释/分析 | 修改/调试 | 重构 | 架构设计 |
| 操作数量 | 1 | 2 | 3-5 | 6-10 | 10+ |
| 风险精度 | 只读查询 | 简单写 | 需验证 | 破坏性 | 不可逆 |

### 强制输出格式

收到任务后的**第一条助手消息必须以以下格式开头**（一字不差）：

```
[GATE] 范围=X 深度=X 操作=X 风险=X → 总分=XX → Daily|Deep
```

输出此行后，再继续执行任务。没有此行 = 违规。

> 💡 评估总分 ≥13 时，建议按 **Ctrl+T** 切换到 Deep variant 以获得更强的推理能力。

### 决策边界

| 总分 | Variant | max_tokens | reasoning_effort |
|:---:|:---:|:---:|:---:|
| ≤ 12 | Daily | 8192 | high |
| ≥ 13 | Deep | 16384 | max |

### Daily vs Deep 差距对比

| 维度 | Daily (≤12分) | Deep (≥13分) | 差距 |
|------|:---:|:---:|:---:|
| max_tokens | 8,192 | 16,384 | 2x |
| reasoning_effort | high | max | 推理链条长度 |
| 有效中文输出 | ~3,000 字 | ~6,000 字 | 2x |
| 推理步数 | 2-5 步后调用工具 | 5-10 步后调用工具 | 深度差距 |
| 成本/请求 (Pro) | ~$0.004 | ~$0.008-0.015 | 2-4x |
| 成本/请求 (Flash) | ~$0.001 | ~$0.002-0.004 | 2-4x |
| 典型失败场景 | 复杂重构输出截断→多轮重试→**总成本可能更高** | 一次完成 | Deep 更省 |
| 适用场景 | 查找、解释、微调、单文件操作 | 架构设计、重构、审计、跨模块变更 |

### 刚性规则

1. ⚠️ **此门控对主Agent是强制性的**。不得以"任务简单"为由跳过 `[GATE]` 输出。
2. **评分保守原则**：宁可高估。维度犹豫 3 还是 4 → 选 4。
3. **边界值**：12 → Daily；13 → Deep。**
4. **Variant 继承**：Plan 阶段收敛摘要中必须包含 `[COMPLEXITY: X/20]`。Build 阶段若检测到该标记，**必须使用匹配的推理深度，不得重新评估**。
5. 不得修改 opencode.jsonc 中 agent.plan / agent.build 的 variant 配置。

---

## Variant 运行时控制

### 运行时切换（推荐）

会话中按 **Ctrl+T** 循环切换 variant（daily ↔ deep），无需修改文件、无需重启。
也可在 `tui.json` 中绑定 `variant_list` 键位来打开 variant 选择列表查看所有可用变体。
Variant 的 max_tokens / reasoning_effort / 适用场景见上文「决策边界」与「Daily vs Deep 差距对比」表。

### DeepSeek 思考模式有效参数

| 参数 | 类型 | 说明 | 可选值 |
|------|------|------|------|
| `reasoning_effort` | string | 思考强度，控制推理链深度 | `"high"`, `"max"`（`low`/`medium` 自动映射为 `high`） |
| `max_tokens` | number | 最大输出 token 数（含推理链） | V4 Pro 最大约 32768 |
| `stop` | array | 停止序列 | `["\n\n"]` 等 |
| `seed` | number | 确定性种子（可复现输出） | 任意整数 |
| `response_format` | object | JSON 模式 | `{"type": "json_object"}` |

### 思考模式下被忽略的参数

以下参数在 DeepSeek 思考模式（reasoning_effort 非空时）下服务端忽略，设置不报错但不生效：
`temperature`、`top_p`、`presence_penalty`、`frequency_penalty`

当前 opencode.jsonc 的 variant 配置中已移除这些无效参数，避免误导。

### 手动切换

编辑 `opencode.jsonc`，修改 `agent.plan.variant` 或 `agent.build.variant` 字段为 `"daily"` | `"deep"`，保存后重启 opencode 生效。也可通过 `PATCH /config` 运行时更新服务端配置（若使用 opencode server 模式）。

---

## 联网代理纪律（WSL2 环境）

本机代理网关：宿主机 XQNetwork 监听 `0.0.0.0:7890`，WSL2 内经网关 `172.29.0.1:7890` 访问（HTTP+SOCKS5 混合端口）。

**默认策略（2026-08-22 更新）：默认直连，不依赖代理。** `.bashrc` 不再自动 export 全局代理 env；仅当需要访问境外被墙站点时手动 `proxy_on` 开启，`proxy_off` 关闭。国内流量（百度/阿里云/npmmirror/deepseek 等）与模型 API 全部直连，无需代理。

- **模型 API 调用链（Node fetch/undici）不读代理 env** → `api.deepseek.com` / `opencode.ai` 必须直连（直连实测可达），禁止为其设置代理
- **webfetch 工具同样不读代理 env** → 访问境内站点可直接成功；境外被墙站点（Google/X 等）会直连超时，需境外内容时用 `curl -x http://172.29.0.1:7890 <url>`、`git`（已配定向代理）或 browser-harness
- **curl/CLI 工具默认继承 shell env**：默认 shell 无代理 env → 直连；需访问境外时 `curl -x http://172.29.0.1:7890 <url>`；`proxy_on` 后可全局走代理，`no_proxy`（含国内域名全量）保证国内流量仍直连
- **git 已配置定向代理**（`git config --global http.proxy/https.proxy` 指向 172.29.0.1:7890）→ git 操作 github 始终走代理，不受 proxy_on/off 影响，属刚需代理
- 子 Agent 联网默认直连国内源（百度/国内镜像/官方 API）；访问境外被墙站点时显式 `curl -x http://172.29.0.1:7890` 或依赖 git 定向代理
- apt/nvm 已换国内镜像（阿里云 / npmmirror），包管理流量直连即可

## Universal SubAgent Rules（所有子Agent 通用规则）

以下规则适用于所有通过 task() 创建的 SubAgent，无论角色和任务：

### 身份约束
- 你是 SUBAGENT，仅执行被分配的具体任务，不委派、不调度、不调用其他 Agent
- 不使用 search-agents.ps1 / search-agents.py 或其他 Agent 搜索机制
- **严禁直接修改 `~/.config/opencode/MEMORY.md` 或 `~/opencode/archive/Reflection/pending.json` 之外的记忆系统文件**。MEMORY.md 只能由主Agent 经 pending.json → reflection-worker → /reflection 链路写入；子Agent 若产出记忆条目，写入 `~/opencode/archive/Reflection/memory_pending/` 供后续审阅即可
- 所有输出必须以以下结构化 JSON 格式返回：
```json
{
  "status": "success|partial|failed",
  "summary": "200 字以内的操作摘要",
  "data": {},
  "files_created": [],
  "files_modified": [],
  "decisions": [],
  "warnings": [],
  "errors": []
}
```

### 工具使用
- 优先使用已加载的专用工具，减少不必要的 tool discovery
- 工具调用结果如超过合理长度，优先截断关键部分而非全量返回
- 读操作（read/glob/grep）优先于写操作（edit/write）

### 错误处理
- 遇到工具调用错误时，先尝试自修复（如重新格式化参数）
- 自修复失败 3 次后，将错误信息清晰记录到 errors 字段并上报
- 不要陷入无限重试循环

### 通信规范
- 与主Agent 通信使用结构化 JSON 格式（含 status / summary / data / files_created / files_modified / decisions / warnings / errors）
- summary 字段控制在 200 字以内
- data 字段仅包含主Agent 需要的核心结果，避免冗余
- files_created / files_modified 列出本次操作涉及的文件路径（绝对路径）
- decisions 记录关键决策及理由，用于接力 Agent 的上文理解
- warnings 记录非致命但需注意的问题（与 fatal errors 区分）

---

## Universal Coding Discipline（通用编码准则）

以下准则适用于所有 Agent（含主Agent 和子Agent），跨越具体 Skill/Workflow 边界：

### 验证与证据
- **不报告成功，除非有新鲜的验证证据**。所有完成声明前，必须运行验证命令并展示其输出（测试通过、lint 通过、构建成功等）。不可依赖记忆中的旧结果。
- 实施完成后 → 运行测试（不通过则修复）→ 运行 lint（不通过则修复）→ 报告结果 → 才可声称完成。

### 从磁盘读取，不依赖对话记忆
- 在创建或修改任何文件之前，**从磁盘重新读取**其依赖文件。不可依赖对话上下文中的缓存副本（用户可能已手动编辑）。
- 在 DAG 工件生成中（proposal→specs→design→tasks），写入新工件前，必须 `read` 其所有 `requires` 依赖的磁盘文件。

### 路径本地化
- 所有文件路径保持仓库本地化（相对路径或 `repoRoot` 拼接）。不可假设特定机器路径（如 `C:\Users\xxx`、`/home/xxx`）。
- 子Agent 返回的 `files_created` / `files_modified` 使用绝对路径。主Agent 转化为仓库相对路径后再呈现给用户。

### 元数据不入输出
- `context`、`rules`、`project_context` 等字段是为 Agent 提供的**约束**，不可复制到产出文件中。
- schema 模板中的 `<context>`、`<rules>` 占位符表示"Agent 理解后填入内容"，而非"复制到输出"。

---

## Cache Awareness（缓存感知原则）

本项目的 API 调用基于 DeepSeek 的 prefix-cache 机制：
- 缓存命中时 input token 成本降低 98%~99%
- 前缀内容的字节级变化会导致整个缓存失效
- 因此：所有文档、规则、工具定义等静态内容必须保持在 prompt 前缀位置且不修改
- 动态内容（用户问题、检索结果、变化参数）始终放在 prompt 末尾

### 协议稳定性承诺
- 本文档（auto-mode.md）在所有 Agent 中作为共享前缀加载
- 委派协议通过 agent.plan.prompt / agent.build.prompt 注入主Agent（方案A：prompt 隔离）
- 子Agent 不再收到调度者角色指令（消除身份冲突）
- 本文档在 session 运行期间不修改、不重排、不动态注入

---

## Parallel & Batching（并行与批处理规范）

以下规则适用于所有 Agent，是缓存性能优化的关键：

### 并行发出
- 互不依赖的独立工具调用（多个 read、多个 glob、多个不相关的 bash）必须在同一消息中并行发出
- 错误示例：先 glob → 等结果 → 再 read（浪费一轮 API 调用和缓存寿命）
- 正确示例：glob + grep + read 三个独立操作在一轮中同时发出

### 合并批次
- 相邻的同类只读操作合并为批次：glob(pattern1) + glob(pattern2) → 同一消息
- 探索代码库时：先并行 glob（找文件）+ grep（搜内容），结果汇总后再决定下一步
- 不在同一消息中混合读写（写完文件再立即读它是依赖操作，必须串行）

### MCP 工具发现
- 首次加载 Skill 后，工具 schema 已被缓存。后续同类任务不要重复 tool discovery
- PDF 任务始终用 pdf-worker 而非重新加载 pdf-ocr skill

---

## Output Discipline（输出规模控制）

### 分段读取
- 文件 > 2000 行时，用 offset/limit 分段读取，不盲目全量返回
- 优先读取文件头部（理解结构）+ 尾部（查看最新改动），中间按需
- grep 命中 > 50 条时，不逐条读取，而是用更精确的正则缩小范围

### 压缩大输出
- 工具返回 > 3000 字符时，优先截断关键部分而非全量返回（headroom MCP 已禁用 2026-08-12，不再依赖该工具）
- 被截断的关键部分保留位置标记，需要精确内容时再按需读取
- 只在确认需要完整内容时才全量展示

### 只读优先
- 同路径同时有 read 和 glob 两种方式时，优先 glob（更快、更少 token）
- 内容搜索优先 grep（不加载完整文件），确认匹配行后再按需 read

---

## Fault Tolerance（故障自愈协议）

### 工具调用失败
- 第 1 次失败：检查参数格式，重新格式化后重试
- 第 2 次失败：换用替代方案（不同工具/不同路径/不同参数）
- 第 3 次失败：记录到 errors[]，向主Agent 或用户报告，不继续重试

### MCP 连接断开
- 第 1 次失败：等待 3 秒后重连
- 仍失败：跳过该 MCP 工具，用内置工具降级处理
- 不在 MCP 重连上浪费超过 2 次 API 调用

### JSON 解析失败
- 子Agent 返回非 JSON 时，从返回文本中提取 JSON 块（正则匹配最外层 `{...}`）
- 提取失败：将原始文本放入 errors[] 上报，不重复调用子Agent

### 超时处理
- bash 命令超时：先尝试用 timeout 参数延长，再失败则拆分命令为更小步骤
- 网络请求超时：先尝试重试 1 次，再失败则缓存现有结果备用

---

## Session Memory 结构化压缩模板

当 compaction 触发时，将当前会话状态压缩为以下结构化模板（5 段），优先裁剪或摘要超大工具输出，减少不必要的 compaction 触发：

### 压缩决策树（阶梯式）
1. **L1 - 剪枝**：标记/截断超大工具输出（如全量日志、大文件读取），仅保留关键部分与位置标记
2. **L2 - 结构化压缩**：当 L1 仍不足时，触发 compaction，按以下模板输出结构化记忆
3. **L3 - 兜底摘要**：仅当前 2 阶失败或不足时，才使用通用全量摘要

### 压缩模板
| 段 | 内容 | 目的 |
|---|------|------|
| 当前状态 | 任务完成度、等待用户的决策、当前阻塞项 | 恢复会话时快速定位卡点 |
| 关键文件 | 本次修改/创建的绝对路径列表（含变更摘要） | 避免重复 glob/grep 探索 |
| 已做决策 | 用户确认过的选择及理由 | 避免重复询问已决策项 |
| 待解决问题 | 未解决的错误、超时、权限拒绝等阻塞 | 知道接下来该修什么 |
| 经验教训 | 发现的技术陷阱、编码规范、工具使用技巧 | 同类问题不踩两次坑 |

### 规则
- Compaction 后保留 tail_turns=4 的最新回合（当前配置：preserve_recent_tokens=16384）
- 模板中不重复记录已被截断/裁剪的工具输出（引用其位置标记即可）
- 模板的语言与当前会话语言一致（中文会话→中文模板，英文会话→英文模板）
