"""Discord bot for the UWS Game Dev Society, originally developed by Martin Grant"""
##### Created 28/02/2018
##### Last Update 18/09/2018
##### Version 0.2
##### Contributors
#
# https://github.com/medallyon
#
#####

import os
from pathlib import Path
import random as rand
import sys
import re
from datetime import datetime, timedelta
from time import time as timestamp
import json
import math as pythonmath
import asyncio
from decimal import Decimal
import discord
from discord.ext import commands
from discord.utils import get
import requests
#import wikipedia
from translate import Translator
from coinmarketcap import Market
from forex_python.converter import CurrencyRates
import wolframalpha

import utilities as utils
# import modules.weather
import modules.hangman

REPOSITORY_URL = "https://github.com/martygrant/uwsgamedevbot"
VERSION_NUMBER = os.getenv('version')
BOT_TOKEN = os.getenv('token')
GIPHY_TOKEN = os.getenv('giphy')
WOLFRAM_KEY = "42XXHU-YEK7852REU"

DEVELOPERS = [ 129036763367735297, 317284059275460608 ]

true = True
false = False

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

		# Create a file handle for this file
		this_dict = {}
		self._file_handle = Path(self._dest)

		# Create this file if it does not exist
		if not self._file_handle.is_file():
			self._file_handle.write_text(json.dumps(this_dict))

		# Or load this file and load it into this object
		else:
			this_dict = json.loads(self._file_handle.read_text())

		for key, val in this_dict.items():
			self[key] = val

	def __setitem__(self, key, val):
		super().__setitem__(key, val)
		self.save()

	def __delitem__(self, key):
		super().__delitem__(key)
		self.save()

	def save(self):
		"""Saves the dict to file"""
		encoded_json = json.dumps(self.raw_dict, indent=2)
		self._file_handle.write_text(encoded_json)

class OngoingPolls(SavableDict):
	"""The class responsible for poll persistence"""
	@property
	def raw_dict(self):
		target_dict = {}

		for key, value in self.items():
			if not str(key).startswith('_') and isinstance(value, Poll):
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
			self.question_message = await self.channel.send(embed=self.embed)
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

		await self.channel.send("**{}**'s poll has finished. Here are the results.".format(self.initiator.mention), embed=self.embed)
		# BOT.ongoing_polls.pop(self.question_message.id, self)
		del BOT.ongoing_polls[self.question_message.id]

	def destroy(self):
		self.destroyed = True

	async def add_reactions(self):
		"""Adds the respective reactions for each option for users to react to"""
		for i in range(len(self.options)):
			await BOT.add_reaction(self.question_message, utils.resolve_emoji_from_alphabet(utils.ALPHABET[i].lower()))

class CustomBot(commands.Bot):
	"""An extension of the discord.py Bot Class"""
	def __init__(self, command_prefix, home_server_id="", formatter=None, description=None, pm_help=False, **options):
		"""Custom constructor that creates some custom attributes"""
		super().__init__(command_prefix, formatter=formatter, description=description, pm_help=pm_help, options=options)

		self.home_server_id = home_server_id
		self.home_server = None

		self.ongoing_polls = OngoingPolls()

	lastBjarneChoice = -1
	last8BallChoice = -1

##### [ BOT INSTANTIATION ] #####

BOT = CustomBot(description="Below is a listing for Bjarne's commands. Use '!' infront of any of them to execute a command, like '!help'", command_prefix="!", home_server_id="405451738804518916")
# BOT.load_extension('modules.weather')
BOT.load_extension('modules.hangman')
BOT.load_extension('modules.dictionary')

##### [ EVENT LISTENERS ] #####

@BOT.event
async def on_ready():
	"""The 'on_ready' event"""
	print("Logged in as {} ({})\n------".format(BOT.user.name, BOT.user.id))
	await BOT.ongoing_polls.reinitialise()

