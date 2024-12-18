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

def update_rotation_scale(data_records):
    data_records.insert(0, data_records.pop())

    for i, data in enumerate(data_records):
        if i == 0:
            # data['FUNÇÃO'] = 'abertura'
            continue
        elif i == 1 or i == 2:
            data['FUNÇÃO'] = 'congregacional'
        elif i == 3:
            data['FUNÇÃO'] = 'harpa'
        elif i == 4:
            data['FUNÇÃO'] = 'oferta'

        if data['ORDEM'].strip() == 'Letícia':
            data['FUNÇÃO'] = 'abertura'
            if i == 3:
                data['FUNÇÃO'] += ' e harpa'

    return data_records

def format_events(events):
    events_by_date = defaultdict(list)
    for event in events:
        events_by_date[event['Data']].append(f"- *Evento:* {event['Evento']}\n   *Departamento:* {event['Departamento']}")

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