import unicodedata
from collections import defaultdict

from gspread_formatting import format_cell_range, CellFormat, TextFormat


def format_scale(data_records):
    date_scale = next((item['DATA ESCALA'] for item in data_records if item['DATA ESCALA']), None)
    scale = [
        {
            "name": item['ORDEM'].strip("\u2060"),
            "function": item['FUNÇÃO']
        }
        for item in data_records
    ]

    return {
        "date_scale": date_scale,
        "scale": scale
    }

def format_message_scale(obj):
    list_scale = "\n".join(
        f"{i+1}. {item['name']} ({item['function']})"
        for i, item in enumerate(obj['scale'])
    )

    return f"*{obj['date_scale']}* \n{list_scale}"

def format_events(events):
    events_by_date = defaultdict(list)
    for event in events:
        events_by_date[event['Data']].append(f"- *Evento:* {event['Evento']} {'\n *Departamento:*' if event['Departamento'] else ''}")

    result = []
    for data, details in events_by_date.items():
        result.append(f"-> *{data}*")
        result.extend(details)
        result.append("\n")
    return "\n".join(result)

def format_first_register(worksheet):
    fmt = CellFormat(
        textFormat=TextFormat(bold=True),
        horizontalAlignment="CENTER"
    )
    format_cell_range(worksheet, "A1:B1", fmt)

def normalize_string(value):
    """
    Normaliza uma string, removendo acentos e espaços extras.
    :param value: String para normalizar.
    :return: String normalizada, em minúsculas.
    """
    return ''.join(
        c for c in unicodedata.normalize('NFD', value)
        if unicodedata.category(c) != 'Mn'
    ).lower().strip()