"""Command-line interface for image checks and preparation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .checks import check_attributes, check_privacy, check_staged, run_checks
from .common import ImageToolError, PillowMissingError
from .prepare import (
    apply_preset,
    open_preview,
    prepare_images,
    write_manifest,
    write_preview,
)
from .presets import PRESETS, resolve_presets


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="images.py",
        description="Check image attributes and privacy, or prepare responsive images.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    attributes = commands.add_parser(
        "check-attributes", help="check generated HTML for required img attributes"
    )
    attributes.add_argument("targets", nargs="+", type=Path)

    privacy = commands.add_parser(
        "check-privacy", help="check images for GPS EXIF metadata"
    )
    privacy.add_argument("targets", nargs="+", type=Path)

    commands.add_parser(
        "check-staged", help="check staged images for GPS and large file sizes"
    )

    check = commands.add_parser(
        "check", help="run attribute and privacy checks on the built site"
    )
    check.add_argument("--site", type=Path, default=Path("public"))
    check.add_argument(
        "--sources", nargs="*", type=Path, default=[Path("content")]
    )

    prepare = commands.add_parser(
        "prepare", help="generate preset variants and a local preview page"
    )
    prepare.add_argument("targets", nargs="+", type=Path)
    prepare.add_argument("--presets", default="all")
    prepare.add_argument("--out", type=Path, default=Path("image-review"))
    prepare.add_argument("--force", action="store_true")
    prepare.add_argument("--dry-run", action="store_true")
    prepare.add_argument("--open", action="store_true")

    apply = commands.add_parser(
        "apply", help="copy same-extension preset outputs back to their sources"
    )
    apply.add_argument("preset", choices=sorted(PRESETS))
    apply.add_argument("--out", type=Path, default=Path("image-review"))
    apply.add_argument("--source", type=str)
    apply.add_argument("--dry-run", action="store_true")
    apply.add_argument("--yes", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "check-attributes":
            return check_attributes(args.targets)
        if args.command == "check-privacy":
            return check_privacy(args.targets)
        if args.command == "check-staged":
            return check_staged()
        if args.command == "check":
            return run_checks(args.site, args.sources)
        if args.command == "prepare":
            results, errors = prepare_images(
                args.targets,
                args.presets,
                args.out,
                force=args.force,
                dry_run=args.dry_run,
            )
            if errors:
                print("Preparation errors:", *errors, sep="\n  ", file=sys.stderr)
            if not args.dry_run and (results or errors):
                presets = resolve_presets(args.presets)
                out_dir = args.out.resolve()
                write_manifest(results, errors, out_dir, presets)
                write_preview(results, errors, out_dir, presets)
                preview = out_dir / "preview.html"
                print(f"Preview: {preview}")
                if args.open:
                    open_preview(preview)
            if results:
                print(f"Prepared {len(results)} image variant(s).")
            return 1 if errors else 0
        if args.command == "apply":
            return apply_preset(
                args.out,
                args.preset,
                source_filter=args.source,
                dry_run=args.dry_run,
                assume_yes=args.yes,
            )
        raise ImageToolError(f"Unsupported command: {args.command}")
    except PillowMissingError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except ImageToolError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130
