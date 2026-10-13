# -*- coding: utf-8 -*-
"""snapshot_opencode_custom.py — 采集 ~/.config/opencode 自改造配置的脱敏快照（证据留档）

安全约束（契约 §7 红线）：
  - 只读源配置，绝不修改源文件
  - 密钥/env 引用统一 <REDACTED>；opencode.env（含真实密钥）一律不拷贝
  - 输出到 07-checkpoint/opencode-custom-snapshot/

版本：v1.4（2026-10-11 刷新）
  - 新增 collected_at 时间戳（v1.3 快照缺时间戳，无法自证采集时点）
  - FILES 随实机漂移更新：+command/rd.md、+instructions/requirement-discovery-behavior.md、
    +instructions/agent-protocol.md、+plugins/*.ts；−instructions/downloads.md（实机已退役）
  - inventory 新增：skills_disabled / instructions_registered / providers / model /
    subagent_depth / compaction / permission_keys（只报键名与结构，不含密钥值）
  - 覆盖前把既有 inventory.json 归档为 inventory-v1.3.json（一次，用于跨版本对账）
"""
import os, re, json, hashlib, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

SRC = os.path.expanduser("~/.config/opencode")
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "opencode-custom-snapshot")  # ★ 本地化：本目录由本文件位置推导
os.makedirs(DST, exist_ok=True)
COLLECTED_AT = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

# 允许拷贝的文本文件（相对 SRC）
FILES = [
    "opencode.jsonc",
    "MEMORY.md",
    "command/reflection.md",
    "command/arch.md",
    "command/rd.md",
    "instructions/auto-mode.md",
    "instructions/search-behavior.md",
    "instructions/architecture-behavior.md",
    "instructions/browser-management.md",
    "instructions/requirement-discovery-behavior.md",
    "instructions/agent-protocol.md",
    "plugins/system-date-transform.ts",
    "plugins/notify-on-pause.ts",
]

def redact(text: str) -> str:
    # 1) 常见密钥字面量
    text = re.sub(r'(?i)(sk-[A-Za-z0-9_\-]{6,})', '<REDACTED_KEY>', text)
    text = re.sub(r'(?i)(Bearer\s+)[A-Za-z0-9_\-\.]{8,}', r'\1<REDACTED>', text)
    # 2) JSON 字段形式 apiKey/token/secret/password（保留 {env:...} 引用）
    def _f(m):
        val = m.group(2)
        if val.strip().startswith("{env:"):
            return m.group(1) + val + m.group(3)
        return m.group(1) + "<REDACTED>" + m.group(3)
    text = re.sub(r'("(?:apiKey|api_key|token|secret|password|accessKey)"\s*:\s*")([^"]*)(")',
                  _f, text, flags=re.I)
    return text

def sha16(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:16]

def listdir(rel: str):
    p = os.path.join(SRC, rel)
    return sorted(os.listdir(p)) if os.path.isdir(p) else []

manifest = []
for rel in FILES:
    src = os.path.join(SRC, rel)
    if not os.path.isfile(src):
        manifest.append({"path": "~/.config/opencode/" + rel, "status": "missing"})
        continue
    raw = open(src, "rb").read()
    text = raw.decode("utf-8", errors="replace")
    red = redact(text)
    out = os.path.join(DST, rel.replace("/", "__"))
    open(out, "w", encoding="utf-8").write(red)
    manifest.append({
        "path": "~/.config/opencode/" + rel,
        "bytes": len(raw),
        "sha256_16": sha16(raw),
        "snapshot": os.path.basename(out),
        "redacted_occurrences": len(re.findall(r'<REDACTED', red)),
    })

# 目录清单（仅名称，不拷贝内容）
inventory = {
    "skills": listdir("skills"),
    "skills_disabled": listdir("skills/disabled"),
    "legacy_skill": listdir("skill"),
    "plugins": listdir("plugins"),
    "tools": listdir("tools"),
    "scripts": listdir("scripts"),
    "command": listdir("command"),
    "instructions": listdir("instructions"),
}

