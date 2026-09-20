import Link from "next/link";

export function DomainPlaceholder({
  title,
  description,
  phase,
}: {
  title: string;
  description: string;
  phase: string;
}) {
  return (
    <>
      <p className="eyebrow">YOUR INTELLIGENCE WORKSPACE</p>
      <h1>{title}</h1>
      <p className="subtitle">{description}</p>
      <section className="panel empty">
        <span className="empty-icon" aria-hidden="true">
          ◇
        </span>
        <h2>Collection has not started</h2>
        <p>
          This section will be connected in {phase}, after the foundation is
          verified.
        </p>
        <p className="muted">Last updated: never · No data collected</p>
        <Link className="text-link" href="/">
          View system overview →
        </Link>
      </section>
    </>
  );
}
