# -*- coding: utf-8 -*-
"""kb_gate.py — 知识库分层门控（7 层，可单独启用）

用途:
    对一个知识库根目录做分层质量门控，逐层输出 PASS/FAIL 与问题清单。
    这是 0907 实战 ISS-01/ISS-05 的修复落点: 导航层不再只验「链接文件是否存在」，
    而是读 nav 数据源，校验每个导航条目在**所有页面**都齐全。

7 层检查（用 --layers 选择，默认全开）:
    structure : 文件存在性 / 0 字节 / 编码纯净(无 U+FFFD) / HTML 标签平衡
    links     : 内部 href/src 断链（解析相对路径，排除 JS 模板拼接假阳性）
    nav       : 导航完整性（读 nav 数据源，校验每条目在所有页面齐全）★关键
    cascade   : 级联一致性（品牌口径/页脚版本/索引条目覆盖/旧报告历史标注）
    coverage  : 交付物清单比对（声明 vs 实际）
    sources   : 信源区块存在性（SRC- 编号 / 证据来源表）
    render    : 可选 headless chromium 渲染冒烟（canvas/JS 错误；无环境跳过标注）

依赖:
    标准库 only。
    render 层可选: playwright（`pip install playwright && playwright install chromium`）
                   或系统 chromium/chrome 可执行文件；缺失时该层标注 skipped。

用法示例:
    # 全部门控层，输出 JSON 报告
    python3 kb_gate.py --root ./kb --json-out gate.json

    # 只跑结构 + 断链 + 导航
    python3 kb_gate.py --root ./kb --layers structure,links,nav

    # 指定 nav 数据源与交付物清单
    python3 kb_gate.py --root ./kb --nav-source ./src/nav_data.py \\
        --manifest ./contract-deliverables.txt

    # 渲染冒烟（需 playwright）
    python3 kb_gate.py --root ./kb --layers render --expect-canvas

输出说明:
    终端打印每层 [PASS]/[FAIL]/[SKIP] 与问题清单；
    --json-out 写结构化 JSON: {layers:{name:{status,issues,warnings,checked}}, summary}
    退出码: 0=全过（允许 skipped），1=至少一层 FAIL。

nav 数据源格式（--nav-source，可省略）:
    - .json : [{"label":"...","href":"..."}, ...] 或 ["path/a.html", ...]
    - .py   : 含 NAV = [("标签","文件名","分组"), ...] 的 Python 字面量（用 ast 解析）
    - 省略  : 自动选取「导航链接最多」的页面作为基线（有风险，仅兜底）
"""

from __future__ import annotations

import argparse
import ast
import glob
import json
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


TEXT_EXTS = {".md", ".markdown", ".txt", ".html", ".htm", ".css", ".js",
             ".json", ".yaml", ".yml", ".xml", ".drawio", ".csv", ".py"}
SKIP_DIR_NAMES = {".git", "__pycache__", "node_modules", ".venv", "vendor",
                  ".cache", "dist", "build"}
BAD_CHAR = "\ufffd"

# 用户通过 --exclude 追加的排除模式（相对 root 的路径前缀或目录名），
# 用于排除外部抓取快照等非交付物，避免误报断链/结构问题。
EXCLUDE_PATTERNS = []


def _is_excluded(path, root):
    """判断 path 是否命中 --exclude 模式（目录名或相对路径前缀）。"""
    if not EXCLUDE_PATTERNS:
        return False
    rel = os.path.relpath(path, root).replace(os.sep, "/")
    parts = rel.split("/")
    for pat in EXCLUDE_PATTERNS:
        pat = pat.strip().strip("/")
        if not pat:
            continue
        if pat in parts:
            return True
        if rel == pat or rel.startswith(pat + "/"):
            return True
    return False

ALL_LAYERS = ["structure", "links", "nav", "cascade",
              "coverage", "sources", "render"]


# ============================================================
# 工具函数
# ============================================================

