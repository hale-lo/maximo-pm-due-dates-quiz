import unittest

from validators import (
    validate_name,
    validate_date,
    validate_frequency
)

class TestValidators(unittest.TestCase):
    
    def test_validate_name_valid(self):
        self.assertEqual(
            validate_name("Yui Hale"),
            (True, "")
        )

    def test_validate_name_empty(self):
        self.assertEqual(
            validate_name(""),
            (False, "Name cannot be empty")
        )

    def test_validate_name_whitespace(self):
        self.assertEqual(
            validate_name("   "),
            (False, "Name cannot be empty")
        )

    def test_validate_date_valid(self):
        self.assertEqual(
            validate_date("01/01/2026"),
            (True, "")
        )

    def test_validate_date_invalid_format(self):
        self.assertEqual(
            validate_date("2026-01-31"),
            (False, "Date must be in DD/MM/YYYY format")
        )