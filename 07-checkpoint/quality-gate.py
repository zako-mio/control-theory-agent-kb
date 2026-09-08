# -*- coding: utf-8 -*-
"""结构层门控: JSON合法/HTML断链/证据区块/覆盖度审计"""
import json, glob, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = "/home/zako-mio/opencode/archive/Mission-file/2026-09/0907-控制理论Agent设计知识库"
issues = []
warnings = []

# 1. JSON 合法性(仅本库产物, 排除 05-source 第三方源码——tsconfig 允许注释, 非标准 JSON)
for jp in glob.glob(os.path.join(BASE, "**/*.json"), recursive=True):
    rel = os.path.relpath(jp, BASE)
    if rel.startswith("05-source") or rel.startswith("03-cases/source"):
        continue  # 第三方源码/pnpm 锁, 非本库交付物
    try:
        json.load(open(jp, encoding="utf-8"))
    except Exception as e:
        issues.append(f"JSON非法: {rel} -> {e}")
kb_json = [os.path.relpath(jp,BASE) for jp in glob.glob(os.path.join(BASE,"**/*.json"),recursive=True) if not os.path.relpath(jp,BASE).startswith("05-source") and not os.path.relpath(jp,BASE).startswith("03-cases/source")]
print("[1] JSON 合法性检查完成 (本库json数=%d, 已排除第三方源码)" % len(kb_json))

# 2. HTML 断链检查(引用本地 vendor/资源) - 仅本库产物
html_files = glob.glob(os.path.join(BASE, "04-interactive/*.html")) + [os.path.join(BASE,"index.html")]
html_files = [h for h in html_files if os.path.exists(h)]
for hf in html_files:
    c = open(hf, encoding="utf-8").read()
    rel = os.path.relpath(hf, BASE)
    # 检查 script src 引用是否存在
    for m in re.findall(r'src="([^"]+)"', c) + re.findall(r'href="([^"]+)"', c):
        if m.startswith("http") or m.startswith("#") or m.startswith("data:"):
            continue
        if m.startswith("./vendor/"):
            vpath = os.path.join(os.path.dirname(hf), m[2:])
            if not os.path.exists(vpath):
                issues.append(f"HTML断链: {rel} 引用缺失 {m}")
            else:
                print(f"   [OK] {rel} vendor {m} 存在")
print("[2] HTML 断链检查完成 (html=%d)" % len(html_files))

# 3. 证据区块完整性(理论 MD 每个知识点应有 📚 证据来源)
for tmd in glob.glob(os.path.join(BASE, "01-theory/*.md")):
    c = open(tmd, encoding="utf-8").read()
    kts = re.findall(r'^## (KT-ctrl-\d{3})', c, re.M)
    evidence = c.count("📚 证据来源")
    rel = os.path.relpath(tmd, BASE)
    if len(kts) != evidence:
        warnings.append(f"{rel}: 知识点KT数={len(kts)} 但证据区块数={evidence} (应相等)")
    else:
        print(f"   [OK] {rel} KT={len(kts)} 证据区块={evidence}")
print("[3] 证据区块完整性检查完成")

# 4. 覆盖度审计(全部交付物齐全)
required = [
    "00-contract/contract.md",
    "01-theory/01-closed-loop.md","01-theory/02-state-est.md","01-theory/03-pid.md",
    "01-theory/04-robust.md","01-theory/05-hierarchical.md",
    "02-framework/framework.md",
    "03-cases/opencode.md","03-cases/deepseek-harness.md","03-cases/prime.md",
    "03-cases/hermes.md","03-cases/claude-code.md","03-cases/codex.md",
    "04-interactive/index.html",
    "05-md/00-index.md",
    "06-experiments/README.md","06-experiments/opencode.md","06-experiments/deepseek-harness.md","06-experiments/prime.md",
    "06-experiments/hermes.md","06-experiments/claude-code.md","06-experiments/codex.md",
    "08-drawio/five-ring-loop.drawio","08-drawio/five-ring-loop.png",
    "08-drawio/ctrl-agent-mapping.drawio","08-drawio/ctrl-agent-mapping.png",
    "README.md","index.html","report.md","report.html",
]
missing = [r for r in required if not os.path.exists(os.path.join(BASE, r))]
if missing:
    issues.append(f"覆盖度缺失: {missing}")
