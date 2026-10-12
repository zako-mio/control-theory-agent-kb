# dsh-opencode-port · opencode → DSH 迁移 bundle

把用户 opencode 配置（`~/.config/opencode/`）里的**行为纪律**、**46 个 skill** 与 **7 个角色**
化用为 DeepSeek Harness 的三个自定义模式。**纯净模式零变化**：本 bundle 只 `insert` 自己的
preset 行，不修改任何 host 行。

| 模式 | preset id | row id | order | 定位 |
|---|---|---|---|---|
| OpenCode 迁移 · 标准 | `opencode-standard` | `preset-opencode-standard` | 11 | 日常调度 + 化用后的行为纪律 + 46 skill + 7 worker |
| OpenCode 迁移 · 创造 | `opencode-creator` | `preset-opencode-creator` | 12 | = 标准 + `tool-cordis` + 启用 `plugin_manager` + 作者技能目录 |
| OpenCode 迁移 · PTC | `opencode-ptc` | `preset-opencode-ptc` | 13 | = 标准 + `tool-presentation(mode: ptc)`，禁用 `workflow` |

---

## 1. 来源与基线

| 项 | 值 |
|---|---|
| 提示词源（只读） | `~/.config/opencode/instructions/*.md`（6 个）+ `MEMORY.md` + `opencode.jsonc` |
| skill 源（只读） | `~/.config/opencode/skills/`（46 个活跃；`disabled/` 下 4 个不在范围） |
| skill 派生副本 | `~/.dsh/skills/opencode/`（由该目录内的 `install.py` 幂等重建，含 `PROVENANCE.md`） |
| DSH 基线 | `0.2.1-alpha.2`（tag `dsh-v0.2.1-alpha.2`） |
| 结构模板 | `@deepseek-ai/dsh-web-app` 的 `presets/standard.patch.yml` 与 `presets/cordis.patch.yml`（逐字派生） |
| profile patch 备份 | `~/.dsh-backups/opencode-port-20261011/`（含 `cordis.patch.yml` / `package.json` / `cordis.yml`） |

## 2. 安装

**前置**：本 bundle 需要 `plugin_manager` 工具。它**不在内置 `standard` 会话的工具面里**
（2026-10-11 复核：会话 `session-246b0544` 实测 31 个工具，**无** `plugin_manager`、**无** `cordis_inspect_*`；
`web-app` bundle 顶层把 `tool-plugin-manager` 写 `disabled: true`）。
可用处是**内置 `cordis` 会话**与 **`opencode-creator` 模式**（preset 内的同名行覆盖顶层 disabled）。
所以**安装/卸载请在 `cordis` 会话或 `opencode-creator` 模式里做**。

> 更正记录（2026-10-11 第二轮）：本节原写「内置 `standard` / `cordis` 会话里可用」，
> 与实测工具面不符 —— 由 `opencode-standard` 模式的真实任务会话（`session-466dd93c`）审查发现，
> 复核后改正。原句是**声明层推断**，未与运行时工具面对照，属口径漂移。

```
plugin_manager install_bundle  target=/home/zako-mio/.dsh/presets/opencode
plugin_manager list_plugins                       # 确认 preset-opencode-* 三行 enabled=true 且无 broken
```

安装会走 `pnpm add`（本地目录 → `link:`），把 `dsh-opencode-port` 链接进
`~/.dsh/profiles/web/node_modules/`，并把 `dsh.profile.bundles` 追加一项。

### 2.1 为什么本 bundle 自带 `node_modules`

loader 解析 patch 里的插件 `name` 时，用的锚点是**该 patch 文件所在目录**
（`vendor/loader/src/config/tree.ts:122` 的 `import(name, ctx.baseUrl)`；`baseUrl` 由
`packages/boot/app-boot/src/index.ts:997` 设为 config 文件目录）。out-of-tree bundle 的祖先目录
（`~/.dsh/presets/`、`~/.dsh/`、`~`）都没有 `@deepseek-ai/*`，所以**必须自带 `node_modules`**。

这与官方 `@deepseek-ai/dsh-web-app` 的做法完全一致 —— 它同样自带
`node_modules/@deepseek-ai/*`（全部是指向 DSH 源码树的符号链接）。

⚠️ **锚点有两个，不是一个**（2026-10-11 修复，见 §10.1）：上面的锚点只服务 **bundle 平面**；
`agentPresets` 里的插件行由注册表以 `record.context.baseUrl` 解析，走的是**活动 profile** 的解析链
（`<profile>/node_modules` + installation 索引）。只链 bundle 锚点，`dsh-opencode-gate-runner`
这类本地插件包在 preset 平面就解析不到 ⇒ 三个 preset 全部 `never started`。

```bash
cd ~/.dsh/presets/opencode
python3 link_modules.py          # 建立/刷新**两个**锚点（bundle 30 包 + preset 平面补链）
python3 link_modules.py --check  # 校验两个锚点（preset 平面用**真实解析器**判定）
```

**回滚**：`link_modules.py` 只在 preset 平面补链**解析不到**的包（当前只有
`dsh-opencode-gate-runner`），输出里会逐条打印 `[preset 锚点] <pkg> -> <src>`；
删除这些链接即回滚（其余不动）。⚠️ `plugin_manager` 的 pnpm install 可能修剪它们 ——
**修剪后重跑 `link_modules.py` 即可**（`--check` 会先报出 `[preset 锚点] … 不可达`）。

> 因此本 bundle **不是**可移植到任意机器的通用包：它的插件符号链接指向本机 DSH 源码树
> `/home/zako-mio/dsh/packages/...`，且 persona 里含本机绝对路径（技能根、门控脚本、留档根）。

### 2.2 为什么 profile patch 要覆盖 `plugin-manager` 的 `pnpmCommand`

web 服务由 systemd 启动，其进程 `PATH` 是
`/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/snap/bin` —— **不含 nvm 的 `node`/`pnpm`**。
corepack 安装的 `pnpm` 是 shebang 为 `#!/usr/bin/env node` 的 shim，因此 `spawn('pnpm')`
直接 `ENOENT`（2026-10-11 实测：`install_bundle` 返回 `exitCode 127`，
`spawn pnpm ENOENT`），使 `plugin_manager` 的 `install_bundle` / `remove_bundle`
**在本机全部不可用**。

