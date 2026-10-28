"""Generated dev parameter boundaries, independent of source-string assertions."""

from copy import deepcopy
from pathlib import Path
import re
import unittest

from arm_inspector import InspectionError, require_literal
from test_composition_contract import load_fresh_artifact


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {'environment', 'location', 'projectPrefix', 'uniqueSuffix', 'appServicePlanSku', 'tags'}


def assert_parameter_contract(document):
    if set(document) != {'$schema', 'contentVersion', 'parameters'}:
        raise InspectionError('parameter document: unexpected top-level fields')
    schema = document['$schema']
    if not isinstance(schema, str) or not schema.endswith('/deploymentParameters.json#'):
        raise InspectionError('$schema: expected ARM deployment parameters')
    parameters = document['parameters']
    if not isinstance(parameters, dict) or set(parameters) != EXPECTED:
        raise InspectionError('parameters: expected only the six nonsecret configuration fields')
    values = {}
    for name, parameter in parameters.items():
        if not isinstance(parameter, dict) or set(parameter) != {'value'}:
            raise InspectionError(f'parameters.{name}: only literal value is allowed; secret references/types are forbidden')
        values[name] = require_literal(parameter['value'], f'parameters.{name}')
    for name in EXPECTED - {'tags'}:
        if not isinstance(values[name], str):
            raise InspectionError(f'parameters.{name}: expected string')
    if values['environment'] != 'dev' or values['appServicePlanSku'] not in ('B1', 'B2', 'B3'):
        raise InspectionError('parameters: only dev and supported Basic SKU values are allowed')
    for name, pattern in (
        ('projectPrefix', r'[a-z0-9]{2,6}'), ('uniqueSuffix', r'[a-z0-9]{6,12}'),
        ('location', r'[a-z][a-z0-9]{1,39}'),
    ):
        if not re.fullmatch(pattern, values[name]):
            raise InspectionError(f'parameters.{name}: invalid configuration syntax')
    tags = values['tags']
    if not isinstance(tags, dict) or set(tags) != {'environment', 'project', 'purpose'}:
        raise InspectionError('parameters.tags: only fictional environment/project/purpose tags are allowed')
    if tags != {'environment': 'dev', 'project': 'fictional-blueprint', 'purpose': 'source-example'}:
        raise InspectionError('parameters.tags: expected fictional example tags without private identifiers')
    def inspect(value, path):
        if isinstance(value, dict):
            for key, child in value.items():
                inspect(child, f'{path}.{key}')
        elif isinstance(value, str) and re.search(
            r'(?i)/subscriptions/|/resourcegroups/|\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b|'
            r'\.onmicrosoft\.com|accountkey\s*=|sharedaccesssignature\s*=|[?&]sig=|-----BEGIN', value
        ):
            raise InspectionError(f'{path}: identifier or secret material is forbidden')
    inspect(values, 'parameters')


def parameter_fixture():
    return {
        '$schema': 'https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#',
        'contentVersion': '1.0.0.0',
        'parameters': {name: {'value': value} for name, value in {
            'environment': 'dev', 'location': 'eastus', 'projectPrefix': 'demo',
            'uniqueSuffix': 'sample01', 'appServicePlanSku': 'B1',
            'tags': {'environment': 'dev', 'project': 'fictional-blueprint', 'purpose': 'source-example'},
        }.items()},
    }


class CompiledParameterBoundaryTests(unittest.TestCase):
    def test_generated_dev_parameters(self):
        sources = [ROOT / 'bicepconfig.json', ROOT / 'params/dev.bicepparam', *(ROOT / 'infra').rglob('*.bicep')]
        assert_parameter_contract(load_fresh_artifact(ROOT / 'build/dev.parameters.json', sources))


class ParameterBoundaryMutationTests(unittest.TestCase):
    def test_positive_fixture(self):
        assert_parameter_contract(parameter_fixture())

    def test_secret_parameter_and_reference_are_rejected(self):
        for change in ('extra', 'reference', 'expression'):
            with self.subTest(change=change):
                document = deepcopy(parameter_fixture())
                if change == 'extra':
                    document['parameters']['password'] = {'value': 'forbidden-example'}
                elif change == 'reference':
                    document['parameters']['uniqueSuffix'] = {'reference': {'keyVault': {'id': 'forbidden'}}}
                else:
                    document['parameters']['uniqueSuffix']['value'] = "[parameters('secret')]"
                with self.assertRaises(InspectionError):
                    assert_parameter_contract(document)

    def test_real_identifier_shape_is_rejected(self):
        document = parameter_fixture()
        document['parameters']['uniqueSuffix']['value'] = '12345678-1234-1234-1234-123456789abc'
        with self.assertRaisesRegex(InspectionError, 'uniqueSuffix'):
            assert_parameter_contract(document)


if __name__ == '__main__':
    unittest.main()
