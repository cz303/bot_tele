from telebot import types
import calendar
import locale
from datetime import datetime



def create_calendar(year,month):
    markup = types.InlineKeyboardMarkup()
    #First row - Month and Year
    row=[]
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    row.append(types.InlineKeyboardButton(calendar.month_name[month]+" "+str(year),callback_data="ignore"))
    markup.row(*row)
    #Second row - Week Days
    week_days=["П","В","С","Ч","П","С","В"]
    row=[]
    for day in week_days:
        row.append(types.InlineKeyboardButton(day,callback_data="ignore"))
    markup.row(*row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row=[]
        for day in week:
            if(day==0):
                row.append(types.InlineKeyboardButton(" ",callback_data="ignore"))
            else:
                row.append(types.InlineKeyboardButton(str(day),callback_data="calendar-day-"+str(day)))
        markup.row(*row)
    #Last row - Buttons
    row=[]
    now = datetime.now()
    if now.strftime("%m.%Y") > datetime.strptime(month+year, "%m.%Y"):
        row.append(types.InlineKeyboardButton("<",callback_data="previous-month"))
    else:
        row.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
    row.append(types.InlineKeyboardButton(" ",callback_data="ignore"))
    row.append(types.InlineKeyboardButton(">",callback_data="next-month"))
    markup.row(*row)
    return markup