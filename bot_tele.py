from tokens \
    import *

import matplotlib
matplotlib.use("Agg")
import psutil
from datetime import datetime
import operator
import time
import telepot
import sqlite3
import logging
import random

logging.basicConfig(filename="logs/tele_bot.log", level=logging.INFO)

setmessage = []
viewstatic = []
inlk = []

userchatid = []
adminchatid = []
graphstart = datetime.now()

stopmarkup = {'inline_keyboard': [ [ {"text": "Yes", "url": "http://www.google.com/"}, {"text": "No", "url": "http://www.google.com/"} ] ]}
helpmarkup = {'keyboard': [['Массовая рассылка'], ['Статистика']]}
staticmarkup = {'keyboard': [['Статистика сервера'], ['Подписки на бота'], ['Назад']]}
yn_markup = {'keyboard': [['Да'], ['Нет'], ['Хватит']]}
yn_only_markup = {'keyboard': [['Да'], ['Нет']]}
elementmarkup_unreg = {'keyboard': [['Про нас'], ['Социальные сети'], ['Подписка на бота']]}
elementmarkup_reg = {'keyboard': [['Про нас'], ['Социальные сети'], ['Личный кабинет'],
                                  ['Proxy для любимого клиента'], ['Отписаться от бота']]}
elementmarkup_lk = {'keyboard': [['Заказать прайслист'], ['Назад']]}
soc_elementmarkup = {'keyboard': [['Instagram'], ['VK'], ['Официальный сайт'], ['Назад']]}
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