def walk_files(root, exts=None):
    out = []
    for dirpath, dirnames, names in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES
                       and not d.startswith(".")
                       and not _is_excluded(os.path.join(dirpath, d), root)]
        for n in names:
            p = os.path.join(dirpath, n)
            if _is_excluded(p, root):
                continue
            if exts is None or os.path.splitext(n)[1].lower() in exts:
                out.append(p)
    return out


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except UnicodeDecodeError:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except Exception:
        return ""


def rel(root, path):
    return os.path.relpath(path, root).replace(os.sep, "/")


def norm_href(href):
    """把 href 归一化为「相对库根的路径」用于集合比对（去锚点/查询串）。"""
    h = href.split("#", 1)[0].split("?", 1)[0].strip()
    h = h.replace("\\", "/")
    while h.startswith("./"):
        h = h[2:]
    return h


# nav 数据源里出现的逻辑名 → 实际文件名（如门户 "portal" 实际渲染到 index.html）
NAV_NAME_ALIAS = {
    "portal": "index.html",
    "portal.html": "index.html",
}


def nav_key(href):
    """导航比对键：按文件名归一（nav_data 语义是文件名，页面用相对路径）。

    - 去锚点/查询串
    - 逻辑名经 NAV_NAME_ALIAS 映射（portal → index.html）
    - 取 basename，使 ../index.html 与 index.html 等价
    """
    h = norm_href(href)
    h = NAV_NAME_ALIAS.get(h, h)
    base = h.rsplit("/", 1)[-1]
    return NAV_NAME_ALIAS.get(base, base)


def is_js_template(s):
    """排除 JS 模板拼接字符串造成的断链假阳性。"""
    return any(ch in s for ch in ["+", "'", "${", "`", "\\", "{{"])


# ============================================================
# 第 1 层: structure
# ============================================================

def layer_structure(root, args, ctx):
    issues, warnings = [], []
    checked = 0
    files = walk_files(root)
    for fp in files:
        checked += 1
        r = rel(root, fp)
        try:
            size = os.path.getsize(fp)
        except OSError:
            continue
        if size == 0:
            warnings.append("0 字节文件: %s" % r)
        ext = os.path.splitext(fp)[1].lower()
        if ext in TEXT_EXTS:
            text = read_text(fp)
            if BAD_CHAR in text:
                issues.append("编码不纯(含 U+FFFD 替换字符): %s" % r)
        if ext in (".html", ".htm"):
            for tag in ("div", "table", "section", "nav"):
                opens = len(re.findall(r"<%s[\s>]" % tag, text, re.I))
                closes = len(re.findall(r"</%s>" % tag, text, re.I))
                if opens != closes:
                    issues.append("HTML 标签不平衡 <%s>: %s (开=%d 闭=%d)"
                                  % (tag, r, opens, closes))
    return _result("structure", issues, warnings, checked)


# ============================================================
# 第 2 层: links（断链）
# ============================================================

def layer_links(root, args, ctx):
    issues, warnings = [], []
    checked = 0
    htmls = [p for p in walk_files(root, {".html", ".htm"})]
    for hp in htmls:
        text = read_text(hp)
        r = rel(root, hp)
        base = os.path.dirname(hp)
        refs = re.findall(r'(?:href|src)\s*=\s*"([^"]+)"', text)
        refs += re.findall(r"(?:href|src)\s*=\s*'([^']+)'", text)
        for ref in refs:
            if not ref or ref.startswith(("http://", "https://", "//",
                                          "data:", "mailto:", "javascript:",
                                          "#")):
                continue
            if is_js_template(ref):
                continue
            clean = norm_href(ref)
            if not clean:
                continue
            checked += 1
            target = os.path.normpath(os.path.join(base, clean))
            if not os.path.exists(target):
                issues.append("断链: %s -> %s" % (r, ref))
    return _result("links", issues, warnings, checked)


# ============================================================
# 第 3 层: nav（导航完整性）★核心
# ============================================================

