import { AlertTriangle, TrendingDown, Clock, Users } from "lucide-react"

const risks = [
  {
    icon: TrendingDown,
    severity: "High",
    title: "Competitor pricing below cost threshold",
    description: "BuildRight Inc is bidding 12% below estimated costs, indicating potential quality compromises.",
    color: "bg-[#ff5c5c] border-black text-black"
  },
  {
    icon: Clock,
    severity: "Medium",
    title: "Tight delivery timeline",
    description: "Requested completion date leaves minimal buffer for delays. Consider discussing timeline flexibility.",
    color: "bg-[#ffdc5c] border-black text-black"
  },
  {
    icon: Users,
    severity: "Low",
    title: "New client relationship",
    description: "First-time client with no payment history. Standard payment terms recommended.",
    color: "bg-[#5cafff] border-black text-black"
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
              className={`flex items-start gap-4 rounded-none border-[3px] p-5 shadow-[4px_4px_0_0_#000] transition-transform hover:-translate-y-1 hover:shadow-[6px_6px_0_0_#000] ${risk.color}`}
            >
              <div className="flex h-12 w-12 shrink-0 items-center justify-center border-[3px] border-black bg-white shadow-[2px_2px_0_0_#000]">
                <risk.icon className="h-6 w-6 text-black" strokeWidth={2.5} />
              </div>
              <div className="flex-1">
                <div className="mb-1 flex items-center gap-2">
                  <span className="text-xs font-black uppercase tracking-wide text-black/80">
                    {risk.severity} Risk
                  </span>
                </div>
                <p className="font-black text-lg text-black">{risk.title}</p>
                <p className="mt-1 text-base font-semibold text-black/80">{risk.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
