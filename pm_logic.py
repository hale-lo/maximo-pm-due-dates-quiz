from datetime import date
from calendar import monthrange

def resolve_job_plan(counter, sequence):
    best_jobplan = None
    largest_interval = 0

    for jobplan, interval in sequence.items():
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