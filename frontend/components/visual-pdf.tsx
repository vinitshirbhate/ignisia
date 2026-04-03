import { FileText, BarChart3, Calendar, DollarSign } from "lucide-react";

export function VisualPDF() {
  return (
    <section className="border-y-[4px] border-black  px-6 py-16 md:py-24">
      <div className="mx-auto max-w-6xl">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-bold text-primary md:text-4xl">
            From Text-Heavy to Visual Impact
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">
            Transform traditional documents into compelling visual proposals
            that win attention.
          </p>
        </div>

        <div className="grid gap-8 lg:grid-cols-2">
          {/* Traditional Document */}
          <div className="rounded-none border-[3px] border-black bg-white p-6 opacity-90 shadow-[8px_8px_0_0_#000]">
            <div className="mb-4 flex items-center gap-2">
              <FileText className="h-5 w-5 text-black" />
              <span className="text-sm font-bold text-black border-b-[3px] border-black pb-1">
                Traditional Proposal
              </span>
            </div>
            <div className="space-y-3">
              <div className="h-3 w-full border-[2px] border-black bg-[#f8fafc]" />
              <div className="h-3 w-11/12 border-[2px] border-black bg-[#f8fafc]" />
              <div className="h-3 w-full border-[2px] border-black bg-[#f8fafc]" />
              <div className="h-3 w-4/5 border-[2px] border-black bg-[#f8fafc]" />
              <div className="h-3 w-full border-[2px] border-black bg-[#f8fafc]" />
              <div className="h-3 w-3/4 border-[2px] border-black bg-[#f8fafc]" />
              <div className="h-3 w-full border-[2px] border-black bg-[#f8fafc]" />
              <div className="h-3 w-5/6 border-[2px] border-black bg-[#f8fafc]" />
              <div className="h-3 w-full border-[2px] border-black bg-[#f8fafc]" />
              <div className="h-3 w-2/3 border-[2px] border-black bg-[#f8fafc]" />
            </div>
          </div>

          {/* Visual Proposal */}
          <div className="rounded-none border-[3px] border-black bg-[#f8fafc] p-6 shadow-[8px_8px_0_0_#000]">
            <div className="mb-4 flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-black" strokeWidth={2.5} />
              <span className="text-sm font-black uppercase text-black border-b-[3px] border-black pb-1">
                BidWise Visual Proposal
              </span>
            </div>

            <div className="grid gap-4">
              {/* Pricing Block */}
              <div className="rounded-none border-[3px] border-black bg-[#ffdc5c] p-4 shadow-[4px_4px_0_0_#000]">
                <div className="mb-2 flex items-center gap-2">
                  <DollarSign
                    className="h-5 w-5 text-black"
                    strokeWidth={2.5}
                  />
                  <span className="text-sm font-black uppercase">
                    Investment Summary
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <div className="border-[3px] border-black bg-white p-2 text-center shadow-[2px_2px_0_0_#000]">
                    <p className="text-xs font-bold uppercase text-black">
                      Phase 1
                    </p>
                    <p className="font-black text-black">$6,200</p>
                  </div>
                  <div className="border-[3px] border-black bg-white p-2 text-center shadow-[2px_2px_0_0_#000]">
                    <p className="text-xs font-bold uppercase text-black">
                      Phase 2
                    </p>
                    <p className="font-black text-black">$8,100</p>
                  </div>
                  <div className="border-[3px] border-black bg-white p-2 text-center shadow-[2px_2px_0_0_#000]">
                    <p className="text-xs font-bold uppercase text-black">
                      Phase 3
                    </p>
                    <p className="font-black text-black">$4,262</p>
                  </div>
                </div>
              </div>

              {/* Chart Preview */}
              <div className="rounded-none border-[3px] border-black  p-4 shadow-[4px_4px_0_0_#000]">
                <p className="mb-2 text-sm font-black uppercase">
                  Progress Breakdown
                </p>
                <div className="flex items-end gap-2">
                  <div className="h-12 w-full border-[3px] border-black bg-[#ff5c5c]" />
                  <div className="h-16 w-full border-[3px] border-black bg-[#A3E635]" />
                  <div className="h-10 w-full border-[3px] border-black bg-[#60a5fa]" />
                  <div className="h-8 w-full border-[3px] border-black bg-[#f472b6]" />
                </div>
              </div>

              {/* Timeline */}
              <div className="rounded-none border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_0_#000]">
                <div className="mb-2 flex items-center gap-2">
                  <Calendar className="h-5 w-5 text-black" strokeWidth={2.5} />
                  <span className="text-sm font-black uppercase">
                    Project Timeline
                  </span>
                </div>
                <div className="space-y-3 mt-4">
                  <div className="flex items-center gap-3">
                    <div className="h-3 w-1/3 border-[2px] border-black bg-[#ff5c5c] shadow-[2px_2px_0_0_#000]" />
                    <span className="text-xs font-bold uppercase">
                      Planning
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="h-3 w-1/2 border-[2px] border-black bg-[#60a5fa] shadow-[2px_2px_0_0_#000]" />
                    <span className="text-xs font-bold uppercase">
                      Execution
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="h-3 w-1/4 border-[2px] border-black bg-[#A3E635] shadow-[2px_2px_0_0_#000]" />
                    <span className="text-xs font-bold uppercase">
                      Delivery
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
