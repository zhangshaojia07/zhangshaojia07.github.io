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
| SITE-001 | Open | Advisory | Photos used by posts retain GPS coordinates in EXIF metadata. |
| SITE-002 | Open | Advisory | Article images are large and lack responsive loading attributes. |
| SITE-003 | Open | Medium | MathJax loads site-wide and its configuration may race the async script. |
| SITE-004 | Fixed | Medium | Homepage metadata used the theme's placeholder subtitle; some page descriptions were empty. |
| SITE-005 | Open | Low | The theme emits 13 separate CSS requests per page. |
| SITE-006 | Open | Low | The CI npm step currently does nothing and can hide future install failures. |

### SITE-001 — GPS metadata in published photos

The following source images contain EXIF GPS latitude and longitude fields:

- [`team-photo.jpeg`](../content/posts/20261017-ukiepc2026/team-photo.jpeg)
- [`venue.jpeg`](../content/posts/20261021-hackathon/venue.jpeg)
- [`leaderboard.jpeg`](../content/posts/20261021-hackathon/leaderboard.jpeg)
- [`swag.jpeg`](../content/posts/20261021-hackathon/swag.jpeg)

Hugo copied the sampled image byte-for-byte into the generated site. If a photo's
location should remain private, remove its GPS metadata. Replacing a file does
not remove its older version from Git history; handle historical copies
separately if location privacy requires it.

**Acceptance check:** Inspect all publishable images for GPS fields, then inspect
the generated copies. Neither should contain unintended location coordinates.

### SITE-002 — Image weight and loading

At the original audit, image files referenced by the Hackathon, THUPC, and UKIEPC
articles totaled approximately **9.0 MB**, **16.3 MB**, and **6.7 MB**, respectively.
The THUPC total is now **6.1 MB** after replacing the 10.5 MB lake PNG with a
0.3 MB display JPEG. Other sampled pages still have no `loading="lazy"` or explicit
image dimensions. The theme's [cover partial](../themes/terminal/layouts/partials/cover.html)
also emits a plain `<img>`.

Original images can intentionally remain at full resolution. When page weight
matters, generate smaller display images, preferably with responsive variants.
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

At the original audit, the homepage's generated `description` and `og:description` both said
“A simple, retro theme for Hugo”, from the `subtitle` in [`hugo.toml`](../hugo.toml).
The `description` front matter was empty for
[`about`](../content/about/index.md),
[`hello-world`](../content/posts/hello-world/index.md),
[`Notes on IMO 2025`](../content/posts/20260206-notes-on-imo-2025/index.md), and
[`Bridg-it`](../content/posts/20260813-bridg-it-disjoint-spanning-trees/index.md).
Section and taxonomy pages had blank descriptions. The head partial also lacked
author tags and emitted a non-ISO publication time.

Replace the placeholder with a site-specific summary and add concise page
descriptions where the automatic summary is unsuitable. Provide descriptions for
section and taxonomy pages. Emit author metadata and an ISO 8601 publication time
for posts.

**Acceptance check:** Inspect generated `description` and `og:description` tags
for all content and list pages, excluding Hugo redirect aliases. Check author
tags and parse the publication time on posts.

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

Record partial progress and completed fixes here, including the verification
performed.

- **2026-10-22 — SITE-002 (partial):** Replaced the 4032×3024, 10.5 MB
  `Weiming-Lake.png` with a 1440×1080, 0.3 MB
  [`Weiming-Lake.jpg`](../content/posts/20260413-thupc2026/Weiming-Lake.jpg).
  The THUPC article's image files now total 6.1 MB. Verified the generated article
  references the JPEG and no longer publishes the PNG. Other images and loading
  behavior remain for review.
- **2026-10-22 — SITE-004 (partial):** The local
  [head override](../layouts/partials/head.html) now treats `cover = ""` as absent,
  so pages without a cover use the default `og-image.png`. It also reports the
  actual dimensions of page cover images. Verified the default on Shapez
  Reachability and explicit covers on THUPC, UKIEPC, and Hackathon. The homepage
  subtitle and empty descriptions remain unchanged.
- **2026-10-22 — SITE-004 (fixed):** Replaced the homepage placeholder subtitle,
  added descriptions to the four affected pages and list pages, and added author
  and ISO 8601 publication metadata. Hugo built successfully. Checked generated
  descriptions on content and list pages, plus author and parseable publication
  tags on posts.

## Commit-time image review

The versioned [pre-commit hook](../.githooks/pre-commit) examines only staged
added, copied, modified, or renamed images. It warns about GPS EXIF and
files over **5 MiB**, then asks whether to continue. It never edits or compresses
images. Its warnings do not resolve SITE-001 or SITE-002.

Enable it once per clone with `git config --local core.hooksPath .githooks`.
Python 3 is required. Install Pillow to inspect GPS EXIF; if Pillow is missing or
an image cannot be read, the hook warns that the metadata check was unavailable
and still asks for confirmation. When a warning occurs, commit from an
interactive terminal: without a terminal, the hook cancels the commit.
