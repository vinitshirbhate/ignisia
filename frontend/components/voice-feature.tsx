import { Play, Volume2 } from "lucide-react"
import { Button } from "@/components/ui/button"

export function VoiceFeature() {
  return (
    <section className="px-6 py-16 md:py-24">
      <div className="mx-auto max-w-6xl">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <div>
            <h2 className="text-3xl font-bold text-primary md:text-4xl">
              AI That Helps You Pitch
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Generate professional voice pitches that complement your proposals. Let AI help you articulate your value proposition clearly and confidently.
            </p>
          </div>
          
          <div className="rounded-xl border border-border bg-card p-6">
            <div className="mb-4 flex items-center gap-2">
              <Volume2 className="h-5 w-5 text-primary" />
              <span className="font-medium">Generated Sales Pitch</span>
            </div>
            
            <div className="rounded-lg bg-secondary p-4">
              <div className="flex items-center gap-4">
                <Button size="icon" variant="outline" className="h-12 w-12 rounded-full">
                  <Play className="h-5 w-5" />
                </Button>
                
                <div className="flex-1">
                  <div className="mb-2 flex justify-between text-sm">
                    <span className="text-muted-foreground">Project Proposal - ABC Construction</span>
                    <span className="text-muted-foreground">0:45</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-border">
                    <div className="h-full w-0 rounded-full bg-primary" />
                  </div>
                </div>
              </div>
            </div>
            
            <p className="mt-4 text-sm italic text-muted-foreground">
              {'"Our proposal for the ABC Construction project offers competitive pricing at $18,562, backed by our track record of on-time delivery and quality craftsmanship..."'}
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
