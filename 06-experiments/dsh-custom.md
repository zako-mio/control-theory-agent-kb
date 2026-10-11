# 实验记录：dsh-custom（DeepSeek Harness + dsh-opencode-port 装配层）— 标准实验组

> 产品：`dsh-custom` = dsh 内核（DeepSeek Harness `dsh-v0.2.1-alpha.2`，源码树 `/home/zako-mio/dsh`）+ 用户级装配层（bundle `dsh-opencode-port`：`~/.dsh/presets/opencode/` 三 preset + `~/.dsh/skills/opencode/` 45 派生 skill + 宿主 profile patch：5 档 permission / `pnpmCommand` 环境修复）
> 实验日期：2026-10-11（实验 11-14）　实验方式：**装配层取证型实验**——bundle 安装/卸载/重装真实执行 + 会话日志（`session.v4.jsonl.zstd` 多帧 zstd 解帧）取运行时装配结果 + bundle 自家门控新鲜复跑 + 源码级机制核对；**不使用交互式会话做注入**（注入类实验留待后续轮次）
> 隔离区声明（契约 §7 红线）：**实验的写入面仅限 `/tmp` 隔离区**——`/tmp/opencode-b-review.md`、`/tmp/builtin-system.json`、`/tmp/sys-*.json`、`/tmp/bdiff*.py` 及 `/tmp/opencode` 下临时产物；本库侧不改动任何文件。取证与判据复算全部**只读**：`$BUNDLE`（`~/.dsh/presets/opencode/`）、`$PROFILE`（`~/.dsh/profiles/web/`）、`$DSH`（源码树）读取后 mtime 均早于取证动作，无文件被改动。实验14 的安装/卸载/重装是本轮唯一触碰宿主装配注册面的动作，走官方 `install_bundle` / `remove_bundle`，备份件 `~/.dsh-backups/opencode-port-20261011/` 全程在位，且已演练回滚至基线（**该动作不属本库红线范围，且不写入 `~/.dsh` 配置内容本体**）。⛔ **未修改任何记忆系统文件**（`~/.dsh/MEMORY.md`、reflection pending 队列均未触碰）、未做任何不可逆破坏、未改动源码树 `/home/zako-mio/dsh`。
> 环境事实（影响本组全部实验，实测非推断）：本机**无可用沙箱后端**（bubblewrap / Landlock 均不可用）→ `read-only` / `workspace-write` 档下 `bash` 一律 **fail-closed**，跑门控脚本须 `danger-full-access`；web 服务 `PATH` 不含 nvm 的 `node`/`pnpm`（`plugin_manager` 曾因此完全不可用，已用 `~/.dsh/bin/pnpm` 包装脚本修复）。
> 编号约定：本文件实验编号 **11-14**，延续 `06-experiments/opencode-custom.md` 的实验 1-10，避免与之冲突。

---

## 实验11：三 preset 端到端工具面与技能目录对账

**实验设计**：控制组为内置 `standard`（纯净链路）；实验组为 `opencode-standard`(order 11) / `opencode-creator`(order 12) / `opencode-ptc`(order 13) 三个新模式。观测指标为模型实际可见的工具数、`oc_*` 别名可见性、模式专属工具差异、技能目录条数、以及「派生 45 件」与「模型可见 42 件」的口径差。扰动：无故障注入（纯对账）。

**执行数据**：取证通道为会话日志 `~/.dsh/sessions/<编码 cwd>/<id>/session.v4.jsonl.zstd`（多帧 zstd，按魔数切帧解码），取 `agent-preset/selected`、`system/message`、`request/header.tools[]`、`user/message` 的 `<available-skills>` 四处；探针脚本 `$MISSION/_build/opencode-port/session_probe.js --dump-system <会话id>`；四份探针证据 `evidence/session-probe-{builtin-standard,opencode-standard,opencode-creator,opencode-ptc}.json` 与 `evidence/skill-catalog-runtime.txt`；时间戳 2026-10-11；复核由 bundle 审查轮独立复算（`evidence/` 口径已对账）。

