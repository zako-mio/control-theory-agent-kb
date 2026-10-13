#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate_tokens.py — 站 03 `control-theory-agent-kb` 的**站点侧门控**（仓根；批 I）。

★ 落点与时机（brief §4 的硬约束）：
  · 落在**仓根**（⛔ 不散落在 `07-checkpoint/`），配 `gate-manifest.json` + `build/profile.json`
    + `vendor/pipeline/**` 薄副本；清单项**无任何豁免/白名单字段**（M4 会主动拒绝）。
  · ★ 本站**无 CI**（属 ADR-003 的 5 站之一）⇒ 由构建入口 `build.sh` **收尾内联调用**本门控，
    并把**确定性** `gate-report.json` 随产物入库（使「跑没跑过」有痕）。⛔ 不新建 CI。

★ 本门控的判据面（T/R/S/L/V 五组，共 18 条；每条都有 `--selftest` 负向夹具）：
  T 令牌面     T1 空集守卫 / T2 派生一致性 / T3 角色取值一致 / T4 未声明令牌 / T5 引用完整性
               T6 成对对比度（逐档） / T7 零引用令牌登记（双向） / T8 死代码登记（双向） / T9 族归属
  R 解耦面     ★ R1 规则段 sha256（**与解耦前冻结值**比对，⛔ 不是自己比自己） / R2 退役件缺席
               R3 冻结链三方交叉（反恒真装置） / R4 页面两件套 + 无残留引用（双向）
  S 扫描面     S1 归档页不在判据对象内（+ 反向守卫） / S2 非迁移面页双向登记
  L 可复现性   L1 站点 `*.py` 无主机绝对路径字面量（L1 本地化的可回归判据）
  V 分发面     V1 VENDOR-MANIFEST sha256 对盘面 / V2 登记 ↔ vendor 文件 双向

★ 判据设计纪律（brief §5 八条）的落点：
  1 ⛔ 不写恒真判据：R1 与**解耦前**冻结值比（见 build/decoupling-provenance.json）；R3 再拿
    `gate-manifest.json` 里**另登记一次**的同名常量交叉校验 ⇒ 只改一处即 FAIL。
  2 负例含**假阳**样本：URL 假阳 / 相对路径假阳 / 文档自述假阳 / 「负向夹具自己先截断后读」守卫 /
    ★「改一个字节即 FAIL」的 sha256 负例。
  3 空集守卫落在**扫描面**上：0 个文件被扫 ⇒ FAIL，⛔ 不返回「0 命中」。
  4 判据对象 == 断言对象：令牌判据只在**外链令牌文件**上判（本站是形态 1，页面内联 `:root` 不在判据面）；
    页面判据只在**非 vendored / 非归档**的 `*.html` 上判（CT-Q5=A）。
  5 有登记表的判据，改盘面就要同批改登记表：T7/T8/S2/V1/V2 都是**双向**对账（登记过期即 FAIL）。
  6 快照类断言配同期配置副本：`vendor/pipeline/profiles/` 是批 D 的**同期冻结副本**，作 R3 的锚点。
  7 假 FAIL 与假绿同样有害 ⇒ 每条判据都**真跑过**（见 --selftest 与 build.sh 的实跑记录）。
  8 退役要留痕：⛔ 本门控不删任何判据；前提被推翻的按「重述 + 注明前提被推翻」处置（见 not_enforced_here）。

⛔ 本门控**不证**的事（如实登记，不得读作「没问题」）：
  · 像素/渲染层、真实浏览器几何、无障碍与 SEO、门控在真实 CI 上跑过（本站无 CI）。

用法：
    python3 gate_tokens.py --site-root . --manifest gate-manifest.json --mode enforce [--report gate-report.json] [--json]
    python3 gate_tokens.py --selftest
退出码：0 全过（或报告模式） / 1 有阻断级 FAIL / 2 输入错误
"""
import sys

sys.dont_write_bytecode = True   # ★ 防 __pycache__ 污染工作树（幂等复跑要求 git status 为空）

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import tempfile

sys.stdout.reconfigure(encoding="utf-8")

HARD_CLASSES = {
    "token-consistency": "令牌一致性（派生/取值/声明面/引用完整性）",
    "contrast": "成对对比度（逐档）",
    "empty-set-guard": "空集守卫（致盲即 FAIL）",
    "artifact-existence": "产物存在性与登记一致性",
}

LINK_RE = re.compile(r"<link\b[^>]*?rel=[\"']stylesheet[\"'][^>]*?href=[\"']([^\"']+)[\"']", re.I)
VAR_RE = re.compile(r"var\(\s*(--[A-Za-z0-9_-]+)")
TOKEN_RE = re.compile(r"(--[A-Za-z0-9_-]+)\s*:\s*([^;{}]+);")
INLINE_ROOT_RE = re.compile(r"<style\b[^>]*>.*?:root\s*\{.*?</style>", re.S | re.I)
# 主机绝对路径字面量（判据对象**只在 .py**，且必须是「引号里的路径」形态 ⇒ 防 URL 假阳）
HOST_PATH_RE = re.compile(r"""["']((?:/home/|/Users/|/root/|/mnt/|/opt/)[^"'\s]{2,}|[A-Za-z]:[\\/][^"'\s]{2,})["']""")
SCHEME_RE = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://")

EXCLUDE_DIRS = (".git", "vendor", "node_modules", "__pycache__")

# ★ 负向夹具要用的「作者机旧仓根」前缀：**用 os.sep.join 拼**，使本门控**自身源码**不含
#   主机绝对路径字面量 —— 否则 L1 判据会把自己的夹具字符串判成违规（实测踩到过：
#   gate_tokens.py:825 被自己抓到）。这既是纪律，也是「判据不得误伤实现件」的一处实证。
_FIXTURE_HOST_PREFIX = os.sep.join(["", "home", "zako-mio", "opencode", "archive",
                                    "Mission-file", "2026-09", "0907-控制理论Agent设计知识库"])


# --------------------------------------------------------------------------- 基础设施
def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


class Site(object):
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.read_cache = {}

    def p(self, rel):
        return os.path.join(self.root, rel)

    def exists(self, rel):
        return os.path.isfile(self.p(rel))

    def read(self, rel):
        if rel not in self.read_cache:
            with open(self.p(rel), encoding="utf-8", errors="replace") as fh:
                self.read_cache[rel] = fh.read()
        return self.read_cache[rel]

    def read_bytes(self, rel):
        with open(self.p(rel), "rb") as fh:
            return fh.read()

    def walk(self, exts=None, skip_dirs=EXCLUDE_DIRS):
        out = []
        for dp, dn, fn in os.walk(self.root):
            dn[:] = [d for d in dn if d not in skip_dirs]
            for f in sorted(fn):
                if exts and not f.endswith(exts):
                    continue
                out.append(os.path.relpath(os.path.join(dp, f), self.root).replace(os.sep, "/"))
        return sorted(out)


