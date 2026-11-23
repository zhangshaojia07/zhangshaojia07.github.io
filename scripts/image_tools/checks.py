"""Image checks used by the CLI and the pre-commit hook."""

from __future__ import annotations

import os
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

from .common import (
    GPS_INFO_TAG,
    IMAGE_SUFFIXES,
    MAX_IMAGE_BYTES,
    PILLOW_SUFFIXES,
    ImageToolError,
    PillowMissingError,
    gps_tags_from_bytes,
    iter_html_paths,
    iter_image_paths,
    require_pillow,
)

REQUIRED = ("src", "width", "height", "loading", "decoding", "alt")
NUMERIC = ("width", "height")
LOADING_VALUES = {"lazy", "eager", "auto"}
DECODING_VALUES = {"async", "sync", "auto"}


class ImageCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.images: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "img":
            self.images.append(dict(attrs))


def attribute_issues(path: Path) -> list[str]:
    parser = ImageCollector()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    issues = []
    for index, attrs in enumerate(parser.images, start=1):
        missing = [name for name in REQUIRED if name not in attrs]
        if missing:
            issues.append(f"{path}: image {index}: missing {', '.join(missing)}")
        for name in (*NUMERIC, "src", "loading", "decoding"):
            if name in attrs and attrs[name] is None:
                issues.append(f"{path}: image {index}: {name} has no value")
        for name in NUMERIC:
            value = attrs.get(name)
            if value is None:
                continue
            try:
                if int(value) <= 0:
                    issues.append(f"{path}: image {index}: {name} must be positive")
            except ValueError:
                issues.append(f"{path}: image {index}: {name} is not an integer: {value}")
        loading = attrs.get("loading")
        if loading is not None and loading not in LOADING_VALUES:
            issues.append(f"{path}: image {index}: invalid loading={loading!r}")
        decoding = attrs.get("decoding")
        if decoding is not None and decoding not in DECODING_VALUES:
            issues.append(f"{path}: image {index}: invalid decoding={decoding!r}")
    return issues


def check_attributes(targets: list[Path]) -> int:
    issues = []
    for file in iter_html_paths(targets):
        issues.extend(attribute_issues(file))
    if issues:
        print("Image attribute check failed:", *issues, sep="\n  ", file=sys.stderr)
        return 1
    print("Image attribute check passed.")
    return 0


def privacy_findings(targets: list[Path]) -> tuple[list[str], list[str], int]:
    require_pillow()
    from PIL import Image, UnidentifiedImageError

    bad = []
    unreadable = []
    scanned = 0
    for path in iter_image_paths(targets, PILLOW_SUFFIXES):
        scanned += 1
        try:
            with Image.open(path) as image:
                gps = image.getexif().get_ifd(GPS_INFO_TAG)
        except (OSError, ValueError, UnidentifiedImageError) as exc:
            unreadable.append(f"{path} ({type(exc).__name__})")
            continue
        if gps:
            bad.append(f"{path} ({len(gps)} GPS tags)")
    return bad, unreadable, scanned


def check_privacy(targets: list[Path]) -> int:
    bad, unreadable, scanned = privacy_findings(targets)
    if unreadable:
        print("Warning: could not inspect:", *unreadable, sep="\n  ", file=sys.stderr)
    if bad:
        print("GPS EXIF found:", *bad, sep="\n  ", file=sys.stderr)
        return 1
    print(f"No GPS EXIF found in {scanned} image(s).")
    return 0


def git_output(*args: str) -> bytes:
    return subprocess.check_output(("git", *args))


def staged_images() -> list[str]:
    names = git_output("diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR")
    paths = [name.decode("utf-8", "surrogateescape") for name in names.split(b"\0") if name]
    return [
        path for path in paths
        if Path(path).suffix.lower() in IMAGE_SUFFIXES
    ]


def staged_warnings(paths: list[str]) -> list[str]:
    warnings = []
    for path in paths:
        # Read the index blob: a partly staged image must be checked as committed.
        data = git_output("cat-file", "blob", f":{path}")
        reasons = []
        if len(data) > MAX_IMAGE_BYTES:
            reasons.append(f"{len(data) / (1024 * 1024):.1f} MiB (over 5 MiB)")
        if Path(path).suffix.lower() != ".svg":
            try:
                gps = gps_tags_from_bytes(data)
            except PillowMissingError:
                reasons.append(
                    "GPS EXIF could not be checked (install Pillow for this check)"
                )
            except (OSError, ValueError) as exc:
                reasons.append(f"GPS EXIF could not be checked ({type(exc).__name__})")
            else:
                if gps:
                    reasons.append("contains GPS EXIF metadata")
        if reasons:
            warnings.append(f"  {path}: {', '.join(reasons)}")
    return warnings


def ask_to_continue() -> bool:
    try:
        terminal = os.open("/dev/tty", os.O_RDWR)
    except OSError:
        print(
            "Image review needs your confirmation. Commit from an interactive "
            "terminal after reviewing the warnings.",
            file=sys.stderr,
        )
        return False
    try:
        os.write(terminal, b"Continue this commit with these images? [y/N] ")
        answer = os.read(terminal, 32).strip().lower().decode("ascii", "ignore")
    except OSError:
        print("Could not read confirmation; commit cancelled.", file=sys.stderr)
        return False
    finally:
        os.close(terminal)
    return answer in {"y", "yes"}


def check_staged() -> int:
    try:
        paths = staged_images()
        if not paths:
            return 0
        warnings = staged_warnings(paths)
    except subprocess.CalledProcessError as exc:
        print(
            f"Image review failed: git exited with status {exc.returncode}.",
            file=sys.stderr,
        )
        return 1

    if not warnings:
        return 0
    print("Staged image review:", *warnings, sep="\n", file=sys.stderr)
    if ask_to_continue():
        return 0
    print("Commit cancelled; staged files were not changed.", file=sys.stderr)
    return 1


def run_checks(site: Path, sources: list[Path]) -> int:
    if not site.exists():
        raise ImageToolError(f"Site directory not found: {site}. Run hugo first.")
    print(f"Checking HTML image attributes in {site}...")
    attribute_status = check_attributes([site])
    print(f"Checking GPS metadata in {site} and {len(sources)} source path(s)...")
    try:
        privacy_status = check_privacy([site, *sources])
    except PillowMissingError as exc:
        print(str(exc), file=sys.stderr)
        privacy_status = 2
    if attribute_status == 1 or privacy_status == 1:
        return 1
    if privacy_status == 2:
        return 2
    return 0

