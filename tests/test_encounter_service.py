"""Tests for the EncounterService class."""

import pytest
from unittest.mock import Mock, MagicMock
from dnd_encounter_tracker.core.encounter_service import EncounterService
from dnd_encounter_tracker.core.models import Encounter, Combatant
from dnd_encounter_tracker.core.exceptions import (
    ValidationError, CombatantNotFoundError, EncounterNotLoadedError,
    InvalidHPValueError, FileFormatError, DuplicateCombatantError, NoteIndexError
)
from dnd_encounter_tracker.data.persistence import DataManager


@pytest.fixture
def mock_data_manager():
    """Create a mock DataManager."""
    return Mock(spec=DataManager)


@pytest.fixture
def service(mock_data_manager):
    """Create an EncounterService with mocked DataManager."""
    return EncounterService(mock_data_manager)


@pytest.fixture
def sample_encounter():
    """Create a sample encounter for testing."""
    encounter = Encounter("Test Encounter")
    encounter.add_combatant(Combatant("Alice", 25, 25, 18, combatant_type="player"))
    encounter.add_combatant(Combatant("Bob", 30, 30, 15, combatant_type="player"))
    encounter.add_combatant(Combatant("Goblin", 7, 7, 12, combatant_type="monster"))
    return encounter


class TestEncounterCreation:
    """Test encounter creation functionality."""
    
    def test_create_encounter_success(self, service):
        """Test successful encounter creation."""
        encounter = service.create_encounter("New Encounter")
        
        assert encounter.name == "New Encounter"
        assert len(encounter.combatants) == 0
        assert service.current_encounter == encounter
    
    def test_create_encounter_strips_whitespace(self, service):
        """Test that encounter name whitespace is stripped."""
        encounter = service.create_encounter("  Spaced Name  ")
        
        assert encounter.name == "Spaced Name"
    
    def test_create_encounter_empty_name_raises_error(self, service):
        """Test that empty encounter name raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid encounter name"):
            service.create_encounter("")
        
        with pytest.raises(ValidationError, match="Invalid encounter name"):
            service.create_encounter("   ")
    
    def test_create_encounter_none_name_raises_error(self, service):
        """Test that None encounter name raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid encounter name"):
            service.create_encounter(None)


class TestEncounterLoading:
    """Test encounter loading functionality."""
    
    def test_load_encounter_success(self, service, mock_data_manager, sample_encounter):
        """Test successful encounter loading."""
        mock_data_manager.load_from_file.return_value = sample_encounter
        
        loaded_encounter = service.load_encounter("test.json")
        
        assert loaded_encounter == sample_encounter
        assert service.current_encounter == sample_encounter
        mock_data_manager.load_from_file.assert_called_once_with("test.json")
    
    def test_load_encounter_file_not_found(self, service, mock_data_manager):
        """Test loading non-existent encounter file."""
        mock_data_manager.load_from_file.side_effect = FileFormatError("nonexistent.json", "load", "File not found")
        
        with pytest.raises(FileFormatError, match="File not found"):
            service.load_encounter("nonexistent.json")
    
    def test_load_encounter_corrupted_file(self, service, mock_data_manager):
        """Test loading corrupted encounter file."""
        mock_data_manager.load_from_file.side_effect = FileFormatError("corrupted.json", "load", "Invalid JSON")
        
        with pytest.raises(FileFormatError, match="Invalid JSON"):
            service.load_encounter("corrupted.json")


class TestEncounterSaving:
    """Test encounter saving functionality."""
    
    def test_save_encounter_success(self, service, mock_data_manager, sample_encounter):
        """Test successful encounter saving."""
        service.current_encounter = sample_encounter
        
        service.save_encounter("test.json")
        
        mock_data_manager.save_to_file.assert_called_once_with(sample_encounter, "test.json")
    
    def test_save_encounter_no_current_encounter(self, service, mock_data_manager):
        """Test saving when no encounter is loaded."""
        with pytest.raises(EncounterNotLoadedError, match="No encounter is currently loaded"):
            service.save_encounter("test.json")
        
        mock_data_manager.save_to_file.assert_not_called()
    
    def test_save_encounter_file_error(self, service, mock_data_manager, sample_encounter):
        """Test saving with file system error."""
        service.current_encounter = sample_encounter
        mock_data_manager.save_to_file.side_effect = FileFormatError("test.json", "save", "Permission denied")
        
        with pytest.raises(FileFormatError, match="Permission denied"):
            service.save_encounter("test.json")


