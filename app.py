import os
import threading
import time

import gspread
import schedule
import telebot
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from telebot.types import Message

from utils.formats import format_scale, format_message_scale, format_events, \
    format_first_register, normalize_string
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

message_commands = ("\n\nSeu assistente pessoal para te ajudar com as escalas, eventos e repertórios de forma simples e eficiente!"
                    "\n✨ Como posso lhe ajudar?"
                    "\n\n ⌨️ Digite ou 👆 clique no comando que deseja.\n"
                    "\n/start ou /help para visualizar os comandos."
                    "\n/escala para visualizar a escala do domingo."
                    "\n/eventos para visualizar os eventos especiais do mês."
                    "\n/repertorio para acessar a playlist de domingo."
                    "\n/minhamatricula para listar sua matrícula."
                    "\n/criarmeubancoderepertorio para criar sua lista de músicas/tons."
                    "\n/addrepertorio para adicionar um hino ao seu repertório."
                    "\n/atualizarrepertorio para atualizar o tom de um hino no seu repertório."
                    "\n/qualmeutom para saber o tom de um hino no seu repertório."
                    "\n\nEstou sempre afinado e pronto para ajudar! 🎸")
message_create_repertory = ("⚠️ *Atenção, servo(a) de Deus!* ⚠️"
                            "\n\n*Você precisa criar seu banco de repertório.*"
                            "\n ⌨️ Digite ou 👆 clique no comando: /criarmeubancoderepertorio")
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
        sheet = data_sheet.get_all_records()

        first = sheet.pop(0)
        sheet.append(first)

        for i, data in enumerate(sheet):

            if i == 0:
                data['FUNÇÃO'] = 'abertura'
            elif i in (1, 2):
                data['FUNÇÃO'] = 'congregacional'
            elif i == 3:
                data['FUNÇÃO'] = 'harpa'
            elif i == 4:
                data['FUNÇÃO'] = 'oferta'

            data['DATA ESCALA'] = next_sunday().strftime('%d/%m/%Y') if i == 0 else None


        data_sheet.update([list(data.values()) for data in sheet], 'A2')

        return True

    except Exception as e:
        return f"Erro ao atualizar a escala: {e}"

# bot.send_message(CHAT_ID, "🎵 Graça e Paz! HarmonyBot agradecendo a oportunidade! 🎵 "
#                           "\n\n ⌨️ Digite /start ou /help e partiu.")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🎵 Graça e Paz! Eu sou o HarmonyBot! 🎵 "+message_commands)

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
def events(message):
    sheet = get_all_content_sheet(1)
    bot.reply_to(message, "🎵 Aqui estão os EVENTOS importantes! 🎵 "
                          f"\n\n {format_events(sheet)}")

@bot.message_handler(commands=['repertorio'])
def repertory(message):
    bot.reply_to(message, "🎵 Aqui está a PLAYLIST! 🎵 "
                          f"\n\n 🎶 https://www.youtube.com/watch?v=S1ziUJSxk2w&list=PLOMUauEK3yzW9gwXRBeyaP6omXz1eCLGz")

@bot.message_handler(commands=['minhamatricula'])
def my_id(message):
    user_id = message.from_user.id
    name = message.from_user.first_name

    bot.reply_to(message, f"🔥 A paz do Senhor, *{name}*! 🔥"
                          f"\n\n 🔑 Matrícula: {user_id}")

@bot.message_handler(commands=['criarmeubancoderepertorio'])
def register(message):
    user_id = message.from_user.id
    register_tab = create_tab_user(user_id)

    if register_tab:
        response = ("*“Assim já não sois estrangeiros, nem forasteiros, mas concidadãos dos santos e da família de Deus.”* (Efésios 2:19)"
                    "\n\n*Você foi registrado com sucesso!* 🎉 Que sua vida seja um instrumento de honra e louvor na obra do Senhor.")
    else:
        response = ("⚠️ *Atenção, servo(a) de Deus!* ⚠️"
                    "\n\n*Você já está registrado* no *Livro da Vida*.")

    bot.reply_to(message, response)

