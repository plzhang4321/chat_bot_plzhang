from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import configparser
import logging
import redis
import os
global redis1

# test
def main():
    # Load your token and create an Updater for your Bot

    # config = configparser.ConfigParser()
    # config.read('config.ini')
    updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    global redis1
    redis1 = redis.Redis(host=(os.environ['HOST']), password=(os.environ['PASSWORD']),
                         port=(os.environ['REDISPORT']))

    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("hiking", hiking))

    # To start the bot:
    updater.start_polling()
    updater.idle()


def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


# Define a few command handlers. These usually take the one arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

def hiking(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /hiking is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]  # /hiking keyword <-- this should store the keyword
        if redis1.exists(msg):
            update.message.reply_text(redis1.get(msg).decode('UTF-8'))
        else:
            msg = "*" + msg + "*"
            key = redis1.keys(msg)
            if len(key) < 1:
                update.message.reply_text(
                    "Sorry we found nothing in our record, but I recommend this to you  https://www.discoverhongkong.cn/index.html")
            else:
                reply = [x.decode('UTF-8') for x in redis1.mget(key[:min(5, len(key))])]
                update.message.reply_text("\n".join(reply))
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /hiking <keyword>')


if __name__ == '__main__':
    main()
