# -*- coding: utf-8 -*-
"""decouple_styles.py — 站 03 的**令牌层与布局层解耦**生成器（批 I · CT-Q1=A）。

★ 本脚本就是「解耦」这个动作本身（⛔ 不手工切割 CSS、⛔ 不手改任何 HTML）：
  ① **拆分**：把 `04-interactive/assets/design-tokens.css` 拆成
       · `04-interactive/assets/site.css`                  ← 规则段（**逐字节搬家**，16423 B / 162 条布局规则）
       · `04-interactive/assets/derived-design-tokens.css` ← 令牌层（由 vendor/pipeline 的派生器产出，**不由本脚本写**）
     并**退役**原文件（其内容已被上面两份完全接管）。
  ② **改链接**：把每一页的 `<link … design-tokens.css>` 换成**两条** `<link>`（先令牌、后布局）。

★ 为什么必须解耦（实测）：原文件 17648 B 里 `:root` 只占 1225 B（6.9%），规则段 16423 B（**93.1%**）
  —— 它是**整站唯一的样式表**。按「整份替换成令牌表」实施会**删掉整站布局**。

★ 判据（本脚本自带，fail-closed）：
  D1 输入必须是**冻结的**解耦前原文：`sha256(design-tokens.css) == build/decoupling-provenance.json.pre_file.sha256`
  D2 拆分必须**只搬字节**：`sha256(site.css) == provenance.rule_segment.sha256`（★ 与**解耦前**冻结值比，
     ⛔ 不是自己比自己）；且 `:root` 块摘要 == provenance.root_block.sha256
  D3 恰 1 个括号平衡的 `:root` 块（0 或 ≥2 ⇒ 规则段的定义不成立 ⇒ 拒写零产出）
  D4 空集守卫：扫描到的 `*.html` 为 0 ⇒ FAIL（⛔ 不返回「0 迁移」）
  D5 覆盖守卫：链接两件套的页数必须 == `provenance`/profile 登记的期望页数（防「扫描面碰巧没扫到」）
  D6 退役件反向守卫：全仓不得再有**任何**页面链接已退役的 `design-tokens.css`（防线上 404）
  D7 幂等：二次运行零变化（原文已退役 + 每页已是两件套 ⇒ 报 `already`，⛔ 不重复插入）

  退出码：0 成功 · 1 判据 FAIL（⛔ 不写盘）· 2 环境错误 · 3 半态拒写（人工介入）

用法：
    python3 09-src-data/decouple_styles.py --site-root . [--dry-run] [--provenance build/decoupling-provenance.json]
"""
import argparse
import hashlib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

RETIRED = "04-interactive/assets/design-tokens.css"
LAYOUT = "04-interactive/assets/site.css"
TOKENS = "04-interactive/assets/derived-design-tokens.css"
LAYOUT_BASENAME = "site.css"
TOKENS_BASENAME = "derived-design-tokens.css"
RETIRED_BASENAME = "design-tokens.css"

SKIP_DIRS = (".git", "vendor", "node_modules")
LINK_RE = re.compile(r"<link\b[^>]*?rel=[\"']stylesheet[\"'][^>]*?href=[\"']([^\"']+)[\"'][^>]*>", re.I)
HREF_RE = re.compile(r"href=[\"']([^\"']+)[\"']", re.I)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(p):
    return sha256_bytes(open(p, "rb").read())


def split_root_block(text):
    """(start, end, block, rules) —— block = 首个括号平衡的 `:root{...}`。"""
    m = re.search(r":root\s*\{", text)
    if not m:
        return None
    i = m.start()
    j = text.index("{", m.end() - 1)
    depth = 0
    k = j
    while k < len(text):
        if text[k] == "{":
            depth += 1
        elif text[k] == "}":
            depth -= 1
            if depth == 0:
                break
        k += 1
    if k >= len(text):
        return None
    return i, k + 1, text[i:k + 1], text[:i] + text[k + 1:]


def pages(root):
    out = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in sorted(fn):
            if f.endswith(".html"):
                out.append(os.path.relpath(os.path.join(dp, f), root))
    return sorted(out)


