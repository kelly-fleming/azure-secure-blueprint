"""Security claim and disclosure boundary assertions, never runtime assurance."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def text(path):
    return ' '.join((ROOT / path).read_text(encoding='utf-8').split()).lower()


class SecurityDocumentationTests(unittest.TestCase):
    def test_both_documents_distinguish_intent_from_evidence(self):
        for path in ('SECURITY.md', 'docs/THREAT_MODEL.md'):
            with self.subTest(path=path):
                source = text(path)
                self.assertIn('nothing has been deployed', source)
                self.assertIn('not production-ready', source)
                self.assertIn('static configuration', source)
                self.assertIn('runtime security', source)
                self.assertIn('a managed identity alone grants no storage permissions', source)
                self.assertNotRegex(source, r'\b(?:is|are)\s+(?:fully\s+)?production[- ]ready\b')

    def test_threat_model_records_gaps_and_compiler_limits(self):
        source = text('docs/THREAT_MODEL.md')
        for phrase in (
            'no private endpoints', 'no role assignments', 'no key vault',
            'no monitoring', 'no app service deployment runtime',
            'no authorized app-to-storage connectivity',
            'template compilation cannot prove effective policy', 'sku availability',
            'global name uniqueness', 'costs, or real deployment',
            'infrastructure would bill if deployed',
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, source)

    def test_private_reporting_is_conditional_and_support_not_promised(self):
        source = text('SECURITY.md')
        for phrase in ('private reporting channel', 'if it is unavailable',
                       'do not publish sensitive details', 'no support sla',
                       'no alternate private address or monitored inbox'):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, source)
        for link in ('docs/THREAT_MODEL.md', 'docs/ARCHITECTURE.md', 'docs/TEST_STRATEGY.md'):
            self.assertIn(f']({link.lower()})', source)
            self.assertTrue((ROOT / link).is_file())


if __name__ == '__main__':
    unittest.main()
