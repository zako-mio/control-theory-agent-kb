# -*- coding: utf-8 -*-
"""生成高可读性 HTML 文档集群 - 控制理论⊗Agent知识库
统一风格: 导航骨架 + 侧边目录 + 卡片式章节 + 证据区块渲染
"""
import json, os, re, sys, html
sys.stdout.reconfigure(encoding='utf-8')
import premium_scores as ps  # 精装房评分模型单一数据源

BASE = "/home/zako-mio/opencode/archive/Mission-file/2026-09/0907-控制理论Agent设计知识库"
OUT = os.path.join(BASE, "04-interactive")

# ---- 全局 CSS (高可读) ----
CSS = """
:root{--bg:#f8fafc;--panel:#fff;--ink:#1e293b;--muted:#64748b;--accent:#0ea5e9;--border:#e2e8f0;
--gold:#b45309;--green:#047857;--red:#b91c1c;--blue:#1d4ed8;}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'PingFang SC','Microsoft YaHei',sans-serif;
background:var(--bg);color:var(--ink);line-height:1.7;font-size:15px}
.wrap{display:flex;min-height:100vh}
aside{width:250px;background:#0f172a;color:#cbd5e1;position:sticky;top:0;height:100vh;overflow-y:auto;flex-shrink:0}
aside .brand{padding:18px 16px;border-bottom:1px solid #1e293b}
aside .brand h1{font-size:15px;color:#fff}
aside .brand p{font-size:11px;color:#64748b;margin-top:4px}
aside nav{padding:10px}
aside nav .grp{font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:.5px;margin:14px 0 6px}
aside nav a{display:block;padding:6px 10px;border-radius:5px;color:#94a3b8;font-size:13px;text-decoration:none;margin-bottom:2px}
aside nav a:hover{background:rgba(255,255,255,.06);color:#fff}
aside nav a.active{background:rgba(14,165,233,.18);color:#7dd3fc;font-weight:600}
main{flex:1;padding:24px 32px 60px;max-width:900px;margin:0 auto}
header.topic{border-bottom:2px solid var(--accent);padding-bottom:12px;margin-bottom:20px}
header.topic h1{font-size:24px}
header.topic .crumb{font-size:12px;color:var(--muted);margin-top:4px}
.breadcrumb{font-size:12px;color:var(--muted);margin-bottom:16px}
.breadcrumb a{color:var(--accent);text-decoration:none}
h2{font-size:19px;margin:28px 0 12px;color:var(--blue);border-bottom:1px solid var(--border);padding-bottom:6px}
h3{font-size:16px;margin:20px 0 8px;color:var(--gold)}
p{margin:8px 0}
.card{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:16px 18px;margin:14px 0;box-shadow:0 1px 2px rgba(0,0,0,.03)}
.card.kt{border-left:3px solid var(--accent)}
.card.kt h3{color:var(--blue);margin-top:0}
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:14px}
th,td{border:1px solid var(--border);padding:8px 10px;text-align:left;vertical-align:top}
th{background:#f1f5f9;font-weight:600}
code{background:#f1f5f9;padding:1px 5px;border-radius:3px;font-family:monospace;font-size:.9em}
blockquote{border-left:3px solid var(--accent);background:#eff6ff;padding:10px 14px;border-radius:0 6px 6px 0;margin:12px 0;color:#334155}
.evidence{background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:14px;margin:14px 0}
.evidence h4{color:var(--green);margin-bottom:8px;font-size:14px}
.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600}
.badge.s1{background:#dcfce7;color:var(--green)}
.badge.s2{background:#fef3c7;color:var(--gold)}
.badge.s4{background:#e0e7ff;color:var(--blue)}
.strong{color:var(--green);font-weight:600}.weak{color:var(--red);font-weight:600}
.chip{display:inline-block;background:#eef2ff;color:#4338ca;padding:2px 8px;border-radius:10px;font-size:11px;font-family:monospace;margin:2px}
.pager{display:flex;justify-content:space-between;margin-top:40px;border-top:1px solid var(--border);padding-top:16px}
.pager a{color:var(--accent);text-decoration:none;font-size:14px}
.pager a:hover{text-decoration:underline}
.hero{background:linear-gradient(135deg,#0f172a,#1e3a8a);color:#fff;border-radius:12px;padding:28px;margin-bottom:24px}
.hero h1{font-size:26px;margin-bottom:8px}
.hero p{color:#cbd5e1}
.note{background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;padding:12px;margin:14px 0;font-size:13px;color:#78350f}
footer{margin-top:40px;color:var(--muted);font-size:12px;border-top:1px solid var(--border);padding-top:12px;text-align:center}
"""

