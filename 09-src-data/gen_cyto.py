# -*- coding: utf-8 -*-
"""重新构建交互 DAG 页 index_cyto.html - 新设计系统配色"""
import json, os, sys, html
sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ★ 本地化：仓库根由本文件位置推导（⛔ 不硬编码作者机路径）
dag = json.load(open(os.path.join(BASE,"09-src-data/five-ring-dag.json"),encoding="utf-8"))
kt = json.load(open(os.path.join(BASE,"09-src-data/kt_details.json"),encoding="utf-8"))

# 五环新语义色
RING_COLOR = {'E':'#B23A2F','R':'#C77700','M':'#1F7A52','P':'#1E5AA8','T':'#5B4B9B'}
# 边缘/结构
EDGE_COLOR = '#A8B3C7'

def colored_concepts():
    return dag['concepts']

# 生成 cyto 元素
elements = []
for r in dag['rings']:
    elements.append({"data":{"id":r['id'],"kind":"ring","label":r['short']+" "+r['label'],"ctrl":r['ctrl']}})
for c in dag['concepts']:
    elements.append({"data":{"id":c['id'],"kind":"concept","label":c['label'],"ring":c['ring']}})
for e in dag['edges']:
    if e['source']==e['target']: continue
    elements.append({"data":{"id":f"e_{e['source']}_{e['target']}","source":e['source'],"target":e['target'],"kind":e['kind'],"label":e.get('label','')}})

def color_of(node):
    d = node['data']
    if d['kind']=='ring': return RING_COLOR[d['id']]
    return RING_COLOR.get(d.get('ring'),'#334155')