@BOT.event
async def on_member_join(member):
	"""The 'on_member_join' event"""

	# Add a temporary role that disallows access to all channels until confirming the rules
	await member.add_roles(*list(filter(lambda r: r.name == "Didn't read the Rules", member.guild.roles)))

	welcome_message = """Welcome to the **UWS Game Development Society**!

Please review the rules in the <#579342050156347392> channel. When you're done, simply click on the :ok_hand: emoji right below the message. This will give you access to a lot more channels.

Type `!help` for a list of my commands.

"""

	# Send the welcome message to the user individually
	await member.send(welcome_message)

	# Return if member is test user
	if member.id == 162606144722829312:
		return

	# Announce a new member joining in the lobby channel
	welcome_channel = member.guild.get_channel(412327350366240768)
	await welcome_channel.send("Welcome {} to the UWS Game Dev Society!".format(member.mention))

@BOT.event
async def on_member_remove(member):
	"""The 'on_member_remove' event"""

	# Return if member is test user
	if member.id == 162606144722829312:
		return

	farewell_channel = member.guild.get_channel(412327350366240768)
	await farewell_channel.send("User **{}** has left the server. Goodbye!".format(str(member)))

@BOT.event
async def on_message_delete(message):
	"""The 'on_message_deleted' event"""
	if message.id not in BOT.ongoing_polls:
		return

	deleted_poll = BOT.ongoing_polls[message.id]
	deleted_poll.destroy()

	await deleted_poll.initiator.send("Your poll with the question `{}` in {} was deleted. Here are the results.".format(deleted_poll.question, deleted_poll.channel.mention), embed=deleted_poll.embed)

@BOT.event
async def on_raw_reaction_add(payload):
	"""The 'on_raw_reaction_add' event"""

	if payload.user_id == BOT.user.id:
		return

	if payload.channel_id not in [579342050156347392, 579308807453409280]:
		return

	# Fetch reactor Message and Member objects
	message = await BOT.get_channel(payload.channel_id).fetch_message(payload.message_id)
	if payload.user_id in list(map(lambda m: m.id, message.guild.members)):
		member = message.guild.get_member(payload.user_id)
	else:
		member = await message.guild.fetch_member(payload.user_id)

	if any(obj is None for obj in (message, message.guild, member)):
		return

	if message.guild.id != 405451738804518916:
		return

	uws_roles = None
	selected_option = None
	delete_other_roles = False

	# Reaction is for rules confirmation message
	if message.id == 579342665368338441:
		if payload.emoji.name == "👌":
			await member.remove_roles(*list(filter(lambda r: r.name == "Didn't read the Rules", member.guild.roles)))
			await member.send("**==============================================\nThanks for taking the time to read through our rules**. You can now add roles/tags to your profile by heading over to the <#579308807453409280> channel, which is recommended as you'll get access to course-specific channels and allows other members of the server to see what courses you are in.\n\nYou can always review the rules and add/remove any roles by re-visiting <#579308807453409280>.\n\nOnce you've done that, please change your server nickname to your real name or an abbreviation of your name. Make sure to visit <#405737395477020682> to see what events are coming up? Maybe introduce yourself in <#413835267557031937>!")
		return

	# Reaction is for 'Level of Study' Role Selection
	elif message.id == 579331851899109387:
		if any(payload.emoji.name == emoji for emoji in utils.NUMBER_EMOJIS):
			selected_option = utils.NUMBER_EMOJIS.index(payload.emoji.name)
			uws_roles = ["1st Year", "2nd Year", "3rd Year", "4th Year", "PhD", "Graduate"]
			delete_other_roles = True

	# Reaction is for 'Course' Role Selection
	elif message.id == 579332663312121886:
		if any(payload.emoji.name == emoji for emoji in utils.NUMBER_EMOJIS):
			selected_option = utils.NUMBER_EMOJIS.index(payload.emoji.name)
			uws_roles = ["Computer Animation Arts", "Computer Games (Art and Animation)", "Computer Games Development", "Computer Games Technology", "Computer Science", "Digital Art & Design", "Ecology", "Information Technology", "Web and Mobile Development"]
			delete_other_roles = True

	# Reaction is for 'Institution' Role Selection
	elif message.id == 579333086018535424:
		if any(payload.emoji.name == emoji for emoji in utils.NUMBER_EMOJIS):
			selected_option = utils.NUMBER_EMOJIS.index(payload.emoji.name)
			uws_roles = ["University of the West of Scotland", "West College Scotland", "Abertay University", "Glasgow Caledonian University", "Strathclyde University"]

	# Reaction is for 'Other' Role Selection
	elif message.id == 579333442089779204:
		if any(payload.emoji.name == emoji for emoji in utils.NUMBER_EMOJIS):
			selected_option = utils.NUMBER_EMOJIS.index(payload.emoji.name)
			uws_roles = ["Bjarne Development", "HNC", "HND"]

	else:
		return

	if selected_option >= 0 and uws_roles:
		await member.add_roles(*list(filter(lambda r: r.name == uws_roles[selected_option], member.guild.roles)))
		if delete_other_roles:
			roles_to_delete = list(filter(lambda r: r.name in uws_roles and r.name != uws_roles[selected_option], member.roles))
			await member.remove_roles(*roles_to_delete)
			for r in roles_to_delete:
				reaction_to_delete = utils.NUMBER_EMOJIS[uws_roles.index(r.name)]
				await message.remove_reaction(reaction_to_delete, member)

