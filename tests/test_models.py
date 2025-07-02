"""Unit tests for data models."""

import pytest
from dnd_encounter_tracker.core.models import Combatant, Encounter
from dnd_encounter_tracker.core.exceptions import ValidationError, InvalidHPValueError, DuplicateCombatantError, CombatantNotFoundError


class TestCombatant:
    """Test cases for Combatant model."""
    
    def test_valid_combatant_creation(self):
        """Test creating a valid combatant."""
        combatant = Combatant(
            name="Thorin",
            max_hp=45,
            current_hp=32,
            initiative=18,
            combatant_type="player"
        )
        
        assert combatant.name == "Thorin"
        assert combatant.max_hp == 45
        assert combatant.current_hp == 32
        assert combatant.initiative == 18
        assert combatant.combatant_type == "player"
        assert combatant.notes == []
        assert combatant.is_alive() is True
        assert combatant.has_notes() is False
    
    def test_combatant_with_notes(self):
        """Test creating a combatant with initial notes."""
        combatant = Combatant(
            name="Gandalf",
            max_hp=30,
            current_hp=30,
            initiative=15,
            notes=["Blessed", "Has inspiration"]
        )
        
        assert len(combatant.notes) == 2
        assert "Blessed" in combatant.notes
        assert combatant.has_notes() is True
    
    def test_empty_name_validation(self):
        """Test that empty name raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid combatant name"):
            Combatant(name="", max_hp=10, current_hp=10, initiative=10)
        
        with pytest.raises(ValidationError, match="Invalid combatant name"):
            Combatant(name="   ", max_hp=10, current_hp=10, initiative=10)
    
    def test_invalid_max_hp_validation(self):
        """Test that invalid max HP raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid maximum HP"):
            Combatant(name="Test", max_hp=0, current_hp=0, initiative=10)
        
        with pytest.raises(ValidationError, match="Invalid maximum HP"):
            Combatant(name="Test", max_hp=-5, current_hp=0, initiative=10)
    
    def test_negative_current_hp_validation(self):
        """Test that negative current HP raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid current HP"):
            Combatant(name="Test", max_hp=10, current_hp=-1, initiative=10)
    
    def test_current_hp_exceeds_max_validation(self):
        """Test that current HP exceeding max HP raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid current HP"):
            Combatant(name="Test", max_hp=10, current_hp=15, initiative=10)
    
    def test_invalid_combatant_type_validation(self):
        """Test that invalid combatant type raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid combatant type"):
            Combatant(name="Test", max_hp=10, current_hp=10, initiative=10, combatant_type="invalid")
    
    def test_valid_combatant_types(self):
        """Test that all valid combatant types are accepted."""
        valid_types = ["player", "monster", "npc", "unknown"]
        
        for combatant_type in valid_types:
            combatant = Combatant(
                name="Test",
                max_hp=10,
                current_hp=10,
                initiative=10,
                combatant_type=combatant_type
            )
            assert combatant.combatant_type == combatant_type
    
    def test_update_hp_absolute_value(self):
        """Test updating HP with absolute values."""
        combatant = Combatant(name="Test", max_hp=50, current_hp=30, initiative=10)
        
        combatant.update_hp("25")
        assert combatant.current_hp == 25
        
        combatant.update_hp("50")
        assert combatant.current_hp == 50
        
        combatant.update_hp("0")
        assert combatant.current_hp == 0
    
    def test_update_hp_addition(self):
        """Test updating HP with addition."""
        combatant = Combatant(name="Test", max_hp=50, current_hp=30, initiative=10)
        
        combatant.update_hp("+5")
        assert combatant.current_hp == 35
        
        combatant.update_hp("+20")
        assert combatant.current_hp == 50  # Capped at max HP
    
    def test_update_hp_subtraction(self):
        """Test updating HP with subtraction."""
        combatant = Combatant(name="Test", max_hp=50, current_hp=30, initiative=10)
        
        combatant.update_hp("-10")
        assert combatant.current_hp == 20
        
        combatant.update_hp("-25")
        assert combatant.current_hp == 0  # Cannot go below 0
    
    def test_update_hp_invalid_format(self):
        """Test that invalid HP formats raise InvalidHPValueError."""
        combatant = Combatant(name="Test", max_hp=50, current_hp=30, initiative=10)
        
        with pytest.raises(InvalidHPValueError, match="HP value cannot be empty"):
            combatant.update_hp("")
        
        with pytest.raises(InvalidHPValueError, match="Invalid HP value format"):
            combatant.update_hp("abc")
        
        with pytest.raises(InvalidHPValueError, match="Invalid HP change format"):
            combatant.update_hp("+abc")
        
        with pytest.raises(InvalidHPValueError, match="Invalid HP change format"):
            combatant.update_hp("+-5")
    
    def test_add_note(self):
        """Test adding notes to combatant."""
        combatant = Combatant(name="Test", max_hp=10, current_hp=10, initiative=10)
        
        combatant.add_note("Blessed by cleric")
        assert len(combatant.notes) == 1
        assert combatant.notes[0] == "Blessed by cleric"
        assert combatant.has_notes() is True
        
        combatant.add_note("Has inspiration")
        assert len(combatant.notes) == 2
        assert "Has inspiration" in combatant.notes
    
    def test_add_empty_note_validation(self):
        """Test that empty notes raise ValidationError."""
        combatant = Combatant(name="Test", max_hp=10, current_hp=10, initiative=10)
        
        with pytest.raises(ValidationError, match="Invalid note"):
            combatant.add_note("")
        
        with pytest.raises(ValidationError, match="Invalid note"):
            combatant.add_note("   ")
    
    def test_remove_note(self):
        """Test removing notes from combatant."""
        combatant = Combatant(
            name="Test",
            max_hp=10,
            current_hp=10,
            initiative=10,
            notes=["Note 1", "Note 2", "Note 3"]
        )
        
        combatant.remove_note(1)  # Remove "Note 2"
        assert len(combatant.notes) == 2
        assert "Note 2" not in combatant.notes
        assert "Note 1" in combatant.notes
        assert "Note 3" in combatant.notes
    
    def test_remove_note_invalid_index(self):
        """Test that invalid note index raises ValidationError."""
        combatant = Combatant(
            name="Test",
            max_hp=10,
            current_hp=10,
            initiative=10,
            notes=["Note 1"]
        )
        
        with pytest.raises(ValidationError, match="Invalid note index"):
            combatant.remove_note(-1)
        
        with pytest.raises(ValidationError, match="Invalid note index"):
            combatant.remove_note(1)
    
    def test_edit_note(self):
        """Test editing notes."""
        combatant = Combatant(
            name="Test",
            max_hp=10,
            current_hp=10,
            initiative=10,
            notes=["Original note"]
        )
        
        combatant.edit_note(0, "Edited note")
        assert combatant.notes[0] == "Edited note"
    
    def test_edit_note_invalid_index(self):
        """Test that invalid note index for editing raises ValidationError."""
        combatant = Combatant(name="Test", max_hp=10, current_hp=10, initiative=10)
        
        with pytest.raises(ValidationError, match="Invalid note index"):
            combatant.edit_note(0, "New note")
    
    def test_edit_note_empty_text(self):
        """Test that editing with empty text raises ValidationError."""
        combatant = Combatant(
            name="Test",
            max_hp=10,
            current_hp=10,
            initiative=10,
            notes=["Original note"]
        )
        
        with pytest.raises(ValidationError, match="Invalid note"):
            combatant.edit_note(0, "")
    
    def test_is_alive(self):
        """Test is_alive method."""
        alive_combatant = Combatant(name="Alive", max_hp=10, current_hp=5, initiative=10)
        dead_combatant = Combatant(name="Dead", max_hp=10, current_hp=0, initiative=10)
        
        assert alive_combatant.is_alive() is True
        assert dead_combatant.is_alive() is False


class TestEncounter:
    """Test cases for Encounter model."""
    
    def test_valid_encounter_creation(self):
        """Test creating a valid encounter."""
        encounter = Encounter(name="Goblin Ambush")
        
        assert encounter.name == "Goblin Ambush"
        assert encounter.combatants == []
        assert encounter.current_turn == 0
        assert encounter.round_number == 1
        assert encounter.has_combatants() is False
    
    def test_encounter_with_combatants(self):
        """Test creating encounter with initial combatants."""
        combatant1 = Combatant(name="Hero", max_hp=20, current_hp=20, initiative=15)
        combatant2 = Combatant(name="Goblin", max_hp=10, current_hp=10, initiative=12)
        
        encounter = Encounter(
            name="Test Encounter",
            combatants=[combatant1, combatant2]
        )
        
        assert len(encounter.combatants) == 2
        assert encounter.has_combatants() is True
    
    def test_empty_name_validation(self):
        """Test that empty encounter name raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid encounter name"):
            Encounter(name="")
        
        with pytest.raises(ValidationError, match="Invalid encounter name"):
            Encounter(name="   ")
    
    def test_negative_current_turn_validation(self):
        """Test that negative current turn raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid current turn"):
            Encounter(name="Test", current_turn=-1)
    
    def test_invalid_round_number_validation(self):
        """Test that invalid round number raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid round number"):
            Encounter(name="Test", round_number=0)
        
        with pytest.raises(ValidationError, match="Invalid round number"):
            Encounter(name="Test", round_number=-1)
    
    def test_current_turn_exceeds_combatants_validation(self):
        """Test that current turn exceeding combatant count raises ValidationError."""
        combatant = Combatant(name="Test", max_hp=10, current_hp=10, initiative=10)
        
        with pytest.raises(ValidationError, match="Invalid current turn"):
            Encounter(name="Test", combatants=[combatant], current_turn=1)
    
    def test_add_combatant(self):
        """Test adding combatants to encounter."""
        encounter = Encounter(name="Test Encounter")
        combatant = Combatant(name="Hero", max_hp=20, current_hp=20, initiative=15)
        
        encounter.add_combatant(combatant)
        
        assert len(encounter.combatants) == 1
        assert encounter.combatants[0] is combatant
        assert encounter.has_combatants() is True
    
    def test_add_duplicate_combatant_name(self):
        """Test that adding combatant with duplicate name raises ValidationError."""
        encounter = Encounter(name="Test Encounter")
        combatant1 = Combatant(name="Hero", max_hp=20, current_hp=20, initiative=15)
        combatant2 = Combatant(name="hero", max_hp=15, current_hp=15, initiative=12)  # Same name, different case
        
        encounter.add_combatant(combatant1)
        
        with pytest.raises(DuplicateCombatantError, match="already exists"):
            encounter.add_combatant(combatant2)
    
    def test_remove_combatant(self):
        """Test removing combatants from encounter."""
        encounter = Encounter(name="Test Encounter")
        combatant1 = Combatant(name="Hero", max_hp=20, current_hp=20, initiative=15)
        combatant2 = Combatant(name="Goblin", max_hp=10, current_hp=10, initiative=12)
        
        encounter.add_combatant(combatant1)
        encounter.add_combatant(combatant2)
        
        encounter.remove_combatant("Hero")
        
        assert len(encounter.combatants) == 1
        assert encounter.combatants[0].name == "Goblin"
    
    def test_remove_nonexistent_combatant(self):
        """Test that removing nonexistent combatant raises ValidationError."""
        encounter = Encounter(name="Test Encounter")
        
        with pytest.raises(CombatantNotFoundError, match="not found"):
            encounter.remove_combatant("Nonexistent")
    
    def test_get_combatant(self):
        """Test getting combatant by name."""
        encounter = Encounter(name="Test Encounter")
        combatant = Combatant(name="Hero", max_hp=20, current_hp=20, initiative=15)
        
        encounter.add_combatant(combatant)
        
        found = encounter.get_combatant("Hero")
        assert found is combatant
        
        found_case_insensitive = encounter.get_combatant("hero")
        assert found_case_insensitive is combatant
        
        not_found = encounter.get_combatant("Nonexistent")
        assert not_found is None
    
    def test_sort_by_initiative(self):
        """Test sorting combatants by initiative."""
        encounter = Encounter(name="Test Encounter")
        
        # Add combatants in random initiative order
        combatant1 = Combatant(name="Slow", max_hp=10, current_hp=10, initiative=8)
        combatant2 = Combatant(name="Fast", max_hp=10, current_hp=10, initiative=18)
        combatant3 = Combatant(name="Medium", max_hp=10, current_hp=10, initiative=12)
        
        encounter.add_combatant(combatant1)
        encounter.add_combatant(combatant2)
        encounter.add_combatant(combatant3)
        
        # Should be sorted by initiative (highest first)
        assert encounter.combatants[0].name == "Fast"
        assert encounter.combatants[1].name == "Medium"
        assert encounter.combatants[2].name == "Slow"
    
    def test_sort_by_initiative_with_ties(self):
        """Test sorting with initiative ties (should sort by name)."""
        encounter = Encounter(name="Test Encounter")
        
        combatant1 = Combatant(name="Zebra", max_hp=10, current_hp=10, initiative=15)
        combatant2 = Combatant(name="Alpha", max_hp=10, current_hp=10, initiative=15)
        
        encounter.add_combatant(combatant1)
        encounter.add_combatant(combatant2)
        
        # Same initiative, should sort by name alphabetically
        assert encounter.combatants[0].name == "Alpha"
        assert encounter.combatants[1].name == "Zebra"
    
    def test_next_turn(self):
        """Test advancing to next turn."""
        encounter = Encounter(name="Test Encounter")
        
        combatant1 = Combatant(name="First", max_hp=10, current_hp=10, initiative=20)
        combatant2 = Combatant(name="Second", max_hp=10, current_hp=10, initiative=15)
        
        encounter.add_combatant(combatant1)
        encounter.add_combatant(combatant2)
        
        # Initially should be first combatant's turn
        current = encounter.get_current_combatant()
        assert current.name == "First"
        assert encounter.current_turn == 0
        assert encounter.round_number == 1
        
        # Advance to next turn
        next_combatant = encounter.next_turn()
        assert next_combatant.name == "Second"
        assert encounter.current_turn == 1
        assert encounter.round_number == 1
        
        # Advance to next round
        next_combatant = encounter.next_turn()
        assert next_combatant.name == "First"
        assert encounter.current_turn == 0
        assert encounter.round_number == 2
    
    def test_next_turn_empty_encounter(self):
        """Test next turn with no combatants."""
        encounter = Encounter(name="Empty Encounter")
        
        result = encounter.next_turn()
        assert result is None
    
    def test_get_current_combatant(self):
        """Test getting current combatant."""
        encounter = Encounter(name="Test Encounter")
        
        # Empty encounter
        current = encounter.get_current_combatant()
        assert current is None
        
        # Add combatants
        combatant1 = Combatant(name="First", max_hp=10, current_hp=10, initiative=20)
        combatant2 = Combatant(name="Second", max_hp=10, current_hp=10, initiative=15)
        
        encounter.add_combatant(combatant1)
        encounter.add_combatant(combatant2)
        
        current = encounter.get_current_combatant()
        assert current.name == "First"
    
    def test_get_initiative_order(self):
        """Test getting initiative order."""
        encounter = Encounter(name="Test Encounter")
        
        combatant1 = Combatant(name="Slow", max_hp=10, current_hp=10, initiative=8)
        combatant2 = Combatant(name="Fast", max_hp=10, current_hp=10, initiative=18)
        
        encounter.add_combatant(combatant1)
        encounter.add_combatant(combatant2)
        
        order = encounter.get_initiative_order()
        
        assert len(order) == 2
        assert order[0].name == "Fast"
        assert order[1].name == "Slow"
        
        # Should be a copy, not the original list
        assert order is not encounter.combatants
    
    def test_remove_combatant_adjusts_current_turn(self):
        """Test that removing combatant adjusts current turn if necessary."""
        encounter = Encounter(name="Test Encounter")
        
        combatant1 = Combatant(name="First", max_hp=10, current_hp=10, initiative=20)
        combatant2 = Combatant(name="Second", max_hp=10, current_hp=10, initiative=15)
        
        encounter.add_combatant(combatant1)
        encounter.add_combatant(combatant2)
        
        # Set current turn to last combatant
        encounter.current_turn = 1
        
        # Remove the last combatant
        encounter.remove_combatant("Second")
        
        # Current turn should be adjusted
        assert encounter.current_turn == 0