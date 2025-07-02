"""Tests for CLI command parsing and execution."""

import pytest
from unittest.mock import Mock, patch
import argparse
import io
import sys

from dnd_encounter_tracker.cli.main import create_parser, main
from dnd_encounter_tracker.cli.commands import CommandHandler
from dnd_encounter_tracker.cli.display import DisplayManager
from dnd_encounter_tracker.core.encounter_service import EncounterService
from dnd_encounter_tracker.core.models import Encounter, Combatant
from dnd_encounter_tracker.core.exceptions import (
    EncounterNotLoadedError,
    CombatantNotFoundError,
    ValidationError,
    FileFormatError
)


class TestArgumentParsing:
    """Test argument parsing for all CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = create_parser()
    
    def test_parser_creation(self):
        """Test that parser is created successfully."""
        assert self.parser is not None
        assert isinstance(self.parser, argparse.ArgumentParser)
        assert self.parser.prog == 'dnd-encounter-tracker'
    
    def test_no_command_shows_help(self):
        """Test that no command shows help."""
        args = self.parser.parse_args([])
        assert args.command is None
    
    def test_version_argument(self):
        """Test --version argument."""
        with pytest.raises(SystemExit):
            self.parser.parse_args(['--version'])
    
    def test_new_command_parsing(self):
        """Test 'new' command argument parsing."""
        args = self.parser.parse_args(['new', 'Test Encounter'])
        assert args.command == 'new'
        assert args.name == 'Test Encounter'
    
    def test_load_command_parsing(self):
        """Test 'load' command argument parsing."""
        args = self.parser.parse_args(['load', 'test_encounter'])
        assert args.command == 'load'
        assert args.filename == 'test_encounter'
    
    def test_save_command_parsing(self):
        """Test 'save' command argument parsing."""
        args = self.parser.parse_args(['save', 'my_encounter'])
        assert args.command == 'save'
        assert args.filename == 'my_encounter'
    
    def test_list_command_parsing(self):
        """Test 'list' command argument parsing."""
        args = self.parser.parse_args(['list'])
        assert args.command == 'list'
    
    def test_add_command_parsing(self):
        """Test 'add' command argument parsing."""
        # Test with all arguments
        args = self.parser.parse_args(['add', 'Thorin', '45', '18', 'player'])
        assert args.command == 'add'
        assert args.name == 'Thorin'
        assert args.hp == 45
        assert args.initiative == 18
        assert args.type == 'player'
        
        # Test with default type
        args = self.parser.parse_args(['add', 'Goblin', '7', '12'])
        assert args.command == 'add'
        assert args.name == 'Goblin'
        assert args.hp == 7
        assert args.initiative == 12
        assert args.type == 'unknown'
    
    def test_add_command_invalid_type(self):
        """Test 'add' command with invalid combatant type."""
        with pytest.raises(SystemExit):
            self.parser.parse_args(['add', 'Test', '10', '15', 'invalid_type'])
    
    def test_remove_command_parsing(self):
        """Test 'remove' command argument parsing."""
        args = self.parser.parse_args(['remove', 'Thorin'])
        assert args.command == 'remove'
        assert args.name == 'Thorin'
    
    def test_hp_command_parsing(self):
        """Test 'hp' command argument parsing."""
        # Test absolute value
        args = self.parser.parse_args(['hp', 'Thorin', '25'])
        assert args.command == 'hp'
        assert args.name == 'Thorin'
        assert args.value == '25'
        
        # Test addition
        args = self.parser.parse_args(['hp', 'Thorin', '+8'])
        assert args.value == '+8'
        
        # Test subtraction
        args = self.parser.parse_args(['hp', 'Thorin', '-12'])
        assert args.value == '-12'
    
    def test_init_command_parsing(self):
        """Test 'init' command argument parsing."""
        args = self.parser.parse_args(['init', 'Thorin', '20'])
        assert args.command == 'init'
        assert args.name == 'Thorin'
        assert args.value == 20
    
    def test_show_command_parsing(self):
        """Test 'show' command argument parsing."""
        # Test basic show
        args = self.parser.parse_args(['show'])
        assert args.command == 'show'
        assert not args.details
        
        # Test with details flag
        args = self.parser.parse_args(['show', '--details'])
        assert args.command == 'show'
        assert args.details
    
    def test_combatant_command_parsing(self):
        """Test 'combatant' command argument parsing."""
        args = self.parser.parse_args(['combatant', 'Thorin'])
        assert args.command == 'combatant'
        assert args.name == 'Thorin'
    
    def test_next_command_parsing(self):
        """Test 'next' command argument parsing."""
        args = self.parser.parse_args(['next'])
        assert args.command == 'next'
    
    def test_note_add_parsing(self):
        """Test 'note add' command argument parsing."""
        args = self.parser.parse_args(['note', 'add', 'Thorin', 'Blessed by cleric'])
        assert args.command == 'note'
        assert args.note_action == 'add'
        assert args.name == 'Thorin'
        assert args.note == 'Blessed by cleric'
    
    def test_note_list_parsing(self):
        """Test 'note list' command argument parsing."""
        args = self.parser.parse_args(['note', 'list', 'Thorin'])
        assert args.command == 'note'
        assert args.note_action == 'list'
        assert args.name == 'Thorin'
    
    def test_note_edit_parsing(self):
        """Test 'note edit' command argument parsing."""
        args = self.parser.parse_args(['note', 'edit', 'Thorin', '1', 'Updated note'])
        assert args.command == 'note'
        assert args.note_action == 'edit'
        assert args.name == 'Thorin'
        assert args.index == 1
        assert args.note == 'Updated note'
    
    def test_note_remove_parsing(self):
        """Test 'note remove' command argument parsing."""
        args = self.parser.parse_args(['note', 'remove', 'Thorin', '2'])
        assert args.command == 'note'
        assert args.note_action == 'remove'
        assert args.name == 'Thorin'
        assert args.index == 2
    
    def test_note_show_parsing(self):
        """Test 'note show' command argument parsing."""
        args = self.parser.parse_args(['note', 'show'])
        assert args.command == 'note'
        assert args.note_action == 'show'


class TestCommandHandler:
    """Test command handler execution."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_encounter_service = Mock(spec=EncounterService)
        self.mock_display_manager = Mock(spec=DisplayManager)
        self.handler = CommandHandler(self.mock_encounter_service, self.mock_display_manager)
    
    def test_handle_new_command(self):
        """Test handling 'new' command."""
        # Setup
        mock_encounter = Mock(spec=Encounter)
        mock_encounter.name = "Test Encounter"
        self.mock_encounter_service.create_encounter.return_value = mock_encounter
        
        args = argparse.Namespace(command='new', name='Test Encounter')
        
        # Execute
        result = self.handler.execute_command(args)
        
        # Verify
        assert result == 0
        self.mock_encounter_service.create_encounter.assert_called_once_with('Test Encounter')
    
    def test_handle_load_command(self):
        """Test handling 'load' command."""
        # Setup
        mock_encounter = Mock(spec=Encounter)
        mock_encounter.name = "Loaded Encounter"
        mock_encounter.has_combatants.return_value = True
        self.mock_encounter_service.load_encounter.return_value = mock_encounter
        self.mock_display_manager.show_encounter_summary.return_value = "Encounter summary"
        
        args = argparse.Namespace(command='load', filename='test_encounter')
        
        # Execute
        result = self.handler.execute_command(args)
        
        # Verify
        assert result == 0
        self.mock_encounter_service.load_encounter.assert_called_once_with('test_encounter')
        self.mock_display_manager.show_encounter_summary.assert_called_once_with(mock_encounter)
    
    def test_handle_save_command(self):
        """Test handling 'save' command."""
        # Setup
        mock_encounter = Mock(spec=Encounter)
        mock_encounter.name = "Test Encounter"
        self.mock_encounter_service.get_current_encounter.return_value = mock_encounter
        
        args = argparse.Namespace(command='save', filename='my_encounter')
        
        # Execute
        result = self.handler.execute_command(args)
        
        # Verify
        assert result == 0
        self.mock_encounter_service.save_encounter.assert_called_once_with('my_encounter')
    
    def test_handle_list_command(self):
        """Test handling 'list' command."""
        # Setup
        self.mock_encounter_service.get_available_encounters.return_value = ['encounter1', 'encounter2']
        
        args = argparse.Namespace(command='list')
        
        # Execute
        result = self.handler.execute_command(args)
        
        # Verify
        assert result == 0
        self.mock_encounter_service.get_available_encounters.assert_called_once()
    
    def test_handle_add_command(self):
        """Test handling 'add' command."""
        # Setup
        mock_combatant = Mock(spec=Combatant)
        mock_combatant.name = "Thorin"
        mock_combatant.max_hp = 45
        mock_combatant.initiative = 18
        mock_combatant.combatant_type = "player"
        
        mock_encounter = Mock(spec=Encounter)
        mock_encounter.combatants = [mock_combatant]
        mock_encounter.current_turn = 0
        
        self.mock_encounter_service.add_combatant.return_value = mock_combatant
        self.mock_encounter_service.get_current_encounter.return_value = mock_encounter
        self.mock_display_manager.show_initiative_order.return_value = "Initiative order"
        
        args = argparse.Namespace(command='add', name='Thorin', hp=45, initiative=18, type='player')
        
        # Execute
        result = self.handler.execute_command(args)
        
        # Verify
        assert result == 0
        self.mock_encounter_service.add_combatant.assert_called_once_with(
            name='Thorin', max_hp=45, initiative=18, combatant_type='player'
        )
    
    def test_handle_hp_command(self):
        """Test handling 'hp' command."""
        # Setup
        mock_combatant = Mock(spec=Combatant)
        mock_combatant.name = "Thorin"
        mock_combatant.current_hp = 25
        mock_combatant.max_hp = 45
        
        self.mock_encounter_service.get_combatant.return_value = mock_combatant
        
        args = argparse.Namespace(command='hp', name='Thorin', value='-8')
        
        # Execute
        result = self.handler.execute_command(args)
        
        # Verify
        assert result == 0
        self.mock_encounter_service.update_hp.assert_called_once_with('Thorin', '-8')
    
    def test_handle_note_add_command(self):
        """Test handling 'note add' command."""
        args = argparse.Namespace(
            command='note', 
            note_action='add', 
            name='Thorin', 
            note='Blessed by cleric'
        )
        
        # Execute
        result = self.handler.execute_command(args)
        
        # Verify
        assert result == 0
        self.mock_encounter_service.add_note.assert_called_once_with('Thorin', 'Blessed by cleric')
    
    def test_error_handling_encounter_not_loaded(self):
        """Test error handling for EncounterNotLoadedError."""
        # Setup
        self.mock_encounter_service.add_combatant.side_effect = EncounterNotLoadedError("No encounter loaded")
        
        args = argparse.Namespace(command='add', name='Thorin', hp=45, initiative=18, type='player')
        
        # Execute
        result = self.handler.execute_command(args)
        
        # Verify
        assert result == 1
    
    def test_error_handling_combatant_not_found(self):
        """Test error handling for CombatantNotFoundError."""
        # Setup
        self.mock_encounter_service.get_combatant.side_effect = CombatantNotFoundError("Combatant not found")
        self.mock_encounter_service.has_current_encounter.return_value = True
        
        mock_encounter = Mock(spec=Encounter)
        mock_encounter.has_combatants.return_value = True
        mock_encounter.combatants = [Mock(name="Goblin")]
        self.mock_encounter_service.get_current_encounter.return_value = mock_encounter
        
        args = argparse.Namespace(command='hp', name='NonExistent', value='10')
        
        # Execute
        result = self.handler.execute_command(args)
        
        # Verify
        assert result == 1
    
    def test_error_handling_validation_error(self):
        """Test error handling for ValidationError."""
        # Setup
        self.mock_encounter_service.create_encounter.side_effect = ValidationError(
            field="name",
            value="",
            reason="Invalid name"
        )
        
        args = argparse.Namespace(command='new', name='')
        
        # Execute
        result = self.handler.execute_command(args)
        
        # Verify
        assert result == 1
    
    def test_unknown_command(self):
        """Test handling of unknown command."""
        args = argparse.Namespace(command='unknown')
        
        # Execute
        result = self.handler.execute_command(args)
        
        # Verify
        assert result == 1


