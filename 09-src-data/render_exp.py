# -*- coding: utf-8 -*-
"""exp 实验记录专用渲染器 - 每个实验渲染为设计卡片，风格与 case/framework 统一
结构: 顶部实验摘要卡(signal) + 每个实验一个卡片(设计/执行/观测/量化/控制论 5 字段框)
"""
import re, html, sys
sys.stdout.reconfigure(encoding='utf-8')

def inline(text):
    t = html.escape(text)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    return t

def parse_exp(md):
    """返回 {title, meta:[], exps:[{num,name,fields:{key:[items]}}]}
    兼容两种结构:
      A. opencode型: ## 实验N: 名称 + **实验设计/执行数据/观测结果/量化指标/控制论解读**
      B. 场景型:     ### 场景N: 名称(或 ## 场景N) + - 注入点/触发行为/控制论/回滚
    """
    lines = md.split('\n')
    title = lines[0].lstrip('# ').strip() if lines else ''
    meta = []
    for l in lines[1:10]:
        if l.strip().startswith('>'):
            meta.append(l.strip().lstrip('>').strip())
    exp = None; exps = []; cur_field = None
    for line in lines:
        s = line.strip()
        # 实验/场景标题 (## 实验N 或 ### 场景N) - 排除 设计框架/源码证据/结论
        m = re.match(r'^#{2,3}\s*(实验|场景)\s*(\d+)?[^\n：:]*[：:]?\s*(.*)$', line)
        if m and not any(kw in m.group(0) for kw in ['实验设计框架','各场景源码证据','标准实验组结论','控制论结论']):
            if exp: exps.append(exp)
            head = m.group(1)+(''+m.group(2) if m.group(2) else '')
            name = m.group(3).strip()
            exp = {'num':head,'name':name,'fields':{}}
            cur_field = None
            continue
        if exp is None: continue
        # 字段匹配: 支持 "- **注入点**：" 和 "**实验设计**："
        body = re.sub(r'^[-*]\s+', '', s)   # 剥列表前缀
        mf = re.match(r'^\*\*(.+?)\*\*\s*[：:]\s*(.*)$', body)
        if mf:
            cur_field = mf.group(1).strip()
            exp['fields'].setdefault(cur_field, [])
            if mf.group(2).strip():
                exp['fields'][cur_field].append(mf.group(2).strip())
            continue
        # 裸列表项(非 **字段** 前缀) → 收集到"关键证据"
        if s.startswith('- ') and not s.startswith('**'):
            exp['fields'].setdefault('关键证据', [])
            exp['fields']['关键证据'].append(s.lstrip('- ').strip())
            cur_field = '关键证据'
            continue
        # 字段内的列表项/承接
        if cur_field and s:
            if s.startswith('- '):
                exp['fields'][cur_field].append(s.lstrip('- ').strip())
            elif s.startswith('|'):
                exp['fields'][cur_field].append(s)
            elif not s.startswith(('---','**','###','##')):
                if exp['fields'][cur_field]:
                    exp['fields'][cur_field][-1] += ' ' + s
    if exp: exps.append(exp)
    return title, meta, exps

FIELD_COLOR = {
  '实验设计':'#1E5AA8','执行数据':'#5B4B9B','观测结果':'#1F7A52',
  '量化指标':'#C77700','控制论解读':'#B23A2F',
}

def render_exp(md, product):
    title, meta, exps = parse_exp(md)
    # 顶部摘要卡
    meta_html = ''.join(f'<div class="exp-meta">{inline(x)}</div>' for x in meta)
    head = f"""
<div class="signal">
  <div class="signal-head"><span class="label">Experiment · 标准实验组</span><span class="tag">{product}</span></div>
  <span class="kicker" style="font-family:var(--font-mono);letter-spacing:.12em;color:#7E8CA5;font-size:11px">EXPERIMENT</span>
  <h1 style="font-size:26px;margin:8px 0 12px;color:#fff;letter-spacing:-.02em">{inline(title)}</h1>
  <div class="exp-meta-list">{meta_html}</div>
</div>
"""
    cards = []
    for e in exps:
        fields_html = ''
        if e['fields']:
            for key, items in e['fields'].items():
                color = FIELD_COLOR.get(key, '#1E5AA8')
                if items and items[0].startswith('|'):
                    # 表格字段
                    fields_html += f'<div class="exp-field"><div class="exp-field-tag" style="border-color:{color};color:{color}">{key}</div>{inline("".join(items[:1]))}</div>'
                else:
                    items_html = ''.join(f'<li>{inline(x)}</li>' for x in items if x)
                    fields_html += f'<div class="exp-field"><div class="exp-field-tag" style="border-color:{color};color:{color}">{key}</div><ul>{items_html}</ul></div>'
        cards.append(f"""
<div class="ring-section exp-card">
  <div class="ring-head">
    <span class="ring-tag" style="background:#1E5AA8">{e['num'].replace('实验','').strip()}</span>
    <div class="ring-title"><h2>{inline(e['num'] + ' ' + e['name'])}</h2></div>
  </div>
  {fields_html}
</div>""")
    body = head + "".join(cards)
    return body