NAV_CONTAINER_RE = re.compile(
    r"<(nav|aside)\b[^>]*>(.*?)</\1>", re.S | re.I)
NAV_CLASS_RE = re.compile(
    r"<(?:div|ul|aside|nav)\b[^>]*(?:class|id)\s*=\s*[\"'][^\"']*"
    r"(?:nav|sidebar|toc|menu)[^\"']*[\"'][^>]*>(.*?)</(?:div|ul|aside|nav)>",
    re.S | re.I)
ANCHOR_RE = re.compile(
    r"<a\b[^>]*href\s*=\s*[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", re.S | re.I)


def _extract_nav_links(html):
    """从导航容器提取 [(normalized_href, label)]；找不到容器则返回 None。"""
    blocks = NAV_CONTAINER_RE.findall(html)
    body = "".join(b[1] for b in blocks) if blocks else ""
    if not body:
        m = NAV_CLASS_RE.findall(html)
        body = "".join(m) if m else ""
    if not body:
        return None
    out = []
    for href, label in ANCHOR_RE.findall(body):
        if href.startswith(("http://", "https://", "//", "mailto:",
                            "javascript:", "#")) or is_js_template(href):
            continue
        label_text = re.sub(r"<[^>]+>", "", label).strip()
        out.append((norm_href(href), label_text))
    return out


def _load_nav_source(path):
    """读 nav 数据源，返回归一化 href 集合（含标签映射）。"""
    if not path or not os.path.isfile(path):
        return None
    text = read_text(path)
    hrefs = {}
    if path.lower().endswith(".json"):
        try:
            data = json.loads(text)
        except Exception as e:
            print("[WARN] nav JSON 解析失败: %s" % e, file=sys.stderr)
            return None
        for item in data:
            if isinstance(item, dict):
                href = item.get("href") or item.get("file") or ""
                label = item.get("label", "")
            else:
                href, label = str(item), ""
            if href:
                hrefs[norm_href(href)] = label
        return hrefs
    # Python: ast 解析 NAV 字面量
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        print("[WARN] nav .py 解析失败: %s" % e, file=sys.stderr)
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "NAV":
                    try:
                        seq = ast.literal_eval(node.value)
                    except Exception:
                        continue
                    for item in seq:
                        if isinstance(item, (list, tuple)) and item:
                            fname = str(item[1] if len(item) > 1 else item[0])
                            label = str(item[0])
                            # 逻辑名（portal 等）不机械拼 .html，交由 nav_key 映射
                            if fname in NAV_NAME_ALIAS or fname.endswith(".html"):
                                key = fname
                            else:
                                key = fname + ".html"
                            hrefs[norm_href(key)] = label
    return hrefs or None


def _resolve_nav_href(root, page_path, nav_href):
    """nav 数据源里的 href 可能是纯文件名，需按页面目录解析出用于比对的键。"""
    return norm_href(nav_href)