修法（同日实测通过，两处都必要）：

1. `~/.dsh/bin/pnpm` —— 包装脚本，用**绝对 `node` 路径**调用 corepack 的 `pnpm.js`，不依赖 `PATH`。
2. profile patch 增加一行覆盖：
   `- id: plugin-manager` → `config.pnpmCommand: /home/zako-mio/.dsh/bin/pnpm`
   （只覆盖这一个键，其余键走 `Config` schema 默认值，与 base 未配置该行时逐字一致）。

> ⚠️ 第 2 项是**卸载的前置条件**：若连同它一起还原掉，`remove_bundle` 会再次 `ENOENT`。
> 回滚请**先卸载、后还原 patch**（见 §7）。这一行不改任何会话的 persona 或工具面，
> 只让 `plugin_manager` 找得到 pnpm。

## 3. 刷新方式

| 改了什么 | 重跑 |
|---|---|
| `persona.md`、`opencode.jsonc` 的 agent description、DSH 的 `standard.patch.yml` | `python3 build_bundle.py` |
| 上面任一项（要更新指纹） | `python3 build_provenance.py` |
| `~/.config/opencode/skills/` | `python3 ~/.dsh/skills/opencode/install.py` |
| **`openspec` 重新生成了 skill**（源侧出现 `metadata.generatedBy` 或内容变长） | 先 `install.py`，再 `reconcile.py`（见 §3.2） |
| 任何改动之后 | `python3 verify_bundle.py`（+ `~/.dsh/skills/opencode/reconcile.py`） |

`cordis.patch.yml` **由脚本生成**（三个 preset 各自声明完整插件列表，persona 约 8 KB，
手写三份必然漂移）；改 persona 请改 `persona.md`。

### 3.1 单一真相源策略（与计划的一处偏离，已论证）

`03-计划-迁移实施.md` §3.2 建议用 `!!js` 在 preset 激活时**实时读取** opencode 源文件。
本 bundle 改为**构建期快照 + 漂移告警**，理由：

1. **可审计**：`!!js` 把 persona 正文藏进 JS 表达式，无法审阅；现在是 `persona.md` 明文 +
   `cordis.patch.yml` 逐字展开，`verify_bundle.py` 断言两者逐字符一致。
2. **缓存稳定**：运行时读文件意味着源侧任何改动都会改变系统前缀、使 prefix-cache 整体失效
   （这正是计划自己把 `MEMORY.md` 排除在 persona 之外的理由）。
3. **fail-closed**：源文件缺失/不可读时 preset 仍能激活，而不是整个模式挂掉。
4. **漂移仍可见**：`build_provenance.py --check` 与 `verify_bundle.py` 重算源指纹，
   漂移会**失败并报出**，不会被静默继承。
5. **活文件按「被消费字段」判漂移**（2026-10-11 第二轮修）：host patch
   `~/.dsh/profiles/web/cordis.patch.yml` 是**活文件** —— GUI 改字号/主题/模型都会写回它。
   若按整文件 sha256 判，一次字号调整就让门控变红；**假阳性会训练人忽略红灯，最终放过真漂移**。
   故该源只对 `system-prompt.personaPrefix` 算 `scoped.sha256`（bundle 实际消费的唯一字段），
   整文件变化但被消费字段未变时，输出 `note … 不算漂移，这是活文件的预期形态`。
   （`PROVENANCE.md` 里的整文件 sha256 仍保留，供人查证。）

### 3.2 openspec 生成物的重派生触发器（2026-10-11，E2）

**先纠正一处此前的推测**：曾有结论称「`openspec update` 会**无条件覆写** `~/.config/opencode/skills/openspec-*`」。
**经代码取证不成立**：

| 判据 | 实测 |
|---|---|
| `opencode` 工具的目标目录 | `skillsDir: '.opencode'`（**项目本地**），**没有** `globalSkillsDir` —— `openspec/dist/core/config.js` 工具表 |
| 解析函数 | `resolveToolSkillsDir()` = `<projectRoot>/.opencode/skills`（无 global 时）—— `dist/core/shared/skill-paths.js:12-22` |
| 本机实况 | `~/.config/opencode/` 下**无** `.opencode/`、**无** openspec 项目根 ⇒ 1.9.0 **不会**写那个目录 |
| 源侧 12 件 | 普通目录（2026-08-19），frontmatter 为 `metadata: {author: openspec, version: "1.0"}`、**无** `generatedBy`（1.9.0 才写）⇒ 由**更早版本**生成 |

**所以真实的失效形态不是「下次 update 必覆写」，而是**：源侧被**任何途径**
（其它工具、更早/更新版本的 openspec、人工搬运）重新生成后，**派生副本不会自己跟**。

⇒ 判据做成「**一旦发生就立刻可见，并给出修复路径**」（`~/.dsh/skills/opencode/reconcile.py` 的 `[1b/4]`）：

- **FAIL 条件（确定性信号）**：12 件源里出现 `metadata.generatedBy` ⇒ 被**新版**重新生成过；
- **NOTE（不是错误）**：源正文 > 8192 的**拆分脆弱件**（当前 5 件）—— 它们的派生副本是
  **人工拆分**产物（骨架 + `references/`），源侧一变就必须重跑 `install.py`；
- **修复路径**：`python3 ~/.dsh/skills/opencode/install.py` → `python3 ~/.dsh/skills/opencode/reconcile.py`；
  ⛔ 脚本**不自动修**（自动重派生会把「有意改动」与「意外改动」一起吞掉）。
- **负向自检**：5 条断言（含「长正文**不得**被判为重新生成」这条**反假阳性**断言 —— 第一版判据正是在此产生 5 条假红）。

### 3.3 会话 PATH 与外部 CLI 可达性（2026-10-11，E1）

