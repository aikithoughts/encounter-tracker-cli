"""Tests for the data persistence layer."""

import json
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from dnd_encounter_tracker.core.models import Encounter, Combatant
from dnd_encounter_tracker.core.exceptions import FileFormatError, ValidationError
from dnd_encounter_tracker.data.persistence import DataManager


class TestDataManager:
    """Test cases for DataManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def data_manager(self, temp_dir):
        """Create a DataManager instance with temporary directory."""
        return DataManager(temp_dir)
    
    @pytest.fixture
    def sample_encounter(self):
        """Create a sample encounter for testing."""
        combatant1 = Combatant(
            name="Thorin",
            max_hp=45,
            current_hp=32,
            initiative=18,
            notes=["Blessed by cleric", "Has inspiration"],
            combatant_type="player"
        )
        combatant2 = Combatant(
            name="Goblin",
            max_hp=15,
            current_hp=8,
            initiative=12,
            notes=["Poisoned"],
            combatant_type="monster"
        )
        
        encounter = Encounter(
            name="Goblin Ambush",
            combatants=[combatant1, combatant2],
            current_turn=1,
            round_number=3
        )
        return encounter
    
    def test_init_creates_directory(self, temp_dir):
        """Test that DataManager creates the data directory."""
        data_dir = Path(temp_dir) / "test_encounters"
        assert not data_dir.exists()
        
        DataManager(str(data_dir))
        assert data_dir.exists()
        assert data_dir.is_dir()
    
    def test_save_to_file_success(self, data_manager, sample_encounter):
        """Test successful saving of encounter to file."""
        filename = "test_encounter"
        data_manager.save_to_file(sample_encounter, filename)
        
        # Check file was created
        filepath = data_manager.data_directory / "test_encounter.json"
        assert filepath.exists()
        
        # Verify file content
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert data["name"] == "Goblin Ambush"
        assert len(data["combatants"]) == 2
        assert data["current_turn"] == 1
        assert data["round_number"] == 3
        assert "metadata" in data
    
    def test_save_to_file_adds_json_extension(self, data_manager, sample_encounter):
        """Test that .json extension is added if missing."""
        data_manager.save_to_file(sample_encounter, "test_encounter")
        
        filepath = data_manager.data_directory / "test_encounter.json"
        assert filepath.exists()
    
    def test_save_to_file_creates_backup(self, data_manager, sample_encounter):
        """Test that backup is created when overwriting existing file."""
        filename = "test_encounter"
        
        # Save first time
        data_manager.save_to_file(sample_encounter, filename)
        
        # Modify encounter and save again
        sample_encounter.name = "Modified Encounter"
        data_manager.save_to_file(sample_encounter, filename)
        
        # Check backup was created
        backup_path = data_manager.data_directory / "test_encounter.json.backup"
        assert backup_path.exists()
        
        # Verify backup contains original data
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        assert backup_data["name"] == "Goblin Ambush"
    
    def test_save_to_file_empty_filename(self, data_manager, sample_encounter):
        """Test that empty filename raises ValidationError."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            data_manager.save_to_file(sample_encounter, "")
    
    def test_save_to_file_io_error(self, data_manager, sample_encounter):
        """Test handling of I/O errors during save."""
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with pytest.raises(FileFormatError, match="Failed to save file"):
                data_manager.save_to_file(sample_encounter, "test")
    
    def test_load_from_file_success(self, data_manager, sample_encounter):
        """Test successful loading of encounter from file."""
        filename = "test_encounter"
        data_manager.save_to_file(sample_encounter, filename)
        
        loaded_encounter = data_manager.load_from_file(filename)
        
        assert loaded_encounter.name == sample_encounter.name
        assert len(loaded_encounter.combatants) == len(sample_encounter.combatants)
        assert loaded_encounter.current_turn == sample_encounter.current_turn
        assert loaded_encounter.round_number == sample_encounter.round_number
        
        # Check combatant details
        loaded_thorin = loaded_encounter.get_combatant("Thorin")
        original_thorin = sample_encounter.get_combatant("Thorin")
        
        assert loaded_thorin.name == original_thorin.name
        assert loaded_thorin.max_hp == original_thorin.max_hp
        assert loaded_thorin.current_hp == original_thorin.current_hp
        assert loaded_thorin.initiative == original_thorin.initiative
        assert loaded_thorin.notes == original_thorin.notes
        assert loaded_thorin.combatant_type == original_thorin.combatant_type
    
    def test_load_from_file_adds_json_extension(self, data_manager, sample_encounter):
        """Test that .json extension is added if missing during load."""
        data_manager.save_to_file(sample_encounter, "test_encounter.json")
        
        loaded_encounter = data_manager.load_from_file("test_encounter")
        assert loaded_encounter.name == sample_encounter.name
    
    def test_load_from_file_not_found(self, data_manager):
        """Test loading non-existent file raises FileFormatError."""
        with pytest.raises(FileFormatError, match="not found"):
            data_manager.load_from_file("nonexistent")
    
    def test_load_from_file_empty_filename(self, data_manager):
        """Test that empty filename raises ValidationError."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            data_manager.load_from_file("")
    
    def test_load_from_file_invalid_json(self, data_manager):
        """Test loading file with invalid JSON raises FileFormatError."""
        filepath = data_manager.data_directory / "invalid.json"
        with open(filepath, 'w') as f:
            f.write("{ invalid json }")
        
        with pytest.raises(FileFormatError, match="Invalid JSON"):
            data_manager.load_from_file("invalid")
    
    def test_load_from_file_io_error(self, data_manager):
        """Test handling of I/O errors during load."""
        # Create file first
        filepath = data_manager.data_directory / "test.json"
        filepath.touch()
        
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with pytest.raises(FileFormatError, match="Failed to load file"):
                data_manager.load_from_file("test")
    
    def test_validate_file_format_valid(self, data_manager, sample_encounter):
        """Test validation of valid file format."""
        filename = "test_encounter"
        data_manager.save_to_file(sample_encounter, filename)
        
        assert data_manager.validate_file_format(filename) is True
    
    def test_validate_file_format_invalid(self, data_manager):
        """Test validation of invalid file format."""
        filepath = data_manager.data_directory / "invalid.json"
        with open(filepath, 'w') as f:
            json.dump({"invalid": "format"}, f)
        
        assert data_manager.validate_file_format("invalid") is False
    
    def test_get_available_encounters(self, data_manager, sample_encounter):
        """Test getting list of available encounters."""
        # Initially empty
        assert data_manager.get_available_encounters() == []
        
        # Save some encounters
        data_manager.save_to_file(sample_encounter, "encounter1")
        sample_encounter.name = "Second Encounter"
        data_manager.save_to_file(sample_encounter, "encounter2")
        
        # Create backup file (should be filtered out)
        backup_path = data_manager.data_directory / "encounter1.json.backup"
        backup_path.touch()
        
        encounters = data_manager.get_available_encounters()
        assert sorted(encounters) == ["encounter1", "encounter2"]
    
    def test_delete_encounter_success(self, data_manager, sample_encounter):
        """Test successful deletion of encounter file."""
        filename = "test_encounter"
        data_manager.save_to_file(sample_encounter, filename)
        
        assert data_manager.encounter_exists(filename)
        data_manager.delete_encounter(filename)
        assert not data_manager.encounter_exists(filename)
    
    def test_delete_encounter_not_found(self, data_manager):
        """Test deletion of non-existent file raises FileFormatError."""
        with pytest.raises(FileFormatError, match="not found"):
            data_manager.delete_encounter("nonexistent")
    
    def test_delete_encounter_empty_filename(self, data_manager):
        """Test that empty filename raises ValidationError."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            data_manager.delete_encounter("")
    
    def test_encounter_exists(self, data_manager, sample_encounter):
        """Test checking if encounter file exists."""
        filename = "test_encounter"
        
        assert not data_manager.encounter_exists(filename)
        data_manager.save_to_file(sample_encounter, filename)
        assert data_manager.encounter_exists(filename)
    
    def test_encounter_exists_empty_filename(self, data_manager):
        """Test that empty filename returns False."""
        assert not data_manager.encounter_exists("")
    
    def test_encounter_to_dict_conversion(self, data_manager, sample_encounter):
        """Test conversion of encounter to dictionary."""
        encounter_dict = data_manager._encounter_to_dict(sample_encounter)
        
        assert encounter_dict["name"] == "Goblin Ambush"
        assert len(encounter_dict["combatants"]) == 2
        assert encounter_dict["current_turn"] == 1
        assert encounter_dict["round_number"] == 3
        assert "metadata" in encounter_dict
        
        # Check combatant data
        thorin_data = next(c for c in encounter_dict["combatants"] if c["name"] == "Thorin")
        assert thorin_data["max_hp"] == 45
        assert thorin_data["current_hp"] == 32
        assert thorin_data["initiative"] == 18
        assert thorin_data["notes"] == ["Blessed by cleric", "Has inspiration"]
        assert thorin_data["combatant_type"] == "player"
    
    def test_dict_to_encounter_conversion(self, data_manager):
        """Test conversion of dictionary to encounter."""
        encounter_dict = {
            "name": "Test Encounter",
            "combatants": [
                {
                    "name": "Fighter",
                    "max_hp": 50,
                    "current_hp": 35,
                    "initiative": 15,
                    "notes": ["Raging"],
                    "combatant_type": "player",
                    "tie_breaker": 0.5
                }
            ],
            "current_turn": 0,
            "round_number": 2
        }
        
        encounter = data_manager._dict_to_encounter(encounter_dict)
        
        assert encounter.name == "Test Encounter"
        assert len(encounter.combatants) == 1
        assert encounter.current_turn == 0
        assert encounter.round_number == 2
        
        fighter = encounter.combatants[0]
        assert fighter.name == "Fighter"
        assert fighter.max_hp == 50
        assert fighter.current_hp == 35
        assert fighter.initiative == 15
        assert fighter.notes == ["Raging"]
        assert fighter.combatant_type == "player"
        assert fighter._tie_breaker == 0.5
    
    def test_dict_to_encounter_missing_fields(self, data_manager):
        """Test conversion with missing required fields raises ValidationError."""
        incomplete_dict = {
            "name": "Test Encounter"
            # Missing combatants - this should default to empty list
        }
        
        # This should actually work since combatants defaults to empty list
        encounter = data_manager._dict_to_encounter(incomplete_dict)
        assert encounter.name == "Test Encounter"
        assert len(encounter.combatants) == 0
        
        # Test with missing name instead
        incomplete_dict_no_name = {
            "combatants": []
        }
        
        with pytest.raises(ValidationError, match="Missing required field"):
            data_manager._dict_to_encounter(incomplete_dict_no_name)
    
    def test_dict_to_encounter_invalid_types(self, data_manager):
        """Test conversion with invalid data types raises ValidationError."""
        invalid_dict = {
            "name": "Test Encounter",
            "combatants": [
                {
                    "name": "Fighter",
                    "max_hp": "not_a_number",  # Invalid type
                    "current_hp": 35,
                    "initiative": 15
                }
            ]
        }
        
        with pytest.raises(ValidationError, match="Invalid data type"):
            data_manager._dict_to_encounter(invalid_dict)


