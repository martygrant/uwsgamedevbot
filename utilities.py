"""This file contains some utility functions"""
import random as rand
import discord

COLOUR_SUCCESS = 0x4BB543
COLOUR_ERROR = 0xB33A3A

ALPHABET = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
            'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
NUMBER_EMOJIS = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣"]
def resolve_emoji_from_alphabet(letter):
    """Returns the unicode emoji representation of a lowercase letter"""
    return chr(ord(letter) + 127365)

def resolve_letter_from_emoji(emoji):
    """Returns the lowercase character representation of a letter emoji"""
    return chr(ord(emoji) - 127365)

def generate_random_colour():
    """Generates a random colour decimal"""
    letters = "0123456789ABCDEF"
    colour_string = ""
    for i in range(6):
        colour_string += rand.choice(letters)
    return int(colour_string, 16)

async def collect_choice_from_embed(message, choices, *, bot, embed, target_user=None):
    count = len(embed.fields)
    letter_count = 0
    for i, choice in enumerate(choices):
        if count == 25 or letter_count > 1900:
            break

        emoji = resolve_emoji_from_alphabet(ALPHABET[i])
        embed.add_field(name="{} {}".format(emoji, choice["name"]), value=choice["value"])
        letter_count += len("{} {}".format(emoji, choice["name"])) + len(choice["value"])

    reaction_message = message
    if isinstance(message, discord.Channel):
        reaction_message = await bot.send_message(message, embed=embed)
    else:
        await bot.edit_message(reaction_message, embed=embed)

    if reaction_message.reactions:
        await bot.clear_reactions(reaction_message)

    for i in range(0, len(choices)):
        await bot.add_reaction(reaction_message, resolve_emoji_from_alphabet(ALPHABET[i]))

    def check(user, reaction):
        if target_user and isinstance(target_user, discord.User):
            if user.id != target_user.id:
                return False
        if resolve_letter_from_emoji(reaction.emoji) in ALPHABET[:len(choices)]:
            return True
        return False
    res = await bot.wait_for_reaction(reaction_message, check=check, timeout=60)
    await bot.clear_reactions(reaction_message)

    return {
        "message": reaction_message,
        "choice": ALPHABET.index(resolve_letter_from_emoji(res.reaction.emoji))
    }
