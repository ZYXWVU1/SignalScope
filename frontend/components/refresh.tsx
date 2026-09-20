"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";

export function Refresh() {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  return (
    <button
      disabled={pending}
      onClick={() => startTransition(() => router.refresh())}
    >
      {pending ? "Checking…" : "↻ Check connection"}
    </button>
  );
}
