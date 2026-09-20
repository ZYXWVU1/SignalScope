import Link from "next/link";
export default function NotFound() {
  return (
    <section className="panel empty">
      <h1>Page not found</h1>
      <Link className="text-link" href="/">
        Back to overview →
      </Link>
    </section>
  );
}
