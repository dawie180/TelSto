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
from datetime import datetime, timedelta
import sqlite3
from sqlite3 import Error
from geopy.geocoders import Nominatim
from geopy import distance
import string
import random


TOKEN = '320663225:AAFVzc1y_7dLUu97g1kqbw9PxkQU1aiSUMk'
#TOKEN = '884457382:AAGrGHxVplHPdM5tCT7MfS6cgueeTZKGtP4' #Store1


SqlitePath = 'D:\pythonsqlite2.db'
geolocator = Nominatim(user_agent="Telsto")

global records  
global Msg_ID



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

def GetUserState(UserID):
    conn = create_connection(SqlitePath)
    cursor = conn.cursor()
    #print("Getting User State...")
    cursor.execute("SELECT TGReferralState from User where User_ID = ?",  (UserID,))
    records = cursor.fetchone()
    cursor.close()
    if records == None:
            return False
    else:
        return records[0]

def ReadSqlEntry(NumVars, ReadString, *argv):
    try:
        conn = create_connection(SqlitePath)
        cursor = conn.cursor()
        #print("Reading DB")
        
        counter=0
        for arg in argv: 
            counter=counter+1
            VarNumber = "var" + str(counter)
            globals()[VarNumber] = arg

        if NumVars==1: cursor.execute(ReadString,  (var1,))
        if NumVars==2: cursor.execute(ReadString,  (var1, var2,))
        if NumVars==3: cursor.execute(ReadString,  (var1, var2, var3))
        if NumVars==4: cursor.execute(ReadString,  (var1, var2, var3, var4))

        records = cursor.fetchall()
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
        #print("\nChecking if User Exists On The DB")

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


def GetLocationDistance(LatBuyer, LongBuyer, LatSeller, LongSeller):
    center_point = [{'lat': LatBuyer, 'lng': LongBuyer}]
    test_point = [{'lat': LatSeller, 'lng': LongSeller}]
    center_point_tuple = tuple(center_point[0].values()) # (-7.7940023, 110.3656535)
    test_point_tuple = tuple(test_point[0].values()) # (-7.79457, 110.36563)
    dis = distance.distance(center_point_tuple, test_point_tuple).km   
    return dis




UnregisteredUserState=0
RegisteredUserState=0


