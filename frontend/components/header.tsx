"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";

export function Header() {
  const [isVisible, setIsVisible] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      if (currentScrollY > lastScrollY && currentScrollY > 80) {
        setIsVisible(false);
      } else {
        setIsVisible(true);
      }
      setLastScrollY(currentScrollY);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, [lastScrollY]);

  return (
    <header
      className={cn(
        "sticky top-0 z-50 border-b-[4px] border-black bg-white transition-transform duration-300",
        isVisible ? "translate-y-0" : "-translate-y-full",
      )}
    >
      <div className="mx-auto flex h-20 max-w-6xl items-center justify-between px-6">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center border-[3px] border-black bg-[#05a3a5] shadow-[2px_2px_0_0_#000]">
            <span className="text-lg font-black text-black">RF</span>
          </div>
          <span className="text-2xl font-black tracking-tight text-black">
            RFP Flow
          </span>
        </Link>

        <nav className="hidden items-center gap-8 md:flex">
          <Link
            href="#features"
            className="text-sm font-bold text-black border-b-2 border-transparent transition-colors hover:border-black"
          >
            Features
          </Link>
          <Link
            href="#product"
            className="text-sm font-bold text-black border-b-2 border-transparent transition-colors hover:border-black"
          >
            Product
          </Link>
          <Link
            href="ai_validate"
            className="text-sm font-bold text-black border-b-2 border-transparent transition-colors hover:border-black"
          >
            AI Validate
          </Link>
        </nav>

        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" className="hidden sm:inline-flex">
            Sign In
          </Button>
          <Button size="sm" asChild>
            <Link href="#ai-validate">Try Demo</Link>
          </Button>
        </div>
      </div>
    </header>
  );
}
