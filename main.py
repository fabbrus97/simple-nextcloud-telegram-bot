import json
import random
import subprocess
import sys
import time

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler, CommandHandler
import logging
import os
from telegram.ext import MessageHandler, Filters
from functools import wraps


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        if update.message:
            chat_id = update.message.chat.id
        else:
            chat_id = update.callback_query.message.chat.id
        user_id = update.effective_user.id
        if (chat_id, user_id) not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(update, context, *args, **kwargs)
    return wrapped


@restricted
def media_sent(update, context):
    try:
        ButtonList = [InlineKeyboardButton("Confirm", callback_data=0)]
        reply_markup = InlineKeyboardMarkup([ButtonList])
        bot.send_message(chat_id=update.effective_chat.id, text="Save media?",
                         reply_markup=reply_markup, reply_to_message_id=update.message.message_id)
    except Exception as e:
        print(e)


@restricted
def save_media(update, context):
    bot.edit_message_text(text="Saving...", chat_id=update.callback_query.message.chat.id, message_id=update.callback_query.message.message_id)
    try:
        file_id = update.callback_query.message.reply_to_message.photo[-1]["file_id"]
    except:
        try:
            file_id = update.callback_query.message.reply_to_message.video["file_id"]
        except:
            try:
                file_id = update.callback_query.message.reply_to_message.document.file_id
            except:
                bot.edit_message_text(text="Error :-(", chat_id=update.callback_query.message.chat.id,
                                      message_id=update.callback_query.message.message_id)
                return
    try:
        print(f"Saving {file_id}")
        newFile = bot.get_file(file_id)
        name = newFile.file_path.split("/")[-1]
        newFile.download(custom_path=f"{local_path}{name}")
        cmd = f'curl -k -u {user}:{password} -T "{local_path}{name}" "https://{myURL}remote.php/dav/files/{user}/{remote_path}{name}"'
        os.system(cmd)
        os.remove(f"{local_path}{name}")
        # Notify the user:
        bot.edit_message_text(text="Saved", chat_id=update.callback_query.message.chat.id,
                              message_id=update.callback_query.message.message_id)

    except Exception as e:
        print(e)
        bot.edit_message_text(text="Error :-(", chat_id=update.callback_query.message.chat.id,
                              message_id=update.callback_query.message.message_id)


def check_code(update, context):
    try:
        global user_authenticated
        if user_authenticated:
            dispatcher.remove_handler(auth_handler)
            if update.message.text == "/start":
                start4groups(update, context)
            return
        code = int(update.message.text)
        if code == auth_number:
            update.message.reply_text("You are authenticated!")
            user_authenticated = True
            media_handler = MessageHandler(Filters.photo | Filters.video | Filters.document, media_sent)
            dispatcher.add_handler(media_handler)
            dispatcher.add_handler(CallbackQueryHandler(save_media))
            dispatcher.add_handler(CommandHandler("start", start4groups))
            # user who successfully performed authentication
            chat_id = update.message.chat.id
            LIST_OF_ADMINS.append((chat_id, update.effective_user.id))
    except Exception as e:
        print(e)


def start4groups(update, context):
    try:
        chat_id = update.message.chat.id
        for admin in bot.get_chat_administrators(chat_id):
            admin = admin.user.id
            if (chat_id, admin) not in LIST_OF_ADMINS:
                LIST_OF_ADMINS.append((chat_id, admin))
        print(f"New user added, now the list is:\n{LIST_OF_ADMINS}")
    except Exception as e:
        print(e)


def configure_bot():
    try:
        with open("config.json") as file:
            parsed_file = json.loads(file.read())
            global TOKEN
            TOKEN = parsed_file["TOKEN"]
            global remote_path
            remote_path = parsed_file["remote_path"]
            global user
            user = parsed_file["user"]
            global password
            password = parsed_file["password"]
            global local_path
            local_path = parsed_file["local_path"]
            global myURL
            myURL = parsed_file["URL"]

            if local_path[-1] != "/":
                local_path = local_path + "/"
            if myURL[-1] != "/":
                myURL = myURL + "/"
            if remote_path[-1] != "/":
                remote_path = remote_path + "/"

            file.close()
    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    TOKEN = ''
    myURL = ""
    remote_path = ""
    user = ""
    password = ""
    local_path = ""
    LIST_OF_ADMINS = []
    auth_number = 0
    user_authenticated = False
    try:
        configure_bot()

        updater = Updater(token=TOKEN, use_context=True)
        bot = Bot(token=TOKEN)
        dispatcher = updater.dispatcher

        auth_handler = MessageHandler(Filters.text, check_code)
        dispatcher.add_handler(auth_handler)
        updater.start_polling()

        if not user_authenticated:
            auth_number = random.randint(1000000, 9999999)
            print("Start the bot and send this number: ", auth_number)
    except Exception as e:
        print(e)
        sys.exit(1)

