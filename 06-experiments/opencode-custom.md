# 实验记录：opencode-custom（自改造 opencode）— 标准实验组

> 产品：opencode-custom = opencode v1.18.29 内核 + 用户级装配层（9 agents / 6 MCP / 35 skills 加载 / Reflection 系统 / GATE 协议）
> 实验日期：2026-09-09　实验方式：`opencode run` 非交互 + 隔离 config 副本（XDG_CONFIG_HOME/XDG_DATA_HOME/XDG_STATE_HOME/XDG_CACHE_HOME 全指向 `/tmp/opencode/`）+ 非 build/plan 代理，规避 Reflection 自检
> 契约约束：`00-contract/contract.md` §7 实验红线三清单（仅可逆 + 受控注入；禁改记忆系统文件；隔离区 `/tmp/opencode`）+ §9 五字段标准记录模板
> 安全校验结论：`MEMORY.md` sha256 前后完全一致（`17581ee40ddf4fe97c0577071da23bec79294ff0835b37a818890b03dcd0d63d`）；`pending.json` 在本实验窗口内被**并发 reflection-worker 会话**（`ses_f7de57ae0ffeXlk1JxAFMSxQbg`，非本实验）由 `30adad4e…` 改为 `60b5e799…`，本实验会话对 pending.json **仅只读**、未写（证据见实验3）
> 降级说明：实验4 简单任务 [GATE] 为实机观测、COMPLEXITY 继承为静态验证（因规避 pending.json 写入未走 plan/build 实机链）

---

## 实验1：正常基线（纯推理）

**实验设计**：控制组无；实验组为隔离 config（无 instructions / 无 MCP / 无 skills）下 `--agent orch` 的纯推理任务；观测指标为输出正确性、收敛轮数、token 与成本、是否触发外部协议。

**执行数据**：命令 `opencode run "用一句话解释什么叫负反馈控制" --agent orch --format json`；环境 XDG_CONFIG_HOME=/tmp/opencode/iso-config，模型 deepseek/deepseek-v4-flash，opencode 1.18.29；时间戳 2026-09-09 01:40:34→01:40:40（耗时 5.77s），会话 ses_f7de47c42ffeNikJxKaLVIXn4D。

**观测结果**：输出为「负反馈控制是指系统通过检测输出与期望值的偏差，并将该偏差反向作用于输入以减小误差，从而自动维持输出稳定的控制方式。」；正确性 ✅（单句、定义完整、无冗余）；1 轮收敛，无工具调用，无外部协议介入。

**量化指标**：计划进度偏差 1/1 步（无偏航）；token total 5645（input 5537 / output 32 / reasoning 76）；成本 $0.000805；反馈信噪比高（一次直出）。

**控制论解读**：属于设定值 r + 开环直出（E 环由人判断达标）；控制律为单次前馈（feedforward），无反馈回路。基线证明隔离态下内核可独立完成任务，为后续实验提供无协议干扰的参照系。

---

## 实验2：专职 worker 委派（P 环强化）

**实验设计**：控制组为实验1（单 agent 直出）；实验组在隔离 config 定义 orch(primary) + general/explore(subagent) 且 `subagent_depth=2`，用一次 prompt 要求同一消息内并行发出两个 task；观测指标为是否委派、是否并行、委派链深度、聚合正确性、轮数。

**执行数据**：命令 `opencode run "请并行委派两个子任务：①委派 general 计算 17×23；②委派 explore 统计 /tmp/opencode 条目数……" --agent orch --format json`；时间戳 01:40:43→01:40:57（14.49s）；父会话 ses_f7de45b7affeIfMveMoZBV5ckG；委派链 orch → task(general)=ses_f7de44e21ffecfmA6NzkdnZHO0 / task(explore)=ses_f7de44b12ffergneqvHoFo2sNK。

