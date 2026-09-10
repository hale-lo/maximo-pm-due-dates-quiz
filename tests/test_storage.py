import os
import shutil
import tempfile
import unittest
from datetime import date, datetime
import storage
from storage import (
    Attempt,
    save_attempt,
    load_results,
    load_timeline_entries,
    export_results
)

class StorageTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

        self.original_results_file = storage.RESULTS_FILE
        self.original_timeline_file = storage.TIMELINE_FILE

        storage.RESULTS_FILE = os.path.join(self.temp_dir, "results.csv")
        storage.TIMELINE_FILE = os.path.join(self.temp_dir, "timeline_entries.csv")

    def tearDown(self):
        storage.RESULTS_FILE = self.original_results_file
        storage.TIMELINE_FILE = self.original_timeline_file

        shutil.rmtree(self.temp_dir)

    def test_save_and_load_round_trip(self):
        attempt = Attempt(
            player_name="Test Player",
            game_id="abc123",
            attempt_started=datetime(2026, 1, 1, 9, 30),
            question_results=[
                {
                    "question_number": 1,
                    "asset_name": "AHU-1234",
                    "pm_id": "PM12345",
                    "correct_due_date": date(2026, 2, 1),
                    "correct_frequency": 1,
                    "submitted_due_date": date(2026, 2, 1),
                    "submitted_frequency": 1,
                    "last_completed": date(2026, 1, 1),
                    "start_counter": 5,
                    "sequence": {
                        "JP114301M": {
                            "interval": 1,
                            "months": 1
                        }
                    },
                    "attempts": 1,
                    "correct": True,
                    "score": 3
                }
            ],
            total_score=3
        )

        saved, message = save_attempt(attempt)

        self.assertTrue(saved)
        self.assertEqual(message, "")

        results = load_results()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["game_id"], "abc123")
        self.assertEqual(results[0]["player_name"], "Test Player")
        self.assertEqual(results[0]["total_score"], 3)
        self.assertEqual(
            results[0]["attempt_started"],
            datetime(2026, 1, 1, 9, 30)
        )

        entries = load_timeline_entries()

        self.assertEqual(len(entries), 1)

        entry = entries[0]

        self.assertEqual(entry["game_id"], "abc123")
        self.assertEqual(entry["question_number"], 1)
        self.assertEqual(entry["asset_name"], "AHU-1234")
        self.assertEqual(entry["pm_id"], "PM12345")
        self.assertEqual(entry["correct_due_date"], date(2026, 2, 1))
        self.assertEqual(entry["correct_frequency"], 1)
        self.assertEqual(entry["submitted_due_date"], date(2026, 2, 1))
        self.assertEqual(entry["submitted_frequency"], 1)
        self.assertEqual(entry["last_completed"], date(2026, 1, 1))
        self.assertEqual(entry["start_counter"], 5)
        self.assertEqual(
            entry["sequence"],
            {
                "JP114301M": {
                    "interval": 1,
                    "months": 1
                }
            }
        )
        self.assertEqual(entry["attempts"], 1)
        self.assertTrue(entry["correct"])
        self.assertEqual(entry["score"], 3)

    def test_load_results_missing_file_returns_empty_list(self):
        self.assertEqual(load_results(), [])

    def test_load_timeline_entries_missing_file_returns_empty_list(self):
        self.assertEqual(load_timeline_entries(), [])

    def test_export_results_failure(self):
        with open(storage.RESULTS_FILE, "w", newline="") as file:
            file.write("game_id,player_name,total_score,attempt_started\n")

        exported, message = export_results(
            os.path.join(self.temp_dir, "missing_folder", "export.csv")
        )

        self.assertFalse(exported)
        self.assertIn("Could not export results", message)

    def test_load_results_skips_corrupted_row(self):
        with open(storage.RESULTS_FILE, "w", newline="") as file:
            file.write("game_id,player_name,total_score,attempt_started\n")
            file.write("good1,Good Player,10,2026-01-01T09:30:00\n")
            file.write("bad1,Bad Player,not-a-number,2026-01-01T09:30:00\n")
            file.write("bad2,Bad Player,10,not-a-date\n")

        results = load_results()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["game_id"], "good1")

    def test_load_timeline_entries_skips_corrupted_row(self):
        header = ",".join(storage.TIMELINE_FIELDNAMES)

        good_row = (
            "good1,1,True,3,1,AHU-1234,PM12345,01/02/2026,1,"
            "01/02/2026,1,01/01/2026,5,"
            '"{""JP114301M"": {""interval"": 1, ""months"": 1}}"'
        )

        bad_row_bad_json = (
            "bad1,1,True,3,1,AHU-1234,PM12345,01/02/2026,1,"
            "01/02/2026,1,01/01/2026,5,not-json"
        )

        bad_row_bad_date = (
            "bad2,1,True,3,1,AHU-1234,PM12345,not-a-date,1,"
            "01/02/2026,1,01/01/2026,5,"
            '"{""JP114301M"": {""interval"": 1, ""months"": 1}}"'
        )

        with open(storage.TIMELINE_FILE, "w", newline="") as file:
            file.write(header + "\n")
            file.write(good_row + "\n")
            file.write(bad_row_bad_json + "\n")
            file.write(bad_row_bad_date + "\n")

        entries = load_timeline_entries()

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["game_id"], "good1")

    def test_load_results_all_rows_corrupted_returns_empty_list(self):
        with open(storage.RESULTS_FILE, "w", newline="") as file:
            file.write("game_id,player_name,total_score,attempt_started\n")
            file.write("bad1,Bad Player,not-a-number,not-a-date\n")

        self.assertEqual(load_results(), [])