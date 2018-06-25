# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.

import telebot
from tokens \
    import *
import random
import logging
from datetime import datetime
import sqlite3
from telebot import types
from telegramcalendar import create_calendar
import psutil
import time
import re

logging.basicConfig(filename="logs/tele_bot.log", level=logging.INFO)

current_shown_dates={}

setmessage = []
viewstatic = []
inlk = []
inorderheader = []
inorderplace = []
inordercomment = []
inordertime = []

userchatid = []
adminchatid = []
graphstart = datetime.now()

rules = "*Жирный*\n_Курсив_\n[Отображаемое имя ссылки](Адрес ссылки, пример https://ya.ru)"

ordermarkup = types.InlineKeyboardMarkup()
row=[]
row.append(types.InlineKeyboardButton(text="➕ Задать шоу", callback_data="order_header"))
row.append(types.InlineKeyboardButton(text="➕ Задать дату", callback_data="order_date"))
ordermarkup.row(*row)
row=[]
row.append(types.InlineKeyboardButton(text="➕ Задать время", callback_data="order_time"))
row.append(types.InlineKeyboardButton(text="➕ Задать место", callback_data="order_place"))
ordermarkup.row(*row)
row=[]
row.append(types.InlineKeyboardButton(text="➕ Задать комментарий", callback_data="order_comment"))
row.append(types.InlineKeyboardButton(text="🔙 Завершить", callback_data="order_back"))
ordermarkup.row(*row)

ordersendmarkup = types.InlineKeyboardMarkup()
row=[]
row.append(types.InlineKeyboardButton(text="➕ Задать шоу", callback_data="order_header"))
row.append(types.InlineKeyboardButton(text="➕ Задать дату", callback_data="order_date"))
ordersendmarkup.row(*row)
row=[]
row.append(types.InlineKeyboardButton(text="➕ Задать время", callback_data="order_time"))
row.append(types.InlineKeyboardButton(text="➕ Задать место", callback_data="order_place"))
ordersendmarkup.row(*row)
row=[]
row.append(types.InlineKeyboardButton(text="➕ Задать комментарий", callback_data="order_comment"))
row.append(types.InlineKeyboardButton(text="🔙 Завершить", callback_data="order_back"))
ordersendmarkup.row(*row)
ordersendmarkup.add(types.InlineKeyboardButton(text="☑ Отправить", callback_data="order_send"))

orderupdatemarkup = types.InlineKeyboardMarkup()
orderupdatemarkup.add(types.InlineKeyboardButton(text="🔄 Вернуться к редактированию", callback_data="order_refresh"))

stopmarkup = types.InlineKeyboardMarkup()
stopmarkup.add(types.InlineKeyboardButton(text="🔙 Завершить", callback_data="back"))

sendmarkup = types.InlineKeyboardMarkup()
sendmarkup.add(types.InlineKeyboardButton(text="☑ Отправить", callback_data="send"))
sendmarkup.add(types.InlineKeyboardButton(text="🔙 Отменить", callback_data="back"))

elementmarkup_unreg = types.ReplyKeyboardMarkup(row_width=1)
elementmarkup_unreg.add(types.KeyboardButton('Про нас'))
elementmarkup_unreg.add(types.KeyboardButton('Подписка на бота'))

stopkeyboardmarkup = types.ReplyKeyboardMarkup(row_width=1)
stopkeyboardmarkup.add(types.KeyboardButton('Завершить'))

elementmarkup_soc = types.InlineKeyboardMarkup()
elementmarkup_soc.add(types.InlineKeyboardButton(text="Instagram", url="https://www.instagram.com/element_show"))
elementmarkup_soc.add(types.InlineKeyboardButton(text="ВКонтакте", url="https://vk.com/club92907131"))
elementmarkup_soc.add(types.InlineKeyboardButton(text="Официальный сайт", url="http://deliriumshow.com"))

adminmarkup = types.ReplyKeyboardMarkup(row_width=1)
itembtn1 = types.KeyboardButton('Массовая рассылка')
itembtn2 = types.KeyboardButton('Статистика')
adminmarkup.add(itembtn1, itembtn2)

yn_markup = types.ReplyKeyboardMarkup(row_width=1)
yn_markup.add('Да', 'Нет', 'Хватит')

yn_only_markup = types.ReplyKeyboardMarkup(row_width=1)
yn_only_markup.add('Да', 'Нет')

elementmarkup_reg = types.ReplyKeyboardMarkup(row_width=1)
elementmarkup_reg.add('Про нас', 'Личный кабинет', 'Proxy для любимого клиента', 'Отписаться от бота')

