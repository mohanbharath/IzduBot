"""
Created 25 Jul 17
Modified 17 Aug 17

@author = Bharath Mohan | MrMonday
"""
import math
import discord
from discord.ext import commands
import config
import database
#import util
from random import randint

class Character:
    """The Character cog handles all character-related rolls and actions. Ability checks, skill checks, saving throws, attack rolls - they all
       come through here. In addition, this cog also provides the functions to look up skill proficiencies or ability scores for characters, or
       get their modifiers. Essentially, if it has to do with the creation, playing, killing, or retirement of characters, it's through here."""

    ability_lookup = {0: 'N/A', # there are better ways to do this, but for now I'm just going to copy-paste these dicts where needed
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

    @commands.command()
    @commands.guild_only()
    async def create(self, ctx, str: int, dex: int, con: int, int: int, wis: int, cha: int, name: str, race: str, char_class: str, lvl: int,
                          align: int, hit_die: int, spell_stat: int):
        """Format: `izd_create STR DEX CON INT WIS CHA "name" "race" "class" level align_id hit_dice spell_stat`
                where:
                align_id is between 1 and 9 inclusive, with 1-3 being Lawful Good, Lawful Neutral, and Lawful Evil, 4-6 being Neutral Good, True Neutral,
                and Neutral Evil, and 7-9 being Chaotic Good, Chaotic Neutral, and Chaotic Evil respectively;
                hit_dice is the hit dice for your class;
                and spell_stat is the ability your class uses to cast spells, with 0 being for non-spell casters,
                1 for STR, 2 for DEX, 3 for CON, 4 for INT, 5 for WIS, and 6 for CHA.

           Creates a new character on the campaign server. """
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        db = database.Database("guilds.db")
        if db.has_char(guild_id, user_id):
            await ctx.send("You appear to currently have an active character. You are limited to one active character per campign(server). Please retire your character before making a new one.")
            db.close_connection()
            return
        error_encountered = False
        if (align < 1 or align > 9):
            await ctx.send("Alignment must be between 1 and 9 inclusive, with the mapping as follows:\n 1 - Lawful Good \n 2 - Lawful Neutral \n 3 - Lawful Evil \n 4 - Neutral Good \n 5 - True Neutral \n 6 - Neutral Evil \n 7 - Chaotic Good \n 8 - Chaotic Neutral \n 9 - Chaotic Evil")
            error_encountered = True
        if (spell_stat < 0 or spell_stat > 6):
            await ctx.send("Spell stat must be between 0 and 6 inclusive, with the mapping as follows:\n 0 - class is not a spellcaster \n 1 - STR \n 2 - DEX \n 3 - CON \n 4 - INT \n 5 - WIS \n 6 - CHA")
            error_encountered = True
        if error_encountered:
            db.close_connection()
            return
        else:
            initiative = math.floor((dex-10)/2) # Just the dex modifier; initiative is just a dex check without class features or feats.
            armor_class = 10 + initiative
            db.add_char(guild_id, user_id, name, race, char_class, lvl, align, hit_die, hit_die, str, dex, con, int, wis, cha, initiative, armor_class, spell_stat, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            char_name = db.get_name(guild_id, user_id)
            await ctx.send("{} - Character {} has been created! Please note that your character currently has no skill or save proficiencies - please use izd_gainskillprof and izd_gainsaveprof to add those. In addition, your character has the default armor class (10 + DEX modifier) - if you want to equip armor with an AC bonus, use izd_changeac to adjust your AC value.".format(ctx.author.mention, char_name))
            db.close_connection()
            return

    @commands.command()
    @commands.guild_only()
    async def retire(self, ctx):
        """Format: izd_retire

           Retire the author's current character from the campaign """
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        db = database.Database("guilds.db")
        if not db.has_char(guild_id, user_id):
            await ctx.send(content='You do not appear to have an active character in this campaign. This may be because you recently retired a character, or because you have not ever made a character in this campaign. Please make a character.')
            db.close_connection()
            return
        db.retire_char(guild_id, user_id)

    @commands.command()
    @commands.guild_only()
    async def abilitycheck(self, ctx, ability: str, advantage: int = 0):
        """Format: izd_abilitycheck "ability" adv
                where ability is STR, DEX, CON, INT, WIS, or CHA,
                and adv is 1 if you have advantage, -1 if you have disadvantage, blank (or 0) otherwise

        Does an ability check using the author's current character sheet."""
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        db = database.Database("guilds.db")
        if not db.has_char(guild_id, user_id):
            await ctx.send(content='You do not appear to have an active character in this campaign. This may be because you recently retired a character, or because you have not ever made a character in this campaign. Please make a character.')
            db.close_connection()
            return
        # if (ability_id < 1 or ability_id > 6):
        #     await ctx.send(content="Ability ID is invalid! Please use the following mapping: 1 for STR, 2 for DEX, 3 for CON, 4 for INT, 5 for WIS, or 6 for CHA")
        #     db.close_connection()
        #     return
        ability_id = -1
        for k,v in self.ability_lookup.items():
            if v.upper() == ability.upper():
                ability_id = k
        if ability_id < 1:
            await ctx.send("Ability is invalid! Valid inputs are STR, DEX, CON, INT, WIS, CHA. Perhaps you misspelled your input?")
            db.close_connection()
            return
        ability_score = db.get_ability_score(guild_id, user_id, ability_id)
        ability_mod = math.floor((ability_score - 10) / 2)
        if (advantage == 0):
            dice_roll = self.advantage_roll(advantage)
        else:
            roll_list = self.advantage_roll(advantage)
            dice_roll, bad_roll = roll_list[0], roll_list[1]
        roll_result = max((dice_roll + ability_mod), 1) # Ability and skill checks technically don't go below one even if mathematically they are supposed to
        message = ctx.author.mention
        message += ": 1d20 "
        if ability_mod >= 0:
            message += "+ " + str(ability_mod) + " = " + str(dice_roll) + " + " + str(ability_mod) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + ability_mod), 1)
                message += "\n~~1d20 + " + str(ability_mod) + " = " + str(bad_roll) + " + " + str(ability_mod) + " = " + str(other_roll_result) + "~~"
        else:
            message += "- " + str(abs(ability_mod)) + " = " + str(dice_roll) + " - " + str(abs(ability_mod)) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + ability_mod), 1)
                message += "\n~~1d20 - " + str(abs(ability_mod)) + " = " + str(bad_roll) + " - " + str(abs(ability_mod)) + " = " + str(other_roll_result) + "~~"
        await ctx.send(content=message)
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def skillcheck(self, ctx, skill: str, advantage: int = 0):
        """Format: izd_skillcheck "skill" adv,
                where skill is the first word of the skill you want to use;
                and adv is 1 if you have advantage, -1 if you have disadvantage, blank (or 0) otherwise

        Does a skill check using the author's current character sheet. """
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        db = database.Database("guilds.db")
        if not db.has_char(guild_id, user_id):
            await ctx.send(content='You do not appear to have an active character in this campaign. This may be because you recently retired a character, or because you have not ever made a character in this campaign. Please make a character.')
            db.close_connection()
            return
        # if (skill_id < 1 or skill_id > 18):
        #     await ctx.send(content="Skill ID is invalid! Please use the following mapping:\n 1 for Athletics \n 2 for Acrobatics \n 3 for Sleight of Hand \n 4 for Stealth \n 5 for Arcana \n 6 for History \n 7 for Investigation \n 8 for Nature \n 9 for Religion \n 10 for Animal Handling \n 11 for Insight \n 12 for Medicine \n 13 for Perception \n 14 for Survival \n 15 for Deception \n 16 for Intimidation \n 17 for Performance \n 18 for Persuasion")
        #     db.close_connection()
        #     return
        skill_id = -1
        for k,v in self.skill_lookup.items():
            if v.upper() == skill.upper():
                skill_id = k
        if skill_id < 1:
            await ctx.send("Skill is invalid! Valid inputs are Athletics, Acrobatics, Sleight, Stealth, Arcana, History, Investigation, Nature, Religion, Animal, Insight, Medicine, Perception, Survival, Deception, Intimidation, Performance, and Persuasion. Perhaps you misspelled your input?")
            db.close_connection()
            return
        ability_id = self.skill_to_ability_lookup[skill_id]
        ability_score = db.get_ability_score(guild_id, user_id, ability_id)
        ability_mod = math.floor((ability_score - 10) / 2)
        char_lvl = db.get_level(guild_id, user_id)
        skill_prof = db.get_skill_prof(guild_id, user_id, skill_id)
        if skill_prof:
            proficiency_mod = 1 + math.ceil(char_lvl / 4)
        else:
            proficiency_mod = 0
        if (advantage == 0):
            dice_roll = self.advantage_roll(advantage)
        else:
            roll_list = self.advantage_roll(advantage)
            dice_roll, bad_roll = roll_list[0], roll_list[1]
        roll_result = max((dice_roll + ability_mod + proficiency_mod), 1)
        message = ctx.author.mention
        message += ": 1d20 "
        if ability_mod >= 0:
            message += "+ " + str(ability_mod) + " + " + str(proficiency_mod) + " = " + str(dice_roll) + " + " + str(ability_mod) + " + " + str(proficiency_mod) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + ability_mod), 1)
                message += "\n~~1d20 + " + str(ability_mod) + " + " + str(proficiency_mod) + " = " + str(bad_roll) + " + " + str(ability_mod) + " + " + str(proficiency_mod) + " = " + str(other_roll_result) + "~~"
        else:
            message += "- " + str(abs(ability_mod)) + " + " + str(proficiency_mod) + " = " + str(dice_roll) + " - " + str(abs(ability_mod)) + " + " + str(proficiency_mod) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + ability_mod), 1)
                message += "\n~~1d20 - " + str(abs(ability_mod)) + " + " + str(proficiency_mod) + " = " + str(bad_roll) + " - " + str(abs(ability_mod)) + " + " + str(proficiency_mod) + " = " + str(other_roll_result) + "~~"
        await ctx.send(content=message)
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def initiativeroll(self, ctx, advantage: int = 0):
        """Format: izd_initiativeroll adv
                where adv is 1 if you have advantage, -1 if you have disadvantage, blank (or 0) otherwise
                Does an initiative roll using the author's current character sheet.

        Currently, IzduBot doesn't keep track of initiative, so this is just a roll with the initiative modifier."""
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        db = database.Database("guilds.db")
        if not db.has_char(guild_id, user_id):
            await ctx.send(content='You do not appear to have an active character in this campaign. This may be because you recently retired a character, or because you have not ever made a character in this campaign. Please make a character.')
            db.close_connection()
            return
        initiative_mod = db.get_initiative(guild_id, user_id)
        if (advantage == 0):
            dice_roll = self.advantage_roll(advantage)
        else:
            roll_list = self.advantage_roll(advantage)
            dice_roll, bad_roll = roll_list[0], roll_list[1]
        roll_result = max((dice_roll + initiative_mod), 1)
        message = ctx.author.mention
        message += ": 1d20 "
        if initiative_mod >= 0:
            message += "+ " + str(initiative_mod) + " = " + str(dice_roll) + " + " + str(initiative_mod) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + initiative_mod), 1)
                message += "\n~~1d20 + " + str(initiative_mod) + " = " + str(bad_roll) + " + " + str(initiative_mod) + " = " + str(other_roll_result) + "~~"
        else:
            message += "- " + str(abs(initiative_mod)) + " = " + str(dice_roll) + " - " + str(abs(initiative_mod)) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + initiative_mod), 1)
                message += "\n~~1d20 - "+ str(abs(initiative_mod)) + " = " + str(bad_roll) + " - " + str(abs(initiative_mod)) + " = " + str(other_roll_result) + "~~"
        await ctx.send(content=message)
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def attackroll(self, ctx, ability: str, weapon_proficiency: int, advantage: int = 0):
        """Format: izd_attackroll "ability" weapon_proficiency adv,
                where "ability" is the same as with abilitycheck;
                weapon_proficiency is 1 if you have proficiency with the weapon being used, 0 otherwise;
                and adv is 1 if you have advantage, -1 if you have disadvantage, blank (or 0) otherwise

        Does an attack roll using the author's character sheet"""
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        db = database.Database("guilds.db")
        if not db.has_char(guild_id, user_id):
            await ctx.send(content='You do not appear to have an active character in this campaign. This may be because you recently retired a character, or because you have not ever made a character in this campaign. Please make a character.')
            db.close_connection()
            return
        ability_id = -1
        for k,v in self.ability_lookup.items():
            if v.upper() == ability.upper():
                ability_id = k
        if ability_id < 1 or ability_id > 2:
            await ctx.send(content="Ability is invalid! Attack rolls only accept either STR or DEX for the ability identifier.")
            db.close_connection()
            return
        if weapon_proficiency > 1 or weapon_proficiency < 0:
            await ctx.send(content="Weapon proficiency invalid! If you have proficiency with the weapon you're using, enter 1; otherwise, enter 0")
            db.close_connection()
            return
        ability_score = db.get_ability_score(guild_id, user_id, ability_id)
        ability_mod = math.floor((ability_score - 10) / 2)
        char_lvl = db.get_level(guild_id, user_id)
        if weapon_proficiency:
            proficiency_mod = 1 + math.ceil(char_lvl / 4)
        else:
            proficiency_mod = 0
        if (advantage == 0):
            dice_roll = self.advantage_roll(advantage)
        else:
            roll_list = self.advantage_roll(advantage)
            dice_roll, bad_roll = roll_list[0], roll_list[1]
        roll_result = max((dice_roll + ability_mod + proficiency_mod), 1)
        message = ctx.author.mention
        message += ": 1d20 "
        if ability_mod >= 0:
            message += "+ " + str(ability_mod) + " + " + str(proficiency_mod) + " = " + str(dice_roll) + " + " + str(ability_mod) + " + " + str(proficiency_mod) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + ability_mod + proficiency_mod), 1)
                message += "\n~~1d20 + " + str(ability_mod) + " + " + str(proficiency_mod) + " = " + str(bad_roll) + " + " + str(ability_mod) + " + " + str(proficiency_mod) + " = " + str(other_roll_result) + "~~"
        else:
            message += "- " + str(abs(ability_mod)) + " + " + str(proficiency_mod) + " = " + str(dice_roll) + " - " + str(abs(ability_mod)) + " + " + str(proficiency_mod) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + ability_mod + proficiency_mod), 1)
                message += "\n~~1d20 + " + str(abs(ability_mod)) + " + " + str(proficiency_mod) + " = " + str(bad_roll) + " - " + str(abs(ability_mod)) + " + " + str(proficiency_mod) + " = " + str(other_roll_result) + "~~"
        await ctx.send(content=message)
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def abilitysave(self, ctx, ability: str, advantage: int = 0):
        """Format: izd_abilitysave "ability" adv
                where ability is STR, DEX, CON, INT, WIS, or CHA;
                and adv is 1 if you have advantage, -1 if you have disadvantage, blank (or 0) otherwise

            Does an ability save."""
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        db = database.Database("guilds.db")
        if not db.has_char(guild_id, user_id):
            await ctx.send(content='You do not appear to have an active character in this campaign. This may be because you recently retired a character, or because you have not ever made a character in this campaign. Please make a character.')
            db.close_connection()
            return
        ability_id = -1
        for k,v in self.ability_lookup.items():
            if v.upper() == ability.upper():
                ability_id = k
        if (ability_id < 1):
            await ctx.send(content="Ability is invalid! Valid inputs are STR, DEX, CON, INT, WIS, CHA. Perhaps you misspelled your input?")
            db.close_connection()
            return
        ability_score = db.get_ability_score(guild_id, user_id, ability_id)
        ability_mod = math.floor((ability_score - 10) / 2)
        char_lvl = db.get_level(guild_id, user_id)
        save_prof = db.get_save_prof(guild_id, user_id, ability_id)
        if save_prof:
            proficiency_mod = 1 + math.ceil(char_lvl / 4)
        else:
            proficiency_mod = 0
        if (advantage == 0):
            dice_roll = self.advantage_roll(advantage)
        else:
            roll_list = self.advantage_roll(advantage)
            dice_roll, bad_roll = roll_list[0], roll_list[1]
        roll_result = max((dice_roll + ability_mod + proficiency_mod), 1)
        message = ctx.author.mention
        message += ": 1d20 "
        if ability_mod >= 0:
            message += "+ " + str(ability_mod) + " + " + str(proficiency_mod) + " = " + str(dice_roll) + " + " + str(ability_mod) + " + " + str(proficiency_mod) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + ability_mod + proficiency_mod), 1)
                message += "\n~~1d20 + " + str(ability_mod) + " + " + str(proficiency_mod) + " = " + str(bad_roll) + " + " + str(ability_mod) + " + " + str(proficiency_mod) + " = " + str(other_roll_result) + "~~"
        else:
            message += "- " + str(abs(ability_mod)) + " + " + str(proficiency_mod) + " = " + str(dice_roll) + " - " + str(abs(ability_mod)) + " + " + str(proficiency_mod) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + ability_mod + proficiency_mod), 1)
                message += "\n~~1d20 - " + str(abs(ability_mod)) + " + " + str(proficiency_mod) + " = " + str(bad_roll) + " - " + str(abs(ability_mod)) + " + " + str(proficiency_mod) + " = " + str(other_roll_result) + "~~"
        await ctx.send(content=message)
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def spellattack(self, ctx, advantage: int = 0):
        """Format: izd_spellattack adv
                where adv is 1 if you have advantage, -1 if you have disadvantage, blank (or 0) otherwise

           Makes a spell attack roll. """
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        db = database.Database("guilds.db")
        if not db.has_char(guild_id, user_id):
            await ctx.send(content='You do not appear to have an active character in this campaign. This may be because you recently retired a character, or because you have not ever made a character in this campaign. Please make a character.')
            db.close_connection()
            return
        ability_id = db.get_spell_stat(guild_id, user_id)
        if ability_id == 0:
            await ctx.send(content="You indicated at character creation that your class does not use spells; are you sure you didn't mean to use izd_attackroll (i.e., make an attack roll)?")
            db.close_connection()
            return
        ability_score = db.get_ability_score(guild_id, user_id, ability_id)
        ability_mod = math.floor((ability_score - 10) / 2)
        char_lvl = db.get_level(guild_id, user_id)
        proficiency_mod = 1 + math.ceil(char_lvl / 4)
        if (advantage == 0):
            dice_roll = self.advantage_roll(advantage)
        else:
            roll_list = self.advantage_roll(advantage)
            dice_roll, bad_roll = roll_list[0], roll_list[1]
        roll_result = max((dice_roll + ability_mod + proficiency_mod), 1)
        message = ctx.author.mention
        message += ": 1d20 "
        if ability_mod >= 0:
            message += "+ " + str(ability_mod) + " + " + str(proficiency_mod) + " = " + str(dice_roll) + " + " + str(ability_mod) + " + " + str(proficiency_mod) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + ability_mod + proficiency_mod), 1)
                message += "\n~~1d20 + " + str(ability_mod) + " + " + str(proficiency_mod) + " = " + str(bad_roll) + " + " + str(ability_mod) + " + " + str(proficiency_mod) + " = " + str(other_roll_result) + "~~"
        else:
            message += "- " + str(abs(ability_mod)) + " + " + str(proficiency_mod) + " = " + str(dice_roll) + " - " + str(abs(ability_mod)) + " + " + str(proficiency_mod) + " = " + str(roll_result)
            if (advantage > 0 or advantage < 0):
                other_roll_result = max((bad_roll + ability_mod + proficiency_mod), 1)
                message += "\n~~1d20 - " + str(ability_mod) + " + " + str(proficiency_mod) + " = " + str(bad_roll) + " - " + str(ability_mod) + " + " + str(proficiency_mod) + " = " + str(other_roll_result) + "~~"
        await ctx.send(content=message)
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def spellsavedc(self, ctx):
        """Format: izd_spellsavedc

           Outputs the save DC for your character's spells."""
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        db = database.Database("guilds.db")
        if not db.has_char(guild_id, user_id):
            await ctx.send(content='You do not appear to have an active character in this campaign. This may be because you recently retired a character, or because you have not ever made a character in this campaign. Please make a character.')
            db.close_connection()
            return
        ability_id = db.get_spell_stat(guild_id, user_id)
        if ability_id == 0:
            await ctx.send(content="You indicated at character creation that your class does not use spells, so you don't have a save DC.")
        ability_score = db.get_ability_score(guild_id, user_id, ability_id)
        ability_mod = math.floor((ability_score - 10) / 2)
        char_lvl = db.get_level(guild_id, user_id)
        proficiency_mod = 1 + math.ceil(char_lvl / 4)
        save_dc = 8 + ability_mod + proficiency_mod
        message = ctx.author.mention
        if ability_mod > 0:
            message += ": Your spell save DC is 8 + " + str(ability_mod) + " + " + str(proficiency_mod) + " = " + str(save_dc)
        else:
            message += ": Your spell save DC is 8 - " + str(abs(ability_mod)) + " + " + str(proficiency_mod) + " = " + str(save_dc)
        await ctx.send(content=message)
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def attackmade(self, ctx, target: discord.Member, attack_roll: int, damage_amt: int):
        """Format: izd_healcharacter @targetplayer attackroll damageamt
                where @targetplayer is a MENTION of the player to heal,
                attackroll is the roll for the attack with all modifiers included (DOES NOT ACCEPT DICE ROLLS)
                and damageamt is the amount of damage the attack would deal if successful (DOES NOT ACCEPT DICE ROLLS)

           An attack is made against a character: does it hit?"""
        guild_id = ctx.guild.id
        user_id = target.id
        db = database.Database("guilds.db")
        if not db.has_char(guild_id, user_id):
            await ctx.send(content='This user doesn\'t seem to have an active character in this campaign - check your target again.')
            db.close_connection()
            return
        prev_temp_hp = db.get_temp_hp(guild_id, user_id)
        armor_class = db.get_armor_class(guild_id, user_id)
        if attack_roll >= armor_class:
            if prev_temp_hp == 0:
                new_cur_hp = db.get_cur_hp(guild_id, user_id)
                message = "{} {} - the enemy rolled a {} against your armor class of {}, dealing {} damage. Your current hp is now {}".format(ctx.author.mention, target.mention, attack_roll, armor_class, damage_amt, new_cur_hp)
            else:
                new_temp_hp = db.get_temp_hp(guild_id, user_id)
                new_cur_hp = db.get_cur_hp(guild_id, user_id)
                message = "{} {} - the enemy rolled a {} against your armor class of {}, dealing {} damage. Your temporary hp was {} and is now {}, and your current hp is now {}".format(ctx.author.mention, target.mention, attack_roll, armor_class, damage_amt, prev_temp_hp, new_temp_hp, new_cur_hp)
        else:
            message = "{} {} - the enemy rolled a {} against your armor class of {} - miss!".format(ctx.author.mention, target.mention, attack_roll, armor_class)
        await ctx.send(content=message)
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def healcharacter(self, ctx, target: discord.Member, heal_amt: int):
        """Format: izd_healcharacter @targetplayer heal_amt
                where @targetplayer is a MENTION of the player to heal, and heal_amt is the amount to heal them (DOES NOT ACCEPT DICE ROLLS, ONLY NUMBERS).

           One character (or the DM) heals another character. """
        guild_id = ctx.guild.id
        user_id = target.id
        db = database.Database("guilds.db")
        prev_cur_hp = db.get_temp_hp(guild_id, user_id)
        new_cur_hp = db.heal_damage(guild_id, user_id, heal_amt)
        await ctx.send(content='{} - You were healed for {}, bringing you from {} HP to {} HP'.format(target.mention, heal_amt, prev_cur_hp, new_cur_hp))
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def updateabilityscore(self, ctx, ability: str, new_score: int):
        """Format: izd_updateabilityscore "ability" new_score,
                where "ability" is STR, DEX, CON, INT, WIS, or CHA in quotes;
                and new_score is the new score for the ability in question

        Updates the ability score on your character sheet"""
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        db = database.Database("guilds.db")
        if not db.has_char(guild_id, user_id):
            await ctx.send("You do not appear to have an active character in this campaign. This may be because you recently retired a character, or because you have not ever made a character in this campaign. Please make a character.")
            db.close_connection()
            return
        ability_id = -1
        for k,v in self.ability_lookup.items():
            if v.upper() == ability.upper():
                ability_id = k
        if (ability_id < 1):
            await ctx.send(content='Ability for save is invalid! Valid inputs are STR, DEX, CON, INT, WIS, CHA. Perhaps you misspelled your input?')
            db.close_connection()
            return
        db.set_ability_score(guild_id, user_id, ability_id, new_score)
        changed_score = db.get_ability_score(guild_id, user_id, ability_id)
        await ctx.send(content='{} - {} ability score is now set to {}'.format(ctx.author.mention, ability.upper(), changed_score))
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def gainsaveprof(self, ctx, ability: str):
        """Format: izd_gainsaveprof "ability"
                where ability is the abilty to gain a save proficiency in (STR, DEX, etc.)

           Adds the requested save proficiency to the character sheet"""
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        db = database.Database("guilds.db")
        if not db.has_char(guild_id, user_id):
            await ctx.send(content='You do not appear to have an active character in this campaign. This may be because you recently retired a character, or because you have not ever made a character in this campaign. Please make a character.')
            db.close_connection()
            return
        ability_id = -1
        for k,v in self.ability_lookup.items():
            if v.upper() == ability.upper():
                ability_id = k
        if (ability_id < 1):
            await ctx.send(content='Ability for save is invalid! Valid inputs are STR, DEX, CON, INT, WIS, CHA. Perhaps you misspelled your input?')
            db.close_connection()
            return
        db.add_save_prof(guild_id, user_id, ability_id)
        char_name = db.get_name(guild_id, user_id)
        await ctx.send(content='{} - {} Save Proficiency added to {}. If this was a typo or mistake, please tell your DM, and they can fix it.'.format(ctx.author.mention, ability.upper(), char_name))
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def gainskillprof(self, ctx, skill: str):
        """Format: izd_gainskillprof "skill"
                where skill is the first word of the skill to gain a save proficiency in (e.g. "stealth" for stealth or "animal" for animal handling)

           Adds the requested skill proficiency to the character sheet"""
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        db = database.Database("guilds.db")
        if not db.has_char(guild_id, user_id):
            await ctx.send(content='You do not appear to have an active character in this campaign. This may be because you recently retired a character, or because you have not ever made a character in this campaign. Please make a character.')
            db.close_connection()
            return
        # if (skill_id < 1 or skill_id > 18):
        #     await ctx.send(content="Skill ID is invalid! Please use the following mapping:\n 1 for Athletics \n 2 for Acrobatics \n 3 for Sleight of Hand \n 4 for Stealth \n 5 for Arcana \n 6 for History \n 7 for Investigation \n 8 for Nature \n 9 for Religion \n 10 for Animal Handling \n 11 for Insight \n 12 for Medicine \n 13 for Perception \n 14 for Survival \n 15 for Deception \n 16 for Intimidation \n 17 for Performance \n 18 for Persuasion")
        #     db.close_connection()
        #     return
        skill_id = -1
        for k,v in self.skill_lookup.items():
            if v.upper() == skill.upper():
                skill_id = k
        if skill_id < 1:
            await ctx.send("Skill is invalid! Valid inputs are Athletics, Acrobatics, Sleight, Stealth, Arcana, History, Investigation, Nature, Religion, Animal, Insight, Medicine, Perception, Survival, Deception, Intimidation, Performance, and Persuasion. Perhaps you misspelled your input?")
            db.close_connection()
            return
        db.add_skill_prof(guild_id, user_id, skill_id)
        char_name = db.get_name(guild_id, user_id)
        await ctx.send(content='{} - {} Skill Proficiency ({}) added to {}. If this was a typo or mistake, please tell your DM, and they can fix it.'.format(ctx.author.mention, self.skill_lookup[skill_id], self.ability_lookup[self.skill_to_ability_lookup[skill_id]], char_name))
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def gaintemphp(self, ctx, hp_amt: int):
        """Format: izd_gainsaveprof amount
                where amount is the amount of temp HP to gain

           Adds the requested amount of temp HP to the character sheet"""
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        db = database.Database("guilds.db")
        if not db.has_char(guild_id, user_id):
            await ctx.send(content='You do not appear to have an active character in this campaign. This may be because you recently retired a character, or because you have not ever made a character in this campaign. Please make a character.')
            db.close_connection()
            return
        new_temp_hp = db.add_temp_hp(guild_id, user_id, hp_amt)
        char_name - db.get_name(guild_id, user_id)
        await ctx.send(content='{} - {} has gained {} temp HP - current temporary hitpoints = {}'.format(ctx.author.mention, char_name, hp_amt, new_temp_hp))
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def changeac(self, ctx, new_ac: int):
        """Format: izd_changeac newac
                where newac is the new AC for the character

           Updates the AC on the character sheet"""
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        db = database.Database("guilds.db")
        if not db.has_char(guild_id, user_id):
            await ctx.send(content='You do not appear to have an active character in this campaign. This may be because you recently retired a character, or because you have not ever made a character in this campaign. Please make a character.')
            db.close_connection()
            return
        db.update_armor_class(guild_id, user_id, new_ac)
        assigned_ac = db.get_armor_class(guild_id, user_id)
        char_name = db.get_name(guild_id, user_id)
        await ctx.send(content='{} - {}\'s new armor class is {}. If this was a mistake, or a typo occurred, you can change it with this command again.'.format(ctx.author.mention, char_name, assigned_ac))
        db.close_connection()
        return

    @commands.command()
    @commands.guild_only()
    async def changealign(self, ctx, new_align: int):
        """Format: izd_gainsaveprof "ability"
                where ability is the the abilty to gain a save proficiency in (STR, DEX, etc.)

           Adds the requested save proficiency to the character sheet"""
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        db = database.Database("guilds.db")
        if not db.has_char(guild_id, user_id):
            await ctx.send(content='You do not appear to have an active character in this campaign. This may be because you recently retired a character, or because you have not ever made a character in this campaign. Please make a character.')
            db.close_connection()
            return
        if (new_align < 1 or new_align > 9):
            await ctx.send(content="Alignment must be between 1 and 9 inclusive, with the mapping as follows:\n 1 - Lawful Good \n 2 - Lawful Neutral \n 3 - Lawful Evil \n 4 - Neutral Good \n 5 - True Neutral \n 6 - Neutral Evil \n 7 - Chaotic Good \n 8 - Chaotic Neutral \n 9 - Chaotic Evil")
            db.close_connection()
            return
        db.change_align(guild_id, user_id, new_align)
        assigned_align = db.get_alignment(guild_id, user_id)
        char_name = db.get_name(guild_id, user_id)
        await ctx.send(content='{} - {}\'s new alignment is {}. If this was a mistake, or a typo occurred, you can change it with this command again.'.format(ctx.author.mention, char_name, assigned_align))
        db.close_connection()
        return




def setup(bot):
    bot.add_cog(Character(bot))
