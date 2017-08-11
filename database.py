"""
Created 24 Jul 17
Modified 10 Aug 17

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

    ##### BEGIN CHARACTER-RELATED DATABASE METHODS

    def add_guild_table(self, guild_id: str):
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS _{}_characters(char_id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, active INTEGER,
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
                                                   )'''.format(guild_id))
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
        self.cursor.execute('''INSERT INTO _{}_characters(user_id, active, alive, char_name, char_race, char_class, char_lvl, char_align, hit_die, rest_die,
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
            self.cursor.execute(''' SELECT char_id FROM _{}_characters
                                    WHERE alive = 1 AND user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        if value is None:
            return False
        return True

    def kill_char(self, guild_id: int, user_id: int):
        self.cursor.execute(''' UPDATE _{}_characters SET alive = 0
                                WHERE alive = 1 AND active = 1 AND user_id = {}
                            '''.format(guild_id, user_id))
        self.database.commit()

    def resurrect_char(self, guild_id: int, user_id: int):
        self.cursor.execute(''' UPDATE _{}_characters SET alive = 1
                                WHERE alive = 0 AND active = 1 AND user_id = {}
                            '''.format(guild_id, user_id))
        self.database.commit()

    def retire_char(self, guild_id: int, user_id: int):
        self.cursor.execute(''' UPDATE _{}_characters SET active = 0
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, user_id))
        self.database.commit()

    def get_name(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT char_name FROM _{}_characters
                                    WHERE active = 1 and user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_ability_score(self, guild_id: int, user_id: int, ability_id: int):
        assert (ability_id < 7 and ability_id > 0)
        ability = self.ability_lookup[ability_id]
        self.cursor.execute(''' SELECT {} FROM _{}_characters
                                WHERE active = 1 AND user_id = {}
                            '''.format(ability, guild_id, user_id))
        value = self.cursor.fetchone()
        return value[0]

    def get_skill_prof(self, guild_id: int, user_id: int, skill_id: int):
        assert (skill_id > 0 and skill_id < 19)
        skill = self.skill_lookup[skill_id]
        self.cursor.execute(''' SELECT {} FROM _{}_characters
                                WHERE active = 1 AND user_id = {}
                            '''.format(skill, guild_id, user_id))
        value = self.cursor.fetchone()
        return value[0]

    def get_save_prof(self, guild_id: int, user_id: int, ability_id: int):
        assert (ability_id < 7 and ability_id > 0)
        ability = self.ability_lookup[ability_id]
        self.cursor.execute(''' SELECT {}_save_prof FROM _{}_characters
                                WHERE active = 1 AND user_id = {}
                            '''.format(ability, guild_id, user_id))
        value = self.cursor.fetchone()
        return value[0]

    def get_spell_stat(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT spell_stat FROM _{}_characters
                                    WHERE active = 1 and user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_level(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT char_lvl FROM _{}_characters
                                    WHERE active = 1 AND user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_hit_die(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT hit_die FROM _{}_characters
                                    WHERE active = 1 AND user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_rest_die(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT rest_die FROM _{}_characters
                                    WHERE active = 1 AND user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_max_hp(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT hp_max FROM _{}_characters
                                    WHERE active = 1 AND user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_cur_hp(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT hp_cur FROM _{}_characters
                                    WHERE active = 1 AND user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_temp_hp(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT hp_temp FROM _{}_characters
                                    WHERE active = 1 AND user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_armor_class(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT armor_class FROM _{}_characters
                                    WHERE active = 1 and user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_initiative(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT initiative FROM _{}_characters
                                    WHERE active = 1 and user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_alignment(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT hp_temp FROM _{}_characters
                                    WHERE active = 1 AND user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_race(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT char_race FROM _{}_characters
                                    WHERE active = 1 and user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_class(self, guild_id: int, user_id: int):
        try:
            self.cursor.execute(''' SELECT char_class FROM _{}_characters
                                    WHERE active = 1 and user_id = {}
                                '''.format(guild_id, user_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def level_up(self, guild_id: int, user_id: int):
        hit_die = self.get_hit_die(guild_id, user_id)
        if hit_die == None:
            return None
        prev_lvl = self.get_level(guild_id, user_id)
        prev_rest_die = self.get_rest_die(guild_id, user_id)
        prev_max_hp = self.get_max_hp(guild_id, user_id)
        prev_cur_hp = self.get_cur_hp(guild_id, user_id)
        level_up_hp = randint(1, hit_die)
        new_lvl = prev_lvl + 1
        new_rest_die = prev_rest_die + 1
        new_max_hp = prev_max_hp + level_up_hp
        new_cur_hp = prev_cur_hp + level_up_hp
        self.cursor.execute(''' UPDATE _{}_characters
                                SET char_lvl = ?
                                    rest_die = ?
                                    hp_max = ?
                                    hp_cur = ?
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, user_id), (new_lvl, new_rest_die, new_max_hp, new_cur_hp))
        self.database.commit()
        return [new_lvl, new_max_hp, level_up_hp, new_cur_hp]

    def take_damage(self, guild_id: int, user_id: int, damage: int):
        prev_temp_hp = self.get_temp_hp(guild_id, user_id)
        if prev_temp_hp >= damage:
            new_temp_hp = prev_temp_hp - damage
            self.cursor.execute(''' UPDATE _{}_characters SET hp_temp = {}
                                    WHERE active = 1 and user_id = {}
                                '''.format(guild_id. new_temp_hp, user_id))
            self.database.commit()
            return
        else:
            damage -= prev_temp_hp
            new_temp_hp = 0
        prev_cur_hp = self.get_cur_hp(guild_id, user_id)
        new_cur_hp = max(prev_cur_hp - damage, 0) # 5th ed does not allow HP below 0
        self.cursor.execute(''' UPDATE _{}_characters
                                SET hp_cur = {}
                                    hp_temp = {}
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id. new_cur_hp, new_temp_hp, user_id))
        self.database.commit()
        return

    def heal_damage(self, guild_id: int, user_id: int, heals: int):
        prev_cur_hp = self.get_cur_hp(guild_id, user_id)
        max_hp = self.get_max_hp(guild_id, user_id)
        new_cur_hp = min(prev_cur_hp + heals, max_hp) # healing does not allow more than max hp, and does not usually add temp HP
        self.cursor.execute(''' UPDATE _{}_characters SET hp_cur = {}
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id. new_cur_hp, user_id))
        self.database.commit()
        return new_cur_hp

    def add_temp_hp(self, guild_id: int, user_id: int, amount: int):
        prev_temp_hp = self.get_temp_hp(guild_id, user_id)
        new_temp_hp = prev_temp_hp + amount
        self.cursor.execute(''' UPDATE _{}_characters SET hp_temp = {}
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, new_temp_hp, user_id))
        self.database.commit()
        return new_temp_hp

    def update_armor_class(self, guild_id: int, user_id: int, new_val: int):
        self.cursor.execute(''' UPDATE _{}_characters SET armor_class = {}
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, new_val, user_id))
        self.database.commit()

    def update_initiative(self, guild_id: int, user_id: int, new_val: int):
        self.cursor.execute(''' UPDATE _{}_characters SET initiative = {}
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, new_val, user_id))
        self.database.commit()

    def add_save_prof(self, guild_id: int, user_id: int, ability_id: int):
        assert (ability_id > 0 and ability_id < 7)
        ability = self.ability_lookup[ability_id]
        self.cursor.execute(''' UPDATE _{}_characters SET {}_save_prof = 1
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, ability, user_id))
        self.database.commit()

    def del_save_prof(self, guild_id: int, user_id: int, ability_id: int):
        assert (ability_id > 0 and ability_id < 7)
        ability = self.ability_lookup[ability_id]
        self.cursor.execute(''' UPDATE _{}_characters SET {}_save_prof = 0
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, ability, user_id))
        self.database.commit()

    def add_skill_prof(self, guild_id: int, user_id: int, skill_id: int):
        assert (skill_id > 0 and skill_id < 19)
        skill = self.skill_lookup[skill_id]
        self.cursor.execute(''' UPDATE _{}_characters SET {} = 1
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, skill, user_id))
        self.database.commit()

    def del_skill_prof(self, guild_id: int, user_id: int, skill_id: int):
        assert (skill_id > 0 and skill_id < 19)
        skill = self.skill_lookup[skill_id]
        self.cursor.execute(''' UPDATE _{}_characters SET {} = 0
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, skill, user_id))
        self.database.commit()

    def change_align(self, guild_id: int, user_id: int, new_align: int):
        assert (new_align > 0 and new_align < 10)
        self.cursor.execute(''' UPDATE _{}_characters SET char_align = {}
                                WHERE active = 1 and user_id = {}
                            '''.format(guild_id, new_align, user_id))
        self.database.commit()

    ##### END CHARACTER-RELATED DATABASE METHODS

    ##### BEGIN MONSTER TEMPLATE-RELATED DATABASE METHODS

    def create_guild_monster_table(self, guild_id: str):
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS _{}_monsters(monster_id INTEGER PRIMARY KEY, monster_name TEXT NOT NULL,
                                                   monster_cr INTEGER, monster_exp INTEGER, monster_alignment TEXT, monster_hp_max INTEGER,
                                                   monster_str INTEGER, monster_dex INTEGER, monster_con INTEGER, monster_int INTEGER,
                                                   monster_wis INTEGER, monster_cha INTEGER, monster_attack_mod INTEGER, monster_ac INTEGER,
                                                   monster_spell_stat INTEGER, monster_str_save INTEGER, monster_dex_save INTEGER,
                                                   monster_con_save INTEGER, monster_int_save INTEGER, monster_wis_save INTEGER,
                                                   monster_cha_save INTEGER)'''.format(guild_id))
            self.database.commit()
        except sqlite3.OperationalError:
            pass

    def add_guild_monster(self, guild_id: str, mons_name: str, mons_cr: int, mons_exp: int, mons_align: int, mons_hp_max: int, mons_str: int,
                             mons_dex: int, mons_con: int, mons_int: int, mons_wis: int, mons_cha: int, mons_am: int, mons_ac: int, mons_spell_stat: int,
                             mons_str_save: int, mons_dex_save: int, mons_con_save: int, mons_int_save: int, mons_wis_save: int, mons_cha_save: int):
        try:
            self.cursor.execute('''INSERT INTO _{}_monsters(monster_name,monster_cr,monster_exp,monster_alignment,monster_hp_max,monster_str,
                                                            monster_dex,monster_con,monster_int,monster_wis,monster_cha,monster_attack_mod,
                                                            monster_ac,monster_spell_stat,monster_str_save,monster_dex_save,monster_con_save,
                                                            monster_int_save,monster_wis_save,monster_cha_save)
                                                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                                '''.format(guild_id), (mons_name, mons_cr, mons_exp, mons_align, mons_hp_max, mons_str, mons_dex, mons_con,
                                                       mons_int, mons_wis, mons_cha, mons_am, mons_ac, mons_spell_stat, mons_str_save, mons_dex_save,
                                                       mons_con_save, mons_int_save, mons_wis_save, mons_cha_save))
            self.database.commit()
            self.cursor.execute('''SELECT monster_id,monster_name FROM _{}_monsters
                                    WHERE monster_id = (SELECT MAX(monster_id) FROM _{}_monsters)'''.format(guild_id, guild_id))
            return self.cursor.fetchone()
        except sqlite3.OperationalError:
            return None

    def list_guild_monsters(self, guild_id: str):
        try:
            self.cursor.execute(''' SELECT monster_id,monster_name FROM _{}_monsters
                                '''.format(guild_id))
            return self.cursor.fetchall()
        except sqlite3.OperationalError:
            return None

    def get_guild_monster_stat(self, guild_id: int, monster_id: int, ability_id: int):
        assert (monster_id > 0 and ability_id > 0 and ability_id < 7)
        ability = self.ability_lookup[ability_id]
        try:
            self.cursor.execute(''' SELECT monster_{} FROM _{}_monsters
                                    WHERE monster_id = {}
                                '''.format(ability, guild_id, monster_id))
        except sqlite3.OperationalError as e:
            print(e)
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_guild_monster_attack_mod(self, guild_id: int, monster_id: int):
        assert (monster_id > 0)
        try:
            self.cursor.execute(''' SELECT monster_attack_mod FROM _{}_monsters
                                    WHERE monster_id = {}
                                '''.format(guild_id, monster_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_guild_monster_hp(self, guild_id: int, monster_id: int):
        assert (monster_id > 0)
        try:
            self.cursor.execute(''' SELECT monster_hp_max FROM _{}_monsters
                                    WHERE monster_id = {}
                                '''.format(guild_id, monster_id))
        except sqlite3.OperationalError as e:
            print(e)
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_guild_monster_save(self, guild_id: int, monster_id: int, ability_id: int):
        assert (monster_id > 0 and ability_id > 0 and ability_id < 7)
        ability = self.ability_lookup[ability_id]
        try:
            self.cursor.execute(''' SELECT monster_{}_save FROM _{}_monsters
                                    WHERE monster_id = {}
                                '''.format(ability, guild_id, monster_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def get_guild_monster_spell_stat(self, guild_id: int, monster_id: int):
        assert (monster_id > 0)
        try:
            self.cursor.execute(''' SELECT monster_spell_stat FROM _{}_monsters
                                    WHERE monster_id = {}
                                '''.format(guild_id, monster_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    ##### END MONSTER TEMPLATE-RELATED DATABASE METHODS

    ##### BEGIN ENCOUNTER PLANNING DATABASE METHODS

    def create_encounter_table(self, guild_id: int):
        try:
            self.cursor.execute(''' CREATE TABLE IF NOT EXISTS _{}_encounters(encounter_id INTEGER PRIMARY KEY, encounter_name TEXT)
                                '''.format(guild_id))
            self.database.commit()
        except sqlite3.OperationalError as e:
            return None

    def add_encounter(self, guild_id: int, encounter_name: str):
        try:
            self.cursor.execute('''INSERT INTO _{}_encounters(encounter_name) VALUES (?)
                                '''.format(guild_id), (encounter_name,))
            self.database.commit()
        except sqlite3.OperationalError as e:
            return None

    def remove_encounter(self, guild_id: int, encounter_id: int):
        try:
            self.cursor.execute('''DELETE FROM _{}_encounters WHERE encounter_id = ?
                                '''.format(guild_id), (encounter_id,))
            self.database.commit()
        except sqlite3.OperationalError as e:
            return None

    def create_encounter_monster_table(self, guild_id: int):
        try:
            self.cursor.execute(''' CREATE TABLE IF NOT EXISTS _{}_encounter_monsters(encounter_id INTEGER, static_monster_id INTEGER,
                                                    quantity INTEGER)
                                '''.format(guild_id))
            self.database.commit()
        except sqlite3.OperationalError as e:
            return None

    def add_encounter_monsters(self, guild_id: int, encounter_id: int, static_monster_id: int, quantity: int):
        try:
            self.cursor.execute(''' INSERT INTO _{}_encounter_monsters(encounter_id,static_monster_id,quantity)
                                    VALUES (?,?,?)
                                '''.format(guild_id), (encounter_id,static_monster_id,quantity))
            self.database.commit()
        except sqlite3.OperationalError as e:
            return None

    ##### END ENCOUNTER PLANNING DATABASE METHODS

    ##### BEGIN SESSION DATABASE METHODS

    def add_session(self, guild_id: int):
        try:
            self.cursor.execute(''' CREATE TABLE IF NOT EXISTS sessions(session_id INTEGER PRIMARY KEY, guild_id INTEGER, start_time)
                                ''')
            self.cursor.execute(''' INSERT INTO sessions(guild_id,start_time) VALUES(?,(datetime('now')))''', (guild_id,))
            self.database.commit()
        except sqlite3.OperationalError as e:
            return None

    def has_session(self, guild_id: int):
        try:
            self.cursor.execute(''' SELECT COUNT(1) FROM sessions WHERE guild_id = ?''', (guild_id,))
        except sqlite3.OperationalError as e:
            return False
        value = self.cursor.fetchone()
        if value[0] == 0:
            return False
        return True

    def remove_session(self, guild_id: int):
        try:
            self.cursor.execute('''DELETE FROM sessions
                                   WHERE guild_id=?''', (guild_id,))
            self.database.commit()
        except sqlite3.OperationalError as e:
            return None

    ##### END SESSION DATABASE METHODS

    ##### BEGIN MONSTER INSTANTIATION-RELATED DATABASE METHODS

    def create_sesssion_table(self, guild_id: int):
        try:
            self.cursor.execute(''' CREATE TABLE IF NOT EXISTS _{}_session_monsters(session_monster_id INTEGER PRIMARY KEY,
                                                    static_monster_id INTEGER, monster_hp_max INTEGER, monster_hp_cur INTEGER)
                                '''.format(guild_id))
            self.database.commit()
        except sqlite3.OperationalError as e:
            return None

    def instantiate_session_monster(self, guild_id: int, static_monster_id: int):
        assert (static_monster_id > 0)
        try:
            m_hp_max = self.get_guild_monster_hp(guild_id, static_monster_id)
        except:
            return -1
        try:
            self.cursor.execute(''' CREATE TABLE IF NOT EXISTS _{}_session_monsters(session_monster_id INTEGER PRIMARY KEY,
                                                    static_monster_id INTEGER, monster_hp_max INTEGER, monster_hp_cur INTEGER)
                                '''.format(guild_id))
            self.cursor.execute(''' INSERT INTO _{}_session_monsters(static_monster_id,monster_hp_max,monster_hp_cur)
                                    VALUES (?,?,?)
                                '''.format(guild_id), (static_monster_id, m_hp_max, m_hp_max))
            self.database.commit()
            self.cursor.execute(''' SELECT MAX(session_monster_id) FROM _{}_session_monsters
                                '''.format(guild_id))
        except sqlite3.OperationalError as e:
            return None
        value = self.cursor.fetchone()
        return value[0]

    def list_session_monsters(self, guild_id: int):
        try:
            self.cursor.execute(''' SELECT session_monster_id,static_monster_id FROM _{}_session_monsters
                                '''.format(guild_id))
            return self.cursor.fetchall()
        except sqlite3.OperationalError:
            return None

    def get_session_monster_hp_cur(self, guild_id: int, session_monster_id: int):
        assert (session_monster_id > 0)
        try:
            self.cursor.execute(''' SELECT monster_hp_cur FROM _{}_session_monsters
                                    WHERE session_monster_id = ?'''.format(guild_id), (session_monster_id,))
        except sqlite3.OperationalError as e:
            print(e)
            return None
        value = self.cursor.fetchone()
        try:
            return value[0]
        except:
            return -1

    def get_session_monster_hp_max(self, guild_id: int, session_monster_id: int):
        assert (session_monster_id > 0)
        try:
            self.cursor.execute(''' SELECT monster_hp_max FROM _{}_session_monsters
                                    WHERE session_monster_id = ?'''.format(guild_id), (session_monster_id,))
        except sqlite3.OperationalError as e:
            print(e)
            return None
        value = self.cursor.fetchone()
        try:
            return value[0]
        except:
            return -1

    def damage_session_monster(self, guild_id: int, session_monster_id: int, damage_amt: int):
        assert (session_monster_id > 0)
        monster_hp_cur = self.get_session_monster_hp_cur(guild_id, session_monster_id)
        if monster_hp_cur == -1:
            return -1
        monster_new_hp = max(monster_hp_cur - damage_amt, 0)
        try:
            self.cursor.execute(''' UPDATE _{}_session_monsters SET monster_hp_cur = {}
                                    WHERE session_monster_id = {}
                                '''.format(guild_id, monster_new_hp, session_monster_id))
            self.database.commit()
        except sqlite3.OperationalError as e:
            return None
        return monster_new_hp

    def kill_session_monster(self, guild_id: int, session_monster_id: int):
        assert (session_monster_id > 0)
        monster_hp_cur = self.get_session_monster_hp_cur(guild_id, session_monster_id)
        if monster_hp_cur == -1:
            return -1
        try:
            self.cursor.execute(''' DELETE FROM _{}_session_monsters WHERE session_monster_id = ?
                                '''.format(guild_id), (session_monster_id,))
            self.database.commit()
        except sqlite3.OperationalError as e:
            return None
        return session_monster_id

    def drop_session_table(self, guild_id: int):
        try:
            self.cursor.execute(''' DROP TABLE IF EXISTS _{}_session_monsters
                                '''.format(guild_id))
            self.database.commit()
        except sqlite3.OperationalError as e:
            return None
        return True

    ##### END MONSTER INSTANTIATION-RELATED DATABASE METHODS

    def close_connection(self):
        """Close connection to database"""
        self.database.close()
