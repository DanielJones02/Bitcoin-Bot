

from discord.ext import commands
from colorama import Fore
from time import ctime

import matplotlib.pyplot as plt
import datetime
import asyncio
import discord
import random
import json
import time
import os
import io


t = f"{Fore.LIGHTYELLOW_EX}{ctime()}{Fore.RESET}"

# Global variables
bitcoin_price = 30000  # Initial Bitcoin price
bitcoin_price_history = []

user_balances = {}  # Holds users' balance
user_bitcoin_balances = {}  # Holds users' Bitcoin balance

# Load the configuration file
with open('config.json') as config_file:
    config = json.load(config_file)


TOKEN = config['bot_token']
bitcoin_price = config['bitcoin_starting_price']
update_channel = config['update_channel']
update_intervals = config['update_intervals']
bitcoin_price_history_file = config['bitcoin_old_prices']
DATA_FILE = config['user_balance_save_file']
BITCOIN_DATA_FILE = config['bitcoin_data_save_file']
PREFIX = config['BOT_PREFIX']


intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)


# Load user data
def load_data():
    global user_balances, user_bitcoin_balances
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            user_balances = json.load(file).get(DATA_FILE, {})
    if os.path.exists(BITCOIN_DATA_FILE):
        with open(BITCOIN_DATA_FILE, 'r') as file:
            user_bitcoin_balances = json.load(file).get(BITCOIN_DATA_FILE, {})


def load_bitcoin_data():
    global bitcoin_price, bitcoin_price_history

    # Load Bitcoin price history
    if os.path.exists(bitcoin_price_history_file):
        with open(bitcoin_price_history_file, 'r') as file:
            bitcoin_price_history = json.load(file)

    # If there's any history, set the latest price from it
    if bitcoin_price_history:
        # Set the current price to the last price in the history
        bitcoin_price = bitcoin_price_history[-1]
    else:
        pass  # bitcoin_price default value is already defined

def load_user_data():
    # Load user data from the file
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            user_balances = data.get('user_balances', {})
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        user_balances = {}

# Load data initially
load_bitcoin_data()


