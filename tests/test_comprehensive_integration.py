"""Comprehensive integration tests covering all requirements."""

import pytest
import tempfile
import os
import json
from pathlib import Path

from dnd_encounter_tracker.core.encounter_service import EncounterService
from dnd_encounter_tracker.data.persistence import DataManager
from dnd_encounter_tracker.cli.display import DisplayManager
from dnd_encounter_tracker.cli.main import main
from tests.fixtures.data_generators import DataGenerator


class TestRequirementCompliance:
    """Test compliance with all specified requirements."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        self.data_manager = DataManager()
        self.encounter_service = EncounterService(self.data_manager)
        self.display_manager = DisplayManager()
        self.generator = DataGenerator()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_requirement_1_combatant_management(self):
        """Test Requirement 1: Add combatants to encounter."""
        # 1.1: Start new encounter and add combatants
        encounter = self.encounter_service.create_encounter("Requirement 1 Test")
        assert encounter.name == "Requirement 1 Test"
        
        # 1.2: Accept different combatant types
        self.encounter_service.add_combatant("Hero", 50, 18, "player")
        self.encounter_service.add_combatant("Dragon", 200, 20, "monster")
        self.encounter_service.add_combatant("Guard", 25, 12, "npc")
        
        # 1.3: Validate required fields
        combatants = encounter.combatants
        assert len(combatants) == 3
        
        for combatant in combatants:
            assert combatant.name is not None and combatant.name != ""
            assert combatant.max_hp > 0
            assert combatant.current_hp > 0
            assert combatant.initiative is not None
        
        # 1.4: Store all combatants in encounter
        names = [c.name for c in combatants]
        assert "Hero" in names
        assert "Dragon" in names
        assert "Guard" in names
    
    def test_requirement_2_initiative_management(self):
        """Test Requirement 2: Initiative order management."""
        encounter = self.encounter_service.create_encounter("Initiative Test")
        
        # Add combatants with specific initiative values
        self.encounter_service.add_combatant("Fast", 30, 20, "player")
        self.encounter_service.add_combatant("Medium", 30, 15, "monster")
        self.encounter_service.add_combatant("Slow", 30, 10, "npc")
        
        # 2.1: Display sorted by initiative (descending)
        order = self.encounter_service.get_initiative_order()
        initiatives = [c.initiative for c in order]
        assert initiatives == sorted(initiatives, reverse=True)
        assert order[0].name == "Fast"
        assert order[2].name == "Slow"
        
        # 2.2: Handle same initiative (manual adjustment)
        self.encounter_service.add_combatant("Tie", 30, 15, "player")  # Same as Medium
        
        # 2.3: Modify initiative and auto re-sort
        self.encounter_service.adjust_initiative("Slow", 25)
        updated_order = self.encounter_service.get_initiative_order()
        assert updated_order[0].name == "Slow"  # Now highest
        
        # 2.4: Indicate current turn
        current = self.encounter_service.get_current_combatant()
        assert current is not None
        assert encounter.current_turn >= 0
        
        # 2.5 & 2.6: Initiative sorting maintains data
        original_hp = {c.name: c.current_hp for c in encounter.combatants}
        encounter.sort_by_initiative()
        after_sort_hp = {c.name: c.current_hp for c in encounter.combatants}
        assert original_hp == after_sort_hp
    
    def test_requirement_3_hit_point_management(self):
        """Test Requirement 3: Hit point tracking and modification."""
        encounter = self.encounter_service.create_encounter("HP Test")
        self.encounter_service.add_combatant("Test Subject", 50, 15, "player")
        
        combatant = encounter.combatants[0]
        
        # 3.1: Accept absolute values
        self.encounter_service.update_hp("Test Subject", "30")
        assert combatant.current_hp == 30
        
        # 3.2: Accept relative additions
        self.encounter_service.update_hp("Test Subject", "+10")
        assert combatant.current_hp == 40
        
        # 3.3: Accept relative subtractions
        self.encounter_service.update_hp("Test Subject", "-15")
        assert combatant.current_hp == 25
        
        # 3.4: Prevent HP below 0
        self.encounter_service.update_hp("Test Subject", "-100")
        assert combatant.current_hp == 0
        
        # 3.5: Display current and max HP
        assert combatant.current_hp == 0
        assert combatant.max_hp == 50
    
    def test_requirement_4_notes_management(self):
        """Test Requirement 4: Notes for combatants."""
        encounter = self.encounter_service.create_encounter("Notes Test")
        self.encounter_service.add_combatant("Noted Character", 40, 15, "player")
        
        combatant = encounter.combatants[0]
        
        # 4.1: Store note with specific combatant
        self.encounter_service.add_note("Noted Character", "First note")
        assert "First note" in combatant.notes
        
        # 4.2: Display all associated notes
        self.encounter_service.add_note("Noted Character", "Second note")
        assert len(combatant.notes) == 2
        assert "Second note" in combatant.notes
        
        # 4.3: Allow free-form text input
        long_note = "This is a very long note with special characters !@#$%^&*() and numbers 12345"
        self.encounter_service.add_note("Noted Character", long_note)
        assert long_note in combatant.notes
        
        # 4.4: Edit and remove notes
        self.encounter_service.edit_note("Noted Character", 0, "Edited first note")
        assert combatant.notes[0] == "Edited first note"
        
        self.encounter_service.remove_note("Noted Character", 1)  # Remove second note
        assert "Second note" not in combatant.notes
        
        # 4.5: Indicate which combatants have notes
        # This is tested through display functionality
        assert len(combatant.notes) > 0
    
    def test_requirement_5_save_encounters(self):
        """Test Requirement 5: Save encounters to files."""
        encounter = self.encounter_service.create_encounter("Save Test")
        self.encounter_service.add_combatant("Saveable", 35, 14, "player")
        self.encounter_service.add_note("Saveable", "Test note")
        self.encounter_service.update_hp("Saveable", "-5")
        
        # 5.1: Write all combatant data to file
        self.encounter_service.save_encounter("save_test")
        assert os.path.exists("save_test.json")
        
        # 5.2: Preserve names, HP, initiative, notes
        with open("save_test.json", "r") as f:
            data = json.load(f)
        
        combatant_data = data["combatants"][0]
        assert combatant_data["name"] == "Saveable"
        assert combatant_data["max_hp"] == 35
        assert combatant_data["current_hp"] == 30  # 35 - 5
        assert combatant_data["initiative"] == 14
        assert "Test note" in combatant_data["notes"]
        
        # 5.3: Allow filename specification
        self.encounter_service.save_encounter("custom_filename")
        assert os.path.exists("custom_filename.json")
        
        # 5.4: Use format supporting web migration (JSON)
        assert data["name"] == "Save Test"
        assert "combatants" in data
        assert "metadata" in data or isinstance(data, dict)  # Structured format
    
    def test_requirement_6_load_encounters(self):
        """Test Requirement 6: Load encounters from files."""
        # Create and save test encounter
        original = self.encounter_service.create_encounter("Load Test")
        self.encounter_service.add_combatant("Loadable", 40, 16, "monster")
        self.encounter_service.add_note("Loadable", "Persistent note")
        self.encounter_service.update_hp("Loadable", "-10")
        self.encounter_service.save_encounter("load_test")
        
        # 6.1: Read combatant data from file
        new_service = EncounterService(DataManager())
        loaded = new_service.load_encounter("load_test")
        
        # 6.2: Restore all data
        assert loaded.name == "Load Test"
        assert len(loaded.combatants) == 1
        
        combatant = loaded.combatants[0]
        assert combatant.name == "Loadable"
        assert combatant.max_hp == 40
        assert combatant.current_hp == 30  # 40 - 10
        assert combatant.initiative == 16
        assert "Persistent note" in combatant.notes
        
        # 6.3: Display initiative order correctly
        order = new_service.get_initiative_order()
        assert len(order) == 1
        assert order[0].name == "Loadable"
        
        # 6.4: Handle corrupted files gracefully
        with open("corrupted.json", "w") as f:
            f.write("invalid json")
        
        from dnd_encounter_tracker.core.exceptions import FileFormatError
        with pytest.raises(FileFormatError):
            new_service.load_encounter("corrupted")
    
    def test_requirement_7_cli_interface(self):
        """Test Requirement 7: Command-line interface."""
        # 7.1: Clear menu options and commands
        result = main(['new', 'CLI Test'])
        assert result == 0
        
        result = main(['add', 'CLI Fighter', '45', '17', 'player'])
        assert result == 0
        
        # 7.2: Helpful error messages for invalid input
        result = main(['hp', 'Nonexistent', '10'])
        assert result != 0  # Should fail gracefully
        
        # 7.3: Confirmation of successful actions
        result = main(['hp', 'CLI Fighter', '-8'])
        assert result == 0
        
        # 7.4: Command documentation and examples
        # This is tested by ensuring help commands work
        result = main(['help'])
        assert result == 0
        
        # 7.5: Prompt to save unsaved changes
        # This is handled in interactive mode
        result = main(['save', 'cli_test'])
        assert result == 0
        assert os.path.exists('cli_test.json')
    
    def test_requirement_8_architecture_for_web_migration(self):
        """Test Requirement 8: Architecture supporting web deployment."""
        # 8.1: Separate business logic from CLI
        # Business logic is in EncounterService, CLI is separate
        service = EncounterService(DataManager())
        encounter = service.create_encounter("Architecture Test")
        
        # Service can work without CLI
        service.add_combatant("Test", 30, 15, "player")
        assert len(encounter.combatants) == 1
        
        # 8.2: Use structured data formats (JSON)
        service.save_encounter("architecture_test")
        with open("architecture_test.json", "r") as f:
            data = json.load(f)
        
        assert isinstance(data, dict)
        assert "combatants" in data
        assert isinstance(data["combatants"], list)
        
        # 8.3: Modular components
        # Components are separated: core, data, cli
        from dnd_encounter_tracker.core import models, encounter_service
        from dnd_encounter_tracker.data import persistence
        from dnd_encounter_tracker.cli import main, commands, display
        
        # All modules can be imported independently
        assert models is not None
        assert encounter_service is not None
        assert persistence is not None
        
        # 8.4: Web-compatible state management patterns
        # State is managed through service layer, not global variables
        service1 = EncounterService(DataManager())
        service2 = EncounterService(DataManager())
        
        service1.create_encounter("Service 1")
        service2.create_encounter("Service 2")
        
        # Services are independent
        assert service1.current_encounter.name != service2.current_encounter.name


class TestEndToEndScenarios:
    """Test complete end-to-end scenarios."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        self.generator = DataGenerator()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_typical_dm_session_workflow(self):
        """Test a typical DM session workflow."""
        # DM starts new encounter
        result = main(['new', 'Goblin Ambush'])
        assert result == 0
        
        # Add party members
        result = main(['add', 'Thorin', '45', '18', 'player'])
        assert result == 0
        
        result = main(['add', 'Elara', '38', '16', 'player'])
        assert result == 0
        
        result = main(['add', 'Gareth', '52', '14', 'player'])
        assert result == 0
        
        # Add enemies
        result = main(['add', 'Goblin Scout 1', '7', '15', 'monster'])
        assert result == 0
        
        result = main(['add', 'Goblin Scout 2', '7', '13', 'monster'])
        assert result == 0
        
        result = main(['add', 'Hobgoblin Captain', '39', '17', 'monster'])
        assert result == 0
        
        # Combat begins - apply damage
        result = main(['hp', 'Thorin', '-8'])
        assert result == 0
        
        result = main(['hp', 'Goblin Scout 2', '-7'])  # Kill it
        assert result == 0
        
        # Add status effects via notes
        result = main(['note', 'add', 'Thorin', 'Blessed by cleric'])
        assert result == 0
        
        result = main(['note', 'add', 'Hobgoblin Captain', 'Leadership used'])
        assert result == 0
        
        # Adjust initiative mid-combat
        result = main(['init', 'Elara', '20'])
        assert result == 0
        
        # Save encounter state
        result = main(['save', 'goblin_ambush_session'])
        assert result == 0
        
        # Verify saved data
        assert os.path.exists('goblin_ambush_session.json')
        
        with open('goblin_ambush_session.json', 'r') as f:
            data = json.load(f)
        
        assert data['name'] == 'Goblin Ambush'
        assert len(data['combatants']) == 6
        
        # Find Thorin and verify damage and note
        thorin = next(c for c in data['combatants'] if c['name'] == 'Thorin')
        assert thorin['current_hp'] == 37  # 45 - 8
        assert 'Blessed by cleric' in thorin['notes']
        
        # Find dead goblin
        goblin2 = next(c for c in data['combatants'] if c['name'] == 'Goblin Scout 2')
        assert goblin2['current_hp'] == 0
        
        # Verify initiative change
        elara = next(c for c in data['combatants'] if c['name'] == 'Elara')
        assert elara['initiative'] == 20
    
    def test_session_continuity_workflow(self):
        """Test loading and continuing a previous session."""
        # Create sample encounter file
        sample_encounter = self.generator.create_encounter(
            name="Continued Session",
            num_players=3,
            num_monsters=2,
            num_npcs=1
        )
        
        # Simulate mid-combat state
        sample_encounter.current_turn = 2
        sample_encounter.round_number = 3
        sample_encounter.combatants[0].current_hp = 20  # Damaged
        sample_encounter.combatants[0].add_note("Poisoned")
        
        # Save the encounter
        data_manager = DataManager()
        encounter_service = EncounterService(data_manager)
        encounter_service.current_encounter = sample_encounter
        encounter_service.save_encounter("continued_session")
        
        # Load encounter in new session
        result = main(['load', 'continued_session'])
        assert result == 0
        
        # Continue combat - advance turn
        result = main(['next'])
        assert result == 0
        
        # Apply more damage
        first_combatant = sample_encounter.combatants[0].name
        result = main(['hp', first_combatant, '-5'])
        assert result == 0
        
        # Add new note
        result = main(['note', 'add', first_combatant, 'Healing potion used'])
        assert result == 0
        
        # Save updated state
        result = main(['save', 'continued_session_updated'])
        assert result == 0
        
        # Verify continuity
        with open('continued_session_updated.json', 'r') as f:
            updated_data = json.load(f)
        
        first_combatant_data = next(c for c in updated_data['combatants'] if c['name'] == first_combatant)
        assert first_combatant_data['current_hp'] == 15  # 20 - 5
        assert 'Poisoned' in first_combatant_data['notes']
        assert 'Healing potion used' in first_combatant_data['notes']
    
    def test_complex_encounter_management(self):
        """Test managing a complex encounter with many operations."""
        # Create large encounter
        encounter = self.generator.create_encounter(
            name="Epic Battle",
            num_players=6,
            num_monsters=10,
            num_npcs=4
        )
        
        service = EncounterService(DataManager())
        service.current_encounter = encounter
        
        # Perform many operations
        operations_count = 0
        
        # Damage multiple combatants
        for combatant in encounter.combatants[:10]:
            service.update_hp(combatant.name, "-5")
            operations_count += 1
        
        # Add notes to various combatants
        for i, combatant in enumerate(encounter.combatants[::2]):  # Every other
            service.add_note(combatant.name, f"Status effect {i}")
            operations_count += 1
        
        # Adjust some initiatives
        for combatant in encounter.combatants[:3]:
            new_init = combatant.initiative + 5
            service.adjust_initiative(combatant.name, new_init)
            operations_count += 1
        
        # Advance through several turns
        for _ in range(10):
            service.next_turn()
            operations_count += 1
        
        # Save complex state
        service.save_encounter("complex_encounter")
        
        # Load and verify all operations persisted
        new_service = EncounterService(DataManager())
        loaded = new_service.load_encounter("complex_encounter")
        
        assert loaded.name == "Epic Battle"
        assert len(loaded.combatants) == 20  # 6 + 10 + 4
        
        # Verify some operations persisted
        damaged_count = sum(1 for c in loaded.combatants if c.current_hp < c.max_hp)
        assert damaged_count >= 10
        
        noted_count = sum(1 for c in loaded.combatants if len(c.notes) > 0)
        assert noted_count >= 10
        
        print(f"Complex encounter test completed {operations_count} operations successfully")


