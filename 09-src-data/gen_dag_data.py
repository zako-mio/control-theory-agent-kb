# -*- coding: utf-8 -*-
"""生成知识库交互总览 DATA (五环 × 控制概念 DAG)"""
import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ★ 本地化：仓库根由本文件位置推导（⛔ 不硬编码作者机路径）

# 五大核心环节点
rings = [
    {"id":"E","type":"ring","kind":"sensor","label":"E 评估/传感器","ctrl":"测量环节+验证器","short":"E","color":"#e74c3c"},
    {"id":"R","type":"ring","kind":"controller","label":"R 反思/反馈闭环","ctrl":"反馈控制器(PID)","short":"R","color":"#f39c12"},
    {"id":"M","type":"ring","kind":"estimator","label":"M 记忆/状态估计","ctrl":"状态观测器+卡尔曼","short":"M","color":"#16a085"},
    {"id":"P","type":"ring","kind":"planner","label":"P 规划/分层控制","ctrl":"慢速上层策略控制器","short":"P","color":"#2980b9"},
    {"id":"T","type":"ring","kind":"actuator","label":"T 工具调用/执行器","ctrl":"执行器+安全阀+仲裁","short":"T","color":"#8e44ad"},
]

# 每环的主控概念(KT)节点
concepts = [
    # E 环
    {"id":"KT-ctrl-006","ring":"E","kind":"concept","label":"灵敏度/鲁棒性基座","kt":"KT-ctrl-006","color":"#e74c3c"},
    {"id":"KT-ctrl-035","ring":"E","kind":"concept","label":"扰动观测器 DOB","kt":"KT-ctrl-035","color":"#e74c3c"},
    {"id":"KT-ctrl-012","ring":"E","kind":"concept","label":"观测噪声 R","kt":"KT-ctrl-012","color":"#e74c3c"},
    {"id":"KT-ctrl-001","ring":"E","kind":"concept","label":"开环vs闭环","kt":"KT-ctrl-001","color":"#e74c3c"},
    # R 环
    {"id":"KT-ctrl-002","ring":"R","kind":"concept","label":"负反馈闭环结构","kt":"KT-ctrl-002","color":"#f39c12"},
    {"id":"KT-ctrl-020","ring":"R","kind":"concept","label":"PID 三环节","kt":"KT-ctrl-020","color":"#f39c12"},
    {"id":"KT-ctrl-021","ring":"R","kind":"concept","label":"比例 P","kt":"KT-ctrl-021","color":"#f39c12"},
    {"id":"KT-ctrl-022","ring":"R","kind":"concept","label":"积分 I","kt":"KT-ctrl-022","color":"#f39c12"},
    {"id":"KT-ctrl-023","ring":"R","kind":"concept","label":"微分 D","kt":"KT-ctrl-023","color":"#f39c12"},
    {"id":"KT-ctrl-004","ring":"R","kind":"concept","label":"误差收敛校正律","kt":"KT-ctrl-004","color":"#f39c12"},
    {"id":"KT-ctrl-025","ring":"R","kind":"concept","label":"稳态误差/超调","kt":"KT-ctrl-025","color":"#f39c12"},
    {"id":"KT-ctrl-026","ring":"R","kind":"concept","label":"LQR 状态反馈","kt":"KT-ctrl-026","color":"#f39c12"},
    # M 环
    {"id":"KT-ctrl-010","ring":"M","kind":"concept","label":"状态估计问题","kt":"KT-ctrl-010","color":"#16a085"},
    {"id":"KT-ctrl-011","ring":"M","kind":"concept","label":"卡尔曼滤波","kt":"KT-ctrl-011","color":"#16a085"},
    {"id":"KT-ctrl-014","ring":"M","kind":"concept","label":"信息滤波/降维","kt":"KT-ctrl-014","color":"#16a085"},
    {"id":"KT-ctrl-015","ring":"M","kind":"concept","label":"贝叶斯滤波/HMM","kt":"KT-ctrl-015","color":"#16a085"},
    {"id":"KT-ctrl-013","ring":"M","kind":"concept","label":"分离性原理","kt":"KT-ctrl-013","color":"#16a085"},
    # P 环
    {"id":"KT-ctrl-041","ring":"P","kind":"concept","label":"分层控制(时标)","kt":"KT-ctrl-041","color":"#2980b9"},
    {"id":"KT-ctrl-043","ring":"P","kind":"concept","label":"时间尺度分离 ε","kt":"KT-ctrl-043","color":"#2980b9"},
    {"id":"KT-ctrl-044","ring":"P","kind":"concept","label":"MPC 滚动时域","kt":"KT-ctrl-044","color":"#2980b9"},
    {"id":"KT-ctrl-045","ring":"P","kind":"concept","label":"规划-执行解耦","kt":"KT-ctrl-045","color":"#2980b9"},
    {"id":"KT-ctrl-042","ring":"P","kind":"concept","label":"多层递阶控制","kt":"KT-ctrl-042","color":"#2980b9"},
    {"id":"KT-ctrl-046","ring":"P","kind":"concept","label":"options/SMDP","kt":"KT-ctrl-046","color":"#2980b9"},
    # T 环
    {"id":"KT-ctrl-034","ring":"T","kind":"concept","label":"饱和/看门狗/anti-windup","kt":"KT-ctrl-034","color":"#8e44ad"},
    {"id":"KT-ctrl-033","ring":"T","kind":"concept","label":"冗余与仲裁","kt":"KT-ctrl-033","color":"#8e44ad"},
    {"id":"KT-ctrl-031","ring":"T","kind":"concept","label":"鲁棒稳定性","kt":"KT-ctrl-031","color":"#8e44ad"},
    {"id":"KT-ctrl-032","ring":"T","kind":"concept","label":"鲁棒方法(H∞/μ/滑模)","kt":"KT-ctrl-032","color":"#8e44ad"},
    {"id":"KT-ctrl-030","ring":"T","kind":"concept","label":"模型不确定性","kt":"KT-ctrl-030","color":"#8e44ad"},
]

# 控制回路边: E→R→M (感知→纠正→认知) ; M→P (认知→规划) ; P→T (规划→执行) ; T→world, world→E
edges = [
    # 控制回路主链
    {"source":"E","target":"R","kind":"feedback","label":"反馈误差 e"},
    {"source":"R","target":"M","kind":"feedback","label":"修正量回灌"},
    {"source":"M","target":"P","kind":"state","label":"信念状态"},
    {"source":"P","target":"T","kind":"command","label":"指令/里程碑"},
    {"source":"T","target":"E","kind":"observe","label":"实际输出 y"},
    # 环内 概念→所属环
]
# 概念挂在所属环上(节点上属)
for c in concepts:
    edges.append({"source":c["ring"],"target":c["id"],"kind":"belongs","label":""})

data = {"rings":rings,"concepts":concepts,"edges":edges}
outpath = os.path.join(base,"09-src-data","five-ring-dag.json")
os.makedirs(os.path.dirname(outpath), exist_ok=True)
with open(outpath,"w",encoding="utf-8") as f:
    json.dump(data,f,ensure_ascii=False,indent=2)
print("OK 写入:",outpath)
print("节点数:", len(rings)+len(concepts), "边数:", len(edges))
# 验证
with open(outpath,encoding="utf-8") as f:
    d=json.load(f)
print("验证: JSON 合法, rings=%d concepts=%d edges=%d"%(len(d["rings"]),len(d["concepts"]),len(d["edges"])))
print("验证: 无替换字符=","\ufffd" not in json.dumps(d,ensure_ascii=False))