# ---- 页面列表(用于侧边导航) ----
PAGES = [
    ("总览", "index", "overview"),
    ("交互DAG", "index_cyto", "overview"),
    ("框架", "framework", "core"),
    ("理论:闭环反馈", "theory-closed-loop", "theory"),
    ("理论:状态估计", "theory-state-est", "theory"),
    ("理论:PID", "theory-pid", "theory"),
    ("理论:鲁棒控制", "theory-robust", "theory"),
    ("理论:分层控制", "theory-hierarchical", "theory"),
    ("案例:opencode", "case-opencode", "cases"),
    ("案例:dsh", "case-dsh", "cases"),
    ("案例:PRIME", "case-prime", "cases"),
    ("案例:hermes", "case-hermes", "cases"),
    ("案例:claude-code", "case-claude-code", "cases"),
    ("案例:codex", "case-codex", "cases"),
    ("实验:opencode", "exp-opencode", "exp"),
    ("实验:dsh", "exp-dsh", "exp"),
    ("实验:PRIME", "exp-prime", "exp"),
    ("实验:hermes", "exp-hermes", "exp"),
    ("实验:claude-code", "exp-claude-code", "exp"),
    ("实验:codex", "exp-codex", "exp"),
]

def esc(s): return s

def inline(text):
    """escape 后处理 inline 标记: **bold**, `code`"""
    t = html.escape(text)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    return t

def md_to_html_simple(md):
    """增强版 MD -> HTML (标题/列表/表格/引用/加粗/代码)"""
    lines = md.split("\n")
    out=[]; in_table=False; code=False
    table_rows=[]
    for line in lines:
        # 代码块(支持缩进)
        if line.lstrip().startswith("```"):
            code = not code
            out.append("<pre><code class='pre'>"+ ("" if code else "</code></pre>"))
            continue
        if code:
            out.append(html.escape(line)); continue
        # 表格
        if line.strip().startswith("|") and line.strip().endswith("|") and line.count("|")>=2:
            if not in_table: in_table=True; table_rows=[]
            # 表头分隔行
            if re.match(r'^\|[\s:\-|]+\|$', line): continue
            cells=[inline(c.strip()) for c in line.strip().strip("|").split("|")]
            table_rows.append(cells)
            continue
        else:
            if in_table and table_rows:
                # 渲染表
                if table_rows:
                    thead = "<thead><tr>"+"".join("<th>"+c+"</th>" for c in table_rows[0])+"</tr></thead>"
                    tbody = "".join("<tr>"+"".join("<td>"+c+"</td>" for c in r)+"</tr>" for r in table_rows[1:])
                    out.append("<table>"+thead+tbody+"</table>")
                table_rows=[]; in_table=False
        # 标题
        m=re.match(r'^(#+)\s+(.*)',line)
        if m and not in_table:
            lvl=len(m.group(1)); txt=m.group(2)
            out.append(f"<h{'123'[lvl-1] if lvl<=3 else '3'}>{inline(txt)}</h>")
            continue
        if line.startswith("- "):
            out.append("<li>"+inline(line.lstrip('- '))+"</li>"); continue
        if line.startswith("### "):
            continue
        if not line.strip():
            continue
        # 引用
        if line.startswith("> "):
            out.append("<blockquote>"+inline(line.lstrip('> '))+"</blockquote>"); continue
        out.append("<p>"+inline(line)+"</p>")
    if in_table and table_rows:
        thead = "<thead><tr>"+"".join("<th>"+c+"</th>" for c in table_rows[0])+"</tr></thead>"
        tbody = "".join("<tr>"+"".join("<td>"+c+"</td>" for c in r)+"</tr>" for r in table_rows[1:])
        out.append("<table>"+thead+tbody+"</table>")
    return "\n".join(out)

def sidebar(active_file):
    import nav_data as nd
    return f"""
<aside class="sidebar">
 {nd.sidebar_brand()}
 <nav class="sidebar-nav">{nd.sidebar_nav(active_file, is_root=False)}
 </nav>
</aside>"""

