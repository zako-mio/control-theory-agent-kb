# -*- coding: utf-8 -*-
"""opencode_custom_scores.py — opencode-custom 精装度评分（复用 premium_scores v2.0 模型）

⚠️ 定位：个人变体·不参与 14 产品市售排名。本文件独立于 premium_scores.PRODUCTS，
    仅为本专题（官方基线 vs 自改造）提供可复算分值，避免污染市售谱系。

基线：官方 opencode 默认 + 最小常规装配（四 agent + 官方内置 skills + 基础 provider）
模型：硬门槛（端到端可跑 0/1）+ 8 维加权（权重同 premium_scores.WEIGHTS）+ 一票否决

重算记录：2026-09-11（v1.2 2026-09-09 快照 → 当前漂移后复评）。
  依据：07-checkpoint/opencode-custom-snapshot/inventory.json（agents=10 / mcp=6 / skills=45+_shared）
        + `opencode debug skill` 实测（42 加载 = 41 装配层 + 1 built-in；4 个 _SKILL.md 不达标未加载）
        + opencode.jsonc（provider 3 家）+ 新增架构三层栈。
  结论：漂移为「能力纵深」增长，未跨任何 5 档产品阈值 → 8 维分值不变，仅刷新 evidence。
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import premium_scores as ps

WEIGHTS = ps.WEIGHTS          # 8 维权重（合计 100）
GATE_CAP = ps.GATE_CAP        # 3.0

# 8 维打分依据见 03-cases/opencode-custom-diff.md §评分
SCORES = {
    "opencode-official": {
        "name": "opencode（官方默认+最小装配）",
        "gate": True,
        "dims": {"multi": 3, "deploy": 3, "model": 3, "workflow": 3,
                 "skill": 2, "sandbox": 3, "mcp": 3, "memory": 3},
        "evidence": {
            "multi": "plan/build/task 委派原语，需用户编排（无专职 worker）",
            "deploy": "npm 安装 + 自填 provider key",
            "model": "多 provider，需填 key/配置",
            "workflow": "plan 模式 + 编排原语，需用户搭建",
            "skill": "内置工具集，无预装 skill 库",
            "sandbox": "permission ask/deny + snapshot 回滚（非完整沙箱）",
            "mcp": "MCP 接入 / 工具节点",
            "memory": "SQLite session + compaction（会话级）",
        },
    },
    "opencode-custom": {
        "name": "opencode-custom（自改造·装配层）",
        "gate": True,
        "dims": {"multi": 4, "deploy": 3, "model": 4, "workflow": 4,
                 "skill": 4, "sandbox": 3, "mcp": 4, "memory": 5},
        "evidence": {
            "multi": "10 agent（+6 专职 worker：pdf/drawio/architect/vision/reflection/search）+ 委派协议 + 并行 + subagent_depth=2；新增 architect-worker 但无真 DAG/画布（inventory.agents=10）→ 与 4 档「无画布编排」一致，不升 5",
            "deploy": "个人 config 需手动复制装配层，无一键分发（仍为个人变体定位）；无 npm/docker/SaaS 分发 → 维持 3",
            "model": "3 provider（opencode-go/deepseek/zhipu）+ deepseek-flash V4.1 原生多模态 + @ai-sdk/openai-compatible 图片链路修复；仍非「数百模型开箱」（厂商 5 档）→ 维持 4",
            "workflow": "GATE/COMPLEXITY 门控 + 契约驱动 + 委派接力；新增架构三层栈 gated SOP（arch.md + architecture-behavior + architecture-judgment + gate_architecture.py）；但无通用可视化工作流/DAG 引擎（厂商 5 档=可视化画布）→ 维持 4",
            "skill": "45 skill 目录（+_shared；41 个可加载 SKILL.md，4 个 _SKILL.md 不达标未加载）+ 单根统一；新增 7 个（capability-extension/architecture-judgment 等）；仍为精选个人库、无市场/分发（5 档=插件市场/数万 skill）→ 维持 4",
            "sandbox": "+ external_directory 白名单 + /tmp/opencode 隔离区，仍非完整沙箱/VM 隔离 → 维持 3",
            "mcp": "6 MCP（vscode-mcp-server/amap/pdf-reader/drawio/drawio-local/headroom，多传输；2 enabled）→ 与 v1.2 同构，维持 4",
            "memory": "MEMORY.md 跨会话 + pending.json 结构化状态机 + reflection-worker + compaction 调优 → 维持 5",
        },
    },
}


# ---- 五环雷达分值（对照页单一数据源，禁止在生成器中硬编码）----
# 环序: SP 设定值 / M 记忆 / P 规划 / R 反思 / T 执行 / E 评估
# 官方=官方内核五环分值；自改造=装配层补强后的综合分值（见 03-cases/opencode-custom-diff.md §3）
RING_ORDER = ["SP", "M", "P", "R", "T", "E"]
RING_META = {
    "SP": {"label": "设定值", "ctrl": "Setpoint · 目标参考序列", "color": "#1E5AA8",
           "change": "GATE 强制门控 + COMPLEXITY 跨阶段继承 + grill-me/question 目标澄清 + 契约驱动委派"},
    "M":  {"label": "记忆", "ctrl": "Estimator · 状态估计", "color": "#1F7A52",
           "change": "MEMORY.md 跨会话长期记忆 + pending.json 结构化状态机 + compaction 调优"},
    "P":  {"label": "规划", "ctrl": "Planner · 分层控制", "color": "#1E5AA8",
           "change": "+6 专职 worker（+architect-worker）+ GATE/COMPLEXITY 推理档分层 + 契约驱动委派接力（P 已处 5.0 上限）"},
    "R":  {"label": "反思", "ctrl": "Feedback · 反馈闭环", "color": "#C77700",
           "change": "Reflection 自演化系统（pending.json + reflection-worker + /reflection 签名门禁）"},
    "T":  {"label": "执行", "ctrl": "Actuator · 工具执行", "color": "#5B4B9B",
           "change": "6 MCP + 权限白名单 + 专职 worker 工具隔离"},
    "E":  {"label": "评估", "ctrl": "Sensor · 评估传感", "color": "#B23A2F",
           "change": "search-behavior 信源分级 + search-worker 证据包 + grill-me/question 用户传感器 + gate_architecture.py ADR schema 门控（领域级自动评估）"},
}
# 2026-09-11 复评：架构三层栈仅强化「架构域」工作流与单点门控；P 已 5.0 封顶，
# E 增量为领域级（单点门控，不足以整体 +0.5），R 无新反思机制 → 三环维持 5.0/4.0/4.5，官方基线不变。
RING_SCORES = {
    "opencode-official": {"SP": 3.5, "M": 3.5, "P": 4.5, "R": 2.0, "T": 4.5, "E": 2.0},
    "opencode-custom":   {"SP": 4.5, "M": 4.0, "P": 5.0, "R": 4.5, "T": 5.0, "E": 4.0},
}


def ring_delta(rid):
    """返回 (官方, 自改造, Δ, 标注)；Δ>=2.0 记为『反转』，否则『增强』。"""
    o = RING_SCORES["opencode-official"][rid]
    c = RING_SCORES["opencode-custom"][rid]
    d = round(c - o, 1)
    return o, c, d, ("反转" if d >= 2.0 else "增强")


def weighted(key):
    return sum(WEIGHTS[k] * SCORES[key]["dims"][k] for k in WEIGHTS) / 100.0


def final(key):
    s = weighted(key)
    if not SCORES[key]["gate"]:
        s = min(s, GATE_CAP)
    return round(s, 1)


if __name__ == "__main__":
    print("key                  raw    final  tier")
    for key in SCORES:
        print("%-20s %5.2f  %4s  %s" % (key, weighted(key), ps.fmt(final(key)), ps.tier(final(key))))
    delta = final("opencode-custom") - final("opencode-official")
    print("\n精装度跃升: %.1f -> %.1f  (Δ %+0.1f)" % (
        final("opencode-official"), final("opencode-custom"), delta))
