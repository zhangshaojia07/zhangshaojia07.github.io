"""Prepare images with presets and generate a local review page."""

from __future__ import annotations

import html
import io
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .common import (
    GPS_INFO_TAG,
    ImageToolError,
    PILLOW_SUFFIXES,
    display_path,
    format_bytes,
    iter_image_paths,
    require_pillow,
    resolve_stored_path,
    stored_path,
)
from .presets import PRESETS, Preset, output_suffix, resolve_presets

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class PreparedImage:
    source: Path
    preset: str
    output: Path
    source_width: int
    source_height: int
    width: int
    height: int
    source_bytes: int
    output_bytes: int
    icc_converted: bool
    alpha_flattened: bool


def _has_alpha(image) -> bool:
    return image.mode in {"RGBA", "LA"} or (
        image.mode == "P" and "transparency" in image.info
    )


def _open_for_preset(path: Path, preset: Preset):
    require_pillow()
    from PIL import Image, ImageCms, ImageOps

    with Image.open(path) as opened:
        if getattr(opened, "is_animated", False):
            raise ImageToolError("animated images are not supported")
        icc = opened.info.get("icc_profile")
        image = ImageOps.exif_transpose(opened)
        image.load()
        source_width, source_height = image.size
        alpha = _has_alpha(image)
        icc_converted = False

        if icc:
            try:
                source_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc))
                target_profile = ImageCms.createProfile("sRGB")
                alpha_channel = (
                    image.convert("RGBA").getchannel("A") if alpha else None
                )
                image = ImageCms.profileToProfile(
                    image.convert("RGB"),
                    source_profile,
                    target_profile,
                    outputMode="RGB",
                )
                if alpha_channel is not None:
                    image.putalpha(alpha_channel)
                icc_converted = True
            except Exception as exc:
                raise ImageToolError(f"ICC conversion failed: {exc}") from exc

        alpha_flattened = False
        if preset.format == "JPEG":
            if _has_alpha(image):
                rgba = image.convert("RGBA")
                background = Image.new("RGB", rgba.size, (255, 255, 255))
                background.paste(rgba, mask=rgba.getchannel("A"))
                image = background
                alpha_flattened = True
            else:
                image = image.convert("RGB")
        elif image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGBA" if _has_alpha(image) else "RGB")

        if image.width > preset.width:
            target_height = round(image.height * preset.width / image.width)
            image = image.resize(
                (preset.width, target_height), Image.Resampling.LANCZOS
            )

        return image, source_width, source_height, icc_converted, alpha_flattened


