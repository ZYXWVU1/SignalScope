import { getStocks } from "@/lib/api";

export const dynamic = "force-dynamic";

export default function Stocks() {
  return <StocksContent />;
}

async function StocksContent() {
  const stocks = await getStocks();
  return (
    <>
      <p className="eyebrow">MARKET RADAR</p>
      <h1>Stocks</h1>
      <p className="subtitle">A focused view of the companies you follow.</p>
      <section className="panel data-panel">
        <div className="panel-heading">
          <h2>Watchlist</h2>
          <span className="muted">Latest stored snapshot</span>
        </div>
        {!stocks ? (
          <div className="empty">
            <h2>Stocks unavailable</h2>
            <p>Connect the backend to read the watchlist.</p>
          </div>
        ) : stocks.length === 0 ? (
          <div className="empty">
            <h2>No monitored stocks yet</h2>
            <p>Add a symbol in Settings, then run the stock collector.</p>
          </div>
        ) : (
          <div className="data-grid">
            {stocks.map((stock) => (
              <article className="data-card" key={stock.symbol}>
                <div>
                  <strong>{stock.symbol}</strong>
                  <p>{stock.companyName ?? "Monitored symbol"}</p>
                </div>
                <div className="data-value">
                  {stock.price == null
                    ? "—"
                    : `$${Number(stock.price).toFixed(2)}`}
                  <small>
                    {stock.changePercent == null
                      ? "No snapshot"
                      : `${Number(stock.changePercent).toFixed(2)}% · ${stock.dataFreshness}`}
                  </small>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </>
  );
}
