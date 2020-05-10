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
import sqlite3
from sqlite3 import Error
from geopy.geocoders import Nominatim
from geopy import distance
import string
from random import seed
from random import randint
import os


TOKEN = '320663225:AAFVzc1y_7dLUu97g1kqbw9PxkQU1aiSUMk'
#TOKEN = '884457382:AAGrGHxVplHPdM5tCT7MfS6cgueeTZKGtP4' #Store1

ImageTempPath = 'D:/'
SqlitePath = 'D:\pythonsqlite2.db'
geolocator = Nominatim(user_agent="Telsto")

global records  
global Msg_ID
Cart = []

seed(1)

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

def writeTofile(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)
    #print("Stored blob data into: ", filename, "\n")

def CreateSqlEntry(conn, User, sqlstring): 
    sql = sqlstring
    cur = conn.cursor()
    cur.execute(sql, User)
    return cur.lastrowid
    #print ("Wrote To Sql")

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
            Cart.clear()
            self.sender.sendMessage("Welcome back to the Telsto main menu, please select one of the following options...", parse_mode= 'Markdown', disable_notification=True,
                            reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                keyboard=[
                                    [KeyboardButton(text="Mary J Near Me" )],
                                    [KeyboardButton(text="Mary J Courier" )],
                                    [KeyboardButton(text="Account Settings" )]
                            ]
                        ))

        if GetUserState(self.id) == False:
            self.sender.sendMessage("Welcome back to the TelSto, we use a referal registration system so please send us your name which will be sent to your referal for approval..", reply_markup=ReplyKeyboardRemove(), parse_mode= 'Markdown', disable_notification=True)
            UnregisteredUserState=1



    def on_chat_message(self, msg):
        print(msg["text"])
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

            global Catagory
            global State
            global StoreName
            global StoreId
            if GetUserState(Msg_ID) == "BUYER CONFIRMED":                              
                if msg["text"] == "/start": 
                    RegisteredUState=0
                    self.sender.sendMessage("Welcome back to the Telsto main menu, please select one of the following options...", parse_mode= 'Markdown',
                            reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                keyboard=[
                                    [KeyboardButton(text="Mary J Near Me" )],
                                    [KeyboardButton(text="Mary J Courier" )],
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
                
                global ProductName
                global ProductsName
                global ProductsCartIndex
                global Catagories
                global State2
                global State3
                global State4
                global State5
                global State6
                global Cart
                if msg["text"] == "Back" and RegisteredUserState==3:                 
                    RegisteredUserState=0
                    self.sender.sendMessage("Welcome back to the Telsto main menu, please select one of the following options...", parse_mode= 'Markdown',                       
                        reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                            keyboard=[
                                [KeyboardButton(text="Mary J Near Me" )],
                                [KeyboardButton(text="Mary J Courier" )],
                                [KeyboardButton(text="Account Settings" )]
                        ]
                    ))

                if msg["text"] == "Back" and RegisteredUserState==4:                   
                    RegisteredUserState=3
                    State=0
                    self.sender.sendMessage("Choose from the following", parse_mode= 'Markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="Collect")],
                                        [KeyboardButton(text="Deliver" )],
                                        [KeyboardButton(text="Back" )]
                                ]
                            ))
                

                if msg["text"] == "Back" and RegisteredUserState==7:
                    RegisteredUserState=5
                    State2=1

                if msg["text"] == "Back" and RegisteredUserState==9:
                    RegisteredUserState=5
                    State2=1

                if msg["text"] == "Back" and RegisteredUserState==6:
                    RegisteredUserState=4
                    State3=1

                if msg["text"] == "Back" and RegisteredUserState==8:
                    RegisteredUserState=5
                    State2=1

                if msg["text"] == "Back" and RegisteredUserState==11:
                    RegisteredUserState=4
                    State3=1

                if msg["text"] == "Back" and RegisteredUserState==5:
                    if len(Cart)==0:
                        RegisteredUserState=3
                        msg["text"] = "Collect"
                    else:
                        RegisteredUserState=11
                        Statement = "There are items in your cart, cannot continue until you checkout or remove itmes.... \n\n"

                        Statement += "*" + str(StoreName) + "*" 
                        Statement += " Store: \n\n"
                        Total=0
                        for i in range (0, int(len(Cart)/3)):
                            Statement += str(i+1) + ".\t\t"
                            Statement2 = 'SELECT Product_Name from  Products where Product_ID = ?'
                            Statement3 = 'SELECT Product_Catagory from  Products where Product_ID = ?'
                            ProductsName = ReadSqlEntry(1, Statement2, Cart[i*3+2])
                            ProductsCatagory = ReadSqlEntry(1, Statement3, Cart[i*3+2])
                            Statement += str(ProductsName[0][0]) + " (" + "_" + str(ProductsCatagory[0][0]) + "_" + ") \n\t\t\t\t\t" + str(Cart[i*3]) + "x " + str(Cart[i*3+1]) + " = R"
                            Total = Total + int(Cart[i*3+1][Cart[i*3+1].find("R")+1:])*int(Cart[i*3])
                            Statement +=str((int(Cart[i*3+1][Cart[i*3+1].find("R")+1:]))*int(Cart[i*3])) + "\n"
                                                      
                        Statement += "\n*Total: R*" + "*" + str(Total) + "*"
                        
                        Test = [[KeyboardButton(text="Checkout")],[KeyboardButton(text="Edit")],[KeyboardButton(text="Delete All")],[KeyboardButton(text="Back" )]]
                        self.sender.sendMessage(Statement, parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=Test))
                


                if "Cart" in msg["text"] and RegisteredUserState==5:                   
                    if msg["text"] == "Cart (0)":
                        RegisteredUserState=4
                        State3=1
                        self.sender.sendMessage("Sorry No Items In The Cart")
                    else:
                        RegisteredUserState=11
                        Statement = "Here Are Your Cart Contents... \n\n"

                        Statement += "*" + str(StoreName) + "*" 
                        Statement += " Store: \n\n"
                        Total=0
                        for i in range (0, int(len(Cart)/3)):
                            Statement += str(i+1) + ".\t\t"
                            Statement2 = 'SELECT Product_Name from  Products where Product_ID = ?'
                            Statement3 = 'SELECT Product_Catagory from  Products where Product_ID = ?'
                            ProductsName = ReadSqlEntry(1, Statement2, Cart[i*3+2])
                            ProductsCatagory = ReadSqlEntry(1, Statement3, Cart[i*3+2])
                            Statement += str(ProductsName[0][0]) + " (" + "_" + str(ProductsCatagory[0][0]) + "_" + ") \n\t\t\t\t\t" + str(Cart[i*3]) + "x " + str(Cart[i*3+1]) + " = R"
                            Total = Total + int(Cart[i*3+1][Cart[i*3+1].find("R")+1:])*int(Cart[i*3])
                            Statement +=str((int(Cart[i*3+1][Cart[i*3+1].find("R")+1:]))*int(Cart[i*3])) + "\n"
                                                      
                        Statement += "\n*Total: R*" + "*" + str(Total) + "*"
                        
                        Test = [[KeyboardButton(text="Checkout")],[KeyboardButton(text="Edit")],[KeyboardButton(text="Delete All")],[KeyboardButton(text="Back" )]]
                        self.sender.sendMessage(Statement, parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=Test))

                        #self.sender.sendMessage(Statement, parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[[KeyboardButton(text="Checkout")],[KeyboardButton(text="Edit")],[KeyboardButton(text="Delete All")],[KeyboardButton(text="Back" )]]))
       
                if msg["text"] == "Delete All" and RegisteredUserState==11:
                    RegisteredUserState=4
                    State3=1
                    Cart.clear()
                    self.sender.sendMessage("Cart cleared...")

                if msg["text"] == "Back" and RegisteredUserState==12:
                    if len(Cart) == 0:
                        RegisteredUserState=4
                        State3=1
                        self.sender.sendMessage("Sorry No Items In The Cart")
                    else:
                        RegisteredUserState=11
                        Statement = "Here Are Your Cart Contents... \n\n"

                        Statement += "*" + str(StoreName) + "*" 
                        Statement += " Store: \n\n"
                        Total=0
                        for i in range (0, int(len(Cart)/3)):
                            Statement += str(i+1) + ".\t\t"
                            Statement2 = 'SELECT Product_Name from  Products where Product_ID = ?'
                            Statement3 = 'SELECT Product_Catagory from  Products where Product_ID = ?'
                            ProductsName = ReadSqlEntry(1, Statement2, Cart[i*3+2])
                            ProductsCatagory = ReadSqlEntry(1, Statement3, Cart[i*3+2])
                            Statement += str(ProductsName[0][0]) + " (" + "_" + str(ProductsCatagory[0][0]) + "_" + ") \n\t\t\t\t\t" + str(Cart[i*3]) + "x " + str(Cart[i*3+1]) + " = R"
                            Total = Total + int(Cart[i*3+1][Cart[i*3+1].find("R")+1:])*int(Cart[i*3])
                            Statement +=str((int(Cart[i*3+1][Cart[i*3+1].find("R")+1:]))*int(Cart[i*3])) + "\n"
                                                      
                        Statement += "\n*Total: R*" + "*" + str(Total) + "*"
                        
                        Test = [[KeyboardButton(text="Checkout")],[KeyboardButton(text="Edit")],[KeyboardButton(text="Delete All")],[KeyboardButton(text="Back" )]]
                        self.sender.sendMessage(Statement, parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=Test))
                
                
                

                              
                if msg["text"] == "Back" and RegisteredUserState==14:
                    RegisteredUserState=12
                    State5=1

                if msg["text"] == "Back" and RegisteredUserState==16:
                    RegisteredUserState=12
                    State5=1
                
                global SelectedItemPrice
                global Quantity
                global CartIndex
                if msg["text"] != None and RegisteredUserState==12:
                    RegisteredUserState=13
                    ProductsCartIndex = msg["text"]
                    #print("State5: " + str(State5))
                    if State5==0:
                        CartIndex = int(msg["text"].rsplit('.', 1)[0])

                    ChangePrice = "Change Price Range:\t\t[" + str(Cart[CartIndex*3-2]) +"]"
                    ChangeQuantity = "Change Quantity:\t\t[" + str(Cart[CartIndex*3-3]) + "]"
                    self.sender.sendMessage("What would you like to do?", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                        [KeyboardButton(text=ChangePrice)],[KeyboardButton(text=ChangeQuantity)],[KeyboardButton(text="Remove")],[KeyboardButton(text="Back" )]]))

                if msg["text"] == "Back" and RegisteredUserState==13:
                    if State5==0:
                        RegisteredUserState=12
                        Statement = []                   
                        for i in range (0, int(len(Cart)/3)):
                            Statement2 = 'SELECT Product_Name from  Products where Product_ID = ?'
                            ProductsName = str(i+1) + ".  " + str(ReadSqlEntry(1, Statement2, Cart[i*3+2])[0][0])
                            Statement.append([KeyboardButton(text=''+ProductsName+'')])
                            #print(Statement)
                        Statement.append([KeyboardButton(text="Back" )])
                        self.sender.sendMessage("Select which item to edit", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=Statement))
                    else:
                        State5=0

                

                if msg["text"] == "Back" and RegisteredUserState==15:
                    State6=1
                    RegisteredUserState=14
                    PriceList = ["1g", "5g", "10g", "20g", "50g", "100g"]
                    PriceList2 = []
                    for i in range (0, 6): 
                        Prices = ReadSqlEntry(1, 'SELECT Price_' + PriceList[i] + ' from ' + Catagory + ' where Product_Name = ?'  , ProductName)
                        if Prices[0][0] != None:
                            PriceList2.append(PriceList[i])
                            PriceList2.append(Prices[0][0])
                    
                    PriceLen = len(PriceList2)/2
                    Statement = []
                    for i in range (0, int(len(PriceList2)/2)):
                        Statement2 = str(PriceList2[i*2]) + ": R" + str(PriceList2[i*2+1])
                        Statement.append([KeyboardButton(text=''+Statement2+'')])
                    Statement.append([KeyboardButton(text="Back" )])
                    self.sender.sendMessage("what would you like to change it to?", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=Statement))



                global RangeToChange
                if msg["text"] != None and RegisteredUserState==15:
                    Cart[CartIndex*3-2] =  RangeToChange
                    Cart[CartIndex*3-3] = msg["text"]

                    RegisteredUserState=11
                    Statement = "Here Are Your Cart Contents... \n\n"

                    Statement += "*" + str(StoreName) + "*" 
                    Statement += " Store: \n\n"
                    Total=0
                    for i in range (0, int(len(Cart)/3)):
                        Statement += str(i+1) + ".\t\t"
                        Statement2 = 'SELECT Product_Name from  Products where Product_ID = ?'
                        Statement3 = 'SELECT Product_Catagory from  Products where Product_ID = ?'
                        ProductsName = ReadSqlEntry(1, Statement2, Cart[i*3+2])
                        ProductsCatagory = ReadSqlEntry(1, Statement3, Cart[i*3+2])
                        Statement += str(ProductsName[0][0]) + " (" + "_" + str(ProductsCatagory[0][0]) + "_" + ") \n\t\t\t\t\t" + str(Cart[i*3]) + "x " + str(Cart[i*3+1]) + " = R"
                        Total = Total + int(Cart[i*3+1][Cart[i*3+1].find("R")+1:])*int(Cart[i*3])
                        Statement +=str((int(Cart[i*3+1][Cart[i*3+1].find("R")+1:]))*int(Cart[i*3])) + "\n"
                                                      
                    Statement += "\n*Total: R*" + "*" + str(Total) + "*"
                        
                    Test = [[KeyboardButton(text="Checkout")],[KeyboardButton(text="Edit")],[KeyboardButton(text="Delete All")],[KeyboardButton(text="Back" )]]
                    self.sender.sendMessage(Statement, parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=Test))


                



                if msg["text"] != None and RegisteredUserState==14:
                    if State6==0:
                        RegisteredUserState=15
                        RangeToChange = msg["text"]
                        self.sender.sendMessage("How many...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                            [KeyboardButton(text="1"), KeyboardButton(text="2")],[KeyboardButton(text="3"), KeyboardButton(text="4")],[KeyboardButton(text="5"), KeyboardButton(text="6")],[KeyboardButton(text="Back" )]]))

                    else:
                        State6=0

                
                    


                
                if "Change Price Range" in msg["text"] and RegisteredUserState==13:
                    RegisteredUserState=14
                    PriceList = ["1g", "5g", "10g", "20g", "50g", "100g"]
                    PriceList2 = []
                    State6=0
                    for i in range (0, 6): 
                        Prices = ReadSqlEntry(1, 'SELECT Price_' + PriceList[i] + ' from ' + Catagory + ' where Product_Name = ?'  , ProductName)
                        if Prices[0][0] != None:
                            PriceList2.append(PriceList[i])
                            PriceList2.append(Prices[0][0])
                    
                    PriceLen = len(PriceList2)/2
                    Statement = []
                    for i in range (0, int(len(PriceList2)/2)):
                        Statement2 = str(PriceList2[i*2]) + ": R" + str(PriceList2[i*2+1])
                        Statement.append([KeyboardButton(text=''+Statement2+'')])
                    Statement.append([KeyboardButton(text="Back" )])
                    self.sender.sendMessage("what would you like to change it to?", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=Statement))


                



                if msg["text"] != None and RegisteredUserState==16:
                    Cart[CartIndex*3-3] = msg["text"]

                    RegisteredUserState=11
                    Statement = "Here Are Your Cart Contents... \n\n"

                    Statement += "*" + str(StoreName) + "*" 
                    Statement += " Store: \n\n"
                    Total=0
                    for i in range (0, int(len(Cart)/3)):
                        Statement += str(i+1) + ".\t\t"
                        Statement2 = 'SELECT Product_Name from  Products where Product_ID = ?'
                        Statement3 = 'SELECT Product_Catagory from  Products where Product_ID = ?'
                        ProductsName = ReadSqlEntry(1, Statement2, Cart[i*3+2])
                        ProductsCatagory = ReadSqlEntry(1, Statement3, Cart[i*3+2])
                        Statement += str(ProductsName[0][0]) + " (" + "_" + str(ProductsCatagory[0][0]) + "_" + ") \n\t\t\t\t\t" + str(Cart[i*3]) + "x " + str(Cart[i*3+1]) + " = R"
                        Total = Total + int(Cart[i*3+1][Cart[i*3+1].find("R")+1:])*int(Cart[i*3])
                        Statement +=str((int(Cart[i*3+1][Cart[i*3+1].find("R")+1:]))*int(Cart[i*3])) + "\n"
                                                      
                    Statement += "\n*Total: R*" + "*" + str(Total) + "*"
                        
                    Test = [[KeyboardButton(text="Checkout")],[KeyboardButton(text="Edit")],[KeyboardButton(text="Delete All")],[KeyboardButton(text="Back" )]]
                    self.sender.sendMessage(Statement, parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=Test))


                
                if "Change Quantity" in msg["text"] and RegisteredUserState==13:
                    RegisteredUserState=16
                    self.sender.sendMessage("How many would you like to change it to?", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                            [KeyboardButton(text="1"), KeyboardButton(text="2")],[KeyboardButton(text="3"), KeyboardButton(text="4")],[KeyboardButton(text="5"), KeyboardButton(text="6")],[KeyboardButton(text="Back" )]]))

              
                    

                if msg["text"] == "Remove" and RegisteredUserState==13:
                    CartIndex = int(ProductsCartIndex.rsplit('.', 1)[0])
                    del Cart[CartIndex*3-3:CartIndex*3]

                    if len(Cart) == 0:
                        RegisteredUserState=4
                        State3=1
                        self.sender.sendMessage("Sorry No Items In The Cart")
                    else:
                        RegisteredUserState=11
                        Statement = "Here Are Your Cart Contents... \n\n"

                        Statement += "*" + str(StoreName) + "*" 
                        Statement += " Store: \n\n"
                        Total=0
                        for i in range (0, int(len(Cart)/3)):
                            Statement += str(i+1) + ".\t\t"
                            Statement2 = 'SELECT Product_Name from  Products where Product_ID = ?'
                            Statement3 = 'SELECT Product_Catagory from  Products where Product_ID = ?'
                            ProductsName = ReadSqlEntry(1, Statement2, Cart[i*3+2])
                            ProductsCatagory = ReadSqlEntry(1, Statement3, Cart[i*3+2])
                            Statement += str(ProductsName[0][0]) + " (" + "_" + str(ProductsCatagory[0][0]) + "_" + ") \n\t\t\t\t\t" + str(Cart[i*3]) + "x " + str(Cart[i*3+1]) + " = R"
                            Total = Total + int(Cart[i*3+1][Cart[i*3+1].find("R")+1:])*int(Cart[i*3])
                            Statement +=str((int(Cart[i*3+1][Cart[i*3+1].find("R")+1:]))*int(Cart[i*3])) + "\n"
                                                      
                        Statement += "\n*Total: R*" + "*" + str(Total) + "*"
                        
                        Test = [[KeyboardButton(text="Checkout")],[KeyboardButton(text="Edit")],[KeyboardButton(text="Delete All")],[KeyboardButton(text="Back" )]]
                        self.sender.sendMessage(Statement, parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=Test))

            
                
                if msg["text"] == "Edit" and RegisteredUserState==11:
                    State5=0
                    RegisteredUserState=12
                    Statement = []                   
                    for i in range (0, int(len(Cart)/3)):
                        Statement2 = 'SELECT Product_Name from  Products where Product_ID = ?'
                        ProductsName = str(i+1) + ".  " + str(ReadSqlEntry(1, Statement2, Cart[i*3+2])[0][0])
                        Statement.append([KeyboardButton(text=''+ProductsName+'')])
                        #print(Statement)
                    Statement.append([KeyboardButton(text="Back" )])
                    self.sender.sendMessage("Select which item to edit", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=Statement))
                
                


                global ProductId               
                if msg["text"] != None and RegisteredUserState==9:
                    RegisteredUserState=10
                    Quantity = msg["text"]
                    SelectedItemPrice2=SelectedItemPrice[SelectedItemPrice.find("R")+1:]
                    #print (SelectedItemPrice)
                    Statement = "Add... " + '\n\n' + str(msg["text"]) + "x " + str(SelectedItemPrice) + '\n' + "Total: " + "R" + str(int(msg["text"])*int(SelectedItemPrice2)) + '\n\n' + "To Cart?"
                    self.sender.sendMessage(Statement, parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                        [KeyboardButton(text="Yes")],[KeyboardButton(text="No")]]))
                
                    
                if msg["text"] == "Yes" and RegisteredUserState==10:
                    State2=1
                    Cart.append(Quantity)
                    Cart.append(SelectedItemPrice)
                    Cart.append(ProductId[0][0])
                    RegisteredUserState=5
                    self.sender.sendMessage("Added To Cart")
                    #print(Cart)

                if msg["text"] == "No" and RegisteredUserState==10:
                    RegisteredUserState=5
                    State2=1

                if msg["text"] != None and RegisteredUserState==8:
                    RegisteredUserState=9
                    SelectedItemPrice = msg["text"]
                    self.sender.sendMessage("How many...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                        [KeyboardButton(text="1"), KeyboardButton(text="2")],[KeyboardButton(text="3"), KeyboardButton(text="4")],[KeyboardButton(text="5"), KeyboardButton(text="6")],[KeyboardButton(text="Back" )]]))

                

                
                if msg["text"] == "Add To Cart" and RegisteredUserState==7:
                    RegisteredUserState=8
                    PriceList = ["1g", "5g", "10g", "20g", "50g", "100g"]
                    PriceList2 = []
                    for i in range (0, 6): 
                        Prices = ReadSqlEntry(1, 'SELECT Price_' + PriceList[i] + ' from ' + Catagory + ' where Product_Name = ?'  , ProductName)
                        if Prices[0][0] != None:
                            PriceList2.append(PriceList[i])
                            PriceList2.append(Prices[0][0])
                    
                    PriceLen = len(PriceList2)/2
                    Statement = []
                    for i in range (0, int(len(PriceList2)/2)):
                        Statement2 = str(PriceList2[i*2]) + ": R" + str(PriceList2[i*2+1])
                        Statement.append([KeyboardButton(text=''+Statement2+'')])
                    Statement.append([KeyboardButton(text="Back" )])
                    self.sender.sendMessage("Pick a quantity...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=Statement))


                   
               
                global Products
                if msg["text"] != None and RegisteredUserState==6:
                    RegisteredUserState=7
                    #print(Catagory)
                    #print(msg["text"])
                    Statement = 'SELECT Image from ' + Catagory + ' where Product_Name = ?'
                    Statement2 = 'SELECT Product_ID from  Products where Product_Name = ?'
                    ProductId = ReadSqlEntry(1, Statement2, msg["text"])  
                    Image = ReadSqlEntry(1, Statement, msg["text"])
                    ProductName = msg["text"]
                    if Image[0][0] != None:
                        print("Image Found")
                        name = randint(0, 10000)
                        ImagePath =  ImageTempPath + str(name) + '.jpg'      
                        writeTofile((Image[0])[0], ImagePath)                    
                        self.sender.sendPhoto(open(ImageTempPath + str(name) + '.jpg', 'rb'))
                        os.remove(ImageTempPath + str(name) + '.jpg')
                    
                    Description = ReadSqlEntry(1, 'SELECT Product_Description from ' + Catagory + ' where Product_Name = ?' , msg["text"])

                    
                    PriceList = ["1g", "5g", "10g", "20g", "50g", "100g"]
                    PriceString = ""
                    for i in range (0, 6):
                        Prices = ReadSqlEntry(1, 'SELECT Price_' + PriceList[i] + ' from ' + Catagory + ' where Product_Name = ?'  , msg["text"])
                        if Prices[0][0] != None:
                            PriceString = PriceString +  str(PriceList[i])  + ": R" +  str(Prices[0][0]) + '\n'
                    #print (PriceString)    



                    Message = 'Category: ' + Catagory + '\n' + 'Type: ' + msg["text"] + '\n' + '\n' + 'Description... ' + '\n' + '\n' + str(Description[0][0]) + '\n' + '\n' + "Price(s)..." + '\n' + '\n' + PriceString
                    self.sender.sendMessage(Message, parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                            [KeyboardButton(text="Add To Cart" )], [KeyboardButton(text="Back" )]]))

                
                if msg["text"] != None and RegisteredUserState==5:
                    RegisteredUserState=6
                    if State2==0:
                        Catagory = msg["text"]
                        Statement = 'SELECT Product_Name from ' + str(msg["text"]) + ' where StoreName = ?'
                        Products = ReadSqlEntry(1, Statement, StoreName)
                    elif State2==1:                       
                        Statement = 'SELECT Product_Name from ' + Catagory + ' where StoreName = ?'
                        Products = ReadSqlEntry(1, Statement, StoreName)
                    
                    if len(Products)<1:
                        self.sender.sendMessage("Sorry no items in store...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                            [KeyboardButton(text="Back" )]]))
                    else:
                        Statement =[]
                        for i in range (0, int(len(Products))):
                            ProductsName = str(Products[i][0])
                            Statement.append([KeyboardButton(text=''+ProductsName+'')])
                        Statement.append([KeyboardButton(text="Back" )])
                        self.sender.sendMessage("Here are the items available...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=Statement))   
                                                                
                  
                
                if msg["text"] != None and RegisteredUserState==4:
                    RegisteredUserState=5  
                    State2=0
                    State=0
                    if State3==0:
                        StoreId = ReadSqlEntry(1, "SELECT Id from User where StoreName = ?", msg["text"])                   
                        StoreName = msg["text"]                   
                        Catagories = ReadSqlEntry(1, "SELECT Product_Catagory from Products where Id = ?", StoreId[0][0])
                        New_Catagories = []
                        for elem in Catagories:
                            if elem not in New_Catagories:
                                New_Catagories.append(elem)
                        Catagories = New_Catagories
                    elif State3==1:
                        StoreId = ReadSqlEntry(1, "SELECT Id from User where StoreName = ?", StoreName)                                 
                        Catagories = ReadSqlEntry(1, "SELECT Product_Catagory from Products where Id = ?", StoreId[0][0])
                        New_Catagories = []
                        for elem in Catagories:
                            if elem not in New_Catagories:
                                New_Catagories.append(elem)
                        Catagories = New_Catagories
                    
                    #print (Cart)
                    if str(Cart)=="[]":
                        CartString = "Cart (0)"
                    else:
                        CartString = "Cart (" + str((int(len(Cart)/3))) + ")"
                    
                    if len(Catagories)<1:
                        self.sender.sendMessage("Sorry no items in store...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                            [KeyboardButton(text="Back" )]]))
                    else:
                        Statement =[]
                        for i in range (0, int(len(Catagories))):
                            CatagoriesStr = str(Catagories[i][0])
                            Statement.append([KeyboardButton(text=''+CatagoriesStr+'')])
                        Statement.append([KeyboardButton(text=CartString )])
                        Statement.append([KeyboardButton(text="Back" )])
                        self.sender.sendMessage("Here are the catagories available...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=Statement))   
                                                                
                  

                
                if msg["text"] == "Collect" and RegisteredUserState==3:
                    State3=0
                    State4=0
                    RegisteredUserState=4
                    Sellers = []
                    SellersNearMe = []
                    SellersNearMe2 = []
                    conn = create_connection(SqlitePath)
                    cur = conn.cursor()
                    cur.execute("SELECT Id FROM User WHERE TGReferralState = ?", ('SELLER CONFIRMED',))
                    rows = cur.fetchall()
                    for row in rows:
                        CheckSellerType = ReadSqlEntry(1, "SELECT StoreType from User where Id = ?", (row[0]))
                        #print(CheckSellerType[0][0])
                        if int(CheckSellerType[0][0]) == 1 or int(CheckSellerType[0][0]) == 3 or int(CheckSellerType[0][0]) == 5 or int(CheckSellerType[0][0]) == 6:   #1 - Collect, 2 = Deliver, 3 - Collect and Deliver, 4 - Courier, 5 Collect and Courier, 6 - Collect, Deliver and Courier, 7 - Deliver and Courier                         
                            Sellers.append(row)
                    
                    
                    NumSellers = (len(Sellers))
                    BuyerLatLong = ReadSqlEntry(1, "SELECT Latitude, Longitude from User where User_ID = ?", Msg_ID)
                    #SellerLatLong = ReadSqlEntry(1, "SELECT Latitude, Longitude from User where Id = ?", SellersNearMe[i][0])
                    for i in range (0, NumSellers):
                         SellerLatLong = ReadSqlEntry(1, "SELECT Latitude, Longitude from User where Id = ?", Sellers[i][0])
                         distanceapart = GetLocationDistance(BuyerLatLong[0][0], BuyerLatLong[0][1], SellerLatLong[0][0], SellerLatLong[0][1])
                         if distanceapart <= 10:
                            SellersNearMe.extend(Sellers[i])
                    Sellers = []

                    for i in range (0, len(SellersNearMe)):                       
                        OnlineOffline = ReadSqlEntry(1, "SELECT OnlineOffline from User where Id = ?", SellersNearMe[i])[0][0]
                        if OnlineOffline == 1:
                            SellersNearMe2.append(SellersNearMe[i])

                    SellersNearMe = SellersNearMe2
                    SellersNearMe2 =[]

                    Now = datetime.datetime.now()
                    NowHour = Now.hour
                    
                    for i in range (0, len(SellersNearMe)):
                        OpenHours = ReadSqlEntry(1, "SELECT Timer24Hours from User where Id = ?", SellersNearMe[i])[0][0]
                        if OpenHours == "24":
                            SellersNearMe2.append(SellersNearMe[i])
                        else:
                            OpenTime = OpenHours[0:2]
                            CloseTime = OpenHours[2:4]
                            if NowHour > int(OpenTime) and int(OpenTime) < NowHour:
                                SellersNearMe2.append(SellersNearMe[i])

                    SellersNearMe = SellersNearMe2
                    SellersNearMe2 =[]


                    if len(SellersNearMe)<1:
                        self.sender.sendMessage("Sorry no Stores near you...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                            [KeyboardButton(text="Back" )]]))
                    else:
                        Statement =[]
                        for i in range (0, int(len(SellersNearMe))):
                            StoresStr = ReadSqlEntry(1, "SELECT StoreName from User where Id = ?", SellersNearMe[i])[0][0]
                            #print(StoresStr)
                            Statement.append([KeyboardButton(text=''+StoresStr+'')])
                        Statement.append([KeyboardButton(text="Back" )])
                        self.sender.sendMessage("Here are the Stores available near you for collection...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=Statement))   
                                       
            
            if msg["text"] == "Deliver" and RegisteredUserState==3:
                    State3=0
                    State4=0
                    RegisteredUserState=4
                    Sellers = []
                    SellersNearMe = []
                    SellersNearMe2 = []
                    conn = create_connection(SqlitePath)
                    cur = conn.cursor()
                    cur.execute("SELECT Id FROM User WHERE TGReferralState = ?", ('SELLER CONFIRMED',))
                    rows = cur.fetchall()
                    for row in rows:
                        CheckSellerType = ReadSqlEntry(1, "SELECT StoreType from User where Id = ?", (row[0]))
                        print(CheckSellerType[0][0])
                        if int(CheckSellerType[0][0]) == 2 or int(CheckSellerType[0][0]) == 3 or int(CheckSellerType[0][0]) == 6 or int(CheckSellerType[0][0]) == 7:   #1 - Collect, 2 = Deliver, 3 - Collect and Deliver, 4 - Courier, 5 Collect and Courier, 6 - Collect, Deliver and Courier, 7 - Deliver and Courier                         
                            Sellers.append(row)
                    
                    
                    NumSellers = (len(Sellers))
                    BuyerLatLong = ReadSqlEntry(1, "SELECT Latitude, Longitude from User where User_ID = ?", Msg_ID)
                    #SellerLatLong = ReadSqlEntry(1, "SELECT Latitude, Longitude from User where Id = ?", SellersNearMe[i][0])
                    for i in range (0, NumSellers):
                         SellerLatLong = ReadSqlEntry(1, "SELECT Latitude, Longitude from User where Id = ?", Sellers[i][0])
                         distanceapart = GetLocationDistance(BuyerLatLong[0][0], BuyerLatLong[0][1], SellerLatLong[0][0], SellerLatLong[0][1])
                         if distanceapart <= 10:
                            SellersNearMe.extend(Sellers[i])
                    Sellers = []

                    for i in range (0, len(SellersNearMe)):                       
                        OnlineOffline = ReadSqlEntry(1, "SELECT OnlineOffline from User where Id = ?", SellersNearMe[i])[0][0]
                        if OnlineOffline == 1:
                            SellersNearMe2.append(SellersNearMe[i])

                    SellersNearMe = SellersNearMe2
                    SellersNearMe2 =[]

                    Now = datetime.datetime.now()
                    NowHour = Now.hour
                    
                    for i in range (0, len(SellersNearMe)):
                        OpenHours = ReadSqlEntry(1, "SELECT Timer24Hours from User where Id = ?", SellersNearMe[i])[0][0]
                        if OpenHours == "24":
                            SellersNearMe2.append(SellersNearMe[i])
                        else:
                            OpenTime = OpenHours[0:2]
                            CloseTime = OpenHours[2:4]
                            if NowHour > int(OpenTime) and int(OpenTime) < NowHour:
                                SellersNearMe2.append(SellersNearMe[i])

                    SellersNearMe = SellersNearMe2
                    SellersNearMe2 =[]


                    if len(SellersNearMe)<1:
                        self.sender.sendMessage("Sorry no Stores near you...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=[
                            [KeyboardButton(text="Back" )]]))
                    else:
                        Statement =[]
                        for i in range (0, int(len(SellersNearMe))):
                            StoresStr = ReadSqlEntry(1, "SELECT StoreName from User where Id = ?", SellersNearMe[i])[0][0]
                            print(StoresStr)
                            Statement.append([KeyboardButton(text=''+StoresStr+'')])
                        Statement.append([KeyboardButton(text="Back" )])
                        self.sender.sendMessage("Here are the Stores available near you for Delivery...", parse_mode= 'Markdown', reply_markup=ReplyKeyboardMarkup(resize_keyboard = True, keyboard=Statement))   
                                       



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
                        UnregisteredUserState=0
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

            
            else:            
                if msg["text"] == "Back" and State==1:
                    State=0
                    RegisteredUserState=0
                    self.sender.sendMessage("Welcome back to the Telsto main menu, please select one of the following options...", parse_mode= 'Markdown',
                                reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                    keyboard=[
                                        [KeyboardButton(text="Mary J Near Me" )],
                                        [KeyboardButton(text="Mary J Courier" )],
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
                                    [KeyboardButton(text="Account Settings" )]
                            ]
                        ))


                else:
                    self.sender.sendMessage(NameForSearch + " not found.", reply_markup=ReplyKeyboardRemove())


        except KeyError as error:   
                pass  







def main():
    print ("Program Start")

    

    

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

#CREATE VIEW Outdoor AS
#	SELECT b.User_ID, b.StoreName, a.Product_Name, a.Product_Description, a.Price_1g, a.Price_5g, a.Price_10g, a.Price_20g, a.Price_50g, a.Price_100g, a.Image
#		FROM Products a, User b
#		WHERE Product_Catagory = "OUTDOOR"
#		AND a.Id = b.Id