**事实（实测）**：DSH 会话 `bash` 的 PATH 是
`/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/snap/bin:/mnt/c/Windows:…:/mnt/c/Windows/System32/OpenSSH`
—— **不含 nvm 的 bin，也不含 `~/.local/bin`**。
因此 `node` 本身 NOT FOUND，而 `openspec`(1.9.0) / `lark-cli`(1.0.88) / `agent-browser`(0.34.0)
（三者 shebang 为 `#!/usr/bin/env node`，被 `node` 缺失连带挡住）与 `headroom`(0.35.0)
（`#!/usr/bin/python3`，目录不在 PATH）**裸名一律不可用**。

⚠ **那 5 个 `/mnt/c/Windows/...` 目录来自 `dsh-wsl-desktop-path` 插件**（启动时追加，
日志：`[dsh-wsl-desktop-path] appended 5 Windows dir(s) to PATH: …`），**不在** systemd 进程自己的
PATH 里。会话内实测（2026-10-11 23:1x，opencode-standard 新会话）确认了完整值。
⛔ 别拿**宿主进程**的 PATH 当基线 —— 那描述的是一个会话里并不存在的环境；
`verify_cli_reachability.py` 的 `SESSION_BASELINE_PATH` 已按会话实测值写全（5 个 Windows 目录里
没有这 4 个 CLI，故负向控制不受影响）。

| 项 | 值 |
|---|---|
| 唯一引导串 | `PATH="$HOME/.nvm/versions/node/v24.19.0/bin:$HOME/.local/bin:$PATH" <cmd>` |
| 写在何处 | `persona.md` §八 第 7 条（**单一真相源**；判据从这里**提取**，不抄副本） |
| 无需引导 | `gh`(`/usr/bin/gh`)、`dot`(`/usr/bin/dot`) 本就在 PATH 上 |
| 为什么没有配置层解法 | `dsh-shell-env` 的命名空间被 `DSH_ENV_PREFIX` 限定为 `DSH_*`（`shell-env/src/index.ts:13,54,68`）；`dsh-tool-bash` 的 Config 只有 `enableRunInBackground`/`promoteOnTimeout`（`tool-bash/src/index.ts:56-59`） |
| 判据 | `verify_bundle.py` **check 17** → `verify_cli_reachability.py` |

**复验命令**：
```bash
cd ~/.dsh/presets/opencode
python3 verify_cli_reachability.py        # 正向 + 负向控制（独立可跑）
python3 verify_bundle.py                  # 全量静态校验（项数与编号以 verify_bundle.py 的 CHECK_TITLES 为准）
```

**check 17 的判据设计**（四条 + 反安慰）：
1. 引导串在 `persona.md` 中须**恰出现 1 次**（0 = 标记被删、判据失效；>1 = 两套阈值）；
2. 文档所述的 nvm bin / `~/.local/bin` 下必须有 `node` / `headroom`，**否则 fail-loud 并列出本机实际版本**
   （要求回刷文档，不静默降级）；
3. 按**文档里的写法**（`PATH=… <cmd>`）跑四个 CLI，退出码 0 且输出含文档所述版本；
4. **负向控制**：以**文档所述的会话基线 PATH**（脚本内 `SESSION_BASELINE_PATH`）**不加前缀**跑
   `command -v node` ⇒ 必须 NOT FOUND。
   ⚠ 必须**显式 pin 基线**：从登录 shell（已 source nvm）跑时 `node` 本就在 PATH 里，
   沿用 ambient PATH 会让这条控制变成**假红**。

**负向自检实测**（4 个变异体各自 rc=1 + 控制组 rc=0）：删标记 / 复制成两份 / nvm 版本写错 / CLI 版本写错
—— 见 `evidence/e1-check17-cli-reachability.out.txt`。

**「已交付」与「已生效」的分界：PENDING-RESTART（rc=3）**（2026-10-11 收尾补）

check 17 只能证明「那条指引**能用**」；它证明不了「那条指引**进了运行实例**」——
后者需要 `persona.md` §八 的引导串**出现在某个会话的 `system/message` 里**，而 bundle 层
**不热载**：改动只在重启 `dsh-web.service` 后进入运行实例。这条实机判据是
`verify_persona_scope.py` 的 **A12-3f**（复用 `verify_cli_reachability.py` 的 `PATH_BOOTSTRAP_RE`，
⛔ 不抄第二份正则）。它有三种结果：

| 退出码 | 含义 | 处置 |
|:--:|---|---|
| `0` | 至少一条会话已带上引导串 | 已生效 |
| `3` | 引导串**在 `persona.md` 里**，但所有会话都还没有 | **PENDING-RESTART** —— 已交付、待重启；不是失败 |
| `1` | 引导串**不在 `persona.md` 里**（E1 被判死 / 标记被删），或**重启后**新会话仍缺 | 真失败 |

**3f 是时间感知的**（2026-10-11 重启收口后补）：一条会话的系统提示是**创建时冻结**的，
重启**前**创建的会话永远不可能含重启后才进 patch 的文本。故 3f 逐会话比对
「该会话 mtime vs 服务启动时刻」（`service_restart_epoch()` 读 `/proc/<MainPID>/stat`）：

- mtime **早于**服务启动 ⇒ 记「**预期陈旧**」（ok，不制造恒红）；
- mtime **晚于**服务启动却仍缺 ⇒ **真失败**（这才是「重启了却没生效」）。

判据强度由负向用例 **N6** 独立守住（合成会话晚于服务启动、仅缺引导串 ⇒ 必须 FAIL），
故「预期陈旧」不会被误当成「3f 恒真」。⛔ 取不到服务启动时刻时**不猜**：一律按失败处理。

`verify_bundle.py` 把 `rc=3` 记为 **note**（不是 FAIL）—— 若一律算红，门控会**长期恒红**，
而「恒红的门控会被忽略，最终与恒绿等效」（分析报告 §5.2 第 4 条，即 G6 的教训）。
交付后要求「运行时必须已生效」时，用**显式开关**把这一态重新当失败：

```bash
python3 verify_bundle.py                          # 默认：rc=3 记 note，门控仍绿
python3 verify_bundle.py --require-runtime-fresh   # 收口复核：未生效即 FAIL（重启后再跑应转绿）
```

