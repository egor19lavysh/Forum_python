import sqlite3
import uuid
import datetime

connection = sqlite3.connect('forum.db')
cursor = connection.cursor()

IS_AUTHENTIFICATED = False

#cursor.execute("DROP TABLE IF EXISTS Users")

#cursor.execute('''
#CREATE TABLE Users (
#    id INTEGER PRIMARY KEY AUTOINCREMENT,
#    name TEXT,
#    surname TEXT,
#    age INTEGER,
#    login TEXT UNIQUE,
#    salt TEXT,
#    password TEXT
#)
#''')

def hash(data : str):
    k = 2872834536
    sum = 0
    for n in range(len(data)):
        sum += ord(data[n]) * k ** n
    return hex(sum % 245390242324457893434353)


cursor.execute('''
CREATE TABLE IF NOT EXISTS Posts (
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT NOT NULL,
content TEXT NOT NULL,
author TEXT NOT NULL,
likes INTEGER,
timestamp TEXT
) 
'''
)

class Post:
    def __init__(self, title, text, author):
        cursor.execute("SELECT * FROM Posts WHERE title = ? AND author = ?", (title, author))
        if not cursor.fetchone():
            self.title = title
            self.text = text
            self.author = author
            self.likes = 0
            self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO Posts (title, content, author, likes, timestamp) VALUES (?, ?, ?, ?, ?)",
                           (self.title, self.text, self.author, self.likes, self.timestamp))
            connection.commit()
            print("пост успешно создан!")
        else:
            print("Ошибка!")

#Post("Java", "Java is hard", "Егор Лавыш")
#for i in cursor.execute("SELECT * FROM Posts").fetchall():
#    print(i)

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Comments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      post_id INTEGER NOT NULL,
      content TEXT,
      author TEXT,
      timestamp TEXT,
      FOREIGN KEY (post_id) REFERENCES Posts(id)
    )
  ''')

class Comment:
    def __init__(self, post_id : int, content, author):
        self.post_id = post_id
        self.content = content
        self.author = author
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("INSERT INTO Comments (post_id, content, author, timestamp) VALUES (?, ?, ?, ?)", (self.post_id, self.content, self.author, self.timestamp))
        connection.commit()
        print("Комментарий создан!")

#Comment(1, "I don't think so")
#for i in cursor.execute("SELECT * FROM Comments WHERE post_id = ?", (1,)).fetchall():
#    print(i)


class User:

    # Будет использоваться как регистрация
    def __init__(self, name : str, surname : str, age : int, login : str, password : str):
        cursor.execute("SELECT * FROM Users WHERE login = ?", (login,))
        if not cursor.fetchall():
            self.name = name
            self.surname = surname
            self.age = age
            self.login = login
            self.SALT = uuid.uuid4()
            self.password = hash(password + self.SALT.hex)
            cursor.execute("INSERT INTO Users (name, surname, age, login, salt, password) VALUES (?, ?, ?, ?, ?, ?)",
                           (self.name, self.surname, self.age, self.login, self.SALT.hex, self.password))
            connection.commit()
            print("Вы зарегистрированы!")
        else:
            print("Такой пользователь уже существует!")

    @staticmethod
    def authentificate(login, password):

        cursor.execute("SELECT * FROM Users WHERE login = ?", (login,))
        result = cursor.fetchone()
        if result[-1] == hash(password + result[-2]):
            global IS_AUTHENTIFICATED
            IS_AUTHENTIFICATED = True
            print("Вы авторизованы!")
        else:
            print("Произошла ошибка!")

    def create_post(self, title, content):
        global IS_AUTHENTIFICATED
        if IS_AUTHENTIFICATED:
            Post(title, content, f"{self.name} {self.surname}")
        else:
            print("Сначала авторизуйтесь!")

    def update_post(self, id, title, content):
        global IS_AUTHENTIFICATED
        if IS_AUTHENTIFICATED:
            result = cursor.execute("SELECT * FROM Posts WHERE id = ? AND author = ?", (id, f"{self.name} {self.surname}")).fetchone()
            if result:
                cursor.execute("UPDATE Posts SET title = ?, content = ? WHERE id = ?", (title, content, id))
                connection.commit()
            else:
                print("Возникла какая-то ошибка либо поста не существует")
        else:
            print("Сначала авторизуйтесь!")

    def delete_post(self, id):
        global IS_AUTHENTIFICATED
        if IS_AUTHENTIFICATED:
            cursor.execute("DELETE FROM Posts WHERE id = ?", (id,))
        else:
            print("Сначала авторизуйтесь!")


    def like_post(self, post_id):
        global IS_AUTHENTIFICATED
        if IS_AUTHENTIFICATED:
            result = cursor.execute("SELECT * FROM Posts WHERE id = ?", (post_id,)).fetchone()
            if result:
                cursor.execute("UPDATE Posts SET likes = ? WHERE id = ?", (result[-2] + 1, post_id))
                connection.commit()
            else:
                print("Возникла какая-то ошибка либо поста не существует")
        else:
            print("Сначала авторизуйтесь!")

    def comment_post(self, post_id, content):
        global IS_AUTHENTIFICATED
        if IS_AUTHENTIFICATED:
            result = cursor.execute("SELECT * FROM Posts WHERE id = ?", (post_id,)).fetchone()
            if result:
                Comment(post_id, content, f"{self.name} {self.surname}")
            else:
                print("Возникла какая-то ошибка либо поста не существует")
        else:
            print("Сначала авторизуйтесь!")


user = User("Иван", "Иванов", 18, "Ivan", "ivan123")
User.authentificate("Ivan", "ivan123")

user.create_post("Golang", "I want to learn GO. I think it's cool")
user.like_post(3)
user.comment_post(3, "In addition, I know only Python at this moment")

# Вывод
print("-------------------------------")
post = cursor.execute("SELECT * FROM Posts WHERE id = ?", (3,)).fetchone()
comment = cursor.execute("SELECT * FROM Comments WHERE post_id = ?", (3,)).fetchone()
print(f"Название: {post[1]}\nТекст: {post[2]}\nАвтор: {post[3]}\nЛайки: {post[4]}\nСоздан: {post[5]}")
print("-------------------------------")
print("Комментарии")
print(f"{comment[2]}\n{comment[3]}\n{comment[4]}")


connection.close()