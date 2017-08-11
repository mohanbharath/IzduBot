# IzduBot

## Intro

IzduBot is a Discord bot that makes it more feasible and simple to run campaigns via Discord. Currently rolls dice, maintains (some) character sheet information, and integrates character-related rolls (like attack rolls and initiative rolls) with stored stats and info.

Invite link: ~~**Let IzduBot judge your players!**~~ CURRENTLY NOT OPEN TO THE PUBLIC

## Current Features

- Simple Dice rolling (of course) with advantage/disadvantage
- Character Features
  - Character sheet info storing
    - Ability stats, level, name, race, class, alignment, max HP, current HP, temporary HP, initiative modifier, armor class, skill and save proficiencies.
  - Character rolls
    - Ability checks, Skill Checks, attack rolls, spell rolls, initiative rolls
      - Roll advantage/disadvantage
        - e.g. you might have advantage on certain skill or attack rolls as part of your class features, or because the DM said so
- DM Features
  - Monster Stat blocks
    - i.e. track basic monster stats. DOES NOT CURRENTLY SUPPORT MONSTER SKILLS, LEGENDARY ACTIONS, OR OTHER ADVANCED FEATURES
  - Monster rolls
    - Attack rolls, save rolls
  - Monster session tracking
    - Add monsters to your session and IzduBot can keep track of their HP so you don't have to write it down, so long as you remember to deduct HP using the command(s) given at appropriate times


## Planned Features

- DM Features
  - Character lookup
    - e.g. lookup a character's passive perception to see if they notice something without cluing them in that they may be supposed to notice something
  - Initiative tracking
  - Monster rolls
    - Skill rolls
  - Encounter planning
    - Add a list of monsters and quantities ahead of time and, with a single command, start a session with the list of monsters loaded up
- Character Features
  - Roll modifiers
    - e.g. your DM might give you a +3 to hit or save because of circumstances

## FAQ

### Why doesn't IzduBot auto-fill hit dice, spell stats, and other class-related information?
IzduBot could do that, and that might actually clean up a lot of the code. However, that comes at the cost of making it unusable for those running custom/homebrew classes. IzduBot is intended to make life easier for DMs, not harder, and potentially locking out homebrew settings seemed too excluding. This might be a feature in future, however, where the SRD classes are included by default, and DMs can add homebrew classes for their own campaigns.

### Why doesn't IzduBot have more functionality for spells?
As with the above regarding class-related information, while I could do that, there are again pitfalls with homebrew settings, and as with class-related information, it might be added as a feature in future, where SRD spells are included, and DMs can add their own homebrew spells.

### Why doesn't IzduBot have [X Feature]?
If I haven't listed the feature above as planned or in the FAQ, there are a number of possible reasons: the feature might be too difficult or tedious to implement at present, the feature might pose problems for homebrewers, or I may just not have thought of the feature at all yet. Feel free to let me know - if you think a feature would be useful, either as a player or DM, I'm interested in hearing about it, or I might tell you why it's not on the table.

## Troubleshooting

### Basic Troubleshooting (e.g. "IzduBot isn't responding to my command")

Try enclosing any text (like ability names, character names, etc) in quotes "like so", and if it still doesn't work, check to make sure your command and arguments are spelled correctly and entered per the format. If you're 100% certain you're entering it correctly and it's still not working, contact me with details, and I'll see what's up.

## Contact
If you need (or want) to get in touch, I'm MrMonday#7732 on Discord, or email me at mohanbharath@gmail.com **with [IzduBot] in the subject line**.
