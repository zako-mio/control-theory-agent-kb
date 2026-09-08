# -*- coding: utf-8 -*-
"""check_premium_consistency.py — 精装房分值五处一致性核对

核对 14 产品的综合分是否在以下 5 处完全一致（与 premium_scores.py 的 final() 对齐）：
  1) 07-checkpoint/premium-evidence.md          （精装度列）
  2) 04-interactive/premium-map.html            （pm-score）
  3) 04-interactive/premium-cyto.html           （产品节点 label 中的分值）
  4) 04-interactive/premium-{slug}.html ×14     （prem-score 评分卡）
  5) 03-cases/premium-{slug}.md ×14             （头部 精装度 + 综合评分）

退出码: 0=全部一致, 1=存在不一致。
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "09-src-data")
sys.path.insert(0, SRC)
import premium_scores as ps  # noqa: E402

# evidence 表中的 bold 名称
EVIDENCE_IDENT = {
    "openhands": "OpenHands", "devin": "Devin", "workbuddy": "WorkBuddy(腾讯)",
    "dify": "Dify", "openclaude": "OpenClaude", "cursor": "Cursor",
    "coze": "Coze扣子(字节)", "windsurf": "Windsurf/Devin Desktop",
    "gptresearcher": "gpt-researcher", "codewhale": "CodeWhale",
    "copilot": "GitHub Copilot", "qcode": "QCode(qcode.cc)",
    "crewai": "CrewAI", "ccrouter": "Claude Code Router",
}

TOL = 0.051


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def num(s):
    try:
        return float(s)
    except Exception:
        return None


def check_evidence():
    text = read(os.path.join(BASE, "07-checkpoint", "premium-evidence.md"))
    out = {}
    for slug, ident in EVIDENCE_IDENT.items():
        m = re.search(r"\|\s*\*\*%s\*\*\s*\|[^|]*\|\s*([0-9.]+)\s*\|"
                      % re.escape(ident), text)
        out[slug] = num(m.group(1)) if m else None
    return out


def check_map():
    text = read(os.path.join(BASE, "04-interactive", "premium-map.html"))
    out = {}
    for m in re.finditer(
            r'pm-name" href="premium-([a-z]+)\.html">.*?pm-score"[^>]*>([0-9.]+)<',
            text, re.S):
        out[m.group(1)] = num(m.group(2))
    return out


def check_cyto():
    text = read(os.path.join(BASE, "04-interactive", "premium-cyto.html"))
    m = re.search(r"const ELEMENTS = (\[.*?\]);", text, re.S)
    out = {}
    if not m:
        return out
    for el in json.loads(m.group(1)):
        d = el.get("data", {})
        if d.get("kind") == "product":
            label = d.get("label", "")
            parts = label.rsplit("\n", 1)
            if len(parts) == 2:
                out[d.get("slug")] = num(parts[1])
    return out


def check_case_html():
    out = {}
    for p in ps.PRODUCTS:
        path = os.path.join(BASE, "04-interactive", "premium-%s.html" % p["slug"])
        if not os.path.isfile(path):
            out[p["slug"]] = None
            continue
        m = re.search(r'prem-score"[^>]*>\s*([0-9.]+)/5', read(path))
        out[p["slug"]] = num(m.group(1)) if m else None
    return out


def check_case_md():
    heads, scores = {}, {}
    for p in ps.PRODUCTS:
        path = os.path.join(BASE, "03-cases", "premium-%s.md" % p["slug"])
        if not os.path.isfile(path):
            heads[p["slug"]] = scores[p["slug"]] = None
            continue
        text = read(path)
        mh = re.search(r"> 精装度：([0-9.]+)/5", text)
        ms = re.search(r"\*\*综合评分\*\*：([0-9.]+)/5", text)
        heads[p["slug"]] = num(mh.group(1)) if mh else None
        scores[p["slug"]] = num(ms.group(1)) if ms else None
    return heads, scores


def main():
    ev = check_evidence()
    mp = check_map()
    cy = check_cyto()
    ch = check_case_html()
    mh, ms = check_case_md()

    header = ("slug            model | evid  map   cyto  html  md-h  md-s | status")
    print(header)
    print("-" * len(header))
    fails = []
    for p in ps.PRODUCTS:
        s = p["slug"]
        model = ps.final(s)
        vals = {"evid": ev.get(s), "map": mp.get(s), "cyto": cy.get(s),
                "html": ch.get(s), "md-h": mh.get(s), "md-s": ms.get(s)}
        bad = [k for k, v in vals.items()
               if v is None or abs(v - model) > TOL]
        status = "OK" if not bad else "MISMATCH:" + ",".join(bad)
        if bad:
            fails.append((s, model, vals, bad))
        print("%-14s %5s | %5s %5s %5s %5s %5s %5s | %s" % (
            s, ps.fmt(model),
            *(ps.fmt(v) if v is not None else "None" for v in
              [vals["evid"], vals["map"], vals["cyto"],
               vals["html"], vals["md-h"], vals["md-s"]]),
            status))
    print("-" * len(header))
    if fails:
        print("一致性核对: FAIL（%d 个产品不一致）" % len(fails))
        for s, model, vals, bad in fails:
            print("  ❌ %s model=%s 异常字段=%s" % (s, ps.fmt(model), bad))
        return 1
    print("一致性核对: PASS（14 产品 × 6 处口径全部一致）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
