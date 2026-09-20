"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  ["/", "Overview", "◫"],
  ["/stocks", "Stocks", "↗"],
  ["/news", "Tech News", "▤"],
  ["/gaming", "Gaming", "◇"],
  ["/settings", "Settings", "⚙"],
];

export function Navigation() {
  const pathname = usePathname();
  return (
    <nav aria-label="Main navigation">
      {links.map(([href, label, icon]) => (
        <Link
          key={href}
          href={href}
          aria-current={pathname === href ? "page" : undefined}
        >
          <span aria-hidden="true">{icon}</span>
          {label}
        </Link>
      ))}
    </nav>
  );
}