elementmarkup_unreg = types.ReplyKeyboardMarkup(row_width=1)
elementmarkup_unreg.add('Про нас', 'Подписка на бота')

elementmarkup_lk = types.ReplyKeyboardMarkup(row_width=1)
elementmarkup_lk.add('Заказать прайслист', 'Предварительный заказ', 'Назад')

likemarkup = types.InlineKeyboardMarkup()
row=[]
row.append(types.InlineKeyboardButton("👍",callback_data="like"))
row.append(types.InlineKeyboardButton("👎",callback_data="dislike"))
likemarkup.row(*row)

conn = sqlite3.connect("mydatabase.db")
cursor = conn.cursor()
for row in cursor.execute("select chat_id from chats where status = 2;"):
    adminchatid.append(float(row[0]))
conn.close()

conn = sqlite3.connect("mydatabase.db")
cursor = conn.cursor()
for row in cursor.execute("select chat_id from chats where status = 1;"):
    userchatid.append(float(row[0]))
conn.close()

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def xstr(s):
    if s is None or s == 'None':
        return ''
    else:
        return str(s)

def is_str(s):
    if s is None or s == 'None':
        return False
    else:
        return True

def is_time(s):
    result = re.findall(r'[0,1,2]\d{1}[:][0,1,2,3,4,5]\d{1}', s)
    if len(result) > 0:
        return True
    else:
        return False

def order(header = None,
          date = None,
          time = None,
          place = None,
          comment = None,
          customer = None):
    order_header = "*Шоу:* " + xstr(header) + "\n"
    order_date = "*Дата:* " + xstr(date) + "\n"
    order_time = "*Время:* " + xstr(time) + "\n"
    order_place = "*Место:* " + xstr(place) + "\n"
    order_comment = "*Ваш комментарий:* " + xstr(comment) + "\n"
    order_customer = "*Заказчик:* " + xstr(customer) + "\n"
    order = order_header + order_date + order_time + order_place + order_comment + order_customer
    return order

def check_order(header, date, time, place, comment):
    if is_str(header) and is_str(date) and is_str(time) and is_str(place) and is_str(comment):
        return True
    else:
        return False

def hello(name):
    phrase = ['Привет, ', 'Добрый день, ', 'Здравствуйте, ', 'Аллоха, ']
    i = random.randint(0, 3)
    result = phrase[i] + name + "!"
    return result

