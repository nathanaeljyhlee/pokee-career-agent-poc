"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Home" },
  { href: "/upload", label: "Upload" },
  { href: "/transcript", label: "Transcript" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/recommendations/courses", label: "Courses" },
  { href: "/recommendations/projects", label: "Projects" },
  { href: "/recommendations/jobs", label: "Jobs" },
  { href: "/explore", label: "Explore" },
];

export function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="bg-[#006747] text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-2 font-bold text-lg">
            <svg viewBox="0 0 24 24" fill="currentColor" className="w-7 h-7">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" fill="none" />
            </svg>
            Babson Career Intelligence
          </Link>
          <div className="hidden md:flex items-center gap-1">
            {links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href))
                    ? "bg-white/20 text-white"
                    : "text-white/80 hover:bg-white/10 hover:text-white"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
}