def layer_nav(root, args, ctx):
    """核心：读 nav 数据源，校验每个导航条目在所有页面齐全。

    兼容两种比对口径:
      A) 有 --nav-source: 以数据源条目集合为期望集，逐页检查缺项/多项。
      B) 无 --nav-source: 取导航条目最多的页面作基线，其余页与之比对。
    """
    issues, warnings = [], []
    checked = 0
    htmls = sorted(walk_files(root, {".html", ".htm"}))
    if not htmls:
        return _result("nav", issues, warnings, 0)

    page_navs = {}
    for hp in htmls:
        text = read_text(hp)
        links = _extract_nav_links(text)
        if links is None:
            continue
        page_navs[rel(root, hp)] = links

    if not page_navs:
        warnings.append("未识别到任何导航容器（nav/sidebar/toc/menu），"
                        "请检查页面结构或添加 --nav-source")
        return _result("nav", issues, warnings, 0)

    src = _load_nav_source(args.nav_source)
    if src:
        expected = set(nav_key(k) for k in src.keys())
        expected_labels = {nav_key(k): v for k, v in src.items()}
        mode = "nav-source:%s" % rel(root, os.path.abspath(args.nav_source)) \
            if args.nav_source.startswith(root) else "nav-source"
    else:
        # 自动基线: 导航条目最多的页面
        baseline_rel, baseline_links = max(
            page_navs.items(), key=lambda kv: len(set(nav_key(h) for h, _ in kv[1])))
        expected = set(nav_key(h) for h, _ in baseline_links)
        expected_labels = {nav_key(h): lab for h, lab in baseline_links}
        mode = "auto-baseline:%s" % baseline_rel
        warnings.append("未提供 --nav-source，自动以 %s 为基线（%d 条目）"
                        % (baseline_rel, len(expected)))

    # 页面自身文件也应在期望集合内（排除 portal 入口 index 的特殊情况）
    for page_rel, links in page_navs.items():
        checked += 1
        page_set = set(nav_key(h) for h, _ in links)
        missing = sorted(expected - page_set)
        if missing:
            labels = ["%s(%s)" % (expected_labels.get(m, m), m) for m in missing]
            issues.append("导航缺项: %s 缺 %d 条 -> %s"
                          % (page_rel, len(missing), ", ".join(labels[:8])
                             + (" ..." if len(labels) > 8 else "")))
        extra = sorted(page_set - expected)
        if extra:
            warnings.append("导航多项(可能合理): %s 多 %s"
                            % (page_rel, ", ".join(extra[:5])))

    # 逐条目全站覆盖矩阵（每条 nav 条目应在多少页面出现）
    coverage = {}
    for href in expected:
        present = sum(1 for _p, lk in page_navs.items()
                      if href in set(nav_key(h) for h, _ in lk))
        coverage[href] = present
        if present == 0:
            issues.append("导航条目全站缺失: %s" % href)
    ctx["nav_coverage"] = coverage
    ctx["nav_mode"] = mode
    ctx["nav_page_count"] = len(page_navs)
    ctx["nav_expected_count"] = len(expected)
    return _result("nav", issues, warnings, checked)


# ============================================================
# 第 4 层: cascade（级联一致性）
# ============================================================

DEFAULT_HISTORY_MARKERS = ["历史", "归档", "已废弃", "deprecated", "archived",
                           "历史版本", "v1.0 遗留"]


def layer_cascade(root, args, ctx):
    issues, warnings = [], []
    checked = 0
    htmls = sorted(walk_files(root, {".html", ".htm"}))

    # 4.1 品牌口径一致
    brand_tokens = {}
    for hp in htmls:
        text = read_text(hp)
        for m in re.findall(
                r'(?:sidebar-brand|brand|logo)[^>]*>(.*?)</(?:div|h1|p|span)>',
                text, re.S | re.I):
            clean = re.sub(r"<[^>]+>", " ", m)
            clean = re.sub(r"\s+", " ", clean).strip()
            if clean:
                brand_tokens.setdefault(clean, []).append(rel(root, hp))
    if args.brand:
        for hp in htmls:
            checked += 1
            if args.brand not in read_text(hp):
                issues.append("品牌口径缺失: %s 未含 '%s'" % (rel(root, hp), args.brand))
    elif len(brand_tokens) > 1:
        for token, pages in brand_tokens.items():
            warnings.append("品牌口径候选不一致: '%s' 出现在 %d 页(如 %s)"
                            % (token[:40], len(pages), pages[0]))

    # 4.2 页脚版本号一致
    versions = {}
    for hp in htmls:
        text = read_text(hp)
        for m in re.findall(r"v\d+\.\d+(?:\.\d+)?", text):
            versions.setdefault(m, set()).add(rel(root, hp))
    checked += 1
    if len(versions) > 1:
        detail = ", ".join("%s(%d页)" % (v, len(p)) for v, p in versions.items())
        warnings.append("版本号口径不统一: %s" % detail)

    # 4.3 索引条目覆盖（index 页应引用全部导航条目）
    nav_cov = ctx.get("nav_coverage") or {}
    if nav_cov:
        index_pages = []
        for pat in args.index_glob:
            index_pages.extend(glob.glob(os.path.join(root, pat), recursive=True))
        for ip in index_pages:
            checked += 1
            text = read_text(ip)
            missing = []
            for href in nav_cov:
                basename = os.path.basename(href)
                if basename and basename not in text and href not in text:
                    missing.append(href)
            if missing:
                issues.append("索引条目覆盖不足: %s 未引用 %d 条 -> %s"
                              % (rel(root, ip), len(missing),
                                 ", ".join(missing[:8])))

    # 4.4 旧报告历史标注
    for pat in args.old_report_glob:
        for fp in glob.glob(os.path.join(root, pat), recursive=True):
            if os.path.isdir(fp):
                continue
            checked += 1
            text = read_text(fp)
            if not any(mk in text for mk in DEFAULT_HISTORY_MARKERS):
                issues.append("旧报告缺历史标注: %s（应含 历史/归档/deprecated 等）"
                              % rel(root, fp))
    return _result("cascade", issues, warnings, checked)


