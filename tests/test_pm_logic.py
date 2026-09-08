import unittest
from datetime import date
from pm_logic import resolve_job_plan
from pm_logic import calculate_next_due_date
from pm_logic import generate_timeline
from pm_logic import score_for_attempt

class PMLogicTest(unittest.TestCase):
    def test_resolve_job_plan(self):

        sequence_entries = {
            "JP114301M": {
                "interval": 1,
                "months": 1
            },
            "JP114306M": {
                "interval": 6,
                "months": 6
            }
        }

        self.assertEqual(
            resolve_job_plan(5, sequence_entries), 
            "JP114301M"
        )

    def test_resolve_job_plan_largest(self):

        sequence_entries = {
            "JP114301M": {
                "interval": 1,
                "months": 1
            },
            "JP114306M": {
                "interval": 6,
                "months": 6
            }
        }

        self.assertEqual(
            resolve_job_plan(12, sequence_entries),
            "JP114306M"
        )

    def test_calculate_next_due_date(self):
        self.assertEqual(
            calculate_next_due_date(date(2026, 1, 30), 6), 
            date(2026, 7, 30)
        )

    def test_calculate_next_due_date_leap_year(self):
        self.assertEqual(
            calculate_next_due_date(date(2028, 1, 31), 1), 
            date(2028, 2, 29)
        )

    def test_calculate_next_due_date_december_boundry(self):
        self.assertEqual(
            calculate_next_due_date(date(2026, 1, 31), 11), 
            date(2026, 12, 31)
        )

    def test_generate_timeline(self):

        sequence_entries = {
            "JP114301M": {
                "interval": 1,
                "months": 1
            },
            "JP114306M": {
                "interval": 6,
                "months": 6
            },
            "JP114305Y": {
                "interval": 60,
                "months": 60
            }
        }

        expected = [
            {
                "counter": 60,
                "jobplan": "JP114305Y",
                "due_date": date(2026, 1, 1)
            },
            {
                "counter": 61,
                "jobplan": "JP114301M",
                "due_date": date(2026, 2, 1)
            },
            {
                "counter": 62,
                "jobplan": "JP114301M",
                "due_date": date(2026, 3, 1)
            },
            {
                "counter": 63,
                "jobplan": "JP114301M",
                "due_date": date(2026, 4, 1)
            },
            {
                "counter": 64,
                "jobplan": "JP114301M",
                "due_date": date(2026, 5, 1)
            },
            {
                "counter": 65,
                "jobplan": "JP114301M",
                "due_date": date(2026, 6, 1)
            },
            {
                "counter": 66,
                "jobplan": "JP114306M",
                "due_date": date(2026, 7, 1)
            },
            {
                "counter": 67,
                "jobplan": "JP114301M",
                "due_date": date(2026, 8, 1)
            },
            {
                "counter": 68,
                "jobplan": "JP114301M",
                "due_date": date(2026, 9, 1)
            }
        ]

        self.assertEqual(
            generate_timeline(
                start_counter=59,
                last_completed=date(2025, 12, 1),
                sequence=sequence_entries,
                span=9
            ),
            expected
        )

    def test_score_for_attempt_success_attempt_1(self):
        self.assertEqual(
            score_for_attempt(1, True),
            3
        )

    def test_score_for_attempt_success_attempt_2(self):
        self.assertEqual(
            score_for_attempt(2, True),
            2
        )

    def test_score_for_attempt_success_attempt_3(self):
        self.assertEqual(
            score_for_attempt(3, True),
            1
        )

    def test_score_for_attempt_fail(self):
        self.assertEqual(
            score_for_attempt(3, False),
            0
    )

if __name__ == "__main__":
    unittest.main(verbosity=2)