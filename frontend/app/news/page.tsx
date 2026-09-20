import { getNews } from "@/lib/api";

export const dynamic = "force-dynamic";

export default function News() {
  return <NewsContent />;
}

async function NewsContent() {
  const response = await getNews();
  const items = response?.items ?? [];
  return (
    <>
      <p className="eyebrow">SIGNALS FROM THE TECH WORLD</p>
      <h1>Technology news</h1>
      <p className="subtitle">
        The stories shaping technology, organized in one place.
      </p>
      <section className="panel data-panel">
        <div className="panel-heading">
          <h2>Latest coverage</h2>
          <span className="muted">Rule-based categories · stored articles</span>
        </div>
        {!response ? (
          <div className="empty">
            <h2>News unavailable</h2>
            <p>Connect the backend to read collected articles.</p>
          </div>
        ) : items.length === 0 ? (
          <div className="empty">
            <h2>No technology articles yet</h2>
            <p>
              Run the technology news collector after configuring NEWS_API_KEY.
            </p>
          </div>
        ) : (
          <div className="data-list">
            {items.map((item) => (
              <article className="data-row" key={item.id}>
                <div>
                  <span className="badge">{item.category}</span>
                  <h3>{item.title}</h3>
                  <p>{item.description ?? ""}</p>
                </div>
                <div className="row-meta">
                  {item.source}
                  <br />
                  {item.publishedAt
                    ? new Date(item.publishedAt).toLocaleString()
                    : "Unknown time"}
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </>
  );
}