**观测结果**：事件序列为 `step_start → text → tool_use(task)×2 → step_finish → step_start → text(聚合) → step_finish`；两个 task 调用在同一步（同一消息）发出（call_00…/call_01…），并行执行且均 status=completed；聚合结果为 general 返回 17×23=391、explore 返回 /tmp/opencode 直接条目 29 个。另跑 exp2b 验证嵌套委派：orch → general → explore 三级链，explore 计算 5+5=10 并逐级回传，证明 `subagent_depth=2` 生效。

**量化指标**：并行委派 2/2 task 同轮发出（并行度=2）；轮数 2 步（委派 1 步 + 聚合 1 步）；token total 12777 / reasoning 94 / 成本 $0.000305；exp2b 嵌套链实测深度 3 层（depth 0→1→2），token 11776 / 成本 $0.000143。

**控制论解读**：属于 P 环（分层控制/慢-快双速）——主 agent 做慢规划（分解+路由），worker 做快执行；控制律为任务分解 + 并行执行器阵列，`subagent_depth=2` 是执行器递归深度限幅（T 环约束 P 环展开）。装配层把单体内核扩展为可并行、可嵌套的分层执行器，P 环由「提示词约定」升级为「runtime 硬支持（task 工具 + depth 限幅）」。

---

## 实验3：Reflection 闭环（R 环反转，只读验证）

**实验设计**：对 Reflection 系统状态机做只读验证，不写入 pending.json；观测指标为三态计数、状态迁移、四层数据结构、内核是否内置 R 环。

**执行数据**：只读读取 `~/opencode/archive/Reflection/pending.json`；静态源为 opencode.jsonc 的 build/plan prompt 内「Build 末尾 Reflection 写入」+「Reflection 自检规则」、`command/reflection.md`、reflection-worker agent 定义（opencode.jsonc L110）；时间戳 01:41 快照，文件在 01:40:36 被并发 reflection-worker 会话 `ses_f7de57ae0ffeXlk1JxAFMSxQbg`（日志 run=70b44a03）写入。

**观测结果**：meta 三态为 waiting_count=33 / processing_count=2 / done_count=2（快照时刻）；状态机为 `waiting →（build 自检置 processing）→ reflection-worker 处理 → done →（/reflection 人审 yes/edit）→ MEMORY.md`；每 cycle.layers = {layerA(GATE/complexity/decisions)、layerB(子Agent JSON)、layerC(MEMORY.md 快照)、layerD(留档报告)}；内核侧 `opencode agent list` 无 reflection 内置 agent，reflection-worker 由装配层 config 定义；安全证据为日志中 pending.json 的 edit 权限全部来自 reflection-worker 会话 `ses_f7de57ae0ffe…`，本实验会话 `ses_f7de57eec…`（agent=general）对 pending.json 仅命中 `permission=read`，未命中 edit。

**量化指标**：待处理积压 33 waiting（异步队列，与主流程解耦）；闭环层级为内核 0 个内置 R 环 agent，装配层 +1 reflection-worker + 1 `/reflection` 命令 + 1 pending.json 队列；人审门控要求 done→MEMORY.md 需 yes/edit 显式确认（写入签名 `[src: cycle_id]`）。

**控制论解读**：属于 R 环（反馈/积分环节），呈现**R 环反转**——内核弱 R（无独立 Critic/反思），装配层补齐异步慢 R 环；控制律为误差（任务经验）不即时回灌，而是入队 pending.json → 延迟批处理 reflection-worker → 人工门控转正，属积分/离散采样反馈，牺牲时延换稳定与去噪。opencode-custom 的 R 环是「外挂式、异步、人审闭环」，用装配层把弱内核 R 补齐为可审计的长期记忆闭环。

---

## 实验4：GATE 门控（协议层）

**实验设计**：在隔离 config 仅注入 auto-mode.md（GATE 协议），以 `--agent gate` 分别跑简单/复杂任务，观测是否输出 `[GATE]`、总分与 Daily/Deep 分派是否一致、runtime 是否硬门控；观测指标为 GATE 输出格式、分派一致性、命中率。

