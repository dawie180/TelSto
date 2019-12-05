import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
from telepot.delegate import pave_event_space, per_chat_id, create_open
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
from geopy.geocoders import Nominatim


TOKEN = '320663225:AAFVzc1y_7dLUu97g1kqbw9PxkQU1aiSUMk'


SqlitePath = 'D:\pythonsqlite2.db'
geolocator = Nominatim(user_agent="Telsto")

#WelcomeMessage = "Welcome to <Placeholer>, please send us the name of your suburb or hit the GEO LOCATION button below"


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
 
 

 
def create_userlocationdb(conn, userlocationdb):
    """
    Create a new task
    :param conn:
    :param userlocationdb:
    :return:
    """
 
    sql = ''' INSERT INTO userlocationdb(user_id,name,latitude,longitude)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, userlocationdb)
    return cur.lastrowid


def select_all_tasks(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM userlocationdb")
 
    rows = cur.fetchall()
 
    for row in rows:
        print(row)
     

def CheckIfUserExistsInDb(id):
    try:
        conn = create_connection(SqlitePath)
        cursor = conn.cursor()
        print("Checking if User Exists On The DB")

        sql_select_query = """select * from userlocationdb where user_id = ?"""
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





class MessageCounter(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MessageCounter, self).__init__(*args, **kwargs)
        self._count = 0

    def on_chat_message(self, msg):
        self._count += 1
        #self.sender.sendMessage(self._count)
        try:
            if msg["text"] == "/start":
                self.sender.sendMessage("Hi " + msg["from"]["first_name"] + ",\n\nWelcome to the TelSto, Please send us the name of your suburb or click the Geo Location button below...",
                                    reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                        keyboard=[
                                            [KeyboardButton(text="\U0001f4cd GEO LOCATION \U0001f4cd", request_location=True)]
                                        ]
                                    ))
        except KeyError as error:   
                pass  











#def handle(msg):
#    content_type, chat_type, chat_id = telepot.glance(msg)
#    Test = msg    
#    #print (Test)

#    try:
#        if msg["location"]:
#            print ("\n""Message with Location Data recieved")
#            if CheckIfUserExistsInDb(msg["from"]["id"])==False:
#                print("user_id not found, creating new Sqlite record...")
#                sqliteinitialinfo = (msg["from"]["id"], msg["from"]["first_name"], msg["location"]["latitude"], msg["location"]["longitude"])
#                conn = create_connection(SqlitePath)
#                create_userlocationdb(conn, sqliteinitialinfo)
#                conn.commit()
#                print ("created new entry in DB")
#                conn = create_connection(SqlitePath)
#                select_all_tasks(conn)
#            else:
#                print ("user_id already exists, updating location and name in DB")
#                conn = create_connection(SqlitePath)
#                cur = conn.cursor()
#                UpdatedName = msg["from"]["first_name"]
#                user_id = msg["from"]["id"]
#                UpdatedsLatitude = msg["location"]["latitude"]
#                UpdatedLongitude = msg["location"]["longitude"]
#                cur.execute('UPDATE userlocationdb SET name = ?, latitude = ?, longitude = ? WHERE user_id = ?', (UpdatedName, UpdatedsLatitude, UpdatedLongitude, user_id))
#                conn.commit()
#                print ("updated DB entry success")
#                conn = create_connection(SqlitePath)
#                select_all_tasks(conn)
            
#    except KeyError as error:   
#        pass
    
#    if msg["text"] != "/start":
#        if CheckIfUserExistsInDb(msg["from"]["id"])==False:
#            print ("Search suburb")
#            location = geolocator.geocode(msg["text"])
#            print(location.address)
#            print((location.latitude, location.longitude))
#            bot.sendMessage(chat_id, location.address + "\n\nIs this correct?",
#                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
#                                    keyboard=[
#                                        [KeyboardButton(text="Yes Sir \U0001f44d")],
#                                        [KeyboardButton(text="Oops, Let me try again \U0001f629" )]
#                                ]
#                            ))



#    try:
#        if msg["text"] == "/start":
#            bot.sendMessage(chat_id, "Hi " + msg["from"]["first_name"] + ",\n\nWelcome to the TelSto, Please send us the name of your suburb or click the Geo Location button below...",
#                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
#                                    keyboard=[
#                                        [KeyboardButton(text="\U0001f4cd GEO LOCATION \U0001f4cd", request_location=True)]
#                                    ]
#                                ))
#    except KeyError as error:   
#        pass  






def main():
    print ("Program Start")

    

main()

bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, MessageCounter, timeout=10),
])

MessageLoop(bot).run_as_thread()


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


