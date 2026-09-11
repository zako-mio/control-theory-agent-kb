# -*- coding: utf-8 -*-
"""snapshot_opencode_custom.py — 采集 ~/.config/opencode 自改造配置的脱敏快照（证据留档）

安全约束（契约 §7 红线）：
  - 只读源配置，绝不修改源文件
  - 密钥/env 引用统一 <REDACTED>；opencode.env（含真实密钥）一律不拷贝
  - 输出到 07-checkpoint/opencode-custom-snapshot/
"""
import os, re, json, hashlib, sys
sys.stdout.reconfigure(encoding='utf-8')

SRC = os.path.expanduser("~/.config/opencode")
DST = "/home/zako-mio/opencode/archive/Mission-file/2026-09/0907-控制理论Agent设计知识库/07-checkpoint/opencode-custom-snapshot"
os.makedirs(DST, exist_ok=True)

# 允许拷贝的文本文件（相对 SRC）
FILES = [
    "opencode.jsonc",
    "MEMORY.md",
    "command/reflection.md",
    "command/arch.md",
    "instructions/auto-mode.md",
    "instructions/search-behavior.md",
    "instructions/architecture-behavior.md",
    "instructions/browser-management.md",
    "instructions/downloads.md",
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

# agent / mcp 列表（JSONC 解析）
agents, mcps = [], []
try:
    cfg = strip_jsonc(open(os.path.join(SRC, "opencode.jsonc"), encoding="utf-8").read())
    cfg = re.sub(r',\s*([}\]])', r'\1', cfg)  # 去尾逗号
    d = json.loads(cfg)
    agents = list(d.get("agent", {}).keys())
    mcps = list(d.get("mcp", {}).keys())
except Exception as e:
    print("warn:", e)
inventory["agents"] = agents
inventory["mcp"] = mcps

open(os.path.join(DST, "inventory.json"), "w", encoding="utf-8").write(
    json.dumps(inventory, ensure_ascii=False, indent=2))
open(os.path.join(DST, "manifest.json"), "w", encoding="utf-8").write(
    json.dumps({"source": "~/.config/opencode", "note": "脱敏快照；opencode.env 不拷贝",
                "files": manifest}, ensure_ascii=False, indent=2))

print("快照完成 ->", DST)
print("文件数:", sum(1 for x in manifest if x.get("status") != "missing"))
print("agents:", agents)
print("mcp:", mcps)
print("skills:", len(inventory["skills"]), "legacy_skill:", len(inventory["legacy_skill"]))
