# sriharshaguthikonda.github.io

Static resume site for Dr. Sri Harsha Guthikonda.

## What’s tracked vs. private
- Tracked: `My_resume.html`, `README.md`, `.gitignore`.
- Ignored (local-only): anything else, including `contact_private.html` (phone/addresses) and `references_private.html`.

## How it works locally
1) Place `My_resume.html`, `contact_private.html`, and `references_private.html` in the same folder.
2) Open `My_resume.html` in a browser.
   - If `contact_private.html` exists, a “Private Contact (local only)” section appears via iframe.
   - If `references_private.html` exists, the References section loads via iframe.
   - If either file is missing, its section stays hidden.

## How it works when published (GitHub Pages)
- Only `My_resume.html` is served; private files are not in the repo (gitignored).
- Visitors will not see phone, addresses, or detailed references.
- Publish by enabling GitHub Pages for this repo (e.g., branch: `main`, folder: `/`).

## Update/publish steps
1) Ensure `.gitignore` keeps everything except `My_resume.html`, `README.md`, `.gitignore`:
   ```
   *
   !.gitignore
   !My_resume.html
   !README.md
   ```
2) Commit and push:
   ```
   git add My_resume.html README.md .gitignore
   git commit -m "Update resume site"
   git push
   ```
3) In GitHub repo settings → Pages: set Source to `main` / root. The site will be at `https://sriharshaguthikonda.github.io/`.

## Notes
- Keep private files local; do not push them.
- To share references/phone, send `contact_private.html` / `references_private.html` separately (not via the public site).
