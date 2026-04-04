import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { 
  MapPin, 
  Package, 
  Users, 
  Calculator, 
  AlertCircle,
  IndianRupee,
  Clock,
  Ruler
} from "lucide-react"

const aiOutput = {
  "project_summary": {
    "region": "Mumbai",
    "state": "Maharashtra",
    "project_type": "commercial",
    "area_sqft": 1000,
    "duration_weeks": 8
  },
  "material_costs": {
    "items": [
      {
        "item": "cement",
        "quantity": 100,
        "unit_price_ex_gst": 437,
        "gst": 7866,
        "total_incl_gst": 51566
      },
      {
        "item": "plywood 18mm BWR",
        "quantity": 2000,
        "unit_price_ex_gst": 83,
        "gst": 29880,
        "total_incl_gst": 195880
      },
      {
        "item": "vitrified tiles 600x600",
        "quantity": 1000,
        "unit_price_ex_gst": 106,
        "gst": 19080,
        "total_incl_gst": 125080
      },
      {
        "item": "LED panel light 36W",
        "quantity": 50,
        "unit_price_ex_gst": 1035,
        "gst": 6210,
        "total_incl_gst": 57960
      },
      {
        "item": "laminate sheet 1mm",
        "quantity": 150,
        "unit_price_ex_gst": 1265,
        "gst": 34155,
        "total_incl_gst": 223905
      }
    ],
    "subtotal_ex_gst": 557200,
    "total_gst": 97191,
    "grand_total_incl_gst": 654391
  },
  "labor_costs": {
    "total_labor_cost": 741255,
    "labor_cost_per_sqft": 741
  },
  "import_costs": {
    "none": "No imported items stated in the RFP."
  },
  "summary_totals": {
    "total_materials_with_gst": 654391,
    "total_labor": 741255,
    "total_project_cost": 1390646
  },
  "contingency": {
    "percentage": 5,
    "amount": 69532.3
  },
  "grand_total": 1460178.3
}

function formatCurrency(amount: number) {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)
}

