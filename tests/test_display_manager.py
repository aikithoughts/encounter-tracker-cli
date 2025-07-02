"""Test cases for DisplayManager output formatting and display logic."""

import pytest
from dnd_encounter_tracker.cli.display import DisplayManager
from dnd_encounter_tracker.core.models import Combatant, Encounter


class TestDisplayManager:
    """Test cases for DisplayManager display and formatting functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.display = DisplayManager()
        self.encounter = Encounter(name="Test Encounter")
        
        # Create test combatants with various states
        self.hero = Combatant(name="Hero", max_hp=20, current_hp=15, initiative=18, combatant_type="player")
        self.goblin = Combatant(name="Goblin", max_hp=10, current_hp=3, initiative=12, combatant_type="monster")
        self.orc = Combatant(name="Orc", max_hp=15, current_hp=0, initiative=10, combatant_type="monster")
        self.wizard = Combatant(name="Wizard", max_hp=12, current_hp=12, initiative=16, combatant_type="player")
        
        # Add notes to some combatants
        self.hero.add_note("Blessed by cleric")
        self.hero.add_note("Has inspiration")
        self.goblin.add_note("Poisoned")
        
        # Add combatants to encounter
        self.encounter.add_combatant(self.hero)
        self.encounter.add_combatant(self.wizard)
        self.encounter.add_combatant(self.goblin)
        self.encounter.add_combatant(self.orc)
        
        # Set current turn
        self.encounter.current_turn = 0
        self.encounter.round_number = 2


class TestEncounterSummaryDisplay:
    """Test encounter summary display functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.display = DisplayManager()
        self.encounter = Encounter(name="Goblin Ambush")
        
        self.hero = Combatant(name="Hero", max_hp=20, current_hp=15, initiative=18, combatant_type="player")
        self.goblin = Combatant(name="Goblin", max_hp=10, current_hp=2, initiative=12, combatant_type="monster")  # 2/10 = 20% (critical)
        self.orc = Combatant(name="Orc", max_hp=15, current_hp=0, initiative=10, combatant_type="monster")
        
        self.hero.add_note("Blessed")
        self.goblin.add_note("Poisoned")
        
        # Add combatants to encounter (this will automatically sort by initiative)
        self.encounter.add_combatant(self.hero)
        self.encounter.add_combatant(self.goblin)
        self.encounter.add_combatant(self.orc)
        self.encounter.current_turn = 0
        self.encounter.round_number = 3
    
    def test_encounter_summary_basic_format(self):
        """Test basic encounter summary formatting."""
        summary = self.display.show_encounter_summary(self.encounter)
        
        # Check header information
        assert "Encounter: Goblin Ambush" in summary
        assert "Round: 3" in summary
        assert "Initiative Order:" in summary
    
    def test_encounter_summary_current_turn_indication(self):
        """Test that current turn is clearly indicated (Requirement 2.4)."""
        summary = self.display.show_encounter_summary(self.encounter)
        lines = summary.split('\n')
        
        # Find the hero line (current turn)
        hero_line = next(line for line in lines if "Hero" in line)
        assert ">>>" in hero_line, "Current turn should be marked with >>>"
        
        # Find other combatant lines (not current turn)
        goblin_line = next(line for line in lines if "Goblin" in line)
        orc_line = next(line for line in lines if "Orc" in line)
        
        assert ">>>" not in goblin_line, "Non-current turn should not have >>> marker"
        assert ">>>" not in orc_line, "Non-current turn should not have >>> marker"
    
    def test_encounter_summary_note_indicators(self):
        """Test that combatants with notes are clearly indicated (Requirement 4.5)."""
        summary = self.display.show_encounter_summary(self.encounter)
        lines = summary.split('\n')
        
        # Find combatant lines (skip header lines)
        combatant_lines = [line for line in lines if "|" in line and any(name in line for name in ["Hero", "Goblin", "Orc"])]
        
        hero_line = next(line for line in combatant_lines if "Hero" in line)
        goblin_line = next(line for line in combatant_lines if "Goblin" in line)
        orc_line = next(line for line in combatant_lines if "Orc" in line)
        
        # Check note indicators
        assert "📝" in hero_line, "Hero should have note indicator"
        assert "📝" in goblin_line, "Goblin should have note indicator"
        assert "📝" not in orc_line, "Orc should not have note indicator"
    
    def test_encounter_summary_hp_display(self):
        """Test hit point display formatting."""
        summary = self.display.show_encounter_summary(self.encounter)
        lines = summary.split('\n')
        
        # Find combatant lines (skip header lines)
        combatant_lines = [line for line in lines if "|" in line and any(name in line for name in ["Hero", "Goblin", "Orc"])]
        
        hero_line = next(line for line in combatant_lines if "Hero" in line)
        goblin_line = next(line for line in combatant_lines if "Goblin" in line)
        orc_line = next(line for line in combatant_lines if "Orc" in line)
        
        assert "15/20" in hero_line, "Hero HP should show current/max"
        assert "2/10" in goblin_line, "Goblin HP should show current/max"
        assert "0/15" in orc_line, "Orc HP should show current/max"
        assert "(DEAD)" in orc_line, "Dead combatant should be marked"
        assert "(CRITICAL)" in goblin_line, "Critical HP should be marked"
    
    def test_encounter_summary_initiative_order(self):
        """Test that combatants are displayed in initiative order."""
        summary = self.display.show_encounter_summary(self.encounter)
        lines = summary.split('\n')
        
        # Find combatant lines (skip header lines)
        combatant_lines = [line for line in lines if "|" in line and any(name in line for name in ["Hero", "Goblin", "Orc"])]
        
        # Check initiative order (Hero: 18, Goblin: 12, Orc: 10)
        assert "Hero" in combatant_lines[0], "Hero should be first (highest initiative)"
        assert "Goblin" in combatant_lines[1], "Goblin should be second"
        assert "Orc" in combatant_lines[2], "Orc should be third (lowest initiative)"
    
    def test_encounter_summary_combatant_types(self):
        """Test that combatant types are displayed."""
        summary = self.display.show_encounter_summary(self.encounter)
        
        assert "Player" in summary, "Player type should be displayed"
        assert "Monster" in summary, "Monster type should be displayed"
    
    def test_encounter_summary_empty_encounter(self):
        """Test encounter summary with no combatants."""
        empty_encounter = Encounter(name="Empty Encounter")
        summary = self.display.show_encounter_summary(empty_encounter)
        
        assert "Encounter: Empty Encounter" in summary
        assert "No combatants in encounter." in summary


