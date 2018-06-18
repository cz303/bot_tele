from tokens \
    import *

import matplotlib

matplotlib.use("Agg")  # has to be before any other matplotlibs imports to set a "headless" backend
import matplotlib.pyplot as plt
import psutil
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
import operator
import collections
# import sys
import time
# import threading
# import random
import telepot
# from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardHide, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
# from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent
import sqlite3
import logging
import subprocess

# add filemode="w" to overwrite
logging.basicConfig(filename="logs/tele_bot.log", level=logging.INFO)

memorythreshold = 85  # If memory usage more this %
poll = 300  # seconds

timelist = []
memlist = []
xaxis = []

setmessage = []
viewstatic = []

adminchatid = []
graphstart = datetime.now()

stopmarkup = {'keyboard': [['Хватит']]}
helpmarkup = {'keyboard': [['Массовая рассылка'], ['Статистика']]}
staticmarkup = {'keyboard': [['Статистика сервера'], ['Память на сервере'], ['Подписки на бота'], ['Назад']]}
yn_markup = {'keyboard': [['Да'], ['Нет'], ['Хватит']]}
yn_only_markup = {'keyboard': [['Да'], ['Нет']]}

elementmarkup = {'keyboard': [['Про нас'], ['Социальные сети'], ['Заказать прайслист'], ['Proxy для любимого клиента']]}
soc_elementmarkup = {'keyboard': [['Instagram'], ['VK'], ['Официальный сайт'], ['Назад']]}
hide_keyboard = {'hide_keyboard': True}

conn = sqlite3.connect("mydatabase.db")
cursor = conn.cursor()
for row in cursor.execute("select chat_id from chats where is_admin = '1';"):
    adminchatid.append((row[0]))
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


def plotmemgraph(memlist, xaxis, tmperiod):
    plt.xlabel(tmperiod)
    plt.ylabel('% Использовано')
    plt.title('График использования памяти')
    plt.text(0.1 * len(xaxis), memorythreshold + 2, 'Максимум: ' + str(memorythreshold) + ' %')
    memthresholdarr = []
    for xas in xaxis:
        memthresholdarr.append(memorythreshold)
    plt.plot(xaxis, memlist, 'b-', xaxis, memthresholdarr, 'r--')
    plt.axis([0, len(xaxis) - 1, 0, 100])
    plt.savefig('/tmp/graph.png')
    plt.close()
    f = open('/tmp/graph.png', 'rb')
    return f


class YourBot(telepot.Bot):
    def __init__(self, *args, **kwargs):
        super(YourBot, self).__init__(*args, **kwargs)
        self._answerer = telepot.helper.Answerer(self)
        # self._message_with_inline_keyboard = None

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
                                "select (case when is_admin = '0' then 'Пользователей' else 'Администраторов' end) as label,count(chat_id) from chats group by label;"):
                            message = message + str(row[0]) + ": *" + str(row[1]) + "*\n"
                        conn.close()
                        bot.sendMessage(chat_id, message, parse_mode='MARKDOWN')
                    elif msg['text'] == 'Память на сервере':
                        bot.sendChatAction(chat_id, 'typing')
                        tmperiod = "Последние %.2f часа" % ((datetime.now() - graphstart).total_seconds() / 3600)
                        bot.sendPhoto(chat_id, plotmemgraph(memlist, xaxis, tmperiod))
            else:
                if msg['text'] == '/start':
                    bot.sendChatAction(chat_id, 'typing')
                    bot.sendMessage(chat_id, "Привет! Справшивай, я расскажу", reply_markup=elementmarkup)
                    conn = sqlite3.connect("mydatabase.db")
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO chats(chat_id, is_admin) VALUES (?, 0);", (str(chat_id),))
                    conn.commit()
                    conn.close()
                elif msg['text'] == "Про нас":
                    bot.sendChatAction(chat_id, 'typing')
                    bot.sendMessage(chat_id,
                                    "Арт-лаборатория ELEMENT\n\nПрофессиональные шоу программы и анимация на любое торжество. Оригинальные, яркие, запоминающиеся!\n\n🔥    Огненное шоу\n💡    Светодиодное шоу\n ⚡️   Электрическое шоу\n 💨   Шоу Ветра\n 🔦   Проекционное шоу\n🚨    Пиксельное шоу\n🎀    Шоу гимнасток\n🔮    Контактное жонглирование\n🎪    Ходулисты, мимы, жонглеры, леди-фуршет, живые статуи",
                                    reply_markup=elementmarkup)
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
                    bot.sendMessage(chat_id, "Вернулись", reply_markup=elementmarkup)
                elif msg['text'] == "Заказать прайслист":
                    bot.sendChatAction(chat_id, 'typing')
                    bot.sendMessage(chat_id, "Мы обязательно с Вами свяжемся", reply_markup=elementmarkup)
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
                                    parse_mode='MARKDOWN', reply_markup=elementmarkup)


TOKEN = telegrambot
bot = YourBot(TOKEN)
bot.message_loop()
tr = 0
xx = 0

# for admin_chat_id in adminchatid:
#    bot.sendChatAction(admin_chat_id, 'typing')
#    bot.sendMessage(admin_chat_id, "Я запущен!", reply_markup=helpmarkup)


# Keep the program running.
while 1:
    if tr == poll:
        tr = 0
        timenow = datetime.now()
        memck = psutil.virtual_memory()
        mempercent = memck.percent
        if len(memlist) > 300:
            memq = collections.deque(memlist)
            memq.append(mempercent)
            memq.popleft()
            memlist = memq
            memlist = list(memlist)
        else:
            xaxis.append(xx)
            xx += 1
            memlist.append(mempercent)
        memfree = memck.available / 1000000
        if mempercent > memorythreshold:
            memavail = "Available memory: %.2f GB" % (memck.available / 1000000000)
            graphend = datetime.now()
            tmperiod = "Last %.2f hours" % ((graphend - graphstart).total_seconds() / 3600)
            for adminid in adminchatid:
                bot.sendMessage(adminid, "CRITICAL! LOW MEMORY!\n" + memavail)
                bot.sendPhoto(adminid, plotmemgraph(memlist, xaxis, tmperiod))
    time.sleep(10)
