import logging , subprocess, os
from uuid import uuid4
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING = range(1)

def you(update, context):
    update.message.reply_text("Hi,\nEnter the youtube video link.")
    return CHOOSING

def down(update, context):
    key = update.message.chat.id
    value = update.message.text
    context.user_data[key] = value
    try:
        value = context.user_data[key]
        command = "youtube-dl {} -o video.mp4".format(value)
        pipe = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        if(pipe.stderr.readlines()):
            raise Exception("This video is download protected.")
        context.bot.send_video(chat_id=update.message.chat_id, video=open('video.mp4', 'rb'), supports_streaming=True)
        update.message.reply_text('Hope you got your video.')
        os.remove("video.mp4")
    except KeyError:
        update.message.reply_text('Not found')

    context.user_data.clear()
    return ConversationHandler.END
    
def fall(update, context):
    pass

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1088799942:AAFo4S4kaRbEbczPy_a466KYEUHeyRSi3Eo", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('youtube', you)],

        states={
            CHOOSING: [MessageHandler(Filters.text, down),
                       ],
        },

        fallbacks=[MessageHandler(Filters.text, fall)]
    )

    dp.add_handler(conv_handler)

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
