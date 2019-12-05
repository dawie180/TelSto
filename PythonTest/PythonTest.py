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

#bot = telepot.Bot('320663225:AAFVzc1y_7dLUu97g1kqbw9PxkQU1aiSUMk') #TelSto
bot = telepot.Bot('884457382:AAGrGHxVplHPdM5tCT7MfS6cgueeTZKGtP4') #Store1
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
 
 

 
def create_Users(conn, Users):
    """
    Create a new task
    :param conn:
    :param Users:
    :return:
    """
 
    sql = ''' INSERT INTO Users(user_id ,name,latitude,longitude)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, Users)
    return cur.lastrowid


def select_all_tasks(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users")
 
    rows = cur.fetchall()
 
    for row in rows:
        print(row)
     

def CheckIfUsersExistsInDb(id):
    try:
        conn = create_connection(SqlitePath)
        cursor = conn.cursor()
        print("Checking if Users Exists On The DB")


        sql_select_query = """select * from Users where user_id  = ?"""
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
            print("The SQLite connection is closed")

def updateSqliteTable(user_id , name, longitude, latitude):
    try:
        conn = create_connection(SqlitePath)
        cursor = conn.cursor()
        print("Connected to SQLite")

        sql_update_query = """Update Users set name = "MCD", longitude = '1',latitude = '2'  where user_id  =297725915"""
        cursor.execute(sql_update_query)
        conn.commit()
        print("Record Updated successfully ")
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to update sqlite table", error)
    finally:
        if (conn):
            conn.close()
            print("The SQLite connection is closed")




def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    Test = msg    
    #print (Test)

    try:
        if msg["location"]:
            print ("\n""Message with Location Data recieved")
            if CheckIfUsersExistsInDb(msg["from"]["id"])==False:
                print("user_id  not found, creating new Sqlite record...")
                sqliteinitialinfo = (msg["from"]["id"], msg["from"]["first_name"], msg["location"]["latitude"], msg["location"]["longitude"])
                print ("saving to sqlite database")
                conn = create_connection(SqlitePath)
                create_Users(conn, sqliteinitialinfo)
                conn.commit()
                print ("saved to sqlite database")
                conn = create_connection(SqlitePath)
                select_all_tasks(conn)
            else:
                print ("user_id  already exists, updating location and name")
                sqliteinitialinfo = (msg["from"]["id"], msg["from"]["first_name"], msg["location"]["latitude"], msg["location"]["longitude"])
                print ("saving to sqlite database")
                conn = create_connection(SqlitePath)
                updateSqliteTable(297725915, "Awe", 10000, 10000)
                print ("updated table to sqlite database")
                conn = create_connection(SqlitePath)
                select_all_tasks(conn)
            
    except KeyError as error:   
        pass
    
    #if msg["text"]:
    #     user_id  = msg["from"]["id"]





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
    print ("Checking if Sqlite Database exists...")
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


