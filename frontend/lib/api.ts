import "server-only";

export type Stock = {
  symbol: string;
  companyName: string | null;
  price: number | string | null;
  change: number | string | null;
  changePercent: number | string | null;
  marketTimestamp: string | null;
  dataFreshness: string | null;
};
export type NewsItem = {
  id: number;
  source: string;
  title: string;
  description: string | null;
  url: string;
  category: string;
  publishedAt: string | null;
};
export type GamingItem = {
  id: number;
  title: string;
  game: string | null;
  source: string;
  url: string;
  summary: string | null;
  likes: number | null;
  comments: number | null;
  views: number | null;
  publishedAt: string | null;
};
export type Dashboard = {
  stocks: Stock[];
  technologyNews: NewsItem[];
  gaming: GamingItem[];
  gamingTrending: Array<{
    game: string;
    postCount: number;
    interactions: number;
  }>;
  collectorStatus: Array<{
    collector: string;
    status: string;
    itemsFound: number;
    itemsInserted: number;
    finishedAt: string | null;
  }>;
};

function apiOrigin(): URL | null {
  const configuredUrl = process.env.NEXT_PUBLIC_API_URL;
  if (!configuredUrl) return null;
  try {
    const base = new URL(configuredUrl);
    if (
      !["http:", "https:"].includes(base.protocol) ||
      base.username ||
      base.password ||
      base.pathname !== "/" ||
      base.search ||
      base.hash
    )
      return null;
    return base;
  } catch {
    return null;
  }
}

async function getJson<T>(path: string): Promise<T | null> {
  const base = apiOrigin();
  if (!base) return null;
  try {
    const response = await fetch(`${base.origin}${path}`, {
      cache: "no-store",
      signal: AbortSignal.timeout(8000),
    });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function getHealth(): Promise<boolean> {
  try {
    const data = await getJson<{ status: string }>("/health");
    return data?.status === "ok";
  } catch {
    return false;
  }
}

export function getDashboard() {
  return getJson<Dashboard>("/api/dashboard");
}

export function getStocks() {
  return getJson<Stock[]>("/api/stocks");
}

export function getNews() {
  return getJson<{ items: NewsItem[] }>("/api/news?limit=20");
}

export function getGaming() {
  return getJson<{ items: GamingItem[] }>("/api/gaming?limit=20");
}

export function getWatchlist() {
  return getJson<
    Array<{ symbol: string; companyName: string | null; enabled: boolean }>
  >("/api/watchlist");
}
