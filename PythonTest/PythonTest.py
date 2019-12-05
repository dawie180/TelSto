import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
from pprint import pprint
#import ConfigParser
import threading
from threading import Thread
import time
import datetime
from datetime import datetime
from datetime import timedelta
import sqlite3
from sqlite3 import Error

bot = telepot.Bot('320663225:AAFVzc1y_7dLUu97g1kqbw9PxkQU1aiSUMk')
SqlitePath = 'C:\TelSto.db'


WelcomeMessage = "Welcome to <Placeholer>, please send us the name of your suburb or hit the GEO LOCATION button below"


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
 
    return conn
 
 

 
def create_User(conn, User):
    """
    Create a new task
    :param conn:
    :param User:
    :return:
    """
 
    sql = ''' INSERT INTO User(Telegram_ID,name,Latitude,Longitude)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, User)
    return cur.lastrowid


def select_all_tasks(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM User")
 
    rows = cur.fetchall()
 
    for row in rows:
        print(row)
     

def CheckIfUserExistsInDb(id):
    try:
        conn = create_connection(SqlitePath)
        cursor = conn.cursor()
        print("Checking if User Exists On The DB")

        sql_select_query = """select * from User where Telegram_ID = ?"""
        cursor.execute(sql_select_query, (id,))
        records = cursor.fetchone()
        cursor.close()
        if records == None:
            return False
        else:
            return True

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if (conn):
            conn.close()
            #print("The SQLite connection is closed")

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    Test = msg    
    #print (Test)

    try:
        if msg["location"]:
            print ("\n""Message with Location Data recieved")
            if CheckIfUserExistsInDb(msg["from"]["id"])==False:
                print("Telegram_ID not found, creating new Sqlite record...")
                sqliteinitialinfo = (msg["from"]["id"], msg["from"]["first_name"], msg["location"]["Latitude"], msg["location"]["Longitude"])
                conn = create_connection(SqlitePath)
                create_User(conn, sqliteinitialinfo)
                conn.commit()
                print ("created new entry in DB")
                conn = create_connection(SqlitePath)
                select_all_tasks(conn)
            else:
                print ("Telegram_ID already exists, updating location and name in DB")
                conn = create_connection(SqlitePath)
                cur = conn.cursor()
                UpdatedName = msg["from"]["first_name"]
                Telegram_ID = msg["from"]["id"]
                UpdatedsLatitude = msg["location"]["Latitude"]
                UpdatedLongitude = msg["location"]["Longitude"]
                cur.execute('UPDATE User SET name = ?, Latitude = ?, Longitude = ? WHERE Telegram_ID = ?', (UpdatedName, UpdatedsLatitude, UpdatedLongitude, Telegram_ID))
                conn.commit()
                print ("updated DB entry success")
                conn = create_connection(SqlitePath)
                select_all_tasks(conn)
            
    except KeyError as error:   
        pass
    #if msg["text"]:
    #     Telegram_ID = msg["from"]["id"]
    try:
        if msg["text"] == "/start":
            bot.sendMessage(chat_id, WelcomeMessage,
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="\U0001f4cd GEO LOCATION \U0001f4cd", request_location=True)]
                                    ]
                                ))
    except KeyError as error:   
        pass  





#class MessageCounter(telepot.helper.ChatHandler):
#    def __init__(self, *args, **kwargs):
#        super(MessageCounter, self).__init__(*args, **kwargs)
#        self._count = 0

#    def on_chat_message(self, msg):
#        self._count += 1
#        self.sender.sendMessage(self._count)

#TOKEN = sys.argv[1]  # get token from command-line

#bot = telepot.DelegatorBot(TOKEN, [
#    pave_event_space()(
#        per_chat_id(), create_open, MessageCounter, timeout=10),
#])
#MessageLoop(bot).run_as_thread()

#while 1:
#    time.sleep(10)

def main():
    print ("Program Start")
    #conn = create_connection(SqlitePath)
    
    main()
    MessageLoop(bot, handle).run_as_thread()




#Start
#Welcome Message
#Set location
#Store list based on location - drop off 
#Stores that offer courier
#Store Select
#Inventory display 
#- Standard text
#- Image display included
#- video display EXTRA POINTS



# DB and Table SCHEMA
# DB - TelSto.DB

# TABLES - 1) User
    #Columns => Telegram_ID         - primary key
    #Columns => Telegram_ID     - varchar(128)
    #Columns => Username        - varchar(128)
    #Columns => ContactNumber   - varchar(128)
    #Columns => Seller          - bit
    #Columns => Buyer           - bit
    #Columns => Latitude             - varchar(128)
    #Columns => Longitude            - varchar(128)
    #Columns => CreateDateTime  - DateTime
    #Columns => SaveDateTime    - DateTime



