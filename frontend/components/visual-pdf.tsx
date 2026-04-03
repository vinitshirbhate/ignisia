import { FileText, BarChart3, Calendar, DollarSign } from "lucide-react"

export function VisualPDF() {
  return (
    <section className="border-y border-border bg-secondary/30 px-6 py-16 md:py-24">
      <div className="mx-auto max-w-6xl">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-bold text-primary md:text-4xl">
            From Text-Heavy to Visual Impact
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">
            Transform traditional documents into compelling visual proposals that win attention.
          </p>
        </div>
        
        <div className="grid gap-8 lg:grid-cols-2">
          {/* Traditional Document */}
          <div className="rounded-xl border border-border bg-card p-6 opacity-60">
            <div className="mb-4 flex items-center gap-2">
              <FileText className="h-5 w-5 text-muted-foreground" />
              <span className="text-sm font-medium text-muted-foreground">Traditional Proposal</span>
            </div>
            <div className="space-y-3">
              <div className="h-3 w-full rounded bg-muted" />
              <div className="h-3 w-11/12 rounded bg-muted" />
              <div className="h-3 w-full rounded bg-muted" />
              <div className="h-3 w-4/5 rounded bg-muted" />
              <div className="h-3 w-full rounded bg-muted" />
              <div className="h-3 w-3/4 rounded bg-muted" />
              <div className="h-3 w-full rounded bg-muted" />
              <div className="h-3 w-5/6 rounded bg-muted" />
              <div className="h-3 w-full rounded bg-muted" />
              <div className="h-3 w-2/3 rounded bg-muted" />
            </div>
          </div>
          
          {/* Visual Proposal */}
          <div className="rounded-xl border border-border bg-card p-6">
            <div className="mb-4 flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-primary" />
              <span className="text-sm font-medium">BidWise Visual Proposal</span>
            </div>
            
            <div className="grid gap-4">
              {/* Pricing Block */}
              <div className="rounded-lg bg-secondary p-4">
                <div className="mb-2 flex items-center gap-2">
                  <DollarSign className="h-4 w-4 text-primary" />
                  <span className="text-sm font-medium">Investment Summary</span>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <div className="rounded bg-card p-2 text-center">
                    <p className="text-xs text-muted-foreground">Phase 1</p>
                    <p className="font-semibold text-primary">$6,200</p>
                  </div>
                  <div className="rounded bg-card p-2 text-center">
                    <p className="text-xs text-muted-foreground">Phase 2</p>
                    <p className="font-semibold text-primary">$8,100</p>
                  </div>
                  <div className="rounded bg-card p-2 text-center">
                    <p className="text-xs text-muted-foreground">Phase 3</p>
                    <p className="font-semibold text-primary">$4,262</p>
                  </div>
                </div>
              </div>
              
              {/* Chart Preview */}
              <div className="rounded-lg bg-secondary p-4">
                <p className="mb-2 text-sm font-medium">Progress Breakdown</p>
                <div className="flex items-end gap-2">
                  <div className="h-12 w-full rounded bg-primary" />
                  <div className="h-16 w-full rounded bg-chart-2" />
                  <div className="h-10 w-full rounded bg-chart-3" />
                  <div className="h-8 w-full rounded bg-chart-5" />
                </div>
              </div>
              
              {/* Timeline */}
              <div className="rounded-lg bg-secondary p-4">
                <div className="mb-2 flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-primary" />
                  <span className="text-sm font-medium">Project Timeline</span>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-1/3 rounded-full bg-primary" />
                    <span className="text-xs text-muted-foreground">Planning</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-1/2 rounded-full bg-chart-2" />
                    <span className="text-xs text-muted-foreground">Execution</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-1/4 rounded-full bg-chart-3" />
                    <span className="text-xs text-muted-foreground">Delivery</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