@BOT.event
async def on_raw_reaction_remove(payload):
	"""The 'on_raw_reaction_remove' event"""

	if payload.user_id == BOT.user.id:
		return

	if payload.channel_id not in [579342050156347392, 579308807453409280]:
		return

	# Fetch reactor Message and Member objects
	message = await BOT.get_channel(payload.channel_id).fetch_message(payload.message_id)
	if payload.user_id in list(map(lambda m: m.id, message.guild.members)):
		member = message.guild.get_member(payload.user_id)
	else:
		member = await message.guild.fetch_member(payload.user_id)

	if any(obj is None for obj in (message, message.guild, member)):
		return

	if message.guild.id != 405451738804518916:
		return

	uws_roles = None
	selected_option = None

	# Reaction is for 'Level of Study' Role Selection
	if message.id == 579331851899109387:
		if any(emoji == payload.emoji.name for emoji in utils.NUMBER_EMOJIS):
			selected_option = utils.NUMBER_EMOJIS.index(payload.emoji.name)
			uws_roles = ["1st Year", "2nd Year", "3rd Year", "4th Year", "PhD", "Graduate"]

	# Reaction is for 'Course' Role Selection
	elif message.id == 579332663312121886:
		if any(emoji == payload.emoji.name for emoji in utils.NUMBER_EMOJIS):
			selected_option = utils.NUMBER_EMOJIS.index(payload.emoji.name)
			uws_roles = ["Computer Animation Arts", "Computer Games (Art and Animation)", "Computer Games Development", "Computer Games Technology", "Computer Science", "Digital Art & Design", "Ecology", "Information Technology", "Web and Mobile Development"]

	# Reaction is for 'Institution' Role Selection
	elif message.id == 579333086018535424:
		if any(emoji == payload.emoji.name for emoji in utils.NUMBER_EMOJIS):
			selected_option = utils.NUMBER_EMOJIS.index(payload.emoji.name)
			uws_roles = ["University of the West of Scotland", "West College Scotland", "Abertay University", "Glasgow Caledonian University", "Strathclyde University"]

	# Reaction is for 'Other' Role Selection
	elif message.id == 579333442089779204:
		if any(emoji == payload.emoji.name for emoji in utils.NUMBER_EMOJIS):
			selected_option = utils.NUMBER_EMOJIS.index(payload.emoji.name)
			uws_roles = ["Bjarne Development", "HNC", "HND"]

	else:
		return

	if selected_option >= 0 and uws_roles:
		await member.remove_roles(*list(filter(lambda r: r.name == uws_roles[selected_option], member.guild.roles)))

@BOT.event
async def on_reaction_add(reaction, user):
	"""The 'on_reaction_add' event"""

	if user.id == BOT.user.id:
		return

	if reaction.message.id in BOT.ongoing_polls:
		current_poll = BOT.ongoing_polls[reaction.message.id]

		# If the reaction is the same as any of the existing reactions
		if any(utils.resolve_emoji_from_alphabet(option) == reaction.emoji for option in current_poll.results.keys()):
			# Add the user to the respective result object
			selected_option = utils.resolve_letter_from_emoji(reaction.emoji)
			if user.id not in current_poll.results[selected_option]:
				current_poll.add_vote(selected_option, user)

			# Update the original poll message
			return await BOT.edit_message(current_poll.question_message, embed=current_poll.embed)

