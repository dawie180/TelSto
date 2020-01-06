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
#TOKEN = '884457382:AAGrGHxVplHPdM5tCT7MfS6cgueeTZKGtP4' #Store1


SqlitePath = 'C:\TelSto.db'
geolocator = Nominatim(user_agent="Telsto")

global records  


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(size))

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
 
    return conn
 
 
# "INSERT INTO User(User_ID,Telegram_ID, TGReferral_ID, TGReferralState, Timer15Min, Timer24Hours) VALUES(?,?,?,?,?,?)"

def CreateSqlEntry(conn, User, sqlstring): 
    sql = sqlstring
    cur = conn.cursor()
    cur.execute(sql, User)
    return cur.lastrowid
    print ("Wrote To Sql")


def ReadSqlEntry(NumVars, ReadString, *argv):
    try:
        conn = create_connection(SqlitePath)
        cursor = conn.cursor()
        print("Reading DB")
        
        counter=0
        for arg in argv: 
            counter=counter+1
            VarNumber = "var" + str(counter)
            globals()[VarNumber] = arg

        if NumVars==1: cursor.execute(ReadString,  (var1,))
        if NumVars==2: cursor.execute(ReadString,  (var1, var2,))
        if NumVars==3: cursor.execute(ReadString,  (var1, var2, var3))
        if NumVars==4: cursor.execute(ReadString,  (var1, var2, var3, var4))

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


def UpdateSqlEntry(UpdateQuery, task):
    conn = create_connection(SqlitePath)
    cur = conn.cursor()
    cur.execute(UpdateQuery, task)
    conn.commit()

def DeleteSqlEntry(UpdateQuery, task):
    conn = create_connection(SqlitePath)
    cur = conn.cursor()
    sql_delete_query = """DELETE from SqliteDb_developers where id = 6"""
    cur.execute(sql_delete_query)
    conn.commit()



