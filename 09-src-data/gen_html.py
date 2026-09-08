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
<span>控制理论 ⊗ Agent 设计知识库 · v1.2 自改造 opencode 变体版（6 框架 + 14 精装房 + opencode-custom）</span>
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
    <span class="tag">v1.2 · 6 framework + 14 premium + opencode-custom</span>
  </div>
  <svg viewBox="0 0 900 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="五环控制回路：目标 r 指令 → P 规划 → T 执行 → 世界/环境 → E 评估 → M 记忆 → R 反思，修正量回馈 P/T">
    <defs>
      <marker id="arrF" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M0 0 L10 5 L0 10 z" fill="#5B9BD5"/>
      </marker>
      <marker id="arrM" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M0 0 L10 5 L0 10 z" fill="#3FBF8A"/>
      </marker>
      <marker id="arrC" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M0 0 L10 5 L0 10 z" fill="#E0A030"/>
      </marker>
    </defs>
    <g font-family="var(--font-mono),ui-monospace,monospace" font-size="12.5" font-weight="600" text-anchor="middle">
      <rect x="20" y="48" width="92" height="44" rx="22" fill="none" stroke="#7E8CA5" stroke-width="1.5"/>
      <text x="66" y="75" fill="#CBD4E2">目标 r</text>
      <rect x="150" y="48" width="132" height="44" rx="8" fill="#2F74BE"/>
      <text x="216" y="75" fill="#FFFFFF">P 规划/分层</text>
      <rect x="320" y="48" width="132" height="44" rx="8" fill="#7263C8"/>
      <text x="386" y="75" fill="#FFFFFF">T 工具/执行</text>
      <rect x="490" y="48" width="132" height="44" rx="8" fill="#627187"/>
      <text x="556" y="75" fill="#FFFFFF">世界/环境</text>
      <rect x="150" y="196" width="132" height="44" rx="8" fill="#A85F00"/>
      <text x="216" y="223" fill="#FFFFFF">R 反思/反馈</text>
      <rect x="320" y="196" width="132" height="44" rx="8" fill="#1F7A52"/>
      <text x="386" y="223" fill="#FFFFFF">M 记忆/状态</text>
      <rect x="490" y="196" width="132" height="44" rx="8" fill="#C64A3C"/>
      <text x="556" y="223" fill="#FFFFFF">E 评估/传感</text>
    </g>
    <path d="M112 70 H150" stroke="#5B9BD5" stroke-width="1.8" fill="none" marker-end="url(#arrF)"/>
    <path d="M282 70 H320" stroke="#5B9BD5" stroke-width="1.8" fill="none" marker-end="url(#arrF)"/>
    <path d="M452 70 H490" stroke="#5B9BD5" stroke-width="1.8" fill="none" marker-end="url(#arrF)"/>
    <path d="M556 92 V196" stroke="#3FBF8A" stroke-width="1.8" fill="none" marker-end="url(#arrM)"/>
    <path d="M490 218 H452" stroke="#3FBF8A" stroke-width="1.8" fill="none" marker-end="url(#arrM)"/>
    <path d="M320 218 H282" stroke="#3FBF8A" stroke-width="1.8" fill="none" marker-end="url(#arrM)"/>
    <path d="M216 196 V92" stroke="#E0A030" stroke-width="1.7" stroke-dasharray="5 4" fill="none" marker-end="url(#arrC)"/>
    <path d="M250 196 V156 Q250 144 262 144 H374 Q386 144 386 156 V92" stroke="#E0A030" stroke-width="1.7" stroke-dasharray="5 4" fill="none" marker-end="url(#arrC)"/>
  </svg>
  <div class="signal-legend">
    <span><i style="background:#2F74BE"></i>P 规划</span><span><i style="background:#7263C8"></i>T 执行</span>
    <span><i style="background:#C64A3C"></i>E 评估</span><span><i style="background:#1F7A52"></i>M 记忆</span>
    <span><i style="background:#A85F00"></i>R 反思</span><span><i style="background:#627187"></i>世界/环境</span>
  </div>
  <div class="signal-legend" style="margin-top:8px">
    <span><i style="width:22px;height:0;border-radius:0;border-top:2px solid #5B9BD5"></i>前向指令链</span>
    <span><i style="width:22px;height:0;border-radius:0;border-top:2px solid #3FBF8A"></i>反馈/测量链</span>
    <span><i style="width:22px;height:0;border-radius:0;border-top:2px dashed #E0A030"></i>修正量回馈</span>
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

