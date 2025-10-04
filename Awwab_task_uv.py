import earthaccess

from datetime import datetime

def get_start_end_of_day(user_input):
    """
    Takes a datetime string and returns the start and end of that day.

    Args:
        user_input (str): Date/time in format "YYYY-MM-DD HH:MM"

    Returns:
        tuple: (start_of_day, end_of_day)
    """
    dt = datetime.strptime(user_input, "%Y-%m-%d %H:%M")
    start_of_day = dt.replace(hour=0, minute=0, second=0)
    end_of_day = dt.replace(hour=23, minute=59, second=59)
    return start_of_day, end_of_day

#How to use 

start, end = get_start_end_of_day("2025-10-04 14:30")

print("Start of day:", start)
print("End of day:", end)
