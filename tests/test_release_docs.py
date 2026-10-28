"""Dated release documents retain evidence boundaries; no publication checks run."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ReleaseDocumentationTests(unittest.TestCase):
    def test_release_documents_preserve_verification_limits(self):
        for relative in ('CHANGELOG.md', 'docs/RELEASE_NOTES_v0.1.0.md'):
            with self.subTest(path=relative):
                source = (ROOT / relative).read_text(encoding='utf-8')
                normalized = ' '.join(source.split()).lower()
                for phrase in ('v0.1.0', '2026-10-28', 'verification pending',
                               'nothing has been deployed', 'no live validation',
                               'tagging and publishing are human only',
                               'not production-ready'):
                    self.assertIn(phrase, normalized)
                self.assertNotRegex(normalized, r'\b(?:ci passed|all tests passed|successfully deployed|azure accepted deployment)\b')
                self.assertNotRegex(source, r'(?i)(?:\$\s*\d|\d\s*(?:usd|dollars))\s*(?:/|per)\s*(?:month|hour)')
                for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', source):
                    self.assertTrue(((ROOT / relative).parent / target).is_file(), f'Missing release link: {target}')

    def test_release_date_matches_maintainer_approval(self):
        source = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
        self.assertRegex(source, r'(?m)^## v0\.1\.0 - 2026-10-28$')
        self.assertNotIn('Unreleased', source)

    def test_existing_mit_license_is_present(self):
        source = (ROOT / 'LICENSE').read_text(encoding='utf-8')
        self.assertTrue(source.startswith('MIT License\n'))
        self.assertIn('Copyright (c) 2026 Kelly Fleming', source)
        self.assertIn('Permission is hereby granted, free of charge', source)
        self.assertIn('THE SOFTWARE IS PROVIDED "AS IS"', source)


if __name__ == '__main__':
    unittest.main()