export default async function AIProposalPage() {
  // Using static mock data directly as requested.
  // Note: Add an await fetch() here later when linking to API.
  const data = aiOutput

  return (
    <div className="flex min-h-screen flex-col bg-[#f8fafc]">
      <Header />
      
      <main className="flex-1 px-6 py-12 md:py-16">
        <div className="mx-auto max-w-6xl space-y-12">
          
          {/* Top Banner */}
          <div>
            <h1 className="mb-4 inline-block border-[3px] border-black bg-[#ffdc5c] p-3 text-4xl font-black uppercase tracking-tight text-black shadow-[6px_6px_0_0_#000] md:text-5xl">
              AI Proposal Breakdown
            </h1>
            <p className="mt-2 text-xl font-bold text-black/80">
              Detailed material, labor, and contingency costings automatically extracted from RFP.
            </p>
          </div>

          {/* Project Summary */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <div className="flex items-center gap-3 border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_0_#000]">
              <div className="flex bg-[#A3E635] p-2 border-[3px] border-black">
                <MapPin className="h-6 w-6 text-black" strokeWidth={2.5}/>
              </div>
              <div>
                <p className="text-xs font-black uppercase tracking-wider text-black/60">Location</p>
                <p className="font-bold text-black">{data.project_summary.region}, {data.project_summary.state}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_0_#000]">
              <div className="flex bg-[#f472b6] p-2 border-[3px] border-black">
                <AlertCircle className="h-6 w-6 text-black" strokeWidth={2.5}/>
              </div>
              <div>
                <p className="text-xs font-black uppercase tracking-wider text-black/60">Project Type</p>
                <p className="font-bold uppercase text-black">{data.project_summary.project_type}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_0_#000]">
              <div className="flex bg-[#60a5fa] p-2 border-[3px] border-black">
                <Ruler className="h-6 w-6 text-black" strokeWidth={2.5}/>
              </div>
              <div>
                <p className="text-xs font-black uppercase tracking-wider text-black/60">Area</p>
                <p className="font-bold text-black">{data.project_summary.area_sqft} sqft</p>
              </div>
            </div>
            <div className="flex items-center gap-3 border-[3px] border-black bg-white p-4 shadow-[4px_4px_0_0_#000]">
              <div className="flex bg-[#ffdc5c] p-2 border-[3px] border-black">
                <Clock className="h-6 w-6 text-black" strokeWidth={2.5}/>
              </div>
              <div>
                <p className="text-xs font-black uppercase tracking-wider text-black/60">Duration</p>
                <p className="font-bold text-black">{data.project_summary.duration_weeks} weeks</p>
              </div>
            </div>
          </div>

          <div className="grid gap-8 lg:grid-cols-3">
            
            {/* Materials Table */}
            <Card className="col-span-1 border-[4px] border-black shadow-[8px_8px_0_0_#000] lg:col-span-2">
              <CardHeader className="border-b-[3px] border-black bg-[#A3E635] pb-4">
                <div className="flex items-center gap-2">
                  <Package className="h-8 w-8 text-black" strokeWidth={2.5} />
                  <CardTitle className="text-2xl font-black uppercase text-black">
                    Material Costs
                  </CardTitle>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead className="border-b-[3px] border-black bg-white">
                      <tr>
                        <th className="p-4 text-xs font-black uppercase tracking-wider text-black">Item</th>
                        <th className="p-4 text-center text-xs font-black uppercase tracking-wider text-black">Qty</th>
                        <th className="p-4 text-right text-xs font-black uppercase tracking-wider text-black">Unit (ex GST)</th>
                        <th className="p-4 text-right text-xs font-black uppercase tracking-wider text-black">Total (inc GST)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y-[3px] divide-black bg-white font-bold">
                      {data.material_costs.items.map((item, i) => (
                        <tr key={i} className="hover:bg-[#f8fafc]">
                          <td className="p-4 uppercase">{item.item}</td>
                          <td className="p-4 text-center">{item.quantity}</td>
                          <td className="p-4 text-right">{formatCurrency(item.unit_price_ex_gst)}</td>
                          <td className="p-4 text-right text-[#05a3a5]">{formatCurrency(item.total_incl_gst)}</td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot className="border-t-[4px] border-black bg-[#ffdc5c] font-black uppercase text-black">
                      <tr>
                        <td colSpan={2} className="p-4">Material Subtotals</td>
                        <td className="p-4 text-right text-xs">GST: {formatCurrency(data.material_costs.total_gst)}</td>
                        <td className="p-4 text-right text-lg">{formatCurrency(data.material_costs.grand_total_incl_gst)}</td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </CardContent>
            </Card>

            {/* Sidebar Costs & Totals */}
            <div className="flex flex-col gap-6">
              <Card className="flex-1 border-[4px] border-black bg-white shadow-[8px_8px_0_0_#000]">
                <CardHeader className="border-b-[3px] border-black bg-[#60a5fa] pb-3">
                  <CardTitle className="flex items-center gap-2 text-lg font-black uppercase text-black">
                    <Users className="h-6 w-6" strokeWidth={3} /> Labor & Imports
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col gap-4 pt-6">
                  <div>
                    <p className="text-xs font-black uppercase text-black/60">Total Labor Cost</p>
                    <p className="text-2xl font-black text-black">{formatCurrency(data.labor_costs.total_labor_cost)}</p>
                    <p className="mt-1 text-sm font-bold text-black/80">{formatCurrency(data.labor_costs.labor_cost_per_sqft)} per sqft</p>
                  </div>
                  <div className="border-t-[3px] border-black pt-4">
                    <p className="text-xs font-black uppercase tracking-wider text-black/60">Import Alerts</p>
                    <div className="mt-2 inline-block border-[3px] border-black bg-[#f472b6] p-2 text-sm font-bold uppercase text-black shadow-[2px_2px_0_0_#000]">
                      {data.import_costs.none}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="flex-1 border-[4px] border-black bg-white shadow-[8px_8px_0_0_#000]">
                <CardHeader className="border-b-[3px] border-black bg-[#ff5c5c] pb-3">
                  <CardTitle className="flex items-center gap-2 text-lg font-black uppercase text-black">
                    <Calculator className="h-6 w-6" strokeWidth={3} /> Grand Total
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 pt-4">
                  <div className="flex justify-between font-bold text-black/80">
                    <span>Base Project Cost</span>
                    <span>{formatCurrency(data.summary_totals.total_project_cost)}</span>
                  </div>
                  <div className="flex justify-between font-bold text-[#ff5c5c]">
                    <span>Contingency ({data.contingency.percentage}%)</span>
                    <span>+{formatCurrency(data.contingency.amount)}</span>
                  </div>
                  <div className="mt-4 border-[3px] border-black bg-black p-4 text-center text-white shadow-[4px_4px_0_0_#A3E635]">
                    <p className="text-sm font-black uppercase tracking-widest text-[#A3E635]">Final Estimated Cost</p>
                    <p className="mt-1 text-4xl font-black">{formatCurrency(data.grand_total)}</p>
                  </div>
                </CardContent>
              </Card>
            </div>
            
          </div>
        </div>
      </main>

      <Footer />
    </div>
  )
}