@BOT.event
async def on_reaction_remove(reaction, user):
	"""The 'on_reaction_remove' event"""

	if user.id == BOT.user.id:
		return

	if reaction.message.id in BOT.ongoing_polls:
		current_poll = BOT.ongoing_polls[reaction.message.id]
		# If the reaction is the same as any of the existing reactions
		if any(utils.resolve_emoji_from_alphabet(option) == reaction.emoji for option in current_poll.results.keys()):
			# Remove the user from the respective result object
			deselected_option = utils.resolve_letter_from_emoji(reaction.emoji)
			if user.id in current_poll.results[deselected_option]:
				current_poll.remove_vote(deselected_option, user)

			# Update the original poll message
			return await BOT.edit_message(current_poll.question_message, embed=current_poll.embed)

DANK_MESSAGE_MAP = [
	["ayy", "lmao"],
	["rip", "Press F to pay respects\n`F`"],
	["vape", "<:vapenation:423973451716624391>"],
	[["putin", "soviet", "lenin", "stalin"], "<:soviet:423927402637295617>"]
]

@BOT.event
async def on_message(message):
	"""The 'on_message' event handler"""

	# Fetch home_server if not existent
	if not BOT.home_server and message.guild and BOT.home_server_id == message.guild.id:
		BOT.home_server = message.guild

	if message.author.id == BOT.user.id:
		return

	# HANGMAN letter listener
	if message.channel.id in BOT.hangman_games and len(message.content) == 1:
		await BOT.hangman_games[message.channel.id].process_message(message)

	await BOT.process_commands(message)

	# Dank Messages - check per word in message
	if message.content and message.content[0] != BOT.command_prefix:
		split_message = message.content.lower().split(' ')
		prog = re.compile("^<:\D+:(\d+)>$")

		# Capsule this into its own function, code re-use
		async def post_message_or_reaction(val):
			# if key is an emoji string
			emoji_match = prog.match(val)
			if emoji_match:
				if BOT.home_server:
					# Get the emoji ID from REGEXP match
					emoji_id = emoji_match[1]
					emoji = next((e for e in BOT.home_server.emojis if e.id == emoji_id), None)
					if emoji:
						await BOT.add_reaction(message, emoji)
					else:
						await message.channel.send(val)
				else:
					await message.channel.send(val)
			else:
				await message.channel.send(val)

		for dankness in DANK_MESSAGE_MAP:
			key = dankness[0]
			val = dankness[1]

			if isinstance(key, list):
				if any(x in split_message for x in key):
					await post_message_or_reaction(val)
					break
			else:
				if key in split_message:
					await post_message_or_reaction(val)
					break

##### [ BOT COMMANDS ] #####

@BOT.command()
async def evaluate(ctx, *expression):
	"""Evaluate an expression."""
	if ctx.message.author.id not in DEVELOPERS:
		return await ctx.message.channel.send("Wait, you're not a developer. Don't try anything.")

	result = None
	try:
		result = eval(' '.join(expression))
	except Exception as error:
		result = error

	await ctx.message.channel.send(result)

@BOT.command()
async def say(ctx, *something):
	"""Make Bjarne say something."""
	if something:
		await ctx.message.channel.send(" ".join(something))

@BOT.command()
async def version(ctx):
	"""Display Bjarne version info."""
	await ctx.message.channel.send("v{} - {}".format(VERSION_NUMBER, REPOSITORY_URL))

