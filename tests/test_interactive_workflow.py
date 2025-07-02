"""Integration tests for interactive CLI workflow and help system."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

from dnd_encounter_tracker.cli.interactive import InteractiveSession
from dnd_encounter_tracker.cli.help import HelpManager
from dnd_encounter_tracker.cli.main import main, interactive_mode
from dnd_encounter_tracker.core.encounter_service import EncounterService
from dnd_encounter_tracker.data.persistence import DataManager


class TestInteractiveSession:
    """Test the interactive CLI session."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary directory for test data."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def session(self, temp_data_dir):
        """Create an interactive session with temporary data directory."""
        session = InteractiveSession()
        # Override the data directory after initialization
        session.data_manager.data_directory = temp_data_dir
        return session
    
    def test_session_initialization(self, session):
        """Test that interactive session initializes correctly."""
        assert session.data_manager is not None
        assert session.encounter_service is not None
        assert session.display_manager is not None
        assert session.help_manager is not None
        assert session.command_handler is not None
        assert session.running is True
        assert session.unsaved_changes is False
    
    def test_get_prompt_no_encounter(self, session):
        """Test prompt when no encounter is loaded."""
        prompt = session._get_prompt()
        assert prompt == "dnd-tracker > "
    
    def test_get_prompt_with_encounter(self, session):
        """Test prompt when encounter is loaded."""
        session.encounter_service.create_encounter("Test Encounter")
        prompt = session._get_prompt()
        assert prompt == "[Test Encounter] > "
    
    def test_get_prompt_with_unsaved_changes(self, session):
        """Test prompt shows unsaved changes indicator."""
        session.encounter_service.create_encounter("Test Encounter")
        session.unsaved_changes = True
        prompt = session._get_prompt()
        assert prompt == "[Test Encounter*] > "
    
    def test_parse_new_command(self, session):
        """Test parsing 'new' command."""
        args = session._parse_interactive_command(['new', 'Test', 'Encounter'])
        assert args.command == 'new'
        assert args.name == 'Test Encounter'
    
    def test_parse_add_command(self, session):
        """Test parsing 'add' command."""
        args = session._parse_interactive_command(['add', 'Thorin', '45', '18', 'player'])
        assert args.command == 'add'
        assert args.name == 'Thorin'
        assert args.hp == 45
        assert args.initiative == 18
        assert args.type == 'player'
    
    def test_parse_add_command_default_type(self, session):
        """Test parsing 'add' command with default type."""
        args = session._parse_interactive_command(['add', 'Goblin', '7', '12'])
        assert args.command == 'add'
        assert args.name == 'Goblin'
        assert args.hp == 7
        assert args.initiative == 12
        assert args.type == 'unknown'
    
    def test_parse_hp_command(self, session):
        """Test parsing 'hp' command."""
        args = session._parse_interactive_command(['hp', 'Thorin', '-8'])
        assert args.command == 'hp'
        assert args.name == 'Thorin'
        assert args.value == '-8'
    
    def test_parse_note_add_command(self, session):
        """Test parsing 'note add' command."""
        args = session._parse_interactive_command(['note', 'add', 'Thorin', 'Blessed', 'by', 'cleric'])
        assert args.command == 'note'
        assert args.note_action == 'add'
        assert args.name == 'Thorin'
        assert args.note == 'Blessed by cleric'
    
    def test_parse_invalid_command(self, session):
        """Test parsing invalid command returns None."""
        with patch('builtins.print') as mock_print:
            args = session._parse_interactive_command(['invalid'])
            assert args is None
            mock_print.assert_called()
    
    def test_parse_insufficient_args(self, session):
        """Test parsing command with insufficient arguments."""
        with patch('builtins.print') as mock_print:
            args = session._parse_interactive_command(['add', 'Thorin'])
            assert args is None
            mock_print.assert_called_with("Usage: add <name> <hp> <initiative> [type]")
    
    def test_show_status_no_encounter(self, session):
        """Test status display with no encounter."""
        with patch('builtins.print') as mock_print:
            session._show_status()
            mock_print.assert_any_call("No encounter loaded")
    
    def test_show_status_with_encounter(self, session):
        """Test status display with encounter."""
        encounter = session.encounter_service.create_encounter("Test Encounter")
        session.encounter_service.add_combatant("Thorin", 45, 18, "player")
        
        with patch('builtins.print') as mock_print:
            session._show_status()
            mock_print.assert_any_call("Current encounter: Test Encounter")
            mock_print.assert_any_call("Combatants: 1")
    
    def test_confirm_exit_no_changes(self, session):
        """Test exit confirmation with no unsaved changes."""
        result = session._confirm_exit()
        assert result is True
    
    def test_confirm_exit_with_changes_yes(self, session):
        """Test exit confirmation with unsaved changes - user confirms."""
        session.unsaved_changes = True
        with patch('builtins.input', return_value='y'):
            result = session._confirm_exit()
            assert result is True
    
    def test_confirm_exit_with_changes_no(self, session):
        """Test exit confirmation with unsaved changes - user cancels."""
        session.unsaved_changes = True
        with patch('builtins.input', return_value='n'):
            result = session._confirm_exit()
            assert result is False
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_execute_command_new(self, mock_print, mock_input, session):
        """Test executing 'new' command in interactive mode."""
        session._execute_command('new "Test Encounter"')
        
        encounter = session.encounter_service.get_current_encounter()
        assert encounter is not None
        assert encounter.name == "Test Encounter"
        assert session.unsaved_changes is True
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_execute_command_help(self, mock_print, mock_input, session):
        """Test executing 'help' command in interactive mode."""
        session._execute_command('help')
        mock_print.assert_called()
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_execute_command_status(self, mock_print, mock_input, session):
        """Test executing 'status' command in interactive mode."""
        session._execute_command('status')
        mock_print.assert_any_call("No encounter loaded")


