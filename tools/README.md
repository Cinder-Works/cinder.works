# tools/check_links.py

Validates internal link and asset integrity for the static site.

Because the site uses extensionless clean URLs (e.g., `/blog/` maps to `blog/index.html` and `/blog/post` maps to `blog/post.html`), this script reads all `.html` files and `sitemap.xml`, extracts internal links (starting with `/` or `https://cinder.works/`), resolves them to the expected file on disk, and errors if the file does not exist.

## Run

Run from the root of the repository:

```bash
python tools/check_links.py
```

It requires no dependencies (Python standard library only). Exits `0` on success, `1` if any errors are found.
