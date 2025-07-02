"""Tests for turn tracking and combat flow functionality."""

import pytest
from unittest.mock import Mock, patch

from dnd_encounter_tracker.core.models import Encounter, Combatant
from dnd_encounter_tracker.core.encounter_service import EncounterService
from dnd_encounter_tracker.core.exceptions import EncounterNotLoadedError
from dnd_encounter_tracker.data.persistence import DataManager
from dnd_encounter_tracker.cli.commands import CommandHandler
from dnd_encounter_tracker.cli.display import DisplayManager


class TestTurnTracking:
    """Test turn tracking functionality."""
    
    @pytest.fixture
    def encounter(self):
        """Create a sample encounter with multiple combatants."""
        encounter = Encounter(name="Combat Test")
        
        # Add combatants in mixed initiative order
        fighter = Combatant(name="Fighter", max_hp=50, current_hp=50, initiative=18)
        wizard = Combatant(name="Wizard", max_hp=30, current_hp=30, initiative=15)
        rogue = Combatant(name="Rogue", max_hp=40, current_hp=40, initiative=20)
        goblin = Combatant(name="Goblin", max_hp=10, current_hp=10, initiative=12)
        
        encounter.add_combatant(rogue)    # Will be sorted to position 0 (init 20)
        encounter.add_combatant(fighter)  # Will be sorted to position 1 (init 18)
        encounter.add_combatant(wizard)   # Will be sorted to position 2 (init 15)
        encounter.add_combatant(goblin)   # Will be sorted to position 3 (init 12)
        
        return encounter
    
    def test_initial_turn_state(self, encounter):
        """Test initial turn state after creating encounter."""
        # The current_turn tracks the combatant that was at index 0 when first added
        # After sorting, this may not be index 0 anymore
        assert encounter.round_number == 1
        
        # Verify the initiative order is correct (highest first)
        expected_order = ["Rogue", "Fighter", "Wizard", "Goblin"]  # 20, 18, 15, 12
        actual_order = [c.name for c in encounter.combatants]
        assert actual_order == expected_order
        
        # The current combatant should be valid
        current_combatant = encounter.get_current_combatant()
        assert current_combatant is not None
        assert current_combatant.name in expected_order
    
    def test_next_turn_advancement(self, encounter):
        """Test advancing through turns in correct order."""
        # Reset to a known state - start with highest initiative combatant
        encounter.current_turn = 0
        encounter.round_number = 1
        
        # Expected order: Rogue(20), Fighter(18), Wizard(15), Goblin(12)
        expected_order = ["Rogue", "Fighter", "Wizard", "Goblin"]
        
        # Verify we start with Rogue (highest initiative)
        assert encounter.get_current_combatant().name == "Rogue"
        assert encounter.round_number == 1
        
        # Advance to Fighter's turn (initiative 18)
        next_combatant = encounter.next_turn()
        assert encounter.current_turn == 1
        assert encounter.round_number == 1
        assert next_combatant.name == "Fighter"
        assert encounter.get_current_combatant().name == "Fighter"
        
        # Advance to Wizard's turn (initiative 15)
        next_combatant = encounter.next_turn()
        assert encounter.current_turn == 2
        assert encounter.round_number == 1
        assert next_combatant.name == "Wizard"
        
        # Advance to Goblin's turn (initiative 12)
        next_combatant = encounter.next_turn()
        assert encounter.current_turn == 3
        assert encounter.round_number == 1
        assert next_combatant.name == "Goblin"
        
        # Advance to next round - back to Rogue
        next_combatant = encounter.next_turn()
        assert encounter.current_turn == 0
        assert encounter.round_number == 2
        assert next_combatant.name == "Rogue"
    
    def test_turn_advancement_with_initiative_changes(self, encounter):
        """Test that turn tracking works correctly when initiative changes."""
        # Start with Rogue's turn
        assert encounter.get_current_combatant().name == "Rogue"
        
        # Change Goblin's initiative to be highest
        encounter.adjust_initiative("Goblin", 25)
        
        # Current combatant should still be Rogue, but at different index
        current_combatant = encounter.get_current_combatant()
        assert current_combatant.name == "Rogue"
        assert encounter.current_turn == 1  # Rogue moved to index 1
        
        # Advance turn - should go to Fighter (now at index 2)
        next_combatant = encounter.next_turn()
        assert next_combatant.name == "Fighter"
        assert encounter.current_turn == 2
    
    def test_turn_advancement_with_combatant_removal(self, encounter):
        """Test turn tracking when combatants are removed."""
        # Set current turn to Fighter (index 1 in sorted order: Rogue, Fighter, Wizard, Goblin)
        encounter.current_turn = 1
        assert encounter.get_current_combatant().name == "Fighter"
        
        # Remove Rogue (index 0) - Fighter should now be at index 0
        encounter.remove_combatant("Rogue")
        # The current turn should still point to Fighter, now at index 0
        assert encounter.get_current_combatant().name == "Fighter"
        assert encounter.current_turn == 0
        
        # Remove Fighter (current combatant) - should adjust to stay within bounds
        encounter.remove_combatant("Fighter")
        # After removing Fighter, we should have Wizard and Goblin left
        # current_turn should be adjusted to 0 (first available combatant)
        assert encounter.current_turn == 0
        assert encounter.get_current_combatant().name == "Wizard"
    
    def test_turn_advancement_single_combatant(self):
        """Test turn advancement with only one combatant."""
        encounter = Encounter(name="Solo Combat")
        solo = Combatant(name="Solo", max_hp=20, current_hp=20, initiative=15)
        encounter.add_combatant(solo)
        
        # Should start at turn 0, round 1
        assert encounter.current_turn == 0
        assert encounter.round_number == 1
        assert encounter.get_current_combatant().name == "Solo"
        
        # Advancing turn should increment round but stay on same combatant
        next_combatant = encounter.next_turn()
        assert encounter.current_turn == 0
        assert encounter.round_number == 2
        assert next_combatant.name == "Solo"
    
    def test_turn_advancement_empty_encounter(self):
        """Test turn advancement with no combatants."""
        encounter = Encounter(name="Empty Combat")
        
        result = encounter.next_turn()
        assert result is None
        assert encounter.current_turn == 0
        assert encounter.round_number == 1
    
    def test_get_current_combatant_edge_cases(self):
        """Test getting current combatant in edge cases."""
        encounter = Encounter(name="Edge Case Test")
        
        # No combatants
        assert encounter.get_current_combatant() is None
        
        # Add combatant
        combatant = Combatant(name="Test", max_hp=10, current_hp=10, initiative=10)
        encounter.add_combatant(combatant)
        
        # Valid current turn
        assert encounter.get_current_combatant() == combatant
        
        # Invalid current turn (beyond combatant count)
        encounter.current_turn = 5
        assert encounter.get_current_combatant() is None