bot = telebot.TeleBot(telegrambot)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    conn = sqlite3.connect("mydatabase.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chats(chat_id) VALUES (" + str(message.chat.id) + ");")
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, "Привет! Справшивай, я расскажу", reply_markup=elementmarkup_unreg)


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    content_type = str(message.content_type)
    chat_type = str(message.chat.type)
    chat_id = message.chat.id

    conn = sqlite3.connect("mydatabase.db")
    cursor = conn.cursor()
    cursor.execute("update stats set number = number+1 where stat = 'messages';")
    conn.commit()

    if chat_id in adminchatid:
        logging.info("Incoming message on admin chat" + str(message) + " time:" + str(datetime.now()))
    else:
        logging.info("Incoming message on public chat" + str(message) + " time:" + str(datetime.now()))
    if content_type == 'text':
        text = str(message.text)
        bot.send_chat_action(chat_id, 'typing')
        if chat_id in adminchatid:
            if chat_id not in setmessage:
                if text == 'Массовая рассылка':
                    setmessage.append(chat_id)
                    bot.send_message(chat_id, "Какое сообщение отправить?\n\n" + rules, reply_markup=stopmarkup, disable_web_page_preview=True)
                elif text == 'Статистика':
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    boottime = datetime.fromtimestamp(psutil.boot_time())
                    now = datetime.now()
                    label_serv = "*Статистика сервера:*"
                    timedif = "Онлайн: *%.1f* часов" % (((now - boottime).total_seconds()) / 3600)
                    memtotal = "Памяти: *%.2f* GB " % (memory.total / 1000000000)
                    memavail = "Доступно: *%.2f* GB" % (memory.available / 1000000000)
                    memuseperc = "Используется: *" + str(memory.percent) + "* %"
                    diskused = "HDD используется: *" + str(disk.percent) + "* %"

                    label_follow = '*На меня подписано:*\n'
                    for row in cursor.execute(
                            "select (case when status = 0 then 'Пользователей' "
                            "when status = 1 then 'Зарегистрированных пользователей' "
                            "else 'Администраторов' end) as label,count(chat_id) from chats group by label;"):
                        label_follow = label_follow + str(row[0]) + ": *" + str(row[1]) + "*\n"

                    label_stats = '*Показатели:*\n'
                    for row in cursor.execute(
                            "select name, number from stats;"):
                        label_stats = label_stats + str(row[0]) + ": *" + str(row[1]) + "*\n"

                    reply = label_serv + "\n" + \
                            timedif + "\n" + \
                            memtotal + "\n" + \
                            memavail + "\n" + \
                            memuseperc + "\n" + \
                            diskused + "\n\n" + \
                            label_follow + "\n" + \
                            label_stats

                    bot.send_message(chat_id, reply, parse_mode='MARKDOWN', disable_web_page_preview=True)
            if chat_id in setmessage:
                if text != 'Массовая рассылка':
                    label = "Собщение для отправки:\n\n"
                    bot.send_message(chat_id, label + text,
                                          reply_markup=sendmarkup, disable_web_page_preview=True)
        else:
            if chat_id in userchatid:
                if chat_id in inorderheader:
                    cursor.execute(
                        "update orders set header = '" + text + "' where chat_id = "
                        + str(chat_id) + " and status = 0;")
                    conn.commit()
                    inorderheader.remove(chat_id)
                    bot.send_message(chat_id, "Шоу задано успешно", parse_mode='MARKDOWN',
                                          reply_markup=orderupdatemarkup)

                elif chat_id in inorderplace:
                    cursor.execute(
                        "update orders set place = '" + text + "' where chat_id = "
                        + str(chat_id) + " and status = 0;")
                    conn.commit()
                    inorderplace.remove(chat_id)
                    bot.send_message(chat_id, "Место проведения шоу задано успешно", parse_mode='MARKDOWN',
                                          reply_markup=orderupdatemarkup)
                elif chat_id in inordercomment:
                    cursor.execute(
                        "update orders set comment = '" + text + "' where chat_id = "
                        + str(chat_id) + " and status = 0;")
                    conn.commit()
                    inordercomment.remove(chat_id)
                    bot.send_message(chat_id, "Комментарий к заказу успешно задан", parse_mode='MARKDOWN',
                                          reply_markup=orderupdatemarkup)
                elif chat_id in inordertime:
                    if is_time(text):
                        inordertime.remove(chat_id)
                        cursor.execute(
                            "update orders set time = '" + text + "' where chat_id = "
                            + str(chat_id) + " and status = 0;")
                        conn.commit()
                        bot.send_message(chat_id, "Время заказа успешно задано", parse_mode='MARKDOWN',
                                         reply_markup=orderupdatemarkup)
                    else:
                        bot.send_message(chat_id,
                                         "Время необходимо задать в формате ЧЧ:ММ")
                elif chat_id in inlk:
                    if text == "Заказать прайслист":
                        try:
                            f = open('/root/bot_tele/etc/element_show_prices.pdf', 'rb', )
                            bot.send_document(chat_id, f)
                        except:
                            bot.send_message(chat_id, 'Приношу свои изминения, у меня нет актуального прайса! \n'
                                                      'Но не переживайте, я уже предупредил администратора!')
                            for admin_chat_id in adminchatid:
                                try:
                                    bot.send_chat_action(admin_chat_id, 'typing')
                                    bot.send_message(admin_chat_id, "Клиент запросил прайс, а файла у бота нет")
                                    bot.forward_message(admin_chat_id, chat_id, message.message_id)
                                except:
                                    print("Хм-м")
                    elif text == 'Назад':
                        inlk.remove(chat_id)
                        bot.send_message(chat_id, "Вернулись", reply_markup=elementmarkup_reg)
                    elif text == 'Предварительный заказ':
                        cursor = cursor.execute("select header, date, time, place, comment, rowid from orders "
                                                "where chat_id = " + str(chat_id) + " and status = 0"
                                                                                    " order by rowid desc limit 1;")
                        if len(cursor.fetchall()) == 0:
                            cursor.execute("INSERT INTO orders(chat_id, header) VALUES (" + str(chat_id)
                                       + ", '_Укажите шоу_');")
                            conn.commit()
                            bot.send_message(message.chat.id, order(header="_Укажите шоу_"), parse_mode='MARKDOWN',
                                             reply_markup=ordermarkup)
                        else:
                            for row in cursor.execute(
                                    "select header, date, time, place, comment, rowid from orders where chat_id = "
                                    + str(chat_id) + " and status = 0 order by rowid desc limit 1;"):
                                text = order(header=row[0], date=row[1], time=row[2], place=row[3], comment=row[4])
                                if check_order(row[0], row[1], row[2], row[3], row[4]):
                                    bot.send_message(chat_id, text,
                                                  parse_mode='MARKDOWN',
                                                  reply_markup=ordersendmarkup)
                                else:
                                    bot.send_message(chat_id, text,
                                                     parse_mode='MARKDOWN',
                                                     reply_markup=ordermarkup)

                else:
                    if text == "Про нас":
                        bot.send_message(chat_id,
                                         "Арт-лаборатория ELEMENT\n\nПрофессиональные шоу программы и анимация на"
                                         " любое торжество. Оригинальные, яркие, запоминающиеся!\n\n🔥    Огненное "
                                         "шоу\n💡    Светодиодное шоу\n ⚡️   Электрическое шоу\n 💨   Шоу Вет"
                                         "ра\n 🔦   Проекционное шоу\n🚨    Пиксельное шоу\n🎀    Шоу гимнасто"
                                         "к\n🔮    Контактное жонглирование\n🎪    Ходулисты, мимы, жонглеры, леди"
                                         "-фуршет, живые статуи",
                                         reply_markup=elementmarkup_soc)
                    elif text == "Proxy для любимого клиента":
                        bot.send_message(chat_id,
                                         "[Настройка Proxy](https://t.me/socks?server=195.201.136.255&"
                                         "port=1080&user=element_89179024466&pass=*****)",
                                         parse_mode='MARKDOWN', reply_markup=elementmarkup_reg)
                    elif text == 'Отписаться от бота':
                        userchatid.remove(chat_id)
                        if str(message.chat.first_name):
                            name = str(message.chat.first_name)
                        else:
                            name = str(message.chat.id)
                        cursor.execute("update chats set status = 0, name = '" + name + "' "
                                                                                        "where "
                                                                                        "chat_id = "
                                                                                        "" + str(chat_id) + ";")
                        conn.commit()
                        bot.send_message(chat_id, "Спасибо, что были с нами!",
                                         reply_markup=elementmarkup_unreg)
                    elif text == "Личный кабинет":
                        inlk.append(chat_id)
                        bot.send_message(chat_id, "Ваш личный кабинет", reply_markup=elementmarkup_lk)
            else:
                if text == 'Подписка на бота':
                    if chat_type == 'private':
                        userchatid.append(chat_id)
                        if str(message.chat.first_name):
                            name = str(message.chat.first_name)
                        else:
                            name = str(message.chat.id)
                        cursor.execute("update chats set status = 1, "
                                       "name = '" + name + "' where chat_id = " + str(chat_id) + ";")
                        conn.commit()
                        bot.send_message(chat_id, "Теперь Вам доступен личный кабинет и будет приходить рассылка",
                                         reply_markup=elementmarkup_reg)
                    else:
                        bot.send_message(chat_id, "Только для личных чатов",
                                         reply_markup=elementmarkup_unreg)
                elif text == "Про нас":
                    bot.send_message(chat_id,
                                     "Арт-лаборатория ELEMENT\n\nПрофессиональные "
                                     "шоу программы и анимация на любое торжество. "
                                     "Оригинальные, яркие, запоминающиеся!\n\n🔥    "
                                     "Огненное шоу\n💡    Светодиодное шоу\n ⚡️   Электрич"
                                     "еское шоу\n 💨   Шоу Ветра\n 🔦   Проекционное шоу\n🚨    Пиксел"
                                     "ьное шоу\n🎀    Шоу гимнасток\n🔮    Контактное жонглирование\n🎪    Ходули"
                                     "сты, мимы, жонглеры, леди-фуршет, живые статуи",
                                     reply_markup=elementmarkup_soc)
    conn.close()

