"""
@author = Bharath Mohan | MrMonday
"""
import sqlite3
import math
from random import randint

class Database:
    """docstring for Database."""

    database = ''
    cursor = ''
    ability_lookup = {0: 'n/a',
                      1: 'str',
                      2: 'dex',
                      3: 'con',
                      4: 'int',
                      5: 'wis',
                      6: 'cha'}
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
    align_lookup = {1: 'Lawful Good',
                    2: 'Lawful Neutral',
                    3: 'Lawful Evil',
                    4: 'Neutral Good',
                    5: 'True Neutral',
                    6: 'Neutral Evil',
                    7: 'Chaotic Good',
                    8: 'Chaotic Neutral',
                    9: 'Chaotic Evil'}

    def __init__(self, database: str):
        self.database = sqlite3.connect(database)
        self.cursor = self.database.cursor()

    def add_guild_table(self, guild_id: str):
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS {}(char_id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, active INTEGER,
                                                   alive INTEGER, char_name TEXT NOT NULL, char_race TEXT NOT NULL, char_class TEXT, char_lvl INTEGER,
                                                   char_align TEXT, hit_die INTEGER, rest_die INTEGER, hp_max INTEGER, hp_cur INTEGER,
                                                   hp_temp INTEGER, str INTEGER, dex INTEGER, con INTEGER, int INTEGER, wis INTEGER, cha INTEGER,
                                                   initiative INTEGER, hp_con_mod INTEGER, armor_class INTEGER, spell_stat INTEGER,
                                                   str_save_prof INTEGER, dex_save_prof INTEGER, con_save_prof INTEGER, int_save_prof INTEGER,
                                                   wis_save_prof INTEGER, cha_save_prof INTEGER, athletics INTEGER, acrobatics INTEGER,
                                                   sleight INTEGER, stealth INTEGER, arcana INTEGER, history INTEGER, investigation INTEGER,
                                                   nature INTEGER, religion INTEGER, animal INTEGER, insight INTEGER, medicine INTEGER,
                                                   perception INTEGER, survival INTEGER, deception INTEGER, intimidation INTEGER, performance INTEGER,
                                                   persuasion INTEGER
                                                   )'''.format("_" + guild_id))
            self.database.commit()
        except sqlite3.OperationalError:
            pass

    def add_char(self, guild_id: int, user_id: int, char_name: str, char_race: str,
                                      char_class: str, char_lvl: int, char_align: int,
                                      hit_die: int, hp_max: int, str: int, dex: int,
                                      con: int, int: int, wis: int, cha: int,
                                      initiative: int, armor_class: int, spell_stat: int,
                                      str_save_prof: int, dex_save_prof: int,
                                      con_save_prof: int, int_save_prof: int,
                                      wis_save_prof: int, cha_save_prof: int,
                                      athletics: int, acrobatics: int, sleight: int,
                                      stealth: int, arcana: int, history: int,
                                      investigation: int, nature: int, religion: int,
                                      animal: int, insight: int, medicine: int,
                                      perception: int, survival: int, deception: int,
                                      intimidation: int, performance: int, persuasion: int):
        self.cursor.execute('''INSERT INTO _{}(user_id, active, alive, char_name, char_race, char_class, char_lvl, char_align, hit_die, rest_die,
                                               hp_max, hp_cur, hp_temp, str, dex, con, int, wis, cha, initiative, hp_con_mod, armor_class,
                                               spell_stat, str_save_prof, dex_save_prof, con_save_prof, int_save_prof, wis_save_prof, cha_save_prof,
                                               athletics, acrobatics, sleight, stealth, arcana, history, investigation, nature, religion, animal,
                                               insight, medicine, perception, survival, deception, intimidation, performance, persuasion)
                               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                                       ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                            '''.format(guild_id), (user_id, 1, 1, char_name.title(),
                                                       char_race.title(), char_class.title(),
                                                       char_lvl, self.align_lookup[char_align], hit_die, 1, hp_max,
                                                       hp_max, 0, str, dex, con, int, wis, cha,  #character starts at full health, not a typo
                                                       initiative, math.floor((con - 10) / 2),
                                                       armor_class, spell_stat, str_save_prof,
                                                       dex_save_prof, con_save_prof,
                                                       int_save_prof, wis_save_prof,
                                                       cha_save_prof, athletics, acrobatics,
                                                       sleight, stealth, arcana, history,
                                                       investigation, nature, religion, animal,
                                                       insight, medicine, perception, survival,
                                                       deception, intimidation, performance,
                                                       persuasion))
        self.database.commit()

    def has_char(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT char_id FROM _{}
                                    WHERE alive = 1 AND user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        if value is None:
            return False
        return True

    def kill_char(self, guild_id: int, user_id: int):
        self.cursor.execute(''' UPDATE _{} SET alive = 0
                                WHERE alive = 1 AND active = 1 AND user_id = {}
                            '''.format(guild_id, user_id))
        self.database.commit()

    def resurrect_char(self, guild_id: int, user_id: int):
        self.cursor.execute(''' UPDATE _{} SET alive = 1
                                WHERE alive = 0 AND active = 1 AND user_id = {}
                            '''.format(guild_id, user_id))
        self.database.commit()

    def retire_char(self, guild_id: int, user_id: int):
        self.cursor.execute(''' UPDATE _{} SET active = 0
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, user_id))
        self.database.commit()

    def get_name(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT char_name FROM _{}
                                    WHERE active = 1 and user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_ability_score(self, guild_id: int, user_id: int, ability_id: int):
        assert (ability_id < 7 and ability_id > 0)
        ability = self.ability_lookup[ability_id]
        self.cursor.execute(''' SELECT {} FROM _{}
                                WHERE active = 1 AND user_id = {}
                            '''.format(ability, guild_id, user_id))
        value = self.cursor.fetchone()
        return value[0]

    def get_skill_prof(self, guild_id: int, user_id: int, skill_id: int):
        assert (skill_id > 0 and skill_id < 19)
        skill = self.skill_lookup[skill_id]
        self.cursor.execute(''' SELECT {} FROM _{}
                                WHERE active = 1 AND user_id = {}
                            '''.format(skill, guild_id, user_id))
        value = self.cursor.fetchone()
        return value[0]

    def get_save_prof(self, guild_id: int, user_id: int, ability_id: int):
        assert (ability_id < 7 and ability_id > 0)
        ability = self.ability_lookup[ability_id]
        self.cursor.execute(''' SELECT {}_save_prof FROM _{}
                                WHERE active = 1 AND user_id = {}
                            '''.format(ability, guild_id, user_id))
        value = self.cursor.fetchone()
        return value[0]

    def get_spell_stat(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT spell_stat FROM _{}
                                    WHERE active = 1 and user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_level(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT char_lvl FROM _{}
                                    WHERE active = 1 AND user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_hit_die(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT hit_die FROM _{}
                                    WHERE active = 1 AND user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_rest_die(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT rest_die FROM _{}
                                    WHERE active = 1 AND user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_max_hp(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT hp_max FROM _{}
                                    WHERE active = 1 AND user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_cur_hp(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT hp_cur FROM _{}
                                    WHERE active = 1 AND user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_temp_hp(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT hp_temp FROM _{}
                                    WHERE active = 1 AND user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_armor_class(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT armor_class FROM _{}
                                    WHERE active = 1 and user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_initiative(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT initiative FROM _{}
                                    WHERE active = 1 and user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_alignment(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT hp_temp FROM _{}
                                    WHERE active = 1 AND user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_race(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT char_race FROM _{}
                                    WHERE active = 1 and user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_class(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT char_class FROM _{}
                                    WHERE active = 1 and user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def level_up(self, guild_id: int, user_id: int):
        hit_die = self.get_hit_die()
        if hit_die == None:
            return None
        prev_lvl = self.get_level()
        prev_rest_die = self.get_rest_die()
        prev_max_hp = self.get_max_hp()
        prev_cur_hp = self.get_cur_hp()
        level_up_hp = randint(1, hit_die)
        new_lvl = prev_lvl + 1
        new_rest_die = prev_rest_die + 1
        new_max_hp = prev_max_hp + level_up_hp
        new_cur_hp = prev_cur_hp + level_up_hp
        self.cursor.execute(''' UPDATE _{}
                                SET char_lvl = ?
                                    rest_die = ?
                                    hp_max = ?
                                    hp_cur = ?
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, user_id), (new_lvl, new_rest_die, new_max_hp, new_cur_hp))
        self.database.commit()
        return [new_lvl, new_max_hp, level_up_hp, new_cur_hp]

    def take_damage(self, guild_id: int, user_id: int, damage: int):
        prev_temp_hp = self.get_temp_hp()
        if prev_temp_hp >= damage:
            new_temp_hp = prev_temp_hp - damage
            self.cursor.execute(''' UPDATE _{} SET hp_temp = {}
                                    WHERE active = 1 and user_id = {}
                                '''.format(guild_id. new_temp_hp, user_id))
            self.database.commit()
            return
        else:
            damage -= prev_temp_hp
            new_temp_hp = 0
        prev_cur_hp = self.get_cur_hp()
        new_cur_hp = max(prev_cur_hp - damage, 0) # 5th ed does not allow HP below 0
        self.cursor.execute(''' UPDATE _{}
                                SET hp_cur = {}
                                    hp_temp = {}
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id. new_cur_hp, new_temp_hp, user_id))
        self.database.commit()
        return

    def heal_damage(self, guild_id: int, user_id: int, heals: int):
        prev_cur_hp = self.get_cur_hp()
        max_hp = self.get_max_hp()
        new_cur_hp = min(prev_cur_hp + heals, max_hp) # healing does not allow more than max hp, and does not usually add temp HP
        self.cursor.execute(''' UPDATE _{} SET hp_cur = {}
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id. new_cur_hp, user_id))
        self.database.commit()
        return new_cur_hp

    def add_temp_hp(self, guild_id: int, user_id: int, amount: int):
        prev_temp_hp = self.get_temp_hp()
        new_temp_hp = prev_temp_hp + amount
        self.cursor.execute(''' UPDATE _{} SET hp_temp = {}
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, new_temp_hp, user_id))
        self.database.commit()
        return new_temp_hp

    def update_armor_class(self, guild_id: int, user_id: int, new_val: int):
        self.cursor.execute(''' UPDATE _{} SET armor_class = {}
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, new_val, user_id))
        self.database.commit()

    def update_initiative(self, guild_id: int, user_id: int, new_val: int):
        self.cursor.execute(''' UPDATE _{} SET initiative = {}
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, new_val, user_id))
        self.database.commit()

    def add_save_prof(self, guild_id: int, user_id: int, ability_id: int):
        assert (ability_id > 0 and ability_id < 7)
        ability = self.ability_lookup[ability_id]
        self.cursor.execute(''' UPDATE _{} SET {} = 1
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, ability, user_id))
        self.database.commit()

    def del_save_prof(self, guild_id: int, user_id: int, ability_id: int):
        assert (ability_id > 0 and ability_id < 7)
        ability = self.ability_lookup[ability_id]
        self.cursor.execute(''' UPDATE _{} SET {} = 0
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, ability, user_id))
        self.database.commit()

    def add_skill_prof(self, guild_id: int, user_id: int, skill_id: int):
        assert (skill_id > 0 and skill_id < 19)
        skill = self.skill_lookup[skill_id]
        self.cursor.execute(''' UPDATE _{} SET {} = 1
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, skill, user_id))
        self.database.commit()

    def del_skill_prof(self, guild_id: int, user_id: int, skill_id: int):
        assert (skill_id > 0 and skill_id < 19)
        skill = self.skill_lookup[skill_id]
        self.cursor.execute(''' UPDATE _{} SET {} = 0
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, skill, user_id))
        self.database.commit()

    def change_align(self, guild_id: int, user_id: int, new_align: int):
        assert (new_align > 0 and new_align < 10)
        self.cursor.execute(''' UPDATE _{} SET char_align = {}
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, new_align, user_id))
        self.database.commit()

    def close_connection(self):
        """Close connection to database"""
        self.database.close()