class TestCombatFlow:
    """Test complete combat flow scenarios."""
    
    @pytest.fixture
    def service(self):
        """Create encounter service with mock data manager."""
        mock_data_manager = Mock(spec=DataManager)
        return EncounterService(mock_data_manager)
    
    @pytest.fixture
    def combat_encounter(self, service):
        """Create a combat encounter with multiple combatants."""
        encounter = service.create_encounter("Epic Battle")
        
        # Add party members
        service.add_combatant("Paladin", 60, 16, "player")
        service.add_combatant("Ranger", 45, 18, "player")
        service.add_combatant("Cleric", 40, 14, "player")
        
        # Add monsters
        service.add_combatant("Orc Chief", 50, 15, "monster")
        service.add_combatant("Orc Warrior", 30, 13, "monster")
        service.add_combatant("Orc Archer", 25, 17, "monster")
        
        return service.get_current_encounter()
    
    def test_complete_combat_round(self, service, combat_encounter):
        """Test a complete round of combat."""
        # Expected initiative order: Ranger(18), Orc Archer(17), Paladin(16), Orc Chief(15), Cleric(14), Orc Warrior(13)
        expected_order = ["Ranger", "Orc Archer", "Paladin", "Orc Chief", "Cleric", "Orc Warrior"]
        
        # Reset to known state - start at beginning of initiative order
        combat_encounter.current_turn = 0
        combat_encounter.round_number = 1
        
        # Verify initial state
        assert combat_encounter.round_number == 1
        assert combat_encounter.get_current_combatant().name == expected_order[0]
        
        # Go through complete round
        for i, expected_name in enumerate(expected_order):
            current = service.get_current_combatant()
            assert current.name == expected_name
            assert combat_encounter.current_turn == i
            assert combat_encounter.round_number == 1
            
            if i < len(expected_order) - 1:  # Don't advance after last combatant
                service.next_turn()
        
        # Advance to next round
        next_combatant = service.next_turn()
        assert combat_encounter.round_number == 2
        assert combat_encounter.current_turn == 0
        assert next_combatant.name == expected_order[0]
    
    def test_combat_with_casualties(self, service, combat_encounter):
        """Test combat flow when combatants are defeated."""
        # Reset to known state - start with highest initiative
        combat_encounter.current_turn = 0
        
        # Start combat
        assert service.get_current_combatant().name == "Ranger"
        
        # Ranger's turn - attack Orc Warrior
        service.update_hp("Orc Warrior", "0")  # Orc Warrior dies
        service.next_turn()
        
        # Orc Archer's turn
        assert service.get_current_combatant().name == "Orc Archer"
        service.next_turn()
        
        # Continue through round
        assert service.get_current_combatant().name == "Paladin"
        service.next_turn()
        assert service.get_current_combatant().name == "Orc Chief"
        service.next_turn()
        assert service.get_current_combatant().name == "Cleric"
        service.next_turn()
        
        # Next turn should be Orc Warrior (even though dead), then round 2
        assert service.get_current_combatant().name == "Orc Warrior"
        service.next_turn()  # This advances to round 2
        assert combat_encounter.round_number == 2
        assert service.get_current_combatant().name == "Ranger"
        
        # Remove dead combatant
        service.remove_combatant("Orc Warrior")
        
        # Verify turn order is maintained
        expected_remaining = ["Ranger", "Orc Archer", "Paladin", "Orc Chief", "Cleric"]
        for expected_name in expected_remaining:
            current = service.get_current_combatant()
            assert current.name == expected_name
            service.next_turn()
        
        # Should be back to round 3, Ranger's turn
        assert combat_encounter.round_number == 3
        assert service.get_current_combatant().name == "Ranger"
    
    def test_combat_with_initiative_changes_mid_combat(self, service, combat_encounter):
        """Test combat flow when initiative changes during combat."""
        # Initial order: Ranger(18), Orc Archer(17), Paladin(16), Orc Chief(15), Cleric(14), Orc Warrior(13)
        
        # Reset to known state - start with highest initiative
        combat_encounter.current_turn = 0
        
        # Start with Ranger's turn
        assert service.get_current_combatant().name == "Ranger"
        
        # Cleric casts a spell that boosts Paladin's initiative
        service.adjust_initiative("Paladin", 20)
        
        # Current combatant should still be Ranger, but order has changed
        # New order: Paladin(20), Ranger(18), Orc Archer(17), Orc Chief(15), Cleric(14), Orc Warrior(13)
        assert service.get_current_combatant().name == "Ranger"
        assert combat_encounter.current_turn == 1  # Ranger moved to index 1
        
        # Advance turn - should go to Orc Archer
        service.next_turn()
        assert service.get_current_combatant().name == "Orc Archer"
        
        # Continue through modified turn order
        service.next_turn()
        assert service.get_current_combatant().name == "Orc Chief"
        
        service.next_turn()
        assert service.get_current_combatant().name == "Cleric"
        
        service.next_turn()
        assert service.get_current_combatant().name == "Orc Warrior"
        
        # Next turn should start new round with Paladin (now highest initiative)
        service.next_turn()
        assert combat_encounter.round_number == 2
        assert service.get_current_combatant().name == "Paladin"


