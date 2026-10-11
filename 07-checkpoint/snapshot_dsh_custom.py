# -*- coding: utf-8 -*-
"""snapshot_dsh_custom.py — 采集 dsh 装配层（dsh-opencode-port bundle + 宿主 profile 增量）的脱敏快照

安全约束（沿用契约 §7 红线）：
  - 只读源配置，绝不修改源文件
  - 密钥/env 引用统一 <REDACTED>；`~/dsh/.env` 与 `~/.dsh/.credentials.yaml` **一律不拷贝**
  - `~/.dsh/sessions/`、`attachments/`、`storages/` 不在采集范围
  - 输出到 07-checkpoint/dsh-custom-snapshot/

采集对象：
  A. bundle：`~/.dsh/presets/opencode/`（cordis.patch.yml / package.json / persona.md /
     README.md / ADAPTATION-NOTES.md / PROVENANCE.md / provenance.json）
  B. 宿主增量：`~/.dsh/profiles/web/{package.json,cordis.patch.yml}`
  C. inventory：preset 表 / worker 别名 / permission 档位 / skill 计数 / provider 键名 / collected_at
"""
import os, re, json, hashlib, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

HOME = os.path.expanduser("~")
BUNDLE = os.path.join(HOME, ".dsh/presets/opencode")
PROFILE = os.path.join(HOME, ".dsh/profiles/web")
SKILLS = os.path.join(HOME, ".dsh/skills/opencode")
DST = "/home/zako-mio/opencode/archive/Mission-file/2026-09/0907-控制理论Agent设计知识库/07-checkpoint/dsh-custom-snapshot"
os.makedirs(DST, exist_ok=True)
COLLECTED_AT = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

# (相对标签, 绝对路径)
FILES = [
    ("bundle/cordis.patch.yml", os.path.join(BUNDLE, "cordis.patch.yml")),
    ("bundle/package.json", os.path.join(BUNDLE, "package.json")),
    ("bundle/persona.md", os.path.join(BUNDLE, "persona.md")),
    ("bundle/README.md", os.path.join(BUNDLE, "README.md")),
    ("bundle/ADAPTATION-NOTES.md", os.path.join(BUNDLE, "ADAPTATION-NOTES.md")),
    ("bundle/PROVENANCE.md", os.path.join(BUNDLE, "PROVENANCE.md")),
    ("bundle/provenance.json", os.path.join(BUNDLE, "provenance.json")),
    ("profile/web-package.json", os.path.join(PROFILE, "package.json")),
    ("profile/web-cordis.patch.yml", os.path.join(PROFILE, "cordis.patch.yml")),
]


def redact(text: str) -> str:
    text = re.sub(r'(?i)(sk-[A-Za-z0-9_\-]{6,})', '<REDACTED_KEY>', text)
    text = re.sub(r'(?i)(Bearer\s+)[A-Za-z0-9_\-\.]{8,}', r'\1<REDACTED>', text)
    # 保留 {env:XXX} / apiKeyEnv 引用名，其余字面量脱敏
    def _f(m):
        val = m.group(2)
        if val.strip().startswith("{env:") or val.strip().startswith("$"):
            return m.group(1) + val + m.group(3)
        return m.group(1) + "<REDACTED>" + m.group(3)
    text = re.sub(r'("(?:apiKey|api_key|apiKeyEnv|token|secret|password|accessKey)"\s*:\s*")([^"]*)(")',
                  _f, text, flags=re.I)
    return text


def sha16(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:16]


manifest = []
texts = {}
for label, path in FILES:
    if not os.path.isfile(path):
        manifest.append({"path": path, "label": label, "status": "missing"})
        continue
    raw = open(path, "rb").read()
    red = redact(raw.decode("utf-8", errors="replace"))
    out = os.path.join(DST, label.replace("/", "__"))
    open(out, "w", encoding="utf-8").write(red)
    texts[label] = red
    manifest.append({
        "path": path, "label": label, "bytes": len(raw), "sha256_16": sha16(raw),
        "snapshot": os.path.basename(out),
        "redacted_occurrences": len(re.findall(r'<REDACTED', red)),
    })

patch = texts.get("bundle/cordis.patch.yml", "")
host = texts.get("profile/web-cordis.patch.yml", "")
bundle_pkg = texts.get("bundle/package.json", "")
host_pkg = texts.get("profile/web-package.json", "")

