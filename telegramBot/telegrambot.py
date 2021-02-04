"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import requests
import re
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
import threading
from datetime import datetime as dt
import mariadb
import time
import sys
import numpy as np
import praw

reddit = praw.Reddit(client_id='9Z2rDs0Ca9vvjw',
                     client_secret='gfiiZR7shkpYLiwxvk_LONioeb-iKg',
                     user_agent='telegram meme bot 1.0 by  /u/willham93')

try:
    conn = mariadb.connect(
        user="reminder",
        password="hami5547",
        host="127.0.0.1",
        port=3306,
        database="remindersdb")
except mariadb.Error as e:
    print(f"error connecting:{e}")
    sys.exit(1)

cur = conn.cursor()
temp = 0
bot = telegram.Bot(token="1574500597:AAH0cU4EFdJzrwtxcgSpyy5MA1ijtoowPR4")
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

eightBallResponse = ["yes", "no", "ask again later", "never in your life"]


def threadFunction():
    global temp
    while True:
        x = time.time()
        if x - temp >= 1:
            readDBandSend()
            temp = x


def readDBandSend():
    lines = list()
    now = dt.now()
    now = now.strftime("%Y-%m-%d %H:%M")
    t = now.split(' ')[1]
    date = now.split(' ')[0]
    cur.execute("SELECT * FROM Reminders where date=? AND time=?",
                (now.split(' ')[0], now.split(' ')[1]))
    for row in cur:
        body = row[3].replace("'", '')
        id = row[2].replace("'", '')
        bot.sendMessage(chat_id=id, text=body)
        query = f"DELETE FROM Reminders WHERE  telegram_id='{id}' AND message='{body}' AND date='{date}' AND time='{t}'"
        lines.append(query)
    for line in lines:
        cur.execute(line)
        conn.commit()


def get_url_dog():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url


def get_url_cat():
    response = requests.get('https://aws.random.cat/meow')
    data = response.json()
    url = data['file']
    return url


def get_image_url_dog():
    allowed_extension = ['jpg', 'jpeg', 'png']
    file_extension = ''
    while file_extension not in allowed_extension:
        url = get_url_dog()
        file_extension = re.search("([^.]*)$", url).group(1).lower()
    return url


def get_image_url_cat():
    allowed_extension = ['jpg', 'jpeg', 'png']
    file_extension = ''
    while file_extension not in allowed_extension:
        url = get_url_cat()
        file_extension = re.search("([^.]*)$", url).group(1).lower()
    return url


def boop(update, context):
    url = get_image_url_dog()
    user = update.message.from_user
    print('You talk with user {} and his user ID: {} '.format(user['username'], user['id']))
    # chat_id = update.message.chat_id
    # bot.send_photo(chat_id=chat_id, photo=url)
    context.bot.send_photo(chat_id=user['id'], photo=url)


def meow(update, context):
    url = get_image_url_cat()
    user = update.message.from_user
    print('You talk with user {} and his user ID: {} '.format(user['username'], user['id']))
    # chat_id = update.message.chat_id
    # bot.send_photo(chat_id=chat_id, photo=url)
    context.bot.send_photo(chat_id=user['id'], photo=url)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('use /help to get a list of commands')


def help(update, context):
    """Send a message when the command /help is issued."""
    help = "list of commands:\n /boop get random dog picture\n " \
           "/meow get random cat picture \n" \
           "/reminder send a reminder at a set date/time user following format \"/message/yyyy-mm-dd/hh:mm\" user 24hr time\n" \
           "/8ball ask the magic 8ball a question\n" \
           "/meme random hot meme from r/memes" \
           ""
    update.message.reply_text(help)


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def reminder(update, context):
    user = update.message.from_user
    text = update.message.text
    text = text.replace("/reminder", "")
    text = text.split('/')

    msg = text[0]
    date = text[1]
    time = text[2]
    dformat = "%Y-%m-%d"
    tformat = "%H:%M"
    try:
        validDate = dt.strptime(date, dformat)
        try:
            validTime = dt.strptime(time, tformat)
            id = user['id']
            realDate = str(validDate).split(' ')[0]
            realTime = str(validTime).split(' ')[1]
            realTime = realTime[:-3]
            query = f"INSERT INTO Reminders (telegram_id,message,send_method,date,time) VALUES (\'{id}\',\'{msg}\',\'telegram\',\'{realDate}\',\'{realTime}\')"
            print(query)
            cur.execute(query)
            conn.commit()
            print(msg, date, time, id)
            update.message.reply_text("reminder added")
        except ValueError:
            update.message.reply_text("Please enter time in the correct format")
    except ValueError:
        update.message.reply_text("Please enter a correctly formated date")


def eightball(update, context):
    rnd = np.random.randint(0, len(eightBallResponse))
    answer = eightBallResponse[rnd]
    update.message.reply_text(answer)


def meme(update, context):
    memes_submissions = reddit.subreddit('memes').new(limit=100)
    post_to_pick = np.random.randint(1, 100)
    count = 0
    sub = ""
    for submission in memes_submissions:
        if count == post_to_pick:
            sub = submission.url
            break
        count += 1
    user = update.message.from_user
    print(user['id'])
    context.bot.send_photo(chat_id=user['id'], photo=sub)


def get_reddit(update, context):
    subred = update.message.text.split(' ')[1]
    memes_submissions = reddit.subreddit(subred).new(limit=100)
    post_to_pick = np.random.randint(1, 100)
    count = 0
    sub = ""
    for submission in memes_submissions:
        if count == post_to_pick:
            sub = submission.url
            break
        count += 1
    user = update.message.from_user
    context.bot.send_photo(chat_id=user['id'], photo=sub)


def main():
    t = threading.Thread(target=threadFunction)
    t.daemon = True
    t.start()
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1574500597:AAH0cU4EFdJzrwtxcgSpyy5MA1ijtoowPR4", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler('boop', boop))
    dp.add_handler(CommandHandler('8ball', eightball))
    dp.add_handler(CommandHandler('meow', meow))
    dp.add_handler(CommandHandler('meme', meme))
    dp.add_handler(CommandHandler('reddit', get_reddit))
    dp.add_handler(CommandHandler("reminder", reminder))
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