⚠ 这不是「把断言降级成警告」：`rc=3` 是**独立退出码**，note 里带引导串与受影响会话数，
且严格模式随时可把它转回失败。3f 的**判据强度**由负向用例 **N6**（合成会话含全部小节标题、
仅缺引导串 ⇒ 必须 FAIL）独立守住，故「rc=3」不会被误当成「3f 恒真」。

## 4. 与 opencode 的差异与损失（**不得声称保真**）

| # | opencode 规则 | DSH 近似后的实际 | 损失 |
|---|---|---|---|
| 1 | `bash` 命令级 deny + 前缀白名单 | 只有档位级 sandbox；`read-only` 档下 bash 仍可跑（只栅栏写） | **命令级 deny** |
| 2 | `read` 对 `auth.json` / `opencode.env` deny | 读一律放行 | **凭据文件可读** |
| 3 | `edit` 跨工作区 allow 列表 | `workspace-write` 只允许会话 cwd 内写 | 跨工作区写需提权 |
| 4 | worker `bash` 白名单（`git status *` 等） | `toolFilter` 整条禁掉 shell（fail-closed）；**门控自跑**另由窄工具 `run_gate` 补回（见 §4.2） | **worker 失去 git 只读与任意命令**（门控自跑已恢复） |
| 5 | `external_directory` allow/deny | 无 | 越界读写边界 |
| 6 | `skill` 加载前的权限门 | DSH 无 | 技能加载权限语义 |
| 7 | `question`/`todowrite`/`skill` 的 per-agent deny | `toolFilter` | 等价 |
| 8 | `task: deny`（worker 不自委派） | 各 worker 的 `toolFilter.deny`（deny 里含 `subagent`/`subagent_fork`/`workflow`/6 个 `oc_*`） | 等价 |
| 9 | 变体（Daily/Deep）、命令级 `/arch` `/rd` `/reflection` | 无 | 见 `ADAPTATION-NOTES.md` §1/§5 |
| 10 | 压缩模板 | 归 `dsh-compaction-basic`，preset 不可配置 | 无法自定义压缩行为 |
| 11 | 反思队列工具链（`reflection_add`/`reflection_mark` + 会话开始自动审阅） | **以 R-A 文件载体重建**（ADR-012，2026-10-12 门控 6/6 PASS）：候选 → `~/.dsh/reflection/candidates/` → 主 Agent 按 `dsh-reflection` 方法论审阅 → `~/.dsh/MEMORY.md`；⛔ 不重建插件队列、⛔ 两侧队列常态互不索引 | **纪律等价**（写入仍须经链）；旧链路实测损失接近零（插件自 2026-09-14 停用、队列文件从未落地） |

> ⚠ **可实现性更正（第 11 轮，2026-10-13）**：上表 **#1 / #2 / #3 / #5** 四行描述的**不是「DSH 做不到」**，
> 而是「**尚未实现**」—— `tools/pre-execute` waterfall **已接线**并被真实调用
> （`packages/core/tools/src/index.ts:1511`；另有 5 个生产监听器），`allow/deny/cancel/ask` 语义、
> 审批链路（`:1733-1774`）与 `callId` 关联应答齐备。旧文（含 `ADAPTATION-NOTES.md` §1 #12 原文）把
> `tool-bash` 的 `TODO(permissions)` 读成「扩展点未接线」属**归因错误**；缺的只是**规则引擎插件本体**。
> ⚠ 同时记住：该扩展点是**可重排策略层，不是安全边界**（⛔ 不能改写 `exec.arguments`）。
> 是否补做见 `1011-全面适配性迁移分析/E11-前置调研与重裁材料.md`（默认维持后置）。

### 4.2 门控执行通道 `run_gate`（2026-10-11，ADR-010）

**要解决的问题**：迁移决策 **D3** 把 worker 的 shell 整条禁掉（fail-closed），门控脚本改由主 Agent
代跑；下游实测出代价 —— worker 交付的脚本**未经任何运行时验证**（只能静态 grep）。某轮 4 个子
Agent 的交付脚本被主 Agent 实跑后修出 **10 处**缺陷，其中 **3 处是恒真/恒假判据**。

**做法**：preset **顶层**新增 `gate-runner` 行（本地插件包 `dsh-opencode-gate-runner`，源码在
`plugins/dsh-opencode-gate-runner/`），注册模型可见的窄工具 `run_gate`：

| 窄性来源 | 说明 |
|---|---|
| 无内联代码通路 | 解释器恒以「脚本路径 = argv[1]」调用 ⇒ `-c`/`-e` 构造上不存在 |
| argv 数组直传 | 不经 shell 解析 ⇒ 无管道/重定向/`&&`/通配/任意二进制 |
| roots 白名单 | 脚本 realpath 后必须落在 `workspace` + 两个固定根内，越界 fail-closed |
| 扩展名白名单 | `.py`/`.js`/`.mjs`/`.sh`，每个必须有解释器映射 |
| 超时 + 输出上限 + spill | 默认 120s / 上限 600s；输出 16 KB 封顶后落 `~/.dsh/spill/gate-runner/` |

⚠ **这是策略，不是边界**：worker 仍可写一个内含 `subprocess` 的 `.py` 脚本。窄性来自「表面收窄 +
每次调用可审计」，不是内核级隔离。

**可见性**（P0 实证，`1011-迁移适配-E环门控通道与R环纠正/evidence/p0-visibility-probe.md`）：deny 型 worker
（`subagent`/`oc_architect`/`oc_requirement`/`oc_reflection`/`oc_pdf`）默认可见；`oc_explore`/`oc_search`
是 allow 型，allow 列表排他 ⇒ `run_gate` 对它们**构造性不可见**。

⛔ **该行必须在 preset 顶层**，不得放进 `delegation` 组：顶层行注册的工具在子 Agent 视角**可被
`toolFilter` 命名**且 deny 真实生效；而 `delegation` 组内 `config` 列表注册的工具（`subagent`/`oc_*`）
**不可**被命名 —— 写进 deny 会抛 `tools.restrict() names unknown global tool`，委派连子会话都起不来。