def _save(image, preset: Preset, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if preset.format == "JPEG":
        image.save(
            output,
            "JPEG",
            quality=preset.quality,
            subsampling=preset.subsampling,
            optimize=True,
            progressive=True,
            exif=b"",
        )
    else:
        image.save(
            output,
            "WEBP",
            quality=preset.quality,
            method=6,
            exif=b"",
        )


def prepare_images(
    targets: list[Path],
    preset_spec: str,
    out_dir: Path,
    force: bool = False,
    dry_run: bool = False,
) -> tuple[list[PreparedImage], list[str]]:
    require_pillow()
    presets = resolve_presets(preset_spec)
    sources = iter_image_paths(targets, PILLOW_SUFFIXES)
    if not sources:
        raise ImageToolError("No images found in the given paths")

    out_dir = out_dir.resolve()
    results: list[PreparedImage] = []
    errors: list[str] = []
    seen_outputs: set[Path] = set()

    for source in sources:
        source = source.resolve()
        try:
            relative = source.relative_to(REPO_ROOT)
        except ValueError:
            relative = Path(source.name)
        source_bytes = source.stat().st_size

        for preset in presets:
            suffix = output_suffix(preset, source)
            output = out_dir / preset.name / relative.with_suffix(suffix)
            if output in seen_outputs:
                errors.append(f"{source} [{preset.name}]: duplicate output {output}")
                continue
            seen_outputs.add(output)

            if output.exists() and not force:
                errors.append(f"{source} [{preset.name}]: output exists, use --force")
                continue
            if dry_run:
                print(f"would write {output}")
                continue

            try:
                image, sw, sh, icc_converted, alpha_flattened = _open_for_preset(
                    source, preset
                )
                width, height = image.size
                _save(image, preset, output)
                data = output.read_bytes()
                from PIL import Image

                with Image.open(io.BytesIO(data)) as check:
                    if check.getexif().get_ifd(GPS_INFO_TAG):
                        raise ImageToolError("output still contains GPS metadata")
                results.append(
                    PreparedImage(
                        source=source,
                        preset=preset.name,
                        output=output,
                        source_width=sw,
                        source_height=sh,
                        width=width,
                        height=height,
                        source_bytes=source_bytes,
                        output_bytes=len(data),
                        icc_converted=icc_converted,
                        alpha_flattened=alpha_flattened,
                    )
                )
            except Exception as exc:
                errors.append(f"{source} [{preset.name}]: {exc}")

    return results, errors


def write_manifest(
    results: list[PreparedImage],
    errors: list[str],
    out_dir: Path,
    presets: list[Preset],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    entries = [
        {
            "source": stored_path(result.source, REPO_ROOT),
            "preset": result.preset,
            "output": stored_path(result.output, REPO_ROOT),
            "source_width": result.source_width,
            "source_height": result.source_height,
            "width": result.width,
            "height": result.height,
            "source_bytes": result.source_bytes,
            "output_bytes": result.output_bytes,
            "icc_converted": result.icc_converted,
            "alpha_flattened": result.alpha_flattened,
        }
        for result in results
    ]
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "presets": {preset.name: asdict(preset) for preset in presets},
        "entries": entries,
        "errors": errors,
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Image review",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "| Source | Preset | Dimensions | Before | After | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for result in results:
        notes = []
        if result.icc_converted:
            notes.append("ICC to sRGB")
        if result.alpha_flattened:
            notes.append("alpha flattened")
        lines.append(
            f"| `{display_path(result.source, REPO_ROOT)}` | {result.preset} | "
            f"{result.source_width}x{result.source_height} -> "
            f"{result.width}x{result.height} | {format_bytes(result.source_bytes)} | "
            f"{format_bytes(result.output_bytes)} | {', '.join(notes) or '-'} |"
        )
    if errors:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in errors)
    (out_dir / "manifest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _preview_src(path: Path, out_dir: Path) -> str:
    try:
        return Path(os.path.relpath(path, out_dir)).as_posix()
    except ValueError:
        return path.as_uri()


def write_preview(
    results: list[PreparedImage],
    errors: list[str],
    out_dir: Path,
    presets: list[Preset],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    by_source: dict[Path, dict[str, PreparedImage]] = {}
    for result in results:
        by_source.setdefault(result.source, {})[result.preset] = result
    preset_names = [preset.name for preset in presets]

    totals = {name: 0 for name in preset_names}
    for result in results:
        totals[result.preset] += result.output_bytes

    sections = []
    for source, group in by_source.items():
        first = next(iter(group.values()))
        original_src = html.escape(_preview_src(source, out_dir), quote=True)
        cells = [
            '<div class="cell">'
            f'<a href="{original_src}"><img src="{original_src}" '
            f'width="{first.source_width}" height="{first.source_height}" '
            'loading="lazy" decoding="async"></a>'
            f'<p class="meta"><strong>original</strong><br>'
            f'{first.source_width}x{first.source_height}<br>'
            f'{format_bytes(first.source_bytes)}</p></div>'
        ]
        for name in preset_names:
            result = group.get(name)
            if result is None:
                cells.append(
                    f'<div class="cell failed"><p class="meta"><strong>{name}</strong>'
                    "<br>not generated</p></div>"
                )
                continue
            src = html.escape(_preview_src(result.output, out_dir), quote=True)
            if result.source_bytes and result.output_bytes <= result.source_bytes:
                change = (
                    f"{round(100 * (1 - result.output_bytes / result.source_bytes))}% smaller"
                )
            elif result.source_bytes:
                change = (
                    f"{round(100 * (result.output_bytes / result.source_bytes - 1))}% larger"
                )
            else:
                change = "-"
            cells.append(
                '<div class="cell">'
                f'<a href="{src}"><img src="{src}" width="{result.width}" '
                f'height="{result.height}" loading="lazy" decoding="async"></a>'
                f'<p class="meta"><strong>{name}</strong><br>'
                f'{result.width}x{result.height}<br>'
                f'{format_bytes(result.output_bytes)} · {change}</p></div>'
            )
        sections.append(
            f'<section><h2>{html.escape(display_path(source, REPO_ROOT))}</h2>'
            f'<div class="grid">{"".join(cells)}</div></section>'
        )

    total_rows = "".join(
        f"<tr><td>{name}</td><td>{format_bytes(totals[name])}</td></tr>"
        for name in preset_names
    )
    errors_block = ""
    if errors:
        errors_block = (
            "<h2>Errors</h2><ul>"
            + "".join(f"<li>{html.escape(error)}</li>" for error in errors)
            + "</ul>"
        )

    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Image review</title>
<style>
  body {{ margin: 24px; background: #1d1f21; color: #c5c8c6;
         font: 14px/1.55 ui-monospace, SFMono-Regular, Menlo, monospace; }}
  h1, h2 {{ color: #f0c674; }}
  h1 {{ margin-bottom: 4px; }}
  .hint {{ color: #969896; margin-top: 0; }}
  section {{ margin: 28px 0 36px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
           gap: 14px; }}
  .cell {{ background: #282a2e; border: 1px solid #373b41; border-radius: 6px;
           padding: 10px; }}
  .cell img {{ display: block; max-width: 100%; height: auto; border: 1px solid #373b41; }}
  .meta {{ margin: 8px 0 0; color: #b4b7b4; }}
  .failed {{ color: #cc6666; }}
  table {{ border-collapse: collapse; margin-top: 8px; }}
  th, td {{ border: 1px solid #373b41; padding: 4px 10px; text-align: left; }}
  a {{ color: #81a2be; }}
</style>
</head>
<body>
<h1>Image review</h1>
<p class="hint">Original is shown for comparison only. After choosing a preset, run
<code>python3 scripts/images.py apply &lt;preset&gt;</code>. See
<a href="manifest.md">manifest.md</a> for details.</p>
<table><tr><th>Preset</th><th>Total output</th></tr>{total_rows}</table>
{"".join(sections)}
{errors_block}
</body>
</html>
"""
    (out_dir / "preview.html").write_text(document, encoding="utf-8")


def open_preview(path: Path) -> None:
    if os.name == "nt":
        command = ["cmd", "/c", "start", "", str(path)]
    elif sys.platform == "darwin":
        command = ["open", str(path)]
    else:
        command = ["xdg-open", str(path)]
    try:
        subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        print(f"Open {path} manually.")


def _print_reference_hints(source: Path, output: Path) -> None:
    index = source.parent / "index.md"
    if not index.exists():
        return
    try:
        lines = index.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    hits = [(number, line.strip()) for number, line in enumerate(lines, 1) if source.name in line]
    if not hits:
        return
    print(f"  references in {display_path(index, REPO_ROOT)}:")
    for number, line in hits[:10]:
        print(f"    {number}: {line}")
    print(f"    replace {source.name!r} with {output.name!r}")


def apply_preset(
    out_dir: Path,
    preset_name: str,
    source_filter: str | None = None,
    dry_run: bool = False,
    assume_yes: bool = False,
) -> int:
    if preset_name not in PRESETS:
        raise ImageToolError(f"Unknown preset: {preset_name}")
    out_dir = out_dir.resolve()
    manifest_path = out_dir / "manifest.json"
    if not manifest_path.exists():
        raise ImageToolError(
            f"Manifest not found: {manifest_path}. Run prepare first."
        )
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ImageToolError(f"Could not read manifest: {exc}") from exc

    entries = [
        entry for entry in payload.get("entries", [])
        if entry.get("preset") == preset_name
    ]
    if source_filter:
        wanted = Path(source_filter).expanduser().resolve()
        entries = [
            entry for entry in entries
            if resolve_stored_path(entry["source"], REPO_ROOT).resolve() == wanted
        ]
    if not entries:
        raise ImageToolError(f"No {preset_name!r} entries found in {manifest_path}")

    same: list[tuple[Path, Path]] = []
    manual: list[tuple[Path, Path]] = []
    missing: list[Path] = []
    for entry in entries:
        source = resolve_stored_path(entry["source"], REPO_ROOT)
        output = resolve_stored_path(entry["output"], REPO_ROOT)
        if not output.exists():
            missing.append(output)
        elif source.suffix.lower() == output.suffix.lower():
            same.append((source, output))
        else:
            manual.append((source, output))

    if missing:
        print("Missing outputs:", *(display_path(path, REPO_ROOT) for path in missing), sep="\n  ")
    if manual:
        print("These outputs change the file extension and need manual reference updates:")
        for source, output in manual:
            print(f"  {display_path(source, REPO_ROOT)} -> {display_path(output, REPO_ROOT)}")
            _print_reference_hints(source, output)
    if not same:
        if manual or missing:
            return 1
        raise ImageToolError(f"No same-extension outputs for preset {preset_name!r}")

    if dry_run:
        for source, _ in same:
            print(f"would overwrite {display_path(source, REPO_ROOT)}")
        return 1 if (manual or missing) else 0

    if not assume_yes:
        try:
            answer = input(
                f"Overwrite {len(same)} source file(s) with preset "
                f"{preset_name!r}? [y/N] "
            )
        except EOFError:
            answer = ""
        if answer.strip().lower() not in {"y", "yes"}:
            print("Cancelled.")
            return 0

    for source, output in same:
        shutil.copy2(output, source)
        print(f"applied {display_path(source, REPO_ROOT)}")
    print(
        "Rebuild with `hugo --gc --minify --cleanDestinationDir` and run "
        "`python3 scripts/images.py check`."
    )
    return 1 if (manual or missing) else 0




