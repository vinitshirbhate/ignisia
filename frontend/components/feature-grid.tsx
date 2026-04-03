import { 
  TrendingUp, 
  Target, 
  ShieldAlert, 
  Lightbulb, 
  Building2, 
  FileCheck, 
  Globe, 
  Users, 
  Mic, 
  FileText 
} from "lucide-react"

const features = [
  {
    icon: TrendingUp,
    title: "Real-Time Price Intelligence",
    description: "Dynamic pricing recommendations based on market conditions and historical data."
  },
  {
    icon: Target,
    title: "Competitor-Aware Strategy",
    description: "Analyze competitor patterns and position your bids for maximum win probability."
  },
  {
    icon: ShieldAlert,
    title: "Business Risk Awareness",
    description: "Identify potential risks and get alerts before submitting critical bids."
  },
  {
    icon: Lightbulb,
    title: "Long-Term Strategic Thinking",
    description: "Balance short-term wins with long-term business relationship goals."
  },
  {
    icon: Building2,
    title: "Built for SMEs",
    description: "Affordable and simple solutions designed specifically for small and medium enterprises."
  },
  {
    icon: FileCheck,
    title: "Bureaucratic Compliance AI",
    description: "Automatically ensure your bids meet regulatory and compliance requirements."
  },
  {
    icon: Globe,
    title: "Tax & Global Currency Intelligence",
    description: "Handle multi-currency conversions and international tax calculations effortlessly."
  },
  {
    icon: Users,
    title: "Human-in-the-Loop Control",
    description: "AI suggestions with full human oversight and editing capabilities."
  },
  {
    icon: Mic,
    title: "Voice-Based Sales Pitcher",
    description: "Generate professional voice pitches to accompany your proposals."
  },
  {
    icon: FileText,
    title: "Visual Proposal PDFs",
    description: "Create stunning visual proposals that stand out from text-heavy documents."
  }
]

export function FeatureGrid() {
  return (
    <section id="features" className="px-6 py-16 md:py-24">
      <div className="mx-auto max-w-6xl">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-bold text-primary md:text-4xl">
            Everything You Need to Win More Bids
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">
            Comprehensive tools designed to give SMEs a competitive edge in every bidding scenario.
          </p>
        </div>
        
        <div className="grid gap-6 md:grid-cols-2">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="group rounded-none border-[3px] border-black bg-white p-6 shadow-[6px_6px_0_0_#000] transition-all hover:translate-x-[3px] hover:translate-y-[3px] hover:shadow-[3px_3px_0_0_#000]"
            >
              <div className="mb-4 flex h-12 w-12 items-center justify-center border-[3px] border-black bg-[#A3E635] shadow-[2px_2px_0_0_#000]">
                <feature.icon className="h-6 w-6 text-black" strokeWidth={2.5} />
              </div>
              <h3 className="mb-2 text-xl font-bold text-black">
                {feature.title}
              </h3>
              <p className="text-base font-medium text-black/80">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
