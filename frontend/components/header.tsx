"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"

export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link href="/" className="flex items-center gap-2">
          {/* <div className="flex h-8 w-8 items-center justify-center rounded-md bg-blue-400">
            <span className="text-sm font-bold text-primary-foreground">QAI</span>
          </div> */}
          <span className="text-lg font-bold text-primary">QuoteAI</span>
        </Link>
        
        <nav className="hidden items-center gap-8 md:flex">
          <Link href="#features" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
            Features
          </Link>
          <Link href="#product" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
            Product
          </Link>
          <Link href="#pricing" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
            Pricing
          </Link>
        </nav>
        
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" className="hidden sm:inline-flex">
            Sign In
          </Button>
          <Button size="sm">
            Try Demo
          </Button>
        </div>
      </div>
    </header>
  )
}
