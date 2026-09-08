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