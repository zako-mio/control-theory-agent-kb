# ADAPTATION-NOTES · opencode 机制处置逐条表（第 3 层）

本文件是 `persona.md` 第十五节的**完整展开**，回答「opencode 的哪条机制被删了、被改了、为什么」。
判据四类：**等价 / 重复 / 增量 / 冲突 / 不可实现**。来源为 `01-调研-提示词化用对照.md` 的 B 表。

> 原则：DSH 已拥有的规则一律**不重复**（重复会产生两套阈值，反而误导）；opencode 引擎绑定内容
> 一律**删除**（在 DSH 无处落地）；只迁移 DSH 没有的**行为纪律增量**，并逐条改写为 DSH 的工具名与机制。

---

## 1. 删除：opencode 引擎绑定，DSH 无对应控制点

| # | opencode 机制 | 源 | 理由 |
|---|---|---|---|
| 1 | 强制门控字面输出 `[GATE] 范围=X 深度=X 操作=X 风险=X → 总分=XX → Daily\|Deep` | `auto-mode.md` | DSH **无变体概念**；保留自评能力，去掉固定字面格式（自评结论写在正文即可） |
| 2 | Daily / Deep 变体切换、TUI 快捷键循环切换、`tui.json` 键位绑定、`PATCH /config` 改变体 | `auto-mode.md` | DSH 只有 `/model` 选择与 route 级 `reasoningEfforts` 映射；模型与推理档由 profile 声明，Agent 不能自行切换 |
| 3 | 决策边界表（≤12 Daily/high，≥13 Deep/max）+ 输出上限列 | `auto-mode.md` | 变体不存在；输出上限由模型 `maxTokens` 声明 |
| 4 | Daily vs Deep 成本对比表（$0.004/请求等） | `auto-mode.md` | opencode 定价与引擎参数，DSH 不适用 |
| 5 | `[COMPLEXITY: X/20]` 跨 plan→build 变体继承 | `agent-protocol.md`、`auto-mode.md` | 无变体继承语义 |
| 6 | DeepSeek 思考模式参数表 + 「思考模式下被忽略的参数」表 | `auto-mode.md` | 归 profile 的 provider `compat.thinkingFormat` / `reasoningEfforts` 声明，不必写进 persona |
| 7 | 会话记忆 5 段压缩模板、L1/L2/L3 压缩决策树、`tail_turns` / `preserve_recent_tokens` 配置 | `auto-mode.md` | DSH 压缩提示词归 `dsh-compaction-basic`，**preset 不可配置**（仅插件可挂 `experimental.session.compacting`） |
| 8 | 浏览器标签页管理、Chrome CDP 通道、`close-chrome-tabs.ps1` | `browser-management.md` | DSH web profile 无该通道 → **整件不适用**（见 PROVENANCE 的「明确未迁移」） |
| 9 | MCP 工具发现纪律（「首次加载 Skill 后不要重复 tool discovery」） | `auto-mode.md` | DSH 工具目录与 schema 由 preset 决定，无该问题；且 MCP 本轮未挂 |
| 10 | 工具结果阈值「>3000 字符截断」、文件「>2000 行分段」、grep「>50 条换正则」 | `auto-mode.md` | **与 DSH 冲突**：DSH 用 `tool-result-pruner`（8192/4096/1024）与 spill 文件，glob/grep 上限 100/250。照抄会产生两套阈值 |
| 11 | opencode 跑在 Bun 上「会读代理环境变量」的联网结论与 `no_proxy` 白名单细节 | `auto-mode.md` | **冲突**：DSH 是 Node/undici，模型 API 与 `web_fetch` **不读**代理环境变量 → 已用 DSH 版替换（persona 第八节第 4 条） |
| 12 | 命令级权限：`bash` 前缀白名单、`read` 对 `auth.json`/`opencode.env` 的 deny、`edit` 跨工作区 allow 列表、`external_directory` | `opencode.jsonc` | **不可实现**：DSH 只有档位级 sandbox（read-only / workspace-write / danger-full-access），无命令级判定 → 标注不保真，见 README §4 |
| 13 | `python -c` 的 runtime 硬 deny、「edit 不可用时切 Build 模式」 | `agent-protocol.md` | DSH 无命令级 deny、无 Build 模式切换 → 降级为纪律约束（persona 第四节第 6 条已注明） |
| 14 | `allowed-tools` frontmatter 键 | 13 个 openspec 系 skill | **两侧都不生效**（惰性键）→ 派生副本原样保留，但不得据此推断工具受限 |

## 2. 改写：名称/机制映射（DSH 有对应物）

