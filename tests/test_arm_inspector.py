"""Hand-authored inspector cases independent of generated production artifacts."""

from pathlib import Path
import tempfile
import unittest

from arm_inspector import (
    InspectionError, find_resources, is_expression, load_template, parse_template,
    require_literal, require_property, require_resource, walk_resources,
)


FIXTURE = Path(__file__).resolve().parent / 'fixtures/minimal_template.json'


class ArmInspectorTests(unittest.TestCase):
    def test_direct_and_deep_nested_resources(self):
        template = load_template(FIXTURE)
        self.assertEqual(
            [item['name'] for item in walk_resources(template)],
            ['direct-example', 'outer-example', 'inner-example', 'nested-example'],
        )
        nested = require_resource(template, 'example.nested/WIDGETS')
        self.assertIs(require_property(nested, 'properties', 'enabled'), False)
        self.assertEqual(len(find_resources(template, 'Microsoft.Resources/deployments')), 2)

    def test_missing_and_duplicate_type(self):
        with self.assertRaisesRegex(InspectionError, 'Example.Missing/widgets; found 0'):
            require_resource({'resources': []}, 'Example.Missing/widgets')
        template = {'resources': [
            {'type': 'Example/widgets', 'name': 'first'},
            {'type': 'Example/widgets', 'name': 'second'},
        ]}
        with self.assertRaisesRegex(InspectionError, "found 2.*first.*second"):
            require_resource(template, 'Example/widgets')
        with self.assertRaisesRegex(InspectionError, 'missing a string type'):
            list(walk_resources({'resources': [{'name': 'no-type'}]}))

    def test_json_and_file_errors(self):
        for source in ('{broken', '[]', 'null'):
            with self.subTest(source=source), self.assertRaises(InspectionError):
                parse_template(source)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(InspectionError, 'generate fresh output'):
                load_template(Path(directory) / 'absent.json')

    def test_exact_property_casing(self):
        direct = require_resource(load_template(FIXTURE), 'Example.Direct/widgets')
        self.assertEqual(require_property(direct, 'properties', 'MixedCase'), 'retained')
        with self.assertRaisesRegex(InspectionError, 'properties.mixedcase'):
            require_property(direct, 'properties', 'mixedcase')

    def test_expressions_are_never_evaluated(self):
        nested = require_resource(load_template(FIXTURE), 'Example.Nested/widgets')
        with self.assertRaisesRegex(InspectionError, 'runtimeId: unresolved ARM expression'):
            require_property(nested, 'properties', 'runtimeId')
        self.assertEqual(
            require_property(nested, 'properties', 'runtimeId', literal=False),
            "[reference('example').id]",
        )
        for value in ("[parameters('enabled')]", "[variables('setting')]", "[listKeys('id', 'version')]"):
            with self.subTest(value=value):
                self.assertTrue(is_expression(value))
                with self.assertRaisesRegex(InspectionError, 'unresolved ARM expression'):
                    require_literal({'nested': [value]})
        for value in (True, False, 0, None, 'Disabled', '[[escaped]', {'safe': [1, 'text']}):
            with self.subTest(value=value):
                self.assertEqual(require_literal(value), value)

    def test_unsupported_shapes_fail_instead_of_hiding_resources(self):
        for template in (
            {}, {'resources': {}}, {'resources': [False]},
            {'resources': [{'type': 'Microsoft.Resources/deployments', 'name': 'linked',
                            'properties': {'templateLink': {'uri': 'unused'}}}]},
        ):
            with self.subTest(template=template), self.assertRaises(InspectionError):
                list(walk_resources(template))


if __name__ == '__main__':
    unittest.main()
