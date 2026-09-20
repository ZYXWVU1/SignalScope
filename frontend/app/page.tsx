import Link from "next/link";
import { getDashboard, getHealth } from "@/lib/api";
import { Refresh } from "@/components/refresh";

export const dynamic = "force-dynamic";

export default async function Overview() {
  const connected = await getHealth();
  const dashboard = connected ? await getDashboard() : null;
  const stocks = dashboard?.stocks ?? [];
  const technologyNews = dashboard?.technologyNews ?? [];
  const gaming = dashboard?.gaming ?? [];
  return (
    <>
      <div className="heading">
        <div>
          <p className="eyebrow">A CLEARER VIEW OF WHAT MATTERS</p>
          <h1>Your intelligence overview</h1>
          <p className="subtitle">
            Follow the markets, ideas, and games that move your world.
          </p>
        </div>
        <Refresh />
      </div>
      <div
        className={`connection ${connected ? "ready" : "offline"}`}
        role="status"
      >
        <span className="status-dot" />
        <div>
          <strong>
            {connected
              ? "Backend and database connected"
              : "Waiting for the backend"}
          </strong>
          <p>
            {connected
              ? "The API and database migration checks passed."
              : "The API or database is unavailable. Your workspace is still accessible."}
          </p>
        </div>
      </div>
      <section className="stats" aria-label="Data sources">
        {[
          ["Markets", "Your personal market radar", "↗", stocks.length],
          [
            "Technology",
            "Keep up with what’s next",
            "▤",
            technologyNews.length,
          ],
          ["Gaming", "Community signals, in focus", "◇", gaming.length],
        ].map(([name, description, icon]) => (
          <article className="panel stat" key={name}>
            <div className="stat-top">
              <span>{name}</span>
              <span className="tile-icon">{icon}</span>
            </div>
            <div className="big-number">
              {icon === "↗"
                ? stocks.length
                : icon === "▤"
                  ? technologyNews.length
                  : gaming.length}
            </div>
            <p>{description}</p>
            <span className="muted">Not collecting yet</span>
          </article>
        ))}
      </section>
      <div className="overview-grid">
        <section className="panel">
          <div className="panel-heading">
            <h2>Monitored stocks</h2>
            <span className="badge">MARKETS</span>
          </div>
          <div className="empty">
            <span className="empty-icon">↗</span>
            <h3>
              {stocks.length
                ? `${stocks.length} monitored stock${stocks.length === 1 ? "" : "s"}`
                : "Your watchlist starts here"}
            </h3>
            <p>
              {stocks.length
                ? stocks.map((stock) => stock.symbol).join(" · ")
                : "Add a stock in Settings, then run the stock collector."}
            </p>
            <Link className="text-link" href="/settings">
              Watchlist settings →
            </Link>
          </div>
        </section>
        <section className="panel">
          <div className="panel-heading">
            <h2>Source status</h2>
            <span className="muted">Last updated</span>
          </div>
          {["Stock prices", "Technology news", "Xiaoheihe gaming"].map(
            (name) => (
              <div className="source-row" key={name}>
                <div>
                  <strong>{name}</strong>
                  <p>No successful collection yet</p>
                </div>
                <span className="badge">PENDING</span>
              </div>
            ),
          )}
          <p className="footnote">
            Freshness will reflect collection timestamps. Market data will
            identify any provider delay.
          </p>
        </section>
      </div>
      <section className="panel foundation">
        <div>
          <p className="eyebrow">BUILT ON A RELIABLE FOUNDATION</p>
          <h2>Independent sources. A unified perspective.</h2>
          <p>
            The foundation connects Next.js, FastAPI, and PostgreSQL. Collectors
            will be added and verified one domain at a time.
          </p>
        </div>
        <span className="foundation-art" aria-hidden="true">
          ◎
        </span>
      </section>
    </>
  );
}
