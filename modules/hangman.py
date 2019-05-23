"""This module implements the hangman command"""

import random
import discord
from discord.ext import commands
import utilities as utils

# Kind courtesy of https://gist.github.com/chrishorton/8510732aa9a80a03c829b09f12e20d9c
HANGMAN_STAGES = ['''```
                  +---+
                  |   |
                      |
                      |
                      |
                      |
                =========```''', '''```
                  +---+
                  |   |
                  O   |
                      |
                      |
                      |
                =========```''', '''```
                  +---+
                  |   |
                  O   |
                  |   |
                      |
                      |
                =========```''', '''```
                  +---+
                  |   |
                  O   |
                 /|   |
                      |
                      |
                =========```''', '''```
                  +---+
                  |   |
                  O   |
                 /|\\  |
                      |
                      |
                =========```''', '''```
                  +---+
                  |   |
                  O   |
                 /|\\  |
                 /    |
                      |
                =========```''', '''```
                  +---+
                  |   |
                  O   |
                 /|\\  |
                 / \\  |
                      |
                =========```''']
HANGMAN_WORDS = ('ant baboon badger bat bear beaver camel cat clam cobra cougar '
                 'coyote crow deer dog donkey duck eagle ferret fox frog goat '
                 'goose hawk lion lizard llama mole monkey moose mouse mule newt '
                 'otter owl panda parrot pigeon python rabbit ram rat raven '
                 'rhino salmon seal shark sheep skunk sloth snake spider '
                 'stork swan tiger toad trout turkey turtle weasel whale wolf '
                 'wombat zebra ').split()

def blank_word(*, word, guessed):
    """Blanks out a word with '_' for un-guessed letters"""
    final = ""
    for letter in word:
        if letter in guessed:
            final += letter + " "
        else:
            final += "_ "

    return final

class HangmanGame:
    """The class that manages a game of 'Hangman'"""
    def __init__(self, ctx, *, bot):
        self.bot = bot
        self.channel = ctx.message.channel
        self.message = None
        self.word = random.choice(HANGMAN_WORDS).upper()
        self.stage = 0
        self.guessed = []

        # Set up the embed template
        self.embed = discord.Embed(colour=utils.generate_random_colour(), timestamp=ctx.message.created_at)
        self.embed.description = "It's Hangman! Guess the word procedurally by typing in a letter - but beware! The more incorrect letters guessed, the more complete the hangman will become. Once the hangman is fully complete, everyone loses."
        self.embed.set_author(name="Hangman")
        self.embed.set_footer(text="Initiated by {}".format(str(ctx.message.author)))
        self.embed.add_field(name="GUESS THE WORD", value="`{}`".format(blank_word(word=self.word, guessed=self.guessed)))
        self.embed.add_field(name="Most recent Guess", value="---")
        self.embed.add_field(name="Guessed Letters", value="---", inline=False)
        self.embed.add_field(name="Hangman", value=HANGMAN_STAGES[self.stage], inline=False)

    async def start(self):
        """Starts the game"""
        self.message = await self.channel.send(embed=self.embed)

    async def process_message(self, msg):
        """Processes the message and declares the main logic flow"""
        limb_add = True
        if msg.content.upper() in self.word or msg.content.upper() in self.guessed:
            limb_add = False

        if msg.content.upper() not in self.guessed:
            self.guessed.append(msg.content.upper())

        await self.update_message(msg, limb_add)
        await msg.delete()

    async def update_message(self, user_message, limb_add):
        """Updates a message (with hangman image) in response to a received letter"""

        # Update the game stage
        if limb_add:
            self.stage += 1

        correct_letters = [x for x in self.guessed if x in self.word]
        # Finish the game if the word was guessed or hangman is ded
        if len(correct_letters) == len(self.word) or self.stage == len(HANGMAN_STAGES) - 1:
            return await self.finish(user_message, len(correct_letters) == len(self.word))

        # Update the embed to match the current game state
        embed = self.embed
        embed.clear_fields()

        embed.add_field(name="GUESS THE WORD", value="**`{}`**".format(blank_word(word=self.word, guessed=self.guessed)))
        embed.add_field(name="Most recent Guess", value="{}: **{}**".format(user_message.author.mention, user_message.content.upper()))

        embed.add_field(name="Guessed Letters", value="**`{}`**".format("`**, **`".join(self.guessed)), inline=False)
        embed.add_field(name="Hangman", value=HANGMAN_STAGES[self.stage], inline=False)

        await self.message.edit(embed=embed)

    async def finish(self, user_message, win):
        """Finishes the game and deletes the instance"""
        embed = self.embed
        embed.clear_fields()

        if win:
            embed.description = "Congratulations, you collectively correctly guessed the word!"
            embed.colour = 0x4BB543
        else:
            embed.description = "You lost the game."
            embed.colour = 0xB33A3A

        embed.set_author(name="Hangman - Game Over")
        embed.add_field(name="THE WORD WAS", value="**`{}`**".format("".join(list(map(lambda x: x + " ", self.word.upper())))))
        embed.add_field(name="Final Guess", value="{}: **{}**".format(user_message.author.mention, user_message.content.upper()))

        embed.add_field(name="Guessed Letters", value="**`{}`**".format("`**, **`".join(self.guessed)), inline=False)
        embed.add_field(name="Hangman", value=HANGMAN_STAGES[self.stage])

        del self.bot.hangman_games[self.channel.id]
        await self.message.edit(embed=embed)

class Hangman(commands.Cog):
    """The `Hangman` class"""
    def __init__(self, bot):
        self.bot = bot
        # Stores a dict of channel IDs paired with their Game Instance
        self.bot.hangman_games = {}

    @commands.command(pass_context=True)
    async def hangman(self, ctx):
        """Let's play a game of hangman!"""
        self.bot.hangman_games[ctx.message.channel.id] = HangmanGame(ctx, bot=self.bot)
        await self.bot.hangman_games[ctx.message.channel.id].start()

def setup(bot):
    """Method that loads this module into the client"""
    bot.add_cog(Hangman(bot))
    print("Hangman module loaded.")