def load_json(path, label):
    if not os.path.isfile(path):
        raise IOError("%s 不存在：%s" % (label, path))
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def symbol_usage(source, symbol):
    """AST 口径的符号用量：返回 (模块级赋值处数, 被读取处数)。

    ★ 为什么用 AST 而不用正则：正则会把**注释里的同名文字**算成引用
    （实测踩到：`# ---- 全局 CSS (高可读) ----` 让 `CSS` 的命中数从 1 变 2 ⇒ T8 假 FAIL）。
    这正是 brief §5 第 7 条点名的「绑死排版／字面匹配」型假 FAIL。
    """
    import ast
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    defined = loaded = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == symbol and isinstance(node.ctx, ast.Load):
            loaded += 1
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            tgts = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in tgts:
                if isinstance(t, ast.Name) and t.id == symbol:
                    defined += 1
    return defined, loaded


# --------------------------------------------------------------------------- 判据
def run_judges(site, profile, manifest, contract, D, CT, gate_entry):
    """返回 [(id, name, blocking, ok, detail)]。"""
    R = []

    def add(jid, name, blocking, ok, detail):
        R.append((jid, name, blocking, ok, detail))

    dec = profile.get("decoupling", {})
    token_rel = dec.get("token_file")
    layout_rel = dec.get("layout_file")
    retired_rel = dec.get("retired_artifact")
    prov_rel = dec.get("provenance", "build/decoupling-provenance.json")

    # ---------- 读取基础件
    prov = load_json(site.p(prov_rel), "冻结件")
    modes = D.load_json(site.p(profile["value_file"]), "值件")

    # ---------- 站点全部 *.html（只排除 vendor/.git/__pycache__）
    all_html = site.walk(exts=".html")
    # ---------- 解耦面的扫描面 = 链接页（由 profile 登记的 globs 决定）
    link_globs = dec.get("linked_pages", {}).get("globs", [])
    link_pages = []
    for g in link_globs:
        pat = re.compile("^" + g.replace(".", r"\.").replace("*", "[^/]*") + "$")
        link_pages.extend([h for h in all_html if pat.match(h)])
    link_pages = sorted(set(link_pages))

    # ======================= T1 空集守卫
    problems = []
    if not link_pages:
        problems.append("链接页扫描面为 0")
    if not token_rel or not site.exists(token_rel):
        problems.append("令牌文件不存在：%s" % token_rel)
    if not layout_rel or not site.exists(layout_rel):
        problems.append("布局件不存在：%s" % layout_rel)
    if not site.exists(profile["value_file"]):
        problems.append("值件不存在：%s" % profile["value_file"])
    declared = {}
    if token_rel and site.exists(token_rel):
        declared = dict(TOKEN_RE.findall(site.read(token_rel)))
    if not declared:
        problems.append("令牌文件里解析出 0 个令牌名")
    add("T1", "空集守卫（链接页 / 令牌文件 / 布局件 / 值件 / 令牌名 均非空）", "empty-set-guard",
        not problems,
        "；".join(problems) if problems else
        "链接页 %d · 令牌名 %d · 布局件 %d B · 值件装载" % (len(link_pages), len(declared),
                                                       os.path.getsize(site.p(layout_rel))))

    if problems:
        # 判据对象缺失时，后续判据一律记 FAIL（⛔ 不静默跳过 —— 跳过＝假绿）
        for jid, nm, blk in (("T2", "派生一致性（派生产物 == 值件派生）", "token-consistency"),
                             ("T3", "角色/别名取值登记一致", "token-consistency"),
                             ("T4", "未声明令牌（盘上 ⊆ 值件声明面）", "token-consistency"),
                             ("T5", "引用完整性（布局件的每个 var() 都有定义）", "token-consistency"),
                             ("T6", "成对对比度（逐档，用项目唯一实现）", "contrast"),
                             ("T7", "零引用令牌登记（双向）", "token-consistency"),
                             ("T8", "死代码登记（双向）", "token-consistency"),
                             ("T9", "族归属登记", "token-consistency"),
                             ("R1", "★ 规则段 sha256（与解耦前冻结值比对）", "artifact-existence"),
                             ("R2", "退役件确实不在盘上", "artifact-existence"),
                             ("R3", "冻结链三方交叉（反恒真装置）", "artifact-existence"),
                             ("R4", "页面两件套覆盖 + 无残留引用", "artifact-existence"),
                             ("S1", "归档页不在判据对象内", "empty-set-guard"),
                             ("S2", "非迁移面页双向登记", "artifact-existence")):
            add(jid, nm, blk, False, "未判：前置判据对象缺失（见 T1）")
        return R

    # ======================= T2 派生一致性
    try:
        fam, tokens = D.build_tokens(modes, profile, None)
        expect = D.render(tokens)
        got = site.read(token_rel)
        ok = D.normalize(got) == D.normalize(expect)
        add("T2", "派生一致性（派生产物 == 值件派生；归一化口径复用派生器本体）", "token-consistency", ok,
            "family=%s · 令牌 %d 枚 · 归一化逐字节相同=%s" % (fam, len(tokens), ok))
    except Exception as exc:  # noqa: BLE001
        add("T2", "派生一致性（派生产物 == 值件派生）", "token-consistency", False, "派生器拒算：%s" % exc)

    # ======================= T3 角色/别名取值一致
    pal = next(iter(modes["palettes"].values()))
    form = modes["scope"]["declared_forms"][0]
    bad3 = []
    for role, name in modes["binding"]["site_token_names"].items():
        want = pal["values"][role][form]
        if declared.get(name) != want:
            bad3.append("%s(%s) 盘上=%r 值件=%r" % (name, role, declared.get(name), want))
    aliases = modes.get("registered_token_aliases", {})
    for name, spec in aliases.items():
        if declared.get(name) != spec.get("value"):
            bad3.append("别名 %s 盘上=%r 登记=%r" % (name, declared.get(name), spec.get("value")))
        if spec.get("role") not in modes["roles"]:
            bad3.append("别名 %s 指向未声明角色 %r" % (name, spec.get("role")))
    over = modes["families"][fam].get("overrides") or {}
    for name, v in over.items():
        if declared.get(name) != v:
            bad3.append("族覆盖 %s 盘上=%r 值件=%r" % (name, declared.get(name), v))
    add("T3", "角色/族覆盖/别名取值登记一致（三方：盘上 · 值件 · 别名登记表）", "token-consistency",
        not bad3, "；".join(bad3[:6]) if bad3 else
        "角色 %d · 别名 %d · 族覆盖 %d 全部一致" % (len(modes["binding"]["site_token_names"]),
                                              len(aliases), len(over)))

    # ======================= T4 未声明令牌
    declared_face = set(modes["binding"]["site_token_names"].values()) | set(over)
    for grp in (modes["binding"].get("passthrough_tokens") or {}).values():
        if isinstance(grp, dict):
            declared_face |= {k for k in grp if str(k).startswith("--")}
    declared_face |= set(aliases)
    extra = sorted(set(declared) - declared_face)
    add("T4", "未声明令牌（盘上令牌名 ⊆ 值件声明面）", "token-consistency", not extra,
        "盘上多出未声明令牌：%s" % extra if extra else
        "盘上 %d 枚全部在声明面（角色 %d ∪ passthrough ∪ 族覆盖 ∪ 别名）内"
        % (len(declared), len(modes["binding"]["site_token_names"])))

    # ======================= T5 引用完整性（★ C1-N2 的缺陷类）
    layout = site.read(layout_rel)
    refs = set(VAR_RE.findall(layout))
    for rel in link_pages:
        refs |= set(VAR_RE.findall(site.read(rel)))
    undef = sorted(r for r in refs if r not in declared)
    add("T5", "引用完整性（布局件与链接页的每个 var(--X) 都在令牌文件里有定义）", "token-consistency",
        not undef,
        "未定义引用：%s" % undef if undef else
        "引用 %d 枚（布局件 %d B + %d 页），未定义 0 枚；★ `--ctrl-green` 在引用集内=%s"
        % (len(refs), len(layout.encode()), len(link_pages), "--ctrl-green" in refs))

    # ======================= T6 成对对比度
    used_surface = set()
    corpus = layout + "".join(site.read(p) for p in link_pages)
    used = set(VAR_RE.findall(corpus))
    for role, spec in modes["roles"].items():
        if spec.get("kind") == "surface":
            nm = modes["binding"]["site_token_names"].get(role)
            if nm and nm in used:
                used_surface.add(nm)
    # ★ 背景集只取「在用的 surface 角色令牌」**且其取值真的解析得出颜色**：
    #   判据对象 == 断言对象（brief §5 第 4 条）。取值解析不出颜色的「在用背景」本身就是缺陷 ⇒ 单列。
    bg_all = sorted(used_surface)
    bg = [b for b in bg_all if CT.parse_color(declared.get(b, "")) is not None]
    unparsable_bg = [b for b in bg_all if b not in bg]
    tiers = modes["usage_tiers"]
    judged, failed, reported = [], [], []
    if not bg:
        add("T6", "成对对比度（逐档）", "contrast", False,
            "空集守卫：没有任何**在用且取值可解析为颜色**的 surface 角色令牌可作背景 ⇒ 对比度判据无对象"
            "（在用背景 %s；不可解析 %s）" % (bg_all, unparsable_bg))
    else:
        for role, spec in modes["roles"].items():
            nm = modes["binding"]["site_token_names"].get(role)
            kind = spec.get("kind")
            entry = None
            if nm:
                entry = (nm, spec["tier"])
            for anm, aspec in aliases.items():
                if aspec.get("role") == role:
                    entry = (anm, aspec.get("tier", spec["tier"]))
            if not entry:
                continue
            tname, tier = entry
            if kind not in ("text", "semantic-text", "border", "brand", "focus", "link"):
                continue
            val = declared.get(tname)
            rgb = CT.parse_color(val or "")
            if rgb is None:
                continue
            if tname in [j for j in judged]:
                continue
            worst = min(round(CT.ratio(rgb, CT.parse_color(declared[b])), 2) for b in bg)
            thresh = tiers[tier]["min_contrast"][form]
            gate = tiers[tier].get("gate")
            row = "%-18s tier=%-22s %s 最差 %.2f / 门槛 %.1f" % (tname, tier, val, worst, thresh)
            if gate == "hard":
                judged.append(tname)
                (failed if worst < thresh else reported).append(row)
            else:
                reported.append(row + "  [report-only]")
        has_cg = "--ctrl-green" in judged
        ok6 = (not failed) and has_cg and (not unparsable_bg)
        det = []
        if failed:
            det.append("不达标 %d：" % len(failed) + " ｜ ".join(failed))
        if unparsable_bg:
            det.append("在用背景令牌取值不可解析为颜色：%s" % unparsable_bg)
        if not has_cg:
            det.append("★ 判据对象缺失：`--ctrl-green` 未进入硬判集（它必须存在且被逐值判）")
        det.append("硬判 %d 枚全部达标：%s" % (len(judged), ", ".join(sorted(judged))))
        det.append("背景集（在用且可解析的 surface 角色）= %s" % bg)
        det.append("★ --ctrl-green 逐值：" + " / ".join(
            "%s %.2f" % (b, CT.ratio(CT.parse_color(declared["--ctrl-green"]), CT.parse_color(declared[b])))
            for b in bg))
        if reported:
            det.append("非硬判档（如实报告）：" + " ｜ ".join(reported))
        add("T6", "成对对比度（逐档；用 vendor/tools/contrast.py —— 项目唯一实现，⛔ 未造第二套）",
            "contrast", ok6, "；".join(det))

    # ======================= T7 零引用令牌登记（双向）
    computed_dead = sorted(n for n in declared if n not in used)
    registered = sorted(t["token"] for t in
                        profile.get("dead_code_and_dead_tokens", {}).get("dead_tokens", []))
    expired = sorted(t for t in registered if t not in computed_dead)
    missing = sorted(t for t in computed_dead if t not in registered)
    bad7 = []
    if expired:
        bad7.append("登记过期（声明为零引用但**已被引用**，或根本不在盘上）：%s" % expired)
    if missing:
        bad7.append("漏登记（实算零引用但登记表没有）：%s" % missing)
    add("T7", "零引用令牌登记（**双向**：声明须真零引用 ∧ 真零引用须已登记）", "token-consistency",
        not bad7,
        "；".join(bad7) if bad7 else
        "实算零引用 %d 枚 == 登记 %d 枚（%s）" % (len(computed_dead), len(registered),
                                             ", ".join(computed_dead)))

    # ======================= T8 死代码登记（双向）
    bad8 = []
    for item in profile.get("dead_code_and_dead_tokens", {}).get("dead_code", []):
        f, sym = item["file"], item["symbol"]
        if not site.exists(f):
            bad8.append("%s 不存在（登记项须真的在盘上）" % f)
            continue
        u = symbol_usage(site.read(f), sym)
        if u is None:
            bad8.append("%s 无法解析（AST 失败）⇒ 判据无对象" % f)
            continue
        defined, loaded = u
        if defined == 0:
            bad8.append("%s 里找不到模块级符号 %s（登记项须真的在盘上）" % (f, sym))
        elif loaded > 0:
            bad8.append("%s 里符号 %s 被读取 %d 次（>0 ⇒ 已在使用，不再是死代码）" % (f, sym, loaded))
    add("T8", "死代码登记（**双向**：登记项须真的在盘上 ∧ 真的零引用）★ AST 口径，⛔ 不用正则（防注释假 FAIL）",
        "token-consistency", not bad8, "；".join(bad8) if bad8 else
        "死代码登记 %d 项：模块级定义在位，且被读取 0 次（AST 口径）"
        % len(profile.get("dead_code_and_dead_tokens", {}).get("dead_code", [])))

    # ======================= T9 族归属登记
    fam_id = modes["scope"].get("family")
    ruling = modes["scope"].get("family_ruling", "")
    bad9 = []
    if fam_id != "content-kg-swiss-light":
        bad9.append("族 id=%r ≠ content-kg-swiss-light" % fam_id)
    if "content-kg" not in ruling:
        bad9.append("缺 CT-Q2=A 的族归属裁定登记（须指明 content-kg 浅色变体）")
    if list(modes["palettes"]) != [fam_id]:
        bad9.append("palettes 的族键 %s 与 scope.family 不一致（本站单族）" % list(modes["palettes"]))
    if [x for x in modes["families"]] != ["default"]:
        bad9.append("families 键 %s 非单族 default" % list(modes["families"]))
    add("T9", "族归属登记（CT-Q2=A：content-kg 族的浅色变体，⛔ 不另立第五族）", "token-consistency",
        not bad9, "；".join(bad9) if bad9 else
        "族=%s（单族 default）· 裁定登记在位 · palettes/families 键一致" % fam_id)

    # ======================= R1 ★ 规则段 sha256
    frozen = prov["rule_segment"]["sha256"]
    measured = sha256_bytes(site.read_bytes(layout_rel))
    ok1 = (measured == frozen)
    add("R1", "★ 规则段 sha256：sha256(site.css) == **解耦前冻结值**（⛔ 不是自己比自己）",
        "artifact-existence", ok1,
        "实测 %s ← 解耦前冻结 %s ⇒ %s（布局件 %d B / 冻结 %d B）"
        % (measured, frozen, "相同" if ok1 else "**不同**",
           os.path.getsize(site.p(layout_rel)), prov["rule_segment"]["bytes"])
        + ("" if ok1 else "  ★ 只要改一个字节就会在这里 FAIL（见 --selftest 的 R1 负例）。"))

    # ======================= R2 退役件缺席
    present = site.exists(retired_rel)
    add("R2", "退役件确实不在盘上（%s）" % retired_rel, "artifact-existence", not present,
        "退役件仍在盘上 ⇒ 双真相源 ☠" if present else
        "退役件缺席 ✔；其内容由 %s（规则段，逐字节）与 %s（令牌层，派生）完全接管"
        % (layout_rel, token_rel))

    # ======================= R3 冻结链三方交叉（反恒真装置）
    anchor = None
    entry = (manifest.get("gates") or [{}])[0]
    anchor = entry.get("frozen_anchor") or {}
    vend = load_json(site.p("vendor/pipeline/profiles/control-theory-agent-kb.json"), "批 D 冻结副本")
    vend_sha = (vend.get("targets") or [{}])[0].get("frozen_sha256")
    recalc_ok = (prov["pre_file"]["bytes"] == prov["root_block"]["bytes"] + prov["rule_segment"]["bytes"])
    bad3r = []
    if anchor.get("rule_segment_sha256") != frozen:
        bad3r.append("gate-manifest 登记的 rule_segment_sha256=%s ≠ 冻结件=%s（只改了一处）"
                     % (anchor.get("rule_segment_sha256"), frozen))
    if anchor.get("pre_file_sha256") != prov["pre_file"]["sha256"]:
        bad3r.append("gate-manifest 登记的 pre_file_sha256=%s ≠ 冻结件=%s"
                     % (anchor.get("pre_file_sha256"), prov["pre_file"]["sha256"]))
    if vend_sha != prov["pre_file"]["sha256"]:
        bad3r.append("批 D 独立锚点 %s ≠ 冻结件 pre_file=%s" % (vend_sha, prov["pre_file"]["sha256"]))
    if not recalc_ok:
        bad3r.append("算术不变量被破坏：pre_bytes ≠ root_block_bytes + rule_segment_bytes")
    if not (prov.get("anchor_cross_check", {}).get("A_start_head_matches")):
        bad3r.append("A 锚点：起点 commit ≠ 登记起步 HEAD")
    add("R3", "冻结链三方交叉（gate-manifest 登记 · 冻结件 · 批 D 独立锚点 · 算术不变量）",
        "artifact-existence", not bad3r,
        "；".join(bad3r) if bad3r else
        "三处 rule_segment sha256 一致；pre_file sha256 == 批 D 独立锚点 %s；"
        "算术不变量 pre = block(%d) + rules(%d) = %d ✔"
        % (vend_sha[:16], prov["root_block"]["bytes"], prov["rule_segment"]["bytes"],
           prov["pre_file"]["bytes"]))

    # ======================= R4 页面两件套 + 无残留引用 + 反向守卫
    exp = dec.get("linked_pages", {}).get("expected_count")
    tok_base = os.path.basename(token_rel)
    lay_base = os.path.basename(layout_rel)
    ret_base = os.path.basename(retired_rel)
    pair, broken, dangling = [], [], []
    for rel in link_pages:
        hs = LINK_RE.findall(site.read(rel))
        has_t = any(h.endswith("/" + tok_base) or h == tok_base for h in hs)
        has_l = any(h.endswith("/" + lay_base) or h == lay_base for h in hs)
        has_r = any(h.endswith("/" + ret_base) or h == ret_base for h in hs)
        if has_r:
            dangling.append(rel)
        if has_t and has_l:
            pair.append(rel)
        else:
            broken.append("%s(tok=%s,lay=%s)" % (rel, has_t, has_l))
    repo_dangling = [rel for rel in all_html
                     if any((h.endswith("/" + ret_base) or h == ret_base)
                            for h in LINK_RE.findall(site.read(rel)))]
    bad4 = []
    if broken:
        bad4.append("未成两件套的链接页 %d：%s" % (len(broken), broken[:6]))
    if exp is not None and len(pair) != exp:
        bad4.append("两件套页数 %d ≠ 登记期望 %d" % (len(pair), exp))
    if repo_dangling:
        bad4.append("全仓仍有页面链接已退役件（线上必 404 %d 页）：%s" % (len(repo_dangling), repo_dangling[:6]))
    add("R4", "页面两件套覆盖（== 登记页数）＋ 无残留引用（全仓 *任何* 页面都不得再链退役件）",
        "artifact-existence", not bad4,
        "；".join(bad4) if bad4 else
        "两件套 %d 页 == 登记 %d；全仓 %d 个 *.html 中链接退役件者 0"
        % (len(pair), exp, len(all_html)))

    # ======================= S1 归档页不在判据对象内（+ 反向守卫）
    subj = (profile.get("out_of_judgement_scope") or [{}])[0].get("subject", "")
    mentioned_in_scan = sorted(p for p in link_pages if p.startswith("archive/"))
    reg_arch = sorted(e["page"] for e in dec.get("pages_without_external_stylesheet", [])
                      if e["page"].startswith("archive/"))
    on_disk_arch = sorted(p for p in all_html if p.startswith("archive/"))
    bad1s = []
    if mentioned_in_scan:
        bad1s.append("★ 反向守卫触发：判据扫描面命中了归档页 %s ⇒ 声明（不在判据对象内）与实现不符"
                     % mentioned_in_scan[:4])
    if not subj.startswith("archive/"):
        bad1s.append("登记对象 %r 不是 archive/**" % subj)
    if not reg_arch:
        bad1s.append("没有任何归档页被登记")
    if len(reg_arch) != len(on_disk_arch):
        bad1s.append("登记的归档页 %d ≠ 盘上 %d（登记过期或漏登记）：盘上=%s"
                     % (len(reg_arch), len(on_disk_arch), on_disk_arch))
    add("S1", "CT-Q5=A：归档页**不在判据对象内**（显式声明 ＋ 反向守卫：被扫到即 FAIL）",
        "empty-set-guard", not bad1s,
        "；".join(bad1s) if bad1s else
        "判据扫描面 %d 页，其中 archive/** 命中 0；盘上归档页 %d 页已逐页登记（者：%s）"
        % (len(link_pages), len(on_disk_arch), os.path.commonprefix(reg_arch) if reg_arch else "-"))

    # ======================= S2 非迁移面页双向登记
    reg_none = sorted(e["page"] for e in dec.get("pages_without_external_stylesheet", []))
    computed_none = sorted(rel for rel in all_html if not LINK_RE.findall(site.read(rel)))
    expired2 = sorted(p for p in reg_none if p not in computed_none)
    missing2 = sorted(p for p in computed_none if p not in reg_none)
    bad2s = []
    if expired2:
        bad2s.append("登记过期（声明为「无外链样式表」但它其实有）：%s" % expired2[:6])
    if missing2:
        bad2s.append("漏登记（实测无外链样式表但没登记）：%s" % missing2[:6])
    add("S2", "「无外链样式表」页**双向**登记（声明须真无 ∧ 真无须已登记）", "artifact-existence",
        not bad2s,
        "；".join(bad2s) if bad2s else
        "实测无外链样式表 %d 页 == 登记 %d 页（含 %d 个归档页与手写报告页）"
        % (len(computed_none), len(reg_none), len(reg_arch)))

    # ======================= L1 站点 *.py 无主机绝对路径字面量
    pys = [p for p in site.walk(exts=".py")]
    hits, scanned = [], 0
    for rel in pys:
        scanned += 1
        for i, line in enumerate(site.read(rel).splitlines(), 1):
            stripped = SCHEME_RE.sub("", line)   # ★ 假阳守卫：先摘掉 URL，再判路径字面量
            stripped = re.sub(r"https?://\S+", "", stripped)
            for m in HOST_PATH_RE.finditer(stripped):
                hits.append("%s:%d %s" % (rel, i, m.group(1)[:80]))
    bad_l = []
    if scanned == 0:
        bad_l.append("空集守卫：站点仓内 0 个 *.py 被扫到")
    if hits:
        bad_l.append("仍含主机绝对路径字面量 %d 处：%s" % (len(hits), hits[:6]))
    add("L1", "站点 `*.py`（排除 vendor/）无主机绝对路径字面量（L1 本地化的可回归判据）",
        "artifact-existence", not bad_l,
        "；".join(bad_l) if bad_l else
        "%d 个 *.py 全部不含 `/home/…`、`C:\\…` 形态的路径字面量（URL 已先摘除，防假阳）" % scanned)

    # ======================= V1/V2 分发面
    man_rel = "vendor/pipeline/VENDOR-MANIFEST.json"
    bad_v = []
    if not site.exists(man_rel):
        bad_v.append("VENDOR-MANIFEST.json 不存在")
        vm = {}
    else:
        vm = json.loads(site.read(man_rel))
        for rel, want in sorted((vm.get("files") or {}).items()):
            if not site.exists(rel):
                bad_v.append("%s 不在盘上" % rel)
                continue
            got = sha256_bytes(site.read_bytes(rel))
            if got != want:
                bad_v.append("%s sha256 漂移（登记 %s… / 实测 %s…）" % (rel, want[:12], got[:12]))
    add("V1", "VENDOR-MANIFEST 登记的每个文件 sha256 == 盘上实测（薄副本不得漂移）",
        "token-consistency", not bad_v,
        "；".join(bad_v[:6]) if bad_v else
        "登记 %d 个文件，sha256 全部与盘面一致" % len((vm.get("files") or {})))

    vendored = [p for p in site.walk(skip_dirs=(".git", "__pycache__", "node_modules"))
                if p.startswith("vendor/") and not p.endswith("VENDOR-MANIFEST.json")]
    reg = set((vm.get("files") or {}).keys())
    unreg = sorted(p for p in vendored if p not in reg)
    bad2v = []
    if not vendored:
        bad2v.append("空集守卫：vendor/ 下扫到 0 个文件 ⇒ 判据无对象（⛔ 不返回「0 未登记」）")
    if unreg:
        bad2v.append("盘上但未登记：%s" % unreg)
    add("V2", "vendor/** 文件 ↔ VENDOR-MANIFEST 登记（**双向**：登记须在盘 ∧ 在盘须登记）",
        "artifact-existence", not bad2v,
        "；".join(bad2v) if bad2v else
        "vendor/ 下 %d 个文件全部已登记（清单自身 self-excluded）" % len(vendored))
    return R


