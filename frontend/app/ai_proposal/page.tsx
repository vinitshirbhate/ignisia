import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { AIProposalContent } from "./AIProposalContent"

export const dynamic = "force-dynamic"

export default function AIProposalPage() {
  return (
    <div className="flex min-h-screen flex-col bg-[#f8fafc]">
      <Header />
      <AIProposalContent />
      <Footer />
    </div>
  )
}