# ============================================================
# 第 5 层: coverage（交付物清单比对）
# ============================================================

def _load_manifest(path):
    text = read_text(path)
    if path.lower().endswith(".json"):
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                data = data.get("required") or data.get("files") or []
            return [str(x) for x in data]
        except Exception:
            return None
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line)
    return out


def layer_coverage(root, args, ctx):
    issues, warnings = [], []
    checked = 0
    required = list(args.require or [])
    if args.manifest:
        if not os.path.isfile(args.manifest):
            issues.append("manifest 文件不存在: %s" % args.manifest)
        else:
            loaded = _load_manifest(args.manifest)
            if loaded is None:
                issues.append("manifest 解析失败: %s" % args.manifest)
            else:
                required.extend(loaded)
    if not required:
        warnings.append("未提供 --manifest/--require，coverage 层跳过比对")
        return _result("coverage", issues, warnings, 0)
    missing = []
    for r in required:
        checked += 1
        if not os.path.exists(os.path.join(root, r)):
            missing.append(r)
    if missing:
        issues.append("交付物缺失 %d/%d: %s"
                      % (len(missing), len(required),
                         ", ".join(missing[:10]) + (" ..." if len(missing) > 10 else "")))
    return _result("coverage", issues, warnings, checked)


# ============================================================
# 第 6 层: sources（信源区块存在性）
# ============================================================

def layer_sources(root, args, ctx):
    issues, warnings = [], []
    checked = 0
    files = []
    for pat in args.content_glob:
        files.extend(glob.glob(os.path.join(root, pat), recursive=True))
    files = sorted(set(f for f in files if os.path.isfile(f)))
    src_re = re.compile(args.src_pattern)
    ev_re = re.compile(args.evidence_pattern, re.I)
    for fp in files:
        checked += 1
        text = read_text(fp)
        has_src = bool(src_re.search(text))
        has_ev = bool(ev_re.search(text))
        if not has_src and not has_ev:
            issues.append("缺信源区块: %s（需含 %s 编号或证据来源表）"
                          % (rel(root, fp), args.src_pattern))
        elif not has_src:
            warnings.append("有证据标题但无 SRC 编号: %s" % rel(root, fp))
    return _result("sources", issues, warnings, checked)


# ============================================================
# 第 7 层: render（headless 渲染冒烟，可选）
# ============================================================

