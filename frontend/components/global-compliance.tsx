import { Globe, Calculator, CheckCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function GlobalCompliance() {
  return (
    <section className="border-y-[4px] border-black  px-6 py-16 md:py-24">
      <div className="mx-auto max-w-6xl">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-bold text-primary md:text-4xl">
            Global Reach, Local Compliance
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">
            Handle international bids with confidence. Automatic currency
            conversions, tax calculations, and compliance checks.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {/* Currency Conversion */}
          <Card className="shadow-[8px_8px_0_0_#000]">
            <CardHeader className="border-b-[3px] border-black pb-4">
              <div className="flex items-center gap-2">
                <Globe className="h-6 w-6 text-black" strokeWidth={2.5} />
                <CardTitle className="text-lg font-black uppercase tracking-tight text-black">
                  Currency Conversion
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between border-[3px] border-black bg-[#ff5c5c] p-3 text-black shadow-[4px_4px_0_0_#000]">
                  <div>
                    <p className="text-xs font-bold uppercase">
                      Original (USD)
                    </p>
                    <p className="text-lg font-black">$18,562.00</p>
                  </div>
                  <span className="font-black">=</span>
                  <div className="text-right">
                    <p className="text-xs font-bold uppercase">
                      Converted (EUR)
                    </p>
                    <p className="text-lg font-black">€17,134.28</p>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground">
                  Rate: 1 USD = 0.923 EUR (Live)
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Tax Calculation */}
          <Card className="shadow-[8px_8px_0_0_#000]">
            <CardHeader className="border-b-[3px] border-black pb-4">
              <div className="flex items-center gap-2">
                <Calculator className="h-6 w-6 text-black" strokeWidth={2.5} />
                <CardTitle className="text-lg font-black uppercase tracking-tight text-black">
                  Tax Calculation
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="space-y-2 text-black">
                <div className="flex justify-between text-sm font-bold uppercase">
                  <span>Subtotal</span>
                  <span>€17,134.28</span>
                </div>
                <div className="flex justify-between text-sm font-bold uppercase">
                  <span>VAT (21%)</span>
                  <span>€3,598.20</span>
                </div>
                <div className="flex justify-between text-sm font-bold uppercase">
                  <span>Withholding</span>
                  <span>-€856.71</span>
                </div>
                <div className="flex justify-between border-t-[3px] border-black pt-2 font-black text-lg">
                  <span>Total</span>
                  <span>€19,875.77</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Compliance Checklist */}
          <Card className="shadow-[8px_8px_0_0_#000]">
            <CardHeader className="border-b-[3px] border-black pb-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-6 w-6 text-black" strokeWidth={2.5} />
                <CardTitle className="text-lg font-black uppercase tracking-tight text-black">
                  Compliance Check
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="space-y-3">
                <div className="flex items-center gap-2 border-[3px] border-black bg-[#A3E635] p-2 shadow-[2px_2px_0_0_#000]">
                  <CheckCircle className="h-5 w-5 text-black" strokeWidth={3} />
                  <span className="text-xs font-black uppercase text-black">
                    GDPR Data Handling
                  </span>
                </div>
                <div className="flex items-center gap-2 border-[3px] border-black bg-[#A3E635] p-2 shadow-[2px_2px_0_0_#000]">
                  <CheckCircle className="h-5 w-5 text-black" strokeWidth={3} />
                  <span className="text-xs font-black uppercase text-black">
                    ISO 9001 Certification
                  </span>
                </div>
                <div className="flex items-center gap-2 border-[3px] border-black bg-[#A3E635] p-2 shadow-[2px_2px_0_0_#000]">
                  <CheckCircle className="h-5 w-5 text-black" strokeWidth={3} />
                  <span className="text-xs font-black uppercase text-black">
                    Insurance Requirements
                  </span>
                </div>
                <div className="flex items-center gap-2 border-[3px] border-black bg-[#A3E635] p-2 shadow-[2px_2px_0_0_#000]">
                  <CheckCircle className="h-5 w-5 text-black" strokeWidth={3} />
                  <span className="text-xs font-black uppercase text-black">
                    Local Business License
                  </span>
                </div>
                <div className="flex items-center gap-2 border-[3px] border-black bg-[#A3E635] p-2 shadow-[2px_2px_0_0_#000]">
                  <CheckCircle className="h-5 w-5 text-black" strokeWidth={3} />
                  <span className="text-xs font-black uppercase text-black">
                    Tax Registration Valid
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
}
