from dataclasses import dataclass
from datetime import date
import numpy as np

@dataclass
class Question:
    """One quiz question: an asset, its PM job plan sequence, and where its counter starts."""
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
    """Build a Question from its parts. Just a thin wrapper around the constructor."""
    return Question(
        asset_name=asset_name,
        pm_id=pm_id,
        sequence=sequence,
        last_completed=last_completed,
        start_counter=start_counter
    )

def create_sequence(jobplan_id, frequencies):
    """Turn a list of frequencies into a job plan sequence dict.

    Each frequency gets its own job plan ID and an interval relative
    to the shortest frequency in the list. Raises ValueError if a
    frequency isn't a clean multiple of the shortest one.
    """
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
    """Pick a random asset type and stick the asset number on the end."""
    asset_type = rng.choice(ASSET_TYPES)

    return f"{asset_type}-{asset_number}"

def generate_frequencies(rng):
    """Pick a random base frequency plus a few compatible ones on top of it.

    Compatible just means "divides evenly by the base frequency", so
    they can all share one job plan sequence.
    """
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
    """Pick a random last-completed date between 2020 and 2025."""
    year = int(rng.integers(2020, 2026))
    month = int(rng.integers(1, 13))
    day = int(rng.integers(1, 29))

    return date(year, month, day)

def generate_start_counter(rng):
    """Pick a random starting counter value for the asset."""
    return int(rng.integers(0, 120))

def generate_question(
    rng,
    asset_number,
    pm_number,
    jobplan_number
):
    """Generate one full random question from the given ID numbers."""
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
    """Generate a bank of random questions with unique assets, PM IDs and job plan IDs.

    Pass a seed to get the same bank back every time, which is what
    the tests do.
    """
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