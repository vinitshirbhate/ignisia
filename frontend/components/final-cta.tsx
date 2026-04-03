import { Button } from "@/components/ui/button"

export function FinalCTA() {
  return (
    <section className="bg-primary px-6 py-16 md:py-20">
      <div className="mx-auto max-w-3xl text-center">
        <h2 className="text-3xl font-bold text-primary-foreground md:text-4xl">
          Make Better Bidding Decisions
        </h2>
        <p className="mx-auto mt-4 max-w-xl text-primary-foreground/80">
          Join hundreds of SMEs already using QuoteAI to win more contracts and grow their business.
        </p>
        <div className="mt-8">
          <Button size="lg" variant="secondary" className="font-semibold">
            Get Started
          </Button>
        </div>
      </div>
    </section>
  )
}
