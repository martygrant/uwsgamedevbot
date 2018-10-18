"""This module implements the role command"""

import asyncio
import discord
from discord.ext import commands
import utilities as utils

ROLE_CATEGORIES = {
    "Course Levels": [
        "1st Year",
        "2nd Year",
        "3rd Year",
        "4th Year",
        "Graduate",
        "PhD Student"
    ],
    "Courses": [
        "Computer Animation Arts",
        "Computer Games (Art and Animation)",
        "Computer Games Development",
        "Computer Games Technology",
        "Computer Science",
        "Digital Art & Design",
        "Ecology",
        "Information Technology",
        "Web and Mobile Development"
    ],
    "Institutions": [
        "Abertay University",
        "Glasgow Caledonian University",
        "Strathclyde University",
        "University of the West of Scotland",
        "West College Scotland"
    ],
    "Others": [
        "Bjarne Development",
        "HNC",
        "HND"
    ]
}

class Roles:
    """The `Role` class that declares methods to add users to specified roles"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def roles(self, ctx):
        """Display a `MessageEmbed` with available Reactions that add respective roles to the user"""
        category = await self.collect_category(ctx)
        roles_to_add = await self.collect_roles(category["category"], category["message"], ctx)
        # Differentiate the two lists (user roles and selected roles)
        roles_to_add = list(set(roles_to_add) - set(ctx.message.author.roles))

        result_embed = discord.Embed(type="rich", colour=utils.generate_random_colour())
        result_embed.set_author(name="Added {} Roles".format(len(roles_to_add)))
        if roles_to_add:
            await self.bot.add_roles(ctx.message.author, *roles_to_add)
            result_embed.add_field(name="You have been granted the following roles:", value="`{}`".format("`, `".join(list(map(lambda r: r.name, roles_to_add)))))
        else:
            result_embed.description = "You were not applicable for or already have some of the roles you picked."

        await self.bot.clear_reactions(category["message"])
        await self.bot.edit_message(category["message"], embed=result_embed)

    async def collect_category(self, ctx):
        """Presents an Embed and finds the category from the Reaction the user provided"""
        embed = discord.Embed(type="rich", colour=utils.generate_random_colour())
        embed.set_author(name="Role Categories")
        embed.description = "Click on an emoji at the bottom of this panel that corresponds with the category of roles you want to assign yourself. Another panel will pop up that will ask you for the specific roles."

        current_emoji_index = 0
        for cat, roles_array in ROLE_CATEGORIES.items():
            embed.add_field(name="{} {}".format(utils.resolve_emoji_from_alphabet(utils.ALPHABET[current_emoji_index]), cat), value="`{}`".format("`\n`".join(roles_array)))
            current_emoji_index += 1

        reaction_message = await self.bot.send_message(ctx.message.channel, embed=embed)
        for i, cat in enumerate(list(ROLE_CATEGORIES)):
            await self.bot.add_reaction(reaction_message, utils.resolve_emoji_from_alphabet(utils.ALPHABET[i]))

        def check(reaction, user):
            if user.id != ctx.message.author.id:
                return False

            letter = utils.resolve_letter_from_emoji(reaction.emoji)
            for i in range(0, len(ROLE_CATEGORIES)):
                if letter == utils.ALPHABET[i]:
                    return True

            return False

        res = await self.bot.wait_for_reaction(message=reaction_message, check=check, timeout=30)

        index = utils.ALPHABET.index(utils.resolve_letter_from_emoji(res.reaction.emoji))
        return {
            "category": list(ROLE_CATEGORIES)[index],
            "message": reaction_message
        }

    async def handle_years(self, selected_year, member):
        """Removes the previous year role, including graduate, if existing"""
        year_names = ROLE_CATEGORIES[list(ROLE_CATEGORIES)[0]][:5]
        if selected_year.name not in year_names:
            return

        previous_role = next((r for r in member.roles if r.id != selected_year.id and r.name in year_names), None)
        if not previous_role:
            return

        await self.bot.remove_roles(member, previous_role)

    async def collect_roles(self, category, reaction_message, ctx):
        """Presents another Embed and gives the user the roles they selected"""
        embed = discord.Embed(type="rich", colour=utils.generate_random_colour())
        embed.set_author(name="Select roles from {}".format(category))
        embed.description = "Click on the emojis at the bottom of this panel that correspond with the roles you want added to your profile. The panel will close itself in 30 seconds, allowing you to select as many roles as you want."
        if category is list(ROLE_CATEGORIES)[0]:
            embed.set_footer(text="Please select one role.")
        else:
            embed.set_footer(text="You have 30 seconds to choose your roles")

        roles_list = []
        for i, r in enumerate(ROLE_CATEGORIES[category]):
            roles_list.append("{} {}".format(utils.resolve_emoji_from_alphabet(utils.ALPHABET[i]), r))

        embed.add_field(name="Available Roles", value="\n".join(roles_list))

        await self.bot.clear_reactions(reaction_message)
        await self.bot.edit_message(reaction_message, embed=embed)

        for i, r in enumerate(ROLE_CATEGORIES[category]):
            await self.bot.add_reaction(reaction_message, utils.resolve_emoji_from_alphabet(utils.ALPHABET[i]))

        # Allow only one role for Years / Course Levels
        if category is list(ROLE_CATEGORIES)[0]:
            def check(reaction, user):
                if user.id != ctx.message.author.id:
                    return False

                letter = utils.resolve_letter_from_emoji(reaction.emoji)
                for i in range(0, len(ROLE_CATEGORIES[list(ROLE_CATEGORIES)[0]])):
                    if letter == utils.ALPHABET[i]:
                        return True

                return False

            res = await self.bot.wait_for_reaction(message=reaction_message, check=check, timeout=30)

            index = utils.ALPHABET.index(utils.resolve_letter_from_emoji(res.reaction.emoji))
            role_to_add = ROLE_CATEGORIES[list(ROLE_CATEGORIES)[0]][index]
            role_to_add = next((r for r in ctx.message.server.roles if r.name == role_to_add), None)

            await self.handle_years(role_to_add, ctx.message.author)
            return [role_to_add]
        else:
            await self.bot.wait_until_ready()
            await asyncio.sleep(30)

            # Update the message that collects the reactions so we can access `.reactions`
            reaction_message = await self.bot.get_message(reaction_message.channel, reaction_message.id)

            selected_emojis = reaction_message.reactions.copy()
            reaction_users = []
            for i, reaction in enumerate(reaction_message.reactions):
                reaction_users.append(await self.bot.get_reaction_users(reaction))

            for i, reaction in enumerate(reaction_message.reactions):
                id_list = list(map(lambda x: x.id, reaction_users[i]))

                if ctx.message.author.id not in id_list:
                    selected_emojis.remove(reaction)

            roles_selected = list(map(lambda r: utils.ALPHABET.index(utils.resolve_letter_from_emoji(r.emoji)), selected_emojis))
            roles_to_add = list(map(lambda i: ROLE_CATEGORIES[category][i], roles_selected))
            for i, role_string in enumerate(roles_to_add):
                roles_to_add[i] = next((r for r in ctx.message.server.roles if r.name == role_string), None)

            # Remove all potential `None` from the list
            roles_to_add = [x for x in roles_to_add if x is not None]
            return roles_to_add

def setup(bot):
    """Method that loads this module into the client"""
    bot.add_cog(Roles(bot))
    print("Roles module loaded.")
