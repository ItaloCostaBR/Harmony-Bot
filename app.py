import os
from datetime import datetime

import gspread
import telebot
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

from utils.formats import format_scale, format_message_scale, update_rotation_scale
from utils.validates import is_past_date, next_sunday

load_dotenv()

API_TOKEN = os.getenv("TOKEN_BOT")
CHAT_ID = os.getenv("CHAT_ID")
SHEET_CREDENTIALS_FILE = os.getenv("SHEET_CREDENTIALS_FILE")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")

bot = telebot.TeleBot(API_TOKEN, parse_mode=None)
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(SHEET_CREDENTIALS_FILE, scope)
client = gspread.authorize(credentials)

# Função para buscar dados no Google Sheets
def get_all_columns_data_sheet(idx_tab = 0, data = None):
    try:
        sheet = client.open(SPREADSHEET_NAME).get_worksheet(idx_tab)
        records = sheet.get_all_records()
        for columns in records:
            if data is not None:
                if columns['Data'] == data:
                    return columns
            else:
                return columns
        return None
    except Exception as e:
        return f"Erro ao acessar a planilha: {e}"

def get_all_content_sheet(idx_tab = 0):
    try:
        sheet = client.open(SPREADSHEET_NAME).get_worksheet(idx_tab)
        records = sheet.get_all_records()
        return records
    except Exception as e:
        return f"Erro ao acessar a planilha: {e}"

def update_scale():
    try:
        data_sheet = client.open(SPREADSHEET_NAME).get_worksheet(2)
        sheet = get_all_content_sheet(2)
        rotation = update_rotation_scale(sheet)

        for data in rotation:
            data['DATA ESCALA'] = ''

        rotation[0]['DATA ESCALA'] = next_sunday().strftime("%d/%m/%Y")
        data_updated = [[data['ORDEM'], data['FUNÇÃO'], data['DATA ESCALA']] for data in rotation]

        data_sheet.update(values=data_updated, range_name="A2:C6")

        return True

    except Exception as e:
        return f"Erro ao atualizar a escala: {e}"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🎵 Graça e Paz! Eu sou o HarmonyBot! 🎵 "
                          "\n\nSeu assistente pessoal para te ajudar com as escalas, eventos e repertórios de forma simples e eficiente!"
                          "\n✨ Como posso lhe ajudar?"
                          "\n\n ⌨️ Digite ou 👆 clique no comando que deseja.\n"
                          "\n/start ou /help para visualizar os comandos."
                          "\n/escala para visualizar a escala do domingo."
                          "\n/eventos para visualizar os eventos especiais do mês."
                          "\n/repertorio para acessar a playlist de domingo."
                          "\n\nEstou sempre afinado e pronto para ajudar! 🎸")
    # bot.reply_to(message, "Olá! Envie uma data no formato DD/MM/AAAA para consultar no calendário.")

@bot.message_handler(commands=['escala'])
def scale(message):
    sheet = format_scale(get_all_content_sheet(2))
    date_scale = sheet['date_scale']

    if is_past_date(date_scale):
        if update_scale():
            sheet = format_scale(get_all_content_sheet(2))

    bot.reply_to(message, "🎵 Aqui está a ESCALA! 🎵 "
                          f"\n\n {format_message_scale(sheet)}")

@bot.message_handler(commands=['repertorio'])
def scale(message):
    bot.reply_to(message, "🎵 Aqui está a PLAYLIST! 🎵 "
                          f"\n\n 🎶 https://www.youtube.com/watch?v=S1ziUJSxk2w&list=PLOMUauEK3yzW9gwXRBeyaP6omXz1eCLGz")

# Tratamento de mensagens com datas
@bot.message_handler(func=lambda message: True)
def consultar_data(message):
    try:
        # # Valida e formata a data
        # data_input = message.text.strip()
        # data_formatada = datetime.strptime(data_input, "%d/%m/%Y").strftime("%d/%m/%Y")
        #
        # # Busca na planilha
        # resultado = get_all_columns_data_sheet(data_formatada)
        # if resultado:
        #     resposta = f"Informações para {data_formatada}:\n"
        #     for chave, valor in resultado.items():
        #         resposta += f"- {chave}: {valor}\n"
        #     bot.reply_to(message, resposta)
        # else:
        #     bot.reply_to(message, f"Não há registros para a data {data_formatada}.")
        send_welcome(message)
    # except ValueError:
    #     bot.reply_to(message, "Por favor, envie uma data válida no formato DD/MM/AAAA.")
    except Exception as e:
        bot.reply_to(message, f"Ocorreu um erro: {e}")

def check_authenticated():
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(SHEET_CREDENTIALS_FILE, scope)
        client = gspread.authorize(credentials)
        print(f"Autenticado com sucesso! {client}")
    except Exception as e:
        print(f"Erro ao autenticar: {e}")

def main():
    os.system('clear')
    # check_authenticated()
    # Inicia o bot
    print("Bot em execução...")
    bot.polling()

if __name__ == '__main__':
    main()