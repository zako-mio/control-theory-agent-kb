# -*- coding: utf-8 -*-
"""case 画像专用渲染器 - 把产品控制论画像 MD 渲染为优质 HTML
结构: 顶部摘要卡(产品/整体范式/最强/最弱环) + 每环画像卡片(承担角色/关键机制/映射/强弱项)
"""
import re, html, sys, json, os
sys.stdout.reconfigure(encoding='utf-8')

def inline(text):
    t = html.escape(text)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    return t

# 环强弱 meta (用于卡片色与强弱标记)
RING_META = {
  'SP': {'id':'SP','color':'#1E5AA8','tag':'Setpoint','desc':'用户意图 → 可验证子目标'},
  'E': {'id':'E','color':'#B23A2F','tag':'Sensor','desc':'评估/传感器'},
  'T': {'id':'T','color':'#5B4B9B','tag':'Actuator','desc':'工具调用/执行器'},
  'M': {'id':'M','color':'#1F7A52','tag':'Estimator','desc':'记忆/状态估计'},
  'P': {'id':'P','color':'#1E5AA8','tag':'Planner','desc':'规划/分层控制'},
  'R': {'id':'R','color':'#C77700','tag':'Feedback','desc':'反思/反馈闭环'},
}

def parse_case(md, product):
    """返回 {title, blocks:[{head, ring_id, role, mech:[], mapping, sw}]}"""
    lines = md.split('\n')
    title_line = md.split('\n')[0].lstrip('# ').strip() if md else ''
    blocks = []
    cur = None
    for line in lines:
        m = re.match(r'^## (\d+)\.\s*(.+)$', line)
        if m:
            if cur: blocks.append(cur)
            num = m.group(1); name = m.group(2).strip()
            # 跳过非环章节(前置/总览/总结/总评/表)
            if any(kw in name for kw in ['前置定位','一图总览','画像总结','控制论画像总结','强弱总评','实验设计流程','实验设计','标准实验组','各场景']):
                cur = None
                continue
            cur = {'num':num,'title':name,'role':'','mech':[],'mapping':'','sw':''}
            continue
        if not cur: continue
        s = line.strip()
        if s.startswith('**承担角色**'):
            cur['role'] = s.replace('**承担角色**','').strip().lstrip('：:').strip()
        elif s.startswith('**控制论映射**'):
            cur['mapping'] = s.replace('**控制论映射**','').strip().lstrip('：:').strip()
        elif s.startswith('**强弱项**'):
            cur['sw'] = s.replace('**强弱项**','').strip().lstrip('：:').strip()
        elif line.lstrip().startswith('###') or line.startswith('# '):
            pass
        # 机制列表项: 支持无序(- ) 和有序(1. 2.)/嵌套, 含空行/换行承接
        elif s and (re.match(r'^[-*]\s+', s) or re.match(r'^\d+[\.\)]\s+', s)):
            if s.startswith(('**关键机制**','**承担角色**','**控制论映射**','**强弱项**')): continue
            txt = re.sub(r'^[-*\d\.\)]+\s+', '', s).strip()
            if txt:
                cur['mech'].append(txt)
        elif s and not line.startswith('---'):
            # 非空非标记行: 若在承担角色后/机制后, 可能是承接内容
            # 简单处理: 如果当前字段尚未有内容且是段落, 追加到 role 或最后一个 mech
            if cur['mech'] and not s.startswith(('**','|','```')):
                cur['mech'][-1] += ' ' + s
            elif not cur['role']:
                cur['role'] = s
    if cur: blocks.append(cur)
    # 过滤: 只保留能映射到环的
    blocks = [b for b in blocks if map_ring_id(b['title']) is not None]
    return title_line, blocks

def map_ring_id(title):
    """从环标题识别环 id。返回 'E','T','M','P','R','SP'(设定值) 或 None"""
    # 优先匹配括号内的环标记: (E 环) / （T 环） / (T环)
    m = re.search(r'[（(]\s*([ETMPR])\s*环', title)
    if m:
        return m.group(1)
    # 开头 E 环 / T 环
    m = re.match(r'^([ETMPR])\s*环', title)
    if m:
        return m.group(1)
    # S 环 (claude-code 用 S 环表示设定值)
    if 'S 环' in title or 'S环' in title:
        return 'SP'
    if '设定值' in title or 'Setpoint' in title or 'SP' in title:
        return 'SP'
    return None

