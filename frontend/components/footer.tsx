import Link from "next/link"

export function Footer() {
  return (
    <footer className="border-t border-border bg-background px-6 py-12">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-8 md:flex-row">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary">
            <span className="text-sm font-bold text-primary-foreground">B</span>
          </div>
          <span className="text-lg font-semibold text-primary">QuoteAI</span>
        </div>
        
        <nav className="flex flex-wrap items-center justify-center gap-6">
          <Link href="#features" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
            Features
          </Link>
          <Link href="#product" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
            Product
          </Link>
          <Link href="#pricing" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
            Pricing
          </Link>
          <Link href="#contact" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
            Contact
          </Link>
        </nav>
        
        <p className="text-sm text-muted-foreground">
          © 2026 QuoteAI. All rights reserved.
        </p>
      </div>
    </footer>
  )
}