@bot.callback_query_handler(func=lambda call: call.data == 'like')
def like(call):
    conn = sqlite3.connect("mydatabase.db")
    cursor = conn.cursor()
    cursor.execute("update stats set number = number+1 where stat = 'likes';")
    conn.commit()
    conn.close()
    bot.answer_callback_query(call.id, text="Спасибо за отзыв")
    bot.edit_message_reply_markup(call.from_user.id,
                          call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'dislike')
def dislike(call):
    conn = sqlite3.connect("mydatabase.db")
    cursor = conn.cursor()
    cursor.execute("update stats set number = number+1 where stat = 'dislikes';")
    conn.commit()
    conn.close()
    bot.answer_callback_query(call.id, text="Спасибо за отзыв")
    bot.edit_message_reply_markup(call.from_user.id,
                          call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data[0:13] == 'calendar-day-')
def get_day(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if(saved_date is not None):
        day=call.data[13:]
        date = datetime(int(saved_date[0]), int(saved_date[1]), int(day))
        conn = sqlite3.connect("mydatabase.db")
        cursor = conn.cursor()
        cursor.execute("update orders set date = '" + str(date.strftime("%d.%m.%Y")) + "' where chat_id = "
                       + str(call.message.chat.id) + " and status = 0;")
        conn.commit()
        for row in cursor.execute("select header, date, time, place, comment, rowid from orders where chat_id = "
                                  + str(call.message.chat.id) + " and status = 0 order by rowid desc limit 1;"):
            text = order(header=row[0], date=row[1], time=row[2], place=row[3], comment=row[4])
            if check_order(row[0], row[1], row[2], row[3], row[4]):
                bot.edit_message_text(text, call.from_user.id, call.message.message_id, parse_mode='MARKDOWN',
                                      reply_markup=ordersendmarkup)
                bot.answer_callback_query(call.id, text="Дата выбрана")
            else:
                bot.edit_message_text(text, call.from_user.id, call.message.message_id, parse_mode='MARKDOWN',
                                      reply_markup=ordermarkup)
                bot.answer_callback_query(call.id, text="Дата выбрана")
        conn.close()
    else:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'next-month')
