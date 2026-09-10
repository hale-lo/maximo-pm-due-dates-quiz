import csv
import json
import os

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

def save_attempt(player_name, game_id, attempt_started, question_results, total_score):
    try:
        _append_row(
            RESULTS_FILE,
            RESULTS_FIELDNAMES,
            {
                "game_id": game_id,
                "player_name": player_name,
                "total_score": total_score,
                "attempt_started": attempt_started.isoformat()
            }
        )

        for result in question_results:
            _append_row(
                TIMELINE_FILE,
                TIMELINE_FIELDNAMES,
                {
                    "game_id": game_id,
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

def _append_row(filename, fieldnames, row):
    file_exists = os.path.isfile(filename)

    with open(filename, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)
