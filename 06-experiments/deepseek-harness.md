# 实验记录：DeepSeek Harness (dsh v0.2.1-alpha.2) — 标准实验组

> 产品：deepseek-harness `v0.2.1-alpha.2`（cordis 插件装配；2026-10-09 发布，commit `d743267`）
> 实验日期：2026-09-07（**历史块**，v0.1.1-rc.2 口径）／ 2026-10-11（**本轮增量**，0.2.1 口径）
> 实验方式：**源码级可逆故障注入点分析**（不实机破坏，符合契约红线「可逆+受控」）
> 契约约束：仅分析可逆注入点，不改源码文件，不实机运行破坏实验

## 版本沿革

| 项 | 值 |
|---|---|
| 本轮基线 | `dsh v0.2.1-alpha.2`（2026-10-09 发布，commit `d743267`，`package.json` version `0.2.1-alpha.2`） |
| 上轮基线 | `dsh v0.1.1-rc.2`（2026-08-21 发布，本实验原记录口径） |
| 跨度 | **21 个预发布 tag**（`0.1.2-alpha.1` … `0.2.1-alpha.2`） |
| 装配口径 | 三层：① base bundle `packages/bundle/base/cordis.patch.yml`（**95 条 `- id:` 装配行**）；② web-app bundle `packages/bundle/web-app/cordis.patch.yml` + `presets/*.patch.yml`；③ profile patch。旧记录「76 核心 + 36 外部 seam」为**分列口径**，与本口径**不可直接相减** |
| 上游 | 仓库 `https://github.com/deepseek-ai/deepseek-harness`；文档站 `https://deepseek-harness.github.io/deepseek-harness/`；`npx @deepseek-ai/dsh web`；`README.md:13` 明示 **Public APIs are pre-stable** |

> 本页**保留全部既有实验结论与观测数据（未重跑、未改写）**，见文末 `## 历史块：v0.1.1-rc.2 期结论`；本轮仅在其后追加「0.2.1 期可逆注入点增量」。

## 实验设计框架

dsh 是 cordis 插件，每个实验场景映射到可逆的源码注入点（guard 目录的插件/投影），通过「修改 guard 配置 → 观察行为 → 回滚」实现。以下为各场景的**可逆注入点分析**（指出改哪里、会触发什么行为、如何回滚）。

| 场景 | 可逆注入点 | 触发行为 | 控制论环节 | 回滚方式 |
|------|-----------|---------|-----------|---------|
| 正常基线 | 无（默认装配） | 三瀑布执行 | 设定值+执行 | — |
| 故障注入 | `guard/timeout-policy` 设 `timeoutMs=0` | 工具超时→`TOOL_TIMEOUT` | T 环看门狗 | 改回 timeoutMs |
| 上下文污染 | `compaction-basic` / `token-meter` 调高压力阈值 | 触发压缩 | M 环信息滤波 | 改回阈值 |
| 超长循环 | `guard/repeat-tool-reminder` 阈值改 1 | 同工具同参达阈值→提醒 | R 环（软 D 项） | 改回阈值 3/5/8 |

## 各场景源码证据

### 场景1：正常模式（基线）
- 装配：`packages/bundle/base/cordis.patch.yml`（v0.1.1-rc.2 口径：76 核心插件；0.2.1 口径：95 条 `- id:` 装配行）
- 执行：`packages/core/tools` 的 pre-execute→execute→post-execute 三瀑布
- 控制论：设定值 r 由 plan-mode/goal/todo 生成，T 环三瀑布执行

### 场景2：故障注入 — 工具超时（T 环看门狗，**可逆注入点**）
- **注入点**：`packages/guard/timeout-policy/src/index.ts` 工具声明 `timeoutMs`，接 `exec.signal`，超时映射为 `TOOL_TIMEOUT`。
- **源码证据**：
  ```
  /**
   * Cooperative tool-call timeout enforcer. A tool declares `timeoutMs` and
   * promises to honor `exec.signal`; this wrapper arms that deadline and maps its
   * own expiry to `TOOL_TIMEOUT` without racing or abandoning the tool promise.
   */
  export const TOOL_TIMEOUT = 'TOOL_TIMEOUT'
  ```
- **触发行为**：工具超时 → 返回 `TOOL_TIMEOUT` 结构化结果（不是抛错）→ 回灌模型（R 环纠偏）。
- **控制论**：KT-ctrl-034 饱和/看门狗——协作式超时，非竞速硬杀。
- **回滚**：延长 `timeoutMs` 即恢复。

### 场景3：上下文污染（M 环信息滤波，**可逆注入点**）
- **注入点**：`packages/llm/token-meter`（回放感知 token 计量）+ `packages/compaction/compaction-basic`（压力压缩）+ `tool-result-pruner`（裁剪）。
- **触发行为**：token 压力超阈值 → `agent/pre-step` 触发压缩 → 先裁工具结果，再 LLM 摘要（复用 KV 前缀缓存），`CONTEXT_WINDOW_EXCEEDED` 时溢出恢复。
- **控制论**：KT-ctrl-011 卡尔曼更新 + KT-ctrl-014 信息降维——只保留增量信息。
- **回滚**：调低压力阈值即恢复。

