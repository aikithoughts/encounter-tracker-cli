"""Unit tests for initiative tracking and sorting functionality."""

import pytest
from dnd_encounter_tracker.core.models import Combatant, Encounter
from dnd_encounter_tracker.core.exceptions import ValidationError, CombatantNotFoundError


class TestInitiativeTracking:
    """Test cases for initiative tracking and sorting."""
    
    def test_basic_initiative_sorting(self):
        """Test that combatants are sorted by initiative in descending order."""
        encounter = Encounter(name="Initiative Test")
        
        # Add combatants in random initiative order
        combatants = [
            Combatant(name="Slow", max_hp=10, current_hp=10, initiative=5),
            Combatant(name="Fast", max_hp=10, current_hp=10, initiative=20),
            Combatant(name="Medium", max_hp=10, current_hp=10, initiative=12),
            Combatant(name="Fastest", max_hp=10, current_hp=10, initiative=25),
        ]
        
        for combatant in combatants:
            encounter.add_combatant(combatant)
        
        # Verify sorting (highest initiative first)
        order = encounter.get_initiative_order()
        assert order[0].name == "Fastest"  # 25
        assert order[1].name == "Fast"     # 20
        assert order[2].name == "Medium"   # 12
        assert order[3].name == "Slow"     # 5
    
    def test_initiative_tie_breaking_by_name(self):
        """Test that initiative ties are broken alphabetically by name."""
        encounter = Encounter(name="Tie Test")
        
        # Add combatants with same initiative
        combatants = [
            Combatant(name="Zebra", max_hp=10, current_hp=10, initiative=15),
            Combatant(name="Alpha", max_hp=10, current_hp=10, initiative=15),
            Combatant(name="Beta", max_hp=10, current_hp=10, initiative=15),
        ]
        
        for combatant in combatants:
            encounter.add_combatant(combatant)
        
        # Verify alphabetical tie-breaking
        order = encounter.get_initiative_order()
        assert order[0].name == "Alpha"
        assert order[1].name == "Beta"
        assert order[2].name == "Zebra"
    
    def test_adjust_initiative_basic(self):
        """Test basic initiative adjustment functionality."""
        encounter = Encounter(name="Adjust Test")
        
        combatant1 = Combatant(name="Hero", max_hp=20, current_hp=20, initiative=10)
        combatant2 = Combatant(name="Villain", max_hp=15, current_hp=15, initiative=15)
        
        encounter.add_combatant(combatant1)
        encounter.add_combatant(combatant2)
        
        # Initially Villain should be first (higher initiative)
        assert encounter.combatants[0].name == "Villain"
        assert encounter.combatants[1].name == "Hero"
        
        # Adjust Hero's initiative to be higher
        encounter.adjust_initiative("Hero", 20)
        
        # Now Hero should be first
        assert encounter.combatants[0].name == "Hero"
        assert encounter.combatants[1].name == "Villain"
        assert encounter.get_combatant("Hero").initiative == 20
    
    def test_adjust_initiative_nonexistent_combatant(self):
        """Test that adjusting initiative for nonexistent combatant raises error."""
        encounter = Encounter(name="Error Test")
        
        with pytest.raises(CombatantNotFoundError, match="not found"):
            encounter.adjust_initiative("Nonexistent", 15)
    
    def test_adjust_initiative_maintains_current_turn(self):
        """Test that adjusting initiative maintains current turn tracking."""
        encounter = Encounter(name="Turn Test")
        
        combatant1 = Combatant(name="First", max_hp=10, current_hp=10, initiative=20)
        combatant2 = Combatant(name="Second", max_hp=10, current_hp=10, initiative=15)
        combatant3 = Combatant(name="Third", max_hp=10, current_hp=10, initiative=10)
        
        encounter.add_combatant(combatant1)
        encounter.add_combatant(combatant2)
        encounter.add_combatant(combatant3)
        
        # Set current turn to Second
        encounter.current_turn = 1
        current_combatant = encounter.get_current_combatant()
        assert current_combatant.name == "Second"
        
        # Adjust Third's initiative to be highest
        encounter.adjust_initiative("Third", 25)
        
        # Current turn should still point to Second, but at new index
        current_combatant = encounter.get_current_combatant()
        assert current_combatant.name == "Second"
        
        # Verify new order
        order = encounter.get_initiative_order()
        assert order[0].name == "Third"   # 25
        assert order[1].name == "First"   # 20
        assert order[2].name == "Second"  # 15
    
    def test_manual_reorder_same_initiative(self):
        """Test manual reordering of combatants with same initiative."""
        encounter = Encounter(name="Reorder Test")
        
        # Add combatants with same initiative
        combatants = [
            Combatant(name="Alpha", max_hp=10, current_hp=10, initiative=15),
            Combatant(name="Beta", max_hp=10, current_hp=10, initiative=15),
            Combatant(name="Gamma", max_hp=10, current_hp=10, initiative=15),
        ]
        
        for combatant in combatants:
            encounter.add_combatant(combatant)
        
        # Initially should be alphabetical
        order = encounter.get_initiative_order()
        assert order[0].name == "Alpha"
        assert order[1].name == "Beta"
        assert order[2].name == "Gamma"
        
        # Manually reorder to Gamma, Alpha, Beta
        encounter.reorder_combatants_with_same_initiative(15, ["Gamma", "Alpha", "Beta"])
        
        # Verify new order
        order = encounter.get_initiative_order()
        assert order[0].name == "Gamma"
        assert order[1].name == "Alpha"
        assert order[2].name == "Beta"
    
    def test_manual_reorder_mixed_initiatives(self):
        """Test manual reordering with mixed initiative values."""
        encounter = Encounter(name="Mixed Reorder Test")
        
        combatants = [
            Combatant(name="High1", max_hp=10, current_hp=10, initiative=20),
            Combatant(name="Mid1", max_hp=10, current_hp=10, initiative=15),
            Combatant(name="Mid2", max_hp=10, current_hp=10, initiative=15),
            Combatant(name="Mid3", max_hp=10, current_hp=10, initiative=15),
            Combatant(name="Low1", max_hp=10, current_hp=10, initiative=10),
        ]
        
        for combatant in combatants:
            encounter.add_combatant(combatant)
        
        # Reorder only the initiative 15 group
        encounter.reorder_combatants_with_same_initiative(15, ["Mid3", "Mid1", "Mid2"])
        
        # Verify order: High1, Mid3, Mid1, Mid2, Low1
        order = encounter.get_initiative_order()
        assert order[0].name == "High1"  # 20
        assert order[1].name == "Mid3"   # 15 (manually ordered first)
        assert order[2].name == "Mid1"   # 15 (manually ordered second)
        assert order[3].name == "Mid2"   # 15 (manually ordered third)
        assert order[4].name == "Low1"   # 10
    
    def test_manual_reorder_insufficient_combatants(self):
        """Test error when trying to reorder with insufficient combatants."""
        encounter = Encounter(name="Error Test")
        
        # Only one combatant with initiative 15
        combatant = Combatant(name="Solo", max_hp=10, current_hp=10, initiative=15)
        encounter.add_combatant(combatant)
        
        with pytest.raises(ValidationError, match="Invalid initiative reorder"):
            encounter.reorder_combatants_with_same_initiative(15, ["Solo"])
    
    def test_manual_reorder_name_mismatch(self):
        """Test error when provided names don't match combatants with that initiative."""
        encounter = Encounter(name="Error Test")
        
        combatants = [
            Combatant(name="Alpha", max_hp=10, current_hp=10, initiative=15),
            Combatant(name="Beta", max_hp=10, current_hp=10, initiative=15),
        ]
        
        for combatant in combatants:
            encounter.add_combatant(combatant)
        
        # Missing Beta, extra Gamma
        with pytest.raises(ValidationError, match="Invalid combatant names"):
            encounter.reorder_combatants_with_same_initiative(15, ["Alpha", "Gamma"])
        
        # Missing Alpha
        with pytest.raises(ValidationError, match="Invalid combatant names"):
            encounter.reorder_combatants_with_same_initiative(15, ["Beta"])
        
        # Extra name
        with pytest.raises(ValidationError, match="Invalid combatant names"):
            encounter.reorder_combatants_with_same_initiative(15, ["Alpha", "Beta", "Gamma"])
    
    def test_manual_reorder_maintains_current_turn(self):
        """Test that manual reordering maintains current turn tracking."""
        encounter = Encounter(name="Turn Maintenance Test")
        
        combatants = [
            Combatant(name="Alpha", max_hp=10, current_hp=10, initiative=15),
            Combatant(name="Beta", max_hp=10, current_hp=10, initiative=15),
            Combatant(name="Gamma", max_hp=10, current_hp=10, initiative=15),
        ]
        
        for combatant in combatants:
            encounter.add_combatant(combatant)
        
        # Set current turn to Beta (index 1)
        encounter.current_turn = 1
        current_combatant = encounter.get_current_combatant()
        assert current_combatant.name == "Beta"
        
        # Reorder to put Beta first
        encounter.reorder_combatants_with_same_initiative(15, ["Beta", "Gamma", "Alpha"])
        
        # Current turn should still point to Beta, now at index 0
        current_combatant = encounter.get_current_combatant()
        assert current_combatant.name == "Beta"
        assert encounter.current_turn == 0
    
    def test_get_combatants_by_initiative(self):
        """Test getting combatants filtered by initiative value."""
        encounter = Encounter(name="Filter Test")
        
        combatants = [
            Combatant(name="High1", max_hp=10, current_hp=10, initiative=20),
            Combatant(name="Mid1", max_hp=10, current_hp=10, initiative=15),
            Combatant(name="Mid2", max_hp=10, current_hp=10, initiative=15),
            Combatant(name="Low1", max_hp=10, current_hp=10, initiative=10),
        ]
        
        for combatant in combatants:
            encounter.add_combatant(combatant)
        
        # Test filtering by initiative 15
        mid_combatants = encounter.get_combatants_by_initiative(15)
        assert len(mid_combatants) == 2
        names = {c.name for c in mid_combatants}
        assert names == {"Mid1", "Mid2"}
        
        # Test filtering by initiative 20
        high_combatants = encounter.get_combatants_by_initiative(20)
        assert len(high_combatants) == 1
        assert high_combatants[0].name == "High1"
        
        # Test filtering by nonexistent initiative
        none_combatants = encounter.get_combatants_by_initiative(99)
        assert len(none_combatants) == 0
    
    def test_complex_initiative_scenario(self):
        """Test a complex scenario with multiple initiative adjustments and reorderings."""
        encounter = Encounter(name="Complex Test")
        
        # Create a complex encounter
        combatants = [
            Combatant(name="Rogue", max_hp=25, current_hp=25, initiative=18),
            Combatant(name="Fighter", max_hp=30, current_hp=30, initiative=12),
            Combatant(name="Wizard", max_hp=20, current_hp=20, initiative=14),
            Combatant(name="Goblin1", max_hp=8, current_hp=8, initiative=12),
            Combatant(name="Goblin2", max_hp=8, current_hp=8, initiative=12),
            Combatant(name="Orc", max_hp=15, current_hp=15, initiative=10),
        ]
        
        for combatant in combatants:
            encounter.add_combatant(combatant)
        
        # Initial order should be: Rogue(18), Wizard(14), Fighter(12), Goblin1(12), Goblin2(12), Orc(10)
        order = encounter.get_initiative_order()
        expected_names = ["Rogue", "Wizard", "Fighter", "Goblin1", "Goblin2", "Orc"]
        actual_names = [c.name for c in order]
        assert actual_names == expected_names
        
        # Manually reorder the initiative 12 group: Goblin2, Goblin1, Fighter
        encounter.reorder_combatants_with_same_initiative(12, ["Goblin2", "Goblin1", "Fighter"])
        
        # New order should be: Rogue(18), Wizard(14), Goblin2(12), Goblin1(12), Fighter(12), Orc(10)
        order = encounter.get_initiative_order()
        expected_names = ["Rogue", "Wizard", "Goblin2", "Goblin1", "Fighter", "Orc"]
        actual_names = [c.name for c in order]
        assert actual_names == expected_names
        
        # Adjust Orc's initiative to be highest
        encounter.adjust_initiative("Orc", 25)
        
        # New order should be: Orc(25), Rogue(18), Wizard(14), Goblin2(12), Goblin1(12), Fighter(12)
        order = encounter.get_initiative_order()
        expected_names = ["Orc", "Rogue", "Wizard", "Goblin2", "Goblin1", "Fighter"]
        actual_names = [c.name for c in order]
        assert actual_names == expected_names
        
        # Verify initiative values
        assert encounter.get_combatant("Orc").initiative == 25
        assert encounter.get_combatant("Rogue").initiative == 18
        assert encounter.get_combatant("Wizard").initiative == 14
        assert encounter.get_combatant("Goblin2").initiative == 12
        assert encounter.get_combatant("Goblin1").initiative == 12
        assert encounter.get_combatant("Fighter").initiative == 12


