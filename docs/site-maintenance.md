# Site maintenance log

This file tracks findings from a read-only audit on **2026-10-22** and a
read-only re-verification on **2026-11-23**. It lives outside Hugo's `content/`
and `static/` directories, so it is not part of the published site.

Both checks used Hugo **0.154.5** locally; the GitHub Actions workflow specifies
**0.155.0**. The build succeeded on both dates, and a check of generated `href`
and `src` values found no missing internal targets. External links were not
checked.

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
| SITE-001 | Fixed | Advisory | Photos used by posts retain GPS coordinates in EXIF metadata. |
| SITE-002 | Fixed | Advisory | Article images are large and lack responsive loading attributes. |
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
0.3 MB display JPEG. The 2026-11-23 re-check measured **8.9 MB**, **6.1 MB**, and
**6.7 MB** for the same three articles; the largest single files remain
`awkward-photo.jpg` (5.6 MB) and `team-photo.jpeg` (5.4 MB). Other sampled pages
still have no `loading="lazy"` or explicit image dimensions. The theme's
[cover partial](../themes/terminal/layouts/partials/cover.html) also emits a plain
`<img>`.

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
- **2026-11-23 — Re-verification:** Built the site locally with Hugo 0.154.5
  (`hugo --gc --minify --cleanDestinationDir`, 69 pages, 84 ms). Re-checked each
  open issue against source and generated output: SITE-001 still finds the same
  four GPS images; SITE-002 measured the same image totals and found no `loading`
  or dimension attributes; SITE-003 confirmed `params.math = true` and that the
  `async` script still precedes its configuration; SITE-005 counted 13 stylesheet
  requests per page; SITE-006 confirmed the npm step is still a no-op. SITE-004
  remains fixed.

- **2026-11-23 - SITE-002 (in progress):** Added local template overrides
  that render responsive images: [`img-set.html`](../layouts/partials/img-set.html)
  computes `src`, `srcset`, and dimensions; [`cover.html`](../layouts/partials/cover.html)
  overrides the theme cover partial; [`figure.html`](../layouts/shortcodes/figure.html)
  replaces the embedded figure shortcode; and
  [`render-image.html`](../layouts/_default/_markup/render-image.html) handles
  Markdown images. JPEG images get 480/960/1200/1600 variants at quality 85;
  PNG/WebP/TIFF images wider than 1600px get 480/960/1200/1600 WebP variants at
  quality 90. `images.AutoOrient` corrects EXIF orientation, and originals wider
  than 1600px are excluded from `srcset` so phones do not fetch them. Every
  generated `<img>` now has `width`, `height`, `loading`, `decoding`, and `alt`;
  the three raw `<img>` tags in the IMO post and the showcase page were given
  explicit dimensions. Built with Hugo 0.154.5: 69 pages, 79 processed images,
  cold build 11.4 s (452 MB peak RSS), warm build under 2 s. Verified 0 images
  missing dimensions, loading, decoding, or alt text, and 0 missing `srcset`
  targets. Deduplicated image transfer fell from 9.04 MB to about 0.75 MB at
  390 CSS px DPR3, 553 KB at 784 CSS px DPR1, and 1.15 MB at DPR2 on the
  Hackathon article. Replacing the six largest source images and removing their
  GPS metadata are still pending. Several source photos use Display P3 ICC
  profiles; replacement images should be converted to sRGB before commit,
  because Hugo's processed variants do not carry the source ICC profile.

- **2026-11-23 - SITE-002 (progress):** Fixed the image distortion introduced by
  the explicit `width`/`height` attributes: [`extended_head.html`](../layouts/partials/extended_head.html)
  now sets `img { height: auto; }`, and browser checks confirm the rendered
  content-box ratios match the source files. Added
  [image templates](../docs/image-templates.md) and made the
  [showcase](../content/showcase/index.md) demonstrate Markdown, raw `<img>`,
  and `figure` forms. Added
  [`scripts/images.py`](../scripts/images.py) to CI so
  generated `<img>` tags without `src`, `width`, `height`, `loading`,
  `decoding`, or `alt` fail the build. Generated a local `image-review/`
  directory (gitignored) with 10 optimized files:
  photos and P3 images converted to sRGB and capped at 1600px width, and three
  PNG images converted to WebP quality 90. Totals fell from 21.6 MB to
  2.8 MB; every output has 0 EXIF keys and 0 GPS tags. `team-photo.jpeg` uses
  JPEG q92 with 4:4:4 chroma for extra face detail; the other photos use q85.
  Originals are untouched;
  replacement awaits review. The privacy checker was added to the same CLI and
  enabled after the GPS sources were replaced.
