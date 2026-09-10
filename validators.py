from datetime import datetime

def validate_name(name):
    """Check the player's name isn't blank or just whitespace.

    Returns a (valid, message) tuple, same pattern as the other
    validators in this file.
    """
    if not name.strip():
        return False, "Name cannot be empty"

    return True, ""

def validate_date(date_string):
    """Check a typed date is non-empty and matches DD/MM/YYYY."""
    if not date_string.strip():
        return False, "Date cannot be empty"

    try:
        datetime.strptime(date_string, "%d/%m/%Y")
    except ValueError:
        return False, "Date must be in DD/MM/YYYY format"

    return True, ""

def validate_frequency(frequency_text, valid):
    """Check a submitted frequency is a whole number from the valid list."""
    if not frequency_text:
        return False, "Frequency cannot be empty"

    try:
        frequency = int(frequency_text)
    except ValueError:
        return False, "Frequency must be a whole number"

    if frequency not in valid:
        return False, "Frequency is not valid"

    return True, ""