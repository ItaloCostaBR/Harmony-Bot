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
        f"{i+1}.⁠ ⁠{item['name']} ({item['function']})"
        for i, item in enumerate(obj['scale'])
    )

    return f"{obj['date_scale']}\n{list_scale}"