- **2026-11-23 - SITE-001 (partial):** The review copies generated for SITE-002
  have GPS metadata removed, but the four source files and Git history still
  contain GPS coordinates. Source replacement is pending.
- **2026-11-23 - SITE-001 (fixed):** Replaced the four GPS source photos with
  GPS-free versions. `scripts/images.py check-privacy` reports 0 GPS tags in `content`
  (27 images) and in the generated site (77 images). Older blobs remain in Git
  history; handle history separately if location privacy requires it.
- **2026-11-23 - SITE-002 (fixed):** Replaced the six largest sources and the
  two additional P3 photos with 1600px sRGB copies, converted three PNGs to
  WebP, updated the cover and figure references, and removed the old PNGs.
  WebP sources now receive 480/960/1200 variants. WebP covers generate a
  1200x630 JPEG for `og:image`. Built with Hugo 0.154.5 and 0.155.0; attribute
  and privacy checks pass. Deduplicated image transfer: Hackathon 9.04 MB to
  0.20 MB at 390px, 0.59 MB at 784px DPR1, and 1.11 MB at DPR2; UKIEPC 6.74 MB
  to 0.12/0.41/1.13 MB; THUPC 6.11 MB to 0.10/0.39/0.70 MB. The SITE-002
  acceptance check passes.

- **2026-11-23 - Image tooling:** Consolidated the image checks into
  `scripts/images.py` with `check-attributes`, `check-privacy`, `check-staged`,
  `check`, `prepare`, and `apply`. `prepare` writes balanced, faces, and
  screenshot variants plus `preview.html` and `manifest.md`; `apply` copies
  same-extension outputs and prints reference hints for format changes. The
  pre-commit hook and CI use the new entry point.

## Repository hygiene

- `themes/terminal` is a git submodule. Do not edit files inside it. Local
  overrides belong in the project root `layouts/` directory, which Hugo checks
  first. Current overrides: `head.html`, `extended_head.html`, `math.html`,
  `cover.html`, and `img-set.html` under `layouts/partials/`; `figure.html`
  under `layouts/shortcodes/`; and `render-image.html` under
  `layouts/_default/_markup/`.
- `git log --all -- AGENTS.md docs` may show commits named
  `Agent host session <id> - baseline checkpoint`. These are Cline tool
  artifacts, referenced only by `refs/agents/<session>/checkpoints/turn/N`.
  They are not under `refs/heads` or `refs/remotes`, so a normal `git push`
  does not publish them, and they are not part of the project history.
  `git gc --prune=now` alone will not remove them because those refs still
  point at them. Reclaim them only with the user's explicit approval, for
  example by listing the refs with `git for-each-ref refs/agents` and deleting
  them with `git update-ref -d`.
- These paths are gitignored local artifacts and must not be committed:
  `public/`, `resources/`, `.hugo_build.lock`, and `.obsidian/` directories
  under `content/`.
- `image-review/` is a gitignored local staging directory for image review.
  Do not commit it. Generated review files can be checked with
  `python3 scripts/images.py check-privacy image-review`.
- Local Hugo is 0.154.5. CI pins its own version in `.github/workflows/hugo.yaml`;
  read that file rather than assuming a version.

## Unlisted pages

`content/showcase/` is intentionally unlisted. It sets `build.list = "never"`,
`build.render = "always"`, `sitemap.disable = true`, and `noindex = true`, and its
menu entry is removed from `hugo.toml`. The page is still published and reachable
at `/showcase/` by direct URL. Under `hugo server`, the homepage footer renders a
`[dev] showcase` link through `layouts/partials/extended_footer.html`; the
production build emits no such link. CI fails the build if the output, sitemap,
or RSS exposes the page link. Do not add it back to menus or collections.

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

CI runs `python3 scripts/images.py check` after the build. It covers image
attributes and GPS privacy over both `public` and `content` using Pillow in a
temporary virtual environment. The job fails on violations.
