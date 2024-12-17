import os
import threading
import time

import gspread
import schedule
import telebot
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from telebot.types import Message

from utils.formats import format_scale, format_message_scale, update_rotation_scale, format_events
from utils.validates import is_past_date, next_sunday

load_dotenv()

API_TOKEN = os.getenv("TOKEN_BOT")
CHAT_ID = os.getenv("CHAT_ID")
SHEET_CREDENTIALS_FILE = os.getenv("SHEET_CREDENTIALS_FILE")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(SHEET_CREDENTIALS_FILE, scope)
client = gspread.authorize(credentials)

message_default = ("\n\nSeu assistente pessoal para te ajudar com as escalas, eventos e repertórios de forma simples e eficiente!"
                   "\n✨ Como posso lhe ajudar?"
                   "\n\n ⌨️ Digite ou 👆 clique no comando que deseja.\n"
                   "\n/start ou /help para visualizar os comandos."
                   "\n/escala para visualizar a escala do domingo."
                   "\n/eventos para visualizar os eventos especiais do mês."
                   "\n/repertorio para acessar a playlist de domingo."
                   "\n\nEstou sempre afinado e pronto para ajudar! 🎸")
title_topics = {
    3: "MULTITRACKS 🎶",
    4: "MP3 🎶",
    5: "FOTOS 📷",
    9: "ESTUDOS 📚",
    116: "Continuos Pad 🎶",
}

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

# bot.send_message(CHAT_ID, "🎵 Graça e Paz! HarmonyBot agradecendo a oportunidade! 🎵 "
#                           "\n\n ⌨️ Digite /start ou /help e partiu.")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🎵 Graça e Paz! Eu sou o HarmonyBot! 🎵 "+message_default)

@bot.message_handler(commands=['escala'])
def scale(message):
    sheet = format_scale(get_all_content_sheet(2))
    date_scale = sheet['date_scale']

    if is_past_date(date_scale):
        if update_scale():
            sheet = format_scale(get_all_content_sheet(2))

    bot.reply_to(message, "🎵 Aqui está a ESCALA! 🎵 "
                          f"\n\n {format_message_scale(sheet)}")

@bot.message_handler(commands=['eventos'])
def scale(message):
    sheet = get_all_content_sheet(1)
    bot.reply_to(message, "🎵 Aqui estão os EVENTOS importantes! 🎵 "
                          f"\n\n {format_events(sheet)}")

@bot.message_handler(commands=['repertorio'])
def scale(message):
    bot.reply_to(message, "🎵 Aqui está a PLAYLIST! 🎵 "
                          f"\n\n 🎶 https://www.youtube.com/watch?v=S1ziUJSxk2w&list=PLOMUauEK3yzW9gwXRBeyaP6omXz1eCLGz")

@bot.message_handler(content_types=["new_chat_members"])
def welcome_new_member(message):
    for new_member in message.new_chat_members:
        user_name = new_member.first_name

        bot.send_message(message.chat.id, f"🔥 A paz do Senhor, *{user_name}*! 🔥"
                                          f"\nSeja muito bem-vindo ao grupo *{message.chat.title}* ! Que o Senhor te abençoe e te fortaleça nesta jornada. Aqui, *louvamos*, *servimos* e *crescemos* juntos, porque “quão bom e quão suave é que os irmãos vivam em união!” *(Salmos 133:1)*. 🎶"
                                          "\n\n🎵 Prepare-se para adorar e servir com alegria! 🎸"
                                          "\nO *HarmonyBot* está aqui para organizar *escalas*, *eventos* e *repertórios*, para que tudo seja feito com *harmonia e excelência*!"
                                          "\n\nDeus te abençoe grandemente! 🙌")