def parse_premium(md):
    """解析精装房画像的「0. 精装度评估」章节。返回 {meta, score, reason, table_rows, claim} 或 None"""
    m = re.search(r'##\s*0\.\s*精装度评估.*?\n(.*?)(?=\n##\s|\Z)', md, re.S)
    if not m:
        return None
    sec = m.group(1)
    # 元信息行（> 定位：... 精装度：X/5 ...）
    meta = {}
    for line in md.split('\n'):
        if line.startswith('>') and ('精装度' in line or '定位' in line):
            for key in ['定位','厂商','分类','审计日期','精装度','一手/二手','证据强度']:
                mm = re.search(re.escape(key) + r'[：:]\s*([^｜|\n]+)', line)
                if mm:
                    meta[key] = mm.group(1).strip().rstrip('　').strip()
    score_m = re.search(r'\*\*综合评分\*\*[：:]\s*([0-9.]+/5)\s*[—-]\s*(.*)', sec)
    score = score_m.group(1) if score_m else (meta.get('精装度',''))
    reason = score_m.group(2).strip() if score_m else ''
    # 预装能力表
    rows = []
    for line in sec.split('\n'):
        s = line.strip()
        if not s.startswith('|'): continue
        if re.match(r'^\|[\s:\-|]+\|$', s): continue
        cells = [c.strip() for c in s.strip('|').split('|')]
        if len(cells) >= 3 and cells[0] != '维度':
            rows.append(cells)
    # 声称 vs 实际
    claim_m = re.search(r'\*\*声称\s*vs\s*实际\*\*[：:]\s*(.*?)(?=\n\n|\Z)', sec, re.S)
    claim = claim_m.group(1).strip() if claim_m else ''
    return {'meta':meta,'score':score,'reason':reason,'rows':rows,'claim':claim}


def render_premium_block(md):
    """渲染精装度评估区块（含评分卡+预装能力表+声称vs实际）"""
    p = parse_premium(md)
    if not p:
        return ''
    meta = p['meta']
    # 评分色：>=4.5 绿, >=3.5 金, else 红
    try:
        sc = float(p['score'].split('/')[0])
    except Exception:
        sc = 0
    color = '#1F7A52' if sc >= 4.5 else ('#C77700' if sc >= 3.5 else '#B23A2F')
    chips = []
    for k in ['分类','一手/二手','证据强度']:
        if meta.get(k):
            chips.append(f'<span class="prem-chip">{k}：{inline(meta[k])}</span>')
    rows_html = ''
    if p['rows']:
        trs = []
        for r in p['rows']:
            status = r[1] if len(r) > 1 else ''
            cls = 'ok' if '✅' in status else ('part' if '部分' in status else ('no' if '✖' in status else ''))
            trs.append(f'<tr><td>{inline(r[0])}</td><td class="prem-{cls}">{inline(status)}</td><td class="prem-ev">{inline(r[2]) if len(r)>2 else ""}</td></tr>')
        rows_html = f'<table class="prem-table"><thead><tr><th>维度</th><th>预装情况</th><th>依据</th></tr></thead><tbody>{"".join(trs)}</tbody></table>'
    claim_html = ''
    if p['claim']:
        claim_html = f'<div class="prem-claim"><strong>声称 vs 实际：</strong>{inline(p["claim"])}</div>'
    return f"""
<div class="ring-section premium-block" id="premium-score">
  <div class="ring-head">
    <span class="ring-tag" style="background:{color}">装</span>
    <div class="ring-title"><h2>精装度评估</h2><span class="ring-ctrl">Premium Score</span></div>
  </div>
  <div class="prem-scorecard">
    <div class="prem-score" style="color:{color}">{inline(p['score'])}</div>
    <div class="prem-reason">{inline(p['reason'])}</div>
  </div>
  <div class="prem-chips">{''.join(chips)}</div>
  {rows_html}
  {claim_html}
</div>"""


