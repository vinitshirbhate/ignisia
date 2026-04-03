import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function DashboardMock() {
  return (
    <div className="rounded-none border-[3px] border-black bg-white p-4 shadow-[8px_8px_0_0_#000]">
      <div className="mb-4 flex items-center justify-between border-b-[3px] border-black pb-3">
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded-full border-2 border-black bg-red-400" />
          <div className="h-4 w-4 rounded-full border-2 border-black bg-yellow-400" />
          <div className="h-4 w-4 rounded-full border-2 border-black bg-green-400" />
        </div>
        <span className="text-xs font-bold uppercase text-black">BidWise Dashboard</span>
      </div>
      
      <div className="grid gap-4">
        {/* Pricing Table */}
        <Card className="py-4 shadow-none">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Pricing Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Base Cost</span>
                <span className="font-medium">$12,500</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Labor</span>
                <span className="font-medium">$4,200</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Overhead</span>
                <span className="font-medium">$2,100</span>
              </div>
              <div className="flex justify-between border-t border-border pt-2">
                <span className="font-medium">Recommended Bid</span>
                <span className="font-bold text-primary">$22,800</span>
              </div>
            </div>
          </CardContent>
        </Card>
        
        {/* Win Probability */}
        <div className="flex items-center justify-between rounded-lg bg-secondary p-3">
          <span className="text-sm font-medium">Win Probability</span>
          <div className="flex items-center gap-2">
            <div className="h-2 w-24 overflow-hidden rounded-full bg-border">
              <div className="h-full w-3/4 rounded-full bg-primary" />
            </div>
            <span className="text-sm font-semibold text-primary">73%</span>
          </div>
        </div>
        
        {/* Competitor Comparison */}
        <Card className="py-4 shadow-none">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Competitor Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">Your Bid</span>
                  <span className="font-medium">$22,800</span>
                </div>
                <div className="h-2 rounded-full bg-primary" />
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">Competitor A (Est.)</span>
                  <span className="font-medium">$24,500</span>
                </div>
                <div className="h-2 w-[107%] rounded-full bg-chart-3" />
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">Competitor B (Est.)</span>
                  <span className="font-medium">$21,200</span>
                </div>
                <div className="h-2 w-[93%] rounded-full bg-chart-3" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
