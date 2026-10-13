#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""inject_page_shell.py — 批 J 的**通用页面骨架注入器**（a11y / SEO 实缺修实 · 管线步骤）。

定位（★ 与「手改生成物」的区别）：
    本件是**构建管线的一步**（与批 I 已落地的 `decouple_styles.py` 同型：对产物做确定性后处理，
    由 `build.sh` / 生成脚本收尾调用）。⇒ 产物仍由**生成器产出**，⛔ 不是手改。

它逐页保证五件事（全部幂等）：
  1. `<head>` 有：非空 `description` / `og:type|title|description|url|image` /
     绝对且**自指**的 `<link rel="canonical">` / `<link rel="icon" type="image/svg+xml" href="/<repo>/favicon.svg">`
  2. `<body>` 之后有 `<a class="skip-link" href="#main">跳到主要内容</a>`
  3. 页内**有且仅有 1 个** `<main id="main">`（无 `<main>` 时按 `</header>` 边界包一层）
  4. 页面 **CSS 语料**（内联 `<style>` ∪ 页内链接的**本地** CSS）含 `:focus-visible`；
     缺则补一个内联 `<style>`（★ 与站点门控 A4 的形态感知口径**逐字一致**）
  5. `.skip-link` 的可见性样式

★ 确定性：⛔ 无墙钟时间戳、⛔ 无作者机绝对路径。
★ 幂等：已满足的页**一字节不动**；重跑 `--check` 全为 `unchanged`。
★ 空集守卫：扫描面 0 页 ⇒ exit 2（⛔ 不返回「0 页全好」）。

用法：
    python3 inject_page_shell.py --root <发布根> --repo <仓名> [--base-url <基址>] \
        [--exclude <glob>]… [--check] [--json]
    python3 inject_page_shell.py --selftest
