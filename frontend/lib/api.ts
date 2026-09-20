import "server-only";

export async function getHealth(): Promise<boolean> {
  try {
    const response = await fetch(
      `${process.env.BACKEND_URL ?? "http://localhost:8000"}/health`,
      {
        cache: "no-store",
        signal: AbortSignal.timeout(6000),
      },
    );
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
