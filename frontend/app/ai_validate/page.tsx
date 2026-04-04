"use client";

import { useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  FileUp,
  Loader2,
  ShieldAlert,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Header } from "@/components/header";
import { Footer } from "@/components/footer";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

type ValidationIssue = {
  id?: string;
  severity?: string;
  category?: string;
  title?: string;
  description?: string;
  recommendation?: string;
  impact?: string;
};

type ValidationResponse = {
  overall_score?: number;
  risk_level?: string;
  executive_summary?: string;
  strengths?: string[];
  missing_sections?: string[];
  issues?: ValidationIssue[];
  detail?: string;
};

const apiBaseUrl =
  process.env.NEXT_PUBLIC_AI_VALIDATE_API_URL?.replace(/\/$/, "") ??
  "http://localhost:8002";

function riskBadgeClasses(riskLevel?: string) {
  switch (riskLevel?.toUpperCase()) {
    case "LOW":
      return "bg-[#A3E635] text-black border-[2px] border-black";
    case "MEDIUM":
      return "bg-[#FACC15] text-black border-[2px] border-black";
    case "HIGH":
      return "bg-[#FB923C] text-black border-[2px] border-black";
    case "CRITICAL":
      return "bg-[#EF4444] text-white border-[2px] border-black";
    default:
      return "bg-white text-black border-[2px] border-black";
  }
}

