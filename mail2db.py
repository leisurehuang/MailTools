import mailbox
import email
import sqlite3
import jinja2
import argparse
import collections
import email.parser
import email.policy
import os.path
from email.header import Header, decode_header, make_header

filePath = './INBOX.partial.mbox/mbox'
dbName = 'test.db'
searchKey = '博客'
ignoreKey = 'Re:'

#############################
# DB information
# table name 'BLOG'
# table keys 'ID, NAME, CREATEDATE, CONTENT'
#######################################


template = jinja2.Template("""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
  </head>
  <body>
  {% for message in messages %}
  {% for key, value in message.header %}
  {% if key in header_filter %}
  <div><strong>{{ key }}</strong>: {{ value }}</div>
  {% endif %}
  {% endfor %}
  <hr/>
  {% if message.is_html %}
  {{ message.body|safe }}
  {% else %}
  <pre>{{ message.body }}</pre>
  {% endif %}
  {% if not loop.last %}
  <hr/>
  {% endif %}
  {% endfor %}
</body>
</html>
""".strip(), trim_blocks=True, lstrip_blocks=True, autoescape=True)

# Command line options
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--plain', action='store_true',
                    help="prefer plain text over html")
parser.add_argument('-o', '--outfile', nargs='?',
                    type=argparse.FileType('w'),
                    default='-',
                    help='output html file')
args = parser.parse_args()


def crateDB():
    conn = sqlite3.connect(dbName)
    print("Opened database successfully")
    c = conn.cursor()
    c.execute('''CREATE TABLE BLOG
       (ID INTEGER PRIMARY KEY AUTOINCREMENT,
       NAME           TEXT    NOT NULL,
       CREATEDATE   DATE,
       CONTENT       TEXT);''')
    print("Table created successfully")
    conn.commit()
    conn.close()


def openDB():
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    print("Opened database successfully")
    return c, conn


def closeDB(conn):
    conn.commit()
    print("closeDB successfully")
    conn.close()


def insert(con, title, content, date):
    con.execute("INSERT INTO BLOG (NAME,CONTENT,CREATEDATE) VALUES (?,?,?)",
                (title, content, date))


# remove and create new DB
os.path.exists(dbName) and os.remove(dbName)
crateDB()
c, conn = openDB()

reverse = -1 if args.plain else 1
preferencelist = ('html', 'plain')[::reverse]

mbox = mailbox.mbox(filePath)
print(mbox)

for message in mbox:
    title = str(make_header(decode_header(message['subject'])))
    if searchKey in title and ignoreKey not in title:
        message_info = collections.defaultdict(dict)
        # Message parser
        msg_parser = email.parser.BytesFeedParser(policy=email.policy.default)
        msg_parser.feed(message.as_bytes())
        msg = msg_parser.close()
        # Header
        message_info['header'] = msg.items()
        sendDate = msg['Date']
        # Body
        simplest = msg.get_body(preferencelist=preferencelist)
        message_info['is_html'] = simplest.get_content_type() == 'text/html'
        message_info['body'] = simplest.get_content()
        # Add result to collection
        info = {
            'title': '',
            'header_filter': [
                'From',
                'Date', ],
            'messages': [],
        }

        info['messages'].append(message_info)
        info['title'] = title
        content = template.render(info)
        print("message:", content)
        insert(c, title, content, sendDate)
    print("**************************************")
closeDB(conn)