def page(title, crumb, body, active_file, prev=None, nxt=None):
    pp = [x for x in PAGES if x[1]==prev] if prev else []
    p = f'<a href="{prev}.html">← {pp[0][0] if pp else ""}</a>' if prev else '<span></span>'
    nn = [x for x in PAGES if x[1]==nxt] if nxt else []
    n = f'<a class="next" href="{nxt}.html">{nn[0][0] if nn else ""}</a>' if nxt else '<span></span>'
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — 控制理论⊗Agent知识库</title>
<link rel="stylesheet" href="assets/design-tokens.css"></head>
<body><div class="shell">{sidebar(active_file)}
<div class="main">
<div class="main-topbar"><div class="crumb"><b>{title}</b> · 控制理论 ⊗ Agent</div></div>
<div class="main-content">
<header class="topic"><div class="crumb">{crumb}</div><h1>{title}</h1></header>
{body}
<div class="pager">{p}{n}</div>
<footer class="footer">
<span>控制理论 ⊗ Agent 设计知识库 · v1.1 精装房全景版（6 框架 + 14 精装房）</span>
<span class="fbrand">data: 09-src-data · contract: 00-contract</span>
</footer>
</div></div></div></body></html>"""

def kt_card_block(md_text):
    """从理论 md 提取 KT 知识点卡片"""
    blocks = re.split(r'\n(?=## KT-)', md_text)
    cards=[]
    for b in blocks[1:]:
        m=re.match(r'## (KT-ctrl-\d{3}) ?(.*)',b)
        if not m: continue
        kt, name = m.group(1), m.group(2).strip()
        def_=re.search(r'- \*\*定义\*\*：(.*)',b)
        math=re.search(r'- \*\*数学\*\*：(.*)',b)
        agent=re.search(r'- \*\*Agent 映射\*\*：(.*)',b)
        src=re.findall(r'\| (SRC[\w-]+) \| (S\d) \| ([^|]+) \|',b)
        cards.append({"kt":kt,"name":name,"def":def_.group(1).strip() if def_ else "",
                      "math":math.group(1).strip() if math else "",
                      "agent":agent.group(1).strip() if agent else "",
                      "src":src})
    return cards

def render_kt_cards(cards):
    html_cards=[]
    for c in cards:
        src_html="".join(f"<tr><td class='mono'>{html.escape(s[0])}</td><td><span class='badge {'s1' if s[1]=='S1' else ('s2' if s[1]=='S2' else 's4')}'>{s[1]}</span></td><td>{html.escape(s[2])}</td></tr>" for s in c["src"])
        mapping = f'<div class="mapping">Agent 映射：{c["agent"]}</div>' if c["agent"] else ''
        html_cards.append(f"""
<div class="kt-card">
<h3>{html.escape(c['name'])} <span class="chip">{c['kt']}</span></h3>
<p><strong>定义</strong>{c['def']}</p>
{'<p><strong>数学</strong>'+c['math']+'</p>' if c['math'] else ''}
{mapping}
{'<div class="evidence"><h4>📚 证据来源</h4><table><thead><tr><th>SRC</th><th>级别</th><th>信源</th></tr></thead><tbody>'+src_html+'</tbody></table></div>' if src_html else ''}
</div>""")
    return "".join(html_cards)

print("生成器已加载: PAGES=%d" % len(PAGES))

# ================= 生成各页面 =================
import io

def read(f): return open(os.path.join(BASE,f),encoding="utf-8").read()

def gen_overview():
    body = """
<!-- 签名元素: 五环控制回路信号图 -->
<div class="signal">
  <div class="signal-head">
    <span class="label">System Loop · 控制回路</span>
    <span class="tag">v1.1 · 6 framework + 14 premium</span>
  </div>
  <svg viewBox="0 0 900 200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="五环控制回路">
    <defs>
      <marker id="arr2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M0 0 L10 5 L0 10 z" fill="#7E8CA5"/>
      </marker>
    </defs>
    <path d="M60 170 L210 170 L330 170 L420 170" stroke="#3B4B66" stroke-width="1.5" fill="none" marker-end="url(#arr2)"/>
    <path d="M420 170 L420 90 L540 90" stroke="#3B4B66" stroke-width="1.5" fill="none" marker-end="url(#arr2)"/>
    <path d="M540 90 L780 90" stroke="#3B4B66" stroke-width="1.5" fill="none" marker-end="url(#arr2)"/>
    <path d="M780 90 L780 170 L660 170" stroke="#3B4B66" stroke-width="1.5" fill="none" marker-end="url(#arr2)"/>
    <path d="M660 170 L420 170" stroke="#3B4B66" stroke-width="1.5" fill="none" marker-end="url(#arr2)"/>
    <path d="M240 170 L240 90" stroke="#C77700" stroke-width="1.5" stroke-dasharray="4 4" fill="none" marker-end="url(#arr2)"/>
    <g font-family="var(--font-mono)" font-size="12" fill="#E6EAF2">
      <rect x="210" y="150" width="120" height="40" rx="7" fill="#1E5AA8"/><text x="270" y="175" text-anchor="middle">P 规划/分层</text>
      <rect x="420" y="70" width="120" height="40" rx="7" fill="#5B4B9B"/><text x="480" y="95" text-anchor="middle">T 工具/执行</text>
      <rect x="660" y="150" width="120" height="40" rx="7" fill="#B23A2F"/><text x="720" y="175" text-anchor="middle">E 评估/传感</text>
      <rect x="420" y="150" width="120" height="40" rx="7" fill="#1F7A52"/><text x="480" y="175" text-anchor="middle">M 记忆/状态</text>
      <rect x="540" y="150" width="120" height="40" rx="7" fill="#C77700"/><text x="600" y="175" text-anchor="middle">R 反思/反馈</text>
      <text x="60" y="176" fill="#7E8CA5" font-size="11">目标 r</text>
    </g>
  </svg>
  <div class="signal-legend">
    <span><i style="background:#1E5AA8"></i>P 规划</span><span><i style="background:#5B4B9B"></i>T 执行</span>
    <span><i style="background:#B23A2F"></i>E 评估</span><span><i style="background:#1F7A52"></i>M 记忆</span>
    <span><i style="background:#C77700"></i>R 反思</span>
  </div>
