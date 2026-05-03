#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

VARIATION_PROFILES = {
    "low": [
        "Pose: slight stance adjustment. Camera: minor framing shift. Expression: subtle smile variation.",
        "Pose: mild torso angle change. Camera: slight crop offset. Expression: small expression shift.",
        "Pose: minor limb placement change. Camera: subtle perspective tweak. Expression: gentle grin variation.",
        "Pose: slight body tilt change. Camera: modest headroom difference. Expression: restrained open-mouth variation.",
    ],
    "medium": [
        "Pose: wider stance with weight shifted left. Camera: low-angle three-quarter view. Expression: open-mouth smile.",
        "Pose: narrower stance with slight torso twist right. Camera: eye-level three-quarter view. Expression: focused smile.",
        "Pose: raised front appendage with mild lean forward. Camera: slightly closer framing. Expression: confident smile.",
        "Pose: slight backward lean with upper-body angle lifted. Camera: medium framing with more headroom. Expression: energetic open-mouth expression.",
        "Pose: subtle side-step posture with hips rotated left. Camera: mild top-down angle. Expression: relaxed smile.",
    ],
    "high": [
        "Pose: strong diagonal stance with dynamic appendage separation. Camera: pronounced low-angle view. Expression: high-energy open-mouth expression.",
        "Pose: deep side-step with torso rotation. Camera: close three-quarter framing. Expression: intense smile.",
        "Pose: lifted front appendage and forward lean. Camera: dramatic perspective shift. Expression: bold confident smile.",
        "Pose: backward lean with elevated upper-body angle. Camera: wider framing and stronger headroom change. Expression: animated expression.",
        "Pose: asymmetric stance with clear silhouette change. Camera: top-down three-quarter variation. Expression: playful expressive smile.",
    ],
}


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
        "subjects",
        "images_per_subject",
        "canvas_size",
        "delay_seconds",
        "prompt_template",
        "file_pattern",
    ]
    missing = [k for k in required if k not in cfg]
    if missing:
        raise ValueError(f"Missing required config keys: {', '.join(missing)}")

    variation_level = cfg.get("variation_level", "medium")
    if variation_level not in VARIATION_PROFILES:
        raise ValueError("variation_level must be one of: low, medium, high")
    profiles = VARIATION_PROFILES[variation_level]

    canvas = cfg["canvas_size"]
    if not isinstance(canvas, dict) or "width" not in canvas or "height" not in canvas:
        raise ValueError("canvas_size must be an object with width and height")
    canvas_w = int(canvas["width"])
    canvas_h = int(canvas["height"])
    if canvas_w <= 0 or canvas_h <= 0:
        raise ValueError("canvas_size.width and canvas_size.height must be positive integers")

    jobs = []
    output_dir = Path(cfg["output_dir"])

    for subject in cfg["subjects"]:
        subject_slug = slugify(subject)
        for i in range(1, int(cfg["images_per_subject"]) + 1):
            filename = cfg["file_pattern"].format(subject_slug=subject_slug, index=i)
            output_file = str(output_dir / filename)
            base_prompt = cfg["prompt_template"].replace("{subject}", subject)
            profile = profiles[(i - 1) % len(profiles)]
            variation_clause = (
                " Keep the same art style and character identity, but do not reuse the exact same composition."
                f" Required controlled variation: {profile}"
                f" Keep variation intensity at {variation_level} level."
            )
            prompt = base_prompt + variation_clause

            jobs.append(
                {
                    "subject": subject,
                    "index": i,
                    "canvas_size": {"width": canvas_w, "height": canvas_h},
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
