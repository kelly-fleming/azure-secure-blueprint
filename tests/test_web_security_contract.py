"""Future compiled Web App contracts; no ARM expression evaluation or cloud calls."""

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


class WebSecurityContractTests(unittest.TestCase):
    def test_compiled_web_security(self):
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
            if resource.get('type', '').lower() == 'microsoft.web/sites'
        ]
        self.assertEqual(len(matches), 1, 'Expected exactly one Web App in nested compiled templates.')
        owner, app = matches[0]
        self.assertEqual(app['type'], 'Microsoft.Web/sites')
        self.assertEqual(app['apiVersion'], '2024-04-01')
        self.assertEqual(app['kind'], 'app,linux')
        self.assertEqual(app['identity'], {'type': 'SystemAssigned'})
        properties = app['properties']
        self.assertIs(properties['httpsOnly'], True)
        self.assertEqual(properties['publicNetworkAccess'], 'Disabled')
        self.assertEqual(properties['serverFarmId'], "[parameters('planId')]")
        self.assertEqual(owner['parameters']['planId']['type'], 'string')
        config = properties['siteConfig']
        self.assertEqual(config['minTlsVersion'], '1.2')
        self.assertEqual(config['scmMinTlsVersion'], '1.2')
        self.assertEqual(config['ftpsState'], 'Disabled')
        self.assertIs(config['remoteDebuggingEnabled'], False)
        # No application settings, publishing credentials, or deployment package.
        self.assertEqual(set(properties), {'serverFarmId', 'httpsOnly', 'publicNetworkAccess', 'siteConfig'})
        self.assertEqual(set(config), {'minTlsVersion', 'scmMinTlsVersion', 'ftpsState', 'remoteDebuggingEnabled'})
        outputs = owner['outputs']
        self.assertEqual(set(outputs), {'appId', 'appName', 'principalId'})
        for name, output in outputs.items():
            with self.subTest(output=name):
                self.assertEqual(output['type'], 'string')
        self.assertEqual(outputs['appId']['value'], "[resourceId('Microsoft.Web/sites', parameters('name'))]")
        self.assertEqual(outputs['appName']['value'], "[parameters('name')]")
        self.assertEqual(
            outputs['principalId']['value'],
            "[reference(resourceId('Microsoft.Web/sites', parameters('name')), '2024-04-01', 'full').identity.principalId]",
        )
        self.assertEqual(
            {parameter['type'] for parameter in owner['parameters'].values()},
            {'string', 'object'},
        )


if __name__ == '__main__':
    unittest.main()