# --- preset 表（bundle patch 中的三行） ---
presets = []
for m in re.finditer(r'-\s*id:\s*(preset-opencode-[a-z]+)\b', patch):
    pid = m.group(1)
    tail = patch[m.start():m.start() + 1200]
    order = re.search(r'order:\s*(\d+)', tail)
    presets.append({"id": pid, "order": int(order.group(1)) if order else None,
                    "top_level_rows": None})

# --- worker 别名（oc_*） ---
aliases = sorted(set(re.findall(r'\boc_[a-z]+', patch)))
# --- permission 档位 ---
known = ["read-only", "workspace-write", "opencode-plan", "opencode-build", "danger-full-access"]
perm = [k for k in known if k in host or k in patch]

# --- skill 面 ---
# 口径（2026-10-11 实测澄清）：DSH 技能根按 `<root>/<name>/SKILL.md` **一层**扫描
#   ⇒ 主根 = 深度 2 的 SKILL.md 数（45）；`_overlay/<name>/SKILL.md` 是深度 3，属叠加层不计入根条目（6）
#   ⇒ 模型可见 = 主根 − 带 `disable-model-invocation: true` 的件数（45 − 3 = 42，与运行时技能目录实测一致）
skill_dirs, model_invocable_off = [], []
if os.path.isdir(SKILLS):
    for name in sorted(os.listdir(SKILLS)):
        if name == "_overlay":
            continue
        d = os.path.join(SKILLS, name)
        if not os.path.isdir(d):
            continue
        sk = os.path.join(d, "SKILL.md")
        if not os.path.isfile(sk):
            continue
        skill_dirs.append(name)
        try:
            head = open(sk, encoding="utf-8", errors="replace").read(4000)
        except Exception:
            head = ""
        if re.search(r'disable-model-invocation:\s*true', head, re.I):
            model_invocable_off.append(name)
overlay = os.path.join(SKILLS, "_overlay")
overlay_count = 0
if os.path.isdir(overlay):
    overlay_count = sum(1 for n in os.listdir(overlay)
                        if os.path.isfile(os.path.join(overlay, n, "SKILL.md")))

# --- provider 键名（宿主 patch 的 llm-pi-ai 段） ---
providers = sorted(set(re.findall(r'^\s{6,}([a-z0-9][a-z0-9\-_]*):\s*$', host, re.M)))
apikey_envs = sorted(set(re.findall(r'apiKeyEnv:\s*([A-Z0-9_]+)', host)))

inventory = {
    "collected_at": COLLECTED_AT,
    "source": {"bundle": BUNDLE, "profile": PROFILE, "skills": SKILLS},
    "presets": presets,
    "worker_aliases": aliases,
    "permission_presets": perm,
    "skills": {
        "main_root": len(skill_dirs),
        "overlay": overlay_count,
        "skill_md_total": len(skill_dirs) + overlay_count,
        "model_invocable_off": model_invocable_off,
        "model_visible_estimate": len(skill_dirs) - len(model_invocable_off),
    },
    "providers": {"keys_found": providers, "apiKeyEnv_names": apikey_envs},
    "bundle_bundles": re.findall(r'"([^"]*opencode[^"]*)"', host_pkg),
    "notes": [
        "只读采集；~/dsh/.env 与 ~/.dsh/.credentials.yaml 未拷贝",
        "persona 与 bundle README 含本机绝对路径（bundle 自述不可移植）",
        "permission 档位由文本存在性判定（非 YAML 解析），缺 YAML 语义时可回退看原文快照",
    ],
}

open(os.path.join(DST, "inventory.json"), "w", encoding="utf-8").write(
    json.dumps(inventory, ensure_ascii=False, indent=2))
open(os.path.join(DST, "manifest.json"), "w", encoding="utf-8").write(
    json.dumps({"source": "~/.dsh/presets/opencode + ~/.dsh/profiles/web",
                "collected_at": COLLECTED_AT,
                "note": "脱敏快照；.env / credentials / sessions / attachments 均不拷贝",
                "files": manifest}, ensure_ascii=False, indent=2))

print("快照完成 ->", DST, "@", COLLECTED_AT)
print("文件数:", sum(1 for x in manifest if x.get("status") != "missing"), "/", len(FILES),
      " 缺失:", [x["label"] for x in manifest if x.get("status") == "missing"])
print("presets:", presets)
print("worker_aliases:", aliases)
print("permission_presets:", perm)
print("skills:", inventory["skills"])
print("apiKeyEnv_names:", apikey_envs)
