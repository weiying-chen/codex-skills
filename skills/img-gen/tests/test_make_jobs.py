import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MAKE_JOBS = REPO_ROOT / "skills" / "img-gen" / "scripts" / "make_jobs.py"


class MakeJobsTests(unittest.TestCase):
    def run_make_jobs(self, tmp_path: Path, config: dict) -> tuple[dict, str]:
        config_path = tmp_path / "config.json"
        jobs_path = tmp_path / "output" / "jobs.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                str(MAKE_JOBS),
                "--config",
                str(config_path),
                "--out",
                str(jobs_path),
            ],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
        )

        jobs_doc = json.loads(jobs_path.read_text(encoding="utf-8"))
        return jobs_doc, result.stdout

    def run_make_jobs_failure(self, tmp_path: Path, config: dict) -> subprocess.CompletedProcess:
        config_path = tmp_path / "config.json"
        jobs_path = tmp_path / "output" / "jobs.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")

        return subprocess.run(
            [
                sys.executable,
                str(MAKE_JOBS),
                "--config",
                str(config_path),
                "--out",
                str(jobs_path),
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

    def base_config(self, skip_existing: bool) -> dict:
        return {
            "reference_image": "./input/reference.png",
            "output_dir": "./output/run-001",
            "skip_existing": skip_existing,
            "subjects": ["Corgi", "Shiba Inu"],
            "images_per_subject": 3,
            "variation_level": "medium",
            "canvas_size": {"width": 1024, "height": 1024},
            "delay_seconds": 2,
            "prompt_template": "Replace the main character with a {subject}.",
            "file_pattern": "{subject_slug}_{index:02d}.png",
        }

    def test_skip_existing_creates_only_missing_jobs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_dir = tmp_path / "output" / "run-001"
            output_dir.mkdir(parents=True)
            for filename in [
                "corgi_01.png",
                "corgi_03.png",
                "shiba-inu_01.png",
                "shiba-inu_02.png",
                "shiba-inu_03.png",
            ]:
                (output_dir / filename).touch()

            jobs_doc, stdout = self.run_make_jobs(tmp_path, self.base_config(True))

        output_files = [job["output_file"] for job in jobs_doc["jobs"]]
        self.assertEqual(output_files, ["output/run-001/corgi_02.png"])
        self.assertIn("Wrote 1 jobs", stdout)
        self.assertIn("skipped 5 existing outputs", stdout)

    def test_skip_existing_false_keeps_all_jobs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_dir = tmp_path / "output" / "run-001"
            output_dir.mkdir(parents=True)
            (output_dir / "corgi_01.png").touch()

            jobs_doc, stdout = self.run_make_jobs(tmp_path, self.base_config(False))

        output_files = [job["output_file"] for job in jobs_doc["jobs"]]
        self.assertEqual(
            output_files,
            [
                "output/run-001/corgi_01.png",
                "output/run-001/corgi_02.png",
                "output/run-001/corgi_03.png",
                "output/run-001/shiba-inu_01.png",
                "output/run-001/shiba-inu_02.png",
                "output/run-001/shiba-inu_03.png",
            ],
        )
        self.assertIn("Wrote 6 jobs", stdout)
        self.assertNotIn("skipped", stdout)

    def test_subject_slugs_are_kebab_case_with_index_suffix(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config = self.base_config(False)
            config["subjects"] = ["Golden Retriever"]
            config["images_per_subject"] = 1

            jobs_doc, _ = self.run_make_jobs(tmp_path, config)

        self.assertEqual(
            jobs_doc["jobs"][0]["output_file"],
            "output/run-001/golden-retriever_01.png",
        )
        self.assertEqual(jobs_doc["jobs"][0]["subject"], "Golden Retriever")
        self.assertIn("Golden Retriever", jobs_doc["jobs"][0]["prompt"])

    def test_custom_file_pattern_is_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config = self.base_config(False)
            config["subjects"] = ["Shiba Inu"]
            config["images_per_subject"] = 1
            config["file_pattern"] = "{index:02d}-{subject_slug}.png"

            jobs_doc, _ = self.run_make_jobs(tmp_path, config)

        self.assertEqual(jobs_doc["jobs"][0]["output_file"], "output/run-001/01-shiba-inu.png")

    def test_job_fields_include_configured_canvas_delay_reference_and_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config = self.base_config(False)
            config["subjects"] = ["Corgi"]
            config["images_per_subject"] = 1
            config["canvas_size"] = {"width": 4500, "height": 5400}
            config["delay_seconds"] = 7
            config["reference_image"] = "./input/custom.png"

            jobs_doc, _ = self.run_make_jobs(tmp_path, config)

        job = jobs_doc["jobs"][0]
        self.assertEqual(job["canvas_size"], {"width": 4500, "height": 5400})
        self.assertEqual(job["delay_seconds"], 7)
        self.assertEqual(job["reference_image"], "./input/custom.png")
        self.assertEqual(job["index"], 1)

    def test_variation_level_defaults_to_medium(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config = self.base_config(False)
            del config["variation_level"]
            config["subjects"] = ["Corgi"]
            config["images_per_subject"] = 1

            jobs_doc, _ = self.run_make_jobs(tmp_path, config)

        prompt = jobs_doc["jobs"][0]["prompt"]
        self.assertIn("low-angle three-quarter view", prompt)
        self.assertIn("Keep variation intensity at medium level", prompt)

    def test_variation_profiles_cycle_when_count_exceeds_profile_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config = self.base_config(False)
            config["subjects"] = ["Corgi"]
            config["images_per_subject"] = 6

            jobs_doc, _ = self.run_make_jobs(tmp_path, config)

        prompts = [job["prompt"] for job in jobs_doc["jobs"]]
        self.assertIn("wider stance with weight shifted left", prompts[0])
        self.assertIn("wider stance with weight shifted left", prompts[5])

    def test_invalid_variation_level_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config = self.base_config(False)
            config["variation_level"] = "extreme"

            result = self.run_make_jobs_failure(tmp_path, config)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("variation_level must be one of", result.stderr)

    def test_missing_required_config_key_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config = self.base_config(False)
            del config["prompt_template"]

            result = self.run_make_jobs_failure(tmp_path, config)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing required config keys: prompt_template", result.stderr)

    def test_canvas_size_must_have_width_and_height(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config = self.base_config(False)
            config["canvas_size"] = {"width": 1024}

            result = self.run_make_jobs_failure(tmp_path, config)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("canvas_size must be an object with width and height", result.stderr)

    def test_canvas_size_dimensions_must_be_positive(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config = self.base_config(False)
            config["canvas_size"] = {"width": 0, "height": 1024}

            result = self.run_make_jobs_failure(tmp_path, config)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "canvas_size.width and canvas_size.height must be positive integers",
            result.stderr,
        )


if __name__ == "__main__":
    unittest.main()