</div>

<span class="kicker">Agent Systems · 控制理论视角</span>
<h1 class="display">把 Agent 当成一架被控的无人机。</h1>
<p class="lead">不是会聊天的搜索引擎——它是装了<b>传感器</b>、<b>执行器</b>、<b>逻辑决断器</b>的闭环系统。控制理论是解决 Agent 工程问题的工具库。</p>

<h2><span class="idx">01</span>核心洞察 · 6 框架对比</h2>
<div class="grid cols-2">
  <div class="card"><span class="num">T RING</span><h3>T 环是共同的「最强环」</h3><p>看门狗/限幅/沙箱是 Agent 工程最成熟环节，<strong class="state-green">无一例外</strong>每产品都做到硬约束。</p></div>
  <div class="card"><span class="num">E RING</span><h3>E 环分化两派</h3><p><strong>hermes</strong>（独立 Critic）、<strong>codex</strong>（双评审器）E 环变强；opencode/dsh/PRIME/claude-code 仍弱。</p></div>
</div>
<table>
  <thead><tr><th>产品</th><th>最弱环</th><th>独立 Critic</th><th>整体范式</th></tr></thead>
  <tbody>
    <tr><td class="mono">opencode</td><td><span class="badge weak"><strong>E</strong>评估</span></td><td>—</td><td>前馈-执行 + 局部反馈</td></tr>
    <tr><td class="mono">deepseek-harness</td><td><span class="badge weak"><strong>E</strong>评估</span></td><td>—</td><td>MPC 滚动 + 强约束执行</td></tr>
    <tr><td class="mono">PRIME</td><td><span class="badge weak"><strong>E</strong>评估</span></td><td>gates 空</td><td>自适应/自整定</td></tr>
    <tr><td class="mono">hermes</td><td><span class="badge neutral"><strong>P</strong>规划</span></td><td><span class="badge strong"><strong>✅</strong>有</span></td><td>鲁棒控制 + 多传感器</td></tr>
    <tr><td class="mono">claude-code</td><td><span class="badge weak"><strong>E</strong>评估</span></td><td><span class="badge neutral"><strong>外挂</strong>贴片</span></td><td>外挂 Critic + 执行限幅</td></tr>
    <tr><td class="mono">codex</td><td><span class="badge neutral"><strong>P</strong>规划</span></td><td><span class="badge strong"><strong>✅</strong>双评审</span></td><td>重执行 + 硬安全阀</td></tr>
  </tbody>
</table>

<h2><span class="idx">02</span>精装房全景 · 声称 vs 实际（v1.1）</h2>
<div class="grid cols-2">
  <div class="card"><span class="num">PREMIUM</span><h3>14 款主流「精装房」Agent</h3><p>精装度 0-5 主轴 × 一手/二手标签 × 4 大类，用源码级/文档级实证鉴别真实精装程度。</p></div>
  <div class="card"><span class="num">EVIDENCE</span><h3>实证发现：声称 ≠ 实际</h3><p><strong class="state-green">二手被高估</strong>：CC-Router/QCode 实为封装中转；<strong class="state-green">一手被低估</strong>：CodeWhale/OpenClaude 实为自研底层。</p></div>
</div>
<div class="grid cols-2" style="margin-top:var(--space-3)">
  <a class="portal-card" href="premium-map.html" style="background:var(--panel);border:1px solid var(--line);border-radius:var(--r-md);padding:var(--space-4);text-decoration:none">
    <span class="num">PREMIUM MAP</span><h3 style="margin:0 0 6px">精装房全景地图</h3><p style="margin:0">精装度主轴 + 四大类 + 声称vs实际 + 框架对照</p>
  </a>
  <a class="portal-card" href="premium-cyto.html" style="background:var(--panel);border:1px solid var(--line);border-radius:var(--r-md);padding:var(--space-4);text-decoration:none">
    <span class="num">PREMIUM DAG</span><h3 style="margin:0 0 6px">精装房 DAG</h3><p style="margin:0">14 节点：精装度着色 + 一手/二手形状</p>
  </a>