class TestCombatantDetailsDisplay:
    """Test combatant details display functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.display = DisplayManager()
        
        # Create combatants with different states
        self.healthy_combatant = Combatant(name="Healthy", max_hp=20, current_hp=20, initiative=15, combatant_type="player")
        self.injured_combatant = Combatant(name="Injured", max_hp=20, current_hp=5, initiative=12, combatant_type="monster")
        self.dead_combatant = Combatant(name="Dead", max_hp=15, current_hp=0, initiative=10, combatant_type="npc")
        
        # Add notes
        self.healthy_combatant.add_note("Blessed by cleric")
        self.healthy_combatant.add_note("Has inspiration")
        self.injured_combatant.add_note("Poisoned")
    
    def test_combatant_details_basic_format(self):
        """Test basic combatant details formatting."""
        details = self.display.show_combatant_details(self.healthy_combatant)
        
        assert "=== Healthy ===" in details
        assert "Type: Player" in details
        assert "Initiative: 15" in details
        assert "Hit Points: 20/20" in details
    
    def test_combatant_details_status_display(self):
        """Test status display for different HP states."""
        # Healthy combatant
        healthy_details = self.display.show_combatant_details(self.healthy_combatant)
        assert "Status: Alive" in healthy_details
        
        # Injured combatant (critical HP)
        injured_details = self.display.show_combatant_details(self.injured_combatant)
        assert "Status: CRITICAL" in injured_details
        
        # Dead combatant
        dead_details = self.display.show_combatant_details(self.dead_combatant)
        assert "Status: DEAD" in dead_details
    
    def test_combatant_details_notes_display(self):
        """Test notes display in combatant details."""
        # Combatant with notes
        details_with_notes = self.display.show_combatant_details(self.healthy_combatant)
        assert "Notes:" in details_with_notes
        assert "1. Blessed by cleric" in details_with_notes
        assert "2. Has inspiration" in details_with_notes
        
        # Combatant without notes
        details_without_notes = self.display.show_combatant_details(self.dead_combatant)
        assert "Notes: None" in details_without_notes


class TestInitiativeOrderDisplay:
    """Test initiative order display functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.display = DisplayManager()
        
        self.combatants = [
            Combatant(name="Fast", max_hp=20, current_hp=20, initiative=20),
            Combatant(name="Medium", max_hp=15, current_hp=10, initiative=15),
            Combatant(name="Slow", max_hp=10, current_hp=5, initiative=10)
        ]
        
        # Add notes to some
        self.combatants[0].add_note("Hasted")
        self.combatants[2].add_note("Slowed")
    
    def test_initiative_order_basic_display(self):
        """Test basic initiative order display."""
        order = self.display.show_initiative_order(self.combatants)
        
        assert "Initiative Order:" in order
        assert "Fast" in order
        assert "Medium" in order
        assert "Slow" in order
    
    def test_initiative_order_with_current_turn(self):
        """Test initiative order with current turn indication."""
        order = self.display.show_initiative_order(self.combatants, current_turn=1)
        lines = order.split('\n')
        
        # Find combatant lines
        fast_line = next(line for line in lines if "Fast" in line)
        medium_line = next(line for line in lines if "Medium" in line)
        slow_line = next(line for line in lines if "Slow" in line)
        
        # Check turn markers
        assert ">>>" not in fast_line, "Fast should not have turn marker"
        assert ">>>" in medium_line, "Medium should have turn marker (current turn)"
        assert ">>>" not in slow_line, "Slow should not have turn marker"
    
    def test_initiative_order_note_indicators(self):
        """Test note indicators in initiative order."""
        order = self.display.show_initiative_order(self.combatants)
        lines = order.split('\n')
        
        fast_line = next(line for line in lines if "Fast" in line)
        medium_line = next(line for line in lines if "Medium" in line)
        slow_line = next(line for line in lines if "Slow" in line)
        
        assert "📝" in fast_line, "Fast should have note indicator"
        assert "📝" not in medium_line, "Medium should not have note indicator"
        assert "📝" in slow_line, "Slow should have note indicator"
    
    def test_initiative_order_empty_list(self):
        """Test initiative order with empty combatant list."""
        order = self.display.show_initiative_order([])
        assert "No combatants to display." in order


