"""Independent synthetic controls exercise the same helpers as artifact tests."""

import re
import unittest

from arm_inspector import InspectionError, require_resource
from test_composition_contract import assert_composition_contract, composition_fixture
from test_storage_security import assert_storage_security
from test_web_security import assert_web_security


def regression_fixture():
    """Synthetic graph and explicit positive controls; never read compiled output."""
    template = composition_fixture()
    storage = require_resource(template, 'Microsoft.Storage/storageAccounts')
    storage.update({
        'kind': 'StorageV2',
        'properties': {
            'supportsHttpsTrafficOnly': True,
            'minimumTlsVersion': 'TLS1_2',
            'allowBlobPublicAccess': False,
            'allowSharedKeyAccess': False,
            'defaultToOAuthAuthentication': True,
            'publicNetworkAccess': 'Disabled',
        },
    })
    app = require_resource(template, 'Microsoft.Web/sites')
    app.update({
        'identity': {'type': 'SystemAssigned'},
        'properties': {
            'httpsOnly': True,
            'publicNetworkAccess': 'Disabled',
            'serverFarmId': "[parameters('planId')]",
            'siteConfig': {
                'minTlsVersion': '1.2',
                'scmMinTlsVersion': '1.2',
                'ftpsState': 'Disabled',
                'remoteDebuggingEnabled': False,
            },
        },
    })
    return template


# Each row identifies one mutation, the production assertion helper it exercises,
# and the exact field expected in that helper's failure. None alters other controls.
CONTROL_CASES = (
    ('storage HTTPS off', assert_storage_security, 'Microsoft.Storage/storageAccounts',
     ('properties', 'supportsHttpsTrafficOnly'), False, 'properties.supportsHttpsTrafficOnly'),
    ('storage TLS lowered', assert_storage_security, 'Microsoft.Storage/storageAccounts',
     ('properties', 'minimumTlsVersion'), 'TLS1_0', 'properties.minimumTlsVersion'),
    ('shared key enabled', assert_storage_security, 'Microsoft.Storage/storageAccounts',
     ('properties', 'allowSharedKeyAccess'), True, 'properties.allowSharedKeyAccess'),
    ('blob public enabled', assert_storage_security, 'Microsoft.Storage/storageAccounts',
     ('properties', 'allowBlobPublicAccess'), True, 'properties.allowBlobPublicAccess'),
    ('storage public enabled', assert_storage_security, 'Microsoft.Storage/storageAccounts',
     ('properties', 'publicNetworkAccess'), 'Enabled', 'properties.publicNetworkAccess'),
    ('web HTTPS off', assert_web_security, 'Microsoft.Web/sites',
     ('properties', 'httpsOnly'), False, 'properties.httpsOnly'),
    ('web TLS lowered', assert_web_security, 'Microsoft.Web/sites',
     ('properties', 'siteConfig', 'minTlsVersion'), '1.0', 'properties.siteConfig.minTlsVersion'),
    ('SCM TLS lowered', assert_web_security, 'Microsoft.Web/sites',
     ('properties', 'siteConfig', 'scmMinTlsVersion'), '1.0', 'properties.siteConfig.scmMinTlsVersion'),
    ('web public enabled', assert_web_security, 'Microsoft.Web/sites',
     ('properties', 'publicNetworkAccess'), 'Enabled', 'properties.publicNetworkAccess'),
    ('FTPS enabled', assert_web_security, 'Microsoft.Web/sites',
     ('properties', 'siteConfig', 'ftpsState'), 'AllAllowed', 'properties.siteConfig.ftpsState'),
    ('remote debug enabled', assert_web_security, 'Microsoft.Web/sites',
     ('properties', 'siteConfig', 'remoteDebuggingEnabled'), True, 'properties.siteConfig.remoteDebuggingEnabled'),
)


class SecurityRegressionTests(unittest.TestCase):
    def test_positive_controls_satisfy_all_validators(self):
        for validator in (assert_storage_security, assert_web_security, assert_composition_contract):
            with self.subTest(validator=validator.__name__):
                validator(regression_fixture())

    def test_single_control_mutations_fail_for_the_intended_field(self):
        for name, validator, resource_type, path, bad_value, expected_field in CONTROL_CASES:
            with self.subTest(case=name, validator=validator.__name__, field=expected_field):
                template = regression_fixture()
                validator(template)  # Establish that this exact baseline has no unrelated failure.
                parent = require_resource(template, resource_type)
                for key in path[:-1]:
                    parent = parent[key]
                parent[path[-1]] = bad_value
                with self.assertRaisesRegex(InspectionError, re.escape(expected_field)):
                    validator(template)

    def test_removed_managed_identity_fails_at_identity(self):
        template = regression_fixture()
        assert_web_security(template)
        del require_resource(template, 'Microsoft.Web/sites')['identity']
        with self.assertRaisesRegex(InspectionError, 'Missing property identity'):
            assert_web_security(template)

    def test_unexpected_key_outputs_fail_in_both_output_validators(self):
        cases = (
            (assert_storage_security, 'storageId', 'outputs.storageId: key/SAS/secret'),
            (assert_composition_contract, 'storageId', 'outputs.storageId: unexpected identifier expression'),
            (assert_composition_contract, 'accountKey', 'outputs: unexpected/missing identifier output'),
        )
        for validator, name, expected_failure in cases:
            with self.subTest(validator=validator.__name__, output=name):
                template = regression_fixture()
                validator(template)
                template['outputs'][name] = {
                    'type': 'string',
                    'value': "[listKeys('fictional-storage', '2023-05-01').keys[0].value]",
                }
                with self.assertRaisesRegex(InspectionError, re.escape(expected_failure)):
                    validator(template)


if __name__ == '__main__':
    unittest.main()