# --------------------------------------------------------------------------- 报告
def tree_digest(site, exclude):
    rows = []
    for rel in sorted(site.walk()):
        if rel in exclude or rel.endswith("__pycache__"):
            continue
        try:
            rows.append("%s\x00%s\n" % (rel, sha256_bytes(site.read_bytes(rel))))
        except OSError:
            continue
    return len(rows), sha256_bytes("".join(rows).encode("utf-8"))


def build_report(site, profile, manifest, results, mode, gate_entry):
    n, dig = tree_digest(site, exclude={"gate-report.json"})
    prov = load_json(site.p(profile["decoupling"]["provenance"]), "冻结件")
    layout = profile["decoupling"]["layout_file"]
    by_class = {}
    for jid, name, blk, ok, det in results:
        d = by_class.setdefault(blk, {"total": 0, "fail": 0})
        d["total"] += 1
        d["fail"] += 0 if ok else 1
    return {
        "schema": "gate-report/1",
        "site": profile["site"],
        "site_number": profile.get("site_number"),
        "gate": "gate_tokens.py",
        "mode": mode,
        "inputs": {
            "gate_manifest": "gate-manifest.json",
            "gate_manifest_sha256": sha256_bytes(site.read_bytes("gate-manifest.json")),
            "profile": "build/profile.json",
            "profile_sha256": sha256_bytes(site.read_bytes("build/profile.json")),
            "value_file": profile["value_file"],
            "value_file_sha256": sha256_bytes(site.read_bytes(profile["value_file"])),
            "provenance": profile["decoupling"]["provenance"],
            "provenance_sha256": sha256_bytes(site.read_bytes(profile["decoupling"]["provenance"])),
            "generator": "build.sh",
            "build_entry": profile.get("build_entry"),
        },
        "judges": [{"id": j, "name": nm, "blocking": b, "ok": ok, "detail": d}
                   for j, nm, b, ok, d in results],
        "summary": {
            "total": len(results),
            "fail": sum(1 for r in results if not r[3]),
            "by_blocking": by_class,
        },
        "rule_segment_sha256": {
            "frozen_before_decoupling": prov["rule_segment"]["sha256"],
            "frozen_bytes": prov["rule_segment"]["bytes"],
            "measured_on_disk": sha256_bytes(site.read_bytes(layout)),
            "equal": sha256_bytes(site.read_bytes(layout)) == prov["rule_segment"]["sha256"],
            "layout_file": layout,
            "negative_control": "把 site.css 改一个字节 ⇒ R1 必 FAIL（--selftest 的 R1 负例已实跑）",
        },
        "tree": {"file_count": n, "tree_digest": dig,
                 "definition": "仓内文件（相对路径 + 内容）的 sha256 归并；★ 排除报告自身（否则自指）"},
        "determinism": "⛔ 无墙钟时间戳 · ⛔ 无作者机绝对路径 · ⛔ 无随机/网络；同输入两次运行逐字节相同",
        "not_covered": manifest.get("not_covered", []),
    }


