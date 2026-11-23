"""Image preparation presets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .common import ImageToolError


@dataclass(frozen=True)
class Preset:
    name: str
    width: int
    format: str
    quality: int
    subsampling: int | None
    extension: str
    description: str


PRESETS: dict[str, Preset] = {
    "balanced": Preset(
        name="balanced",
        width=1600,
        format="JPEG",
        quality=85,
        subsampling=2,
        extension=".jpg",
        description="Normal photos; smaller files",
    ),
    "faces": Preset(
        name="faces",
        width=1600,
        format="JPEG",
        quality=92,
        subsampling=0,
        extension=".jpg",
        description="Group photos and faces; 4:4:4 chroma",
    ),
    "screenshot": Preset(
        name="screenshot",
        width=1600,
        format="WEBP",
        quality=90,
        subsampling=None,
        extension=".webp",
        description="Screenshots, diagrams, and UI",
    ),
}
DEFAULT_PRESET_NAMES = ("balanced", "faces", "screenshot")


def resolve_presets(spec: str) -> list[Preset]:
    text = spec.strip().lower()
    names = DEFAULT_PRESET_NAMES if text == "all" else tuple(
        name.strip() for name in text.split(",") if name.strip()
    )
    unknown = [name for name in names if name not in PRESETS]
    if unknown:
        raise ImageToolError(
            f"Unknown preset(s): {', '.join(unknown)}. "
            f"Choose from: {', '.join(PRESETS)}"
        )
    if not names:
        raise ImageToolError("At least one preset is required")
    return [PRESETS[name] for name in names]


def output_suffix(preset: Preset, source: Path) -> str:
    if preset.format != "JPEG":
        return preset.extension
    if source.suffix.lower() in {".jpg", ".jpeg"}:
        return source.suffix.lower()
    return ".jpg"
