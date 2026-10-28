"""Parameter source contracts and future compiled ARM checks, without Azure."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = {
    'environment', 'location', 'projectPrefix', 'uniqueSuffix',
    'appServicePlanSku', 'tags',
}


class ParameterSourceTests(unittest.TestCase):
    def test_interface_and_defaults(self):
        source = (ROOT / 'infra/main.bicep').read_text(encoding='utf-8')
        self.assertEqual(set(re.findall(r'^param (\w+) ', source, re.M)), PARAMETERS)
        for declaration in (
            "param environment string = 'dev'",
            'param location string = resourceGroup().location',
            "param projectPrefix string = 'demo'",
            "param uniqueSuffix string = 'sample01'",
            "param appServicePlanSku string = 'B1'",
            'param tags object = {',
        ):
            with self.subTest(declaration=declaration):
                self.assertIn(declaration, source)
        self.assertNotIn('@secure()', source)

    def test_name_wiring_and_normalization(self):
        source = (ROOT / 'infra/main.bicep').read_text(encoding='utf-8')
        for parameter, variable in (
            ('projectPrefix', 'normalizedPrefix'), ('uniqueSuffix', 'normalizedSuffix'),
        ):
            line = next(line for line in source.splitlines() if line.startswith(f'var {variable} ='))
            self.assertIn(f'length({parameter})', line)
            self.assertIn(f'toLower(substring({parameter}, i, 1))', line)
            self.assertIn(" : '0'", line)
        self.assertIn("var storageAccountName = '${normalizedPrefix}${environment}${normalizedSuffix}'", source)
        self.assertIn("var appServicePlanName = '${normalizedPrefix}-${environment}-plan-${normalizedSuffix}'", source)
        self.assertIn("var webAppName = '${normalizedPrefix}-${environment}-web-${normalizedSuffix}'", source)

    def test_independent_name_bound_fixtures(self):
        for prefix, suffix in (('ab', '123456'), ('abcdef', '123456789012'), ('demo', 'sample01')):
            with self.subTest(prefix=prefix, suffix=suffix):
                storage = f'{prefix}dev{suffix}'
                self.assertRegex(storage, r'^[a-z0-9]{3,24}$')
                for name in (f'{prefix}-dev-plan-{suffix}', f'{prefix}-dev-web-{suffix}'):
                    self.assertLessEqual(len(name), 60)
                    self.assertRegex(name, r'^[a-z0-9][a-z0-9-]*[a-z0-9]$')
        self.assertEqual('demo' + 'dev' + 'sample01', 'demodevsample01')


class CompiledParameterTests(unittest.TestCase):
    def test_compiled_interface(self):
        artifact = ROOT / 'build/main.json'
        self.assertTrue(artifact.is_file(), 'Generate fresh build/main.json with Bicep before compiled checks; do not reuse stale output.')
        template = json.loads(artifact.read_text(encoding='utf-8'))
        parameters = template['parameters']
        self.assertEqual(set(parameters), PARAMETERS)
        self.assertEqual(parameters['environment']['allowedValues'], ['dev'])
        self.assertEqual(parameters['environment']['defaultValue'], 'dev')
        self.assertEqual(parameters['appServicePlanSku']['defaultValue'], 'B1')
        for name, minimum, maximum in (('projectPrefix', 2, 6), ('uniqueSuffix', 6, 12)):
            with self.subTest(name=name):
                self.assertEqual(parameters[name]['minLength'], minimum)
                self.assertEqual(parameters[name]['maxLength'], maximum)
        for name, parameter in parameters.items():
            with self.subTest(name=name):
                self.assertIn(parameter['type'], ('string', 'object'))
        for name in ('storageName', 'planName', 'appName'):
            self.assertEqual(template['outputs'][name]['type'], 'string')
        # ARM expressions are intentionally not evaluated by this source suite.


if __name__ == '__main__':
    unittest.main()