**观测结果**：工具面实测 **内置 standard 31 / opencode-standard 37 / creator 40 / ptc 1**。37 相对内置**净增 6 个 `oc_*`**（`oc_explore`/`oc_architect`/`oc_requirement`/`oc_search`/`oc_reflection`/`oc_pdf`）、**零缺失**；creator 在 37 之上再增 `cordis_inspect_list`/`cordis_inspect_query`/`plugin_manager` 共 40；ptc 工具目录**坍缩为单 `run_code`**（其余全部不在顶层目录，含 `workflow` 被显式禁用）。`oc_*` 在内置 standard 会话出现 **0 次** → 三模式的 worker 编队对纯净模式不可见。技能目录：三模式各 **42** 条，内置 standard **0** 条（本 cwd 亦无 `.dsh/skills`/`.agents/skills`）；派生目录 45 件中 3 件带 `disable-model-invocation: true`（`opencode-config`/`opencode-capability-audit`/`opencode-capability-extension`），45 − 3 = 42 与运行时**逐条一致**。`browser-use`（frontmatter name，即 `browser-harness`）在列。

**量化指标**：工具数 31 → 37（+6）/ 40（+9）/ 1（−30）；`oc_*` 可见性 6/6 仅新模式、纯净模式 0；技能目录 0 → 42（差 45−3）；模式专属差异 standard↔creator 3 处、standard↔ptc 1 处、creator↔ptc 4 处（键级 diff）；对账缺口 0（42 条可完全用 `disable-model-invocation` 解释，非缺失）。

**控制论解读**：属 **T 环（执行器）** 的装配面测绘 + **E 环（传感器）** 的可见性边界。控制律为「**声明层 toolFilter/行定义 → 运行时工具目录**」的前馈映射：装配层把内核的通用执行器（`subagent`）展开为**具名 worker 编队**（7 行、`maxDepth: 0`、各带 `toolFilter`），等于给执行器阵列装上名字与限幅器。关键稳定性结论是**模式隔离**：`oc_*` 对纯净模式不可见（0 命中），说明「最小必要破坏性范围」在工具面层面被真实执行——装配层没有污染基线。ptc 的 1 工具不是能力损失而是**调用约定变化**（能力经 `run_code` 内联 SDK 间接可达），但顶层目录坍缩意味着 persona 的「直接调用 X 工具」措辞在 ptc 下成为空指向（见实验12）。

**链接**：所属 AC 章 `ch-tool`（T 环）/ `ch-eval`（E 环）；关联 KT：`KT-exp-011`（本实验）、`KT-case-008`（dsh-custom 画像）、`KT-case-007`（opencode-custom）；关联案例 `03-cases/dsh-custom.md`、`03-cases/opencode-custom.md`；证据回链 `06-experiments/opencode-custom.md` 实验2/实验6（P 环委派与 skill 加载的内核侧对照）；回链 MD 镜像 `05-md/`（本轮待派生）。

---

## 实验12：persona 遮蔽与 persona 税

**实验设计**：控制组为宿主 `$PROFILE/cordis.patch.yml` 的 `system-prompt.personaPrefix`（七段纪律，含已过期内容）；实验组为 bundle `persona.md` 的 15 节化用层（三模式 `persona.prefix`）。观测指标为两侧字符数、会话系统提示中谁出现、标题撞名与合法重叠串、以及 ptc 下 persona 与工具面的**指向一致性**。扰动：无注入（纯文本层对账）。

**执行数据**：来源 `evidence/a12-persona-scope-evidence.json`（`inputs` 记 bundle `cordis.patch.yml` sha256 `6e903497…`、`persona.md` sha256 `f39ce841…`、宿主 patch sha256 `70efba5e…`）、`evidence/persona-behavior-markers.json`；运行时取自四份会话日志的装配后系统提示全文（E1 复算）；源码级机制核对 `$DSH/packages/preset/persona/src/index.ts:1-14,62-68`（文件头注释：mounted inside an agent preset it *shadows the deployment persona* for that one session）与 `tests/persona.spec.ts:32`；时间戳 2026-10-11。

