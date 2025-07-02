"""Data models for the D&D Encounter Tracker."""

from dataclasses import dataclass, field
from typing import List, Optional
import re

from .exceptions import ValidationError, InvalidHPValueError, DuplicateCombatantError, CombatantNotFoundError


@dataclass
class Combatant:
    """Represents a combatant in an encounter."""
    
    name: str
    max_hp: int
    current_hp: int
    initiative: int
    notes: List[str] = field(default_factory=list)
    combatant_type: str = "unknown"  # "player", "monster", "npc"
    _tie_breaker: float = field(default=0.0, init=False)  # For manual initiative ordering
    
    def __post_init__(self):
        """Validate combatant data after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate combatant data."""
        if not self.name or not self.name.strip():
            raise ValidationError("combatant name", self.name, "cannot be empty", ["Hero", "Goblin Scout", "Ancient Dragon"])
        
        if self.max_hp <= 0:
            raise ValidationError("maximum HP", self.max_hp, "must be positive", ["10", "25", "100"])
        
        if self.current_hp < 0:
            raise ValidationError("current HP", self.current_hp, "cannot be negative", ["0", "10", "25"])
        
        if self.current_hp > self.max_hp:
            raise ValidationError("current HP", self.current_hp, "cannot exceed maximum HP", [str(self.max_hp)])
        
        if self.combatant_type not in ["player", "monster", "npc", "unknown"]:
            raise ValidationError("combatant type", self.combatant_type, "is not valid", ["player", "monster", "npc", "unknown"])
    
    def update_hp(self, value: str) -> None:
        """Update hit points with absolute, addition, or subtraction values.
        
        Args:
            value: HP value as string (e.g., "15", "+5", "-8")
        """
        value = value.strip()
        
        if not value:
            raise InvalidHPValueError(
                hp_value=value,
                reason="HP value cannot be empty"
            )
        
        # Handle relative changes (+5, -8)
        if value.startswith(('+', '-')):
            if not re.match(r'^[+-]\d+$', value):
                raise InvalidHPValueError(
                    hp_value=value,
                    reason="Invalid HP change format"
                )
            
            change = int(value)
            new_hp = self.current_hp + change
        else:
            # Handle absolute values (15)
            if not value.isdigit():
                raise InvalidHPValueError(
                    hp_value=value,
                    reason="Invalid HP value format"
                )
            
            new_hp = int(value)
        
        # Validate new HP value
        if new_hp < 0:
            new_hp = 0
        elif new_hp > self.max_hp:
            new_hp = self.max_hp
        
        self.current_hp = new_hp
    
    def add_note(self, note: str) -> None:
        """Add a note to the combatant.
        
        Args:
            note: Note text to add
        """
        if not note or not note.strip():
            raise ValidationError("note", note, "cannot be empty", ["Status effect", "Blessed", "Prone"])
        
        self.notes.append(note.strip())
    
    def remove_note(self, index: int) -> None:
        """Remove a note by index.
        
        Args:
            index: Index of note to remove
        """
        if index < 0 or index >= len(self.notes):
            valid_indices = [str(i) for i in range(len(self.notes))] if self.notes else []
            raise ValidationError("note index", index, f"is invalid (valid range: 0-{len(self.notes)-1})" if self.notes else "is invalid (no notes exist)", valid_indices)
        
        self.notes.pop(index)
    
    def edit_note(self, index: int, new_note: str) -> None:
        """Edit a note by index.
        
        Args:
            index: Index of note to edit
            new_note: New note text
        """
        if index < 0 or index >= len(self.notes):
            valid_indices = [str(i) for i in range(len(self.notes))] if self.notes else []
            raise ValidationError("note index", index, f"is invalid (valid range: 0-{len(self.notes)-1})" if self.notes else "is invalid (no notes exist)", valid_indices)
        
        if not new_note or not new_note.strip():
            raise ValidationError("note", new_note, "cannot be empty", ["Status effect", "Blessed", "Prone"])
        
        self.notes[index] = new_note.strip()
    
    def is_alive(self) -> bool:
        """Check if combatant is alive (has HP > 0)."""
        return self.current_hp > 0
    
    def has_notes(self) -> bool:
        """Check if combatant has any notes."""
        return len(self.notes) > 0


