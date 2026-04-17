import sqlite3
conn = sqlite3.connect("blog.db")
cursor = conn.cursor()


# all users table 

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)""")

# ALL BLOG TABLE 

cursor.execute("""
CREATE TABLE IF NOT EXISTS blogs (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, image TEXT, author TEXT)""")


conn.commit()

conn.close()

print('database created')