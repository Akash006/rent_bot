#!/usr/bin/env python

import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
import datetime
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('cread_py.json', scope)
client = gspread.authorize(creds)
sheet = ""
row = []
new_row = []
dat = datetime.date.today()
new_row.append(str(dat))

logger = logging.getLogger(__name__)

SELECT, RENT, LAST_UNIT, CURRENT_UNIT, MAID, DUSTBIN, WIFI, ADD, SHOW, T_PAID, PAID_BY, END = range(12)
        

def choose(update, context):
    reply_keyboard = [['Room-1', 'Room-2']]

    update.message.reply_text(
        'Hi! I will collect on your behalf. I will hold a conversation with you. '
        'Choose the room for which you want to collect.\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return SELECT

def select(update, context):
    room = str(update.message.text)
    print(room)
    if(room == 'Room-1'):
        sheet = client.open('test_sp').sheet1
        row = sheet.row_values(2)
        print(row)
    elif(room == 'Room-2'):
        sheet = client.open('test_sp').sheet2
        row = sheet.row_values(2)
    else:
        update.message.reply_text(' Choose the method of payment : ')
        
    return RENT

def rent(update, context):
    print('Entering into rent')
    prev_rent = str(row[1])
    reply_keyboard = [[prev_rent]]
    update.message.reply_text('Your previous rent is \n Press the button or type new amount'
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
    reply_keyboard = [[prev_maid]]
    update.message.reply_text('Choose previous maid amount or enter new :',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    
    return DUSTBIN


def dustbin(update, context):
    new_row.append(str(update.message.text))
    prev_dust = row[7]
    
    reply_keyboard = [[prev_dust]]
    update.message.reply_text('Choose previous Dustbin amount or enter new : '
        ,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return WIFI

def wifi(update, context):
    new_row.append(str(update.message.text))
    prev_wifi = row[8]
    
    reply_keyboard = [[prev_wifi]]
    update.message.reply_text('Choose previous WIFI amount or enter new : '
        ,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ADD


def add(update, context):
    new_row.append(str(update.message.text))
    print(new_row)
    reply_keyboard = [['0']]
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
    update.message.reply_text('{0} : {1}\n{2} : {3}\n\
{4} :\t{5}\n{6} :\t{7}\n\
{8} :\t{9}\n{10} :\t{11}\n\
{12} :\t{13}\n{14} :\t{15}\n\
{16} :\t{17}\n{18} :\t{19}\n\
{20} :\t{21}\n{22} :\t{23}\n'.format(header[0],new_row[0],header[1],new_row[1],header[2],new_row[2],
                                                                     header[3],new_row[3],header[4],new_row[4],header[5],new_row[5],
                                                                     header[6],new_row[6],header[7],new_row[7],header[8],new_row[8],
                                                                     header[9],new_row[9],header[10],new_row[10],header[11],new_row[11]),
                                  reply_markup=ReplyKeyboardRemove())

    reply_keyboard = [['Continue']]
    update.message.reply_text('Press Continue to Go Ahead',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return T_PAID

def t_paid(update, context):
    t_amt = new_row[11]
    reply_keyboard = [[t_amt]]
    update.message.reply_text('This is the total amount choose this or Enter whatever is been paid : '
        ,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return PAID_BY


def by(update, context):
    new_row.append(str(update.message.text))
    
    reply_keyboard = [['Cash','PhonePe','Google Pay', 'Net Banking']]
    update.message.reply_text(' Choose the method of payment : '
        ,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return END

def end(update, context):
    new_row.append(str(update.message.text))
    bal = int(new_row[11]) - int(new_row[12])
    new_row.append(str(bal))
    
    sheet.insert_row(new_row, 2)
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
            SELECT : [MessageHandler(Filters.regex('^(Room-1|Room-2)$'), select)],
            
            RENT: [MessageHandler(Filters.text, rent)],

            CURRENT_UNIT: [MessageHandler(Filters.text, current)],

            MAID: [MessageHandler(Filters.text, maid)],

            DUSTBIN: [MessageHandler(Filters.text, dustbin)],

            WIFI: [MessageHandler(Filters.text, wifi)],

            ADD: [MessageHandler(Filters.text, add)],

            SHOW: [MessageHandler(Filters.text, show)],

            T_PAID: [MessageHandler(Filters.text, t_paid)],

            PAID_BY: [MessageHandler(Filters.text, by)],

            END: [MessageHandler(Filters.text, end)],

        },

        fallbacks=[CommandHandler('cancel', cancel)]
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
    