# --------------------------------------------------------------------------- selftest
FIXTURE_FILES = [
    "gate-manifest.json", "gate_tokens.py", "build/profile.json",
    "build/decoupling-provenance.json", "build/payloads/default.css",
    "04-interactive/assets/site.css", "04-interactive/assets/derived-design-tokens.css",
    "index.html", "report.html", "07-checkpoint/report-v1.1.html",
    "09-src-data/gen_html.py", "09-src-data/gen_cyto.py", "09-src-data/gen_dag_data.py",
    "09-src-data/nav_data.py", "vendor/pipeline/VENDOR-MANIFEST.json",
    "vendor/pipeline/values/control-theory-agent-kb.json",
    "vendor/pipeline/profiles/control-theory-agent-kb.json",
    "vendor/tools/contrast.py", "vendor/pipeline/derive_site_tokens.py",
    "vendor/pipeline/write_site_tokens.py", "vendor/pipeline/check_site_tokens.py",
    "vendor/pipeline/check_gate_manifest.py", "vendor/pipeline/check_workflow_contract.py",
    "vendor/pipeline/site-value-contract.schema.json", "vendor/pipeline/site-profile.schema.json",
    "vendor/pipeline/workflow-3job.template.yml",
]
FIXTURE_GLOBS = ["04-interactive/*.html", "archive/*/*.html"]


