import { getGaming } from "@/lib/api";

export const dynamic = "force-dynamic";

export default function Gaming() {
  return <GamingContent />;
}

async function GamingContent() {
  const response = await getGaming();
  const items = response?.items ?? [];
  return (
    <>
      <p className="eyebrow">PUBLIC COMMUNITY SIGNALS</p>
      <h1>Gaming</h1>
      <p className="subtitle">Public gaming content and community trends.</p>
      <section className="panel data-panel">
        <div className="panel-heading">
          <h2>Latest gaming posts</h2>
          <span className="muted">SignalScope stored content</span>
        </div>
        {!response ? (
          <div className="empty">
            <h2>Gaming unavailable</h2>
            <p>Connect the backend to read collected posts.</p>
          </div>
        ) : items.length === 0 ? (
          <div className="empty">
            <h2>No gaming posts yet</h2>
            <p>
              Run the conservative public Xiaoheihe collector after configuring
              a permitted URL.
            </p>
          </div>
        ) : (
          <div className="data-list">
            {items.map((item) => (
              <article className="data-row" key={item.id}>
                <div>
                  <span className="badge">{item.game ?? "Gaming"}</span>
                  <h3>{item.title}</h3>
                  <p>{item.summary ?? ""}</p>
                </div>
                <div className="row-meta">
                  {item.likes ?? 0} likes · {item.comments ?? 0} comments
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
