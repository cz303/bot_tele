# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.

import telebot
from tokens \
    import *
import random
import logging
from datetime import datetime
import sqlite3

logging.basicConfig(filename="logs/tele_bot.log", level=logging.INFO)

setmessage = []
viewstatic = []
inlk = []

userchatid = []
adminchatid = []
graphstart = datetime.now()

stopmarkup = {'keyboard': [['Хватит']]}
helpmarkup = {'keyboard': [['Массовая рассылка'], ['Статистика']]}
staticmarkup = {'keyboard': [['Статистика сервера'], ['Подписки на бота'], ['Назад']]}
yn_markup = {'keyboard': [['Да'], ['Нет'], ['Хватит']]}
yn_only_markup = {'keyboard': [['Да'], ['Нет']]}
elementmarkup_unreg = {'keyboard': [['Про нас'], ['Подписка на бота']]}
elementmarkup_reg = {'keyboard': [['Про нас'], ['Личный кабинет'],
                                  ['Proxy для любимого клиента'], ['Отписаться от бота']]}
elementmarkup_lk = {'keyboard': [['Заказать прайслист'], ['Назад']]}
elementmarkup_soc = {'inline_keyboard': [[{"text": "Instagram", "url": "https://www.instagram.com/element_show/"}],
                                         [{"text": "ВКонтакте", "url": "https://vk.com/club92907131"}],
                     [{"text": "Официальный сайт", "url": "http://deliriumshow.com/"}]]}
hide_keyboard = {'hide_keyboard': True}

conn = sqlite3.connect("mydatabase.db")
cursor = conn.cursor()
for row in cursor.execute("select chat_id from chats where status = 2;"):
    adminchatid.append((row[0]))
conn.close()

conn = sqlite3.connect("mydatabase.db")
cursor = conn.cursor()
for row in cursor.execute("select chat_id from chats where status = 1;"):
    userchatid.append((row[0]))
conn.close()

def clearall(chat_id):
    if chat_id in setmessage:
        setmessage.remove(chat_id)
    if chat_id in viewstatic:
        viewstatic.remove(chat_id)

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def hello(name):
    phrase = ['Привет, ', 'Добрый день, ', 'Здравствуйте, ', 'Аллоха, ']
    i = random.randint(0,2)
    result = phrase[i] + name +"!"
    return result

