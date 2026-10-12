# PROVENANCE · dsh-opencode-port bundle

- 源（只读，单一真相源）：`/home/zako-mio/.config/opencode`
- persona 正文的规范副本：`persona.md`（`cordis.patch.yml` 由 `build_bundle.py` 从它展开）
- 指纹策略：**构建期快照 + 漂移告警**。`verify_bundle.py` 会重算下方 sha256；
  源侧改动不会被静默继承，而会让校验失败并要求显式重建。

## persona 段落溯源

| persona 段落 | 源文件 | 变换 | 源行数 | 源 sha256(前12) |
|---|---|---|---|---|
| 一、调度者定位与复杂度自评 | `~/.config/opencode/instructions/auto-mode.md` | rewritten | 282 | `d204b86d6f13` |
| 二、委派纪律 | `~/.config/opencode/instructions/agent-protocol.md` | rewritten | 83 | `125ef86d3897` |
| 二、委派纪律（返回契约补充） | `~/.config/opencode/instructions/auto-mode.md` | verbatim | 282 | `d204b86d6f13` |
| 三、子 Agent 约束 | `~/.config/opencode/instructions/auto-mode.md` | rewritten | 282 | `d204b86d6f13` |
| 四、编码安全 | `~/.config/opencode/instructions/agent-protocol.md` | rewritten | 83 | `125ef86d3897` |
| 五、验证与证据 | `~/.config/opencode/instructions/auto-mode.md` | rewritten | 282 | `d204b86d6f13` |
| 六、故障自愈 | `~/.config/opencode/instructions/auto-mode.md` | verbatim | 282 | `d204b86d6f13` |
| 七、缓存与并行 | `~/.config/opencode/instructions/auto-mode.md` | rewritten | 282 | `d204b86d6f13` |
| 八、环境事实 | `~/.dsh/profiles/web/cordis.patch.yml` | rewritten | 373 | `70d7abf72773` |
| 九、留档规范 | `~/.config/opencode/instructions/agent-protocol.md` | rewritten | 83 | `125ef86d3897` |
| 十、记忆纪律 | `~/.config/opencode/instructions/auto-mode.md` | rewritten | 282 | `d204b86d6f13` |
| 十一、搜索行为 | `~/.config/opencode/instructions/search-behavior.md` | verbatim | 22 | `71769f677042` |
| 十二、架构行为 | `~/.config/opencode/instructions/architecture-behavior.md` | rewritten | 74 | `732fe6fa6a14` |
| 十三、需求发现行为 | `~/.config/opencode/instructions/requirement-discovery-behavior.md` | rewritten | 20 | `85764851fff5` |
| 十四、视觉与出图归位 | `~/.config/opencode/instructions/agent-protocol.md` | rewritten | 83 | `125ef86d3897` |
| 十五、迁移适配注记 | `~/.config/opencode/instructions/auto-mode.md 等` | summary | 282 | `d204b86d6f13` |

### 变换说明

- **一、调度者定位与复杂度自评**（rewritten）：自评四维表逐字保留；删除强制门控字面输出格式、变体切换、成本对比表、决策边界表
- **二、委派纪律**（rewritten）：保留 5 步委派流程与 JSON 返回字段；删除角色检索脚本步骤；工具名改 DSH
- **二、委派纪律（返回契约补充）**（verbatim）：子 Agent 结构化 JSON 字段逐字保留
- **三、子 Agent 约束**（rewritten）：保留不委派 / 禁改记忆 / 结构化返回；补「无用户发问通道」
- **四、编码安全**（rewritten）：保留 5 条；删除「切 Build 模式」；补注 DSH 侧无命令级硬拒绝
- **五、验证与证据**（rewritten）：保留验证证据 / 路径本地化 / 元数据不入输出；「从磁盘读」改为强调依赖文件
- **六、故障自愈**（verbatim）：工具失败 3 次阶梯 + 子 Agent 非 JSON 处理逐字保留
- **七、缓存与并行**（rewritten）：压缩为各一句；删除 MCP 工具发现段与具体阈值
- **八、环境事实**（rewritten）：**2026-10-12 起**：机器特定事实已外迁至 `dsh-config` 技能的 `local/host-env-facts.md`（单一承载处）；本节只留「唯一指针 + 被判据直接提取的第 7 条」。第 7 条（外部 CLI 不在会话 PATH 上）的引导串是 check 17 的判据来源，⛔ 不得搬走或复制
- **九、留档规范**（rewritten）：5 段模板与三门控保留；发问工具改为 ask_user_question
- **十、记忆纪律**（rewritten）：保留 MEMORY.md 只读纪律；队列工具链缺失按实测收窄登记（候选产出通道仍在）；补「不常驻上下文」理由
- **十一、搜索行为**（verbatim）：整节逐字保留（含时效性准则）
- **十二、架构行为**（rewritten）：保留规模三问 / 知识分层 / 产出契约；/arch 与 architect-worker 改写；门控执行方由窄通道 run_gate 承担（ADR-010）
- **十三、需求发现行为**（rewritten）：/rd 改为点名触发；$TIER_TOOL 展开为绝对路径；worker 名改写
- **十四、视觉与出图归位**（rewritten）：保留出图归位与视觉降级规则；pdf-worker 改写为 oc_pdf；标注未挂 MCP
- **十五、迁移适配注记**（summary）：汇总 01 号调研 B 表的「冲突 / 不可实现 / 重复删除」条目；详表见 ADAPTATION-NOTES.md

## 直接搬运

| 项 | 源 | 变换 | 源行数 | 源 sha256(前12) |
|---|---|---|---|---|
| worker persona ×7 | `~/.config/opencode/opencode.jsonc` | verbatim | 806 | `8b29dd21d445` |
| plan-mode section | `~/.dsh/profiles/node_modules/@deepseek-ai/dsh-web-app/presets/standard.patch.yml` | rewritten | 138 | `6462f63e24ea` |

- **worker persona ×7**：agent.<name>.description 逐字用作对应 worker 的 persona
- **plan-mode section**：DSH 原文逐字保留，末尾追加 3 行 opencode 逐题访谈指引（指向 grill-me skill）

## 明确未迁移

| 源文件 | 理由 |
|---|---|
| `~/.config/opencode/instructions/browser-management.md` | DSH web profile 无浏览器标签页通道（close-chrome-tabs.ps1 不存在）→ 整件不适用 |

## 刷新方式

```bash
cd ~/.dsh/presets/opencode
python3 build_provenance.py      # 重算指纹并重写本文件
python3 build_bundle.py          # persona.md / opencode.jsonc 变更后重建 cordis.patch.yml
python3 verify_bundle.py         # 全量静态校验（含漂移检测）
```

## 回滚

`plugin_manager remove_bundle dsh-opencode-port` + 还原
`~/.dsh-backups/opencode-port-20261011/cordis.patch.yml`。详见 `README.md`。
