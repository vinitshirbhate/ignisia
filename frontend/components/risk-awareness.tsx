import { AlertTriangle, TrendingDown, Clock, Users } from "lucide-react"

const risks = [
  {
    icon: TrendingDown,
    severity: "High",
    title: "Competitor pricing below cost threshold",
    description: "BuildRight Inc is bidding 12% below estimated costs, indicating potential quality compromises.",
    color: "bg-amber-50 border-amber-200"
  },
  {
    icon: Clock,
    severity: "Medium",
    title: "Tight delivery timeline",
    description: "Requested completion date leaves minimal buffer for delays. Consider discussing timeline flexibility.",
    color: "bg-blue-50 border-blue-200"
  },
  {
    icon: Users,
    severity: "Low",
    title: "New client relationship",
    description: "First-time client with no payment history. Standard payment terms recommended.",
    color: "bg-slate-50 border-slate-200"
  }
]

export function RiskAwareness() {
  return (
    <section className="px-6 py-16 md:py-24">
      <div className="mx-auto max-w-6xl">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-bold text-primary md:text-4xl">
            Risk-Aware Decision Making
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">
            Identify potential risks before they become problems. QuoteAI analyzes every aspect of your bids.
          </p>
        </div>
        
        <div className="mx-auto max-w-3xl space-y-4">
          {risks.map((risk) => (
            <div
              key={risk.title}
              className={`flex items-start gap-4 rounded-lg border p-5 ${risk.color}`}
            >
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-background">
                <risk.icon className="h-5 w-5 text-primary" />
              </div>
              <div className="flex-1">
                <div className="mb-1 flex items-center gap-2">
                  <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    {risk.severity} Risk
                  </span>
                </div>
                <p className="font-medium text-foreground">{risk.title}</p>
                <p className="mt-1 text-sm text-muted-foreground">{risk.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
