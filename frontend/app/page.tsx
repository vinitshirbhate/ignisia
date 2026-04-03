import { Header } from "@/components/header"
import { HeroSection } from "@/components/hero-section"
import { ValueStatement } from "@/components/value-statement"
import { FeatureGrid } from "@/components/feature-grid"
// import { AIValidateDemo } from "@/components/ai-validate-demo"
import { ProductPreview } from "@/components/product-preview"
import { VoiceFeature } from "@/components/voice-feature"
import { VisualPDF } from "@/components/visual-pdf"
import { RiskAwareness } from "@/components/risk-awareness"
import { GlobalCompliance } from "@/components/global-compliance"
import { HumanInTheLoop } from "@/components/human-in-the-loop"
import { FinalCTA } from "@/components/final-cta"
import { Footer } from "@/components/footer"

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <Header />
      <HeroSection />
      <ValueStatement />
      <FeatureGrid />
      {/* <AIValidateDemo /> */}
      <ProductPreview />
      <VoiceFeature />
      <VisualPDF />
      <RiskAwareness />
      <GlobalCompliance />
      <HumanInTheLoop />
      <FinalCTA />
      <Footer />
    </main>
  )
}
