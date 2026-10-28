"""Source-layout checks requiring neither Azure nor generated ARM artifacts."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RepositoryLayoutTests(unittest.TestCase):
    def test_source_directories_exist(self):
        for directory in ("infra", "infra/modules", "params", "tests", "scripts", "docs"):
            with self.subTest(directory=directory):
                self.assertTrue((ROOT / directory).is_dir(), f"Missing source directory: {directory}")

    def test_scaffold_source_files_exist(self):
        for filename in (
            "README.md",
            "LICENSE",
            ".gitignore",
            "infra/main.bicep",
            "params/dev.bicepparam",
            "scripts/check.sh",
            "docs/REPOSITORY_LAYOUT.md",
        ):
            with self.subTest(filename=filename):
                self.assertTrue((ROOT / filename).is_file(), f"Missing source file: {filename}")

    def test_entry_point_targets_existing_resource_group(self):
        source = (ROOT / "infra/main.bicep").read_text(encoding="utf-8")
        self.assertRegex(source, r"(?m)^targetScope\s*=\s*'resourceGroup'\s*$")

    def test_planned_source_files_exist(self):
        # These assertions become satisfied by the corresponding later tasks.
        # Missing authored files must not be substituted with generated output.
        for filename in (
            "infra/modules/storage.bicep",
            "infra/modules/app-plan.bicep",
            "infra/modules/web-app.bicep",
            "docs/ARCHITECTURE.md",
            "docs/THREAT_MODEL.md",
            "docs/VALIDATION.md",
        ):
            with self.subTest(filename=filename):
                self.assertTrue((ROOT / filename).is_file(), f"Missing planned source file: {filename}")

    def test_dev_parameters_bind_to_authored_entry_point(self):
        source = (ROOT / "params/dev.bicepparam").read_text(encoding="utf-8")
        self.assertRegex(source, r"(?m)^using\s+'\.\./infra/main\.bicep'\s*$")


if __name__ == "__main__":
    unittest.main()
