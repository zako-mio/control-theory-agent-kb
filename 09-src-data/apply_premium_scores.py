# -*- coding: utf-8 -*-
"""apply_premium_scores.py — 把 premium_scores.py 的综合分同步写入画像 MD 与 evidence

用法: python3 apply_premium_scores.py
只改「结构化分值位」：
  1) 画像 MD 头部 `> 精装度：X/5`
  2) 画像 MD `**综合评分**：X/5 — ...`
  3) premium-evidence.md 各产品行的「精装度」列
不改证据文字/机制描述（那部分是人工核验内容）。
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
sys.path.insert(0, BASE)
import premium_scores as ps  # noqa: E402

# 产品 slug → evidence.md 行内标识（bold 名称）
EVIDENCE_IDENT = {
    "openhands": "OpenHands",
    "devin": "Devin",
    "workbuddy": "WorkBuddy(腾讯)",
    "dify": "Dify",
    "openclaude": "OpenClaude",
    "cursor": "Cursor",
    "coze": "Coze扣子(字节)",
    "windsurf": "Windsurf/Devin Desktop",
    "gptresearcher": "gpt-researcher",
    "codewhale": "CodeWhale",
    "copilot": "GitHub Copilot",
    "qcode": "QCode(qcode.cc)",
    "crewai": "CrewAI",
    "ccrouter": "Claude Code Router",
}


def fmt(slug):
    return ps.fmt(ps.final(slug))


def patch_case_md(slug):
    path = os.path.join(ROOT, "03-cases", "premium-%s.md" % slug)
    if not os.path.isfile(path):
        return False, "missing"
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    orig = text
    new = fmt(slug)
    # 头部：> 精装度：X/5　｜
    text = re.sub(r"(> 精装度：)[0-9.\-]+/5", r"\g<1>%s/5" % new, text, count=1)
    # 综合评分：**综合评分**：X/5 —
    text = re.sub(r"(\*\*综合评分\*\*：)[0-9.\-]+/5", r"\g<1>%s/5" % new, text, count=1)
    if text != orig:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return True, new
    return False, new


# 散文/结论中残留的旧分值引用（(文件, 旧串, 新串, 次数) 次数=0 表示全部）
PROSE_FIXES = [
    ("premium-ccrouter.md", "精装度达 3，", "精装度达 2.1，", 1),
    ("premium-codewhale.md", "精装度 4 ", "精装度 3.5 ", 0),
    ("premium-coze.md", "精装度 4.5、一手", "精装度 4.2、一手", 1),
    ("premium-coze.md", "精装度 4.5 的", "精装度 4.2 的", 0),
    ("premium-coze.md", "4.5 分精装房", "4.2 分精装房", 1),
    ("premium-coze.md", "与 5 分产品（Dify/OpenHands/Devin/WorkBuddy）的差距",
     "与更高分产品（Devin 5.0 / WorkBuddy 4.6）的差距", 1),
    ("premium-dify.md", "精装度 5 ", "精装度 4.3 ", 0),
    ("premium-dify.md", "一手满分精装（源码级）", "一手高精装（4.3，源码级）", 1),
    ("premium-dify.md", "一手满分精装房，且是罕见的", "一手高精装房（4.3），且是罕见的", 1),
    ("premium-gptresearcher.md", "精装度 4、源码级", "精装度 3.7、源码级", 0),
    ("premium-gptresearcher.md", "精装度停在 4 而非 5", "精装度停在 3.7 而非 5", 1),
    ("premium-gptresearcher.md", "精装度 4 ", "精装度 3.7 ", 0),
    ("premium-openclaude.md", "精装度 5 ", "精装度 3.8 ", 0),
    ("premium-openclaude.md", "一手满分精装房", "一手精装房（3.8）", 1),
    ("premium-openhands.md", "精装度 5 ", "精装度 4.2 ", 0),
    ("premium-openhands.md", "一手满分精装房", "一手高精装房（4.2）", 1),
    ("premium-qcode.md", "精装度达 3.5", "精装度达 1.4", 1),
    ("premium-copilot.md", "**3.5-4 分、一手", "**4.1 分、一手", 1),
    ("premium-copilot.md", "弱于 5 分产品（Devin/WorkBuddy/OpenHands）",
     "弱于更高分产品（Devin 5.0 / WorkBuddy 4.6）", 1),
    ("premium-cursor.md", "**4.5 分、一手", "**4.4 分、一手", 1),
    ("premium-cursor.md", "与 5 分产品（Devin/WorkBuddy/OpenHands/Dify）的差距",
     "与更高分产品（Devin 5.0 / WorkBuddy 4.6）的差距", 1),
    ("premium-devin.md", "区别于其他 5 分产品在于",
     "区别于其他高分产品（如 WorkBuddy 4.6）在于", 1),
    ("premium-workbuddy.md", "国内满分第一方成品闭环",
     "国内高分第一方成品闭环（4.6）", 1),
    ("premium-workbuddy.md",
     "**5 分、一手、文档级证实、声称相符（但需保留置信度边界）**——WorkBuddy 与 Devin/OpenHands/Dify 同处「真·开箱即用成品」档",
     "**4.6 分、一手、文档级证实、声称相符（但需保留置信度边界）**——WorkBuddy 与 Devin（5.0）同处「真·开箱即用」档（≥4.5），OpenHands/Dify 等紧随其后（成品化受限档）", 1),
    ("premium-workbuddy.md", "需明确：5 分是「预装度」意义",
     "需明确：4.6 分是「预装度」意义", 1),
    ("premium-devin.md", "Devin 与 OpenHands/WorkBuddy/Dify 同处「真·开箱即用成品」档",
     "Devin 与 WorkBuddy 同处「真·开箱即用」档（≥4.5），OpenHands/Dify 等紧随其后（成品化受限档）", 1),
]

# premium-evidence.md 散文中的分层引用
EVIDENCE_PROSE_FIXES = [
    ("二手精装中：CCR(3), QCode(3.5)（封装底座中转，预装度中等但非自研）",
     "二手精装低：CCR(2.1), QCode(1.4)（封装底座中转，无自研 Agent 底座）"),
    ("一手精装中：CrewAI(3)/gpt-researcher(4)（自研但预装受限）",
     "一手精装中：CrewAI(3.0)/gpt-researcher(3.7)（自研但预装受限）"),
    ("3. **精装度分层**：真·开箱即用成品（OpenHands/Devin/WorkBuddy/Dify/OpenClaude 5分）> 成品化受限（Cursor/Windsurf/Coze 4-4.5）> 需配置框架（CrewAI/CCR/QCode 3-3.5）。",
     "3. **精装度分层（v2.0 加权模型）**：真·开箱即用（≥4.5）Devin(5.0)/WorkBuddy(4.6) > 成品化受限（3.5-4.5）Cursor(4.4)/Dify(4.3)/OpenHands(4.2)/Coze(4.2)/Copilot(4.1)/Windsurf(4.0)/OpenClaude(3.8)/GPT-Researcher(3.7)/CodeWhale(3.5) > 需装修/中转（<3.5）CrewAI(3.0)/CC-Router(2.1)/QCode(1.4)。详见 `premium-score-recompute.md`。"),
]


def patch_prose():
    changed = 0
    for fname, old, new, cnt in PROSE_FIXES:
        path = os.path.join(ROOT, "03-cases", fname)
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        if old not in text:
            continue
        text2 = text.replace(old, new, cnt) if cnt else text.replace(old, new)
        if text2 != text:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text2)
            changed += 1
    return changed


def patch_evidence():
    path = os.path.join(ROOT, "07-checkpoint", "premium-evidence.md")
    if not os.path.isfile(path):
        return False
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    orig = text
    for slug, ident in EVIDENCE_IDENT.items():
        pat = re.compile(r"(\|\s*\*\*%s\*\*\s*\|[^|]*\|\s*)[0-9.]+(\s*\|)"
                         % re.escape(ident))
        text = pat.sub(lambda m: m.group(1) + fmt(slug) + m.group(2), text)
    for old, new in EVIDENCE_PROSE_FIXES:
        text = text.replace(old, new)
    if text != orig:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return True
    return False


def main():
    changed = 0
    for p in ps.PRODUCTS:
        ok, val = patch_case_md(p["slug"])
        changed += 1 if ok else 0
        print("画像 %-14s -> %s/5  %s" % (p["slug"], val,
                                         "updated" if ok else "unchanged/missing"))
    ev = patch_evidence()
    print("evidence.md: %s" % ("updated" if ev else "unchanged"))
    prose = patch_prose()
    print("散文分值修正: %d 处" % prose)
    print("完成: 画像改动 %d 篇" % changed)


if __name__ == "__main__":
    main()
