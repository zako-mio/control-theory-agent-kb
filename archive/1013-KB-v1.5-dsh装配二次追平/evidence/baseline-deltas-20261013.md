# 取证记录 — KB v1.5 前期摸底实测读数

> 任务：`1013-v1.5-dsh装配二次追平`
> 采集人：主 Agent　采集日期：2026-10-13
> 性质：**点时读数**。`as_of` 见各节；他线（迁移线）可能并发变更 ⇒ 下游引用一律以实跑为准。
> 本件为 `PLAN-v1.5.md` 与 `report.md` 中数值的溯源凭据，含所用命令，可复算。

---

## 一、采集时点

| 项 | 值 |
|---|---|
| 会话起点 | 2026-10-13 02:35:55 +0800 |
| 主要读数时点 | 2026-10-13 02:36–02:52 +0800 |
| v1.4 快照点（比对基准） | 2026-10-11T17:09:09+08:00 |
| 分析对象是否静止 | **否**（迁移线 R11 进行中，见 §五） |

---

## 二、文件级差量（快照 vs 现盘）

命令（主 Agent 实测）：

```bash
SN=<KB>/07-checkpoint/dsh-custom-snapshot
B=~/.dsh/presets/opencode
for f in cordis.patch.yml README.md ADAPTATION-NOTES.md persona.md provenance.json PROVENANCE.md package.json; do
  echo "$f $(wc -c < "$SN/bundle__$f") $(wc -c < "$B/$f")"
done
wc -c "$SN/profile__web-cordis.patch.yml" ~/.dsh/profiles/web/cordis.patch.yml
```

读数：

| 文件 | 快照字节 | 现盘字节 | 快照行数 | 现盘行数 | 判定 |
|---|---:|---:|---:|---:|---|
| bundle `cordis.patch.yml` | 93283 | 85501 | 1305 | 1299 | 变化 |
| bundle `README.md` | 22168 | 40812 | 324 | 530 | 变化 |
| bundle `ADAPTATION-NOTES.md` | 9108 | 10913 | 85 | 86 | 变化 |
| bundle `persona.md` | 15403 | 12066 | 160 | 127 | 变化 |
| bundle `provenance.json` | 11907 | 12209 | 261 | 281 | 变化 |
| bundle `PROVENANCE.md` | 5692 | 5994 | — | 76 | 变化（内容差异待复核 U3） |
| bundle `package.json` | 392 | 392 | 13 | 13 | 未变 |
| profile `cordis.patch.yml` | 17538 | 25569 | 282 | 372 | 变化 |

---

## 三、装配行 / 插件行集合差

命令：

```bash
grep -oE "^[[:space:]]*- id: .*" <快照 cordis.patch.yml> | sed 's/^[[:space:]]*//' | sort -u > /tmp/snap_ids.txt
grep -oE "^[[:space:]]*- id: .*" <现盘 cordis.patch.yml>      | sed 's/^[[:space:]]*//' | sort -u > /tmp/cur_ids.txt
comm -13 /tmp/snap_ids.txt /tmp/cur_ids.txt   # 新增
comm -23 /tmp/snap_ids.txt /tmp/cur_ids.txt   # 移除
```

| 面 | 快照唯一 id 数 | 现盘唯一 id 数 | 新增 | 移除 |
|---|---:|---:|---|---|
| bundle `cordis.patch.yml` | 42 | 43 | `gate-runner` | 无 |
| profile `cordis.patch.yml` | 17 | 19 | `agent-preset-registry`、`dsh-wsl-desktop-path` | 无 |

profile 顶层 key 集合：快照与现盘**逐条一致**（`diff` 无输出）。

---

## 四、计数类读数