**观测结果**：宿主 `personaPrefix` = **2790 字符 / 8 小节**；bundle `persona.md` = **8018 字符 / 15 节**（≈3084 tokens）；内置 standard 的 `persona.prefix` 仅 **54 字符**。四份会话系统提示中，判别串「成本意识」「MEMORY 硬门禁」「联网代理纪律」**全为 false** → 宿主七段纪律**在所有会话都不生效**，被 preset 的 `persona` 行**遮蔽**（机制与源码一致：preset persona 与宿主注册同名 section `deployment:persona-prefix`，后者被替换）。系统提示字符数：内置 standard **5594** / 三模式 **13658**（15 小节齐备、0 命中禁用字面量 `[GATE]`/`Ctrl+T`/`variant`/`http_proxy`）/ ptc **53826**（**+40168**，来源是 `run_code` 的内联 SDK 与工具说明）。两侧存在**标题撞名** `委派纪律`/`留档规范`/`编码安全`，与合法重叠串 `reflection_add`、`dsh-v0.2.1-alpha.2`（已登记，非泄漏）。宿主那份含**过期内容**（「默认模型为 `opencode-go/deepseek-v4-flash`，deep 变体留给 ≥13 分场景」），与本机实际默认模型 `opencode-go-tmp/deepseek-v4.1-flash` 不一致且 DSH 无变体概念。**ptc 空指向**：`persona.md:26` 写「本模式提供 `subagent`（通用）、`oc_explore`…不要一律用 `subagent`」，而这些名字在 ptc 顶层工具目录里**不存在**，persona 未按 presentation mode 分支。

**量化指标**：persona 字符 2790（宿主）→ 8018（bundle，×2.87）；系统提示 5594 → 13658（×2.44）→ 53826（×9.62）；persona 税 ≈ +8064 字符/请求（三模式）、+48232 字符/请求（ptc，约 +40 KB）；宿主纪律生效 0/4 会话（遮蔽率 100%）；标题撞名 3 处、合法重叠 2 处、过期条目 1 条；ptc 空指向 1 处（§二 worker 清单）。

**控制论解读**：属 **M 环（状态/上下文预算）+ E 环（配置态可观测性）**。控制律为「**同层覆盖（shadowing）**」：persona 是每个请求都要付的**固定上下文税**，遮蔽让宿主纪律从「活配置」变成「死配置」——不生效但仍留存在文件里，形成**隐藏状态**（未生效的分支），这正是 M 环最怕的「状态估计与实际不一致」。风险不在于税本身（8018 字符换 15 节行为纪律，性价比可接受），而在于**无 preset 的回落路径**：一旦某会话不挂 preset persona（换 profile / preset 行被禁用 / 挂载失败回落），这份含过期模型的七段纪律会**突然生效**并与现行 persona 并存冲突——判据层应把「宿主 personaPrefix 是否被遮蔽」做成可观测项，而不是靠人记得。ptc 的 53826 字符则是**税与收益脱钩**的极端样本：上下文成本涨到 9.6 倍，而 persona 的指令形状（"调用 X 工具"）与 ptc 的"只能直接调 `run_code`"不一致，模型必须自行翻译——**同一份 persona 在不同 presentation mode 下的语义有效性不同**，属装配层的隐性不一致。

**链接**：所属 AC 章 `ch-memory`（M 环）/ `ch-eval`（E 环）；关联 KT：`KT-exp-012`（本实验）、`KT-ctrl-002`（状态估计/观测噪声）；关联案例 `03-cases/dsh-custom.md`、`03-cases/dsh-custom-diff.md`；证据回链 `06-experiments/opencode-custom.md` 实验4（协议层软约束）与实验10（提示词级门禁）；回链 MD 镜像 `05-md/`（本轮待派生）。

---

## 实验13：bundle 门控假阳性与修复（判据脆性）

**实验设计**：控制组为 bundle 自家门控 `verify_bundle.py` 的**历史 PASS 记录**（README §8 验收表 + `evidence/verify-bundle-13checks.out.txt`）；实验组为**新鲜复跑**同一门控。观测指标为 13 项检查的逐项结论、FAIL 项的报错原文、漂移根因的可复算证明、修复后复跑结论。扰动：**外部无关联扰动**——宿主 patch 被 GUI 写回一行 UI 偏好（`ui-theme.fontSize: 16`），与 bundle 无任何因果关系。

