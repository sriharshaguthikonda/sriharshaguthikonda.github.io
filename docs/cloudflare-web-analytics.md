# Cloudflare Web Analytics

## Status

Cloudflare Web Analytics is enabled in the portfolio homepage `index.html` using the owner-supplied site token `eca18986ce194f0ca27ea9a8847ff3c6`.

The site remains hosted on GitHub Pages; no DNS, CDN or hosting change is required. The beacon is a third-party module script loaded from Cloudflare. Its token is a public browser-side site identifier, not an API secret.

## Installation

One beacon script directly before the closing `</body>` tag:

```html
<!-- Cloudflare Web Analytics -->
<script type="module" src="https://static.cloudflareinsights.com/beacon.min.js"
        data-cf-beacon='{"token":"eca18986ce194f0ca27ea9a8847ff3c6"}'></script>
<!-- End Cloudflare Web Analytics -->
```

Do not add a second copy in `index.html`, a shared template, tag manager or Cloudflare automatic injection; duplicate beacons can lead to missing or skewed data.

## Verification after merge

1. Run repository checks:
   ```sh
   python scripts/sync_navigation.py --check
   python -m unittest discover -s tests -p "test_*.py"
   ```
   Check the GitHub Actions status before merging; a local/static inspection alone is not a substitute for CI.
2. Load https://sriharshaguthikonda.github.io/ in an ordinary browser (without a blocking extension) and inspect Page Source for **one** Cloudflare script with the exact token.
3. In Developer Tools > Network, confirm `beacon.min.js` loads from `static.cloudflareinsights.com` and a POST to `cloudflareinsights.com/cdn-cgi/rum` appears (may be sent when the page is hidden).
4. In Cloudflare > Web Analytics, select the `sriharshaguthikonda.github.io` site. Wait a few minutes for reporting; only visits after activation can appear.
5. If missing, verify the hostname is correct in Cloudflare's **Manage site**, disable blockers while checking, and inspect browser console for Content Security Policy (CSP) or CORS errors.
6. Audit any standalone HTML pages that visitors can navigate to independently; the manual beacon only tracks pages where it is embedded.

## Privacy and interpretation

Cloudflare Web Analytics reports aggregated visits, page views, sources and performance, not the real identity of a visitor. Do not infer an individual recruiter or employer from a network, city or referral. Do not add extra identity tracking.

Official docs:
- https://developers.cloudflare.com/web-analytics/get-started/
- https://developers.cloudflare.com/web-analytics/faq/
- https://developers.cloudflare.com/web-analytics/data-metrics/data-origin-and-collection/
