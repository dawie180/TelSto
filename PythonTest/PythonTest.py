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

bot = telepot.Bot('320663225:AAFVzc1y_7dLUu97g1kqbw9PxkQU1aiSUMk')

WelcomeMessage = "Welcome to <Placeholer>, please send us your location"


def handle(msg):
    pprint(msg)
   
    if msg['text'] == "/start":
        bot.sendMessage(297725915, WelcomeMessage)
        
 
MessageLoop(bot, handle).run_as_thread()




