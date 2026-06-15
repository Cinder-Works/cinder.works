# cinder.works

Minimal static landing page intended for GitHub Pages.

## Deploy (owner / admin) 
1. Repo **Settings → Pages**
2. Source: **GitHub Actions** — `.github/workflows/deploy.yml` publishes `main` to the `gh-pages` branch automatically (no manual branch/folder setting needed)
3. (Pages auto-configures from the Actions deploy; `pr-preview.yml` publishes per-PR previews under `pr-preview/`)
4. (Optional) Custom domain: `cinder.works` (adds/maintains a `CNAME` file)

## Notes
- If the repo stays **private**, GitHub Pages may require a paid plan. Easiest path is making it public.
- This repo is intentionally simple (no build step).
