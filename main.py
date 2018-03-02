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
import random
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
    quote = random.choice(quoteList) + " - Bjarne Stroustrup."
    await bot.say(quote)



"""
@bot.command(pass_context=True)
async def test(ctx):
    await bot.send_message(ctx.message.author, 'test')
"""

bot.run(token)