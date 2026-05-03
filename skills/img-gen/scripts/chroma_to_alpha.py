#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from PIL import Image


def hex_to_rgb(value: str):
    v = value.strip().lstrip('#')
    if len(v) != 6:
        raise ValueError('key_color must be #RRGGBB')
    return tuple(int(v[i:i+2], 16) for i in (0, 2, 4))


def dist(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1]) + abs(a[2]-b[2])


def remove_chroma(path: Path, key_rgb, threshold: int, edge_softness: int, despill_strength: float):
    img = Image.open(path).convert('RGBA')
    px = img.load()
    w, h = img.size

    changed = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            d = dist((r, g, b), key_rgb)
            if d <= threshold:
                if a != 0:
                    px[x, y] = (r, g, b, 0)
                    changed += 1
            elif edge_softness > 0 and d <= threshold + edge_softness:
                # Soft edge to reduce jagged border.
                alpha = int(255 * (d - threshold) / edge_softness)
                alpha = max(0, min(255, alpha))
                if alpha < a:
                    px[x, y] = (r, g, b, alpha)
                    changed += 1

    despilled = 0
    if despill_strength > 0:
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                # De-spill only on anti-aliased edge pixels.
                if 0 < a < 255:
                    target_g = max(r, b)
                    new_g = int(round(g - (g - target_g) * despill_strength))
                    new_g = max(0, min(255, new_g))
                    if new_g != g:
                        px[x, y] = (r, new_g, b, a)
                        despilled += 1

    img.save(path, 'PNG')
    return changed, despilled


def main():
    parser = argparse.ArgumentParser(description='Convert chroma-key background to true alpha')
    parser.add_argument('--jobs', required=True, help='jobs.json path')
    parser.add_argument('--key-color', default='#00FF00', help='Chroma key color in #RRGGBB')
    parser.add_argument('--threshold', type=int, default=60, help='Color distance threshold')
    parser.add_argument('--edge-softness', type=int, default=20, help='Soft transition outside threshold')
    parser.add_argument('--despill-strength', type=float, default=0.85, help='0..1 edge de-spill strength')
    args = parser.parse_args()

    key_rgb = hex_to_rgb(args.key_color)

    with open(args.jobs, 'r', encoding='utf-8') as f:
        jobs = json.load(f).get('jobs', [])

    processed = 0
    for job in jobs:
        out = Path(job['output_file'])
        if not out.exists():
            continue
        changed, despilled = remove_chroma(
            out,
            key_rgb,
            args.threshold,
            args.edge_softness,
            args.despill_strength,
        )
        processed += 1
        print(f'processed={out} changed_pixels={changed} despilled_edge_pixels={despilled}')

    print(f'done processed={processed}')


if __name__ == '__main__':
    main()
