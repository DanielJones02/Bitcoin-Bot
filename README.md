# Bitcoin-Bot
A discord bot that allows users to buy and sell bitcoin in a virtual game to make profit.

# How it works

The aim of the game is to trade bitcoin. To put it in simple terms, buy bitcoin whem the price is low, amd sell when the price is high.

The chance of the price increasing is 2/3 (66%) chance of increasing with a value of 15-20%.

The chance of the price decreasing is a 1/3 (33%) chance of decreasing with a value of 20-21%.

The currency i put in the bot is British Pounds (£). You can change it by editing bitcoin.py

# Installation

1. Simply run `bitcoin.py` (it should auto-install required modules). Or run `pip install -r requirements.txt` in your terminal. THEN run bitcoin.py

2. Without editing config.json you will probably run into an error saying 'improper token passed' or 'cannot find channel id'. You must enter your bot token and you update channel ID for the bot to run.

3. Now let the bot run. Be aware. This is a very resource intensive bot, I didn't add any more commands or any more background tasks, because from my experience the code is very unstable and causes the bot to crash after some time.

# COMMAND LIST

PREFIX is $ by default

`bitcoin_price` - Shows the current bitcoin price

`bitcoin_bal` - Shows the user their current bitcoin balance

`bitcoin_buy <amount>` - Buy bitcoin

`bitcoin_sell <amount>` - Sell bitcoin

`bal` - Check your current balance

`baltop` - Check for the top 10 richest users

`give @user <amount>` - Give a user money (admin needed)

# Common Bugs

1. `json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)` - Just delete bitcoin_price_history.json

2. Random Crashes. I am well aware of this, I'm not sure if its limited CPU power of just the script bugging out. I'm trying to fix it.
