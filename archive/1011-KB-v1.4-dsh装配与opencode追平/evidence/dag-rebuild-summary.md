# opencode-dag 库重建摘要（2026-10-11）

库：`/home/zako-mio/opencode/archive/Mission-file/2026-09/0902-opencode-dag`（remote `zako-mio/opencode-dag-analysis`）
有效脚本链：`08-collect/`（v2 链）；`07-checkpoint/` 同名脚本为 0817/0902 旧链，勿混跑。

## 官方侧点检
- `git fetch --depth=1 origin refs/tags/v1.18.35` → 包级结构**零变化**（36 包 / 32 顶层目录，包集合 diff 完全一致）
- 文件变更量：29→30 = 105 files +1676/−403（与 KB 既有记录吻合）；29→35 = 328 files +17411/−8779；30→35 = 318 files +15961/−8602
- 结论：官方只需**版本标注** v1.18.30 → v1.18.35，包图（36 包 / 68 边）不变

## 装配层重建
- 活体采集 `s2-assembly-inventory.py`：**68 组件**（skill 46 / agent 9 / mcp 4 / instruction 6 / command 3）
- 合并 `s2-merge-assembly.py`：**87 组件**（+ mechanism 18 + config 1）
- 相对 0911：83 → 87（skills 41→46、agents 10→9、mcp 6→4、instr 5→6、cmd 2→3、mech 18 不变）

## 数据与产物
| 指标 | 0911 | 本轮 |
|---|---|---|
| modified 节点 | 129 | **133**（36 包 + 87 装配 + 10 外部） |
| modified 边 | 190 | **177**（悬空清洗 189→177） |
| 组 | 43 | **42** |
| diff 图 | 46/68/20 | 46/68/20（不变） |
| diff-list | 90 | **94** |
| 节点页 / 组页 | 129 / 43 | **133 / 42**（+index） |
- 重生成删除陈旧节点页 7 个、陈旧组页 1 个（A6b）

## 门控与验证
- `08-collect/quality-gate.py`：**33/33 ALL PASS**；期望值改为从 `modified-dag.json` 的 `stats` **动态读取**（黄金值仅兜底 + `# GOLDEN:` 注释），新增「不得为 0」非空断言
- `07-checkpoint/headless-final-v11829.py`：**ALL OK**（zcount 36/46/133、三图截图 255–276 KB、节点页 h2=6）
  - 修复：`CHROME="chromium-browser"` 写死 → `detect_browser()` 自动探测（snap chromium 在容器内缺 cap_dac_override 无法启动）

## 未做（如实登记）
1. 2 个新插件未入图（pipeline 无 `plugin` kind）
2. `05-drawio/` 主图与关键装配图未重生成（无生成脚本，手工产物）
3. 内部模块 import 数据仍用 `internal-v1.18.29.json`（包集合未变、core 仅 10 文件变更）
4. `build-dag.py` 仍保留引用已退役组件的旧规则（悬空边由清洗丢弃，不影响 133/177）
5. 委派名单未含新增 `agent-requirement-discovery-worker`