</div>

<h2><span class="idx">03</span>五大核心环</h2>
<table>
  <thead><tr><th>环</th><th>控制理论对应</th><th>Agent 工程问题</th></tr></thead>
  <tbody>
    <tr><td><span class="ring-tag M">M</span> 记忆/状态</td><td>状态估计/卡尔曼滤波</td><td>长上下文取舍、工作记忆蒸馏、观测噪声过滤</td></tr>
    <tr><td><span class="ring-tag P">P</span> 规划/分层</td><td>分层控制/慢快双速</td><td>任务分解、里程碑设定、慢规划器+快执行器</td></tr>
    <tr><td><span class="ring-tag R">R</span> 反思/反馈</td><td>反馈闭环/误差收敛</td><td>自我反思、错误回馈、长期偏航补偿</td></tr>
    <tr><td><span class="ring-tag T">T</span> 工具/执行</td><td>执行器/容错/鲁棒</td><td>工具调用失败、冗余仲裁、看门狗限幅</td></tr>
    <tr><td><span class="ring-tag E">E</span> 评估/传感</td><td>传感器/验证器/信噪比</td><td>Critic 模块、验证器、反馈信号质量</td></tr>
  </tbody>
</table>

<div class="insight"><strong>闭环方向</strong>：E 决定反馈信号质量 → R 决定纠偏量 → P/T 决定轨迹 → M 决定"我以为我在哪"。任一环失效，闭环即破。</div>
<h2><span class="idx">04</span>进入</h2>
<div class="grid cols-2">
  <a class="portal-card" href="index_cyto.html" style="background:var(--panel);border:1px solid var(--line);border-radius:var(--r-md);padding:var(--space-4);text-decoration:none">
    <span class="num">INTERACT</span><h3 style="margin:0 0 6px">交互 DAG 总览</h3><p style="margin:0">五环 × 控制概念可点击下钻（cytoscape）</p>
  </a>
  <div class="card"><span class="num">SOURCE</span><h3>数据源</h3><p>09-src-data/five-ring-dag.json · 31 知识点 · 契约 00-contract</p></div>
</div>
"""
    return page("知识库总览","五大核心环控制回路",body,"index",None,"framework")

def gen_framework():
    md = read("02-framework/framework.md")
    # 使用专用渲染器(五环结构化章节)
    import render_framework as rf
    body = rf.render_framework(md, "")
    return page("五大核心环映射框架","框架 · 核心","<p class='breadcrumb'><a href='index.html'>总览</a> › 框架</p>"+body,"framework","index","theory-closed-loop")

THEORY_META=[
    ("theory-closed-loop","理论：闭环反馈与稳定性","01-closed-loop.md"),
    ("theory-state-est","理论：状态估计与记忆","02-state-est.md"),
    ("theory-pid","理论：PID 与误差收敛","03-pid.md"),
    ("theory-robust","理论：鲁棒控制与不确定性","04-robust.md"),
    ("theory-hierarchical","理论：分层控制与慢快双速","05-hierarchical.md"),
]
def gen_theory(fname,title,md_file,prev,nxt):
    md=read("01-theory/"+md_file)
    cards=kt_card_block(md)
    body="<span class='kicker'>Theory · 控制理论证据包</span><p class='breadcrumb'><a href='index.html'>总览</a> › 理论</p>"+render_kt_cards(cards)
    return page(title,"理论证据包 · 31 知识点",body,fname,prev,nxt)

def gen_case(fname,title,md_file,prev,nxt):
    md=read("03-cases/"+md_file)
    import render_case as rc
    body = rc.render_case(md, md_file.replace('.md',''))
    return page(title,"产品控制论画像","<p class='breadcrumb'><a href='index.html'>总览</a> › 案例</p>"+body,fname,prev,nxt)

def gen_exp(fname,title,md_file,prev,nxt):
    md=read("06-experiments/"+md_file)
    import render_exp as rexp
    body = rexp.render_exp(md, md_file.replace('.md',''))
    return page(title,"标准实验组","<p class='breadcrumb'><a href='index.html'>总览</a> › 实验</p>"+body,fname,prev,nxt)

# 精装房数据（精装度主轴排序，供全景页）
# 分值来自 09-src-data/premium_scores.py（硬门槛+8维加权+一票否决），禁止硬编码
PREMIUM_DATA = [
    # (slug, 名称, 厂商, 精装度, 一手二手, 大类, 证据级, 关键结论)
    (p["slug"], p["name"], p["vendor"], ps.final(p["slug"]),
     p["hand"], p["cat"], p["ev"], p["note"])
    for p in ps.PRODUCTS
]

# 现有 6 产品（技术框架）纳入同一坐标系 —— 均为开源、需装配/定制，精装度偏低
FRAMEWORK_DATA = [
    # (slug, 名称, 厂商, 精装度, 一手二手, 大类, 证据级, 关键结论)
    ("claude-code","claude-code","Anthropic",3.0,"一手","开源成品化","源码级","官方CLI+skills+MCP，相对开箱但需自配"),
    ("codex","codex","OpenAI",3.0,"一手","开源成品化","源码级","Rust CLI+沙箱+双评审器，需自配"),
    ("opencode","opencode","SST",3.0,"一手","开源成品化","源码级","plan/build双速+权限+snapshot，需配置装配层"),
    ("dsh","deepseek-harness","DeepSeek",2.5,"一手","开源成品化","源码级","cordis插件装配，需组装76核心+36 seam"),
    ("prime","PRIME","Prime Intellect",2.5,"一手","开源成品化","源码级","RLM+continual harness，需配gate/skills"),
    ("hermes","hermes","NousResearch",2.5,"一手","开源成品化","源码级","MCP-based观测器，需配置"),
]

def gen_premium_map():
    # 按精装度降序
    data = sorted(PREMIUM_DATA, key=lambda x: -x[3])
    def score_color(s):
        return '#1F7A52' if s >= 4.5 else ('#C77700' if s >= 3.5 else '#B23A2F')
    def hand_badge(h):
        c = '#1E5AA8' if h == '一手' else '#B23A2F'
        return f'<span class="pm-badge" style="background:{c}">{h}</span>'
    # 主轴谱系（横向条形）
    bars = []
    for slug,name,vendor,score,hand,cat,ev,note in data:
        pct = score/5*100
        bars.append(f"""
