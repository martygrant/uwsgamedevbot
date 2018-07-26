"""Discord bot for the UWS Game Dev Society, originally developed by Martin Grant"""
##### Created 28/02/2018
##### Last Update 25/07/2018
##### Version 0.1
##### Contributors
#
# https://github.com/medallyon
#
#####

import os
import random as rand
import sys
from datetime import datetime, timedelta
from time import time as timestamp
import json
import math as pythonmath
import asyncio
from decimal import Decimal
import discord
from discord.ext import commands
from weather import Weather, Unit

REPOSITORY_URL = "https://github.com/martygrant/uwsgamedevbot"
VERSION_NUMBER = os.getenv('version')
BOT_TOKEN = os.getenv('token')

class CustomBot(commands.Bot):
    """An extension of the discord.py Bot Class"""
    def __init__(self, command_prefix, formatter=None, description=None, pm_help=False, **options):
        """Custom constructor that creates a 'config' attribute"""
        super().__init__(command_prefix, formatter=formatter, description=description, pm_help=pm_help, options=options)
        self.config = dict()

    def send_message(self, destination, content=None, *, tts=False, embed=None):
        """Custom method that allows a channel ID as the 'destination' parameter"""
        if isinstance(destination, str):
            return super().send_message(self.get_channel(destination), content, tts=tts, embed=embed)
        return super().send_message(destination, content, tts=tts, embed=embed)

BOT = CustomBot(description="Below is a listing for Bjarne's commands. Use '!' infront of any of them to execute a command, like '!help'", command_prefix="!")

def refresh_config():
    """Refreshes the config file and its properties"""
    config_file = open('config.json', 'r')
    BOT.config = config_file.read()
    config_file.close()

    decoder = json.JSONDecoder()
    BOT.config = decoder.decode(BOT.config)

@BOT.event
async def on_ready():
    """The 'on_ready' event"""
    print("Logged in as {} ({})\n------".format(BOT.user.name, BOT.user.id))

@BOT.event
async def on_member_join(member):
    """The 'on_member_join' event"""

    # Refresh channel IDs
    refresh_config()

    welcome_message = """Welcome to the UWS Game Dev Society!

Please check out {} and set your server nickname to your real name. Visit {} to see what events are coming up! Why not {}?
Please conduct yourself professionally in public-facing channels like {}. Thanks!

Type '!help' for a list of my commands.""".format("<#{}>".format(BOT.config["channels"]["rules"]), "<#{}>".format(BOT.config["channels"]["announcements"]), "<#{}>".format(BOT.config["channels"]["introductions"]), "<#{}>".format(BOT.config["channels"]["lobby"]))

    # Send the welcome message to the user individually
    await BOT.send_message(member, welcome_message)
    # Announce a new member joining in the lobby channel
    await BOT.send_message(BOT.config["channels"]["lobby"], "Welcome {} to the UWS Game Dev Society!".format(member.mention))

@BOT.event
async def on_member_remove(member):
    """The 'on_member_remove' event"""

    # Refresh channel IDs
    refresh_config()

    await BOT.send_message(BOT.config["channels"]["lobby"], "User **{}** has left the server. Goodbye!".format(str(member)))

@BOT.command()
async def say(*something):
    """Make Bjarne say something."""
    if something:
        await BOT.say(" ".join(something))

@BOT.command()
async def version():
    """Display Bjarne version info."""
    await BOT.say("v{} - {}".format(VERSION_NUMBER, REPOSITORY_URL))

@BOT.command()
async def bjarnequote():
    """Get a quote from Bjarne Stroustrup, creator of C++."""
    quotes = [
        'A program that has not been tested does not work.',
        'An organisation that treats its programmers as morons will soon have programmers that are willing and able to act like morons only.',
        'Anybody who comes to you and says he has a perfect language is either naïve or a salesman.',
        'C makes it easy to shoot yourself in the foot; C++ makes it harder, but when you do it blows your whole leg off.',
    ]
    await BOT.say(rand.choice(quotes) + " - Bjarne Stroustrup.")

