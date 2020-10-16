import discord
from discord.ext import commands

class GameDevDictionary(commands.Cog):
    """The `GameDevDictionary` class"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def tutorials(self, ctx):
        """Command Description"""
        return await self.bot.send_message(ctx.message.channel, "See how to use this command by running `{}help tutorials`".format(ctx.prefix))

    @commands.command(pass_context=True, name='DictionaryTest')
    async def test(self, ctx):
        await ctx.send('Dictionary Test Working')

    @commands.command(pass_context=True, name='Info')
    async def DInfo(self, ctx):
        await ctx.send('Game Development Dictionary \n'
                       'this module allows you to put in terms related to game dev and get more information and resources \n'
                       'for example !Unity would pull up links related to Unity \n '
                       'current terms in the dictionary\n'
                       '`!General`\n'
                       '`!Unity`\n'
                       '`!Unreal`\n'
                       '`!Godot`\n'
                       '`!Art`\n'
                       '`!Programming`\n'
                       '`!Audio`\n'
                       '`!shaders`')

    @commands.command(pass_context=True, name='General')
    async def GeneralInfo(self, ctx):
        await ctx.send('General game Development Resources \n' 
                       'Game Dev Data base| <https://gamedevelop.io/resources>\n'
                       ' GDC Vault|<https://www.gdcvault.com/free>\n'
                       ' reddit | <https://www.reddit.com/r/gamedev/> \n'
                       'learn anything general resource| <https://learn-anything.xyz> \n'
                       'more resources| <https://www.gamedev.net/> \n'
                       'industry news | <https://www.gamesindustry.biz/> \n'
                       'news software/tools | <https://gamefromscratch.com/>')


    @commands.command(pass_context=True, name='Unity')
    async def Unity(self,ctx):
        await ctx.send('Unity \n'
                        'Unity learning website| <https://learn.unity.com/> \n'
                        'unity documentation| <https://docs.unity3d.com/Manual/index.html> \n'
                        'unity forums | <https://answers.unity.com/index.html> \n'
                        'unity reddit | <https://www.reddit.com/r/Unity3D/>')


    @commands.command(pass_context=True, name='Unreal')
    async def Unreal(self, ctx):
        await ctx.send('Unreal \n '
                       'Unreal learning site | <https://www.unrealengine.com/en-US/onlinelearning-courses?sessionInvalidated=true> \n'
                       'Unreal Engine Docuumentation | <https://docs.unrealengine.com/en-US/index.html> \n'
                       'Unreal engine Reddit | <https://www.reddit.com/r/unrealengine/> \n'
                       'Community wiki | <https://www.ue4community.wiki/> \n'
                       'different tutorial | <https://www.raywenderlich.com/unreal-engine>')

    @commands.command(pass_context=True, name='Godot')
    async def Godot(self, ctx):
        await ctx.send('Godot \n'
                       'godot website | <https://godotengine.org/> \n'
                       'Godot documentation| <https://docs.godotengine.org/en/stable/index.html> \n'
                       'Reddit Godot| <https://www.reddit.com/r/godot/>')


    @commands.command(pass_context=True, name='Art')
    async def Art(self, ctx):
        await ctx.send('General game Art /n'
                       'massive art resource page| <https://www.notion.so/The-Empire-Command-3a3bf979f8df4ca2a49315bc0dc31f9f> \n'
                       ' artstation learning| <https://www.artstation.com/learning> \n'
                       'Art news site| <https://80.lv/> \n'
                       'game art forum| <https://polycount.com/> \n'
                       'Blender resources mixed of resources| <https://www.blendernation.com/> \n'
                       'flipped normals| <https://flippednormals.com/> \n'
                       'collab drawing program| <https://magmastudio.io/>')


    @commands.command(pass_context=True, name='Programming')
    async def Programming(self, ctx):
        await ctx.send('General programming resources \n'
                       'Programming patterns| <http://gameprogrammingpatterns.com/contents.html> \n'
                       'Infallible Code | <https://www.youtube.com/channel/UCTjnCCcuIbrprhOiaDJxxHA> \n'
                       'General programming resources books and some general game dev books| <https://eliasdaler.github.io/programming-and-gamedev-resources/> \n'
                       'Lean C# by building a rpg| <https://scottlilly.com/learn-c-by-building-a-simple-rpg-index/> \n'
                       'c# book| <https://www.amazon.co.uk/Beginning-Programming-Premier-Development-Paperback/dp/1592005179> \n'
                       'Beginning C++ Through Game Programming by Michael Dawson| <https://www.amazon.com/gp/product/B011T6YIGK/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B011T6YIGK&linkCode=as2&tag=compubookstut-20&linkId=4457fe1663d015ec863b587857a5920d>')


    @commands.command(pass_context=True, name='Audio')
    async def Audio(self, ctx):
        await ctx.send('Audio resources \n'
                       '| <https://www.reddit.com/r/GameAudio/wiki/resources?utm_source=reddit&utm_medium=usertext&utm_name=GameAudio&utm_content=t5_2scqj#/button/c/purple/> \n'
                       '| <https://www.gamedevmarket.net/category/audio/sound-fx/> \n'
                       '| <https://www.gamasutra.com/blogs/PavelShylenok/20190506/342095/Designing_Sounds_for_a_Game.php> \n'
                       '| <https://www.gamedesigning.org/learn/video-game-sound/>')


    @commands.command(pass_context=True, name='Shaders')
    async def Shaders(self, ctx):
        await ctx.send('Shaders resources \n'
                       'book of shaders| <http://thebookofshaders.com> \n'
                       'Shader resource archive| <http://halisavakis.com/archive/> \n'
                       'shaderlab | <http://www.shaderslab.com/>')

def setup(bot):
    """Method that loads this module into the client"""
    bot.add_cog(GameDevDictionary(bot))
    print("GameDevDictionary module loaded.")
