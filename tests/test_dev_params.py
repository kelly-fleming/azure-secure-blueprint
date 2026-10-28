"""Source checks for the fictional example; not a Bicep parser or secret scanner."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DevParameterTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / 'params/dev.bicepparam').read_text(encoding='utf-8')

    def test_binding_and_explicit_interface(self):
        self.assertRegex(self.source, r"(?m)^using\s+'\.\./infra/main\.bicep'\s*$")
        names = re.findall(r'^param\s+(\w+)\s*=', self.source, re.M)
        expected = {'environment', 'location', 'projectPrefix', 'uniqueSuffix', 'appServicePlanSku', 'tags'}
        self.assertEqual(set(names), expected)
        self.assertEqual(len(names), len(expected), 'Duplicate parameter assignment')
        for assignment in ("environment = 'dev'", "location = 'eastus'", "appServicePlanSku = 'B1'"):
            self.assertIn('param ' + assignment, self.source)

    def test_example_names_fit_contract(self):
        prefix = re.search(r"(?m)^param projectPrefix = '([a-z0-9]{2,6})'$", self.source)
        suffix = re.search(r"(?m)^param uniqueSuffix = '([a-z0-9]{6,12})'$", self.source)
        self.assertIsNotNone(prefix, 'Prefix must be lowercase ASCII alphanumeric within bounds')
        self.assertIsNotNone(suffix, 'Suffix must be lowercase ASCII alphanumeric within bounds')
        self.assertRegex(prefix[1] + 'dev' + suffix[1], r'^[a-z0-9]{3,24}$')
        # This checks syntax only; it never asserts global name availability.

    def test_no_identifiers_or_secret_material(self):
        self.assertNotRegex(self.source, r'(?i)\b(?:password|secret|token|credential|connectionstring|accountkey|clientid|tenantid|subscriptionid)\b\s*[:=]')
        self.assertNotRegex(self.source, r'(?i)\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b')
        self.assertNotRegex(self.source, r'(?i)/subscriptions/|/resourcegroups/|\.onmicrosoft\.com|-----BEGIN|AccountKey\s*=|SharedAccessSignature\s*=|[?&]sig=')
        self.assertNotRegex(self.source, r'(?i)\b(?:changeme|replace[_-]?me|your[_-]?(?:secret|password|token))\b')
        self.assertNotRegex(self.source, r'[^\s\x27]+@[^\s\x27]+\.[a-zA-Z]{2,}')
        keys = re.findall(r'^\s+(\w+):', self.source, re.M)
        self.assertEqual(set(keys), {'environment', 'project', 'purpose'})
        self.assertIn("project: 'fictional-blueprint'", self.source)
        self.assertIn("purpose: 'source-example'", self.source)


if __name__ == '__main__':
    unittest.main()
