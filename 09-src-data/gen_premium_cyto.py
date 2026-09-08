# -*- coding: utf-8 -*-
"""生成精装房 DAG 交互图 premium-cyto.html
节点=14 产品（精装度着色 + 一手/二手形状）；分类=4大类（分组框）；边=产品→分类归属 + 声称vs实际标注
"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = "/home/zako-mio/opencode/archive/Mission-file/2026-09/0907-控制理论Agent设计知识库"
sys.path.insert(0, os.path.join(BASE, "09-src-data"))
import nav_data as nd
import premium_scores as ps

# 精装度色阶（与模型一致）
score_color = ps.score_color

# 分类色
CAT_COLOR = {
    '第一方成品': '#1E5AA8',
    '低代码平台': '#5B4B9B',
    '开源成品化': '#1F7A52',
    '二次封装': '#C77700',
}

# 产品数据 (slug, 名称, 厂商, 精装度, 一手二手, 大类, 证据级, 结论)
# 分值来自 09-src-data/premium_scores.py（硬门槛+8维加权+一票否决），禁止硬编码
PRODUCTS = [
    (p["slug"], p["name"], p["vendor"], ps.final(p["slug"]),
     p["hand"], p["cat"], p["ev"], p["note"])
    for p in ps.PRODUCTS
]

elements = []
# 分类组节点（作为锚点）
cats = {}
for p in PRODUCTS:
    cats.setdefault(p[5], []).append(p)

cat_node_ids = {}
for i,(cat, rows) in enumerate(cats.items()):
    cid = f"cat_{i}"
    cat_node_ids[cat] = cid
    elements.append({"data":{"id":cid,"kind":"cat","label":f"{cat}\n({len(rows)})","color":CAT_COLOR.get(cat,'#334155')}})

# 产品节点
for slug,name,vendor,score,hand,cat,ev,note in PRODUCTS:
    elements.append({"data":{
        "id":f"p_{slug}","kind":"product","label":f"{name}\n{ps.fmt(score)}","color":score_color(score),
        "hand":hand,"cat":cat,"score":score,"vendor":vendor,"ev":ev,"note":note,"slug":slug
    }})
    # 边：产品 → 所属分类
    elements.append({"data":{"id":f"e_{slug}_{cat_node_ids[cat]}","source":f"p_{slug}","target":cat_node_ids[cat],"kind":"belong"}})

# 声称vs实际标注边（关键案例）
CLAIM_EDGES = [
    ("ccrouter","二手被高估：声称增强Claude Code，实依赖@the-next-ai网关"),
    ("qcode","二手被高估：声称平替，实为官价×倍率中转"),
    ("codewhale","一手被低估：声称平替，实为自研Rust底层"),
    ("openclaude","一手被低估：声称替代，实为独立TS实现"),
    ("windsurf","声称功能不存在：无Flows DAG"),
]
for slug, label in CLAIM_EDGES:
    elements.append({"data":{"id":f"flag_{slug}","kind":"flag","label":label,"source":f"p_{slug}","target":cat_node_ids[PRODUCTS[[p[0] for p in PRODUCTS].index(slug)][5]]}})

HTML = """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>精装房 DAG — 控制理论⊗Agent知识库</title>
<link rel="stylesheet" href="assets/design-tokens.css">
<style>
  .cy-shell{display:flex;min-height:100vh;flex-direction:column}
  .cy-toolbar{display:flex;align-items:center;gap:14px;padding:0 var(--space-5);height:48px;border-bottom:1px solid var(--line);background:var(--panel)}
  .cy-toolbar .lab{font-family:var(--font-mono);font-size:11px;color:var(--signal-amber);letter-spacing:.1em}
  #cy{flex:1;min-height:600px;position:relative;background:var(--panel)}
  .info-panel{position:absolute;right:16px;top:16px;width:340px;max-height:calc(100% - 40px);background:rgba(255,255,255,.98);border:1px solid var(--line);border-radius:var(--r-md);padding:var(--space-4);overflow-y:auto;display:none;box-shadow:0 6px 24px rgba(11,18,32,.12)}
  .info-panel .ip-close{cursor:pointer;color:var(--muted);float:right;font-size:18px;line-height:1}
  .info-panel h4{color:var(--ink);margin-bottom:6px;font-size:16px}
  .info-panel .ip-kt{font-family:var(--font-mono);font-size:11px;color:var(--signal-amber);margin-bottom:8px}
  .info-panel .ip-def{font-size:13px;color:var(--muted);line-height:1.6}
  .info-panel .ip-agent{margin-top:10px;padding-top:10px;border-top:1px solid var(--line);font-size:13px}
  .info-panel .ip-agent a{color:var(--ctrl-blue);font-weight:600}
  .cy-legend{display:flex;gap:var(--space-3);flex-wrap:wrap;padding:10px var(--space-5);border-top:1px solid var(--line);background:var(--panel)}
  .cy-legend span{display:flex;align-items:center;gap:5px;font-size:12px;color:var(--muted)}
  .cy-legend i{width:11px;height:11px;border-radius:3px;display:inline-block}
  body{overflow:hidden}