**执行数据**：简单任务 `opencode run "计算 2+2 等于多少" --agent gate`（XDG_CONFIG_HOME=/tmp/opencode/iso-gate）；复杂任务 `opencode run "设计一个跨 5 个模块的重构方案……架构级论证" --agent gate`；静态源为 auto-mode.md L7「MANDATORY GATE」、L26 输出格式、L37-38 决策边界（≤12 Daily / ≥13 Deep）、opencode.jsonc L547 注入 auto-mode.md、build prompt「Variant 继承规则」。

**观测结果**：简单任务仅输出 `4`，**未输出 [GATE]**（协议被模型省略）；复杂任务首行输出 `[GATE] 范围=5 深度=5 操作=4 风险=2 → 总分=16 → Deep`，随后按 Deep 展开架构论证；分派一致性 16≥13 → Deep，与边界表一致 ✅；COMPLEXITY 继承为静态降级验证（auto-mode.md L58 + build prompt 要求 Plan 摘要含 `[COMPLEXITY: X/20]`、Build 继承，本实验因规避 pending.json 写入未走 plan/build 实机链）。

**量化指标**：复杂任务 3 步、tools=[bash,glob,bash,glob]、token total 40753 / reasoning 1264 / 成本 $0.001542；简单任务 1 步、token total 10617 / 成本 $0.001223；协议命中率 复杂 1/1、简单 0/1（模型侧省略）。

**控制论解读**：属于协议层门控（P/E 环的元控制——决定用多大推理预算）；控制律为开环规则 + 模型软执行，runtime 不强制拦截，GATE 是「提示词级」约束而非「看门狗级」硬限幅。GATE 能对复杂任务正确量化并分派 Deep，但简单任务存在漏触发，暴露协议层门控可靠性依赖模型遵循度的稳定性风险（建议将 GATE 缺失纳入 E 环校验或 runtime 提示）。

---

## 实验5：MCP 连通性（T 环扩展）

**实验设计**：用 `opencode mcp list` 枚举 6 个 MCP 的配置与连通状态；观测指标为配置数、connected 数、disabled 数、传输方式。

**执行数据**：命令 `opencode mcp list`（真实 config，只读）；时间戳 01:41；输出保存 `/tmp/opencode/exp/exp5_mcp.txt`。

**观测结果**：共 6 server(s)：pdf-reader ✓connected（`npx -y @sylphx/pdf-reader-mcp@latest`）、drawio ✓connected（`node /mnt/d/Opencode/drawio-mcp-minimal/package/src/index.js`）、vscode-mcp-server ○disabled、amap ○disabled、drawio-local ○disabled、headroom ○disabled；传输方式为 3 个 stdio（npx/node）+ 3 个 powershell launcher（WSL 下不可达故 disabled）。

**量化指标**：配置 MCP 6 个；连通 2 个（33%）；禁用 4 个（67%）；可用工具域为 PDF 读取与 draw.io 图表。

**控制论解读**：属于 T 环（执行器/工具扩展）——MCP 是外部执行器的即插即用接口；控制律为按需启用 + 状态可观测，disabled 的 3 个是 WSL 不可达的 Windows 侧 launcher（环境约束）而非配置错误。MCP 层提供可观测的执行器拓扑，但跨环境（WSL/Windows）连通性存在硬约束，需环境适配才能全量激活。

---

## 实验6：Skill 加载

**实验设计**：用 `opencode debug skill` 枚举已加载 skills，核对 inventory.json 的 28 skills + 11 legacy_skill 口径；观测指标为实际加载数、路径来源分布、未加载项原因。

**执行数据**：命令 `opencode debug skill`（真实 config，只读），输出保存 `/tmp/opencode/exp/exp6_skills.txt`；时间戳 01:41。

**观测结果**：实际加载 **35** 个，来源为 `skills/` 27 个 + `skill/` 7 个 + 内置 `customize-opencode` 1 个；未加载 4 个 inventory legacy（amap-budget-control / amap-jsapi-skill / amap-lbs-skill / model-switcher），原因其目录内文件名为 `_SKILL.md`（下划线前缀），不满足 opencode 的 `SKILL.md` 命名约定；`_shared` 为共享资源目录、非 skill，不计入。

