"""Optional release documents describe scope without freezing verification status."""

from datetime import date
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


def assert_release_document(source, document):
    """Check lasting safety boundaries, not whether a particular CI run passed."""
    normalized = ' '.join(source.split()).lower()
    boundaries = {
        'source/template scope': r'\b(?:source[- ]only|template intent)\b',
        'no production assurance': r'\b(?:not production[- ]ready|no production[- ]readiness (?:claim|assurance))\b',
        'identity does not authorize storage': (
            r'\bmanaged identity alone (?:grants no|does not grant) storage permissions\b'
        ),
        'deployment cost warning': (
            r'\b(?:incur costs|cost[- ]bearing|bill) if deployed\b'
        ),
    }
    for boundary, pattern in boundaries.items():
        if not re.search(pattern, normalized):
            raise AssertionError(f'Missing release safety boundary: {boundary}')
    if re.search(r'\b(?:is|are)\s+(?:fully\s+)?production[- ]ready\b', normalized):
        raise AssertionError('Unsupported production readiness claim')
    if re.search(r'(?i)(?:\$\s*\d|\d\s*(?:usd|dollars))\s*(?:/|per)\s*(?:month|hour)', source):
        raise AssertionError('Unsupported measured cost claim')

    # Validate dates when supplied, without requiring a release date or pinning it.
    for stamp in re.findall(r'(?m)^##\s+v?\d+\.\d+\.\d+\s+-\s+(\d{4}-\d{2}-\d{2})\s*$', source):
        date.fromisoformat(stamp)
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', source):
        if '://' in target or target.startswith('#'):
            continue
        if not (document.parent / target.split('#')[0]).is_file():
            raise AssertionError(f'Missing release link: {target}')


class ReleaseDocumentationTests(unittest.TestCase):
    def test_optional_release_documents_preserve_safety_boundaries(self):
        documents = sorted({
            *ROOT.glob('CHANGELOG.md'),
            *ROOT.glob('RELEASE_NOTES*.md'),
            *(ROOT / 'docs').glob('RELEASE_NOTES*.md'),
        })
        for document in documents:
            with self.subTest(path=document.relative_to(ROOT)):
                assert_release_document(document.read_text(encoding='utf-8'), document)

    def test_successful_ci_and_updated_release_dates_are_allowed(self):
        for status in ('CI execution is pending.', 'CI passed. All tests passed.'):
            for heading in ('## Unreleased', '## v1.2.3 - 2027-02-15'):
                with self.subTest(status=status, heading=heading):
                    assert_release_document(
                        self.release_example(heading, status), ROOT / 'CHANGELOG.md'
                    )

    def test_missing_safety_boundaries_and_broken_links_are_rejected(self):
        source = self.release_example()
        for phrase in (
            'Source-only.', 'Not production-ready.',
            'Managed identity alone does not grant storage permissions.',
            'Resources incur costs if deployed.',
        ):
            with self.subTest(removed=phrase), self.assertRaises(AssertionError):
                assert_release_document(source.replace(phrase, ''), ROOT / 'CHANGELOG.md')
        for addition in (
            'It is production-ready.',
            '$5 per month',
            '[Missing](docs/nonexistent-release-document.md)',
        ):
            with self.subTest(addition=addition), self.assertRaises(AssertionError):
                assert_release_document(source + addition, ROOT / 'CHANGELOG.md')

    @staticmethod
    def release_example(heading='## Unreleased', status='CI passed.'):
        return f'''# Release notes

{heading}

{status}
Source-only. Not production-ready.
Managed identity alone does not grant storage permissions.
Resources incur costs if deployed.
See [License](LICENSE).
'''


if __name__ == '__main__':
    unittest.main()