class TestCombatantManagement:
    """Test combatant management functionality."""
    
    def test_add_combatant_success(self, service):
        """Test successful combatant addition."""
        service.create_encounter("Test")
        
        combatant = service.add_combatant("Alice", 25, 18, "player")
        
        assert combatant.name == "Alice"
        assert combatant.max_hp == 25
        assert combatant.current_hp == 25  # Should start at full HP
        assert combatant.initiative == 18
        assert combatant.combatant_type == "player"
        assert len(service.current_encounter.combatants) == 1
    
    def test_add_combatant_default_type(self, service):
        """Test adding combatant with default type."""
        service.create_encounter("Test")
        
        combatant = service.add_combatant("Bob", 30, 15)
        
        assert combatant.combatant_type == "unknown"
    
    def test_add_combatant_no_encounter(self, service):
        """Test adding combatant when no encounter is loaded."""
        with pytest.raises(EncounterNotLoadedError, match="No encounter is currently loaded"):
            service.add_combatant("Alice", 25, 18)
    
    def test_add_combatant_duplicate_name(self, service):
        """Test adding combatant with duplicate name."""
        service.create_encounter("Test")
        service.add_combatant("Alice", 25, 18)
        
        with pytest.raises(DuplicateCombatantError, match="already exists"):
            service.add_combatant("Alice", 30, 15)
    
    def test_add_combatant_invalid_data(self, service):
        """Test adding combatant with invalid data."""
        service.create_encounter("Test")
        
        with pytest.raises(ValidationError):
            service.add_combatant("", 25, 18)  # Empty name
        
        with pytest.raises(ValidationError):
            service.add_combatant("Alice", 0, 18)  # Zero HP
        
        with pytest.raises(ValidationError):
            service.add_combatant("Alice", 25, 18, "invalid_type")  # Invalid type
    
    def test_remove_combatant_success(self, service, sample_encounter):
        """Test successful combatant removal."""
        service.current_encounter = sample_encounter
        initial_count = len(sample_encounter.combatants)
        
        service.remove_combatant("Alice")
        
        assert len(service.current_encounter.combatants) == initial_count - 1
        assert service.current_encounter.get_combatant("Alice") is None
    
    def test_remove_combatant_not_found(self, service, sample_encounter):
        """Test removing non-existent combatant."""
        service.current_encounter = sample_encounter
        
        with pytest.raises(CombatantNotFoundError, match="not found"):
            service.remove_combatant("NonExistent")
    
    def test_remove_combatant_no_encounter(self, service):
        """Test removing combatant when no encounter is loaded."""
        with pytest.raises(EncounterNotLoadedError, match="No encounter is currently loaded"):
            service.remove_combatant("Alice")


class TestHitPointManagement:
    """Test hit point management functionality."""
    
    def test_update_hp_absolute_value(self, service, sample_encounter):
        """Test updating HP with absolute value."""
        service.current_encounter = sample_encounter
        
        service.update_hp("Alice", "20")
        
        alice = service.current_encounter.get_combatant("Alice")
        assert alice.current_hp == 20
    
    def test_update_hp_addition(self, service, sample_encounter):
        """Test updating HP with addition."""
        service.current_encounter = sample_encounter
        alice = service.current_encounter.get_combatant("Alice")
        # Reduce HP first so we can test addition
        alice.current_hp = 20
        initial_hp = alice.current_hp
        
        service.update_hp("Alice", "+5")
        
        assert alice.current_hp == initial_hp + 5
    
    def test_update_hp_subtraction(self, service, sample_encounter):
        """Test updating HP with subtraction."""
        service.current_encounter = sample_encounter
        alice = service.current_encounter.get_combatant("Alice")
        initial_hp = alice.current_hp
        
        service.update_hp("Alice", "-8")
        
        assert alice.current_hp == initial_hp - 8
    
    def test_update_hp_combatant_not_found(self, service, sample_encounter):
        """Test updating HP for non-existent combatant."""
        service.current_encounter = sample_encounter
        
        with pytest.raises(CombatantNotFoundError, match="not found"):
            service.update_hp("NonExistent", "20")
    
    def test_update_hp_no_encounter(self, service):
        """Test updating HP when no encounter is loaded."""
        with pytest.raises(EncounterNotLoadedError, match="No encounter is currently loaded"):
            service.update_hp("Alice", "20")
    
    def test_update_hp_invalid_value(self, service, sample_encounter):
        """Test updating HP with invalid value."""
        service.current_encounter = sample_encounter
        
        with pytest.raises(InvalidHPValueError):
            service.update_hp("Alice", "invalid")