@dataclass
class Encounter:
    """Represents a combat encounter."""
    
    name: str
    combatants: List[Combatant] = field(default_factory=list)
    current_turn: int = 0
    round_number: int = 1
    
    def __post_init__(self):
        """Validate encounter data after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate encounter data."""
        if not self.name or not self.name.strip():
            raise ValidationError("encounter name", self.name, "cannot be empty", ["Goblin Ambush", "Dragon's Lair", "Tavern Brawl"])
        
        if self.current_turn < 0:
            raise ValidationError("current turn", self.current_turn, "cannot be negative", ["0", "1", "2"])
        
        if self.round_number < 1:
            raise ValidationError("round number", self.round_number, "must be at least 1", ["1", "2", "3"])
        
        if self.combatants and self.current_turn >= len(self.combatants):
            max_turn = len(self.combatants) - 1
            raise ValidationError("current turn", self.current_turn, f"exceeds combatant count (max: {max_turn})", [str(i) for i in range(len(self.combatants))])
    
    def add_combatant(self, combatant: Combatant) -> None:
        """Add a combatant to the encounter.
        
        Args:
            combatant: Combatant to add
        """
        # Check for duplicate names
        if any(c.name.lower() == combatant.name.lower() for c in self.combatants):
            raise DuplicateCombatantError(combatant.name)
        
        self.combatants.append(combatant)
        self.sort_by_initiative()
    
    def remove_combatant(self, name: str) -> None:
        """Remove a combatant by name.
        
        Args:
            name: Name of combatant to remove
        """
        # Find the index of the combatant to remove
        removed_index = None
        for i, combatant in enumerate(self.combatants):
            if combatant.name.lower() == name.lower():
                removed_index = i
                break
        
        if removed_index is None:
            available_names = [c.name for c in self.combatants]
            raise CombatantNotFoundError(name, available_names)
        
        # Remove the combatant
        self.combatants.pop(removed_index)
        
        # Adjust current turn if necessary
        if not self.combatants:
            # No combatants left
            self.current_turn = 0
        elif removed_index < self.current_turn:
            # Removed combatant was before current turn, shift current turn back
            self.current_turn -= 1
        elif removed_index == self.current_turn:
            # Removed the current combatant
            if self.current_turn >= len(self.combatants):
                # Current turn is now beyond the list, wrap to beginning
                self.current_turn = 0
        # If removed_index > self.current_turn, no adjustment needed
    
    def get_combatant(self, name: str) -> Optional[Combatant]:
        """Get a combatant by name.
        
        Args:
            name: Name of combatant to find
            
        Returns:
            Combatant if found, None otherwise
        """
        for combatant in self.combatants:
            if combatant.name.lower() == name.lower():
                return combatant
        return None
    
    def sort_by_initiative(self) -> None:
        """Sort combatants by initiative in descending order."""
        if not self.combatants:
            return
        
        # Remember current combatant if any
        current_combatant = None
        if self.combatants and 0 <= self.current_turn < len(self.combatants):
            current_combatant = self.combatants[self.current_turn]
        
        # Sort by initiative (highest first), then by tie_breaker, then by name for final tie-breaking
        self.combatants.sort(key=lambda c: (-c.initiative, c._tie_breaker, c.name.lower()))
        
        # Update current turn index to follow the same combatant
        if current_combatant:
            for i, combatant in enumerate(self.combatants):
                if combatant is current_combatant:
                    self.current_turn = i
                    break
    
    def next_turn(self) -> Optional[Combatant]:
        """Advance to the next turn and return the current combatant.
        
        Returns:
            Current combatant after advancing turn, None if no combatants
        """
        if not self.combatants:
            return None
        
        self.current_turn += 1
        if self.current_turn >= len(self.combatants):
            self.current_turn = 0
            self.round_number += 1
        
        return self.get_current_combatant()
    
    def get_current_combatant(self) -> Optional[Combatant]:
        """Get the combatant whose turn it is.
        
        Returns:
            Current combatant, None if no combatants or invalid turn
        """
        if not self.combatants or self.current_turn >= len(self.combatants):
            return None
        
        return self.combatants[self.current_turn]
    
    def adjust_initiative(self, name: str, new_initiative: int) -> None:
        """Adjust a combatant's initiative and re-sort the encounter.
        
        Args:
            name: Name of combatant to adjust
            new_initiative: New initiative value
        """
        combatant = self.get_combatant(name)
        if not combatant:
            available_names = [c.name for c in self.combatants]
            raise CombatantNotFoundError(name, available_names)
        
        combatant.initiative = new_initiative
        self.sort_by_initiative()
    
    def reorder_combatants_with_same_initiative(self, initiative_value: int, ordered_names: List[str]) -> None:
        """Manually reorder combatants that have the same initiative value.
        
        This allows for manual tie-breaking when multiple combatants have identical initiative.
        
        Args:
            initiative_value: The initiative value to reorder
            ordered_names: List of combatant names in desired order (first to last)
        """
        # Find all combatants with the specified initiative
        same_init_combatants = [c for c in self.combatants if c.initiative == initiative_value]
        
        if len(same_init_combatants) < 2:
            raise ValidationError("initiative reorder", initiative_value, f"not enough combatants with this initiative to reorder (found {len(same_init_combatants)})", ["Need at least 2 combatants with same initiative"])
        
        # Validate that all provided names exist and have the correct initiative
        same_init_names = {c.name.lower() for c in same_init_combatants}
        provided_names = {name.lower() for name in ordered_names}
        
        if same_init_names != provided_names:
            missing = same_init_names - provided_names
            extra = provided_names - same_init_names
            error_msg = f"Name mismatch for initiative {initiative_value}"
            if missing:
                error_msg += f" - Missing: {', '.join(missing)}"
            if extra:
                error_msg += f" - Extra: {', '.join(extra)}"
            expected_names = [c.name for c in same_init_combatants]
            raise ValidationError("combatant names", ordered_names, error_msg, expected_names)
        
        # Set tie-breaker values based on desired order
        name_to_order = {name.lower(): i for i, name in enumerate(ordered_names)}
        
        for combatant in same_init_combatants:
            combatant._tie_breaker = name_to_order.get(combatant.name.lower(), 999)
        
        # Re-sort the encounter
        self.sort_by_initiative()
    
    def get_initiative_order(self) -> List[Combatant]:
        """Get combatants in initiative order.
        
        Returns:
            List of combatants sorted by initiative
        """
        return self.combatants.copy()
    
    def get_combatants_by_initiative(self, initiative_value: int) -> List[Combatant]:
        """Get all combatants with a specific initiative value.
        
        Args:
            initiative_value: Initiative value to filter by
            
        Returns:
            List of combatants with the specified initiative
        """
        return [c for c in self.combatants if c.initiative == initiative_value]
    
    def has_combatants(self) -> bool:
        """Check if encounter has any combatants."""
        return len(self.combatants) > 0