### 场景4：超长循环（R 环软 D 项，**可逆注入点**）
- **注入点**：`packages/guard/repeat-tool-reminder`，阈值 3/5/8（连续同参调用同一工具），只 enrich 注入提醒，**不 veto**（软 D）。
- **触发行为**：同工具同参连续超阈值 → 注入提醒到提示词（趋势预警）。
- **控制论**：KT-ctrl-023 微分 D（趋势预判）——但只提醒不硬停。
- **回滚**：改回阈值或移除插件。

## 0.2.1 期可逆注入点增量

> 口径：仅新增/变化的注入点；**不改动上述 1–4 号既有场景的观测数据**。全部为源码级定位，未实机运行。

| # | 场景 | 可逆注入点（源码路径） | 触发行为 | 控制论环节 | 回滚方式 |
|---|------|---------------------|---------|-----------|---------|
| 5 | **PTC 运行时切换** | `packages/core/tools/src/index.ts:672`（`ToolPresentationMode = 'native' \| 'ptc'`）+ `:812`（union 仅二者，`both` 被拒）；运行时 provider `packages/ptc-runtime/ptc-runtime-node`（`ctx.ptcRuntime` seam） | 由 `native` 切到 `ptc`：原生工具 schema 从请求中**消失**，模型只见 `run_code` + SDK 说明；每次调用起**受管 Node 进程**，宿主函数以 async binding 注入，受**同一套平台沙箱策略**约束（deadline / 输出上限 / V8 heap limit） | T 环跨语言执行（KT-ctrl-030/034） | 把 `mode` 改回 `native`；或卸载 `ctx.ptcRuntime` 实现（`ptc` 模式缺运行时会**装配期报错**，非静默降级） |
| 6 | **sandbox fail-closed** | `packages/sandbox/sandbox-local/README.md:71`（runner 链：`linux` bwrap→Landlock / `darwin` Seatbelt / `win32` ACL restricted-token；另有 `sandbox-ssh`）+ `docs/subsystems/permission-presets.md:73`（preset 打包 sandbox+approval） | 平台无 runner 链、或链上**所有探针失败** ⇒ provider 不可用，在 `confine()` **fail-closed**；请求受限模式而无法建立约束 ⇒ `SANDBOX_UNAVAILABLE`。⚠️ **本机 bubblewrap/Landlock 均不可用 ⇒ 本机实际走此分支（环境事实）** | T 环鲁棒稳定（KT-ctrl-031）+ 限幅（KT-ctrl-034） | 恢复可用后端即恢复；或以 `permission preset` 降/升档（log-only `permission/preset` 事件 + 两个 knob 事件） |
| 7 | **auto-review opt-in** | `packages/experimental/auto-review/src/index.ts:684-714`（挂 `tools/pre-execute`，仅当 preset == `AUTO_PRESET` 时介入，`:689`）+ `:41-62`（`REVIEW_POLICY`）；**base bundle 未装配** | 装配后：单个待执行工具调用交**独立 LLM 审查器**做 low/medium/high 风险分级 + allow/deny；allow **替代人工审批**并立即以完整主机权限执行；`high` 恒 deny 且不可被人类/父级指令降级；deny 时若 `approval.overrideOf === 'never'` 直接 `denied` | E 环（**局部闭环的审批传感器**，评「可授权性」而非「目标达成度」） | 从装配中移除该包即回到默认审批路径；**零残留**（不写上下文、不改历史） |
| 8 | **repeat-output-guard cancel** | `packages/guard/repeat-output-guard/`；**base bundle 默认启用**：`packages/bundle/base/cordis.patch.yml:454-461`（`mode: cancel`、`windowLines: 400`、`ngram: 5`、`minCount: 8`、`minChars: 2000`） | 实时输出流中一段短行序列在滑动窗口内重复达阈值 ⇒ `agent.cancel({kind:'hook'})`，在塌缩**早期**中止该次尝试（而非烧完输出预算）；**KV cache 无影响**（不写上下文） | R 环锐化 D 项（**检测—停机**，非「算误差—修正」） | `mode: observe`（只记日志不取消）或调高 `minCount`/`windowLines`/`minChars`；⚠️ README:136 明写 **"Stops, never repairs"**——已持久化的退化文本仍在历史中并被重放，清除需适配侧重放策略或压缩触发，**本包不实现** |

