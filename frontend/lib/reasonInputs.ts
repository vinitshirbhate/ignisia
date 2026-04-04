import fs from "fs/promises"
import path from "path"

/**
 * Find backend/reason/*.json from common layouts:
 * - cwd = .../ignisia/frontend  -> ../backend/reason
 * - cwd = .../ignisia           -> backend/reason
 * - cwd = .../igni (repo root)  -> ignisia/backend/reason
 * Walks up from cwd a few levels and dedupes paths.
 */
export async function loadReasonJsonFiles(): Promise<{
  proposal: unknown
  external: unknown
  resolvedDir: string
} | null> {
  const envDir = process.env.BACKEND_REASON_DIR?.trim()
  if (envDir) {
    try {
      const dir = path.resolve(envDir)
      const [proposalText, externalText] = await Promise.all([
        fs.readFile(path.join(dir, "proposal.json"), "utf8"),
        fs.readFile(path.join(dir, "external.json"), "utf8"),
      ])
      return {
        proposal: JSON.parse(proposalText),
        external: JSON.parse(externalText),
        resolvedDir: dir,
      }
    } catch {
      /* fall through to discovery */
    }
  }

  const tried = new Set<string>()

  async function tryDir(reasonDir: string): Promise<{ proposal: unknown; external: unknown; resolvedDir: string } | null> {
    const resolved = path.resolve(reasonDir)
    if (tried.has(resolved)) return null
    tried.add(resolved)
    try {
      const [proposalText, externalText] = await Promise.all([
        fs.readFile(path.join(resolved, "proposal.json"), "utf8"),
        fs.readFile(path.join(resolved, "external.json"), "utf8"),
      ])
      return {
        proposal: JSON.parse(proposalText),
        external: JSON.parse(externalText),
        resolvedDir: resolved,
      }
    } catch {
      return null
    }
  }

  let cur = path.resolve(process.cwd())
  for (let i = 0; i < 10; i++) {
    const candidates = [
      path.join(cur, "backend", "reason"),
      path.join(cur, "..", "backend", "reason"),
      path.join(cur, "ignisia", "backend", "reason"),
    ]
    for (const c of candidates) {
      const hit = await tryDir(c)
      if (hit) return hit
    }
    const parent = path.dirname(cur)
    if (parent === cur) break
    cur = parent
  }

  return null
}
