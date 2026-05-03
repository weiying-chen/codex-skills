---
name: img-gen
description: Generate recurring transparent PNG variants from a reference image using JSON config, script-based alpha enforcement, and strict verification.
---

# Img-gen

## Behavior when invoked
When user invokes `$img-gen`, do the full run automatically:
1. Run dependency preflight (`scripts/check_deps.py`). If it fails, tell user to install from `requirements.txt`.
2. Read `config.json`.
3. Build jobs file.
4. Generate images in-session for all jobs using solid key-color background prompt instructions.
5. Run script-based transparency processing on outputs.
6. Strictly verify alpha and fail if any file is not truly transparent.
7. Regenerate only failed/missing jobs and repeat steps 5-6 until pass.

## Modes
- `auto`: edge-connected background removal (`enforce_transparency.py`).
- `chroma`: key-color removal + edge de-spill (`chroma_to_alpha.py`).

Default mode for `$img-gen` is `chroma` with anti-fringe settings:
- `--threshold 55`
- `--edge-softness 16`
- `--despill-strength 1.0`


## Dependencies
Install before first run:

```bash
pip install -r requirements.txt
```

If you use `uv`:

```bash
uv pip install -r requirements.txt
```

## Files
- `config.json`: run settings.
- `scripts/make_jobs.py`: creates deterministic `jobs.json`.
- `scripts/check_deps.py`: dependency preflight with install instructions.
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
