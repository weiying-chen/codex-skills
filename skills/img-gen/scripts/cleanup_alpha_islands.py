#!/usr/bin/env python3
import argparse
import json
from collections import deque
from pathlib import Path

from PIL import Image


def remove_small_alpha_islands(path: Path, min_pixels: int = 800):
    img = Image.open(path).convert('RGBA')
    px = img.load()
    w, h = img.size

    visited = [[False] * w for _ in range(h)]
    removed = 0

    for y in range(h):
        for x in range(w):
            if visited[y][x]:
                continue
            if px[x, y][3] == 0:
                visited[y][x] = True
                continue

            # BFS connected component on non-transparent pixels
            q = deque([(x, y)])
            visited[y][x] = True
            comp = []

            while q:
                cx, cy = q.popleft()
                comp.append((cx, cy))
                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx]:
                        visited[ny][nx] = True
                        if px[nx, ny][3] > 0:
                            q.append((nx, ny))

            if len(comp) < min_pixels:
                for cx, cy in comp:
                    r, g, b, _ = px[cx, cy]
                    px[cx, cy] = (r, g, b, 0)
                removed += len(comp)

    img.save(path, 'PNG')
    return removed


def main():
    parser = argparse.ArgumentParser(description='Remove tiny disconnected opaque/sem-opaque alpha islands')
    parser.add_argument('--jobs', required=True, help='jobs.json path')
    parser.add_argument('--min-pixels', type=int, default=800, help='Minimum component size to keep')
    args = parser.parse_args()

    with open(args.jobs, 'r', encoding='utf-8') as f:
        jobs = json.load(f).get('jobs', [])

    for job in jobs:
        out = Path(job['output_file'])
        if not out.exists():
            continue
        removed = remove_small_alpha_islands(out, min_pixels=args.min_pixels)
        print(f'processed={out} removed_alpha_pixels={removed}')


if __name__ == '__main__':
    main()
