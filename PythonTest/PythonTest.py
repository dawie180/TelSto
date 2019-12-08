import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
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
import string
import random


TOKEN = '320663225:AAFVzc1y_7dLUu97g1kqbw9PxkQU1aiSUMk'


SqlitePath = 'D:\pythonsqlite2.db'
geolocator = Nominatim(user_agent="Telsto")



def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(size))

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
 
 

 
def save_preapproved_user_info_to_db(conn, User):
    """
    Create a new task
    :param conn:
    :param User:
    :return:
    """
 
    sql = ''' INSERT INTO User(User_ID,Telegram_ID, TGReferral_ID, TGReferralState, SaveDateTime)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, User)
    return cur.lastrowid
    print ("Wrote To Sql")


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
        print("\nChecking if User Exists On The DB")

        sql_select_query = """select * from User where User_ID = ?"""
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

global records  
def CheckIfReferralIDExistsInDb(Ref_ID):
    try:
        conn = create_connection(SqlitePath)
        cursor = conn.cursor()
        print("\nChecking if User Exists On The DB")

        sql_select_query =  """SELECT User_ID from User where TGReferralSelf_ID = ?"""
        cursor.execute(sql_select_query, (Ref_ID,))
        records = cursor.fetchone()
        cursor.close()
        if records == None:
            return False
        else:
            return records
        

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if (conn):
            conn.close()
            #print("The SQLite connection is closed")

UnregisteredUserState=0

class MessageCounter(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MessageCounter, self).__init__(*args, **kwargs)
        self._count = 0
    

    def on_chat_message(self, msg):
        self._count += 1
        #self.sender.sendMessage(self._count)
        try:
            if msg["text"] == "/start":
                global UnregisteredUserState
                global NameForApproval
                if CheckIfUserExistsInDb(msg["from"]["id"])==False:
                    self.sender.sendMessage("Hi " + "*"+msg["from"]["first_name"]+"*" + ",\n\nWelcome to the TelSto, we use a referal registration system so please send us your name which will be sent to your referal for approval..", reply_markup=ReplyKeyboardRemove(), parse_mode= 'Markdown')
                    UnregisteredUserState=1
                else:
                    print ("Welcome Back")

            if msg["text"] != "/start":
                if UnregisteredUserState==1:
                    UnregisteredUserState=2
                    NameForApproval =msg['text']
                    self.sender.sendMessage("*"+ NameForApproval + "*" + "\n\nIs this name correct? This name will be sent to your referal for approval, in the next step we will need your referal code", parse_mode= 'Markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="Yes Sir \U0001f44d")],
                                        [KeyboardButton(text="Oops, Let me try again \U0001f629" )]
                                ]
                            ))
                
                
                global ReferralCode
                if UnregisteredUserState==3:
                    UnregisteredUserState=4
                    ReferralCode =msg['text']
                    self.sender.sendMessage("Name:\t" + "*"+ NameForApproval + "*" + "\nCode:\t\t" + "*"+ReferralCode+"*" + "\n\nIs this correct? These details will be now sent to your referal for approval", parse_mode= 'Markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="Yes Sir \U0001f44d")],
                                        [KeyboardButton(text="Oops, Let me try again \U0001f629" )],
                                        [KeyboardButton(text="Cancel, im scared \u26d4\ufe0f" )]
                                ]
                            ))
                
                if msg["text"] == "Yes Sir \U0001f44d" and UnregisteredUserState==4:
                    preapproved_sql = (msg["from"]["id"], NameForApproval, ReferralCode, "AWAITING BUYER APPROVAL", datetime.now())         #User(User_ID,Telegram_ID, TGReferral_ID, TGReferralState, SaveDateTime)
                    if CheckIfReferralIDExistsInDb(ReferralCode) != False:
                        bot.sendMessage(CheckIfReferralIDExistsInDb(ReferralCode)[0], "Hi, " + "*"+NameForApproval+"*" + " needs approval, select appropriate answer below...", parse_mode= 'Markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="\u2705  " + "Yes i know " + NameForApproval + "  \u2705" )],
                                        [KeyboardButton(text="\u26d4\ufe0f  " + "No i don't know " + NameForApproval + "  \u26d4\ufe0f" )]
                                ]
                            ))

                        self.sender.sendMessage("Sent for approval, wait for response", parse_mode= 'Markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="Resend Approval Request (Wait 1 Hour)" )],
                                ]
                            ))

                        conn = create_connection(SqlitePath)
                        save_preapproved_user_info_to_db(conn, preapproved_sql)
                        conn.commit()

                    else:
                        UnregisteredUserState=4
                        self.sender.sendMessage("Referral Code " + "*"+ReferralCode+"*" + " not found, please send another code", parse_mode= 'Markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="Cancel, im scared \u26d4\ufe0f" )]
                                ]
                            ))
                        

                    #conn = create_connection(SqlitePath)
                    #save_preapproved_user_info_to_db(conn, preapproved_sql)
                    #conn.commit()
                    #select_all_tasks(conn)
                    #print (CheckIfReferralIDExistsInDb(ReferralCode))


                if msg["text"] == "Cancel, im scared \u26d4\ufe0f" and UnregisteredUserState==4:                  
                    if CheckIfUserExistsInDb(msg["from"]["id"])==False:
                        self.sender.sendMessage("Hi " + "*"+msg["from"]["first_name"]+"*" + ",\n\nWelcome to the TelSto, we use a referal registration system so please send us your name which will be sent to your referal for approval..", reply_markup=ReplyKeyboardRemove(), parse_mode= 'Markdown')
                        UnregisteredUserState=1
                    else:
                        print ("Welcome Back")

                if msg["text"] ==  "Oops, Let me try again \U0001f629" and UnregisteredUserState==4:
                    UnregisteredUserState=3
                    self.sender.sendMessage("Next please send us your referal code, this you should have received from somone else is registered to the platform", reply_markup=ReplyKeyboardRemove())



            if msg["text"] == "Oops, Let me try again \U0001f629" and UnregisteredUserState==2:
                UnregisteredUserState=1
                self.sender.sendMessage("Please send us your name, this name will be sent to your referal for approval, in the next step we will need your referal code", reply_markup=ReplyKeyboardRemove())


            if msg["text"] == "Yes Sir \U0001f44d" and UnregisteredUserState==2:
                UnregisteredUserState=3
                self.sender.sendMessage("Next please send us your referal code, this you should have received from somone else is registered to the platform", reply_markup=ReplyKeyboardRemove())

            
            if "Yes i know" in msg["text"]:
                print ("Success")


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
    print 
    #print(id_generator())
    #print (CheckIfReferralIDExistsInDb("8N5N89"))

    

main()

bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, MessageCounter, timeout=60),
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