class TestTurnPersistence:
    """Test that turn state is properly saved and loaded."""
    
    @pytest.fixture
    def temp_data_manager(self, tmp_path):
        """Create a DataManager with temporary directory."""
        return DataManager(str(tmp_path))
    
    @pytest.fixture
    def service_with_temp_data(self, temp_data_manager):
        """Create encounter service with temporary data manager."""
        return EncounterService(temp_data_manager)
    
    def test_save_and_load_turn_state(self, service_with_temp_data):
        """Test that turn state is preserved when saving and loading."""
        service = service_with_temp_data
        
        # Create encounter with combatants
        encounter = service.create_encounter("Turn Persistence Test")
        service.add_combatant("Alpha", 30, 15, "player")
        service.add_combatant("Beta", 25, 18, "monster")
        service.add_combatant("Gamma", 20, 12, "npc")
        
        # Reset to known state and advance through turns
        encounter.current_turn = 0  # Start with Beta (highest initiative: 18)
        encounter.round_number = 1
        
        # Advance to specific turn and round
        service.next_turn()  # Alpha's turn (init 15)
        service.next_turn()  # Gamma's turn (init 12)
        service.next_turn()  # Back to Beta, round 2
        
        # Verify state before saving
        encounter = service.get_current_encounter()
        assert encounter.current_turn == 0
        assert encounter.round_number == 2
        assert service.get_current_combatant().name == "Beta"  # Highest initiative
        
        # Save encounter
        service.save_encounter("turn_test")
        
        # Create new service and load encounter
        new_service = EncounterService(service.data_manager)
        loaded_encounter = new_service.load_encounter("turn_test")
        
        # Verify turn state is preserved
        assert loaded_encounter.current_turn == 0
        assert loaded_encounter.round_number == 2
        assert new_service.get_current_combatant().name == "Beta"
        
        # Verify we can continue combat from saved state
        new_service.next_turn()
        assert new_service.get_current_combatant().name == "Alpha"
        assert loaded_encounter.current_turn == 1
        assert loaded_encounter.round_number == 2
    
    def test_save_and_load_mid_combat_with_damage(self, service_with_temp_data):
        """Test saving and loading encounter with damage and turn state."""
        service = service_with_temp_data
        
        # Create combat scenario
        encounter = service.create_encounter("Mid Combat Save")
        service.add_combatant("Hero", 50, 16, "player")
        service.add_combatant("Villain", 40, 14, "monster")
        
        # Simulate some combat
        service.update_hp("Hero", "-10")  # Hero takes damage
        service.add_note("Hero", "Poisoned")
        service.next_turn()  # Villain's turn
        service.update_hp("Villain", "-15")  # Villain takes damage
        service.next_turn()  # Back to Hero, round 2
        
        # Verify state before saving
        encounter = service.get_current_encounter()
        assert encounter.round_number == 2
        assert service.get_current_combatant().name == "Hero"
        hero = service.get_combatant("Hero")
        villain = service.get_combatant("Villain")
        assert hero.current_hp == 40
        assert villain.current_hp == 25
        assert "Poisoned" in hero.notes
        
        # Save and reload
        service.save_encounter("mid_combat")
        new_service = EncounterService(service.data_manager)
        loaded_encounter = new_service.load_encounter("mid_combat")
        
        # Verify all state is preserved
        assert loaded_encounter.round_number == 2
        assert new_service.get_current_combatant().name == "Hero"
        
        loaded_hero = new_service.get_combatant("Hero")
        loaded_villain = new_service.get_combatant("Villain")
        assert loaded_hero.current_hp == 40
        assert loaded_villain.current_hp == 25
        assert "Poisoned" in loaded_hero.notes


