import { Button } from "@/components/ui/button"
import { DashboardMock } from "@/components/dashboard-mock"

export function HeroSection() {
  return (
    <section className="px-6 py-16 md:py-24">
      <div className="mx-auto grid max-w-6xl items-center gap-12 lg:grid-cols-2 lg:gap-16">
        <div className="flex flex-col gap-6">
          <h1 className="text-balance text-4xl font-bold tracking-tight text-primary md:text-5xl lg:text-6xl">
            Strategic Bidding Intelligence for SMEs
          </h1>
          <p className="max-w-lg text-pretty text-lg text-muted-foreground">
            Real-time pricing, competitor-aware strategy, and risk-aware decisions — all in one system.
          </p>
          <div className="flex flex-wrap gap-3 pt-2">
            <Button size="lg">
              Try Demo
            </Button>
            <Button variant="outline" size="lg">
              View Product
            </Button>
          </div>
        </div>
        
        <div className="relative">
          <DashboardMock />
        </div>
      </div>
    </section>
  )
}
