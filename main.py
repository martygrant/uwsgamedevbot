"""Discord bot for the UWS Game Dev Society, originally developed by Martin Grant"""
##### Created 28/02/2018
##### Last Update 30/07/2018
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
        """Custom constructor that creates some custom attributes"""
        super().__init__(command_prefix, formatter=formatter, description=description, pm_help=pm_help, options=options)

        self.config = dict()
        self.ongoing_polls = dict()

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

@BOT.event
async def on_reaction_add(reaction, user):
    """The 'on_reaction_add' event"""
    if reaction.message.id not in BOT.ongoing_polls or user.id == BOT.user.id:
        return

    current_poll = BOT.ongoing_polls[reaction.message.id]
    # If the reaction is the same as any of the existing reactions
    if any(resolve_emoji_from_alphabet(option) == reaction.emoji for option in current_poll.results.keys()):
        # Add the user to the respective result object
        selected_option = resolve_letter_from_emoji(reaction.emoji)
        if user.id not in current_poll.results[selected_option]:
            current_poll.results[selected_option].append(user.id)

        # Update the original poll message
        await BOT.edit_message(current_poll.question_message, embed=current_poll.embed)

@BOT.event
async def on_reaction_remove(reaction, user):
    """The 'on_reaction_remove' event"""
    if reaction.message.id not in BOT.ongoing_polls or user.id == BOT.user.id:
        return

    current_poll = BOT.ongoing_polls[reaction.message.id]
    # If the reaction is the same as any of the existing reactions
    if any(resolve_emoji_from_alphabet(option) == reaction.emoji for option in current_poll.results.keys()):
        # Remove the user from the respective result object
        deselected_option = resolve_letter_from_emoji(reaction.emoji)
        if user.id in current_poll.results[deselected_option]:
            current_poll.results[deselected_option].remove(user.id)

        # Update the original poll message
        await BOT.edit_message(current_poll.question_message, embed=current_poll.embed)

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
    await BOT.say(rand.randint(1, 6))

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
    random_message = messages[rand.randint(0, len(messages))]
    await BOT.say("{} once said: `{}`".format(user, random_message))

ALPHABET = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
            'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
def resolve_emoji_from_alphabet(letter):
    """Returns the emoji representation of a letter"""
    return chr(ord(letter) + 127365)

def resolve_letter_from_emoji(emoji):
    """Returns the character representation of a letter emoji (in lowercase)"""
    return chr(ord(emoji) - 127365)

@BOT.command(pass_context=True)
async def poll(ctx):
    """Starts a new poll. Usage: !poll -Question -durationInSeconds -Option -Option -Option..."""
    args = ctx.message.content.split("-")
    question = args[1]
    duration = args[2]

    duration_float = float(duration)
    if duration_float > 86400:
        return await BOT.say("Poll cannot last longer than one day (86400 seconds).")

    args.pop(0)
    args.pop(0)
    args.pop(0)

    # Create a list of options and trim any whitespace from the string
    options = []
    for option in args:
        if option.strip() not in options:
            options.append(option.strip())

    # Create a new Poll instance and start it
    new_poll = Poll(question, options, duration_float, ctx.message.author, ctx.message.channel)
    await new_poll.start()

def generate_random_colour():
    """Generates a random colour decimal"""
    letters = "0123456789ABCDEF"
    colour_string = ""
    for i in range(6):
        colour_string += rand.choice(letters)
    return int(colour_string, 16)

class Poll:
    """An instance of this class handles the creation of a poll and monitoring of reactions"""

    @property
    def time_left(self):
        """Gets the time left for this instance of the poll (in seconds)"""
        return (timestamp() / 1000) - self.time_to_stop

    @property
    def embed(self):
        """Constructs a Rich Embed for this poll"""
        e = discord.Embed(type="rich",
                          description="This is {}'s poll.".format(self.initiator.mention),
                          timestamp=datetime.now() + timedelta(seconds=self.time_to_stop),
                          colour=generate_random_colour())

        e.add_field(name="\u200b", value="**Options**", inline=False)
        for i, option in enumerate(self.options):
            current_votes = len(self.results[ALPHABET[i]])
            e.add_field(name="{}. {}".format(ALPHABET[i].upper(), option), value="{} votes".format(current_votes), inline=True)

        e.set_author(name=self.question,
                     icon_url=self.initiator.avatar_url)
        if self.time_left > 0:
            e.set_footer(text="Time remaining: {} seconds".format(self.time_left))

        return e

    def __init__(self, question, options, duration, owner, message=None):
        self.question = question
        self.question_message = None
        self.options = options
        self.duration = duration
        self.time_to_stop = (timestamp() / 1000) + duration
        self.initiator = owner
        self.results = {}
        for i in range(len(self.options)):
            self.results[ALPHABET[i]] = []

        # If a 'message' object already exists, use that
        if isinstance(message, discord.Message):
            self.channel = message.channel
            self.question_message = message

        # If not, create a new message in 'Poll.start()'
        elif isinstance(message, discord.Channel):
            self.channel = message
        else:
            raise TypeError("The \{message\} argument must be of type 'Discord.Message' or 'Discord.Channel'")

    async def start(self):
        """Starts the poll and creates a task for the poll to end using by the duration"""
        # Send a new message if one wasn't already passed to the constructor
        if self.question_message is None:
            self.question_message = await BOT.send_message(self.channel, embed=self.embed)
        BOT.ongoing_polls[self.question_message.id] = self

        await self.add_reactions()
        BOT.loop.create_task(self.stop())

    async def stop(self):
        """Stops the poll and posts the results"""

        await BOT.wait_until_ready()
        await asyncio.sleep(self.duration)

        # TODO: finalise data to prettify output

        await BOT.send_message(self.channel, "**{}**'s poll has finished. Here are the results.".format(self.initiator.name), embed=self.embed)
        BOT.ongoing_polls.pop(self.question_message.id, self)

    async def add_reactions(self):
        """Adds the respective reactions for each option for users to react to"""
        for i in range(len(self.options)):
            await BOT.add_reaction(self.question_message, resolve_emoji_from_alphabet(ALPHABET[i].lower()))

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
