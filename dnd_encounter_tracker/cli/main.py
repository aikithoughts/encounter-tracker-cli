"""Main CLI entry point for D&D Encounter Tracker."""

import argparse
import sys
from typing import List, Optional

from .commands import CommandHandler
from .display import DisplayManager
from ..core.encounter_service import EncounterService
from ..data.persistence import DataManager


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with all subcommands.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='dnd-encounter-tracker',
        description='D&D Encounter Tracker - Manage combat encounters for tabletop D&D sessions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s new "Goblin Ambush"              Create a new encounter
  %(prog)s load goblin_ambush               Load an existing encounter
  %(prog)s add Thorin 45 18 player          Add a player character
  %(prog)s add "Goblin Scout" 7 12 monster  Add a monster
  %(prog)s hp Thorin -8                     Subtract 8 HP from Thorin
  %(prog)s hp Thorin 25                     Set Thorin's HP to 25
  %(prog)s init Thorin 20                   Set Thorin's initiative to 20
  %(prog)s note add Thorin "Blessed by cleric"  Add a note
  %(prog)s show                             Display current encounter
  %(prog)s save goblin_ambush               Save the encounter
        """
    )
    
    # Add global options
    parser.add_argument(
        '--version',
        action='version',
        version='D&D Encounter Tracker 1.0.0'
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        metavar='COMMAND'
    )
    
    # Encounter management commands
    _add_encounter_commands(subparsers)
    
    # Combatant management commands
    _add_combatant_commands(subparsers)
    
    # Display and utility commands
    _add_display_commands(subparsers)
    
    # Note management commands
    _add_note_commands(subparsers)
    
    # Help and documentation commands
    _add_help_commands(subparsers)
    
    return parser


def _add_encounter_commands(subparsers) -> None:
    """Add encounter management subcommands."""
    
    # New encounter
    new_parser = subparsers.add_parser(
        'new',
        help='Create a new encounter',
        description='Create a new encounter with the specified name'
    )
    new_parser.add_argument(
        'name',
        help='Name for the new encounter'
    )
    
    # Load encounter
    load_parser = subparsers.add_parser(
        'load',
        help='Load an encounter from file',
        description='Load a previously saved encounter from a JSON file'
    )
    load_parser.add_argument(
        'filename',
        help='Name of the encounter file to load (without .json extension)'
    )
    
    # Save encounter
    save_parser = subparsers.add_parser(
        'save',
        help='Save the current encounter',
        description='Save the current encounter to a JSON file'
    )
    save_parser.add_argument(
        'filename',
        help='Name to save the encounter as (without .json extension)'
    )
    
    # List encounters
    list_parser = subparsers.add_parser(
        'list',
        help='List available encounters',
        description='List all saved encounter files'
    )
    list_parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed information including metadata'
    )
    
    # Backup encounter
    backup_parser = subparsers.add_parser(
        'backup',
        help='Create a backup of an encounter file',
        description='Create a timestamped backup copy of an encounter file'
    )
    backup_parser.add_argument(
        'filename',
        help='Name of the encounter file to backup (without .json extension)'
    )
    
    # Cleanup old backups
    cleanup_parser = subparsers.add_parser(
        'cleanup',
        help='Clean up old backup files',
        description='Remove old backup files, keeping only the most recent ones'
    )
    cleanup_parser.add_argument(
        '--max-backups',
        type=int,
        default=5,
        help='Maximum number of backup files to keep per encounter (default: 5)'
    )


def _add_combatant_commands(subparsers) -> None:
    """Add combatant management subcommands."""
    
    # Add combatant
    add_parser = subparsers.add_parser(
        'add',
        help='Add a combatant to the encounter',
        description='Add a new combatant with name, hit points, and initiative'
    )
    add_parser.add_argument(
        'name',
        help='Name of the combatant'
    )
    add_parser.add_argument(
        'hp',
        type=int,
        help='Maximum hit points'
    )
    add_parser.add_argument(
        'initiative',
        type=int,
        help='Initiative value'
    )
    add_parser.add_argument(
        'type',
        nargs='?',
        default='unknown',
        choices=['player', 'monster', 'npc', 'unknown'],
        help='Type of combatant (default: unknown)'
    )
    
    # Remove combatant
    remove_parser = subparsers.add_parser(
        'remove',
        help='Remove a combatant from the encounter',
        description='Remove a combatant by name'
    )
    remove_parser.add_argument(
        'name',
        help='Name of the combatant to remove'
    )
    
    # Update hit points
    hp_parser = subparsers.add_parser(
        'hp',
        help='Update hit points',
        description='Update a combatant\'s hit points using absolute values, additions (+), or subtractions (-)'
    )
    hp_parser.add_argument(
        'name',
        help='Name of the combatant'
    )
    hp_parser.add_argument(
        'value',
        help='HP value: absolute (25), addition (+8), or subtraction (-12)'
    )
    
    # Adjust initiative
    init_parser = subparsers.add_parser(
        'init',
        help='Adjust initiative',
        description='Set a combatant\'s initiative to a new value'
    )
    init_parser.add_argument(
        'name',
        help='Name of the combatant'
    )
    init_parser.add_argument(
        'value',
        type=int,
        help='New initiative value'
    )


def _add_display_commands(subparsers) -> None:
    """Add display and utility subcommands."""
    
    # Show encounter
    show_parser = subparsers.add_parser(
        'show',
        help='Display the current encounter',
        description='Show the current encounter with initiative order and combatant details'
    )
    show_parser.add_argument(
        '--details',
        action='store_true',
        help='Show detailed information for all combatants'
    )
    
    # Show specific combatant
    combatant_parser = subparsers.add_parser(
        'combatant',
        help='Show details for a specific combatant',
        description='Display detailed information about a single combatant'
    )
    combatant_parser.add_argument(
        'name',
        help='Name of the combatant to show'
    )
    
    # Next turn
    next_parser = subparsers.add_parser(
        'next',
        help='Advance to the next turn',
        description='Move to the next combatant in initiative order'
    )


def _add_note_commands(subparsers) -> None:
    """Add note management subcommands."""
    
    # Note management
    note_parser = subparsers.add_parser(
        'note',
        help='Manage combatant notes',
        description='Add, edit, remove, or view notes for combatants'
    )
    note_subparsers = note_parser.add_subparsers(
        dest='note_action',
        help='Note actions',
        metavar='ACTION'
    )
    
    # Add note
    note_add_parser = note_subparsers.add_parser(
        'add',
        help='Add a note to a combatant'
    )
    note_add_parser.add_argument(
        'name',
        help='Name of the combatant'
    )
    note_add_parser.add_argument(
        'note',
        help='Note text to add'
    )
    
    # List notes
    note_list_parser = note_subparsers.add_parser(
        'list',
        help='List notes for a combatant'
    )
    note_list_parser.add_argument(
        'name',
        help='Name of the combatant'
    )
    
    # Edit note
    note_edit_parser = note_subparsers.add_parser(
        'edit',
        help='Edit a note by index'
    )
    note_edit_parser.add_argument(
        'name',
        help='Name of the combatant'
    )
    note_edit_parser.add_argument(
        'index',
        type=int,
        help='Index of the note to edit (1-based)'
    )
    note_edit_parser.add_argument(
        'note',
        help='New note text'
    )
    
    # Remove note
    note_remove_parser = note_subparsers.add_parser(
        'remove',
        help='Remove a note by index'
    )
    note_remove_parser.add_argument(
        'name',
        help='Name of the combatant'
    )
    note_remove_parser.add_argument(
        'index',
        type=int,
        help='Index of the note to remove (1-based)'
    )
    
    # Show all notes
    note_show_parser = note_subparsers.add_parser(
        'show',
        help='Show all combatants with notes'
    )


def _add_help_commands(subparsers) -> None:
    """Add help and documentation subcommands."""
    
    # Help command
    help_parser = subparsers.add_parser(
        'help',
        help='Show detailed help for commands',
        description='Display comprehensive help and examples for using the encounter tracker'
    )
    help_parser.add_argument(
        'topic',
        nargs='?',
        choices=['commands', 'examples', 'workflow', 'notes', 'hp', 'initiative', 'aliases', 'colors'],
        help='Specific help topic to display'
    )
    
    # Interactive mode command
    interactive_parser = subparsers.add_parser(
        'interactive',
        help='Start interactive mode',
        description='Launch the interactive command-line interface'
    )


def main(args: Optional[List[str]] = None) -> int:
    """Main CLI entry point.
    
    Args:
        args: Command line arguments (defaults to sys.argv)
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    from .aliases import aliases
    from .colors import formatter
    
    parser = create_parser()
    
    # If no arguments provided, start interactive mode
    if args is None and len(sys.argv) == 1:
        return interactive_mode()
    
    # Process command aliases before parsing
    if args is None:
        args = sys.argv[1:]
    
    if args:
        # Resolve command aliases
        original_command = args[0]
        resolved_command = aliases.resolve_alias(original_command)
        if resolved_command != original_command:
            args[0] = resolved_command
            print(f"Using '{resolved_command}' (alias for '{original_command}')")
    
    try:
        parsed_args = parser.parse_args(args)
    except SystemExit as e:
        # Handle argument parsing errors with suggestions
        if args and e.code != 0:
            invalid_command = args[0] if args else ""
            suggestions = aliases.get_suggestions(invalid_command)
            if suggestions:
                print(formatter.error(f"Unknown command: {invalid_command}"))
                print(formatter.info(f"Did you mean: {', '.join(suggestions)}?"))
                print(formatter.dim("Use 'help' to see all available commands."))
            return e.code
        return e.code
    
    # If no command provided, show help
    if not parsed_args.command:
        parser.print_help()
        return 0
    
    # Initialize services
    data_manager = DataManager()
    encounter_service = EncounterService(data_manager)
    display_manager = DisplayManager()
    command_handler = CommandHandler(encounter_service, display_manager)
    
    try:
        # Execute the command
        return command_handler.execute_command(parsed_args)
    except KeyboardInterrupt:
        print(formatter.warning("\nOperation cancelled by user."))
        return 1
    except Exception as e:
        print(formatter.error(f"Unexpected error: {e}"))
        print(formatter.dim("Use 'help' for usage information."))
        return 1


def interactive_mode() -> int:
    """Run the application in interactive mode.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    from .interactive import InteractiveSession
    
    try:
        session = InteractiveSession()
        return session.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())