"""Documentation boundaries; these assertions do not establish runtime security."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def normalized_document(relative_path):
    return " ".join((ROOT / relative_path).read_text(encoding="utf-8").split()).lower()


class DocumentationContractTests(unittest.TestCase):
    def test_architecture_declares_no_deployment_and_no_production_assurance(self):
        architecture = normalized_document("docs/ARCHITECTURE.md")
        self.assertIn("nothing has been deployed", architecture)
        self.assertIn("not production-ready", architecture)
        # Catch affirmative readiness claims even if a disclaimer is also present.
        self.assertNotRegex(
            architecture,
            r"\b(?:is|are)\s+(?:fully\s+)?production[- ]ready\b",
        )

    def test_networking_and_identity_limits_are_explicit(self):
        architecture = normalized_document("docs/ARCHITECTURE.md")
        self.assertRegex(
            architecture,
            r"endpoints remain inaccessible until private networking is implemented",
        )
        self.assertIn("a managed identity alone grants no storage permissions", architecture)
        self.assertIn("there are no role assignments", architecture)
        self.assertIn("no runtime application", architecture)

    def test_scope_diagram_and_cost_caveat_are_present(self):
        architecture = normalized_document("docs/ARCHITECTURE.md")
        self.assertIn("targetscope = 'resourcegroup'", architecture)
        self.assertIn("web app --x--> storage data plane", architecture)
        self.assertIn("cost-bearing resources if deployed", architecture)

if __name__ == "__main__":
    unittest.main()
