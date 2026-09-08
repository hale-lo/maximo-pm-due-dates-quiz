import unittest
from datetime import date

from question_bank import (
    create_question,
    create_sequence,
    generate_question_bank
)

class TestQuestionBank(unittest.TestCase):
    def test_create_question(self):
        sequence = {
            "JP114301M": {
                "interval": 1,
                "months": 1
            }
        }

        expected = {
            "asset_name": "AHU-1234",
            "pm_id": "PM12345",
            "sequence": sequence,
            "last_completed": date(2025, 12, 1),
            "start_counter": 59
        }

        self.assertEqual(
            create_question(
                asset_name="AHU-1234",
                pm_id="PM12345",
                sequence=sequence,
                last_completed=date(2025, 12, 1),
                start_counter=59
            ),
            expected
        )

    def test_create_sequence_invalid_frequencies(self):
        with self.assertRaises(ValueError):
            create_sequence(
                11430,
                [2, 3]
            )