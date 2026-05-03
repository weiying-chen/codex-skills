#!/usr/bin/env python3
import argparse
import json
from collections import deque
from pathlib import Path

from PIL import Image


def color_dist(c1, c2):
    return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2])


def estimate_bg_color(img):
    w, h = img.size
    px = img.load()
    samples = [
        px[0, 0][:3],
        px[w - 1, 0][:3],
        px[0, h - 1][:3],
        px[w - 1, h - 1][:3],
    ]
    return (
        sum(s[0] for s in samples) // 4,
        sum(s[1] for s in samples) // 4,
        sum(s[2] for s in samples) // 4,
    )


def strip_connected_background(img, threshold):
    img = img.convert("RGBA")
    w, h = img.size
    px = img.load()
    bg = estimate_bg_color(img)

    visited = [[False] * w for _ in range(h)]
    q = deque()

    seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    for x, y in seeds:
        q.append((x, y))
        visited[y][x] = True

    changed = 0
    while q:
        x, y = q.popleft()
        r, g, b, a = px[x, y]
        if color_dist((r, g, b), bg) <= threshold:
            if a != 0:
                px[x, y] = (r, g, b, 0)
                changed += 1

            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx]:
                    visited[ny][nx] = True
                    q.append((nx, ny))

    return img, changed


def main():
    parser = argparse.ArgumentParser(description="Force true transparency by removing connected background")
    parser.add_argument("--jobs", required=True, help="jobs.json path")
    parser.add_argument("--threshold", type=int, default=50, help="RGB distance threshold (default: 50)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite files in place")
    parser.add_argument("--out-dir", help="Output directory if not overwriting")
    args = parser.parse_args()

    with open(args.jobs, "r", encoding="utf-8") as f:
        jobs = json.load(f).get("jobs", [])

    out_dir = Path(args.out_dir) if args.out_dir else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    processed = 0
    for job in jobs:
        p = Path(job["output_file"])
        if not p.exists():
            continue

        img = Image.open(p)
        fixed, changed = strip_connected_background(img, args.threshold)

        if args.overwrite:
            target = p
        else:
            target = out_dir / p.name if out_dir else p

        fixed.save(target, "PNG")
        processed += 1
        print(f"processed={p} changed_pixels={changed} saved={target}")

    print(f"done processed={processed}")


if __name__ == "__main__":
    main()
