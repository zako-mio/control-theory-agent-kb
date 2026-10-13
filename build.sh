#!/bin/sh
# ============================================================================
# build.sh — 站 03 `control-theory-agent-kb` 的**构建入口**（批 I · 标准档）
#
# ★ 为什么不接 CI：本站属 ADR-003 的**无 CI 5 站**之一，且「发布形态收敛」是项目的
#   **常设排除项** ⇒ 本轮 ⛔ 不新建 CI。门控改为**在生成脚本收尾处内联调用**，
#   并把**确定性** `gate-report.json` 随产物入库 —— 使「跑没跑过」有痕迹。
#
# ★ 幂等：本脚本的全部步骤都是纯函数（无时钟、无随机、不联网、不读仓外输入），
#   连跑两遍第二遍**零字节变化**（判据：`git status --porcelain` 为空）。
#
# ★ 顺序是有意的：
#   ① 数据 → ② 交互页 → ③ 首页/案例/实验/精装房页 → ④ **解耦**（拆 CSS ＋ 改 `<link>`）
#   → ⑤ 由值件**派生**令牌文件 → ⑥ 覆盖度清单与结构门控 → ⑦ **门控内联调用**
#   ④必须在⑤之前：解耦先落地令牌层与布局层的**分离**，派生再把令牌层写进新文件。
# ============================================================================
set -e
cd "$(dirname "$0")"

echo "=== [1/7] 数据层：五环 DAG ==="
python3 09-src-data/gen_dag_data.py

echo "=== [2/7] 交互页：index_cyto.html（生成 + 幂等后处理）==="
python3 09-src-data/gen_cyto.py
python3 09-src-data/fix_cyto.py

echo "=== [3/7] 页面集群：premium-cyto.html + 40 个页面族页 ==="
python3 09-src-data/gen_premium_cyto.py
python3 09-src-data/gen_html.py

echo "=== [4/7] 解耦：令牌层与布局层分离（拆分 CSS ＋ 每页 <link> 两件套）==="
echo "    ★ 判据：sha256(site.css) == 解耦前冻结的规则段 sha256（改一个字节即 FAIL）"
python3 09-src-data/decouple_styles.py --site-root .

echo "=== [5/7] 派生：值件 → build/payloads/default.css → 04-interactive/assets/derived-design-tokens.css ==="
python3 vendor/pipeline/derive_site_tokens.py \
  --contract vendor/pipeline/values/control-theory-agent-kb.json \
  --profile build/profile.json --family default \
  --out build/payloads/default.css --apply
python3 vendor/pipeline/write_site_tokens.py \
  --profile build/profile.json --payloads build/payloads --site-root . --apply

echo "=== [6/7] 覆盖度清单与既有结构门控 ==="
python3 07-checkpoint/gen_coverage_manifest.py
python3 07-checkpoint/quality-gate.py

echo "=== [7/7] ★ 站点侧门控（内联调用；无 CI ⇒ 这就是「跑没跑过」的痕迹）==="
python3 gate_tokens.py --site-root . --manifest gate-manifest.json \
  --mode enforce --report gate-report.json
python3 vendor/pipeline/check_gate_manifest.py \
  --manifest gate-manifest.json --profile build/profile.json

echo "=== 构建完成：门控已跑并写出确定性 gate-report.json ==="
