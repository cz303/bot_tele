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
import operator

logging.basicConfig(filename="logs/tele_bot.log", level=logging.INFO)

current_shown_dates={}

setmessage = []
viewstatic = []
inlk = []

userchatid = []
adminchatid = []
graphstart = datetime.now()

stopmarkup = types.ReplyKeyboardMarkup(one_time_keyboard=False)
stopmarkup.add('Хватит')

elementmarkup_unreg = types.ReplyKeyboardMarkup(one_time_keyboard=False)
elementmarkup_unreg.add('Про нас', 'Подписка на бота')

elementmarkup_soc = types.InlineKeyboardMarkup()
callback_button = types.InlineKeyboardButton(text="Instagram", url="https://www.instagram.com/element_show/")
elementmarkup_soc.add(callback_button)
callback_button = types.InlineKeyboardButton(text="ВКонтакте", url="https://vk.com/club92907131")
elementmarkup_soc.add(callback_button)
callback_button = types.InlineKeyboardButton(text="Официальный сайт", url="http://deliriumshow.com/")
elementmarkup_soc.add(callback_button)

adminmarkup = types.ReplyKeyboardMarkup(one_time_keyboard=False)
adminmarkup.add('Массовая рассылка', 'Статистика')

yn_markup = types.ReplyKeyboardMarkup(one_time_keyboard=False)
yn_markup.add('Да', 'Нет', 'Хватит')

yn_only_markup = types.ReplyKeyboardMarkup(one_time_keyboard=False)
yn_only_markup.add('Да', 'Нет')

elementmarkup_reg = types.ReplyKeyboardMarkup(one_time_keyboard=False)
elementmarkup_reg.add('Про нас', 'Личный кабинет', 'Proxy для любимого клиента', 'Отписаться от бота')

elementmarkup_unreg = types.ReplyKeyboardMarkup(one_time_keyboard=False)
elementmarkup_unreg.add('Про нас', 'Подписка на бота')

elementmarkup_lk = types.ReplyKeyboardMarkup(one_time_keyboard=False)
elementmarkup_lk.add('Заказать прайслист', 'Календарь', 'Назад')

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
                    bot.send_message(chat_id, "Какое сообщение отправить?", reply_markup=stopmarkup)
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
                            label_follow + "\n\n" + \
                            label_stats

                    bot.send_message(chat_id, reply, parse_mode='MARKDOWN', disable_web_page_preview=True)
            if chat_id in setmessage:
                if text == 'Хватит':
                    setmessage.remove(chat_id)
                    bot.send_message(chat_id, "Всё закончил", reply_markup=adminmarkup)
                elif text != 'Массовая рассылка':
                    setmessage.remove(chat_id)
                    k = 0
                    for row in cursor.execute("select chat_id, name from chats where status = 1"):
                        bot.send_message(row[0], hello(row[1]) + "\n\n" + text,
                                         parse_mode='MARKDOWN', disable_web_page_preview=True, reply_markup=likemarkup)
                        k = k + 1
                    cursor.execute("update stats set number = number+" + str(k) + " where stat = 'mass_messages';")
                    conn.commit()
                    bot.send_message(chat_id, "Отправил *" + str(k) + "* сообщений, "
                                                                      "продолжим...",
                                     parse_mode='MARKDOWN', reply_markup=adminmarkup)
        else:
            if chat_id in userchatid:
                if chat_id in inlk:
                    if text == "Заказать прайслист":
                        try:
                            f = open('/root/bot_tele/etc/list.xml', 'rb', )
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
                    elif text == 'Календарь':
                        now = datetime.now()  # Current date
                        chat_id = message.chat.id
                        date = (now.year, now.month)
                        current_shown_dates[chat_id] = date  # Saving the current date in a dict
                        markup = create_calendar(now.year, now.month)
                        bot.send_message(message.chat.id, "Пожалуйста, выберете дату", reply_markup=markup)
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
    bot.edit_message_text(call.message.text, call.from_user.id,
                          call.message.message_id, parse_mode='MARKDOWN', disable_web_page_preview=True)

@bot.callback_query_handler(func=lambda call: call.data == 'dislike')
def dislike(call):
    conn = sqlite3.connect("mydatabase.db")
    cursor = conn.cursor()
    cursor.execute("update stats set number = number+1 where stat = 'dislikes';")
    conn.commit()
    conn.close()
    bot.answer_callback_query(call.id, text="Спасибо за отзыв")
    bot.edit_message_text(call.message.text, call.from_user.id,
                          call.message.message_id, parse_mode='MARKDOWN', disable_web_page_preview=True)

@bot.callback_query_handler(func=lambda call: call.data[0:13] == 'calendar-day-')
def get_day(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if(saved_date is not None):
        day=call.data[13:]
        date = datetime(int(saved_date[0]),int(saved_date[1]),int(day))
        bot.edit_message_text("Вы выбрали: *" + str(date.strftime("%d.%m.%Y")) + "*", call.from_user.id, call.message.message_id, parse_mode='MARKDOWN')
        bot.answer_callback_query(call.id, text="Дата выбрана")

    else:
        #Do something to inform of the error
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
        bot.edit_message_text("Пожалуйста, выберете дату", call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        #Do something to inform of the error
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
        bot.edit_message_text("Пожалуйста, выберете дату", call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        #Do something to inform of the error
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'ignore')
def ignore(call):
    bot.answer_callback_query(call.id, text="")

@bot.callback_query_handler(func=lambda call: call.data == 'less_day')
def less_day(call):
    bot.answer_callback_query(call.id, text="Дата должна быть позже сегодня")


for admin_chat_id in adminchatid:
    bot.send_chat_action(admin_chat_id, 'typing')
    bot.send_message(admin_chat_id, "Я запущен!", reply_markup=adminmarkup)
bot.polling()
