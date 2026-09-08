from datetime import date

def validate_name(name):
    if not name.strip():
        return False, "Name cannot be empty"

    return True, ""

def validate_date(date_string):
    return None

def validate_frequency(frequency, valid):
    return None