<div class="pm-row">
  <a class="pm-name" href="premium-{slug}.html">{name}</a>
  <span class="pm-vendor">{vendor}</span>
  <div class="pm-bar-wrap"><div class="pm-bar" style="width:{pct:.0f}%;background:{score_color(score)}"></div></div>
  <span class="pm-score" style="color:{score_color(score)}">{ps.fmt(score)}</span>
  {hand_badge(hand)}
  <span class="pm-cat">{cat}</span>
</div>""")
    # 技术框架对照组条形
    fw_bars = []
    for slug,name,vendor,score,hand,cat,ev,note in sorted(FRAMEWORK_DATA, key=lambda x:-x[3]):
        pct = score/5*100
        fw_bars.append(f"""
<div class="pm-row">
  <a class="pm-name" href="case-{slug}.html">{name}</a>
  <span class="pm-vendor">{vendor}</span>
  <div class="pm-bar-wrap"><div class="pm-bar" style="width:{pct:.0f}%;background:{score_color(score)}"></div></div>
  <span class="pm-score" style="color:{score_color(score)}">{score}</span>
  {hand_badge(hand)}
  <span class="pm-cat">{cat}</span>
</div>""")

    # 4大类分组卡片
    cats = {}
    for row in data:
        cats.setdefault(row[5], []).append(row)
    cat_cards = []
    cat_desc = {
        "第一方成品":"大厂/公司自研的端到端成品 Agent，开箱即用度最高",
        "低代码平台":"拖拽/配置即用的 Agent 搭建平台，非开发者也可上手",
        "开源成品化":"开源项目预装到可运维程度，clone 即用（部分限单一域）",
        "二次封装":"声称『平替/增强XX』的发行版——实证区分：一手自研底层 vs 二手封装/中转（声称 vs 实际关键案例）",
    }
    for cat, rows in cats.items():
        items = "".join(f'<li><a href="premium-{r[0]}.html">{r[1]}</a> <span class="pm-mini" style="color:{score_color(r[3])}">{ps.fmt(r[3])}</span> {hand_badge(r[4])}</li>' for r in sorted(rows,key=lambda x:-x[3]))
        cat_cards.append(f"""
<div class="pm-catcard">
  <h3>{cat} <span class="pm-count">{len(rows)}</span></h3>
  <p class="pm-catdesc">{cat_desc.get(cat,'')}</p>
  <ul>{items}</ul>
