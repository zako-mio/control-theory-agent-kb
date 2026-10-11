# dsh v0.2.1-alpha.2 五环复核判定（证据包摘要）

> 来源：三个只读子 Agent 的源码级/文档级取证（oc_explore，2026-10-11）。路径均为 `file:line` 可定位。

| 环 | 判定 | 关键增量（源码依据） |
|---|---|---|
| **SP 设定值** | **维持** ⭐强 | goal 权威/阈值硬校验（`packages/goal/tool-goal/README.md:55`：create/edit/pause/resume 须顶层 agent 当前轮直人消息；autonomous blocked 须连续 3 轮 `blockedAfterConsecutiveRounds`）；plan/mode 改 log-only 整值替换（`docs/subsystems/plan.md:11`）；**schedule 四工具把时间变成一等设定值**（`docs/subsystems/schedule.md:265`，cron/IANA 时区，子会话被拒） |
| **E 评估** | **部分修正**（实质结论成立） | 新增 `packages/experimental/auto-review/`：独立 LLM 审查器，`REVIEW_POLICY` 自我定位「final authorization reviewer for exactly one pending tool call」（`src/index.ts:41-62`），挂 `tools/pre-execute`（:684-714）⇒ 评的是**动作可授权性**而非**目标达成度**，且 base bundle 默认未装配。telemetry 族＝资源/性能镜像（`docs/subsystems/session-telemetry.md:60`、`product-telemetry.md:5-7`）；`verify-*` 脚本族＝**开发期门控**；`workspace-changes` 只记录事实（`docs/subsystems/deliverables.md:45-60`）；message-feedback 仍 log-only |
| **T 执行** | **维持** ⭐⭐最突出 | 呈现模式收敛 `native \| ptc`（`both` 被拒）+ PTC 真运行时（`packages/ptc-runtime/README.md:30`）；沙箱后端族 bwrap→Landlock / Seatbelt / Windows ACL / SSH，`enforcement` full/partial，不可用即 `SANDBOX_UNAVAILABLE` **fail-closed**（`packages/sandbox/sandbox-local/README.md:71`）；permission preset 打包 sandbox+approval 并可派生 custom/Auto（`docs/subsystems/permission-presets.md:73`）。⚠️ 本机无可用后端 |
| **M 记忆** | **维持** ⭐次强（增量最大之一） | `session-query-sqlite` FTS5 派生索引（`packages/session-query/session-query-sqlite/README.md:61`：确定性排序 + generation-bound cursor，语料变化即 `STALE_CURSOR`）；五只读工具（`docs/tool-catalog.md:39`）；`SESSION_FORMAT_VERSION=4`（`packages/core/session/src/types.ts:89`）；skill 注册表 host+per-scope（`docs/subsystems/skills.md:13`）；压缩恢复改「generation 前进才重试」（`docs/subsystems/compaction.md:101`）。**仍无置信度/协方差** |
| **P 规划** | **维持** ⭐强（增量最大之一） | 委派统一为**托管式 activations**（`docs/upgrade-guide/v0.2.1-alpha.1/subagent-activations/guide.md:12`）；provider 契约 **6 个**（spawn/fork/acp/codex/claude-code/dsh-sdk；`docs/subsystems/subagent.md:326`）；**新增全局控制面** `send_message`/`interrupt_agent`/`list_agents`（`packages/subagent/tool-subagent-control/README.md:12`）；**Agent Teams（实验）** 持久 roster + 任务 DAG + 直投 inbox（`docs/subsystems/agent-team.md:58`，默认关闭）。**规划时域仍由配置固定** |
| **R 反思** | **维持** ⚠️中弱 | retry 对模型不可见（`packages/llm/llm-retry/README.md:50-58`）；hooks deny→steer（`packages/experimental/hooks-claude-code/README.md:89`）；repeat-tool-reminder 只 enrich（`packages/guard/repeat-tool-reminder/README.md:91`）；**新增 `repeat-output-guard`**：输出塌缩即 cancel，但 README:136 明写「**it never rewrites a message, and a trip is stopped, not repaired**」；`packages/core/agent-loop/README.md:220`「No built-in turn budget」。**无 self-critique、无 e=r−y** |

## 结论
- 基线（v0.1.1-rc.2）的实质判断**仍成立**：E 环无「目标达成度」独立测量、R 环无内源误差修正、T 环最强。
- 唯一需修正处：**auto-review** 是真实存在的独立 LLM 审查器（若按「有无独立审查器」的字面读，原结论会被部分推翻）；但按「是否测量目标达成度」的口径，结论不变 ⇒ 记为**部分修正**，并在画像中显式写出以免读者以为漏检。
- 装配口径修正：基线记「76 核心 + 36 外部 seam」，当前 `packages/bundle/base/cordis.patch.yml` 的 `- id:` 条目 **95 行**（源码实测；另一子 Agent 记 94 行，差异已注明）——**口径不同不可相减**，画像改为「base bundle 装配行 + web-app bundle + profile patch」三层描述。