@BOT.command()
async def random(*arg):
    """Generate a random number. Use '!help random' for usage.
    !random for any random number.
    !random x for between 0 and x.
    !random x y for between 0 and y.
    """
    random_number = -1
    # If no argument passed, get any random number
    if not arg:
        random_number = rand.randint(0, sys.maxsize)
    else:
        # If we have 1 argument, get a number between 0 and x
        if len(arg) == 1:
            x = int(arg[0])
            random_number = rand.randint(0, x)
        else:
            # If we have 2 arguments, get a number between them
            x = int(arg[0])
            y = int(arg[1])
            random_number = rand.randint(x, y)

    await BOT.say(random_number)

@BOT.command()
async def dice():
    """Roll a dice."""
    await BOT.say(rand.randint(0, 6))

@BOT.command()
async def math(*, arg):
    """Perform math operations, e.g '10 + 20'
    Supports: (+ / * -)
    sq x - square x
    sqrt x - square root of x
    pi - the constant pi
    degrees - convert radians to degrees
    radians - convert degrees to radians
    ceiling - get ceiling of a float, e.g ceil 7.7 = 8
    floor - get floor of a float, e.g. floor 7.7 = 7
    """
    arg = arg.split()
    z = "Error."
    if arg[0] == "sq":
        x = float(arg[1])
        z = float(x * x)
    elif arg[0] == "sqrt":
        x = float(arg[1])
        z = float(pythonmath.sqrt(x))
    elif arg[0] == "pi":
        z = pythonmath.pi
    elif arg[0] == "degrees":
        x = float(arg[1])
        z = pythonmath.degrees(x)
    elif arg[0] == "radians":
        x = float(arg[1])
        z = pythonmath.radians(x)
    elif arg[0] == "ceiling":
        x = float(arg[1])
        z = pythonmath.ceil(x)
    elif arg[0] == "floor":
        x = float(arg[1])
        z = pythonmath.floor(x)
    else:
        operator = arg[1]
        x = float(arg[0])
        y = float(arg[2])
        if operator == "+":
            z = x + y
        if operator == "/":
            if y == 0:
                z = "DENIED."
            else:
                z = x / y
        if operator == "*":
            z = x * y
        if operator == "-":
            z = x - y

    if z != "DENIED.":
        # Strip trailing 0s if we just have a whole number result
        z = '%g' % (Decimal(str(z)))

    await BOT.say(z)

@BOT.command(pass_context=True)
async def quote(ctx, *arg):
    """Quote a user randomly. Usage: !quote <username>, if no user is specified it will quote yourself."""
    channel = ctx.message.channel
    messages = []

    user = ctx.message.author.nick
    if arg:
        user = arg[0]
        user = ""
        # If username has spaces, we need to build a string for it and remove the last space
        for x in arg:
            user += x
            user += " "
        user = user[:-1]

    user = user.lower()

    async for message in BOT.logs_from(channel, limit=2000):
        if message.author.nick.lower() == user:
            messages.append(message.content)

    # Pick a random message and output it

votingActive = False 
question = ""
duration = ""
options = ""
results = []
participants = []

async def stopPoll(duration):
    global votingActive
    global question
    global options
    global results
    global participants

    await bot.wait_until_ready()
    await asyncio.sleep(duration)
    channel = bot.get_channel('412327350366240768')

    message = "Current poll has now finished. The question was: `"
    message += question
    message += "` The results are: "
    
    await bot.send_message(channel, message) 

    numberOfVotes = 0
    for x in results:
        numberOfVotes += x

    for x in range(0, len(options)):
        message = "`"
        message += options[x]
        message += "- "
        message += str(results[x])
        message += " ("
        message += str((results[x] / numberOfVotes) * 100)
        message += "%)`"
        await bot.send_message(channel, message)

    message = ""

    message = "Number of voters: " 
    message += str(len(participants))
    await bot.send_message(channel, message)

    message = "Type '!poll help' to start a new poll."
    await bot.send_message(channel, message)

    votingActive = False 
    question = ""
    duration = ""
    options = ""
    results = []
    participants = []
    