</style></head>
<body>
<div class="shell">
__SIDEBAR__
<div class="main">
  <div class="main-topbar"><div class="crumb"><b>精装房 DAG</b> · 14 产品 × 精装度 × 一手/二手（点击查看）</div></div>
  <div class="cy-toolbar">
    <span class="lab">PREMIUM-HOUSING / 14 PRODUCTS</span>
    <span style="color:var(--muted);font-size:12px">精装度着色：绿(≥4.5)/金(3.5-4.5)/红(&lt;3.5) · 形状：矩形=一手 / 菱形=二手 · 虚线=声称vs实际标注</span>
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
    <span><i style="background:#1F7A52"></i>精装度 ≥4.5</span>
    <span><i style="background:#C77700"></i>精装度 3.5-4.5</span>
    <span><i style="background:#B23A2F"></i>精装度 &lt;3.5</span>
    <span><i style="background:#1E5AA8"></i>第一方成品</span>
    <span><i style="background:#5B4B9B"></i>低代码平台</span>
    <span><i style="background:#1F7A52"></i>开源成品化</span>
    <span><i style="background:#C77700"></i>二次封装</span>
  </div>
  <footer class="footer"><span>控制理论 ⊗ Agent 设计知识库 · v1.2 自改造 opencode 变体版（6 框架 + 14 精装房 + opencode-custom）</span><span class="fbrand">data: 09-src-data · contract: 00-contract</span></footer>
</div>
</div>
<script src="vendor/cytoscape.min.js"></script>
<script src="vendor/cytoscape-dagre.min.js"></script>
<script>
const ELEMENTS = __ELEMENTS__;
let cy;
function initCy(){
  cy = cytoscape({
    container: document.getElementById('cy'),
    elements: ELEMENTS,
    style: [
      { selector:'node', style:{
        'label':'data(label)','background-color':'data(color)','color':'#fff',
        'text-valign':'center','text-halign':'center','font-size':'11','font-weight':'600',
        'text-wrap':'wrap','text-max-width':'100','border-width':'1.5','border-color':'#fff',
        'shape':'round-rectangle'
      }},
      { selector:'node[kind="cat"]', style:{
        'width':'130','height':'54','font-size':'12','font-weight':'700','shape':'round-rectangle',
        'background-opacity':'0.92','border-width':'2','border-color':'#fff'
      }},
      { selector:'node[kind="product"]', style:{'width':'104','height':'46','font-size':'10'}},
      { selector:'node[kind="product"][hand="二手"]', style:{'shape':'diamond','width':'118','height':'70'}},
      { selector:'edge', style:{
        'width':'1.3','line-color':'#A8B3C7','target-arrow-color':'#A8B3C7',
        'target-arrow-shape':'triangle','curve-style':'bezier',
        'font-size':'8','color':'#8794A8','text-rotation':'autorotate',
        'text-background-color':'#fff','text-background-opacity':'0.9','text-wrap':'wrap','text-max-width':'130'
      }},
      { selector:'edge[kind="flag"]', style:{
        'line-style':'dashed','line-color':'#B23A2F','target-arrow-color':'#B23A2F',
        'width':'1.6','label':'data(label)','color':'#B23A2F'
      }},
    ],
    layout:{name:'dagre',rankDir:'RL',spacingFactor:1.1,nodeSep:28,edgeSep:14,rankSep:150},
    wheelSensitivity:0.2,
  });
  cy.on('tap','node', evt=>{
    const d = evt.target.data();
    if(d.kind==='cat'){
      document.getElementById('ipTitle').textContent = d.label.replace('\\n',' ');
      document.getElementById('ipKt').textContent = '分类';
      document.getElementById('ipDef').textContent = '该分类下的精装房产品（点击产品节点查看详情）';
      document.getElementById('ipAgent').innerHTML = '—';
    } else if(d.kind==='product'){
      document.getElementById('ipTitle').textContent = d.label.replace('\\n',' · ');
      document.getElementById('ipKt').textContent = d.cat + ' · ' + d.hand + ' · 精装度 ' + d.score + ' · ' + d.ev;
      document.getElementById('ipDef').textContent = d.vendor + ' — ' + d.note;
      document.getElementById('ipAgent').innerHTML = '<a href="premium-'+d.slug+'.html">查看完整画像 →</a>';
    }
    document.getElementById('infoPanel').style.display='block';
  });
}
function closeInfo(){ document.getElementById('infoPanel').style.display='none'; }
window.__cy = cy;
document.addEventListener('DOMContentLoaded', initCy);
</script></body></html>
"""

elements_js = json.dumps(elements, ensure_ascii=False)
HTML = HTML.replace("__ELEMENTS__", elements_js)

# 注入统一 sidebar
sidebar = f"""<aside class="sidebar">
 {nd.sidebar_brand()}
 <nav class="sidebar-nav">{nd.sidebar_nav('premium-cyto', is_root=False)}
 </nav>
</aside>"""
HTML = HTML.replace("__SIDEBAR__", sidebar)

out = os.path.join(BASE,"04-interactive","premium-cyto.html")
with open(out,"w",encoding="utf-8") as f:
    f.write(HTML)
print("OK 生成精装房 DAG 页:", out, "节点/边:", len(elements))