def layer_render(root, args, ctx):
    issues, warnings = [], []
    checked = 0
    pages = []
    for pat in args.render_glob:
        pages.extend(glob.glob(os.path.join(root, pat), recursive=True))
    pages = sorted(set(p for p in pages if os.path.isfile(p)))
    if not pages:
        warnings.append("render_glob 未匹配到页面，render 层跳过")
        return _result("render", issues, warnings, 0, status="skipped")

    engine = detect_render_engine()
    if engine is None:
        warnings.append("无 headless 渲染环境（playwright/chromium 均缺失），"
                        "render 层 skipped。安装: pip install playwright && "
                        "playwright install chromium")
        return _result("render", issues, warnings, 0, status="skipped")

    for pg in pages:
        checked += 1
        ok, errs, has_canvas = render_one(engine, pg, args)
        if not ok:
            issues.append("渲染失败: %s -> %s" % (rel(root, pg), "; ".join(errs[:3])))
            continue
        if args.expect_canvas and not has_canvas:
            issues.append("渲染无 canvas: %s" % rel(root, pg))
    return _result("render", issues, warnings, checked)


def detect_render_engine():
    try:
        import playwright  # noqa: F401
        return "playwright"
    except Exception:
        pass
    for exe in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        try:
            subprocess.run([exe, "--version"], capture_output=True, timeout=10)
            return exe
        except Exception:
            continue
    return None


def render_one(engine, path, args):
    url = "file://" + os.path.abspath(path)
    if engine == "playwright":
        try:
            from playwright.sync_api import sync_playwright
        except Exception:
            return False, ["playwright 导入失败"], False
        errors = []
        has_canvas = False
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(args=["--no-sandbox"])
                page = browser.new_page()
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.on("console",
                        lambda m: errors.append("console.%s: %s" % (m.type, m.text))
                        if m.type == "error" else None)
                page.goto(url, wait_until="load", timeout=args.render_timeout * 1000)
                page.wait_for_timeout(args.render_wait * 1000)
                has_canvas = page.evaluate("!!document.querySelector('canvas')")
                browser.close()
        except Exception as e:
            return False, [str(e)], False
        return (len(errors) == 0), errors, has_canvas
    # 系统 chromium: dump-dom 冒烟
    try:
        res = subprocess.run(
            [engine, "--headless", "--no-sandbox", "--dump-dom", url],
            capture_output=True, timeout=args.render_timeout)
        dom = res.stdout.decode("utf-8", "replace")
        has_canvas = "<canvas" in dom.lower()
        if res.returncode != 0:
            return False, [res.stderr.decode("utf-8", "replace")[:200]], has_canvas
        if "about:neterror" in dom or "ERR_FILE_NOT_FOUND" in dom:
            return False, ["页面加载错误"], has_canvas
        return True, [], has_canvas
    except Exception as e:
        return False, [str(e)], False


# ============================================================
# 结果封装 / 主流程
# ============================================================

