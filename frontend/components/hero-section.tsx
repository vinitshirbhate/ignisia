import { Button } from "@/components/ui/button";
import { DashboardMock } from "@/components/dashboard-mock";

export function HeroSection() {
  return (
    <section className="px-6 py-16 md:py-24">
      <div className="mx-auto grid max-w-6xl items-center gap-12 lg:grid-cols-2 lg:gap-16">
        <div className="flex flex-col gap-6">
          <h1 className="text-balance text-5xl font-black uppercase leading-tight tracking-tight text-black md:text-6xl lg:text-7xl">
            <span className="bg-[#A3E635] px-2 py-1 shadow-[4px_4px_0_0_#000] border-[3px] border-black mr-2">
              Strategic
            </span>
            <br /> Bidding Intelligence for SMEs
          </h1>
          <p className="max-w-lg text-pretty text-xl font-bold text-black/80">
            Real-time pricing, competitor-aware strategy, and risk-aware
            decisions — all in one system.
          </p>
          <div className="flex flex-wrap gap-3 pt-2">
            <Button size="lg">Try Demo</Button>
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
  );
}
