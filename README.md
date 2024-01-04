# Bitcoin-Bot
A discord bot that allows users to buy and sell bitcoin in a virtual game to make profit.

# How it works

1. Edit config.json and put in your infomation (bot token, channel id and change anything you want to change)

2. Run the bot in your terminal `python bitcoin.py` or `python3 bitcoin.py` for linux users

3. After sucessfully logging in the bot should automatically start posting the new bitcoin price in your designated channel_id.

4. Now that there is a constantly changing bitcoin price. Users can use the commands `buy_bitcoin <amount>` and `sell_bitcoin <amount>`.  to buy and sell bitcoin when they want. The aim of the game is for users to buy bitcoin when its at a low price and sell their bitcoin when its at a higher price. Changing the update_interval will make the bitcoin price change more often or less often.

# Installation

1. Simply run `bitcoin.py` (it should auto-install required modules). Or run `pip install -r requirements.txt` in your terminal. THEN run bitcoin.py

2. Without editing config.json you will probably run into an error saying 'improper token passed' or 'cannot find channel id'. You must enter your bot token and you update channel ID for the bot to run.