def render_case(md, product):
    title, blocks = parse_case(md, product)
    cards = []
    ordered = []
    for b in blocks:
        rid = map_ring_id(b['title'])
        meta = RING_META[rid]
        mech_html = ''.join(f"<li>{inline(x)}</li>" for x in b['mech'] if x and not x.startswith('##') and not x.startswith('---'))
        sw_html = ''
        if b['sw']:
            sw_html = f"<div class='ring-sw'>{inline(b['sw'])}</div>"
        cards.append(f"""
<div class="ring-section" id="ring-{meta['id']}">
  <div class="ring-head">
    <span class="ring-tag" style="background:{meta['color']}">{meta['id']}</span>
    <div class="ring-title"><h2>{inline(b['title'])}</h2><span class="ring-ctrl">{meta['desc']}</span></div>
  </div>
  <div class="ring-loc"><strong>承担角色：</strong>{inline(b['role'])}</div>
  {'<h3>关键机制</h3><ul>'+mech_html+'</ul>' if mech_html else ''}
  {'<div class="mapping-box"><strong>控制论映射：</strong>'+inline(b['mapping'])+'</div>' if b['mapping'] else ''}
  {sw_html}
</div>""")
        ordered.append(rid)

    # 顶部摘要卡
    summary_card = f"""
<div class="signal">
  <div class="signal-head"><span class="label">Product Portrait · 控制论画像</span><span class="tag">{product}</span></div>
  <span class="kicker" style="font-family:var(--font-mono);letter-spacing:.12em;color:#7E8CA5;font-size:11px">CASE</span>
  <h1 style="font-size:26px;margin:8px 0 10px;color:#fff;letter-spacing:-.02em">{inline(title)}</h1>
  <p style="color:#CBD4E2;max-width:720px;line-height:1.7;font-size:15px;margin:0">{inline(blocks[0]['role'][:220] if blocks else '')}</p>
</div>
"""

    # 七大核心环强弱总评表 + 画像总结
    total_html = ''
    summary_block = ''
    mt = re.search(r'## [^\n]*总评\s*\n(.*?)(?=\n## |\Z)', md, re.S)
    if mt:
        rows=[]
        for line in mt.group(1).split('\n'):
            s=line.strip()
            if not s.startswith('|'): continue
            if re.match(r'^\|[\s:\-|]+\|$', s): continue
            cells=[inline(c.strip()) for c in s.strip('|').split('|')]
            if len(cells)>=3:
                rows.append(cells)
        # 去掉表头(cells[0] 含 '环')
        if rows and ('环' in rows[0][0]): rows=rows[1:]
        if rows:
            thead='<tr><th>环</th><th>承担角色</th><th>强度</th><th>主控概念</th></tr>'
            tbody=''.join(f'<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3] if len(r)>3 else ""}</td></tr>' for r in rows)
            total_html=f'<div class="ring-section"><div class="ring-head"><span class="ring-tag" style="background:#1E5AA8">Σ</span><div class="ring-title"><h2>七大核心环强弱总评</h2></div></div><div style="overflow-x:auto"><table><thead>{thead}</thead><tbody>{tbody}</tbody></table></div></div>'
    ms = re.search(r'## [^\n]*画像总结\s*\n(.*?)(?=\n## |\Z)', md, re.S)
    if ms:
        lines=[l.strip() for l in ms.group(1).split('\n') if l.strip()]
        lead = inline(lines[0]) if lines else ''
        rest=''.join(f'<li>{inline(x.lstrip("- ").strip())}</li>' for x in lines[1:] if x.startswith('-') and x.lstrip("- ").strip())
        summary_block=f"""
<div class="ring-section summary-block">
  <div class="ring-head"><span class="ring-tag" style="background:#C77700">★</span><div class="ring-title"><h2>控制论画像总结</h2></div></div>
  <div class="case-verdict"><strong>整体范式：</strong>{lead}</div>
  {'<ul>'+rest+'</ul>' if rest else ''}
</div>"""

    premium_html = render_premium_block(md)
    body = summary_card + premium_html + "".join(cards) + total_html + summary_block
    return body
