# -*- coding: utf-8 -*-
"""framework.md 专用渲染器 - 把五环结构化内容渲染为高质量 HTML"""
import re, html, sys
sys.stdout.reconfigure(encoding='utf-8')

RING_META = {
  'M': {'name':'记忆 / 状态估计','ctrl':'状态观测器 / 卡尔曼','color':'#1F7A52','tag':'KT-ctrl-010~015','desc':'从带噪观测估计无法直测的内部状态，维护信念与置信度'},
  'P': {'name':'规划 / 分层控制','ctrl':'慢速上层策略控制器','color':'#1E5AA8','tag':'KT-ctrl-041~046','desc':'把目标+当前信念拆成里程碑序列，滚动重规划'},
  'R': {'name':'反思 / 反馈闭环','ctrl':'反馈控制器（PID/校正律）','color':'#C77700','tag':'KT-ctrl-002~026','desc':'算误差、累积纠偏、抑制超调，向 P/T 回灌修正量'},
  'T': {'name':'工具调用 / 执行器','ctrl':'执行器+安全阀+仲裁','color':'#5B4B9B','tag':'KT-ctrl-030~035','desc':'以限幅/冗余/看门狗执行动作，容忍不确定性'},
  'E': {'name':'评估 / 传感器','ctrl':'测量环节+验证器','color':'#B23A2F','tag':'KT-ctrl-001~006','desc':'产出反馈信号，其信噪比决定整个闭环能走多远'},
}

def bold(text):
    """escape 后处理 **加粗** 和 `code`"""
    t = html.escape(text)
    # **粗体** 已转义为 &#x2A;，这里文本中的 ** 是字面 *
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    return t

def parse_framework(md):
    """返回 {ring_id: {name, loc, concepts:[], mapping:[], decisions:[], paradigm:[]}}"""
    # 按章节切分
    sections = re.split(r'\n(?=## )', md)
    rings = {}
    order = []
    for sec in sections:
        m = re.match(r'## (\d)\. ([MPRTE]) 环 — (.*)', sec)
        if not m:
            continue
        rid = m.group(2)
        order.append(rid)
        # 环定位 (### 环定位 后的 blockquote)
        loc = ''
        lm = re.search(r'### 环定位\s*\n>\s*(.*)', sec)
        if lm: loc = lm.group(1).strip()
        # 核心控制概念表
        concepts = []
        cm = re.search(r'### 核心控制概念\s*\n(.*?)(?=\n### |\Z)', sec, re.S)
        if cm:
            # 解析 md 表格行
            for line in cm.group(1).split('\n'):
                if not line.strip().startswith('|'): continue
                # 跳过表头分隔行 (纯 - 和 : 组成)
                if re.match(r'^\|[\s:|-]+\|$', line.strip()):
                    continue
                cells = [c.strip() for c in line.strip().strip('|').split('|')]
                if cells and cells[0].replace('*','').strip() in ('概念',''):
                    continue
                if len(cells) >= 4:
                    concepts.append({'name':cells[0].replace('**','').strip(),'kt':cells[1].strip(),'one':cells[2].strip(),'carry':cells[3].strip()})
        # 列表提取 (### 小节标题 → 列表项)
        def list_of(sub):
            msub = re.search(r'### %s\s*\n(.*?)(?=\n### |\Z)' % sub, sec, re.S)
            if not msub: return []
            items = []
            for line in msub.group(1).split('\n'):
                line=line.strip()
                if line.startswith('- '):
                    items.append(line[2:].strip())
            return items
        rings[rid] = {
          'name': m.group(3).strip(), 'loc': loc, 'concepts': concepts,
          'mapping': list_of('Agent 映射'), 'decisions': list_of('关键工程决策'),
          'paradigm': list_of('设计范式')
        }
    return rings, order

def render_framework(md, title):
    rings, order = parse_framework(md)
    cards = []
    for rid in order:
        r = rings[rid]
        meta = RING_META[rid]
        # 控制概念表
        concept_rows = ''
        for c in r['concepts']:
            concept_rows += f"<tr><td><strong>{html.escape(c['name'])}</strong></td><td class='mono'>{html.escape(c['kt'])}</td><td>{bold(c['one'])}</td><td>{bold(c['carry'])}</td></tr>"
        mapping_html = ''.join(f"<li>{bold(x)}</li>" for x in r['mapping']) if r['mapping'] else ''
        dec_html = ''.join(f"<li>{bold(x)}</li>" for x in r['decisions']) if r['decisions'] else ''
        para_html = ''.join(f"<li>{bold(x)}</li>" for x in r['paradigm']) if r['paradigm'] else ''
        cards.append(f"""
<div class="ring-section" id="ring-{rid}">
  <div class="ring-head">
    <span class="ring-tag {rid}">{rid}</span>
    <div class="ring-title">
      <h2>{rid} 环 · {html.escape(r['name'])}</h2>
      <span class="ring-ctrl">{html.escape(meta['ctrl'])}</span>
    </div>
    <span class="ring-tag-mono">{meta['tag']}</span>
  </div>
  <div class="ring-loc"><strong>控制部件：</strong>{bold(r['loc'])}</div>
  <h3>核心控制概念</h3>
  <table><thead><tr><th>概念</th><th>KT</th><th>一句话</th><th>Agent 承载</th></tr></thead><tbody>{concept_rows}</tbody></table>
  {'<h3>Agent 映射（控制概念→Agent 实现）</h3><ul>'+mapping_html+'</ul>' if mapping_html else ''}
  {'<h3>关键工程决策</h3><ul>'+dec_html+'</ul>' if dec_html else ''}
  {'<h3>设计范式</h3><div class="paradigm"><ul>'+para_html+'</ul></div>' if para_html else ''}
</div>""")
    # Hero
    hero = """
<div class="signal">
  <div class="signal-head"><span class="label">System Loop · 五环构成一个 Agent 控制回路</span><span class="tag">FRAMEWORK</span></div>
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
<span class="kicker">Framework · 五环映射框架</span>
<h1 class="display">五大核心环，构成一个<br>Agent 控制回路。</h1>
<p class="lead">E 决定反馈信号质量 → R 决定纠偏量 → P/T 决定轨迹 → M 决定"我以为我在哪"。任一环失效，闭环即破。</p>
<div class="insight"><strong>上下文（Core）</strong>：五环不是五个孤立 map，而是一条闭环信号链——把 Agent 当作被控系统，控制理论是它的建模语言。</div>
"""
    return hero + "".join(cards)