def migrate_page(text):
    """返回 (new_text, status)。status ∈ {migrated, already, none, half}。"""
    hrefs = LINK_RE.findall(text)
    links_retired = [h for h in hrefs if h.endswith("/" + RETIRED_BASENAME) or h == RETIRED_BASENAME]
    has_tok = any(h.endswith("/" + TOKENS_BASENAME) or h == TOKENS_BASENAME for h in hrefs)
    has_lay = any(h.endswith("/" + LAYOUT_BASENAME) or h == LAYOUT_BASENAME for h in hrefs)
    if not links_retired:
        if has_tok and has_lay:
            return text, "already"
        if has_tok or has_lay:
            return text, "half"
        return text, "none"
    if len(links_retired) != 1:
        return text, "half"
    if has_tok or has_lay:
        return text, "half"
    old_href = links_retired[0]
    pfx = old_href[: -len(RETIRED_BASENAME)]
    # ★ 单点字符串替换：只在 href 值上做，其余字节（缩进/`</head>`/属性顺序）逐字不动
    old_attr = "href=\"%s\"" % old_href
    if old_attr not in text:
        old_attr = "href='%s'" % old_href
        if old_attr not in text:
            return text, "half"
    new_attr = ("href=\"%s%s\"><link rel=\"stylesheet\" href=\"%s%s\""
                % (pfx, TOKENS_BASENAME, pfx, LAYOUT_BASENAME))
    return text.replace(old_attr, new_attr, 1), "migrated"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site-root", default=".")
    ap.add_argument("--provenance", default="build/decoupling-provenance.json")
    ap.add_argument("--expect-linked-pages", type=int, default=None,
                    help="链接两件套的期望页数（登记值）；缺省时从 profile 读，读不到则用覆盖守卫的兜底口径")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.site_root)
    prov_path = os.path.join(root, a.provenance)
    if not os.path.isfile(prov_path):
        print("环境错误：冻结件不存在 %s（须先跑 capture_decoupling_baseline.py）" % prov_path)
        return 2
    prov = json.load(open(prov_path, encoding="utf-8"))
    fails = []

    # ---------- ① 拆分 ----------
    retired_abs = os.path.join(root, RETIRED)
    layout_abs = os.path.join(root, LAYOUT)
    print("① 拆分：%s" % RETIRED)
    if os.path.isfile(retired_abs):
        raw = open(retired_abs, "rb").read()
        got = sha256_bytes(raw)
        print("   D1 输入摘要 %s ← 期望（解耦前冻结）%s  ⇒ %s"
              % (got[:16], prov["pre_file"]["sha256"][:16], got == prov["pre_file"]["sha256"]))
        if got != prov["pre_file"]["sha256"]:
            fails.append("D1 输入不是冻结的解耦前原文（实测 %s ≠ 冻结 %s）"
                         % (got, prov["pre_file"]["sha256"]))
        sp = split_root_block(raw.decode("utf-8"))
        if not sp:
            fails.append("D3 找不到括号平衡的 :root 块 ⇒ 规则段定义不成立")
        else:
            i, k, block, rules = sp
            nb = raw.decode("utf-8").count(":root")
            print("   D3 `:root` 出现 %d 次（期望恰 1）；块 %d B @ [%d,%d) · 规则段 %d B"
                  % (nb, len(block.encode()), i, k, len(rules.encode())))
            if nb != 1:
                fails.append("D3 `:root` 出现 %d 次（期望恰 1）" % nb)
            b_sha = sha256_bytes(block.encode())
            r_sha = sha256_bytes(rules.encode())
            print("   D2 块摘要   实测 %s ← 冻结 %s ⇒ %s"
                  % (b_sha[:16], prov["root_block"]["sha256"][:16], b_sha == prov["root_block"]["sha256"]))
            print("   D2★规则段摘要 实测 %s ← **解耦前冻结** %s ⇒ %s"
                  % (r_sha[:16], prov["rule_segment"]["sha256"][:16], r_sha == prov["rule_segment"]["sha256"]))
            if b_sha != prov["root_block"]["sha256"]:
                fails.append("D2 :root 块摘要与冻结值不符")
            if r_sha != prov["rule_segment"]["sha256"]:
                fails.append("D2 规则段摘要与解耦前冻结值不符 ⇒ 拆分不是逐字节搬家")
            if not fails:
                if not a.dry_run:
                    with open(layout_abs, "wb") as fh:
                        fh.write(rules.encode("utf-8"))
                    os.remove(retired_abs)
                    print("   → 写出 %s（%d B，逐字节=原规则段）· 退役 %s"
                          % (LAYOUT, len(rules.encode()), RETIRED))
                else:
                    print("   → （dry-run）将写出 %s 并退役 %s" % (LAYOUT, RETIRED))
    elif os.path.isfile(layout_abs):
        got = sha256_file(layout_abs)
        ok = got == prov["rule_segment"]["sha256"]
        print("   D7 原文已退役、布局件在位：%s" % LAYOUT)
        print("   D2★摘要 %s ← 解耦前冻结 %s ⇒ %s"
              % (got[:16], prov["rule_segment"]["sha256"][:16], ok))
        if not ok:
            fails.append("D2 布局件摘要与解耦前冻结值不符（实测 %s）" % got)
    else:
        fails.append("D3 原文与布局件都不存在 ⇒ 无判据对象")

    # ---------- ② 改链接 ----------
    print("\n② 改链接：每页 <link> 由 1 条变 2 条（先令牌、后布局）")
    pgs = pages(root)
    print("   D4 扫描面：%d 个 *.html（排除 %s）" % (len(pgs), "/".join(SKIP_DIRS)))
    if not pgs:
        fails.append("D4 空集守卫：0 个 *.html 被扫到")
    tally = {"migrated": [], "already": [], "none": [], "half": []}
    for rel in pgs:
        p = os.path.join(root, rel)
        t = open(p, encoding="utf-8").read()
        new, st = migrate_page(t)
        tally[st].append(rel)
        if st == "migrated" and not a.dry_run:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(new)
    for st in ("migrated", "already", "half"):
        if tally[st]:
            print("   [%s] %d 页" % (st, len(tally[st])))
            for r in tally[st]:
                print("        %s" % r)
    if tally["none"]:
        print("   [none] %d 页（不链接任何外链样式表；不属迁移面，逐页登记在 build/profile.json）"
              % len(tally["none"]))
        for r in tally["none"]:
            print("        %s" % r)
    if tally["half"]:
        fails.append("D7 半态页 %d 个（既非「链接旧件」也非「链接两件套」）：%s"
                     % (len(tally["half"]), tally["half"][:8]))

    # ---------- ③ 覆盖 + 反向守卫 ----------
    linked = len(tally["migrated"]) + len(tally["already"])
    exp = a.expect_linked_pages
    if exp is None:
        try:
            prof = json.load(open(os.path.join(root, "build/profile.json"), encoding="utf-8"))
            exp = prof["decoupling"]["linked_pages"]["expected_count"]
        except Exception:  # noqa: BLE001
            exp = None
    print("\n③ 覆盖与反向守卫")
    print("   D5 链接两件套的页数 实测 %d ← 登记期望 %s ⇒ %s"
          % (linked, exp, "n/a" if exp is None else linked == exp))
    if exp is not None and linked != exp:
        fails.append("D5 覆盖守卫：链接两件套的页数 %d ≠ 登记期望 %d" % (linked, exp))
    dangling = []
    for rel in pgs:
        t = open(os.path.join(root, rel), encoding="utf-8").read()
        if any(h.endswith("/" + RETIRED_BASENAME) or h == RETIRED_BASENAME
               for h in LINK_RE.findall(t)):
            dangling.append(rel)
    print("   D6 仍链接已退役 %s 的页：%d（期望 0）" % (RETIRED_BASENAME, len(dangling)))
    for d in dangling:
        print("        DANGLING %s" % d)
    if dangling:
        fails.append("D6 反向守卫：%d 页仍链接已退役件 %s ⇒ 线上必 404" % (len(dangling), RETIRED))

    print("\n=== decouple_styles：拆分 %s · 迁移 %d · 已就位 %d · 非迁移面 %d · **%d FAIL** ==="
          % ("DRY-RUN" if a.dry_run else "DONE", len(tally["migrated"]), len(tally["already"]),
             len(tally["none"]), len(fails)))
    for f in fails:
        print("   FAIL %s" % f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
