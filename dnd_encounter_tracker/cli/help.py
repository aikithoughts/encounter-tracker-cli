"""Help system for D&D Encounter Tracker CLI."""

from typing import Dict, List


class HelpManager:
    """Manages help documentation and examples."""
    
    def __init__(self):
        """Initialize help manager."""
        self.help_topics = {
            'commands': self._get_commands_help,
            'examples': self._get_examples_help,
            'workflow': self._get_workflow_help,
            'notes': self._get_notes_help,
            'hp': self._get_hp_help,
            'initiative': self._get_initiative_help,
            'interactive': self._get_interactive_help,
            'aliases': self._get_aliases_help,
            'colors': self._get_colors_help
        }
    
    def show_help_topic(self, topic: str) -> None:
        """Show help for a specific topic.
        
        Args:
            topic: Help topic to display
        """
        if topic in self.help_topics:
            print(self.help_topics[topic]())
        else:
            print(f"Unknown help topic: {topic}")
            print("Available topics:", ", ".join(self.help_topics.keys()))
    
    def show_interactive_help(self) -> None:
        """Show help for interactive mode."""
        print(self._get_interactive_help())
    
    def show_command_help(self) -> None:
        """Show comprehensive command help."""
        print(self._get_commands_help())
    
    def _get_interactive_help(self) -> str:
        """Get interactive mode help text."""
        return """
D&D Encounter Tracker - Interactive Mode Help
============================================

BASIC COMMANDS:
  help                    Show this help message
  help <topic>           Show help for specific topic
  status                 Show current session status
  clear                  Clear the screen
  exit, quit, q          Exit the program

ENCOUNTER MANAGEMENT:
  new <name>             Create a new encounter
  load <filename>        Load a saved encounter
  save [filename]        Save current encounter
  list                   List available encounters

COMBATANT MANAGEMENT:
  add <name> <hp> <init> [type]    Add a combatant
  remove <name>                    Remove a combatant
  hp <name> <value>               Update hit points
  init <name> <value>             Update initiative

DISPLAY COMMANDS:
  show                   Show encounter summary
  show --details         Show detailed encounter info
  combatant <name>       Show specific combatant details
  next                   Advance to next turn

NOTE MANAGEMENT:
  note add <name> <text>         Add a note
  note list <name>               List notes for combatant
  note edit <name> <index> <text> Edit a note
  note remove <name> <index>     Remove a note
  note show                      Show all combatants with notes

HELP TOPICS:
  help commands          Detailed command reference
  help examples          Usage examples
  help workflow          Typical workflow guide
  help notes             Note management guide
  help hp                Hit point management guide
  help initiative        Initiative system guide
  help aliases           Command shortcuts and aliases
  help colors            Color system and visual indicators

TIPS:
  • Commands are case-insensitive
  • Use quotes for names with spaces: add "Goblin Scout" 7 12
  • Many commands have short aliases: 'a' for add, 'h' for hp, 's' for save
  • The system suggests corrections for typos and invalid commands
  • Colors indicate HP status: green (healthy), yellow (wounded), red (critical)
  • The prompt shows your current encounter name
  • An asterisk (*) in the prompt indicates unsaved changes
  • Press Ctrl+C to interrupt any command
        """.strip()
    
    def _get_commands_help(self) -> str:
        """Get detailed commands help text."""
        return """
D&D Encounter Tracker - Command Reference
========================================

ENCOUNTER MANAGEMENT:
  new <encounter_name>
    Create a new encounter with the specified name.
    Example: new "Goblin Ambush"

  load <filename>
    Load a previously saved encounter from file.
    Example: load goblin_ambush

  save <filename>
    Save the current encounter to a file.
    Example: save goblin_ambush

  list
    Display all available saved encounters.

COMBATANT MANAGEMENT:
  add <name> <max_hp> <initiative> [type]
    Add a new combatant to the encounter.
    Types: player, monster, npc, unknown (default)
    Example: add Thorin 45 18 player
    Example: add "Goblin Scout" 7 12 monster

  remove <name>
    Remove a combatant from the encounter.
    Example: remove Thorin

  hp <name> <value>
    Update a combatant's hit points.
    Formats:
      - Absolute value: hp Thorin 25
      - Addition: hp Thorin +8
      - Subtraction: hp Thorin -12

  init <name> <value>
    Set a combatant's initiative to a new value.
    Example: init Thorin 20

DISPLAY COMMANDS:
  show [--details]
    Display the current encounter.
    Use --details for comprehensive information.

  combatant <name>
    Show detailed information about a specific combatant.
    Example: combatant Thorin

  next
    Advance to the next combatant's turn.

NOTE MANAGEMENT:
  note add <name> <note_text>
    Add a note to a combatant.
    Example: note add Thorin "Blessed by cleric"

  note list <name>
    List all notes for a combatant.
    Example: note list Thorin

  note edit <name> <index> <new_text>
    Edit an existing note (1-based index).
    Example: note edit Thorin 1 "Blessed by cleric (+1 to saves)"

  note remove <name> <index>
    Remove a note by index (1-based).
    Example: note remove Thorin 2

  note show
    Show all combatants that have notes.

HELP COMMANDS:
  help [topic]
    Show help information.
    Topics: commands, examples, workflow, notes, hp, initiative
        """.strip()
    
    def _get_examples_help(self) -> str:
        """Get usage examples help text."""
        return """
D&D Encounter Tracker - Usage Examples
=====================================

STARTING A NEW ENCOUNTER:
  > new "Goblin Ambush"
  > add Thorin 45 18 player
  > add Legolas 38 16 player
  > add "Goblin Scout" 7 12 monster
  > add "Goblin Warrior" 11 10 monster
  > show

MANAGING COMBAT:
  > hp Thorin -8          # Thorin takes 8 damage
  > hp "Goblin Scout" 0   # Goblin Scout dies
  > note add Thorin "Poisoned (1d4 damage per turn)"
  > next                  # Advance to next turn
  > show --details        # See full encounter status

WORKING WITH SAVED ENCOUNTERS:
  > save goblin_ambush    # Save current encounter
  > list                  # See all saved encounters
  > load dragon_fight     # Load a different encounter
  > show                  # Display loaded encounter

MANAGING NOTES:
  > note add Legolas "Has inspiration"
  > note add Thorin "AC +2 from shield spell"
  > note list Thorin      # See Thorin's notes
  > note edit Thorin 1 "AC +2 from shield spell (3 rounds left)"
  > note show             # See all combatants with notes

INITIATIVE ADJUSTMENTS:
  > init Thorin 20        # Change Thorin's initiative
  > show                  # See updated initiative order

HP MANAGEMENT EXAMPLES:
  > hp Thorin 25          # Set HP to exactly 25
  > hp Thorin +8          # Add 8 HP (healing)
  > hp Thorin -12         # Subtract 12 HP (damage)

TYPICAL COMBAT ROUND:
  > show                  # See whose turn it is
  > hp "Current Fighter" -6  # Apply damage
  > note add "Current Fighter" "Grappled"
  > next                  # Move to next combatant
  > show                  # See updated status
        """.strip()
    
    def _get_workflow_help(self) -> str:
        """Get workflow guide help text."""
        return """
D&D Encounter Tracker - Typical Workflow
=======================================

SETTING UP AN ENCOUNTER:
1. Create or load an encounter:
   > new "Boss Fight"
   OR
   > load saved_encounter

2. Add all combatants:
   > add "Player 1" 45 18 player
   > add "Player 2" 38 16 player
   > add "Boss Monster" 120 15 monster
   > add "Minion 1" 8 12 monster

3. Verify setup:
   > show

RUNNING COMBAT:
1. Start the first round:
   > show                    # See initiative order

2. For each turn:
   > show                    # Check current turn
   > hp <name> <damage>      # Apply damage/healing
   > note add <name> <effect> # Track conditions
   > next                    # Move to next turn

3. Manage conditions:
   > note list <name>        # Check active effects
   > note edit <name> <index> <updated_text>
   > note remove <name> <index>  # Remove expired effects

4. Handle special situations:
   > init <name> <new_value> # Adjust initiative
   > remove <name>           # Remove defeated enemies
   > add <name> <hp> <init>  # Add reinforcements

SAVING YOUR WORK:
> save encounter_name        # Save progress
> status                     # Check if changes are saved

BETWEEN SESSIONS:
> list                       # See available encounters
> load encounter_name        # Resume previous session
> show --details            # Review full status

TIPS FOR SMOOTH GAMEPLAY:
• Use short, memorable names for combatants
• Add notes immediately when effects are applied
• Save frequently, especially after major events
• Use 'status' to check if you have unsaved changes
• Keep the encounter display visible with 'show'
        """.strip()
    
    def _get_notes_help(self) -> str:
        """Get notes management help text."""
        return """
D&D Encounter Tracker - Note Management Guide
============================================

WHAT ARE NOTES?
Notes help you track temporary effects, conditions, and tactical
information for each combatant during combat.

ADDING NOTES:
  > note add <name> <text>
  
  Examples:
  > note add Thorin "Blessed (+1d4 to attacks)"
  > note add "Goblin Scout" "Poisoned (1d4 damage/turn)"
  > note add Wizard "Concentration: Fireball"

VIEWING NOTES:
  > note list <name>        # Show all notes for one combatant
  > note show              # Show all combatants with notes
  > combatant <name>       # Show combatant details including notes

EDITING NOTES:
  > note edit <name> <index> <new_text>
  
  Example:
  > note edit Thorin 1 "Blessed (+1d4 to attacks, 2 rounds left)"

REMOVING NOTES:
  > note remove <name> <index>
  
  Example:
  > note remove Thorin 1   # Remove first note

NOTE INDEXING:
• Notes are numbered starting from 1 (not 0)
• When you remove a note, other notes renumber automatically
• Always check current notes with 'note list' before editing

COMMON NOTE TYPES:
• Conditions: "Poisoned", "Charmed", "Frightened"
• Buffs/Debuffs: "Blessed", "Bane", "Faerie Fire"
• Concentration: "Concentration: Hold Person"
• Tactical: "Behind cover", "Prone", "Grappled"
• Temporary HP: "Temp HP: 8"
• Duration tracking: "Shield spell (2 rounds left)"

BEST PRACTICES:
• Be specific about effects: "Poisoned (1d4 damage/turn)"
• Include duration when known: "Bless (3 rounds left)"
• Use consistent naming for similar effects
• Remove expired effects promptly
• Use notes for anything you might forget

VISUAL INDICATORS:
• Combatants with notes show a 📝 symbol in the encounter display
• Use 'note show' to quickly see who has active effects
        """.strip()
    
    def _get_hp_help(self) -> str:
        """Get hit points management help text."""
        return """
D&D Encounter Tracker - Hit Points Management
===========================================

HP UPDATE FORMATS:
The 'hp' command supports three different formats for maximum flexibility:

1. ABSOLUTE VALUES:
   > hp Thorin 25
   Sets Thorin's HP to exactly 25 points.

2. DAMAGE (Subtraction):
   > hp Thorin -8
   Subtracts 8 HP from Thorin's current total.
   
3. HEALING (Addition):
   > hp Thorin +12
   Adds 12 HP to Thorin's current total.

HP VALIDATION:
• HP cannot go below 0 (automatically clamped)
• HP cannot exceed maximum HP (automatically clamped)
• Invalid formats will show helpful error messages

HP STATUS INDICATORS:
• Normal: Shows as "current/max" (e.g., "32/45")
• Critical: Shows "current/max (CRITICAL)" when ≤25% of max
• Dead: Shows "0/max (DEAD)" when HP reaches 0

EXAMPLES:
  Starting HP: 45/45
  > hp Thorin -12        # Takes 12 damage → 33/45
  > hp Thorin -20        # Takes 20 damage → 13/45 (CRITICAL)
  > hp Thorin +5         # Heals 5 HP → 18/45
  > hp Thorin 45         # Full heal → 45/45

COMMON SCENARIOS:
• Weapon damage: hp Fighter -8
• Spell damage: hp "Goblin Scout" -14
• Healing potion: hp Rogue +7
• Healing spell: hp Cleric +12
• Massive damage: hp Monster -50
• Setting to unconscious: hp Player 0
• Revival: hp Player 1

TIPS:
• Use negative numbers for damage (easier to read)
• Use positive numbers for healing
• Use absolute values for special situations
• Check status with 'show' after major HP changes
• Critical HP combatants are highlighted in red
        """.strip()
    
    def _get_initiative_help(self) -> str:
        """Get initiative system help text."""
        return """
D&D Encounter Tracker - Initiative System Guide
==============================================

HOW INITIATIVE WORKS:
• Combatants are automatically sorted by initiative (highest first)
• The current turn is marked with ">>>" in the display
• Use 'next' to advance to the next combatant's turn

SETTING INITIATIVE:
When adding combatants:
  > add Thorin 45 18 player    # Initiative 18

Adjusting initiative:
  > init Thorin 20             # Change to initiative 20

INITIATIVE ORDER:
The encounter automatically maintains initiative order:
  >>> 20 | Thorin      | HP: 45/45    | Player
      18 | Legolas     | HP: 38/38    | Player  
      15 | Orc Chief   | HP: 58/58    | Monster
      12 | Orc Warrior | HP: 15/15    | Monster

TURN MANAGEMENT:
  > next                       # Advance to next turn
  > show                       # See whose turn it is

HANDLING INITIATIVE CHANGES:
• When you change someone's initiative, the order updates automatically
• New combatants are inserted in the correct position
• Removed combatants don't affect turn tracking

INITIATIVE TIES:
• If two combatants have the same initiative, manually adjust one:
  > init "Slower Combatant" 17  # Break the tie

ROUND TRACKING:
• Rounds advance automatically when you cycle through all combatants
• The current round number is shown in the encounter display
• Use 'show' to see the current round

COMMON INITIATIVE VALUES:
• Very Fast: 20+ (high Dex characters, some monsters)
• Fast: 15-19 (rogues, rangers, dexterous characters)
• Average: 10-14 (most characters and monsters)
• Slow: 5-9 (heavily armored characters, some monsters)
• Very Slow: 0-4 (surprised or heavily encumbered)

TIPS:
• Roll initiative for groups of identical monsters together
• Use distinctive names for multiple similar creatures
• Adjust initiative if someone uses the Ready action
• Remember that initiative can change due to spells or abilities
        """.strip()    

    def _get_aliases_help(self) -> str:
        """Get command aliases help text."""
        return """
D&D Encounter Tracker - Command Aliases and Shortcuts
====================================================

COMMAND ALIASES:
Many commands have shorter aliases for faster input during gameplay.

ENCOUNTER MANAGEMENT:
  new        → n, create
  load       → l, open  
  save       → s, write
  list       → ls, dir

COMBATANT MANAGEMENT:
  add        → a
  remove     → r, rm, del, delete
  hp         → h, health, damage, heal
  init       → i, initiative

DISPLAY COMMANDS:
  show       → display, view, status
  combatant  → c, char, character
  next       → next-turn, advance

NOTE MANAGEMENT:
  note       → n, notes, comment, comments

HELP AND UTILITY:
  help       → h, ?, man
  interactive → int, shell, repl
  quit       → q, exit, bye (interactive mode)

USAGE EXAMPLES:
  Instead of: add Thorin 45 18 player
  Use:        a Thorin 45 18 player

  Instead of: hp Thorin -8
  Use:        h Thorin -8

  Instead of: show --details
  Use:        status --details

  Instead of: combatant Thorin
  Use:        c Thorin

TYPO CORRECTIONS:
The system automatically corrects common typos:
  ad         → add
  sav        → save
  loa        → load
  sho        → show
  nex        → next
  hel        → help
  combatan   → combatant

CONTEXTUAL SHORTCUTS:
Some shortcuts provide context-aware behavior:
  hurt <name>    → hp <name> - (damage)
  heal <name>    → hp <name> + (healing)
  kill <name>    → hp <name> 0 (set to 0 HP)
  revive <name>  → hp <name> 1 (set to 1 HP)

TIPS:
• Aliases work in both command-line and interactive modes
• Mix full commands and aliases as needed
• The system suggests corrections for unrecognized commands
• Use 'help commands' to see all available commands with aliases
• Tab completion works in interactive mode for combatant names

ADDITIONAL SHORTCUTS:
  ko <n>       → hp <n> 0 (knock out)
  stabilize <n> → hp <n> 1 (stabilize dying)
  
  fast <n>     → init <n> +5 (increase initiative)
  slow <n>     → init <n> -5 (decrease initiative)
  first <n>    → init <n> 30 (move to top)
  last <n>     → init <n> 1 (move to bottom)

SMART SUGGESTIONS:
The system provides intelligent suggestions for:
• Misspelled combatant names
• Invalid command syntax
• Alternative command options
• Common typos and corrections
        """.strip()
    
    def _get_colors_help(self) -> str:
        """Get color system help text."""
        return """
D&D Encounter Tracker - Color System Guide
=========================================

VISUAL INDICATORS:
The encounter tracker uses colors to provide quick visual feedback
about combat status and system messages.

HP STATUS COLORS:
  Green      → Healthy (>50% HP)
  Yellow     → Wounded (25-50% HP)  
  Red        → Critical (1-25% HP)
  Bright Red → Dead (0 HP)

COMBATANT TYPE COLORS:
  Bright Blue    → Player Characters
  Bright Red     → Monsters
  Bright Magenta → NPCs
  Dim/Gray       → Unknown type

INITIATIVE DISPLAY:
  Bright Yellow  → Current turn indicator (>>>)
  Cyan           → Initiative values
  Default        → Other combatants

MESSAGE TYPES:
  ✓ Green        → Success messages
  ✗ Bright Red   → Error messages
  ⚠ Bright Yellow → Warning messages
  ℹ Bright Blue   → Information messages

SPECIAL INDICATORS:
  📝             → Combatant has notes
  Bold text      → Important information (names, headers)
  Dim text       → Secondary information

EXAMPLES:
Initiative Order:
>>> 18 | Thorin               | HP: 32/45     | Player 📝
    15 | Goblin Scout         | HP: 2/7       | Monster
    12 | Ancient Dragon       | HP: 0/200     | Monster

Messages:
✓ Added Player 'Thorin'
✗ Combatant 'Thrain' not found
⚠ This would set HP below 0 (will be clamped to 0)
ℹ Use 'help hp' for HP management guide

DISABLING COLORS:
If colors don't display correctly or you prefer plain text:
• Set environment variable: NO_COLOR=1
• Colors auto-disable on non-terminal output
• Windows users may need colorama package for best results

TROUBLESHOOTING:
• If colors appear as strange characters, your terminal may not support ANSI codes
• Try updating your terminal or using a different one
• Colors work best with modern terminals (Terminal.app, iTerm2, Windows Terminal, etc.)
        """.strip()