import csv
import json
import os
import shutil
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Attempt:
    """One full quiz playthrough: who played, when, and how it went."""
    player_name: str
    game_id: str
    attempt_started: datetime
    question_results: list
    total_score: int

RESULTS_FILE = "results.csv"
TIMELINE_FILE = "timeline_entries.csv"

RESULTS_FIELDNAMES = [
    "game_id",
    "player_name",
    "total_score",
    "attempt_started"
]

TIMELINE_FIELDNAMES = [
    "game_id",
    "question_number",
    "correct",
    "score",
    "attempts",
    "asset_name",
    "pm_id",
    "correct_due_date",
    "correct_frequency",
    "submitted_due_date",
    "submitted_frequency",
    "last_completed",
    "start_counter",
    "sequence"
]

def save_attempt(attempt):
    """Append an Attempt to results.csv and its questions to timeline_entries.csv.

    Returns a (success, message) tuple rather than raising, so the
    caller can show the user a friendly error if the write fails.
    """
    try:
        _append_row(
            RESULTS_FILE,
            RESULTS_FIELDNAMES,
            {
                "game_id": attempt.game_id,
                "player_name": attempt.player_name,
                "total_score": attempt.total_score,
                "attempt_started": attempt.attempt_started.isoformat()
            }
        )

        for result in attempt.question_results:
            _append_row(
                TIMELINE_FILE,
                TIMELINE_FIELDNAMES,
                {
                    "game_id": attempt.game_id,
                    "question_number": result["question_number"],
                    "correct": result["correct"],
                    "score": result["score"],
                    "attempts": result["attempts"],
                    "asset_name": result["asset_name"],
                    "pm_id": result["pm_id"],
                    "correct_due_date": result["correct_due_date"].strftime("%d/%m/%Y"),
                    "correct_frequency": result["correct_frequency"],
                    "submitted_due_date": result["submitted_due_date"].strftime("%d/%m/%Y"),
                    "submitted_frequency": result["submitted_frequency"],
                    "last_completed": result["last_completed"].strftime("%d/%m/%Y"),
                    "start_counter": result["start_counter"],
                    "sequence": json.dumps(result["sequence"])
                }
            )

        return True, ""

    except OSError as error:
        return False, f"Could not save results: {error}"

def load_results():
    """Load every saved attempt from results.csv.

    Returns an empty list if the file doesn't exist yet. Any row
    that fails to parse (a corrupted or partially-written line) gets
    skipped and logged rather than blowing up the whole load.
    """
    try:
        with open(RESULTS_FILE, mode="r", newline="") as file:
            reader = csv.DictReader(file)

            results = []

            for row in reader:
                try:
                    row["total_score"] = int(row["total_score"])
                    row["attempt_started"] = datetime.fromisoformat(row["attempt_started"])
                except (KeyError, TypeError, ValueError) as error:
                    print(f"Skipping corrupted row in {RESULTS_FILE}: {error}")
                    continue

                results.append(row)

            return results

    except FileNotFoundError:
        return []

def load_timeline_entries():
    """Load every saved question result from timeline_entries.csv.

    Same deal as load_results: missing file returns an empty list,
    and a corrupted row gets skipped and logged rather than
    crashing the load.
    """
    try:
        with open(TIMELINE_FILE, mode="r", newline="") as file:
            reader = csv.DictReader(file)

            entries = []

            for row in reader:
                try:
                    row["question_number"] = int(row["question_number"])
                    row["correct"] = row["correct"] == "True"
                    row["score"] = int(row["score"])
                    row["attempts"] = int(row["attempts"])
                    row["correct_frequency"] = int(row["correct_frequency"])
                    row["submitted_frequency"] = int(row["submitted_frequency"])
                    row["start_counter"] = int(row["start_counter"])
                    row["sequence"] = json.loads(row["sequence"])
                    row["correct_due_date"] = datetime.strptime(row["correct_due_date"], "%d/%m/%Y").date()
                    row["submitted_due_date"] = datetime.strptime(row["submitted_due_date"], "%d/%m/%Y").date()
                    row["last_completed"] = datetime.strptime(row["last_completed"], "%d/%m/%Y").date()
                except (KeyError, TypeError, ValueError) as error:
                    print(f"Skipping corrupted row in {TIMELINE_FILE}: {error}")
                    continue

                entries.append(row)

            return entries

    except FileNotFoundError:
        return []

def export_results(destination_path):
    """Copy results.csv to wherever the user picked in the save dialog.

    Returns a (success, message) tuple, same as save_attempt.
    """
    try:
        shutil.copyfile(RESULTS_FILE, destination_path)

        return True, ""

    except OSError as error:
        return False, f"Could not export results: {error}"

def _append_row(filename, fieldnames, row):
    """Append one row to a CSV, writing the header first if the file is new."""
    file_exists = os.path.isfile(filename)

    with open(filename, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)