class TestFileFormatValidation:
    """Test cases for file format validation."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def data_manager(self, temp_dir):
        """Create a DataManager instance with temporary directory."""
        return DataManager(temp_dir)
    
    def test_validate_file_format_not_dict(self, data_manager):
        """Test validation fails when file doesn't contain JSON object."""
        filepath = data_manager.data_directory / "invalid.json"
        with open(filepath, 'w') as f:
            json.dump(["not", "an", "object"], f)
        
        with pytest.raises(FileFormatError, match="does not contain a valid JSON object"):
            data_manager._validate_file_format(["not", "an", "object"], "invalid.json")
    
    def test_validate_file_format_missing_required_fields(self, data_manager):
        """Test validation fails when required fields are missing."""
        invalid_data = {"name": "Test"}  # Missing combatants
        
        with pytest.raises(FileFormatError, match="Missing required field: combatants"):
            data_manager._validate_file_format(invalid_data, "test.json")
    
    def test_validate_file_format_invalid_encounter_name(self, data_manager):
        """Test validation fails with invalid encounter name."""
        invalid_data = {
            "name": "",  # Empty name
            "combatants": []
        }
        
        with pytest.raises(FileFormatError, match="Invalid encounter name"):
            data_manager._validate_file_format(invalid_data, "test.json")
    
    def test_validate_file_format_combatants_not_list(self, data_manager):
        """Test validation fails when combatants is not a list."""
        invalid_data = {
            "name": "Test",
            "combatants": "not_a_list"
        }
        
        with pytest.raises(FileFormatError, match="Combatants field must be a list"):
            data_manager._validate_file_format(invalid_data, "test.json")
    
    def test_validate_file_format_invalid_combatant_structure(self, data_manager):
        """Test validation fails with invalid combatant structure."""
        invalid_data = {
            "name": "Test",
            "combatants": [
                "not_an_object"  # Should be dict
            ]
        }
        
        with pytest.raises(FileFormatError, match="Combatant 0 is not a valid object"):
            data_manager._validate_file_format(invalid_data, "test.json")
    
    def test_validate_file_format_missing_combatant_fields(self, data_manager):
        """Test validation fails when combatant fields are missing."""
        invalid_data = {
            "name": "Test",
            "combatants": [
                {
                    "name": "Fighter"
                    # Missing required fields
                }
            ]
        }
        
        with pytest.raises(FileFormatError, match="Combatant 0 missing field: max_hp"):
            data_manager._validate_file_format(invalid_data, "test.json")
    
    def test_validate_file_format_invalid_combatant_field_types(self, data_manager):
        """Test validation fails with invalid combatant field types."""
        invalid_data = {
            "name": "Test",
            "combatants": [
                {
                    "name": "Fighter",
                    "max_hp": "not_a_number",
                    "current_hp": 35,
                    "initiative": 15
                }
            ]
        }
        
        with pytest.raises(FileFormatError, match="field 'max_hp' must be an integer"):
            data_manager._validate_file_format(invalid_data, "test.json")
    
    def test_validate_file_format_invalid_optional_fields(self, data_manager):
        """Test validation fails with invalid optional field types."""
        invalid_data = {
            "name": "Test",
            "combatants": [
                {
                    "name": "Fighter",
                    "max_hp": 50,
                    "current_hp": 35,
                    "initiative": 15,
                    "notes": "not_a_list"  # Should be list
                }
            ]
        }
        
        with pytest.raises(FileFormatError, match="notes must be a list"):
            data_manager._validate_file_format(invalid_data, "test.json")


