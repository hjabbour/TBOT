from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import pandas as pd 
from pandas_datareader import data
import json


import logging
import os

import telegram_bot.settings

from . utils.dbutils import DBUtil
from . models.user import UserModel
from . system_info import BasicSystemInfo


masterUserId = os.getenv('master_user_id')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

updater = Updater(token=os.getenv("telegram_token"), use_context=True)

DBUtil.initDB()

job_queue = updater.job_queue

sysInf = BasicSystemInfo()
listCommand = []

def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def sysInfo(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=sysInf.getSysInfo())

systemInfo_handler = CommandHandler('sysinfo', sysInfo)
dispatcher.add_handler(systemInfo_handler)

def helP(update, context):
    
    context.bot.send_message(chat_id=update.message.chat_id, text=listCommand)

helP_handler = CommandHandler('help', helP)
dispatcher.add_handler(helP_handler)

def capRatio(update, context):
    cap = pd.read_csv('/localdata/capratio.csv')
    cap = pd.DataFrame(cap, columns =['Indicator','supply_ratio','cap_ratio']) 
    #result = cap.to_json(orient="table")
    #parsed = json.loads(result)
    #msgcap = parsed
    msgcap = cap.to_markdown()
    context.bot.send_message(chat_id=update.message.chat_id, text=msgcap)

capRatio_handler = CommandHandler('capratio', capRatio)
listCommand.append('/capratio')
dispatcher.add_handler(capRatio_handler)

def allBands(update, context):
    allb = pd.read_csv('/localdata/allbands.csv')
    allb = pd.DataFrame(allb, columns =['Indicator','RED','ORANGE','GREEN','Current']) 
    #result = cap.to_json(orient="table")
    #parsed = json.loads(result)
    #msgcap = parsed
    for i, j in zip(range(0,len(allb.index),30), range(30,len(allb.index),30)):
        msgcap = allb.iloc[i:j,0:5]
        msgcap= msgcap.to_markdown()
        context.bot.send_message(chat_id=update.message.chat_id, text=msgcap)
        if j+30 > len(allb.index):
            msgcap = allb.iloc[j:len(allb.index),0:5]
            msgcap = msgcap.to_markdown()
            context.bot.send_message(chat_id=update.message.chat_id, text=msgcap)
allBands_handler = CommandHandler('allbands', allBands)
listCommand.append('/allbands')
dispatcher.add_handler(allBands_handler)


def orangeBand(update, context):
    orangeb = pd.read_csv('/localdata/orangeband.csv')
    orangeb1 = pd.DataFrame(orangeb, columns =['Indicator','GREEN','ORANGE','RED','Current']) 
    orangeb = orangeb1[['Indicator','ORANGE','Current']]
    #result = cap.to_json(orient="table")
    #parsed = json.loads(result)
    #msgcap = parsed
    for i, j in zip(range(0,len(orangeb.index),30), range(30,len(orangeb.index),30)):
        msgcap = orangeb.iloc[i:j,0:5]
        msgcap= msgcap.to_markdown()
        context.bot.send_message(chat_id=update.message.chat_id, text=msgcap)
        if j+30 > len(orangeb.index):
            msgcap = orangeb.iloc[j:len(orangeb.index),0:5]
            msgcap = msgcap.to_markdown()
            context.bot.send_message(chat_id=update.message.chat_id, text=msgcap)
orangeBand_handler = CommandHandler('orangeband', orangeBand)
listCommand.append('/orangeband')
dispatcher.add_handler(orangeBand_handler)


def easyBand(update, context):
    easyb = pd.read_csv('/localdata/easyband.csv')
    easyb1 = pd.DataFrame(easyb, columns =['Indicator','ATH','CLOSERATIO','RED','ORANGE','GREEN','Current']) 
    easyb = easyb1[['Indicator','GREEN','Current']]
    #result = cap.to_json(orient="table")
    #parsed = json.loads(result)
    #msgcap = parsed
    for i, j in zip(range(0,len(easyb.index),5), range(5,len(easyb.index),5)):
        msgcap = easyb.iloc[i:j,0:3]
        msgcap= msgcap.to_markdown()
        context.bot.send_message(chat_id=update.message.chat_id, text=msgcap)
        if j+5 > len(easyb.index):
            msgcap = easyb.iloc[j:len(easyb.index),0:3]
            msgcap = msgcap.to_markdown()
            context.bot.send_message(chat_id=update.message.chat_id, text=msgcap)
easyBand_handler = CommandHandler('easyband', easyBand)
listCommand.append('/easyband')
dispatcher.add_handler(easyBand_handler)

def echo(update, context):
    logging.info(f"MESSAGE {update.message}")
    context.bot.send_message(chat_id=update.message.chat_id, text=f'thanks {update.message.from_user.first_name}')

def selfie(update, context):
    logging.info(f"PHOTO {update}")
    context.bot.send_message(chat_id=update.message.chat_id, text=f'thanks {update.message.from_user.first_name} for the photo')

def all(update, context):
    user = UserModel.get_or_none(UserModel.telegramUserId == update.message.from_user.id)
    if user is None :
        newUser = UserModel.create(telegramUserId = update.message.from_user.id, firstName=update.message.from_user.first_name, lastName=update.message.from_user.last_name, userName=update.message.from_user.username)
        newUser.save()

    logging.info(f"UNKNOWN {update}")
    context.bot.send_message(chat_id=update.message.chat_id, text=f'???? {update.message.from_user.first_name} ')

echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)

photo_handler = MessageHandler(Filters.photo, selfie)
dispatcher.add_handler(photo_handler)

all_handler = MessageHandler(Filters.all, all)
dispatcher.add_handler(all_handler)



#def callback_minute(context):
#    context.bot.send_message(chat_id=masterUserId, 
#                             text='One message every minute')

#job_minute = job_queue.run_repeating(callback_minute, interval=60, first=0)

def config():
    pass
    

def main():
    updater.start_polling()


if __name__ == "__main__" :
    main()