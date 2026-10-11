// notify-on-pause.ts — opencode global plugin: desktop notification on session pause.
// Contract: spec/P3-IMPLEMENTATION-INTERFACES.md (§0.3 §2.1 §3.1-§3.4), spec/P2-IMPLEMENTATION-CONTRACT.md §2/§7.
// Hard constraints (P3 §3.1): C1 factory body zero async-wait, all fs synchronous;
//   C2 config only from ~/.config/opencode/notify.json; C3 fire-and-forget separated spawn + fail-open.
// Shape: single named export OpencodeNotify(ctx) => { event }. Single file. No relative import.
// Any failure anywhere is swallowed inside the hook: a request is never broken.

const EV_QUESTION = "question.asked"
const EV_PERMISSION = "permission.asked"
const EV_IDLE_TRANSITION = "idle-transition"
const ALLOWED_EVENTS = [EV_QUESTION, EV_PERMISSION, EV_IDLE_TRANSITION]
const ERROR_WINDOW_MS = 30000
// Only a genuine abort suppresses the following idle.  Measured payload (T-P13):
//   session.error -> {error:{name:"MessageAbortedError",data:{message:"Aborted"}}}
// A non-abort error therefore does NOT suppress: the user is still "stopped" and
// wants to know (requirement-owner decision, T-P23).  The window is additionally
// cleared as soon as a new turn starts for that sid (see the session.status
// branch), which removes the measured false negative (T-P19): previously an
// abort followed by a *new* completed turn within 30 s was silently suppressed.
const ABORT_ERROR_NAME = "MessageAbortedError"
const IN_FLIGHT_MAX = 4

const LABEL_QUESTION = "提问"
const LABEL_PERMISSION = "权限请求"
const LABEL_IDLE = "轮次结束"

function cacheDir(): string {
  const os = require("node:os")
  const path = require("node:path")
  return path.join(os.homedir(), ".cache", "opencode")
}

// Test seam (documented in P3 §3.2): OPENCODE_NOTIFY_LOG overrides the log path so
// gates can run without mutating the live log. Production default is unchanged.
function pluginLogPath(): string {
  const path = require("node:path")
  const env = process.env.OPENCODE_NOTIFY_LOG
  if (typeof env === "string" && env.length > 0) return env
  return path.join(cacheDir(), "notify-plugin.log")
}

// Test seam (documented in P3 §3.2): OPENCODE_NOTIFY_CONFIG overrides the config FILE PATH only.
// The config source stays "a dedicated plugin file, read synchronously" (ADR-004 decision B).
function configFilePath(): string {
  const os = require("node:os")
  const path = require("node:path")
  const env = process.env.OPENCODE_NOTIFY_CONFIG
  if (typeof env === "string" && env.length > 0) return env
  return path.join(os.homedir(), ".config", "opencode", "notify.json")
}

function receiptWsPath(): string {
  const path = require("node:path")
  return path.join(cacheDir(), "notify-receipts.log")
}

function rec(kind: string, fields: any): any {
  return Object.assign(
    { ts: new Date().toISOString(), pid: process.pid, kind: kind },
    fields || {},
  )
}

function writeLog(obj: any): void {
  try {
    const fs = require("node:fs")
    const path = require("node:path")
    const p = pluginLogPath()
    fs.mkdirSync(path.dirname(p), { recursive: true })
    fs.appendFileSync(p, JSON.stringify(obj) + "\n")
  } catch {
    // logging is best-effort only
  }
}