</div>""")
    # 分层速览（按 v2.0 加权模型动态生成）
    tiers = {}
    for slug, name, vendor, score, hand, cat, ev, note in data:
        tiers.setdefault(ps.tier(score), []).append("%s(%s)" % (name, ps.fmt(score)))
    tier_defs = [
        ("真·开箱即用", "≥4.5", "预装 UI+多Agent+沙箱/工具+一键部署，零配置跑端到端"),
        ("成品化受限", "3.5-4.5", "预装大部分能力，个别维度受限"),
        ("需装修/中转", "&lt;3.5", "需填角色流程/依赖底座/纯中转，未达零配置门槛"),
    ]
    tier_cards = []
    for t, rng, desc in tier_defs:
        names = " / ".join(tiers.get(t, [])) or "—"
        tier_cards.append(f'<div class="insight"><b>{t}（{rng}）</b><br>{desc}<br><span style="color:var(--muted)">{names}</span></div>')
    tier_cards.append('<div class="insight"><b>实证方法</b><br>开源产品走源码级（raw.githubusercontent 依赖/入口/包壳）；闭源产品走文档级（官方文档）+ 声称级标注。</div>')
    body = f"""
<div class="signal">
  <div class="signal-head"><span class="label">Premium Housing · 精装房全景</span><span class="tag">v2.0 · {len(data)} product</span></div>
  <span class="kicker" style="font-family:var(--font-mono);letter-spacing:.12em;color:#7E8CA5;font-size:11px">PREMIUM</span>
  <h1 style="font-size:26px;margin:8px 0 10px;color:#fff;letter-spacing:-.02em">市面「精装房」Agent 全景</h1>
  <p style="color:#CBD4E2;max-width:760px;line-height:1.7;font-size:15px;margin:0">核心命题：<b>声称 ≠ 实际</b>。以「精装度」为主轴（0-5 分，<b>v2.0 加权模型：硬门槛 + 8 维加权 + 一票否决</b>），「一手/二手」为标签，「4 大类」为分组，「五环」定控制本质——用源码级/文档级实证，鉴别每款产品到底精装到什么程度。</p>
</div>

<h2><span class="idx">01</span>精装度主轴（0-5 分，降序）</h2>
<div class="pm-axis">{''.join(bars)}</div>

<h2><span class="idx">02</span>四大类分布</h2>
<div class="pm-cats">{''.join(cat_cards)}</div>

<h2><span class="idx">03</span>核心实证发现：声称 vs 实际</h2>
<div class="premium-block" style="border:1.5px solid var(--ctrl-blue-soft)">
  <div class="prem-claim" style="background:var(--signal-red-bg);border-color:var(--signal-red)">
    <strong>二手被高估</strong>：CC-Router 声称「Claude Code 增强」，源码级铁证依赖 <code>@the-next-ai/ai-gateway</code> 第三方网关；QCode 声称「平替」，官方明示「官方价×服务倍率」——<b>实为封装/中转</b>。
  </div>
  <div class="prem-claim" style="background:var(--signal-amber-bg);border-color:var(--signal-amber)">
    <strong>一手被低估</strong>：CodeWhale、OpenClaude 都打「平替 Claude Code」标签，源码证实<b>独立自研底层</b>（Rust crate / 独立 TS 实现），比声称更原创。
  </div>
  <div class="prem-claim" style="background:var(--ctrl-blue-soft);border-color:var(--ctrl-blue)">
    <strong>声称功能不存在</strong>：Windsurf 被传有「Flows DAG」多Agent编排，官方文档检索证实<b>并无此功能</b>——多Agent并发靠 Arena Mode + worktrees + Managed Devins。
  </div>
  <div class="prem-claim" style="background:var(--signal-amber-bg);border-color:var(--signal-amber)">
    <strong>精装度与一手/二手正交</strong>：二手未必精装（QCode 1.4 / CC-Router 2.1），一手也未必精装（CrewAI 3.0）——两根独立的轴，必须分开标注。
  </div>
</div>

<h2><span class="idx">04</span>技术框架对照（原 6 产品，纳入同一坐标系）</h2>
<p style="font-size:13px;color:var(--muted);margin:0 0 var(--space-3)">原 6 产品均为<b>开源技术框架</b>——不是"精装房"而是"毛坯/简装房"：能力强大但需自行装配、配置、定制。它们落在精装度主轴的低段（2.5-3），归入"开源成品化"类作对照。</p>
<div class="pm-axis">{''.join(fw_bars)}</div>

<h2><span class="idx">05</span>精装度分层速览</h2>
<div class="grid cols-2">{''.join(tier_cards)}</div>

