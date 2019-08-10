from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import logging
import os
import settings
import systemInfo

from Utils.dbutils import DBUtil

from models.user import UserModel

masterUserId = os.getenv('master_user_id')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

updater = Updater(token=os.getenv("telegram_token"), use_context=True)

DBUtil.initDB()

job_queue = updater.job_queue

sysInf = systemInfo.BasicSystemInfo()

def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def sysInfo(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=sysInf.getSysInfo())

systemInfo_handler = CommandHandler('sysinfo', sysInfo)
dispatcher.add_handler(systemInfo_handler)

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



def callback_minute(context):
    context.bot.send_message(chat_id=masterUserId, 
                             text='One message every minute')

job_minute = job_queue.run_repeating(callback_minute, interval=60, first=0)

updater.start_polling()