def _result(name, issues, warnings, checked, status=None):
    if status is None:
        status = "FAIL" if issues else "PASS"
    return {
        "name": name,
        "status": status,
        "issues": issues,
        "warnings": warnings,
        "checked": checked,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="知识库分层门控（7 层）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--root", required=True, help="知识库根目录")
    ap.add_argument("--layers", default="all",
                    help="逗号分隔的层名，或 all。可选: %s" % ",".join(ALL_LAYERS))
    ap.add_argument("--json-out", help="结构化 JSON 报告输出路径")
    ap.add_argument("--quiet", action="store_true", help="只打印汇总，不打印逐条问题")
    ap.add_argument("--exclude", action="append", default=[],
                    help="排除目录名或相对路径前缀（可重复），用于排除外部抓取快照等非交付物")
    # nav
    ap.add_argument("--nav-source", help="导航数据源 (.json 或 nav_data.py)")
    # cascade
    ap.add_argument("--brand", help="必须出现的品牌口径字符串")
    ap.add_argument("--index-glob", action="append",
                    default=["index.html", "**/index.html", "**/00-index.md"],
                    help="索引页 glob（可重复）")
    ap.add_argument("--old-report-glob", action="append",
                    default=["**/report*.md", "**/audit-report*.md"],
                    help="旧报告 glob（需含历史标注，可重复）")
    # coverage
    ap.add_argument("--manifest", help="交付物清单文件（JSON 或纯文本每行一个）")
    ap.add_argument("--require", action="append", default=[],
                    help="必须存在的相对路径（可重复）")
    # sources
    ap.add_argument("--content-glob", action="append",
                    default=["**/*.md"],
                    help="需含信源区块的内容文件 glob（可重复）")
    ap.add_argument("--src-pattern", default=r"SRC-\d+",
                    help="信源编号正则（默认 SRC-\\d+）")
    ap.add_argument("--evidence-pattern", default=r"证据来源|证据表|信源",
                    help="证据区块标题正则")
    # render
    ap.add_argument("--render-glob", action="append", default=["**/*.html"],
                    help="渲染冒烟页面 glob（可重复）")
    ap.add_argument("--expect-canvas", action="store_true",
                    help="要求渲染后页面存在 <canvas>")
    ap.add_argument("--render-timeout", type=int, default=30, help="渲染超时秒")
    ap.add_argument("--render-wait", type=float, default=2.0,
                    help="渲染后额外等待秒（等 JS 执行）")
    args = ap.parse_args(argv)

    if not os.path.isdir(args.root):
        print("[ERROR] root 不存在或非目录: %s" % args.root, file=sys.stderr)
        return 2

    if args.exclude:
        EXCLUDE_PATTERNS[:] = [p for p in args.exclude if p and p.strip()]
    layers = ALL_LAYERS if args.layers.strip().lower() == "all" \
        else [x.strip() for x in args.layers.split(",") if x.strip()]
    unknown = [x for x in layers if x not in ALL_LAYERS]
    if unknown:
        print("[ERROR] 未知层: %s（可选 %s）"
              % (", ".join(unknown), ", ".join(ALL_LAYERS)), file=sys.stderr)
        return 2

    ctx = {}
    dispatcher = {
        "structure": layer_structure,
        "links": layer_links,
        "nav": layer_nav,
        "cascade": layer_cascade,
        "coverage": layer_coverage,
        "sources": layer_sources,
        "render": layer_render,
    }

    results = []
    for name in layers:
        res = dispatcher[name](args.root, args, ctx)
        results.append(res)
        mark = {"PASS": "[PASS]", "FAIL": "[FAIL]", "SKIP": "[SKIP]"}.get(
            res["status"], "[????]")
        if res["status"] == "PASS" and res["warnings"]:
            mark += "(warn)"
        if res["status"] == "skipped":
            mark = "[SKIP]"
        print("%s %-10s 检查项=%d 问题=%d 提醒=%d"
              % (mark, name, res["checked"], len(res["issues"]),
                 len(res["warnings"])))
        if not args.quiet:
            for it in res["issues"]:
                print("    ❌ %s" % it)
            for w in res["warnings"]:
                print("    ⚠️  %s" % w)

    failed = [r for r in results if r["status"] == "FAIL"]
    skipped = [r for r in results if r["status"] == "skipped"]
    print("=" * 64)
    print("门控汇总: 层=%d PASS=%d FAIL=%d SKIP=%d"
          % (len(results), len(results) - len(failed) - len(skipped),
             len(failed), len(skipped)))
    if ctx.get("nav_mode"):
        print("nav 模式=%s 页面=%s 期望条目=%s"
              % (ctx.get("nav_mode"), ctx.get("nav_page_count"),
                 ctx.get("nav_expected_count")))
    print("=" * 64)

    report = {
        "root": os.path.abspath(args.root),
        "layers": {r["name"]: r for r in results},
        "summary": {
            "total": len(results),
            "pass": len(results) - len(failed) - len(skipped),
            "fail": len(failed),
            "skip": len(skipped),
            "issue_total": sum(len(r["issues"]) for r in results),
            "warning_total": sum(len(r["warnings"]) for r in results),
            "nav_coverage": ctx.get("nav_coverage", {}),
        },
    }
    if args.json_out:
        out_dir = os.path.dirname(os.path.abspath(args.json_out))
        if out_dir and not os.path.isdir(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
        print("JSON 报告 -> %s" % args.json_out)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
