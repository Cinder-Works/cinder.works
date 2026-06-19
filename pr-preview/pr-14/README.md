# cinder.works

Minimal static landing page intended for GitHub Pages.

## Repository structure

- `index.html` — The main landing page.
- `blog/` — The blog directory, including individual post files and the `index.html` post list.
- `products/` — Contains product pages like `ai-blueprint.html` and `pcb-keychain.html`.
- `oauth/callback.html` — OAuth callback handler.
- `assets/` — CSS and JS assets (e.g., `cinder-triggers.css` and `cinder-triggers.js`).
- `downloads/` — Downloadable files.
- `tools/` — Helper scripts, notably `check_links.py`.
- `sitemap.xml` — Site map for search engines.
- `robots.txt` — Web crawler instructions.
- `CNAME` — Custom domain configuration.
- `404.html` — Custom error page.
- `privacy.html` / `terms.html` — Legal pages.
- `google-apps-script.js` — Google Apps Script for backend functionality.
- `.github/workflows/` — GitHub Actions workflows for `deploy.yml` and `pr-preview.yml`.

## Clean URLs / routing

The site is served as static files with extensionless URLs. This means that a request to `/blog/foo` will map to `blog/foo.html` on the server. A trailing slash like `/blog/` maps to `blog/index.html`. This structure mirrors the logic validated in `tools/check_links.py`.

## Validate links

You can validate internal links and asset integrity by running the included python script from the repository root:

```bash
python tools/check_links.py
```

This script requires no dependencies (Python standard library only) and will exit `0` on success, or `1` if any broken internal links or `sitemap.xml` references are found. See `tools/README.md` for more details.

## Adding a blog post

To add a new blog post, follow this checklist:
1. Create a new file `blog/<slug>.html`. You can copy an existing post like `blog/the-agent-stack.html` as a template, making sure to keep the same `<head>` meta, canonical, and open graph (`og:`) patterns.
2. Add a new `<a class="post-item">` entry to the post list in `blog/index.html`.
3. Add a `<url>` entry to `sitemap.xml` for the new post.
4. Run `python tools/check_links.py` to confirm nothing is broken.

## Deploy (owner / admin) 
1. Repo **Settings → Pages**
2. Source: **GitHub Actions** — `.github/workflows/deploy.yml` publishes `main` to the `gh-pages` branch automatically (no manual branch/folder setting needed)
3. (Pages auto-configures from the Actions deploy; `pr-preview.yml` publishes per-PR previews under `pr-preview/`)
4. (Optional) Custom domain: `cinder.works` (adds/maintains a `CNAME` file)

## Notes
- If the repo stays **private**, GitHub Pages may require a paid plan. Easiest path is making it public.
- This repo is intentionally simple (no build step).
