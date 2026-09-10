from dataclasses import dataclass
from datetime import date
import numpy as np

@dataclass
class Question:
    asset_name: str
    pm_id: str
    sequence: dict
    last_completed: date
    start_counter: int

ASSET_TYPES = [
    "AHU",
    "PUMP",
    "FAN",
    "CHILLER",
    "BOILER"
]

FREQUENCIES = [1, 2, 3, 6, 12, 24, 60]

FREQUENCY_LABELS = {
    1: "1M",
    2: "2M",
    3: "3M",
    6: "6M",
    12: "1Y",
    24: "2Y",
    60: "5Y"
}

def create_question(
    asset_name,
    pm_id,
    sequence,
    last_completed,
    start_counter
):
    return Question(
        asset_name=asset_name,
        pm_id=pm_id,
        sequence=sequence,
        last_completed=last_completed,
        start_counter=start_counter
    )

def create_sequence(jobplan_id, frequencies):
    sequence = {}

    base_frequency = min(frequencies)

    for months in frequencies:
        if months % base_frequency != 0:
            raise ValueError(
                f"{months} is not a multiple of {base_frequency}"
            )

        interval = months // base_frequency
        frequency_label = FREQUENCY_LABELS[months]

        jobplan = f"JP{jobplan_id}{frequency_label}"

        sequence[jobplan] = {
            "interval": interval,
            "months": months
        }

    return sequence

def generate_asset_name(rng, asset_number):
    asset_type = rng.choice(ASSET_TYPES)

    return f"{asset_type}-{asset_number}"

def generate_frequencies(rng):
    possible_base_frequencies = [1, 2, 3, 6, 12]

    base_frequency = int(
        rng.choice(possible_base_frequencies)
    )

    valid_frequencies = [
        frequency
        for frequency in FREQUENCIES
        if frequency % base_frequency == 0
    ]

    number_of_frequencies = int(
        rng.integers(
            3,
            len(valid_frequencies) + 1
        )
    )

    other_frequencies = rng.choice(
        valid_frequencies[1:],
        size=number_of_frequencies - 1,
        replace=False
    )

    frequencies = [base_frequency] + [
        int(frequency)
        for frequency in other_frequencies
    ]

    frequencies.sort()

    return frequencies

def generate_last_completed(rng):
    year = int(rng.integers(2020, 2026))
    month = int(rng.integers(1, 13))
    day = int(rng.integers(1, 29))

    return date(year, month, day)

def generate_start_counter(rng):
    return int(rng.integers(0, 120))

def generate_question(
    rng,
    asset_number,
    pm_number,
    jobplan_number
):
    asset_name = generate_asset_name(
        rng,
        asset_number
    )

    pm_id = f"PM{pm_number}"

    frequencies = generate_frequencies(rng)

    sequence = create_sequence(
        jobplan_number,
        frequencies
    )

    last_completed = generate_last_completed(rng)

    start_counter = generate_start_counter(rng)

    return create_question(
        asset_name,
        pm_id,
        sequence,
        last_completed,
        start_counter
    )

def generate_question_bank(
    number_of_questions=10,
    seed=None
):
    rng = np.random.default_rng(seed)

    asset_numbers = rng.choice(
        np.arange(1000, 10000),
        size=number_of_questions,
        replace=False
    )

    pm_numbers = rng.choice(
        np.arange(10000, 100000),
        size=number_of_questions,
        replace=False
    )

    jobplan_numbers = rng.choice(
        np.arange(10000, 100000),
        size=number_of_questions,
        replace=False
    )

    questions = []

    for i in range(number_of_questions):
        question = generate_question(
            rng,
            asset_number=int(asset_numbers[i]),
            pm_number=int(pm_numbers[i]),
            jobplan_number=int(jobplan_numbers[i])
        )

        questions.append(question)

    return questions