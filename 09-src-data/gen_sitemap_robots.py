#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_sitemap_robots.py — 批 J 的**站点级元信息产物生成器**（`sitemap.xml` ＋ `robots.txt`）。

判据定义源：`solutions/_shared/SH4-seo-meta.md` §4.2 标准档第 2 / 3 条
（「新增 `sitemap.xml` 生成」＋「新增 `robots.txt`」）。

★ 确定性（J6 幂等的硬前提）：⛔ **不写 `<lastmod>`**、⛔ 不写墙钟时间戳、⛔ 不写作者机绝对路径。
★ 覆盖完整性：`<loc>` 覆盖发布根下**全部**产物页（`vendor/` 与 `--exclude` 除外），逐页用与
  `gate_seo_meta.py` **同一套** URL 归一化（`X/index.html` → `X/`）⇒ 判据对象 == 断言对象。
★ 幂等：内容不变则不重写（`--force` 可强制）。

用法：
    python3 gen_sitemap_robots.py --root <发布根> --repo <仓名> [--base-url <基址>] \
        [--exclude <glob>]… [--force] [--json]
    python3 gen_sitemap_robots.py --selftest
退出码：0 成功 / 1 空集（0 页 ⇒ 防空集假绿）/ 2 输入错误
"""
import argparse
import fnmatch
import glob
import hashlib
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")


def page_url(base_url, rel):
    if not base_url.endswith("/"):
        base_url += "/"
    if rel == "index.html":
        return base_url
    if rel.endswith("/index.html"):
        return base_url + rel[: -len("index.html")]
    return base_url + rel


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


def build(base_url, rels):
    locs = [page_url(base_url, r) for r in rels]
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "".join("  <url><loc>%s</loc></url>\n" % u for u in locs)
               + "</urlset>\n")
    robots = ("User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n" % base_url)
    return sitemap, robots, locs


def write_if_changed(path, data, force=False):
    if isinstance(data, str):
        data = data.encode("utf-8")
    if os.path.isfile(path) and not force:
        if open(path, "rb").read() == data:
            return "unchanged"
    with open(path, "wb") as fh:
        fh.write(data)
    return "written"


def run(root, repo, base_url=None, excludes=(), force=False):
    base_url = base_url or ("https://zako-mio.github.io/%s/" % repo)
    if not base_url.endswith("/"):
        base_url += "/"
    rels = enum_pages(root, excludes)
    if not rels:
        return None
    sitemap, robots, locs = build(base_url, rels)
    r1 = write_if_changed(os.path.join(root, "sitemap.xml"), sitemap, force)
    r2 = write_if_changed(os.path.join(root, "robots.txt"), robots, force)
    return {"root": root, "repo": repo, "base_url": base_url, "pages": len(rels),
            "sitemap.xml": r1, "robots.txt": r2,
            "sitemap_sha256": hashlib.sha256(sitemap.encode()).hexdigest(),
            "first_loc": locs[0], "last_loc": locs[-1]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--repo")
    ap.add_argument("--base-url", dest="base_url")
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.root and a.repo):
        print("ERROR: 需要 --root 与 --repo")
        return 2
    if not os.path.isdir(a.root):
        print("ERROR: root 不是目录：%s" % a.root)
        return 2
    res = run(os.path.abspath(a.root), a.repo, a.base_url, a.exclude, a.force)
    if res is None:
        print("EMPTY-SET: 发布根下 0 个产物页 ⇒ 拒写（防空集假绿）")
        return 1
    print("sitemap.xml %s（%d 页）· robots.txt %s（base=%s）"
          % (res["sitemap.xml"], res["pages"], res["robots.txt"], res["base_url"]))
    if a.json:
        import json
        print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


def selftest():
    import json
    cases = []
    tmp = tempfile.mkdtemp(prefix="sitemap-")
    os.makedirs(os.path.join(tmp, "sub"), exist_ok=True)
    os.makedirs(os.path.join(tmp, "vendor"), exist_ok=True)
    for n in ("index.html", "a.html", "sub/b.html", "sub/index.html", "vendor/v.html"):
        open(os.path.join(tmp, n), "w", encoding="utf-8").write("<html></html>")
    r1 = run(tmp, "demo-site")
    sm = open(os.path.join(tmp, "sitemap.xml"), encoding="utf-8").read()
    rb = open(os.path.join(tmp, "robots.txt"), encoding="utf-8").read()
    cases.append(("★ 覆盖全部产物页（vendor 被排除）", r1["pages"] == 4, str(r1["pages"])))
    cases.append(("★ X/index.html → X/ 归一化（与门控同口径）",
                  "<loc>https://zako-mio.github.io/demo-site/sub/</loc>" in sm, ""))
    cases.append(("★ 根 index.html → 基址本身",
                  "<loc>https://zako-mio.github.io/demo-site/</loc>" in sm, ""))
    cases.append(("★ ⛔ 无 lastmod（确定性硬前提）", "lastmod" not in sm, ""))
    cases.append(("robots.txt 含 Sitemap: 指向 sitemap.xml",
                  "Sitemap: https://zako-mio.github.io/demo-site/sitemap.xml" in rb, ""))
    r2 = run(tmp, "demo-site")
    cases.append(("★ 幂等：二次运行为 unchanged",
                  r2["sitemap.xml"] == "unchanged" and r2["robots.txt"] == "unchanged", ""))
    r3 = run(tmp, "demo-site", excludes=["*.html", "sub/*.html"])
    cases.append(("★ 空集守卫：全部页被 exclude ⇒ 返回 None（拒写）", r3 is None, str(r3)[:80]))
    empty = tempfile.mkdtemp(prefix="sitemap-empty-")
    cases.append(("★ 空集守卫：发布根 0 页 ⇒ None", run(empty, "x") is None, ""))
    ok = all(v for _, v, _ in cases)
    for name, res, note in cases:
        print("  [%s] %s%s" % ("PASS" if res else "FAIL", name, ("  ← " + note) if note and not res else ""))
    print("\n=== gen_sitemap_robots.py 自检：%d 项，%d FAIL ===" % (len(cases), sum(1 for _, v, _ in cases if not v)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
