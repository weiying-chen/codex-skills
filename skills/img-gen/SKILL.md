---
name: img-gen
description: Generate recurring transparent PNG variants from a reference image using JSON config, script-based alpha enforcement, and strict verification.
---

# Img-gen

## Behavior when invoked
When user invokes `$img-gen`, do the full run automatically:
1. Read `config.json`.
2. Build jobs file.
3. Generate images in-session for all jobs using solid key-color background prompt instructions.
4. Run script-based transparency processing on outputs.
5. Strictly verify alpha and fail if any file is not truly transparent.
6. Regenerate only failed/missing jobs and repeat steps 4-5 until pass.

## Modes
- `auto`: edge-connected background removal (`enforce_transparency.py`).
- `chroma`: key-color removal + edge de-spill (`chroma_to_alpha.py`).

Default mode for `$img-gen` is `chroma` with anti-fringe settings:
- `--threshold 55`
- `--edge-softness 16`
- `--despill-strength 1.0`

## Files
- `config.json`: run settings.
- `scripts/make_jobs.py`: creates deterministic `jobs.json`.
- `scripts/enforce_transparency.py`: connected background to alpha.
- `scripts/chroma_to_alpha.py`: chroma-to-alpha with de-spill.
- `scripts/verify_alpha.py`: strict alpha checks.
- `scripts/finalize_run.py`: one command for process + verify.

## Standard commands

```bash
python3 scripts/make_jobs.py --config config.json --out output/jobs.json
```

```bash
python3 scripts/finalize_run.py --jobs output/jobs.json --report output/alpha_report.json --mode chroma --key-color '#00FF00' --threshold 55 --edge-softness 16 --despill-strength 1.0
```
