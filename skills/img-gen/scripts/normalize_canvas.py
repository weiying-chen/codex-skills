#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from PIL import Image


def parse_size(s: str):
    w, h = s.lower().split('x', 1)
    return int(w), int(h)


def fit_and_center(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    img = img.convert('RGBA')
    w, h = img.size
    scale = min(target_w / w, target_h / h)
    nw = max(1, int(round(w * scale)))
    nh = max(1, int(round(h * scale)))
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)

    canvas = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 0))
    x = (target_w - nw) // 2
    y = (target_h - nh) // 2
    canvas.paste(resized, (x, y), resized)
    return canvas


def main():
    p = argparse.ArgumentParser(description='Normalize outputs to target canvas size from jobs.json')
    p.add_argument('--jobs', required=True)
    args = p.parse_args()

    jobs = json.load(open(args.jobs, 'r', encoding='utf-8')).get('jobs', [])
    for job in jobs:
        out = Path(job['output_file'])
        if not out.exists():
            continue
        tw, th = parse_size(job['size'])
        img = Image.open(out)
        if img.size != (tw, th):
            norm = fit_and_center(img, tw, th)
            norm.save(out, 'PNG')
            print(f'normalized={out} from={img.size} to={(tw, th)}')
        else:
            print(f'normalized={out} unchanged={(tw, th)}')


if __name__ == '__main__':
    main()
