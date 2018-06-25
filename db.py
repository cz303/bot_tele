import sqlite3
 
conn = sqlite3.connect("mydatabase.db") # или :memory: чтобы сохранить в RAM
cursor = conn.cursor()
 
# Создание таблицы "Чаты"
#cursor.execute("DROP TABLE chats;")
#cursor.execute("CREATE TABLE chats(chat_id real, name text DEFAULT 'Your name', status INTEGER DEFAULT 0, UNIQUE(chat_id) );")
#моя личка chat_id = '109099327'
#cursor.execute("UPDATE chats SET status = 2 where chat_id = -241874218;")

# Создание таблицы "Статистики"
#cursor.execute("DROP TABLE stats;")
#cursor.execute("CREATE TABLE stats(stat text, number INTEGER DEFAULT 0, name text,  UNIQUE(stat) );")
#cursor.execute("INSERT INTO stats(stat,name) VALUES ('likes','Лайков');")
#cursor.execute("INSERT INTO stats(stat,name) VALUES ('dislikes','Дизлайков');")
#cursor.execute("INSERT INTO stats(stat,name) VALUES ('messages','Всего получено сообщений');")
#cursor.execute("INSERT INTO stats(stat,name) VALUES ('mass_messages','Всего отправлено сообщений в рассылках');")


# Создание таблицы "Заказы"
cursor.execute("DROP TABLE registed_orders;")
cursor.execute("CREATE TABLE orders(chat_id real, status INTEGER DEFAULT 0, header text DEFAULT 'None',date text DEFAULT 'None',time text DEFAULT 'None',place text DEFAULT 'None',comment text DEFAULT 'None',customer text DEFAULT 'None');")

conn.commit()
conn.close()