def next_month(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if(saved_date is not None):
        year,month = saved_date
        month+=1
        if month>12:
            month=1
            year+=1
        date = (year,month)
        current_shown_dates[chat_id] = date
        markup= create_calendar(year,month)
        bot.edit_message_text(call.message.text, call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'previous-month')
def previous_month(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if(saved_date is not None):
        year,month = saved_date
        month-=1
        if month<1:
            month=12
            year-=1
        date = (year,month)
        current_shown_dates[chat_id] = date
        markup= create_calendar(year,month)
        bot.edit_message_text(call.message.text, call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'ignore')
def ignore(call):
    bot.answer_callback_query(call.id, text="")

@bot.callback_query_handler(func=lambda call: call.data == 'less_day')
def less_day(call):
    bot.answer_callback_query(call.id, text="Дата должна быть позже сегодня")

@bot.callback_query_handler(func=lambda call: call.data == 'back')
def less_day(call):
    bot.answer_callback_query(call.id, text="Отправка отменена")
    try:
        if call.from_user.username:
            text = "Отправка массовой рассылки отменена.\n\nПользователем: [" + call.from_user.first_name \
                   + "](https://t.me/" + call.from_user.username + ")"
        else:
            text = "Отправка массовой рассылки отменена"
        bot.edit_message_text(text, call.message.chat.id,
                          call.message.message_id, parse_mode='MARKDOWN', disable_web_page_preview=True)
        setmessage.remove(call.message.chat.id)
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'send')
def less_day(call):
    bot.answer_callback_query(call.id, text="Сообщения отправляются")
    try:
        k = 0
        text = call.message.text.lstrip('Собщение для отправки:\n\n')
        conn = sqlite3.connect("mydatabase.db")
        cursor = conn.cursor()
        for row in cursor.execute("select chat_id, name from chats where status = 1"):
            bot.send_message(row[0], hello(row[1]) + "\n\n" + text,
                         parse_mode='MARKDOWN', disable_web_page_preview=True, reply_markup=likemarkup)
            k = k + 1
        cursor.execute("update stats set number = number+" + str(k) + " where stat = 'mass_messages';")
        conn.commit()
        conn.close()
        if call.from_user.username:
            text = "*Отправлено: *\n\n" + text + "\n\nВсего отправлено: " + str(k) + " сообщений"\
                   + "\n\nПользователем: [" + call.from_user.first_name \
                   + "](https://t.me/" + call.from_user.username + ")"
        else:
            text = "*Отправлено: *\n\n" + text + "\n\nВсего отправлено: " + str(k) + " сообщений"\
                   + "\n\nПользователем: " + call.from_user.first_name
        bot.edit_message_text(text, call.message.chat.id,
                              call.message.message_id, parse_mode='MARKDOWN', disable_web_page_preview=True)
        setmessage.remove(call.message.chat.id)
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'order_back')
def less_day(call):
    try:
        bot.answer_callback_query(call.id, text="Предварительный заказ отменен")
        bot.edit_message_text("*Предварительный заказ отменен*", call.message.chat.id,
                          call.message.message_id, parse_mode='MARKDOWN', disable_web_page_preview=True)
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'order_header')
def less_day(call):
    inorderheader.append(call.message.chat.id)
    bot.send_message(call.message.chat.id, "Укажите название шоу из прайса", parse_mode='MARKDOWN',
                         disable_web_page_preview=True)