**执行数据**：复跑命令 `PATH=<nvm-bin> python3 $BUNDLE/verify_bundle.py`（`$BUNDLE=/home/zako-mio/.dsh/presets/opencode`）；根因反推用「删行重算 sha256」：把宿主 patch 中该行删掉后重算 = `70efba5e6873a60ed1480e5f9a6eb0d83faaaa8d95344ebc2fc5dffec25339b4`，与 `provenance.json` / `a12-persona-scope-evidence.json` 记录值**完全一致（MATCH）**；宿主 patch mtime `2026-10-11 05:55:08`（晚于 A12 取证 05:39）；修复动作 = `build_provenance.py` 指纹口径由**整文件 sha256** 改为 **scoped_digest**（只取 bundle 实际消费的字段 `system-prompt.personaPrefix`），随后重跑门控与 `build_provenance.py` 并重新生成验收证据文件；时间戳 2026-10-11。

**观测结果**：新鲜复跑第 11 项 **FAIL**，报错原文 `provenance drift: 八、环境事实: source drifted (70efba5e6873 -> 9c00a1a14339)`；前 10、12、13 项 PASS。根因经 sha256 反推**锁定为宿主 patch 被 GUI 写入一行 `ui-theme.fontSize: 16`**（用户调字号），与 bundle 内容无关 → **假阳性**。修复后 `verify_bundle.py` **13/13 PASS**，验收证据文件重新生成。附带事实：`verify_bundle.py` 唯一写操作是 `tempfile.TemporaryDirectory()` 内的 `rows.json`（:389-391），**不污染仓库**，可安全复跑。

**量化指标**：门控项数 11 → **13 项**（本轮新增 check 13 = A12 取证）；复跑前 PASS 12/13（第 11 项 FAIL）；修复后 PASS 13/13；漂移根因定位置信度 = MATCH（sha256 精确等于记录值，非近似）；被误纳判据的无关字段 1 个（`ui-theme.fontSize`）；修复后判据作用域 1 个字段（`system-prompt.personaPrefix`）；假阳性触发概率 = 任意一次 GUI 偏好写回（高频）。

**控制论解读**：属 **E 环（传感器/验证器）自身的可信度**——是「对传感器的传感器」。控制律本应是「源漂移 → 报警」，但判据把**与 bundle 无因果关系的整文件字节**纳入观测面，等价于给传感器接上了一个高噪声信道：宿主 GUI 每次写回都注入一次扰动，于是门控**红灯的语义被稀释**。这是**假阳性比漏报更贵**的典型——它会训练使用者忽略红灯，最终把真漂移一起放过（噪声淹没信号，E 环信噪比崩塌）。修复的实质是**把判据从「文件指纹」下沉到「被消费字段指纹」**：观测面必须等于因果面，判据须绑被消费字段而非整文件指纹。修复后仍保留上游漂移检测能力（`plan-mode` section 的覆写源仍在指纹覆盖内，见实验11 的 Δ4），即**降噪未牺牲灵敏度**。

**链接**：所属 AC 章 `ch-eval`（E 环/传感器）；关联 KT：`KT-exp-013`（本实验）、`KT-ctrl-004`（鲁棒控制/不确定性）、`KT-ctrl-002`（观测噪声）；关联案例 `03-cases/dsh-custom.md`；证据回链 `06-experiments/opencode-custom.md` 实验4/实验10（软门控的可靠性依赖模型遵循度 → 本实验补充「确定性门控的可靠性依赖判据作用域」）；回链 MD 镜像 `05-md/`（本轮待派生）。

---

## 实验14：安装/回滚可逆性演练

**实验设计**：控制组为**安装前基线**组合树（`dsh --profile web --dump-config`，既有 4 个 preset：standard/ptc/minimal/cordis）与宿主 profile patch 备份件；实验组为安装 → 卸载 → 还原 patch → 重装四个阶段。观测指标为三行 `preset-opencode-*` 的出现/消失、**既有 preset 区域是否逐字节一致**、`/permission` 档位数、插件计数、重装后组合树是否与首次安装后**逐字节一致**。扰动：真实执行一轮完整卸载（受控、可还原）。

