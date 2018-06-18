import sqlite3
 
conn = sqlite3.connect("mydatabase.db") # или :memory: чтобы сохранить в RAM
cursor = conn.cursor()
 
# Создание таблицы
#cursor.execute("DROP TABLE chats;")
#cursor.execute("CREATE TABLE chats(chat_id text, is_admin INTEGER DEFAULT 0, is_registered_user INTEGER DEFAULT 0, UNIQUE(chat_id) );")
#cursor.execute("UPDATE chats SET is_admin = '1' where chat_id = '109099327';")
#cursor.execute("UPDATE chats SET is_admin = '1' where chat_id = '-311521038';")
cursor.execute("UPDATE chats SET is_admin = '1' where chat_id = '-241874218';")

conn.commit()
conn.close()