<h2><span class="idx">05</span>opencode 自改造专题</h2>
<p class="lead">官方 opencode 的衍生变体 · 装配层补强 E/R 弱环 · 精装度 2.9→3.9</p>
<div class="grid cols-2">
  <a class="portal-card" href="case-opencode-custom.html" style="background:var(--panel);border:1px solid var(--line);border-radius:var(--r-md);padding:var(--space-4);text-decoration:none">
    <span class="num">VARIANT</span><h3 style="margin:0 0 6px">opencode-custom 控制论画像</h3><p style="margin:0">内核继承 + 装配层增强：GATE/契约/专职 worker/Reflection 把前馈主导内核改造为跨会话自演化闭环</p>
  </a>
  <a class="portal-card" href="compare-opencode.html" style="background:var(--panel);border:1px solid var(--line);border-radius:var(--r-md);padding:var(--space-4);text-decoration:none">
    <span class="num">COMPARE</span><h3 style="margin:0 0 6px">官方 vs 自改造对照</h3><p style="margin:0">五环雷达叠加 + 逐环 delta + 精装度 8 维对比，量化 2.9→3.9 的跃升来源</p>
  </a>
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

def gen_compare_opencode():
    """官方 opencode vs opencode-custom 对照页：五环雷达叠加 + 逐环 delta + 精装度 8 维对比。"""
    import math
    import opencode_custom_scores as ocs
    OFF, CUS = "opencode-official", "opencode-custom"
    order, n = ocs.RING_ORDER, len(ocs.RING_ORDER)
    cx, cy, RAD = 240, 210, 150

    def pt(i, val):
        ang = math.radians(-90 + i * 360.0 / n)
        r = RAD * val / 5.0
        return cx + r * math.cos(ang), cy + r * math.sin(ang)

    grids = []
    for lvl in range(1, 6):
        pts = " ".join("%.1f,%.1f" % pt(i, lvl) for i in range(n))
        grids.append(f'<polygon points="{pts}" fill="none" stroke="#DFE5EC" stroke-width="1"/>')
    spokes = []
    for i in range(n):
        x, y = pt(i, 5)
        spokes.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#E4E9F0" stroke-width="1"/>')

    def poly(key, fill, stroke):
        pts = " ".join("%.1f,%.1f" % pt(i, ocs.RING_SCORES[key][rid]) for i, rid in enumerate(order))
        return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="2.4" stroke-linejoin="round"/>'

    def dots(key, color):
        out = []
        for i, rid in enumerate(order):
            x, y = pt(i, ocs.RING_SCORES[key][rid])
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{color}"/>')
        return "".join(out)

    labels = []
    for i, rid in enumerate(order):
        x, y = pt(i, 5.62)
        labels.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" dominant-baseline="middle" '
                      f'font-size="13" font-weight="700" fill="#0B1220">{rid} {ocs.RING_META[rid]["label"]}</text>')

    radar_svg = ("\n<svg viewBox=\"0 0 480 420\" xmlns=\"http://www.w3.org/2000/svg\" role=\"img\" "
                 "aria-label=\"五环雷达图：官方 opencode 内核与自改造综合分值叠加对比\">\n"
                 "  <g>" + "".join(grids) + "".join(spokes) + "</g>\n"
                 "  <g>" + poly(OFF, "rgba(90,107,133,.20)", "#5A6B85")
                 + poly(CUS, "rgba(199,119,0,.22)", "#C77700") + "</g>\n"
                 "  <g>" + "".join(labels) + dots(OFF, "#5A6B85") + dots(CUS, "#C77700") + "</g>\n"
                 "</svg>")

    # 逐环 delta 卡片
    cards = []
    for rid in order:
        o, c, d, tag = ocs.ring_delta(rid)
        m = ocs.RING_META[rid]
        badge_cls = "weak" if tag == "反转" else "strong"
        dstr = ("+%.1f" % d) if d >= 0 else ("%.1f" % d)
        cards.append(f"""
<div class="card" style="border-left:4px solid {m['color']}">
  <span class="num" style="color:{m['color']}">{rid} RING · {m['ctrl']}</span>
  <h3 style="margin:2px 0 10px;color:var(--ink)">{m['label']} <span class="badge {badge_cls}">{tag}</span></h3>
  <div style="display:flex;align-items:baseline;flex-wrap:wrap;gap:10px;font-family:var(--font-mono);margin-bottom:8px">
    <span style="color:var(--muted);font-size:12.5px">官方内核</span><b style="font-size:20px;color:#5A6B85">{o}</b>
    <span style="color:var(--muted-2)">→</span>
    <span style="color:var(--muted);font-size:12.5px">自改造综合</span><b style="font-size:22px;color:{m['color']}">{c}</b>
    <span style="color:var(--muted);font-size:12.5px">Δ{dstr}</span>
  </div>
  <p style="margin:0;font-size:13.5px;color:var(--muted)">{m['change']}</p>
</div>""")

    # 精装度 8 维对比表（数值唯一来源 opencode_custom_scores.SCORES）
    dim_rows = []
    for dim, label, w in ps.DIMS:
        o = ocs.SCORES[OFF]["dims"][dim]
        c = ocs.SCORES[CUS]["dims"][dim]
        d = c - o
        dstr = ("+%d" % d) if d > 0 else ("%d" % d)
        col = "var(--state-green)" if d > 0 else "var(--muted-2)"
        ev = ocs.SCORES[CUS]["evidence"][dim]
        dim_rows.append(f'<tr><td>{label}</td><td class="mono">{w}%</td><td class="mono">{o}</td>'
                        f'<td class="mono" style="font-weight:700">{c}</td>'
                        f'<td class="mono" style="color:{col};font-weight:700">{dstr}</td>'
                        f'<td style="font-size:12.5px;color:var(--muted)">{ev}</td></tr>')

    # 8 类改造清单（来自 03-cases/opencode-custom-diff.md §2）
    changes = [
        ("Agent 扩展", "新增 5 个专职 worker：pdf / drawio / vision / reflection / search（hidden subagent，subagent_depth=2）", "P 主 + T", "P：双速→分层编排平台；T：工具能力按 worker 隔离授权"),
        ("协议层", "auto-mode.md（GATE/COMPLEXITY/variant/委派/留档）+ search-behavior.md（外部信息实证）+ agent-protocol.md（委派/Reflection 自检/MCP 路由）", "P / E / R 跨环", "P：目标物化+推理档分层；E：信源分级+用户确认；R：反思启动即触发"),
        ("Skill 库", "28 个 skills（cytoscape / kb-construction / openspec 系列等）+ 11 个 legacy skill", "T + E", "T：能力密度大幅提升；E：grill-me 收敛 + 方法论 skill 提供评估范式"),
        ("MCP 集成", "6 个 MCP：vscode / amap / pdf-reader / drawio / drawio-local / headroom（多传输，部分启用）", "T", "T：外部工具生态可插拔，pdf/drawio 仅授权对应 worker"),
        ("Reflection 自演化系统", "MEMORY.md 跨会话记忆 + pending.json 结构化状态机 + reflection-worker + /reflection 命令", "R（核心）", "R：半开环→跨会话闭环自演化（核心反转）；M：补齐长期记忆"),
        ("Provider 扩展", "3 个 provider 预设：opencode-go / deepseek / zhipu，含多模型与 Daily/Deep variant", "T（基建）", "T：模型接入面扩大，支撑专职 worker 与视觉降级路径"),
        ("Compaction / variant 调优", "tail_turns=4、preserve_recent_tokens=16384、reserved=10000；Daily/Deep 推理档分档", "M（基建）", "M：状态估计更新预算精细可控；P：推理档随复杂度动态分配"),
        ("Permission 规则", "external_directory 白名单 + read auth.json deny + bash 危险命令 deny/ask + edit 分层授权", "T（安全）", "T：执行器最小授权与越权收口，仍非完整沙箱"),
    ]
    ch_rows = "".join(f'<tr><td><b>{a}</b></td><td>{b}</td><td class="mono">{c}</td><td>{d}</td></tr>'
                      for a, b, c, d in changes)

    findings = [
        ("发现一 · 弱环反转", "官方两大最弱环 E/R 被装配层补齐并反转。",
         "E 环 2.0→4.0（信源分级 + search-worker 证据包 + 用户传感器）；R 环 2.0→4.5（pending.json 状态机 + reflection-worker + /reflection 签名门禁）。补强方式不是改引擎，而是协议 + 专职 worker + 记忆系统。"),
        ("发现二 · 精装度跃升", f"{ps.fmt(ocs.final(OFF))} → {ps.fmt(ocs.final(CUS))}（Δ+%.1f），主要来自记忆与 skill 两维。" % (ocs.final(CUS) - ocs.final(OFF)),
         "8 维中 6 维提升：记忆 +2（达满分 5）、skill +2，多Agent/工作流/模型/MCP 各 +1；仅一键部署与沙箱未提升——个人装配层无分发渠道、无完整沙箱，是精装度封顶的主因。"),
        ("发现三 · 编排升级", "从单体双速控制器到分层编排平台。",
         "官方是 plan/build 双速 + task 委派的单体结构；自改造叠加 5 个专职 worker，形成「主 Agent 编排 + 专职 worker 执行 + Reflection 自演化」三层平台，P 环与 T 环均升至 5.0。代价：编排拓扑仍靠协议文本而非 DAG 画布，闭环反思仍需人工确认。"),
    ]
    find_cards = "".join(f'<div class="card"><span class="num">{t.split(" · ")[0]}</span>'
                         f'<h3 style="margin:0 0 6px">{t.split(" · ", 1)[1]}</h3>'
                         f'<p style="margin:0 0 8px;color:var(--ink);font-size:14px">{lead}</p>'
                         f'<p style="margin:0;color:var(--muted);font-size:13.5px">{body}</p></div>'
                         for t, lead, body in findings)

    signal = f"""
<div class="signal">
  <div class="signal-head"><span class="label">Compare · 官方基线 ⊗ 自改造装配层</span>
    <span class="tag">opencode {ps.fmt(ocs.final(OFF))} → {ps.fmt(ocs.final(CUS))}</span></div>
  <span class="kicker" style="font-family:var(--font-mono);letter-spacing:.12em;color:#7E8CA5;font-size:11px">COMPARE</span>
  <h1 style="font-size:26px;margin:8px 0 10px;color:#fff;letter-spacing:-.02em">官方 opencode ⊗ opencode-custom</h1>
  <p style="color:#CBD4E2;max-width:760px;line-height:1.7;font-size:15px;margin:0 0 14px">核心命题三线：<b>弱环定向补强</b>（不改引擎，仅在配置/协议/skill/MCP/记忆五层补 E/R）· <b>精装度跃升 {ps.fmt(ocs.final(OFF))}→{ps.fmt(ocs.final(CUS))}</b>（8 维中 6 维提升，记忆达满分）· <b>编排升级</b>（plan/build 双速 → 三层分层编排平台）。</p>
  <div class="signal-legend">
    <span><i style="background:#5A6B85"></i>官方内核</span>
    <span><i style="background:#C77700"></i>自改造综合</span>
    <span><i style="width:22px;height:0;border-radius:0;border-top:2px solid #C77700"></i>增强 / 反转环</span>
  </div>
</div>"""

    body = signal + f"""
<h2><span class="idx">01</span>五环雷达 · 官方内核 vs 自改造综合</h2>
<div class="ring-section" style="padding:var(--space-4)">
  <div style="display:flex;flex-wrap:wrap;gap:var(--space-4);align-items:center">
    <div style="flex:1 1 420px;min-width:300px;max-width:560px">{radar_svg}</div>
    <div style="flex:1 1 260px;min-width:240px">
      <table>
        <thead><tr><th>环</th><th>官方</th><th>自改造</th><th>Δ</th></tr></thead>
        <tbody>
        {''.join(f'<tr><td><span class="ring-tag" style="background:{ocs.RING_META[r]["color"]}">{r}</span> {ocs.RING_META[r]["label"]}</td><td class="mono">{ocs.RING_SCORES[OFF][r]}</td><td class="mono" style="font-weight:700;color:{ocs.RING_META[r]["color"]}">{ocs.RING_SCORES[CUS][r]}</td><td class="mono">+{ocs.RING_SCORES[CUS][r]-ocs.RING_SCORES[OFF][r]:.1f}</td></tr>' for r in order)}
        </tbody>
      </table>
      <p style="font-size:12.5px;color:var(--muted);margin:0">分值 0–5，取自 <code>09-src-data/opencode_custom_scores.py</code>（RING_SCORES）。E/R 两环为「反转」，其余为「增强」。</p>
    </div>
  </div>
</div>

<h2><span class="idx">02</span>逐环 delta 卡片</h2>
<div class="grid cols-3">{''.join(cards)}</div>

<h2><span class="idx">03</span>精装度 8 维对比</h2>
<table>
  <thead><tr><th>维度</th><th>权重</th><th>官方</th><th>自改造</th><th>Δ</th><th>依据</th></tr></thead>
  <tbody>{''.join(dim_rows)}</tbody>
</table>
<p style="font-size:12.5px;color:var(--muted)">数值唯一来源：<code>opencode_custom_scores.py</code> 的 <code>SCORES</code> / <code>WEIGHTS</code>；官方加权 {ocs.weighted(OFF):.2f}→{ps.fmt(ocs.final(OFF))}，自改造加权 {ocs.weighted(CUS):.2f}→{ps.fmt(ocs.final(CUS))}，均过端到端硬门槛、无一票否决。</p>

<h2><span class="idx">04</span>8 类改造清单</h2>
<table>
  <thead><tr><th>类别</th><th>改造内容</th><th>五环权重</th><th>对环影响</th></tr></thead>
  <tbody>{ch_rows}</tbody>
</table>

<h2><span class="idx">05</span>三大核心发现</h2>
<div class="grid cols-3">{find_cards}</div>
"""
    return page("官方 vs 自改造对照", "opencode 官方基线 ⊗ opencode-custom 装配层",
                "<p class='breadcrumb'><a href='index.html'>总览</a> › 官方 vs 自改造对照</p>" + body,
                "compare-opencode", prev="case-opencode-custom", nxt="case-dsh")

