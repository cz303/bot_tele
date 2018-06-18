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

logging.basicConfig(filename="logs/tele_bot.log", level=logging.INFO)

setmessage = []
viewstatic = []

userchatid = []
adminchatid = []
graphstart = datetime.now()

stopmarkup = {'keyboard': [['Хватит']]}
helpmarkup = {'keyboard': [['Массовая рассылка'], ['Статистика']]}
staticmarkup = {'keyboard': [['Статистика сервера'], ['Память на сервере'], ['Подписки на бота'], ['Назад']]}
yn_markup = {'keyboard': [['Да'], ['Нет'], ['Хватит']]}
yn_only_markup = {'keyboard': [['Да'], ['Нет']]}
elementmarkup_unreg = {'keyboard': [['Про нас'], ['Социальные сети'], ['Подписка на бота'], ['Proxy для любимого клиента']]}
elementmarkup_reg = {'keyboard': [['Про нас'], ['Социальные сети'], ['Личный кабинет'], ['Proxy для любимого клиента']]}
soc_elementmarkup = {'keyboard': [['Instagram'], ['VK'], ['Официальный сайт'], ['Назад']]}
hide_keyboard = {'hide_keyboard': True}

conn = sqlite3.connect("mydatabase.db")
cursor = conn.cursor()
for row in cursor.execute("select chat_id from chats where is_admin = '1';"):
    adminchatid.append((row[0]))
for row in cursor.execute("select chat_id from chats where is_registered_user = '1';"):
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
                if chat_id not in setmessage and chat_id not in viewstatic:
                    if msg['text'] == 'Массовая рассылка':
                        bot.sendChatAction(chat_id, 'typing')
                        setmessage.append(chat_id)
                        bot.sendMessage(chat_id, "Какое сообщение отправить?", reply_markup=stopmarkup)
                    elif msg['text'] == 'Статистика':
                        bot.sendChatAction(chat_id, 'typing')
                        viewstatic.append(chat_id)
                        bot.sendMessage(chat_id, "Смотрим статистику", reply_markup=staticmarkup)
                if chat_id in setmessage:
                    if msg['text'] == 'Хватит':
                        bot.sendChatAction(chat_id, 'typing')
                        setmessage.remove(chat_id)
                        bot.sendMessage(chat_id, "Всё закончил", reply_markup=helpmarkup)
                    elif msg['text'] != 'Массовая рассылка':
                        bot.sendChatAction(chat_id, 'typing')
                        setmessage.remove(chat_id)
                        conn = sqlite3.connect("mydatabase.db")
                        cursor = conn.cursor()
                        for row in cursor.execute("select chat_id from chats where is_admin = '0'"):
                            bot.sendMessage(row[0], msg['text'], parse_mode='MARKDOWN', disable_web_page_preview=True)
                        conn.close()
                        bot.sendMessage(chat_id, "Сообщение отправил, продолжим...", reply_markup=helpmarkup)
                if chat_id in viewstatic:
                    if msg['text'] == 'Назад':
                        bot.sendChatAction(chat_id, 'typing')
                        viewstatic.remove(chat_id)
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
                                "select (case when is_admin = 0 then 'Пользователей' else 'Администраторов' end) as label,count(chat_id) from chats group by label;"):
                            message = message + str(row[0]) + ": *" + str(row[1]) + "*\n"
                        conn.close()
                        bot.sendMessage(chat_id, message, parse_mode='MARKDOWN')
            else:
                if chat_id in userchatid:
                    if msg['text'] == 'Тест':
                        bot.sendChatAction(chat_id, 'typing')
                        bot.sendMessage(chat_id, "Всё работает!", reply_markup=elementmarkup_reg)
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
                        userchatid.append(chat_id)
                        conn = sqlite3.connect("mydatabase.db")
                        cursor = conn.cursor()
                        cursor.execute("update chats set is_registered_user = 1 where chat_id = '" + (str(chat_id)) + "';")
                        conn.commit()
                        conn.close()
                        bot.sendMessage(chat_id, "Теперь Вам доступен личный кабинет и будет приходить рассылка",
                                        reply_markup=elementmarkup_reg)
                    elif msg['text'] == "Про нас":
                        bot.sendChatAction(chat_id, 'typing')
                        bot.sendMessage(chat_id,
                                        "Арт-лаборатория ELEMENT\n\nПрофессиональные шоу программы и анимация на любое торжество. Оригинальные, яркие, запоминающиеся!\n\n🔥    Огненное шоу\n💡    Светодиодное шоу\n ⚡️   Электрическое шоу\n 💨   Шоу Ветра\n 🔦   Проекционное шоу\n🚨    Пиксельное шоу\n🎀    Шоу гимнасток\n🔮    Контактное жонглирование\n🎪    Ходулисты, мимы, жонглеры, леди-фуршет, живые статуи",
                                        reply_markup=elementmarkup_unreg)
                    elif msg['text'] == "Социальные сети":
                        bot.sendChatAction(chat_id, 'typing')
                        bot.sendMessage(chat_id, "Социальные сети Арт-лаборатории ELEMENT", reply_markup=soc_elementmarkup)
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
                    elif msg['text'] == "Заказать прайслист":
                        bot.sendChatAction(chat_id, 'typing')
                        bot.sendMessage(chat_id, "Мы обязательно с Вами свяжемся", reply_markup=elementmarkup_unreg)
                        for admin_chat_id in adminchatid:
                            try:
                                bot.sendChatAction(admin_chat_id, 'typing')
                                bot.sendMessage(admin_chat_id, "Наш любимый клиент просит прислать ему прайс!")
                                bot.forwardMessage(admin_chat_id, chat_id, msg['message_id'])
                            except:
                                print("Хм-м")
                    elif msg['text'] == "Proxy для любимого клиента":
                        bot.sendChatAction(chat_id, 'typing')
                        bot.sendMessage(chat_id,
                                        "[Настройка Proxy](https://t.me/socks?server=195.201.136.255&port=1080&user=element_89179024466&pass=*****)",
                                        parse_mode='MARKDOWN', reply_markup=elementmarkup_unreg)


TOKEN = telegrambot
bot = YourBot(TOKEN)
bot.message_loop()

for admin_chat_id in adminchatid:
    bot.sendChatAction(admin_chat_id, 'typing')
    bot.sendMessage(admin_chat_id, "Я запущен!", reply_markup=helpmarkup)


# Keep the program running.
while 1:
    time.sleep(10)