class TestNotesDisplay:
    """Test notes-specific display functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.display = DisplayManager()
        self.encounter = Encounter(name="Notes Test")
        
        self.combatant_with_notes = Combatant(name="Noted", max_hp=20, current_hp=20, initiative=15)
        self.combatant_without_notes = Combatant(name="Plain", max_hp=15, current_hp=15, initiative=12)
        
        self.combatant_with_notes.add_note("First note")
        self.combatant_with_notes.add_note("Second note")
        self.combatant_with_notes.add_note("Third note")
        
        self.encounter.add_combatant(self.combatant_with_notes)
        self.encounter.add_combatant(self.combatant_without_notes)
    
    def test_show_notes_list_with_notes(self):
        """Test displaying notes list for combatant with notes."""
        notes_display = self.display.show_notes_list(self.combatant_with_notes)
        
        assert "Notes for Noted:" in notes_display
        assert "1. First note" in notes_display
        assert "2. Second note" in notes_display
        assert "3. Third note" in notes_display
    
    def test_show_notes_list_without_notes(self):
        """Test displaying notes list for combatant without notes."""
        notes_display = self.display.show_notes_list(self.combatant_without_notes)
        assert "Plain has no notes." in notes_display
    
    def test_show_combatants_with_notes(self):
        """Test displaying all combatants that have notes."""
        display = self.display.show_combatants_with_notes(self.encounter)
        
        assert "Combatants with notes:" in display
        assert "• Noted (3 notes)" in display
        assert "Plain" not in display
    
    def test_show_combatants_with_notes_empty(self):
        """Test displaying combatants with notes when none have notes."""
        empty_encounter = Encounter(name="Empty Notes")
        empty_encounter.add_combatant(self.combatant_without_notes)
        
        display = self.display.show_combatants_with_notes(empty_encounter)
        assert "No combatants have notes." in display


class TestHelpDisplay:
    """Test help and documentation display functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.display = DisplayManager()
    
    def test_note_management_help_format(self):
        """Test note management help formatting (Requirement 7.1)."""
        help_text = self.display.format_note_management_help()
        
        # Check that help contains clear command documentation
        assert "Note Management Commands:" in help_text
        assert "note add" in help_text
        assert "note list" in help_text
        assert "note edit" in help_text
        assert "note remove" in help_text
        assert "note show" in help_text
        
        # Check examples are provided
        assert "Examples:" in help_text
        assert "note add Thorin" in help_text
        assert "note list Thorin" in help_text
        
        # Check explanatory text
        assert "Indices are 1-based" in help_text


