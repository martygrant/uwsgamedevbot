"""Discord bot for the UWS Game Dev Society, originally developed by Martin Grant"""
##### Created 28/02/2018
##### Last Update 31/07/2018
##### Version 0.2
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

import utilities as utils

REPOSITORY_URL = "https://github.com/martygrant/uwsgamedevbot"
VERSION_NUMBER = os.getenv('version')
BOT_TOKEN = os.getenv('token')

##### [ CLASSES ] #####

class SavableDict(dict):
    """An extended dict that allows saving to file"""
    @property
    def raw_dict(self):
        """Returns a readable representation of this dict"""
        target = {}

        for key, val in self.items():
            if not str(key).startswith('_'):
                target[key] = val

        return target

    def __init__(self, destination, **kwarg):
        super().__init__(kwarg)
        self._dest = destination

    def __setitem__(self, key, val):
        super().__setitem__(key, val)
        self.save()

    def __delitem__(self, key):
        super().__delitem__(key)
        self.save()

    def save(self):
        """Saves the dict to file"""
        with open(self._dest, 'w') as file:
            file.write(json.dumps(self.raw_dict))

class Config(SavableDict):
    """The config class"""
    @property
    def raw_dict(self):
        """Returns a custom representation of this dict"""
        return {
            "channels": {
                "lobby": self["channels"]["lobby"],
                "rules": self["channels"]["rules"],
                "announcements": self["channels"]["announcements"],
                "introductions": self["channels"]["introductions"]
            }
        }

    def __init__(self):
        super().__init__("config.json")

    def refresh(self):
        """Refreshes the dict from file"""
        new_config = {}
        with open(self._dest, 'r') as file:
            new_config = json.loads(file.read())

        # Remove any properties that are not part of the new config
        for key, val in self.raw_dict:
            if key not in new_config:
                del self[key]

        # Overwrite any new properties
        for key, val in new_config:
            self[key] = val

class OngoingPolls(SavableDict):
    """The class responsible for poll persistence"""
    @property
    def raw_dict(self):
        target_dict = {}

        for key, value in self.items():
            if not str(key).startswith('_'):
                target_dict[key] = value.raw_dict

        return target_dict

    def __init__(self):
        super().__init__("persistence/ongoing_polls.json")

    async def reinitialise(self):
        """Re-instantiates the polls saved to file"""
        decoded = {}
        with open(self._dest) as file:
            decoded = json.loads(file.read())

        for key, val in decoded.items():
            if val["timestamp"] + val["duration"] <= timestamp():
                continue

            restored_poll = await Poll.restore(val)
            if restored_poll is not None:
                self[key] = restored_poll