async def update_bitcoin_price():
    global bitcoin_price, bitcoin_price_history
    channel = bot.get_channel(update_channel)

    while True:
        try:
            print("Prices posting...")
            # Store the previous Bitcoin price
            old_price = bitcoin_price

            # Determine whether to increase or decrease the price
            increase_price = random.choice([True, True, False])

            if increase_price:
                # Increase the price by 500-600%
                change_percent = random.uniform(15, 20)
            else:
                # Decrease the price by 500-600%
                change_percent = random.uniform(-20, -21)

            new_price = round(max(20000, min(bitcoin_price * (1 + change_percent / 100), 60000)))
            bitcoin_price = new_price  # Update the global bitcoin_price
            bitcoin_price_history.append(new_price)

            # Save Bitcoin price history to file
            with open(bitcoin_price_history_file, 'w') as file:
                json.dump(bitcoin_price_history, file, indent=4)

            # Generate timestamps for plotting
            times = [datetime.datetime.now() - datetime.timedelta(seconds=i * update_intervals) for i in range(len(bitcoin_price_history))]

            # Generate the entire graph
            plt.figure()
            plt.plot(times, bitcoin_price_history, '-o')
            plt.title("Bitcoin Price History")
            plt.xlabel("Time")
            plt.ylabel("Price (pounds)")
            plt.xticks(rotation=45)

            # Save plot to a BytesIO object
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()

            price_change = new_price - old_price
            change_direction = "increased" if price_change > 0 else "decreased"
            message = f"Bitcoin has {change_direction} by {abs(price_change)} pounds. The new Bitcoin value is {new_price} pounds!"

            # Send message to the specific channel
            await channel.send(message, file=discord.File(buf, filename='bitcoin_price.png'))

            # Wait for 30 seconds before next update
            await asyncio.sleep(update_intervals)

        except Exception as e:
            print(f"An error occurred in update_bitcoin_price: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="Invalid Command",
            description="That is not a valid command. Use `$help` to list all available commands!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        # Handle other types of errors (optional)
        pass


@bot.event
async def on_ready():
    print(Fore.LIGHTGREEN_EX, f"{t}{Fore.LIGHTGREEN_EX} | Ready and online - {bot.user.display_name}\n", Fore.RESET)
    await bot.change_presence(activity=discord.Game(f'Bitcoin | {PREFIX}help'))

    try:
        guild_count = 0

        for guild in bot.guilds:
            print(Fore.RED, f"- {guild.id} (name: {guild.name})\n", Fore.RESET)

            guild_count = guild_count + 1

        print(Fore.GREEN, f"{t}{Fore.GREEN} | {bot.user.display_name} is in " + str(guild_count) + " guilds.\n", Fore.RESET)

    except Exception as e:
        print(e)

    await update_bitcoin_price()


def message_log(ctx, command, extra = None):
    log_text = f"{t}{Fore.CYAN} | ${command} {extra} | {ctx.channel} | Executed by {ctx.author}{Fore.RESET}"
    print(log_text)


def save_user_data():
    with open(DATA_FILE, 'w') as f:
        json.dump({'user_balances': user_balances}, f)


def get_user_balance(user_id):
    return user_balances.get(str(user_id), 0)


def update_user_balance(user_id, amount):
    user_balances[str(user_id)] = get_user_balance(user_id) + amount
    save_user_data()


# Function to load user's Bitcoin balance
def load_user_bitcoin(user_id):
    # Replace 'BITCOIN_DATA_FILE' with the correct file path
    bitcoin_data_file = 'bitcoin_data.json'
    if not os.path.exists(bitcoin_data_file):
        with open(bitcoin_data_file, 'w') as file:
            json.dump({}, file)

    try:
        with open(bitcoin_data_file, 'r') as file:
            data = json.load(file)
            user_bitcoin_balances = data.get('user_bitcoin_balances', {})
            return user_bitcoin_balances.get(str(user_id), 0)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return 0


def get_bitcoin_price():
    try:
        with open(bitcoin_price_history_file, 'r') as file:
            bitcoin_price_history = json.load(file)
            if bitcoin_price_history:
                # Assuming each entry is a dictionary with a 'price' key
                latest_entry = bitcoin_price_history[-1]
                latest_price = latest_entry.get('price')
                return latest_price
            else:
                return None
    except FileNotFoundError:
        print("Bitcoin price history file not found.")
        return None
    except json.decoder.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return None



# Function to get user's Bitcoin balance
def get_user_bitcoin(user_id):
    # Load Bitcoin balance data from the file
    bitcoin_data_file = 'bitcoin_data.json'
    try:
        with open(bitcoin_data_file, 'r') as file:
            data = json.load(file)
            user_bitcoin_balances = data.get('user_bitcoin_balances', {})
            return user_bitcoin_balances.get(str(user_id), 0)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return 0


# Existing function to update user's Bitcoin balance
def update_user_bitcoin(user_id, amount):
    user_bitcoin_balances[str(user_id)] = amount
    save_user_bitcoin_data()


# Existing function to save user Bitcoin balance data
def save_user_bitcoin_data():
    with open(BITCOIN_DATA_FILE, 'w') as file:
        json.dump({'user_bitcoin_balances': user_bitcoin_balances}, file)


def setup_trading(bot):

    @bot.command(name='bitcoin_price')
    async def bitcoin_price(ctx):
        try:
            # Load the latest Bitcoin price
            with open(bitcoin_price_history_file, 'r') as file:
                bitcoin_price_history = json.load(file)
                if bitcoin_price_history:
                    # Assuming the latest price is at the end of the list
                    latest_price = bitcoin_price_history[-1]
                    embed = discord.Embed(title="Bitcoin Price", description=f"The latest Bitcoin price is {latest_price} pounds.", color=discord.Colour.green())
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="Bitcoin Price", description="Bitcoin price history is empty.", color=discord.Colour.red())
                    await ctx.send(embed=embed)
        except FileNotFoundError:
            embed = discord.Embed(title="Bitcoin Price", description="Bitcoin price history file not found.", color=discord.Colour.red())
            await ctx.send(embed=embed)
        except json.decoder.JSONDecodeError as e:
            embed = discord.Embed(title="Bitcoin Price", description=f"JSON Decode Error: {e}", color=discord.Colour.red())
            await ctx.send(embed=embed)


    @bot.command(name='buy_bitcoin')
    async def buy_bitcoin(ctx, amount: float):
        if amount <= 0:
            embed = discord.Embed(
                title="Error",
                description="Please enter a valid amount of Bitcoin to buy.",
                color=discord.Colour.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            # Load the latest Bitcoin price
            with open(bitcoin_price_history_file, 'r') as file:
                bitcoin_price_history = json.load(file)
                if not bitcoin_price_history:
                    embed = discord.Embed(
                        title="Error",
                        description="Unable to fetch the latest Bitcoin price.",
                        color=discord.Colour.red()
                    )
                    await ctx.send(embed=embed)
                    return
                latest_price = bitcoin_price_history[-1]

            # Calculate the total cost
            total_cost = latest_price * amount

            # Get the user's balance
            user_id = str(ctx.author.id)
            user_balance = get_user_balance(user_id)

            # Check if the user has enough balance
            if user_balance < total_cost:
                embed = discord.Embed(
                    title="Error",
                    description=f"You do not have enough balance to buy {amount} Bitcoin.",
                    color=discord.Colour.red()
                )
                await ctx.send(embed=embed)
            else:
                # Update the user's balance
                update_user_balance(user_id, -total_cost)

                # Get and update user's Bitcoin balance
                user_bitcoin_balance = get_user_bitcoin(user_id)
                update_user_bitcoin(user_id, user_bitcoin_balance + amount)

                embed = discord.Embed(
                    title="Bitcoin Purchase",
                    description=f"You have successfully purchased {amount} Bitcoin for {total_cost}.",
                    color=discord.Colour.green()
                )
                await ctx.send(embed=embed)

        except FileNotFoundError:
            embed = discord.Embed(
                title="Error",
                description="Bitcoin data file not found.",
                color=discord.Colour.red()
            )
            await ctx.send(embed=embed)
        except json.decoder.JSONDecodeError as e:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {e}",
                color=discord.Colour.red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {e}",
                color=discord.Colour.red()
            )
            await ctx.send(embed=embed)


    @bot.command(name='sell_bitcoin', help='Sell your Bitcoin')
    async def sell_bitcoin(ctx, amount_to_sell: float):
        if amount_to_sell <= 0:
            embed = discord.Embed(
                title="Error",
                description="Please enter a valid amount of Bitcoin to sell.",
                color=discord.Colour.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            # Load the latest Bitcoin price
            with open(bitcoin_price_history_file, 'r') as file:
                bitcoin_price_history = json.load(file)
                if not bitcoin_price_history:
                    embed = discord.Embed(
                        title="Error",
                        description="Unable to fetch the latest Bitcoin price.",
                        color=discord.Colour.red()
                    )
                    await ctx.send(embed=embed)
                    return
                current_bitcoin_price = bitcoin_price_history[-1]

            # Get the user's Bitcoin balance
            user_id = str(ctx.author.id)
            user_bitcoin_balance = get_user_bitcoin(user_id)

            # Check if the user has enough Bitcoin to sell
            if user_bitcoin_balance < amount_to_sell:
                embed = discord.Embed(
                    title="Error",
                    description=f"You do not have enough Bitcoin to sell {amount_to_sell}.",
                    color=discord.Colour.red()
                )
                await ctx.send(embed=embed)
            else:
                # Calculate the money to add to the user's balance
                money_to_add = amount_to_sell * current_bitcoin_price

                # Update user's bitcoin and money balance
                update_user_bitcoin(user_id, user_bitcoin_balance - amount_to_sell)
                update_user_balance(user_id, money_to_add)
                save_user_data()

                embed = discord.Embed(
                    title="Bitcoin Sold",
                    description=f"You've successfully sold {amount_to_sell} Bitcoin for {money_to_add} pounds.",
                    color=discord.Colour.green()
                )
                await ctx.send(embed=embed)

        except FileNotFoundError:
            embed = discord.Embed(
                title="Error",
                description="Bitcoin data file not found.",
                color=discord.Colour.red()
            )
            await ctx.send(embed=embed)
        except json.decoder.JSONDecodeError as e:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {e}",
                color=discord.Colour.red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {e}",
                color=discord.Colour.red()
            )
            await ctx.send(embed=embed)


    @bot.command(name='bitcoin_bal', help='Check your Bitcoin balance and its current worth')
    async def bitcoin_bal(ctx):
        user_id = str(ctx.author.id)

        try:
            # Load the latest Bitcoin price
            with open(bitcoin_price_history_file, 'r') as file:
                bitcoin_price_history = json.load(file)
                if not bitcoin_price_history:
                    embed = discord.Embed(
                        title="Error",
                        description="Unable to fetch the latest Bitcoin price.",
                        color=discord.Colour.red()
                    )
                    await ctx.send(embed=embed)
                    return
                current_bitcoin_price = bitcoin_price_history[-1]

            # Get the user's Bitcoin balance
            user_bitcoin_balance = get_user_bitcoin(user_id)
            current_value = user_bitcoin_balance * current_bitcoin_price

            embed = discord.Embed(
                title="Bitcoin Balance",
                description=f"You have {user_bitcoin_balance} BTC.\n"
                            f"Current value: {current_value} pounds.",
                color=discord.Colour.blue()
            )
            await ctx.send(embed=embed)

        except FileNotFoundError:
            embed = discord.Embed(
                title="Error",
                description="Bitcoin data file not found.",
                color=discord.Colour.red()
            )
            await ctx.send(embed=embed)
        except json.decoder.JSONDecodeError as e:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {e}",
                color=discord.Colour.red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {e}",
                color=discord.Colour.red()
            )
            await ctx.send(embed=embed)
    
    @bot.command(name='help')
    async def custom_help(ctx):
        embed = discord.Embed(
            title="Help - My Bot Commands",
            description="List of available commands:\n\nMy prefix is `$`",
            color=discord.Color.blue()
        )

        # Customize these lines with your bot's commands and descriptions
        embed.add_field(name="help", value="Shows this message.", inline=True)
        embed.add_field(name="buy_bitcoin <amount>", value="Buy bitcoin", inline=False)
        embed.add_field(name="sell_bitcoin <amount>", value="Sell bitcoin", inline=False)
        embed.add_field(name="bitcoin_price", value="Shows the current bitcoin price", inline=False)
        embed.add_field(name="bitcoin_bal", value="Check your bitcoin balance", inline=False)
        embed.add_field(name="ba;", value="Shows your balance", inline=False)
        embed.add_field(name="baltop", value="Shows the top 10 richest players", inline=False)
        #embed.add_field(name="", value="", inline=False)

        await ctx.send(embed=embed)
        message_log(ctx, 'help')
    

    @bot.command(name='give')
    @commands.has_permissions(administrator=True)
    async def give(ctx, target: commands.MemberConverter, amount: int):
        update_user_balance(target.id, amount)
        embed = discord.Embed(
            title="Coins Given!",
            description=f"Admin {ctx.author.display_name} has given {amount} coins to {target.display_name}.",
            color=discord.Color.orange()
        )

        # Send the embed
        await ctx.send(embed=embed)

        message_log(ctx, "give", f"{target} | {amount}")
    

    @bot.command(name='baltop', aliases=['topbalance', 'richest', 'topbal', 'balancetop'])
    async def baltop(ctx):
        # Check if the file exists and is not empty
        if not os.path.exists('user_data.json') or os.path.getsize('user_data.json') == 0:
            await ctx.send("No data available.")
            return

        try:
            with open('user_data.json', 'r') as f:
                data = json.load(f)
                user_balances = data.get("user_balances", {})
        except json.JSONDecodeError:
            await ctx.send("Error reading user data.")
            return

        # Extracting user ID and balance, ignoring other keys
        balances = {user_id: balance for user_id, balance in user_balances.items() if user_id.isdigit() and isinstance(balance, int)}

        # Sorting the dictionary by balance and getting top 10
        top_balances = dict(sorted(balances.items(), key=lambda item: item[1], reverse=True)[:10])

        # Creating an embedded message with orange color
        embed = discord.Embed(
            title="Top 10 Balances",
            description="\n".join([f"<@{user_id}>: {balance}" for user_id, balance in top_balances.items()]),
            color=discord.Color.orange()
        )

        # Sending the leaderboard
        await ctx.send(embed=embed)


    @bot.command(name='balance', help="Check your balance", aliases=['bal'])
    async def balance(ctx):
        user_id = ctx.author.id
        balance = get_user_balance(user_id)

        embed = discord.Embed(
            title="Balance",
            description=f'Balance: {balance}',
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)


setup_trading(bot)


token = TOKEN
bot.run(token)