class TestDisplayFormatting:
    """Test display formatting and alignment."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.display = DisplayManager()
        
        # Create combatants with varying name lengths
        self.short_name = Combatant(name="A", max_hp=10, current_hp=5, initiative=20)
        self.long_name = Combatant(name="VeryLongCombatantName", max_hp=25, current_hp=12, initiative=15)
        self.medium_name = Combatant(name="Medium", max_hp=15, current_hp=15, initiative=10)
        
        self.encounter = Encounter(name="Format Test")
        self.encounter.add_combatant(self.short_name)
        self.encounter.add_combatant(self.long_name)
        self.encounter.add_combatant(self.medium_name)
    
    def test_encounter_summary_formatting_consistency(self):
        """Test that encounter summary maintains consistent formatting."""
        summary = self.display.show_encounter_summary(self.encounter)
        lines = summary.split('\n')
        
        # Find combatant lines
        combatant_lines = [line for line in lines if any(name in line for name in ["A", "VeryLong", "Medium"])]
        
        # Check that all lines have consistent structure
        for line in combatant_lines:
            assert "|" in line, "Each combatant line should have pipe separators"
            assert "HP:" in line, "Each combatant line should show HP"
            parts = line.split("|")
            assert len(parts) >= 3, "Each line should have at least 3 parts separated by pipes"
    
    def test_initiative_order_formatting_consistency(self):
        """Test that initiative order maintains consistent formatting."""
        order = self.display.show_initiative_order([self.short_name, self.long_name, self.medium_name])
        lines = order.split('\n')
        
        # Skip header line
        combatant_lines = [line for line in lines[1:] if line.strip()]
        
        # Check formatting consistency
        for line in combatant_lines:
            assert "|" in line, "Each line should have pipe separators"
            assert "HP:" in line, "Each line should show HP"


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.display = DisplayManager()
    
    def test_display_with_special_characters_in_names(self):
        """Test display with special characters in combatant names."""
        special_combatant = Combatant(name="Troll's Bane", max_hp=20, current_hp=15, initiative=12)
        special_combatant.add_note("Has a 'magic' sword")
        
        details = self.display.show_combatant_details(special_combatant)
        assert "=== Troll's Bane ===" in details
        assert "Has a 'magic' sword" in details
    
    def test_display_with_very_long_notes(self):
        """Test display with very long notes."""
        combatant = Combatant(name="Verbose", max_hp=20, current_hp=20, initiative=15)
        long_note = "This is a very long note that contains a lot of information about the combatant's current status, including multiple status effects, spell durations, and tactical considerations that the DM needs to track."
        combatant.add_note(long_note)
        
        details = self.display.show_combatant_details(combatant)
        assert long_note in details
        
        notes_list = self.display.show_notes_list(combatant)
        assert long_note in notes_list
    
    def test_display_with_zero_initiative(self):
        """Test display with zero or negative initiative values."""
        zero_init = Combatant(name="Slow", max_hp=10, current_hp=10, initiative=0)
        encounter = Encounter(name="Edge Case")
        encounter.add_combatant(zero_init)
        
        summary = self.display.show_encounter_summary(encounter)
        assert "0 |" in summary or " 0|" in summary  # Initiative should be displayed
    
    def test_display_with_maximum_hp_values(self):
        """Test display with very high HP values."""
        high_hp = Combatant(name="Dragon", max_hp=999, current_hp=500, initiative=20)
        
        details = self.display.show_combatant_details(high_hp)
        assert "500/999" in details
        
        encounter = Encounter(name="High HP Test")
        encounter.add_combatant(high_hp)
        summary = self.display.show_encounter_summary(encounter)
        assert "500/999" in summary