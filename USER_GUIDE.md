# D&D Encounter Tracker - Complete User Guide

Welcome to the D&D Encounter Tracker! This comprehensive guide will help you master all features of this powerful combat management tool.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation & Setup](#installation--setup)
3. [Basic Commands](#basic-commands)
4. [Advanced Features](#advanced-features)
5. [Interactive Mode](#interactive-mode)
6. [Command Aliases & Shortcuts](#command-aliases--shortcuts)
7. [Visual Indicators & Colors](#visual-indicators--colors)
8. [Combat Workflow Guide](#combat-workflow-guide)
9. [Tips & Best Practices](#tips--best-practices)
10. [Troubleshooting](#troubleshooting)

## Quick Start

### 30-Second Setup

```bash
# Start interactive mode (easiest for beginners)
python -m dnd_encounter_tracker

# Or create your first encounter directly
python -m dnd_encounter_tracker new "My First Fight"
python -m dnd_encounter_tracker add Hero 50 15 player
python -m dnd_encounter_tracker add Goblin 7 12 monster
python -m dnd_encounter_tracker show
```

### Your First Combat Round

```bash
# In interactive mode:
> new "Goblin Ambush"
> add Thorin 45 18 player
> add "Goblin Scout" 7 12 monster
> show                    # See initiative order
> hp "Goblin Scout" -5    # Thorin attacks for 5 damage
> next                    # Advance to goblin's turn
> hp Thorin -3            # Goblin attacks for 3 damage
> save goblin_fight       # Save your progress
```

## Installation & Setup

### Requirements

- Python 3.7 or higher
- No additional dependencies required (uses only standard library)

### Installation Options

#### Option 1: Direct Download
```bash
# Download and run directly
git clone <repository-url>
cd dnd-encounter-tracker
python -m dnd_encounter_tracker
```

#### Option 2: System Installation
```bash
# Install system-wide (if setup.py is available)
pip install -e .
dnd-encounter-tracker
```

### First Run

The application will create necessary directories automatically:
- `encounters/` - Saved encounter files
- Backup files are created automatically when overwriting

## Basic Commands

### Essential Commands Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `new` | Create encounter | `new "Dragon Fight"` |
| `add` | Add combatant | `add Thorin 45 18 player` |
| `hp` | Update hit points | `hp Thorin -8` |
| `show` | Display encounter | `show` |
| `next` | Next turn | `next` |
| `save` | Save encounter | `save my_fight` |
| `load` | Load encounter | `load my_fight` |

### Command Syntax Patterns

#### Adding Combatants
```bash
add <name> <max_hp> <initiative> [type]

# Examples:
add Thorin 45 18 player
add "Goblin Scout" 7 12 monster
add Shopkeeper 15 10 npc
add "Unknown Assassin" 25 20    # type defaults to 'unknown'
```

#### HP Management
```bash
hp <name> <value>

# Absolute values:
hp Thorin 25        # Set HP to exactly 25

# Relative changes:
hp Thorin -8        # Subtract 8 HP (damage)
hp Thorin +5        # Add 5 HP (healing)
```

#### Note Management
```bash
note <action> <name> [arguments]

# Examples:
note add Thorin "Blessed by cleric"
note list Thorin
note edit Thorin 1 "Blessed (+1d4 to attacks)"
note remove Thorin 2
note show           # Show all combatants with notes
```

## Advanced Features

### Initiative Management

#### Automatic Sorting
- Combatants are automatically sorted by initiative (highest first)
- Order updates automatically when initiative changes
- Current turn is clearly marked with `>>>`

#### Manual Adjustments
```bash
# Change initiative (triggers automatic re-sort)
init Thorin 20

# Handle ready actions
init Ranger 16      # Ranger readies action, moves in initiative
note add Ranger "Ready: Shoot when dragon lands"

# Delay turns
init Wizard 5       # Wizard delays, moves to later in round
```

### Complex HP Scenarios

#### Temporary Hit Points
```bash
# Add temporary HP as a note, then add to current HP
note add Barbarian "Temp HP: 12 (Inspiring Leader)"
hp Barbarian +12

# When temp HP is lost, subtract and update note
hp Barbarian -8
note edit Barbarian 1 "Temp HP: 4 (Inspiring Leader)"
```

#### Massive Damage
```bash
# System automatically prevents negative HP
hp Goblin -50       # If goblin has 7 HP, result is 0 HP
```

#### Healing Above Maximum
```bash
# System automatically caps at maximum HP
hp Thorin +100      # If max is 45, result is 45 HP
```

### Advanced Note Management

#### Duration Tracking
```bash
# Add spell with duration
note add Paladin "Bless (+1d4 attacks/saves, 10 rounds)"

# Update each round
note edit Paladin 1 "Bless (+1d4 attacks/saves, 9 rounds)"
note edit Paladin 1 "Bless (+1d4 attacks/saves, 8 rounds)"

# Remove when expired
note remove Paladin 1
```

#### Concentration Tracking
```bash
# Track concentration spells
note add Wizard "Concentration: Fireball"
note add Cleric "Concentration: Hold Person on Orc"

# When concentration breaks
note remove Wizard 1
note remove Cleric 1
```

#### Status Effects
```bash
# Ongoing effects
note add Rogue "Poisoned (1d4 damage/turn, 3 rounds)"
note add Fighter "Grappled by Owlbear"
note add Barbarian "Rage (+2 damage, resist physical)"

# Beneficial effects
note add Ranger "Hunter's Mark on Dragon (+1d6 damage)"
note add Paladin "Divine Favor (+1d4 radiant damage)"
```

### File Management

#### Backup System
```bash
# Manual backup creation
backup my_encounter

# Automatic backups when overwriting
save existing_encounter    # Creates backup automatically

# Cleanup old backups
cleanup --max-backups 5    # Keep only 5 most recent backups
```

#### Encounter Organization
```bash
# List with details
list --detailed

# Shows:
# - File size
# - Creation date
# - Last modified
# - Encounter name
```

## Interactive Mode

### Starting Interactive Mode

```bash
# Method 1: Explicit command
python -m dnd_encounter_tracker interactive

# Method 2: No arguments (auto-starts interactive)
python -m dnd_encounter_tracker

# Method 3: From within command mode
python -m dnd_encounter_tracker interactive
```

### Interactive Features

#### Smart Prompts
```
[No Encounter] >           # No encounter loaded
[Goblin Fight] >           # Clean encounter
[Goblin Fight*] >          # Unsaved changes (asterisk)
```

#### Special Commands
```bash
# Interactive-only commands
status                     # Show session status
clear                      # Clear screen
help                       # Interactive help
quit, exit, q             # Exit program
```

#### Command History
- Use ↑/↓ arrow keys to navigate command history
- Repeat previous commands easily
- Edit previous commands before re-running

### Interactive Workflow Example

```
$ python -m dnd_encounter_tracker
D&D Encounter Tracker - Interactive Mode
========================================

[No Encounter] > new "Tavern Brawl"
✓ Created new encounter: Tavern Brawl

[Tavern Brawl] > a Bard 32 16 player        # 'a' is alias for 'add'
✓ Added Player 'Bard'

[Tavern Brawl] > a "Drunk Patron" 12 8 npc
✓ Added NPC 'Drunk Patron'

[Tavern Brawl] > show
Encounter: Tavern Brawl
Round: 1

Initiative Order:
>>> 16 | Bard                 | HP: 32/32     | Player
     8 | Drunk Patron         | HP: 12/12     | NPC

[Tavern Brawl] > h Bard -5                   # 'h' is alias for 'hp'
✓ Updated Bard's HP: 32 → 27

[Tavern Brawl] > next
Round 1
Current turn: Drunk Patron

[Tavern Brawl] > save
✓ Saved encounter 'Tavern Brawl' to tavern_brawl.json

[Tavern Brawl] > quit
Goodbye!
```

## Command Aliases & Shortcuts

### Primary Aliases

| Full Command | Aliases | Usage |
|--------------|---------|-------|
| `new` | `n`, `create` | `n "Fight"` |
| `add` | `a` | `a Orc 15 12 monster` |
| `remove` | `r`, `rm`, `del` | `r Orc` |
| `hp` | `h`, `health` | `h Orc -8` |
| `init` | `i`, `initiative` | `i Orc 15` |
| `show` | `display`, `view`, `status` | `show` |
| `combatant` | `c`, `char`, `character` | `c Orc` |
| `next` | `advance`, `next-turn` | `next` |
| `save` | `s`, `write` | `s fight` |
| `load` | `l`, `open` | `l fight` |
| `list` | `ls`, `dir` | `ls` |
| `help` | `?`, `man` | `?` |

### Contextual Shortcuts

#### HP Shortcuts
```bash
# Instead of: hp Orc -damage
hurt Orc 8          # Equivalent to: hp Orc -8
damage Orc 12       # Equivalent to: hp Orc -12

# Instead of: hp Orc +healing
heal Orc 5          # Equivalent to: hp Orc +5
restore Orc 10      # Equivalent to: hp Orc +10

# Special states
kill Orc            # Equivalent to: hp Orc 0
dead Orc            # Equivalent to: hp Orc 0
revive Orc          # Equivalent to: hp Orc 1
```

#### Initiative Shortcuts
```bash
# Quick adjustments
fast Orc            # Equivalent to: init Orc +5
slow Orc            # Equivalent to: init Orc -5
first Orc           # Equivalent to: init Orc 30
last Orc            # Equivalent to: init Orc 1
```

### Typo Correction

The system automatically corrects common typos:

| Typo | Corrected To | Typo | Corrected To |
|------|--------------|------|--------------|
| `ad` | `add` | `sav` | `save` |
| `remov` | `remove` | `loa` | `load` |
| `sho` | `show` | `nex` | `next` |
| `hel` | `help` | `lis` | `list` |
| `combatan` | `combatant` | `initt` | `init` |

## Visual Indicators & Colors

### HP Status Colors

| Color | Status | HP Range | Example |
|-------|--------|----------|---------|
| 🟢 Green | Healthy | >50% HP | `45/45` |
| 🟡 Yellow | Wounded | 25-50% HP | `22/45` |
| 🔴 Red | Critical | 1-25% HP | `8/45 (CRITICAL)` |
| ⚫ Bright Red | Dead | 0 HP | `0/45 (DEAD)` |

### Combatant Type Colors

| Type | Color | Example |
|------|-------|---------|
| Player | 🔵 Bright Blue | `Thorin` |
| Monster | 🔴 Bright Red | `Goblin Scout` |
| NPC | 🟣 Bright Magenta | `Shopkeeper` |
| Unknown | ⚪ Dim Gray | `Mysterious Figure` |

### Message Types

| Symbol | Color | Meaning | Example |
|--------|-------|---------|---------|
| ✓ | 🟢 Green | Success | `✓ Added Player 'Thorin'` |
| ✗ | 🔴 Red | Error | `✗ Combatant not found` |
| ⚠ | 🟡 Yellow | Warning | `⚠ HP exceeds maximum` |
| ℹ | 🔵 Blue | Information | `ℹ Use 'help hp' for guide` |

### Special Indicators

| Symbol | Meaning | Usage |
|--------|---------|-------|
| `>>>` | Current turn | Initiative order |
| `📝` | Has notes | Combatant display |
| `*` | Unsaved changes | Interactive prompt |
| `💀` | Critical status | Death/unconscious |
| `⚔️` | Combat action | Action descriptions |
| `✨` | Spell effect | Magical effects |

### Disabling Colors

If colors don't display correctly:

```bash
# Disable colors via environment variable
export NO_COLOR=1
python -m dnd_encounter_tracker

# Colors auto-disable for:
# - Non-terminal output (pipes, files)
# - Unsupported terminals
# - When NO_COLOR environment variable is set
```

## Combat Workflow Guide

### Pre-Combat Setup

#### 1. Create Encounter
```bash
new "Encounter Name"
```

#### 2. Add All Combatants
```bash
# Players first (easier to track)
add "Player 1" 45 18 player
add "Player 2" 38 16 player

# Then NPCs/Allies
add "Friendly NPC" 25 14 npc

# Finally enemies
add "Boss Monster" 120 15 monster
add "Minion 1" 8 12 monster
add "Minion 2" 8 11 monster
```

#### 3. Verify Setup
```bash
show                    # Check initiative order
show --details          # Full combatant details if needed
```

### During Combat

#### Round Structure
```bash
# Start of each round
show                    # See whose turn it is

# For each combatant's turn:
# 1. Resolve actions
hp Target -damage       # Apply damage
hp Healer +healing      # Apply healing

# 2. Track effects
note add Combatant "Status effect"
note edit Combatant 1 "Updated effect"
note remove Combatant 2  # Remove expired effects

# 3. Advance turn
next                    # Move to next combatant
```

#### Common Combat Actions

##### Damage Resolution
```bash
# Single target damage
hp Goblin -12

# Area effect damage
hp Goblin1 -14
hp Goblin2 -14
hp Goblin3 -14

# Massive damage (auto-kills)
hp Minion -50           # Sets to 0 HP if overkill
```

##### Healing
```bash
# Healing spells
hp Cleric +8
hp Fighter +12

# Healing potions
hp Rogue +7
note add Rogue "Used healing potion"
```

##### Status Effects
```bash
# Apply conditions
note add Target "Poisoned (1d4 damage/turn)"
note add Caster "Concentration: Hold Person"

# Track durations
note edit Target 1 "Poisoned (1d4 damage/turn, 2 rounds left)"

# Remove expired effects
note remove Target 1
```

##### Initiative Changes
```bash
# Ready actions
init Ranger 12          # Ranger readies, moves in initiative
note add Ranger "Ready: Attack when enemy moves"

# Delay turns
init Wizard 5           # Wizard delays turn

# Spell effects on initiative
init Rogue 25           # Haste spell increases initiative
```

### End of Combat

#### Cleanup
```bash
# Remove defeated enemies (optional)
remove "Dead Goblin 1"
remove "Dead Goblin 2"

# Clear temporary effects
note remove Barbarian 1  # Remove rage
note remove Wizard 1     # Remove concentration spell
```

#### Save Progress
```bash
save encounter_name     # Save final state
backup encounter_name   # Create backup if needed
```

### Between Sessions

#### Session Preparation
```bash
# Review available encounters
list --detailed

# Load previous session
load last_session

# Check encounter state
show --details
```

#### Session Continuation
```bash
# Reset for new combat
# Option 1: Modify existing encounter
hp Player1 45           # Reset to full HP
hp Player2 38
note remove Player1 1   # Clear old effects

# Option 2: Create new encounter
new "Session 2 - Cave Entrance"
# Re-add combatants with current stats
```

## Tips & Best Practices

### Naming Conventions

#### Effective Names
```bash
# Good: Short, memorable, unique
add Thorin 45 18 player
add Goblin1 7 12 monster
add Goblin2 7 11 monster
add Boss 120 15 monster

# Avoid: Long, complex, similar names
add "Thorin Oakenshield the Dwarf Fighter" 45 18 player  # Too long
add "Goblin Scout" 7 12 monster
add "Goblin Warrior" 7 11 monster                        # Too similar
```

#### Handling Duplicates
```bash
# Use numbers for identical creatures
add Orc1 15 12 monster
add Orc2 15 11 monster
add Orc3 15 10 monster

# Or descriptive suffixes
add "Orc Leader" 25 14 monster
add "Orc Grunt" 15 12 monster
add "Orc Archer" 12 16 monster
```

### Combat Management

#### Initiative Best Practices
```bash
# Roll initiative for groups of identical monsters together
add Goblin1 7 12 monster
add Goblin2 7 12 monster    # Same initiative = group turn
add Goblin3 7 12 monster

# Use distinctive initiatives for important NPCs
add "Boss Monster" 120 15 monster    # Unique initiative
add "Lieutenant" 45 14 monster       # Slightly different
```

#### HP Tracking Tips
```bash
# Use relative changes during combat (easier to track)
hp Fighter -8           # Damage taken
hp Fighter +5           # Healing received

# Use absolute values for major changes
hp Fighter 0            # Knocked unconscious
hp Fighter 1            # Stabilized/revived
hp Fighter 45           # Full heal (long rest)
```

#### Note Management Strategy
```bash
# Be specific about effects
note add Fighter "Poisoned (1d4 damage/turn, 3 rounds)"
note add Wizard "Concentration: Fireball"
note add Rogue "Hidden (advantage on next attack)"

# Include mechanical effects
note add Paladin "Bless (+1d4 to attacks and saves)"
note add Barbarian "Rage (+2 damage, resist physical)"

# Track resources
note add Cleric "Spell slots: 3/4 level 1, 2/3 level 2"
note add Fighter "Action Surge used"
```

### File Organization

#### Encounter Naming
```bash
# Use descriptive, sortable names
save "01_goblin_ambush"
save "02_tavern_brawl"
save "03_dragon_lair"

# Include session information
save "session_5_cave_entrance"
save "session_5_underground_lake"
```

#### Backup Strategy
```bash
# Create manual backups before major changes
backup important_encounter

# Regular cleanup
cleanup --max-backups 3    # Keep recent backups only
```

### Performance Optimization

#### Large Encounters
```bash
# For 15+ combatants, use efficient commands
show                    # Quick overview
combatant SpecificName  # Individual details only when needed

# Avoid frequent --details with large groups
show --details          # Use sparingly

# Remove defeated enemies to reduce clutter
remove DefeatedEnemy1
remove DefeatedEnemy2
```

#### Session Management
```bash
# Save frequently during long sessions
save current_state      # After each major event

# Use status to check for unsaved changes
status                  # Shows if save is needed
```

## Troubleshooting

### Common Error Messages

#### "Combatant not found"
```bash
# Error example:
> hp Thrain -5
✗ Combatant 'Thrain' not found
ℹ Did you mean: Thorin?

# Solutions:
show                    # Check exact names
combatant Thorin        # Verify spelling
hp Thorin -5           # Use correct name
```

#### "Invalid HP value"
```bash
# Error example:
> hp Thorin abc
✗ Invalid HP value: HP value must be a number
ℹ Examples: 25 (set to 25), +8 (heal 8), -12 (damage 12)

# Solutions:
hp Thorin -8           # Use number
hp Thorin +5           # Use +/- for relative
hp Thorin 25           # Use absolute value
```

#### "File not found"
```bash
# Error example:
> load missing_file
✗ Failed to load encounter 'missing_file': File not found
ℹ Available encounters: goblin_fight, dragon_lair

# Solutions:
list                   # Check available files
load goblin_fight      # Use existing file
new "New Encounter"    # Create new instead
```

### Recovery Procedures

#### Corrupted Encounter File
```bash
# If encounter won't load:
load encounter_name.backup    # Try backup file
list --detailed              # Check file status

# If backup doesn't exist:
new "Recovered Encounter"    # Start fresh
# Re-add combatants manually
```

#### Accidental Data Loss
```bash
# Accidentally removed combatant:
add "Restored Name" HP INIT TYPE    # Re-add immediately

# Accidentally overwrote file:
load filename.backup               # Load backup
save filename                      # Restore original
```

#### Session Recovery
```bash
# If session crashes or closes unexpectedly:
list --detailed                    # Check last modified files
load most_recent_encounter         # Resume from last save
status                            # Check current state
```

### Performance Issues

#### Slow Response Times
```bash
# For very large encounters (20+ combatants):
# Use specific commands instead of show --details
combatant SpecificName    # Individual lookup
note list SpecificName    # Specific note check

# Clean up old data:
cleanup --max-backups 3   # Remove old backups
remove DefeatedEnemy      # Remove unnecessary combatants
```

#### Memory Usage
```bash
# If running multiple long sessions:
# Exit and restart periodically
quit                      # Exit interactive mode
python -m dnd_encounter_tracker  # Restart fresh
load current_encounter    # Resume session
```

### Getting Additional Help

#### Built-in Help System
```bash
help                      # General help
help commands             # Command reference
help examples             # Usage examples
help workflow             # Combat workflow
help hp                   # HP management
help notes                # Note management
help aliases              # Shortcuts and aliases
help colors               # Visual indicators
```

#### Interactive Help
```bash
# In interactive mode:
?                         # Quick help
help interactive          # Interactive-specific help
status                    # Current session info
```

#### Command-Specific Help
```bash
# Most commands show usage when run incorrectly:
add                       # Shows: Usage: add <n> <hp> <initiative> [type]
note                      # Shows available note actions
hp Thorin                 # Shows: Usage: hp <n> <value>
```

---

This guide covers all features of the D&D Encounter Tracker. For additional examples and advanced scenarios, see the `USAGE_EXAMPLES.md` file. Happy gaming!