import mailbox
import email
import sqlite3
from email.header import Header, decode_header, make_header


def getbody(message):  # getting plain text 'email body'
    body = None
    if message.is_multipart():
        for part in message.walk():
            if part.is_multipart():
                continue
            elif part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True).decode('utf-8', 'ignore')
    elif message.get_content_type() == 'text/plain':
        body = message.get_payload(decode=True).decode('utf-8', 'ignore')
    return body


def crateDB():
    conn = sqlite3.connect('test.db')
    print("Opened database successfully")
    c = conn.cursor()
    c.execute('''CREATE TABLE BLOG
       (ID INTEGER PRIMARY KEY AUTOINCREMENT,
       NAME           TEXT    NOT NULL,
       CONTENT       TEXT);''')
    print("Table created successfully")
    conn.commit()
    conn.close()


def openDB():
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    print("Opened database successfully")
    return c, conn


def closeDB(conn):
    conn.commit()
    print("Records created successfully")
    conn.close()


def insert(con, title, content):
    con.execute("INSERT INTO BLOG (NAME,CONTENT) VALUES (?,?)",
                (title, content))


mbox = mailbox.mbox('./INBOX.partial.mbox/mbox')
crateDB()
print(mbox)
i = 1
c, conn = openDB()
for message in mbox:
    print(i)
    print("from   :", message['from'])
    print("subject:", message['subject'])
    title = str(make_header(decode_header(message['subject'])))
    print("title:", title)
    if "博客" in title and "Re:" not in title:
        content = getbody(message)
        print("message:", content)
        insert(c, title, content)
    print("**************************************")
    i += 1
closeDB(conn)
