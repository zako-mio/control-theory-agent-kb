# -*- coding: utf-8 -*-
"""dsh_custom_scores.py — dsh（DeepSeek Harness）官方 vs 装配层 精装度评分

⚠️ 定位：与 opencode_custom_scores.py 同构——「个人装配层变体」专题，**不参与 14 产品市售排名**。
    本文件独立于 premium_scores.PRODUCTS，仅为本专题提供可复算分值。

模型：硬门槛（端到端可跑 0/1）+ 8 维加权（权重同 premium_scores.WEIGHTS）+ 一票否决
基线：dsh v0.2.1-alpha.2（2026-10-09，commit d743267）官方默认装配 —— **v1.4 → v1.5 内核未变**
装配层：`dsh-opencode-port` bundle（~/.dsh/presets/opencode/，3 preset / 主根 49 skill / 7 worker）
        + 宿主 profile patch（4 provider + permission 5 档 + plugin-manager pnpmCommand）

================================ v1.5 复评（2026-10-13）================================
触发判据（契约 §2.7⑥）：内核未升版，但装配层命中「能力纵深增长 / 机制新增」六项
  （run_gate 门控通道 / dsh-config 能力包 / R-A 记忆载体 / 两个新插件 / 判据 13→20 / 沙箱本机可强制）。
证据基准：`07-checkpoint/dsh-custom-snapshot/`（collected_at 2026-10-13T05:09:43+08:00）；
  v1.4 旧快照归档于 `archive/1011-KB-v1.4-dsh装配与opencode追平/dsh-custom-snapshot-v1.4/`。

v1.5 相对 v1.4 的**唯一 8 维变动**：`memory` 4 → 5（权重 10% ⇒ +0.10）
  · 依据：R 环 R-A 载体已落地（ADR-012）——`~/.dsh/MEMORY.md` 存在（14 个 `§` 段 / 10815 B /
    14 条 `[src:]` 签名）+ `~/.dsh/reflection/candidates/` 15 份候选 + `archive/` 1 份 +
    `dsh-reflection` skill（承载零和预算 / 生命周期五件 / 容量口径）。
  · 档位依据（premium-scoring-model.md §3.2 记忆列）：5 档 = 「跨 session 知识库 + 长期记忆 + 结构化状态」，
    三项均已具备；v1.4 不取 5 的理由（「无跨会话学习型长期记忆」）**已被现实推翻**。
  · ⚠️ 诚实口径：机制齐备但**内容体量仍小**（14 段 / 10.8 KB），且写入为「候选 → 主 Agent 审阅 → 落库」
    的**显式链**（非自动自省）。判 5 的依据是**档位措辞三项齐备**，不是「内容规模」。

五环双层变动（v1.5）：M 4.0→4.5（+0.5）· R 3.0→4.0（+1.0）· E 3.5→4.0（+1.5 对官方 2.0 ⇒ Δ+2.0 **反转**）
  · R：R-A 载体使反思链由「断裂」变为「可用」，故不再是迁移损失；
  · E：`run_gate` 窄通道（ADR-010）为产出方恢复了门控执行通道 ⇒ v1.4 的「门控脚本依赖 bash 而子 Agent
    无 bash」这一抑制项**已消解**，Δ 达反转阈值；仍为领域级覆盖（架构 / 需求两域）故不取 4.5+。
  · ⚠️ 最弱环结论**再次改变**：v1.4 判「最弱环由 E 转移到 R」；v1.5 下 R=4.0 与 E=4.0 **并列**，
    不再存在单一最弱环。

⚠️ **口径披露（重要，两条）**：
  (1) v1.3 之前 dsh 只有「技术框架对照」的**单点分 2.5**（gen_html.py FRAMEWORK_DATA），不是本 8 维模型的
      输出。v1.4 **首次**回填 v2.0 模型得 3.6，故 3.6 与旧 2.5 **不同源、不可直接相减**（历史口径保留）。
  (2) 沙箱维**分值未变（4）但证据文本被更正**：v1.4 记「本机无可用后端（bubblewrap/Landlock 均不可用）
      → 实际 fail-closed」；v1.5 实测**该断言已被证伪**（bwrap 已装、链选中 bwrap、enforcement=full，
      read-only / workspace-write 在 shell+fs 双侧真强制）。此为**环境事实更正**，不是装配层能力增量，
      故 ⛔ 不计入分值变动、⛔ 不得呈现为装配层收益。

分值依据（全部源码级/配置级实证，见 03-cases/dsh-custom-diff.md §评分与 07-checkpoint/dsh-custom-snapshot/）：
  multi    : 官方=4（subagent 6 provider 后端 + fork + workflow + Agent Teams 实验，无可视化 DAG）；
             装配层=4（+7 worker + oc_* 别名 + 3 preset 编队 + run_gate 窄通道工具行，仍无 DAG 画布）
  deploy   : 3（自托管 CLI/npx + 自填 key；本库口径：5 档保留给托管 SaaS 或单命令容器化成品）
  model    : 4（DeepSeek 直连 + pi-ai 目录 + 自定义 OpenAI Chat/Responses/Anthropic 三协议；非「千级预设开箱」）
  workflow : 4（plan/goal/workflow/ralph + jobs + schedule 四工具触发；无通用可视化画布）
  skill    : 官方=3（skill 注册表 host+per-scope + 官方 skill 包，非市场）；装配层=4（+主根 49 精选库）
  sandbox  : 官方=4（bwrap/Landlock/Seatbelt/Windows ACL/SSH 后端族 + enforcement full/partial + fail-closed）；
             装配层=4（Δ0，未新增隔离能力）
  mcp      : 3（内置 MCP client + resources 三工具，无 marketplace）；装配层=3（Δ0，宿主 0 MCP 配置）
  memory   : 官方=4（事件溯源 session + 投影 + token-meter + compaction + session-format v4 + session-query FTS5
             跨会话检索；无跨会话学习型长期记忆）；装配层=5（+R-A 载体，见上）
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import premium_scores as ps

WEIGHTS = ps.WEIGHTS          # 8 维权重（合计 100）
GATE_CAP = ps.GATE_CAP        # 3.0

# v1.4 时点读数（历史记录，⛔ 不得当作当前值；用于口径变更逐条对账）
HISTORY = {
    "v1.4": {
        "collected_at": "2026-10-11T17:09:09+08:00",
        "dims": {
            "dsh-official": {"multi": 4, "deploy": 3, "model": 4, "workflow": 4,
                             "skill": 3, "sandbox": 4, "mcp": 3, "memory": 4},
            "dsh-custom": {"multi": 4, "deploy": 3, "model": 4, "workflow": 4,
                           "skill": 4, "sandbox": 4, "mcp": 3, "memory": 4},
        },
        "rings": {
            "dsh-official": {"SP": 4.5, "M": 4.0, "P": 4.5, "R": 3.0, "T": 5.0, "E": 2.0},
            "dsh-custom":   {"SP": 5.0, "M": 4.0, "P": 5.0, "R": 3.0, "T": 5.0, "E": 3.5},
        },
        "note": "v1.4 快照口径；skill 主根 45（派生 45 / 原生 0）/ 模型可见 42 / _overlay 6 / verify_bundle 13 项",
    },
}

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
            "sandbox": "sandbox 后端族（linux bwrap→Landlock、darwin Seatbelt、win32 ACL 受限令牌、sandbox-ssh）+ enforcement full/partial + 不可用即 SANDBOX_UNAVAILABLE fail-closed；permission presets 五档并可派生 custom/Auto。✅ v1.5 事实更正：本机 bwrap 已装且链选中 bwrap，enforcement=full（read-only / workspace-write 于 shell+fs 双侧真强制）——v1.4 的「本机无可用后端」断言已证伪",
            "mcp": "内置 MCP client（外部 server 暴露为原生工具）+ mcp-resources 三工具；无 marketplace",
            "memory": "事件溯源 session（append-only）+ projection 纯函数折叠 + token-meter + compaction 三插件 + session-format v4 代际迁移 + session-query/FTS5 五只读工具；无跨会话学习型长期记忆（不取 5）",
        },
    },
    "dsh-custom": {
        "name": "dsh-custom（dsh + dsh-opencode-port 装配层）",
        "gate": True,
        "dims": {"multi": 4, "deploy": 3, "model": 4, "workflow": 4,
                 "skill": 4, "sandbox": 4, "mcp": 3, "memory": 5},
        "evidence": {
            "multi": "3 preset 编队（opencode-standard/creator/ptc，order 11/12/13）+ 7 worker（general/explore/architect/requirement-discovery/search/reflection/pdf）+ 全局控制面 send_message/interrupt_agent/list_agents；v1.5 新增 preset 顶层 gate-runner 行（窄工具 run_gate）；无真 DAG/画布 → 与 4 档一致，不升 5",
            "deploy": "bundle 需手动 install_bundle 且**不可移植**（persona 含本机绝对路径、node_modules 符号链接指向本机源码树）；无 npm/docker/SaaS 分发 → 维持 3",
            "model": "宿主 profile 提供 4 provider（zai/opencode-go/commandcode/opencode-go-tmp）+ deepseek；v1.5 新增 reasoningEfforts 三档映射（low/high/max，刻意不声明 off）与 maxTokens 输出上限治理（8192→32768 撤销「方案 D」）；仍非「千级模型开箱」→ 维持 4",
            "workflow": "persona 15 节把 GATE/COMPLEXITY/契约委派/留档 5 段等流程纪律迁入 preset 层 + plan-mode section 追加 grill-me 逐题访谈指引；v1.5 新增 dsh-opencode-commands 插件注册 `/arch` `/rd` `/reflection` 三条命令（命令级工作流入口）；无通用可视化画布 → 维持 4",
            "skill": "主根 49 = 派生 47 + DSH 原生 2（dsh-config / dsh-reflection），模型可见 46 = 49 − 3 件 disable-model-invocation；_overlay 另 6 件 openspec 系叠加；精选个人库、无市场/分发 → 4 档",
            "sandbox": "宿主 permission presets 5 档（read-only / workspace-write / opencode-plan / opencode-build / danger-full-access），defaultPreset 由 read-only 改为 opencode-plan；opencode-plan/build 属**审批档**而非隔离档。✅ v1.5 事实更正：本机沙箱后端已可用且 enforcement=full（v1.4 记「本机仍无沙箱后端」已证伪）——但此为环境事实更正、非装配层新增隔离能力 → **维持 4（Δ0）**",
            "mcp": "宿主 0 个 MCP 配置（对比 opencode-custom 侧 4 个）→ 维持 3（迁移相对损失，见 diff §5）",
            "memory": "R 环 R-A 载体已落地（ADR-012，门控 6/6）：`~/.dsh/MEMORY.md` 存在（14 个 § 段 / 10815 B / 14 条 [src:] 签名）+ `~/.dsh/reflection/candidates/` 15 份候选 + `archive/` 1 份 + `dsh-reflection` skill 承载零和预算 / 生命周期五件 / 容量口径；档位措辞「跨 session 知识库 + 长期记忆 + 结构化状态」三项齐备 → **4 → 5**。⚠ 机制齐备但内容体量小（14 段 / 10.8 KB），写入为显式链非自动自省",
        },
    },
}


# ---- 五环双层分值（对照页单一数据源，禁止在生成器中硬编码）----
# 环序: SP 设定值 / M 记忆 / P 规划 / R 反思 / T 执行 / E 评估
# 官方=内核分值（由 KB v1.3 的定性判定映射：最突出 5.0 / 强 4.5 / 次强 4.0 / 中弱 3.0 / 最弱 2.0）
RING_ORDER = ["SP", "M", "P", "R", "T", "E"]
RING_META = {
    "SP": {"label": "设定值", "ctrl": "Setpoint · 目标参考序列", "color": "#1E5AA8",
           "change": "3 preset 层固化 persona 15 节（GATE/COMPLEXITY/契约委派/留档 5 段）+ plan-mode section 追加逐题访谈指引；v1.5 新增命令注册（/arch /rd /reflection）作为显式设定值入口 → 维持 5.0"},
    "M":  {"label": "记忆", "ctrl": "Estimator · 状态估计", "color": "#1F7A52",
           "change": "v1.5 反转项：R-A 载体落地（ADR-012）——~/.dsh/MEMORY.md（14 段 / 10815 B / 14 条 [src:]）+ 候选目录 15 份 + archive 1 份 + dsh-reflection skill；v1.4 的「装配层未新增跨会话记忆」已推翻 → 4.0 → 4.5（增强）"},
    "P":  {"label": "规划", "ctrl": "Planner · 分层控制", "color": "#1E5AA8",
           "change": "+7 专职 worker + oc_* 别名 + delegation 编队（12 子行）+ 全局控制面（send_message/interrupt_agent/list_agents）→ 维持 5.0"},
    "R":  {"label": "反思", "ctrl": "Feedback · 反馈闭环", "color": "#C77700",
           "change": "v1.5 反转项：反思链由「断裂」变为「可用」——候选→主 Agent 审阅→落库链 + 零和预算 + 生命周期五件（准入去重 / 退役三态 / 陈旧引用机检 / Coverage-Citation 双机检 / 零和）+ 容量口径（memory_capacity_check.py）；v1.4 的「迁移损失、Δ0」已推翻 → 3.0 → 4.0（增强，Δ+1.0）"},
    "T":  {"label": "执行", "ctrl": "Actuator · 工具执行", "color": "#5B4B9B",
           "change": "permission 5 档（defaultPreset → opencode-plan）+ 工具面按 preset 收敛 + plugin_manager 收口；v1.5 新增 run_gate 窄通道与命令注册插件；本机沙箱 enforcement=full → 维持 5.0（已封顶）"},
    "E":  {"label": "评估", "ctrl": "Sensor · 评估传感", "color": "#B23A2F",
           "change": "v1.5 达反转阈值：run_gate 门控执行通道（ADR-010）为产出方恢复脚本执行能力 ⇒ v1.4 的抑制项「门控脚本依赖 bash 而子 Agent 无 bash」消解；叠加 oc_architect + gate_architecture.py / oc_requirement + 分层定档 / oc_search 证据包 + 信源分级 / criterion-design-validation；仍为领域级覆盖（架构 / 需求两域）故不取 4.5+ → 3.5 → 4.0（对官方 2.0 为 Δ+2.0，反转）"},
}
RING_SCORES = {
    "dsh-official": {"SP": 4.5, "M": 4.0, "P": 4.5, "R": 3.0, "T": 5.0, "E": 2.0},
    "dsh-custom":   {"SP": 5.0, "M": 4.5, "P": 5.0, "R": 4.0, "T": 5.0, "E": 4.0},
}


def ring_delta(rid):
    """返回 (官方, 装配层, Δ, 标注)；Δ>=2.0 记为『反转』，否则『增强』。"""
    o = RING_SCORES["dsh-official"][rid]
    c = RING_SCORES["dsh-custom"][rid]
    d = round(c - o, 1)
    return o, c, d, ("反转" if d >= 2.0 else ("增强" if d > 0 else "持平"))


def weakest(key):
    """返回装配层侧的最弱环（并列时全部返回）。"""
    sc = RING_SCORES[key]
    lo = min(sc.values())
    return [r for r in RING_ORDER if sc[r] == lo], lo


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
    wr, lo = weakest("dsh-custom")
    print("\n装配层最弱环: %s = %.1f" % ("/".join(wr), lo))
    print("\n口径变更对账（v1.4 → v1.5）：")
    h = HISTORY["v1.4"]
    for key in SCORES:
        for k in WEIGHTS:
            old, new = h["dims"][key][k], SCORES[key]["dims"][k]
            if old != new:
                print("  dim  %-12s %-8s %s -> %s" % (key, k, old, new))
        for rid in RING_ORDER:
            old, new = h["rings"][key][rid], RING_SCORES[key][rid]
            if old != new:
                print("  ring %-12s %-8s %s -> %s" % (key, rid, old, new))
