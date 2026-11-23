# Image templates

Copy these snippets into content files. The site uses a responsive image
pipeline for Markdown images and the `figure` shortcode; raw HTML `<img>`
tags bypass that pipeline and must list their attributes explicitly.

## Rules

- Prefer a Markdown image or the `figure` shortcode. Both get `srcset`,
  `width`, `height`, `loading`, `decoding`, and `alt` automatically.
- Use raw `<img>` only when you need an `id`, inline HTML, or unusual markup.
  Raw tags do not get `srcset`.
- `width` and `height` are the image's intrinsic pixel dimensions, not CSS
  dimensions. Get them with `magick identify -format '%wx%h\n' image.jpg`.
- Always include `decoding="async"`. `<img>` has no `async` attribute.
- Use `loading="lazy"` below the fold. For the first visible or LCP image use
  `loading="eager" fetchpriority="high"`.
- Use `alt=""` only for decorative images. Otherwise describe the image.
- Do not reference generated `_hu_*` files in raw HTML. Use the source filename;
  those hashed files are build artifacts with unstable names.
- When a post cover is WebP, the head partial generates a 1200x630 JPEG
  automatically for `og:image`, because some social crawlers do not accept
  WebP previews.
- The global stylesheet sets `img { height: auto; }`, so the explicit
  `width` and `height` attributes preserve the aspect ratio while reserving
  layout space.

## Preparing images before committing

Put new images in the post bundle, then run:

```bash
python3 scripts/images.py prepare content/posts/20261101-new-post/ --open
```

This writes three preset variants to `image-review/`, generates `preview.html`
and `manifest.md`, and opens the preview. Compare the original with the presets,
then apply a same-extension preset:

```bash
python3 scripts/images.py apply faces
```

`apply` only overwrites files whose extension does not change. If a preset
changes the extension, for example PNG to WebP, it prints the new file and the
references that need updating. It exits with status 1 when some entries still
need manual reference updates.

| Preset | Width | Format | Quality | Best for |
| --- | --- | --- | --- | --- |
| `balanced` | 1600 | JPEG | q85, 4:2:0 | normal photos |
| `faces` | 1600 | JPEG | q92, 4:4:4 | group photos, faces, text |
| `screenshot` | 1600 | WebP | q90 | screenshots, diagrams, UI |

Useful options:

- `--presets all|balanced,faces,screenshot`
- `--out image-review`
- `--force`
- `--dry-run`
- `--open`

All presets auto-orient, convert Display P3 or DCI-P3 to sRGB, cap width at
1600, and strip EXIF, GPS, and ICC. Images are never upscaled. JPEG presets
flatten transparency onto white; `screenshot` preserves alpha in WebP.

### Manual fallback

Resize by width, not by long edge. A portrait image must still be 1600px wide,
otherwise it will be soft on 2x displays.

Photos:

```bash
magick input.jpg \
  -auto-orient \
  -resize '1600x>' \
  -profile /usr/share/color/icc/colord/sRGB.icc \
  -strip \
  -interlace Plane \
  -quality 85 \
  output.jpg
```

Use `-quality 92 -sampling-factor 4:4:4` for group photos or images with faces
and text where q85 looks soft.

Screenshots:

```bash
magick input.png -resize '1600x>' -strip -quality 90 output.webp
```

`-auto-orient` applies the EXIF rotation, `-profile` converts Display P3 or
DCI-P3 to sRGB, and `-strip` removes GPS and the remaining EXIF. Hugo's
processed variants do not carry the source ICC profile, so converting sources
to sRGB matters.

If you change a file extension, update the `cover` front matter and every
`figure` or Markdown reference in the post.

Optionally write outputs to a staging directory such as `image-review/` and
inspect them before replacing the originals. That directory is ignored locally
through `.gitignore`.

## Local checks

Before committing or pushing:

```bash
hugo --gc --minify --cleanDestinationDir
python3 scripts/images.py check
```

The pre-commit hook uses `scripts/images.py check-staged`. It warns about GPS
metadata and images over 5 MiB; commit from an interactive terminal so it can
ask for confirmation.

## Markdown image

```markdown
![A white kitten](kitten.jpg "Optional title")
```

Best for inline images without a caption. The image is resolved as a page
resource when possible and rendered with responsive `srcset`.

## Figure with a caption

```markdown
{{< figure src="kitten.jpg" alt="A white kitten" caption="A white kitten on a sofa" >}}
```

Also supported: `class`, `link`, `target`, `rel`, `width`, `height`,
`loading`, `title`, `attr`, and `attrlink`. `position` and `captionPosition`
are accepted for compatibility with existing content.

```markdown
{{< figure src="kitten.jpg" alt="A white kitten" caption="A white kitten" link="kitten-full.jpg" loading="lazy" >}}
```

## Raw HTML img in a page bundle

```html
<img src="kitten.jpg" alt="A white kitten" width="1600" height="1067" loading="lazy" decoding="async">
```

`src` is relative to the page bundle.

## Raw HTML img with an anchor target

```html
<img id="fig-1" src="fig-1.png" alt="Figure 1" width="910" height="312" loading="lazy" decoding="async">
```

The `id` can be linked as `[Figure 1](#fig-1)`.

## Clickable full-resolution image

```html
<a href="photo.jpg">
  <img src="photo.jpg" alt="Team photo" width="1600" height="1067" loading="lazy" decoding="async">
</a>
```

## External image

```html
<img src="https://example.com/photo.jpg" alt="Example" width="1200" height="630" loading="lazy" decoding="async">
```

Add real dimensions even for remote images; otherwise reserve space with CSS.

## Above-the-fold or LCP image

```html
<img src="cover.jpg" alt="Cover" width="1600" height="900" loading="eager" fetchpriority="high" decoding="async">
```

Use this only for the image that should load first. Do not add
`fetchpriority="high"` to many images on the same page.

## Decorative image

```html
<img src="divider.png" alt="" width="800" height="40" loading="lazy" decoding="async">
```

## Choosing a format

| Need | Use |
| --- | --- |
| Inline image, no caption | Markdown `![]()` |
| Caption, link, or fixed size | `figure` shortcode |
| `id`, inline HTML, or special markup | Raw `<img>` with all attributes |
| Above-the-fold image | `figure` or raw `<img>` with `loading="eager" fetchpriority="high"` |