class TestMainFunction:
    """Test main function integration."""
    
    @patch('dnd_encounter_tracker.cli.main.DataManager')
    @patch('dnd_encounter_tracker.cli.main.EncounterService')
    @patch('dnd_encounter_tracker.cli.main.DisplayManager')
    @patch('dnd_encounter_tracker.cli.main.CommandHandler')
    def test_main_function_success(self, mock_command_handler_class, mock_display_manager_class, 
                                  mock_encounter_service_class, mock_data_manager_class):
        """Test main function with successful command execution."""
        # Setup mocks
        mock_handler = Mock()
        mock_handler.execute_command.return_value = 0
        mock_command_handler_class.return_value = mock_handler
        
        # Execute
        result = main(['new', 'Test Encounter'])
        
        # Verify
        assert result == 0
        mock_handler.execute_command.assert_called_once()
    
    @patch('dnd_encounter_tracker.cli.main.DataManager')
    @patch('dnd_encounter_tracker.cli.main.EncounterService')
    @patch('dnd_encounter_tracker.cli.main.DisplayManager')
    @patch('dnd_encounter_tracker.cli.main.CommandHandler')
    def test_main_function_error(self, mock_command_handler_class, mock_display_manager_class, 
                                mock_encounter_service_class, mock_data_manager_class):
        """Test main function with command execution error."""
        # Setup mocks
        mock_handler = Mock()
        mock_handler.execute_command.side_effect = Exception("Test error")
        mock_command_handler_class.return_value = mock_handler
        
        # Execute
        result = main(['new', 'Test Encounter'])
        
        # Verify
        assert result == 1
    
    def test_main_function_no_command(self):
        """Test main function with no command (shows help)."""
        # Execute
        result = main([])
        
        # Verify
        assert result == 0
    
    @patch('dnd_encounter_tracker.cli.main.DataManager')
    @patch('dnd_encounter_tracker.cli.main.EncounterService')
    @patch('dnd_encounter_tracker.cli.main.DisplayManager')
    @patch('dnd_encounter_tracker.cli.main.CommandHandler')
    def test_main_function_keyboard_interrupt(self, mock_command_handler_class, mock_display_manager_class, 
                                            mock_encounter_service_class, mock_data_manager_class):
        """Test main function with keyboard interrupt."""
        # Setup mocks
        mock_handler = Mock()
        mock_handler.execute_command.side_effect = KeyboardInterrupt()
        mock_command_handler_class.return_value = mock_handler
        
        # Execute
        result = main(['new', 'Test Encounter'])
        
        # Verify
        assert result == 1


