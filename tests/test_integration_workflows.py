"""Integration tests covering complete encounter workflows."""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch

from dnd_encounter_tracker.core.encounter_service import EncounterService
from dnd_encounter_tracker.data.persistence import DataManager
from dnd_encounter_tracker.cli.main import main
from dnd_encounter_tracker.core.exceptions import (
    CombatantNotFoundError,
    EncounterNotLoadedError,
    FileFormatError
)
from tests.fixtures.data_generators import DataGenerator


class TestCompleteEncounterWorkflows:
    """Test complete end-to-end encounter workflows."""
    
    def setup_method(self):
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        self.data_manager = DataManager()
        self.encounter_service = EncounterService(self.data_manager)
        self.generator = DataGenerator()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_complete_encounter_creation_workflow(self):
        """Test creating a complete encounter from scratch."""
        # Create new encounter
        encounter = self.encounter_service.create_encounter("Test Battle")
        assert encounter.name == "Test Battle"
        assert len(encounter.combatants) == 0
        
        # Add various combatants
        self.encounter_service.add_combatant("Thorin", 45, 18, "player")
        self.encounter_service.add_combatant("Goblin Scout", 7, 12, "monster")
        self.encounter_service.add_combatant("Captain Marcus", 32, 15, "npc")
        
        # Verify combatants were added and sorted
        combatants = self.encounter_service.get_initiative_order()
        assert len(combatants) == 3
        assert combatants[0].name == "Thorin"  # Highest initiative
        assert combatants[1].name == "Captain Marcus"
        assert combatants[2].name == "Goblin Scout"
        
        # Update hit points
        self.encounter_service.update_hp("Thorin", "-8")
        thorin = next(c for c in combatants if c.name == "Thorin")
        assert thorin.current_hp == 37
        
        # Add notes
        self.encounter_service.add_note("Thorin", "Blessed by cleric")
        assert "Blessed by cleric" in thorin.notes
        
        # Adjust initiative and verify re-sorting
        self.encounter_service.adjust_initiative("Goblin Scout", 20)
        updated_order = self.encounter_service.get_initiative_order()
        assert updated_order[0].name == "Goblin Scout"  # Now highest
        
        # Save encounter
        self.encounter_service.save_encounter("test_battle")
        assert os.path.exists("test_battle.json")
    
    def test_encounter_save_load_cycle(self):
        """Test saving and loading encounters preserves all data."""
        # Create encounter with complex data
        original_encounter = self.generator.create_encounter(
            name="Save Load Test",
            num_players=3,
            num_monsters=4,
            num_npcs=2
        )
        
        # Set specific state
        original_encounter.current_turn = 2
        original_encounter.round_number = 5
        
        # Add some damage and notes
        original_encounter.combatants[0].current_hp = 20
        original_encounter.combatants[0].add_note("Test note 1")
        original_encounter.combatants[0].add_note("Test note 2")
        
        # Save through service
        self.encounter_service.current_encounter = original_encounter
        self.encounter_service.save_encounter("save_load_test")
        
        # Load into new service instance
        new_service = EncounterService(DataManager())
        loaded_encounter = new_service.load_encounter("save_load_test")
        
        # Verify all data preserved
        assert loaded_encounter.name == original_encounter.name
        assert loaded_encounter.current_turn == original_encounter.current_turn
        assert loaded_encounter.round_number == original_encounter.round_number
        assert len(loaded_encounter.combatants) == len(original_encounter.combatants)
        
        # Check specific combatant data
        orig_first = original_encounter.combatants[0]
        loaded_first = loaded_encounter.combatants[0]
        assert loaded_first.name == orig_first.name
        assert loaded_first.current_hp == orig_first.current_hp
        assert loaded_first.max_hp == orig_first.max_hp
        assert loaded_first.initiative == orig_first.initiative
        assert loaded_first.notes == orig_first.notes
        assert loaded_first.combatant_type == orig_first.combatant_type
    
    def test_combat_flow_workflow(self):
        """Test complete combat flow with turn management."""
        # Create encounter
        encounter = self.encounter_service.create_encounter("Combat Flow Test")
        
        # Add combatants
        self.encounter_service.add_combatant("Fighter", 50, 15, "player")
        self.encounter_service.add_combatant("Wizard", 30, 12, "player")
        self.encounter_service.add_combatant("Orc", 25, 10, "monster")
        
        # Start combat
        current = self.encounter_service.get_current_combatant()
        assert current.name == "Fighter"  # Highest initiative
        assert encounter.current_turn == 0
        assert encounter.round_number == 1
        
        # Advance turns
        self.encounter_service.next_turn()
        current = self.encounter_service.get_current_combatant()
        assert current.name == "Wizard"
        assert encounter.current_turn == 1
        
        self.encounter_service.next_turn()
        current = self.encounter_service.get_current_combatant()
        assert current.name == "Orc"
        assert encounter.current_turn == 2
        
        # Next turn should wrap to new round
        self.encounter_service.next_turn()
        current = self.encounter_service.get_current_combatant()
        assert current.name == "Fighter"
        assert encounter.current_turn == 0
        assert encounter.round_number == 2
        
        # Simulate combat damage
        self.encounter_service.update_hp("Orc", "-15")
        orc = next(c for c in encounter.combatants if c.name == "Orc")
        assert orc.current_hp == 10
        
        # Kill the orc
        self.encounter_service.update_hp("Orc", "-10")
        assert orc.current_hp == 0
        assert not orc.is_alive()
    
    def test_file_management_workflow(self):
        """Test file management operations."""
        # Create multiple encounters
        encounters = self.generator.create_sample_encounters()
        
        # Save all encounters
        for name, encounter in encounters.items():
            self.encounter_service.current_encounter = encounter
            self.encounter_service.save_encounter(name)
        
        # Verify files exist
        for name in encounters.keys():
            assert os.path.exists(f"{name}.json")
        
        # Test file listing
        available = self.data_manager.get_available_encounters()
        assert len(available) == len(encounters)
        for name in encounters.keys():
            assert name in available
        
        # Test backup creation
        original_file = "goblin_ambush.json"
        self.data_manager.create_backup(original_file)
        
        # Check backup file exists
        backup_files = [f for f in os.listdir('.') if f.startswith("goblin_ambush") and f.endswith(".backup")]
        assert len(backup_files) > 0
        
        # Test loading different encounters
        for name in list(encounters.keys())[:3]:  # Test first 3
            loaded = self.encounter_service.load_encounter(name)
            assert loaded.name == encounters[name].name
    
    def test_error_handling_workflow(self):
        """Test error handling in various scenarios."""
        # Test operations without loaded encounter
        with pytest.raises(EncounterNotLoadedError):
            self.encounter_service.add_combatant("Test", 10, 10)
        
        with pytest.raises(EncounterNotLoadedError):
            self.encounter_service.update_hp("Test", "10")
        
        # Create encounter for further tests
        self.encounter_service.create_encounter("Error Test")
        self.encounter_service.add_combatant("Test Fighter", 30, 15)
        
        # Test invalid combatant operations
        with pytest.raises(CombatantNotFoundError):
            self.encounter_service.update_hp("Nonexistent", "10")
        
        with pytest.raises(CombatantNotFoundError):
            self.encounter_service.add_note("Nonexistent", "Test note")
        
        # Test invalid HP values
        from dnd_encounter_tracker.core.exceptions import InvalidHPValueError
        with pytest.raises(InvalidHPValueError):
            self.encounter_service.update_hp("Test Fighter", "invalid")
        
        # Test file operations
        with pytest.raises(FileNotFoundError):
            self.encounter_service.load_encounter("nonexistent_file")
        
        # Test corrupted file
        with open("corrupted.json", "w") as f:
            f.write("invalid json content")
        
        with pytest.raises(FileFormatError):
            self.encounter_service.load_encounter("corrupted")
    
    def test_note_management_workflow(self):
        """Test complete note management workflow."""
        # Create encounter with combatant
        self.encounter_service.create_encounter("Note Test")
        self.encounter_service.add_combatant("Test Character", 40, 15)
        
        # Add multiple notes
        self.encounter_service.add_note("Test Character", "First note")
        self.encounter_service.add_note("Test Character", "Second note")
        self.encounter_service.add_note("Test Character", "Third note")
        
        combatant = self.encounter_service.current_encounter.combatants[0]
        assert len(combatant.notes) == 3
        assert "First note" in combatant.notes
        
        # Edit note
        self.encounter_service.edit_note("Test Character", 0, "Edited first note")
        assert combatant.notes[0] == "Edited first note"
        
        # Remove note
        self.encounter_service.remove_note("Test Character", 1)  # Remove second note
        assert len(combatant.notes) == 2
        assert "Second note" not in combatant.notes
        
        # Verify notes persist through save/load
        self.encounter_service.save_encounter("note_test")
        loaded = self.encounter_service.load_encounter("note_test")
        loaded_combatant = loaded.combatants[0]
        assert len(loaded_combatant.notes) == 2
        assert "Edited first note" in loaded_combatant.notes
        assert "Third note" in loaded_combatant.notes


