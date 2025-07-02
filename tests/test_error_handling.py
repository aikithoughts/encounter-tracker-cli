"""Tests for comprehensive error handling and user feedback."""

import pytest
import tempfile
import os
from pathlib import Path

from dnd_encounter_tracker.core.exceptions import (
    EncounterTrackerError,
    CombatantNotFoundError,
    InvalidHPValueError,
    FileFormatError,
    EncounterNotLoadedError,
    ValidationError,
    DuplicateCombatantError,
    NoteIndexError,
    InitiativeError,
    CommandError
)
from dnd_encounter_tracker.core.models import Combatant, Encounter
from dnd_encounter_tracker.core.encounter_service import EncounterService
from dnd_encounter_tracker.data.persistence import DataManager
from dnd_encounter_tracker.cli.commands import CommandHandler
from dnd_encounter_tracker.cli.display import DisplayManager
import argparse


class TestExceptionHierarchy:
    """Test the custom exception hierarchy and user-friendly messages."""
    
    def test_base_exception_user_message(self):
        """Test that base exception provides formatted user message."""
        error = EncounterTrackerError(
            message="Test error",
            details="Additional details",
            suggestions=["Try this", "Or this"]
        )
        
        message = error.get_user_message()
        assert "Error: Test error" in message
        assert "Details: Additional details" in message
        assert "Suggestions:" in message
        assert "Try this" in message
        assert "Or this" in message
    
    def test_combatant_not_found_error_with_suggestions(self):
        """Test CombatantNotFoundError provides helpful suggestions."""
        available_combatants = ["Thorin", "Legolas", "Gimli"]
        error = CombatantNotFoundError("Thrain", available_combatants)
        
        message = error.get_user_message()
        assert "Combatant 'Thrain' not found" in message
        assert "Did you mean: Thorin" in message  # Similar name suggestion
        assert "Check the spelling" in message
    
    def test_combatant_not_found_error_empty_encounter(self):
        """Test CombatantNotFoundError with no combatants."""
        error = CombatantNotFoundError("Thorin", [])
        
        message = error.get_user_message()
        assert "Add combatants to the encounter first" in message
    
    def test_invalid_hp_value_error_with_context(self):
        """Test InvalidHPValueError provides context and suggestions."""
        error = InvalidHPValueError(
            hp_value="abc",
            reason="Invalid format",
            current_hp=25,
            max_hp=50
        )
        
        message = error.get_user_message()
        assert "Invalid HP value 'abc'" in message
        assert "Current HP: 25/50" in message
        assert "Use absolute values" in message
        assert "Use additions" in message
        assert "Use subtractions" in message
    
    def test_file_format_error_with_operation_context(self):
        """Test FileFormatError provides operation-specific suggestions."""
        error = FileFormatError(
            filename="test.json",
            operation="load",
            reason="File not found"
        )
        
        message = error.get_user_message()
        assert "Failed to load file 'test.json'" in message
        assert "Check that the file exists" in message
        assert "Use 'list' to see available" in message
    
    def test_encounter_not_loaded_error_with_operation(self):
        """Test EncounterNotLoadedError provides context-specific suggestions."""
        error = EncounterNotLoadedError("add combatant")
        
        message = error.get_user_message()
        assert "No encounter is currently loaded to add combatant" in message
        assert "Create a new encounter with 'new <name>'" in message
        assert "Load an existing encounter with 'load <filename>'" in message
    
    def test_validation_error_with_examples(self):
        """Test ValidationError provides valid examples."""
        error = ValidationError(
            field="hit points",
            value=-5,
            reason="Must be positive",
            valid_examples=["1", "25", "100"]
        )
        
        message = error.get_user_message()
        assert "Invalid hit points" in message
        assert "Provided value: -5" in message
        assert "Valid examples: 1, 25, 100" in message
    
    def test_duplicate_combatant_error(self):
        """Test DuplicateCombatantError provides helpful suggestions."""
        error = DuplicateCombatantError("Thorin")
        
        message = error.get_user_message()
        assert "A combatant named 'Thorin' already exists" in message
        assert "Use a different name" in message
        assert "Add a number or descriptor" in message
    
    def test_note_index_error_no_notes(self):
        """Test NoteIndexError when combatant has no notes."""
        error = NoteIndexError(1, 0, "Thorin")
        
        message = error.get_user_message()
        assert "'Thorin' has no notes" in message
        assert "Add a note first" in message
    
    def test_note_index_error_invalid_index(self):
        """Test NoteIndexError with invalid index."""
        error = NoteIndexError(5, 3, "Thorin")
        
        message = error.get_user_message()
        assert "Invalid note index 5 for 'Thorin'" in message
        assert "Valid indices: 1 to 3" in message
        assert "Use 'note list Thorin'" in message
    
    def test_initiative_error_with_context(self):
        """Test InitiativeError provides context."""
        error = InitiativeError("Invalid initiative value", current_initiative=15)
        
        message = error.get_user_message()
        assert "Invalid initiative value" in message
        assert "Current initiative: 15" in message
        assert "Initiative values should be integers" in message
    
    def test_command_error_with_usage(self):
        """Test CommandError provides usage examples."""
        error = CommandError(
            command="note",
            reason="Missing action",
            usage_example="note add <name> \"<text>\""
        )
        
        message = error.get_user_message()
        assert "Command 'note' failed: Missing action" in message
        assert "Usage: note add <name> \"<text>\"" in message
        assert "Use --help with any command" in message