@bot.message_handler(func=lambda message: message.message_thread_id is not None)
def watch_topics(message: Message):
    thread_id = message.message_thread_id
    topic_name = title_topics.get(thread_id, "Tópico desconhecido")
    user = message.from_user.full_name

    message = (
        f"🔔 *Atualização no Tópico:* {topic_name}\n"
        f"👤 *Irmã(o):* {user}\n"
    )

    bot.send_message(CHAT_ID, "🔥 TEERRRAAAA! 🔥 "
                              f"\n\n {message}")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    try:
        user_first_name = str(message.from_user.first_name)
        bot.reply_to(message, f"Paz, {user_first_name}! Você disse: {message.text}"
                              f"{message_default}")
    except Exception as e:
        bot.reply_to(message, f"Ocorreu um erro: {e}")

def automatic_message(custom_message = None):
    message = ("🔥 *Atenção, irmãos!* 🔥"
               "\n\n“Desperta, ó tu que dormes!” (*Efésios 5:14*)"
               "\nVamos ficar *atentos* e firmes, porque a obra do Senhor requer *compromisso* e *excelência*! 🙌"
               f"\n\n{custom_message}"
               "\n\nQuem está junto, diga GLÓRIA! ✨🔥")
    bot.send_message(CHAT_ID, message)

def cron_messages():
    schedule.every().monday.at("20:00").do(lambda: automatic_message("🎶 *Revisem as escalas, escolham os hinos e estejam prontos para o louvor!* 🎶"
                                                             "\nPois *“tudo quanto fizerdes, fazei-o de todo o coração, como ao Senhor, e não aos homens.”* (Colossenses 3:23)"))

    schedule.every().wednesday.at("20:00").do(lambda: automatic_message("*“Tudo tem o seu tempo determinado, e há tempo para todo o propósito debaixo do céu.”* (Eclesiastes 3:1)"
                                                                "\nO tempo chegou, e o *hino ainda não foi escolhido!* 🎶"
                                                                "\n*Lembre-se:* o Senhor merece nossa dedicação e prontidão. Não deixe a oportunidade passar, pois o louvor abre os céus e prepara o coração! 🙌"
                                                                "\n*Escolha logo o seu hino, pois o culto não pode parar e a adoração precisa subir como um incenso suave ao Senhor!* 🔥"))
    schedule.every().friday.at("18:00").do(lambda: automatic_message("*“Procura apresentar-te a Deus aprovado, como obreiro que não tem de que se envergonhar, que maneja bem a palavra da verdade.”* (2 Timóteo 2:15)"
                                                             "\nNão se esqueçam de estudar e se preparar com dedicação!"
                                                             "\nSeja o louvor, a Palavra ou o instrumento, *façamos tudo com excelência para o Senhor*. 🎶🙌"
                                                             "\nLembrem-se: *“O Espírito Santo unge o preparo, não a preguiça!”* 🔥"
                                                             "\nVamos buscar mais, crescer mais e honrar a obra do Pai!"))
    schedule.every().saturday.at("17:00").do(lambda: automatic_message("Não esqueçam de se consagrar, pois a obra do Senhor exige santidade e compromisso!"
                                                               "\n*“Santificai-vos, porque amanhã o Senhor fará maravilhas no meio de vós.”* (Josué 3:5)"
                                                               "\nA consagração é a chave para que o poder de Deus se manifeste através de nós. Sem oração e santidade, o altar fica vazio e a unção não desce. 🙌"
                                                               "\n*Preparem-se! O Senhor merece o nosso melhor: corpo, alma e espírito em consagração*"
                                                               "\nVamos buscar, orar e jejuar, porque grande será a obra! 🔥"))
    # schedule.every().tuesday.at("13:14").do(lambda: automatic_message("13:14"))

    while True:
        schedule.run_pending()  # Check if there are any scheduled tasks
        time.sleep(1)

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
    print("HarmonyBot running...")
    schedule_threads = threading.Thread(target=cron_messages)
    schedule_threads.start()
    bot.polling()

if __name__ == '__main__':
    main()