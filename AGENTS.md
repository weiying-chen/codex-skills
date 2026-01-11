# Repository Guidelines

## Project Structure & Module Organization
- `skills/`: Source for individual Codex skills. Each skill has a `SKILL.md` and optional `scripts/` helpers (e.g., `skills/watch-file-wl-copy/`).
- `dist/`: Built skill artifacts (e.g., `.skill` files) produced from the sources in `skills/`.

## Build, Test, and Development Commands
- No build or test runner is defined in this repository. The primary workflow is editing skill content directly under `skills/`.
- Example utility command (from a skill directory): `python3 scripts/watch_cmd.py "(1)"` generates a watch command for a matching file.

## Coding Style & Naming Conventions
- Python: follow PEP 8, 4-space indentation, and clear function names (see `skills/watch-file-wl-copy/scripts/watch_cmd.py`).
- Skill layout: `SKILL.md` at the skill root, with helpers under `scripts/` and any generated outputs under `dist/`.
- Filenames: use lowercase with hyphens for skill folders (e.g., `watch-file-wl-copy`).

## Testing Guidelines
- No test framework or coverage requirements are present. If you add tests, document how to run them here and colocate them under the relevant skill directory.

## Commit & Pull Request Guidelines
- This repository does not include Git history in the workspace, so no commit message conventions are available.
- If you open a PR, include a brief summary of the skill changes and any manual verification steps (e.g., the command you ran).

## Security & Configuration Tips
- `skills/watch-file-wl-copy/scripts/watch_cmd.py` uses `wl-copy` for clipboard access and reads `SUB_WATCH_TS` to locate `watch.ts`.
- If clipboard access is unavailable, run without `--copy` and paste the printed command manually.
