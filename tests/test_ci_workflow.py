"""Static checks for the authored workflow shape, not a YAML/Actions evaluator."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


def assert_ci_contract(source):
    required_patterns = {
        'workflow name': r'(?m)^name: CI$',
        'push and PR triggers': r'(?m)^on:\n  push:\n  pull_request:\n',
        'read-only permission': r'(?m)^permissions:\n  contents: read\n',
        'concurrency': r'(?m)^concurrency:\n  group: \$\{\{ github.workflow \}\}-\$\{\{ github.ref \}\}\n  cancel-in-progress: true\n',
        'checks job': r'(?m)^jobs:\n  checks:\n    runs-on: ubuntu-24.04\n',
        'checkout': r'(?m)^        uses: actions/checkout@v4$',
        'no persisted credentials': r'(?m)^          persist-credentials: false$',
        'Python setup': r'(?m)^        uses: actions/setup-python@v5$',
        'Python version': r"(?m)^          python-version: '3.12'$",
        'required checks': r'(?m)^        run: bash scripts/check.sh$',
    }
    for name, pattern in required_patterns.items():
        if not re.search(pattern, source):
            raise AssertionError(f'Missing required CI contract: {name}')
    for text in (
        'set -Eeuo pipefail',
        'curl --fail --silent --show-error --location --retry 3',
        'https://github.com/Azure/bicep/releases/download/v0.37.4/bicep-linux-x64',
        'chmod +x "$bicep_bin_dir/bicep"',
        'echo "$bicep_bin_dir" >> "$GITHUB_PATH"',
    ):
        if text not in source:
            raise AssertionError(f'Missing required CI setup: {text}')
    if re.search(r'(?i)continue-on-error|\|\|\s*(?:true|:)\b|\bsecrets\.|azure/login|\baz\s|\bwhat-if\b|\bbicep\s+publish\b', source):
        raise AssertionError('CI must preserve failures and use no cloud credentials/operations')
    if re.search(r'(?m)^\s+(?:if|paths|paths-ignore|branches|branches-ignore):', source):
        raise AssertionError('Required checks must not be conditionally skipped or trigger-filtered')
    if source.index('uses: actions/checkout@v4') > source.index('run: bash scripts/check.sh'):
        raise AssertionError('Checkout must precede checks')
    if source.index('>> "$GITHUB_PATH"') > source.index('run: bash scripts/check.sh'):
        raise AssertionError('Bicep PATH setup must precede checks')


class CIWorkflowTests(unittest.TestCase):
    def test_authored_workflow_contract(self):
        assert_ci_contract((ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8'))

    def test_missing_checks_and_suppressed_failure_are_rejected(self):
        source = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')
        for changed in (
            source.replace('run: bash scripts/check.sh', 'run: echo skipped'),
            source.replace('run: bash scripts/check.sh', 'continue-on-error: true\n        run: bash scripts/check.sh'),
            source.replace('contents: read', 'contents: write'),
        ):
            with self.subTest(source=changed), self.assertRaises(AssertionError):
                assert_ci_contract(changed)


if __name__ == '__main__':
    unittest.main()
