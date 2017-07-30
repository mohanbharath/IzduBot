"""
@author = Bharath Mohan | MrMonday
"""
import discord
from discord.ext import commands
import config
import database

STARTUP_EXTENSIONS = ['world', 'character', 'util']

class IzduBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('izd!'), description="temp")
        self.bot_token = config.token
        #self.api_key = "temp"

        for ext in STARTUP_EXTENSIONS:
            try:
                self.load_extension(ext)
            except Exception as exception:
                print("FAILED TO LOAD EXTENSION: {ext}")
                traceback.print_exc()

    # async def on_message(self, message):
    #     pass

    async def on_ready(self):
        game = "with your fate"
        await self.change_presence(game=discord.Game(name=game))
        print('On ready triggered - bot logged in as: {0} (ID: {0.id})'.format(self.user))
        print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')

    # async def on_message(self, message):
    #     if message.author.bot: # No need to process bot messages - that might end badly
    #         return
    #     await self.process_commands(message)

    # async def process_commands(self, message):
    #     ctx = await self.get_context(message, cls=context.Context)
    #
    #     if ctx.command is None:
    #         return
    #     async with ctx.acquire():
    #         await self.invoke(ctx)

    async def on_guild_join(self, guild):
        botlist = list(filter(lambda u: u.bot, guild.members))
        member_count = len(guild.members)
        if len(botlist) / member_count >= 0.60:
            await guild.default_channel.send("To avoid bot collection servers, I auto leave any server where 60% or above of the users are bots, sorry!")
            await guild.leave()
            print('Joined and left guild {} due to high bot population'.format(str(guild.id)))
        else:
            db = database.Database("guilds.db")
            db.add_guild_table(str(guild.id))
            db.close_connection()
            await guild.default_channel.send('Bleep bloop. IzduBot hath arrived to judge your worth and bless or curse your luck.')
            print('Joined guild {} successfully'.format(str(guild.id)))

    async def on_guild_remove(self, guild):
        # We're going to figure out what (if anything) needs to be done for this, but we don't want to remove the guild table in case it was an accident or something
        pass

    def run(self):
        super().run(self.bot_token, reconnect=True)


if __name__ == "__main__":
    IzduBot().run()
