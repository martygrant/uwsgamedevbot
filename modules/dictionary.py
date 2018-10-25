"""Look up definitions online using this Oxford Dictionary-powered command"""

import os
from datetime import datetime
from urllib import parse
import requests
import json
import discord
from discord.ext import commands
import utilities as utils

OXFORD_IMAGE_URL = "https://developer.oxforddictionaries.com/images/PBO_black.png"
OXFORD_API_URL = "https://developer.oxforddictionaries.com/"
OXFORD_BASE_SEARCH = "https://en.oxforddictionaries.com/definition/"

class Dictionary:
    def __init__(self, bot):
        self.bot = bot

        self.app_id = os.getenv('oxford-appid')
        self.app_key = os.getenv('oxford-key')

        self.base_address = "https://od-api.oxforddictionaries.com/api/v1"
        self.endpoints = {
            "definitions": "/entries/en",
            "lemmatron": "/inflections/en"
        }
        self.default_headers = {
            "app_id": self.app_id,
            "app_key": self.app_key
        }

    def _set_error(self, *, embed, res, ctx):
        embed.set_author(name="Error {}".format(res.status_code), icon_url=ctx.message.author.avatar_url)
        embed.colour = utils.COLOUR_ERROR
        embed.timestamp = datetime.now()

        if str(res.status_code)[0] == '4':
            if res.status_code == 404:
                embed.description = "No headword could be found for `{}`.".format(' '.join(ctx.message.content.split(' ')[1:]))
            elif res.status_code == 414:
                embed.description = "The word you searched for is too long. Please keep your search to a maximum of 128 characters."
            else:
                embed.description = "Something went wrong while communicating with the Dictionary services. Please report this to a developer."
        elif str(res.status_code)[0] == '5':
            embed.description = "The Dictionary Services are experiencing technical issues. Try again later."

        return embed

    async def run_lemmatron(self, ctx):
        word = parse.quote('_'.join(ctx.message.content.split(' ')[1:]).lower())
        url = "{}{}/{}".format(self.base_address, self.endpoints["lemmatron"], word)

        res = requests.get(url, headers=self.default_headers)

        embed = discord.Embed(colour=utils.generate_random_colour())
        embed.timestamp = ctx.message.timestamp
        embed.set_author(name="Inflections for {}".format(word), icon_url=ctx.message.author.avatar_url)
        embed.set_thumbnail(url=OXFORD_IMAGE_URL)
        embed.set_footer(text="Powered by the Oxford Dictionary API")

        if res.status_code != 200:
            embed = self._set_error(embed=embed, res=res, ctx=ctx)
            await self.bot.send_message(ctx.message.channel.id, embed=embed)
            return 1

        result_words = json.loads(res.text)["results"]
        headword = result_words[0]["word"]

        user_choice = None
        if len(result_words) > 1:
            embed.description = "{}, I have found multiple headwords for your inflection. Select your word now.".format(ctx.message.author.mention)
            choices = list(map(lambda x: {
                "name": x.word,
                "value": "Inflections: `" + ("`, `".join(list(map(lambda y: y["inflectionOf"][0]["text"], result_words["lexicalEntries"])))) + "`"
            }, result_words))

            user_choice = await utils.collect_choice_from_embed(ctx.message.channel, choices=choices, bot=self.bot, embed=embed, target_user=ctx.message.author)
            headword = result_words[user_choice["choice"]]["word"]

        return {
            "headword": headword,
            "message": user_choice["message"] if user_choice else None
        }

    async def fetch_definitions(self, ctx, word):
        url = "{}{}/{}".format(self.base_address, self.endpoints["definitions"], word)
        res = requests.get(url, headers=self.default_headers)

        if res.status_code != 200:
            embed = discord.Embed()
            embed.timestamp = datetime.now()
            embed.set_thumbnail(url=OXFORD_IMAGE_URL)
            embed.set_footer(text="Powered by the Oxford Dictionary API")

            embed = self._set_error(embed=embed, res=res, ctx=ctx)
            await self.bot.send_message(ctx.message.channel.id, embed=embed)
            return 1

        definitions = json.loads(res.text)["results"][0]["lexicalEntries"]
        return definitions

    @commands.command(pass_context=True)
    async def define(self, ctx):
        """Get the definition of a specified word, like '!define computer'."""
        await self.bot.send_typing(ctx.message.channel)

        if len(ctx.message.content.split(' ')) == 1:
            return await self.bot.send_message(ctx.message.channel, "See how to use this command by running `{}help define`".format(ctx.prefix))

        user_word = ' '.join(ctx.message.content.split(' ')[1:])
        embed = discord.Embed(colour=utils.generate_random_colour())
        embed.timestamp = datetime.now()
        embed.set_author(name="Definitions for {}".format(user_word), url=OXFORD_BASE_SEARCH + user_word, icon_url=ctx.message.author.avatar_url)
        embed.set_thumbnail(url=OXFORD_IMAGE_URL)
        embed.set_footer(text="Powered by the Oxford Dictionary API")

        lemmatron_data = await self.run_lemmatron(ctx)
        if isinstance(lemmatron_data, int) and lemmatron_data > 0:
            return

        definitions = await self.fetch_definitions(ctx, parse.quote('_'.join(lemmatron_data["headword"].split(' ')).lower()))
        if isinstance(definitions, int) and definitions > 0:
            return

        for word in definitions:
            senses = []
            for entry in word["entries"]:
                for i, sense in enumerate(entry["senses"]):
                    if "definitions" not in sense:
                        continue

                    definition = "\n{} `{}`".format(utils.resolve_emoji_from_alphabet(utils.ALPHABET[i]), sense["definitions"][0])
                    examples = list(map(lambda x: x["text"], sense["examples"] if "examples" in sense else []))

                    senses.append({
                        "definition": definition,
                        "examples": examples
                    })

            definition_text = ""
            for sense in senses:
                definition_text += "\n{}{}{}{}".format(sense["definition"], "\n• *" if sense["examples"] else "", "*\n• *".join(sense["examples"]), '*' if sense["examples"] else "")

            name = "{} ({})".format(word["text"], word["lexicalCategory"])
            embed.add_field(name=name, value=definition_text, inline=False)

        if lemmatron_data["message"]:
            await self.bot.edit_message(lemmatron_data["message"], embed=embed)
        else:
            await self.bot.send_message(ctx.message.channel, embed=embed)

def setup(bot):
    """Method that loads this module into the client"""
    bot.add_cog(Dictionary(bot))
    print("Dictionary module loaded.")