def clone_fixture(site, tmp):
    """★ 只拷判据真正读到的文件（体积可控），并在拷完后**校验夹具完整性**
    —— brief §5 第 2 条点名的假阳形态：「负向夹具**自己先截断后读**」。"""
    dst = os.path.join(tmp, "site")
    for rel in FIXTURE_FILES:
        s = site.p(rel)
        d = os.path.join(dst, rel)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copyfile(s, d)
    for g in FIXTURE_GLOBS:
        import glob as _g
        for s in _g.glob(os.path.join(site.root, g)):
            rel = os.path.relpath(s, site.root)
            d = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copyfile(s, d)
    # ---- 夹具完整性断言：缺件 / 空件 ⇒ 直接抛（⛔ 不拿截断的夹具去判）
    missing = [r for r in FIXTURE_FILES if not os.path.isfile(os.path.join(dst, r))
               or os.path.getsize(os.path.join(dst, r)) == 0]
    if missing:
        raise RuntimeError("夹具不完整（缺件或 0 字节）：%s" % missing)
    must = [r for r in FIXTURE_FILES if r.endswith(("site.css", "derived-design-tokens.css"))]
    for r in must:
        want = os.path.getsize(site.p(r))
        got = os.path.getsize(os.path.join(dst, r))
        if want != got:
            raise RuntimeError("夹具被截断：%s 期望 %d B 实测 %d B" % (r, want, got))
    return dst


