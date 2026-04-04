"use client"

import { useCallback, useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  Target,
  Activity,
  Lightbulb,
  ArrowRight,
  TrendingUp,
  AlertTriangle,
  RefreshCw,
  FileDown,
} from "lucide-react"
import { RFP_ANALYZE_STORAGE_KEY } from "@/lib/rfpTypes"

type StrategyResponse = {
  strategy: string
  financials: {
    estimated_cost: number
    recommended_bid_price: number
    expected_margin_percent: number
    competitor_price: number
    price_difference_percent: number
  }
  decision: {
    price_strategy: string
    reason: string
  }
  win_probability: number
  risk_score: string
  strategic_actions: { action: string; impact: string }[]
  positioning: { type: string; message: string }
  scenario_comparison: {
    aggressive_pricing: { bid_price: number; margin: number; result: string }
    balanced_pricing: { bid_price: number; margin: number; result: string }
    value_based: { bid_price: number; margin: number; result: string }
  }
  explanation: string
  confidence_score: number
}

function formatCurrency(amount: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount)
}

export function AIReasonContent() {
  const [data, setData] = useState<StrategyResponse | null>(null)
  const [source, setSource] = useState<string>("")
  const [hint, setHint] = useState<string>("")
  const [resolvedDir, setResolvedDir] = useState<string>("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshTick, setRefreshTick] = useState(0)

  const [formProposal, setFormProposal] = useState("")
  const [formExternal, setFormExternal] = useState("")
  const [formBusy, setFormBusy] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)
  const [pdfBusy, setPdfBusy] = useState(false)
  const [pdfError, setPdfError] = useState<string | null>(null)

  const loadFromApi = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch("/api/reason-strategy", { cache: "no-store" })
      const payload = await res.json()
      if (!res.ok || !payload.ok) {
        setError(
          typeof payload.error === "string" ? payload.error : `Request failed (${res.status})`,
        )
        if (payload.detail) {
          setError((e) => (e ? `${e} — ${payload.detail}` : String(payload.detail)))
        }
        if (payload.cwd) setResolvedDir(String(payload.cwd))
        if (payload.resolvedDir) setResolvedDir(String(payload.resolvedDir))
        setData(null)
        setHint("")
        return
      }
      setData(payload.data as StrategyResponse)
      setSource(String(payload.source ?? ""))
      setHint(typeof payload.hint === "string" ? payload.hint : "")
      setResolvedDir(String(payload.resolvedDir ?? ""))
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load strategy")
      setData(null)
      setHint("")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadFromApi()
  }, [refreshTick, loadFromApi])

  const refresh = () => setRefreshTick((t) => t + 1)

  const generateResponsePdf = async () => {
    if (!data) return
    setPdfError(null)
    setPdfBusy(true)
    try {
      const raw = typeof window !== "undefined" ? sessionStorage.getItem(RFP_ANALYZE_STORAGE_KEY) : null
      if (!raw) {
        setPdfError("No RFP analyze data in this browser. Run an RFP from the home flow first, then open this page.")
        return
      }
      let ai_proposal: unknown
      try {
        ai_proposal = JSON.parse(raw) as unknown
      } catch {
        setPdfError("Stored RFP data is not valid JSON. Re-run analyze from the proposal flow.")
        return
      }
      if (!ai_proposal || typeof ai_proposal !== "object") {
        setPdfError("Stored RFP payload is invalid.")
        return
      }

      const res = await fetch("/api/rfp/response-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ai_proposal, ai_reason: data }),
      })
      const ct = res.headers.get("content-type") || ""
      if (!res.ok) {
        if (ct.includes("application/json")) {
          const payload = (await res.json()) as { error?: string; detail?: string; hint?: string }
          const parts = [payload.error, payload.detail, payload.hint].filter(Boolean)
          setPdfError(parts.join(" — ") || `Request failed (${res.status})`)
        } else {
          setPdfError(`PDF request failed (${res.status})`)
        }
        return
      }
      const blob = await res.blob()
      const disp = res.headers.get("content-disposition") || ""
      const m = /filename\*?=(?:UTF-8'')?["']?([^"';]+)/i.exec(disp)
      const name = m?.[1]?.trim() || "rfp-response.pdf"
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = name
      a.rel = "noopener"
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
    } catch (e) {
      setPdfError(e instanceof Error ? e.message : "PDF download failed")
    } finally {
      setPdfBusy(false)
    }
  }

  const submitJson = async () => {
    setFormError(null)
    setFormBusy(true)
    try {
      let proposal: unknown
      let external: unknown
      try {
        proposal = JSON.parse(formProposal || "{}")
      } catch {
        setFormError("Proposal field: invalid JSON")
        return
      }
      try {
        external = JSON.parse(formExternal || "{}")
      } catch {
        setFormError("External field: invalid JSON")
        return
      }
      const res = await fetch("/api/reason-strategy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ proposal, external }),
      })
      const payload = await res.json()
      if (!res.ok || !payload.ok) {
        setFormError(
          typeof payload.error === "string" ? payload.error : `POST failed (${res.status})`,
        )
        if (payload.detail) setFormError((e) => `${e} — ${payload.detail}`)
        return
      }
      setData(payload.data as StrategyResponse)
      setSource(String(payload.source ?? "api-post-body"))
      setHint(typeof payload.hint === "string" ? payload.hint : "")
      setResolvedDir("")
      setError(null)
    } catch (e) {
      setFormError(e instanceof Error ? e.message : "Submit failed")
    } finally {
      setFormBusy(false)
    }
  }

  const JsonForm = (
    <Card className="border-4 border-dashed border-black/50 bg-white shadow-[4px_4px_0_0_#000]">
      <CardHeader className="border-b-2 border-black/20 pb-2">
        <CardTitle className="text-base font-black uppercase">Send the same body as POST /reason/strategy</CardTitle>
        <p className="text-sm font-bold text-black/70">
          Paste <code className="rounded bg-black/10 px-1">proposal</code> and{" "}
          <code className="rounded bg-black/10 px-1">external</code> JSON (as in Swagger). This updates the UI and the
          server &quot;latest&quot; cache.
        </p>
      </CardHeader>
      <CardContent className="space-y-3 pt-4">
        <div>
          <label className="text-xs font-black uppercase text-black/60">proposal</label>
          <textarea
            className="mt-1 min-h-[120px] w-full border-2 border-black p-2 font-mono text-sm"
            value={formProposal}
            onChange={(e) => setFormProposal(e.target.value)}
            placeholder='{ "grand_total": ..., "project_summary": ... }'
          />
        </div>
        <div>
          <label className="text-xs font-black uppercase text-black/60">external</label>
          <textarea
            className="mt-1 min-h-[100px] w-full border-2 border-black p-2 font-mono text-sm"
            value={formExternal}
            onChange={(e) => setFormExternal(e.target.value)}
            placeholder='{ "external_factors": {...}, "constraints": {...} }'
          />
        </div>
        {formError ? <p className="text-sm font-bold text-red-600">{formError}</p> : null}
        <Button
          type="button"
          disabled={formBusy}
          onClick={() => void submitJson()}
          className="border-2 border-black font-black uppercase shadow-[4px_4px_0_0_#000]"
        >
          {formBusy ? "Running…" : "Run strategy"}
        </Button>
      </CardContent>
    </Card>
  )

  if (loading) {
    return (
      <main className="flex flex-1 flex-col items-center justify-center gap-6 px-6 py-24">
        <p className="text-lg font-black uppercase text-black">Loading…</p>
        <p className="max-w-md text-center text-sm font-bold text-black/60">
          Fetching last POST /reason/strategy from FastAPI (or local JSON fallback).
        </p>
      </main>
    )
  }

  if (error || !data) {
    return (
      <main className="flex flex-1 flex-col items-center justify-center gap-8 px-6 py-16">
        <Card className="max-w-lg border-4 border-black shadow-[8px_8px_0_0_#000]">
          <CardHeader className="border-b-[3px] border-black bg-[#ffdc5c]">
            <CardTitle className="flex items-center gap-2 font-black uppercase">
              <AlertTriangle className="h-6 w-6" />
              Nothing to show yet
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 pt-6 font-bold text-black/80">
            <p>{error}</p>
            <p className="text-sm">
              <strong className="uppercase">Workflow:</strong> In Swagger, call{" "}
              <code className="rounded bg-black/10 px-1">POST /reason/strategy</code> once, then press{" "}
              <strong>Refresh</strong> below — the UI reads{" "}
              <code className="rounded bg-black/10 px-1">GET /reason/strategy/latest</code> on the same Python process.
            </p>
            {resolvedDir ? (
              <p className="break-all text-sm font-mono text-black/60">Path hint: {resolvedDir}</p>
            ) : null}
            <div className="flex flex-wrap gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={refresh}
                className="border-2 border-black font-black uppercase"
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Refresh
              </Button>
            </div>
          </CardContent>
        </Card>
        <div className="mx-auto w-full max-w-3xl">{JsonForm}</div>
      </main>
    )
  }

  return (
    <main className="flex-1 px-6 py-12 md:py-16">
      <div className="mx-auto max-w-6xl space-y-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="mb-4 inline-block border-[3px] border-black bg-[#A3E635] p-3 text-4xl font-black uppercase tracking-tight text-black shadow-[6px_6px_0_0_#000] md:text-5xl">
              AI Bid Reasoning
            </h1>
            
            
            {/* {hint ? <p className="mt-1 max-w-3xl text-sm font-bold text-black/60">{hint}</p> : null}
            {resolvedDir ? (
              <p className="mt-1 break-all text-[10px] font-mono text-black/50">Files: {resolvedDir}</p>
            ) : null} */}
          </div>
          <div className="flex shrink-0 flex-wrap items-center gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={refresh}
              className="border-[3px] border-black font-black uppercase shadow-[4px_4px_0_0_#000]"
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>
            <Button
              type="button"
              variant="outline"
              disabled={pdfBusy}
              onClick={() => void generateResponsePdf()}
              className="border-[3px] border-black font-black uppercase shadow-[4px_4px_0_0_#000]"
            >
              <FileDown className="mr-2 h-4 w-4" />
              {pdfBusy ? "Generating…" : "Generate Response PDF"}
            </Button>
          </div>
        </div>

        {pdfError ? (
          <p className="text-sm font-bold text-red-600" role="alert">
            {pdfError}
          </p>
        ) : null}

        <div className="grid gap-8 lg:grid-cols-3">
          <Card className="col-span-1 border-4 border-black shadow-[8px_8px_0_0_#000] lg:col-span-2">
            <CardHeader className="border-b-[3px] border-black pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Target className="h-8 w-8 text-black" strokeWidth={2.5} />
                  <CardTitle className="text-2xl font-black uppercase text-black">Recommended Strategy</CardTitle>
                </div>
                <div className="border-[3px] border-black bg-[#A3E635] px-3 py-1 text-sm font-black uppercase shadow-[2px_2px_0_0_#000]">
                  {Math.round(data.confidence_score * 100)}% Confidence
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6 pt-6">
              <h2 className="bg-[#ffdc5c] text-4xl font-black text-black">{data.strategy}</h2>
              <div className="border-[3px] border-black bg-[#e0f2fe] p-4 shadow-[4px_4px_0_0_#000]">
                <p className="text-xs font-black uppercase text-black/60">Price decision</p>
                <p className="text-lg font-black text-black">{data.decision.price_strategy}</p>
                <p className="mt-2 font-bold text-black/80">{data.decision.reason}</p>
              </div>
              <div className="border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_0_#000]">
                <p className="text-lg font-bold text-black/80">{data.explanation}</p>
              </div>
            </CardContent>
          </Card>

          <div className="flex flex-col gap-6">
            <Card className="flex-1 border-4 border-black bg-white shadow-[8px_8px_0_0_#000]">
              <CardHeader className="border-b-[3px] border-black bg-[#05a3a5] pb-3">
                <CardTitle className="flex items-center gap-2 text-lg font-black uppercase text-black">
                  <Activity className="h-6 w-6" strokeWidth={3} /> Win Prob. & Risk
                </CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col justify-center gap-4 pt-6">
                <div className="flex items-center justify-between">
                  <span className="font-bold uppercase text-black">Win Probability</span>
                  <span className="border-[3px] border-black bg-[#A3E635] px-2 py-1 text-xl font-black shadow-[2px_2px_0_0_#000]">
                    {Math.round(data.win_probability * 100)}%
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-bold uppercase text-black">Risk Score</span>
                  <span className="border-[3px] border-black bg-[#ffdc5c] px-2 py-1 text-xl font-black shadow-[2px_2px_0_0_#000]">
                    {data.risk_score}
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card className="flex-1 border-4 border-black bg-white shadow-[8px_8px_0_0_#000]">
              <CardHeader className="border-b-[3px] border-black bg-[#05a3a5] pb-3">
                <CardTitle className="text-lg font-black uppercase text-black">Financial Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 pt-4">
                <div className="flex justify-between font-bold">
                  <span>Est. Cost</span>
                  <span>{formatCurrency(data.financials.estimated_cost)}</span>
                </div>
                <div className="flex justify-between font-bold">
                  <span>Comp. Price</span>
                  <span>{formatCurrency(data.financials.competitor_price)}</span>
                </div>
                <div className="flex justify-between border-t-[3px] border-black pt-2 text-xl font-black text-black">
                  <span>Our Target</span>
                  <span className="text-[#05a3a5]">{formatCurrency(data.financials.recommended_bid_price)}</span>
                </div>
                <div className="flex items-center justify-between text-sm font-bold uppercase text-black/60">
                  <span>Projected Margin</span>
                  <span>{data.financials.expected_margin_percent}%</span>
                </div>
                <div className="flex items-center justify-between text-sm font-bold uppercase text-black/60">
                  <span>vs competitor</span>
                  <span>
                    {data.financials.price_difference_percent > 0 ? "+" : ""}
                    {data.financials.price_difference_percent}%
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <div className="grid gap-8 lg:grid-cols-2">
          <Card className="border-4 border-black shadow-[8px_8px_0_0_#000]">
            <CardHeader className="border-b-[3px] border-black pb-4">
              <div className="flex items-center gap-2">
                <Lightbulb className="h-6 w-6 text-black" strokeWidth={3} />
                <CardTitle className="text-xl font-black uppercase text-black">Strategic Actions</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4 pt-6">
              {data.strategic_actions.map((action, i) => (
                <div
                  key={i}
                  className="flex gap-4 border-[3px] border-black bg-[#f8fafc] p-4 shadow-[4px_4px_0_0_#000]"
                >
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center border-[3px] border-black bg-[#A3E635] text-lg font-black">
                    {i + 1}
                  </div>
                  <div>
                    <p className="font-bold text-black">{action.action}</p>
                    <div className="mt-2 flex items-center gap-2 text-sm font-bold text-black/60">
                      <ArrowRight className="h-4 w-4" />
                      <span>{action.impact}</span>
                    </div>
                  </div>
                </div>
              ))}

              <div className="mt-6 border-[3px] border-black bg-[#ffdc5c] p-4 shadow-[4px_4px_0_0_#000]">
                <p className="text-xs font-black uppercase tracking-wider text-black">Positioning: {data.positioning.type}</p>
                <p className="mt-1 text-lg font-bold text-black">{data.positioning.message}</p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-4 border-black shadow-[8px_8px_0_0_#000]">
            <CardHeader className="border-b-[3px] border-black pb-4">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-6 w-6 text-black" strokeWidth={3} />
                <CardTitle className="text-xl font-black uppercase text-black">Scenario Comparison</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4 pt-6">
              <div className="flex items-center justify-between border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_0_#000]">
                <div>
                  <h4 className="font-black uppercase text-black">Aggressive Pricing</h4>
                  <p className="font-bold text-black/70">{data.scenario_comparison.aggressive_pricing.result}</p>
                </div>
                <div className="text-right">
                  <p className="text-xl font-black text-black">
                    {formatCurrency(data.scenario_comparison.aggressive_pricing.bid_price)}
                  </p>
                  <p className="font-bold text-[#ff5c5c]">{data.scenario_comparison.aggressive_pricing.margin}% Margin</p>
                </div>
              </div>

              <div className="flex items-center justify-between border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_0_#000]">
                <div>
                  <h4 className="font-black uppercase text-black">Balanced Pricing</h4>
                  <p className="font-bold text-black/70">{data.scenario_comparison.balanced_pricing.result}</p>
                </div>
                <div className="text-right">
                  <p className="text-xl font-black text-black">
                    {formatCurrency(data.scenario_comparison.balanced_pricing.bid_price)}
                  </p>
                  <p className="font-bold text-[#f472b6]">{data.scenario_comparison.balanced_pricing.margin}% Margin</p>
                </div>
              </div>

              <div className="relative flex items-center justify-between border-[3px] border-black bg-[#A3E635] p-4 shadow-[4px_4px_0_0_#000]">
                <div className="absolute -left-3 -top-3 border-[3px] border-black bg-white px-2 py-1 text-xs font-black uppercase shadow-[2px_2px_0_0_#000]">
                  Selected
                </div>
                <div>
                  <h4 className="pt-2 font-black uppercase text-black">Value Based</h4>
                  <p className="font-bold text-black/80">{data.scenario_comparison.value_based.result}</p>
                </div>
                <div className="pt-2 text-right">
                  <p className="text-xl font-black text-black">{formatCurrency(data.scenario_comparison.value_based.bid_price)}</p>
                  <p className="font-bold text-black">{data.scenario_comparison.value_based.margin}% Margin</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  )
}