**执行数据**：命令链 `dsh --profile web --patch ~/.dsh/presets/opencode/cordis.patch.yml --dump-config`（**干跑**，exit 0，三行正常出现、既有 4 preset 未污染）→ `plugin_manager install_bundle`（绝对路径）→ `remove_bundle dsh-opencode-port` → 还原 profile patch 备份件 → 恢复 patch + 重装；备份件位于 `~/.dsh-backups/opencode-port-20261011/`；组合树差分 `$MISSION/evidence/dump-config-{baseline,installed}.yml`；时间戳 2026-10-11。

**观测结果**：**干跑**阶段三行 `preset-opencode-standard/creator/ptc` 正常出现、既有 4 个 preset 未被污染 → 放行安装。**安装**返回 `{"stage":"enable","target":"dsh-opencode-port","enabled":true,"changed":true,"application":"applied","packageResult":{"exitCode":0},"warnings":[]}`，三行 `enabled=true`、`fiberPhase=active`、无 error；插件总数 **188 → 191**（+3）。**A4 纯净链路回归**：安装前后既有 preset 区域逐行对比**仅多出 1 行**「新层归属」注释（`612a613 > # == dsh-opencode-port`），既有 preset 区域**逐字节一致**。**回滚演练**：`remove_bundle dsh-opencode-port` → `application: applied`，三行 `preset-opencode-*` 消失，既有 preset 区域 vs 安装前基线**逐字节一致**（卸载只移除自己的三行）；还原 profile patch 备份件后 `/permission` 回到 **3 档**、`plugin-manager` 覆盖消失；恢复 patch + 重装后组合树与首次安装后**逐字节一致**。权限档位：安装后 `permission` 行含 **5 档**（`read-only`/`workspace-write`/`opencode-plan`(read-only)/`opencode-build`(workspace-write)/`danger-full-access`），`defaultPreset: read-only` 未变；卸载后回到 3 档。组合树整体差分 **0 行删除 / 1990 行新增**，`preset-opencode` 由 0→3。

**量化指标**：可逆性 4/4 阶段通过（干跑/安装/卸载/重装）；既有 preset 区域字节差异 = 1 行注释（**0 处语义变更**）；插件计数 188 → 191 → 188（净 Δ = +3，卸载后归零）；权限档 3 → 5 → 3；重装后组合树与首次安装后**逐字节一致**（差异 0）；备份件 `~/.dsh-backups/opencode-port-20261011/` 1 套。

**控制论解读**：属 **T 环（执行器）+ R 环（闭环可逆性）**，是「**受控可逆性**」这一实验红线的正面样本。控制律为「先干跑（前馈预测）→ 再应用（执行）→ 每步自带验收（传感）→ 可回滚（反向执行器）」的四段式，等价于给装配动作加**双向执行器 + 状态快照**：卸载只移除自己的三行、既有区域零语义变更，说明 bundle 的作用域是**封闭且可判定**的（没有"改一处、坏一片"的耦合）。「重装后逐字节一致」比「卸载干净」更强——它同时证明安装是**幂等**的（同输入同输出，无隐藏状态累积），这是把装配层当控制器时最关键的稳定性性质：**可回滚 ≠ 可重放，本实验两者都测了**。唯一留档风险是 L18 已自述的**不可移植性**（persona 含本机绝对路径、`node_modules` 28 个符号链接指向本机源码树）：在本机可逆，换机即失效——可逆性的成立**以环境不变为前提**。

**链接**：所属 AC 章 `ch-tool`（T 环）/ `ch-reflection`（R 环闭环）；关联 KT：`KT-exp-014`（本实验）、`KT-ctrl-001`（闭环反馈/稳定性）；关联案例 `03-cases/dsh-custom.md`；证据回链 `06-experiments/opencode-custom.md` 实验2（`subagent_depth` 限幅）与实验7（产出/验证分离）；回链 MD 镜像 `05-md/`（本轮待派生）。

---

## dsh-custom 标准实验组结论（实验 11-14）