class TestEdgeCases:
    """Test edge cases and error scenarios."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def data_manager(self, temp_dir):
        """Create a DataManager instance with temporary directory."""
        return DataManager(temp_dir)
    
    def test_save_load_empty_encounter(self, data_manager):
        """Test saving and loading encounter with no combatants."""
        encounter = Encounter(name="Empty Encounter")
        
        data_manager.save_to_file(encounter, "empty")
        loaded = data_manager.load_from_file("empty")
        
        assert loaded.name == "Empty Encounter"
        assert len(loaded.combatants) == 0
        assert loaded.current_turn == 0
        assert loaded.round_number == 1
    
    def test_save_load_encounter_with_tie_breakers(self, data_manager):
        """Test that tie breaker values are preserved during save/load."""
        combatant1 = Combatant("Fighter1", 50, 50, 15)
        combatant2 = Combatant("Fighter2", 40, 40, 15)
        
        # Set tie breakers
        combatant1._tie_breaker = 1.0
        combatant2._tie_breaker = 2.0
        
        encounter = Encounter("Tie Test", [combatant1, combatant2])
        
        data_manager.save_to_file(encounter, "tie_test")
        loaded = data_manager.load_from_file("tie_test")
        
        assert loaded.combatants[0]._tie_breaker == 1.0
        assert loaded.combatants[1]._tie_breaker == 2.0
    
    def test_atomic_save_operation(self, data_manager):
        """Test that save operation is atomic (uses temporary file)."""
        encounter = Encounter(name="Test Encounter")
        
        # Mock file operations to simulate failure during write
        original_open = open
        
        def mock_open_func(filepath, *args, **kwargs):
            if str(filepath).endswith('.json.tmp'):
                raise OSError("Simulated write failure")
            return original_open(filepath, *args, **kwargs)
        
        with patch("builtins.open", side_effect=mock_open_func):
            with pytest.raises(FileFormatError):
                data_manager.save_to_file(encounter, "test")
        
        # Verify original file wasn't corrupted (doesn't exist in this case)
        assert not data_manager.encounter_exists("test")
    
    def test_get_available_encounters_io_error(self, data_manager):
        """Test that I/O errors in get_available_encounters return empty list."""
        # Patch the pathlib.Path.glob method instead
        with patch('pathlib.Path.glob', side_effect=OSError("Permission denied")):
            encounters = data_manager.get_available_encounters()
            assert encounters == []