@BOT.command()
async def bjarnequote(ctx):
	"""Get a quote from Bjarne Stroustrup, creator of C++."""
	quotes = [
		'A program that has not been tested does not work.',
		'An organisation that treats its programmers as morons will soon have programmers that are willing and able to act like morons only.',
		'Anybody who comes to you and says he has a perfect language is either naïve or a salesman.',
		'C makes it easy to shoot yourself in the foot; C++ makes it harder, but when you do it blows your whole leg off.',
		'The standard library saves programmers from having to reinvent the wheel.',
		'Certainly not every good program is object-oriented, and not every object-oriented program is good.',
		'Clearly, I reject the view that there is one way that is right for everyone and for every problem.',
		'Thus, the standard library will serve as both a tool and as a teacher.',
		'There are only two kinds of languages: the ones people complain about and the ones nobody uses.',
		'I have always wished for my computer to be as easy to use as my telephone; my wish has come true because I can no longer figure out how to use my telephone.',
		'If you think it\'s simple, then you have misunderstood the problem.',
		'C++ is designed to allow you to express ideas, but if you don\'t have ideas or don\'t have any clue about how to express them, C++ doesn\'t offer much help.',
		'Programming is like sex: It may give some concrete results, but that is not why we do it.',
	]

	choice = rand.choice(quotes)
	
	# so we don't get the same quote twice in a row
	while choice == BOT.lastBjarneChoice:
		choice = rand.choice(quotes)
	
	BOT.lastBjarneChoice = choice

	await ctx.message.channel.send(choice)

@BOT.command()
async def random(ctx, *arg):
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

	await ctx.message.channel.send(random_number)

@BOT.command()
async def dice(ctx):
	"""Roll a dice."""
	await ctx.message.channel.send(rand.randint(1, 6))

# todo: use arguments, should make this command much simpler
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

	await ctx.message.channel.send(z)

@BOT.command()
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
	await ctx.message.channel.send("{} once said: `{}`".format(user, random_message))

@BOT.command()
async def poll(ctx):
	"""Starts a new poll. Usage: !poll -Question -durationInSeconds -Option -Option -Option..."""
	args = ctx.message.content.split("-")
	if len(args) < 2:
		return await ctx.message.channel.send("Please see the command usage for this command: `{}poll -Question -durationInSeconds -Option -Option -Option...`".format(BOT.command_prefix))

	question = args[1]
	duration = args[2]

	duration_float = float(duration)
	if duration_float > 86400:
		return await ctx.message.channel.send("Poll cannot last longer than one day (86400 seconds).")

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


@BOT.command()
async def stats(ctx):
	"""Get server statistics."""
	server = ctx.message.author.guild
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

	await ctx.message.channel.send(embed=embed)


@BOT.command()
async def urban(ctx, query):
	"""Search for a definition from Urban Dictionary."""

	defineURL = 'https://api.urbandictionary.com/v0/define?term='

	response = requests.get(defineURL + query)
	data = response.json()

	firstEntry = data["list"][0]

	definition = firstEntry["definition"]
	example = firstEntry["example"]
	url = firstEntry["permalink"]

	title = "Urban Dictionary: "
	title += query

	embed = discord.Embed(type="rich", colour=utils.generate_random_colour(), timestamp=datetime.now())
	embed.set_author(name=title)
	embed.add_field(name="Definition", value=definition)
	embed.add_field(name="Example", value=example)
	embed.add_field(name="URL", value=url)
	
	await ctx.message.channel.send(embed=embed)


@BOT.command()
async def report(ctx, user):
	"""Report a user anonymously to the society committee. Usage: !report <user> <reason>"""

	reason = ctx.message.content
	reason = reason.replace("!report " + user, "")
	reason = reason[1:]

	message = "A user has made a report against another user.\nThis is against: "
	message += "`" + user + "` for the reason: `"
	message += reason + "`."

	await BOT.get_channel(416255534438547456).send(message)


@BOT.command()
async def eightball(ctx, *arg):
	"""Let the magic 8 ball provide you with wisdom."""
	if arg:
		options = [
			"It is certain. :+1:",
			"It is decidedly so. :+1:",
			"Without a doubt. :+1:",
			"Yes - definitely. :+1:",
			"You may rely on it. :+1:",
			"As I see it, yes. :+1:",
			"Most likely. :+1:",
			"Outlook good. :+1:",
			"Yes. :+1:",
			"Signs point to yes. :+1:",
			"Reply hazy, try again. :shrug:",
			"Ask again later. :shrug:",
			"Better not tell you now. :shrug:",
			"Cannot predict now. :shrug:",
			"Concentrate and ask again. :shrug:",
			"Don't count on it. :shrug:",
			"My reply is no. :-1:",
			"My sources say no. :-1:",
			"Outlook not so good. :-1:",
			"Very doubtful. :-1:"
		]

		choice = rand.choice(options)
		
		# so we don't get the same quote twice in a row
		while choice == BOT.last8BallChoice:
			choice = rand.choice(options)
		
		BOT.last8BallChoice = choice

		await ctx.message.channel.send(choice)
	else:
		await ctx.message.channel.send("You must ask a question!")


