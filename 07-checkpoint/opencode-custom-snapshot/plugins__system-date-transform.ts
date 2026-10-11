// V4-C04 prefix-cache governance plugin (opencode 1.18.30 runtime).
// 1) Strip `Today's date:` from the system prompt so system+tools bytes stay
//    stable across days (prefix cache).
// 2) Reinject the current date into the LAST user message so the model still sees it.
// Fail-open: every hook swallows its own exceptions; a request is never broken.
//
// Install path (global): ~/.config/opencode/plugins/system-date-transform.ts
//   (scanner globs {plugin,plugins}/*.{ts,js} under each config directory)
// Project path: <project>/.opencode/plugin/system-date-transform.ts
//
// Reinjection is idempotent: any previously injected marker is removed before
// appending, so a reused/persisted part cannot accumulate markers across steps.

const DATE_LINE = /\n[ \t]*Today's date:[^\n]*/g
const INJECTED = /\n?\[Current date: [^\]]*\]/g

function log(line: string) {
  try {
    const fs = require("node:fs")
    const os = require("node:os")
    const path = require("node:path")
    const dir = path.join(os.homedir(), ".cache", "opencode")
    fs.mkdirSync(dir, { recursive: true })
    fs.appendFileSync(path.join(dir, "plugin-system-date.log"), line + "\n")
  } catch {
    // logging is best-effort only
  }
}

export const SystemDateTransform = async (_ctx: any) => ({
  "experimental.chat.messages.transform": async (_input: any, output: any) => {
    try {
      const msgs = output?.messages
      if (!Array.isArray(msgs)) return
      const injection = "\n[Current date: " + new Date().toDateString() + "]"
      for (let i = msgs.length - 1; i >= 0; i--) {
        const m = msgs[i]
        if (!m || !m.info || m.info.role !== "user" || !Array.isArray(m.parts)) continue
        let target: any = null
        for (let j = m.parts.length - 1; j >= 0; j--) {
          const p = m.parts[j]
          if (p && p.type === "text" && typeof p.text === "string") {
            target = p
            break
          }
        }
        if (target) {
          target.text = String(target.text).replace(INJECTED, "") + injection
        } else {
          m.parts.push({ type: "text", text: injection.slice(1) })
        }
        log("messages-transform: injected " + injection.trim())
        return
      }
    } catch (e) {
      log("messages-transform-error " + String(e))
    }
  },
  "experimental.chat.system.transform": async (_input: any, output: any) => {
    try {
      const sys = output?.system
      if (!Array.isArray(sys)) return
      for (let i = 0; i < sys.length; i++) {
        if (typeof sys[i] === "string" && sys[i].includes("Today's date:")) {
          sys[i] = sys[i].replace(DATE_LINE, "")
        }
      }
    } catch (e) {
      log("system-transform-error " + String(e))
    }
  },
})