function linuxToWindows(p: any): any {
  try {
    if (typeof p !== "string" || p.length === 0) return p
    if (/^[A-Za-z]:[\\/]/.test(p)) return p.replace(/\//g, "\\")
    if (p.indexOf("\\\\") === 0) return p
    const m = /^\/mnt\/([A-Za-z])\/(.*)$/.exec(p)
    if (m) return m[1].toUpperCase() + ":\\" + m[2].replace(/\//g, "\\")
    const rest = p.replace(/\//g, "\\")
    const distro = process.env.WSL_DISTRO_NAME || "Ubuntu"
    return "\\\\wsl.localhost\\" + distro + (rest.charAt(0) === "\\" ? rest : "\\" + rest)
  } catch {
    return p
  }
}

// P3 §3.4 asks for `cwd = <exe 所在 Windows 目录>` to avoid interop cwd jitter.
// Measured in this WSL2 host: Bun.posix_spawn rejects a backslash/UNC cwd string
// (ENOENT before exec), so the spawnable form of "the exe's directory" is the
// Linux-side dirname (e.g. /mnt/c/... -> the same Windows dir via interop).
function cwdFor(exe: any): any {
  try {
    if (typeof exe !== "string" || exe.length === 0) return undefined
    if (/^[A-Za-z]:[\\/]/.test(exe) || exe.indexOf("\\\\") === 0) return undefined
    const path = require("node:path")
    return path.dirname(exe)
  } catch {
    return undefined
  }
}

// P3 §0.3 resolution order: (1) configured value (2) OPENCODE_NOTIFY_EXE
// (3) /mnt/c/Users/*/AppData/Local/opencode-notify/opencode-notify.exe first existing
// (4) ~/.local/share/opencode-notify/opencode-notify.exe
function resolveNotifierPath(configured: any): any {
  try {
    if (typeof configured === "string" && configured.length > 0) return configured
    const env = process.env.OPENCODE_NOTIFY_EXE
    if (typeof env === "string" && env.length > 0) return env
    const fs = require("node:fs")
    try {
      const users = fs.readdirSync("/mnt/c/Users")
      for (let i = 0; i < users.length; i++) {
        const cand = "/mnt/c/Users/" + users[i] + "/AppData/Local/opencode-notify/opencode-notify.exe"
        if (fs.existsSync(cand)) return cand
      }
    } catch {
      // no Windows mount: fall through
    }
    const os = require("node:os")
    const path = require("node:path")
    return path.join(os.homedir(), ".local", "share", "opencode-notify", "opencode-notify.exe")
  } catch {
    return null
  }
}

function defaultConfig(): any {
  return {
    enabled: true,
    duration_ms: 3000,
    events: [EV_QUESTION, EV_PERMISSION, EV_IDLE_TRANSITION],
    only_when_blurred: true,
    startup_quiet_ms: 5000,
    notifier_path: resolveNotifierPath(""),
  }
}

function validateConfig(raw: any): any {
  try {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return null
    const enabled = (raw as any).enabled
    const duration = (raw as any).duration_ms
    const events = (raw as any).events
    const onlyBlurred = (raw as any).only_when_blurred
    const quiet = (raw as any).startup_quiet_ms
    const notifier = (raw as any).notifier_path
    if (typeof enabled !== "boolean") return null
    if (typeof duration !== "number" || !Number.isInteger(duration) || duration < 3000 || duration > 4000) return null
    if (!Array.isArray(events)) return null
    for (let i = 0; i < events.length; i++) {
      if (typeof events[i] !== "string" || ALLOWED_EVENTS.indexOf(events[i]) === -1) return null
    }
    if (typeof onlyBlurred !== "boolean") return null
    if (typeof quiet !== "number" || !Number.isInteger(quiet) || quiet < 0) return null
    if (typeof notifier !== "string" || notifier.length === 0) return null
    return {
      enabled: enabled,
      duration_ms: duration,
      events: events.slice(),
      only_when_blurred: onlyBlurred,
      startup_quiet_ms: quiet,
      notifier_path: notifier,
    }
  } catch {
    return null
  }
}

function loadConfig(): any {
  try {
    const fs = require("node:fs")
    const file = configFilePath()
    let text: any
    try {
      text = fs.readFileSync(file, "utf8")
    } catch (e: any) {
      if (e && e.code === "ENOENT") return { config: defaultConfig(), source: "default" }
      return { config: defaultConfig(), source: "file-invalid" }
    }
    let raw: any
    try {
      raw = JSON.parse(text)
    } catch {
      return { config: defaultConfig(), source: "file-invalid" }
    }
    const cfg = validateConfig(raw)
    if (!cfg) return { config: defaultConfig(), source: "file-invalid" }
    return { config: cfg, source: "file" }
  } catch {
    return { config: defaultConfig(), source: "file-invalid" }
  }
}

function hasSid(m: any, sid: any): boolean {
  if (sid === null || sid === undefined) return false
  let found = false
  m.forEach((v: any) => {
    if (v === sid) found = true
  })
  return found
}

export const OpencodeNotify = async (ctx: any) => {
  const instanceStartTs = Date.now()
  const loaded = loadConfig()
  const config = loaded.config

  writeLog(
    rec("load", {
      config_source: loaded.source,
      config: {
        enabled: config.enabled,
        duration_ms: config.duration_ms,
        events: config.events,
        only_when_blurred: config.only_when_blurred,
        startup_quiet_ms: config.startup_quiet_ms,
        notifier_path: config.notifier_path,
      },
    }),
  )

  const lastStatus = new Map() // sid -> "busy" | "retry" | "idle"
  const pendingQ = new Map() // requestID -> sid
  const pendingP = new Map() // requestID -> sid
  const errWindow = new Map() // sid -> ts
  let inFlight = 0
  let receiptPending = false

  const readReceipt = () => {
    try {
      const fs = require("node:fs")
      let text = ""
      try {
        text = fs.readFileSync(receiptWsPath(), "utf8")
      } catch {
        text = ""
      }
      const raw = text.length === 0 ? [] : text.split(/\r?\n/)
      const lines = raw.filter((l: string) => l.length > 0)
      let lastMode: any = null
      if (lines.length > 0) {
        try {
          const parsed = JSON.parse(lines[lines.length - 1])
          lastMode = parsed && typeof parsed === "object" ? parsed.mode ?? null : null
        } catch {
          lastMode = null
        }
      }
      writeLog(rec("receipt_read", { lines: lines.length, last_mode: lastMode }))
    } catch {
      writeLog(rec("receipt_read", { lines: 0, last_mode: null }))
    }
  }

  const buildArgs = (exe: any, label: string, sid: any): any => {
    const path = require("node:path")
    const title = "opencode · " + (ctx && typeof ctx.directory === "string" ? path.basename(ctx.directory) : "")
    const body = label + " · " + (sid === null || sid === undefined ? "" : String(sid))
    const hint = process.env.OPENCODE_NOTIFY_WINDOW_HINT ?? ""
    return [
      exe,
      "--title", title,
      "--body", body,
      "--session-id", sid === null || sid === undefined ? "" : String(sid),
      "--window-hint", hint,
      "--duration-ms", String(config.duration_ms),
      "--only-when-blurred", config.only_when_blurred ? "1" : "0",
      // ADR-002 call.params declares `urgency` (optional, default "normal").  The
      // notifier implements low/normal/high (accent bar only, never the duration).
      // The plugin forwards the declared default explicitly so that the frozen
      // contract is fully exercised rather than silently half-implemented
      // (G7 reconciliation used to raise a WARN for this).  Mapping event type ->
      // urgency is a deliberate non-goal for now: it would be an event-derived
      // severity classification and is left as an opt-in enhancement (UNVERIFIED).
      "--urgency", "normal",
      "--receipt", linuxToWindows(receiptWsPath()),
    ]
  }

  const notify = (reason: string, sid: any, eventType: string) => {
    const label = reason === "question" ? LABEL_QUESTION : reason === "permission" ? LABEL_PERMISSION : LABEL_IDLE
    try {
      if (!config.enabled) {
        writeLog(rec("decide", { notify: false, why: "disabled", reason: reason, sid: sid, event: eventType }))
        return
      }
      writeLog(rec("decide", { notify: true, reason: reason, why: "hit", sid: sid, event: eventType }))

      if (receiptPending) {
        receiptPending = false
        readReceipt()
      }

      const exe = config.notifier_path
      if (typeof exe !== "string" || exe.length === 0) {
        writeLog(rec("spawn", { ok: false, err: "no_notifier_path" }))
        return
      }

      if (inFlight >= IN_FLIGHT_MAX) {
        writeLog(rec("throttle_drop", { in_flight: inFlight, sid: sid }))
        return
      }

      const args = buildArgs(exe, label, sid)
      const t0 = Date.now()
      const spawnOpts: any = { stdin: "ignore", stdout: "ignore", stderr: "ignore" }
      const cwd = cwdFor(exe)
      if (cwd) spawnOpts.cwd = cwd
      const p = Bun.spawn(args, spawnOpts)
      inFlight += 1
      receiptPending = true
      p.exited.then(
        () => {
          inFlight -= 1
        },
        () => {
          inFlight -= 1
        },
      )
      writeLog(rec("spawn", { ok: true, exe: exe, in_flight: inFlight, spawn_ms: Date.now() - t0 }))
    } catch (e: any) {
      writeLog(rec("spawn", { ok: false, err: String(e && e.message ? e.message : e) }))
    }
  }

  const handleEvent = (ev: any, now: number) => {
    const props = ev.properties && typeof ev.properties === "object" ? ev.properties : {}
    const sid = props.sessionID ?? props.sessionId ?? null
    const type = ev.type

    if (now - instanceStartTs < config.startup_quiet_ms) {
      writeLog(rec("decide", { notify: false, why: "startup_quiet", sid: sid, event: type }))
      return
    }

    if (type === "session.error") {
      const ename = props.error && typeof props.error.name === "string" ? props.error.name : null
      if (ename === ABORT_ERROR_NAME) {
        if (sid !== null && sid !== undefined) errWindow.set(sid, now)
        writeLog(rec("decide", { notify: false, why: "error_abort_window", sid: sid, event: type, err_name: ename }))
      } else {
        writeLog(rec("decide", { notify: false, why: "error_not_abort", sid: sid, event: type, err_name: ename }))
      }
      return
    }

    if (type === EV_QUESTION) {
      if (config.events.indexOf(EV_QUESTION) === -1) {
        writeLog(rec("decide", { notify: false, why: "not_whitelisted", sid: sid, event: type }))
        return
      }
      const rid = props.id ?? props.requestID ?? null
      if (rid !== null && pendingQ.has(rid)) {
        writeLog(rec("decide", { notify: false, why: "dup", sid: sid, event: type }))
        return
      }
      if (rid !== null) pendingQ.set(rid, sid)
      notify("question", sid, type)
      return
    }

    if (type === EV_PERMISSION) {
      if (config.events.indexOf(EV_PERMISSION) === -1) {
        writeLog(rec("decide", { notify: false, why: "not_whitelisted", sid: sid, event: type }))
        return
      }
      const rid = props.id ?? props.requestID ?? null
      if (rid !== null && pendingP.has(rid)) {
        writeLog(rec("decide", { notify: false, why: "dup", sid: sid, event: type }))
        return
      }
      if (rid !== null) pendingP.set(rid, sid)
      notify("permission", sid, type)
      return
    }

    if (type === "question.replied" || type === "question.rejected") {
      const rid = props.requestID ?? props.id ?? null
      if (rid !== null) pendingQ.delete(rid)
      return
    }

    if (type === "permission.replied") {
      const rid = props.requestID ?? props.id ?? null
      if (rid !== null) pendingP.delete(rid)
      return
    }

    if (type === "session.status") {
      if (config.events.indexOf(EV_IDLE_TRANSITION) === -1) {
        writeLog(rec("decide", { notify: false, why: "not_whitelisted", sid: sid, event: type }))
        return
      }
      const status = props.status && typeof props.status.type === "string" ? props.status.type : null
      const prev = sid === null || sid === undefined ? undefined : lastStatus.get(sid)
      if (sid !== null && sid !== undefined) lastStatus.set(sid, status)
      // A new turn supersedes a stale abort window (fixes the measured false
      // negative T-P19: abort -> new turn completed within 30 s used to be
      // silently suppressed).
      if ((status === "busy" || status === "retry") && sid !== null && sid !== undefined && errWindow.has(sid)) {
        errWindow.delete(sid)
      }

      let why: any = null
      if (prev === undefined || prev === null) {
        why = "not_falling_edge"
      } else if (prev === "idle" && status === "idle") {
        why = "idle_to_idle"
      } else if ((prev === "busy" || prev === "retry") && (status === "busy" || status === "retry")) {
        why = "busy_to_busy"
      } else if (!((prev === "busy" || prev === "retry") && status === "idle")) {
        why = "not_falling_edge"
      }
      if (why !== null) {
        writeLog(rec("decide", { notify: false, why: why, sid: sid, event: type }))
        return
      }

      if (sid !== null && sid !== undefined && errWindow.has(sid) && now - errWindow.get(sid) < ERROR_WINDOW_MS) {
        writeLog(rec("decide", { notify: false, why: "error_window", sid: sid, event: type }))
        return
      }
      if (hasSid(pendingQ, sid) || hasSid(pendingP, sid)) {
        writeLog(rec("decide", { notify: false, why: "pending_question", sid: sid, event: type }))
        return
      }
      notify("idle", sid, type)
      return
    }

    writeLog(rec("decide", { notify: false, why: "not_in_listen_face", sid: sid, event: type }))
  }

  const hook = (input: any) => {
    try {
      const ev = input && input.event ? input.event : null
      if (!ev || typeof ev.type !== "string") return
      handleEvent(ev, Date.now())
    } catch {
      // fail-open: never throw into the host hook
    }
  }

  return { event: hook }
}
