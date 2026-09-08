# -*- coding: utf-8 -*-
"""kb_gate.py — 知识库分层门控（7 层，可单独启用）

用途:
    对一个知识库根目录做分层质量门控，逐层输出 PASS/FAIL 与问题清单。
    这是 0907 实战 ISS-01/ISS-05 的修复落点: 导航层不再只验「链接文件是否存在」，
    而是读 nav 数据源，校验每个导航条目在**所有页面**都齐全。

7 层检查（用 --layers 选择，默认全开）:
    structure : 文件存在性 / 0 字节 / 编码纯净(无 U+FFFD) / HTML 标签平衡
                / 空正文检测(主内容区可见文本过短，--min-content-chars)
    links     : 内部 href/src 断链（解析相对路径，排除 JS 模板拼接假阳性）
    nav       : 导航完整性（读 nav 数据源，校验每条目在所有页面齐全）★关键
    cascade   : 级联一致性（品牌口径/页脚版本/索引条目覆盖/旧报告历史标注）
                + 可配置规则引擎（口径/页数/分值/术语，见 --cascade-rules）
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

    # 可配置级联规则引擎（口径/页数/分值/术语）
    python3 kb_gate.py --root ./kb --layers cascade --cascade-rules ./cascade-rules.yaml
    python3 kb_gate.py --root ./kb --layers cascade --cascade-manual   # 仅原有 4 项自动检查

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
from urllib.parse import unquote

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


def glob_files(root, patterns):
    """按 glob 收集文件，并应用 --exclude 排除模式（与 walk_files 口径一致）。

    修复：cascade/sources/render 层原先直接用 glob.glob，忽略 --exclude，
    导致外部抓取快照（05-source/tmp-evidence 等）产生大量误报。
    """
    out = []
    for pat in patterns:
        out.extend(glob.glob(os.path.join(root, pat), recursive=True))
    out = sorted(set(f for f in out
                     if os.path.isfile(f) and not _is_excluded(f, root)))
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

# --- 空正文检测 ---------------------------------------------------------
# 缺陷背景: 0907 总览页 (04-interactive/index.html) 曾因 gen_overview() 漏传
# body 而正文为空，只剩标题/翻页器/页脚；渲染层只查「加载无错」，未查
# 「内容是否为空」，故漏检并交付给用户。structure 层补此检查。
#
# 主内容区定义: </header> 之后 → <div class="pager"> 或 <footer class="footer">
# 之前；无 </header> 时回退 <body ...> 之后（兼容门户/报告/cyto 模板）。
# 可见文本 = 剥离 script/style/svg、HTML 注释与标签后的非空白文本。
#
# 豁免规则: 页面（主内容区）含 canvas / cytoscape 渲染时跳过——纯 canvas 页
# 正文以 canvas 呈现，静态文本天然稀少（index_cyto.html / premium-cyto.html），
# 仅凭文本长度判空会误伤。
#
# 阈值校准（0907 全库 39 个在范围 HTML 实测，2026-09-09；--exclude 与 README
# 复现命令一致）:
#   - 合法 header 页主内容区可见文本最小 = 1245 字符 (04-interactive/index.html)
#   - body 回退页最小 = 1647 (根 index.html)，报告页 2604 / 6504
#   - 纯 canvas 页 = 657 / 727 字符（豁免，不参与阈值判定）
#   - 缺陷样例（git fac6427 总览页正文缺失）= 0 字符
#   → 默认阈值 400：约合法最小值的 1/3，与 0 之间留出充足间隔，且远高于
#     纯 canvas 页文本量（即使不豁免也不误伤，豁免为双重保险）。
#   → --min-content-chars 可覆盖，0 表示关闭该检查。
DEFAULT_MIN_CONTENT_CHARS = 400

# canvas / 动态图渲染指纹（用于豁免，避免仅凭文本长度误判纯 canvas 页）
CANVAS_RENDER_RE = re.compile(
    r"<canvas\b|cytoscape\s*\(|getElementById\(\s*['\"]cy|id\s*=\s*['\"]cy['\"]",
    re.I)


def _html_main_region(html):
    """抽取主内容区；返回 (文本, mode) 或 (None, reason)。"""
    i = html.find("</header>")
    if i >= 0:
        rest = html[i + len("</header>"):]
        mode = "header"
    else:
        m = re.search(r"<body\b[^>]*>", html, re.I)
        if not m:
            return None, "no-body"
        rest = html[m.end():]
        mode = "body"
    cut = len(rest)
    for mm in (re.search(r'<div\s+class="pager"', rest),
               re.search(r'<footer\s+class="footer"', rest)):
        if mm:
            cut = min(cut, mm.start())
    return rest[:cut], mode


def _visible_text(seg):
    """剥离 script/style/svg、注释与标签，返回压缩后的可见文本。"""
    seg = re.sub(r"<(script|style|svg)\b[^>]*>.*?</\1>", " ", seg,
                 flags=re.S | re.I)
    seg = re.sub(r"<!--.*?-->", " ", seg, flags=re.S)
    seg = re.sub(r"<[^>]+>", " ", seg)
    seg = (seg.replace("&nbsp;", " ").replace("&amp;", "&")
              .replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"'))
    return re.sub(r"\s+", " ", seg).strip()


def layer_structure(root, args, ctx):
    issues, warnings = [], []
    checked = 0
    min_chars = getattr(args, "min_content_chars", DEFAULT_MIN_CONTENT_CHARS)
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
            if min_chars and min_chars > 0:
                region, mode = _html_main_region(text)
                if region is None:
                    warnings.append("空正文检测跳过(%s): %s" % (mode, r))
                elif CANVAS_RENDER_RE.search(region):
                    # 纯 canvas 页豁免（正文由 canvas 动态呈现）
                    pass
                else:
                    n = len(_visible_text(region))
                    if n < min_chars:
                        issues.append(
                            "主内容区可见文本过短(疑似空正文): %s (%d < %d 字符)"
                            % (r, n, min_chars))
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
# 报告页自带「报告目录」而非站点导航，不参与站点导航完整性比对（自动检测优先）
REPORT_NAV_MARKERS = ("报告目录", "报告大纲")


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
        nav_body = "".join(b[1] for b in NAV_CONTAINER_RE.findall(text))
        if any(mk in nav_body for mk in REPORT_NAV_MARKERS):
            warnings.append("跳过报告页导航完整性检查: %s（自带报告目录）"
                            % rel(root, hp))
            continue
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
    exempt_pats = [p.strip() for p in (getattr(args, "nav_exempt", None) or []) if p and p.strip()]

    def _nav_exempt(page_rel):
        import fnmatch
        for pat in exempt_pats:
            if fnmatch.fnmatch(page_rel, pat) or page_rel == pat or pat in page_rel:
                return True
        return False

    for page_rel, links in page_navs.items():
        checked += 1
        if _nav_exempt(page_rel):
            warnings.append("导航豁免: %s（按 --nav-exempt）" % page_rel)
            continue
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
        # 仅对「主导品牌」告警：出现页数 >= 总数一半的品牌为基准，其余才算不一致。
        # 报告页/中间产物页的独立品牌属设计行为，避免噪声。
        total = max(1, len(htmls))
        dominant = max(brand_tokens.items(), key=lambda kv: len(kv[1]))
        dom_token = dominant[0]
        for token, pages in brand_tokens.items():
            if token == dom_token:
                continue
            if len(pages) >= max(2, total * 0.5):
                warnings.append("品牌口径候选不一致: '%s' 出现在 %d 页(如 %s)"
                                % (token[:40], len(pages), pages[0]))
        ctx["brand_dominant"] = dom_token

    # 4.2 页脚版本号一致（仅统计「本站版本」语义：vX.Y 且出现在 footer/页脚区域）
    versions = {}
    for hp in htmls:
        text = read_text(hp)
        foot = " ".join(re.findall(r"<footer[^>]*>(.*?)</footer>", text, re.S | re.I))
        scope = foot if foot else ""
        for m in re.findall(r"v\d+\.\d+(?:\.\d+)?", scope):
            versions.setdefault(m, set()).add(rel(root, hp))
    checked += 1
    if len(versions) > 1:
        # 主导版本（出现页数最多）之外的版本才告警
        if versions:
            dom_v = max(versions.items(), key=lambda kv: len(kv[1]))[0]
            others = {v: p for v, p in versions.items() if v != dom_v}
            if others:
                detail = ", ".join("%s(%d页)" % (v, len(p)) for v, p in others.items())
                warnings.append("页脚版本号不统一（主导 %s）: %s" % (dom_v, detail))

    # 4.3 索引条目覆盖（index 页应引用全部导航条目）
    nav_cov = ctx.get("nav_coverage") or {}
    if nav_cov:
        index_pages = glob_files(root, args.index_glob)
        for ip in index_pages:
            checked += 1
            text = read_text(ip)
            # .md 索引是 AI 镜像，引用的是 .md 源文件；按扩展名匹配对应命名
            is_md_index = ip.lower().endswith(".md")
            missing = []
            for href in nav_cov:
                basename = os.path.basename(href)
                if not basename:
                    continue
                candidates = {basename, href}
                if is_md_index:
                    stem = os.path.splitext(basename)[0]
                    candidates |= {stem + ".md", stem}
                if not any(c in text for c in candidates):
                    missing.append(href)
            if missing:
                issues.append("索引条目覆盖不足: %s 未引用 %d 条 -> %s"
                              % (rel(root, ip), len(missing),
                                 ", ".join(missing[:8])))

    # 4.4 旧报告历史标注
    for fp in glob_files(root, args.old_report_glob):
        relp = rel(root, fp)
        # 带 vX.Y（Y>=1）后缀的报告为当前版本，非「旧报告」
        if re.search(r"v\d+\.\d+", os.path.basename(relp)) and \
                not re.search(r"v1\.0(?!\d)", os.path.basename(relp)):
            continue
        checked += 1
        text = read_text(fp)
        if not any(mk in text for mk in DEFAULT_HISTORY_MARKERS):
            issues.append("旧报告缺历史标注: %s（应含 历史/归档/deprecated 等）"
                          % relp)
    # 4.5 可配置规则引擎（口径/页数/分值/术语）；--cascade-manual 时跳过
    if not getattr(args, "cascade_manual", False):
        rules_path, explicit = _discover_cascade_rules(
            root, getattr(args, "cascade_rules", None))
        if rules_path:
            if explicit and not os.path.isfile(rules_path):
                warnings.append("--cascade-rules 指定文件不存在，已跳过规则引擎: %s"
                                % rules_path)
            else:
                data, err = _read_rule_file(rules_path)
                if err:
                    warnings.append(err)
                elif data is None:
                    warnings.append("规则文件为空: %s" % rel(root, rules_path))
                else:
                    rules = data.get("rules") if isinstance(data, dict) else data
                    if not isinstance(rules, list):
                        warnings.append("规则文件应为 list 或 {rules: [...]}: %s"
                                        % rel(root, rules_path))
                    else:
                        r_iss, r_warn, r_chk = run_cascade_rules(root, rules)
                        issues.extend(r_iss)
                        warnings.extend(r_warn)
                        checked += r_chk
        elif explicit:
            warnings.append("--cascade-rules 指定文件不存在: %s" % rules_path)
    return _result("cascade", issues, warnings, checked)


# ============================================================
# cascade 规则引擎（口径/页数/分值/术语，可配置）
# ============================================================

CASCADE_RULE_TYPES = ("occurrence", "count", "cross_compare", "terminology",
                      "link_reachability")


def _discover_cascade_rules(root, explicit):
    """定位规则文件。

    返回 (path, explicit)。显式传入的路径原样返回（explicit=True）；
    否则在 root 下自动探测 cascade-rules.yaml/.yml/.json。
    """
    if explicit:
        return explicit, True
    for name in ("cascade-rules.yaml", "cascade-rules.yml", "cascade-rules.json"):
        p = os.path.join(root, name)
        if os.path.isfile(p):
            return p, False
    return None, False


def _read_rule_file(path):
    """读规则文件，返回 (data, error)。

    YAML 优先（yaml.safe_load）；缺 pyyaml 时自动回退同名 .json。
    """
    candidates = [path]
    base, ext = os.path.splitext(path)
    if ext.lower() in (".yaml", ".yml"):
        candidates.append(base + ".json")
    for cand in candidates:
        if not os.path.isfile(cand):
            continue
        text = read_text(cand)
        if cand.lower().endswith(".json"):
            try:
                return json.loads(text), None
            except Exception as e:
                return None, "规则 JSON 解析失败(%s): %s" % (cand, e)
        try:
            import yaml
        except ImportError:
            alt = os.path.splitext(cand)[0] + ".json"
            if os.path.isfile(alt):
                try:
                    return json.loads(read_text(alt)), None
                except Exception as e:
                    return None, "规则 JSON 回退解析失败(%s): %s" % (alt, e)
            return None, ("缺 pyyaml 且无同名 .json 回退: %s"
                          "（pip install pyyaml）" % cand)
        try:
            return yaml.safe_load(text), None
        except Exception as e:
            return None, "规则 YAML 解析失败(%s): %s" % (cand, e)
    return None, None


def _rule_targets(root, rule):
    """解析规则的目标文件，返回 [{rel, path, pattern}]。

    - sources: [{file, pattern}] 可为每个文件指定不同 pattern
    - files / files_glob / glob: 相对 root 的路径或 glob（可字符串或列表）
    """
    targets = []
    sources = rule.get("sources")
    if isinstance(sources, list) and sources:
        for src in sources:
            if isinstance(src, dict):
                f = src.get("file") or src.get("path")
                pat = src.get("pattern")
            else:
                f, pat = src, None
            if not f:
                continue
            ap = os.path.join(root, str(f))
            targets.append({
                "rel": str(f),
                "path": ap if os.path.isfile(ap) else None,
                "pattern": pat if pat else rule.get("pattern"),
            })
        return targets
    pats = []
    for key in ("files", "files_glob", "glob"):
        v = rule.get(key)
        if isinstance(v, str):
            pats.append(v)
        elif isinstance(v, list):
            pats.extend(str(x) for x in v)
    seen = set()
    for pat in pats:
        ap = os.path.join(root, pat)
        matches = [ap] if os.path.isfile(ap) else glob.glob(ap, recursive=True)
        for fp in matches:
            if not os.path.isfile(fp) or _is_excluded(fp, root):
                continue
            relp = rel(root, fp)
            if relp in seen:
                continue
            seen.add(relp)
            targets.append({"rel": relp, "path": fp, "pattern": rule.get("pattern")})
    targets.sort(key=lambda t: t["rel"])
    return targets


def _count_files(root, pattern):
    """统计 root 下匹配 glob 的文件数（排除 --exclude）。"""
    ap = os.path.join(root, str(pattern))
    matches = [ap] if os.path.isfile(ap) else glob.glob(ap, recursive=True)
    return sum(1 for fp in matches if os.path.isfile(fp) and not _is_excluded(fp, root))


def _to_num(s):
    try:
        return float(str(s).strip())
    except (TypeError, ValueError):
        return None


def _num_eq(a, b):
    na, nb = _to_num(a), _to_num(b)
    if na is None or nb is None:
        return str(a).strip() == str(b).strip()
    return abs(na - nb) < 1e-9


def _fmt_num(v):
    n = _to_num(v)
    if n is None:
        return str(v)
    return str(int(n)) if abs(n - int(n)) < 1e-9 else str(n)


def _count_expectation(root, expected, value):
    """判定 count 规则：返回 (ok, 期望描述)。"""
    if expected is None:
        return True, str(value)
    if isinstance(expected, dict):
        glob_pat = expected.get("file_count") or expected.get("glob")
        if glob_pat:
            want = _count_files(root, glob_pat)
            return _num_eq(value, want), "%d(%s)" % (want, glob_pat)
        lo, hi = expected.get("min"), expected.get("max")
        ok = True
        if lo is not None and (_to_num(value) or 0) < lo:
            ok = False
        if hi is not None and (_to_num(value) or 0) > hi:
            ok = False
        return ok, "%s..%s" % (_fmt_num(lo), _fmt_num(hi))
    if isinstance(expected, str) and expected.startswith("file_count:"):
        glob_pat = expected.split(":", 1)[1]
        want = _count_files(root, glob_pat)
        return _num_eq(value, want), "%d(%s)" % (want, glob_pat)
    return _num_eq(value, expected), _fmt_num(expected)


def _rule_occurrence(root, rule):
    """口径一致性：pattern 应在目标文件集合按 mode 一致出现/不出现。"""
    rid = rule.get("id")
    pattern = rule.get("pattern")
    if not pattern:
        return ["[规则 %s] occurrence 缺少 pattern" % rid]
    expected = rule.get("expected", True)
    mode = str(rule.get("mode", "all")).lower()
    rx = re.compile(pattern)
    targets = _rule_targets(root, rule)
    if not targets:
        return ["[规则 %s] 未匹配到任何目标文件(files/files_glob/sources)" % rid]
    issues, oks = [], []
    for t in targets:
        if t["path"] is None:
            issues.append("[规则 %s] 目标文件不存在: %s" % (rid, t["rel"]))
            oks.append(False)
            continue
        present = bool(rx.search(read_text(t["path"])))
        ok = present if expected else not present
        oks.append(ok)
        if not ok and mode == "all":
            if expected:
                issues.append("[规则 %s] 口径缺失: %s 未出现 %r"
                              % (rid, t["rel"], pattern))
            else:
                issues.append("[规则 %s] 禁用口径出现: %s 出现 %r"
                              % (rid, t["rel"], pattern))
    if mode == "any" and not any(oks):
        issues.append("[规则 %s] 任一目标应%s出现 %r，实际 %d 个均未满足"
                      % (rid, "「" if expected else "不", pattern, len(targets)))
    return issues


def _rule_count(root, rule):
    """页数/计数一致：捕获声明值并与 expected（字面值/区间/文件数）比对。"""
    rid = rule.get("id")
    expected = rule.get("expected")
    targets = _rule_targets(root, rule)
    if not targets:
        return ["[规则 %s] 未匹配到任何目标文件(files/files_glob/sources)" % rid]
    issues = []
    for t in targets:
        if t["path"] is None:
            issues.append("[规则 %s] 目标文件不存在: %s" % (rid, t["rel"]))
            continue
        pattern = t["pattern"]
        if not pattern:
            issues.append("[规则 %s] count 缺少 pattern: %s" % (rid, t["rel"]))
            continue
        found = re.findall(pattern, read_text(t["path"]))
        if not found:
            issues.append("[规则 %s] 计数声明未找到: %s (pattern=%r)"
                          % (rid, t["rel"], pattern))
            continue
        for raw in found:
            if isinstance(raw, tuple):
                raw = raw[0] if raw else ""
            if _to_num(raw) is None:
                issues.append("[规则 %s] 捕获值非数值: %s -> %r"
                              % (rid, t["rel"], raw))
                continue
            ok, want = _count_expectation(root, expected, raw)
            if not ok:
                issues.append("[规则 %s] 计数不一致: %s 声明=%s 期望=%s"
                              % (rid, t["rel"], _fmt_num(raw), want))
    return issues


def _rule_cross_compare(root, rule):
    """分值一致：从各目标文件提取值，两两相等且等于 expected。"""
    rid = rule.get("id")
    expected = rule.get("expected")
    targets = _rule_targets(root, rule)
    if not targets:
        return ["[规则 %s] 未匹配到任何目标文件(files/files_glob/sources)" % rid]
    issues, values = [], {}
    for t in targets:
        if t["path"] is None:
            issues.append("[规则 %s] 目标文件不存在: %s" % (rid, t["rel"]))
            continue
        pattern = t["pattern"]
        if not pattern:
            issues.append("[规则 %s] cross_compare 缺少 pattern: %s"
                          % (rid, t["rel"]))
            continue
        m = re.search(pattern, read_text(t["path"]))
        if not m:
            issues.append("[规则 %s] 未提取到比对值: %s (pattern=%r)"
                          % (rid, t["rel"], pattern))
            continue
        raw = m.group(1) if m.groups() else m.group(0)
        values[t["rel"]] = raw.strip()
    if len(values) >= 2:
        uniq = set(values.values())
        if len(uniq) > 1:
            detail = ", ".join("%s=%s" % (r, v) for r, v in sorted(values.items()))
            issues.append("[规则 %s] 跨产物数值不一致: %s" % (rid, detail))
    if expected is not None:
        for r, v in sorted(values.items()):
            if not _num_eq(v, expected) and str(v) != str(expected).strip():
                issues.append("[规则 %s] 与期望值不符: %s=%s 期望=%s"
                              % (rid, r, v, expected))
    return issues


def _rule_terminology(root, rule):
    """术语统一：禁用术语不得出现（forbidden 列表或 pattern 正则）。"""
    rid = rule.get("id")
    terms = rule.get("forbidden") or rule.get("terms")
    if isinstance(terms, str):
        terms = [terms]
    if not terms and rule.get("pattern"):
        terms = [rule["pattern"]]
    if not terms:
        return ["[规则 %s] terminology 缺少 forbidden/terms/pattern" % rid]
    except_rx = None
    if rule.get("except"):
        try:
            except_rx = re.compile(rule["except"])
        except re.error:
            except_rx = None
    targets = _rule_targets(root, rule)
    if not targets:
        return ["[规则 %s] 未匹配到任何目标文件(files/files_glob/sources)" % rid]
    issues = []
    for t in targets:
        if t["path"] is None:
            issues.append("[规则 %s] 目标文件不存在: %s" % (rid, t["rel"]))
            continue
        lines = read_text(t["path"]).splitlines()
        for term in terms:
            rx = re.compile(term)
            for i, line in enumerate(lines, 1):
                if except_rx and except_rx.search(line):
                    continue
                if rx.search(line):
                    issues.append("[规则 %s] 禁用术语 %r 出现: %s:%d"
                                  % (rid, term, t["rel"], i))
    return issues


# --- link_reachability：相对引用可达性（硬门控） --------------------------

_LINK_ATTR_RE = re.compile(
    r"<(?:link|img|a)\b[^>]*?\b(?:href|src)\s*=\s*([\"'])([^\"']+)\1",
    re.S | re.I)

# 正文示例里可能出现的字面量（如 href="..."）
_LINK_EXAMPLE_REFS = {"...", "..", "…", "path", "url", "链接", "#"}


def _link_ref_false_positive(ref):
    """判断相对引用是否为应忽略的假阳性（口径对齐 scan_broken_html.py）。

    排除：外链/锚点/JS、JS 模板拼接、服务端绝对路径(/static/ 等)、
    {{}}/<%= %>/${}/{...} 占位符、正文示例、.bak 备份目录。
    """
    if not ref:
        return True
    if ref.startswith(("#", "http://", "https://", "//", "data:", "mailto:",
                       "javascript:")):
        return True
    if is_js_template(ref):
        return True
    # 服务端绝对路径（相对站点根，而非当前文件）
    if ref.startswith("/"):
        return True
    # 模板/占位符：{{...}}、<%= ... %>、${...}、{prev} 等
    if "<%=" in ref or "%>" in ref or "${" in ref:
        return True
    if re.search(r"\{[^}]*\}", ref):
        return True
    # 正文示例字面量
    if ref.strip() in _LINK_EXAMPLE_REFS:
        return True
    # .bak 备份目录（含 .bak-YYYYMMDD 变体）
    if any(".bak" in part for part in ref.replace("\\", "/").split("/")):
        return True
    return False


def scan_link_reachability(root, html_paths):
    """扫描 HTML 内 <link href>/<img src>/<a href> 的相对引用可达性。

    返回 (issues, checked)。相对路径解析到实际文件，缺失即 issue；
    假阳性过滤与 scan_broken_html.py 一致。
    """
    issues = []
    checked = 0
    for hp in html_paths:
        text = read_text(hp)
        base = os.path.dirname(hp)
        r = rel(root, hp)
        for m in _LINK_ATTR_RE.finditer(text):
            raw = m.group(2)
            if _link_ref_false_positive(raw):
                continue
            # JS 字符串拼接：属性值闭合引号后紧跟 +（如 href="premium-'+d.slug+'"）
            if text[m.end():m.end() + 4].lstrip().startswith("+"):
                continue
            # URL 百分号解码 + 去锚点/查询串（对齐 scan_broken_html.py）
            clean = unquote(raw.split("#", 1)[0].split("?", 1)[0]).strip()
            clean = clean.replace("\\", "/")
            if not clean or clean.endswith("/"):
                continue
            checked += 1
            target = os.path.normpath(os.path.join(base, clean))
            if not os.path.exists(target):
                issues.append("相对引用不可达: %s -> %s" % (r, raw))
    return issues, checked


def _rule_link_reachability(root, rule):
    """相对引用可达性规则：HTML 内 link/img/a 的相对路径缺失即 issue。"""
    rid = rule.get("id")
    htmls = []
    sources = rule.get("sources")
    if isinstance(sources, list) and sources:
        for src in sources:
            f = src.get("file") if isinstance(src, dict) else src
            if not f:
                continue
            ap = os.path.join(root, str(f))
            if os.path.isfile(ap) and not _is_excluded(ap, root):
                htmls.append(ap)
    else:
        pats = []
        for key in ("files", "files_glob", "glob"):
            v = rule.get(key)
            if isinstance(v, str):
                pats.append(v)
            elif isinstance(v, list):
                pats.extend(str(x) for x in v)
        if not pats:
            pats = ["**/*.html"]
        htmls = [p for p in glob_files(root, pats)
                 if p.lower().endswith((".html", ".htm"))]
    if not htmls:
        return ["[规则 %s] 未匹配到任何 HTML 目标文件" % rid]
    issues, _checked = scan_link_reachability(root, htmls)
    return ["[规则 %s] %s" % (rid, x) for x in issues]


_RULE_DISPATCH = {
    "occurrence": _rule_occurrence,
    "count": _rule_count,
    "cross_compare": _rule_cross_compare,
    "terminology": _rule_terminology,
    "link_reachability": _rule_link_reachability,
}


def run_cascade_rules(root, rules):
    """执行规则列表，返回 (issues, warnings, checked)。"""
    issues, warnings = [], []
    checked = 0
    for rule in rules:
        if not isinstance(rule, dict):
            warnings.append("跳过非法规则(非映射): %r" % (rule,))
            continue
        rid = rule.get("id") or "?"
        rtype = rule.get("type")
        checked += 1
        if rtype not in _RULE_DISPATCH:
            warnings.append("[规则 %s] 未知 type=%r（支持 %s）"
                            % (rid, rtype, "/".join(CASCADE_RULE_TYPES)))
            continue
        try:
            issues.extend(_RULE_DISPATCH[rtype](root, rule))
        except re.error as e:
            warnings.append("[规则 %s] 正则错误: %s" % (rid, e))
    return issues, warnings, checked


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
    globs = args.content_glob or ["**/*.md"]
    files = glob_files(root, globs)
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
    pages = glob_files(root, args.render_glob)
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
        ok, errs, has_canvas = render_one(engine, pg, args, root=root)
        if not ok:
            issues.append("渲染失败: %s -> %s" % (rel(root, pg), "; ".join(errs[:3])))
            continue
        if args.expect_canvas and not has_canvas:
            issues.append("渲染无 canvas: %s" % rel(root, pg))

    # 清理 /tmp 镜像（若本次触发自动镜像）
    if os.path.abspath(root).startswith("/tmp/"):
        import shutil, glob as _g
        for d in _g.glob(os.path.join(os.path.expanduser("~"), "kb_gate_mirror_*")):
            try:
                shutil.rmtree(d)
            except Exception:
                pass
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


def _mirror_for_render(path, root):
    """snap chromium 无法读取 /tmp 下 file://；若页面在 /tmp 内，
    自动镜像整库到 $HOME 临时目录并返回镜像内对应路径（用完可删）。
    """
    ap = os.path.abspath(path)
    if not ap.startswith("/tmp/"):
        return ap, None
    import shutil, tempfile
    mirror_root = tempfile.mkdtemp(prefix="kb_gate_mirror_", dir=os.path.expanduser("~"))
    dst_root = os.path.join(mirror_root, "root")
    try:
        shutil.copytree(root, dst_root)
    except Exception:
        return ap, mirror_root
    relp = os.path.relpath(ap, root)
    return os.path.join(dst_root, relp), mirror_root


def render_one(engine, path, args, root=None):
    tmp_mirror = None
    if root:
        path, tmp_mirror = _mirror_for_render(path, root)
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
    # structure
    ap.add_argument("--min-content-chars", type=int,
                    default=DEFAULT_MIN_CONTENT_CHARS,
                    help="structure 层空正文阈值：HTML 主内容区可见文本少于此值报 "
                         "issue（默认 %d；0=关闭）" % DEFAULT_MIN_CONTENT_CHARS)
    # nav
    ap.add_argument("--nav-source", help="导航数据源 (.json 或 nav_data.py)")
    ap.add_argument("--nav-exempt", action="append", default=[],
                    help="豁免导航完整性检查的页面（glob 或相对路径，可重复），"
                         "用于报告页等含「报告目录」而非全站导航的页面")
    # cascade
    ap.add_argument("--brand", help="必须出现的品牌口径字符串")
    ap.add_argument("--index-glob", action="append", default=None,
                    help="索引页 glob（可重复；省略用内置默认）")
    ap.add_argument("--old-report-glob", action="append", default=None,
                    help="旧报告 glob（需含历史标注，可重复；省略用内置默认）")
    ap.add_argument("--cascade-rules",
                    help="级联规则文件（cascade-rules.yaml/.json）；缺省自动探测 "
                         "root 下同名文件；无则仅跑原有 4 项自动检查")
    ap.add_argument("--cascade-manual", action="store_true",
                    help="跳过规则引擎，仅保留原有 4 项 cascade 自动检查（向后兼容）")
    # coverage
    ap.add_argument("--manifest", help="交付物清单文件（JSON 或纯文本每行一个）")
    ap.add_argument("--require", action="append", default=[],
                    help="必须存在的相对路径（可重复）")
    # sources
    ap.add_argument("--content-glob", action="append",
                    default=None,
                    help="需含信源区块的内容文件 glob（可重复，默认 **/*.md）")
    ap.add_argument("--src-pattern", default=r"SRC-\d+",
                    help="信源编号正则（默认 SRC-\\d+）")
    ap.add_argument("--evidence-pattern", default=r"证据来源|证据表|信源",
                    help="证据区块标题正则")
    # render
    ap.add_argument("--render-glob", action="append", default=None,
                    help="渲染冒烟页面 glob（可重复；省略用内置默认）")
    ap.add_argument("--expect-canvas", action="store_true",
                    help="要求渲染后页面存在 <canvas>")
    ap.add_argument("--render-timeout", type=int, default=30, help="渲染超时秒")
    ap.add_argument("--render-wait", type=float, default=2.0,
                    help="渲染后额外等待秒（等 JS 执行）")
    args = ap.parse_args(argv)

    # 显式传入的 glob 覆盖内置默认（action="append" 会与 default 合并，故默认置 None）
    if args.index_glob is None:
        args.index_glob = ["index.html", "**/index.html", "**/00-index.md"]
    if args.old_report_glob is None:
        args.old_report_glob = ["**/report*.md", "**/audit-report*.md"]
    if args.content_glob is None:
        args.content_glob = ["**/*.md"]
    if args.render_glob is None:
        args.render_glob = ["**/*.html"]

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