else:
    print(f"[4] 覆盖度审计通过 (required={len(required)} 全部存在)")

# 5. 精装房交付物覆盖度(v1.1)
PREMIUM_SLUGS = ["cursor","devin","workbuddy","windsurf","copilot","dify","openhands",
                 "coze","openclaude","codewhale","gptresearcher","qcode","ccrouter","crewai"]
premium_required = ["03-cases/premium-%s.md"%s for s in PREMIUM_SLUGS] + \
                   ["04-interactive/premium-%s.html"%s for s in PREMIUM_SLUGS] + \
                   ["04-interactive/premium-map.html","04-interactive/premium-cyto.html",
                    "07-checkpoint/premium-evidence.md","07-checkpoint/premium-diff-analysis.md"]
pm_missing = [r for r in premium_required if not os.path.exists(os.path.join(BASE, r))]
if pm_missing:
    issues.append(f"精装房覆盖度缺失: {pm_missing}")
else:
    print(f"[5] 精装房覆盖度审计通过 ({len(premium_required)} 文件全部存在)")

# 6. 精装房案例页环结构校验(SP+E/T/M/P/R 齐全 + 精装度区块)
for s in PREMIUM_SLUGS:
    hp = os.path.join(BASE,"04-interactive","premium-%s.html"%s)
    if not os.path.exists(hp): continue
    c = open(hp, encoding="utf-8").read()
    need = ['id="premium-score"','id="ring-SP"','id="ring-E"','id="ring-T"','id="ring-M"','id="ring-P"','id="ring-R"']
    miss = [n for n in need if n not in c]
    if miss:
        issues.append(f"精装房页面结构缺失: premium-{s}.html 缺 {miss}")
    # 未渲染 markdown 残留检查
    if re.search(r'\*\*[^*\n]+\*\*', c):
        warnings.append(f"premium-{s}.html 可能残留未渲染 **markdown** 标记")
print("[6] 精装房案例页结构校验完成")

# 7. 导航链接完整性(全站 HTML 的 .html 内链是否指向存在的文件)
nav_issues = []
for hf in html_files:
    c = open(hf, encoding="utf-8").read()
    rel = os.path.relpath(hf, BASE)
    for m in re.findall(r'href="([^"#]+\.html)"', c):
        if m.startswith("http"): continue
        # 排除 JS 动态拼接字符串(含 + 或 ' 或 ${ 的模板片段)
        if any(ch in m for ch in ["+", "'", "${", "\\"]):
            continue
        target = os.path.join(os.path.dirname(hf), m)
        if not os.path.exists(target):
            nav_issues.append(f"{rel} -> 死链 {m}")
if nav_issues:
    for n in nav_issues: issues.append(f"导航死链: {n}")
else:
    print("[7] 导航链接完整性通过 (无死链)")
print("[6/7] 精装房结构+导航检查完成")

print()
print("="*60)
print("结构门控结果:")
print("  问题(issues):", len(issues))
for i in issues: print("   ❌", i)
print("  提醒(warnings):", len(warnings))
for w in warnings: print("   ⚠️", w)
print("="*60)

# 落地结果
with open(os.path.join(BASE,"07-checkpoint","quality-gate-result.txt"),"w",encoding="utf-8") as f:
    f.write("ISSUES=%d\nWARNINGS=%d\n"%(len(issues),len(warnings)))
    for i in issues: f.write("ISSUE: %s\n"%i)
    for w in warnings: f.write("WARN: %s\n"%w)
print("结果已写入 07-checkpoint/quality-gate-result.txt")
sys.exit(0 if not issues else 1)