**验证**：`verify_bundle.py` check 14（结构 P1–P5 + 行为负向由 `check_gate_policy.mjs` 承担 + 结构变异体负向自检）；行为断言与插件单测的条数 ⛔ **不在本行写死** —— 分别以 `check_gate_policy.mjs` 现跑输出（`policy behavior: N passed`）与 `tests/policy.test.mjs` 的现跑读数为准（后者由迁移状态判据的 `C-DOCNUM` 机检）；
插件自身 26 条离线单测（`plugins/dsh-opencode-gate-runner/tests/`）。
**实机生效需重启 `dsh-web.service`**（bundle 层不热载），重启后跑 `verify_gate_channel_live.py`。

### 4.1 环境硬约束

**沙箱后端已可用（2026-10-12 更新 —— 推翻此前结论）**：旧文档写「本机没有可用的沙箱后端
（bubblewrap 与 Landlock 均不可用）」，**该结论已证伪**。真相：

| 项 | 实测（2026-10-12） |
|---|---|
| 内核 Landlock | **一直支持**：`CONFIG_SECURITY_LANDLOCK=y`，`CONFIG_LSM` 首项即 `landlock`；但 `/sys/kernel/security/lsm` 不存在 ⇒ **基于该路径的探测会假阴性** |
| user namespaces | `unshare --user --map-root-user` **成功** |
| `bwrap` | 修复前 **未安装** ⇒ Linux 链 `['bwrap','landlock']` 首选落空 |
| Landlock 平台包 | `@deepseek-ai/node-addon-system-linux-x64` **MODULE_NOT_FOUND** ⇒ 二级后端也缺件 |
| ⇒ 旧后果 | 两级都挂 → 所有 `read-only`/`workspace-write` 命令被 `SandboxUnavailableError` fail-closed 拒绝（**档位看起来存在、实际无法执行**） |
| ⇒ 修复 | `sudo apt-get install -y bubblewrap` + 重启 `dsh-web.service` |
| ⇒ 现状 | 链选中 **bwrap**，`enforcement=full`；`read-only` 拒写、`workspace-write` 限写（**shell + fs 双侧**） |

⚠ **两个必须记住的点**：
1. **`workspaceRoot` 是逐会话解析的**（`sandbox-policy/src/index.ts:168` → `session.header.cwd`），
   不是服务进程的 cwd —— 边界跟着**会话工作区**走。
2. **`confine()` 恒返回受限 argv**，包括 `danger-full-access`；full-access 的**旁路在调用方**
   （`terminal-bash/src/index.ts:103` 对 danger-full-access 直接 `return argv`，不调 `confine`）。
   把「provider 会自己放行 full-access」当契约就会误判。

**取证工具**：`verify_sandbox_enforcement.mts`（真实启动链 + 真 confine + 真写盘，含负向控制）、
`sandbox_p0_probe.py`（**会话内**自测当前档位语义）。

## 5. 权限档（profile patch 增量）

`~/.dsh/profiles/web/cordis.patch.yml` 的 `permission` 行已**整表重述**（bundle patch 会整体替换
config，必须写全），新增两档，原有三档与 `defaultPreset: read-only` 逐字保留：

| 档位 | sandbox | approval | 展示名 | 对应 opencode |
|---|---|---|---|---|
| `read-only`（原） | read-only | ask | — | explore 类只读 |
| `workspace-write`（原） | workspace-write | ask | — | — |
| `opencode-plan`（新） | read-only | ask | `OC·Plan（只读）` | `agent.plan`（edit 全 deny） |
| `opencode-build`（新） | workspace-write | ask | `OC·Build（工作区写）` | `agent.build`（edit 分层） |
| `danger-full-access`（原） | danger-full-access | never | — | 本机**唯一可跑 bash** 的档 |

`/permission` 裸调用应列出 5 档，行为无回归。

## 6. 子 Agent 编队

7 个 worker（`provider: spawn`，各自带 persona 与 `toolFilter`）+ DSH 原生
`subagent_fork`。**全部声明在 preset 内，因此纯净模式看不到这些名字。**

> **不写 `maxDepth`（2026-10-11 第二轮修正）**：`maxDepth` 是**子 Agent 的绝对委派深度上限**
> （`0` 禁止委派；省略读 Host 默认 `1`）。主 Agent 深度 0 → 子 Agent 必为深度 1，
> 故 `maxDepth: 0` 会让 worker **一调用即报 `subagent depth 1 exceeds maxDepth 0`** ——
> 7 个具名 worker 变成「目录里可见、一调用即报错」。
> 旧写法 `maxDepth: 0` 的意图（worker 不再往下委派）**已由每个 worker 的 `toolFilter.deny`
> 正确实现**，故该键冗余且有害；省略后 worker **可被调用**、**不可再往下委派**。
> 门控 `verify_bundle.py` check 7 已同步：断言**可委派**，并带两条负向用例
> （把 `maxDepth` 改回 0、抽掉 `DENY_DELEGATION` 都必须 FAIL）。

| opencode agent | toolName | persona 来源 | toolFilter |
|---|---|---|---|
| `general` | `subagent` | `agent.general.description` | deny `todo_write`/`ask_user_question`/schedule 组 |
| `explore` | `oc_explore` | description | allow `read`/`glob`/`grep`/`skill` |
| `architect-worker` | `oc_architect` | description | deny shell/`todo_write`/`ask_user_question` |
| `requirement-discovery-worker` | `oc_requirement` | description | 同上 |
| `search-worker` | `oc_search` | description | allow `read`/`glob`/`grep`/`web_search`/`web_fetch`/`skill` |
| `reflection-worker` | `oc_reflection` | description | deny shell/`ask_user_question` |
| `pdf-worker` | `oc_pdf` | description | deny shell/`todo_write`/`ask_user_question` |

**平台互斥的 shell deny**：`bash` 与 `pwsh` 二者按平台只有一个注册，写死名字会命中
`tools.restrict()` 的「未知工具」并让该 worker 无法创建。故 shell deny 用
`!!js process.platform === 'win32' ? ['pwsh'] : ['bash']` 按平台取其一。

`oc_reflection` 的注记：opencode 的反思写入链（`reflection_add`/`reflection_mark`）在 DSH 已不存在
（插件 2026-10-10 移出），该 worker 仅保留「分析并产出候选条目」的语义，**不能写记忆**。

