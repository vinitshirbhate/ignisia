import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle } from "lucide-react";

export function ProductPreview() {
  return (
    <section
      id="product"
      className="border-y-[4px] border-black  px-6 py-16 md:py-24"
    >
      <div className="mx-auto max-w-6xl">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-bold text-primary md:text-4xl">
            See RFP Flow in Action
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">
            A clear, data-driven interface that helps you make informed bidding
            decisions.
          </p>
        </div>

        <div className="mx-auto max-w-4xl rounded-none border-[3px] border-black bg-white p-6 shadow-[8px_8px_0_0_#000]">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Pricing Breakdown */}
            <Card className="shadow-none">
              <CardHeader>
                <CardTitle className="text-base">Pricing Breakdown</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between border-b border-border pb-2">
                    <span className="text-muted-foreground">Materials</span>
                    <span className="font-medium">$8,450</span>
                  </div>
                  <div className="flex justify-between border-b border-border pb-2">
                    <span className="text-muted-foreground">Labor (40hrs)</span>
                    <span className="font-medium">$3,200</span>
                  </div>
                  <div className="flex justify-between border-b border-border pb-2">
                    <span className="text-muted-foreground">Equipment</span>
                    <span className="font-medium">$1,800</span>
                  </div>
                  <div className="flex justify-between border-b border-border pb-2">
                    <span className="text-muted-foreground">
                      Overhead (15%)
                    </span>
                    <span className="font-medium">$2,018</span>
                  </div>
                  <div className="flex justify-between border-b border-border pb-2">
                    <span className="text-muted-foreground">
                      Profit Margin (20%)
                    </span>
                    <span className="font-medium">$3,094</span>
                  </div>
                  <div className="flex justify-between pt-1">
                    <span className="font-semibold">Total Bid</span>
                    <span className="text-lg font-bold text-primary">
                      $18,562
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Competitor Comparison */}
            <Card className="shadow-none">
              <CardHeader>
                <CardTitle className="text-base">
                  Competitor Comparison
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="mb-1 flex justify-between text-sm">
                      <span className="font-medium text-primary">Your Bid</span>
                      <span className="font-semibold">$18,562</span>
                    </div>
                    <div className="h-3 rounded-full bg-primary" />
                  </div>
                  <div>
                    <div className="mb-1 flex justify-between text-sm">
                      <span className="text-muted-foreground">
                        Acme Corp (Est.)
                      </span>
                      <span>$19,800</span>
                    </div>
                    <div className="h-3 w-[107%] rounded-full bg-chart-3" />
                  </div>
                  <div>
                    <div className="mb-1 flex justify-between text-sm">
                      <span className="text-muted-foreground">
                        BuildRight Inc (Est.)
                      </span>
                      <span>$17,200</span>
                    </div>
                    <div className="h-3 w-[93%] rounded-full bg-chart-3" />
                  </div>
                  <div>
                    <div className="mb-1 flex justify-between text-sm">
                      <span className="text-muted-foreground">
                        QuickBuild (Est.)
                      </span>
                      <span>$20,500</span>
                    </div>
                    <div className="h-3 w-[110%] rounded-full bg-chart-3" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Risk Alert */}
          <div className="mt-6 flex items-start gap-3 rounded-none border-[3px] border-black bg-[#ffdc5c] p-4 shadow-[4px_4px_0_0_#000]">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center border-[3px] border-black bg-white shadow-[2px_2px_0_0_#000]">
              <AlertTriangle className="h-5 w-5 text-black" strokeWidth={2.5} />
            </div>
            <div>
              <p className="font-black text-black">Attention Required</p>
              <p className="text-sm font-semibold text-black/80">
                BuildRight Inc typically bids 7% below market average. Consider
                highlighting your quality guarantees to justify pricing.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