def get_referral_user_id(Ref_ID):
    try:
        conn = create_connection(SqlitePath)
        cursor = conn.cursor()
        print("\nChecking if User Exists On The DB")

        sql_select_query =  """SELECT TGReferral_ID from User where User_ID = ?"""
        cursor.execute(sql_select_query, (Ref_ID,))
        records = cursor.fetchone()
        cursor.close()
        if records == None:
            return False
        else:
            conn = create_connection(SqlitePath)
            cursor = conn.cursor()
            sql_select_query =  """SELECT User_ID from User where TGReferralSelf_ID = ?"""
            cursor.execute(sql_select_query, (records[0],))
            records = cursor.fetchone()
            cursor.close()
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
        try:
            if msg["text"] == "/start" and ReadSqlEntry(1, "SELECT TGReferralState from User where User_ID = ?", msg["from"]["id"]) == "AWAITING BUYER APPROVAL":
                global UnregisteredUserState
                global NameForApproval
                WaitTimeDbDString = ReadSqlEntry(1, "SELECT Timer15Min from User where User_ID = ?", msg["from"]["id"])[0]                       
                WaitTimeRemaining = str(59 - int((datetime.now() - datetime.strptime(WaitTimeDbDString, '%Y-%m-%d %H:%M:%S.%f')).total_seconds() / 60))
                WaitTime24DbDString = ReadSqlEntry(1, "SELECT Timer24Hours from User where User_ID = ?", msg["from"]["id"])[0]           
                WaitTime24Remaining = str(24 - int((datetime.now() - datetime.strptime(WaitTime24DbDString, '%Y-%m-%d %H:%M:%S.%f')).total_seconds() / 60 / 60))
                self.sender.sendMessage("Hi " + "*"+msg["from"]["first_name"]+"*" + ",\n\nYou are currently awaiting a approval response from your referral, you have to wait another " + WaitTimeRemaining + " minutes before resending the approval request and a " + WaitTime24Remaining + " hour wait before you can restart the approval process." , parse_mode= 'Markdown',
                            reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                keyboard=[
                                    [KeyboardButton(text="Resend Approval Request (Wait " + WaitTimeRemaining + " Minutes)" )],
                                    [KeyboardButton(text="Restart Approval Process (Wait " + WaitTime24Remaining + " Hours)" )]
                            ]
                        ))

            elif msg["text"] == "/start" and ReadSqlEntry(1, "SELECT TGReferralState from User where User_ID = ?", msg["from"]["id"]) == False:                
                self.sender.sendMessage("Hi " + "*"+msg["from"]["first_name"]+"*" + ",\n\nWelcome to the TelSto, we use a referal registration system so please send us your name which will be sent to your referal for approval..", reply_markup=ReplyKeyboardRemove(), parse_mode= 'Markdown')
                UnregisteredUserState=1
            else:
                print ("Welcome Back")




            if msg["text"] != "/start" and UnregisteredUserState==1:
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
            if msg["text"] != "/start" and UnregisteredUserState==3:
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
                preapproved_sql = (msg["from"]["id"], NameForApproval, ReferralCode, "AWAITING BUYER APPROVAL", datetime.now(), datetime.now(), datetime.now())         #User(User_ID,Telegram_ID, TGReferral_ID, TGReferralState, Timer15Min)
                if ReadSqlEntry(1, "SELECT User_ID from User where TGReferralSelf_ID = ?", ReferralCode) != False:
                    bot.sendMessage(ReadSqlEntry(1, "SELECT User_ID from User where TGReferralSelf_ID = ?", ReferralCode)[0], "Hi, " + "*"+NameForApproval+"*" + " needs approval, select appropriate answer below...", parse_mode= 'Markdown',
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
                                    [KeyboardButton(text="Restart Approval Process (Wait 24 Hours)" )]
                            ]
                        ))

                    conn = create_connection(SqlitePath)
                    CreateSqlEntry(conn, preapproved_sql, ''' INSERT INTO User(User_ID,Telegram_ID, TGReferral_ID, TGReferralState, DateTimeCreated, Timer15Min, Timer24Hours) VALUES(?,?,?,?,?,?,?) ''')
                    conn.commit()

                else:
                    UnregisteredUserState=3
                    self.sender.sendMessage("Referral Code " + "*"+ReferralCode+"*" + " not found, please send another code", parse_mode= 'Markdown',
                            reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                keyboard=[
                                    [KeyboardButton(text="Cancel, im scared \u26d4\ufe0f" )]
                            ]
                        ))


            if msg["text"] == "Cancel, im scared \u26d4\ufe0f" and UnregisteredUserState==4:                  
                if ReadSqlEntry(1, "SELECT TGReferralState from User where User_ID = ?", msg["from"]["id"])[0] == False:
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

            

            if "Resend Approval Request" in msg["text"] and ReadSqlEntry(1, "SELECT TGReferralState from User where User_ID = ?", msg["from"]["id"])[0] == "AWAITING BUYER APPROVAL":
                WaitTimeDbDString = ReadSqlEntry(1, "SELECT Timer15Min from User where User_ID = ?", msg["from"]["id"])[0]                 
                WaitTimeRemaining = str(59 - int((datetime.now() - datetime.strptime(WaitTimeDbDString, '%Y-%m-%d %H:%M:%S.%f')).total_seconds() / 60))
                WaitTime24DbDString = ReadSqlEntry(1, "SELECT Timer24Hours from User where User_ID = ?", msg["from"]["id"])[0] 
                WaitTime24Remaining = str(24 - int((datetime.now() - datetime.strptime(WaitTime24DbDString, '%Y-%m-%d %H:%M:%S.%f')).total_seconds() / 60 / 60))
                if int(WaitTimeRemaining) > 0 and int(WaitTime24Remaining) > 0:
                    print (WaitTime24DbDString)
                    self.sender.sendMessage("Please wait another " + WaitTimeRemaining + " minutes before sending another refereeal request" , parse_mode= 'Markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="Resend Approval Request (Wait " + WaitTimeRemaining + " Minutes)" )],
                                        [KeyboardButton(text="Restart Approval Process (Wait " + WaitTime24Remaining + " Hours)" )]
                                ]
                            ))

                elif int(WaitTimeRemaining) > 0 and int(WaitTime24Remaining) < 1:
                    print (WaitTime24DbDString)
                    self.sender.sendMessage("Please wait another " + WaitTimeRemaining + " minutes before sending another refereeal request" , parse_mode= 'Markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="Resend Approval Request (Wait " + WaitTimeRemaining + " Minutes)" )],
                                        [KeyboardButton(text="Restart Approval Process" )]
                                ]
                            ))

                elif int(WaitTimeRemaining) < 1 and int(WaitTime24Remaining) > 0:
                    print (WaitTime24DbDString)
                    self.sender.sendMessage("Please wait another " + WaitTimeRemaining + " minutes before sending another refereeal request" , parse_mode= 'Markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="Resend Approval Request" )],
                                        [KeyboardButton(text="Restart Approval Process (Wait " + WaitTime24Remaining + " Hours)" )]
                                ]
                            ))


                else:
                    resendapproved_sql = datetime.now()       #User(User_ID,Telegram_ID, TGReferral_ID, TGReferralState, Timer15Min)
                    nameforapproval = ReadSqlEntry(1, "SELECT Telegram_ID from User where User_ID = ?", msg["from"]["id"])[0]     
                    bot.sendMessage(get_referral_user_id(msg["from"]["id"])[0], "hi, " + "*"+nameforapproval+"*" + " needs approval, select appropriate answer below...", parse_mode= 'markdown',
                            reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                keyboard=[
                                    [KeyboardButton(text="\u2705  " + "Yes i know " + nameforapproval + "  \u2705" )],
                                    [KeyboardButton(text="\u26d4\ufe0f  " + "no i don't know " + nameforapproval + "  \u26d4\ufe0f" )]
                            ]
                        ))
                    WaitTime24DbDString = ReadSqlEntry(1, "SELECT Timer24Hours from User where User_ID = ?", msg["from"]["id"])[0] 
                    WaitTime24Remaining = str(24 - int((datetime.now() - datetime.strptime(WaitTime24DbDString, '%Y-%m-%d %H:%M:%S.%f')).total_seconds() / 60 / 60))
                    if int(WaitTime24Remaining) > 0:
                        self.sender.sendMessage("sent for approval, wait for response", parse_mode= 'markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="Resend Approval Request (Wait 1 Hour)" )],
                                        [KeyboardButton(text="Restart Approval Process (Wait " + WaitTime24Remaining + " Hours)" )]
                                ]
                            ))
                    else:
                        self.sender.sendMessage("sent for approval, wait for response", parse_mode= 'markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="Resend Approval Request (Wait 1 Hour)" )],
                                        [KeyboardButton(text="Restart Approval Process")]
                                ]
                            ))

                    conn = create_connection(SqlitePath)
                    cursor = conn.cursor()
                    cursor.execute('UPDATE User SET Timer15Min=? WHERE User_ID=?', (datetime.now(), msg["from"]["id"]))
                    conn.commit()
                    conn.close()

            if "Restart Approval Process" in msg["text"] and ReadSqlEntry(1, "SELECT TGReferralState from User where User_ID = ?", msg["from"]["id"])[0] == "AWAITING BUYER APPROVAL":
                WaitTimeDbDString = ReadSqlEntry(1, "SELECT Timer15Min from User where User_ID = ?", msg["from"]["id"])[0]                 
                WaitTimeRemaining = str(59 - int((datetime.now() - datetime.strptime(WaitTimeDbDString, '%Y-%m-%d %H:%M:%S.%f')).total_seconds() / 60))
                WaitTime24DbDString = ReadSqlEntry(1, "SELECT Timer24Hours from User where User_ID = ?", msg["from"]["id"])[0] 
                WaitTime24Remaining = str(24 - int((datetime.now() - datetime.strptime(WaitTime24DbDString, '%Y-%m-%d %H:%M:%S.%f')).total_seconds() / 60 / 60))
                if int(WaitTime24Remaining) <= 0:
                    conn = create_connection(SqlitePath)
                    sql = 'DELETE FROM User WHERE User_ID=?'
                    cur = conn.cursor()
                    cur.execute(sql, (msg["from"]["id"],))
                    conn.commit()

                    conn.commit()
                    conn.close()
                    self.sender.sendMessage("Hi " + "*"+msg["from"]["first_name"]+"*" + ",\n\nWelcome to the TelSto, we use a referal registration system so please send us your name which will be sent to your referal for approval..", reply_markup=ReplyKeyboardRemove(), parse_mode= 'Markdown')
                    UnregisteredUserState=1

                else:
                    self.sender.sendMessage("Please wait another " + WaitTime24Remaining + " hours before restarting the approval process" , parse_mode= 'Markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="Resend Approval Request (Wait " + WaitTimeRemaining + " Minutes)" )],
                                        [KeyboardButton(text="Restart Approval Process (Wait " + WaitTime24Remaining + " Hours)" )]
                            ]
                        ))

            
            if "Yes i know" in msg["text"]:
                NameForSearch = msg["text"].split('\u2705')[1]                
                NameForSearch = NameForSearch[NameForSearch.find('know')+5:]
                NameForSearch = NameForSearch[0:-2]
                ReferralCode = ReadSqlEntry(1, "SELECT TGReferralSelf_ID from User where User_ID = ?", msg["from"]["id"])[0]  
                if ReadSqlEntry(2, "SELECT User_ID from User where TGReferral_ID = ? AND Telegram_ID = ?", ReferralCode, NameForSearch) != False:
                    print ("Awe")
                    UpdateSqlEntry("UPDATE User SET TGReferralState = ?, DateTimeApproved = ?, Timer15Min = ?, Timer24Hours = ? WHERE User_ID = ?", ("BUYER CONFIRMED", datetime.now(), None, None, ReadSqlEntry(2, "SELECT User_ID from User where TGReferral_ID = ? AND Telegram_ID = ?", ReferralCode, NameForSearch)[0] ))

                    bot.sendMessage(ReadSqlEntry(2, "SELECT User_ID from User where TGReferral_ID = ? AND Telegram_ID = ?", ReferralCode, NameForSearch)[0], "Congratulations, your application was successful, welcome to the Telsto, please select one of the following options...", parse_mode= 'Markdown',
                            reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                keyboard=[
                                    [KeyboardButton(text="Mary J Near Me" )],
                                    [KeyboardButton(text="Mary J Courier" )],
                                    [KeyboardButton(text="Cart" )],
                                    [KeyboardButton(text="Account Settings" )]
                            ]
                        ))


                else:
                    self.sender.sendMessage(NameForSearch + " not found.", reply_markup=ReplyKeyboardRemove())


        except KeyError as error:   
                pass  







def main():
    print ("Program Start")
    #print(id_generator())

    

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




# DB and Table SCHEMA
# DB - TelSto.DB

    #sql_create_User_table = """CREATE TABLE IF NOT EXISTS User (
    #                            User_ID INTEGER PRIMARY KEY,
    #                            Telegram_ID TEXT NOT NULL,
    #                            TGReferral_ID TEXT NULL,
    #                            TGReferralState BIT NULL,
    #                            Seller bit NULL,
    #                            Buyer bit NULL,
    #                            Latitude TEXT NOT NULL,
    #                            Longitude TEXT NOT NULL,
    #                            AddressLine1 TEXT NULL,
    #                            AddressLine2 TEXT NULL,
    #                            City text NULL,
    #                            PostCode TEXT NULL,
    #                            Country TEXT NULL,
    #                            Timer24Hours NOT NULL,
    #                            Timer15Min DATETIME NOT NULL
                                
    #                        );"""