## 7. 回滚

```bash
# 1) 先卸载 bundle（在 cordis preset 会话里；此时 §2.2 的 pnpmCommand 覆盖必须还在）
plugin_manager remove_bundle  target=dsh-opencode-port

# 2) 再还原 profile patch 与 manifest
cp ~/.dsh-backups/opencode-port-20261011/cordis.patch.yml ~/.dsh/profiles/web/cordis.patch.yml
cp ~/.dsh-backups/opencode-port-20261011/package.json    ~/.dsh/profiles/web/package.json

# 3) 删除 skill 派生副本与 bundle（可选）
rm -rf ~/.dsh/skills/opencode ~/.dsh/presets/opencode
```

回滚后三行 `preset-opencode-*` 应消失，`/permission` 回到 3 档，其余 profile 行为不受影响。
⚠️ 第 2 步的备份 patch 早于 §2.2 的 `pnpmCommand` 覆盖，还原后 `plugin_manager` 会再次
`ENOENT`；如需保留插件管理能力，请把那一行手工加回（或别执行第 2 步）。

**2026-10-11 实测**：按「先 remove_bundle → 还原 patch → 恢复 patch → 再 install_bundle」
演练一轮，`remove_bundle` 返回 `application: applied`；卸载后既有 4 个 preset 区域与安装前
基线**逐字节一致**，`/permission` 随 patch 还原回到 3 档；重新安装后组合树与首次安装后
**逐字节一致**（见 §8 A11）。

## 8. 验收状态

<!-- BEGIN GENERATED: acceptance-status -->

> 本表由 `gen_status_table.py` **生成**（14 行），请勿手改；
> 改判据后重跑：`python3 gen_status_table.py --write`。
> 来源等级：**可复算** = 本轮现跑命令；**复算至产物** = 读机检产物重跑断言；
> **未复算** = 无自动化判据或本轮未跑（⚠️，不得当作 ✅）。

| 判据 | 状态 | 取证方式 | 来源等级 |
|---|---|---|---|
| 静态校验（项数见下） | ✅ | `verify_bundle.py`（本轮现跑） → 20/20 项全通过 | ✅ 可复算 |
| 源指纹（活文件按被消费字段判） | ✅ | `build_provenance.py --check`（本轮现跑） → 19 provenance fingerprints | ✅ 可复算 |
| skill 派生（件数见下 + 幂等重派生） | ✅ | `reconcile.py`（本轮现跑） → 47 件逐字节一致 | ✅ 可复算 |
| dsh-config 声明账本漂移（源指针 / 层归属 / 层间冲突 / 台账一致性） | ✅ | `verify_dsh_config.py`（本轮现跑） → 跨层 row 13 条；其中 9 条 | ✅ 可复算 |
| A1 三行 preset `enabled=true` 且无 broken | ✅ | `evidence/plugin-preset-rows.txt`（机检产物，可重跑断言）→ 3 行 enabled=true / active | ✅ 复算至产物 |
| A2 / A3 persona 内容与去重（运行时装配） | ✅ | `evidence/a12-persona-scope-evidence.json`（机检产物，可重跑断言）→ 3 个模式会话：persona 小节 15/15，host 正文泄漏 0；断言 25 条全通过 | ✅ 复算至产物 |
| A4 纯净 `standard` 零变化 | ✅ | `check_dump_purity.py`（本轮现跑） → 既有 4 个 preset 逐字节一致 | ✅ 可复算 |
| A5 / A6 skill 目录与渲染长度 | ⚠️ | 45 件 / 0 件超限为第一轮门控结论；本轮未复算（`install.py --gate-only` 需源目录只读副本）。⚠ 两个数字都已过期：源侧现为 **47 件**（见上一行 reconcile 的现跑读数），本行未随之一并复算 —— 数字的**唯一可机检来源**是上一行，本行只登记「未复算」这一事实。（留档：`evidence/skill-catalog-runtime.txt`） | ⚠️ 未复算 |
| A7 `oc_*` 仅新模式可见（工具面） | ✅ | `evidence/session-probe-opencode-standard.json`（机检产物，可重跑断言）→ opencode-standard 工具面 37 个，含 6 个 oc_* | ✅ 复算至产物 |
| A8 `/permission` 5 档 | ⚠️ | 组合树 permission 行含 5 档（第一轮实测）；本轮未复算（留档：`evidence/dump-config-installed.yml`） | ⚠️ 未复算 |
| A9 creator / ptc 差异（工具面） | ✅ | `evidence/session-probe-opencode-creator.json`（机检产物，可重跑断言）→ creator 40 工具含 cordis_inspect_* + plugin_manager | ✅ 复算至产物 |
| A10 / A10b 负向用例 | ⚠️ | 两条负向实测已留档（坏 frontmatter 被拦、toolFilter 回退成数组被拦）；本轮未复跑（留档：`evidence/a10-negative-skill-gate.out.txt / a10b-negative-toolfilter.out.txt`） | ⚠️ 未复算 |
| A11 回滚演练 | ⚠️ | 第一轮真实 remove + 还原 + 重装；**无机检产物**，属一次性演练（留档：`evidence/—`） | ⚠️ 未复算 |
| A12 七段纪律处置取证 | ✅ | `evidence/a12-persona-scope-evidence.json`（机检产物，可重跑断言）→ 三条命题 25 条断言全通过 + 负向用例 5/5 按预期失败；接入 check 13 | ✅ 复算至产物 |

<!-- END GENERATED: acceptance-status -->

> **本节是生成物**（2026-10-11 第二轮改造）。原因见 §8.1：
> 人写的状态列会随判据演进而过期，且**不会自己报错**。

### 8.1 为什么改成生成（口径漂移的根因）

2026-10-11 第二轮用 `opencode-standard` 模式跑了一条真实审查任务
（会话 `session-466dd93c`），它在报告里点出根因：

> 7 条发现里 3 条纯属**口径漂移**，共同成因是「**验收结论写死在 markdown 里，而判据是脚本**」。

当场被复核成立的两例：

