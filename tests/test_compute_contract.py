"""Independent Linux plan contracts against future compiled ARM; no cloud calls."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def templates(template):
    yield template
    for resource in template.get('resources', []):
        if resource.get('type', '').lower() == 'microsoft.resources/deployments':
            nested = resource.get('properties', {}).get('template')
            if isinstance(nested, dict):
                yield from templates(nested)


class ComputeContractTests(unittest.TestCase):
    def test_compiled_linux_plan(self):
        artifact = ROOT / 'build/main.json'
        self.assertTrue(
            artifact.is_file(),
            'Compile infra/main.bicep to fresh build/main.json after composition; do not reuse stale output.',
        )
        template = json.loads(artifact.read_text(encoding='utf-8'))
        matches = [
            (owner, resource)
            for owner in templates(template)
            for resource in owner.get('resources', [])
            if resource.get('type', '').lower() == 'microsoft.web/serverfarms'
        ]
        self.assertEqual(len(matches), 1, 'Expected exactly one App Service Plan in compiled templates.')
        owner, plan = matches[0]
        self.assertEqual(plan['type'], 'Microsoft.Web/serverfarms')
        self.assertEqual(plan['apiVersion'], '2024-04-01')
        self.assertEqual(plan['kind'], 'linux')
        self.assertIs(plan['properties']['reserved'], True)
        self.assertEqual(plan['sku']['name'], "[parameters('sku')]")
        self.assertEqual(plan['sku']['tier'], 'Basic')
        self.assertIs(type(plan['sku']['capacity']), int)
        self.assertEqual(plan['sku']['capacity'], 1)
        sku = owner['parameters']['sku']
        self.assertEqual(sku['type'], 'string')
        self.assertEqual(sku['defaultValue'], 'B1')
        self.assertEqual(set(sku['allowedValues']), {'B1', 'B2', 'B3'})
        outputs = owner['outputs']
        self.assertEqual(set(outputs), {'planId', 'planName'})
        self.assertEqual(outputs['planId']['type'], 'string')
        self.assertEqual(
            outputs['planId']['value'],
            "[resourceId('Microsoft.Web/serverfarms', parameters('name'))]",
        )
        self.assertEqual(outputs['planName']['type'], 'string')
        self.assertEqual(outputs['planName']['value'], "[parameters('name')]")


if __name__ == '__main__':
    unittest.main()
