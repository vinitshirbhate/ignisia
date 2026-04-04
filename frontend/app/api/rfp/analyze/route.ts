import { NextResponse } from "next/server"

export const dynamic = "force-dynamic"
export const maxDuration = 300

function docRagBase(): string {
  return (process.env.DOC_RAG_URL || process.env.NEXT_PUBLIC_DOC_RAG_URL || "http://127.0.0.1:8001").replace(
    /\/$/,
    "",
  )
}

/**
 * Proxies PDF upload to doc_rag FastAPI /analyze-rfp (PDF → LLM → optional pricing agent on :9000).
 */
export async function POST(req: Request) {
  const form = await req.formData()
  const file = form.get("file")
  if (!file || !(file instanceof Blob)) {
    return NextResponse.json({ ok: false, error: "Missing file field (PDF)." }, { status: 400 })
  }

  const outbound = new FormData()
  outbound.append("file", file, (file as File).name || "rfp.pdf")

  const base = docRagBase()
  const url = `${base}/analyze-rfp`

  try {
    const res = await fetch(url, {
      method: "POST",
      body: outbound,
      cache: "no-store",
      signal: AbortSignal.timeout(300_000),
    })
    const text = await res.text()
    if (!res.ok) {
      let detail: string = text.slice(0, 800)
      try {
        const j = JSON.parse(text) as { detail?: unknown }
        if (j.detail != null) detail = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail)
      } catch {
        /* keep text */
      }
      return NextResponse.json(
        { ok: false, error: `doc_rag ${res.status}`, detail, docRagUrl: base },
        { status: 502 },
      )
    }
    let data: unknown
    try {
      data = JSON.parse(text)
    } catch {
      return NextResponse.json({ ok: false, error: "Invalid JSON from doc_rag", detail: text.slice(0, 200) }, { status: 502 })
    }
    return NextResponse.json({ ok: true, data })
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Request failed"
    return NextResponse.json(
      {
        ok: false,
        error: msg,
        hint: `Ensure doc_rag is running: uvicorn app:app --port 8001 (and pricing agent on 9000 if pricing questions exist). Target: ${url}`,
      },
      { status: 502 },
    )
  }
}
