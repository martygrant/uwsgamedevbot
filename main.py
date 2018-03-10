##### Discord bot for the UWS Game Dev Society, originally developed by Martin Grant
##### Created 28/02/2018 
##### Last Update 2/03/2018
##### Version 0.1
##### Contributors
#
#
#
#####

import discord
import os
import random as rand
import sys
import math as pythonmath
from decimal import Decimal
from discord.ext import commands

versionNumber = os.getenv('version')
token = os.getenv('token')

bot = commands.Bot(description="Below is a listing for Bjarne's commands. Use '!' infront of any of them to execute a command, like '!help'", command_prefix="!")

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_member_join(member):
    # get channel IDs
    lobbyChannel = bot.get_channel('412327350366240768')
    rulesChannel = bot.get_channel('405741154643214356')
    announcementChannel = bot.get_channel('405451914973806602')
    introductionChannel = bot.get_channel('413835267557031937')

    # Announce a new member joining in the lobby channel.
    welcomeMessage = 'Welcome ' + member.mention 
    welcomeMessage += ' to the UWS Game Dev Society!'
    welcomeMessage += ' Please check out ' + rulesChannel.mention
    welcomeMessage += ' and set your server nickname to your real name.'
    welcomeMessage += ' Visit ' + announcementChannel.mention
    welcomeMessage += ' to see what events are coming up!'
    welcomeMessage += ' Why not ' + introductionChannel.mention
    welcomeMessage += '? Please conduct yourself professionally in public-facing channels like ' + lobbyChannel.mention
    welcomeMessage += '. Thanks!'
    await bot.send_message(lobbyChannel, welcomeMessage)

    # Send above message to new member in a private messag
    welcomeMessage += " Type '!help' for a list of my commands."
    await bot.send_message(member, welcomeMessage)

@bot.command()
async def say(*, something):
    """Make Bjarne say something."""
    await bot.say(something)

@bot.command()
async def version():
    """Display Bjarne version info."""
    versionMessage = 'v' + versionNumber
    versionMessage += " - https://github.com/martygrant/uwsgamedevbot"
    await bot.say(versionMessage)

@bot.command()
async def bjarnequote():
    """Get a quote from Bjarne Stroustrup, creator of C++."""
    quoteList = [
        'A program that has not been tested does not work.',
        'An organisation that treats its programmers as morons will soon have programmers that are willing and able to act like morons only.',
        'Anybody who comes to you and says he has a perfect language is either naïve or a salesman.',
        'C makes it easy to shoot yourself in the foot; C++ makes it harder, but when you do it blows your whole leg off.',
    ]
    quote = rand.choice(quoteList) + " - Bjarne Stroustrup."
    await bot.say(quote)

@bot.command()
async def random(*arg):
    """Generate a random number. Use '!help random' for usage.
    !random for any random number. 
    !random x for between 0 and x. 
    !random x y for between 0 and y.
    """
    randomNumber = -1
    # If no argument passed, get any random number
    if not arg:
        randomNumber = rand.randint(0, sys.maxsize)
    else:
        # Split argument by spaces if we have more than one argument
        splitArg = str(arg[0]).split()
        
        # If we have 1 argument, get a number between 0 and x
        if len(arg) == 1:
            x = int(arg[0])
            randomNumber = rand.randint(0, x)
        else:
            # If we have 2 arguments, get a number between them
            x = int(arg[0])
            y = int(arg[1])
            randomNumber = rand.randint(x, y)
    
    await bot.say(randomNumber)

@bot.command()
async def dice():
    """Roll a dice."""
    await bot.say(rand.randint(0, 6))

@bot.command()
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

    await bot.say(z)

"""
@bot.command(pass_context=True)
async def test(ctx):
    await bot.send_message(ctx.message.author, 'test')
"""

bot.run(token)
