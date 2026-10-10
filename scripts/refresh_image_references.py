"""Promote human-reviewed generated plots to test references."""

import argparse
import io
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIRS = (
    "generated-example-images-cont",
    "generated-example-images-adv",
)
EXAMPLE_ID = re.compile(r"[A-Za-z0-9_]+")


@dataclass(frozen=True)
class ReferenceUpdate:
    generated: Path
    reference: Path
    data: bytes
    changed: bool
    size: tuple[int, int]


def plan_updates(
    root: Path, example_ids: list[str], all_generated: bool = False
) -> list[ReferenceUpdate]:
    """Validate the entire selection before allowing any file changes."""
    if all_generated:
        example_ids = sorted(
            {
                path.stem.removeprefix("gen_fig_")
                for directory in GENERATED_DIRS
                for path in (root / directory).glob("gen_fig_*.png")
                if EXAMPLE_ID.fullmatch(
                    path.stem.removeprefix("gen_fig_")
                )
            }
        )
    if not example_ids:
        raise ValueError("No generated examples selected or found.")

    updates = []
    for example_id in dict.fromkeys(example_ids):
        if not EXAMPLE_ID.fullmatch(example_id):
            raise ValueError(f"Invalid example ID: {example_id!r}")
        candidates = [
            root / directory / f"gen_fig_{example_id}.png"
            for directory in GENERATED_DIRS
        ]
        sources = [path for path in candidates if path.exists()]
        if len(sources) != 1:
            raise ValueError(
                f"Example {example_id}: expected one generated image, "
                f"found {len(sources)}."
            )
        generated = sources[0]
        reference = (
            root / "tests" / "reference-example-images"
            / f"ref_fig_{example_id}.png"
        )
        if generated.is_symlink() or reference.is_symlink():
            raise ValueError(f"Example {example_id}: symlinks not allowed.")
        if not reference.is_file():
            raise ValueError(f"Missing existing reference: {reference}")
        data = generated.read_bytes()
        with Image.open(io.BytesIO(data)) as image:
            if image.format != "PNG":
                raise ValueError(f"Not a PNG image: {generated}")
            image.load()
            size = image.size
        updates.append(
            ReferenceUpdate(
                generated, reference, data,
                data != reference.read_bytes(), size,
            )
        )
    return updates


def apply_updates(updates: list[ReferenceUpdate]) -> None:
    """Replace selected references and remove only their stale diff images."""
    for update in updates:
        if update.changed:
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(
                    dir=update.reference.parent, suffix=".png", delete=False
                ) as output:
                    temporary = Path(output.name)
                    output.write(update.data)
                temporary.chmod(update.reference.stat().st_mode & 0o777)
                os.replace(temporary, update.reference)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
        diff = update.generated.with_name(
            f"{update.generated.stem}-failed-diff.png"
        )
        diff.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "examples", nargs="*", help="Reviewed example IDs, e.g. 4 5 16b"
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Select all generated examples, not just current failures",
    )
    parser.add_argument(
        "--write", action="store_true",
        help="Confirm human review and replace references; otherwise preview",
    )
    args = parser.parse_args(argv)
    if args.all and args.examples:
        parser.error("Use either explicit example IDs or --all, not both.")
    if not args.all and not args.examples:
        parser.error("Select example IDs or use --all.")
    try:
        updates = plan_updates(REPO_ROOT, args.examples, args.all)
        for update in updates:
            action = "UPDATE" if update.changed else "UNCHANGED"
            print(
                f"{action}: {update.generated.relative_to(REPO_ROOT)} "
                f"-> {update.reference.relative_to(REPO_ROOT)} "
                f"({update.size[0]}x{update.size[1]})"
            )
        if args.write:
            apply_updates(updates)
            print(
                "References refreshed; selected failure diffs removed. "
                "Rerun pytest to verify and clear its failure cache."
            )
        else:
            print(
                "Preview only; no files changed. Inspect the generated "
                "plots, then repeat with --write to confirm approval. "
                "Writing also removes the selected failure diffs."
            )
    except (OSError, ValueError) as error:
        print(f"Reference refresh failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
