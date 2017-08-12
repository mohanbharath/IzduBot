"""
Created 07 Aug 17
Modified 10 Aug 17

@author = Bharath Mohan | MrMonday
"""
import math
import discord
from discord.ext import commands
import config
import database
from random import randint

class DungeonMaster:
    """The DungeonMaster class covers all commands that a DM might want to use in setting up and running encounters"""

    ability_lookup = {0: 'N/A',
                      1: 'STR',
                      2: 'DEX',
                      3: 'CON',
                      4: 'INT',
                      5: 'WIS',
                      6: 'CHA'}
    skill_lookup = {1: 'athletics',
                    2: 'acrobatics',
                    3: 'sleight',
                    4: 'stealth',
                    5: 'arcana',
                    6: 'history',
                    7: 'investigation',
                    8: 'nature',
                    9: 'religion',
                    10: 'animal',
                    11: 'insight',
                    12: 'medicine',
                    13: 'perception',
                    14: 'survival',
                    15: 'deception',
                    16: 'intimidation',
                    17: 'performance',
                    18: 'persuasion'}
    skill_to_ability_lookup = {1: 1,
                               2: 2,
                               3: 2,
                               4: 2,
                               5: 4,
                               6: 4,
                               7: 4,
                               8: 4,
                               9: 4,
                               10: 5,
                               11: 5,
                               12: 5,
                               13: 5,
                               14: 5,
                               15: 6,
                               16: 6,
                               17: 6,
                               18: 6,}


    def __init__(self, bot):
        self.bot = bot

    # @commands.command()
    # @commands.guild_only()
    # async def startsession(self, ctx, )

    ##### BEGIN UTILITY/HELPER FUNCTIONS

    def check_role(self, ctx, author):
        '''Helper function to check for GM role on people calling these commands
           Context is currently unnecessary as an argument, but in case we need it later, we'll keep it here'''
        role_list = author.roles
        for r in role_list:
            if r.name == 'DM':
                return True
        return False

    def advantage_roll(self, advantage: int):
        '''Helper command to handle d20 advantage/disadvantage rolls for checks'''
        first_roll = randint(1,20)
        second_roll = randint(1, 20)
        if (advantage == 0):
            return first_roll
        elif (advantage > 0):
            dice_roll = max(first_roll, second_roll)
            bad_roll = min(first_roll, second_roll)
        else:
            dice_roll = min(first_roll, second_roll)
            bad_roll = max(first_roll, second_roll)
        return (dice_roll, bad_roll)

    ##### END UTILITY/HELPER FUNCTIONS

    ##### BEGIN MONSTER TEMPLATE-RELATED COMMANDS

    @commands.command()
    @commands.guild_only()
    async def addmonster(self, ctx, mons_name: str, mons_align: int, mons_hp_max: int, mons_str: int, mons_dex: int, mons_con: int, mons_int: int,
                                mons_wis: int, mons_cha: int, mons_am: int, mons_ac: int, mons_spell_stat: int, mons_str_save: int, mons_dex_save: int,
                                mons_con_save: int, mons_int_save: int, mons_wis_save: int, mons_cha_save: int):
        guild_id = ctx.guild.id
        author = ctx.author
        if not self.check_role(ctx, author):
            await ctx.send('''You do not appear to have the DM role on this campaign. If you are, in fact, a DM, have the server admin assign you the
                                "DM" role. If you are the server admin, please make a role called "DM" and assign yourself, as that is how Izdubot
                                checks permissions for DM commands.''')
            return None
        db = database.Database('guilds.db')
        db.create_guild_monster_table(guild_id)
        canary = db.add_guild_monster(guild_id, mons_name, 0, 0, mons_align, mons_hp_max, mons_str, mons_dex, mons_con, mons_int, mons_wis, mons_cha,
                                mons_am, mons_ac, mons_spell_stat, mons_str_save, mons_dex_save, mons_con_save, mons_int_save, mons_wis_save,
                                mons_cha_save)
        if (canary is None):
            await ctx.send('Catastrophic error encountered - please report to creator that addmonster killed the canary.')
            db.close_connection()
            return None
        m_id = canary[0]
        m_name = canary[1]
        await ctx.send("Monster \"{}\" successfully created; monster id is {}".format(m_name, m_id))
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def listmonsters(self, ctx):
        '''Format: izd_listmonsters
                REQUIRES GM ROLE ON CAMPAIGN

           Lists all monsters for this campaign'''
        guild_id = ctx.guild.id
        author = ctx.author
        if not self.check_role(ctx, author):
            await ctx.send('''You do not appear to have the DM role on this campaign. If you are, in fact, a DM, have the server admin assign you the
                                "DM" role. If you are the server admin, please make a role called "DM" and assign yourself, as that is how Izdubot
                                checks permissions for DM commands.''')
            return None
        db = database.Database('guilds.db')
        results = db.list_guild_monsters(guild_id)
        message = "\nID   |   Name\n"
        for r in results:
            message += "{}   |   {} \n".format(r[0], r[1])
        await ctx.send(message)
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def monsterabilitycheck(self, ctx, monster_id: int, ability: str, advantage: int = 0):
        """Format: izd_monsterabilitycheck monsterid "ability" advantage
                where monster_id is the STATIC (not session) Monster ID
                ability is the the abilty to gain a save proficiency in (STR, DEX, etc.)
                and advantage is 1 if the creature has advantage, -1 if the creature has disadvantage, and 0 (or blank) for neither

           Makes a monster ability check for the specified monster."""
        guild_id = ctx.guild.id
        author = ctx.author
        if not self.check_role(ctx, author):
            await ctx.send('''You do not appear to have the DM role on this campaign. If you are, in fact, a DM, have the server admin assign you the
                                "DM" role. If you are the server admin, please make a role called "DM" and assign yourself, as that is how Izdubot
                                checks permissions for DM commands.''')
            return None
        db = database.Database('guilds.db')
        if advantage == 0:
            dice_roll = self.advantage_roll(advantage)
        else:
            roll_list = self.advantage_roll(advantage)
            dice_roll, bad_roll = roll_list[0], roll_list[1]
        ability_id = -1
        for k,v in self.ability_lookup.items():
            if v.upper() == ability.upper():
                ability_id = k
        if ability_id < 1:
            await ctx.send("Ability is invalid! Valid inputs are STR, DEX, CON, INT, WIS, CHA. Perhaps you misspelled your input?")
            db.close_connection()
            return
        monster_ability_stat = db.get_guild_monster_stat(guild_id, monster_id, ability_id)
        monster_ability_mod = math.floor((monster_ability_stat - 10) / 2)
        roll_result = max((dice_roll + monster_ability_mod), 1)
        message = ctx.author.mention
        message += ": 1d20 "
        if monster_ability_mod >= 0:
            message += "+ " + str(monster_ability_mod) + " = " + str(dice_roll) + " + " + str(monster_ability_mod) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + monster_ability_mod), 1)
                message += "\n~~1d20 + " + str(monster_ability_mod) + " = " + str(bad_roll) + " + " + str(monster_ability_mod) + " = " + str(other_roll_result) + "~~"
        else:
            message += "- " + str(abs(monster_ability_mod)) + " = " + str(dice_roll) + " - " + str(abs(monster_ability_mod)) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + monster_ability_mod), 1)
                message += "\n~~1d20 - " + str(abs(monster_ability_mod)) + " = " + str(bad_roll) + " - " + str(abs(monster_ability_mod)) + " = " + str(other_roll_result) + "~~"
        await ctx.send(content=message)
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def monsterabilitysave(self, ctx, monster_id: int, ability: str, advantage: int = 0):
        """Format: izd_monsterabilitysave monsterid "ability" advantage
                where monster_id is the STATIC (not session) Monster ID
                ability is the the abilty to gain a save proficiency in (STR, DEX, etc.)
                and advantage is 1 if the creature has advantage, -1 if the creature has disadvantage, and 0 (or blank) for neither

           Makes a monster ability save for the specified monster."""
        guild_id = ctx.guild.id
        author = ctx.author
        if not self.check_role(ctx, author):
            await ctx.send('''You do not appear to have the DM role on this campaign. If you are, in fact, a DM, have the server admin assign you the
                                "DM" role. If you are the server admin, please make a role called "DM" and assign yourself, as that is how Izdubot
                                checks permissions for DM commands.''')
            return None
        db = database.Database('guilds.db')
        if advantage == 0:
            dice_roll = self.advantage_roll(advantage)
        else:
            roll_list = self.advantage_roll(advantage)
            dice_roll, bad_roll = roll_list[0], roll_list[1]
        ability_id = -1
        for k,v in self.ability_lookup.items():
            if v.upper() == ability.upper():
                ability_id = k
        if ability_id < 1:
            await ctx.send("Ability is invalid! Valid inputs are STR, DEX, CON, INT, WIS, CHA. Perhaps you misspelled your input?")
            db.close_connection()
            return
        monster_ability_save_mod = db.get_guild_monster_save(guild_id, monster_id, ability_id)
        roll_result = max((dice_roll + monster_ability_save_mod), 1)
        message = ctx.author.mention
        message += ": 1d20 "
        if monster_ability_save_mod >= 0:
            message += "+ " + str(monster_ability_save_mod) + " = " + str(dice_roll) + " + " + str(monster_ability_save_mod) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + monster_ability_save_mod), 1)
                message += "\n~~1d20 + " + str(monster_ability_save_mod) + " = " + str(bad_roll) + " + " + str(monster_ability_save_mod) + " = " + str(other_roll_result) + "~~"
        else:
            message += "- " + str(abs(monster_ability_save_mod)) + " = " + str(dice_roll) + " - " + str(abs(monster_ability_save_mod)) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + monster_ability_save_mod), 1)
                message += "\n~~1d20 - " + str(abs(monster_ability_save_mod)) + " = " + str(bad_roll) + " - " + str(abs(monster_ability_save_mod)) + " = " + str(other_roll_result) + "~~"
        await ctx.send(content=message)
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def monsterattackroll(self, ctx, monster_id: int, advantage: int = 0):
    """Format: izd_monsterattackroll monsterid advantage
            where monster_id is the STATIC (not session) Monster ID
            and advantage is 1 if the creature has advantage, -1 if the creature has disadvantage, and 0 (or blank) for neither

       Makes an attack roll for the specified monster."""
        guild_id = ctx.guild.id
        author = ctx.author
        if not self.check_role(ctx, author):
            await ctx.send('''You do not appear to have the DM role on this campaign. If you are, in fact, a DM, have the server admin assign you the
                                "DM" role. If you are the server admin, please make a role called "DM" and assign yourself, as that is how Izdubot
                                checks permissions for DM commands.''')
            return None
        db = database.Database('guilds.db')
        if advantage == 0:
            dice_roll = self.advantage_roll(advantage)
        else:
            roll_list = self.advantage_roll(advantage)
            dice_roll, bad_roll = roll_list[0], roll_list[1]
        monster_attack_mod = db.get_guild_monster_attack_mod(guild_id, monster_id)
        roll_result = max((dice_roll + monster_attack_mod), 1)
        message = ctx.author.mention
        message += ": 1d20 "
        if monster_attack_mod >= 0:
            message += "+ " + str(monster_attack_mod) + " = " + str(dice_roll) + " + " + str(monster_attack_mod) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + monster_attack_mod), 1)
                message += "\n~~1d20 + " + str(monster_attack_mod) + " = " + str(bad_roll) + " + " + str(monster_attack_mod) + " = " + str(other_roll_result) + "~~"
        else:
            message += "- " + str(abs(monster_attack_mod)) + " = " + str(dice_roll) + " - " + str(abs(monster_attack_mod)) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + monster_attack_mod), 1)
                message += "\n~~1d20 - " + str(abs(monster_attack_mod)) + " = " + str(bad_roll) + " - " + str(abs(monster_attack_mod)) + " = " + str(other_roll_result) + "~~"
        await ctx.send(content=message)
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def monsterinitiative(self, ctx, monster_id: int, advantage: int = 0):
    """Format: izd_monsterinitiativeroll monsterid advantage
            where monster_id is the STATIC (not session) Monster ID
            and advantage is 1 if the creature has advantage, -1 if the creature has disadvantage, and 0 (or blank) for neither

       Makes an initiative roll for the specified monster."""
        guild_id = ctx.guild.id
        author = ctx.author
        if not self.check_role(ctx, author):
            await ctx.send('''You do not appear to have the DM role on this campaign. If you are, in fact, a DM, have the server admin assign you the
                                "DM" role. If you are the server admin, please make a role called "DM" and assign yourself, as that is how Izdubot
                                checks permissions for DM commands.''')
            return None
        db = database.Database('guilds.db')
        if advantage == 0:
            dice_roll = self.advantage_roll(advantage)
        else:
            roll_list = self.advantage_roll(advantage)
            dice_roll, bad_roll = roll_list[0], roll_list[1]
        ability_id = 2
        monster_ability_save_mod = db.get_guild_monster_save(guild_id, monster_id, ability_id)
        roll_result = max((dice_roll + monster_ability_save_mod), 1)
        message = ctx.author.mention
        message += ": 1d20 "
        if monster_ability_save_mod >= 0:
            message += "+ " + str(monster_ability_save_mod) + " = " + str(dice_roll) + " + " + str(monster_ability_save_mod) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + monster_ability_save_mod), 1)
                message += "\n~~1d20 + " + str(monster_ability_save_mod) + " = " + str(bad_roll) + " + " + str(monster_ability_save_mod) + " = " + str(other_roll_result) + "~~"
        else:
            message += "- " + str(abs(monster_ability_save_mod)) + " = " + str(dice_roll) + " - " + str(abs(monster_ability_save_mod)) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + monster_ability_save_mod), 1)
                message += "\n~~1d20 - " + str(abs(monster_ability_save_mod)) + " = " + str(bad_roll) + " - " + str(abs(monster_ability_save_mod)) + " = " + str(other_roll_result) + "~~"
        await ctx.send(content=message)
        db.close_connection()
        return

    # @commands.command()
    # @commands.guild_only()
    # async def monsterspellattack(self, ctx, monster_id: int, advantage: int = 0)

    ##### END MONSTER TEMPLATE-RELATED COMMANDS

    ##### BEGIN SESSION DURATION COMMANDS

    @commands.command()
    @commands.guild_only()
    async def sessionstart(self, ctx):
        """Format: izd_sessionstart

           Starts a combat session to keep track of monster health in encounters"""
        guild_id = ctx.guild.id
        author = ctx.author
        if not self.check_role(ctx, author):
            await ctx.send('''You do not appear to have the DM role on this campaign. If you are, in fact, a DM, have the server admin assign you the
                                "DM" role. If you are the server admin, please make a role called "DM" and assign yourself, as that is how Izdubot
                                checks permissions for DM commands.''')
            return None
        db = database.Database('guilds.db')
        if db.has_session(guild_id):
            await ctx.send("You currently have a session active. Please end that session before starting a new one.")
            db.close_connection()
            return None
        db.add_session(guild_id)
        db.create_sesssion_table(guild_id)
        db.close_connection()
        await ctx.send(author.mention + ": Session successfully created!")
        return

    @commands.command()
    @commands.guild_only()
    async def sessionend(self, ctx):
        """Format: izd_sessionend

           End the current combat session, effectively killing all monsters present"""
        guild_id = ctx.guild.id
        author = ctx.author
        if not self.check_role(ctx, author):
            await ctx.send('''You do not appear to have the DM role on this campaign. If you are, in fact, a DM, have the server admin assign you the
                                "DM" role. If you are the server admin, please make a role called "DM" and assign yourself, as that is how Izdubot
                                checks permissions for DM commands.''')
            return None
        db = database.Database('guilds.db')
        if not db.has_session(guild_id):
            await ctx.send("You do not currently have an active session to end.")
            db.close_connection()
            return None
        db.remove_session(guild_id)
        db.drop_session_table(guild_id)
        await ctx.send(author.mention + ": Session successfully ended!")
        return

    ##### END SESSION DURATION COMMANDS

    ##### BEGIN MONSTER SESSION COMMANDS

    @commands.command()
    @commands.guild_only()
    async def addsessionmonster(self, ctx, static_monster_id: int):
        """Format: izd_addsessionmonster staticmonsterid
                where staticmonsterid is the STATIC ID of the monster to be added

           Add one instance or copy of the specified monster to the combat session"""
        guild_id = ctx.guild.id
        author = ctx.author
        if not self.check_role(ctx, author):
            await ctx.send('''You do not appear to have the DM role on this campaign. If you are, in fact, a DM, have the server admin assign you the
                                "DM" role. If you are the server admin, please make a role called "DM" and assign yourself, as that is how Izdubot
                                checks permissions for DM commands.''')
            return None
        db = database.Database('guilds.db')
        if not db.has_session(guild_id):
            await ctx.send("You do not currently have an active session to add a monster to. Please create a session before adding monsters.")
            db.close_connection()
            return None
        session_monster_id = db.instantiate_session_monster(guild_id, static_monster_id)
        if session_monster_id == -1:
            await ctx.send("There exists no monster with the ID {} for this campaign - are you sure you entered the correct ID? Use izd_listmonsters to check.".format(static_monster_id))
            db.close_connection()
            return None
        else:
            await ctx.send("Monster added. The session ID for this monster is {} - use this to deal damage to damage or otherwise interact with this particular instance of the monster.".format(session_monster_id))
            db.close_connection()
            return

    @commands.command()
    @commands.guild_only()
    async def listsessionmonsters(self, ctx):
        """Format: izd_listsessionmonsters

           List all monsters in the current combat session, giving session and static IDs"""
        guild_id = ctx.guild.id
        author = ctx.author
        if not self.check_role(ctx, author):
            await ctx.send('''You do not appear to have the DM role on this campaign. If you are, in fact, a DM, have the server admin assign you the
                                "DM" role. If you are the server admin, please make a role called "DM" and assign yourself, as that is how Izdubot
                                checks permissions for DM commands.''')
            return None
        db = database.Database('guilds.db')
        results = db.list_session_monsters(guild_id)
        message = author.mention + " \nSession ID   |   Monster Template ID\n"
        for r in results:
            message += "{}        |        {} \n".format(r[0], r[1])
        await ctx.send(message)
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def getsessionmonsterhp(self, ctx, session_monster_id: int):
        """Format: izd_sessionstart sessionmonsterid
                where sessionmonsterid is the SESSION ID of the monster you want to check

           Tells you how much HP the specified monster has."""
        guild_id = ctx.guild.id
        author = ctx.author
        if not self.check_role(ctx, author):
            await ctx.send('''You do not appear to have the DM role on this campaign. If you are, in fact, a DM, have the server admin assign you the
                                "DM" role. If you are the server admin, please make a role called "DM" and assign yourself, as that is how Izdubot
                                checks permissions for DM commands.''')
            return None
        db = database.Database('guilds.db')
        if not db.has_session(guild_id):
            await ctx.send("You do not currently have an active session. You must first create a session and add monsters to it.")
            db.close_connection()
            return None
        monster_hp_cur = db.get_session_monster_hp_cur(guild_id, session_monster_id)
        if monster_hp_cur == -1:
            await ctx.send("There exists no monster in the session with the ID {} - are you sure you entered the correct ID? Use izd_listsessionmonsters to check.".format(static_monster_id))
            db.close_connection()
            return None
        else:
            await ctx.send(author.mention + ": Session monster ID {} currently has {} HP.".format(session_monster_id, monster_hp_cur))
            db.close_connection()
            return

    @commands.command()
    @commands.guild_only()
    async def dealdmgsessionmonster(self, ctx, session_monster_id: int, damage_amt: int):
        """Format: izd_sessionstart sessionmonsterid damageamt
                where sessionmonsterid is the SESSION ID of the monster you want to damage
                and damageamt is the amount of damage to deal (can be negative for healing)

           Deals damageamt damage to the monster. Can use negative numbers to heal monsters"""
        guild_id = ctx.guild.id
        author = ctx.author
        if not self.check_role(ctx, author):
            await ctx.send('''You do not appear to have the DM role on this campaign. If you are, in fact, a DM, have the server admin assign you the
                                "DM" role. If you are the server admin, please make a role called "DM" and assign yourself, as that is how Izdubot
                                checks permissions for DM commands.''')
            return None
        db = database.Database('guilds.db')
        if not db.has_session(guild_id):
            await ctx.send("You do not currently have an active session. You must first create a session and add monsters to it.")
            db.close_connection()
            return None
        new_monster_cur_hp = db.damage_session_monster(guild_id, session_monster_id, damage_amt)
        if new_monster_cur_hp == -1:
            await ctx.send("There exists no monster in the session with the ID {} - are you sure you entered the correct ID? Use izd_listsessionmonsters to check.".format(static_monster_id))
            db.close_connection()
            return None
        else:
            await ctx.send(author.mention + ": Monster {}'s new current HP is {}.".format(session_monster_id, new_monster_cur_hp))
            db.close_connection()
            return

    @commands.command()
    @commands.guild_only()
    async def killsessionmonster(self, ctx, session_monster_id: int):
        """Format: izd_sessionstart sessionmonsterid
                where sessionmonsterid is the SESSION ID of the monster you want to kill

           Kills the specified monster, deleting it. THIS ACTION CANNOT BE UNDONE - a 0 health monster is still in the session.
            Only kill to remove the possiblity of reviving the monster."""
        guild_id = ctx.guild.id
        author = ctx.author
        if not self.check_role(ctx, author):
            await ctx.send('''You do not appear to have the DM role on this campaign. If you are, in fact, a DM, have the server admin assign you the
                                "DM" role. If you are the server admin, please make a role called "DM" and assign yourself, as that is how Izdubot
                                checks permissions for DM commands.''')
            return None
        db = database.Database('guilds.db')
        if not db.has_session(guild_id):
            await ctx.send("You do not currently have an active session. You must first create a session and add monsters to it.")
            db.close_connection()
            return None
        monster_id = db.kill_session_monster(guild_id, session_monster_id)
        if monster_id == -1:
            await ctx.send("There exists no monster in the session with the ID {} - are you sure you entered the correct ID? Use izd_listsessionmonsters to check.".format(static_monster_id))
            db.close_connection()
            return None
        else:
            await ctx.send(author.mention + ": Monster {} has been killed and removed from the session.".format(session_monster_id))
            db.close_connection()
            return

    ##### END MONSTER SESSION COMMANDS


def setup(bot):
    bot.add_cog(DungeonMaster(bot))
