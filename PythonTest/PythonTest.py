import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
from pprint import pprint
#import ConfigParser
#import threading
#from threading import Thread
#import time
#import datetime
from datetime import datetime
from datetime import timedelta

bot = telepot.Bot('320663225:AAFVzc1y_7dLUu97g1kqbw9PxkQU1aiSUMk')

WelcomeMessage = "Welcome to <Placeholer>, please send us your the name of your suburb or hit the GEO LOCATION button below"


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    Test = msg    
    #print (Test)

    
    
    if "location" in msg:
        print ("Location Found")
    
    
    if msg['text'] == "/start":
        bot.sendMessage(chat_id, WelcomeMessage,
                            reply_markup=ReplyKeyboardMarkup(resize_keyboard = True,
                                keyboard=[
                                    [KeyboardButton(text="\U0001f4cd GEO LOCATION \U0001f4cd", request_location=True)]
                                ]
                            ))
        
 
MessageLoop(bot, handle).run_as_thread()

ReplyKeyboardMarkup(keyboard=[[
    KeyboardButton(
        text='Location',
        request_location=True
    )
]])

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