**0.2.1 增量结论**：新增注入点呈现两条清晰趋势——(a) **执行器侧**从「配置开关」扩展到「**执行面选择**」（`native|ptc` 是语义级切换，且缺运行时即装配期失败，属 fail-fast 而非静默降级）；(b) **安全侧**统一走 **fail-closed**（sandbox 不可用即拒绝），而 **E 环的独立审查器仍是 opt-in**、R 环新增的 guard 是 **cancel-only（只停机不修复）**。⇒ 可逆注入点的**模块化容错性**（改配置即注入扰动、回滚即恢复）在本轮继续成立，且**新增点的回滚成本全部为「改回配置/移除插件」量级，无不可逆副作用**。

## dsh 标准实验组结论

| 场景 | 控制论环节 | 可逆注入点 | 行为 | 强弱项 |
|------|-----------|-----------|------|-------|
| 1 正常 | 设定值+执行 | 默认装配 | 三瀑布执行 | 基线 |
| 2 超时故障 | T 环看门狗 | timeout-policy | TOOL_TIMEOUT 回灌 | 强（协作式超时） |
| 3 上下文污染 | M 环信息滤波 | token-meter+compaction | 压力压缩 | 强（只留增量） |
| 4 超长循环 | R 环软 D | repeat-tool-reminder | 注入提醒 | 弱（只提醒不否决） |
| 5 PTC 切换（0.2.1 新） | T 环跨语言执行 | `tools` mode + `ctx.ptcRuntime` | schema 收敛为 `run_code`；受管进程执行 | 强（fail-fast：缺运行时装配期报错） |
| 6 沙箱不可用（0.2.1 新） | T 环鲁棒稳定 | sandbox-local runner 链 | `confine()` fail-closed / `SANDBOX_UNAVAILABLE` | 强（不可用即拒绝，不静默降级） |
| 7 auto-review（0.2.1 新） | E 环审批传感器 | `experimental/auto-review`（opt-in） | 单动作风险分级 → allow 替代人工审批 / deny | 中（真独立 LLM 审查器，但评授权非评达标，且默认关闭） |
| 8 输出塌缩（0.2.1 新） | R 环锐化 D | repeat-output-guard（默认启用） | `agent.cancel({kind:'hook'})` 早期停机 | 中（只停机不修复，已落历史文本仍重放） |

**整体控制论结论（0.2.1 口径）**：dsh 的**可逆注入点设计优秀**——把看门狗/限幅/压缩/提醒/沙箱/输出塌缩全部沉淀为 guard 或独立插件，实现"改插件配置即注入扰动、回滚即恢复"。这体现了**模块化的容错性**。本轮该性质继续成立并扩展：新增注入点全部支持配置级回滚，其中 PTC 与 sandbox 均**fail-fast/fail-closed**（宁可拒绝也不静默降级）。但 **E 环仍无「目标达成度」的独立 validator**——`experimental/auto-review` 是真正的独立 LLM 审查器，却评的是**动作可授权性**且**默认未装配**；R 环新增的 repeat-output-guard 是 **cancel-only**。⇒ R 环仍只能对「感知到的失败」纠偏，放大的是错误信号而非误差信号。**印证 phase3 画像：T 环最强（本轮领先幅度扩大）、E 环最弱（判定记为「部分修正」，实质结论不变）。**

---

## 历史块：v0.1.1-rc.2 期结论

> **保留原因**：本节逐字保留 2026-09-07 在 `v0.1.1-rc.2` 口径下完成的实验记录与观测数据（**未重跑、未改写**），供跨版本对照；**不得静默删除**。上方 1–4 号场景即该期原始观测，此处汇总其结论原文。

**旧整体控制论结论（原文）**：dsh 的**可逆注入点设计优秀**——把看门狗/限幅/压缩/提醒全部沉淀为 guard 目录的独立插件，实现"改插件配置即注入扰动、回滚即恢复"。这体现了**模块化的容错性**。但 E 环无独立 validator（全库 grep 无 critic），R 环只能对「感知到的失败」纠偏，放大的是错误信号而非误差信号。印证 phase3 画像：T 环最强、E 环最弱。

**旧场景结论表（原文）**：

| 场景 | 控制论环节 | 可逆注入点 | 行为 | 强弱项 |
|------|-----------|-----------|------|-------|
| 1 正常 | 设定值+执行 | 默认装配 | 三瀑布执行 | 基线 |
| 2 超时故障 | T 环看门狗 | timeout-policy | TOOL_TIMEOUT 回灌 | 强（协作式超时） |
| 3 上下文污染 | M 环信息滤波 | token-meter+compaction | 压力压缩 | 强（只留增量） |
| 4 超长循环 | R 环软 D | repeat-tool-reminder | 注入提醒 | 弱（只提醒不否决） |

**旧装配口径（原文）**：`packages/bundle/base/cordis.patch.yml`（76 核心插件）——⚠️ 与 0.2.1 的「95 条 `- id:` 装配行」**口径不同，不可直接相减**（旧为 base 与 seam 分列统计）。

> ⚠️ 契约遵守确认（两期一致）：本次实验为**纯源码分析**（未实机运行、未修改任何源码/配置文件、无破坏）。可逆注入点为理论定位，实际注入需在隔离环境执行且可回滚。
