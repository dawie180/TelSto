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
SqlitePath = 'D:\pythonsqlite.db'


WelcomeMessage = "Welcome to <Placeholer>, please send us the name of your suburb or hit the GEO LOCATION button below"

sql_create_user_table = """CREATE TABLE IF NOT EXISTS user (
                                    id integer PRIMARY KEY,
                                    user_id integer NOT NULL,
                                    name text NOT NULL,
                                    latitude text NOT NULL,
                                    longitude text NOT NULL
                                );"""

def create_intitaldb(conn, task):
    """
    Create a new task
    :param conn:
    :param task:
    :return:
    """
 
    sql = ''' INSERT INTO tasks(user_id,name,latitude,longitude)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, task)
    return cur.lastrowid


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Sqlite db Opened v" + sqlite3.version)
        return conn
    except Error as e:
        print(e)
 
    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def select_all_tasks(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks")
 
    rows = cur.fetchall()
 
    for row in rows:
        print(row)


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    Test = msg    
    #print (Test)

    try:
        if msg["location"]:
            print ("\n""location found")
            sqliteinitialinfo = (msg["from"]["id"], msg["from"]["first_name"], msg["location"]["latitude"], msg["location"]["longitude"])
            print ("saving to sqlite database")
            conn = create_connection(SqlitePath)
            create_intitaldb(conn, sqliteinitialinfo)
            print ("saved to sqlite database")
            select_all_tasks(conn)
            conn.close()
    except KeyError as error:   
        pass
    

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





def main():
    print ("Setting Up Sqlite Database")
    conn = create_connection(SqlitePath)
            
    if conn is not None:
            # create user database table
            create_table(conn, sql_create_user_table)
            print("Sqlite db Tables Created")
            conn.close()
    else:
            print("Error! cannot create the database connection.")




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


