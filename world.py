"""
Created 24 Jul 17
Modified 11 Aug 17

@author = Bharath Mohan | MrMonday
"""
import math
import discord
from discord.ext import commands
import config
import database
from random import randint

class World:
    """The World cog represents actions taken by or in the world - monster actions, random chance, and any miscellaneous rolls not covered under
       character stats (e.g. simple luck rolls) go through here. Contains the roll(), advantage(), and disadvantage() functions. """
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def roll(self, ctx, dice: str):
        """Format: izd_roll NdM
                where N is the number of dice to roll and M is the number of sides on the dice

           Handles miscellaneous rolls. """
        try:
            rolls, sides = map(int, dice.split('d'))
        except:
            await ctx.send(content='Improper format; dice must be in NdM format')
            return
        results = [randint(1, sides) for i in range(0, rolls)]
        total = sum(results)
        message = ctx.author.mention
        message += ': '
        message += ' + '.join(map(str, results))
        message += ' = {}'.format(total)
        await ctx.send(content=message)
        return

    @commands.command()
    @commands.guild_only()
    async def rollsix(self, ctx):
        """Format: izd_rollsix

           Was a test command left in for posterity's sake. No input, rolls a single d6. """
        result = randint(1, 6)
        message = '{}: 1d6 = {}'.format(ctx.author.mention, result)
        await ctx.send(content=message)
        return

    @commands.command()
    @commands.guild_only()
    async def advantage(self, ctx, dice: str, keep: int):
        """Format: izd_advantage NdM K
                where N is the number of dice to roll, M is the number of sides on the dice,
                and K is the number of high rolls to keep

           Rolls dice with advantage. """
        try:
            rolls, sides = map(int, dice.split('d'))
        except:
            await ctx.send(content='Improper command format. Proper command format is izd_advantage NdM K, where K is the number of rolls to keep')
            return
        results = sorted([randint(1, sides) for i in range(0, rolls)],reverse=True)
        kept = results[:keep]
        discarded = results[keep:]
        total = sum(kept)
        message = ctx.author.mention
        message += ': ~~'
        message += ' + '.join(map(str, discarded))
        message += ' +~~ '
        message += ' + '.join(map(str, kept))
        message += ' = {}'.format(total)
        await ctx.send(content=message)
        return

    @commands.command()
    @commands.guild_only()
    async def disadvantage(self, ctx, dice: str, keep: int):
        """Format: izd_disadvantage NdM K
                where N is the number of dice to roll, M is the number of sides on the dice,
                and K is the number of low rolls to keep

           Rolls dice with disadvantage. """
        try:
            rolls, sides = map(int, dice.split('d'))
        except:
            await ctx.send(content='Improper command format. Proper command format is izd_disadvantage NdM K, where K is the number of rolls to keep')
            return
        results = sorted([randint(1, sides) for i in range(0, rolls)])
        kept = results[:keep]
        discarded = results[keep:]
        total = sum(kept)
        message = ctx.author.mention
        message += ': ~~'
        message += ' + '.join(map(str, discarded))
        message += ' +~~ '
        message += ' + '.join(map(str, kept))
        message += ' = {}'.format(total)
        await ctx.send(content=message)
        return


def setup(bot):
    bot.add_cog(World(bot))