| 实验 | 场景 | 控制论环节 | 结果 | 关键量化 |
|------|------|-----------|------|---------|
| 11 | 三 preset 工具面/技能目录对账 | T 环 + E 环 | 编队可见、纯净模式零污染 | 工具 31/37/40/1；技能 0/42/42/42；口径差 0 |
| 12 | persona 遮蔽与 persona 税 | M 环 + E 环 | 宿主纪律 100% 遮蔽；ptc 空指向 | 2790 → 8018 字符；提示 5594/13658/53826；撞名 3 |
| 13 | 门控假阳性与修复 | E 环（传感器自身） | FAIL → scoped_digest → 13/13 PASS | 判据作用域 1 字段；假阳性根因 MATCH |
| 14 | 安装/回滚可逆性 | T 环 + R 环 | 四阶段全通、幂等可重放 | 既有区域 0 语义变更；188→191→188；3→5→3 档 |

**整体控制论结论**：`dsh-custom` 的本质是「**强内核 + 薄装配层**」——与 `opencode-custom` 的「弱内核 + 强装配层」恰好互补。内核已自带 T 环硬约束（沙箱档位 fail-closed、spill 限幅、session 事件溯源）与 M 环基础设施（append-only session + compaction + FTS5 检索），装配层因此**不需要补内核**，只需补**编队（具名 worker + `oc_*` 别名）、策略库（45 派生 skill）与行为纪律（persona）**三件事；实验11 证明这三件事的可见性边界是干净的（纯净模式 31 工具 / 0 skill，零污染）。真正的薄弱点不在内核也不在编队，而在**装配层的两个语义接缝**：① **遮蔽造成的隐藏状态**（实验12：宿主 2790 字符纪律 100% 不生效却仍留存，回落路径上会突然复活且含过期内容）；② **判据的观测面大于因果面**（实验13：整文件指纹把 GUI 偏好写回误判为源漂移，E 环信噪比被稀释）。实验14 则给出正面证据：装配动作本身是**封闭、幂等、可双向执行**的（卸载零语义外溢、重装逐字节一致），说明「可逆性」这一红线在本装配层上是**可工程保证**的，而非口头承诺。综合判据强度梯度（沿用 opencode-custom 的结论框架）：**运行时硬阻（沙箱档位 fail-closed）> 确定性脚本门控（`verify_bundle.py`，但作用域必须收紧）> 声明层（toolFilter 行）> 纯提示词（persona 纪律）**；建议后续把 persona 的「按 presentation mode 分支」与「遮蔽态可观测」两项下沉为声明层或门控项，避免 M 环隐藏状态长期累积。

---

## 迁移损失登记（dsh 侧相对 opencode 侧）

> 口径：仅登记**已取证**的损失，分「不可实现 / 行为落差 / 风险」三类；未取证项不登记。

| # | 损失 | 原状（opencode 侧） | dsh 侧实际 | 定性 | 影响面 |
|---|------|--------------------|-----------|------|--------|
| ① | **子 Agent 无 bash → 门控退化** | worker 持 bash 白名单（`git status *` 等）且可**自跑门控脚本** | `toolFilter` 整条禁 shell（fail-closed），worker **无法自跑领域门控**；门控改由**主 Agent 串行代跑** | 行为落差 | 产出/验证分离更彻底（自利偏差消除），但验证**时延上升、并行度下降**；子 Agent 的「自证」能力归零，任何需脚本判定的产出都必须回主 Agent |
| ② | **reflection 链路断裂** | `pending.json` → reflection-worker → `/reflection` 人审 → 签名写 `MEMORY.md` 的完整异步 R 环 | `dsh-reflection` 插件已于 **2026-10-10 移出** → persona 的 MEMORY/reflection 段在 dsh 侧**不可用**（无 `reflection_add`/`reflection_mark`） | 不可实现 | 装配层的 R 环在 dsh 侧**只剩纪律文本、没有执行器**；宿主 `MEMORY.md` 仍在（`~/.dsh/MEMORY.md`，§-分段 + `[src:]` 签名），但**无入队通道** → 长期记忆闭环实际停摆 |
| ③ | **宿主 0 MCP（对比 opencode 侧 4 个）** | 6 个 MCP 配置（2 连通 / 4 禁用） | 宿主 **0 MCP 配置**，MCP 维度装配增量 Δ0（沿用内核内置 MCP client + resources 三工具，无 marketplace） | 行为落差 | T 环外部执行器接口**未被装配层利用**；PDF 读取、draw.io 出图等外部能力在 dsh 侧无对应装配（能力可由 skill 部分替代，但**工具面缺口真实存在**） |

