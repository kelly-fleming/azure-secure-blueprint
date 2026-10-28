"""Documentation source/link contracts; no setup commands are executed."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ReadmeTests(unittest.TestCase):
    def test_first_screen_sets_scope_and_workflow(self):
        text = ' '.join((ROOT / 'README.md').read_text(encoding='utf-8').split())
        for phrase in ('fictional, source-only', 'Nothing has been deployed',
                       'No Azure account is needed', 'not production-ready',
                       'bash scripts/check.sh', 'ignored `build/`'):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_required_docs_are_linked_and_local_targets_exist(self):
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        for target in ('docs/ARCHITECTURE.md', 'docs/DECISIONS.md', 'docs/QUICKSTART.md',
                       'docs/VALIDATION.md', 'docs/TOOLCHAIN.md', 'docs/PARAMETERS.md',
                       'docs/TEST_STRATEGY.md'):
            self.assertIn(f']({target})', readme)
        for relative in ('README.md', 'docs/QUICKSTART.md'):
            document = ROOT / relative
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', document.read_text(encoding='utf-8')):
                if '://' in target or target.startswith('#'):
                    continue
                with self.subTest(document=relative, target=target):
                    self.assertTrue((document.parent / target.split('#')[0]).is_file(), 'Broken local documentation link')

    def test_quickstart_has_setup_and_direct_commands(self):
        source = (ROOT / 'docs/QUICKSTART.md').read_text(encoding='utf-8')
        for text in (
            'https://github.com/Azure/bicep/releases/tag/v0.37.4',
            'https://www.python.org/downloads/', 'Python 3.12 or newer',
            'bash scripts/check.sh', 'bicep lint infra/main.bicep',
            'bicep build infra/main.bicep --outfile build/main.json',
            'bicep build-params params/dev.bicepparam --outfile build/dev.parameters.json',
            'python -m unittest discover -s tests -v',
        ):
            with self.subTest(text=text):
                self.assertIn(text, source)


if __name__ == '__main__':
    unittest.main()
