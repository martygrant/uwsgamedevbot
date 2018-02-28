import discord
from discord.ext import commands

#token = ''

bot = commands.Bot(description="Below is a listing for Bjarne's commands. Use '!' infront of any of them to execute a command, like '!help'", command_prefix="!")

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_member_join(member):
    # Announce a new member joining in the lobby channel.
    welcomeMesssage = member.mention + ' has joined the server. Welcome!'
    channel = bot.get_channel('400075802018054146')
    await bot.send_message(channel, welcomeMesssage)

    # Send a private message to the new member with server info
    rulesChannel = bot.get_channel('400443010153709569')
    introductionChannel = bot.get_channel('418194492059811842')
    msg = 'Welcome to the UWS Game Dev Society Discord! You can find our rules in ' + rulesChannel.mention
    msg += '. Please set your server nickname to your real name for networking purposes. '
    msg += 'Let us know who you are in ' + introductionChannel.mention + " . "
    msg += "Type '!help' for a list of my commands."
    await bot.send_message(member, msg)


@bot.command()
async def say(*, something):
    """Make Bjarne say something."""
    await bot.say(something)

@bot.command()
async def version():
    """Display Bjarne version info."""
    await bot.say('alphaaa')
    

"""
@bot.command(pass_context=True)
async def test(ctx):
    await bot.send_message(ctx.message.author, 'test')
"""

bot.run(token)