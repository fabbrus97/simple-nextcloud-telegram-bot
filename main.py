from pyrogram import Client, filters, enums
import sys
import json
import random
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.handlers import MessageHandler
import os
from datetime import datetime

def configure_bot():
    try:
        with open("config.json") as file:
            parsed_file = json.loads(file.read())
            global configs
            configs = parsed_file
            
            configs["user_authenticated"] = (configs.get("ADMINS") != None)
            if configs["user_authenticated"] == False:
                configs["ADMINS"] = []

            if configs["local_path"][-1] != "/":
                configs["local_path"] = configs["local_path"] + "/"
            if configs["URL"][-1] != "/":
                configs["URL"] = configs["URL"] + "/"
            if configs["remote_path"][-1] != "/":
                configs["remote_path"] = configs["remote_path"] + "/"

            file.close()
    except Exception as e:
        print(e)
        sys.exit(1)

############# global variables ##############

auth_number = None
configs = {}
configure_bot()
app = Client("my_bot", api_id=configs["api_id"], api_hash=configs["api_hash"], bot_token=configs["TOKEN"])

#############################################

@app.on_callback_query()
async def save_media(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    if ([chat_id, user_id]) not in configs["ADMINS"]:
            print("Unauthorized access denied for {}.".format(user_id))

            return
    
    await app.edit_message_text(chat_id, callback_query.message.id, "Saving...")

    try:        
        name = datetime.isoformat(datetime.now())

        local_path = configs["local_path"]
        file_name = os.path.join(local_path, name)
        await callback_query.message.reply_to_message.download(
            file_name=file_name
        )
        user = configs["user"]
        password = configs["password"]
        URL = configs["URL"]
        remote_path = configs["remote_path"]
        cmd = f'curl -k -u {user}:{password} -T "{os.path.join(local_path, name)}" "https://{URL}remote.php/dav/files/{user}/{remote_path}{name}"'
        os.system(cmd)
        os.remove(f"{local_path}{name}")
        # Notify the user:
        await app.edit_message_text(chat_id, callback_query.message.id, "Saved")

    except Exception as e:
        print(e)
        await app.edit_message_text(chat_id, callback_query.message.id, "Error :-(")

@app.on_message(filters.command(commands="start", prefixes="/"))
async def startgroup(client, message):
    if not configs["user_authenticated"]:
        print("User not authenticated, cannot start bot in this group")
        return
    try:
        chat_id = message.chat.id
        async for admin in app.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            admin = admin.user.id
            if ((chat_id, admin)) not in configs["ADMINS"]:
                configs["ADMINS"].append((chat_id, admin))
                save_config()
        print(f'New user added, now the list is:\n{configs["ADMINS"]}')
    except Exception as e:
        print(e)


# @app.on_message(filters.chat(["me"]))
@app.on_message()
async def handle(client, message: Message):
    if not configs["user_authenticated"]: 
        code = ""
        try: 
            code = int(message.text)
        except:
            pass
        global auth_number
        if code == auth_number:
            await message.reply("You are authenticated!")
            configs["user_authenticated"] = True
            chat_id = message.chat.id
            user_id = message.from_user.id
            configs["ADMINS"].append([chat_id, user_id])
            save_config()
    else:
        if message.photo or message.video or message.document:
            ButtonList = [InlineKeyboardButton("Confirm", callback_data="0")]
            reply_markup = InlineKeyboardMarkup([ButtonList])
            await message.reply(text="Save media?", quote=True, reply_markup=reply_markup)


def save_config():
    with open("config.json", "r+") as config:
        parsed_config = json.loads(config.read())
        parsed_config["ADMINS"] = configs["ADMINS"]
        config.seek(0)
        config.write(json.dumps(parsed_config))
        config.close()

# app.run()
if __name__ == "__main__":
    if not configs["user_authenticated"]:
        auth_number = random.randint(1000000, 9999999)
        print("Start the bot and send this number: ", auth_number)
    else:
        print("Bot started!")
        # app.add_handler(MessageHandler(startgroup))     
    app.run()

