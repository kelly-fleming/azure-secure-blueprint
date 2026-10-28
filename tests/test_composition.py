"""Compiled module graph contracts; structural assertions do not execute ARM."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CompositionTests(unittest.TestCase):
    def test_compiled_module_graph(self):
        artifact = ROOT / 'build/main.json'
        self.assertTrue(artifact.is_file(), 'Compile infra/main.bicep to fresh build/main.json; do not reuse stale output.')
        template = json.loads(artifact.read_text(encoding='utf-8'))
        self.assertIn('deploymentTemplate.json', template['$schema'])
        self.assertNotIn('subscriptionDeploymentTemplate.json', template['$schema'])
        resources = template['resources']
        self.assertEqual(len(resources), 3)
        self.assertEqual({item['type'] for item in resources}, {'Microsoft.Resources/deployments'})
        modules = {item['name']: item for item in resources}
        self.assertEqual(set(modules), {'storage', 'plan', 'web'})
        contracts = {
            'storage': ('Microsoft.Storage/storageAccounts', 'storageAccountName', {'name', 'location', 'tags'}),
            'plan': ('Microsoft.Web/serverfarms', 'appServicePlanName', {'name', 'location', 'tags', 'sku'}),
            'web': ('Microsoft.Web/sites', 'webAppName', {'name', 'location', 'tags', 'planId'}),
        }
        for name, (resource_type, name_variable, parameter_names) in contracts.items():
            with self.subTest(module=name):
                module = modules[name]
                properties = module['properties']
                self.assertEqual(properties['mode'], 'Incremental')
                nested = properties['template']['resources']
                self.assertEqual(len(nested), 1)
                self.assertEqual(nested[0]['type'], resource_type)
                # Exact nested inventories reject hidden deployments/RBAC or other resources.
                self.assertNotIn('resources', nested[0])
                parameters = properties['parameters']
                self.assertEqual(set(parameters), parameter_names)
                self.assertEqual(parameters['name']['value'], f"[variables('{name_variable}')]")
                self.assertEqual(parameters['location']['value'], "[parameters('location')]")
                self.assertEqual(parameters['tags']['value'], "[parameters('tags')]")
        self.assertEqual(modules['plan']['properties']['parameters']['sku']['value'], "[parameters('appServicePlanSku')]")
        plan_reference = modules['web']['properties']['parameters']['planId']['value']
        self.assertRegex(plan_reference, r"^\[reference\(resourceId\('Microsoft.Resources/deployments', 'plan'\), '[^']+'\)\.outputs\.planId\.value\]$")
        self.assertEqual(modules['web']['dependsOn'], ["[resourceId('Microsoft.Resources/deployments', 'plan')]"])
        for name in ('storage', 'plan'):
            self.assertEqual(modules[name].get('dependsOn', []), [])
        output_modules = {
            'storageName': 'storage', 'storageId': 'storage',
            'planName': 'plan', 'planId': 'plan',
            'appName': 'web', 'appId': 'web', 'principalId': 'web',
        }
        self.assertEqual(set(template['outputs']), set(output_modules))
        for output_name, module_name in output_modules.items():
            with self.subTest(output=output_name):
                output = template['outputs'][output_name]
                self.assertEqual(output['type'], 'string')
                self.assertRegex(
                    output['value'],
                    rf"^\[reference\(resourceId\('Microsoft.Resources/deployments', '{module_name}'\), '[^']+'\)\.outputs\.{output_name}\.value\]$",
                )


if __name__ == '__main__':
    unittest.main()
