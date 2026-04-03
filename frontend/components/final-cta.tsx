import { Button } from "@/components/ui/button";

export function FinalCTA() {
  return (
    <section className="border-t-[4px] border-black  px-6 py-20 md:py-32 shadow-[inset_0_8px_0_0_#000]">
      <div className="mx-auto max-w-3xl text-center">
        <h2 className="text-4xl font-black uppercase tracking-tight text-black md:text-5xl lg:text-6xl">
          Make Better Bidding Decisions
        </h2>
        <p className="mx-auto mt-6 max-w-xl text-xl font-bold text-black/80">
          Join hundreds of SMEs already using RFP Flow to win more contracts and
          grow their business.
        </p>
        <div className="mt-10">
          <Button
            size="lg"
            className="h-14 px-10 text-lg border-[3px] border-black shadow-[6px_6px_0_0_#000]"
          >
            GET STARTED NOW
          </Button>
        </div>
      </div>
    </section>
  );
}
