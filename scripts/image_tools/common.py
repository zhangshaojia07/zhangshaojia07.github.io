"""Shared helpers for the image command-line tools."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Iterable

GPS_INFO_TAG = 0x8825
MAX_IMAGE_BYTES = 5 * 1024 * 1024
IMAGE_SUFFIXES = {
    ".avif", ".bmp", ".gif", ".heic", ".heif", ".jpeg", ".jpg",
    ".png", ".svg", ".tif", ".tiff", ".webp",
}
PILLOW_SUFFIXES = IMAGE_SUFFIXES - {".svg"}


class ImageToolError(Exception):
    """An expected error that should be printed without a traceback."""


class PillowMissingError(ImageToolError):
    """Raised when a command needs Pillow but it is not installed."""

    def __init__(self) -> None:
        super().__init__("Pillow is required for this command: python3 -m pip install pillow")


def require_pillow() -> None:
    try:
        import PIL.Image  # noqa: F401
    except ImportError as exc:
        raise PillowMissingError() from exc


def iter_image_paths(
    targets: Iterable[Path],
    suffixes: set[str] = IMAGE_SUFFIXES,
) -> list[Path]:
    found: list[Path] = []
    for target in targets:
        if target.is_dir():
            found.extend(
                path for path in sorted(target.rglob("*"))
                if path.is_file() and path.suffix.lower() in suffixes
            )
        elif target.is_file():
            if target.suffix.lower() in suffixes:
                found.append(target)
        else:
            raise ImageToolError(f"Path not found: {target}")
    return found


def iter_html_paths(targets: Iterable[Path]) -> list[Path]:
    found: list[Path] = []
    for target in targets:
        if target.is_dir():
            found.extend(sorted(target.rglob("*.html")))
        elif target.is_file():
            found.append(target)
        else:
            raise ImageToolError(f"Path not found: {target}")
    return found


def gps_tags_from_bytes(data: bytes) -> dict:
    require_pillow()
    from PIL import Image, UnidentifiedImageError

    try:
        with Image.open(io.BytesIO(data)) as image:
            return image.getexif().get_ifd(GPS_INFO_TAG)
    except (OSError, ValueError, UnidentifiedImageError):
        raise


def gps_tags_from_path(path: Path) -> dict:
    require_pillow()
    from PIL import Image, UnidentifiedImageError

    try:
        with Image.open(path) as image:
            return image.getexif().get_ifd(GPS_INFO_TAG)
    except (OSError, ValueError, UnidentifiedImageError):
        raise


def format_bytes(value: int) -> str:
    if value >= 1024 * 1024:
        return f"{value / (1024 * 1024):.2f} MiB"
    return f"{value / 1024:.0f} KiB"


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path)


def stored_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path.resolve())


def resolve_stored_path(value: str, root: Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path