class TestHelpManager:
    """Test the help management system."""
    
    @pytest.fixture
    def help_manager(self):
        """Create a help manager instance."""
        return HelpManager()
    
    def test_help_manager_initialization(self, help_manager):
        """Test help manager initializes with all topics."""
        expected_topics = ['commands', 'examples', 'workflow', 'notes', 'hp', 'initiative', 'interactive']
        assert all(topic in help_manager.help_topics for topic in expected_topics)
    
    def test_show_help_topic_valid(self, help_manager):
        """Test showing help for valid topic."""
        with patch('builtins.print') as mock_print:
            help_manager.show_help_topic('commands')
            mock_print.assert_called_once()
            # Verify the help content contains expected information
            help_content = mock_print.call_args[0][0]
            assert 'Command Reference' in help_content
    
    def test_show_help_topic_invalid(self, help_manager):
        """Test showing help for invalid topic."""
        with patch('builtins.print') as mock_print:
            help_manager.show_help_topic('invalid')
            mock_print.assert_any_call("Unknown help topic: invalid")
    
    def test_interactive_help_content(self, help_manager):
        """Test interactive help contains essential information."""
        help_content = help_manager._get_interactive_help()
        
        # Check for key sections
        assert 'BASIC COMMANDS:' in help_content
        assert 'ENCOUNTER MANAGEMENT:' in help_content
        assert 'COMBATANT MANAGEMENT:' in help_content
        assert 'help' in help_content
        assert 'new <name>' in help_content
        assert 'exit' in help_content
    
    def test_commands_help_content(self, help_manager):
        """Test commands help contains comprehensive information."""
        help_content = help_manager._get_commands_help()
        
        # Check for key command categories
        assert 'ENCOUNTER MANAGEMENT:' in help_content
        assert 'COMBATANT MANAGEMENT:' in help_content
        assert 'DISPLAY COMMANDS:' in help_content
        assert 'NOTE MANAGEMENT:' in help_content
        
        # Check for specific commands
        assert 'new <encounter_name>' in help_content
        assert 'add <name> <max_hp> <initiative>' in help_content
        assert 'hp <name> <value>' in help_content
    
    def test_examples_help_content(self, help_manager):
        """Test examples help contains practical usage examples."""
        help_content = help_manager._get_examples_help()
        
        # Check for example sections
        assert 'STARTING A NEW ENCOUNTER:' in help_content
        assert 'MANAGING COMBAT:' in help_content
        assert 'HP MANAGEMENT EXAMPLES:' in help_content
        
        # Check for specific examples
        assert 'new "Goblin Ambush"' in help_content
        assert 'hp Thorin -8' in help_content
        assert 'note add' in help_content
    
    def test_workflow_help_content(self, help_manager):
        """Test workflow help provides step-by-step guidance."""
        help_content = help_manager._get_workflow_help()
        
        # Check for workflow sections
        assert 'SETTING UP AN ENCOUNTER:' in help_content
        assert 'RUNNING COMBAT:' in help_content
        assert 'SAVING YOUR WORK:' in help_content
        assert 'TIPS FOR SMOOTH GAMEPLAY:' in help_content
    
    def test_notes_help_content(self, help_manager):
        """Test notes help explains note management thoroughly."""
        help_content = help_manager._get_notes_help()
        
        # Check for note management sections
        assert 'WHAT ARE NOTES?' in help_content
        assert 'ADDING NOTES:' in help_content
        assert 'EDITING NOTES:' in help_content
        assert 'COMMON NOTE TYPES:' in help_content
        assert 'BEST PRACTICES:' in help_content
    
    def test_hp_help_content(self, help_manager):
        """Test HP help explains hit point management."""
        help_content = help_manager._get_hp_help()
        
        # Check for HP management sections
        assert 'HP UPDATE FORMATS:' in help_content
        assert 'ABSOLUTE VALUES:' in help_content
        assert 'DAMAGE (Subtraction):' in help_content
        assert 'HEALING (Addition):' in help_content
        assert 'HP VALIDATION:' in help_content
    
    def test_initiative_help_content(self, help_manager):
        """Test initiative help explains the initiative system."""
        help_content = help_manager._get_initiative_help()
        
        # Check for initiative sections
        assert 'HOW INITIATIVE WORKS:' in help_content
        assert 'SETTING INITIATIVE:' in help_content
        assert 'TURN MANAGEMENT:' in help_content
        assert 'ROUND TRACKING:' in help_content


