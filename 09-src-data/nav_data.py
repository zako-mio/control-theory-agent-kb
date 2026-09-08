# -*- coding: utf-8 -*-
"""共享导航数据 + 渲染 - 全站统一完整目录(00门户入口 + 01总览~36精装CrewAI，含6框架+14精装房)"""
import html

# 完整目录: (标签, 文件名, 分组)
NAV = [
    ("门户入口", "portal", "portal"),          # 00 门户(链接 ../index.html 或 index.html)
    ("总览", "index", "overview"),            # 01 文档总览(04-interactive/index.html)
    ("交互DAG", "index_cyto", "overview"),    # 02
    ("框架", "framework", "core"),            # 03
    ("理论:闭环反馈", "theory-closed-loop", "theory"),
    ("理论:状态估计", "theory-state-est", "theory"),
    ("理论:PID", "theory-pid", "theory"),
    ("理论:鲁棒控制", "theory-robust", "theory"),
    ("理论:分层控制", "theory-hierarchical", "theory"),
    ("案例:opencode", "case-opencode", "cases"),
    ("案例:opencode-custom", "case-opencode-custom", "cases"),
    ("对照:官方vs自改造", "compare-opencode", "cases"),
    ("案例:dsh", "case-dsh", "cases"),
    ("案例:PRIME", "case-prime", "cases"),
    ("案例:hermes", "case-hermes", "cases"),
    ("案例:claude-code", "case-claude-code", "cases"),
    ("案例:codex", "case-codex", "cases"),
    ("实验:opencode", "exp-opencode", "exp"),
    ("实验:opencode-custom", "exp-opencode-custom", "exp"),
    ("实验:dsh", "exp-dsh", "exp"),
    ("实验:PRIME", "exp-prime", "exp"),
    ("实验:hermes", "exp-hermes", "exp"),
    ("实验:claude-code", "exp-claude-code", "exp"),
    ("实验:codex", "exp-codex", "exp"),
    ("精装房全景", "premium-map", "premium"),
    ("精装房DAG", "premium-cyto", "premium"),
    ("精装:Cursor", "premium-cursor", "premium"),
    ("精装:Devin", "premium-devin", "premium"),
    ("精装:WorkBuddy", "premium-workbuddy", "premium"),
    ("精装:Windsurf", "premium-windsurf", "premium"),
    ("精装:Copilot", "premium-copilot", "premium"),
    ("精装:Dify", "premium-dify", "premium"),
    ("精装:OpenHands", "premium-openhands", "premium"),
    ("精装:Coze", "premium-coze", "premium"),
    ("精装:OpenClaude", "premium-openclaude", "premium"),
    ("精装:CodeWhale", "premium-codewhale", "premium"),
    ("精装:GPT-Researcher", "premium-gptresearcher", "premium"),
    ("精装:QCode", "premium-qcode", "premium"),
    ("精装:CC-Router", "premium-ccrouter", "premium"),
    ("精装:CrewAI", "premium-crewai", "premium"),
]

GROUP_LABEL = {
    'portal':'入门','overview':'概览','core':'核心','theory':'理论',
    'cases':'案例','exp':'实验','premium':'精装房全景',
}

def href_for(fname, is_root):
    """返回链接。is_root=True(门户页) → 文档页加 04-interactive/ 前缀; 门户入口链接根index"""
    if fname == 'portal':
        return "index.html" if is_root else "../index.html"
    prefix = "04-interactive/" if is_root else ""
    return prefix + fname + ".html"

def sidebar_nav(active_file, is_root=False):
    """生成完整目录侧边栏导航。active_file: 'portal'/'index'/'framework'/... 高亮。"""
    items = []
    current_grp = None
    for label, fname, grp in NAV:
        if grp != current_grp:
            items.append(f'<div class="grp">{GROUP_LABEL.get(grp,grp)}</div>')
            current_grp = grp
        item_idx = NAV.index((label,fname,grp))
        mag = f"{item_idx:02d}" if item_idx>0 else "00"
        cls = "active" if fname == active_file else ""
        items.append(f'<a class="{cls}" href="{href_for(fname,is_root)}"><span class="mag">{mag}</span>{label}</a>')
    return "".join(items)

def sidebar_brand():
    return f"""
<div class="sidebar-brand">
  <div class="mark"><span class="dot"></span><h1>控制理论 ⊗ Agent</h1></div>
  <p>五大核心环 · 6 框架 + 14 精装房 + 自改造 opencode · 6 实验组</p>
</div>"""
