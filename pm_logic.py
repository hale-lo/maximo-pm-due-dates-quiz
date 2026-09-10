from datetime import date
from calendar import monthrange

def resolve_job_plan(counter, sequence):
    """Work out which job plan is correct at a given counter value.

    Picks the job plan with the largest interval that divides evenly
    into the counter, since that's the one due at the same time as
    all the smaller ones.
    """
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
    """Add a number of calendar months to a date.

    Sets the day to the last valid day of the target month, so
    31 Jan plus 1 month lands on 28 Feb (or 29 Feb in a leap year)
    instead of throwing an error.
    """
    month = last_completed.month - 1 + frequency_months
    year = last_completed.year + month // 12
    month = month % 12 + 1

    day = min(last_completed.day, monthrange(year, month)[1])

    return date(year, month, day)

def get_base_frequency(sequence):
    """Return the shortest frequency (in months) across a job plan sequence."""
    return min(
        details["months"]
        for details in sequence.values()
    )

def generate_timeline(start_counter, last_completed, sequence, span):
    """Build a list of upcoming PM due dates for a given asset.

    Steps forward one base-frequency period at a time from
    start_counter, working out which job plan is due and when, for
    span periods.
    """
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
    """Score a question based on which attempt got it right.

    3 points on the first try, 2 on the second, 1 on the third,
    0 for a wrong answer or anything past attempt 3.
    """
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