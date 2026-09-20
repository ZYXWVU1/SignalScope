import "server-only";

export async function getHealth(): Promise<boolean> {
  try {
    const configuredUrl = process.env.NEXT_PUBLIC_API_URL;
    if (!configuredUrl) return false;
    const base = new URL(configuredUrl);
    if (
      !["http:", "https:"].includes(base.protocol) ||
      base.username ||
      base.password ||
      base.pathname !== "/" ||
      base.search ||
      base.hash
    ) {
      return false;
    }
    const response = await fetch(`${base.origin}/health`, {
      cache: "no-store",
      signal: AbortSignal.timeout(6000),
    });
    if (!response.ok) return false;
    const data: unknown = await response.json();
    return (
      typeof data === "object" &&
      data !== null &&
      "status" in data &&
      data.status === "ok"
    );
  } catch {
    return false;
  }
}
