"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  RFP_ANALYZE_STORAGE_KEY,
  type RfpAnalyzeResponse,
} from "@/lib/rfpTypes";
import { Loader2 } from "lucide-react";

export function FinalCTA() {
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const onPick = () => {
    setErr(null);
    inputRef.current?.click();
  };

  const onFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setErr("Please choose a PDF file.");
      return;
    }
    setBusy(true);
    setErr(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch("/api/rfp/analyze", {
        method: "POST",
        body: fd,
      });
      const payload = await res.json();
      if (!res.ok || !payload.ok) {
        const msg =
          typeof payload.error === "string"
            ? payload.error
            : `Upload failed (${res.status})`;
        const detail = payload.detail
          ? ` — ${String(payload.detail).slice(0, 400)}`
          : "";
        setErr(msg + detail);
        return;
      }
      const data = payload.data as RfpAnalyzeResponse;
      sessionStorage.setItem(RFP_ANALYZE_STORAGE_KEY, JSON.stringify(data));
      router.push("/ai_proposal");
    } catch (x) {
      setErr(x instanceof Error ? x.message : "Network error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="border-t-[4px] border-black px-6 py-20 shadow-[inset_0_8px_0_0_#000] md:py-32">
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf,.pdf"
        className="hidden"
        onChange={(e) => void onFile(e)}
      />
      <div className="mx-auto max-w-3xl text-center">
        <h2 className="text-4xl font-black uppercase tracking-tight text-black md:text-5xl lg:text-6xl">
          Make Better Bidding Decisions
        </h2>
        <p className="mx-auto mt-6 max-w-xl text-xl font-bold text-black/80">
          Join hundreds of SMEs already using RFP Flow to win more contracts and
          grow their business.
        </p>
        <div className="mt-10 flex flex-col items-center gap-3">
          <Button
            type="button"
            size="lg"
            disabled={busy}
            onClick={onPick}
            className="h-14 border-[3px] border-black px-10 text-lg shadow-[6px_6px_0_0_#000]"
          >
            {busy ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Analyzing RFP &amp; pricing…
              </>
            ) : (
              "Upload Your RFP Now"
            )}
          </Button>
          {/* <p className="max-w-md text-xs font-bold text-black/50">
            PDF is sent to doc_rag (port 8001) and the pricing agent (port 9000) when the RFP includes pricing
            questions. This can take several minutes.
          </p> */}
          {err ? (
            <p className="max-w-lg text-sm font-bold text-red-600">{err}</p>
          ) : null}
        </div>
      </div>
    </section>
  );
}
