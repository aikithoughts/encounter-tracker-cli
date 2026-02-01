"""Interactive CLI session for D&D Encounter Tracker."""

import shlex
import sys
from typing import List, Optional

from .commands import CommandHandler
from .display import DisplayManager
from .help import HelpManager
from ..core.encounter_service import EncounterService
from ..data.persistence import DataManager
from ..core.exceptions import EncounterTrackerError


class InteractiveSession:
    """Manages an interactive CLI session."""
    
    def __init__(self):
        """Initialize the interactive session."""
        # Initialize services
        self.data_manager = DataManager()
        self.encounter_service = EncounterService(self.data_manager)
        self.display_manager = DisplayManager()
        self.help_manager = HelpManager()
        self.command_handler = CommandHandler(self.encounter_service, self.display_manager)
        
        # Session state
        self.running = True
        self.unsaved_changes = False
    
    def run(self) -> int:
        """Run the interactive session.
        
        Returns:
            Exit code (0 for success, non-zero for error)
        """
        self._show_welcome()
        
        while self.running:
            try:
                # Get user input
                prompt = self._get_prompt()
                user_input = input(prompt).strip()
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    if self._confirm_exit():
                        break
                    continue
                
                if user_input.lower() in ['help', '?']:
                    self.help_manager.show_interactive_help()
                    continue
                
                # Parse and execute command
                self._execute_command(user_input)
                
            except KeyboardInterrupt:
                print()  # New line after ^C
                if self._confirm_exit():
                    break
            except EOFError:
                print()  # New line after ^D
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                print("Type 'help' for assistance or 'exit' to quit.")
        
        print("Goodbye!")
        return 0
    
    def _show_welcome(self) -> None:
        """Display welcome message and basic instructions."""
        print("=" * 60)
        print("D&D Encounter Tracker - Interactive Mode")
        print("=" * 60)
        print()
        print("Welcome! This tool helps you manage combat encounters.")
        print()
        print("Quick start:")
        print("  • Type 'help' for detailed instructions")
        print("  • Type 'new <name>' to create an encounter")
        print("  • Type 'load <name>' to load a saved encounter")
        print("  • Type 'exit' to quit")
        print()
        
        # Show available encounters if any exist
        encounters = self.encounter_service.get_available_encounters()
        if encounters:
            print("Available encounters:")
            for encounter in sorted(encounters[:5]):  # Show first 5
                print(f"  • {encounter}")
            if len(encounters) > 5:
                print(f"  ... and {len(encounters) - 5} more")
            print()
    
    def _get_prompt(self) -> str:
        """Get the command prompt string.
        
        Returns:
            Formatted prompt string
        """
        encounter = self.encounter_service.get_current_encounter()
        
        if encounter:
            unsaved_indicator = "*" if self.unsaved_changes else ""
            return f"[{encounter.name}{unsaved_indicator}] > "
        else:
            return "dnd-tracker > "
    
    def _execute_command(self, user_input: str) -> None:
        """Execute a user command.
        
        Args:
            user_input: Raw user input string
        """
        try:
            # Parse the command line
            args = shlex.split(user_input)
            if not args:
                return
            
            # Handle help requests
            if args[0] == 'help':
                if len(args) > 1:
                    self.help_manager.show_help_topic(args[1])
                else:
                    self.help_manager.show_interactive_help()
                return
            
            # Handle interactive-specific commands
            if args[0] == 'clear':
                self._clear_screen()
                return
            
            if args[0] == 'status':
                self._show_status()
                return
            
            # Create a mock args object for the command handler
            from argparse import Namespace
            
            # Map command to arguments
            parsed_args = self._parse_interactive_command(args)
            if parsed_args:
                # Track if this command might modify data
                modifying_commands = ['new', 'add', 'remove', 'hp', 'init', 'note', 'next']
                if args[0] in modifying_commands:
                    self.unsaved_changes = True
                elif args[0] == 'save':
                    self.unsaved_changes = False
                elif args[0] == 'load':
                    self.unsaved_changes = False  # Fresh load has no unsaved changes
                
                # Execute the command
                result = self.command_handler.execute_command(parsed_args)
                
                # Show encounter summary after certain commands
                if args[0] in ['add', 'remove', 'hp', 'init'] and result == 0:
                    encounter = self.encounter_service.get_current_encounter()
                    if encounter and encounter.has_combatants():
                        print()
        
        except EncounterTrackerError as e:
            print(e.get_user_message())
        except Exception as e:
            print(f"Error: {e}")
            print("Type 'help' for command syntax or 'help examples' for usage examples.")
    
    def _parse_interactive_command(self, args: List[str]) -> Optional:
        """Parse interactive command into argparse Namespace.
        
        Args:
            args: List of command arguments
            
        Returns:
            Parsed arguments namespace or None if invalid
        """
        from argparse import Namespace
        
        if not args:
            return None
        
        command = args[0]
        
        # Map commands to their expected arguments
        if command == 'new':
            if len(args) < 2:
                print("Usage: new <encounter_name>")
                return None
            return Namespace(command='new', name=' '.join(args[1:]))
        
        elif command == 'load':
            if len(args) < 2:
                print("Usage: load <filename>")
                return None
            return Namespace(command='load', filename=args[1])
        
        elif command == 'save':
            if len(args) < 2:
                encounter = self.encounter_service.get_current_encounter()
                if encounter:
                    filename = encounter.name.lower().replace(' ', '_')
                    return Namespace(command='save', filename=filename)
                else:
                    print("Usage: save <filename>")
                    return None
            return Namespace(command='save', filename=args[1])
        
        elif command == 'list':
            return Namespace(command='list')
        
        elif command == 'add':
            if len(args) < 4:
                print("Usage: add <name> <hp> <initiative> [type]")
                return None
            try:
                hp = int(args[2])
                initiative = int(args[3])
                combatant_type = args[4] if len(args) > 4 else 'unknown'
                return Namespace(
                    command='add',
                    name=args[1],
                    hp=hp,
                    initiative=initiative,
                    type=combatant_type
                )
            except ValueError:
                print("Error: HP and initiative must be numbers")
                return None
        
        elif command == 'remove':
            if len(args) < 2:
                print("Usage: remove <name>")
                return None
            return Namespace(command='remove', name=args[1])
        
        elif command == 'hp':
            if len(args) < 3:
                print("Usage: hp <name> <value>")
                return None
            return Namespace(command='hp', name=args[1], value=args[2])
        
        elif command == 'init':
            if len(args) < 3:
                print("Usage: init <name> <value>")
                return None
            try:
                value = int(args[2])
                return Namespace(command='init', name=args[1], value=value)
            except ValueError:
                print("Error: Initiative must be a number")
                return None
        
        elif command == 'show':
            details = '--details' in args or '-d' in args
            return Namespace(command='show', details=details)
        
        elif command == 'combatant':
            if len(args) < 2:
                print("Usage: combatant <name>")
                return None
            return Namespace(command='combatant', name=args[1])
        
        elif command == 'next':
            return Namespace(command='next')
        
        elif command == 'note':
            if len(args) < 2:
                print("Usage: note <action> [args...]")
                print("Actions: add, list, edit, remove, show")
                return None
            
            action = args[1]
            if action == 'add':
                if len(args) < 4:
                    print("Usage: note add <name> <note_text>")
                    return None
                return Namespace(
                    command='note',
                    note_action='add',
                    name=args[2],
                    note=' '.join(args[3:])
                )
            elif action == 'list':
                if len(args) < 3:
                    print("Usage: note list <name>")
                    return None
                return Namespace(command='note', note_action='list', name=args[2])
            elif action == 'edit':
                if len(args) < 5:
                    print("Usage: note edit <name> <index> <note_text>")
                    return None
                try:
                    index = int(args[3])
                    return Namespace(
                        command='note',
                        note_action='edit',
                        name=args[2],
                        index=index,
                        note=' '.join(args[4:])
                    )
                except ValueError:
                    print("Error: Index must be a number")
                    return None
            elif action == 'remove':
                if len(args) < 4:
                    print("Usage: note remove <name> <index>")
                    return None
                try:
                    index = int(args[3])
                    return Namespace(
                        command='note',
                        note_action='remove',
                        name=args[2],
                        index=index
                    )
                except ValueError:
                    print("Error: Index must be a number")
                    return None
            elif action == 'show':
                return Namespace(command='note', note_action='show')
            else:
                print(f"Unknown note action: {action}")
                print("Actions: add, list, edit, remove, show")
                return None
        
        else:
            print(f"Unknown command: {command}")
            print("Type 'help' for available commands")
            return None
    
    def _show_status(self) -> None:
        """Show current session status."""
        encounter = self.encounter_service.get_current_encounter()
        
        if encounter:
            print(f"Current encounter: {encounter.name}")
            if self.unsaved_changes:
                print("Status: Unsaved changes")
            else:
                print("Status: Saved")
            
            if encounter.has_combatants():
                print(f"Combatants: {len(encounter.combatants)}")
                print(f"Round: {encounter.round_number}")
                current = encounter.get_current_combatant()
                if current:
                    print(f"Current turn: {current.name}")
            else:
                print("No combatants in encounter")
        else:
            print("No encounter loaded")
            encounters = self.encounter_service.get_available_encounters()
            if encounters:
                print(f"Available encounters: {len(encounters)}")
            else:
                print("No saved encounters found")
    
    def _clear_screen(self) -> None:
        """Clear the terminal screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _confirm_exit(self) -> bool:
        """Confirm exit if there are unsaved changes.
        
        Returns:
            True if user confirms exit, False otherwise
        """
        if not self.unsaved_changes:
            return True
        
        try:
            response = input("You have unsaved changes. Exit anyway? (y/N): ").strip().lower()
            return response in ['y', 'yes']
        except (KeyboardInterrupt, EOFError):
            return True