class TestCompleteWorkflows:
    """Test complete user workflows from start to finish."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary directory for test data."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def session(self, temp_data_dir):
        """Create an interactive session with temporary data directory."""
        session = InteractiveSession()
        # Override the data directory after initialization
        session.data_manager.data_directory = temp_data_dir
        return session
    
    def test_complete_encounter_workflow(self, session):
        """Test a complete encounter creation and management workflow."""
        # Create new encounter
        session._execute_command('new "Goblin Ambush"')
        encounter = session.encounter_service.get_current_encounter()
        assert encounter.name == "Goblin Ambush"
        assert session.unsaved_changes is True
        
        # Add combatants
        session._execute_command('add Thorin 45 18 player')
        session._execute_command('add Legolas 38 16 player')
        session._execute_command('add "Goblin Scout" 7 12 monster')
        
        encounter = session.encounter_service.get_current_encounter()
        assert len(encounter.combatants) == 3
        
        # Manage combat
        session._execute_command('hp Thorin -8')
        thorin = encounter.get_combatant("Thorin")
        assert thorin.current_hp == 37
        
        # Add notes
        session._execute_command('note add Thorin "Blessed by cleric"')
        assert len(thorin.notes) == 1
        assert thorin.notes[0] == "Blessed by cleric"
        
        # Advance turns
        session._execute_command('next')
        assert encounter.current_turn == 1  # Should be Legolas (initiative 16)
        
        # Save encounter
        session._execute_command('save goblin_ambush')
        assert session.unsaved_changes is False
    
    def test_load_and_modify_workflow(self, session, temp_data_dir):
        """Test loading an existing encounter and modifying it."""
        # First create and save an encounter
        session._execute_command('new "Dragon Fight"')
        session._execute_command('add "Ancient Red Dragon" 546 23 monster')
        session._execute_command('add Gandalf 165 20 player')
        session._execute_command('save dragon_fight')
        
        # Create a new session to simulate restarting the application
        new_session = InteractiveSession()
        new_session.data_manager.data_directory = temp_data_dir
        
        # Load the encounter
        new_session._execute_command('load dragon_fight')
        encounter = new_session.encounter_service.get_current_encounter()
        assert encounter.name == "Dragon Fight"
        assert len(encounter.combatants) == 2
        
        # Modify the encounter
        new_session._execute_command('add Aragorn 87 19 player')
        assert len(encounter.combatants) == 3
        
        # Verify initiative order is maintained
        combatants = encounter.get_initiative_order()
        assert combatants[0].name == "Ancient Red Dragon"  # Initiative 23
        assert combatants[1].name == "Gandalf"  # Initiative 20
        assert combatants[2].name == "Aragorn"  # Initiative 19
    
    def test_note_management_workflow(self, session):
        """Test complete note management workflow."""
        # Setup encounter
        session._execute_command('new "Status Effects Test"')
        session._execute_command('add Wizard 32 15 player')
        
        # Add multiple notes
        session._execute_command('note add Wizard "Concentration: Fireball"')
        session._execute_command('note add Wizard "Shield spell (3 rounds)"')
        session._execute_command('note add Wizard "Blessed (+1d4 to attacks)"')
        
        wizard = session.encounter_service.get_current_encounter().get_combatant("Wizard")
        assert len(wizard.notes) == 3
        
        # Edit a note
        session._execute_command('note edit Wizard 2 "Shield spell (2 rounds left)"')
        assert wizard.notes[1] == "Shield spell (2 rounds left)"
        
        # Remove a note
        session._execute_command('note remove Wizard 1')
        assert len(wizard.notes) == 2
        assert "Concentration: Fireball" not in wizard.notes
    
    def test_hp_management_workflow(self, session):
        """Test comprehensive HP management workflow."""
        # Setup encounter
        session._execute_command('new "HP Test"')
        session._execute_command('add Fighter 58 16 player')
        
        fighter = session.encounter_service.get_current_encounter().get_combatant("Fighter")
        assert fighter.current_hp == 58
        
        # Test damage
        session._execute_command('hp Fighter -15')
        assert fighter.current_hp == 43
        
        # Test healing
        session._execute_command('hp Fighter +8')
        assert fighter.current_hp == 51
        
        # Test absolute value
        session._execute_command('hp Fighter 25')
        assert fighter.current_hp == 25
        
        # Test damage to 0
        session._execute_command('hp Fighter -30')
        assert fighter.current_hp == 0
        
        # Test healing from 0
        session._execute_command('hp Fighter +1')
        assert fighter.current_hp == 1
    
    def test_initiative_adjustment_workflow(self, session):
        """Test initiative adjustment and reordering workflow."""
        # Setup encounter
        session._execute_command('new "Initiative Test"')
        session._execute_command('add Alice 30 15 player')
        session._execute_command('add Bob 25 15 player')  # Same initiative
        session._execute_command('add Charlie 20 10 player')
        
        encounter = session.encounter_service.get_current_encounter()
        combatants = encounter.get_initiative_order()
        
        # Verify initial order (Alice and Bob both have 15, order by name)
        assert combatants[0].name == "Alice"
        assert combatants[1].name == "Bob"
        assert combatants[2].name == "Charlie"
        
        # Adjust Charlie's initiative to be highest
        session._execute_command('init Charlie 20')
        combatants = encounter.get_initiative_order()
        assert combatants[0].name == "Charlie"
        assert combatants[1].name == "Alice"
        assert combatants[2].name == "Bob"
    
    def test_error_handling_workflow(self, session):
        """Test error handling in various scenarios."""
        # Test command without encounter
        with patch('builtins.print') as mock_print:
            session._execute_command('show')
            # Should print error message about no encounter loaded
            mock_print.assert_called()
        
        # Create encounter for further tests
        session._execute_command('new "Error Test"')
        session._execute_command('add TestChar 30 15 player')
        
        # Test invalid combatant name
        with patch('builtins.print') as mock_print:
            session._execute_command('hp NonExistent -5')
            mock_print.assert_called()
        
        # Test invalid HP format
        with patch('builtins.print') as mock_print:
            session._execute_command('hp TestChar invalid')
            mock_print.assert_called()
        
        # Test invalid note index
        with patch('builtins.print') as mock_print:
            session._execute_command('note remove TestChar 1')  # No notes exist
            mock_print.assert_called()


class TestMainEntryPoints:
    """Test main entry points and command-line integration."""
    
    def test_main_no_args_starts_interactive(self):
        """Test that main() with no arguments starts interactive mode."""
        with patch('dnd_encounter_tracker.cli.main.interactive_mode') as mock_interactive:
            mock_interactive.return_value = 0
            with patch('sys.argv', ['dnd-encounter-tracker']):
                result = main()
                assert result == 0
                mock_interactive.assert_called_once()
    
    def test_main_with_help_command(self):
        """Test main() with help command."""
        with patch('builtins.print') as mock_print:
            result = main(['help', 'commands'])
            assert result == 0
            mock_print.assert_called()
    
    def test_main_with_interactive_command(self):
        """Test main() with explicit interactive command."""
        with patch('dnd_encounter_tracker.cli.interactive.InteractiveSession') as mock_session_class:
            mock_session = MagicMock()
            mock_session.run.return_value = 0
            mock_session_class.return_value = mock_session
            
            result = main(['interactive'])
            assert result == 0
            mock_session.run.assert_called_once()
    
    def test_interactive_mode_function(self):
        """Test the interactive_mode() function."""
        with patch('dnd_encounter_tracker.cli.interactive.InteractiveSession') as mock_session_class:
            mock_session = MagicMock()
            mock_session.run.return_value = 0
            mock_session_class.return_value = mock_session
            
            result = interactive_mode()
            assert result == 0
            mock_session.run.assert_called_once()
    
    def test_interactive_mode_keyboard_interrupt(self):
        """Test interactive mode handles keyboard interrupt gracefully."""
        with patch('dnd_encounter_tracker.cli.interactive.InteractiveSession') as mock_session_class:
            mock_session = MagicMock()
            mock_session.run.side_effect = KeyboardInterrupt()
            mock_session_class.return_value = mock_session
            
            with patch('builtins.print') as mock_print:
                result = interactive_mode()
                assert result == 0
                mock_print.assert_called_with("\nGoodbye!")


if __name__ == '__main__':
    pytest.main([__file__])