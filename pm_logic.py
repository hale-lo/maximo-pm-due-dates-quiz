from datetime import date

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
    return None