bot = telebot.TeleBot(telegrambot)

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Справшивай, я расскажу")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    content_type = str(message.content_type)
    chat_type =  str(message.chat.type)
    chat_id = message.chat.id


    if chat_id in adminchatid:
        logging.info("Incoming message on admin chat" + str(message) + " time:" + str(datetime.now()))
    else:
        logging.info("Incoming message on public chat" + str(message) + " time:" + str(datetime.now()))
    if content_type == 'text':
        text = str(message.text)
        bot.sendChatAction(chat_id, 'typing')
        if chat_id in adminchatid:
            if chat_id not in setmessage and chat_id not in viewstatic:
                if text == 'Массовая рассылка':
                    setmessage.append(chat_id)
                    bot.sendMessage(chat_id, "Какое сообщение отправить?", reply_markup=stopmarkup)
                elif text == 'Статистика':
                    viewstatic.append(chat_id)
                    bot.sendMessage(chat_id, "Смотрим статистику", reply_markup=staticmarkup)
            if chat_id in setmessage:
                if text == 'Хватит':
                    setmessage.remove(chat_id)
                    bot.sendMessage(chat_id, "Всё закончил", reply_markup=helpmarkup)
                elif text != 'Массовая рассылка':
                    setmessage.remove(chat_id)
                    k = 0
                    conn = sqlite3.connect("mydatabase.db")
                    cursor = conn.cursor()
                    for row in cursor.execute("select chat_id, name from chats where status = 1"):
                        bot.sendMessage(row[0], hello(row[1]) + "\n\n" + msg['text'],
                                        parse_mode='MARKDOWN', disable_web_page_preview=True)
                        k = k + 1
                    conn.close()
                    bot.sendMessage(chat_id, "Отправил *" + str(k) + "* сообщений, "
                                                                     "продолжим...",
                                    parse_mode='MARKDOWN', reply_markup=helpmarkup)
            if chat_id in viewstatic:
                if text == 'Назад':
                    viewstatic.remove(chat_id)
                    bot.sendMessage(chat_id, "Вернулись", reply_markup=helpmarkup)
                elif text == 'Статистика сервера':
                    bot.sendMessage(chat_id, 'reply', disable_web_page_preview=True)
                elif text == 'Подписки на бота':
                    message = '*На меня подписано:*\n'
                    conn = sqlite3.connect("mydatabase.db")
                    cursor = conn.cursor()
                    for row in cursor.execute(
                            "select (case when status = 0 then 'Пользователей' "
                            "when status = 1 then 'Зарегистрированных пользователей' "
                            "else 'Администраторов' end) as label,count(chat_id) from chats group by label;"):
                        message = message + str(row[0]) + ": *" + str(row[1]) + "*\n"
                    conn.close()
                    bot.sendMessage(chat_id, message, parse_mode='MARKDOWN')
        else:
            if chat_id in userchatid:
                if chat_id in inlk:
                    if text == "Заказать прайслист":
                        try:
                            f = open('/root/bot_tele/etc/list.xml', 'rb', )
                            bot.sendDocument(chat_id, f)
                        except:
                            bot.sendMessage(chat_id, 'Приношу свои изминения, у меня нет актуального прайса! \n'
                                                     'Но не переживайте, я уже предупредил администратора!')
                            for admin_chat_id in adminchatid:
                                try:
                                    bot.sendChatAction(admin_chat_id, 'typing')
                                    bot.sendMessage(admin_chat_id, "Клиент запросил прайс, а файла у бота нет")
                                    bot.forwardMessage(admin_chat_id, chat_id, msg['message_id'])
                                except:
                                    print("Хм-м")
                    if text == 'Назад':
                        inlk.remove(chat_id)
                        bot.sendMessage(chat_id, "Вернулись", reply_markup=elementmarkup_reg)
                else:
                    if text == "Про нас":
                        bot.sendMessage(chat_id,
                                        "Арт-лаборатория ELEMENT\n\nПрофессиональные шоу программы и анимация на"
                                        " любое торжество. Оригинальные, яркие, запоминающиеся!\n\n🔥    Огненное "
                                        "шоу\n💡    Светодиодное шоу\n ⚡️   Электрическое шоу\n 💨   Шоу Вет"
                                        "ра\n 🔦   Проекционное шоу\n🚨    Пиксельное шоу\n🎀    Шоу гимнасто"
                                        "к\n🔮    Контактное жонглирование\n🎪    Ходулисты, мимы, жонглеры, леди"
                                        "-фуршет, живые статуи",
                                        reply_markup=elementmarkup_soc)
                    elif text == "Proxy для любимого клиента":
                        bot.sendMessage(chat_id,
                                        "[Настройка Proxy](https://t.me/socks?server=195.201.136.255&"
                                        "port=1080&user=element_89179024466&pass=*****)",
                                        parse_mode='MARKDOWN', reply_markup=elementmarkup_reg)
                    elif text == 'Отписаться от бота':
                        userchatid.remove(chat_id)
                        if str(message.chat.first_name):
                            name = str(message.chat.first_name)
                        else:
                            name = str(message.chat.id)
                        conn = sqlite3.connect("mydatabase.db")
                        cursor = conn.cursor()
                        cursor.execute("update chats set status = 0, name = '" + name + "' "
                                                                                        "where "
                                                                                        "chat_id = '"
                                                                                        "" + chat_id + "';")
                        conn.commit()
                        conn.close()
                        bot.sendMessage(chat_id, "Спасибо, что были с нами!",
                                        reply_markup=elementmarkup_unreg)
                    elif text == "Личный кабинет":
                        inlk.append(chat_id)
                        bot.sendMessage(chat_id, "Ваш личный кабинет", reply_markup=elementmarkup_lk)
            else:
                if text == '/start':
                    conn = sqlite3.connect("mydatabase.db")
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO chats(chat_id) VALUES (?);", chat_id)
                    conn.commit()
                    conn.close()
                    bot.sendMessage(chat_id, "Привет! Справшивай, я расскажу", reply_markup=elementmarkup_unreg)
                elif text == 'Подписка на бота':
                    if chat_type == 'private':
                        userchatid.append(chat_id)
                        if str(message.chat.first_name):
                            name = str(message.chat.first_name)
                        else:
                            name = str(message.chat.id)
                        conn = sqlite3.connect("mydatabase.db")
                        cursor = conn.cursor()
                        cursor.execute("update chats set status = 1, "
                                       "name = '" + name + "' where chat_id = '" + chat_id + "';")
                        conn.commit()
                        conn.close()
                        bot.sendMessage(chat_id, "Теперь Вам доступен личный кабинет и будет приходить рассылка",
                                        reply_markup=elementmarkup_reg)
                    else:
                        bot.sendMessage(chat_id, "Только для личных чатов",
                                        reply_markup=elementmarkup_unreg)
                elif text == "Про нас":
                    bot.sendMessage(chat_id,
                                    "Арт-лаборатория ELEMENT\n\nПрофессиональные "
                                    "шоу программы и анимация на любое торжество. "
                                    "Оригинальные, яркие, запоминающиеся!\n\n🔥    "
                                    "Огненное шоу\n💡    Светодиодное шоу\n ⚡️   Электрич"
                                    "еское шоу\n 💨   Шоу Ветра\n 🔦   Проекционное шоу\n🚨    Пиксел"
                                    "ьное шоу\n🎀    Шоу гимнасток\n🔮    Контактное жонглирование\n🎪    Ходули"
                                    "сты, мимы, жонглеры, леди-фуршет, живые статуи",
                                    reply_markup=elementmarkup_soc)



bot.polling()
