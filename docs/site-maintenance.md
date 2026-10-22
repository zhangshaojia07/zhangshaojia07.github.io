# Site maintenance log

This file tracks findings from a read-only audit on **2026-10-22**. It lives outside
Hugo's `content/` and `static/` directories, so it is not part of the published site.

The audit used Hugo **0.154.5** locally; the GitHub Actions workflow specifies
**0.155.0**. The build succeeded, and a check of generated `href` and `src` values
found no missing internal targets. External links were not checked.

## How to maintain this log

- Use `Open`, `In progress`, `Fixed`, or `Deferred` in the status column.
- Keep issue IDs and descriptions after a fix. Mark an issue `Fixed` only after
  its acceptance check passes.
- For each fix, add a dated entry to the resolution log with the issue ID, a
  commit or PR reference if available, and the verification performed.
- Recheck measurements when changing images or build tooling; the numbers below
  are from the audit date.

## Issues

| ID | Status | Priority | Summary |
| --- | --- | --- | --- |
| SITE-001 | Open | High | Photos used by posts retain GPS coordinates in EXIF metadata. |
| SITE-002 | Open | High | Article images are large and lack responsive loading attributes. |
| SITE-003 | Open | Medium | MathJax loads site-wide and its configuration may race the async script. |
| SITE-004 | Open | Medium | Homepage metadata uses the theme's placeholder subtitle; some page descriptions are empty. |
| SITE-005 | Open | Low | The theme emits 13 separate CSS requests per page. |
| SITE-006 | Open | Low | The CI npm step currently does nothing and can hide future install failures. |

### SITE-001 — GPS metadata in published photos

The following source images contain EXIF GPS latitude and longitude fields:

- [`team-photo.jpeg`](../content/posts/20261017-ukiepc2026/team-photo.jpeg)
- [`venue.jpeg`](../content/posts/20261021-hackathon/venue.jpeg)
- [`leaderboard.jpeg`](../content/posts/20261021-hackathon/leaderboard.jpeg)
- [`swag.jpeg`](../content/posts/20261021-hackathon/swag.jpeg)

Hugo copied the sampled image byte-for-byte into the generated site. Remove
unwanted metadata from published copies. Replacing a file does not remove its
older version from Git history; handle historical copies separately if location
privacy requires it.

**Acceptance check:** Inspect all publishable images for GPS fields, then inspect
the generated copies. Neither should contain unintended location coordinates.

### SITE-002 — Image weight and loading

In the generated pages, image files referenced by the Hackathon, THUPC, and UKIEPC
articles total approximately **9.0 MB**, **16.3 MB**, and **6.7 MB**, respectively.
[`Weiming-Lake.png`](../content/posts/20260413-thupc2026/Weiming-Lake.png)
alone is about **10.5 MB**. The sampled pages have no `loading="lazy"` or explicit
image dimensions. The theme's [cover partial](../themes/terminal/layouts/partials/cover.html)
also emits a plain `<img>`.

Generate appropriately sized display images, preferably with responsive variants.
Add explicit dimensions to avoid layout shifts, and lazy-load images below the
initial viewport. Preserve an accessible full-resolution version where useful.

**Acceptance check:** Compare the generated image transfer sizes and inspect the
rendered `<img>` tags for responsive sources, dimensions, and appropriate loading
behavior. Check visual quality on mobile and desktop.

### SITE-003 — MathJax on every page

[`hugo.toml`](../hugo.toml) sets `params.math = true`, so the MathJax CDN script
appears even on pages without formulas. In [`math.html`](../layouts/partials/math.html),
the `async` script tag precedes the inline MathJax configuration; it can run
before that configuration is assigned.

Enable math only on pages that need it, and place the configuration before the
loader script.

**Acceptance check:** Non-math pages should have no MathJax request; formulas
should render correctly on math pages, including with a warm cache.

### SITE-004 — Site descriptions and social metadata

The homepage's generated `description` and `og:description` both say
“A simple, retro theme for Hugo”, from the `subtitle` in [`hugo.toml`](../hugo.toml).
The `description` front matter is empty for
[`about`](../content/about/index.md),
[`hello-world`](../content/posts/hello-world/index.md),
[`Notes on IMO 2025`](../content/posts/20260206-notes-on-imo-2025/index.md), and
[`Bridg-it`](../content/posts/20260813-bridg-it-disjoint-spanning-trees/index.md).

Replace the placeholder with a site-specific summary and add concise page
descriptions where the automatic summary is unsuitable.

**Acceptance check:** Inspect generated `description` and `og:description` tags
for the homepage and affected pages.

### SITE-005 — Separate CSS requests

The theme's [head partial](../themes/terminal/layouts/partials/head.html) outputs
each `assets/css/*.css` file as its own stylesheet. The audit build emitted **13**
stylesheet requests per page, including one with no CSS rules.

Consider a local template override that combines styles while preserving their
cascade order.

**Acceptance check:** Confirm fewer stylesheet requests and compare the appearance
of representative pages before and after the change.

### SITE-006 — CI dependency setup

The [workflow](../.github/workflows/hugo.yaml) runs
`[[ -f package-lock.json || -f npm-shrinkwrap.json ]] && npm ci || true` at the
repository root. Neither lockfile currently exists there, so this step is a no-op.
If a lockfile is added, `|| true` would also suppress an `npm ci` failure.

Remove unused setup steps, or use an explicit conditional that lets installation
errors fail the build.

**Acceptance check:** Run the workflow after the change and confirm that required
dependencies install and a failed required install fails the job.

## Resolution log

No fixes recorded as of **2026-10-22**. Add entries here when issues are fixed,
for example:

`YYYY-MM-DD — SITE-XXX — Fixed in <commit or PR>. Verified with <specific check>.`
