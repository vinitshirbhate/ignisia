import { Bot, Pencil, FileCheck, ArrowRight } from "lucide-react"

const steps = [
  {
    icon: Bot,
    title: "AI Suggestion",
    description: "BidWise analyzes data and generates an optimized bid recommendation."
  },
  {
    icon: Pencil,
    title: "Human Edit",
    description: "Review, adjust, and refine the AI suggestion based on your expertise."
  },
  {
    icon: FileCheck,
    title: "Final Output",
    description: "Submit a polished, data-driven proposal with full confidence."
  }
]

export function HumanInTheLoop() {
  return (
    <section className="px-6 py-16 md:py-24">
      <div className="mx-auto max-w-6xl">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-bold text-primary md:text-4xl">
            AI + Human Expertise
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">
            The best decisions combine AI intelligence with human judgment. Stay in control at every step.
          </p>
        </div>
        
        <div className="flex flex-col items-center gap-4 md:flex-row md:justify-center md:gap-0">
          {steps.map((step, index) => (
            <div key={step.title} className="flex items-center">
              <div className="flex w-64 flex-col items-center text-center">
                <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-secondary">
                  <step.icon className="h-7 w-7 text-primary" />
                </div>
                <h3 className="mb-2 font-semibold text-foreground">{step.title}</h3>
                <p className="text-sm text-muted-foreground">{step.description}</p>
              </div>
              
              {index < steps.length - 1 && (
                <div className="hidden px-4 md:block">
                  <ArrowRight className="h-6 w-6 text-border" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
