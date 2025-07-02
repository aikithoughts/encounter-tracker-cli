# D&D Encounter Tracker

A command-line tool for managing combat encounters in tabletop D&D sessions. Track initiative order, hit points, notes, and combat state with an intuitive interface designed for live gameplay.

## Features

- **Initiative Management**: Automatic sorting by initiative with turn tracking
- **Hit Point Tracking**: Flexible HP updates with damage/healing calculations
- **Combat Notes**: Track status effects, spells, and tactical information
- **Encounter Persistence**: Save and load encounters between sessions
- **Interactive Mode**: Streamlined interface for live gameplay
- **Colored Output**: Visual indicators for HP status and combat state
- **Command Aliases**: Shortcuts and abbreviations for faster input
- **Input Validation**: Helpful error messages and suggestions

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd dnd-encounter-tracker

# Install dependencies (if any)
pip install -r requirements.txt

# Run the application
python -m dnd_encounter_tracker
```

### Basic Usage

```bash
# Create a new encounter
python -m dnd_encounter_tracker new "Goblin Ambush"

# Add combatants
python -m dnd_encounter_tracker add Thorin 45 18 player
python -m dnd_encounter_tracker add "Goblin Scout" 7 12 monster

# Update hit points
python -m dnd_encounter_tracker hp Thorin -8    # Take 8 damage
python -m dnd_encounter_tracker hp Thorin +5    # Heal 5 HP

# Show encounter status
python -m dnd_encounter_tracker show

# Save the encounter
python -m dnd_encounter_tracker save goblin_ambush
```

### Interactive Mode

For live gameplay, use interactive mode:

```bash
python -m dnd_encounter_tracker interactive
```

Or simply run without arguments:

```bash
python -m dnd_encounter_tracker
```

## Command Reference

### Encounter Management

| Command | Aliases | Description | Example |
|---------|---------|-------------|---------|
| `new` | `n`, `create` | Create new encounter | `new "Dragon Fight"` |
| `load` | `l`, `open` | Load saved encounter | `load goblin_ambush` |
| `save` | `s`, `write` | Save current encounter | `save my_encounter` |
| `list` | `ls`, `dir` | List saved encounters | `list --detailed` |

### Combatant Management

| Command | Aliases | Description | Example |
|---------|---------|-------------|---------|
| `add` | `a` | Add combatant | `add Thorin 45 18 player` |
| `remove` | `r`, `rm`, `del` | Remove combatant | `remove "Goblin Scout"` |
| `hp` | `h`, `health` | Update hit points | `hp Thorin -12` |
| `init` | `i` | Set initiative | `init Thorin 20` |

### Display Commands

| Command | Aliases | Description | Example |
|---------|---------|-------------|---------|
| `show` | `display`, `status` | Show encounter | `show --details` |
| `combatant` | `c`, `char` | Show combatant details | `combatant Thorin` |
| `next` | `advance` | Next turn | `next` |

### Note Management

| Command | Description | Example |
|---------|-------------|---------|
| `note add` | Add note to combatant | `note add Thorin "Blessed"` |
| `note list` | List combatant's notes | `note list Thorin` |
| `note edit` | Edit note by index | `note edit Thorin 1 "New text"` |
| `note remove` | Remove note by index | `note remove Thorin 2` |
| `note show` | Show all combatants with notes | `note show` |

## HP Management

The HP system supports three formats for maximum flexibility:

### Absolute Values
```bash
hp Thorin 25        # Set HP to exactly 25
```

### Damage (Subtraction)
```bash
hp Thorin -8        # Subtract 8 HP (damage)
hp Thorin -12       # Subtract 12 HP
```

### Healing (Addition)
```bash
hp Thorin +5        # Add 5 HP (healing)
hp Thorin +12       # Add 12 HP
```

### HP Status Indicators

- **Green**: Healthy (>50% HP)
- **Yellow**: Wounded (25-50% HP)
- **Red**: Critical (1-25% HP)
- **Bright Red**: Dead (0 HP)

## Combat Workflow

### Setting Up an Encounter

1. **Create or load encounter**:
   ```bash
   new "Boss Fight"
   # or
   load saved_encounter
   ```

2. **Add all combatants**:
   ```bash
   add "Player 1" 45 18 player
   add "Player 2" 38 16 player
   add "Boss Monster" 120 15 monster
   add "Minion" 8 12 monster
   ```

3. **Verify setup**:
   ```bash
   show
   ```

### Running Combat

1. **Check initiative order**:
   ```bash
   show                    # See whose turn it is
   ```

2. **For each turn**:
   ```bash
   hp Fighter -6           # Apply damage
   note add Fighter "Grappled"  # Track conditions
   next                    # Move to next turn
   ```

3. **Manage conditions**:
   ```bash
   note list Fighter       # Check active effects
   note edit Fighter 1 "Updated condition"
   note remove Fighter 2   # Remove expired effects
   ```

### Between Sessions

```bash
save encounter_name     # Save progress
list                   # See available encounters
load encounter_name    # Resume session
```

## Interactive Mode Features

Interactive mode provides a streamlined interface for live gameplay:

- **Persistent session**: Stay in one encounter without reloading
- **Command history**: Use arrow keys to repeat commands
- **Auto-completion**: Tab completion for combatant names
- **Status display**: Always shows current encounter state
- **Quick commands**: Shortened syntax for common operations

### Interactive Commands

```
> new "Goblin Ambush"           # Create encounter
> a Thorin 45 18 player         # Add combatant (short form)
> h Thorin -8                   # Update HP (short form)
> show                          # Display encounter
> next                          # Advance turn
> save                          # Save encounter
> help                          # Get help
> quit                          # Exit
```

## Advanced Features

### Command Aliases

Many commands have shorter aliases for faster input:

```bash
# These are equivalent:
add Thorin 45 18 player
a Thorin 45 18 player

