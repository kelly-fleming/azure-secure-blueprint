"""Static storage posture checks; no deployment or ARM expression evaluation."""

from copy import deepcopy
import json
from pathlib import Path
import re
import unittest

from arm_inspector import InspectionError, load_template, require_property, require_resource, walk_resources


ROOT = Path(__file__).resolve().parents[1]


def assert_storage_security(template):
    """Assert literal security controls on the unique recursively located account."""
    storage = require_resource(template, 'Microsoft.Storage/storageAccounts')
    expected_fields = {
        ('kind',): 'StorageV2',
        ('properties', 'supportsHttpsTrafficOnly'): True,
        ('properties', 'minimumTlsVersion'): 'TLS1_2',
        ('properties', 'allowBlobPublicAccess'): False,
        ('properties', 'allowSharedKeyAccess'): False,
        ('properties', 'defaultToOAuthAuthentication'): True,
        ('properties', 'publicNetworkAccess'): 'Disabled',
    }
    for path, expected in expected_fields.items():
        value = require_property(storage, *path)
        if type(value) is not type(expected) or value != expected:
            raise InspectionError(f"{'.'.join(path)}: expected literal {expected!r}, got {value!r}")

    # Inspect every template's outputs, including the main template and modules.
    owners = [template] + [
        resource['properties']['template'] for resource in walk_resources(template)
        if resource['type'].lower() == 'microsoft.resources/deployments'
    ]
    allowed_names = {'storageId', 'storageName', 'planId', 'planName', 'appId', 'appName', 'principalId'}
    for owner in owners:
        outputs = owner.get('outputs', {})
        if not isinstance(outputs, dict):
            raise InspectionError('outputs: expected object')
        for name, output in outputs.items():
            if name not in allowed_names:
                raise InspectionError(f'outputs.{name}: unexpected potentially secret output')
            if not isinstance(output, dict) or output.get('type') != 'string' or not isinstance(output.get('value'), str):
                raise InspectionError(f'outputs.{name}: expected nonsecret string output')
            # Known module references/resource IDs are intentionally unresolved;
            # never evaluate or accept key-returning functions as safe identifiers.
            text = json.dumps(output).lower()
            if re.search(r'\blist\w*\s*\(', text) or re.search(
                r'accountkey\s*=|sharedaccesssignature\s*=|[?&]sig=|-----begin', text
            ):
                raise InspectionError(f'outputs.{name}: key/SAS/secret material is forbidden')
            # A variable/parameter reference could conceal a key retrieval outside
            # the output itself. Accept only the identifier expressions we author.
            value = output['value']
            module_name = {
                'storageId': 'storage', 'storageName': 'storage',
                'planId': 'plan', 'planName': 'plan',
                'appId': 'web', 'appName': 'web', 'principalId': 'web',
            }[name]
            resource_type = {
                'storage': 'Microsoft.Storage/storageAccounts',
                'plan': 'Microsoft.Web/serverfarms', 'web': 'Microsoft.Web/sites',
            }[module_name]
            safe_patterns = [
                rf"\[reference\(resourceId\('Microsoft.Resources/deployments', '{module_name}'\), '[^']+'\)\.outputs\.{name}\.value\]",
            ]
            if name.endswith('Name'):
                safe_patterns.extend([r"\[parameters\('name'\)\]", r'[a-z0-9][a-z0-9-]{0,59}'])
            elif name.endswith('Id') and name != 'principalId':
                safe_patterns.append(rf"\[resourceId\('{re.escape(resource_type)}', parameters\('name'\)\)\]")
            else:
                safe_patterns.append(
                    r"\[reference\(resourceId\('Microsoft.Web/sites', parameters\('name'\)\), '[^']+', 'full'\)\.identity\.principalId\]"
                )
            if not any(re.fullmatch(pattern, value) for pattern in safe_patterns):
                raise InspectionError(f'outputs.{name}: unrecognized identifier expression may conceal a secret')


def storage_fixture():
    """Independent positive nested ARM, not copied from generated build output."""
    return {
        'resources': [{
            'type': 'Microsoft.Resources/deployments', 'name': 'fixture-module',
            'properties': {'template': {
                'resources': [{
                    'type': 'Microsoft.Storage/storageAccounts', 'name': 'fictionalstore',
                    'kind': 'StorageV2',
                    'properties': {
                        'supportsHttpsTrafficOnly': True, 'minimumTlsVersion': 'TLS1_2',
                        'allowBlobPublicAccess': False, 'allowSharedKeyAccess': False,
                        'defaultToOAuthAuthentication': True, 'publicNetworkAccess': 'Disabled',
                    },
                }],
                'outputs': {'storageName': {'type': 'string', 'value': 'fictionalstore'}},
            }},
        }],
    }


class CompiledStorageSecurityTests(unittest.TestCase):
    def test_generated_main_storage_security(self):
        # load_template fails with fresh-build advice when the artifact is missing.
        assert_storage_security(load_template(ROOT / 'build/main.json'))


class StorageSecurityMutationTests(unittest.TestCase):
    def test_positive_fixture(self):
        assert_storage_security(storage_fixture())

    def test_public_blob_and_shared_key_are_rejected(self):
        for field in ('allowBlobPublicAccess', 'allowSharedKeyAccess'):
            with self.subTest(field=field):
                template = deepcopy(storage_fixture())
                require_resource(template, 'Microsoft.Storage/storageAccounts')['properties'][field] = True
                with self.assertRaisesRegex(InspectionError, field):
                    assert_storage_security(template)

    def test_unresolved_security_expression_is_rejected(self):
        template = storage_fixture()
        require_resource(template, 'Microsoft.Storage/storageAccounts')['properties']['allowSharedKeyAccess'] = "[parameters('sharedKey')]"
        with self.assertRaisesRegex(InspectionError, 'allowSharedKeyAccess: unresolved ARM expression'):
            assert_storage_security(template)

    def test_key_output_cannot_hide_under_allowed_name(self):
        template = storage_fixture()
        template['outputs'] = {'storageId': {
            'type': 'string', 'value': "[listKeys('fictional-id', '2023-05-01').keys[0].value]",
        }}
        with self.assertRaisesRegex(InspectionError, 'outputs.storageId: key/SAS/secret'):
            assert_storage_security(template)

    def test_key_output_cannot_hide_behind_variable_or_parameter(self):
        for value in ("[variables('leakedKey')]", "[parameters('secretValue')]"):
            with self.subTest(value=value):
                template = storage_fixture()
                template['variables'] = {'leakedKey': "[listKeys('fictional-id', '2023-05-01').keys[0].value]"}
                template['outputs'] = {'storageId': {'type': 'string', 'value': value}}
                with self.assertRaisesRegex(InspectionError, 'outputs.storageId: unrecognized identifier expression'):
                    assert_storage_security(template)


if __name__ == '__main__':
    unittest.main()