def strip_jsonc(s: str) -> str:
    """去 // 与 /* */ 注释（跳过字符串内部）。"""
    out, in_str, esc, i = [], False, False, 0
    while i < len(s):
        c = s[i]
        if in_str:
            out.append(c)
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == '"': in_str = False
            i += 1; continue
        if c == '"': in_str = True; out.append(c); i += 1; continue
        if c == '/' and i + 1 < len(s) and s[i + 1] == '/':
            while i < len(s) and s[i] != '\n': i += 1
            continue
        if c == '/' and i + 1 < len(s) and s[i + 1] == '*':
            i += 2
            while i + 1 < len(s) and not (s[i] == '*' and s[i + 1] == '/'): i += 1
            i += 2; continue
        out.append(c); i += 1
    return ''.join(out)

# agent / mcp / provider / 结构（JSONC 解析）
agents, mcps, providers, cfg_struct = [], [], [], {}
try:
    cfg = strip_jsonc(open(os.path.join(SRC, "opencode.jsonc"), encoding="utf-8").read())
    cfg = re.sub(r',\s*([}\]])', r'\1', cfg)  # 去尾逗号
    d = json.loads(cfg)
    agents = list(d.get("agent", {}).keys())
    mcps = list(d.get("mcp", {}).keys())
    providers = list(d.get("provider", {}).keys())
    cfg_struct = {
        "top_level_keys": sorted(d.keys()),
        "model": d.get("model"),
        "small_model": d.get("small_model"),
        "subagent_depth": d.get("subagent_depth"),
        "compaction_keys": sorted((d.get("compaction") or {}).keys()),
        "instructions_registered": d.get("instructions"),
        "permission_keys": sorted((d.get("permission") or {}).keys()),
        "mcp_enabled": [k for k, v in (d.get("mcp") or {}).items()
                        if isinstance(v, dict) and v.get("enabled") is not False],
        "provider_apikey_env_names": sorted({
            str(v.get("options", {}).get("apiKey", "")) for v in (d.get("provider") or {}).values()
            if isinstance(v, dict) and v.get("options", {}).get("apiKey")
        }),
    }
except Exception as e:
    print("warn:", e)

inventory["agents"] = agents
inventory["mcp"] = mcps
inventory["providers"] = providers
inventory["config"] = cfg_struct
inventory["collected_at"] = COLLECTED_AT

# 覆盖前归档既有 inventory（一次）
inv_path = os.path.join(DST, "inventory.json")
arch_path = os.path.join(DST, "inventory-v1.3.json")
if os.path.isfile(inv_path) and not os.path.isfile(arch_path):
    old = json.load(open(inv_path, encoding="utf-8"))
    old["_archived_note"] = "v1.3 快照（2026-09-11 采集）的 inventory，归档以支持跨版本对账"
    open(arch_path, "w", encoding="utf-8").write(json.dumps(old, ensure_ascii=False, indent=2))
    print("归档旧 inventory ->", os.path.basename(arch_path))

open(inv_path, "w", encoding="utf-8").write(json.dumps(inventory, ensure_ascii=False, indent=2))
open(os.path.join(DST, "manifest.json"), "w", encoding="utf-8").write(
    json.dumps({"source": "~/.config/opencode", "collected_at": COLLECTED_AT,
                "note": "脱敏快照；opencode.env 不拷贝；MEMORY.md 已在 .gitignore 排除（仅本地证据）",
                "files": manifest}, ensure_ascii=False, indent=2))

print("快照完成 ->", DST, "@", COLLECTED_AT)
print("文件数:", sum(1 for x in manifest if x.get("status") != "missing"),
      "/", len(FILES), " 缺失:", [x["path"] for x in manifest if x.get("status") == "missing"])
print("agents:", agents)
print("mcp:", mcps)
print("providers:", providers)
print("skills:", len(inventory["skills"]), "disabled:", len(inventory["skills_disabled"]),
      "plugins:", len(inventory["plugins"]))
