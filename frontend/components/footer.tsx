import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t-[4px] border-black bg-white px-6 py-12">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-8 md:flex-row">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center border-[3px] border-black bg-[#05a3a5] shadow-[2px_2px_0_0_#000]">
            <span className="text-lg font-black text-black">RF</span>
          </div>
          <span className="text-2xl font-black tracking-tight text-black">
            RFP Flow
          </span>
        </div>

        <nav className="flex flex-wrap items-center justify-center gap-6">
          <Link
            href="#features"
            className="text-sm font-bold uppercase text-black border-b-2 border-transparent transition-colors hover:border-black"
          >
            Features
          </Link>
          <Link
            href="#product"
            className="text-sm font-bold uppercase text-black border-b-2 border-transparent transition-colors hover:border-black"
          >
            Product
          </Link>
          <Link
            href="#pricing"
            className="text-sm font-bold uppercase text-black border-b-2 border-transparent transition-colors hover:border-black"
          >
            Pricing
          </Link>
          <Link
            href="#contact"
            className="text-sm font-bold uppercase text-black border-b-2 border-transparent transition-colors hover:border-black"
          >
            Contact
          </Link>
        </nav>

        <p className="text-sm font-bold text-black/60">
          © 2026 RFP Flow. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