class Poll:
    """An instance of this class handles the creation of a poll and monitoring of reactions"""

    @staticmethod
    async def restore(poll_dict):
        """Restores a poll from a given dictionary"""
        question_message = None
        owner = None
        try:
            question_message = await BOT.get_message(poll_dict["channel_id"], poll_dict["message_id"])
            owner = await BOT.get_user_info(poll_dict["owner_id"])
        except discord.NotFound:
            # Message or Owner don't exist or cannot be found: skip instancing poll
            return None

        options = []
        results = {}
        for letter, result in poll_dict["results"].items():
            options.append(result["option_name"])
            results[letter] = result["votes"]

        new_poll = Poll(poll_dict["question"], options, poll_dict["timestamp"], poll_dict["duration"] - (timestamp() - poll_dict["timestamp"]), owner, question_message)
        new_poll.results = results

        await new_poll.start()
        return new_poll

    @property
    def raw_dict(self):
        """Returns the raw dict representation of this instance"""
        results = {}
        for i, letter in enumerate(self.results):
            results[letter] = {
                "option_name": self.options[i],
                "votes": self.results[letter]
            }

        return {
            "message_id": self.question_message.id,
            "timestamp": self.timestamp,
            "duration": self.duration,
            "question": self.question,
            "owner_id": self.initiator.id,
            "channel_id": self.channel.id,
            "results": results
        }

    @property
    def time_left(self):
        """Gets the time left for this instance of the poll (in milliseconds)"""
        return self.time_to_stop - timestamp()

    @property
    def embed(self):
        """Constructs a Rich Embed for this poll"""
        e = discord.Embed(type="rich",
                          description="This is {}'s poll.".format(self.initiator.mention),
                          timestamp=datetime.now() + timedelta(seconds=self.duration),
                          colour=utils.generate_random_colour())

        e.add_field(name="\u200b", value="**Options**", inline=False)
        for i, option in enumerate(self.options):
            current_votes = len(self.results[utils.ALPHABET[i]])
            e.add_field(name="{}. {}".format(utils.ALPHABET[i].upper(), option), value="{} votes".format(current_votes), inline=True)

        e.set_author(name=self.question,
                     icon_url=self.initiator.avatar_url)
        if self.time_left > 0:
            e.set_footer(text="Time remaining: {} seconds".format(int(self.time_left)))

        return e

    def __init__(self, question, options, ts, duration, owner, message=None):
        self.destroyed = False
        self.question = question
        self.question_message = None
        self.options = options
        self.timestamp = ts
        self.duration = duration
        self.time_to_stop = self.timestamp + duration
        self.initiator = owner
        self.results = {}
        for i in range(len(self.options)):
            self.results[utils.ALPHABET[i]] = []

        # If a 'message' object already exists, use that
        if isinstance(message, discord.Message):
            self.channel = message.channel
            self.question_message = message

        # If not, create a new message in 'Poll.start()'
        elif isinstance(message, discord.Channel):
            self.channel = message
        else:
            raise TypeError("The \{message\} argument must be of type 'Discord.Message' or 'Discord.Channel'")

    def add_vote(self, option, user):
        """Adds a vote to the current voting pool"""
        user_id = user
        if isinstance(user, discord.User):
            user_id = user.id

        self.results[option].append(user_id)
        BOT.ongoing_polls.save()

    def remove_vote(self, option, user):
        """Removes a vote from the current voting pool"""
        user_id = user
        if isinstance(user, discord.User):
            user_id = user.id

        self.results[option].remove(user_id)
        BOT.ongoing_polls.save()

    async def start(self):
        """Starts the poll and creates a task for the poll to end using by the duration"""
        # Send a new message if one wasn't already passed to the constructor
        if self.question_message is None:
            self.question_message = await BOT.send_message(self.channel, embed=self.embed)
        BOT.ongoing_polls[self.question_message.id] = self

        if self.question_message not in BOT.messages:
            BOT.messages.append(self.question_message)

        await self.add_reactions()
        BOT.loop.create_task(self.stop())

    async def stop(self):
        """Stops the poll and posts the results"""
        await BOT.wait_until_ready()
        await asyncio.sleep(self.duration)

        if self.destroyed:
            return

        # TODO: finalise data to prettify output

        await BOT.send_message(self.channel, "**{}**'s poll has finished. Here are the results.".format(self.initiator.mention), embed=self.embed)
        BOT.ongoing_polls.pop(self.question_message.id, self)

    def destroy(self):
        self.destroyed = True

    async def add_reactions(self):
        """Adds the respective reactions for each option for users to react to"""
        for i in range(len(self.options)):
            await BOT.add_reaction(self.question_message, utils.resolve_emoji_from_alphabet(utils.ALPHABET[i].lower()))

class CustomBot(commands.Bot):
    """An extension of the discord.py Bot Class"""
    def __init__(self, command_prefix, formatter=None, description=None, pm_help=False, **options):
        """Custom constructor that creates some custom attributes"""
        super().__init__(command_prefix, formatter=formatter, description=description, pm_help=pm_help, options=options)

        self.config = Config()
        self.ongoing_polls = OngoingPolls()

    def get_message(self, channel, message_id):
        """Custom method that allows a channel string instead of a channel object"""
        if isinstance(channel, str):
            return super().get_message(self.get_channel(channel), message_id)
        return super().get_message(channel, message_id)

    def send_message(self, destination, content=None, *, tts=False, embed=None):
        """Custom method that allows a channel ID as the 'destination' parameter"""
        if isinstance(destination, str):
            return super().send_message(self.get_channel(destination), content, tts=tts, embed=embed)
        return super().send_message(destination, content, tts=tts, embed=embed)

##### [ BOT INSTANTIATION ] #####

BOT = CustomBot(description="Below is a listing for Bjarne's commands. Use '!' infront of any of them to execute a command, like '!help'", command_prefix="!")

##### [ EVENT LISTENERS ] #####

@BOT.event
async def on_ready():
    """The 'on_ready' event"""
    print("Logged in as {} ({})\n------".format(BOT.user.name, BOT.user.id))
    await BOT.ongoing_polls.reinitialise()

@BOT.event
async def on_member_join(member):
    """The 'on_member_join' event"""

    # Refresh channel IDs
    BOT.config.refresh()

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
    BOT.config.refresh()

    await BOT.send_message(BOT.config["channels"]["lobby"], "User **{}** has left the server. Goodbye!".format(str(member)))