| 例 | 手写结论 | 实测 | 性质 |
|---|---|---|---|
| §2 `plugin_manager` 可用范围 | 「内置 `standard` / `cordis` 会话里可用」 | 内置 `standard` 工具面 **31 个、无它** | **声明层推断未对照运行时** |
| §8 源指纹行 | 「✅ 通过」 | 新鲜复跑 **FAIL**（活文件整文件 sha256） | **判据演进后结论未跟** |

修法：状态列由 `gen_status_table.py` 生成，**来源分级**：

- **可复算** —— 本轮现跑命令（`verify_bundle.py` / `build_provenance.py` / `reconcile.py`）；
- **复算至产物** —— 读 `evidence/` 里的机检产物**重跑断言**（不是复述文字）；
- **未复算** —— 无自动化判据或本轮未跑，**必须显示 ⚠️，不得标 ✅**。

改判据后重跑：`python3 gen_status_table.py --write`；一致性由 `gen_status_table.py --check` 断言。

### 8.2 补充口径

> A2/A3/A7/A9 的「运行时」一半必须在**新模式的新会话**里看（工具面与系统提示的实际装配）。
> 组合树（`dsh --profile web --dump-config`）只能证明声明层正确。
> 二者已于 2026-10-11 第二轮全部补齐，见 `report.md` §4.1 与 `evidence/session-probe-*.json`。

> **技能目录口径（2026-10-11 用户裁决：有意保留）**：`skill-filesystem` 的 `customSkillDirs`
> 是**追加**而非替换（`includeDefaultRoots` 默认 `true`），因此新模式目录 = 46 个 opencode skill
> **+ 会话 cwd 项目根与用户根自带的 skill**（如 cwd 在 DSH 仓库内，还有 `.agents/skills` 的 16 件）。
> 这是**有意行为**：预设/项目 skill 本身也在「opencode 适配」的考虑范围内，故**不加**
> `includeDefaultRoots: false`。「46 件」指 opencode 派生目录本身，不是新模式会话的目录总数。

## 9. 文件清单

| 文件 | 角色 |
|---|---|
| `package.json` | bundle manifest（`dsh.bundle.patch`） |
| `cordis.patch.yml` | **生成物**：三个 preset 的完整声明 |
| `persona.md` | persona 正文的**规范副本**（唯一手写来源） |
| `build_bundle.py` | 生成 `cordis.patch.yml`（persona 展开 + worker persona 取自 `opencode.jsonc`） |
| `build_provenance.py` | 生成 `provenance.json` + `PROVENANCE.md`（含源指纹与漂移检测） |
| `link_modules.py` | 建立**两个** `node_modules` 解析锚点（bundle 30 包 + preset 平面补链）；`--check` 用真实解析器判定 preset 平面 |
| `verify_bundle.py` | **20 项**静态校验（安装前可跑；含 check 15 真实挂载审计、check 16 工具 schema 子集、check 17 CLI 可达性、check 18 dsh-config 账本、check 19 迁移状态、check 20 命令注册插件） |
| `plugins/dsh-opencode-commands/` | **命令注册插件**（`E10`）：`/arch` `/rd` `/reflection` → 把「点名 skill + 用户原文」steer 成用户消息；自带注册单测（check 20 的引擎） |
| `verify_rows.mjs` | 用**真实插件的 `Config`** 递归校验每个子行（含 group 内）；check 9 的引擎 |
| `verify_preset_resolution.mts` | **preset 平面锚点判据**：真 `createRuntimeResolution` + 真解析拦截器；check 10 的引擎（带负向控制） |
| `mount_audit.mts` | **真实挂载审计**：真 `runProfile` + 真 Loader，临时端口 3099；check 15 的引擎（内建负向控制 patch） |
| `mount_audit-negative.patch.yml` | 上述审计的**负向控制**：故意插入引用不存在插件包的 preset（不进生产组合） |
| `check_tool_output_schema.mts` | **工具 schema 子集判据**：插件真实导出的 schema 过 DSH `assertSupportedJsonSchema`；check 16 的引擎 |
| `verify_gate_channel_live.mjs` | **实机复验**：从会话日志判定 `run_gate` 是否已进入运行实例（cutoff = 最近一次重启，按 `session.createdAt` 归属） |
| `verify_persona_scope.py` | **A12 取证**：host `personaPrefix`（七段纪律）对 preset 会话的作用域边界；check 13 的引擎。probe 路径已参数化：`--probe` > `DSH_PROBE` > `--probe-cwd` > `DSH_PROBE_CWD` > 脚本自身目录；缺省找不到即 **fail-loud**（⛔ 不静默退化成 0 条会话） |
| `session_probe.js` + `probe/` | **探针随 bundle 分发**（`R08-F3`/`R09-F3`）：根上是**转发 shim**，本体在 `probe/session_probe.js`（逐字节等于归档原件，11 433 B），`probe/package.json` 标 `commonjs` —— 因为 bundle 根 `package.json` 是 `type: module`，探针用 `require` 平铺在根会被当 ESM 直接报 `require is not defined` |
| `check_dump_purity.py` | **A4 判据**：安装前后 `--dump-config` 的既有 4 个 preset 逐字节比对（含负向自检） |
| `gen_status_table.py` | **从门控输出派生 README §8 状态表**（消除「结论手写、判据是脚本」的漂移源）；`--check` 可作门控 |
| `PROVENANCE.md` / `provenance.json` | persona 段落溯源 + 源指纹 |
| `ADAPTATION-NOTES.md` | 第 3 层：opencode 机制处置逐条表 |

## 10. 踩坑记录：GUI 预设「加载失败」（2026-10-11 已修）

**现象**：三个 `opencode-*` 模式在 GUI 的预设菜单里显示「加载失败」角标
（`packages/client/ui-agent-preset/src/client/locales.ts` 的 `brokenBadge`），
选中后无法切换，新建会话落回内置 `standard`。

**定位链**：

1. 客户端角标来自主机名册的 `broken` 字段
   （`packages/preset/agent-preset-registry/src/index.ts` 的 `list()` → `diagnostic()`）。
2. `diagnostic()` 的 `broken` = 挂载失败（`activate()` 的 catch）或逐行审计
   （`auditRows` 报 failed/pending 行）。
