import { Globe, Calculator, CheckCircle } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function GlobalCompliance() {
  return (
    <section className="border-y border-border bg-secondary/30 px-6 py-16 md:py-24">
      <div className="mx-auto max-w-6xl">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-bold text-primary md:text-4xl">
            Global Reach, Local Compliance
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">
            Handle international bids with confidence. Automatic currency conversions, tax calculations, and compliance checks.
          </p>
        </div>
        
        <div className="grid gap-6 md:grid-cols-3">
          {/* Currency Conversion */}
          <Card className="shadow-none">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Globe className="h-5 w-5 text-primary" />
                <CardTitle className="text-base">Currency Conversion</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between rounded-lg bg-secondary p-3">
                  <div>
                    <p className="text-xs text-muted-foreground">Original (USD)</p>
                    <p className="text-lg font-semibold">$18,562.00</p>
                  </div>
                  <span className="text-muted-foreground">=</span>
                  <div className="text-right">
                    <p className="text-xs text-muted-foreground">Converted (EUR)</p>
                    <p className="text-lg font-semibold text-primary">€17,134.28</p>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground">
                  Rate: 1 USD = 0.923 EUR (Live)
                </p>
              </div>
            </CardContent>
          </Card>
          
          {/* Tax Calculation */}
          <Card className="shadow-none">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Calculator className="h-5 w-5 text-primary" />
                <CardTitle className="text-base">Tax Calculation</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Subtotal</span>
                  <span>€17,134.28</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">VAT (21%)</span>
                  <span>€3,598.20</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Withholding</span>
                  <span>-€856.71</span>
                </div>
                <div className="flex justify-between border-t border-border pt-2 font-medium">
                  <span>Total</span>
                  <span className="text-primary">€19,875.77</span>
                </div>
              </div>
            </CardContent>
          </Card>
          
          {/* Compliance Checklist */}
          <Card className="shadow-none">
            <CardHeader>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-primary" />
                <CardTitle className="text-base">Compliance Check</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span className="text-sm">GDPR Data Handling</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span className="text-sm">ISO 9001 Certification</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span className="text-sm">Insurance Requirements</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span className="text-sm">Local Business License</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span className="text-sm">Tax Registration Valid</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  )
}