@BOT.event
async def on_message_delete(message):
    """The 'on_message_deleted' event"""
    if message.id not in BOT.ongoing_polls:
        return

    deleted_poll = BOT.ongoing_polls[message.id]
    deleted_poll.destroy()

    await BOT.send_message(deleted_poll.initiator, "Your poll with the question `{}` in {} was deleted. Here are the results.".format(deleted_poll.question, deleted_poll.channel.mention), embed=deleted_poll.embed)

@BOT.event
async def on_reaction_add(reaction, user):
    """The 'on_reaction_add' event"""
    if reaction.message.id not in BOT.ongoing_polls or user.id == BOT.user.id:
        return

    current_poll = BOT.ongoing_polls[reaction.message.id]
    # If the reaction is the same as any of the existing reactions
    if any(utils.resolve_emoji_from_alphabet(option) == reaction.emoji for option in current_poll.results.keys()):
        # Add the user to the respective result object
        selected_option = utils.resolve_letter_from_emoji(reaction.emoji)
        if user.id not in current_poll.results[selected_option]:
            current_poll.add_vote(selected_option, user)

        # Update the original poll message
        await BOT.edit_message(current_poll.question_message, embed=current_poll.embed)

@BOT.event
async def on_reaction_remove(reaction, user):
    """The 'on_reaction_remove' event"""
    if reaction.message.id not in BOT.ongoing_polls or user.id == BOT.user.id:
        return

    current_poll = BOT.ongoing_polls[reaction.message.id]
    # If the reaction is the same as any of the existing reactions
    if any(utils.resolve_emoji_from_alphabet(option) == reaction.emoji for option in current_poll.results.keys()):
        # Remove the user from the respective result object
        deselected_option = utils.resolve_letter_from_emoji(reaction.emoji)
        if user.id in current_poll.results[deselected_option]:
            current_poll.remove_vote(deselected_option, user)

        # Update the original poll message
        await BOT.edit_message(current_poll.question_message, embed=current_poll.embed)

##### [ BOT COMMANDS ] #####

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
        if channel.is_private == False:
            if message.author.display_name.lower() == user:
                messages.append(message.content)
        else:
            if message.author.nick.lower() == user:
                messages.append(message.content)

    # Pick a random message and output it
    random_message = messages[rand.randint(0, len(messages))]
    await BOT.say("{} once said: `{}`".format(user, random_message))

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
    new_poll = Poll(question, options, timestamp(), duration_float, ctx.message.author, ctx.message.channel)
    await new_poll.start()

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

    embed = discord.Embed(type="rich", colour=utils.generate_random_colour(), timestamp=datetime.now())
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
    embed = discord.Embed(type="rich", colour=utils.generate_random_colour(), timestamp=datetime.now())
    embed.set_author(name="5-day forecast for {}".format(location.title))

    for cast in forecasts:
        if count > 4:
            break
        count += 1
        embed.add_field(name=cast.date, value="{}\nHigh: {}{}{}\nLow: {}{}{}".format(cast.text, cast.high, degree_sign, location.units.temperature, cast.low, degree_sign, location.units.temperature))

    await BOT.say(embed=embed)


def getOnlineUserCount(users):
    count = 0
    for user in users:
        if str(user.status) == "online" or str(user.status) == "idle" or str(user.status) == "dnd":
            count += 1

    return count

def getNewestMember(users):
    userList = list(users)

    newest = userList[0]
    for x in userList[2:]:
        if x.joined_at > newest.joined_at:
            newest = x

    return newest

@BOT.command(pass_context=True)
async def stats(ctx):
    """Get server statistics."""
    server = ctx.message.author.server
    serverName = server.name
    numberOfUsers = server.member_count
    members = server.members
    numberOfOnlineUsers = getOnlineUserCount(members)
    createdDate = server.created_at.strftime('%Y-%m-%d')
    newestMember = getNewestMember(members)

    embed = discord.Embed(type="rich", colour=utils.generate_random_colour(), timestamp=datetime.now())
    embed.set_thumbnail(url=server.icon_url)
    embed.set_author(name=serverName)
    embed.add_field(name="Created", value=createdDate)
    embed.add_field(name="Users Online", value=numberOfOnlineUsers)
    embed.add_field(name="Users Total", value=numberOfUsers)
    embed.add_field(name="Newest Member", value=newestMember)
    
    await BOT.say(embed=embed)

##### [ BOT LOGIN ] #####

BOT.run(BOT_TOKEN)
