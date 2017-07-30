"""
@author = Bharath Mohan | MrMonday
"""
import math
import discord
from discord.ext import commands
import config
import database
from random import randint

class Util:
    """This cog covers miscellaneous bot functions not directly related to the role-play experience - roll manuals, bot information, etc. """
    def __init__(self, bot):
        self.bot = bot

    # @commands.group()
    # async def help(self, ctx):
    #     if ctx.invoked_subcommand is None:
    #         message = 'The great IzduBot offers many features. Use izd!help list for a full list, or izd!help [command] for more information on a specific command.'
    #         await ctx.send(content=message)

    # @help.command()
    # async def list(self, ctx):
    #     cmd_list = ["izd!roll", "izd!advantage", "izd!disadvantage", "izd!create", "izd!abilitycheck", "izd!skillcheck", "izd!initiativeroll", "izd!attackroll", "izd!abilitysave", "izd!spellattack", "izd!spellsavedc", "izd!attackmade", "izd!healcharacter", "izd!gainsaveprof", "izd!gainskillprof", "izd!changeac", "izd!gaintemphp", "izd!changealign"]
    #     message = " ".join(cmd_list)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        print("Shutdown signal received, going down...")
        await ctx.send("Shutting down... ")
        await self.bot.close()

    @commands.command()
    async def temp(self, ctx):
        return


def setup(bot):
    bot.add_cog(Util(bot))