<p style="font-size:13px;color:var(--muted);margin-top:var(--space-5)">注：精装度采用 <b>v2.0 加权模型</b>（硬门槛前置 + 8 维加权 + 一票否决），以「用户零配置即可跑端到端任务」为核心锚点；证据强度分级：源码级 &gt; 文档级 &gt; 行为级 &gt; 声称级。模型/权重/评分标准见 <code>07-checkpoint/premium-scoring-model.md</code>，重算矩阵见 <code>07-checkpoint/premium-score-recompute.md</code>，详细证据见 <code>07-checkpoint/premium-evidence.md</code>。</p>
"""
    return page("精装房全景","市面精装房 Agent 全景","<p class='breadcrumb'><a href='index.html'>总览</a> › 精装房全景</p>"+body,"premium-map",prev=None,nxt="premium-cyto")

def gen_premium_case(fname,title,md_file,prev,nxt):
    md=read("03-cases/"+md_file)
    import render_case as rc
    body = rc.render_case(md, md_file.replace('.md','').replace('premium-',''))
    return page(title,"精装房控制论画像","<p class='breadcrumb'><a href='index.html'>总览</a> › <a href='premium-map.html'>精装房全景</a> › 画像</p>"+body,fname,prev,nxt)

# 生成
pages={}
pages["index"]=gen_overview()
pages["framework"]=gen_framework()
for i,(fn,ti,mf) in enumerate(THEORY_META):
    prev = "framework" if i==0 else THEORY_META[i-1][0]
    nxt = "theory-state-est" if fn=="theory-closed-loop" else (THEORY_META[i+1][0] if i+1<len(THEORY_META) else "case-opencode")
    pages[fn]=gen_theory(fn,ti,mf,prev,nxt)

CASES=[("case-opencode","案例：opencode","opencode.md"),("case-dsh","案例：deepseek-harness","deepseek-harness.md"),("case-prime","案例：PRIME","prime.md"),("case-hermes","案例：hermes","hermes.md"),("case-claude-code","案例：claude-code","claude-code.md"),("case-codex","案例：codex","codex.md")]
for i,(fn,ti,mf) in enumerate(CASES):
    prev="theory-hierarchical" if i==0 else CASES[i-1][0]
    nxt=CASES[i+1][0] if i+1<len(CASES) else "exp-opencode"
    pages[fn]=gen_case(fn,ti,mf,prev,nxt)

EXPS=[("exp-opencode","实验：opencode","opencode.md"),("exp-dsh","实验：dsh","deepseek-harness.md"),("exp-prime","实验：PRIME","prime.md"),("exp-hermes","实验：hermes","hermes.md"),("exp-claude-code","实验：claude-code","claude-code.md"),("exp-codex","实验：codex","codex.md")]
for i,(fn,ti,mf) in enumerate(EXPS):
    prev="case-codex" if i==0 else EXPS[i-1][0]
    nxt=EXPS[i+1][0] if i+1<len(EXPS) else None
    pages[fn]=gen_exp(fn,ti,mf,prev,nxt)

# 精装房全景页
pages["premium-map"]=gen_premium_map()

# 精装房案例（与 nav_data NAV 顺序一致）
PREMIUM=[("premium-cursor","精装房：Cursor","premium-cursor.md"),
         ("premium-devin","精装房：Devin","premium-devin.md"),
         ("premium-workbuddy","精装房：WorkBuddy","premium-workbuddy.md"),
         ("premium-windsurf","精装房：Windsurf","premium-windsurf.md"),
         ("premium-copilot","精装房：GitHub Copilot","premium-copilot.md"),
         ("premium-dify","精装房：Dify","premium-dify.md"),
         ("premium-openhands","精装房：OpenHands","premium-openhands.md"),
         ("premium-coze","精装房：Coze","premium-coze.md"),
         ("premium-openclaude","精装房：OpenClaude","premium-openclaude.md"),
         ("premium-codewhale","精装房：CodeWhale","premium-codewhale.md"),
         ("premium-gptresearcher","精装房：GPT Researcher","premium-gptresearcher.md"),
         ("premium-qcode","精装房：QCode","premium-qcode.md"),
         ("premium-ccrouter","精装房：CC-Router","premium-ccrouter.md"),
         ("premium-crewai","精装房：CrewAI","premium-crewai.md")]
for i,(fn,ti,mf) in enumerate(PREMIUM):
    prev="premium-map" if i==0 else PREMIUM[i-1][0]
    nxt=PREMIUM[i+1][0] if i+1<len(PREMIUM) else None
    pages[fn]=gen_premium_case(fn,ti,mf,prev,nxt)

for fn,content in pages.items():
    with open(os.path.join(OUT,fn+".html"),"w",encoding="utf-8") as f:
        f.write(content)
    print("生成: %s.html (%d 字符)"%(fn,len(content)))
print("完成! 共生成 %d 个 HTML 页面" % len(pages))
