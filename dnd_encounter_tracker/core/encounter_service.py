"""Encounter service layer for the D&D Encounter Tracker."""

from typing import List, Optional
from .models import Encounter, Combatant
from .exceptions import (
    ValidationError, 
    CombatantNotFoundError, 
    EncounterNotLoadedError,
    DuplicateCombatantError,
    InvalidHPValueError,
    NoteIndexError
)
from ..data.persistence import DataManager


class EncounterService:
    """Core business logic for encounter management.
    
    This service layer provides a clean interface for encounter operations
    and maintains separation between business logic and data persistence.
    """
    
    def __init__(self, data_manager: DataManager):
        """Initialize the encounter service.
        
        Args:
            data_manager: Data manager for persistence operations
        """
        self.data_manager = data_manager
        self.current_encounter: Optional[Encounter] = None
    
    def create_encounter(self, name: str) -> Encounter:
        """Create a new encounter.
        
        Args:
            name: Name for the new encounter
            
        Returns:
            Created encounter
            
        Raises:
            ValidationError: If name is invalid
        """
        if not name or not name.strip():
            raise ValidationError(
                field="encounter name",
                value=name,
                reason="cannot be empty",
                valid_examples=["Goblin Ambush", "Dragon's Lair", "Tavern Brawl"]
            )
        
        encounter = Encounter(name=name.strip())
        self.current_encounter = encounter
        return encounter
    
    def load_encounter(self, filename: str) -> Encounter:
        """Load an encounter from file.
        
        Args:
            filename: Name of the file to load
            
        Returns:
            Loaded encounter
            
        Raises:
            FileFormatError: If file doesn't exist or is corrupted
            ValidationError: If encounter data is invalid
        """
        encounter = self.data_manager.load_from_file(filename)
        self.current_encounter = encounter
        return encounter
    
    def save_encounter(self, filename: str) -> None:
        """Save the current encounter to file.
        
        Args:
            filename: Name of the file to save to
            
        Raises:
            EncounterNotLoadedError: If no encounter is currently loaded
            FileFormatError: If file operations fail
            ValidationError: If encounter data is invalid
        """
        if not self.current_encounter:
            raise EncounterNotLoadedError("No encounter is currently loaded")
        
        self.data_manager.save_to_file(self.current_encounter, filename)
    
    def get_current_encounter(self) -> Optional[Encounter]:
        """Get the currently loaded encounter.
        
        Returns:
            Current encounter or None if no encounter is loaded
        """
        return self.current_encounter
    
    def add_combatant(self, name: str, max_hp: int, initiative: int, 
                     combatant_type: str = "unknown") -> Combatant:
        """Add a combatant to the current encounter.
        
        Args:
            name: Combatant name
            max_hp: Maximum hit points
            initiative: Initiative value
            combatant_type: Type of combatant ("player", "monster", "npc", "unknown")
            
        Returns:
            Created combatant
            
        Raises:
            EncounterNotLoadedError: If no encounter is currently loaded
            ValidationError: If combatant data is invalid
            DuplicateCombatantError: If combatant name already exists
        """
        if not self.current_encounter:
            raise EncounterNotLoadedError("add combatant")
        
        # Validate input parameters
        if not name or not name.strip():
            raise ValidationError(
                field="combatant name",
                value=name,
                reason="Name cannot be empty",
                valid_examples=["Thorin", "Goblin Scout", "Ancient Dragon"]
            )
        
        if max_hp <= 0:
            raise ValidationError(
                field="hit points",
                value=max_hp,
                reason="Hit points must be positive",
                valid_examples=["1", "25", "100"]
            )
        
        if combatant_type not in ["player", "monster", "npc", "unknown"]:
            raise ValidationError(
                field="combatant type",
                value=combatant_type,
                reason="Invalid combatant type",
                valid_examples=["player", "monster", "npc", "unknown"]
            )
        
        # Check for duplicate names
        if any(c.name.lower() == name.strip().lower() for c in self.current_encounter.combatants):
            raise DuplicateCombatantError(name.strip())
        
        # Create combatant
        combatant = Combatant(
            name=name.strip(),
            max_hp=max_hp,
            current_hp=max_hp,  # Start at full HP
            initiative=initiative,
            combatant_type=combatant_type
        )
        
        # Add to encounter and sort
        self.current_encounter.add_combatant(combatant)
        
        return combatant
    
    def remove_combatant(self, name: str) -> None:
        """Remove a combatant from the current encounter.
        
        Args:
            name: Name of combatant to remove
            
        Raises:
            EncounterNotLoadedError: If no encounter is currently loaded
            CombatantNotFoundError: If combatant doesn't exist
        """
        if not self.current_encounter:
            raise EncounterNotLoadedError("No encounter is currently loaded")
        
        try:
            self.current_encounter.remove_combatant(name)
        except ValidationError as e:
            raise CombatantNotFoundError(str(e))
    
    def update_hp(self, combatant_name: str, hp_change: str) -> None:
        """Update a combatant's hit points.
        
        Args:
            combatant_name: Name of combatant to update
            hp_change: HP change as string (e.g., "15", "+5", "-8")
            
        Raises:
            EncounterNotLoadedError: If no encounter is currently loaded
            CombatantNotFoundError: If combatant doesn't exist
            InvalidHPValueError: If HP value is invalid
        """
        if not self.current_encounter:
            raise EncounterNotLoadedError("update hit points")
        
        combatant = self.current_encounter.get_combatant(combatant_name)
        if not combatant:
            available_names = [c.name for c in self.current_encounter.combatants]
            raise CombatantNotFoundError(combatant_name, available_names)
        
        try:
            combatant.update_hp(hp_change)
        except InvalidHPValueError as e:
            # Enhance with current HP context
            raise InvalidHPValueError(
                hp_value=hp_change,
                reason=str(e),
                current_hp=combatant.current_hp,
                max_hp=combatant.max_hp
            )
    
    def adjust_initiative(self, combatant_name: str, new_initiative: int) -> None:
        """Adjust a combatant's initiative value.
        
        Args:
            combatant_name: Name of combatant to adjust
            new_initiative: New initiative value
            
        Raises:
            EncounterNotLoadedError: If no encounter is currently loaded
            CombatantNotFoundError: If combatant doesn't exist
        """
        if not self.current_encounter:
            raise EncounterNotLoadedError("No encounter is currently loaded")
        
        try:
            self.current_encounter.adjust_initiative(combatant_name, new_initiative)
        except ValidationError as e:
            raise CombatantNotFoundError(str(e))
    
    def add_note(self, combatant_name: str, note: str) -> None:
        """Add a note to a combatant.
        
        Args:
            combatant_name: Name of combatant to add note to
            note: Note text to add
            
        Raises:
            EncounterNotLoadedError: If no encounter is currently loaded
            CombatantNotFoundError: If combatant doesn't exist
            ValidationError: If note is invalid
        """
        if not self.current_encounter:
            raise EncounterNotLoadedError("add note")
        
        combatant = self.current_encounter.get_combatant(combatant_name)
        if not combatant:
            available_names = [c.name for c in self.current_encounter.combatants]
            raise CombatantNotFoundError(combatant_name, available_names)
        
        if not note or not note.strip():
            raise ValidationError(
                field="note text",
                value=note,
                reason="Note cannot be empty",
                valid_examples=["Blessed by cleric", "Poisoned", "Has inspiration"]
            )
        
        combatant.add_note(note)
    
    def remove_note(self, combatant_name: str, note_index: int) -> None:
        """Remove a note from a combatant.
        
        Args:
            combatant_name: Name of combatant to remove note from
            note_index: Index of note to remove (0-based)
            
        Raises:
            EncounterNotLoadedError: If no encounter is currently loaded
            CombatantNotFoundError: If combatant doesn't exist
            NoteIndexError: If note index is invalid
        """
        if not self.current_encounter:
            raise EncounterNotLoadedError("remove note")
        
        combatant = self.current_encounter.get_combatant(combatant_name)
        if not combatant:
            available_names = [c.name for c in self.current_encounter.combatants]
            raise CombatantNotFoundError(combatant_name, available_names)
        
        if note_index < 0 or note_index >= len(combatant.notes):
            raise NoteIndexError(note_index + 1, len(combatant.notes), combatant_name)
        
        combatant.remove_note(note_index)
    
    def edit_note(self, combatant_name: str, note_index: int, new_note: str) -> None:
        """Edit a note for a combatant.
        
        Args:
            combatant_name: Name of combatant to edit note for
            note_index: Index of note to edit (0-based)
            new_note: New note text
            
        Raises:
            EncounterNotLoadedError: If no encounter is currently loaded
            CombatantNotFoundError: If combatant doesn't exist
            NoteIndexError: If note index is invalid
            ValidationError: If note is empty
        """
        if not self.current_encounter:
            raise EncounterNotLoadedError("edit note")
        
        combatant = self.current_encounter.get_combatant(combatant_name)
        if not combatant:
            available_names = [c.name for c in self.current_encounter.combatants]
            raise CombatantNotFoundError(combatant_name, available_names)
        
        if note_index < 0 or note_index >= len(combatant.notes):
            raise NoteIndexError(note_index + 1, len(combatant.notes), combatant_name)
        
        if not new_note or not new_note.strip():
            raise ValidationError(
                field="note text",
                value=new_note,
                reason="Note cannot be empty",
                valid_examples=["Blessed by cleric", "Poisoned", "Has inspiration"]
            )
        
        combatant.edit_note(note_index, new_note)
    
    def get_initiative_order(self) -> List[Combatant]:
        """Get combatants in initiative order.
        
        Returns:
            List of combatants sorted by initiative, empty list if no encounter
        """
        if not self.current_encounter:
            return []
        
        return self.current_encounter.get_initiative_order()
    
    def get_combatant(self, name: str) -> Optional[Combatant]:
        """Get a combatant by name.
        
        Args:
            name: Name of combatant to find
            
        Returns:
            Combatant if found, None otherwise
        """
        if not self.current_encounter:
            return None
        
        return self.current_encounter.get_combatant(name)
    
    def next_turn(self) -> Optional[Combatant]:
        """Advance to the next turn.
        
        Returns:
            Current combatant after advancing turn, None if no encounter
        """
        if not self.current_encounter:
            return None
        
        return self.current_encounter.next_turn()
    
    def get_current_combatant(self) -> Optional[Combatant]:
        """Get the combatant whose turn it is.
        
        Returns:
            Current combatant, None if no encounter or no combatants
        """
        if not self.current_encounter:
            return None
        
        return self.current_encounter.get_current_combatant()
    
    def reorder_combatants_with_same_initiative(self, initiative_value: int, 
                                              ordered_names: List[str]) -> None:
        """Manually reorder combatants that have the same initiative value.
        
        Args:
            initiative_value: The initiative value to reorder
            ordered_names: List of combatant names in desired order
            
        Raises:
            EncounterNotLoadedError: If no encounter is currently loaded
            ValidationError: If reordering parameters are invalid
        """
        if not self.current_encounter:
            raise EncounterNotLoadedError("No encounter is currently loaded")
        
        self.current_encounter.reorder_combatants_with_same_initiative(
            initiative_value, ordered_names
        )
    
    def get_available_encounters(self) -> List[str]:
        """Get list of available encounter files.
        
        Returns:
            List of encounter filenames (without .json extension)
        """
        return self.data_manager.get_available_encounters()
    
    def encounter_exists(self, filename: str) -> bool:
        """Check if an encounter file exists.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            True if file exists
        """
        return self.data_manager.encounter_exists(filename)
    
    def delete_encounter(self, filename: str) -> None:
        """Delete an encounter file.
        
        Args:
            filename: Name of the file to delete
            
        Raises:
            FileFormatError: If file doesn't exist or deletion fails
        """
        self.data_manager.delete_encounter(filename)
    
    def has_current_encounter(self) -> bool:
        """Check if there is a currently loaded encounter.
        
        Returns:
            True if an encounter is currently loaded
        """
        return self.current_encounter is not None
    
    def get_encounter_summary(self) -> dict:
        """Get a summary of the current encounter.
        
        Returns:
            Dictionary with encounter summary information
        """
        if not self.current_encounter:
            return {
                "name": None,
                "combatant_count": 0,
                "current_turn": None,
                "round_number": 0,
                "has_combatants": False
            }
        
        current_combatant = self.current_encounter.get_current_combatant()
        
        return {
            "name": self.current_encounter.name,
            "combatant_count": len(self.current_encounter.combatants),
            "current_turn": current_combatant.name if current_combatant else None,
            "round_number": self.current_encounter.round_number,
            "has_combatants": self.current_encounter.has_combatants()
        }
    
    def get_encounter_metadata(self, filename: str) -> dict:
        """Get metadata for an encounter file.
        
        Args:
            filename: Name of the file to get metadata for
            
        Returns:
            Dictionary with file metadata
            
        Raises:
            FileFormatError: If file doesn't exist or can't be read
        """
        return self.data_manager.get_encounter_metadata(filename)
    
    def list_encounters_with_metadata(self) -> List[dict]:
        """Get list of available encounters with their metadata.
        
        Returns:
            List of dictionaries containing encounter info and metadata
        """
        return self.data_manager.list_encounters_with_metadata()
    
    def backup_encounter(self, filename: str) -> str:
        """Create a backup of an encounter file.
        
        Args:
            filename: Name of the file to backup
            
        Returns:
            Path to the backup file
            
        Raises:
            FileFormatError: If file doesn't exist or backup fails
        """
        return self.data_manager.backup_encounter(filename)
    
    def cleanup_old_backups(self, max_backups: int = 5) -> List[str]:
        """Clean up old backup files.
        
        Args:
            max_backups: Maximum number of backup files to keep per encounter
            
        Returns:
            List of deleted backup file paths
        """
        return self.data_manager.cleanup_old_backups(max_backups)