"use client";
export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <section role="alert" className="panel empty">
      <h1>Unable to load this view</h1>
      <p>Please try again.</p>
      <button onClick={reset}>Retry</button>
    </section>
  );
}
