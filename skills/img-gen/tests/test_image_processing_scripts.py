import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = REPO_ROOT / "skills" / "img-gen" / "scripts"


class ImageProcessingScriptTests(unittest.TestCase):
    def script(self, name: str) -> str:
        return str(SCRIPT_DIR / name)

    def write_jobs(self, tmp_path: Path, image_path: Path, canvas_size=None, final_size=None) -> Path:
        jobs_path = tmp_path / "jobs.json"
        if canvas_size is None:
            with Image.open(image_path) as img:
                canvas = {"width": img.width, "height": img.height}
        else:
            canvas = canvas_size
        job = {
            "subject": "Fixture",
            "index": 1,
            "canvas_size": canvas,
            "output_file": str(image_path),
        }
        if final_size is not None:
            job["final_size"] = final_size
        jobs_path.write_text(
            json.dumps(
                {
                    "jobs": [job]
                }
            ),
            encoding="utf-8",
        )
        return jobs_path

    def run_script(self, tmp_path: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, *args],
            cwd=tmp_path,
            check=check,
            capture_output=True,
            text=True,
        )

    def test_verify_alpha_accepts_true_transparency(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            image_path = tmp_path / "ok.png"
            img = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
            for y in range(2, 8):
                for x in range(2, 8):
                    img.putpixel((x, y), (255, 0, 0, 255))
            img.save(image_path)
            jobs_path = self.write_jobs(tmp_path, image_path)
            report_path = tmp_path / "report.json"

            result = self.run_script(
                tmp_path,
                [
                    self.script("verify_alpha.py"),
                    "--jobs",
                    str(jobs_path),
                    "--report",
                    str(report_path),
                    "--fail-on-error",
                ],
            )

        self.assertIn("ok=1", result.stdout)

    def test_verify_alpha_rejects_missing_alpha_channel(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            image_path = tmp_path / "rgb.png"
            Image.new("RGB", (10, 10), (255, 0, 0)).save(image_path)
            jobs_path = self.write_jobs(tmp_path, image_path)
            report_path = tmp_path / "report.json"

            result = self.run_script(
                tmp_path,
                [
                    self.script("verify_alpha.py"),
                    "--jobs",
                    str(jobs_path),
                    "--report",
                    str(report_path),
                    "--fail-on-error",
                ],
                check=False,
            )
            report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report["results"][0]["reason"], "no_alpha_channel")

    def test_verify_alpha_rejects_opaque_key_color(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            image_path = tmp_path / "key.png"
            img = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
            for y in range(2, 8):
                for x in range(2, 8):
                    img.putpixel((x, y), (0, 255, 0, 255))
            img.save(image_path)
            jobs_path = self.write_jobs(tmp_path, image_path)
            report_path = tmp_path / "report.json"

            result = self.run_script(
                tmp_path,
                [
                    self.script("verify_alpha.py"),
                    "--jobs",
                    str(jobs_path),
                    "--report",
                    str(report_path),
                    "--key-color",
                    "#00FF00",
                    "--fail-on-error",
                ],
                check=False,
            )
            report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report["results"][0]["reason"], "opaque_key_color_remains")

    def test_chroma_to_alpha_removes_key_color_and_preserves_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            image_path = tmp_path / "chroma.png"
            img = Image.new("RGBA", (8, 8), (0, 255, 0, 255))
            for y in range(2, 6):
                for x in range(2, 6):
                    img.putpixel((x, y), (255, 0, 0, 255))
            img.save(image_path)
            jobs_path = self.write_jobs(tmp_path, image_path)

            self.run_script(
                tmp_path,
                [
                    self.script("chroma_to_alpha.py"),
                    "--jobs",
                    str(jobs_path),
                    "--key-color",
                    "#00FF00",
                    "--threshold",
                    "0",
                    "--edge-softness",
                    "0",
                ],
            )
            fixed = Image.open(image_path).convert("RGBA")

        self.assertEqual(fixed.getpixel((0, 0))[3], 0)
        self.assertEqual(fixed.getpixel((3, 3))[3], 255)

    def test_enforce_transparency_removes_only_connected_background(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            image_path = tmp_path / "connected.png"
            img = Image.new("RGBA", (8, 8), (255, 255, 255, 255))
            for y in range(2, 6):
                for x in range(2, 6):
                    img.putpixel((x, y), (255, 0, 0, 255))
            img.save(image_path)
            jobs_path = self.write_jobs(tmp_path, image_path)

            self.run_script(
                tmp_path,
                [
                    self.script("enforce_transparency.py"),
                    "--jobs",
                    str(jobs_path),
                    "--threshold",
                    "0",
                    "--overwrite",
                ],
            )
            fixed = Image.open(image_path).convert("RGBA")

        self.assertEqual(fixed.getpixel((0, 0))[3], 0)
        self.assertEqual(fixed.getpixel((3, 3))[3], 255)

    def test_cleanup_alpha_islands_removes_small_disconnected_component(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            image_path = tmp_path / "islands.png"
            img = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
            for y in range(1, 5):
                for x in range(1, 5):
                    img.putpixel((x, y), (255, 0, 0, 255))
            img.putpixel((9, 9), (0, 0, 255, 255))
            img.save(image_path)
            jobs_path = self.write_jobs(tmp_path, image_path)

            self.run_script(
                tmp_path,
                [
                    self.script("cleanup_alpha_islands.py"),
                    "--jobs",
                    str(jobs_path),
                    "--min-pixels",
                    "2",
                ],
            )
            fixed = Image.open(image_path).convert("RGBA")

        self.assertEqual(fixed.getpixel((9, 9))[3], 0)
        self.assertEqual(fixed.getpixel((2, 2))[3], 255)

    def test_normalize_canvas_resizes_and_centers_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            image_path = tmp_path / "small.png"
            Image.new("RGBA", (2, 4), (255, 0, 0, 255)).save(image_path)
            jobs_path = self.write_jobs(tmp_path, image_path, {"width": 8, "height": 8})

            self.run_script(tmp_path, [self.script("normalize_canvas.py"), "--jobs", str(jobs_path)])
            fixed = Image.open(image_path).convert("RGBA")

        self.assertEqual(fixed.size, (8, 8))
        self.assertEqual(fixed.getpixel((0, 0))[3], 0)
        self.assertGreater(fixed.getpixel((4, 4))[3], 0)

    def test_upscale_outputs_applies_final_size_and_dpi(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            image_path = tmp_path / "upscale.png"
            img = Image.new("RGBA", (4, 6), (0, 0, 0, 0))
            for y in range(1, 5):
                for x in range(1, 3):
                    img.putpixel((x, y), (255, 0, 0, 255))
            img.save(image_path)
            jobs_path = self.write_jobs(
                tmp_path,
                image_path,
                {"width": 4, "height": 6},
                {"width": 8, "height": 12, "dpi": 300},
            )

            self.run_script(tmp_path, [self.script("upscale_outputs.py"), "--jobs", str(jobs_path)])
            fixed = Image.open(image_path).convert("RGBA")

        self.assertEqual(fixed.size, (8, 12))
        self.assertEqual(fixed.info.get("dpi"), (299.9994, 299.9994))
        self.assertEqual(fixed.getpixel((0, 0))[3], 0)
        self.assertGreater(fixed.getpixel((4, 6))[3], 0)

    def test_finalize_run_auto_smoke_processes_and_verifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            image_path = tmp_path / "final.png"
            img = Image.new("RGBA", (20, 20), (255, 255, 255, 255))
            for y in range(6, 14):
                for x in range(6, 14):
                    img.putpixel((x, y), (255, 0, 0, 255))
            img.save(image_path)
            jobs_path = self.write_jobs(tmp_path, image_path, {"width": 20, "height": 20})
            report_path = tmp_path / "alpha_report.json"

            result = self.run_script(
                tmp_path,
                [
                    self.script("finalize_run.py"),
                    "--jobs",
                    str(jobs_path),
                    "--report",
                    str(report_path),
                    "--mode",
                    "auto",
                    "--threshold",
                    "0",
                    "--min-island-pixels",
                    "1",
                    "--min-subject-ratio",
                    "0.1",
                ],
            )
            report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertIn("strict verify passed", result.stdout)
        self.assertEqual(report["summary"]["ok"], 1)

    def test_finalize_run_applies_final_size_after_transparency_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            image_path = tmp_path / "final-size.png"
            img = Image.new("RGBA", (20, 20), (255, 255, 255, 255))
            for y in range(6, 14):
                for x in range(6, 14):
                    img.putpixel((x, y), (255, 0, 0, 255))
            img.save(image_path)
            jobs_path = self.write_jobs(
                tmp_path,
                image_path,
                {"width": 20, "height": 20},
                {"width": 40, "height": 40, "dpi": 300},
            )
            report_path = tmp_path / "alpha_report.json"

            result = self.run_script(
                tmp_path,
                [
                    self.script("finalize_run.py"),
                    "--jobs",
                    str(jobs_path),
                    "--report",
                    str(report_path),
                    "--mode",
                    "auto",
                    "--threshold",
                    "0",
                    "--min-island-pixels",
                    "1",
                    "--min-subject-ratio",
                    "0.1",
                ],
            )
            fixed = Image.open(image_path).convert("RGBA")

        self.assertIn("final export passed", result.stdout)
        self.assertEqual(fixed.size, (40, 40))
        self.assertEqual(fixed.info.get("dpi"), (299.9994, 299.9994))

    def test_check_deps_passes_when_required_dependencies_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            result = self.run_script(tmp_path, [self.script("check_deps.py")])

        self.assertIn("Dependency check passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
