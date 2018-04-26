##### Discord bot for the UWS Game Dev Society, originally developed by Martin Grant
##### Created 28/02/2018 
##### Last Update 26/04/2018
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
import string
import asyncio
from threading import Timer
from decimal import Decimal
from discord.ext import commands
from weather import Weather, Unit

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

    # Send above message to new member in a private message
    welcomeMessage += " Type '!help' for a list of my commands."
    await bot.send_message(member, welcomeMessage)
    
@bot.event
async def on_member_remove(member):
    lobbyChannel = bot.get_channel('412327350366240768')
    
    message = "User " + member.mention
    message += " has left the server. Goodbye!"
    
    await bot.send_message(lobbyChannel, message)

"""
@bot.event
async def on_message(message):
    # If this line isn't used, any commands are ignored as this function
    # overrides an interal discord.py function
    await bot.process_commands(message)

    if message.author.id == bot.user.id:
        return
    elif "power" in message.content: # Post a daft Palpatine meme if anyone says 'power'
        embed = discord.Embed()
        embed.set_image(url="https://i.imgur.com/msS0CHv.jpg")
        await bot.send_message(message.channel, embed=embed)
    else:
        return
"""

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

@bot.command(pass_context=True)
async def quote(ctx, *arg):
    """Quote a user randomly. Usage: !quote <username>, if no user is specified it will quote yourself."""
    # If argument is specified find a quote from that user, else 
    # get a quote from the user who executed the command
    user = ctx.message.author.name
    if arg:
        user = arg[0]
        user = ""
        # If username has spaces, we need to build a string for it and remove the last space
        for x in arg:
            user += x
            user += " "
        user = user[:-1]
            
    print(user)

    # Get a quote from the channel the command was executed in
    channel = ctx.message.channel

    # Store a list of retrieved messages
    messages = []

    #lobbyChannel = bot.get_channel('412327350366240768')

    # Get all messages matching the specified user in the channel this command
    # was executed in. It will only check the last x messages specified by the limit in the
    # function call below
    async for message in bot.logs_from(channel, limit=1000):
        if message.author.name == user:
            messages.append(message.content)

    # Pick a random message and output it
    randomMessage = messages[rand.randint(0, len(messages))]
    output = user
    output += " once said: `"
    output += randomMessage
    output += "`"
    await bot.say(output)



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

@bot.command()
async def weather(*, arg):
    """Get current weather conditions at a specified location from Yahoo. E.g '!weather glasgow'"""
    weather = Weather(unit=Unit.CELSIUS)
    degree_sign = u'\N{DEGREE SIGN}'

    location = weather.lookup_by_location(arg)

    conditions = ""
    conditions += location.title
    conditions += ") - "
    conditions += location.condition.text
    conditions += " - "
    conditions += location.condition.temp
    conditions += degree_sign
    conditions += location.units.temperature
    conditions += " - " 
    conditions += "Humidity: "
    conditions += location.atmosphere['humidity']
    conditions += "%"
    conditions += " - "
    conditions += "Wind: "
    conditions += location.wind.speed
    conditions += " "
    conditions += location.units.speed

    await bot.say(conditions)


@bot.command()
async def forecast(*, arg):
    """Get the forecast for the next 5 days for a specified location from Yahoo. E.g '!forecast glasgow'"""
    weather = Weather(unit=Unit.CELSIUS)
    degree_sign = u'\N{DEGREE SIGN}'

    location = weather.lookup_by_location(arg)
    await bot.say("5 Day Forecast for: " + location.title)

    forecasts = location.forecast
    count = 0
    for forecast in forecasts:
        if count > 4:
            break
        forecastOutput = "("
        forecastOutput += forecast.date
        forecastOutput += " - "
        forecastOutput += forecast.text
        forecastOutput += " - "
        forecastOutput += "High: " + forecast.high + degree_sign + location.units.temperature
        forecastOutput += " - Low: "
        forecastOutput += forecast.low + degree_sign + location.units.temperature
        count += 1
        await bot.say(forecastOutput)

"""
@bot.command(pass_context=True)
async def test(ctx):
    await bot.send_message(ctx.message.author, 'test')
"""

bot.run(token)