class TestInitiativeManagement:
    """Test initiative management functionality."""
    
    def test_adjust_initiative_success(self, service, sample_encounter):
        """Test successful initiative adjustment."""
        service.current_encounter = sample_encounter
        
        service.adjust_initiative("Alice", 20)
        
        alice = service.current_encounter.get_combatant("Alice")
        assert alice.initiative == 20
        # Should be sorted by initiative, so Alice should be first
        assert service.current_encounter.combatants[0] == alice
    
    def test_adjust_initiative_combatant_not_found(self, service, sample_encounter):
        """Test adjusting initiative for non-existent combatant."""
        service.current_encounter = sample_encounter
        
        with pytest.raises(CombatantNotFoundError, match="not found"):
            service.adjust_initiative("NonExistent", 20)
    
    def test_adjust_initiative_no_encounter(self, service):
        """Test adjusting initiative when no encounter is loaded."""
        with pytest.raises(EncounterNotLoadedError, match="No encounter is currently loaded"):
            service.adjust_initiative("Alice", 20)
    
    def test_get_initiative_order(self, service, sample_encounter):
        """Test getting initiative order."""
        service.current_encounter = sample_encounter
        
        order = service.get_initiative_order()
        
        assert len(order) == 3
        # Should be sorted by initiative (highest first)
        assert order[0].name == "Alice"  # Initiative 18
        assert order[1].name == "Bob"    # Initiative 15
        assert order[2].name == "Goblin" # Initiative 12
    
    def test_get_initiative_order_no_encounter(self, service):
        """Test getting initiative order when no encounter is loaded."""
        order = service.get_initiative_order()
        
        assert order == []
    
    def test_reorder_combatants_with_same_initiative(self, service):
        """Test manually reordering combatants with same initiative."""
        service.create_encounter("Test")
        service.add_combatant("Alice", 25, 15)
        service.add_combatant("Bob", 30, 15)
        service.add_combatant("Charlie", 20, 15)
        
        service.reorder_combatants_with_same_initiative(15, ["Bob", "Charlie", "Alice"])
        
        order = service.get_initiative_order()
        assert order[0].name == "Bob"
        assert order[1].name == "Charlie"
        assert order[2].name == "Alice"
    
    def test_reorder_combatants_no_encounter(self, service):
        """Test reordering combatants when no encounter is loaded."""
        with pytest.raises(EncounterNotLoadedError, match="No encounter is currently loaded"):
            service.reorder_combatants_with_same_initiative(15, ["Alice", "Bob"])


class TestNoteManagement:
    """Test note management functionality."""
    
    def test_add_note_success(self, service, sample_encounter):
        """Test successful note addition."""
        service.current_encounter = sample_encounter
        
        service.add_note("Alice", "Blessed by cleric")
        
        alice = service.current_encounter.get_combatant("Alice")
        assert "Blessed by cleric" in alice.notes
    
    def test_add_note_combatant_not_found(self, service, sample_encounter):
        """Test adding note to non-existent combatant."""
        service.current_encounter = sample_encounter
        
        with pytest.raises(CombatantNotFoundError, match="not found"):
            service.add_note("NonExistent", "Some note")
    
    def test_add_note_no_encounter(self, service):
        """Test adding note when no encounter is loaded."""
        with pytest.raises(EncounterNotLoadedError, match="No encounter is currently loaded"):
            service.add_note("Alice", "Some note")
    
    def test_remove_note_success(self, service, sample_encounter):
        """Test successful note removal."""
        service.current_encounter = sample_encounter
        alice = service.current_encounter.get_combatant("Alice")
        alice.add_note("Test note")
        
        service.remove_note("Alice", 0)
        
        assert len(alice.notes) == 0
    
    def test_remove_note_invalid_index(self, service, sample_encounter):
        """Test removing note with invalid index."""
        service.current_encounter = sample_encounter
        
        with pytest.raises(NoteIndexError, match="has no notes"):
            service.remove_note("Alice", 0)  # No notes exist
    
    def test_edit_note_success(self, service, sample_encounter):
        """Test successful note editing."""
        service.current_encounter = sample_encounter
        alice = service.current_encounter.get_combatant("Alice")
        alice.add_note("Original note")
        
        service.edit_note("Alice", 0, "Edited note")
        
        assert alice.notes[0] == "Edited note"
    
    def test_edit_note_invalid_index(self, service, sample_encounter):
        """Test editing note with invalid index."""
        service.current_encounter = sample_encounter
        
        with pytest.raises(NoteIndexError, match="has no notes"):
            service.edit_note("Alice", 0, "New note")  # No notes exist


