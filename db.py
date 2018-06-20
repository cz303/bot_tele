import sqlite3
 
conn = sqlite3.connect("mydatabase.db") # или :memory: чтобы сохранить в RAM
cursor = conn.cursor()
 
# Создание таблицы "Чаты"
cursor.execute("DROP TABLE chats;")
cursor.execute("CREATE TABLE chats(chat_id text, name text dafault 'Your name', status INTEGER DEFAULT 0, UNIQUE(chat_id) );")
#моя личка chat_id = '109099327'
#cursor.execute("UPDATE chats SET status = 2 where chat_id = '-241874218';")

# Создание таблицы "Заказы"

#cursor.execute("DROP TABLE registed_chats;")
#cursor.execute("CREATE TABLE registed_chats(chat_id text, status INTEGER DEFAULT 0, name text,  UNIQUE(chat_id) );")

conn.commit()
conn.close()
