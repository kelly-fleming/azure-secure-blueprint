"""Storage module contracts against future compiled ARM; never contact Azure."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def templates(template):
    """Visit inline module templates without evaluating ARM expressions."""
    yield template
    for resource in template.get('resources', []):
        if resource.get('type', '').lower() == 'microsoft.resources/deployments':
            nested = resource.get('properties', {}).get('template')
            if isinstance(nested, dict):
                yield from templates(nested)


class StorageContractTests(unittest.TestCase):
    def test_compiled_storage_module(self):
        artifact = ROOT / 'build/main.json'
        self.assertTrue(
            artifact.is_file(),
            'Compile infra/main.bicep to fresh build/main.json after module composition; do not use stale output.',
        )
        template = json.loads(artifact.read_text(encoding='utf-8'))
        matches = [
            (owner, resource)
            for owner in templates(template)
            for resource in owner.get('resources', [])
            if resource.get('type', '').lower() == 'microsoft.storage/storageaccounts'
        ]
        self.assertEqual(len(matches), 1, 'Expected exactly one storage account in compiled module templates.')
        owner, storage = matches[0]
        self.assertEqual(storage['type'], 'Microsoft.Storage/storageAccounts')
        self.assertEqual(storage['apiVersion'], '2023-05-01')
        self.assertEqual(storage['kind'], 'StorageV2')
        self.assertEqual(storage['sku']['name'], 'Standard_LRS')
        properties = storage['properties']
        for field, expected in {
            'supportsHttpsTrafficOnly': True,
            'minimumTlsVersion': 'TLS1_2',
            'allowBlobPublicAccess': False,
            'allowSharedKeyAccess': False,
            'defaultToOAuthAuthentication': True,
            'publicNetworkAccess': 'Disabled',
        }.items():
            with self.subTest(field=field):
                self.assertIn(field, properties)
                self.assertIs(type(properties[field]), type(expected), f'{field} must be a literal of the expected type')
                self.assertEqual(properties[field], expected, f'{field} must match the fixed security contract')
        outputs = owner.get('outputs', {})
        self.assertEqual(set(outputs), {'storageId', 'storageName'})
        self.assertEqual(outputs['storageName']['value'], "[parameters('name')]")
        self.assertEqual(
            outputs['storageId']['value'],
            "[resourceId('Microsoft.Storage/storageAccounts', parameters('name'))]",
        )
        for name, output in outputs.items():
            with self.subTest(output=name):
                self.assertEqual(output['type'], 'string')
                self.assertIsInstance(output['value'], str)
        serialized = json.dumps(owner).lower()
        for forbidden in ('listkeys(', 'listaccountsas(', 'listservicesas('):
            self.assertNotIn(forbidden, serialized)

    def test_source_does_not_retrieve_or_output_credentials(self):
        source = (ROOT / 'infra/modules/storage.bicep').read_text(encoding='utf-8')
        declarations = [line.split()[1] for line in source.splitlines() if line.startswith('output ')]
        self.assertEqual(set(declarations), {'storageId', 'storageName'})
        for forbidden in ('listkeys(', 'listaccountsas(', 'listservicesas('):
            self.assertNotIn(forbidden, source.lower())


if __name__ == '__main__':
    unittest.main()