@bot.command()
async def poll(*, arg=None):
    """Start a new poll. Usage: !poll -Question -durationInSeconds -Option -Option -Option..."""
    
    global votingActive
    global question
    global duration
    global options
    global results
    global participants

    if not votingActive:
        
        arg = arg.split("-")

        question = arg[1]
        duration = arg[2]
        durationFloat = float(duration)

        if durationFloat < 86400:
            votingActive = True

            bot.loop.create_task(stopPoll(durationFloat))

            arg.pop(0)
            arg.pop(0)
            arg.pop(0)

            options = []

            alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

            for x in range(0, len(arg)):
                option = alphabet[x]
                option += ": "
                option += arg[x]
                options.append(option)
                results.append(0)

            print(results)

            prompt = "New poll started! It will close in "
            prompt += duration
            prompt += " seconds."
            prompt += " Use '!vote A' etc. to enter your vote."
            await bot.say(prompt)
            prompt = "`"
            prompt += question
            prompt += "`"
            
            await bot.say(prompt)

            for x in options:
                opt = "`"
                opt += x
                opt += "`"
                await bot.say(opt)
    random_message = messages[rand.randint(0, len(messages))]
    await BOT.say("{} once said: `{}`".format(user, random_message))

ALPHABET = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
            'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
def resolve_emoji_from_alphabet(letter):
    """Returns the emoji representation of a letter"""
    return chr(ord(letter) + 127365)

def generate_random_colour():
    """Generates a random colour decimal"""
    letters = "0123456789ABCDEF"
    colour_string = ""
    for i in range(6):
        colour_string += rand.choice(letters)
    return int(colour_string, 16)

        else:
            await bot.say("Poll cannot last longer than one day (86400 seconds).")

    else:
        await bot.say("A poll is already active. Use !vote to participate and see how long is left.")


@bot.command(pass_context=True)
async def vote(ctx, *arg):
    """Use '!vote A' to vote for an option in the current poll. Use '!vote' to see the question."""
    if votingActive:
        if not arg:
            prompt = "`Current poll: "
            prompt += question
            prompt += "`"
            prompt += " Poll closes in "
            prompt += duration
            prompt += " seconds. Use !vote A etc to enter your vote."
            await bot.say(prompt)

            for x in options:
                opt = "`"
                opt += x
                opt += "`"
                await bot.say(opt)

        else:
            if ctx.message.author not in participants:
                arg = arg[0]
                arg = arg.upper()
                alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

                if arg not in alphabet:
                    await bot.say("Invalid option.")
                else:
                    results[alphabet.index(arg)] += 1
                    participants.append(ctx.message.author)
                    await bot.say("Vote registered!")
            else:
                prompt = ctx.message.author.mention
                prompt += " you have already voted."
                await bot.say(prompt)
    else:
        await bot.say("No poll active. Use '!poll help' to start a poll.")


@BOT.command()
async def weather(*arg):
    """Get current weather conditions at a specified location from Yahoo. E.g '!weather glasgow'"""
    weather_object = Weather(unit=Unit.CELSIUS)
    degree_sign = u'\N{DEGREE SIGN}'

    # Default to glasgow if no argument passed
    if not arg:
        city = 'glasgow'
    else:
        city = arg[0]

    location = weather_object.lookup_by_location(city)

    embed = discord.Embed(type="rich", colour=generate_random_colour(), timestamp=datetime.now())
    embed.set_author(name=location.title)
    embed.add_field(name="Temperature", value="{}{}{}".format(location.condition.temp, degree_sign, location.units.temperature))
    embed.add_field(name="Condition", value=location.condition.text)
    embed.add_field(name="Humidity", value="{}%".format(location.atmosphere["humidity"]))
    embed.add_field(name="Wind", value="{} {}".format(location.wind.speed, location.units.speed))

    await BOT.say(embed=embed)

@BOT.command()
async def forecast(*arg):
    """Get the forecast for the next 5 days for a specified location from Yahoo. E.g '!forecast glasgow'"""
    weather_object = Weather(unit=Unit.CELSIUS)
    degree_sign = u'\N{DEGREE SIGN}'

    # Default to glasgow if no argument passed
    if not arg:
        city = 'glasgow'
    else:
        city = arg[0]

    location = weather_object.lookup_by_location(city)
    forecasts = location.forecast
    count = 0
    embed = discord.Embed(type="rich", colour=generate_random_colour(), timestamp=datetime.now())
    embed.set_author(name="5-day forecast for {}".format(location.title))

    for cast in forecasts:
        if count > 4:
            break
        count += 1
        embed.add_field(name=cast.date, value="{}\nHigh: {}{}{}\nLow: {}{}{}".format(cast.text, cast.high, degree_sign, location.units.temperature, cast.low, degree_sign, location.units.temperature))

    await BOT.say(embed=embed)

BOT.run(BOT_TOKEN)
