"""Service layer for note management operations."""

from typing import List, Optional
from .models import Encounter, Combatant
from .exceptions import ValidationError, CombatantNotFoundError, EncounterNotLoadedError


class NoteService:
    """Service for managing combatant notes within encounters."""
    
    def __init__(self, encounter: Optional[Encounter] = None):
        """Initialize note service.
        
        Args:
            encounter: The encounter to manage notes for
        """
        self.encounter = encounter
    
    def set_encounter(self, encounter: Encounter) -> None:
        """Set the current encounter.
        
        Args:
            encounter: The encounter to manage notes for
        """
        self.encounter = encounter
    
    def add_note(self, combatant_name: str, note_text: str) -> None:
        """Add a note to a combatant.
        
        Args:
            combatant_name: Name of the combatant
            note_text: Text of the note to add
            
        Raises:
            CombatantNotFoundError: If combatant doesn't exist
            ValidationError: If note text is invalid
        """
        if not self.encounter:
            raise EncounterNotLoadedError("add note")
        
        combatant = self.encounter.get_combatant(combatant_name)
        if not combatant:
            available_names = [c.name for c in self.encounter.combatants]
            raise CombatantNotFoundError(combatant_name, available_names)
        
        combatant.add_note(note_text)
    
    def remove_note(self, combatant_name: str, note_index: int) -> None:
        """Remove a note from a combatant by index.
        
        Args:
            combatant_name: Name of the combatant
            note_index: Index of the note to remove (0-based)
            
        Raises:
            CombatantNotFoundError: If combatant doesn't exist
            ValidationError: If note index is invalid
        """
        if not self.encounter:
            raise EncounterNotLoadedError("remove note")
        
        combatant = self.encounter.get_combatant(combatant_name)
        if not combatant:
            available_names = [c.name for c in self.encounter.combatants]
            raise CombatantNotFoundError(combatant_name, available_names)
        
        combatant.remove_note(note_index)
    
    def edit_note(self, combatant_name: str, note_index: int, new_text: str) -> None:
        """Edit a note for a combatant.
        
        Args:
            combatant_name: Name of the combatant
            note_index: Index of the note to edit (0-based)
            new_text: New text for the note
            
        Raises:
            CombatantNotFoundError: If combatant doesn't exist
            ValidationError: If note index is invalid or text is empty
        """
        if not self.encounter:
            raise EncounterNotLoadedError("edit note")
        
        combatant = self.encounter.get_combatant(combatant_name)
        if not combatant:
            available_names = [c.name for c in self.encounter.combatants]
            raise CombatantNotFoundError(combatant_name, available_names)
        
        combatant.edit_note(note_index, new_text)
    
    def get_notes(self, combatant_name: str) -> List[str]:
        """Get all notes for a combatant.
        
        Args:
            combatant_name: Name of the combatant
            
        Returns:
            List of notes for the combatant
            
        Raises:
            CombatantNotFoundError: If combatant doesn't exist
        """
        if not self.encounter:
            raise EncounterNotLoadedError("get notes")
        
        combatant = self.encounter.get_combatant(combatant_name)
        if not combatant:
            available_names = [c.name for c in self.encounter.combatants]
            raise CombatantNotFoundError(combatant_name, available_names)
        
        return combatant.notes.copy()
    
    def get_combatants_with_notes(self) -> List[Combatant]:
        """Get all combatants that have notes.
        
        Returns:
            List of combatants with notes
        """
        if not self.encounter:
            raise EncounterNotLoadedError("get combatants with notes")
        
        return [c for c in self.encounter.combatants if c.has_notes()]
    
    def clear_all_notes(self, combatant_name: str) -> int:
        """Clear all notes for a combatant.
        
        Args:
            combatant_name: Name of the combatant
            
        Returns:
            Number of notes that were cleared
            
        Raises:
            CombatantNotFoundError: If combatant doesn't exist
        """
        if not self.encounter:
            raise EncounterNotLoadedError("clear notes")
        
        combatant = self.encounter.get_combatant(combatant_name)
        if not combatant:
            available_names = [c.name for c in self.encounter.combatants]
            raise CombatantNotFoundError(combatant_name, available_names)
        
        note_count = len(combatant.notes)
        combatant.notes.clear()
        return note_count
    
    def search_notes(self, search_term: str) -> List[tuple[str, int, str]]:
        """Search for notes containing a specific term.
        
        Args:
            search_term: Term to search for in notes
            
        Returns:
            List of tuples (combatant_name, note_index, note_text) for matching notes
        """
        if not self.encounter:
            raise EncounterNotLoadedError("search notes")
        
        results = []
        search_lower = search_term.lower()
        
        for combatant in self.encounter.combatants:
            for i, note in enumerate(combatant.notes):
                if search_lower in note.lower():
                    results.append((combatant.name, i, note))
        
        return results
    
    def get_note_statistics(self) -> dict:
        """Get statistics about notes in the encounter.
        
        Returns:
            Dictionary with note statistics
        """
        if not self.encounter:
            raise EncounterNotLoadedError("get note statistics")
        
        total_notes = 0
        combatants_with_notes = 0
        max_notes_per_combatant = 0
        
        for combatant in self.encounter.combatants:
            note_count = len(combatant.notes)
            total_notes += note_count
            
            if note_count > 0:
                combatants_with_notes += 1
                max_notes_per_combatant = max(max_notes_per_combatant, note_count)
        
        return {
            'total_notes': total_notes,
            'total_combatants': len(self.encounter.combatants),
            'combatants_with_notes': combatants_with_notes,
            'combatants_without_notes': len(self.encounter.combatants) - combatants_with_notes,
            'max_notes_per_combatant': max_notes_per_combatant,
            'average_notes_per_combatant': total_notes / len(self.encounter.combatants) if self.encounter.combatants else 0
        }