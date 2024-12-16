from datetime import datetime, timedelta


def is_past_date(date_str):
    try:
        input_date = datetime.strptime(date_str, "%d/%m/%Y").date()
        current_date = datetime.now().date()
        return current_date > input_date
    except ValueError:
        print("Formato de data inválido. Use DD/MM/AAAA.")
        return False

def next_sunday():
    currant_date = datetime.now().date()
    days_from_sunday = 6 - currant_date.weekday()
    if days_from_sunday < 0:
        days_from_sunday += 7
    return currant_date + timedelta(days=days_from_sunday)