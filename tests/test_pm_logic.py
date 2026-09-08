import unittest
from datetime import date
from pm_logic import resolve_job_plan
from pm_logic import calculate_next_due_date

class PMLogicTest(unittest.TestCase):
    def test_resolve_job_plan(self):

        sequence_entries = {
            "JP11430A": 1,
            "JP11430": 4
        }

        self.assertEqual(resolve_job_plan(5, sequence_entries), "JP11430A")

    def test_resolve_job_plan_largest(self):

        sequence_entries = {
            "JP11430A": 1,
            "JP11430": 4
        }

        self.assertEqual(resolve_job_plan(8, sequence_entries), "JP11430")

    def test_calculate_next_due_date(self):
        self.assertEqual(calculate_next_due_date(date(2026, 1, 30), 6), date(2026, 7, 30))

    def test_calculate_next_due_date_leap_year(self):
            self.assertEqual(calculate_next_due_date(date(2028, 1, 31), 1), date(2028, 2, 29))

if __name__ == "__main__":
    unittest.main(verbosity=2)