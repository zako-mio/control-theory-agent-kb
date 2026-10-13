# -*- coding: utf-8 -*-
"""gen_coverage_manifest.py — 生成 L6 覆盖度层的**显式期望清单**（入库，替代 v1.3 的 /tmp 临时件）

动机（v1.3 教训）：v1.3 的 coverage manifest 是 `/tmp/opencode/kb-gate/coverage-manifest-v1.3.txt`，
既不入库也不可复现；本脚本把它改为「从 nav_data.NAV（期望页面）+ 显式非页面交付物清单」派生，
写入 `07-checkpoint/coverage-manifest.txt` 并入库 ⇒ 缺件会被 coverage 层**真实判失败**，而不是静默跳过。

用法：
    python3 07-checkpoint/gen_coverage_manifest.py            # 写出清单 + 自检缺件
    python3 07-checkpoint/gen_coverage_manifest.py --check    # 只自检，不写文件
"""
import os, sys, glob
sys.stdout.reconfigure(encoding='utf-8')

KB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ★ 本地化：仓库根由本文件位置推导（⛔ 不硬编码作者机路径）
OUT = os.path.join(KB, "07-checkpoint/coverage-manifest.txt")

sys.path.insert(0, os.path.join(KB, "09-src-data"))
import nav_data  # noqa: E402

# ---- 1) 期望页面：nav_data.NAV 的每一项（portal 对应根 index.html）----
# NAV 元组形状 = (标签, 文件名, 分组)
pages = []
for item in nav_data.NAV:
    fn = item[1] if isinstance(item, (list, tuple)) and len(item) >= 2 else str(item)
    if fn in ("portal", "index-root"):
        pages.append("index.html")
    elif fn.endswith(".html"):
        pages.append("04-interactive/" + fn)
    else:
        pages.append("04-interactive/" + fn + ".html")

# ---- 2) 非页面交付物（显式期望清单；新增交付物必须登记在此）----
explicit = [
    # 契约与门户
    "00-contract/contract.md", "README.md", "index.html", "report.html", "report.md",
    # 理论证据包
    "01-theory/01-closed-loop.md", "01-theory/02-state-est.md", "01-theory/03-pid.md",
    "01-theory/04-robust.md", "01-theory/05-hierarchical.md",
    # 框架
    "02-framework/framework.md",
    # 画像：6 框架
    "03-cases/prime.md", "03-cases/deepseek-harness.md", "03-cases/opencode.md",
    "03-cases/hermes.md", "03-cases/claude-code.md", "03-cases/codex.md",
    # 画像：2 自改造变体 + 对照
    "03-cases/opencode-custom.md", "03-cases/opencode-custom-diff.md",
    "03-cases/dsh-custom.md", "03-cases/dsh-custom-diff.md",
    # AI 索引
    "05-md/00-index.md",
    # 实验组：6 框架 + 2 变体
    "06-experiments/prime.md", "06-experiments/deepseek-harness.md", "06-experiments/opencode.md",
    "06-experiments/hermes.md", "06-experiments/claude-code.md", "06-experiments/codex.md",
    "06-experiments/opencode-custom.md", "06-experiments/dsh-custom.md",
    # 门控与评分
    "07-checkpoint/kb_gate.py", "07-checkpoint/quality-gate.py",
    "07-checkpoint/premium-scoring-model.md", "07-checkpoint/premium-score-recompute.md",
    "07-checkpoint/premium-evidence.md", "07-checkpoint/premium-diff-analysis.md",
    "07-checkpoint/PREMIUM-CASE-TEMPLATE.md", "07-checkpoint/check_premium_consistency.py",
    "07-checkpoint/snapshot_opencode_custom.py", "07-checkpoint/snapshot_dsh_custom.py",
    "07-checkpoint/coverage-manifest.txt",
    # 评分单一数据源与生成脚本
    "09-src-data/premium_scores.py", "09-src-data/opencode_custom_scores.py",
    "09-src-data/dsh_custom_scores.py", "09-src-data/apply_premium_scores.py",
    "09-src-data/gen_html.py", "09-src-data/nav_data.py", "09-src-data/gen_cyto.py",
    "09-src-data/fix_cyto.py", "09-src-data/gen_premium_cyto.py", "09-src-data/gen_dag_data.py",
    "09-src-data/render_case.py", "09-src-data/render_exp.py", "09-src-data/render_framework.py",
    "09-src-data/five-ring-dag.json", "09-src-data/kt_details.json",
]

# ---- 3) 精装房画像（14 产品，按 premium_scores 动态取，避免写死）----
try:
    sys.path.insert(0, os.path.join(KB, "09-src-data"))
    import premium_scores as ps
    premium = ["03-cases/premium-%s.md" % p["slug"] for p in ps.PRODUCTS]
except Exception as e:
    premium = []
    print("warn: 精装房清单动态派生失败：%s" % e)

items = []
for p in pages + explicit + premium:
    if p not in items:
        items.append(p)

missing = [p for p in items if not os.path.exists(os.path.join(KB, p))]

check_only = "--check" in sys.argv
if not check_only:
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# 交付物期望清单（L6 覆盖度层）— 由 07-checkpoint/gen_coverage_manifest.py 派生\n")
        f.write("# 期望页面取自 09-src-data/nav_data.py 的 NAV；非页面交付物为脚本内显式清单\n")
        f.write("# 缺件 = 交付缺失，coverage 层必须 FAIL；新增交付物须在脚本的 explicit 列表登记\n")
        for p in items:
            f.write(p + "\n")

print("清单项数: %d（期望页面 %d + 非页面 %d + 精装房 %d，去重后 %d）"
      % (len(items), len(pages), len(explicit), len(premium), len(items)))
print("缺失: %d" % len(missing))
for m in missing:
    print("  MISSING", m)
if not missing:
    print("OK: 全部期望交付物存在")
print("写入:", OUT if not check_only else "(仅自检，未写)")
