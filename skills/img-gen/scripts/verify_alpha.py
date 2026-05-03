#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

from PIL import Image


def _hex_to_rgb(value: str):
    v = value.strip().lstrip("#")
    if len(v) != 6:
        raise ValueError("key_color must be #RRGGBB")
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


def check_png_alpha(path: Path, key_rgb=None, key_threshold=60, max_opaque_key_ratio=0.0, min_subject_ratio=0.12):
    if not path.exists():
        return {"status": "missing", "reason": "file_not_found"}

    try:
        img = Image.open(path)
        bands = img.getbands()
        mode = img.mode

        if "A" not in bands:
            return {
                "status": "fail",
                "reason": "no_alpha_channel",
                "mode": mode,
            }

        alpha = img.getchannel("A")
        alpha_min, alpha_max = alpha.getextrema()
        hist = alpha.histogram()
        total = sum(hist)
        transparent = hist[0] if hist else 0
        subject_ratio = (total - transparent) / total if total else 0.0

        if alpha_min != 0:
            return {
                "status": "fail",
                "reason": "not_truly_transparent",
                "mode": mode,
                "alpha_min": int(alpha_min),
                "alpha_max": int(alpha_max),
            }
        if subject_ratio < min_subject_ratio:
            return {
                "status": "fail",
                "reason": "subject_coverage_too_low",
                "mode": mode,
                "subject_ratio": subject_ratio,
            }

        result = {
            "status": "ok",
            "mode": mode,
            "alpha_min": int(alpha_min),
            "alpha_max": int(alpha_max),
            "subject_ratio": subject_ratio,
        }
        if key_rgb is not None:
            px = img.convert("RGBA").load()
            w, h = img.size
            total = w * h
            opaque_key = 0
            for y in range(h):
                for x in range(w):
                    r, g, b, a = px[x, y]
                    if abs(r - key_rgb[0]) + abs(g - key_rgb[1]) + abs(b - key_rgb[2]) <= key_threshold and a > 0:
                        opaque_key += 1
            ratio = opaque_key / total if total else 0.0
            result["opaque_key_pixels"] = opaque_key
            result["opaque_key_ratio"] = ratio
            if ratio > max_opaque_key_ratio:
                return {
                    "status": "fail",
                    "reason": "opaque_key_color_remains",
                    "mode": mode,
                    "alpha_min": int(alpha_min),
                    "alpha_max": int(alpha_max),
                    "opaque_key_pixels": opaque_key,
                    "opaque_key_ratio": ratio,
                }
        return result
    except Exception as e:
        return {"status": "error", "reason": str(e)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify transparent PNG outputs from jobs.json")
    parser.add_argument("--jobs", required=True, help="Path to jobs.json from make_jobs.py")
    parser.add_argument("--report", required=True, help="Path to write alpha verification report JSON")
    parser.add_argument("--key-color", help="Optional key color (#RRGGBB) that must not remain opaque")
    parser.add_argument("--key-threshold", type=int, default=60, help="Key color distance threshold")
    parser.add_argument("--max-opaque-key-ratio", type=float, default=0.0, help="Max allowed opaque key-color ratio")
    parser.add_argument("--min-subject-ratio", type=float, default=0.12, help="Minimum non-transparent coverage ratio")
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with status 1 when any file is fail/missing/error",
    )
    args = parser.parse_args()

    jobs_path = Path(args.jobs)
    report_path = Path(args.report)

    with jobs_path.open("r", encoding="utf-8") as f:
        jobs_doc = json.load(f)

    results = []
    counts = {"ok": 0, "fail": 0, "missing": 0, "error": 0}

    key_rgb = _hex_to_rgb(args.key_color) if args.key_color else None

    for job in jobs_doc.get("jobs", []):
        out = Path(job["output_file"])
        check = check_png_alpha(
            out,
            key_rgb=key_rgb,
            key_threshold=args.key_threshold,
            max_opaque_key_ratio=args.max_opaque_key_ratio,
            min_subject_ratio=args.min_subject_ratio,
        )
        status = check["status"]
        counts[status] = counts.get(status, 0) + 1

        results.append(
            {
                "output_file": str(out),
                "subject": job.get("subject"),
                "index": job.get("index"),
                **check,
            }
        )

    report = {
        "summary": {
            "total": len(results),
            "ok": counts.get("ok", 0),
            "fail": counts.get("fail", 0),
            "missing": counts.get("missing", 0),
            "error": counts.get("error", 0),
        },
        "results": results,
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")

    s = report["summary"]
    print(
        f"Verified {s['total']} files: ok={s['ok']} fail={s['fail']} missing={s['missing']} error={s['error']}"
    )
    if args.fail_on_error and (s["fail"] > 0 or s["missing"] > 0 or s["error"] > 0):
        sys.exit(1)


if __name__ == "__main__":
    main()