| 指标 | 快照口径 | 实测现盘 | 命令 |
|---|---:|---:|---|
| 派生 skill（主根，含 SKILL.md） | 45 | **49** | `find ~/.dsh/skills/opencode -maxdepth 2 -name SKILL.md -not -path '*/_overlay/*' \| wc -l` |
| `_overlay` 技能 | 6 | **7** | `find ~/.dsh/skills/opencode/_overlay -maxdepth 2 -name SKILL.md \| wc -l` |
| SKILL.md 总数 | 51 | **55** | `find ~/.dsh/skills/opencode -maxdepth 3 -name SKILL.md \| wc -l` |
| `verify_bundle.py` 判据项 | 13 | **19** | 读 `CHECK_TITLES`（`verify_bundle.py:48-68`） |
| persona 小节数 | 15 | **15** | `grep -cE '^## ' persona.md` |
| 具名 worker（`oc_*`） | 6 | **6** | `grep -oE 'oc_[a-z_]+' persona.md \| sort -u` |
| `~/.dsh/plugins/` 本地插件 | — | **1**（`dsh-wsl-desktop-path`） | `ls ~/.dsh/plugins/` |
| bundle 内插件包 | — | **1**（`dsh-opencode-gate-runner`） | `ls ~/.dsh/presets/opencode/plugins/` |

**口径分歧（须在 P0 归一）**：同一事实四套读数并存 —— 快照 `inventory.json` 45 / bundle `README.md` 46 / `reconcile` 47 / 本件实测主根 49。

`verify_bundle.py` 的 19 项 `CHECK_TITLES`（P2 须收录为证据）：

1. `package.json`　2. `cordis.patch.yml` 结构　3. persona 与 persona.md 一致性　4. persona 禁用字面量与插值变量　5. 插件名可解析（bundle 平面）　6. toolFilter 求值为扁平字符串数组且名字已知　7. worker 编队　8. 三模式差异　9. 子行 config 通过真实插件 Config schema　10. node_modules 锚点　11. 源指纹漂移　12. 生成幂等　13. A12 host personaPrefix 作用域取证　14. 门控执行通道 run_gate　15. 真实挂载审计　16. 工具 output.schema / parameters 子集校验　17. 会话 PATH 引导（外部 CLI 可达性）　18. dsh-config 声明账本漂移　19. 迁移状态（E3 residue / 陈旧断言 / E7 互斥 / R 环载体）+ 判据自检

---

## 五、时序与静止点判定

命令：

```bash
stat -c '%y %s' ~/.dsh/presets/opencode/verify_migration_state.py
# 02:40:26 → 45470 B；02:40:35 → 49212 B；02:40:45 → 50893 B；02:48:55 → 58080 B
```

| 时点 | 观测 | 判定 |
|---|---|---|
| 2026-10-12 19:13:41 | `迁移台账.yaml` 落笔（27166 B） | 迁移线第 10 轮收尾 |
| 2026-10-13 02:37 | `r11-caps-ledger.out.txt`（521 B） | 第 11 轮取证 |
| 2026-10-13 02:39 | `r11-audit-unify.out.txt`（469 B） | 第 11 轮取证 |
| 2026-10-13 02:40–02:48 | `verify_migration_state.py` 45470 → 58080 B | **仍在写入，非静止** |

结论：用户裁定的 D3 条件（第 10 轮落地）已满足，但该线已进入 R11 且未收尾 ⇒ **取快照前须重判静止点**。

---

## 六、来源与限制

- 全部读数来自本机磁盘（`~/.dsh/**`、知识库仓库、迁移线任务目录），**未联网**；
- 对 `~/.dsh/**` 与迁移线目录**全程只读**，本轮 0 写入；
- `~/.dsh/profiles/web/cordis.patch.yml` 与 bundle 的语义层对账（`reasoningEfforts` 三档、`defaultPreset` read-only → opencode-plan、maxTokens 回调）由只读探索子 Agent 逐段通读得出，**本轮未逐字复核**，P2 须以现盘重读为准；
- `PROVENANCE.md` 字节微增但内容判定为「逐行同文」，两者矛盾未解（未决项 U3）；
- 迁移线的 `r11` 取证件在采集时点仍在生成，其结论仅作**指针**引用，未纳入本件读数。
