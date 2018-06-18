import sqlite3
 
conn = sqlite3.connect("mydatabase.db") # или :memory: чтобы сохранить в RAM
cursor = conn.cursor()
 
# Создание таблицы
#cursor.execute("DROP TABLE chats;")
#cursor.execute("CREATE TABLE chats(chat_id text, status INTEGER DEFAULT 0, UNIQUE(chat_id) );")
#моя личка chat_id = '109099327'
cursor.execute("UPDATE chats SET status = 2 where chat_id = '-241874218';")

conn.commit()
conn.close()
