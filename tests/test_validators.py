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