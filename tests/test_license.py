"""The project's MIT license is independent of optional release documentation."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class LicenseTests(unittest.TestCase):
    def test_existing_mit_license_is_present(self):
        source = (ROOT / 'LICENSE').read_text(encoding='utf-8')
        self.assertTrue(source.startswith('MIT License\n'))
        self.assertIn('Copyright (c) 2026 Kelly Fleming', source)
        self.assertIn('Permission is hereby granted, free of charge', source)
        self.assertIn('THE SOFTWARE IS PROVIDED "AS IS"', source)


if __name__ == '__main__':
    unittest.main()
