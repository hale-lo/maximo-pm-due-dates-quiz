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

    def test_generate_question_bank_count_and_unique_ids(self):
        questions = generate_question_bank(
            number_of_questions=10,
            seed=42
        )

        self.assertEqual(len(questions), 10)

        asset_numbers = [
            question["asset_name"].split("-")[-1]
            for question in questions
        ]

        pm_ids = [
            question["pm_id"]
            for question in questions
        ]

        jobplan_ids = []

        for question in questions:
            jobplan_ids.extend(
                question["sequence"].keys()
            )

        self.assertEqual(
            len(asset_numbers),
            len(set(asset_numbers))
        )

        self.assertEqual(
            len(pm_ids),
            len(set(pm_ids))
        )

        self.assertEqual(
            len(jobplan_ids),
            len(set(jobplan_ids))
        )