| opencode | DSH | 处置位置 |
|---|---|---|
| `task(subagent_type)` | 7 个具名 worker：`subagent` / `oc_explore` / `oc_architect` / `oc_requirement` / `oc_search` / `oc_reflection` / `oc_pdf` | persona 第二节；bundle 的 `delegation` 组 |
| `question` | `ask_user_question` | persona 第九节 |
| `todowrite` | `todo_write` | 派生 skill 与 persona |
| `webfetch` / `websearch` | `web_fetch` / `web_search` | persona 第十一节 |
| `read`（图片） | `read_image` | persona 第十四节 |
| `plan_exit` | `exit_plan_mode` | plan-mode section |
| `architect-worker` / `requirement-discovery-worker` / `search-worker` / `pdf-worker` / `exploration` / `reflection-worker` | `oc_architect` / `oc_requirement` / `oc_search` / `oc_pdf` / `oc_explore` / `oc_reflection` | persona 第十二/十三/十四节；bundle worker 行 |
| `/arch <任务>` | **点名 `architecture-judgment`**（DSH 无该命令，命令注册需插件） | persona 第十二节；派生 skill 内已同步改写 |
| `/rd <需求>` | **点名 `requirement-discovery`** | persona 第十三节；派生 skill 内已同步改写 |
| `search-agents.py` / `search-agents.ps1` 角色检索 | 按具名 worker 的 description 选择；需要角色时由子 Agent 加载 `agency-agents` skill 自取 | persona 第二节（删除检索脚本步骤） |
| 子 Agent `task: deny`（不自委派） | `maxDepth: 0` | bundle worker 行 |
| 子 Agent `bash` 白名单（如 `git status *`） | `toolFilter.deny` 整条禁掉 shell（fail-closed，决策 D3） | bundle worker 行；**损失**：worker 失去 git 只读与门控自跑能力 |
| 门控脚本由 worker 自跑（0916 D-01「打通生产者-验证者」） | **主 Agent 串行执行**（D3）；本机需 `danger-full-access` 档 | persona 第十二节；派生 skill 的迁移适配注记 |
| 子 Agent 通过父会话间接发问 | 子 Agent **无发问通道**，问题结构化回传 `errors`/`warnings` | persona 第三节 |
| 全局指令注入（`instructions/*.md` 注入所有会话） | preset `persona` 行承载（DSH 侧 preset persona **遮蔽** host `system-prompt.personaPrefix`） | bundle 的 `persona` 行；**已取证**：`verify_persona_scope.py`（2026-10-11 第二轮，三条命题 + 5 个负向用例，接入 `verify_bundle.py` check 13） |

## 3. 保留（增量，DSH 未覆盖）

| 机制 | 源 | 说明 |
|---|---|---|
| 调度者定位 + 复杂度自评四维表（各 1-5，≥13 高档） | `auto-mode.md` | 去掉字面门控格式与变体，保留判据 |
| 委派 5 步流程 + 子 Agent prompt 模板 + 结构化 JSON 返回字段 | `agent-protocol.md`、`auto-mode.md` | 工具名改 DSH |
| 子 Agent 身份约束（不委派 / 禁改记忆 / 无发问通道） | `auto-mode.md` | 补第三条 |
| 编码安全 5 条（优先 edit/write、独立 .py、中文 JSON 回读、stdout reconfigure） | `agent-protocol.md` | 保留；注明 DSH 侧非硬 deny |
| 验证与证据 / 路径本地化 / 元数据不入输出 | `auto-mode.md` | 保留；「从磁盘读」改为强调**依赖文件** |
| 故障自愈 3 次阶梯 + 子 Agent 非 JSON 处理 | `auto-mode.md` | 逐字保留 |
| 缓存与并行各一句 | `auto-mode.md` | 压缩保留 |
| 留档规范（5 段 + 完整性/询问/路径三门控 + 双版本 + HTML 质量门控） | `agent-protocol.md` | 保留；发问工具改写 |
| 搜索行为（先搜后答 / 多源交叉验证 / 信源分级 / 时效性） | `search-behavior.md` | **整节逐字保留** |
| 架构行为（规模三问 / 知识分层 / 产出契约 / openspec design 门控） | `architecture-behavior.md` | 保留；命令与 worker 名改写 |
| 需求发现行为（定档前置 / 边界防抢词 / 验证优先 V1–V4） | `requirement-discovery-behavior.md` | 保留；`$TIER_TOOL` 展开为绝对路径 |
| 视觉与出图归位（diagram-lite 档位 / 无代看子 Agent） | `agent-protocol.md` | 保留；`read_image` 改写 |

## 4. 不重复（DSH 自带提示面已覆盖，一律不写进 persona）

按 `01` 号文件 §A2 的清单逐条排除：`[exit code: N]` 检查与失败先查、`read` 读文本与 offset/limit 续读、
改前先读（`fs-observation-policy` runtime 强制）、`glob` 代替 find、`grep` 代替 shell grep、
后台 job 追踪与收尾、web 结果不可信与 markdown 链接引用、独立委派同一消息并行发起、
计划模式全套纪律（含 `exit_plan_mode` 唯一末调用）、技能目录「先加载再执行」、
工作目录/沙箱/审批/子 Agent 委派 4 个 runtime context、输出尾部截断与 spill、glob/grep 命中上限。

## 5. 已知缺口（本轮不实现）

| 缺口 | 原因 | 后置方案 |
|---|---|---|
| 命令级权限规则引擎 | DSH 只有档位级 sandbox | 权限插件（`tools/pre-execute` 纯函数规则引擎 + `approval/request` 关联应答），见 `03-计划-迁移实施.md` §12 |
| `/arch` `/rd` `/reflection` 斜杠命令 | 命令注册需插件 | 本轮以「点名 skill」替代 |
| `pdf-reader` MCP | 避免 host 平面污染（决策 D5） | 本轮 `oc_pdf` 走 `read` + OCR |
| 逐 skill 的 sandbox 档位 | 子 Agent 继承父 preset 权限档，不能逐子 Agent 设 sandbox | 子 Agent 的 shell 一律 deny（fail-closed） |