@BOT.command()
async def xkcd(ctx):
	"""Get a random XKCD comic."""

	choice = rand.randint(0, 2058)
	url = 'http://xkcd.com/' + str(choice) + '/info.0.json'

	response = requests.get(url)
	data = response.json()

	comic = data["img"]
	await ctx.message.channel.send(comic)


@BOT.command()
async def wiki(ctx):
	"""Get the first few sentences of a Wikipedia page."""

	query = ctx.message.content
	query = query.replace('!wiki', '')

	summary = wikipedia.summary(query, auto_suggest=True, sentences=2)
	page = wikipedia.page(query, auto_suggest=True)

	title = "Wikipedia: "
	title += page.title
	URL = page.url

	embed = discord.Embed(type="rich", colour=utils.generate_random_colour(), timestamp=datetime.now())
	embed.set_author(name=title)
	embed.add_field(name="Summary", value=summary)
	embed.add_field(name="Read More", value=URL)
	
	await ctx.message.channel.send(embed=embed)


@BOT.command()
async def translate(ctx):
	"""Translate a message like '!translate en ja hello' to translate 'hello' from English to Japanese. See https://en.wikipedia.org/wiki/ISO_639-1 for language codes."""

	query = ctx.message.content
	query = query.split()

	fromlang = query[1]
	tolang = query[2]

	message = ""
	for x in query[3:]:
		message += x 
		message += " "

	translator = Translator(to_lang=tolang, from_lang=fromlang)
	translation = translator.translate(message)

	output = "`" + translation + "` <- "
	output += message
	output += " ("
	output += fromlang
	output += "-"
	output += tolang
	output += ")"

	await ctx.message.channel.send(output)


def cryptoChange(val):
	if (val > 0):
		return " :arrow_up:"
	else:
		return " :arrow_down:"

@BOT.command()
async def crypto(ctx, *symbol):
	"""Get info about crypto currencies. '!crypto btc' to get info about one specific currency."""
	coins = Market()
	listings = coins.ticker(start=0, limit=10, convert='GBP')

	t = listings["data"]
	coinOutputs = []
	for x in t:
		coin = listings["data"][x]
		output = ""
		output += coin["name"]
		output += " ("
		output += coin["symbol"]
		output += ") £"
		output += str(round(coin["quotes"]["GBP"]["price"], 3))
		output += "\t1hr % "

		hr = coin["quotes"]["GBP"]["percent_change_1h"]
		output += str(hr)
		output += cryptoChange(hr)

		output += "\t24hr % "

		hr = coin["quotes"]["GBP"]["percent_change_24h"]
		output += str(hr)
		output += cryptoChange(hr)

		output += "\t7d % "

		hr = coin["quotes"]["GBP"]["percent_change_7d"]
		output += str(hr)
		output += cryptoChange(hr)
		output += "\n"
		coinOutputs.append(output)

	output = ""
	for x in coinOutputs:
		output += x

	if symbol:
		for x in coinOutputs:
			if x.find(str(symbol[0].upper())) >= 0:
				output = x

	await ctx.message.channel.send(output)