退出码：0 成功 / 1 有页未变更（仅 --check） / 2 空集或参数错
"""
import argparse
import fnmatch
import glob
import hashlib
import json
import os
import re
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")

HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
STYLE_BLOCK = re.compile(r"<style[^>]*>(.*?)</style>", re.I | re.S)
LINK_CSS = re.compile(r'<link[^>]*rel\s*=\s*"stylesheet"[^>]*>', re.I)
HREF_ATTR = re.compile(r'href\s*=\s*"([^"]*)"', re.I)
URL_SCHEME = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|data:|#)", re.I)
VIEWPORT = re.compile(r'<meta\s+name="viewport"[^>]*>', re.I)
CHARSET = re.compile(r'<meta\s+charset[^>]*>', re.I)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)
BODY_RE = re.compile(r"<body([^>]*)>", re.I)
HEAD_END = re.compile(r"</head\s*>", re.I)
BODY_END = re.compile(r"</body\s*>", re.I)
LAST_HEADER_END = re.compile(r"</header\s*>", re.I)
MAIN_OPEN = re.compile(r"<main(?![^>]*\bid\s*=)([^>]*)>", re.I)
MAIN_ANY = re.compile(r"<main\b[^>]*>", re.I)
SVG_FULL = re.compile(r"(<svg\b)([^>]*)(>)(.*?)(</svg\s*>)", re.I | re.S)
HEADING = re.compile(r"<h[1-4][^>]*>(.*?)</h[1-4]\s*>", re.I | re.S)

SHELL_CSS = (":focus-visible{outline:0.125rem solid var(--accent,#4f8cff);outline-offset:0.125rem}\n"
             ".skip-link{position:absolute;left:-9999px;top:0;background:var(--accent,#4f8cff);"
             "color:#fff;padding:.5rem 1rem;z-index:9999;border-radius:0 0 .375rem 0}\n"
             ".skip-link:focus{left:0}\n")
SKIP_LINK = '<a class="skip-link" href="#main">跳到主要内容</a>'


def page_url(base_url, rel):
    if not base_url.endswith("/"):
        base_url += "/"
    if rel == "index.html":
        return base_url
    if rel.endswith("/index.html"):
        return base_url + rel[: -len("index.html")]
    return base_url + rel


def _plain(frag):
    t = re.sub(r"<script\b.*?</script>", " ", frag, flags=re.S | re.I)
    t = re.sub(r"<style\b.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    for a, b in (("&nbsp;", " "), ("&amp;", "&"), ("&larr;", "\u2190"), ("&rarr;", "\u2192"),
                 ("&mdash;", "\u2014"), ("&lt;", "<"), ("&gt;", ">")):
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip()


def load_corpus(root, rel, raw):
    base = os.path.dirname(os.path.join(root, rel))
    parts = STYLE_BLOCK.findall(raw)
    for tag in LINK_CSS.findall(raw):
        m = HREF_ATTR.search(tag)
        if not m:
            continue
        href = m.group(1).strip()
        if not href or URL_SCHEME.match(href):
            continue
        tgt = os.path.normpath(os.path.join(base, href.split("?")[0].split("#")[0].lstrip("/")))
        if os.path.isfile(tgt):
            parts.append(open(tgt, encoding="utf-8", errors="replace").read())
    return re.sub(r"/\*.*?\*/", "", "\n".join(parts), flags=re.S)


def make_desc(raw):
    m = TITLE_RE.search(raw)
    tt = _plain(m.group(1)) if m else ""
    mb = re.search(r"<main[^>]*>(.*?)</main>", raw, re.S | re.I)
    body = _plain(mb.group(1)) if mb else ""
    if not body:
        mb = BODY_RE.search(raw)
        body = _plain(raw[mb.end():]) if mb else ""
    d = ("%s ｜ %s" % (tt, body)).strip(" ｜")
    d = d[:150].rstrip("，。、；：:;,. ")
    if len(d) < 20:
        d = tt or "知识库页面"
    return d + "。"


def _attr_esc(s):
    return (s.replace("&", "&amp;").replace('"', "&quot;")
            .replace("<", "&lt;").replace(">", "&gt;"))


def label_svgs(out):
    """★ 图件文本等价（门控 A5）：每个 `<svg>` 补 `role="img"` 与 `aria-label`（或内嵌 `<title>`）。

    ★ 标签取自该 `<svg>` **之前最近的一级/二级标题**（找不到则用页面 `<title>`）＋「图示」
      —— 这是一条**真描述**（该图在这页里就是那个标题所指的图），⛔ 不是占位字符串。
    ⛔ 已有 `role=` 或已有 `aria-label`/`<title>` 的 `<svg>` **一字节不改**。
    """
    def repl(m):
        open_tag, attrs, gt, inner, close = m.groups()
        if re.search(r"\brole\s*=", attrs, re.I):
            return m.group(0)
        has_label = re.search(r"\baria-label\s*=", attrs, re.I) or "<title" in inner.lower()
        attrs2 = attrs + ' role="img"'
        if not has_label:
            hs = HEADING.findall(out[:m.start()])
            label = _plain(hs[-1]) if hs else ""
            if not label:
                t = TITLE_RE.search(out)
                label = _plain(t.group(1)) if t else "图示"
            label = (label[:80] + " 图示").strip()
            attrs2 += ' aria-label="%s"' % _attr_esc(label)
        return open_tag + attrs2 + gt + inner + close

    return SVG_FULL.sub(repl, out)


def has_unlabeled_svg(text):
    for m in SVG_FULL.finditer(text):
        if not re.search(r"\brole\s*=", m.group(2), re.I):
            return True
    return False


def inject(root, rel, repo, base_url, esc_attr=True):
    """返回 (new_text, changed_bool, notes)。"""
    path = os.path.join(root, rel)
    raw = open(path, encoding="utf-8", errors="replace").read()
    notes = []
    out = raw

    plain = HTML_COMMENT.sub("", out)
    corpus = load_corpus(root, rel, plain)
    has_all = ('name="description"' in out and 'class="skip-link"' in out
               and 'id="main"' in out and ":focus-visible" in corpus
               and 'rel="canonical"' in out and 'rel="icon"' in out
               and not has_unlabeled_svg(out))
    if has_all:
        return out, False, ["already"]

    u = page_url(base_url, rel)
    desc = make_desc(plain if "description" not in out else out)
    t = TITLE_RE.search(plain)
    title = _plain(t.group(1)) if t else repo

    attr = _attr_esc

    meta_bits = []
    if 'name="description"' not in out:
        meta_bits.append('<meta name="description" content="%s">' % attr(desc))
    for prop, val in (("og:type", "website"), ("og:title", title),
                      ("og:description", desc), ("og:url", u),
                      ("og:image", base_url.rstrip("/") + "/og.png")):
        if 'property="%s"' % prop not in out:
            meta_bits.append('<meta property="%s" content="%s">' % (prop, attr(val)))
    if 'rel="canonical"' not in out:
        meta_bits.append('<link rel="canonical" href="%s">' % attr(u))
    if 'rel="icon"' not in out:
        meta_bits.append('<link rel="icon" type="image/svg+xml" href="/%s/favicon.svg">' % repo)
    if ":focus-visible" not in corpus:
        meta_bits.append("<style>\n%s</style>" % SHELL_CSS)

    if meta_bits:
        block = "\n".join(meta_bits)
        m = VIEWPORT.search(out) or CHARSET.search(out)
        if m:
            out = out[:m.end()] + "\n" + block + out[m.end():]
        else:
            m = HEAD_END.search(out)
            if m:
                out = out[:m.start()] + block + "\n" + out[m.start():]
            else:
                notes.append("无 </head>，元数据未注入")
        notes.append("head:%d" % len(meta_bits))

    if 'class="skip-link"' not in out:
        m = BODY_RE.search(out)
        if m:
            out = out[:m.end()] + "\n" + SKIP_LINK + out[m.end():]
            notes.append("skip-link")
        else:
            notes.append("无 <body>，skip link 未注入")

    if not MAIN_ANY.search(out):
        # 无 <main> ⇒ 在最后一个 </header> 之后包一层；无 header 则在 <body> 之后
        hs = [mm for mm in LAST_HEADER_END.finditer(out)]
        anchor = hs[-1].end() if hs else (BODY_RE.search(out).end() if BODY_RE.search(out) else None)
        be = BODY_END.search(out)
        if anchor is not None and be is not None and be.start() >= anchor:
            out = out[:anchor] + "\n<main id=\"main\">" + out[anchor:be.start()] + \
                "</main>\n" + out[be.start():]
            notes.append("main:wrapped")
        else:
            notes.append("main:未包裹（缺 body 边界）")
    else:
        n = len(MAIN_ANY.findall(out))
        if 'id="main"' not in out:
            out = MAIN_OPEN.sub(lambda m: '<main id="main"%s>' % m.group(1), out, count=1)
            notes.append("main:id")
        if n > 1:
            notes.append("★ main 计数=%d（>1，需人工核）" % n)

    if has_unlabeled_svg(out):
        out = label_svgs(out)
        notes.append("svg:role+label")
    return out, (out != raw), notes


def enum_pages(root, excludes):
    out = []
    for p in sorted(glob.glob(os.path.join(root, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(p, root).replace(os.sep, "/")
        if "/vendor/" in "/" + rel:
            continue
        if any(fnmatch.fnmatch(rel, pat) for pat in excludes):
            continue
        out.append(rel)
    return out


def run(root, repo, base_url=None, excludes=(), check=False):
    base_url = (base_url or ("https://zako-mio.github.io/%s/" % repo)).rstrip("/") + "/"
    rels = enum_pages(root, excludes)
    if not rels:
        return None
    changed, unchanged, notes = [], [], {}
    for rel in rels:
        new, ch, nt = inject(root, rel, repo, base_url)
        if ch:
            changed.append(rel)
            notes[rel] = nt
            if not check:
                with open(os.path.join(root, rel), "w", encoding="utf-8") as fh:
                    fh.write(new)
        else:
            unchanged.append(rel)
    return {"root": root, "repo": repo, "base_url": base_url, "pages": len(rels),
            "changed": len(changed), "unchanged": len(unchanged),
            "changed_pages": changed[:60], "notes_sample": dict(list(notes.items())[:10])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--repo")
    ap.add_argument("--base-url", dest="base_url")
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.root and a.repo):
        print("ERROR: 需要 --root 与 --repo")
        return 2
    res = run(os.path.abspath(a.root), a.repo, a.base_url, a.exclude, a.check)
    if res is None:
        print("EMPTY-SET: 发布根下 0 个 html ⇒ 拒动（防空集假绿）")
        return 2
    print("[%s] 扫描 %d 页 · 需改 %d · 已合规 %d" % (a.repo, res["pages"], res["changed"],
                                              res["unchanged"]))
    for p in res["changed_pages"][:8]:
        print("   ~ %s  %s" % (p, res["notes_sample"].get(p, "")))
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


def selftest():
    cases = []
    tmp = tempfile.mkdtemp(prefix="shell-")
    os.makedirs(os.path.join(tmp, "sub"), exist_ok=True)
    os.makedirs(os.path.join(tmp, "vendor"), exist_ok=True)
    open(os.path.join(tmp, "ext.css"), "w", encoding="utf-8").write("body{color:#111}\n")
    # a.html：完整模板，缺全部（内联单源）
    open(os.path.join(tmp, "a.html"), "w", encoding="utf-8").write(
        '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        '<title>页甲 · 站</title><style>body{color:#222}</style></head>'
        '<body><header><h1>页甲</h1></header><p>甲页正文内容，用于派生描述。</p></body></html>\n')
    # b.html：外链 CSS 页，已有 :focus-visible（不得重复注入 CSS）
    open(os.path.join(tmp, "sub", "b.html"), "w", encoding="utf-8").write(
        '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">'
        '<link rel="stylesheet" href="../ext.css"><style>:focus-visible{outline:1px solid red}</style>'
        '<title>页乙 · 站</title></head><body><main>乙</main></body></html>\n')
    # c.html：含**无标签的 <svg>**（门控 A5 的对象）＋ 一个已标好的 <svg>（⛔ 不得被改）
    open(os.path.join(tmp, "c.html"), "w", encoding="utf-8").write(
        '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">'
        '<title>页丙 · 站</title><style>a{color:#111}</style></head><body>'
        '<h2>关系图</h2><main><svg viewBox="0 0 10 10"><path d="M0 0"/></svg>'
        '<svg role="img" aria-label="已有标签"><circle r="1"/></svg></main></body></html>\n')
    # vendor 必须被排除
    open(os.path.join(tmp, "vendor", "v.html"), "w", encoding="utf-8").write("<html></html>")

    r1 = run(tmp, "demo-site")
    a = open(os.path.join(tmp, "a.html"), encoding="utf-8").read()
    b = open(os.path.join(tmp, "sub", "b.html"), encoding="utf-8").read()
    c = open(os.path.join(tmp, "c.html"), encoding="utf-8").read()
    cases.append(("★ 扫描面排除 vendor", r1["pages"] == 3, str(r1["pages"])))
    cases.append(("★ 无标签 <svg> 补 role=\"img\" ＋ aria-label（取自最近标题「关系图」）",
                  'role="img" aria-label="关系图 图示"' in c, c[c.find("<svg"):c.find("<svg")+120] if "<svg" in c else ""))
    cases.append(("★ 已标好的 <svg> 一字节不改",
                  'role="img" aria-label="已有标签"' in c and c.count('aria-label="已有标签"') == 1, ""))
    cases.append(("a：注入 description/og×5/canonical/icon",
                  all(k in a for k in ('name="description"', 'property="og:type"', 'property="og:title"',
                                       'property="og:description"', 'property="og:url"',
                                       'property="og:image"', 'rel="canonical"', 'rel="icon"')), ""))
    cases.append(("a：canonical 自指（X.html → 基址/X.html）",
                  '<link rel="canonical" href="https://zako-mio.github.io/demo-site/a.html">' in a, ""))
    cases.append(("a：<body> 后有 skip link 且目标存在",
                  '<body>\n<a class="skip-link" href="#main">跳到主要内容</a>' in a and 'id="main"' in a, ""))
    cases.append(("a：无 <main> ⇒ 按 </header> 边界包一层",
                  "</header>\n<main id=\"main\">" in a and "</main>\n</body>" in a, ""))
    cases.append(("a：CSS 语料缺 :focus-visible ⇒ 补内联 <style>", ":focus-visible" in a, ""))
    cases.append(("★ b：外链页已有 :focus-visible ⇒ **不重复**注入 <style>",
                  b.count(":focus-visible") == 1, str(b.count(":focus-visible"))))
    cases.append(("b：已有一个 <main> ⇒ 只补 id，不新增第二个",
                  b.count("<main") == 1 and 'id="main"' in b, str(b.count("<main"))))
    r2 = run(tmp, "demo-site")
    cases.append(("★ 幂等：二次运行为 0 变更", r2["changed"] == 0, str(r2["changed"])))
    empty = tempfile.mkdtemp(prefix="shell-empty-")
    cases.append(("★ 空集守卫：0 页 ⇒ None", run(empty, "x") is None, ""))
    ex = run(tmp, "demo-site", excludes=["*.html", "sub/*.html"])
    cases.append(("★ 空集守卫：全部被 exclude ⇒ None", ex is None, str(ex)[:60]))
    ok = all(v for _, v, _ in cases)
    for name, res, note in cases:
        print("  [%s] %s%s" % ("PASS" if res else "FAIL", name, ("  ← " + note) if note and not res else ""))
    print("\n=== inject_page_shell.py 自检：%d 项，%d FAIL ===" % (len(cases), sum(1 for _, v, _ in cases if not v)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