class TestTurnManagementCLI:
    """Test CLI commands for turn management."""
    
    @pytest.fixture
    def mock_service(self):
        """Create mock encounter service."""
        return Mock(spec=EncounterService)
    
    @pytest.fixture
    def mock_display(self):
        """Create mock display manager."""
        return Mock(spec=DisplayManager)
    
    @pytest.fixture
    def command_handler(self, mock_service, mock_display):
        """Create command handler with mocks."""
        return CommandHandler(mock_service, mock_display)
    
    def test_next_command_success(self, command_handler, mock_service, mock_display):
        """Test successful next turn command."""
        # Setup mocks
        mock_combatant = Mock()
        mock_combatant.name = "Test Combatant"
        mock_encounter = Mock()
        mock_encounter.round_number = 2
        mock_encounter.current_turn = 1
        mock_encounter.combatants = [mock_combatant]
        
        mock_service.next_turn.return_value = mock_combatant
        mock_service.get_current_encounter.return_value = mock_encounter
        mock_display.show_initiative_order.return_value = "Initiative order display"
        
        # Create args
        args = Mock()
        args.command = 'next'
        
        # Execute command
        result = command_handler._handle_next(args)
        
        # Verify calls
        mock_service.next_turn.assert_called_once()
        mock_service.get_current_encounter.assert_called_once()
        mock_display.show_initiative_order.assert_called_once_with(
            mock_encounter.combatants, mock_encounter.current_turn
        )
        
        assert result == 0
    
    def test_next_command_no_encounter(self, command_handler, mock_service):
        """Test next turn command when no encounter is loaded."""
        mock_service.next_turn.side_effect = EncounterNotLoadedError("advance to next turn")
        
        args = Mock()
        args.command = 'next'
        
        with pytest.raises(EncounterNotLoadedError):
            command_handler._handle_next(args)
    
    def test_next_command_no_combatants(self, command_handler, mock_service, mock_display):
        """Test next turn command when encounter has no combatants."""
        mock_service.next_turn.return_value = None
        mock_encounter = Mock()
        mock_encounter.has_combatants.return_value = False
        mock_service.get_current_encounter.return_value = mock_encounter
        
        args = Mock()
        args.command = 'next'
        
        result = command_handler._handle_next(args)
        
        mock_service.next_turn.assert_called_once()
        assert result == 0


