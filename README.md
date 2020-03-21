#Simple Nextcloud Telegram Bot
This bot allows users to send media files shared on telegram to a owncloud server.

It downloads the chosen media on the computer, sends and then deletes it. 

###Quickstart
-1. Create the folder on your owncloud server where you want to receive the files (skip this step if you want to use an existing one)
0. Create the bot with Botfather on telegram
1. Configure the bot editing the file `config.json`
2. Launch `python3 main.py`

####Personal use
For personal use, you just need to send the authentication code generated in `main.py` to the bot; then it is possible to send files to the bot.

####Groups
You can add the bot to groups; after that, send the command `/start` on the telegram group. That's it!
 
**Note:** only group admins can send photos to the server.


  

