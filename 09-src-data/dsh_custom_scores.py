# -*- coding: utf-8 -*-
"""dsh_custom_scores.py — dsh（DeepSeek Harness）官方 vs 装配层 精装度评分

⚠️ 定位：与 opencode_custom_scores.py 同构——「个人装配层变体」专题，**不参与 14 产品市售排名**。
    本文件独立于 premium_scores.PRODUCTS，仅为本专题提供可复算分值。

模型：硬门槛（端到端可跑 0/1）+ 8 维加权（权重同 premium_scores.WEIGHTS）+ 一票否决
基线：dsh v0.2.1-alpha.2（2026-10-09）官方默认装配
装配层：`dsh-opencode-port` bundle（~/.dsh/presets/opencode/，3 preset / 45 派生 skill / 7 worker）
        + 宿主 profile patch（4 provider + permission 5 档 + plugin-manager pnpmCommand）

⚠️ **口径披露（重要）**：v1.3 之前 dsh 只有「技术框架对照」的**单点分 2.5**（gen_html.py FRAMEWORK_DATA），
   不是本 8 维模型的输出。本轮**首次**对 dsh 回填 v2.0 模型，故 3.6 与旧 2.5 **不同源、不可直接相减**；
   旧单点分作为历史口径保留（见 03-cases/dsh-custom-diff.md §口径披露）。

分值依据（全部源码级/配置级实证，见 03-cases/dsh-custom-diff.md §评分与 07-checkpoint/dsh-custom-snapshot/）：
  multi    : 官方=4（subagent 6 provider 后端 + fork + workflow + Agent Teams 实验，无可视化 DAG）；
             装配层=4（+7 worker + oc_* 别名 + 3 preset 编队，仍无 DAG 画布）
  deploy   : 3（自托管 CLI/npx + 自填 key；本库口径：5 档保留给托管 SaaS 或单命令容器化成品）
  model    : 4（DeepSeek 直连 + pi-ai 目录 + 自定义 OpenAI Chat/Responses/Anthropic 三协议；非「千级预设开箱」）
  workflow : 4（plan/goal/workflow/ralph + jobs + schedule 四工具触发；无通用可视化画布）
  skill    : 官方=3（skill 注册表 host+per-scope + 官方 skill 包，非市场）；装配层=4（+45 派生 skill 精选库）
  sandbox  : 官方=4（bwrap/Landlock/Seatbelt/Windows ACL/SSH 后端族 + enforcement full/partial + fail-closed；
             注意本机无可用后端 → fail-closed，属环境事实）；装配层=4（Δ0，未新增隔离能力）
  mcp      : 3（内置 MCP client + resources 三工具，无 marketplace）；装配层=3（Δ0，宿主 0 MCP 配置）
  memory   : 4（事件溯源 session + 投影 + token-meter + compaction + session-format v4 + session-query FTS5
             跨会话检索；无「跨会话学习型长期记忆」，故不取 5）
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import premium_scores as ps

WEIGHTS = ps.WEIGHTS          # 8 维权重（合计 100）
GATE_CAP = ps.GATE_CAP        # 3.0

SCORES = {
    "dsh-official": {
        "name": "dsh（DeepSeek Harness v0.2.1-alpha.2 官方默认）",
        "gate": True,
        "dims": {"multi": 4, "deploy": 3, "model": 4, "workflow": 4,
                 "skill": 3, "sandbox": 4, "mcp": 3, "memory": 4},
        "evidence": {
            "multi": "subagent 6 个 provider 后端（spawn/fork/acp/codex/claude-code/dsh-sdk）+ 托管式 activations + fork + workflow + Agent Teams（实验：持久 roster + 任务 DAG + 直投 inbox）；无可视化 DAG 画布",
            "deploy": "npx @deepseek-ai/dsh web 单命令起 + 自填 provider key；本库口径：自托管 CLI + 自填 key = 3 档",
            "model": "DeepSeek 直连 + llm-pi-ai 第三方目录 + 自定义 OpenAI Chat Completions / OpenAI Responses / Anthropic Messages 三协议",
            "workflow": "plan-mode + goal/goal-round-driver + workflow（JS 编排）+ ralph + jobs 运行时 + schedule 四工具（cron/IANA 时区）；无通用可视化画布",
            "skill": "skill 注册表 host + per-scope 分层 + filesystem/badge/office/ACL provider + 官方 skill 包；非市场",
            "sandbox": "sandbox 后端族（linux bwrap→Landlock、darwin Seatbelt、win32 ACL 受限令牌、sandbox-ssh）+ enforcement full/partial + 不可用即 SANDBOX_UNAVAILABLE fail-closed；permission presets 五档并可派生 custom/Auto。⚠️ 本机无可用后端（bubblewrap/Landlock 均不可用）→ 实际 fail-closed",
            "mcp": "内置 MCP client（外部 server 暴露为原生工具）+ mcp-resources 三工具；无 marketplace",
            "memory": "事件溯源 session（append-only）+ projection 纯函数折叠 + token-meter + compaction 三插件 + session-format v4 代际迁移 + session-query/FTS5 五只读工具；无跨会话学习型长期记忆（不取 5）",
        },
    },
    "dsh-custom": {
        "name": "dsh-custom（dsh + dsh-opencode-port 装配层）",
        "gate": True,
        "dims": {"multi": 4, "deploy": 3, "model": 4, "workflow": 4,
                 "skill": 4, "sandbox": 4, "mcp": 3, "memory": 4},
        "evidence": {
            "multi": "3 preset 编队（opencode-standard/creator/ptc，order 11/12/13）+ 7 worker（general/explore/architect/requirement-discovery/search/reflection/pdf）+ 全局控制面 send_message/interrupt_agent/list_agents；无真 DAG/画布 → 与 4 档一致，不升 5",
            "deploy": "bundle 需手动 install_bundle 且**不可移植**（persona 含本机绝对路径、node_modules 28 个符号链接指向本机源码树）；无 npm/docker/SaaS 分发 → 维持 3",
            "model": "宿主 profile 提供 4 provider（zai/opencode-go/commandcode/opencode-go-tmp）+ deepseek；含 inputModalities 视觉声明；仍非「千级模型开箱」→ 维持 4",
            "workflow": "persona 15 节把 GATE/COMPLEXITY/契约委派/留档 5 段等流程纪律迁入 preset 层 + plan-mode section 追加 grill-me 逐题访谈指引；无通用可视化画布 → 维持 4",
            "skill": "45 派生 skill 单根（模型可见 42 = 45 − 3 件 disable-model-invocation）+ _overlay 6 件 openspec 系叠加；精选个人库、无市场/分发 → 4 档",
            "sandbox": "宿主 permission presets 增至 5 档（read-only / workspace-write / opencode-plan / opencode-build / danger-full-access）；opencode-plan/build 属**审批档**而非隔离档，且本机仍无沙箱后端 → 维持 4（Δ0）",
            "mcp": "宿主 0 个 MCP 配置（对比 opencode-custom 侧 4 个）→ 维持 3（迁移相对损失，见 diff §5）",
            "memory": "装配层未新增跨会话记忆：persona 中的 MEMORY/reflection 段在 dsh 侧**不可用**（提供 reflection_add/reflection_mark 的 dsh-reflection 插件已于 2026-10-10 移出）→ 维持 4（Δ0）",
        },
    },
}


# ---- 五环双层分值（对照页单一数据源，禁止在生成器中硬编码）----
# 环序: SP 设定值 / M 记忆 / P 规划 / R 反思 / T 执行 / E 评估
# 官方=内核分值（由 KB v1.3 的定性判定映射：最突出 5.0 / 强 4.5 / 次强 4.0 / 中弱 3.0 / 最弱 2.0）
RING_ORDER = ["SP", "M", "P", "R", "T", "E"]
RING_META = {
    "SP": {"label": "设定值", "ctrl": "Setpoint · 目标参考序列", "color": "#1E5AA8",
           "change": "3 preset 层固化 persona 15 节（GATE/COMPLEXITY/契约委派/留档 5 段）+ plan-mode section 追加逐题访谈指引"},
    "M":  {"label": "记忆", "ctrl": "Estimator · 状态估计", "color": "#1F7A52",
           "change": "装配层未新增跨会话记忆；persona 的 MEMORY/reflection 段在 dsh 侧不可用（dsh-reflection 插件已移出）→ Δ0"},
    "P":  {"label": "规划", "ctrl": "Planner · 分层控制", "color": "#1E5AA8",
           "change": "+7 专职 worker + oc_* 别名 + delegation 编队（12 子行）+ 全局控制面（send_message/interrupt_agent/list_agents）"},
    "R":  {"label": "反思", "ctrl": "Feedback · 反馈闭环", "color": "#C77700",
           "change": "装配层未新增内源反思；reflection 链路在 dsh 侧断裂（插件已移出）→ Δ0（迁移损失）"},
    "T":  {"label": "执行", "ctrl": "Actuator · 工具执行", "color": "#5B4B9B",
           "change": "permission 5 档 + 工具面按 preset 收敛（standard 37 / creator 40 / ptc 1）+ plugin_manager 收口（188→191）"},
    "E":  {"label": "评估", "ctrl": "Sensor · 评估传感", "color": "#B23A2F",
           "change": "oc_architect + gate_architecture.py 领域门控 / oc_requirement + 分层定档工具 / oc_search 证据包 + 信源分级 / criterion-design-validation；但①门控脚本依赖 bash 而 dsh 子 Agent 无 bash（迁移损失）②仍为领域级单点 → 增强而非反转"},
}
RING_SCORES = {
    "dsh-official": {"SP": 4.5, "M": 4.0, "P": 4.5, "R": 3.0, "T": 5.0, "E": 2.0},
    "dsh-custom":   {"SP": 5.0, "M": 4.0, "P": 5.0, "R": 3.0, "T": 5.0, "E": 3.5},
}


def ring_delta(rid):
    """返回 (官方, 装配层, Δ, 标注)；Δ>=2.0 记为『反转』，否则『增强』。"""
    o = RING_SCORES["dsh-official"][rid]
    c = RING_SCORES["dsh-custom"][rid]
    d = round(c - o, 1)
    return o, c, d, ("反转" if d >= 2.0 else ("增强" if d > 0 else "持平"))


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
    delta = final("dsh-custom") - final("dsh-official")
    print("\n精装度跃升: %.1f -> %.1f  (Δ %+0.1f)" % (
        final("dsh-official"), final("dsh-custom"), delta))
    print("\n五环双层（官方 → 装配层）：")
    for rid in RING_ORDER:
        o, c, d, tag = ring_delta(rid)
        print("  %-3s %s %.1f -> %.1f  (Δ %+0.1f, %s)" % (rid, RING_META[rid]["label"], o, c, d, tag))
