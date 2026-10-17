# Cloudflare Web Analytics setup

This GitHub Pages site can use **Cloudflare Web Analytics** without moving DNS or hosting.

## Owner action needed

1. Sign in to [Cloudflare Web Analytics](https://dash.cloudflare.com/?to=/:account/web-analytics) using your own Cloudflare account (a free account is fine).
2. Choose **Add a site**. For the site hostname, enter **sriharshaguthikonda.github.io** (hostname only, no `https://` or path).
3. Choose the manual JavaScript snippet option, then copy the **site token** (or complete beacon snippet) from **Manage site**.
4. Share only the site token/snippet with the maintainer, **not** your Cloudflare password or an API key. The site token is a public browser-side identifier.

## Maintainer activation

- In `index.html`, near `</body>`, replace `REPLACE_WITH_CLOUDFLARE_SITE_TOKEN` with the real site token and remove the surrounding HTML comment markers.
- Keep a **single** beacon script per page. This site's main portfolio is `index.html`; if other standalone HTML pages also need analytics, add that same snippet there once verified.
- Run the repository's navigation checks and existing tests. Merge only when they pass.
- After deployment, load the public website in an ordinary browser (ad blockers can suppress the beacon). Check the browser Network panel for `beacon.min.js` and the analytics request to `cloudflareinsights.com/cdn-cgi/rum`.
- Check Cloudflare **Web Analytics** for visits; the dashboard may take a few minutes. This does not restore visits from before activation.

## Visitor privacy

Cloudflare Web Analytics does not identify named visitors or individual recruiters. Avoid claiming that a visitor from an organisation or city is a named person. Add a short factual privacy statement if site policy calls for it.

References: [Cloudflare official manual setup](https://developers.cloudflare.com/web-analytics/get-started/), [Cloudflare data collection](https://developers.cloudflare.com/web-analytics/data-metrics/data-origin-and-collection/).
