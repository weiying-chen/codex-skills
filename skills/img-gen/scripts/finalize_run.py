#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd, cwd):
    print('+', ' '.join(cmd))
    r = subprocess.run(cmd, cwd=cwd)
    if r.returncode != 0:
        sys.exit(r.returncode)


def main():
    parser = argparse.ArgumentParser(description='Enforce and verify true transparency for a jobs file')
    parser.add_argument('--jobs', required=True, help='Path to jobs.json')
    parser.add_argument('--report', required=True, help='Path to alpha report JSON')
    parser.add_argument('--mode', choices=['auto', 'chroma'], default='chroma', help='Transparency processing mode')
    parser.add_argument('--key-color', default='#00FF00', help='Key color for chroma mode')
    parser.add_argument('--edge-softness', type=int, default=16, help='Edge softness for chroma mode (legacy arg)')
    parser.add_argument('--despill-strength', type=float, default=1.0, help='Edge de-spill strength for chroma mode (legacy arg)')
    parser.add_argument('--threshold', type=int, default=55, help='Background threshold for enforcement')
    parser.add_argument('--min-island-pixels', type=int, default=800, help='Remove disconnected alpha islands smaller than this')
    parser.add_argument('--min-subject-ratio', type=float, default=0.12, help='Fail if non-transparent coverage falls below this ratio')
    args = parser.parse_args()

    here = Path(__file__).resolve().parent

    if args.mode == 'chroma':
        chroma_helper = Path.home() / '.codex' / 'skills' / '.system' / 'imagegen' / 'scripts' / 'remove_chroma_key.py'
        # Single-pass chroma extraction with stable helper to avoid conflicting mattes.
        import json
        with open(args.jobs, 'r', encoding='utf-8') as f:
            jobs_doc = json.load(f)
        for job in jobs_doc.get('jobs', []):
            out = Path(job['output_file'])
            if not out.exists():
                continue
            run([
                'python3', str(chroma_helper),
                '--input', str(out),
                '--out', str(out),
                '--auto-key', 'border',
                '--soft-matte',
                '--transparent-threshold', '12',
                '--opaque-threshold', '220',
                '--edge-contract', '1',
                '--despill',
                '--force',
            ], cwd=Path.cwd())
    else:
        run([
            'python3', str(here / 'enforce_transparency.py'),
            '--jobs', args.jobs,
            '--threshold', str(args.threshold),
            '--overwrite',
        ], cwd=Path.cwd())

    run([
        'python3', str(here / 'cleanup_alpha_islands.py'),
        '--jobs', args.jobs,
        '--min-pixels', str(args.min_island_pixels),
    ], cwd=Path.cwd())

    run([
        'python3', str(here / 'verify_alpha.py'),
        '--jobs', args.jobs,
        '--report', args.report,
        '--min-subject-ratio', str(args.min_subject_ratio),
        '--fail-on-error',
    ], cwd=Path.cwd())

    print('finalize_run: transparency enforcement + strict verify passed')


if __name__ == '__main__':
    main()
