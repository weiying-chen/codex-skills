#!/usr/bin/env python3

import argparse
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


DEFAULT_WATCH_TS = os.environ.get("SUB_WATCH_TS") or "/home/wei-ying-chen/node/sub/src/cli/watch.ts"
SKIP_DIR_NAMES = {".git", "node_modules", "dist", "build", "__pycache__"}


@dataclass(frozen=True)
class Candidate:
    path: Path
    score: tuple[int, int, str]


def _iter_files(root: Path, recursive: bool) -> list[Path]:
    if recursive:
        results: list[Path] = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [
                d
                for d in dirnames
                if not d.startswith(".") and d not in SKIP_DIR_NAMES and not d.endswith(".tmp")
            ]
            for filename in filenames:
                path = Path(dirpath) / filename
                if path.is_file():
                    results.append(path)
        return results

    return [p for p in root.iterdir() if p.is_file()]


def _normalize_ext(ext: str | None) -> str | None:
    if not ext:
        return None
    return ext if ext.startswith(".") else f".{ext}"


def _score(path: Path, query_cf: str) -> tuple[int, int, str]:
    name_cf = path.name.casefold()
    stem_cf = path.stem.casefold()
    if query_cf == name_cf or query_cf == stem_cf:
        match_rank = 0
    elif name_cf.startswith(query_cf) or stem_cf.startswith(query_cf):
        match_rank = 1
    else:
        match_rank = 2
    return (match_rank, len(path.name), path.name)


def _choose_candidate(
    candidates: list[Path], query: str, index: int | None
) -> tuple[Path | None, list[Candidate]]:
    query_cf = query.casefold()
    scored = [Candidate(path=p, score=_score(p, query_cf)) for p in candidates]
    scored.sort(key=lambda c: c.score)
    if not scored:
        return None, []

    best_score = scored[0].score
    best = [c for c in scored if c.score == best_score]

    if index is not None:
        if index < 1 or index > len(scored):
            raise ValueError(f"--index must be between 1 and {len(scored)} (got {index})")
        return scored[index - 1].path, scored

    if len(best) == 1:
        return best[0].path, scored

    return None, scored


def _default_baseline_for(file_path: Path) -> Path:
    return file_path.with_name(f"{file_path.stem}.baseline{file_path.suffix}")


def _build_watch_command(
    *,
    watch_ts: str,
    file_path: Path,
    type_: str,
    no_warn: bool,
    baseline_path: Path | None,
    passthrough: list[str],
) -> str:
    argv: list[str] = ["npx", "tsx", watch_ts, str(file_path)]
    argv += ["--type", type_]
    if no_warn:
        argv.append("--no-warn")
    if baseline_path is not None:
        argv += ["--baseline", str(baseline_path)]
    argv += passthrough
    return " ".join(shlex.quote(a) for a in argv)


def _wl_copy(command: str, copy_cmd: str) -> None:
    argv = shlex.split(copy_cmd)
    try:
        subprocess.run(argv, input=(command + "\n").encode("utf-8"), check=True)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Copy command not found: {argv[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Copy command failed (exit {exc.returncode}): {copy_cmd}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build a watch command for a file in the current directory (supports partial matches) "
            "and optionally copy it to the clipboard."
        )
    )
    parser.add_argument(
        "query",
        nargs="?",
        default="",
        help="Substring to match against filenames (case-insensitive). If omitted, pick latest by mtime.",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Search root (default: current directory).",
    )
    parser.add_argument(
        "--ext",
        default="txt",
        help="File extension filter (default: txt). Use '*' to disable filtering.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search recursively under --root (default: only current directory).",
    )
    parser.add_argument(
        "--index",
        type=int,
        default=None,
        help="Pick by 1-based index when there are multiple matches (based on printed candidate list).",
    )
    parser.add_argument(
        "--watch-ts",
        default=DEFAULT_WATCH_TS,
        help=f"Path to watch.ts (default: {DEFAULT_WATCH_TS!r} or $SUB_WATCH_TS).",
    )
    parser.add_argument(
        "--type",
        dest="type_",
        default="subs",
        help="Value for --type (default: subs).",
    )
    parser.add_argument(
        "--no-warn",
        action="store_true",
        default=True,
        help="Include --no-warn (default: true).",
    )
    parser.add_argument(
        "--warn",
        action="store_false",
        dest="no_warn",
        help="Do not include --no-warn.",
    )
    parser.add_argument(
        "--baseline",
        default=None,
        help="Override baseline path (default: <file>.baseline<ext>).",
    )
    parser.add_argument(
        "--no-baseline",
        action="store_true",
        help="Omit --baseline entirely.",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy the generated command to the clipboard.",
    )
    parser.add_argument(
        "--copy-cmd",
        default="wl-copy",
        help="Clipboard command (default: wl-copy).",
    )
    args, passthrough = parser.parse_known_args()

    root = Path(args.root)
    if not root.exists():
        print(f"error: --root does not exist: {root}", file=sys.stderr)
        return 1

    ext = _normalize_ext(args.ext) if args.ext != "*" else None
    all_files = _iter_files(root, recursive=args.recursive)
    if ext is not None:
        all_files = [p for p in all_files if p.suffix == ext]

    query = args.query.strip()
    if query:
        matches = [p for p in all_files if query.casefold() in p.name.casefold()]
    else:
        matches = all_files

    if not matches:
        hint = " (try --recursive)" if not args.recursive else ""
        print(f"error: no matches for query={query!r} under {root}{hint}", file=sys.stderr)
        return 1

    if not query and args.index is None:
        matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        selected = matches[0]
        scored = [Candidate(path=p, score=(0, 0, p.name)) for p in matches[:10]]
    else:
        try:
            selected, scored = _choose_candidate(matches, query, args.index)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    if selected is None:
        print("error: multiple equally-good matches; re-run with --index", file=sys.stderr)
        for i, cand in enumerate(scored[:20], start=1):
            print(f"{i:>2}. {cand.path}", file=sys.stderr)
        return 2

    file_path = selected.resolve()
    baseline_path: Path | None
    if args.no_baseline:
        baseline_path = None
    elif args.baseline is not None:
        baseline_path = Path(args.baseline).resolve()
    else:
        baseline_path = _default_baseline_for(file_path)

    if passthrough and passthrough[0] == "--":
        passthrough = passthrough[1:]

    command = _build_watch_command(
        watch_ts=args.watch_ts,
        file_path=file_path,
        type_=args.type_,
        no_warn=args.no_warn,
        baseline_path=baseline_path,
        passthrough=passthrough,
    )
    print(command)

    if args.copy:
        try:
            _wl_copy(command, args.copy_cmd)
        except RuntimeError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