**量化指标**：加载数 35（27+7+1）；inventory 名义 28+11=39；口径差 39−35=4，均为 `_SKILL.md` 命名不达标，另 +1 内置、−1 `_shared`。

**控制论解读**：属于知识/策略注入层（对 M/E 环的能力扩展）；控制律为静态按需加载（路由式），skill 是可调用的专家策略库。skill 加载机制可靠，inventory 与实载差异可完全用命名约定解释（非缺失），可用于校正 inventory 口径。

---

## opencode-custom 标准实验组结论

**实验组结论表**：
| 实验 | 场景 | 控制论环节 | 结果 | 关键量化 |
|------|------|-----------|------|---------|
| 1 | 纯推理基线 | 开环前馈 | 1 轮收敛 | 5645 tok / $0.000805 |
| 2 | worker 并行委派 + 嵌套 | P 环分层 | 并行 2/2，链深 3 | 2 步 / $0.000305；depth=2 实测 |
| 3 | Reflection 闭环（只读） | R 环反转 | 异步人审闭环 | waiting 33；内核 0 内置 R |
| 4 | GATE 门控 | 协议层元控制 | 复杂命中/简单漏触发 | 16→Deep；1/1 vs 0/1 |
| 5 | MCP 连通性 | T 环扩展 | 2/6 连通 | 6 配置 / 2 connected |
| 6 | Skill 加载 | 策略注入 | 35 加载 | 27+7+1；4 个 `_SKILL.md` 未载 |

**整体控制论结论**：opencode-custom 的本质是「弱内核 + 强装配层」的分层控制器——P 环被装配层显著强化（task 工具 + `subagent_depth=2` 把单体内核扩展为可并行、可嵌套的分层执行器阵列，实验2 实测链深 3）；R 环发生反转（内核无独立反思/Critic，装配层用 pending.json 队列 → reflection-worker → /reflection 人审补齐异步慢 R 环，实验3）；T 环通过 MCP 扩展但受 WSL/Windows 环境约束（实验5，仅 2/6 连通）；协议层门控 GATE 是软约束（复杂任务正确分派 Deep、简单任务漏触发，暴露「提示词级门控 ≠ 看门狗级硬限幅」的稳定性风险，实验4）；隔离实验范式（XDG 隔离 + 非 build 代理）证明装配层协议可被安全分片观测，且内核在无装配时仍能独立完成任务（实验1）。

> ⚠️ 契约遵守确认：本次实验仅在 `/tmp/opencode/` 隔离区执行（隔离 config/data/state/cache + 临时夹具，含 iso-config / iso-gate / backup / exp 子目录），全程使用 `--agent orch` / `--agent gate` 等非 build/plan 代理，**未写入 pending.json、未修改 MEMORY.md**；未做不可逆破坏，未改真实 API 密钥（密钥仅经进程环境注入，未落盘副本）。安全校验：MEMORY.md sha256 前后一致（`17581ee4…`）；pending.json 在本实验窗口内被**并发 reflection-worker 会话 `ses_f7de57ae0ffe…`（非本实验）**从 `30adad4e…` 改为 `60b5e799…`（meta 由 processing 3 / done 1 变为 processing 2 / done 2，仅状态计数迁移、无本实验写入），本实验会话 `ses_f7de57eec…`（agent=general）对 pending.json 仅执行只读 read，opencode 日志（run=70b44a03）可证；本实验未触发 Reflection 自检。清理说明：已删除本次实验的隔离 config/data/state/cache 目录（`/tmp/opencode/iso-*`），保留必要证据日志 `/tmp/opencode/exp/`（各实验 JSON 原始输出 + MCP/skill 清单）与 `/tmp/opencode/backup/`（实验前两文件副本 + pre_sha256.txt），未触碰 `/tmp/opencode/` 内既有的其它文件。
