# Xiaoheihe public collection research

Research completed before implementing the collector on 2026-09-20.

## Public pages inspected

- `https://xiaoheihe.cn/` is the official public site listed in search results, but its
  homepage timed out during this environment's direct fetch. No authenticated session was used.
- `https://api.xiaoheihe.cn/maxnews/app/share/detail/2651936` returned public HTML. The page
  exposed a public title, source branding, a PC-game label, summary text, images, publication
  content, and a public post URL. It also showed that comments are presented as a separate
  public section, but this collector does not request comments or private data.
- No public feed endpoint was invented from search results. The repository contained no prior
  endpoint, selector, or collector implementation to reuse.

## Robots and rendering

The official homepage and `robots.txt` were not reliably fetchable from this environment.
The selected method therefore does not crawl an unverified feed. It accepts explicitly
configured public post URLs or a configured public feed URL and parses only public JSON-LD
`Article`, `NewsArticle`, or `SocialMediaPosting` records in returned HTML. It does not use
Playwright, login, CAPTCHA handling, anti-bot bypass, private endpoints, or hidden API calls.

## Selected collection method

`app.collectors.gaming.XiaoheihePublicProvider` uses a bounded `httpx` client, an explicit
User-Agent, one request at a time, and the configured `XHH_REQUEST_DELAY_SECONDS` between
multiple URLs. `parse_public_html` is deliberately conservative: when the public document
does not expose JSON-LD records, it returns zero records and records a successful empty run.
The endpoint can be exercised without touching a website by injecting a mocked client in tests.

Set `XHH_PUBLIC_POST_URLS` to a JSON list of known public post URLs for a controlled first run,
or set `XHH_PUBLIC_FEED_URL` to a public page that the site rules allow the operator to collect.
With neither setting, the finite command records a successful empty run and makes no request.
Do not add guessed API routes. If the official site requires JavaScript or authentication to
display a feed, leave the collector empty and document the limitation rather than bypassing it.

## Data and limits

The collector stores only public post ID/title/game/author/URL/summary/image/engagement fields
when present. Missing values stay nullable. A SHA-256 hash of normalized title and URL prevents
duplicates. Every successful run adds a metrics snapshot; failures are isolated in `collector_runs`.

Source: [public Xiaoheihe detail page](https://api.xiaoheihe.cn/maxnews/app/share/detail/2651936).
