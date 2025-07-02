"""Command handlers for CLI operations."""

import argparse
from typing import List

from .display import DisplayManager
from .help import HelpManager
from .colors import formatter
from .aliases import aliases, validator
from ..core.encounter_service import EncounterService
from ..core.exceptions import (
    EncounterTrackerError,
    EncounterNotLoadedError,
    CombatantNotFoundError,
    ValidationError,
    FileFormatError,
    CommandError,
    DuplicateCombatantError,
    InvalidHPValueError,
    NoteIndexError,
    InitiativeError
)


class CommandHandler:
    """Handles execution of CLI commands."""
    
    def __init__(self, encounter_service: EncounterService, display_manager: DisplayManager):
        """Initialize command handler.
        
        Args:
            encounter_service: Service for encounter operations
            display_manager: Manager for formatted output
        """
        self.encounter_service = encounter_service
        self.display_manager = display_manager
        self.help_manager = HelpManager()
    
    def execute_command(self, args: argparse.Namespace) -> int:
        """Execute a command based on parsed arguments.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            Exit code (0 for success, non-zero for error)
        """
        try:
            # Route to appropriate command handler
            if args.command == 'new':
                return self._handle_new(args)
            elif args.command == 'load':
                return self._handle_load(args)
            elif args.command == 'save':
                return self._handle_save(args)
            elif args.command == 'list':
                return self._handle_list(args)
            elif args.command == 'add':
                return self._handle_add(args)
            elif args.command == 'remove':
                return self._handle_remove(args)
            elif args.command == 'hp':
                return self._handle_hp(args)
            elif args.command == 'init':
                return self._handle_init(args)
            elif args.command == 'show':
                return self._handle_show(args)
            elif args.command == 'combatant':
                return self._handle_combatant(args)
            elif args.command == 'next':
                return self._handle_next(args)
            elif args.command == 'note':
                return self._handle_note(args)
            elif args.command == 'backup':
                return self._handle_backup(args)
            elif args.command == 'cleanup':
                return self._handle_cleanup(args)
            elif args.command == 'help':
                return self._handle_help(args)
            elif args.command == 'interactive':
                return self._handle_interactive(args)
            else:
                error = CommandError(
                    command=args.command,
                    reason="Unknown command",
                    usage_example="Use --help to see available commands"
                )
                print(error.get_user_message())
                return 1
                
        except EncounterTrackerError as e:
            print(e.get_user_message())
            return 1
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return 1
        except Exception as e:
            # Catch any unexpected errors and provide helpful feedback
            print(f"Unexpected error: {e}")
            print("This appears to be a bug. Please report this issue.")
            print("You can try the following:")
            print("  - Check your command syntax")
            print("  - Verify your encounter file isn't corrupted")
            print("  - Try creating a new encounter")
            return 1
    
    def _handle_new(self, args: argparse.Namespace) -> int:
        """Handle 'new' command."""
        try:
            # Validate encounter name
            is_valid, error_msg = validator.validate_combatant_name(args.name)
            if not is_valid:
                print(formatter.error(f"Invalid encounter name: {error_msg}"))
                print(formatter.info("Examples: 'Goblin Ambush', 'Dragon's Lair', 'Tavern Brawl'"))
                return 1
            
            encounter = self.encounter_service.create_encounter(args.name)
            print(formatter.success(f"Created new encounter: {encounter.name}"))
            print(formatter.info("Add combatants with: add <name> <hp> <initiative> [type]"))
            return 0
        except ValidationError as e:
            print(formatter.error(f"Failed to create encounter: {e}"))
            print(formatter.info("Examples: 'Goblin Ambush', 'Dragon's Lair', 'Tavern Brawl'"))
            return 1
    
    def _handle_load(self, args: argparse.Namespace) -> int:
        """Handle 'load' command."""
        try:
            encounter = self.encounter_service.load_encounter(args.filename)
            print(formatter.success(f"Loaded encounter: {encounter.name}"))
            
            # Show encounter summary after loading
            if encounter.has_combatants():
                print()
                print(self.display_manager.show_encounter_summary(encounter))
            else:
                print(formatter.dim("No combatants in this encounter."))
                print(formatter.info("Add combatants with: add <name> <hp> <initiative> [type]"))
            
            return 0
        except FileFormatError as e:
            available_encounters = self.encounter_service.get_available_encounters()
            print(formatter.error(f"Failed to load encounter '{args.filename}': {e}"))
            if available_encounters:
                print(formatter.info(f"Available encounters: {', '.join(available_encounters)}"))
            else:
                print(formatter.info("No saved encounters found. Create one with: new <name>"))
            return 1
    
    def _handle_save(self, args: argparse.Namespace) -> int:
        """Handle 'save' command."""
        try:
            # Check if file already exists and warn user
            if self.encounter_service.encounter_exists(args.filename):
                print(f"Warning: Overwriting existing encounter '{args.filename}'")
            
            self.encounter_service.save_encounter(args.filename)
            encounter = self.encounter_service.get_current_encounter()
            print(f"Saved encounter '{encounter.name}' to {args.filename}.json")
            return 0
        except FileFormatError as e:
            # Add suggestions for common save issues
            raise FileFormatError(
                filename=args.filename,
                operation="save",
                reason=str(e)
            )
    
    def _handle_list(self, args: argparse.Namespace) -> int:
        """Handle 'list' command."""
        if hasattr(args, 'detailed') and args.detailed:
            return self._handle_list_detailed(args)
        
        encounters = self.encounter_service.get_available_encounters()
        
        if not encounters:
            print("No saved encounters found.")
            print("Create a new encounter with 'new <name>' to get started.")
        else:
            print("Available encounters:")
            for encounter in sorted(encounters):
                print(f"  - {encounter}")
        
        return 0
    
    def _handle_list_detailed(self, args: argparse.Namespace) -> int:
        """Handle 'list --detailed' command."""
        encounters_with_metadata = self.encounter_service.list_encounters_with_metadata()
        
        if not encounters_with_metadata:
            print("No saved encounters found.")
            print("Create a new encounter with 'new <n>' to get started.")
            return 0
        
        print("Available encounters (most recently modified first):")
        print("=" * 70)
        
        for encounter_info in encounters_with_metadata:
            filename = encounter_info["filename"]
            encounter_name = encounter_info["encounter_name"]
            metadata = encounter_info["metadata"]
            
            # Format dates for display
            try:
                from datetime import datetime
                created = datetime.fromisoformat(metadata["created"].replace('Z', '+00:00'))
                modified = datetime.fromisoformat(metadata["last_modified"].replace('Z', '+00:00'))
                created_str = created.strftime("%Y-%m-%d %H:%M")
                modified_str = modified.strftime("%Y-%m-%d %H:%M")
            except (ValueError, KeyError):
                created_str = metadata.get("created", "Unknown")[:16]
                modified_str = metadata.get("last_modified", "Unknown")[:16]
            
            # Format file size
            size_bytes = metadata.get("size_bytes", 0)
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f} KB"
            else:
                size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
            
            print(f"File: {filename}.json")
            print(f"Name: {encounter_name}")
            print(f"Created: {created_str}")
            print(f"Modified: {modified_str}")
            print(f"Size: {size_str}")
            print("-" * 40)
        
        return 0
    
    def _handle_add(self, args: argparse.Namespace) -> int:
        """Handle 'add' command."""
        try:
            # Validate combatant name
            is_valid, error_msg = validator.validate_combatant_name(args.name)
            if not is_valid:
                print(formatter.error(f"Invalid name: {error_msg}"))
                return 1
            
            # Validate HP value
            if args.hp <= 0:
                print(formatter.error("Hit points must be positive"))
                print(formatter.info("Examples: 1, 25, 100"))
                return 1
            
            # Validate initiative
            is_valid, warning = validator.validate_initiative_value(str(args.initiative))
            if not is_valid:
                print(formatter.error(f"Invalid initiative: {warning}"))
                return 1
            elif warning:
                print(formatter.warning(warning))
            
            # Validate and correct combatant type
            type_valid, corrected_type, type_error = validator.validate_combatant_type(args.type)
            if not type_valid:
                print(formatter.error(type_error))
                return 1
            
            combatant = self.encounter_service.add_combatant(
                name=args.name,
                max_hp=args.hp,
                initiative=args.initiative,
                combatant_type=corrected_type or args.type
            )
            
            # Color the type for display
            type_colors = {
                'player': formatter.bright_blue,
                'monster': formatter.bright_red,
                'npc': formatter.bright_magenta,
                'unknown': formatter.dim
            }
            type_formatter = type_colors.get(combatant.combatant_type.lower(), formatter.dim)
            type_display = type_formatter(combatant.combatant_type.title())
            
            print(formatter.success(f"Added {type_display} '{formatter.bold(combatant.name)}'"))
            print(formatter.dim(f"HP: {combatant.max_hp}, Initiative: {combatant.initiative}"))
            
            # Show updated initiative order
            encounter = self.encounter_service.get_current_encounter()
            print()
            print(self.display_manager.show_initiative_order(
                encounter.combatants, encounter.current_turn
            ))
            
            return 0
        except ValidationError as e:
            if "already exists" in str(e):
                print(formatter.error(f"Combatant '{args.name}' already exists"))
                encounter = self.encounter_service.get_current_encounter()
                if encounter:
                    existing_names = [c.name for c in encounter.combatants]
                    print(formatter.info(f"Existing combatants: {', '.join(existing_names)}"))
                return 1
            print(formatter.error(str(e)))
            return 1
    
    def _handle_remove(self, args: argparse.Namespace) -> int:
        """Handle 'remove' command."""
        try:
            self.encounter_service.remove_combatant(args.name)
            print(f"Removed combatant '{args.name}'")
            
            # Show updated encounter if there are still combatants
            encounter = self.encounter_service.get_current_encounter()
            if encounter.has_combatants():
                print()
                print(self.display_manager.show_initiative_order(
                    encounter.combatants, encounter.current_turn
                ))
            else:
                print("No combatants remaining in encounter.")
            
            return 0
        except CombatantNotFoundError:
            # Enhance error with available combatants
            encounter = self.encounter_service.get_current_encounter()
            available_names = [c.name for c in encounter.combatants] if encounter else []
            raise CombatantNotFoundError(args.name, available_names)
    
    def _handle_hp(self, args: argparse.Namespace) -> int:
        """Handle 'hp' command."""
        try:
            # Get combatant before update to show change
            combatant = self.encounter_service.get_combatant(args.name)
            if not combatant:
                encounter = self.encounter_service.get_current_encounter()
                available_names = [c.name for c in encounter.combatants] if encounter else []
                print(formatter.error(f"Combatant '{args.name}' not found"))
                if available_names:
                    suggestions = validator.suggest_name_completion(args.name, available_names)
                    if suggestions:
                        print(formatter.info(f"Did you mean: {', '.join(suggestions)}?"))
                    else:
                        print(formatter.info(f"Available: {', '.join(available_names)}"))
                return 1
            
            # Validate HP value
            is_valid, warning = validator.validate_hp_value(
                args.value, combatant.current_hp, combatant.max_hp
            )
            if not is_valid:
                print(formatter.error(f"Invalid HP value: {warning}"))
                print(formatter.info(f"Current HP: {combatant.current_hp}/{combatant.max_hp}"))
                return 1
            elif warning:
                print(formatter.warning(warning))
            
            old_hp = combatant.current_hp
            
            # Update HP
            self.encounter_service.update_hp(args.name, args.value)
            
            # Show the change with colors
            new_hp = combatant.current_hp
            hp_ratio = new_hp / combatant.max_hp if combatant.max_hp > 0 else 0
            
            # Color the HP change
            if new_hp == 0:
                hp_display = formatter.bright_red(f"{old_hp} → {new_hp} (DEAD)")
            elif hp_ratio <= 0.25:
                hp_display = formatter.red(f"{old_hp} → {new_hp} (CRITICAL)")
            elif new_hp > old_hp:
                hp_display = formatter.green(f"{old_hp} → {new_hp}")  # Healing
            else:
                hp_display = formatter.yellow(f"{old_hp} → {new_hp}")  # Damage
            
            print(formatter.success(f"Updated {formatter.bold(args.name)}'s HP: {hp_display}"))
            
            return 0
        except InvalidHPValueError as e:
            print(formatter.error(f"Invalid HP value: {e}"))
            if combatant:
                print(formatter.info(f"Current HP: {combatant.current_hp}/{combatant.max_hp}"))
                print(formatter.info("Examples: 25 (set to 25), +8 (heal 8), -12 (damage 12)"))
            return 1
    
    def _handle_init(self, args: argparse.Namespace) -> int:
        """Handle 'init' command."""
        try:
            # Get combatant before update to show change
            combatant = self.encounter_service.get_combatant(args.name)
            if not combatant:
                encounter = self.encounter_service.get_current_encounter()
                available_names = [c.name for c in encounter.combatants] if encounter else []
                raise CombatantNotFoundError(args.name, available_names)
            
            old_init = combatant.initiative
            
            # Update initiative
            self.encounter_service.adjust_initiative(args.name, args.value)
            
            print(f"Updated {args.name}'s initiative: {old_init} → {args.value}")
            
            # Show updated initiative order
            encounter = self.encounter_service.get_current_encounter()
            print()
            print(self.display_manager.show_initiative_order(
                encounter.combatants, encounter.current_turn
            ))
            
            return 0
        except ValidationError as e:
            raise InitiativeError(str(e), combatant.initiative if combatant else None)
    
    def _handle_show(self, args: argparse.Namespace) -> int:
        """Handle 'show' command."""
        encounter = self.encounter_service.get_current_encounter()
        
        if not encounter:
            raise EncounterNotLoadedError("display encounter information")
        
        if args.details:
            # Show detailed view
            print(self.display_manager.show_encounter_summary(encounter))
            
            if encounter.has_combatants():
                print("\nDetailed Combatant Information:")
                print("=" * 50)
                for combatant in encounter.combatants:
                    print()
                    print(self.display_manager.show_combatant_details(combatant))
        else:
            # Show summary view
            print(self.display_manager.show_encounter_summary(encounter))
        
        return 0
    
    def _handle_combatant(self, args: argparse.Namespace) -> int:
        """Handle 'combatant' command."""
        try:
            combatant = self.encounter_service.get_combatant(args.name)
            if not combatant:
                encounter = self.encounter_service.get_current_encounter()
                available_names = [c.name for c in encounter.combatants] if encounter else []
                raise CombatantNotFoundError(args.name, available_names)
            
            print(self.display_manager.show_combatant_details(combatant))
            return 0
        except EncounterNotLoadedError:
            raise EncounterNotLoadedError("show combatant details")
    
    def _handle_next(self, args: argparse.Namespace) -> int:
        """Handle 'next' command."""
        try:
            current_combatant = self.encounter_service.next_turn()
            
            if not current_combatant:
                encounter = self.encounter_service.get_current_encounter()
                if not encounter or not encounter.has_combatants():
                    print("No combatants in encounter.")
                    print("Add combatants with 'add <name> <hp> <initiative> [type]'")
                    return 0
            
            encounter = self.encounter_service.get_current_encounter()
            
            print(f"Round {encounter.round_number}")
            print(f"Current turn: {current_combatant.name}")
            print()
            print(self.display_manager.show_initiative_order(
                encounter.combatants, encounter.current_turn
            ))
            
            return 0
        except EncounterNotLoadedError:
            raise EncounterNotLoadedError("advance to next turn")
    
    def _handle_note(self, args: argparse.Namespace) -> int:
        """Handle 'note' command and its subcommands."""
        if not hasattr(args, 'note_action') or not args.note_action:
            raise CommandError(
                command="note",
                reason="Note action required",
                usage_example="note add <name> \"<note text>\""
            )
        
        if args.note_action == 'add':
            return self._handle_note_add(args)
        elif args.note_action == 'list':
            return self._handle_note_list(args)
        elif args.note_action == 'edit':
            return self._handle_note_edit(args)
        elif args.note_action == 'remove':
            return self._handle_note_remove(args)
        elif args.note_action == 'show':
            return self._handle_note_show(args)
        else:
            raise CommandError(
                command=f"note {args.note_action}",
                reason="Unknown note action",
                usage_example="note {add|list|edit|remove|show} ..."
            )
    
    def _handle_note_add(self, args: argparse.Namespace) -> int:
        """Handle 'note add' command."""
        try:
            if not args.note.strip():
                raise ValidationError(
                    field="note text",
                    value=args.note,
                    reason="Note cannot be empty",
                    valid_examples=["Blessed by cleric", "Poisoned", "Has inspiration"]
                )
            
            self.encounter_service.add_note(args.name, args.note)
            print(f"Added note to {args.name}: \"{args.note}\"")
            return 0
        except CombatantNotFoundError:
            encounter = self.encounter_service.get_current_encounter()
            available_names = [c.name for c in encounter.combatants] if encounter else []
            raise CombatantNotFoundError(args.name, available_names)
    
    def _handle_note_list(self, args: argparse.Namespace) -> int:
        """Handle 'note list' command."""
        try:
            combatant = self.encounter_service.get_combatant(args.name)
            if not combatant:
                encounter = self.encounter_service.get_current_encounter()
                available_names = [c.name for c in encounter.combatants] if encounter else []
                raise CombatantNotFoundError(args.name, available_names)
            
            print(self.display_manager.show_notes_list(combatant))
            return 0
        except EncounterNotLoadedError:
            raise EncounterNotLoadedError("list notes")
    
    def _handle_note_edit(self, args: argparse.Namespace) -> int:
        """Handle 'note edit' command."""
        try:
            # Convert to 0-based index for internal use
            note_index = args.index - 1
            
            if not args.note.strip():
                raise ValidationError(
                    field="note text",
                    value=args.note,
                    reason="Note cannot be empty",
                    valid_examples=["Blessed by cleric", "Poisoned", "Has inspiration"]
                )
            
            combatant = self.encounter_service.get_combatant(args.name)
            if not combatant:
                encounter = self.encounter_service.get_current_encounter()
                available_names = [c.name for c in encounter.combatants] if encounter else []
                raise CombatantNotFoundError(args.name, available_names)
            
            # Validate note index
            if note_index < 0 or note_index >= len(combatant.notes):
                raise NoteIndexError(args.index, len(combatant.notes), args.name)
            
            self.encounter_service.edit_note(args.name, note_index, args.note)
            print(f"Updated note {args.index} for {args.name}: \"{args.note}\"")
            return 0
        except EncounterNotLoadedError:
            raise EncounterNotLoadedError("edit notes")
    
    def _handle_note_remove(self, args: argparse.Namespace) -> int:
        """Handle 'note remove' command."""
        try:
            # Convert to 0-based index for internal use
            note_index = args.index - 1
            
            # Get the note text before removing for confirmation
            combatant = self.encounter_service.get_combatant(args.name)
            if not combatant:
                encounter = self.encounter_service.get_current_encounter()
                available_names = [c.name for c in encounter.combatants] if encounter else []
                raise CombatantNotFoundError(args.name, available_names)
            
            # Validate note index
            if note_index < 0 or note_index >= len(combatant.notes):
                raise NoteIndexError(args.index, len(combatant.notes), args.name)
            
            removed_note = combatant.notes[note_index]
            
            self.encounter_service.remove_note(args.name, note_index)
            print(f"Removed note {args.index} from {args.name}: \"{removed_note}\"")
            return 0
        except EncounterNotLoadedError:
            raise EncounterNotLoadedError("remove notes")
    
    def _handle_note_show(self, args: argparse.Namespace) -> int:
        """Handle 'note show' command."""
        try:
            encounter = self.encounter_service.get_current_encounter()
            if not encounter:
                raise EncounterNotLoadedError("show notes")
            
            print(self.display_manager.show_combatants_with_notes(encounter))
            return 0
        except EncounterNotLoadedError:
            raise EncounterNotLoadedError("show notes")
    
    def _handle_backup(self, args: argparse.Namespace) -> int:
        """Handle 'backup' command."""
        try:
            backup_path = self.encounter_service.backup_encounter(args.filename)
            print(f"Created backup: {backup_path}")
            return 0
        except FileFormatError as e:
            available_encounters = self.encounter_service.get_available_encounters()
            if available_encounters:
                print(f"Available encounters: {', '.join(available_encounters)}")
            raise
    
    def _handle_cleanup(self, args: argparse.Namespace) -> int:
        """Handle 'cleanup' command."""
        max_backups = getattr(args, 'max_backups', 5)
        deleted_files = self.encounter_service.cleanup_old_backups(max_backups)
        
        if deleted_files:
            print(f"Cleaned up {len(deleted_files)} old backup files:")
            for deleted_file in deleted_files:
                print(f"  - {deleted_file}")
        else:
            print("No old backup files to clean up.")
        
        return 0
    
    def _handle_help(self, args: argparse.Namespace) -> int:
        """Handle 'help' command."""
        if hasattr(args, 'topic') and args.topic:
            self.help_manager.show_help_topic(args.topic)
        else:
            self.help_manager.show_command_help()
        return 0
    
    def _handle_interactive(self, args: argparse.Namespace) -> int:
        """Handle 'interactive' command."""
        from .interactive import InteractiveSession
        
        print("Starting interactive mode...")
        session = InteractiveSession()
        return session.run()