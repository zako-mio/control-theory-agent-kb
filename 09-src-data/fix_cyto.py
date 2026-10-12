# -*- coding: utf-8 -*-
"""给 index_cyto.html 注入统一 sidebar 导航(与全站一致) + 页脚版本同步

v1.5 起本脚本改为**幂等**：
  - 头/尾替换若已是目标形态（上次已注入）则跳过，⛔ 不再 assert 失败；
  - 页脚版本号一律同步为当前版本（`FOOTER_VER`），保证「生成脚本 + 生成物双轨零残留」。
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '/home/zako-mio/opencode/archive/Mission-file/2026-09/0907-控制理论Agent设计知识库/09-src-data')
import nav_data as nd

FOOTER_VER = "v1.5 dsh 装配层二次追平版"
OLD_FOOTER_VERS = [
    "v1.4 dsh 装配层 + opencode 月度追平版",
    "v1.4 装配层变体版",
    "v1.1 精装房全景版",
    "v1.0.0",
]

p = '/home/zako-mio/opencode/archive/Mission-file/2026-09/0907-控制理论Agent设计知识库/04-interactive/index_cyto.html'
c = open(p, encoding='utf-8').read()

# 生成统一 sidebar(active='index_cyto')
sidebar = f"""
<aside class="sidebar">
 {nd.sidebar_brand()}
 <nav class="sidebar-nav">{nd.sidebar_nav('index_cyto', is_root=False)}
 </nav>
</aside>"""

# --- 头部：cy-shell → shell（幂等） ---
old_head = '''<div class="cy-shell">
  <div class="main-topbar"><div class="crumb"><b>交互 DAG 总览</b> · 五环 × 控制概念（点击下钻）</div></div>'''
new_head = f'''<div class="shell">
{sidebar}
<div class="main">
  <div class="main-topbar"><div class="crumb"><b>交互 DAG 总览</b> · 五环 × 控制概念（点击下钻）</div></div>'''
if old_head in c:
    c = c.replace(old_head, new_head)
    head_action = "注入"
elif '<div class="shell">' in c and 'class="sidebar"' in c:
    head_action = "已注入（跳过）"
else:
    raise SystemExit("未找到 cy-shell 头，且非已注入形态 —— 请检查 index_cyto.html 来源")

# --- 尾部：关闭标签 + 统一页脚（幂等） ---
old_foot = '''  <div class="cy-legend">
    <span><i style="background:#1E5AA8"></i>P 规划</span>
    <span><i style="background:#5B4B9B"></i>T 执行</span>
    <span><i style="background:#B23A2F"></i>E 评估</span>
    <span><i style="background:#1F7A52"></i>M 记忆</span>
    <span><i style="background:#C77700"></i>R 反思</span>
  </div>
</div>'''
new_foot = f'''  <div class="cy-legend">
    <span><i style="background:#1E5AA8"></i>P 规划</span>
    <span><i style="background:#5B4B9B"></i>T 执行</span>
    <span><i style="background:#B23A2F"></i>E 评估</span>
    <span><i style="background:#1F7A52"></i>M 记忆</span>
    <span><i style="background:#C77700"></i>R 反思</span>
  </div>
  <footer class="footer"><span>控制理论 ⊗ Agent 设计知识库 · {FOOTER_VER}（6 框架 + 14 精装房 + opencode-custom + dsh-custom）</span><span class="fbrand">data: 09-src-data · contract: 00-contract</span></footer>
</div>
</div>'''
if old_foot in c:
    c = c.replace(old_foot, new_foot)
    foot_action = "注入"
else:
    foot_action = "已注入（跳过）"

# --- 页脚版本同步（双轨零残留） ---
ver_synced = 0
for old_ver in OLD_FOOTER_VERS:
    if old_ver in c:
        c = c.replace(old_ver, FOOTER_VER)
        ver_synced += 1

# 若 cy-shell 的 CSS 定义影响布局, 保留但嵌套在 shell 内可兼容. main 需要 min-width.
open(p, 'w', encoding='utf-8').write(c)
print(f"OK index_cyto.html：头 {head_action} / 尾 {foot_action} / 页脚版本替换 {ver_synced} 处")
print("含sidebar:", 'class="sidebar"' in c, "| 导航项:", c.count('class="mag"'), "| 门户入口:", '门户入口' in c)
print("页脚版本:", FOOTER_VER, "| 残留旧版本:", [v for v in OLD_FOOTER_VERS if v in c])