@bot.message_handler(commands=['addrepertorio'])
def add_repertory(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    not_register = check_is_not_register(user_id)

    if not_register:
        response = message_create_repertory
    else:
        response = (f"🔥 A paz do Senhor, *{name}*! 🔥"
                    "\n\nPara adicionar um hino ao seu repertório, envie uma frase nesse formato:"
                    "\n*adicionar: NOME DO LOUVOR,TOM*"
                    "\n*Ex:* adicionar: Agnus Dei,F#")

    bot.reply_to(message, response)

@bot.message_handler(commands=['atualizarrepertorio'])
def change_repertory(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    not_register = check_is_not_register(user_id)

    if not_register:
        response = message_create_repertory
    else:
        response = (f"🔥 A paz do Senhor, *{name}*! 🔥"
                    "\n\nPara atualizar o tom de um hino no seu repertório, envie uma frase nesse formato:"
                    "\n*atualizar: NOME DO LOUVOR,NOVOTOM*"
                    "\n*Ex:* atualizar: Agnus Dei,F#")

    bot.reply_to(message, response)

@bot.message_handler(commands=['qualmeutom'])
def get_my_tone(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    not_register = check_is_not_register(user_id)

    if not_register:
        response = message_create_repertory
    else:
        response = (f"🔥 A paz do Senhor, *{name}*! 🔥"
                    "\n\nPara saber o tom de um hino no seu repertório, envie uma frase nesse formato:"
                    "\n*qual o tom: NOME DO LOUVOR*"
                    "\n*Ex:* qual o tom: Agnus Dei")

    bot.reply_to(message, response)

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
    topic_name = title_topics.get(thread_id)
    user = message.from_user.full_name

    print(topic_name)

    message = (
        f"🔔 *Atualização no Tópico:* {topic_name}\n"
        f"👤 *Irmã(o):* {user}\n"
    )

    if topic_name is not None:
        bot.send_message(CHAT_ID, "🔥 TEERRRAAAA! 🔥 "
                                  f"\n\n {message}")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    user_id = message.from_user.id
    user_name = str(message.from_user.first_name)
    input_user = message.text

    commands = {
        "adicionar:": post_repertory,
        "atualizar:": update_repertory,
        "qual o tom:": get_repertory
    }

    for cmd, callback in commands.items():
        if cmd in input_user:
            return callback(message, user_name, user_id, input_user)

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

def check_is_not_register(user_id):
    tab = str(user_id)
    sheet = client.open(SPREADSHEET_NAME)
    get_all_tabs = [sheet.title for sheet in sheet.worksheets()]

    return tab not in get_all_tabs

def create_tab_user(tab_id):
    tab = str(tab_id)
    sheet = client.open(SPREADSHEET_NAME)

    get_all_tabs = [sheet.title for sheet in sheet.worksheets()]

    if tab in get_all_tabs:
        return False
    else:
        worksheet = sheet.add_worksheet(title=tab, rows=500, cols=2)
        worksheet.append_row(["NOME", "TOM"])
        worksheet.freeze(rows=1)
        format_first_register(worksheet)

        print(f"Create tab '{tab}'!")
        return True

def post_repertory(message, user_name, user_id, input_user):
    try:
        sheet = client.open(SPREADSHEET_NAME).worksheet(str(user_id))
        content = input_user.replace("adicionar: ", "")

        if "," in content:
            name, tone = content.split(",", 1)
            name = name.strip()
            tone = tone.strip()
            sheet.append_row([name, tone])
            response = ("🎶 *Glória a Deus, servo(a) do Senhor!* 🎶"
                        f"\n\nMais um louvor foi adicionado ao seu repertório *{user_name}*, e o céu se alegra quando nos preparamos com zelo e dedicação para adorar ao Rei dos reis! 🙌"
                        "\n*“Louvai ao Senhor, porque o Senhor é bom; cantai louvores ao Seu nome, porque é agradável.”* (Salmos 135:3)"
                        "\nQue este louvor seja usado com unção, toque corações e eleve vidas à presença do Senhor. Lembre-se: o louvor quebra cadeias, traz cura e abre caminhos! 🔥"
                        "\n\nContinue firme, pois *“Deus procura adoradores que O adorem em espírito e em verdade.”* (João 4:23)")

        else:
            response = (f"⚠️ Atenção, *{user_name}*! ⚠️"
                        "\n*“O justo cai sete vezes, mas torna a levantar-se.”* (Provérbios 24:16)"
                        "\n\n Você não seguiu o formato correto:"
                        "\n*adicionar: NOME DO LOUVOR,TOM*")

        bot.reply_to(message, response)

    except gspread.exceptions.WorksheetNotFound:
        bot.reply_to(message, f"❌ Oh irmã(o) {user_name}! Seu repertório não foi encontrada!"
                              f"\n\n Acesse o /criarmeubancoderepertorio e tente novamente.")
    except Exception:
        bot.reply_to(message, f"❌ Oh irmã(o) {user_name}! Tente novamente.")
def get_repertory(message, user_name, user_id, input_user):
    try:
        sheet = client.open(SPREADSHEET_NAME).worksheet(str(user_id))
        search = input_user.replace("qual o tom: ", "")
        data = sheet.get_all_records()

        if search:
            result = [
                (column["NOME"], column["TOM"])
                for column in data
                if "NOME" in column and "TOM" in column
                   and search.lower() in column["NOME"].lower()
            ]

            if result:
                response = "*Louvores encontrados* no seu repertório:\n"
                response += "\n".join([f"{i}. {name_music} - *{tone}*" for i, (name_music, tone) in enumerate(result[:5], start=1)])

            else:
                response = "❌ Nenhuma música encontrada no seu repertório."

            bot.reply_to(message, f"🔥 A paz do Senhor, *{user_name}*! 🔥"
                                  f"\n\n{response}")

        else:
            bot.reply_to(message, f"⚠️ Atenção, *{user_name}*! ⚠️"
                                  "\n*“O justo cai sete vezes, mas torna a levantar-se.”* (Provérbios 24:16)"
                                  "\n*qual o tom: NOME DO LOUVOR*"
                                  "\n*Ex:* qual o tom: Agnus Dei")

    except gspread.exceptions.WorksheetNotFound:
        bot.reply_to(message, f"❌ Oh irmã(o) {user_name}! Seu repertório não foi encontrada!"
                              f"\n\n Acesse o /criarmeubancoderepertorio e tente novamente.")
    except Exception as error:
        bot.reply_to(message, f"❌ Oh irmã(o) {user_name}! Tente novamente."
                     f"\n\n{error}")
def update_repertory(message, user_name, user_id, input_user):
    try:
        sheet = client.open(SPREADSHEET_NAME).worksheet(str(user_id))
        content = input_user.replace("atualizar: ", "")
        data = sheet.get_all_records()

        if "," in content:
            name, tone = content.split(",", 1)
            name = name.strip()
            tone = tone.strip()

            for i, columns in enumerate(data, start=2):
                if columns["NOME"] == name:
                    sheet.update_cell(i, 2, tone)

                    bot.reply_to(message, f"✅ TOM da música '{name}' atualizado para '{tone}'.")
                    return

            bot.reply_to(message, f"❌ Música '{name}' não encontrada no seu repertório! Tente novamente.")

        else:
            bot.reply_to(message, f"⚠️ Atenção, *{user_name}*! ⚠️"
                                  "\n*“O justo cai sete vezes, mas torna a levantar-se.”* (Provérbios 24:16)"
                                  "\n\n Você não seguiu o formato correto:"
                                  "\n*atualizar: NOME DO LOUVOR,TOM*")

    except gspread.exceptions.WorksheetNotFound:
        bot.reply_to(message, f"❌ Oh irmã(o) {user_name}! Seu repertório não foi encontrada!"
                              f"\n\n Acesse o /criarmeubancoderepertorio e tente novamente.")
    except Exception:
        bot.reply_to(message, f"❌ Oh irmã(o) {user_name}! Tente novamente.")

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