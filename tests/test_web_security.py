"""Web App template intent assertions; no deployment or runtime verification."""

from pathlib import Path
import unittest

from arm_inspector import InspectionError, load_template, require_property, require_resource


ROOT = Path(__file__).resolve().parents[1]


def assert_web_security(template):
    """Inspect literal controls and structurally require the module's plan reference."""
    app = require_resource(template, 'Microsoft.Web/sites')
    expected_fields = {
        ('identity', 'type'): 'SystemAssigned',
        ('properties', 'httpsOnly'): True,
        ('properties', 'publicNetworkAccess'): 'Disabled',
        ('properties', 'siteConfig', 'ftpsState'): 'Disabled',
        ('properties', 'siteConfig', 'remoteDebuggingEnabled'): False,
    }
    for path, expected in expected_fields.items():
        value = require_property(app, *path)
        if type(value) is not type(expected) or value != expected:
            raise InspectionError(f"{'.'.join(path)}: expected literal {expected!r}, got {value!r}")
    for field in ('minTlsVersion', 'scmMinTlsVersion'):
        value = require_property(app, 'properties', 'siteConfig', field)
        if not isinstance(value, str) or value not in ('1.2', '1.3'):
            raise InspectionError(f'properties.siteConfig.{field}: expected supported TLS 1.2 or 1.3 literal, got {value!r}')
    # Runtime plan references must remain expressions, not fabricated resolved IDs.
    plan = require_property(app, 'properties', 'serverFarmId', literal=False)
    if plan != "[parameters('planId')]":
        raise InspectionError('properties.serverFarmId: expected module planId parameter reference')
    # Effective parent-to-module wiring is the separate composition contract.
    # No principal ID is evaluated or treated as runtime security evidence here.


def web_fixture():
    """Independent nested ARM fixture with every required control present."""
    return {'resources': [{
        'type': 'Microsoft.Resources/deployments', 'name': 'fixture-web-module',
        'properties': {'template': {'resources': [{
            'type': 'Microsoft.Web/sites', 'name': 'fictional-web',
            'identity': {'type': 'SystemAssigned'},
            'properties': {
                'serverFarmId': "[parameters('planId')]",
                'httpsOnly': True,
                'publicNetworkAccess': 'Disabled',
                'siteConfig': {
                    'minTlsVersion': '1.2', 'scmMinTlsVersion': '1.2',
                    'ftpsState': 'Disabled', 'remoteDebuggingEnabled': False,
                },
            },
        }]}},
    }]}


class CompiledWebSecurityTests(unittest.TestCase):
    def test_generated_main_web_security(self):
        # Missing artifacts fail with build advice from the shared loader.
        assert_web_security(load_template(ROOT / 'build/main.json'))


class WebSecurityMutationTests(unittest.TestCase):
    def test_positive_fixture(self):
        assert_web_security(web_fixture())

    def test_disabled_https_and_enabled_network_are_rejected(self):
        for field, value in (('httpsOnly', False), ('publicNetworkAccess', 'Enabled')):
            with self.subTest(field=field):
                template = web_fixture()
                app = require_resource(template, 'Microsoft.Web/sites')
                app['properties'][field] = value
                with self.assertRaisesRegex(InspectionError, field):
                    assert_web_security(template)

    def test_tls_for_main_and_scm_is_required(self):
        for field in ('minTlsVersion', 'scmMinTlsVersion'):
            with self.subTest(field=field):
                template = web_fixture()
                app = require_resource(template, 'Microsoft.Web/sites')
                app['properties']['siteConfig'][field] = '1.0'
                with self.assertRaisesRegex(InspectionError, field):
                    assert_web_security(template)

    def test_unresolved_security_control_is_rejected(self):
        template = web_fixture()
        require_resource(template, 'Microsoft.Web/sites')['properties']['httpsOnly'] = "[parameters('https')]"
        with self.assertRaisesRegex(InspectionError, 'httpsOnly: unresolved ARM expression'):
            assert_web_security(template)

    def test_missing_plan_reference_is_rejected(self):
        template = web_fixture()
        del require_resource(template, 'Microsoft.Web/sites')['properties']['serverFarmId']
        with self.assertRaisesRegex(InspectionError, 'serverFarmId'):
            assert_web_security(template)


if __name__ == '__main__':
    unittest.main()