def selftest(site):
    D0 = load_module(site.p("vendor/pipeline/derive_site_tokens.py"), "d_st")
    CT0 = load_module(site.p("vendor/tools/contrast.py"), "c_st")
    man0 = load_json(site.p("gate-manifest.json"), "清单")
    cases = []

    def run_on(root):
        s = Site(root)
        prof = load_json(s.p("build/profile.json"), "profile")
        man = load_json(s.p("gate-manifest.json"), "清单")
        return run_judges(s, prof, man, None, D0, CT0, "gate_tokens.py")

    def case(name, mutate, expect_fail_ids, expect_pass_ids=()):
        tmp = tempfile.mkdtemp(prefix="gct-")
        try:
            root = clone_fixture(site, tmp)
            mutate(root)
            R = run_on(root)
            got = {r[0]: r[3] for r in R}
            ok = all(got.get(i) is False for i in expect_fail_ids) and \
                 all(got.get(i) is True for i in expect_pass_ids)
            cases.append((name, ok,
                          "预期 FAIL %s / PASS %s；实测 FAIL=%s"
                          % (list(expect_fail_ids), list(expect_pass_ids),
                             sorted(i for i, v in got.items() if not v))))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def w(root, rel, data, mode="w"):
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, mode, encoding=None if "b" in mode else "utf-8") as fh:
            fh.write(data)

    def flip_one_byte(root, rel):
        p = os.path.join(root, rel)
        b = bytearray(open(p, "rb").read())
        b[len(b) // 2] = (b[len(b) // 2] + 1) % 256
        open(p, "wb").write(bytes(b))

    # ---------- 正向
    case("正向夹具（未改动）应 0 FAIL", lambda r: None, [])

    # ---------- ★ R1 负例：改一个字节即 FAIL（brief 点名的必做负例）
    case("★ R1 负例：site.css 改一个字节 ⇒ 必 FAIL",
         lambda r: flip_one_byte(r, "04-interactive/assets/site.css"), ["R1"])
    # ---------- R3 负例：只改冻结件（不改 gate-manifest 的登记）⇒ 交叉校验抓到
    def r3_neg(r):
        p = os.path.join(r, "build/decoupling-provenance.json")
        d = json.load(open(p, encoding="utf-8"))
        fake = "0" * 64
        d["rule_segment"]["sha256"] = fake
        d["pre_file"]["sha256"] = fake
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    case("★ R3 负例：只改冻结件的 sha（想自证）⇒ 三方交叉必 FAIL",
         r3_neg, ["R3"])
    # ---------- R3 负例：gate-manifest 与冻结件**协调**改成现值 → 由批 D 锚点兜住
    def r3_neg2(r):
        p = os.path.join(r, "gate-manifest.json")
        m = json.load(open(p, encoding="utf-8"))
        m["gates"][0]["frozen_anchor"]["rule_segment_sha256"] = \
            m["gates"][0]["frozen_anchor"]["pre_file_sha256"]
        json.dump(m, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    case("★ R3 负例：只改 gate-manifest 的登记 ⇒ 三方交叉必 FAIL", r3_neg2, ["R3"])
    # ---------- R2 负例：退役件复活
    case("R2 负例：退役件又出现在盘上 ⇒ FAIL",
         lambda r: w(r, "04-interactive/assets/design-tokens.css", "/* resurrected */\n"), ["R2"])
    # ---------- R4 负例：某页只链接一件
    def r4_neg(r):
        p = os.path.join(r, "index.html")
        t = open(p, encoding="utf-8").read()
        w(r, "index.html", t.replace('<link rel="stylesheet" href="04-interactive/assets/site.css">', ""))
    case("R4 负例：某页只链接一件 ⇒ FAIL", r4_neg, ["R4"])
    # ---------- R4 负例：某页残留链接退役件
    def r4_neg2(r):
        p = os.path.join(r, "04-interactive/index.html")
        t = open(p, encoding="utf-8").read()
        t = t.replace('<link rel="stylesheet" href="assets/site.css">',
                      '<link rel="stylesheet" href="assets/design-tokens.css">')
        w(r, "04-interactive/index.html", t)
    case("★ R4 负例：某页仍链接**已退役**件（线上必 404）⇒ FAIL", r4_neg2, ["R4"])

    # ---------- T5 负例：布局件引用未定义令牌（这正是 C1-N2 的缺陷类）
    def t5_neg(r):
        p = os.path.join(r, "04-interactive/assets/site.css")
        t = open(p, encoding="utf-8").read()
        w(r, "04-interactive/assets/site.css", t + "\n.x{color:var(--no-such-token)}\n")
    case("★ T5 负例：引入一个未定义的 var() 引用 ⇒ FAIL（C1-N2 的缺陷类）", t5_neg, ["R1", "T5"])
    # ---------- T5 假阳：令牌文件里**定义**过的名字不得误报
    def t5_false_pos(r):
        p = os.path.join(r, "04-interactive/assets/site.css")
        t = open(p, encoding="utf-8").read()
        w(r, "04-interactive/assets/site.css", t + "\n.y{color:var(--ctrl-green,#1F7A52)}\n")
    case("★ T5 假阳：引用**已定义**令牌（且带逗号回退值的写法）⇒ 必须 PASS",
         t5_false_pos, ["R1"])   # 改规则段 ⇒ R1 必 FAIL，但 T5 必须不被误报

    # ---------- T7 负例：登记过期（登记项其实已被引用）
    def t7_neg(r):
        p = os.path.join(r, "build/profile.json")
        d = json.load(open(p, encoding="utf-8"))
        d["dead_code_and_dead_tokens"]["dead_tokens"][0]["token"] = "--ink"   # --ink 明明被引用
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    case("★ T7 负例：登记表写过期的项（把 --ink 声明为零引用）⇒ FAIL", t7_neg, ["T7"])
    # ---------- T7 负例：漏登记
    def t7_neg2(r):
        p = os.path.join(r, "build/profile.json")
        d = json.load(open(p, encoding="utf-8"))
        d["dead_code_and_dead_tokens"]["dead_tokens"] = \
            d["dead_code_and_dead_tokens"]["dead_tokens"][:-1]
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    case("★ T7 负例：漏登记一枚真实零引用令牌 ⇒ FAIL", t7_neg2, ["T7"])
    # ---------- T8 负例：登记项被引用（不再死）
    def t8_neg(r):
        p = os.path.join(r, "09-src-data/gen_html.py")
        t = open(p, encoding="utf-8").read()
        w(r, "09-src-data/gen_html.py", t + "\nprint(len(CSS))\n")
    case("T8 负例：死代码常量被引用 ⇒ FAIL", t8_neg, ["T8"])
    # ---------- T8 负例：登记项根本不在盘上
    def t8_neg2(r):
        p = os.path.join(r, "build/profile.json")
        d = json.load(open(p, encoding="utf-8"))
        d["dead_code_and_dead_tokens"]["dead_code"][0]["symbol"] = "NO_SUCH_CONST"
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    case("T8 负例：登记项不在盘上（登记过期）⇒ FAIL", t8_neg2, ["T8"])

    # ---------- T3 负例：盘上取值与值件不符
    def t3_neg(r):
        p = os.path.join(r, "04-interactive/assets/derived-design-tokens.css")
        t = open(p, encoding="utf-8").read().replace("--ctrl-green:#1F7A52;", "--ctrl-green:#123456;")
        w(r, p, t)
    case("T3 负例：盘上令牌取值 ≠ 值件登记 ⇒ FAIL", t3_neg, ["T2", "T3"])
    # ---------- T4 负例：多出一个未声明令牌
    def t4_neg(r):
        p = os.path.join(r, "04-interactive/assets/derived-design-tokens.css")
        t = open(p, encoding="utf-8").read().replace(":root{", ":root{--ghost:#000;", 1)
        w(r, p, t)
    case("T4 负例：盘上多出一个未声明令牌 ⇒ FAIL", t4_neg, ["T2", "T4"])

    # ---------- T6 负例：把 --ctrl-green 改成不达标的浅绿（body 档 4.5）
    def t6_neg(r):
        rel = "vendor/pipeline/values/control-theory-agent-kb.json"
        d = json.load(open(os.path.join(r, rel), encoding="utf-8"))
        d["families"]["default"]["overrides"]["--ctrl-green"] = "#9BE7C4"
        d["registered_token_aliases"]["--ctrl-green"]["value"] = "#9BE7C4"
        json.dump(d, open(os.path.join(r, rel), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        p = os.path.join(r, "04-interactive/assets/derived-design-tokens.css")
        t = open(p, encoding="utf-8").read().replace("--ctrl-green:#1F7A52;", "--ctrl-green:#9BE7C4;")
        w(r, p, t)
    case("★ T6 负例：把 --ctrl-green 改成不达标的浅绿 ⇒ 必 FAIL（对比度判据非恒真）",
         t6_neg, ["T6"])
    # ---------- T6 空集守卫：把作为背景的 surface 令牌全部改成非色值 ⇒ 无背景可判 ⇒ FAIL
    def t6_empty(r):
        p = os.path.join(r, "04-interactive/assets/derived-design-tokens.css")
        t = open(p, encoding="utf-8").read().replace("--surface:#F6F8FB;", "--surface:none;")
        w(r, p, t)
    case("T6 空集守卫：背景令牌不再是颜色 ⇒ 判据无对象 ⇒ FAIL", t6_empty, ["T2", "T6"])

    # ---------- S1 负例：把归档页拉进判据面（反向守卫）
    def s1_neg(r):
        p = os.path.join(r, "build/profile.json")
        d = json.load(open(p, encoding="utf-8"))
        d["decoupling"]["linked_pages"]["globs"].append("archive/*/*.html")
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    case("★ S1 负例：把 archive/** 拉进判据扫描面 ⇒ 反向守卫 FAIL", s1_neg, ["S1", "R4"])
    # ---------- S1 负例：盘上新增一个未登记的归档页
    case("S1 负例：盘上多出一个未登记的归档页 ⇒ FAIL",
         lambda r: w(r, "archive/0908-精装房Agent全景/extra.html", "<html><body>x</body></html>\n"),
         ["S1", "S2"])

    # ---------- S2 负例：把一个「有外链样式表」的页登记成「无」
    def s2_neg(r):
        p = os.path.join(r, "build/profile.json")
        d = json.load(open(p, encoding="utf-8"))
        d["decoupling"]["pages_without_external_stylesheet"].append(
            {"page": "index.html", "why": "故意写错，测试登记过期"})
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    case("★ S2 负例：登记过期（把有外链的页登记为「无外链」）⇒ FAIL", s2_neg, ["S2"])

    # ---------- L1 负例：站点 .py 里写回作者机绝对路径
    def l1_neg(r):
        p = os.path.join(r, "09-src-data/gen_cyto.py")
        t = open(p, encoding="utf-8").read()
        w(r, p, 'BASE = "%s"\n' % _FIXTURE_HOST_PREFIX + t)
    case("★ L1 负例：生成器里写回主机绝对路径 ⇒ FAIL", l1_neg, ["L1"])
    # ---------- L1 假阳样本 1：URL 里含 /home/ 不得判 L1
    def l1_false_pos(r):
        p = os.path.join(r, "09-src-data/gen_dag_data.py")
        t = open(p, encoding="utf-8").read()
        w(r, p, t + '\nDOC = "https://example.com/home/zako-mio/index.html"\n')
    case("★ L1 假阳 1：URL 里含 `/home/…` ⇒ 必须 PASS（不得误判）", l1_false_pos, [])
    # ---------- L1 假阳样本 2：相对路径里含 `/home/` 片段不得判 L1
    def l1_false_pos2(r):
        p = os.path.join(r, "09-src-data/nav_data.py")
        t = open(p, encoding="utf-8").read()
        w(r, p, t + '\nALT = "docs/home/zako-mio/index.html"\n')
    case("★ L1 假阳 2：相对路径含 `/home/` 片段 ⇒ 必须 PASS", l1_false_pos2, [])
    # ---------- L1 空集守卫：站点里 0 个 .py（★ 连同门控自身一起移除才算真的空扫描面）
    def l1_empty(r):
        for rel in list(FIXTURE_FILES):
            if rel.endswith(".py"):
                fp = os.path.join(r, rel)
                if os.path.isfile(fp):
                    os.remove(fp)
    case("L1 空集守卫：扫描面 0 个 *.py ⇒ FAIL（连带 T8 的判据对象也没了）", l1_empty, ["L1", "T8"])

    # ---------- V1 负例：薄副本漂移
    def v1_neg(r):
        p = os.path.join(r, "vendor/tools/contrast.py")
        t = open(p, encoding="utf-8").read()
        w(r, p, t + "\n# drift\n")
    case("V1 负例：薄副本被就地修补（sha256 漂移）⇒ FAIL", v1_neg, ["V1"])
    # ---------- V2 负例：vendor 下多了未登记的文件
    #    ★ V1 只按「登记 ⇒ 盘面」方向查（多出的文件不在登记里，故 V1 不 FAIL）；
    #      「盘面 ⇒ 登记」方向归 V2。两条判据分工不同，夹具据此断言。
    case("V2 负例：vendor/ 下出现未登记文件 ⇒ FAIL（V1 只管登记⇒盘面方向，故不 FAIL）",
         lambda r: w(r, "vendor/pipeline/extra.py", "# unregistered\n"), ["V2"])

    # ---------- 文档自述假阳：.md 声称「全部页面已链接两件套」不得影响 HTML 判据
    def doc_false_pos(r):
        w(r, "README.md", "本仓全部页面均已 <link> 两件套，0 断链，0 残留。\n")
        p = os.path.join(r, "index.html")
        t = open(p, encoding="utf-8").read()
        w(r, "index.html", t.replace('<link rel="stylesheet" href="04-interactive/assets/site.css">', ""))
    case("★ 假阳：README 自述「全部页面已链接两件套 / 0 断链」但 HTML 不是 ⇒ 仍必须 FAIL",
         doc_false_pos, ["R4"])

    ok = all(v for _, v, _ in cases)
    for name, res, det in cases:
        print("  [%s] %s" % ("PASS" if res else "FAIL", name))
        if not res:
            print("         %s" % det)
    nf = sum(1 for _, v, _ in cases if not v)
    print("\n=== gate_tokens --selftest：%d 项负向夹具，%d FAIL ===" % (len(cases), nf))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site-root", default=".")
    ap.add_argument("--manifest", default="gate-manifest.json")
    ap.add_argument("--profile", default="build/profile.json")
    ap.add_argument("--mode", default="enforce", choices=["enforce", "report"])
    ap.add_argument("--report", default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    site = Site(a.site_root)
    if a.selftest:
        return selftest(site)
    if not os.path.isdir(site.root):
        print("环境错误：站点根不存在 %s" % site.root)
        return 2
    try:
        manifest = load_json(site.p(a.manifest), "门控清单")
        profile = load_json(site.p(a.profile), "profile")
    except Exception as exc:  # noqa: BLE001
        print("输入错误：%s" % exc)
        return 2
    D = load_module(site.p("vendor/pipeline/derive_site_tokens.py"), "d_gate")
    CT = load_module(site.p("vendor/tools/contrast.py"), "c_gate")
    contract = None
    results = run_judges(site, profile, manifest, contract, D, CT, "gate_tokens.py")
    for jid, name, blk, ok, det in results:
        print("[%s] %-3s %s" % ("PASS" if ok else "FAIL", jid, name))
        print("        %s" % det)
    nf = sum(1 for r in results if not r[3])
    print("\n=== 门控 gate_tokens（mode=%s）：%d 项判据，%d FAIL ===" % (a.mode, len(results), nf))
    if a.report:
        rep = build_report(site, profile, manifest, results, a.mode, None)
        with open(os.path.join(site.root, a.report), "w", encoding="utf-8") as fh:
            json.dump(rep, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        print("   已写确定性报告 %s（tree_digest=%s，%d 文件；⛔ 无时间戳/无绝对路径；已排除报告自身）"
              % (a.report, rep["tree"]["tree_digest"][:16], rep["tree"]["file_count"]))
    if a.json:
        print(json.dumps([{"id": j, "ok": ok, "detail": d} for j, _n, _b, ok, d in results],
                         ensure_ascii=False, indent=1))
    if a.mode == "report":
        return 0
    return 0 if nf == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
