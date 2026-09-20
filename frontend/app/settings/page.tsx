import { getWatchlist } from "@/lib/api";

export const dynamic = "force-dynamic";

export default function Settings() {
  return <SettingsContent />;
}

async function SettingsContent() {
  const stocks = await getWatchlist();
  return (
    <>
      <p className="eyebrow">YOUR INTELLIGENCE WORKSPACE</p>
      <h1>Settings & watchlist</h1>
      <p className="subtitle">
        Choose the stocks you want SignalScope to monitor.
      </p>
      <section className="panel data-panel">
        <div className="panel-heading">
          <h2>Monitored stocks</h2>
          <span className="badge">PERSISTED IN POSTGRESQL</span>
        </div>
        {!stocks ? (
          <div className="empty">
            <h2>Watchlist unavailable</h2>
            <p>Connect the backend to manage monitored symbols.</p>
          </div>
        ) : stocks.length === 0 ? (
          <div className="empty">
            <h2>No monitored stocks yet</h2>
            <p>
              Use POST /api/watchlist to add a symbol, then run the stock
              collector.
            </p>
          </div>
        ) : (
          <div className="data-list">
            {stocks.map((stock) => (
              <div className="data-row" key={stock.symbol}>
                <div>
                  <strong>{stock.symbol}</strong>
                  <p>{stock.companyName ?? "Monitored symbol"}</p>
                </div>
                <span className="badge">
                  {stock.enabled ? "ENABLED" : "DISABLED"}
                </span>
              </div>
            ))}
          </div>
        )}
      </section>
    </>
  );
}
