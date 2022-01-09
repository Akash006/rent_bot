#!/usr/bin/env python

import time
import os
import logging
import pprint
import datetime
import telegram
import sys
from sheets import Connection
from threading import Thread
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

SELECT, LAST_UNIT, CURRENT_UNIT, MAID, DUSTBIN, WIFI, ADD, SHOW, T_PAID, PAID_BY, END = range(11)
L2, L1, L1_2, EXTRA, ADDITIONAL, SHOW_MILK, DEPOSIT, SUBMIT = range(8)

def choose(update, context):
    reply_keyboard = [['Room1', 'Room2'],['/cancel']]
    update.message.reply_text(
        'Hi! I will collect the rent from your behalf.\n\nChoose the Room .\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    log.info("Bot started...")
    return SELECT

def select(update, context):
    global new_row
    new_row = []
    dat = datetime.date.today()
    new_row.append(str(dat.strftime("%d-%b-%y %a")))
    room = update.message.text
    log.info(f"{room} is choosen.")
    prev_data(room)
    prev_rent = str(last_row_data[1])
    reply_keyboard = [[prev_rent],['/cancel']]
    update.message.reply_text('Enter the Rent Amount : {}'.format(prev_rent)
        ,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return CURRENT_UNIT

def prev_data(room):
    global last_row, last_row_data, con
    con = Connection("Rent Sheet", room)
    data = con.get_last_row()
    last_row_data = data[0]
    last_row = data[1]
    log.info("Previous data is collected.")

def current(update, context):
    new_row.append(str(update.message.text))
    new_row.append(str(last_row_data[3]))
    log.info("Collecting current unit")
    update.message.reply_text('Last month unit : {0}\n\nEnter the current Unit :'.format(str(last_row_data[3])))
    return MAID

def maid(update, context):
    new_row.append(str(update.message.text))
    total = int(new_row[3])-int(new_row[2])
    new_row.append(str(total))
    total_bill = total * 9
    new_row.append(str(total_bill))
    prev_maid = last_row_data[6]
    reply_keyboard = [[prev_maid],['/cancel']]
    update.message.reply_text('Enter the Maid charges :',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    
    return DUSTBIN

def dustbin(update, context):
    new_row.append(str(update.message.text))
    prev_dust = last_row_data[7]
    
    reply_keyboard = [[prev_dust],['/cancel']]
    update.message.reply_text('Enter the Dustbin charges : '
        ,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return WIFI

def wifi(update, context):
    new_row.append(str(update.message.text))
    prev_wifi = last_row_data[8]
    
    reply_keyboard = [[prev_wifi],['/cancel']]
    update.message.reply_text('Enter the WiFi charges : '
        ,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ADD

def add(update, context):
    new_row.append(str(update.message.text))
    reply_keyboard = [['0','/cancel']]
    update.message.reply_text('Enter any Additional amount : '
        ,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    
    return SHOW

def show(update, context):
    new_row.append(str(update.message.text))
    new_row.append(last_row_data[14])
    total_amt = int(new_row[1]) + int(new_row[5]) + int(new_row[6]) + int(new_row[7]) + int(new_row[8]) + int(new_row[9]) + int(new_row[10])
    new_row.append(str(total_amt))
    
    header = ['Date','Rent','Last Unit','Current unit','Total unit','Electricity bill',
              'Maid','Dustbin','WiFi','Additional Amt','Last Month Balance','Total Amount',
              'Total Paid', 'Paid By','Balance']

    ss = []
    for x in range(len(new_row)):
        data = '*{0}* : {1}'.format(header[x],new_row[x])
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
    reply_keyboard = [[t_amt],['/cancel']]
    update.message.reply_text('Total amount paid : '
        ,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return PAID_BY

def by(update, context):
    new_row.append(str(update.message.text))
    
    reply_keyboard = [['Cash','PhonePe'],['Google Pay', 'Net Banking']]
    update.message.reply_text(' Choose the payment method : '
        ,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return END

def end(update, context):
    new_row.append(str(update.message.text))
    bal = int(new_row[11]) - int(new_row[12])
    new_row.append(str(bal))
    print(new_row)
    #sheet.insert_row(new_row, 2)
    header = ['Date','Rent','Last Unit','Current unit','Total unit','Electricity bill',
              'Maid','Dustbin','WiFi','Additional Amt','Last Month Balance','Total Amount',
              'Total Paid', 'Paid By','Balance']
    
    tet=[]
    for x in range(len(new_row)):
        data = '*{0}* : {1}'.format(header[x],new_row[x])
        tet.append(data)

    s="\n"
    print(s.join(tet))
    context.bot.send_message(chat_id=update.effective_chat.id,text=s.join(tet), parse_mode=telegram.ParseMode.MARKDOWN)
    context.bot.send_message(chat_id=update.effective_chat.id,text="Data added to sheet successfully !!")
    add_row(new_row)
    return ConversationHandler.END

def add_row(item):
    con.add_data(last_row + 1, item)
    log.info("Data added to spreadsheet.")

def cancel(update, context):
    user = update.message.from_user
    log.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def stop_and_restart():
        # Gracefully stop the Updater and replace the current process with a new one
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)
    
def error(update, context):
    """Log Errors caused by Updates."""
    log.warning('Update "%s" caused error "%s"', update, context.error)
    update.message.reply_text('Restarting bot server....')
    Thread(target=stop_and_restart).start()

def sheet(update, context):

    keyboard = [
        [
            InlineKeyboardButton("Milk Sheet", callback_data='milk'),
            InlineKeyboardButton("Rent Sheet", callback_data='rent'),
        ]
    ]

    update.message.reply_text('Please choose: ', reply_markup=InlineKeyboardMarkup(keyboard))

    # get = update.message.text
    # args = get.split(" ")[1]
    # if args.lower() == 'rent':
    #     context.bot.send_message(chat_id=update.effective_chat.id, text="[Rent Sheet]\n\nhttps://docs.google.com/spreadsheets/d/1mcsqntfLwI_vlRrJHJJj9Tfbf7gfH9BzoicR7dYr97I/edit?usp=sharing")
    # elif args.lower() == 'milk':
    #     context.bot.send_message(chat_id=update.effective_chat.id, text="[Milk Sheet]\n\nhttps://docs.google.com/spreadsheets/d/1mIICv0ZWB6hM2hbNcC3nEE9bzDlGgCPmP33ubPP65Mg/edit?usp=sharing")
    # else:
    #     context.bot.send_message(chat_id=update.effective_chat.id, text="No arguments received.")

def button(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'milk':
        query.edit_message_text(text="[Milk Sheet]\n\nhttps://docs.google.com/spreadsheets/d/1mIICv0ZWB6hM2hbNcC3nEE9bzDlGgCPmP33ubPP65Mg/edit?usp=sharing")
    elif query.data == 'rent':
        query.edit_message_text(text="[Rent Sheet]\n\nhttps://docs.google.com/spreadsheets/d/1mcsqntfLwI_vlRrJHJJj9Tfbf7gfH9BzoicR7dYr97I/edit?usp=sharing")

def milk_sheet(worksheet):
    global msheet, msheet_last_row, con
    con = Connection("Milk", worksheet)
    data = con.get_last_row()
    msheet = data[0]
    msheet_last_row = data[1]
    log.info("Previous data is collected.")

def milk(update, context):
    dat = datetime.date.today()
    milk_sheet(str(dat.strftime("%b")))
    global milk_data
    milk_data = []
    milk_data.append(str(dat.strftime("%d-%b-%y %a")))
    milk_data.append("0")
    reply_keyboard = [['0', '1', '2'],['/cancel']]
    update.message.reply_text(
        'Hi! Good morning...mom\n\nEnter the 2L packets :\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    log.info("Milk Bot started...")
    return L2

def L2(update, context):
    liters2 = int(update.message.text)
    milk_data.append(liters2)
    reply_keyboard = [['0', '1', '2', '3'],['/cancel']]
    update.message.reply_text(
        f'Enter the 1L packets :\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return L1

def L1(update, context):
    liters1 = int(update.message.text)
    milk_data.append(liters1)
    reply_keyboard = [['0', '1', '2','3', '4', '5'],['/cancel']]
    update.message.reply_text(
        f'Enter the 1/2 L packets :\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return L1_2

def L1_2(update, context):
    liters1_2 = int(update.message.text)
    milk_data.append(liters1_2)
    reply_keyboard = [['0'],['/cancel']]
    update.message.reply_text(
        f'Enter any extra item price :\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return EXTRA

def extra(update, context):
    extra = int(update.message.text)
    milk_data.append(extra)
    reply_keyboard = [['Deposit', 'Submit'],['/cancel']]
    update.message.reply_text(
        f'Want to Deposit money ?\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    
    return ADDITIONAL

def Additional(update, context):
    total_milk = (int(milk_data[2])*112) + (int(milk_data[3]*55)) + (int(milk_data[4]*28)) + int(milk_data[5])
    milk_data.append(total_milk)
    rec = str(update.message.text)
    if rec == 'Submit':
        bal = int(msheet[7]) - total_milk
        milk_data.append(bal)
        reply_keyboard = [['Continue'],['/cancel']]
        update.message.reply_text(
            f'Press continue to Go Ahead.',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return SHOW_MILK
    else:
        reply_keyboard = [['500','1000'],['/cancel']]
        update.message.reply_text(
            f'Enter the amount you want to deposit : ',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return DEPOSIT

def deposit(update, context):
    depo = int(update.message.text)
    milk_data[1] = depo
    bal = int(msheet[7]) + int(milk_data[1]) - int(milk_data[6])
    milk_data.append(bal)
    reply_keyboard = [['Continue'],['/cancel']]
    update.message.reply_text(
        f'Press continue to Go Ahead.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return SHOW_MILK

def show_milk(update, context):
    header = ['Date','Deposit','2 Liter', '1 Liter', '1/2 Liter', 'Extra', 'Total Amount', 'Baclance']

    ss = []
    for x in range(len(milk_data)):
        data = '*{0}* : {1}'.format(header[x],milk_data[x])
        ss.append(data)

    s="\n"
    context.bot.send_message(chat_id=update.effective_chat.id, 
                 text=s.join(ss), 
                 parse_mode=telegram.ParseMode.MARKDOWN)
    
    reply_keyboard = [['Continue','/cancel']]
    update.message.reply_text('Press continue to Go Ahead.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return SUBMIT

def submit(update, context):
    con.add_data(msheet_last_row + 1, milk_data)
    update.message.reply_text('Data is added successfully.')
    log.info("Data added to spreadsheet.")
    return ConversationHandler.END

def main():
    global updater
    updater = Updater("1324554598:AAGmEBRZtgqM0qo4mwAOy_nLx1KmiCZ8jMk", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    milk_handler = ConversationHandler(
        entry_points=[CommandHandler('milk', milk)],

        states={
            L2 : [CommandHandler('cancel', cancel),
                    MessageHandler(Filters.text, L2)],

            L1 : [CommandHandler('cancel', cancel),
                    MessageHandler(Filters.text, L1)],

            L1_2 : [CommandHandler('cancel', cancel),
                    MessageHandler(Filters.text, L1_2)],

            EXTRA : [CommandHandler('cancel', cancel),
                    MessageHandler(Filters.text, extra)],

            ADDITIONAL : [CommandHandler('cancel', cancel),
                    MessageHandler(Filters.text, Additional)],

            SHOW_MILK : [CommandHandler('cancel', cancel),
                    MessageHandler(Filters.text, show_milk)],

            DEPOSIT : [CommandHandler('cancel', cancel),
                    MessageHandler(Filters.text, deposit)],

            SUBMIT : [CommandHandler('cancel', cancel),
                    MessageHandler(Filters.text, submit)],

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('rent', choose)],

        states={
            SELECT : [CommandHandler('cancel', cancel),
                        MessageHandler(Filters.regex('^(Room1|Room2)$'), select)],

            CURRENT_UNIT: [CommandHandler('cancel', cancel),
                            MessageHandler(Filters.text, current)],

            MAID: [CommandHandler('cancel', cancel),
                    MessageHandler(Filters.text, maid)],

            DUSTBIN: [CommandHandler('cancel', cancel),
                        MessageHandler(Filters.text, dustbin)],

            WIFI: [CommandHandler('cancel', cancel),
                    MessageHandler(Filters.text, wifi)],

            ADD: [CommandHandler('cancel', cancel),
                    MessageHandler(Filters.text, add)],

            SHOW: [CommandHandler('cancel', cancel),
                    MessageHandler(Filters.text, show)],

            T_PAID: [CommandHandler('cancel', cancel),
                        MessageHandler(Filters.text, t_paid)],

            PAID_BY: [CommandHandler('cancel', cancel),
                        MessageHandler(Filters.text, by)],

            END: [CommandHandler('cancel', cancel),
                    MessageHandler(Filters.text, end)]

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )  

    dp.add_handler(conv_handler)
    dp.add_handler(milk_handler)
    dp.add_handler(CommandHandler('sheet', sheet))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler('restart', error))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':

    logging.basicConfig(filename="/home/pi/scripts/rent_bot/rentBot.log", level=logging.INFO, format="[%(asctime)-8s] %(levelname)-8s : %(message)s")
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)-8s] %(levelname)-8s : %(message)s")
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
    global log
    log = logging.getLogger()
    main()
