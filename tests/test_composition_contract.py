"""Resource/output boundaries on fresh compiled ARM, separate from source checks."""

from pathlib import Path
import re
import unittest

from arm_inspector import InspectionError, load_template, walk_resources


ROOT = Path(__file__).resolve().parents[1]
MODULE_TYPES = {
    'storage': 'Microsoft.Storage/storageAccounts',
    'plan': 'Microsoft.Web/serverfarms',
    'web': 'Microsoft.Web/sites',
}
OUTPUT_MODULES = {
    'storageId': 'storage', 'storageName': 'storage', 'planId': 'plan',
    'planName': 'plan', 'appId': 'web', 'appName': 'web', 'principalId': 'web',
}


def load_fresh_artifact(path, sources):
    """Reject artifacts older than any listed source; never compile implicitly.

    Timestamp checks detect stale local output, not provenance or compiler success.
    The final check script must still remove old artifacts and rebuild every run.
    """
    template = load_template(path)
    try:
        artifact_time = Path(path).stat().st_mtime_ns
        for source in sources:
            if Path(source).stat().st_mtime_ns > artifact_time:
                raise InspectionError(f'{path}: stale relative to {source}; regenerate fresh Bicep output')
    except OSError as error:
        raise InspectionError(f'{path}: cannot establish artifact freshness: {error}') from error
    return template


def assert_composition_contract(template):
    schema = template.get('$schema', '')
    if not isinstance(schema, str) or not schema.endswith('/deploymentTemplate.json#'):
        raise InspectionError('$schema: expected resource-group deployment template')
    resources = list(walk_resources(template))
    allowed_types = set(MODULE_TYPES.values()) | {'Microsoft.Resources/deployments'}
    for resource in resources:
        if resource['type'] not in allowed_types:
            raise InspectionError(f"Unexpected resource type {resource['type']}")
        if 'resources' in resource:
            raise InspectionError('Unexpected child resources outside the supported module contracts')
    top = template['resources']
    if len(top) != 3 or any(item['type'] != 'Microsoft.Resources/deployments' for item in top):
        raise InspectionError('Expected exactly storage, plan and web module deployments')
    modules = {item.get('name'): item for item in top}
    if set(modules) != set(MODULE_TYPES):
        raise InspectionError('Module names must be storage, plan and web')
    owners = [(template, OUTPUT_MODULES)]
    for name, resource_type in MODULE_TYPES.items():
        module = modules[name]
        properties = module['properties']
        nested = properties['template']
        if properties.get('mode') != 'Incremental':
            raise InspectionError(f'{name}: expected Incremental deployment')
        if len(nested['resources']) != 1 or nested['resources'][0]['type'] != resource_type:
            raise InspectionError(f'{name}: expected only {resource_type}')
        parameter_names = {'name', 'location', 'tags'} | ({'sku'} if name == 'plan' else {'planId'} if name == 'web' else set())
        if set(properties.get('parameters', {})) != parameter_names:
            raise InspectionError(f'{name}: unexpected module parameter contract')
        owners.append((nested, {key: value for key, value in OUTPUT_MODULES.items() if value == name}))
    for owner, outputs_expected in owners:
        outputs = owner.get('outputs', {})
        if not isinstance(outputs, dict) or set(outputs) != set(outputs_expected):
            raise InspectionError('outputs: unexpected/missing identifier output; secret-looking outputs are forbidden')
        for name, module_name in outputs_expected.items():
            output = outputs[name]
            if not isinstance(output, dict) or output.get('type') != 'string' or not isinstance(output.get('value'), str):
                raise InspectionError(f'outputs.{name}: expected nonsecret identifier string')
            if owner is template:
                pattern = rf"\[reference\(resourceId\('Microsoft.Resources/deployments', '{module_name}'\), '[^']+'\)\.outputs\.{name}\.value\]"
            elif name.endswith('Name'):
                pattern = r"\[parameters\('name'\)\]"
            elif name == 'principalId':
                pattern = r"\[reference\(resourceId\('Microsoft.Web/sites', parameters\('name'\)\), '[^']+', 'full'\)\.identity\.principalId\]"
            else:
                pattern = rf"\[resourceId\('{re.escape(MODULE_TYPES[module_name])}', parameters\('name'\)\)\]"
            if not re.fullmatch(pattern, output['value']):
                raise InspectionError(f'outputs.{name}: unexpected identifier expression or secret value')


def composition_fixture():
    """Minimal independent graph; not a generated template snapshot."""
    template = {'$schema': 'https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#',
                'resources': [], 'outputs': {}}
    for name, resource_type in MODULE_TYPES.items():
        nested = {'resources': [{'type': resource_type, 'name': 'fixture'}], 'outputs': {}}
        params = {'name': {'value': 'fixture'}, 'location': {'value': 'eastus'}, 'tags': {'value': {}}}
        if name == 'plan':
            params['sku'] = {'value': 'B1'}
        if name == 'web':
            params['planId'] = {'value': "[parameters('planId')]"}
        for output_name, owner in OUTPUT_MODULES.items():
            if owner != name:
                continue
            if output_name.endswith('Name'):
                expression = "[parameters('name')]"
            elif output_name == 'principalId':
                expression = "[reference(resourceId('Microsoft.Web/sites', parameters('name')), '2024-04-01', 'full').identity.principalId]"
            else:
                expression = f"[resourceId('{resource_type}', parameters('name'))]"
            nested['outputs'][output_name] = {'type': 'string', 'value': expression}
            template['outputs'][output_name] = {'type': 'string', 'value': f"[reference(resourceId('Microsoft.Resources/deployments', '{name}'), '2022-09-01').outputs.{output_name}.value]"}
        template['resources'].append({'type': 'Microsoft.Resources/deployments', 'name': name,
                                      'properties': {'mode': 'Incremental', 'parameters': params, 'template': nested}})
    return template


class CompiledCompositionContractTests(unittest.TestCase):
    def test_generated_resource_boundaries(self):
        sources = [ROOT / 'bicepconfig.json', *(ROOT / 'infra').rglob('*.bicep')]
        assert_composition_contract(load_fresh_artifact(ROOT / 'build/main.json', sources))


class SourceScopeTests(unittest.TestCase):
    def test_main_targets_resource_group(self):
        source = (ROOT / 'infra/main.bicep').read_text(encoding='utf-8')
        self.assertRegex(source, r"(?m)^targetScope\s*=\s*'resourceGroup'\s*$")


class CompositionBoundaryMutationTests(unittest.TestCase):
    def test_positive_fixture(self):
        assert_composition_contract(composition_fixture())

    def test_extra_role_assignment_is_rejected(self):
        template = composition_fixture()
        template['resources'][0]['properties']['template']['resources'].append(
            {'type': 'Microsoft.Authorization/roleAssignments', 'name': 'extra-role'})
        with self.assertRaisesRegex(InspectionError, 'Unexpected resource type Microsoft.Authorization/roleAssignments'):
            assert_composition_contract(template)

    def test_secret_output_is_rejected(self):
        for allowed_name in (False, True):
            with self.subTest(allowed_name=allowed_name):
                template = composition_fixture()
                name = 'storageId' if allowed_name else 'accountKey'
                template['outputs'][name] = {'type': 'string', 'value': "[listKeys('fixture', '2023-05-01').keys[0].value]"}
                with self.assertRaisesRegex(InspectionError, 'outputs'):
                    assert_composition_contract(template)


if __name__ == '__main__':
    unittest.main()
