---
name: watch-file-wl-copy
description: Build a watch command for a file in the current working directory using partial filename matching, and copy the resulting command to the clipboard (via wl-copy). Use when the user says they want to "watch" a file but only provides part of the name (e.g. "(1)"), or when they ask to copy a watch command to the clipboard.
---

# Watch File Wl Copy

## Overview

Generate a `npx tsx ...watch.ts` command for a file in the current directory (even from a partial filename) and optionally copy the command to the clipboard.

## Workflow

1. Identify the target file from the user's hint.
2. Generate a watch command using `scripts/watch_cmd.py`.
3. Ask permission to copy, then copy the command via `wl-copy`.

### 1) Generate the command

Run (from the directory containing the target file):

`python3 scripts/watch_cmd.py "(1)"`

Notes:
- Defaults to matching `*.txt` in the current directory. Disable filtering with `--ext '*'`.
- If no query is provided, it picks the most recently modified matching file: `python3 scripts/watch_cmd.py`.

If there are multiple good matches, the script exits with code 2 and prints a numbered list. Re-run with `--index N`:

`python3 scripts/watch_cmd.py "(1)" --index 2`

### 2) Copy to clipboard

Ask the user for permission to copy, then run:

`python3 scripts/watch_cmd.py "(1)" --copy`

If `wl-copy` is not available, run without `--copy` and paste the printed command manually.

### scripts/
`watch_cmd.py` generates and optionally clipboard-copies the watch command; configure the watch.ts path via `--watch-ts` or `$SUB_WATCH_TS`.
