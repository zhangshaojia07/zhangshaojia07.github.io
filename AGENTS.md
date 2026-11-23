# Agent notes

Read [docs/site-maintenance.md](docs/site-maintenance.md) before working on site
configuration, templates, images, or deployment. It records known issues, their
status, and checks for confirming fixes.

When your work addresses an issue in that file, update its status and add a dated
entry to the resolution log with the change and verification performed. Keep the
original issue entry so future maintainers can see what was fixed. Keep work within
the user's requested scope; open issues are context for future work.

## Project constraints

- `themes/terminal` is a git submodule. Do not edit files inside it; override
  templates from the project root `layouts/` directory instead. Existing
  overrides are `head.html`, `extended_head.html`, `math.html`, `cover.html`,
  and `img-set.html` under `layouts/partials/`; `figure.html` under
  `layouts/shortcodes/`; and `render-image.html` under
  `layouts/_default/_markup/`.
- When adding images, follow [docs/image-templates.md](docs/image-templates.md).
  Prefer Markdown images or the `figure` shortcode. Raw `<img>` tags must list
  `width`, `height`, `loading`, `decoding`, and `alt`.
- Before committing a new image, resize photos to 1600px width, auto-orient,
  convert P3 to sRGB, and strip metadata. See the preparation section in the
  image templates doc. CI checks GPS metadata and `<img>` attributes.
- Image checks and preset preparation live in `scripts/images.py`. Use
  `python3 scripts/images.py prepare ... --open` to compare presets, and
  `python3 scripts/images.py check` before committing.
- `public/`, `resources/`, `.hugo_build.lock`, and `.obsidian/` are local build
  or editor artifacts. They are gitignored and must not be committed.
- Local Hugo is 0.154.5. CI pins its own version in
  `.github/workflows/hugo.yaml`; read the workflow rather than assuming.
- `hugo` builds with the production environment; `hugo server` uses development.
  Use `hugo.IsProduction` or `hugo.IsServer` for environment-specific rendering.
- To publish a page that stays reachable by URL but hidden from menus, page
  collections, RSS, and sitemaps, set front matter `[build] list = 'never'`,
  `render = 'always'`, `[sitemap] disable = true`, and `noindex = true`.
  `site.GetPage` still resolves such pages, which supports local-only links.

Before committing image changes in this clone, enable the checked-in hook with
`git config --local core.hooksPath .githooks`. If it reports image warnings, show
them to the user and wait for an explicit decision before confirming the prompt.
Do not bypass the hook.