class TestInitiativeEdgeCases:
    """Test edge cases for initiative management."""
    
    def test_negative_initiative_values(self):
        """Test handling of negative initiative values."""
        encounter = Encounter(name="Negative Test")
        
        combatants = [
            Combatant(name="Fast", max_hp=10, current_hp=10, initiative=15),
            Combatant(name="Slow", max_hp=10, current_hp=10, initiative=-5),
            Combatant(name="Normal", max_hp=10, current_hp=10, initiative=10),
        ]
        
        for combatant in combatants:
            encounter.add_combatant(combatant)
        
        # Should sort correctly with negative values
        order = encounter.get_initiative_order()
        assert order[0].name == "Fast"    # 15
        assert order[1].name == "Normal"  # 10
        assert order[2].name == "Slow"    # -5
        
        # Test adjusting to negative value
        encounter.adjust_initiative("Normal", -10)
        
        order = encounter.get_initiative_order()
        assert order[0].name == "Fast"    # 15
        assert order[1].name == "Slow"    # -5
        assert order[2].name == "Normal"  # -10
    
    def test_zero_initiative_values(self):
        """Test handling of zero initiative values."""
        encounter = Encounter(name="Zero Test")
        
        combatants = [
            Combatant(name="Positive", max_hp=10, current_hp=10, initiative=5),
            Combatant(name="Zero1", max_hp=10, current_hp=10, initiative=0),
            Combatant(name="Zero2", max_hp=10, current_hp=10, initiative=0),
            Combatant(name="Negative", max_hp=10, current_hp=10, initiative=-3),
        ]
        
        for combatant in combatants:
            encounter.add_combatant(combatant)
        
        order = encounter.get_initiative_order()
        assert order[0].name == "Positive"  # 5
        assert order[1].name == "Zero1"     # 0 (alphabetical)
        assert order[2].name == "Zero2"     # 0 (alphabetical)
        assert order[3].name == "Negative"  # -3
        
        # Test manual reordering of zero initiative
        encounter.reorder_combatants_with_same_initiative(0, ["Zero2", "Zero1"])
        
        order = encounter.get_initiative_order()
        assert order[0].name == "Positive"  # 5
        assert order[1].name == "Zero2"     # 0 (manually ordered first)
        assert order[2].name == "Zero1"     # 0 (manually ordered second)
        assert order[3].name == "Negative"  # -3
    
    def test_very_large_initiative_values(self):
        """Test handling of very large initiative values."""
        encounter = Encounter(name="Large Test")
        
        combatants = [
            Combatant(name="Normal", max_hp=10, current_hp=10, initiative=15),
            Combatant(name="Huge", max_hp=10, current_hp=10, initiative=999999),
            Combatant(name="Large", max_hp=10, current_hp=10, initiative=1000),
        ]
        
        for combatant in combatants:
            encounter.add_combatant(combatant)
        
        order = encounter.get_initiative_order()
        assert order[0].name == "Huge"    # 999999
        assert order[1].name == "Large"   # 1000
        assert order[2].name == "Normal"  # 15
    
    def test_single_combatant_operations(self):
        """Test initiative operations with single combatant."""
        encounter = Encounter(name="Single Test")
        
        combatant = Combatant(name="Solo", max_hp=10, current_hp=10, initiative=15)
        encounter.add_combatant(combatant)
        
        # Test adjustment
        encounter.adjust_initiative("Solo", 20)
        assert encounter.get_combatant("Solo").initiative == 20
        
        # Test getting by initiative
        solo_list = encounter.get_combatants_by_initiative(20)
        assert len(solo_list) == 1
        assert solo_list[0].name == "Solo"
        
        # Manual reordering should fail with single combatant
        with pytest.raises(ValidationError, match="Invalid initiative reorder"):
            encounter.reorder_combatants_with_same_initiative(20, ["Solo"])
    
    def test_empty_encounter_operations(self):
        """Test initiative operations on empty encounter."""
        encounter = Encounter(name="Empty Test")
        
        # Test getting by initiative
        empty_list = encounter.get_combatants_by_initiative(15)
        assert len(empty_list) == 0
        
        # Test adjustment should fail
        with pytest.raises(CombatantNotFoundError, match="not found"):
            encounter.adjust_initiative("Nonexistent", 15)
        
        # Test manual reordering should fail
        with pytest.raises(ValidationError, match="Invalid initiative reorder"):
            encounter.reorder_combatants_with_same_initiative(15, ["Someone"])