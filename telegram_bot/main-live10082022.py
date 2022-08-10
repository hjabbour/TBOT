#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
"""
databasestring = raqebloc
tablestring = raqebdata"""

from geopy.geocoders import Nominatim
import os
from pymongo import MongoClient
import pandas as pd
from pandas_datareader import data
from datetime import date
clientstring = os.environ['clientstring'] 
databasestring = os.environ['databasestring'] 
tablestring = os.environ['tablestring'] 
client = MongoClient(clientstring)
db = client[databasestring]
collection = db[tablestring]
ttoken = os.environ['telegram_token']

import logging
from typing import Dict

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import KeyboardButton,InlineKeyboardButton,InlineKeyboardMarkup,ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PicklePersistence,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE, LOCATION = range(4)

tab=[]
col=['lng','lat','loc','rawloc','user_id','product','price']
loc={}
start_keyboard = [ [KeyboardButton("\U0001F447 \U0001F447 \U0001F447  \n Click Here  to send the location\U0001F4CC \n or use the attach \U0001F4CE  location \n   \U0001F30D \U0001F30D \U0001F30D  ", request_location=True)],]
reply_keyboard = [
    ["Tomato", "Cucumber"],
    ["Chicken", "Eggs"],
    ["Meat-Beef", "Meat-Lamb"],
    ["Electricity-5A","Electricity-10A"],
    ["Other Location","Other Product"],
    ["Done"],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
startk = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=True)

def revglocation(lat,lng):
    geolocator = Nominatim(user_agent="maps_app")
    location = geolocator.reverse(str(lat)+','+str(lng))
    return location.raw

def mongoadd(data,col,conn):
    now= pd.to_datetime('today')
    logger.info(
        "data in tab  %s/  data in col %s  user %s ", tab, col,loc['userid']
    )
    frame=pd.DataFrame(data,columns=col)
    frame['time']=now
    frame['price'].astype(float)
    tab.clear()
        #frame.drop_duplicates(subset=['Time','Indicator'])
        #frame.set_index(['Time','Indicator'],inplace=True)
    data_dict = frame.to_dict("records")
    conn.insert_many(data_dict)
    #conn.append(symbol,frame)


def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation, display any stored data and ask user for input."""
    reply_text = "Hi! My name is Muraqeb "
    if context.user_data:
        reply_text += (
            f" You already shared the price of  {', '.join(context.user_data.keys())} "
            f"<b>Click the  Menu below</b> to send the location and start  reporting prices "
        )
    else:
        reply_text += (
            " I am an automated bot am here to help you report <b>Index</b> prices in your region \
            \n To track price differences  of vergabtles per example we  record prices of Tomtato and Cucumbers\
            \n Every reports starts by sending the location\
            \n <b>Click the Menu below</b> to send the location and start  reporting prices "
           
        )
    await update.message.reply_text(reply_text, reply_markup=startk,parse_mode='HTML')
    #await update.message.reply_markdown_v2(reply_text, reply_markup=startk)
   
    return LOCATION

async def custom_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for a new location."""
    await update.message.reply_text(
        'please attach the new location '
    )

    return LOCATION

async def regular_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text.lower()
    context.user_data["choice"] = text
    if context.user_data.get(text):
        reply_text = (
            f" {text}: I already know the following price: {context.user_data[text]}"
        )
    else:
        reply_text = f" {text}: please type  the Price in Lebanese Lira  example 20000 "
    await update.message.reply_text(reply_text)

    return TYPING_REPLY


async def custom_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for a description of a custom category."""
    await update.message.reply_text(
        'Alright, please type  me the product name , for example "Bananas"'
    )

    return TYPING_CHOICE


async def received_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    text = update.message.text
    category = context.user_data["choice"]
    context.user_data[category] = text.lower()
    if text.isnumeric():
        tuple=[loc['long'],loc['lat'],loc['loc'],loc['rawloc'],loc['userid'],category,float(text.lower())]
        tab.append(tuple)
        del context.user_data["choice"]

        await update.message.reply_text(
            "Neat! Just so you know, this is what you already told me:"
            f"{facts_to_str(context.user_data)}"
            "You can tell me more, change a price or "
            "If you finished please press Done ",
            reply_markup=markup,
        )

        return CHOOSING
    else:
        await update.message.reply_text(
            "Price should be a number :) example 10000",reply_markup=markup,)
        return TYPING_REPLY


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: with  id %s: bot? %s  %f / %f", user.first_name,user.id,user.is_bot, user_location.latitude, user_location.longitude
    )
    loc['lat'] = user_location.latitude
    loc['long']= user_location.longitude
    loc['loc'] = [user_location.longitude,user_location.latitude]
    loc['rawloc'] = revglocation(user_location.latitude,user_location.longitude)
    loc['userid']= user.id
    if loc['rawloc']['address']['country_code'] in ['lb','lb']:
        await update.message.reply_text(
        "choose the product to report ",reply_markup=markup,
        )
        return CHOOSING
    else: 
        await update.message.reply_text("location must be in lebanon ")
        return LOCATION

async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    await update.message.reply_text(
        "You seem a bit paranoid!"
    )

    return CHOOSING

async def show_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display the gathered info."""
    await update.message.reply_text(
        f"This is what you already told me: {facts_to_str(context.user_data)}"
    )



async def betterp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    chat_id = update.message.chat_id
    if "choice" in context.user_data:
        del context.user_data["choice"]
    if  len(tab)!=0:
        mongoadd(tab,col,collection)
    await context.bot.send_location(chat_id,latitude=33.877671, longitude=35.552461)
    await update.message.reply_text(
        f"Thank you for sharing the below: {facts_to_str(context.user_data)}Until next time!\
        \n  http://muraqeb.41lebanon.org to follow the progress ",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END



async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    if "choice" in context.user_data:
        del context.user_data["choice"]
    if  len(tab)!=0:
        mongoadd(tab,col,collection)
    await update.message.reply_text(
        f"Thank you for sharing the below: {facts_to_str(context.user_data)}Until next time!\
        \n  http://muraqeb.41lebanon.org to follow the progress ",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    persistence = PicklePersistence(filepath="conversationbot")
    application = Application.builder().token(ttoken).persistence(persistence).build()

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LOCATION: [
                MessageHandler(filters.LOCATION, location),
                CommandHandler("skip", skip_location),
            ],
            CHOOSING: [
                MessageHandler(
                    filters.Regex("^(Tomato|Cucumber|Meat-Beef|Meat-Lamb|Electricity-5A|Electricity-10A|Chicken|Eggs)$"), regular_choice
                ),
                MessageHandler(filters.Regex("^Other Product$"), custom_choice),
                MessageHandler(filters.Regex("^Other Location$"), custom_location),
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), regular_choice
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
        name="my_conversation",
        persistent=False,
        conversation_timeout = 180
    )

    application.add_handler(conv_handler)

    show_data_handler = CommandHandler("show_data", show_data)
    application.add_handler(show_data_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()