# 生成
pages={}
pages["index"]=gen_overview()
pages["framework"]=gen_framework()
for i,(fn,ti,mf) in enumerate(THEORY_META):
    prev = "framework" if i==0 else THEORY_META[i-1][0]
    nxt = "theory-state-est" if fn=="theory-closed-loop" else (THEORY_META[i+1][0] if i+1<len(THEORY_META) else "case-opencode")
    pages[fn]=gen_theory(fn,ti,mf,prev,nxt)

CASES=[("case-opencode","案例：opencode","opencode.md"),("case-opencode-custom","案例：opencode-custom（自改造）","opencode-custom.md"),("case-dsh","案例：deepseek-harness","deepseek-harness.md"),("case-prime","案例：PRIME","prime.md"),("case-hermes","案例：hermes","hermes.md"),("case-claude-code","案例：claude-code","claude-code.md"),("case-codex","案例：codex","codex.md")]
for i,(fn,ti,mf) in enumerate(CASES):
    prev="theory-hierarchical" if i==0 else CASES[i-1][0]
    nxt=CASES[i+1][0] if i+1<len(CASES) else "exp-opencode"
    pages[fn]=gen_case(fn,ti,mf,prev,nxt)

EXPS=[("exp-opencode","实验：opencode","opencode.md"),("exp-opencode-custom","实验：opencode-custom","opencode-custom.md"),("exp-dsh","实验：dsh","deepseek-harness.md"),("exp-prime","实验：PRIME","prime.md"),("exp-hermes","实验：hermes","hermes.md"),("exp-claude-code","实验：claude-code","claude-code.md"),("exp-codex","实验：codex","codex.md")]
for i,(fn,ti,mf) in enumerate(EXPS):
    prev="case-codex" if i==0 else EXPS[i-1][0]
    nxt=EXPS[i+1][0] if i+1<len(EXPS) else None
    pages[fn]=gen_exp(fn,ti,mf,prev,nxt)

# 官方 vs 自改造对照页
pages["compare-opencode"]=gen_compare_opencode()

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
