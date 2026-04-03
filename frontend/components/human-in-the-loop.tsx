import { Bot, Pencil, FileCheck, ArrowRight } from "lucide-react";

const steps = [
  {
    icon: Bot,
    title: "AI Suggestion",
    description:
      "BidWise analyzes data and generates an optimized bid recommendation.",
  },
  {
    icon: Pencil,
    title: "Human Edit",
    description:
      "Review, adjust, and refine the AI suggestion based on your expertise.",
  },
  {
    icon: FileCheck,
    title: "Final Output",
    description:
      "Submit a polished, data-driven proposal with full confidence.",
  },
];

export function HumanInTheLoop() {
  return (
    <section className="px-6 py-16 md:py-24">
      <div className="mx-auto max-w-6xl">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-black uppercase tracking-tight text-black md:text-4xl lg:text-5xl border-[3px] border-black  p-4 shadow-[6px_6px_0_0_#000] inline-block mb-4">
            AI + Human Expertise
          </h2>
          <p className="mx-auto mt-6 max-w-2xl text-lg font-bold text-black/80">
            The best decisions combine AI intelligence with human judgment. Stay
            in control at every step.
          </p>
        </div>

        <div className="flex flex-col items-center gap-8 md:flex-row md:justify-center md:gap-4">
          {steps.map((step, index) => (
            <div key={step.title} className="flex items-center">
              <div className="flex w-64 flex-col items-center text-center border-[3px] border-black bg-white p-6 shadow-[6px_6px_0_0_#000] transition-transform hover:-translate-y-2">
                <div className="mb-4 flex h-16 w-16 items-center justify-center border-[3px] border-black bg-[#ffdc5c] shadow-[4px_4px_0_0_#000]">
                  <step.icon className="h-8 w-8 text-black" strokeWidth={2.5} />
                </div>
                <h3 className="mb-2 text-xl font-black uppercase text-black">
                  {step.title}
                </h3>
                <p className="text-sm font-bold text-black/80">
                  {step.description}
                </p>
              </div>

              {index < steps.length - 1 && (
                <div className="hidden px-4 md:block">
                  <ArrowRight
                    className="h-10 w-10 text-black drop-shadow-[2px_2px_0_rgba(0,0,0,1)]"
                    strokeWidth={3}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
