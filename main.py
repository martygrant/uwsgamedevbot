import discord
import os
from discord.ext import commands

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
    await bot.say('super early, dont expect much yet, details on contributing to Bjarne will come soon')
    

"""
@bot.command(pass_context=True)
async def test(ctx):
    await bot.send_message(ctx.message.author, 'test')
"""

bot.run(token)