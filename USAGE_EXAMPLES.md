# D&D Encounter Tracker - Usage Examples

This document provides comprehensive examples of using the D&D Encounter Tracker for various scenarios.

## Table of Contents

1. [Quick Start Examples](#quick-start-examples)
2. [Complete Combat Scenarios](#complete-combat-scenarios)
3. [Advanced Usage Patterns](#advanced-usage-patterns)
4. [Interactive Mode Examples](#interactive-mode-examples)
5. [Troubleshooting Examples](#troubleshooting-examples)

## Quick Start Examples

### Creating Your First Encounter

```bash
# Create a new encounter
$ python -m dnd_encounter_tracker new "Goblin Ambush"
✓ Created new encounter: Goblin Ambush
ℹ Add combatants with: add <name> <hp> <initiative> [type]

# Add player characters
$ python -m dnd_encounter_tracker add Thorin 45 18 player
✓ Added Player 'Thorin'
HP: 45, Initiative: 18

# Add monsters
$ python -m dnd_encounter_tracker add "Goblin Scout" 7 12 monster
✓ Added Monster 'Goblin Scout'
HP: 7, Initiative: 12

# View the encounter
$ python -m dnd_encounter_tracker show
Encounter: Goblin Ambush
Round: 1

Initiative Order:
>>> 18 | Thorin               | HP: 45/45     | Player
    12 | Goblin Scout         | HP: 7/7       | Monster
```

### Basic Combat Actions

```bash
# Thorin attacks and deals damage to the goblin
$ python -m dnd_encounter_tracker hp "Goblin Scout" -5
✓ Updated Goblin Scout's HP: 7 → 2 (CRITICAL)

# Goblin attacks Thorin
$ python -m dnd_encounter_tracker hp Thorin -8
✓ Updated Thorin's HP: 45 → 37

# Add a status effect
$ python -m dnd_encounter_tracker note add Thorin "Poisoned (1d4 damage/turn)"
✓ Added note to Thorin: "Poisoned (1d4 damage/turn)"

# Advance to next turn
$ python -m dnd_encounter_tracker next
Round 1
Current turn: Goblin Scout

# Save the encounter
$ python -m dnd_encounter_tracker save goblin_ambush
✓ Saved encounter 'Goblin Ambush' to goblin_ambush.json
```

## Complete Combat Scenarios

### Scenario 1: Tavern Brawl

A chaotic fight breaks out in a tavern with multiple participants.

```bash
# Set up the encounter
$ python -m dnd_encounter_tracker new "Tavern Brawl"
$ python -m dnd_encounter_tracker add "Bard (PC)" 32 16 player
$ python -m dnd_encounter_tracker add "Rogue (PC)" 28 19 player
$ python -m dnd_encounter_tracker add "Drunk Patron" 12 8 npc
$ python -m dnd_encounter_tracker add "Tavern Keeper" 18 10 npc
$ python -m dnd_encounter_tracker add "Town Guard" 25 14 npc

# View initial setup
$ python -m dnd_encounter_tracker show
Encounter: Tavern Brawl
Round: 1

Initiative Order:
>>> 19 | Rogue (PC)           | HP: 28/28     | Player
    16 | Bard (PC)            | HP: 32/32     | Player
    14 | Town Guard           | HP: 25/25     | NPC
    10 | Tavern Keeper        | HP: 18/18     | NPC
     8 | Drunk Patron         | HP: 12/12     | NPC

# Round 1: Rogue's turn - tries to calm things down
$ python -m dnd_encounter_tracker note add "Rogue (PC)" "Attempting to de-escalate"
$ python -m dnd_encounter_tracker next

# Bard's turn - casts sleep spell
$ python -m dnd_encounter_tracker note add "Bard (PC)" "Concentration: Sleep spell"
$ python -m dnd_encounter_tracker hp "Drunk Patron" 0
$ python -m dnd_encounter_tracker note add "Drunk Patron" "Unconscious (Sleep spell)"
$ python -m dnd_encounter_tracker next

# Town Guard tries to arrest the bard
$ python -m dnd_encounter_tracker hp "Bard (PC)" -6
$ python -m dnd_encounter_tracker note add "Bard (PC)" "Grappled by guard"
$ python -m dnd_encounter_tracker next

# Continue the encounter...
$ python -m dnd_encounter_tracker save tavern_brawl
```

### Scenario 2: Dragon Boss Fight

A climactic battle against an ancient dragon with multiple phases.

```bash
# Create the encounter
$ python -m dnd_encounter_tracker new "Ancient Red Dragon"

# Add the party
$ python -m dnd_encounter_tracker add "Paladin" 68 12 player
$ python -m dnd_encounter_tracker add "Wizard" 45 15 player
$ python -m dnd_encounter_tracker add "Ranger" 52 18 player
$ python -m dnd_encounter_tracker add "Cleric" 48 10 player

# Add the dragon and minions
$ python -m dnd_encounter_tracker add "Ancient Red Dragon" 546 17 monster
$ python -m dnd_encounter_tracker add "Kobold Minion 1" 5 14 monster
$ python -m dnd_encounter_tracker add "Kobold Minion 2" 5 13 monster

# Dragon breathes fire on the party
$ python -m dnd_encounter_tracker hp Paladin -28
$ python -m dnd_encounter_tracker hp Wizard -35
$ python -m dnd_encounter_tracker hp Ranger -22
$ python -m dnd_encounter_tracker hp Cleric -30

# Add conditions from the breath weapon
$ python -m dnd_encounter_tracker note add Wizard "Fire resistance (potion)"
$ python -m dnd_encounter_tracker note add Cleric "Concentration: Shield of Faith"

# Wizard casts fireball, kills minions
$ python -m dnd_encounter_tracker hp "Kobold Minion 1" 0
$ python -m dnd_encounter_tracker hp "Kobold Minion 2" 0
$ python -m dnd_encounter_tracker hp "Ancient Red Dragon" -28

# Cleric heals the party
$ python -m dnd_encounter_tracker hp Paladin +22
$ python -m dnd_encounter_tracker hp Wizard +18

# Show current status
$ python -m dnd_encounter_tracker show --details
```

### Scenario 3: Stealth Mission Gone Wrong

A stealth mission that escalates into combat partway through.

```bash
# Start with stealth encounter
$ python -m dnd_encounter_tracker new "Infiltration"
$ python -m dnd_encounter_tracker add "Rogue" 35 20 player
$ python -m dnd_encounter_tracker add "Ranger" 42 17 player

# Add guards (not yet in combat)
$ python -m dnd_encounter_tracker add "Guard Captain" 58 16 monster
$ python -m dnd_encounter_tracker add "Elite Guard 1" 32 14 monster
$ python -m dnd_encounter_tracker add "Elite Guard 2" 32 13 monster

# Rogue gets spotted, combat begins
$ python -m dnd_encounter_tracker note add Rogue "Hidden (advantage on next attack)"
$ python -m dnd_encounter_tracker note add "Guard Captain" "Surprised (can't act first round)"

# Rogue sneak attacks
$ python -m dnd_encounter_tracker hp "Guard Captain" -24
$ python -m dnd_encounter_tracker note add "Guard Captain" "Sneak attack damage"

# Ranger shoots with bow
$ python -m dnd_encounter_tracker hp "Elite Guard 1" -12

# Guards raise alarm
$ python -m dnd_encounter_tracker note add "Elite Guard 2" "Shouting for reinforcements"

# Add reinforcements mid-combat
$ python -m dnd_encounter_tracker add "Reinforcement 1" 11 8 monster
$ python -m dnd_encounter_tracker add "Reinforcement 2" 11 7 monster

# Update initiative order automatically
$ python -m dnd_encounter_tracker show
```

## Advanced Usage Patterns

### Managing Large Encounters

```bash
# Create encounter with many combatants
$ python -m dnd_encounter_tracker new "Mass Battle"

# Add groups of similar creatures efficiently
$ python -m dnd_encounter_tracker add "Orc Warrior 1" 15 12 monster
$ python -m dnd_encounter_tracker add "Orc Warrior 2" 15 11 monster
$ python -m dnd_encounter_tracker add "Orc Warrior 3" 15 10 monster
$ python -m dnd_encounter_tracker add "Orc Warrior 4" 15 9 monster
$ python -m dnd_encounter_tracker add "Orc Warrior 5" 15 8 monster

# Use area effect spells
$ python -m dnd_encounter_tracker hp "Orc Warrior 1" -14
$ python -m dnd_encounter_tracker hp "Orc Warrior 2" -14
$ python -m dnd_encounter_tracker hp "Orc Warrior 3" -14
$ python -m dnd_encounter_tracker note add Wizard "Concentration: Fireball aftermath"

# Remove defeated enemies
$ python -m dnd_encounter_tracker remove "Orc Warrior 1"
$ python -m dnd_encounter_tracker remove "Orc Warrior 2"
```

### Complex Status Effect Management

```bash
# Spell with multiple effects
$ python -m dnd_encounter_tracker note add Paladin "Bless (+1d4 to attacks and saves, 3 rounds)"
$ python -m dnd_encounter_tracker note add Cleric "Concentration: Bless spell"

# Ongoing damage effects
$ python -m dnd_encounter_tracker note add "Fire Elemental" "Burning (2d6 fire damage/turn)"
$ python -m dnd_encounter_tracker hp "Fire Elemental" -7  # Apply burning damage

# Temporary hit points
$ python -m dnd_encounter_tracker note add Barbarian "Temp HP: 12 (Inspiring Leader)"
$ python -m dnd_encounter_tracker hp Barbarian +12  # Add temp HP

# Duration tracking
$ python -m dnd_encounter_tracker note edit Paladin 1 "Bless (+1d4 to attacks and saves, 2 rounds)"
$ python -m dnd_encounter_tracker note edit Paladin 1 "Bless (+1d4 to attacks and saves, 1 round)"
$ python -m dnd_encounter_tracker note remove Paladin 1  # Spell ends
```

### Initiative Adjustments

```bash
# Character delays their turn
$ python -m dnd_encounter_tracker init Wizard 5  # Move to later in initiative

# Ready action changes initiative
$ python -m dnd_encounter_tracker note add Ranger "Ready action: Shoot when dragon lands"
$ python -m dnd_encounter_tracker init Ranger 16  # Adjust for ready action

# Spell effects change initiative
$ python -m dnd_encounter_tracker note add Rogue "Haste spell (+1 AC, +2 Dex saves, extra action)"
$ python -m dnd_encounter_tracker init Rogue 25  # Haste increases initiative
```

## Interactive Mode Examples

### Starting Interactive Session

```bash
$ python -m dnd_encounter_tracker
D&D Encounter Tracker - Interactive Mode
Type 'help' for commands or 'quit' to exit.

[No Encounter] > help
D&D Encounter Tracker - Interactive Mode Help
============================================

BASIC COMMANDS:
  help                    Show this help message
  new <name>             Create a new encounter
  load <filename>        Load a saved encounter
  ...

[No Encounter] > new "Quick Combat"
✓ Created new encounter: Quick Combat

[Quick Combat] > add Fighter 58 15 player
✓ Added Player 'Fighter'

[Quick Combat] > add Orc 15 12 monster
✓ Added Monster 'Orc'

[Quick Combat] > show
Encounter: Quick Combat
Round: 1

Initiative Order:
>>> 15 | Fighter              | HP: 58/58     | Player
    12 | Orc                  | HP: 15/15     | Monster

[Quick Combat] > h Fighter -8    # Short form for 'hp'
✓ Updated Fighter's HP: 58 → 50

[Quick Combat] > next
Round 1
Current turn: Orc

[Quick Combat] > save
✓ Saved encounter 'Quick Combat' to quick_combat.json

[Quick Combat] > quit
Goodbye!
```

### Complex Interactive Session

```bash
[Dragon Lair] > status
Encounter: Dragon Lair
Round: 3

Initiative Order:
    20 | Rogue                | HP: 28/35     | Player 📝
>>> 18 | Young Red Dragon     | HP: 178/200   | Monster 📝
    15 | Wizard               | HP: 22/40     | Player 📝
    12 | Fighter              | HP: 45/65     | Player

[Dragon Lair] > note list Rogue
Notes for Rogue:
  1. Hidden (advantage on next attack)
  2. Sneak attack ready

[Dragon Lair] > note list "Young Red Dragon"
Notes for Young Red Dragon:
  1. Breath weapon recharging (roll 5-6 on d6)
  2. Frightful presence active

[Dragon Lair] > h "Young Red Dragon" -35    # Rogue sneak attack
✓ Updated Young Red Dragon's HP: 178 → 143

[Dragon Lair] > note remove Rogue 1         # No longer hidden
✓ Removed note 1 from Rogue: "Hidden (advantage on next attack)"

[Dragon Lair] > next
Round 3
Current turn: Wizard

[Dragon Lair] > note add Wizard "Concentration: Counterspell ready"
✓ Added note to Wizard: "Concentration: Counterspell ready"
```

## Troubleshooting Examples

### Common Error Scenarios

#### Combatant Not Found

```bash
$ python -m dnd_encounter_tracker hp Thrain -5
✗ Combatant 'Thrain' not found
ℹ Did you mean: Thorin?

# Solution: Check spelling or use correct name
$ python -m dnd_encounter_tracker show
$ python -m dnd_encounter_tracker hp Thorin -5
✓ Updated Thorin's HP: 45 → 40
```

#### Invalid HP Values

```bash
$ python -m dnd_encounter_tracker hp Thorin abc
✗ Invalid HP value: HP value must be a number
ℹ Current HP: 40/45
ℹ Examples: 25 (set to 25), +8 (heal 8), -12 (damage 12)

# Solution: Use proper format
$ python -m dnd_encounter_tracker hp Thorin -12
✓ Updated Thorin's HP: 40 → 28
```

#### File Loading Issues

```bash
$ python -m dnd_encounter_tracker load nonexistent
✗ Failed to load encounter 'nonexistent': File not found or corrupted
ℹ Available encounters: goblin_ambush, tavern_brawl, dragon_fight

# Solution: Use correct filename
$ python -m dnd_encounter_tracker load goblin_ambush
✓ Loaded encounter: Goblin Ambush
```

#### Note Management Errors

```bash
$ python -m dnd_encounter_tracker note edit Thorin 5 "New note"
✗ Note index 5 out of range for Thorin (has 2 notes)
ℹ Use 'note list Thorin' to see available notes

# Solution: Check available notes first
$ python -m dnd_encounter_tracker note list Thorin
Notes for Thorin:
  1. Poisoned (1d4 damage/turn)
  2. Blessed (+1d4 to attacks)

$ python -m dnd_encounter_tracker note edit Thorin 2 "Blessed (+1d4 to attacks, 2 rounds left)"
✓ Updated note 2 for Thorin: "Blessed (+1d4 to attacks, 2 rounds left)"
```

### Recovery Scenarios

#### Corrupted Encounter File

```bash
$ python -m dnd_encounter_tracker load corrupted_file
✗ Failed to load encounter 'corrupted_file': Invalid JSON format

# Solution: Load from backup
$ python -m dnd_encounter_tracker load corrupted_file.backup
✓ Loaded encounter from backup

# Or start fresh
$ python -m dnd_encounter_tracker new "Recovered Encounter"
```

#### Accidental Data Loss

```bash
# Accidentally removed wrong combatant
$ python -m dnd_encounter_tracker remove "Important NPC"
✓ Removed combatant 'Important NPC'

# Solution: Re-add immediately (if you remember stats)
$ python -m dnd_encounter_tracker add "Important NPC" 25 14 npc
✓ Added NPC 'Important NPC'

# Or load from last save
$ python -m dnd_encounter_tracker load last_save
```

### Performance Optimization

#### Large Encounter Management

```bash
# For encounters with 20+ combatants
$ python -m dnd_encounter_tracker show          # Quick overview
$ python -m dnd_encounter_tracker combatant "Specific Character"  # Individual details

# Avoid frequent --details flag with large groups
$ python -m dnd_encounter_tracker show --details  # Use sparingly

# Clean up defeated enemies
$ python -m dnd_encounter_tracker remove "Dead Orc 1"
$ python -m dnd_encounter_tracker remove "Dead Orc 2"
```

#### File Management

```bash
# Regular cleanup of old backups
$ python -m dnd_encounter_tracker cleanup --max-backups 3
Cleaned up 5 old backup files:
  - old_encounter_20240101_120000.backup
  - old_encounter_20240102_130000.backup
  ...

# List encounters with metadata
$ python -m dnd_encounter_tracker list --detailed
Available encounters (most recently modified first):
File: dragon_fight.json
Name: Ancient Red Dragon
Created: 2024-01-15 14:30
Modified: 2024-01-15 16:45
Size: 2.3 KB
```

These examples demonstrate the full range of capabilities available in the D&D Encounter Tracker. Use them as templates for your own encounters and adapt the patterns to fit your specific gameplay needs.