class TestServiceLayerErrorHandling:
    """Test error handling in the service layer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_manager = DataManager(self.temp_dir)
        self.service = EncounterService(self.data_manager)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_encounter_empty_name(self):
        """Test creating encounter with empty name."""
        with pytest.raises(ValidationError) as exc_info:
            self.service.create_encounter("")
        
        error = exc_info.value
        assert error.field == "encounter name"
        assert "cannot be empty" in error.reason
        assert "Goblin Ambush" in error.valid_examples
    
    def test_add_combatant_no_encounter(self):
        """Test adding combatant when no encounter is loaded."""
        with pytest.raises(EncounterNotLoadedError) as exc_info:
            self.service.add_combatant("Thorin", 45, 18)
        
        error = exc_info.value
        assert error.operation == "add combatant"
    
    def test_add_combatant_invalid_hp(self):
        """Test adding combatant with invalid HP."""
        self.service.create_encounter("Test")
        
        with pytest.raises(ValidationError) as exc_info:
            self.service.add_combatant("Thorin", -5, 18)
        
        error = exc_info.value
        assert error.field == "hit points"
        assert error.value == -5
        assert "must be positive" in error.reason
    
    def test_add_combatant_duplicate_name(self):
        """Test adding combatant with duplicate name."""
        self.service.create_encounter("Test")
        self.service.add_combatant("Thorin", 45, 18)
        
        with pytest.raises(DuplicateCombatantError) as exc_info:
            self.service.add_combatant("Thorin", 50, 20)
        
        error = exc_info.value
        assert error.combatant_name == "Thorin"
    
    def test_update_hp_combatant_not_found(self):
        """Test updating HP for non-existent combatant."""
        self.service.create_encounter("Test")
        self.service.add_combatant("Thorin", 45, 18)
        
        with pytest.raises(CombatantNotFoundError) as exc_info:
            self.service.update_hp("Gandalf", "-10")
        
        error = exc_info.value
        assert error.combatant_name == "Gandalf"
        assert "Thorin" in error.available_combatants
    
    def test_update_hp_invalid_format(self):
        """Test updating HP with invalid format."""
        self.service.create_encounter("Test")
        combatant = self.service.add_combatant("Thorin", 45, 18)
        
        with pytest.raises(InvalidHPValueError) as exc_info:
            self.service.update_hp("Thorin", "abc")
        
        error = exc_info.value
        assert error.hp_value == "abc"
        assert error.current_hp == 45
        assert error.max_hp == 45
    
    def test_add_note_empty_text(self):
        """Test adding empty note."""
        self.service.create_encounter("Test")
        self.service.add_combatant("Thorin", 45, 18)
        
        with pytest.raises(ValidationError) as exc_info:
            self.service.add_note("Thorin", "")
        
        error = exc_info.value
        assert error.field == "note text"
        assert "cannot be empty" in error.reason
    
    def test_remove_note_invalid_index(self):
        """Test removing note with invalid index."""
        self.service.create_encounter("Test")
        self.service.add_combatant("Thorin", 45, 18)
        self.service.add_note("Thorin", "Test note")
        
        with pytest.raises(NoteIndexError) as exc_info:
            self.service.remove_note("Thorin", 5)  # 0-based, so this is index 5
        
        error = exc_info.value
        assert error.index == 6  # Converted back to 1-based for user
        assert error.note_count == 1
        assert error.combatant_name == "Thorin"


class TestDataLayerErrorHandling:
    """Test error handling in the data persistence layer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_manager = DataManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        with pytest.raises(FileFormatError) as exc_info:
            self.data_manager.load_from_file("nonexistent")
        
        error = exc_info.value
        assert error.filename == "nonexistent.json"
        assert error.operation == "load"
        assert "File not found" in error.reason
    
    def test_load_invalid_json(self):
        """Test loading a file with invalid JSON."""
        filepath = Path(self.temp_dir) / "invalid.json"
        with open(filepath, 'w') as f:
            f.write("{ invalid json }")
        
        with pytest.raises(FileFormatError) as exc_info:
            self.data_manager.load_from_file("invalid")
        
        error = exc_info.value
        assert error.filename == "invalid.json"
        assert error.operation == "load"
        assert "Invalid JSON format" in error.reason
    
    def test_load_missing_required_fields(self):
        """Test loading a file missing required fields."""
        filepath = Path(self.temp_dir) / "incomplete.json"
        with open(filepath, 'w') as f:
            f.write('{"name": "Test"}')  # Missing combatants field
        
        with pytest.raises(FileFormatError) as exc_info:
            self.data_manager.load_from_file("incomplete")
        
        error = exc_info.value
        assert "Missing required field: combatants" in error.reason
    
    def test_save_to_readonly_directory(self):
        """Test saving to a read-only directory."""
        # Create a read-only directory
        readonly_dir = Path(self.temp_dir) / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only
        
        try:
            readonly_data_manager = DataManager(str(readonly_dir))
            encounter = Encounter("Test")
            
            with pytest.raises(FileFormatError) as exc_info:
                readonly_data_manager.save_to_file(encounter, "test")
            
            error = exc_info.value
            assert error.operation == "save"
            assert "File system error" in error.reason
        finally:
            # Restore permissions for cleanup
            readonly_dir.chmod(0o755)


