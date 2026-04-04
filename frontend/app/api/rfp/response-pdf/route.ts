import { NextResponse } from "next/server"

export const dynamic = "force-dynamic"
export const revalidate = 0

function pdfApiBase(): string {
  return (
    process.env.PDF_PROPOSAL_API_URL?.replace(/\/$/, "") ||
    process.env.NEXT_PUBLIC_PDF_PROPOSAL_API_URL?.replace(/\/$/, "") ||
    "http://localhost:8100"
  )
}

/**
 * POST { ai_proposal, ai_reason } → pdf_generation FastAPI /api/proposals/pdf-from-rfp
 */
export async function POST(req: Request) {
  let body: unknown
  try {
    body = await req.json()
  } catch {
    return NextResponse.json({ ok: false, error: "Invalid JSON body" }, { status: 400 })
  }
  if (!body || typeof body !== "object" || Array.isArray(body)) {
    return NextResponse.json({ ok: false, error: "Body must be a JSON object" }, { status: 400 })
  }
  const b = body as Record<string, unknown>
  const ap = b.ai_proposal
  const ar = b.ai_reason
  if (!ap || typeof ap !== "object" || Array.isArray(ap)) {
    return NextResponse.json({ ok: false, error: 'Body must include object "ai_proposal"' }, { status: 400 })
  }
  if (!ar || typeof ar !== "object" || Array.isArray(ar)) {
    return NextResponse.json({ ok: false, error: 'Body must include object "ai_reason"' }, { status: 400 })
  }

  const base = pdfApiBase()
  try {
    const res = await fetch(`${base}/api/proposals/pdf-from-rfp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ai_proposal: ap, ai_reason: ar }),
      cache: "no-store",
    })
    if (!res.ok) {
      const text = await res.text()
      return NextResponse.json(
        {
          ok: false,
          error: `PDF service returned ${res.status}`,
          detail: text.slice(0, 800),
          hint: `Expected pdf_generation uvicorn at ${base} (set PDF_PROPOSAL_API_URL if different).`,
        },
        { status: 502 },
      )
    }
    const buf = Buffer.from(await res.arrayBuffer())
    const headers = new Headers()
    headers.set("Content-Type", "application/pdf")
    const cd = res.headers.get("content-disposition")
    if (cd) headers.set("Content-Disposition", cd)
    headers.set("Cache-Control", "no-store")
    return new NextResponse(buf, { headers })
  } catch (e) {
    const msg = e instanceof Error ? e.message : "fetch failed"
    return NextResponse.json(
      { ok: false, error: msg, hint: `Is the PDF API running at ${base}?` },
      { status: 502 },
    )
  }
}
