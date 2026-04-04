/** Normalized proposal for AI Proposal page (matches orchestrator + mock shape). */

export type MaterialLine = {
  item: string
  quantity: number
  unit_price_ex_gst: number
  gst: number
  total_incl_gst: number
}

export type ProposalDisplay = {
  project_summary: {
    region: string
    state: string
    project_type: string
    area_sqft: number
    duration_weeks: number
  }
  material_costs: {
    items: MaterialLine[]
    subtotal_ex_gst: number
    total_gst: number
    grand_total_incl_gst: number
  }
  labor_costs: {
    total_labor_cost: number
    labor_cost_per_sqft: number
  }
  import_costs: Record<string, string>
  summary_totals: {
    total_materials_with_gst: number
    total_labor: number
    total_project_cost: number
  }
  contingency: {
    percentage: number
    amount: number
  }
  grand_total: number
}

export type RfpAnalyzeResponse = {
  analysis?: {
    rfp_name?: string
    questions?: Array<{ question?: string; category?: string; intent?: string }>
  }
  pricing_payload?: unknown
  pricing_result?: unknown
}

const EMPTY_IMPORT = { none: "No import data." }

function num(v: unknown, fallback = 0): number {
  const n = typeof v === "number" ? v : parseFloat(String(v))
  return Number.isFinite(n) ? n : fallback
}

/** Extract display proposal from pricing agent / doc_rag pricing_result. */
export function normalizeProposalFromPricingResult(pricingResult: unknown): ProposalDisplay | null {
  if (!pricingResult || typeof pricingResult !== "object") return null
  const root = pricingResult as Record<string, unknown>
  if (typeof root.error === "string" && root.error) return null

  let p: Record<string, unknown> = root
  if (root.proposal && typeof root.proposal === "object") {
    p = root.proposal as Record<string, unknown>
  }

  const ps = p.project_summary
  if (!ps || typeof ps !== "object") return null
  const summary = ps as Record<string, unknown>

  const mc = p.material_costs
  const mat = mc && typeof mc === "object" ? (mc as Record<string, unknown>) : {}
  const rawItems = Array.isArray(mat.items) ? mat.items : []

  const items: MaterialLine[] = rawItems.map((row) => {
    const r = row as Record<string, unknown>
    return {
      item: String(r.item ?? r.name ?? "Item"),
      quantity: num(r.quantity),
      unit_price_ex_gst: num(r.unit_price_ex_gst),
      gst: num(r.gst),
      total_incl_gst: num(r.total_incl_gst),
    }
  })

  const lc = (p.labor_costs as Record<string, unknown>) || {}
  const ic = (p.import_costs as Record<string, unknown>) || {}
  const st = (p.summary_totals as Record<string, unknown>) || {}
  const ct = (p.contingency as Record<string, unknown>) || {}

  const importStrings: Record<string, string> = {}
  for (const [k, v] of Object.entries(ic)) {
    importStrings[k] = typeof v === "string" ? v : JSON.stringify(v)
  }
  if (Object.keys(importStrings).length === 0) {
    Object.assign(importStrings, EMPTY_IMPORT)
  }

  return {
    project_summary: {
      region: String(summary.region ?? "—"),
      state: String(summary.state ?? "—"),
      project_type: String(summary.project_type ?? "—"),
      area_sqft: num(summary.area_sqft),
      duration_weeks: Math.round(num(summary.duration_weeks)),
    },
    material_costs: {
      items,
      subtotal_ex_gst: num(mat.subtotal_ex_gst),
      total_gst: num(mat.total_gst),
      grand_total_incl_gst: num(mat.grand_total_incl_gst),
    },
    labor_costs: {
      total_labor_cost: num(lc.total_labor_cost),
      labor_cost_per_sqft: num(lc.labor_cost_per_sqft),
    },
    import_costs: importStrings,
    summary_totals: {
      total_materials_with_gst: num(st.total_materials_with_gst),
      total_labor: num(st.total_labor),
      total_project_cost: num(st.total_project_cost),
    },
    contingency: {
      percentage: num(ct.percentage, 5),
      amount: num(ct.amount),
    },
    grand_total: num(p.grand_total),
  }
}

export const RFP_ANALYZE_STORAGE_KEY = "ignisia_last_rfp_analyze"

const DEFAULT_EXTERNAL = {
  external_factors: {
    competitor_price: 0,
    market_condition: "unknown",
    material_trend: "unknown",
    demand_level: "unknown",
  },
  constraints: { min_margin_percent: 15 },
} as const

/**
 * Build the body for POST /reason/strategy from doc_rag analyze output.
 * Uses only `pricing_result.proposal` + `pricing_result.external`, or a flat pricing_result cost object.
 * Omits analysis, pricing_payload, and questions.
 */
export function extractReasonPayloadFromAnalyze(
  raw: RfpAnalyzeResponse | null,
): { proposal: Record<string, unknown>; external: Record<string, unknown> } | null {
  if (!raw?.pricing_result || typeof raw.pricing_result !== "object") return null
  const pr = raw.pricing_result as Record<string, unknown>
  if (typeof pr.error === "string" && pr.error) return null

  let proposal: Record<string, unknown> | null = null
  let external: Record<string, unknown> | null = null

  if (pr.proposal && typeof pr.proposal === "object") {
    proposal = { ...(pr.proposal as Record<string, unknown>) }
    if (pr.external && typeof pr.external === "object") {
      external = { ...(pr.external as Record<string, unknown>) }
    }
  } else if (pr.project_summary && typeof pr.project_summary === "object") {
    proposal = { ...pr }
    delete proposal.error
    delete proposal.raw_response
    delete proposal.external
  }

  if (!proposal || typeof proposal.project_summary !== "object") return null

  const efIn =
    external?.external_factors && typeof external.external_factors === "object"
      ? (external.external_factors as Record<string, unknown>)
      : {}
  const cIn =
    external?.constraints && typeof external.constraints === "object"
      ? (external.constraints as Record<string, unknown>)
      : {}
  const externalOut = {
    external_factors: { ...DEFAULT_EXTERNAL.external_factors, ...efIn },
    constraints: { ...DEFAULT_EXTERNAL.constraints, ...cIn },
  }

  return { proposal, external: externalOut }
}

