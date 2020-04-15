from youtube_dl import YoutubeDL
from telegram.ext.updater import Updater
from telegram.ext.commandhandler import CommandHandler
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.chataction import ChatAction
from time import sleep
from urllib import parse
import re
import os

updater = Updater("920296790:AAF0BZei36n2WNrIhMyWaF_hiDbjjhBCS8w",
                  use_context=True)


def download(update: Update, ctx: CallbackContext):
    FILE = None

    _ = re.findall(r"(?:/download )(.+)", update.message.text)
    if len(_) == 0:
        update.message.reply_text(
            text=
            "Rerun the command with payload such that '/download YOUTUBE_URL'")
        return

    ctx.bot.send_chat_action(chat_id=update.effective_chat.id,
                             action=ChatAction.RECORD_VIDEO)

    id: str = dict(parse.parse_qsl(parse.urlsplit(_[0]).query))["v"]

    try:
        FILE: str = [
            files for files in os.listdir(os.getcwd()) if files.find(id) != -1
        ][0]
    except IndexError:
        with YoutubeDL() as ytdl:
            ytdl.download(_)
            FILE: str = [
                files for files in os.listdir(os.getcwd())
                if files.find(id) != -1
            ][0]

    update.message.reply_video(
        video=open(os.path.join(os.getcwd(), FILE), "rb"))
    pass


updater.dispatcher.add_handler(CommandHandler("download", download))

if __name__ == "__main__":
    updater.start_polling()
    print("running")