class TestCLIErrorHandling:
    """Test error handling in the CLI layer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        data_manager = DataManager(self.temp_dir)
        encounter_service = EncounterService(data_manager)
        display_manager = DisplayManager()
        self.command_handler = CommandHandler(encounter_service, display_manager)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_unknown_command_error(self):
        """Test handling of unknown commands."""
        args = argparse.Namespace(command="unknown_command")
        
        exit_code = self.command_handler.execute_command(args)
        assert exit_code == 1
    
    def test_keyboard_interrupt_handling(self):
        """Test graceful handling of keyboard interrupts."""
        # Mock a method to raise KeyboardInterrupt
        original_method = self.command_handler._handle_new
        
        def mock_method(args):
            raise KeyboardInterrupt()
        
        self.command_handler._handle_new = mock_method
        
        try:
            args = argparse.Namespace(command="new", name="Test")
            exit_code = self.command_handler.execute_command(args)
            assert exit_code == 1
        finally:
            self.command_handler._handle_new = original_method
    
    def test_unexpected_error_handling(self):
        """Test handling of unexpected errors."""
        # Mock a method to raise an unexpected error
        original_method = self.command_handler._handle_new
        
        def mock_method(args):
            raise RuntimeError("Unexpected error")
        
        self.command_handler._handle_new = mock_method
        
        try:
            args = argparse.Namespace(command="new", name="Test")
            exit_code = self.command_handler.execute_command(args)
            assert exit_code == 1
        finally:
            self.command_handler._handle_new = original_method


class TestErrorRecoveryMechanisms:
    """Test error recovery and user guidance mechanisms."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_manager = DataManager(self.temp_dir)
        self.service = EncounterService(self.data_manager)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_similar_name_suggestions(self):
        """Test that similar name suggestions work correctly."""
        error = CombatantNotFoundError("Thrain", ["Thorin", "Legolas", "Gimli"])
        
        # Test Levenshtein distance calculation
        assert "Thorin" in error.get_user_message()  # Similar to "Thrain"
    
    def test_partial_name_matching(self):
        """Test partial name matching in suggestions."""
        error = CombatantNotFoundError("Gob", ["Goblin Scout", "Goblin Warrior", "Orc"])
        
        message = error.get_user_message()
        assert "Goblin Scout" in message or "Goblin Warrior" in message
    
    def test_case_insensitive_suggestions(self):
        """Test case-insensitive name suggestions."""
        error = CombatantNotFoundError("thorin", ["Thorin", "Legolas"])
        
        message = error.get_user_message()
        assert "Thorin" in message
    
    def test_file_backup_on_save_error(self):
        """Test that file backups are created when save operations might fail."""
        # Create an encounter and save it
        encounter = Encounter("Test")
        encounter.add_combatant(Combatant("Thorin", 45, 45, 18))
        
        self.data_manager.save_to_file(encounter, "test")
        
        # Verify file exists
        assert self.data_manager.encounter_exists("test")
        
        # Save again to trigger backup creation
        encounter.add_combatant(Combatant("Legolas", 40, 40, 20))
        self.data_manager.save_to_file(encounter, "test")
        
        # Verify backup was created
        backup_path = Path(self.data_manager.data_directory) / "test.json.backup"
        assert backup_path.exists()
    
    def test_atomic_file_operations(self):
        """Test that file operations are atomic (temp file then rename)."""
        encounter = Encounter("Test")
        
        # Mock a failure during the write operation
        original_open = open
        
        def mock_open(*args, **kwargs):
            if args[0].endswith('.tmp'):
                raise IOError("Simulated write failure")
            return original_open(*args, **kwargs)
        
        import builtins
        builtins.open = mock_open
        
        try:
            with pytest.raises(FileFormatError):
                self.data_manager.save_to_file(encounter, "test")
            
            # Verify that the original file wasn't corrupted
            assert not self.data_manager.encounter_exists("test")
        finally:
            builtins.open = original_open


if __name__ == "__main__":
    pytest.main([__file__])