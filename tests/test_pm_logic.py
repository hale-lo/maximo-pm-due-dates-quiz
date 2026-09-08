import unittest
from pm_logic import resolve_job_plan

class PMLogicTest(unittest.TestCase):
    def test_resolve_job_plan(self):

        sequence_entries = [{"jobplan": "JP11430A", "interval": 1}, {"jobplan": "JP11430", "interval": 4}]
        self.assertEqual(resolve_job_plan(5, sequence_entries), "JP11430A")

    def test_resolve_job_plan_largest(self):

        sequence_entries = [{"jobplan": "JP11430A", "interval": 1}, {"jobplan": "JP11430", "interval": 4}]
        self.assertEqual(resolve_job_plan(8, sequence_entries), "JP11430")

if __name__ == "__main__":
    unittest.main(verbosity=2)