class TestCommandValidation:
    """Test command validation and edge cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = create_parser()
    
    def test_add_command_missing_arguments(self):
        """Test 'add' command with missing required arguments."""
        with pytest.raises(SystemExit):
            self.parser.parse_args(['add'])
        
        with pytest.raises(SystemExit):
            self.parser.parse_args(['add', 'Thorin'])
        
        with pytest.raises(SystemExit):
            self.parser.parse_args(['add', 'Thorin', '45'])
    
    def test_add_command_invalid_hp(self):
        """Test 'add' command with invalid HP value."""
        with pytest.raises(SystemExit):
            self.parser.parse_args(['add', 'Thorin', 'invalid', '18'])
    
    def test_add_command_invalid_initiative(self):
        """Test 'add' command with invalid initiative value."""
        with pytest.raises(SystemExit):
            self.parser.parse_args(['add', 'Thorin', '45', 'invalid'])
    
    def test_init_command_invalid_value(self):
        """Test 'init' command with invalid initiative value."""
        with pytest.raises(SystemExit):
            self.parser.parse_args(['init', 'Thorin', 'invalid'])
    
    def test_note_edit_invalid_index(self):
        """Test 'note edit' command with invalid index."""
        with pytest.raises(SystemExit):
            self.parser.parse_args(['note', 'edit', 'Thorin', 'invalid', 'note'])
    
    def test_note_remove_invalid_index(self):
        """Test 'note remove' command with invalid index."""
        with pytest.raises(SystemExit):
            self.parser.parse_args(['note', 'remove', 'Thorin', 'invalid'])
    
    def test_note_command_missing_action(self):
        """Test 'note' command without action."""
        # This should parse successfully but will be handled by command handler
        args = self.parser.parse_args(['note'])
        assert args.command == 'note'
        assert not hasattr(args, 'note_action') or args.note_action is None