HTML = """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>交互 DAG 总览 — 控制理论⊗Agent知识库</title>
<link rel="stylesheet" href="assets/derived-design-tokens.css"><link rel="stylesheet" href="assets/site.css">
<style>
  .cy-shell{display:flex;min-height:100vh;flex-direction:column}
  .cy-toolbar{display:flex;align-items:center;gap:14px;padding:0 var(--space-5);height:48px;border-bottom:1px solid var(--line);background:var(--panel)}
  .cy-toolbar .lab{font-family:var(--font-mono);font-size:11px;color:var(--signal-amber);letter-spacing:.1em}
  #cy{flex:1;min-height:560px;position:relative;background:var(--panel)}
  .info-panel{position:absolute;right:16px;top:16px;width:320px;max-height:calc(100% - 40px);background:rgba(255,255,255,.98);border:1px solid var(--line);border-radius:var(--r-md);padding:var(--space-4);overflow-y:auto;display:none;box-shadow:0 6px 24px rgba(11,18,32,.12)}
  .info-panel .ip-close{cursor:pointer;color:var(--muted);float:right;font-size:18px;line-height:1}
  .info-panel h4{color:var(--ink);margin-bottom:6px;font-size:16px}
  .info-panel .ip-kt{font-family:var(--font-mono);font-size:11px;color:var(--signal-amber);margin-bottom:8px}
  .info-panel .ip-def{font-size:13px;color:var(--muted);line-height:1.6}
  .info-panel .ip-agent{margin-top:10px;padding-top:10px;border-top:1px solid var(--line);font-size:13px}
  .info-panel .ip-agent b{color:var(--ctrl-blue)}
  .cy-legend{display:flex;gap:var(--space-3);flex-wrap:wrap;padding:10px var(--space-5);border-top:1px solid var(--line);background:var(--panel)}
  .cy-legend span{display:flex;align-items:center;gap:5px;font-size:12px;color:var(--muted)}
  .cy-legend i{width:11px;height:11px;border-radius:3px;display:inline-block}
  body{overflow:hidden}
</style></head>
<body>
<div class="cy-shell">
  <div class="main-topbar"><div class="crumb"><b>交互 DAG 总览</b> · 五环 × 控制概念（点击下钻）</div></div>
  <div class="cy-toolbar">
    <span class="lab">SYSTEM-LOOP / 5 RINGS × 28 CONCEPTS</span>
    <span style="color:var(--muted);font-size:12px">E→R→M→P→T 闭环 · 点击节点查看控制概念</span>
  </div>
  <div id="cy">
    <div class="info-panel" id="infoPanel">
      <span class="ip-close" onclick="closeInfo()">✕</span>
      <h4 id="ipTitle">节点</h4>
      <div class="ip-kt" id="ipKt">—</div>
      <div class="ip-def" id="ipDef">—</div>
      <div class="ip-agent" id="ipAgent">—</div>
    </div>
  </div>
  <div class="cy-legend">
    <span><i style="background:#1E5AA8"></i>P 规划</span>
    <span><i style="background:#5B4B9B"></i>T 执行</span>
    <span><i style="background:#B23A2F"></i>E 评估</span>
    <span><i style="background:#1F7A52"></i>M 记忆</span>
    <span><i style="background:#C77700"></i>R 反思</span>
  </div>
</div>
<script src="vendor/cytoscape.min.js"></script>
<script src="vendor/cytoscape-dagre.min.js"></script>
<script>
const ELEMENTS = __ELEMENTS__;
const RING_COLOR = __RING_COLOR__;
const KT = __KT__;
const RING_DESC = {
  'E':'输出反馈信号 y，其信噪比决定整个闭环能走多远 · 最易被低估却最致命',
  'R':'计算误差 e=r−y，生成修正量回灌 · P(即时)/I(累积)/D(预判)三通道',
  'M':'从带噪观测估计内部状态 · 保真推断信念+显式置信度',
  'P':'慢速上层策略控制器 · 任务分解+里程碑+滚动重规划',
  'T':'执行器+安全阀+仲裁 · 限幅/冗余/看门狗，唯一触碰外界',
};
let cy;
function initCy(){
  cy = cytoscape({
    container: document.getElementById('cy'),
    elements: ELEMENTS,
    style: [
      { selector:'node', style:{
        'label':'data(label)','background-color':'data(color)','color':'#fff',
        'text-valign':'center','text-halign':'center','font-size':'10','font-weight':'600',
        'text-wrap':'wrap','text-max-width':'110','border-width':'1.5','border-color':'#fff',
        'shape':'round-rectangle'
      }},
      { selector:'node[kind="ring"]', style:{'width':'128','height':'44','font-size':'12','font-weight':'700'}},
      { selector:'node[kind="concept"]', style:{'width':'112','height':'34','font-size':'9.5','opacity':'0.92'}},
      { selector:'edge', style:{
        'width':'1.5','line-color':__EDGE_COLOR__,'target-arrow-color':__EDGE_COLOR__,
        'target-arrow-shape':'triangle','curve-style':'bezier','label':'data(label)',
        'font-size':'8','color':'#8794A8','text-rotation':'autorotate','text-background-color':'#fff','text-background-opacity':'0.85'
      }},
      { selector:'edge[kind="feedback"]', style:{'line-style':'dashed','line-color':__RING_R__}},
    ],
    layout:{name:'dagre',rankDir:'LR',spacingFactor:1.15,nodeSep:24,edgeSep:12,rankSep:130},
    wheelSensitivity:0.2,
  });
  cy.on('tap','node', evt=>{
    const d = evt.target.data();
    if(d.kind==='ring'){
      document.getElementById('ipTitle').textContent = d.label;
      document.getElementById('ipKt').textContent = '控制部件: '+(d.ctrl||'');
      document.getElementById('ipDef').textContent = RING_DESC[d.id]||'';
      document.getElementById('ipAgent').innerHTML = '点击同色概念节点查看该环控制论概念';
      document.getElementById('infoPanel').style.display='block';
    } else {
      const det = KT[d.id]||{};
      document.getElementById('ipTitle').textContent = d.label;
      document.getElementById('ipKt').textContent = 'KT: '+d.id+' · 归属 '+d.ring+' 环';
      document.getElementById('ipDef').textContent = det.definition||'—';
      document.getElementById('ipAgent').innerHTML = det.agent_mapping ? '<b>Agent 映射：</b>'+det.agent_mapping : '—';
      document.getElementById('infoPanel').style.display='block';
    }
  });
}
function closeInfo(){ document.getElementById('infoPanel').style.display='none'; }
window.__cy = cy;
document.addEventListener('DOMContentLoaded', initCy);
</script></body></html>
"""

# 注入数据
elements_js = json.dumps(elements, ensure_ascii=False)
# 给每个节点注入 color 字段
for el in elements:
    el["data"]["color"] = color_of(el)
elements_js = json.dumps(elements, ensure_ascii=False)
HTML = HTML.replace("__ELEMENTS__", elements_js)
HTML = HTML.replace("__RING_COLOR__", json.dumps(RING_COLOR, ensure_ascii=False))
HTML = HTML.replace("__KT__", json.dumps(kt, ensure_ascii=False))
HTML = HTML.replace("__EDGE_COLOR__", json.dumps(EDGE_COLOR))
HTML = HTML.replace("__RING_R__", json.dumps(RING_COLOR['R']))

out = os.path.join(BASE,"04-interactive","index_cyto.html")
with open(out,"w",encoding="utf-8") as f:
    f.write(HTML)
print("OK 重建交互 DAG 页:", out)
print("注入: %d 节点(elements) + %d KT详情, 无占位符残留=%s" % (len(elements), len(kt), "__INJECT" not in HTML and "__ELEMENTS__" not in HTML and "__KT__" not in HTML))
