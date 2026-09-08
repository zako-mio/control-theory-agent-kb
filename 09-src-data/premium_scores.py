# -*- coding: utf-8 -*-
"""premium_scores.py — 精装房评分模型（硬门槛 + 8 维加权 + 一票否决）单一数据源

本模块是「精装房」14 产品分值的唯一权威来源。所有生成物
（premium-map.html / premium-cyto.html / premium-*.html）与一致性自检脚本
均从此处读取；禁止在生成脚本或画像 MD 之外再硬编码分值。

模型（完整对标笔记本选购法，见 07-checkpoint/premium-scoring-model.md）:
  1) 硬门槛前置（0/1，不计权重）: 端到端可跑门槛——用户零配置（仅填 API Key）
     即可跑通一个端到端任务。不达标 → 综合分封顶 GATE_CAP=3.0，并降档标注。
  2) 8 维加权（合计 100%）: 每维 0-5 分，加权平均得 0-5 综合分。
  3) 一票否决: 「声称功能不存在」→ 封顶 4.0；「纯中转无自研底座」→ 封顶 3.5。
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---- 8 维与权重（合计 100%）----
DIMS = [
    ("multi",    "多Agent编排", 16),
    ("skill",    "Skill库",     12),
    ("workflow", "工作流",      13),
    ("model",    "模型接入",    14),
    ("deploy",   "一键部署",    15),
    ("sandbox",  "沙箱",        10),
    ("mcp",      "MCP生态",     10),
    ("memory",   "记忆",        10),
]
WEIGHTS = {k: w for k, _label, w in DIMS}
DIM_LABELS = {k: label for k, label, _w in DIMS}

GATE_CAP = 3.0     # 硬门槛未过 → 综合分封顶（"需装修"档）
VETO_CAP = 3.5     # 一票否决（纯中转）→ 综合分封顶
VETO_CLAIM_CAP = 4.0  # 一票否决（声称功能不存在）→ 综合分封顶

# ---- 14 产品登记表（分值来自 8 维实证评分）----
PRODUCTS = [
    {
        "slug": "openhands", "name": "OpenHands", "vendor": "All Hands AI",
        "hand": "一手", "cat": "开源成品化", "ev": "源码级",
        "note": "Agent Canvas UI+沙箱+子Agent预设+技能市场，真开箱即用成品",
        "dims": {"multi": 5, "skill": 5, "workflow": 4, "model": 4,
                 "deploy": 5, "sandbox": 4, "mcp": 3, "memory": 3},
        "gate": True, "gate_note": "npm/docker 一键起，预装端到端能力",
        "veto": None, "veto_note": "",
    },
    {
        "slug": "devin", "name": "Devin", "vendor": "Cognition",
        "hand": "一手", "cat": "第一方成品", "ev": "文档级",
        "note": "每session独立VM沙箱+Managed Devins并行+Dynamic Workflows(真DAG)",
        "dims": {"multi": 5, "skill": 5, "workflow": 5, "model": 5,
                 "deploy": 5, "sandbox": 5, "mcp": 5, "memory": 5},
        "gate": True, "gate_note": "注册即用 SaaS + Devin CLI 一键安装",
        "veto": None, "veto_note": "",
    },
    {
        "slug": "workbuddy", "name": "WorkBuddy", "vendor": "腾讯云",
        "hand": "一手", "cat": "第一方成品", "ev": "文档级",
        "note": "多Agent并行+7万Skills+托管底座+企业级安全治理",
        "dims": {"multi": 5, "skill": 5, "workflow": 4, "model": 4,
                 "deploy": 5, "sandbox": 5, "mcp": 4, "memory": 5},
        "gate": True, "gate_note": "注册即用托管 SaaS（旗舰/专享/私有化）",
        "veto": None, "veto_note": "",
    },
    {
        "slug": "dify", "name": "Dify", "vendor": "LangGenius",
        "hand": "一手", "cat": "低代码平台", "ev": "源码级",
        "note": "自研graphon编排引擎+可视化画布+RAG+插件市场，无LangChain",
        "dims": {"multi": 4, "skill": 5, "workflow": 5, "model": 5,
                 "deploy": 5, "sandbox": 3, "mcp": 4, "memory": 3},
        "gate": True, "gate_note": "docker compose 一键起，可视化画布端到端",
        "veto": None, "veto_note": "",
    },
    {
        "slug": "openclaude", "name": "OpenClaude", "vendor": "Gitlawb",
        "hand": "一手", "cat": "二次封装", "ev": "源码级",
        "note": "200+模型开箱接入+agents/tasks+MCP，独立TS实现非CC封装",
        "dims": {"multi": 4, "skill": 3, "workflow": 4, "model": 5,
                 "deploy": 4, "sandbox": 3, "mcp": 4, "memory": 3},
        "gate": True, "gate_note": "单 CLI 安装即用 + 引导式 provider",
        "veto": None, "veto_note": "",
    },
    {
        "slug": "cursor", "name": "Cursor", "vendor": "Anysphere",
        "hand": "一手", "cat": "第一方成品", "ev": "文档级",
        "note": "Cloud Agents并行+Composer规划+MCP生态+语义索引",
        "dims": {"multi": 4, "skill": 4, "workflow": 4, "model": 5,
                 "deploy": 5, "sandbox": 4, "mcp": 5, "memory": 4},
        "gate": True, "gate_note": "编辑器安装即用 + Cloud Agents 一键拉起",
        "veto": None, "veto_note": "",
    },
    {
        "slug": "coze", "name": "Coze扣子", "vendor": "字节跳动",
        "hand": "一手", "cat": "低代码平台", "ev": "文档级",
        "note": "可视化工作流+单/多Agent+插件商店+知识库+长期记忆",
        "dims": {"multi": 4, "skill": 5, "workflow": 5, "model": 4,
                 "deploy": 5, "sandbox": 3, "mcp": 2, "memory": 5},
        "gate": True, "gate_note": "平台托管，发布即用 Bot/API/渠道",
        "veto": None, "veto_note": "",
    },
    {
        "slug": "windsurf", "name": "Windsurf/Devin Desktop", "vendor": "Cognition",
        "hand": "一手", "cat": "第一方成品", "ev": "文档级",
        "note": "Cascade agent+RAG索引+MCP+SKILL.md（无Flows DAG）",
        "dims": {"multi": 3, "skill": 4, "workflow": 5, "model": 5,
                 "deploy": 5, "sandbox": 5, "mcp": 5, "memory": 5},
        "gate": True, "gate_note": "编辑器安装即用 + App Deploys 一键部署",
        "veto": {"type": "claim_false", "label": "声称功能不存在：无 Flows DAG 多Agent编排",
                 "cap": VETO_CLAIM_CAP},
        "veto_note": "多Agent编排维按实证计 3 分（Arena/worktrees/Managed Devins），综合分封顶 4.0",
    },
    {
        "slug": "gptresearcher", "name": "GPT Researcher", "vendor": "assafelovic",
        "hand": "一手", "cat": "开源成品化", "ev": "源码级",
        "note": "Web UI+8-agent编排+报告生成，编排自研",
        "dims": {"multi": 5, "skill": 3, "workflow": 4, "model": 4,
                 "deploy": 5, "sandbox": 0, "mcp": 4, "memory": 3},
        "gate": True, "gate_note": "Docker/Colab 一键 + pip install，给主题即跑",
        "veto": None, "veto_note": "",
    },
    {
        "slug": "codewhale", "name": "CodeWhale", "vendor": "Hmbown",
        "hand": "一手", "cat": "二次封装", "ev": "源码级",
        "note": "自研Rust底层，20个crate含agent/mcp/hooks/execpolicy",
        "dims": {"multi": 4, "skill": 3, "workflow": 4, "model": 4,
                 "deploy": 3, "sandbox": 3, "mcp": 4, "memory": 3},
        "gate": True, "gate_note": "cargo 原生构建安装，CLI 即跑端到端",
        "veto": None, "veto_note": "",
    },
    {
        "slug": "copilot", "name": "GitHub Copilot", "vendor": "GitHub/MS",
        "hand": "一手", "cat": "第一方成品", "ev": "文档级",
        "note": "Agent mode+Workspace任务化+多模型路由+MCP",
        "dims": {"multi": 3, "skill": 4, "workflow": 4, "model": 5,
                 "deploy": 5, "sandbox": 5, "mcp": 4, "memory": 3},
        "gate": True, "gate_note": "付费计划内即用，Cloud Agent 自动起环境",
        "veto": None, "veto_note": "",
    },
    {
        "slug": "qcode", "name": "QCode", "vendor": "qcode.cc",
        "hand": "二手", "cat": "二次封装", "ev": "文档级",
        "note": "一Key七模型族+Claude Code一键，官方价×服务倍率",
        "dims": {"multi": 0, "skill": 0, "workflow": 0, "model": 4,
                 "deploy": 4, "sandbox": 0, "mcp": 2, "memory": 0},
        "gate": False, "gate_note": "纯 API 中转，需外部客户端才能跑端到端任务",
        "veto": {"type": "relay", "label": "纯中转无自研底座（官方价×服务倍率）",
                 "cap": VETO_CAP},
        "veto_note": "无自研 Agent 底座，多Agent/Skill/工作流/沙箱/记忆全为 0",
    },
    {
        "slug": "crewai", "name": "CrewAI", "vendor": "CrewAI Inc",
        "hand": "一手", "cat": "开源成品化", "ev": "源码级",
        "note": "角色编排+工具库+JSON脚手架，需用户填角色流程",
        "dims": {"multi": 4, "skill": 4, "workflow": 4, "model": 4,
                 "deploy": 4, "sandbox": 0, "mcp": 4, "memory": 5},
        "gate": False, "gate_note": "需用户编写角色/流程才能跑端到端任务（框架非成品）",
        "veto": None, "veto_note": "",
    },
    {
        "slug": "ccrouter", "name": "CC-Router", "vendor": "musistudio",
        "hand": "二手", "cat": "二次封装", "ev": "源码级",
        "note": "多provider路由，核心依赖@the-next-ai/ai-gateway网关",
        "dims": {"multi": 0, "skill": 2, "workflow": 2, "model": 4,
                 "deploy": 4, "sandbox": 0, "mcp": 4, "memory": 0},
        "gate": False, "gate_note": "纯路由/中转，需外部客户端才能跑端到端任务",
        "veto": {"type": "relay", "label": "纯中转无自研底座（依赖第三方网关）",
                 "cap": VETO_CAP},
        "veto_note": "无自研 Agent 底座，多Agent/沙箱/记忆为 0",
    },
]

_BY_SLUG = {p["slug"]: p for p in PRODUCTS}


def by_slug(slug):
    return _BY_SLUG[slug]


def weighted(slug):
    """8 维加权原始分（0-5，未过门槛/否决）。"""
    p = by_slug(slug)
    return sum(WEIGHTS[k] * p["dims"][k] for k in WEIGHTS) / 100.0


def final(slug):
    """最终综合分（0-5，应用硬门槛封顶与一票否决封顶，四舍五入到 0.1）。"""
    p = by_slug(slug)
    s = weighted(slug)
    if not p["gate"]:
        s = min(s, GATE_CAP)
    if p.get("veto"):
        s = min(s, p["veto"]["cap"])
    return round(s, 1)


def fmt(score):
    """显示用：5.0→'5'，4.2→'4.2'。"""
    return "%g" % score


def score_color(s):
    if s >= 4.5:
        return "#1F7A52"
    if s >= 3.5:
        return "#C77700"
    return "#B23A2F"


def tier(s):
    if s >= 4.5:
        return "真·开箱即用"
    if s >= 3.5:
        return "成品化受限"
    return "需装修/中转"


if __name__ == "__main__":
    print("slug            raw    gate  veto  final  tier")
    for p in PRODUCTS:
        s = p["slug"]
        print("%-14s %5.2f  %-4s  %-4s  %4s  %s" % (
            s, weighted(s), "PASS" if p["gate"] else "FAIL",
            p["veto"]["type"] if p.get("veto") else "-",
            fmt(final(s)), tier(final(s))))