export default function AIValidateDemo() {
  const [file, setFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ValidationResponse | null>(null);

  async function handleSubmit() {
    if (!file) {
      setError("Choose a PDF proposal before running validation.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/validate`, {
        method: "POST",
        body: formData,
      });

      const data = (await response.json()) as ValidationResponse;

      if (!response.ok) {
        throw new Error(data.detail || "Validation failed.");
      }

      setResult(data);
    } catch (submissionError) {
      const message =
        submissionError instanceof Error
          ? submissionError.message
          : "Something went wrong while contacting AI Validate.";
      setResult(null);
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-[#f8fafc]">
      <Header />
      <main id="ai-validate" className="flex-1 px-6 py-12 md:py-16">
        <div className="mx-auto max-w-6xl">
          <div className="mb-10 max-w-3xl">
            <h1 className="mb-4 inline-block border-[3px] border-black bg-[#A3E635] p-3 text-4xl font-black uppercase tracking-tight text-black shadow-[6px_6px_0_0_#000] md:text-5xl">
              AI Validate
            </h1>
            <h2 className="text-2xl font-black text-black md:text-3xl">
              Upload a proposal and get a structured risk review.
            </h2>
            {/* <p className="mt-4 text-base font-medium text-black/80 md:text-lg">
              This connects the frontend directly to the FastAPI validator so you
              can inspect score, risk level, missing sections, and issue-by-issue
              feedback in one place.
            </p> */}
          </div>

          <div className="grid gap-8 lg:grid-cols-[0.95fr_1.05fr]">
          <Card className="border-[4px] border-black bg-white shadow-[8px_8px_0_0_#000]">
            <CardHeader>
              <CardTitle className="text-2xl font-black text-black">
                Run validation
              </CardTitle>
              
            </CardHeader>
            <CardContent className="space-y-5">
              <label
                htmlFor="proposal-upload"
                className="flex min-h-56 cursor-pointer flex-col items-center justify-center gap-4 border-[3px] border-dashed border-black bg-[#F8FAFC] p-6 text-center"
              >
                <div className="flex h-16 w-16 items-center justify-center border-[3px] border-black bg-[#05A3A5] shadow-[3px_3px_0_0_#000]">
                  <FileUp className="h-8 w-8 text-black" strokeWidth={2.5} />
                </div>
                <div>
                  <p className="text-lg font-black text-black">
                    {file ? file.name : "Select a proposal PDF"}
                  </p>
                  <p className="mt-2 text-sm font-medium text-black/70">
                    Click to browse and upload a proposal document for review.
                  </p>
                </div>
              </label>

              <input
                id="proposal-upload"
                type="file"
                accept="application/pdf"
                className="hidden"
                onChange={(event) => {
                  const nextFile = event.target.files?.[0] ?? null;
                  setFile(nextFile);
                  setResult(null);
                  setError(null);
                }}
              />

              <div className="flex flex-wrap items-center gap-3">
                <Button
                  onClick={handleSubmit}
                  disabled={!file || isSubmitting}
                  size="lg"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Validating...
                    </>
                  ) : (
                    "Validate proposal"
                  )}
                </Button>
                {file ? (
                  <span className="text-sm font-bold text-black/70">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                ) : null}
              </div>

              {error ? (
                <div className="flex gap-3 border-[3px] border-black bg-[#FEE2E2] p-4 text-sm font-medium text-black">
                  <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />
                  <p>{error}</p>
                </div>
              ) : null}
            </CardContent>
          </Card>

          <Card className="border-[4px] border-black bg-white shadow-[8px_8px_0_0_#000]">
            <CardHeader>
              <CardTitle className="text-2xl font-black text-black">
                Validation output
              </CardTitle>
              
            </CardHeader>
            <CardContent className="space-y-6 max-h-[800px] overflow-y-auto pr-2">
              {!result ? (
                <div className="flex min-h-80 flex-col items-center justify-center border-[3px] border-black bg-[#F8FAFC] p-8 text-center">
                  <ShieldAlert
                    className="h-12 w-12 text-black"
                    strokeWidth={2.5}
                  />
                  <p className="mt-4 text-lg font-black text-black">
                    No report yet
                  </p>
                  <p className="mt-2 max-w-md text-sm font-medium text-black/70">
                    Upload a PDF and run validation to see the proposal score,
                    risk level, and the most important issues called out here.
                  </p>
                </div>
              ) : (
                <>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="border-[3px] border-black bg-[#EEF2FF] p-4">
                      <p className="text-xs font-black uppercase tracking-[0.2em] text-black/70">
                        Overall score
                      </p>
                      <p className="mt-2 text-5xl font-black text-black">
                        {result.overall_score ?? "--"}
                      </p>
                    </div>
                    <div className="border-[3px] border-black bg-[#F8FAFC] p-4">
                      <p className="text-xs font-black uppercase tracking-[0.2em] text-black/70">
                        Risk level
                      </p>
                      <Badge
                        className={`mt-3 text-sm font-black ${riskBadgeClasses(result.risk_level)}`}
                      >
                        {result.risk_level ?? "Unknown"}
                      </Badge>
                    </div>
                  </div>

                  {result.executive_summary ? (
                    <div className="border-[3px] border-black bg-[#FFF7E8] p-4">
                      <p className="text-xs font-black uppercase tracking-[0.2em] text-black/70">
                        Executive summary
                      </p>
                      <p className="mt-3 text-sm font-medium leading-6 text-black">
                        {result.executive_summary}
                      </p>
                    </div>
                  ) : null}

                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="border-[3px] border-black bg-white p-4">
                      <p className="mb-3 text-sm font-black text-black">
                        Strengths
                      </p>
                      <div className="space-y-3">
                        {(result.strengths?.length
                          ? result.strengths
                          : ["No strengths were returned."]
                        ).map((strength) => (
                          <div
                            key={strength}
                            className="flex gap-3 text-sm font-medium text-black/80"
                          >
                            <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-[#0F766E]" />
                            <span>{strength}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="border-[3px] border-black bg-white p-4">
                      <p className="mb-3 text-sm font-black text-black">
                        Missing sections
                      </p>
                      <div className="space-y-3">
                        {(result.missing_sections?.length
                          ? result.missing_sections
                          : ["No missing sections were reported."]
                        ).map((section) => (
                          <div
                            key={section}
                            className="flex gap-3 text-sm font-medium text-black/80"
                          >
                            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-[#B45309]" />
                            <span>{section}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div>
                    <p className="mb-4 text-lg font-black text-black">
                      Key issues ({result.issues?.length ?? 0})
                    </p>
                    <div className="space-y-4">
                      {(result.issues?.length ? result.issues : []).map(
                        (issue, index) => (
                          <div
                            key={issue.id ?? `${issue.title}-${index}`}
                            className="border-[3px] border-black bg-[#F8FAFC] p-4"
                          >
                            <div className="flex flex-wrap items-center gap-2">
                              <Badge className="border-[2px] border-black bg-white text-black">
                                {issue.severity ?? "UNSPECIFIED"}
                              </Badge>
                              {issue.category ? (
                                <Badge className="border-[2px] border-black bg-[#E0F2FE] text-black">
                                  {issue.category}
                                </Badge>
                              ) : null}
                            </div>
                            <p className="mt-3 text-base font-black text-black">
                              {issue.title ?? `Issue ${index + 1}`}
                            </p>
                            {issue.description ? (
                              <p className="mt-2 text-sm font-medium leading-6 text-black/80">
                                {issue.description}
                              </p>
                            ) : null}
                            {issue.recommendation ? (
                              <p className="mt-3 text-sm font-bold text-black">
                                Fix:{" "}
                                <span className="font-medium">
                                  {issue.recommendation}
                                </span>
                              </p>
                            ) : null}
                            {issue.impact ? (
                              <p className="mt-2 text-sm font-bold text-black">
                                Impact:{" "}
                                <span className="font-medium">
                                  {issue.impact}
                                </span>
                              </p>
                            ) : null}
                          </div>
                        ),
                      )}
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
      </main>
      <Footer />
    </div>
  );
}