class YourBot(telepot.Bot):
    def __init__(self, *args, **kwargs):
        super(YourBot, self).__init__(*args, **kwargs)
        self._answerer = telepot.helper.Answerer(self)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if str(chat_id) in adminchatid:
            logging.info("Incoming message on admin chat" + str(msg) + " time:" + str(datetime.now()))
        else:
            logging.info("Incoming message on public chat" + str(msg) + " time:" + str(datetime.now()))
        if content_type == 'text':
            if str(chat_id) in adminchatid:
                if str(chat_id) not in setmessage and str(chat_id) not in viewstatic:
                    if msg['text'] == 'Массовая рассылка':
                        bot.sendChatAction(chat_id, 'typing')
                        setmessage.append(str(chat_id))
                        bot.sendMessage(chat_id, "Какое сообщение отправить?", reply_markup=stopmarkup)
                    elif msg['text'] == 'Статистика':
                        bot.sendChatAction(chat_id, 'typing')
                        viewstatic.append(str(chat_id))
                        bot.sendMessage(chat_id, "Смотрим статистику", reply_markup=staticmarkup)
                if str(chat_id) in setmessage:
                    if msg['text'] == 'Хватит':
                        bot.sendChatAction(chat_id, 'typing')
                        setmessage.remove(str(chat_id))
                        bot.sendMessage(chat_id, "Всё закончил", reply_markup=helpmarkup)
                    elif msg['text'] != 'Массовая рассылка':
                        bot.sendChatAction(chat_id, 'typing')
                        setmessage.remove(str(chat_id))
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
                if str(chat_id) in viewstatic:
                    if msg['text'] == 'Назад':
                        bot.sendChatAction(chat_id, 'typing')
                        viewstatic.remove(str(chat_id))
                        bot.sendMessage(chat_id, "Вернулись", reply_markup=helpmarkup)
                    elif msg['text'] == 'Статистика сервера':
                        bot.sendChatAction(chat_id, 'typing')
                        memory = psutil.virtual_memory()
                        disk = psutil.disk_usage('/')
                        boottime = datetime.fromtimestamp(psutil.boot_time())
                        now = datetime.now()
                        timedif = "Онлайн: %.1f часов" % (((now - boottime).total_seconds()) / 3600)
                        memtotal = "Памяти: %.2f GB " % (memory.total / 1000000000)
                        memavail = "Доступно: %.2f GB" % (memory.available / 1000000000)
                        memuseperc = "Используется: " + str(memory.percent) + " %"
                        diskused = "HDD используется: " + str(disk.percent) + " %"
                        pids = psutil.pids()
                        pidsreply = ''
                        procs = {}
                        for pid in pids:
                            p = psutil.Process(pid)
                            try:
                                pmem = p.memory_percent()
                                if pmem > 0.5:
                                    if p.name() in procs:
                                        procs[p.name()] += pmem
                                    else:
                                        procs[p.name()] = pmem
                            except:
                                print("Хм-м")
                        sortedprocs = sorted(procs.items(), key=operator.itemgetter(1), reverse=True)
                        for proc in sortedprocs:
                            pidsreply += proc[0] + " " + ("%.2f" % proc[1]) + " %\n"
                        reply = timedif + "\n" + \
                                memtotal + "\n" + \
                                memavail + "\n" + \
                                memuseperc + "\n" + \
                                diskused + "\n\n" + \
                                pidsreply
                        bot.sendMessage(chat_id, reply, disable_web_page_preview=True)
                    elif msg['text'] == 'Подписки на бота':
                        bot.sendChatAction(chat_id, 'typing')
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
                if str(chat_id) in userchatid:
                    if str(chat_id) in inlk:
                        if msg['text'] == "Заказать прайслист":
                            bot.sendChatAction(chat_id, 'typing')
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
                        if msg['text'] == 'Назад':
                            bot.sendChatAction(chat_id, 'typing')
                            inlk.remove(str(chat_id))
                            bot.sendMessage(chat_id, "Вернулись", reply_markup=elementmarkup_reg)
                    else:
                        if msg['text'] == "Про нас":
                            bot.sendChatAction(chat_id, 'typing')
                            bot.sendMessage(chat_id,
                                            "Арт-лаборатория ELEMENT\n\nПрофессиональные шоу программы и анимация на"
                                            " любое торжество. Оригинальные, яркие, запоминающиеся!\n\n🔥    Огненное "
                                            "шоу\n💡    Светодиодное шоу\n ⚡️   Электрическое шоу\n 💨   Шоу Вет"
                                            "ра\n 🔦   Проекционное шоу\n🚨    Пиксельное шоу\n🎀    Шоу гимнасто"
                                            "к\n🔮    Контактное жонглирование\n🎪    Ходулисты, мимы, жонглеры, леди"
                                            "-фуршет, живые статуи",
                                            reply_markup=elementmarkup_reg)
                        elif msg['text'] == "Социальные сети":
                            bot.sendChatAction(chat_id, 'typing')
                            bot.sendMessage(chat_id, "Социальные сети Арт-лаборатории ELEMENT",
                                            reply_markup=soc_elementmarkup)
                        elif msg['text'] == "Instagram":
                            bot.sendChatAction(chat_id, 'typing')
                            bot.sendMessage(chat_id, "[Instagram](https://www.instagram.com/element_show/)",
                                            parse_mode='MARKDOWN', disable_web_page_preview=True)
                        elif msg['text'] == "VK":
                            bot.sendChatAction(chat_id, 'typing')
                            bot.sendMessage(chat_id, "[ВКонтакте](https://vk.com/club92907131)", parse_mode='MARKDOWN',
                                            disable_web_page_preview=True)
                        elif msg['text'] == "Официальный сайт":
                            bot.sendChatAction(chat_id, 'typing')
                            bot.sendMessage(chat_id, "[Официальный сайт](http://deliriumshow.com/)",
                                            parse_mode='MARKDOWN',
                                            disable_web_page_preview=True)
                        elif msg['text'] == "Назад":
                            bot.sendChatAction(chat_id, 'typing')
                            bot.sendMessage(chat_id, "Вернулись", reply_markup=elementmarkup_reg)
                        elif msg['text'] == "Proxy для любимого клиента":
                            bot.sendChatAction(chat_id, 'typing')
                            bot.sendMessage(chat_id,
                                            "[Настройка Proxy](https://t.me/socks?server=195.201.136.255&"
                                            "port=1080&user=element_89179024466&pass=*****)",
                                            parse_mode='MARKDOWN', reply_markup=elementmarkup_reg)
                        elif msg['text'] == 'Отписаться от бота':
                            bot.sendChatAction(chat_id, 'typing')
                            userchatid.remove(str(chat_id))
                            name = ""
                            if msg['chat']['first_name']:
                                name = msg['chat']['first_name']
                            elif msg['chat']['username']:
                                name = msg['chat']['username']
                            else:
                                name = msg['chat']['id']
                            conn = sqlite3.connect("mydatabase.db")
                            cursor = conn.cursor()
                            cursor.execute("update chats set status = 0, name = '" + name + "' "
                                                                                            "where "
                                                                                            "chat_id = '"
                                                                                            "" + (str(chat_id)) + "';")
                            conn.commit()
                            conn.close()
                            bot.sendMessage(chat_id, "Спасибо, что были с нами!",
                                            reply_markup=elementmarkup_unreg)
                        elif msg['text'] == "Личный кабинет":
                            bot.sendChatAction(chat_id, 'typing')
                            inlk.append(str(chat_id))
                            bot.sendMessage(chat_id, "Ваш личный кабинет", reply_markup=elementmarkup_lk)
                else:
                    if msg['text'] == '/start':
                        bot.sendChatAction(chat_id, 'typing')
                        conn = sqlite3.connect("mydatabase.db")
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO chats(chat_id) VALUES (?);", (str(chat_id),))
                        conn.commit()
                        conn.close()
                        bot.sendMessage(chat_id, "Привет! Справшивай, я расскажу", reply_markup=elementmarkup_unreg)
                    elif msg['text'] == 'Подписка на бота':
                        bot.sendChatAction(chat_id, 'typing')
                        if msg['chat']['type'] == 'private':
                            userchatid.append(str(chat_id))
                            name = ""
                            if msg['chat']['first_name']:
                                name = msg['chat']['first_name']
                            elif msg['chat']['username']:
                                name = msg['chat']['username']
                            else:
                                name = msg['chat']['id']
                            conn = sqlite3.connect("mydatabase.db")
                            cursor = conn.cursor()
                            cursor.execute("update chats set status = 1, "
                                           "name = '" + name + "' where chat_id = '" + (str(chat_id)) + "';")
                            conn.commit()
                            conn.close()
                            bot.sendMessage(chat_id, "Теперь Вам доступен личный кабинет и будет приходить рассылка",
                                            reply_markup=elementmarkup_reg)
                        else:
                            bot.sendMessage(chat_id, "Только для личных чатов",
                                            reply_markup=elementmarkup_unreg)
                    elif msg['text'] == "Про нас":
                        bot.sendChatAction(chat_id, 'typing')
                        bot.sendMessage(chat_id,
                                        "Арт-лаборатория ELEMENT\n\nПрофессиональные "
                                        "шоу программы и анимация на любое торжество. "
                                        "Оригинальные, яркие, запоминающиеся!\n\n🔥    "
                                        "Огненное шоу\n💡    Светодиодное шоу\n ⚡️   Электрич"
                                        "еское шоу\n 💨   Шоу Ветра\n 🔦   Проекционное шоу\n🚨    Пиксел"
                                        "ьное шоу\n🎀    Шоу гимнасток\n🔮    Контактное жонглирование\n🎪    Ходули"
                                        "сты, мимы, жонглеры, леди-фуршет, живые статуи",
                                        reply_markup=elementmarkup_unreg)
                    elif msg['text'] == "Социальные сети":
                        bot.sendChatAction(chat_id, 'typing')
                        bot.sendMessage(chat_id, "Социальные сети Арт-лаборатории ELEMENT",
                                        reply_markup=soc_elementmarkup)
                    elif msg['text'] == "Instagram":
                        bot.sendChatAction(chat_id, 'typing')
                        bot.sendMessage(chat_id, "[Instagram](https://www.instagram.com/element_show/)",
                                        parse_mode='MARKDOWN', disable_web_page_preview=True)
                    elif msg['text'] == "VK":
                        bot.sendChatAction(chat_id, 'typing')
                        bot.sendMessage(chat_id, "[ВКонтакте](https://vk.com/club92907131)", parse_mode='MARKDOWN',
                                        disable_web_page_preview=True)
                    elif msg['text'] == "Официальный сайт":
                        bot.sendChatAction(chat_id, 'typing')
                        bot.sendMessage(chat_id, "[Официальный сайт](http://deliriumshow.com/)", parse_mode='MARKDOWN',
                                        disable_web_page_preview=True)
                    elif msg['text'] == "Назад":
                        bot.sendChatAction(chat_id, 'typing')
                        bot.sendMessage(chat_id, "Вернулись", reply_markup=elementmarkup_unreg)


TOKEN = telegrambot
bot = YourBot(TOKEN)
bot.message_loop()

for admin_chat_id in adminchatid:
    bot.sendChatAction(admin_chat_id, 'typing')
    bot.sendMessage(admin_chat_id, "Я запущен!", reply_markup=helpmarkup)


# Keep the program running.
while 1:
    time.sleep(10)
