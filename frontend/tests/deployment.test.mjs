import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { getHealth } from "../lib/api.ts";

const frontendRoot = fileURLToPath(new URL("../", import.meta.url));

function withApiUrl(t, value) {
  const previous = process.env.NEXT_PUBLIC_API_URL;
  if (value === undefined) delete process.env.NEXT_PUBLIC_API_URL;
  else process.env.NEXT_PUBLIC_API_URL = value;
  t.after(() => {
    if (previous === undefined) delete process.env.NEXT_PUBLIC_API_URL;
    else process.env.NEXT_PUBLIC_API_URL = previous;
  });
}

test("missing API configuration never falls back to localhost", async (t) => {
  withApiUrl(t, undefined);
  const fetch = t.mock.method(globalThis, "fetch", async () => {
    throw new Error("No request expected");
  });
  assert.equal(await getHealth(), false);
  assert.equal(fetch.mock.callCount(), 0);
});

test("configured cloud API is used with a fresh, bounded health request", async (t) => {
  withApiUrl(t, "https://api.example/");
  t.mock.method(globalThis, "fetch", async (url, options) => {
    assert.equal(url, "https://api.example/health");
    assert.equal(options.cache, "no-store");
    assert.ok(options.signal instanceof AbortSignal);
    return Response.json({ status: "ok" });
  });
  assert.equal(await getHealth(), true);
});

test("backend outages remain an offline state", async (t) => {
  withApiUrl(t, "https://api.example");
  t.mock.method(
    globalThis,
    "fetch",
    async () => new Response(null, { status: 503 }),
  );
  assert.equal(await getHealth(), false);
});

test("invalid credential-bearing API URLs are never requested", async (t) => {
  withApiUrl(t, "https://user:password@api.example");
  const fetch = t.mock.method(globalThis, "fetch", async () => {
    throw new Error("No request expected");
  });
  assert.equal(await getHealth(), false);
  assert.equal(fetch.mock.callCount(), 0);
});

for (const value of [
  undefined,
  "http://api.example",
  "https://localhost",
  "https://127.0.0.1",
]) {
  test(`Vercel configuration rejects ${value ?? "missing API URL"}`, () => {
    const env = { ...process.env, VERCEL: "1" };
    if (value === undefined) delete env.NEXT_PUBLIC_API_URL;
    else env.NEXT_PUBLIC_API_URL = value;
    const result = spawnSync(
      process.execPath,
      [
        "--experimental-strip-types",
        "--input-type=module",
        "-e",
        "import('./next.config.ts')",
      ],
      { cwd: frontendRoot, env, encoding: "utf8" },
    );
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Set NEXT_PUBLIC_API_URL/);
  });
}

test("Vercel configuration accepts an HTTPS cloud origin", () => {
  const result = spawnSync(
    process.execPath,
    [
      "--experimental-strip-types",
      "--input-type=module",
      "-e",
      "import('./next.config.ts')",
    ],
    {
      cwd: frontendRoot,
      env: {
        ...process.env,
        VERCEL: "1",
        NEXT_PUBLIC_API_URL: "https://api.example",
      },
      encoding: "utf8",
    },
  );
  assert.equal(result.status, 0, result.stderr);
});