3. 逐行比对内置 `standard` preset：行集合几乎相同，差异只在我们的配置里 ——
   嫌疑落在 `delegation` 组的 `toolFilter`。
4. 验证：`@deepseek-ai/dsh-tool-subagent` 的
   `Config.toolFilter = z.object({ allow: z.array(z.string()), deny: z.array(z.string()) })`；
   把产物里的 `deny` 喂给它 → 抛 `$.toolFilter.deny[1] expected string but got bash`。

**根因**：`build_bundle.py` 原先把平台互斥的 shell deny 写成**列表项**
`- !!js "process.platform === 'win32' ? ['pwsh'] : ['bash']"`。
但 loader 的 `interpolate`（`vendor/loader/src/config/utils.ts`）对序列是
`value.map(interpolate)` —— **一个表达式求出一个元素，不会把数组展开**。
于是得到嵌套数组 `deny: [..., ['bash'], ...]`，违反 `z.array(z.string())`，
`subagent`/`oc-*` 这些行挂载即失败 → 整个 preset 报 `broken`。

**修复**：`shell_deny_js()` 改为返回**字符串**表达式
`!!js "process.platform === 'win32' ? 'pwsh' : 'bash'"`，重跑 `build_bundle.py`。

**门控加固**（避免同类再犯）：

- check 6 不再「见到 `!!js` 就跳过」，而是按 loader 语义**求值一次**，
  断言结果是字符串且是已知工具名。
- 新增 check 9：`verify_rows.mjs` 走运行时同一条解析路径
  （`createRequire` + `exports` → 已构建 lib），取插件导出的 `Config`
  对**递归展开后的每个子行**做 schema 校验（当前 43 行，跳过 9 行无 Config 者）。
- 端到端负向用例：把表达式回退成数组形态后跑 `verify_bundle.py` → 17 项失败。

## 10.1 两层故障的门控缺口修复（G1–G4，2026-10-11 晚）

§10 修好了现象，但**门控本身仍有四个缺口** —— 它们正是「两轮全绿之后故障仍然存活」的原因。
本轮（`1011-全面适配性迁移分析`）把它们逐个关掉。核心教训一句话：
**门控必须断言被判对象所用的锚点，并覆盖「插件 apply / 注册是否成功」**。

| # | 缺口 | 修法 | 负向控制（判据必须能失败） |
|---|---|---|---|
| **G1** | `link_modules.py` **锚点错位**：只链 bundle 自己的 `node_modules`，而 preset 行从不使用该锚点 ⇒「30 个包链接齐备」是对错误锚点的绿 | 新增 **preset 平面锚点**：`verify_preset_resolution.mts` 用真 `createRuntimeResolution` + 真解析拦截器（起点 `<profile>/cordis.yml`）判定；`--check` 同时断言两个平面 | 移走链接 → `--check` 报 `[preset 锚点] dsh-opencode-gate-runner: 不可达`（rc=1） |
| **G2a** | `verify_bundle.py` **缺真实挂载审计**：check 9 只校验行的 `config`，「整行能否真实挂载」在覆盖面外 | 新增 **check 15**：`mount_audit.mts` 跑真 `runProfile`（临时端口 3099，不碰线上 3080），断言 3 个生产 preset 无 `broken` | 审计**内建**：叠加 `mount_audit-negative.patch.yml`（引用不存在的插件包），断言它必须被判为 broken 且原因串含该包名 |
| **G2b** | 工具 `output.schema` 的 DSH 子集越界（P2）无静态判据 | 新增 **check 16**：`check_tool_output_schema.mts` 拿插件**真实导出**的 `OUTPUT_SCHEMA` / `inputSchema` 跑 `assertSupportedJsonSchema` | 联合 `type` 数组（P2 逐字形态）/ 单分支 `oneOf` / `type` 与 `oneOf` 并存 —— 三条都必须 REJECTED；另加「判据恒真/恒假」反安慰断言 |
| **G3** | P1 修复是**手工软链**，未持久化（`plugin_manager` 的 pnpm install 可能修剪） | 由 `link_modules.py` **可复现地**建立，`--check` 断言；回滚方式见 §2.1 | 见 G1（同一条负向控制即证明「可复现修复」：跑一次写入路径 → 自验「补链后真实解析器判定全部可解析」） |
| **G4** | `verify_gate_channel_live.mjs` 的 cutoff 语义不明（重启前后不同），且**时间戳被按错时区解析** | cutoff 明确为「最近一次重启」并打印 `MainPID` / `ActiveState` / `ExecMainStartTimestamp`；会话归属改按日志内 **`session.createdAt`**（不再用文件 mtime）；systemctl 加 `--timestamp=utc` | 解析到**未来**的 cutoff 直接判 FAIL（`service-restart-invalid`）—— `CST` 陷阱会让 cutoff 差 14 小时、判据变恒假 |

> **G4 的时区陷阱值得单记**：systemd 默认按本机时区打印，缩写是 `CST`，而 JS 的
> `Date.parse('… CST')` 按**美国中部时间**（UTC−6）解释 ⇒ `2026-10-11 18:58:18 CST`
> 被解析成 `2026-10-12T00:58:18Z`（差 14 小时），cutoff 跑到未来、L1 恒假。
> 加 `--timestamp=utc` 即绕开，并保留「未来 cutoff ⇒ FAIL」这条自检。

**实测（2026-10-11 19:2x，全部现跑）**：

```
$ python3 verify_bundle.py        # 16/16 PASS，elapsed 19.3s
$ python3 link_modules.py --check # 两个锚点 OK（bundle 30 包 / preset 31 个插件名）
$ node verify_gate_channel_live.mjs
  PASS: 门控执行通道实机生效（1 个会话含 run_gate，只读面 0 泄漏；
        cutoff=2026-10-11T10:58:18.000Z 来源=service-restart PID=308104）
```

⚠️ **check 15 需要 DSH 源码树**（`/home/zako-mio/dsh`，可用 `DSH_SOURCE_TREE` 覆盖）：
它跑的是与线上完全同一条启动链。这是**有意的**依赖 —— 静态判据已被证明抓不到这两层故障，
用「不需要源码树」换来的绿是假绿。