class TestTurnManagement:
    """Test turn management functionality."""
    
    def test_next_turn_success(self, service, sample_encounter):
        """Test advancing to next turn."""
        service.current_encounter = sample_encounter
        initial_turn = sample_encounter.current_turn
        
        current_combatant = service.next_turn()
        
        assert sample_encounter.current_turn == (initial_turn + 1) % len(sample_encounter.combatants)
        assert current_combatant == sample_encounter.get_current_combatant()
    
    def test_next_turn_no_encounter(self, service):
        """Test advancing turn when no encounter is loaded."""
        result = service.next_turn()
        
        assert result is None
    
    def test_get_current_combatant(self, service, sample_encounter):
        """Test getting current combatant."""
        service.current_encounter = sample_encounter
        
        current = service.get_current_combatant()
        
        assert current == sample_encounter.combatants[sample_encounter.current_turn]
    
    def test_get_current_combatant_no_encounter(self, service):
        """Test getting current combatant when no encounter is loaded."""
        current = service.get_current_combatant()
        
        assert current is None


class TestUtilityMethods:
    """Test utility methods."""
    
    def test_get_combatant_success(self, service, sample_encounter):
        """Test getting combatant by name."""
        service.current_encounter = sample_encounter
        
        alice = service.get_combatant("Alice")
        
        assert alice is not None
        assert alice.name == "Alice"
    
    def test_get_combatant_not_found(self, service, sample_encounter):
        """Test getting non-existent combatant."""
        service.current_encounter = sample_encounter
        
        result = service.get_combatant("NonExistent")
        
        assert result is None
    
    def test_get_combatant_no_encounter(self, service):
        """Test getting combatant when no encounter is loaded."""
        result = service.get_combatant("Alice")
        
        assert result is None
    
    def test_has_current_encounter(self, service, sample_encounter):
        """Test checking if encounter is loaded."""
        assert not service.has_current_encounter()
        
        service.current_encounter = sample_encounter
        assert service.has_current_encounter()
    
    def test_get_encounter_summary_with_encounter(self, service, sample_encounter):
        """Test getting encounter summary with loaded encounter."""
        service.current_encounter = sample_encounter
        
        summary = service.get_encounter_summary()
        
        assert summary["name"] == "Test Encounter"
        assert summary["combatant_count"] == 3
        assert summary["current_turn"] == "Alice"  # First in initiative order
        assert summary["round_number"] == 1
        assert summary["has_combatants"] is True
    
    def test_get_encounter_summary_no_encounter(self, service):
        """Test getting encounter summary with no loaded encounter."""
        summary = service.get_encounter_summary()
        
        assert summary["name"] is None
        assert summary["combatant_count"] == 0
        assert summary["current_turn"] is None
        assert summary["round_number"] == 0
        assert summary["has_combatants"] is False


class TestFileManagement:
    """Test file management functionality."""
    
    def test_get_available_encounters(self, service, mock_data_manager):
        """Test getting available encounter files."""
        mock_data_manager.get_available_encounters.return_value = ["encounter1", "encounter2"]
        
        encounters = service.get_available_encounters()
        
        assert encounters == ["encounter1", "encounter2"]
        mock_data_manager.get_available_encounters.assert_called_once()
    
    def test_encounter_exists(self, service, mock_data_manager):
        """Test checking if encounter file exists."""
        mock_data_manager.encounter_exists.return_value = True
        
        result = service.encounter_exists("test.json")
        
        assert result is True
        mock_data_manager.encounter_exists.assert_called_once_with("test.json")
    
    def test_delete_encounter(self, service, mock_data_manager):
        """Test deleting encounter file."""
        service.delete_encounter("test.json")
        
        mock_data_manager.delete_encounter.assert_called_once_with("test.json")
    
    def test_delete_encounter_error(self, service, mock_data_manager):
        """Test deleting encounter file with error."""
        mock_data_manager.delete_encounter.side_effect = FileFormatError("test.json", "delete", "File not found")
        
        with pytest.raises(FileFormatError, match="File not found"):
            service.delete_encounter("nonexistent.json")


class TestGetCurrentEncounter:
    """Test getting current encounter."""
    
    def test_get_current_encounter_loaded(self, service, sample_encounter):
        """Test getting current encounter when one is loaded."""
        service.current_encounter = sample_encounter
        
        result = service.get_current_encounter()
        
        assert result == sample_encounter
    
    def test_get_current_encounter_none(self, service):
        """Test getting current encounter when none is loaded."""
        result = service.get_current_encounter()
        
        assert result is None