from datetime import date, timedelta

def is_consecutive_day(last_date: date, current_date: date) -> bool:
    return last_date + timedelta(days=1) == current_date
