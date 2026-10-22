#!/usr/bin/env python3
"""Ask before committing staged images with GPS EXIF or large file size."""

from __future__ import annotations

import io
import os
import subprocess
import sys
from pathlib import Path


MAX_IMAGE_BYTES = 5 * 1024 * 1024
IMAGE_SUFFIXES = {
    ".avif", ".bmp", ".gif", ".heic", ".heif", ".jpeg", ".jpg",
    ".png", ".svg", ".tif", ".tiff", ".webp",
}
GPS_INFO_TAG = 0x8825


def git_output(*args: str) -> bytes:
    return subprocess.check_output(("git", *args))


def staged_images() -> list[str]:
    names = git_output("diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR")
    paths = [name.decode("utf-8", "surrogateescape") for name in names.split(b"\0") if name]
    return [path for path in paths if Path(path).suffix.lower() in IMAGE_SUFFIXES]


def gps_warning(data: bytes) -> str | None:
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError:
        return "GPS EXIF could not be checked (install Pillow for this check)"

    try:
        with Image.open(io.BytesIO(data)) as image:
            gps = image.getexif().get_ifd(GPS_INFO_TAG)
    except (OSError, ValueError, UnidentifiedImageError) as exc:
        return f"GPS EXIF could not be checked ({type(exc).__name__})"

    if gps:
        return "contains GPS EXIF metadata"
    return None


def warnings_for_images(paths: list[str]) -> list[str]:
    warnings = []
    for path in paths:
        # Read the index blob: a partly staged image must be checked as committed.
        data = git_output("cat-file", "blob", f":{path}")
        reasons = []
        if len(data) > MAX_IMAGE_BYTES:
            reasons.append(f"{len(data) / (1024 * 1024):.1f} MiB (over 5 MiB)")
        if Path(path).suffix.lower() != ".svg":
            if issue := gps_warning(data):
                reasons.append(issue)
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


def main() -> int:
    try:
        paths = staged_images()
        if not paths:
            return 0
        warnings = warnings_for_images(paths)
    except subprocess.CalledProcessError as exc:
        print(f"Image review failed: git exited with status {exc.returncode}.", file=sys.stderr)
        return 1

    if not warnings:
        return 0
    print("Staged image review:", *warnings, sep="\n", file=sys.stderr)
    if ask_to_continue():
        return 0
    print("Commit cancelled; staged files were not changed.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