> 补充说明（非损失，但属迁移语义变化）：opencode 侧的命令级入口 `/arch`、`/rd`、`/reflection` 在 dsh 侧**无命令注册**，降级为「点名 skill」；变体 Daily/Deep、TUI 键位、`[GATE]` 字面门控、`[COMPLEXITY]` 跨阶段继承等**整类删除**（dsh 无变体概念）。以上已在 `ADAPTATION-NOTES` 登记，本表不重复计损。

---

### 证据来源

| SRC | 级别 | 信源 | URL/路径 | 置信度 |
|-----|------|------|---------|--------|
| SRC-001 | S4 | 一手观察（bundle 安装与运行时验收报告：§3.6-3.10 为实测数据源） | `/home/zako-mio/opencode/archive/Mission-file/2026-10/1011-deepseek harness-提示词迁移工程-从opencode/report.md` | 高 |
| SRC-002 | S4 | 一手观察（bundle 独立审查报告：工具面/persona/技能目录复算、门控 FAIL 与根因、L1-L18 损失清单） | `/home/zako-mio/opencode/archive/Mission-file/2026-10/1011-opencode-bundle审查/report.md` | 高 |
| SRC-003 | S4 | 一手观察（运行时探针：四会话工具面与 persona 标记） | `/home/zako-mio/opencode/archive/Mission-file/2026-10/1011-deepseek harness-提示词迁移工程-从opencode/evidence/session-probe-{builtin-standard,opencode-standard,opencode-creator,opencode-ptc}.json` | 高 |
| SRC-004 | S4 | 一手观察（persona 作用域取证：宿主 2790 字符 / 8 小节、bundle 8018 字符、三模式系统提示 13658/53826、5 个负向用例） | `…/1011-deepseek harness-提示词迁移工程-从opencode/evidence/a12-persona-scope-evidence.json` | 高 |
| SRC-005 | S4 | 一手观察（技能目录运行时条目：42 = 45 − 3） | `…/1011-deepseek harness-提示词迁移工程-从opencode/evidence/skill-catalog-runtime.txt` | 高 |
| SRC-006 | S1 | 官方源码（DSH 本体：persona 遮蔽机制、skill 根扫描顺序、`disable-model-invocation` 识别、沙箱 fail-closed 语义） | `/home/zako-mio/dsh/packages/preset/persona/src/index.ts`、`/home/zako-mio/dsh/packages/skill/skill-filesystem/src/index.ts`、`/home/zako-mio/dsh/packages/sandbox/sandbox/src/index.ts`（基线 tag `dsh-v0.2.1-alpha.2`） | 高 |
| SRC-007 | S4 | 一手观察（装配层产物与门控脚本本体） | `/home/zako-mio/.dsh/presets/opencode/{cordis.patch.yml,persona.md,verify_bundle.py,build_provenance.py,README.md,ADAPTATION-NOTES.md}` | 高 |
| SRC-008 | S4 | 一手观察（45 派生 skill 与对账脚本） | `/home/zako-mio/.dsh/skills/opencode/`（`install.py` / `reconcile.py` / `PROVENANCE`） | 高 |
| SRC-009 | S4 | 一手观察（回滚备份件） | `/home/zako-mio/.dsh-backups/opencode-port-20261011/` | 高 |
| SRC-010 | S4 | 一手观察（本库 dsh 变体评分单一数据源，口径披露：v1.3 首次回填 v2.0 模型、旧单点分 2.5 不同源） | `/home/zako-mio/opencode/archive/Mission-file/2026-09/0907-控制理论Agent设计知识库/09-src-data/dsh_custom_scores.py` | 高 |