"""Contribution instructions must remain connected to the actual offline workflow."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ContributingTests(unittest.TestCase):
    def test_documented_commands_match_script(self):
        guide = (ROOT / 'CONTRIBUTING.md').read_text(encoding='utf-8')
        script = (ROOT / 'scripts/check.sh').read_text(encoding='utf-8')
        self.assertIn('bash scripts/check.sh', guide)
        commands = [line for line in script.splitlines()
                    if line.startswith(('bicep ', 'python -m unittest '))]
        self.assertEqual(len(commands), 4, 'Expected lint/build/build-params/unittest pipeline')
        for command in commands:
            with self.subTest(command=command):
                self.assertIn(command, guide.splitlines())

    def test_no_credentials_rule_matches_ci_and_script(self):
        guide = ' '.join((ROOT / 'CONTRIBUTING.md').read_text(encoding='utf-8').split())
        self.assertIn('No Azure credentials are required for local checks or CI', guide)
        self.assertIn('Do not introduce credentials', guide)
        for relative in ('scripts/check.sh', '.github/workflows/ci.yml'):
            source = (ROOT / relative).read_text(encoding='utf-8')
            with self.subTest(path=relative):
                self.assertNotRegex(source, r'(?i)\bsecrets\.|azure/login|\baz\s+(?:login|deployment)\b|\bbicep\s+publish\b')

    def test_workflow_and_editor_conventions_are_explicit(self):
        guide = ' '.join((ROOT / 'CONTRIBUTING.md').read_text(encoding='utf-8').split())
        for phrase in ('feature branch', 'Open a PR', 'completed validation results',
                       'module parameter/output wiring', 'fixed security defaults'):
            self.assertIn(phrase, guide)
        config = (ROOT / '.editorconfig').read_text(encoding='utf-8')
        for setting in ('end_of_line = lf', 'insert_final_newline = true',
                        'indent_style = space', 'indent_size = 2', '[*.py]\nindent_size = 4'):
            self.assertIn(setting, config)


if __name__ == '__main__':
    unittest.main()
