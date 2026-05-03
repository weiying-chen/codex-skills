#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from PIL import Image, ImageFilter


def upscale_one(path: Path, width: int, height: int, dpi: int) -> None:
    img = Image.open(path).convert("RGBA")
    resized = img.resize((width, height), Image.Resampling.LANCZOS)
    resized = resized.filter(ImageFilter.UnsharpMask(radius=1.2, percent=80, threshold=3))
    resized.save(path, "PNG", dpi=(dpi, dpi))

    with Image.open(path) as saved:
        if saved.size != (width, height):
            raise ValueError(f"{path} saved as {saved.size}, expected {(width, height)}")
        if "A" not in saved.getbands():
            raise ValueError(f"{path} lost alpha channel during final export")


def main() -> None:
    parser = argparse.ArgumentParser(description="Upscale outputs with final_size from jobs.json")
    parser.add_argument("--jobs", required=True, help="jobs.json path")
    args = parser.parse_args()

    with open(args.jobs, "r", encoding="utf-8") as f:
        jobs = json.load(f).get("jobs", [])

    processed = 0
    skipped = 0
    for job in jobs:
        final_size = job.get("final_size")
        if not final_size:
            skipped += 1
            continue

        out = Path(job["output_file"])
        if not out.exists():
            skipped += 1
            continue

        width = int(final_size["width"])
        height = int(final_size["height"])
        dpi = int(final_size["dpi"])
        upscale_one(out, width, height, dpi)
        processed += 1
        print(f"finalized={out} size={(width, height)} dpi={dpi}")

    print(f"final export passed processed={processed} skipped={skipped}")


if __name__ == "__main__":
    main()
