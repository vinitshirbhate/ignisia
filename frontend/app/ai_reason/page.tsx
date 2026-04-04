import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { AIReasonContent } from "./AIReasonContent"

/** Always run client fetch; avoids stale RSC cache and fixes cwd mismatches via /api/reason-strategy. */
export const dynamic = "force-dynamic"
export const revalidate = 0

export default function AIReasonPage() {
  return (
    <div className="flex min-h-screen flex-col bg-[#f8fafc]">
      <Header />
      <AIReasonContent />
      <Footer />
    </div>
  )
}