class TestTurnManagementIntegration:
    """Integration tests for turn management across all layers."""
    
    @pytest.fixture
    def temp_service(self, tmp_path):
        """Create service with temporary data directory."""
        data_manager = DataManager(str(tmp_path))
        return EncounterService(data_manager)
    
    def test_full_combat_scenario(self, temp_service):
        """Test a complete combat scenario from start to finish."""
        service = temp_service
        
        # Setup encounter
        encounter = service.create_encounter("Integration Test Combat")
        service.add_combatant("Fighter", 45, 17, "player")
        service.add_combatant("Wizard", 30, 14, "player")
        service.add_combatant("Orc", 25, 15, "monster")
        service.add_combatant("Goblin", 15, 12, "monster")
        
        # Expected order: Fighter(17), Orc(15), Wizard(14), Goblin(12)
        
        # Reset to known state - start with highest initiative
        encounter.current_turn = 0
        encounter.round_number = 1
        
        # Round 1
        assert service.get_current_combatant().name == "Fighter"
        service.add_note("Fighter", "Action Surge available")
        service.next_turn()
        
        assert service.get_current_combatant().name == "Orc"
        service.update_hp("Fighter", "-8")  # Orc attacks Fighter
        service.next_turn()
        
        assert service.get_current_combatant().name == "Wizard"
        service.update_hp("Orc", "-12")  # Wizard casts spell
        service.add_note("Wizard", "Spell slot used")
        service.next_turn()
        
        assert service.get_current_combatant().name == "Goblin"
        service.update_hp("Wizard", "-5")  # Goblin attacks Wizard
        service.next_turn()
        
        # Round 2
        encounter = service.get_current_encounter()
        assert encounter.round_number == 2
        assert service.get_current_combatant().name == "Fighter"
        
        # Save mid-combat
        service.save_encounter("integration_test")
        
        # Load and continue
        loaded_encounter = service.load_encounter("integration_test")
        assert service.get_current_combatant().name == "Fighter"
        assert loaded_encounter.round_number == 2
        
        # Verify damage and notes persisted
        fighter = service.get_combatant("Fighter")
        wizard = service.get_combatant("Wizard")
        orc = service.get_combatant("Orc")
        
        assert fighter.current_hp == 37  # 45 - 8
        assert wizard.current_hp == 25   # 30 - 5
        assert orc.current_hp == 13      # 25 - 12
        assert "Action Surge available" in fighter.notes
        assert "Spell slot used" in wizard.notes
        
        # Finish combat
        service.update_hp("Orc", "0")     # Fighter kills Orc
        service.remove_combatant("Orc")
        service.next_turn()
        
        # Continue with remaining combatants
        assert service.get_current_combatant().name == "Wizard"
        service.next_turn()
        assert service.get_current_combatant().name == "Goblin"
        service.next_turn()
        
        # Round 3 with only 3 combatants
        current_encounter = service.get_current_encounter()
        assert current_encounter.round_number == 3
        assert service.get_current_combatant().name == "Fighter"