@BOT.command()
async def convert(ctx, value: float, fromUnit, toUnit):
	"""Convert between quantities.
	Metre to Imperial: feet, mile, yard, inch.
	Temperatures: c, f, k.
	Time: secs, mins, hours, days.
	Currency: Forex symbols e.g USD, GBP etc.
	"""

	message = "Conversion not yet supported. Use !help convert to see supported conversions."
	result = value
	valid = False

	# Metre to Imperial Lengths
	metreToImperial = {
		"feet": 3.281,
		"mile": 1609.344,
		"yard": 1.094,
		"inch": 39.37
	}
	
	if fromUnit == "m" and toUnit in metreToImperial:
		result = value * metreToImperial[toUnit]

	if fromUnit in metreToImperial and toUnit == "m":
		result = value / metreToImperial[fromUnit]

	# Temperatures
	if fromUnit == "c":
		if toUnit == "k":
			result = value + 273.15
		if toUnit == "f":
			result = (value * 9/5) + 32
	if fromUnit == "k":
		if toUnit == "c":
			result = value - 273.15
		if toUnit == "f":
			result = (value - 273.15) * (9/5) + 32
	if fromUnit == "f":
		if toUnit == "c":
			result = (value - 32) * 5/9
		if toUnit == "k":
			result = (value + -32) * (5/9) + 273.15

	# Time
	if fromUnit == "secs":
		if toUnit == "mins":
			result = value / 60
		if toUnit == "hours":
			result = value / 3600
		if toUnit == "days":
			result = value / 86400

	if fromUnit == "mins":
		if toUnit == "secs":
			result = value * 60
		if toUnit == "hours":
			result = value / 60
		if toUnit == "days":
			result = value / 1440

	if fromUnit == "hours":
		if toUnit == "secs":
			result = value * 3600
		if toUnit == "mins":
			result = value * 60
		if toUnit == "days":
			result = value / 24

	if fromUnit == "days":
		if toUnit == "secs":
			result = value * 86400
		if toUnit == "mins":
			result = value * 1440
		if toUnit == "hours":
			result = value * 24

	# Currency
	currency = False
	c = CurrencyRates()
	try: 
		currency = True
		result = c.convert(fromUnit.upper(), toUnit.upper(), value)
		message = "Conversion: " + str(value)
		message += " "
		message += fromUnit
		message += " equals "
		message += str(result)
		message += " "
		message += toUnit
	except:
		currency = False
		pass

	if result != value and currency == False:
		message = "Conversion: " + str(value)
		message += " "
		message += fromUnit
		message += " equals "
		message += str(result)
		message += " "
		message += toUnit

	await ctx.message.channel.send(message)


@BOT.command()
async def modules(ctx, course):
	"""Display course module ratings. Options are: CGT, CGD."""

	message = "Module ratings for: `"
	message += course.upper()
	message += "`\n"

	course = course.lower()

	with open('courseratings.json') as f:
		data = json.load(f)
		for x in data[course].items():
			message += x[0]
			message += ":\t `"
			message += str(x[1][0])
			message += "` ("
			message += str(len(x[1][1])) + " votes)"
			message += "\n"

	await ctx.message.channel.send(message)



@BOT.command()
async def ratemodule(ctx, *arg):
	"""Rate a course module at UWS. Specify command like '!ratecourse course rating module' e.g: '!ratecourse cgt 5 intro to programming'"""

	message = ""

	course = arg[0]
	rating = float(arg[1])
	module = ""
	for x in arg[2:]:
		module += x
		module += " "
	module = module[:-1]
	
	print(course)
	print(rating)
	print(module)

	if rating < 1 or rating > 5:
		message = "Rating must be between 1 and 5, inclusive."
	else:
		data = ""
		with open('courseratings.json') as f:
			data = json.load(f)

			for x in data[course].items():
				if module == x[0].lower():
					x[1][1].append(rating)
					print(x[1][1])

					avg = 0
					for y in x[1][1]:
						avg += y
					avg = round(avg / len(x[1][1]), 2)
					x[1][0] = avg
					message = "New rating for `" 
					message += course.upper()
					message += " - "
					message += x[0] 
					message += "` is `"
					message += str(avg)
					message += "`."

			with open('courseratings.json', 'w') as outfile:
				json.dump(data, outfile)


	await ctx.message.channel.send(message)


@BOT.command()
async def ask(ctx):
	"""Submit a question to Wolfram Alpha."""

	query = ctx.message.content
	query = query[4:]

	client = wolframalpha.Client(WOLFRAM_KEY)

	res = client.query(query)

	query = next(res.results).text

	await ctx.message.channel.send(query)


##### [ BOT LOGIN ] #####

BOT.run(BOT_TOKEN)