class MessageCounter(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MessageCounter, self).__init__(*args, **kwargs)
        self._count = 0
    
    def on_close(self, exception):
        print("%s %d: closed" % (type(self).__name__, self.id))
        global UnregisteredUserState
        global RegisteredUserState
        if GetUserState(self.id) == "BUYER CONFIRMED":
            RegisteredUserState=0
            self.sender.sendMessage("Welcome back to the Telsto main menu, please select one of the following options...", parse_mode= 'Markdown', disable_notification=True,
                            reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                keyboard=[
                                    [KeyboardButton(text="Mary J Near Me" )],
                                    [KeyboardButton(text="Mary J Courier" )],
                                    [KeyboardButton(text="Cart" )],
                                    [KeyboardButton(text="Account Settings" )]
                            ]
                        ))

        if GetUserState(self.id) == False:
            self.sender.sendMessage("Welcome back to the TelSto, we use a referal registration system so please send us your name which will be sent to your referal for approval..", reply_markup=ReplyKeyboardRemove(), parse_mode= 'Markdown', disable_notification=True)
            UnregisteredUserState=1



    def on_chat_message(self, msg):
        Msg_ID = msg["from"]["id"]
        self._count += 1       
        try:
            global ReferralCode
            global UnregisteredUserState
            global NameForApproval     
            global RegisteredUserState


            if GetUserState(Msg_ID) == "AWAITING BUYER APPROVAL":              
                if msg["text"] == "/start":
                    global LatTemp
                    global LongTemp
                    WaitTimeDbDString = ReadSqlEntry(1, "SELECT Timer15Min from User where User_ID = ?", Msg_ID)[0]                       
                    WaitTimeRemaining = str(59 - int((datetime.now() - datetime.strptime(WaitTimeDbDString, '%Y-%m-%d %H:%M:%S.%f')).total_seconds() / 60))
                    WaitTime24DbDString = ReadSqlEntry(1, "SELECT Timer24Hours from User where User_ID = ?", Msg_ID)[0]           
                    WaitTime24Remaining = str(24 - int((datetime.now() - datetime.strptime(WaitTime24DbDString, '%Y-%m-%d %H:%M:%S.%f')).total_seconds() / 60 / 60))
                    self.sender.sendMessage("Hi " + "*"+msg["from"]["first_name"]+"*" + ",\n\nYou are currently awaiting a approval response from your referral, you have to wait another " + WaitTimeRemaining + " minutes before resending the approval request and a " + WaitTime24Remaining + " hour wait before you can restart the approval process." , parse_mode= 'Markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="Resend Approval Request (Wait " + WaitTimeRemaining + " Minutes)" )],
                                        [KeyboardButton(text="Restart Approval Process (Wait " + WaitTime24Remaining + " Hours)" )]
                                ]
                            ))

                if "Restart Approval Process" in msg["text"]:
                    WaitTimeDbDString = ReadSqlEntry(1, "SELECT Timer15Min from User where User_ID = ?", Msg_ID)[0][0]                 
                    WaitTimeRemaining = str(59 - int((datetime.now() - datetime.strptime(WaitTimeDbDString, '%Y-%m-%d %H:%M:%S.%f')).total_seconds() / 60))
                    WaitTime24DbDString = ReadSqlEntry(1, "SELECT Timer24Hours from User where User_ID = ?", Msg_ID)[0][0] 
                    WaitTime24Remaining = str(24 - int((datetime.now() - datetime.strptime(WaitTime24DbDString, '%Y-%m-%d %H:%M:%S.%f')).total_seconds() / 60 / 60))
                    if int(WaitTime24Remaining) <= 0:
                        conn = create_connection(SqlitePath)
                        sql = 'DELETE FROM User WHERE User_ID=?'
                        cur = conn.cursor()
                        cur.execute(sql, (Msg_ID,))
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

                if "Resend Approval Request" in msg["text"]:
                    WaitTimeDbDString = ReadSqlEntry(1, "SELECT Timer15Min from User where User_ID = ?", Msg_ID)[0][0]             
                    WaitTimeRemaining = str(59 - int((datetime.now() - datetime.strptime(WaitTimeDbDString, '%Y-%m-%d %H:%M:%S.%f')).total_seconds() / 60))
                    WaitTime24DbDString = ReadSqlEntry(1, "SELECT Timer24Hours from User where User_ID = ?", Msg_ID)[0][0]
                    WaitTime24Remaining = str(24 - int((datetime.now() - datetime.strptime(WaitTime24DbDString, '%Y-%m-%d %H:%M:%S.%f')).total_seconds() / 60 / 60))
                    if int(WaitTimeRemaining) > 0 and int(WaitTime24Remaining) > 0:
                        self.sender.sendMessage("Please wait another " + WaitTimeRemaining + " minutes before sending another refereeal request" , parse_mode= 'Markdown',
                                    reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                        keyboard=[
                                            [KeyboardButton(text="Resend Approval Request (Wait " + WaitTimeRemaining + " Minutes)" )],
                                            [KeyboardButton(text="Restart Approval Process (Wait " + WaitTime24Remaining + " Hours)" )]
                                    ]
                                ))

                    elif int(WaitTimeRemaining) > 0 and int(WaitTime24Remaining) < 1:
                        self.sender.sendMessage("Please wait another " + WaitTimeRemaining + " minutes before sending another refereeal request" , parse_mode= 'Markdown',
                                    reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                        keyboard=[
                                            [KeyboardButton(text="Resend Approval Request (Wait " + WaitTimeRemaining + " Minutes)" )],
                                            [KeyboardButton(text="Restart Approval Process" )]
                                    ]
                                ))

                    elif int(WaitTimeRemaining) < 1 and int(WaitTime24Remaining) > 0:
                        self.sender.sendMessage("Please wait another " + WaitTimeRemaining + " minutes before sending another refereeal request" , parse_mode= 'Markdown',
                                    reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                        keyboard=[
                                            [KeyboardButton(text="Resend Approval Request" )],
                                            [KeyboardButton(text="Restart Approval Process (Wait " + WaitTime24Remaining + " Hours)" )]
                                    ]
                                ))


                    else:
                        resendapproved_sql = datetime.now()       #User(User_ID,Telegram_ID, TGReferral_ID, TGReferralState, Timer15Min)
                        nameforapproval = ReadSqlEntry(1, "SELECT Telegram_ID from User where User_ID = ?", Msg_ID)[0][0]     
                        bot.sendMessage(get_referral_user_id(Msg_ID)[0], "hi, " + "*"+nameforapproval+"*" + " needs approval, select appropriate answer below...", parse_mode= 'markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="\u2705  " + "Yes i know " + nameforapproval + "  \u2705" )],
                                        [KeyboardButton(text="\u26d4\ufe0f  " + "no i don't know " + nameforapproval + "  \u26d4\ufe0f" )]
                                ]
                            ))
                        WaitTime24DbDString = ReadSqlEntry(1, "SELECT Timer24Hours from User where User_ID = ?", Msg_ID)[0][0] 
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
                        cursor.execute('UPDATE User SET Timer15Min=? WHERE User_ID=?', (datetime.now(), Msg_ID))
                        conn.commit()
                        conn.close()


            global State    
            if GetUserState(Msg_ID) == "BUYER CONFIRMED":
                if msg["text"] == "/start": 
                    RegisteredUState=0
                    State=0
                    self.sender.sendMessage("Welcome back to the Telsto main menu, please select one of the following options...", parse_mode= 'Markdown',
                            reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                keyboard=[
                                    [KeyboardButton(text="Mary J Near Me" )],
                                    [KeyboardButton(text="Mary J Courier" )],
                                    [KeyboardButton(text="Cart" )],
                                    [KeyboardButton(text="Account Settings" )]
                            ]
                        ))

                if msg["text"] == "Yes Sir \U0001f44d" and RegisteredUserState==2:
                    RegisteredUserState=3
                    UpdateSqlEntry("UPDATE User SET Latitude = ?, Longitude = ? WHERE User_ID = ?", (LatTemp, LongTemp, Msg_ID))
                    self.sender.sendMessage("Choose from the following", parse_mode= 'Markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="Collect")],
                                        [KeyboardButton(text="Deliver" )],
                                        [KeyboardButton(text="Back" )]
                                ]
                            ))

                if msg["text"] == "Cancel \U0001f629" and RegisteredUserState==2:
                        RegisteredUserState=0
                        self.sender.sendMessage("Welcome back to the Telsto main menu, please select one of the following options...", parse_mode= 'Markdown',                       
                        reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                            keyboard=[
                                [KeyboardButton(text="Mary J Near Me" )],
                                [KeyboardButton(text="Mary J Courier" )],
                                [KeyboardButton(text="Cart" )],
                                [KeyboardButton(text="Account Settings" )]
                        ]
                    ))


                if msg["text"] != None and RegisteredUserState==1:
                    try:
                        RegisteredUserState=2
                        location = geolocator.geocode(str(msg["text"]))
                        print(location.address)
                        print((location.latitude, location.longitude))
                        LatTemp = location.latitude
                        LongTemp = location.longitude
                        self.sender.sendMessage("*"+ location.address + "*" + "\n\nIs this address correct?", parse_mode= 'Markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="Yes Sir \U0001f44d")],
                                        [KeyboardButton(text="Cancel \U0001f629" )]
                                ]
                            ))
                    except:
                        RegisteredUserState=2
                        self.sender.sendMessage("Address not found, please send it again or use the locatation button below...",
                                            reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                                keyboard=[
                                                    [KeyboardButton(text="\U0001f4cd GEO LOCATION \U0001f4cd", request_location=True)]
                                                ]
                                            ))


                elif msg["text"] != None and RegisteredUserState==2:
                    try:
                        location = geolocator.geocode(str(msg["text"]))
                        print(location.address)
                        print((location.latitude, location.longitude))
                        LatTemp = location.latitude
                        LongTemp = location.longitude
                        self.sender.sendMessage("*"+ location.address + "*" + "\n\nIs this address correct?", parse_mode= 'Markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="Yes Sir \U0001f44d")],
                                        [KeyboardButton(text="Cancel \U0001f629" )]
                                ]
                            ))
                    except:
                        RegisteredUserState=2
                        self.sender.sendMessage("Address not found, please send it again or use the locatation button below...",
                                            reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                                keyboard=[
                                                    [KeyboardButton(text="\U0001f4cd GEO LOCATION \U0001f4cd", request_location=True)]
                                                ]
                                            ))



                if msg["text"] == "Mary J Near Me" and RegisteredUserState==0:                   
                    if ReadSqlEntry(1, "SELECT Latitude from User where User_ID = ?", Msg_ID)[0][0] == None:
                        RegisteredUserState=1
                        State=1
                        self.sender.sendMessage("We will need your location in order to match you up with sellers nearby, please send us your location using the button below or send us your address in words",
                                            reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                                keyboard=[
                                                    [KeyboardButton(text="\U0001f4cd GEO LOCATION \U0001f4cd", request_location=True)]
                                                ]
                                            ))
                    else:
                        RegisteredUserState=3
                        State=1
                        self.sender.sendMessage("Choose from the following", parse_mode= 'Markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="Collect")],
                                        [KeyboardButton(text="Deliver" )],
                                        [KeyboardButton(text="Back" )]
                                ]
                            ))


                if "location" in msg and RegisteredUserState==1:
                    RegisteredUserState=2
                    print ("Location Found")
                    UpdateSqlEntry("UPDATE User SET Latitude = ?, Longitude = ? WHERE User_ID = ?", (msg["location"]["latitude"], msg["location"]["longitude"], Msg_ID))
                    print ("Saving To Sqlite Database")
                    conn = create_connection(SqlitePath)
                    create_intitaldb(conn, SqliteInitialinfo)
                    print ("Saved To Sqlite Database")
                    select_all_tasks(conn)
                    conn.close()
             
                              
                if msg["text"] == "Collect":
                    State=2
                    SellersNearMe = []
                    conn = create_connection(SqlitePath)
                    cur = conn.cursor()
                    cur.execute("SELECT COUNT(Seller) FROM User")
                    conn.commit()
                    NumSellers = (list(cur)[0])[0]
                    BuyerLatLong = ReadSqlEntry(1, "SELECT Latitude, Longitude from User where User_ID = ?", Msg_ID)
                    SellerLatLong = ReadSqlEntry(1, "SELECT Latitude, Longitude, User_ID from User where Seller = ?", 1)
                    for i in range (0, NumSellers):
                        distanceapart = GetLocationDistance(BuyerLatLong[0][0], BuyerLatLong[0][1], SellerLatLong[i][0], SellerLatLong[i][1])
                        if distanceapart <= 5:
                            SellersNearMe.extend([str(SellerLatLong[i][2])])
                    
                    print (SellersNearMe)        

                    if len(SellersNearMe)==1:
                        self.sender.sendMessage("Here is a list of stores available for collection near you...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[0])[0][0]))],
                            [KeyboardButton(text="Back" )]]))            
                    if len(SellersNearMe)==2:    
                        self.sender.sendMessage("Here is a list of stores available for collection near you...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[0])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[1])[0][0]))],
                            [KeyboardButton(text="Back" )]]))
                    if len(SellersNearMe)==3:
                        self.sender.sendMessage("Here is a list of stores available for collection near you...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[0])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[1])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[2])[0][0]))],
                            [KeyboardButton(text="Back" )]]))
                    if len(SellersNearMe)==4:    
                        self.sender.sendMessage("Here is a list of stores available for collection near you...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[0])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[1])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[2])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[3])[0][0]))],
                            [KeyboardButton(text="Back" )]]))
                    if len(SellersNearMe)==5:
                        self.sender.sendMessage("Here is a list of stores available for collection near you...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[0])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[1])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[2])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[3])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[4])[0][0]))],
                            [KeyboardButton(text="Back" )]]))
                    if len(SellersNearMe)==6:
                        self.sender.sendMessage("Here is a list of stores available for collection near you...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[0])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[1])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[2])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[3])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[4])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[5])[0][0]))], 
                            [KeyboardButton(text="Back" )]]))
                    if len(SellersNearMe)==7:
                        self.sender.sendMessage("Here is a list of stores available for collection near you...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[0])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[1])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[2])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[3])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[4])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[5])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[6])[0][0]))], 
                            [KeyboardButton(text="Back" )]]))
                    if len(SellersNearMe)==8:
                        self.sender.sendMessage("Here is a list of stores available for collection near you...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[0])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[1])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[2])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[3])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[4])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[5])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[6])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[7])[0][0]))], 
                            [KeyboardButton(text="Back" )]]))
                    if len(SellersNearMe)==9:
                        self.sender.sendMessage("Here is a list of stores available for collection near you...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[0])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[1])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[2])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[3])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[4])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[5])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[6])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[7])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[8])[0][0]))], 
                            [KeyboardButton(text="Back" )]]))
                    if len(SellersNearMe)==10:
                        self.sender.sendMessage("Here is a list of stores available for collection near you...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[0])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[1])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[2])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[3])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[4])[0][0]))],
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[5])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[6])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[7])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[8])[0][0]))], 
                            [KeyboardButton(text=str(ReadSqlEntry(1, "SELECT StoreName from User where User_ID = ?", SellersNearMe[9])[0][0]))],
                            [KeyboardButton(text="Back" )]]))

            if msg["text"] == "Back" and State==1:
                State=0
                RegisteredUserState=0
                self.sender.sendMessage("Welcome back to the Telsto main menu, please select one of the following options...", parse_mode= 'Markdown',
                            reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                keyboard=[
                                    [KeyboardButton(text="Mary J Near Me" )],
                                    [KeyboardButton(text="Mary J Courier" )],
                                    [KeyboardButton(text="Cart" )],
                                    [KeyboardButton(text="Account Settings" )]
                            ]
                        ))
            
            if msg["text"] == "Back" and State==2:
                State=1
                self.sender.sendMessage("Choose from the following", parse_mode= 'Markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="Collect")],
                                        [KeyboardButton(text="Deliver" )],
                                        [KeyboardButton(text="Back" )]
                                ]
                            ))


            if GetUserState(Msg_ID) == False:    
                if msg["text"] == "/start" and UnregisteredUserState==0:                         
                    self.sender.sendMessage("Hi " + "*"+msg["from"]["first_name"]+"*" + ",\n\nWelcome to the TelSto, we use a referal registration system so please send us your name which will be sent to your referal for approval..", reply_markup=ReplyKeyboardRemove(), parse_mode= 'Markdown')
                    UnregisteredUserState=1

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
                    preapproved_sql = (Msg_ID, NameForApproval, ReferralCode, "AWAITING BUYER APPROVAL", datetime.now(), datetime.now(), datetime.now())         #User(User_ID,Telegram_ID, TGReferral_ID, TGReferralState, Timer15Min)
                    if ReadSqlEntry(1, "SELECT User_ID from User where TGReferralSelf_ID = ?", ReferralCode) != False:
                        bot.sendMessage(ReadSqlEntry(1, "SELECT User_ID from User where TGReferralSelf_ID = ?", ReferralCode)[0][0], "Hi, " + "*"+NameForApproval+"*" + " needs approval, select appropriate answer below...", parse_mode= 'Markdown',
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
                    if ReadSqlEntry(1, "SELECT TGReferralState from User where User_ID = ?", Msg_ID)[0] == False:
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
                NameForSearch = msg["text"].split('\u2705')[1]                
                NameForSearch = NameForSearch[NameForSearch.find('know')+5:]
                NameForSearch = NameForSearch[0:-2]
                ReferralCode = ReadSqlEntry(1, "SELECT TGReferralSelf_ID from User where User_ID = ?", Msg_ID)[0][0]  
                if ReadSqlEntry(2, "SELECT User_ID from User where TGReferral_ID = ? AND Telegram_ID = ?", ReferralCode, NameForSearch) != False:
                    UpdateSqlEntry("UPDATE User SET TGReferralState = ?, DateTimeApproved = ?, Timer15Min = ?, Timer24Hours = ? WHERE User_ID = ?", ("BUYER CONFIRMED", datetime.now(), None, None, ReadSqlEntry(2, "SELECT User_ID from User where TGReferral_ID = ? AND Telegram_ID = ?", ReferralCode, NameForSearch)[0][0] ))                   
                    RegisteredUserState=0
                    bot.sendMessage(ReadSqlEntry(2, "SELECT User_ID from User where TGReferral_ID = ? AND Telegram_ID = ?", ReferralCode, NameForSearch)[0][0], "Congratulations, your application was successful, welcome to the Telsto, please select one of the following options...", parse_mode= 'Markdown',
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
        per_chat_id(), create_open, MessageCounter, timeout=30),
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