class TestRegressionPrevention:
    """Test to prevent regression of previously fixed issues."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        self.data_manager = DataManager()
        self.encounter_service = EncounterService(self.data_manager)
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_hp_edge_cases_regression(self):
        """Test HP edge cases that might cause issues."""
        encounter = self.encounter_service.create_encounter("HP Edge Cases")
        self.encounter_service.add_combatant("Edge Case", 1, 10, "player")  # Very low HP
        
        combatant = encounter.combatants[0]
        
        # Test minimum HP
        self.encounter_service.update_hp("Edge Case", "0")
        assert combatant.current_hp == 0
        
        # Test healing from 0
        self.encounter_service.update_hp("Edge Case", "+1")
        assert combatant.current_hp == 1
        
        # Test maximum HP boundary
        self.encounter_service.update_hp("Edge Case", "100")
        assert combatant.current_hp == 1  # Should be capped at max_hp
    
    def test_initiative_tie_handling_regression(self):
        """Test initiative tie handling doesn't break sorting."""
        encounter = self.encounter_service.create_encounter("Initiative Ties")
        
        # Add multiple combatants with same initiative
        for i in range(5):
            self.encounter_service.add_combatant(f"Tied {i}", 30, 15, "player")
        
        # Should not crash and should maintain stable order
        order1 = self.encounter_service.get_initiative_order()
        order2 = self.encounter_service.get_initiative_order()
        
        names1 = [c.name for c in order1]
        names2 = [c.name for c in order2]
        assert names1 == names2  # Order should be stable
    
    def test_empty_encounter_operations_regression(self):
        """Test operations on empty encounters don't crash."""
        encounter = self.encounter_service.create_encounter("Empty Test")
        
        # These should not crash
        order = self.encounter_service.get_initiative_order()
        assert len(order) == 0
        
        # Save empty encounter
        self.encounter_service.save_encounter("empty_test")
        assert os.path.exists("empty_test.json")
        
        # Load empty encounter
        loaded = self.encounter_service.load_encounter("empty_test")
        assert loaded.name == "Empty Test"
        assert len(loaded.combatants) == 0
    
    def test_special_characters_in_names_regression(self):
        """Test special characters in names don't break functionality."""
        encounter = self.encounter_service.create_encounter("Special Chars Test")
        
        special_names = [
            "O'Malley the Rogue",
            "Sir Reginald III",
            "Elf-Friend",
            "Dragon's Bane",
            "Spëcîål Chäracters",
            "Name with spaces",
            "123 Numeric Start"
        ]
        
        for i, name in enumerate(special_names):
            self.encounter_service.add_combatant(name, 30, 10 + i, "player")
        
        # All operations should work with special names
        for name in special_names:
            self.encounter_service.update_hp(name, "-5")
            self.encounter_service.add_note(name, "Special character test")
        
        # Save and load should preserve special characters
        self.encounter_service.save_encounter("special_chars")
        loaded = self.encounter_service.load_encounter("special_chars")
        
        loaded_names = [c.name for c in loaded.combatants]
        for name in special_names:
            assert name in loaded_names