@bot.callback_query_handler(func=lambda call: call.data == 'order_place')
def less_day(call):
    try:
        inorderplace.append(call.message.chat.id)
        bot.send_message(call.message.chat.id, "Укажите место проведения шоу с указанием адреса", parse_mode='MARKDOWN',
                         disable_web_page_preview=True)
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'order_comment')
def less_day(call):
    try:
        inordercomment.append(call.message.chat.id)
        bot.send_message(call.message.chat.id, "Укажите комментарий", parse_mode='MARKDOWN',
                         disable_web_page_preview=True)
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'order_time')
def less_day(call):
    try:
        inordertime.append(call.message.chat.id)
        bot.send_message(call.message.chat.id, "Укажите время\nВ формате ЧЧ:ММ", parse_mode='MARKDOWN',
                         disable_web_page_preview=True)
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'order_date')
def less_day(call):
    try:
        bot.answer_callback_query(call.id, text="Выберете дату")
        now = datetime.now()  # Current date
        chat_id = call.message.chat.id
        date = (now.year, now.month)
        current_shown_dates[chat_id] = date  # Saving the current date in a dict
        markup = create_calendar(now.year, now.month)
        conn = sqlite3.connect("mydatabase.db")
        cursor = conn.cursor()
        for row in cursor.execute("select header, date, time, place, comment, rowid from orders where chat_id = "
                                  + str(call.message.chat.id) + " and status = 0 order by rowid desc limit 1;"):
            text = order(header=str(row[0]), date=str(row[1]), time=str(row[2]), place=str(row[3]), comment=str(row[4]))
        conn.close()
        bot.edit_message_text(text, call.message.chat.id,
                              call.message.message_id, parse_mode='MARKDOWN', reply_markup=markup)
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'order_refresh')
def less_day(call):
    try:
        conn = sqlite3.connect("mydatabase.db")
        cursor = conn.cursor()
        for row in cursor.execute("select header, date, time, place, comment, rowid from orders where chat_id = "
                                  + str(call.message.chat.id) + " and status = 0 order by rowid desc limit 1;"):
            text = order(header=str(row[0]), date=str(row[1]), time=str(row[2]), place=str(row[3]), comment=str(row[4]))
        if check_order(row[0], row[1], row[2], row[3], row[4]):
            bot.edit_message_text(text, call.from_user.id, call.message.message_id, parse_mode='MARKDOWN',
                                  reply_markup=ordersendmarkup)
        else:
            bot.edit_message_text(text, call.from_user.id, call.message.message_id, parse_mode='MARKDOWN',
                                  reply_markup=ordermarkup)
        conn.close()
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'order_send')
def less_day(call):
        bot.answer_callback_query(call.id, text="Заказ отправлен")
        if call.from_user.username:
            customer = "[" + call.from_user.first_name \
                   + "](https://t.me/" + call.from_user.username + ")"
        else:
            customer = call.from_user.first_name
        conn = sqlite3.connect("mydatabase.db")
        cursor = conn.cursor()
        for row in cursor.execute("select header, date, time, place, comment, rowid from orders where chat_id = "
                                  + str(call.message.chat.id) + " and status = 0 order by rowid desc limit 1;"):
            text = order(header=str(row[0]), date=str(row[1]), time=str(row[2]), place=str(row[3]),
                         comment=str(row[4]), customer=customer)
        cursor.execute("update orders set status = 1, customer = '" + customer + "' where chat_id = "
                       + str(call.message.chat.id) + " and status = 0;")
        conn.commit()
        conn.close()
        bot.edit_message_text(text + "\n *Предзаказ отправлен*", call.message.chat.id,
                              call.message.message_id, parse_mode='MARKDOWN', disable_web_page_preview=True)
        for admin_chat_id in adminchatid:
            bot.send_message(admin_chat_id, "Клиент сделал предзаказ\n\n" + text)

try:
    for admin_chat_id in adminchatid:
        bot.send_chat_action(admin_chat_id, 'typing')
        bot.send_message(admin_chat_id, "Я запущен!", reply_markup=adminmarkup)
except:
    pass

while True:
    try:
        bot.polling(none_stop=True)
    except:
        time.sleep(15)