class TestCLIIntegration:
    """Test CLI integration with complete workflows."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_cli_encounter_creation_workflow(self):
        """Test creating encounter through CLI commands."""
        # Create new encounter
        result = main(['new', 'CLI Test Encounter'])
        assert result == 0
        
        # Add combatants
        result = main(['add', 'Hero', '50', '18', 'player'])
        assert result == 0
        
        result = main(['add', 'Villain', '30', '15', 'monster'])
        assert result == 0
        
        # Update HP
        result = main(['hp', 'Hero', '-10'])
        assert result == 0
        
        # Add note
        result = main(['note', 'add', 'Hero', 'Test note'])
        assert result == 0
        
        # Save encounter
        result = main(['save', 'cli_test'])
        assert result == 0
        
        # Verify file was created
        assert os.path.exists('cli_test.json')
        
        # Load and verify
        with open('cli_test.json', 'r') as f:
            data = json.load(f)
        
        assert data['name'] == 'CLI Test Encounter'
        assert len(data['combatants']) == 2
        
        # Find hero and check HP
        hero = next(c for c in data['combatants'] if c['name'] == 'Hero')
        assert hero['current_hp'] == 40  # 50 - 10
        assert 'Test note' in hero['notes']
    
    def test_cli_load_and_modify_workflow(self):
        """Test loading existing encounter and modifying it."""
        # Create sample encounter file
        sample_data = {
            "name": "Sample Encounter",
            "combatants": [
                {
                    "name": "Existing Fighter",
                    "max_hp": 40,
                    "current_hp": 40,
                    "initiative": 16,
                    "notes": [],
                    "combatant_type": "player"
                }
            ],
            "current_turn": 0,
            "round_number": 1,
            "metadata": {
                "created": "2025-01-07T12:00:00Z",
                "version": "1.0"
            }
        }
        
        with open('sample.json', 'w') as f:
            json.dump(sample_data, f)
        
        # Load encounter
        result = main(['load', 'sample'])
        assert result == 0
        
        # Add new combatant
        result = main(['add', 'New Enemy', '25', '12', 'monster'])
        assert result == 0
        
        # Modify existing combatant
        result = main(['hp', 'Existing Fighter', '-15'])
        assert result == 0
        
        result = main(['note', 'add', 'Existing Fighter', 'Took damage'])
        assert result == 0
        
        # Save modified encounter
        result = main(['save', 'modified_sample'])
        assert result == 0
        
        # Verify modifications
        with open('modified_sample.json', 'r') as f:
            modified_data = json.load(f)
        
        assert len(modified_data['combatants']) == 2
        
        fighter = next(c for c in modified_data['combatants'] if c['name'] == 'Existing Fighter')
        assert fighter['current_hp'] == 25  # 40 - 15
        assert 'Took damage' in fighter['notes']
        
        enemy = next(c for c in modified_data['combatants'] if c['name'] == 'New Enemy')
        assert enemy['max_hp'] == 25
    
    def test_cli_error_handling(self):
        """Test CLI error handling."""
        # Test command without encounter loaded
        result = main(['add', 'Test', '10', '10'])
        assert result != 0  # Should fail
        
        # Create encounter first
        result = main(['new', 'Error Test'])
        assert result == 0
        
        # Test invalid HP update
        result = main(['add', 'Test Fighter', '30', '15'])
        assert result == 0
        
        result = main(['hp', 'Nonexistent', '10'])
        assert result != 0  # Should fail
        
        # Test loading nonexistent file
        result = main(['load', 'nonexistent'])
        assert result != 0  # Should fail
    
    @patch('builtins.input')
    def test_cli_interactive_workflow(self, mock_input):
        """Test interactive CLI workflow."""
        # Mock user inputs for interactive session
        mock_input.side_effect = [
            'new Test Interactive',  # Create encounter
            'add Fighter 50 18 player',  # Add combatant
            'add Orc 25 12 monster',  # Add another
            'show',  # Display encounter
            'hp Fighter -8',  # Update HP
            'note add Fighter "Took damage"',  # Add note
            'save interactive_test',  # Save
            'quit'  # Exit
        ]
        
        # This would test the interactive mode, but requires more complex mocking
        # For now, we'll test that the interactive mode can be imported
        from dnd_encounter_tracker.cli.interactive import InteractiveSession
        assert InteractiveSession is not None


class TestDataIntegrity:
    """Test data integrity across operations."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        self.data_manager = DataManager()
        self.encounter_service = EncounterService(self.data_manager)
        self.generator = DataGenerator()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initiative_order_consistency(self):
        """Test that initiative order remains consistent across operations."""
        # Create encounter with specific initiative values
        encounter = self.encounter_service.create_encounter("Initiative Test")
        
        # Add combatants with known initiative order
        combatants_data = [
            ("Alpha", 20),
            ("Beta", 15),
            ("Gamma", 18),
            ("Delta", 12),
            ("Epsilon", 22)
        ]
        
        for name, init in combatants_data:
            self.encounter_service.add_combatant(name, 30, init)
        
        # Verify initial order
        order = self.encounter_service.get_initiative_order()
        expected_order = ["Epsilon", "Alpha", "Gamma", "Beta", "Delta"]
        actual_order = [c.name for c in order]
        assert actual_order == expected_order
        
        # Modify HP and verify order unchanged
        self.encounter_service.update_hp("Alpha", "-10")
        order_after_hp = self.encounter_service.get_initiative_order()
        actual_order_after_hp = [c.name for c in order_after_hp]
        assert actual_order_after_hp == expected_order
        
        # Add notes and verify order unchanged
        self.encounter_service.add_note("Beta", "Test note")
        order_after_note = self.encounter_service.get_initiative_order()
        actual_order_after_note = [c.name for c in order_after_note]
        assert actual_order_after_note == expected_order
        
        # Save/load and verify order preserved
        self.encounter_service.save_encounter("initiative_test")
        loaded_encounter = self.encounter_service.load_encounter("initiative_test")
        loaded_order = [c.name for c in loaded_encounter.combatants]
        assert loaded_order == expected_order
    
    def test_hp_constraints_enforcement(self):
        """Test that HP constraints are enforced consistently."""
        encounter = self.encounter_service.create_encounter("HP Test")
        self.encounter_service.add_combatant("Test Subject", 50, 15)
        
        combatant = encounter.combatants[0]
        
        # Test HP cannot go below 0
        self.encounter_service.update_hp("Test Subject", "-60")
        assert combatant.current_hp == 0
        
        # Test HP cannot exceed maximum
        self.encounter_service.update_hp("Test Subject", "100")
        assert combatant.current_hp == 50  # Should be capped at max_hp
        
        # Test relative updates work correctly
        self.encounter_service.update_hp("Test Subject", "30")  # Set to 30
        assert combatant.current_hp == 30
        
        self.encounter_service.update_hp("Test Subject", "+15")  # Add 15
        assert combatant.current_hp == 45
        
        self.encounter_service.update_hp("Test Subject", "+10")  # Try to add 10 more
        assert combatant.current_hp == 50  # Should be capped at max
        
        self.encounter_service.update_hp("Test Subject", "-25")  # Subtract 25
        assert combatant.current_hp == 25
    
    def test_concurrent_modifications(self):
        """Test handling of rapid successive modifications."""
        encounter = self.encounter_service.create_encounter("Concurrent Test")
        
        # Add multiple combatants
        for i in range(5):
            self.encounter_service.add_combatant(f"Combatant {i}", 30, 15 + i)
        
        # Perform rapid modifications
        for i in range(10):
            for j in range(5):
                combatant_name = f"Combatant {j}"
                self.encounter_service.update_hp(combatant_name, f"-{i+1}")
                self.encounter_service.add_note(combatant_name, f"Note {i}")
        
        # Verify data integrity
        for j in range(5):
            combatant = next(c for c in encounter.combatants if c.name == f"Combatant {j}")
            # HP should be 0 (30 - sum of 1+2+...+10 = 55, capped at 0)
            assert combatant.current_hp == 0
            # Should have 10 notes
            assert len(combatant.notes) == 10
        
        # Save and reload to verify persistence
        self.encounter_service.save_encounter("concurrent_test")
        loaded = self.encounter_service.load_encounter("concurrent_test")
        
        for j in range(5):
            combatant = next(c for c in loaded.combatants if c.name == f"Combatant {j}")
            assert combatant.current_hp == 0
            assert len(combatant.notes) == 10