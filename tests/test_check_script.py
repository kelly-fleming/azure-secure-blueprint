"""Inspect Bash source only; never execute the validation pipeline."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CheckScriptTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / 'scripts/check.sh').read_text(encoding='utf-8')

    def test_fail_fast_and_repository_anchor(self):
        self.assertTrue(self.source.startswith('#!/usr/bin/env bash\nset -Eeuo pipefail\n'))
        self.assertIn('"${BASH_SOURCE[0]}"', self.source)
        self.assertIn('dirname --', self.source)
        self.assertIn('cd -- "$repo_root"', self.source)
        self.assertIn("trap 'status=$?;", self.source)
        self.assertIn('exit "$status"', self.source)

    def test_tool_preflight_has_setup_advice(self):
        for text in ('command -v bicep', 'command -v python', 'sys.version_info >= (3, 12)',
                     'Install standalone Bicep CLI', 'Install Python 3.12', 'exit 1'):
            with self.subTest(text=text):
                self.assertIn(text, self.source)

    def test_exact_order_and_stale_artifact_removal(self):
        commands = (
            'mkdir -p -- build',
            'rm -f -- build/main.json build/dev.parameters.json',
            'bicep lint infra/main.bicep',
            'bicep build infra/main.bicep --outfile build/main.json',
            'bicep build-params params/dev.bicepparam --outfile build/dev.parameters.json',
            'python -m unittest discover -s tests -v',
        )
        lines = self.source.splitlines()
        positions = [lines.index(command) for command in commands]
        self.assertEqual(positions, sorted(positions))
        for command in commands:
            self.assertEqual(lines.count(command), 1)

    def test_no_cloud_operations_or_failure_suppression(self):
        self.assertNotRegex(self.source, r'(?im)^\s*(?:az|curl|wget)\b')
        self.assertNotRegex(self.source, r'(?i)\bbicep\s+(?:publish|format)\b|\bwhat-if\b|\baz\s+(?:login|deployment)\b')
        self.assertNotRegex(self.source, r'\|\|\s*(?:true|:)\b|continue-on-error')
        self.assertNotIn('unittest.main', self.source)


if __name__ == '__main__':
    unittest.main()
