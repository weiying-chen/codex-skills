#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create deterministic image generation jobs from config.json")
    parser.add_argument("--config", required=True, help="Path to config.json")
    parser.add_argument("--out", required=True, help="Path to output jobs.json")
    args = parser.parse_args()

    config_path = Path(args.config)
    out_path = Path(args.out)

    with config_path.open("r", encoding="utf-8") as f:
        cfg = json.load(f)

    required = [
        "reference_image",
        "output_dir",
        "breeds",
        "images_per_breed",
        "size",
        "delay_seconds",
        "prompt_template",
        "file_pattern",
    ]
    missing = [k for k in required if k not in cfg]
    if missing:
        raise ValueError(f"Missing required config keys: {', '.join(missing)}")

    jobs = []
    output_dir = Path(cfg["output_dir"])

    for breed in cfg["breeds"]:
        breed_slug = slugify(breed)
        for i in range(1, int(cfg["images_per_breed"]) + 1):
            filename = cfg["file_pattern"].format(breed_slug=breed_slug, index=i)
            output_file = str(output_dir / filename)
            prompt = cfg["prompt_template"].format(breed=breed)

            jobs.append(
                {
                    "breed": breed,
                    "index": i,
                    "size": cfg["size"],
                    "delay_seconds": cfg["delay_seconds"],
                    "reference_image": cfg["reference_image"],
                    "prompt": prompt,
                    "output_file": output_file,
                }
            )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump({"jobs": jobs}, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(jobs)} jobs to {out_path}")


if __name__ == "__main__":
    main()
