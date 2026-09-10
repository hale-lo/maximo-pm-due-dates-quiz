from datetime import datetime

def validate_name(name):
    if not name.strip():
        return False, "Name cannot be empty"

    return True, ""

def validate_date(date_string):
    if not date_string.strip():
        return False, "Date cannot be empty"

    try:
        datetime.strptime(date_string, "%d/%m/%Y")
    except ValueError:
        return False, "Date must be in DD/MM/YYYY format"

    return True, ""

def validate_frequency(frequency_text, valid):
    if not frequency_text:
        return False, "Frequency cannot be empty"

    try:
        frequency = int(frequency_text)
    except ValueError:
        return False, "Frequency must be a whole number"

    if frequency not in valid:
        return False, "Frequency is not valid"

    return True, ""