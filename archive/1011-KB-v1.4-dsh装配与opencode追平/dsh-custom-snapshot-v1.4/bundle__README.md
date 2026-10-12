# dsh-opencode-port · opencode → DSH 迁移 bundle

把用户 opencode 配置（`~/.config/opencode/`）里的**行为纪律**、**45 个 skill** 与 **7 个角色**
化用为 DeepSeek Harness 的三个自定义模式。**纯净模式零变化**：本 bundle 只 `insert` 自己的
preset 行，不修改任何 host 行。

| 模式 | preset id | row id | order | 定位 |
|---|---|---|---|---|
| OpenCode 迁移 · 标准 | `opencode-standard` | `preset-opencode-standard` | 11 | 日常调度 + 化用后的行为纪律 + 45 skill + 7 worker |
| OpenCode 迁移 · 创造 | `opencode-creator` | `preset-opencode-creator` | 12 | = 标准 + `tool-cordis` + 启用 `plugin_manager` + 作者技能目录 |
| OpenCode 迁移 · PTC | `opencode-ptc` | `preset-opencode-ptc` | 13 | = 标准 + `tool-presentation(mode: ptc)`，禁用 `workflow` |

---

## 1. 来源与基线

| 项 | 值 |
|---|---|
| 提示词源（只读） | `~/.config/opencode/instructions/*.md`（6 个）+ `MEMORY.md` + `opencode.jsonc` |
| skill 源（只读） | `~/.config/opencode/skills/`（45 个活跃；`disabled/` 下 4 个不在范围） |
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
`node_modules/@deepseek-ai/*`（全部是指向 DSH 源码树的符号链接）。本 bundle 用
`link_modules.py` 建立 28 个同样的链接（来源优先取 web-app 的嵌套 `node_modules`，实测 28/28 覆盖）。

```bash
cd ~/.dsh/presets/opencode
python3 link_modules.py          # 建立/刷新解析锚点
python3 link_modules.py --check  # 校验齐备
```

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

## 4. 与 opencode 的差异与损失（**不得声称保真**）

| # | opencode 规则 | DSH 近似后的实际 | 损失 |
|---|---|---|---|
| 1 | `bash` 命令级 deny + 前缀白名单 | 只有档位级 sandbox；`read-only` 档下 bash 仍可跑（只栅栏写） | **命令级 deny** |
| 2 | `read` 对 `auth.json` / `opencode.env` deny | 读一律放行 | **凭据文件可读** |
| 3 | `edit` 跨工作区 allow 列表 | `workspace-write` 只允许会话 cwd 内写 | 跨工作区写需提权 |
| 4 | worker `bash` 白名单（`git status *` 等）与「生产者自跑门控」 | `toolFilter` 整条禁掉 shell（fail-closed） | **worker 失去 git 只读与门控自跑** |
| 5 | `external_directory` allow/deny | 无 | 越界读写边界 |
| 6 | `skill` 加载前的权限门 | DSH 无 | 技能加载权限语义 |
| 7 | `question`/`todowrite`/`skill` 的 per-agent deny | `toolFilter` | 等价 |
| 8 | `task: deny`（worker 不自委派） | 各 worker 的 `toolFilter.deny`（deny 里含 `subagent`/`subagent_fork`/`workflow`/6 个 `oc_*`） | 等价 |
| 9 | 变体（Daily/Deep）、命令级 `/arch` `/rd` `/reflection` | 无 | 见 `ADAPTATION-NOTES.md` §1/§5 |
| 10 | 压缩模板 | 归 `dsh-compaction-basic`，preset 不可配置 | 无法自定义压缩行为 |

### 4.1 环境硬约束

**本机没有可用的沙箱后端**（bubblewrap 与 Landlock 均不可用）。后果：
`workspace-write` 档下 `bash` 被 fail-closed 拒绝。新模式要跑命令必须把会话权限档切到
`danger-full-access`，或先给宿主机装后端。**这是环境事实，不是迁移缺陷。**

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

> 本表由 `gen_status_table.py` **生成**（13 行），请勿手改；
> 改判据后重跑：`python3 gen_status_table.py --write`。
> 来源等级：**可复算** = 本轮现跑命令；**复算至产物** = 读机检产物重跑断言；
> **未复算** = 无自动化判据或本轮未跑（⚠️，不得当作 ✅）。

| 判据 | 状态 | 取证方式 | 来源等级 |
|---|---|---|---|
| 静态校验（13 项） | ✅ | `verify_bundle.py`（本轮现跑） → 13/13 项全通过 | ✅ 可复算 |
| 源指纹（活文件按被消费字段判） | ✅ | `build_provenance.py --check`（本轮现跑） → 19 provenance fingerprints | ✅ 可复算 |
| skill 派生（45 件 + 幂等重派生） | ✅ | `reconcile.py`（本轮现跑） → 45 件逐字节一致 | ✅ 可复算 |
| A1 三行 preset `enabled=true` 且无 broken | ✅ | `evidence/plugin-preset-rows.txt`（机检产物，可重跑断言）→ 3 行 enabled=true / active | ✅ 复算至产物 |
| A2 / A3 persona 内容与去重（运行时装配） | ✅ | `evidence/a12-persona-scope-evidence.json`（机检产物，可重跑断言）→ 3 个模式会话：persona 小节 15/15，host 正文泄漏 0；断言 25 条全通过 | ✅ 复算至产物 |
| A4 纯净 `standard` 零变化 | ✅ | `check_dump_purity.py`（本轮现跑） → 既有 4 个 preset 逐字节一致 | ✅ 可复算 |
| A5 / A6 skill 目录与渲染长度 | ⚠️ | 45 件 / 0 件超限为第一轮门控结论；本轮未复算（`install.py --gate-only` 需源目录只读副本）（留档：`evidence/skill-catalog-runtime.txt`） | ⚠️ 未复算 |
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
> 是**追加**而非替换（`includeDefaultRoots` 默认 `true`），因此新模式目录 = 45 个 opencode skill
> **+ 会话 cwd 项目根与用户根自带的 skill**（如 cwd 在 DSH 仓库内，还有 `.agents/skills` 的 16 件）。
> 这是**有意行为**：预设/项目 skill 本身也在「opencode 适配」的考虑范围内，故**不加**
> `includeDefaultRoots: false`。「45 件」指 opencode 派生目录本身，不是新模式会话的目录总数。

## 9. 文件清单

| 文件 | 角色 |
|---|---|
| `package.json` | bundle manifest（`dsh.bundle.patch`） |
| `cordis.patch.yml` | **生成物**：三个 preset 的完整声明 |
| `persona.md` | persona 正文的**规范副本**（唯一手写来源） |
| `build_bundle.py` | 生成 `cordis.patch.yml`（persona 展开 + worker persona 取自 `opencode.jsonc`） |
| `build_provenance.py` | 生成 `provenance.json` + `PROVENANCE.md`（含源指纹与漂移检测） |
| `link_modules.py` | 建立 `node_modules` 解析锚点（28 个包） |
| `verify_bundle.py` | **13 项**静态校验（安装前可跑） |
| `verify_rows.mjs` | 用**真实插件的 `Config`** 递归校验每个子行（含 group 内）；check 9 的引擎 |
| `verify_persona_scope.py` | **A12 取证**：host `personaPrefix`（七段纪律）对 preset 会话的作用域边界；check 13 的引擎 |
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