# These are equivalent:
hp Thorin -8
h Thorin -8
damage Thorin -8
```

### Input Validation

The system provides helpful validation and suggestions:

```bash
# Invalid HP format
> hp Thorin abc
✗ Invalid HP value: HP value must be a number
ℹ Examples: 25 (set to 25), +8 (heal 8), -12 (damage 12)

# Combatant not found
> hp Thrain -5
✗ Combatant 'Thrain' not found
ℹ Did you mean: Thorin?
```

### Colored Output

Visual indicators help track combat state:

- **Initiative order**: Current turn highlighted in yellow
- **HP status**: Color-coded health levels
- **Combatant types**: Players (blue), monsters (red), NPCs (magenta)
- **Messages**: Success (green), errors (red), warnings (yellow), info (blue)

## File Management

### Encounter Files

Encounters are saved as JSON files in the current directory:

```
encounters/
├── goblin_ambush.json
├── dragon_fight.json
└── tavern_brawl.json
```

### Backup System

The system automatically creates backups when overwriting files:

```bash
save goblin_ambush              # Creates backup if file exists
backup goblin_ambush            # Manual backup creation
cleanup --max-backups 3         # Clean old backups
```

## Tips for Smooth Gameplay

### Naming Conventions

- Use short, memorable names: "Thorin", "Goblin1", "Boss"
- Avoid special characters that might cause parsing issues
- Use quotes for names with spaces: `"Goblin Scout"`

### Combat Management

- Save frequently, especially after major events
- Use notes immediately when effects are applied
- Keep the encounter display visible with frequent `show` commands
- Use initiative adjustments for Ready actions or spell effects

### Performance

- The system handles large encounters efficiently
- Use `show --details` sparingly for very large groups
- Clean up old backup files periodically with `cleanup`

## Troubleshooting

### Common Issues

**"Combatant not found" errors**:
- Check spelling and capitalization
- Use quotes for names with spaces
- Use `show` to see all combatant names

**File loading errors**:
- Verify the file exists with `list`
- Check for file corruption
- Try loading a backup file

**HP calculation errors**:
- Use proper format: number, +number, or -number
- Check current HP with `combatant <name>`
- Remember HP cannot go below 0 or above maximum

### Getting Help

```bash
help                    # General help
help commands           # Command reference
help examples           # Usage examples
help workflow           # Combat workflow guide
help hp                 # HP management guide
help notes              # Note management guide
```

## Development

### Architecture

The application uses a modular architecture:

- **CLI Layer**: User interface and command parsing
- **Service Layer**: Business logic for encounter management
- **Data Layer**: File I/O and persistence
- **Model Layer**: Data structures and validation

### Future Enhancements

- Web interface for remote play
- Real-time encounter sharing
- Advanced combat automation
- Integration with digital character sheets
- Mobile companion app

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]

## Support

[Add support information here]