# -*- coding: utf-8 -*-
"""给 index_cyto.html 注入统一 sidebar 导航(与全站一致)"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '/home/zako-mio/opencode/archive/Mission-file/2026-09/0907-控制理论Agent设计知识库/09-src-data')
import nav_data as nd
p = '/home/zako-mio/opencode/archive/Mission-file/2026-09/0907-控制理论Agent设计知识库/04-interactive/index_cyto.html'
c = open(p, encoding='utf-8').read()

# 生成统一 sidebar(active='index_cyto')
sidebar = f"""
<aside class="sidebar">
 {nd.sidebar_brand()}
 <nav class="sidebar-nav">{nd.sidebar_nav('index_cyto', is_root=False)}
 </nav>
</aside>"""

# 替换 cy-shell 外层为标准 shell
old_head = '''<div class="cy-shell">
  <div class="main-topbar"><div class="crumb"><b>交互 DAG 总览</b> · 五环 × 控制概念（点击下钻）</div></div>'''
new_head = f'''<div class="shell">
{sidebar}
<div class="main">
  <div class="main-topbar"><div class="crumb"><b>交互 DAG 总览</b> · 五环 × 控制概念（点击下钻）</div></div>'''
assert old_head in c, "未找到 cy-shell 头"
c = c.replace(old_head, new_head)

# 关闭: 把 cy-shell 的结尾 </div>(45行) 改为 .main 和 .shell 两个关闭
old_foot = '''  <div class="cy-legend">
    <span><i style="background:#1E5AA8"></i>P 规划</span>
    <span><i style="background:#5B4B9B"></i>T 执行</span>
    <span><i style="background:#B23A2F"></i>E 评估</span>
    <span><i style="background:#1F7A52"></i>M 记忆</span>
    <span><i style="background:#C77700"></i>R 反思</span>
  </div>
</div>'''
new_foot = '''  <div class="cy-legend">
    <span><i style="background:#1E5AA8"></i>P 规划</span>
    <span><i style="background:#5B4B9B"></i>T 执行</span>
    <span><i style="background:#B23A2F"></i>E 评估</span>
    <span><i style="background:#1F7A52"></i>M 记忆</span>
    <span><i style="background:#C77700"></i>R 反思</span>
  </div>
  <footer class="footer"><span>控制理论 ⊗ Agent 设计知识库 · v1.3 自改造 opencode 变体版（6 框架 + 14 精装房 + opencode-custom）</span><span class="fbrand">data: 09-src-data · contract: 00-contract</span></footer>
</div>
</div>'''
assert old_foot in c, "未找到 cy-shell 尾"
c = c.replace(old_foot, new_foot)

# 若 cy-shell 的 CSS 定义影响布局, 保留但嵌套在 shell 内可兼容. main 需要 min-width.
open(p, 'w', encoding='utf-8').write(c)
print("OK 注入统一导航到 index_cyto")
print("含sidebar:", 'class="sidebar"' in c, "| 导航项:", c.count('class="mag"'), "| 门户入口:", '门户入口' in c)
