"""Static configuration contracts; no compiler or Azure calls."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BicepConfigTests(unittest.TestCase):
    def test_core_analyzer_is_explicitly_enabled(self):
        config = json.loads((ROOT / "bicepconfig.json").read_text(encoding="utf-8"))
        self.assertIsInstance(config, dict)
        self.assertIs(config["analyzers"]["core"]["enabled"], True)

    def test_required_rules_fail_on_violations(self):
        config = json.loads((ROOT / "bicepconfig.json").read_text(encoding="utf-8"))
        rules = config["analyzers"]["core"]["rules"]
        for rule in (
            "no-hardcoded-env-urls",
            "no-unused-params",
            "secure-secrets-in-params",
            "outputs-should-not-contain-secrets",
        ):
            with self.subTest(rule=rule):
                self.assertEqual(rules[rule]["level"], "error")


if __name__ == "__main__":
    unittest.main()
