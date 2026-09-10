from datetime import date
from calendar import monthrange

def resolve_job_plan(counter, sequence):
    best_jobplan = None
    largest_interval = 0

    for jobplan, details in sequence.items():
        interval = details["interval"]

        if counter % interval == 0:
            if interval > largest_interval:
                largest_interval = interval
                best_jobplan = jobplan

    return best_jobplan

def calculate_next_due_date(last_completed, frequency_months):
    month = last_completed.month - 1 + frequency_months
    year = last_completed.year + month // 12
    month = month % 12 + 1

    day = min(last_completed.day, monthrange(year, month)[1])

    return date(year, month, day)

def get_base_frequency(sequence):
    return min(
        details["months"]
        for details in sequence.values()
    )

def generate_timeline(start_counter, last_completed, sequence, span):
    timeline = []
    current_date = last_completed

    frequency_months = get_base_frequency(sequence)

    for i in range(span):

        counter = (start_counter + 1) + i

        jobplan = resolve_job_plan(counter, sequence)

        current_date = calculate_next_due_date(
            current_date,
            frequency_months
        )

        timeline.append({
            "counter": counter,
            "jobplan": jobplan,
            "due_date": current_date
        })

    return timeline

def score_for_attempt(attempt_number, correct):
    if correct:
        match attempt_number:
            case 3:
                return 1
            case 2:
                return 2
            case 1:
                return 3
            case _:
                return 0
    return 0