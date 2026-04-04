"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  MapPin,
  Package,
  Users,
  Calculator,
  AlertCircle,
  Ruler,
  Clock,
  FileQuestion,
  RefreshCw,
  Sparkles,
  Loader2,
} from "lucide-react";
import {
  RFP_ANALYZE_STORAGE_KEY,
  extractReasonPayloadFromAnalyze,
  normalizeProposalFromPricingResult,
  type ProposalDisplay,
  type RfpAnalyzeResponse,
} from "@/lib/rfpTypes";

function formatCurrency(amount: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

function importSummary(ic: Record<string, string>): string {
  if (ic.none) return ic.none;
  const vals = Object.values(ic);
  return vals[0] ?? "—";
}

export function AIProposalContent() {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [raw, setRaw] = useState<RfpAnalyzeResponse | null>(null);
  const [proposal, setProposal] = useState<ProposalDisplay | null>(null);
  const [loadErr, setLoadErr] = useState<string | null>(null);
  const [reasonBusy, setReasonBusy] = useState(false);
  const [reasonErr, setReasonErr] = useState<string | null>(null);

  const reasonPayload = useMemo(
    () => extractReasonPayloadFromAnalyze(raw),
    [raw],
  );

  const sendForReasoning = async () => {
    setReasonErr(null);
    const body = extractReasonPayloadFromAnalyze(raw);
    if (!body) {
      setReasonErr(
        "No proposal + external data to send. Complete pricing first.",
      );
      return;
    }
    setReasonBusy(true);
    try {
      const res = await fetch("/api/reason-strategy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const j = (await res.json()) as {
        ok?: boolean;
        error?: string;
        detail?: string;
      };
      if (!res.ok || !j.ok) {
        const msg = [j.error, j.detail].filter(Boolean).join(" — ");
        setReasonErr(msg || `Request failed (${res.status})`);
        return;
      }
      router.push("/ai_reason");
    } catch (e) {
      setReasonErr(e instanceof Error ? e.message : "Request failed");
    } finally {
      setReasonBusy(false);
    }
  };

  const reload = () => {
    try {
      const s = sessionStorage.getItem(RFP_ANALYZE_STORAGE_KEY);
      if (!s) {
        setRaw(null);
        setProposal(null);
        setLoadErr(null);
        return;
      }
      const parsed = JSON.parse(s) as RfpAnalyzeResponse;
      setRaw(parsed);
      const pr = normalizeProposalFromPricingResult(parsed.pricing_result);
      setProposal(pr);
      if (!pr) {
        const prr = parsed.pricing_result as
          | Record<string, unknown>
          | undefined;
        if (prr?.error) {
          setLoadErr(String(prr.error));
        } else if (prr?.raw_response) {
          setLoadErr(
            "Pricing agent returned non-JSON. See raw response below.",
          );
        } else {
          setLoadErr(
            "No pricing breakdown yet. The RFP may have had no pricing questions, or the pricing agent failed.",
          );
        }
      } else {
        setLoadErr(null);
      }
    } catch {
      setLoadErr("Could not read saved proposal from this browser session.");
      setRaw(null);
      setProposal(null);
    } finally {
      setReady(true);
    }
  };

  useEffect(() => {
    reload();
  }, []);

  const pricingErr = useMemo(() => {
    const pr = raw?.pricing_result as Record<string, unknown> | undefined;
    if (!pr) return null;
    if (typeof pr.error === "string") return pr.error;
    return null;
  }, [raw]);

  const rawResponse = useMemo(() => {
    const pr = raw?.pricing_result as Record<string, unknown> | undefined;
    if (pr?.raw_response && typeof pr.raw_response === "string")
      return pr.raw_response;
    return null;
  }, [raw]);

  if (!ready) {
    return (
      <main className="flex flex-1 items-center justify-center px-6 py-24">
        <p className="text-lg font-black uppercase text-black">Loading…</p>
      </main>
    );
  }

  if (!raw && !loadErr) {
    return (
      <main className="flex flex-1 flex-col items-center justify-center gap-6 px-6 py-24">
        <p className="text-center text-lg font-black uppercase text-black">
          No proposal loaded
        </p>
        {/* <p className="max-w-md text-center text-sm font-bold text-black/70">
          Upload a PDF from the home page (&quot;Upload Your RFP Now&quot;).
          When analysis finishes, you&apos;ll land here automatically.
        </p> */}
        <Button
          asChild
          className="border-[3px] border-black font-black uppercase shadow-[4px_4px_0_0_#000]"
        >
          <Link href="/">Back to upload</Link>
        </Button>
      </main>
    );
  }

  if (!proposal) {
    return (
      <main className="mx-auto flex max-w-3xl flex-col gap-6 px-6 py-16">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <h1 className="text-3xl font-black uppercase text-black">
            AI Proposal
          </h1>
          <div className="flex flex-wrap items-center gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={reload}
              className="border-2 border-black font-bold"
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Reload
            </Button>
            {reasonPayload ? (
              <Button
                type="button"
                disabled={reasonBusy}
                onClick={() => void sendForReasoning()}
                className="border-2 border-black bg-[#A3E635] font-black uppercase shadow-[4px_4px_0_0_#000] hover:bg-[#95d92e]"
              >
                {reasonBusy ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Sparkles className="mr-2 h-4 w-4" />
                )}
                Send for reasoning
              </Button>
            ) : null}
          </div>
        </div>
        {reasonErr ? (
          <p className="text-sm font-bold text-red-600">{reasonErr}</p>
        ) : null}
        <Card className="border-4 border-black shadow-[8px_8px_0_0_#000]">
          <CardHeader className="border-b-2 border-black bg-[#ffdc5c]">
            <CardTitle className="font-black uppercase">
              Could not build cost table
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 pt-4 font-bold text-black/80">
            {loadErr ? <p>{loadErr}</p> : null}
            {pricingErr ? (
              <p className="text-red-600">Pricing: {pricingErr}</p>
            ) : null}
            {raw?.analysis?.rfp_name ? (
              <p>
                RFP: <span className="text-black">{raw.analysis.rfp_name}</span>
              </p>
            ) : null}
            {raw?.analysis?.questions?.length ? (
              <div>
                <p className="mb-2 text-sm uppercase text-black/60">
                  Extracted questions ({raw.analysis.questions.length})
                </p>
                <ul className="list-inside list-disc text-sm">
                  {raw.analysis.questions.slice(0, 8).map((q, i) => (
                    <li key={i}>{q.question ?? "—"}</li>
                  ))}
                </ul>
              </div>
            ) : null}
            {rawResponse ? (
              <pre className="max-h-64 overflow-auto border-2 border-black bg-neutral-100 p-3 text-xs">
                {rawResponse.slice(0, 4000)}
              </pre>
            ) : null}
            <Button asChild variant="outline" className="border-2 border-black">
              <Link href="/">Upload another RFP</Link>
            </Button>
          </CardContent>
        </Card>
      </main>
    );
  }

  const data = proposal;

  return (
    <main className="flex-1 px-6 py-12 md:py-16">
      <div className="mx-auto max-w-6xl space-y-12">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="mb-4 inline-block border-[3px] border-black bg-[#ffdc5c] p-3 text-4xl font-black uppercase tracking-tight text-black shadow-[6px_6px_0_0_#000] md:text-5xl">
              AI Proposal Breakdown
            </h1>
            {/* <p className="mt-2 text-xl font-bold text-black/80">
              From your uploaded RFP (doc_rag + pricing agent). Session only — refresh clears if you didn&apos;t re-upload.
            </p>
            {raw?.analysis?.rfp_name ? (
              <p className="mt-2 text-sm font-bold text-black/60">RFP: {raw.analysis.rfp_name}</p>
            ) : null} */}
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={reload}
              className="border-[3px] border-black font-black uppercase"
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Reload
            </Button>
            {reasonPayload ? (
              <Button
                type="button"
                disabled={reasonBusy}
                onClick={() => void sendForReasoning()}
                className="border-[3px] border-black bg-[#A3E635] font-black uppercase shadow-[4px_4px_0_0_#000] hover:bg-[#95d92e]"
              >
                {reasonBusy ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Sparkles className="mr-2 h-4 w-4" />
                )}
                Send for reasoning
              </Button>
            ) : null}
          </div>
        </div>
        {reasonErr ? (
          <p className="text-sm font-bold text-red-600">{reasonErr}</p>
        ) : null}

        {/* {raw?.analysis?.questions?.length ? (
          <Card className="border-4 border-black shadow-[8px_8px_0_0_#000]">
            <CardHeader className="border-b-[3px] border-black bg-[#e0f2fe] pb-3">
              <CardTitle className="flex items-center gap-2 text-lg font-black uppercase text-black">
                <FileQuestion className="h-6 w-6" strokeWidth={3} />
                RFP analysis ({raw.analysis.questions.length} questions)
              </CardTitle>
            </CardHeader>
            <CardContent className="max-h-56 overflow-y-auto pt-4">
              <ul className="space-y-2 text-sm font-bold text-black/80">
                {raw.analysis.questions.slice(0, 20).map((q, i) => (
                  <li key={i} className="border-b border-black/10 pb-2">
                    <span className="text-black/50">[{q.category ?? "?"}]</span>{" "}
                    {q.question}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        ) : null} */}

        {pricingErr ? (
          <p className="rounded border-2 border-red-500 bg-red-50 p-3 text-sm font-bold text-red-700">
            Pricing note: {pricingErr}
          </p>
        ) : null}

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <div className="flex items-center gap-3 border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_0_#000]">
            <div className="flex border-[3px] border-black bg-[#A3E635] p-2">
              <MapPin className="h-6 w-6 text-black" strokeWidth={2.5} />
            </div>
            <div>
              <p className="text-xs font-black uppercase tracking-wider text-black/60">
                Location
              </p>
              <p className="font-bold text-black">
                {data.project_summary.region}, {data.project_summary.state}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_0_#000]">
            <div className="flex border-[3px] border-black bg-[#ff5c5c] p-2">
              <AlertCircle className="h-6 w-6 text-black" strokeWidth={2.5} />
            </div>
            <div>
              <p className="text-xs font-black uppercase tracking-wider text-black/60">
                Project Type
              </p>
              <p className="font-bold uppercase text-black">
                {data.project_summary.project_type}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_0_#000]">
            <div className="flex border-[3px] border-black bg-[#60a5fa] p-2">
              <Ruler className="h-6 w-6 text-black" strokeWidth={2.5} />
            </div>
            <div>
              <p className="text-xs font-black uppercase tracking-wider text-black/60">
                Area
              </p>
              <p className="font-bold text-black">
                {data.project_summary.area_sqft} sqft
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_0_#000]">
            <div className="flex border-[3px] border-black bg-[#ffdc5c] p-2">
              <Clock className="h-6 w-6 text-black" strokeWidth={2.5} />
            </div>
            <div>
              <p className="text-xs font-black uppercase tracking-wider text-black/60">
                Duration
              </p>
              <p className="font-bold text-black">
                {data.project_summary.duration_weeks} weeks
              </p>
            </div>
          </div>
        </div>

        <div className="grid gap-8 lg:grid-cols-3">
          <Card className="col-span-1 border-4 border-black shadow-[8px_8px_0_0_#000] lg:col-span-2">
            <CardHeader className="border-b-[3px] border-black bg-[#A3E635] pb-4">
              <div className="flex items-center gap-2">
                <Package className="h-8 w-8 text-black" strokeWidth={2.5} />
                <CardTitle className="text-2xl font-black uppercase text-black">
                  Material Costs
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead className="border-b-[3px] border-black bg-white">
                    <tr>
                      <th className="p-4 text-xs font-black uppercase tracking-wider text-black">
                        Item
                      </th>
                      <th className="p-4 text-center text-xs font-black uppercase tracking-wider text-black">
                        Qty
                      </th>
                      <th className="p-4 text-right text-xs font-black uppercase tracking-wider text-black">
                        Unit (ex GST)
                      </th>
                      <th className="p-4 text-right text-xs font-black uppercase tracking-wider text-black">
                        Total (inc GST)
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y-[3px] divide-black bg-white font-bold">
                    {data.material_costs.items.map((item, i) => (
                      <tr key={i} className="hover:bg-[#f8fafc]">
                        <td className="p-4 uppercase">{item.item}</td>
                        <td className="p-4 text-center">{item.quantity}</td>
                        <td className="p-4 text-right">
                          {formatCurrency(item.unit_price_ex_gst)}
                        </td>
                        <td className="p-4 text-right text-[#05a3a5]">
                          {formatCurrency(item.total_incl_gst)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot className="border-t-4 border-black bg-[#ffdc5c] font-black uppercase text-black">
                    <tr>
                      <td colSpan={2} className="p-4">
                        Material Subtotals
                      </td>
                      <td className="p-4 text-right text-xs">
                        GST: {formatCurrency(data.material_costs.total_gst)}
                      </td>
                      <td className="p-4 text-right text-lg">
                        {formatCurrency(
                          data.material_costs.grand_total_incl_gst,
                        )}
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </CardContent>
          </Card>

          <div className="flex flex-col gap-6">
            <Card className="flex-1 border-4 border-black bg-white shadow-[8px_8px_0_0_#000]">
              <CardHeader className="border-b-[3px] border-black bg-[#60a5fa] pb-3">
                <CardTitle className="flex items-center gap-2 text-lg font-black uppercase text-black">
                  <Users className="h-6 w-6" strokeWidth={3} /> Labor &amp;
                  Imports
                </CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col gap-4 pt-6">
                <div>
                  <p className="text-xs font-black uppercase text-black/60">
                    Total Labor Cost
                  </p>
                  <p className="text-2xl font-black text-black">
                    {formatCurrency(data.labor_costs.total_labor_cost)}
                  </p>
                  <p className="mt-1 text-sm font-bold text-black/80">
                    {formatCurrency(data.labor_costs.labor_cost_per_sqft)} per
                    sqft
                  </p>
                </div>
                <div className="border-t-[3px] border-black pt-4">
                  <p className="text-xs font-black uppercase tracking-wider text-black/60">
                    Import / FX
                  </p>
                  <div className="mt-2 inline-block border-[3px] border-black bg-[#ff5c5c] p-2 text-sm font-bold text-black shadow-[2px_2px_0_0_#000]">
                    {importSummary(data.import_costs)}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="flex-1 border-4 border-black bg-white shadow-[8px_8px_0_0_#000]">
              <CardHeader className="border-b-[3px] border-black bg-[#ff5c5c] pb-3">
                <CardTitle className="flex items-center gap-2 text-lg font-black uppercase text-black">
                  <Calculator className="h-6 w-6" strokeWidth={3} /> Grand Total
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 pt-4">
                <div className="flex justify-between font-bold text-black/80">
                  <span>Base Project Cost</span>
                  <span>
                    {formatCurrency(data.summary_totals.total_project_cost)}
                  </span>
                </div>
                <div className="flex justify-between font-bold text-[#ff5c5c]">
                  <span>Contingency ({data.contingency.percentage}%)</span>
                  <span>+{formatCurrency(data.contingency.amount)}</span>
                </div>
                <div className="mt-4 border-[3px] border-black bg-black p-4 text-center text-white shadow-[4px_4px_0_0_#A3E635]">
                  <p className="text-sm font-black uppercase tracking-widest text-[#A3E635]">
                    Final Estimated Cost
                  </p>
                  <p className="mt-1 text-4xl font-black">
                    {formatCurrency(data.grand_total)}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </main>
  );
}
