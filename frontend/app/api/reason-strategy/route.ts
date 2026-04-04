import { NextResponse } from "next/server"
import { loadReasonJsonFiles } from "@/lib/reasonInputs"

export const dynamic = "force-dynamic"
export const revalidate = 0

function apiBase(): string {
  return (
    process.env.STRATEGY_API_URL?.replace(/\/$/, "") ||
    process.env.NEXT_PUBLIC_STRATEGY_API_URL?.replace(/\/$/, "") ||
    "http://127.0.0.1:8000"
  )
}

/**
 * GET: Prefer FastAPI GET /reason/strategy/latest (matches your last Swagger/Postman POST).
 * If 404, fall back to reading local JSON files and POSTing them.
 */
export async function GET() {
  const base = apiBase()

  try {
    const latestRes = await fetch(`${base}/reason/strategy/latest`, { cache: "no-store" })
    if (latestRes.ok) {
      const data = await latestRes.json()
      return NextResponse.json({
        ok: true,
        source: "latest-post",
        resolvedDir: "",
        data,
        hint: "Showing the last POST /reason/strategy result from the API (Swagger/Postman/UI).",
      })
    }
  } catch {
    /* fall through */
  }

  const inputs = await loadReasonJsonFiles()
  if (!inputs) {
    return NextResponse.json(
      {
        ok: false,
        error:
          "No cached strategy from the API yet (POST /reason/strategy in Swagger first), " +
          "and local proposal.json was not found. Set BACKEND_REASON_DIR or keep ignisia/backend/reason/*.json.",
        cwd: process.cwd(),
      },
      { status: 404 },
    )
  }

  try {
    const res = await fetch(`${base}/reason/strategy`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ proposal: inputs.proposal, external: inputs.external }),
      cache: "no-store",
    })
    const text = await res.text()
    if (!res.ok) {
      return NextResponse.json(
        { ok: false, error: `FastAPI ${res.status}`, detail: text.slice(0, 500), resolvedDir: inputs.resolvedDir },
        { status: 502 },
      )
    }
    let data: unknown
    try {
      data = JSON.parse(text)
    } catch {
      return NextResponse.json({ ok: false, error: "Invalid JSON from FastAPI", detail: text.slice(0, 200) }, { status: 502 })
    }
    return NextResponse.json({
      ok: true,
      source: "api-post-files",
      resolvedDir: inputs.resolvedDir,
      data,
      hint: "No prior API POST in this server session; used local JSON files + POST.",
    })
  } catch (e) {
    const msg = e instanceof Error ? e.message : "fetch failed"
    return NextResponse.json(
      { ok: false, error: msg, hint: `Is uvicorn running at ${base}?`, resolvedDir: inputs.resolvedDir },
      { status: 502 },
    )
  }
}

/**
 * POST body: { "proposal": {...}, "external": {...} } → forwards to FastAPI (same as Swagger).
 */
export async function POST(req: Request) {
  let body: unknown
  try {
    body = await req.json()
  } catch {
    return NextResponse.json({ ok: false, error: "Invalid JSON body" }, { status: 400 })
  }
  if (!body || typeof body !== "object") {
    return NextResponse.json({ ok: false, error: "Body must be a JSON object" }, { status: 400 })
  }
  const b = body as Record<string, unknown>
  if (!b.proposal || !b.external) {
    return NextResponse.json(
      { ok: false, error: 'Body must include "proposal" and "external" objects' },
      { status: 400 },
    )
  }

  const base = apiBase()
  try {
    const res = await fetch(`${base}/reason/strategy`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ proposal: b.proposal, external: b.external }),
      cache: "no-store",
    })
    const text = await res.text()
    if (!res.ok) {
      return NextResponse.json(
        { ok: false, error: `FastAPI ${res.status}`, detail: text.slice(0, 500) },
        { status: 502 },
      )
    }
    let data: unknown
    try {
      data = JSON.parse(text)
    } catch {
      return NextResponse.json({ ok: false, error: "Invalid JSON from FastAPI", detail: text.slice(0, 200) }, { status: 502 })
    }
    return NextResponse.json({
      ok: true,
      source: "api-post-body",
      data,
      hint: "Computed from JSON you submitted; also stored as latest on the server.",
    })
  } catch (e) {
    const msg = e instanceof Error ? e.message : "fetch failed"
    return NextResponse.json({ ok: false, error: msg, hint: `Is uvicorn running at ${base}?` }, { status: 502 })
  }
}
