"""Additional edge case tests for HP management system."""

import pytest
from dnd_encounter_tracker.core.models import Combatant
from dnd_encounter_tracker.core.exceptions import InvalidHPValueError


class TestHPEdgeCases:
    """Test edge cases for HP management system."""
    
    def test_update_hp_with_whitespace(self):
        """Test HP updates with various whitespace scenarios."""
        combatant = Combatant(name="Test", max_hp=50, current_hp=30, initiative=10)
        
        # Leading/trailing whitespace
        combatant.update_hp("  25  ")
        assert combatant.current_hp == 25
        
        combatant.update_hp("  +10  ")
        assert combatant.current_hp == 35
        
        combatant.update_hp("  -5  ")
        assert combatant.current_hp == 30
    
    def test_update_hp_zero_values(self):
        """Test HP updates with zero values."""
        combatant = Combatant(name="Test", max_hp=50, current_hp=30, initiative=10)
        
        # Absolute zero
        combatant.update_hp("0")
        assert combatant.current_hp == 0
        
        # Zero addition (no change)
        combatant.current_hp = 25
        combatant.update_hp("+0")
        assert combatant.current_hp == 25
        
        # Zero subtraction (no change)
        combatant.update_hp("-0")
        assert combatant.current_hp == 25
    
    def test_update_hp_large_values(self):
        """Test HP updates with large values."""
        combatant = Combatant(name="Test", max_hp=100, current_hp=50, initiative=10)
        
        # Large absolute value within max
        combatant.update_hp("99")
        assert combatant.current_hp == 99
        
        # Large addition that exceeds max
        combatant.current_hp = 50
        combatant.update_hp("+100")
        assert combatant.current_hp == 100  # Capped at max
        
        # Large subtraction that would go below 0
        combatant.update_hp("-200")
        assert combatant.current_hp == 0  # Capped at 0
    
    def test_update_hp_boundary_conditions(self):
        """Test HP updates at boundary conditions."""
        combatant = Combatant(name="Test", max_hp=50, current_hp=25, initiative=10)
        
        # Exactly at max HP
        combatant.update_hp("50")
        assert combatant.current_hp == 50
        
        # One above max HP (should be capped)
        combatant.update_hp("51")
        assert combatant.current_hp == 50
        
        # Exactly at 0 HP
        combatant.update_hp("0")
        assert combatant.current_hp == 0
        
        # Below 0 HP (should be capped)
        combatant.update_hp("-1")
        assert combatant.current_hp == 0
    
    def test_update_hp_addition_at_max(self):
        """Test addition when already at max HP."""
        combatant = Combatant(name="Test", max_hp=50, current_hp=50, initiative=10)
        
        # Adding to max HP should stay at max
        combatant.update_hp("+1")
        assert combatant.current_hp == 50
        
        combatant.update_hp("+10")
        assert combatant.current_hp == 50
    
    def test_update_hp_subtraction_at_zero(self):
        """Test subtraction when already at 0 HP."""
        combatant = Combatant(name="Test", max_hp=50, current_hp=0, initiative=10)
        
        # Subtracting from 0 HP should stay at 0
        combatant.update_hp("-1")
        assert combatant.current_hp == 0
        
        combatant.update_hp("-10")
        assert combatant.current_hp == 0
    
    def test_update_hp_invalid_formats(self):
        """Test various invalid HP formats."""
        combatant = Combatant(name="Test", max_hp=50, current_hp=30, initiative=10)
        
        # Empty string
        with pytest.raises(InvalidHPValueError, match="HP value cannot be empty"):
            combatant.update_hp("")
        
        # Only whitespace
        with pytest.raises(InvalidHPValueError, match="HP value cannot be empty"):
            combatant.update_hp("   ")
        
        # Non-numeric absolute values
        with pytest.raises(InvalidHPValueError, match="Invalid HP value format"):
            combatant.update_hp("abc")
        
        with pytest.raises(InvalidHPValueError, match="Invalid HP value format"):
            combatant.update_hp("12.5")
        
        with pytest.raises(InvalidHPValueError, match="Invalid HP value format"):
            combatant.update_hp("1a2")
        
        # Invalid relative formats
        with pytest.raises(InvalidHPValueError, match="Invalid HP change format"):
            combatant.update_hp("+abc")
        
        with pytest.raises(InvalidHPValueError, match="Invalid HP change format"):
            combatant.update_hp("-xyz")
        
        with pytest.raises(InvalidHPValueError, match="Invalid HP change format"):
            combatant.update_hp("++5")
        
        with pytest.raises(InvalidHPValueError, match="Invalid HP change format"):
            combatant.update_hp("--5")
        
        with pytest.raises(InvalidHPValueError, match="Invalid HP change format"):
            combatant.update_hp("+-5")
        
        with pytest.raises(InvalidHPValueError, match="Invalid HP change format"):
            combatant.update_hp("-+5")
        
        # Mixed formats
        with pytest.raises(InvalidHPValueError, match="Invalid HP value format"):
            combatant.update_hp("5+")
        
        with pytest.raises(InvalidHPValueError, match="Invalid HP value format"):
            combatant.update_hp("5-")
    
    def test_update_hp_preserves_max_hp(self):
        """Test that HP updates don't affect max HP."""
        combatant = Combatant(name="Test", max_hp=50, current_hp=30, initiative=10)
        original_max = combatant.max_hp
        
        # Various HP updates
        combatant.update_hp("25")
        assert combatant.max_hp == original_max
        
        combatant.update_hp("+10")
        assert combatant.max_hp == original_max
        
        combatant.update_hp("-5")
        assert combatant.max_hp == original_max
        
        combatant.update_hp("0")
        assert combatant.max_hp == original_max
    
    def test_update_hp_sequence(self):
        """Test a sequence of HP updates."""
        combatant = Combatant(name="Test", max_hp=100, current_hp=50, initiative=10)
        
        # Sequence: 50 -> 75 -> 25 -> 30 -> 0 -> 10
        combatant.update_hp("+25")  # 50 + 25 = 75
        assert combatant.current_hp == 75
        
        combatant.update_hp("-50")  # 75 - 50 = 25
        assert combatant.current_hp == 25
        
        combatant.update_hp("+5")   # 25 + 5 = 30
        assert combatant.current_hp == 30
        
        combatant.update_hp("-100") # 30 - 100 = 0 (capped)
        assert combatant.current_hp == 0
        
        combatant.update_hp("10")   # Set to 10
        assert combatant.current_hp == 10
        
        combatant.update_hp("+200") # 10 + 200 = 100 (capped at max)
        assert combatant.current_hp == 100
    
    def test_is_alive_after_hp_updates(self):
        """Test is_alive status after various HP updates."""
        combatant = Combatant(name="Test", max_hp=50, current_hp=25, initiative=10)
        
        # Should be alive initially
        assert combatant.is_alive() is True
        
        # Still alive after damage
        combatant.update_hp("-20")
        assert combatant.current_hp == 5
        assert combatant.is_alive() is True
        
        # Dead after fatal damage
        combatant.update_hp("-10")
        assert combatant.current_hp == 0
        assert combatant.is_alive() is False
        
        # Alive again after healing
        combatant.update_hp("+1")
        assert combatant.current_hp == 1
        assert combatant.is_alive() is True
    
    def test_update_hp_with_single_digit_max(self):
        """Test HP updates with single-digit max HP."""
        combatant = Combatant(name="Test", max_hp=5, current_hp=3, initiative=10)
        
        combatant.update_hp("+1")
        assert combatant.current_hp == 4
        
        combatant.update_hp("+5")  # Should cap at max
        assert combatant.current_hp == 5
        
        combatant.update_hp("-10") # Should cap at 0
        assert combatant.current_hp == 0
    
    def test_update_hp_with_high_max(self):
        """Test HP updates with very high max HP."""
        combatant = Combatant(name="Test", max_hp=999, current_hp=500, initiative=10)
        
        combatant.update_hp("999")
        assert combatant.current_hp == 999
        
        combatant.update_hp("+1")  # Should cap at max
        assert combatant.current_hp == 999
        
        combatant.update_hp("-1000") # Should cap at 0
        assert combatant.current_hp == 0