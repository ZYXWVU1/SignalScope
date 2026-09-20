import type { Metadata } from "next";
import Link from "next/link";
import { Navigation } from "@/components/navigation";
import "./globals.css";

export const metadata: Metadata = {
  title: "SignalScope | Intelligence dashboard",
  description: "Your market, technology, and gaming intelligence workspace.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <a className="skip" href="#main">
          Skip to content
        </a>
        <aside className="sidebar">
          <Link className="brand" href="/">
            <span className="brand-mark">S</span>SignalScope
            <span className="brand-dot">.</span>
          </Link>
          <p className="nav-label">WORKSPACE</p>
          <Navigation />
          <div className="sidebar-footer">
            <span className="status-dot" /> Foundation build
            <p>Three sources. One clear view.</p>
          </div>
        </aside>
        <div className="workspace">
          <header>
            <span>Intelligence workspace</span>
            <span className="badge">PHASE 01</span>
          </header>
          <main id="main">{children}</main>
          <footer>
            SignalScope <span>Markets · Technology · Gaming</span>
          </footer>
        </div>
      </body>
    </html>
  );
}
