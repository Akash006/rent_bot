#!/usr/bin/env python

import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
import datetime
import telegram
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('cread_py.json', scope)
client = gspread.authorize(creds)
new_row = []
dat = datetime.date.today()
new_row.append(str(dat))

logger = logging.getLogger(__name__)

SELECT, RENT, LAST_UNIT, CURRENT_UNIT, MAID, DUSTBIN, WIFI, ADD, SHOW, T_PAID, PAID_BY, END = range(12)
        

def choose(update, context):
    reply_keyboard = [['Room-1', 'Room-2','/cancel']]
    update.message.reply_text(
        'Hi! I will collect the rent from your behalf.\n I will hold a conversation with you. '
        'Choose the room for which you want to collect.\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return SELECT

def select(update, context):
    reply_keyboard = [['Continue','/cancel']]
    room = str(update.message.text)
    global sheet, row
    if(room == 'Room-1'):
        sheet = client.open('test_sp').worksheet("Room1")
        row = sheet.row_values(2)
        context.bot.send_message(chat_id=update.effective_chat.id, text="You have choosen Room-1.",
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        #print(row)
    elif(room == 'Room-2'):
        sheet = client.open('test_sp').worksheet("Room2")
        row = sheet.row_values(2)
        context.bot.send_message(chat_id=update.effective_chat.id, text="You have choosen Room-2.",
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    else:
        update.message.reply_text(' Choose the method of payment : ')
        
    return RENT

def rent(update, context):
    prev_rent = str(row[1])
    reply_keyboard = [[prev_rent],['/cancel']]
    update.message.reply_text('Your previous rent was %s \n Press the button or type new amount' % prev_rent
        ,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return CURRENT_UNIT

def current(update, context):
    new_row.append(str(update.message.text))
    new_row.append(str(row[3]))
    
    update.message.reply_text('Last month unit : {0}\n\nEnter the current Unit :'.format(row[3]))
    return MAID


def maid(update, context):
    new_row.append(str(update.message.text))
    total = int(new_row[3])-int(new_row[2])
    new_row.append(str(total))
    total_bill = total * 9
    new_row.append(str(total_bill))
    
    prev_maid = row[6]
    reply_keyboard = [[prev_maid],['/cancel']]
    update.message.reply_text('Choose previous maid amount or enter new :',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    
    return DUSTBIN


def dustbin(update, context):
    new_row.append(str(update.message.text))
    prev_dust = row[7]
    
    reply_keyboard = [[prev_dust],['/cancel']]
    update.message.reply_text('Choose previous Dustbin amount or enter new : '
        ,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return WIFI

def wifi(update, context):
    new_row.append(str(update.message.text))
    prev_wifi = row[8]
    
    reply_keyboard = [[prev_wifi],['/cancel']]
    update.message.reply_text('Choose previous WIFI amount or enter new : '
        ,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ADD


def add(update, context):
    new_row.append(str(update.message.text))
    reply_keyboard = [['0','/cancel']]
    update.message.reply_text('Enter Additional amount or choose 0 : '
        ,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    
    return SHOW


def show(update, context):
    new_row.append(str(update.message.text))
    new_row.append(row[14])
    total_amt = int(new_row[1]) + int(new_row[5]) + int(new_row[6]) + int(new_row[7]) + int(new_row[8]) + int(new_row[9]) + int(new_row[10])
    new_row.append(str(total_amt))
    
    header = ['Date','Rent','Last Unit','Current unit','Total unit','Electricity bill',
              'Maid','Dustbin','WiFi','Additional Amt','Last Month Balance','Total Amount',
              'Total Paid', 'Paid By','Balance']

    ss = []
    for x in range(len(new_row)):
        data = '*{0}*  :  {1}'.format(header[x],new_row[x])
        ss.append(data)

    s="\n"
    context.bot.send_message(chat_id=update.effective_chat.id, 
                 text=s.join(ss), 
                 parse_mode=telegram.ParseMode.MARKDOWN)
    

    reply_keyboard = [['Continue','/cancel']]
    update.message.reply_text('Press Continue to Go Ahead',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return T_PAID

def t_paid(update, context):
    t_amt = new_row[11]
    reply_keyboard = [[t_amt,'/cancel']]
    update.message.reply_text('This is the total amount choose this or Enter whatever is been paid : '
        ,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return PAID_BY


def by(update, context):
    new_row.append(str(update.message.text))
    
    reply_keyboard = [['Cash','PhonePe'],['Google Pay', 'Net Banking']]
    update.message.reply_text(' Choose the method of payment : '
        ,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return END

def end(update, context):
    new_row.append(str(update.message.text))
    bal = int(new_row[11]) - int(new_row[12])
    new_row.append(str(bal))
    print(new_row)
    sheet.insert_row(new_row, 2)
    header = ['Date','Rent','Last Unit','Current unit','Total unit','Electricity bill',
              'Maid','Dustbin','WiFi','Additional Amt','Last Month Balance','Total Amount',
              'Total Paid', 'Paid By','Balance']
    
    tet=[]
    for x in range(len(new_row)):
        data = '*{0}* : {1}'.format(header[x],new_row[x])
        tet.append(data)

    s="\n"
    print(s.join(tet))
    result=s.join(tet)
    context.bot.send_message(chat_id=update.effective_chat.id,text=s.join(tet))
    context.bot.send_message(chat_id=update.effective_chat.id, text="These are the Entries updates in this [Google Sheet](https://drive.google.com/open?id=14yCcMjWZajFBKJlwsgufbRGY99QwQKH4emDNywKeoxU)",
                             parse_mode=telegram.ParseMode.MARKDOWN)
    
    return ConversationHandler.END
    

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater("634661342:AAEnmZa-BC5MljutbdAjRAlocikd0wTE0RA", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', choose)],

        states={
            SELECT : [MessageHandler(Filters.regex('^(Room-1|Room-2)$'), select),
                      CommandHandler('cancel', cancel)],
            
            RENT: [MessageHandler(Filters.text, rent),
                   CommandHandler('cancel', cancel)],

            CURRENT_UNIT: [MessageHandler(Filters.text, current)],

            MAID: [MessageHandler(Filters.text, maid),
                   CommandHandler('cancel', cancel)],

            DUSTBIN: [MessageHandler(Filters.text, dustbin),
                      CommandHandler('cancel', cancel)],

            WIFI: [MessageHandler(Filters.text, wifi),
                   CommandHandler('cancel', cancel)],

            ADD: [MessageHandler(Filters.text, add),
                  CommandHandler('cancel', cancel)],

            SHOW: [MessageHandler(Filters.text, show)],

            T_PAID: [MessageHandler(Filters.text, t_paid)],

            PAID_BY: [MessageHandler(Filters.text, by)],

            END: [MessageHandler(Filters.text, end)],

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    ##echo_handler = MessageHandler(Filters.text, echo)
    #dp.add_handler(echo_handler)    

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
    
