import type { NextConfig } from "next";

// Vercel deployments must not accidentally ship local or missing API configuration.
if (process.env.VERCEL === "1") {
  const configuredUrl = process.env.NEXT_PUBLIC_API_URL;
  let valid = false;
  try {
    const url = new URL(configuredUrl ?? "");
    valid =
      url.protocol === "https:" &&
      !url.username &&
      !url.password &&
      url.pathname === "/" &&
      !url.search &&
      !url.hash &&
      !["localhost", "[::1]", "0.0.0.0"].includes(url.hostname) &&
      !url.hostname.startsWith("127.") &&
      !url.hostname.endsWith(".localhost");
  } catch {
    valid = false;
  }
  if (!valid) {
    throw new Error(
      "Set NEXT_PUBLIC_API_URL to your public HTTPS Railway API origin before deploying.",
    );
  }
}

const config: NextConfig = { poweredByHeader: false };
export default config;
