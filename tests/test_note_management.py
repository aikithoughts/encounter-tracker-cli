"""Tests for note management functionality."""

import pytest
from dnd_encounter_tracker.core.models import Combatant, Encounter
from dnd_encounter_tracker.core.note_service import NoteService
from dnd_encounter_tracker.cli.display import DisplayManager
from dnd_encounter_tracker.core.exceptions import ValidationError, CombatantNotFoundError, EncounterNotLoadedError


class TestNoteService:
    """Test cases for NoteService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.encounter = Encounter(name="Test Encounter")
        self.combatant1 = Combatant(name="Hero", max_hp=20, current_hp=20, initiative=15)
        self.combatant2 = Combatant(name="Goblin", max_hp=10, current_hp=10, initiative=12)
        
        self.encounter.add_combatant(self.combatant1)
        self.encounter.add_combatant(self.combatant2)
        
        self.note_service = NoteService(self.encounter)
    
    def test_add_note_success(self):
        """Test successfully adding a note to a combatant."""
        self.note_service.add_note("Hero", "Blessed by cleric")
        
        notes = self.note_service.get_notes("Hero")
        assert len(notes) == 1
        assert notes[0] == "Blessed by cleric"
        assert self.combatant1.has_notes() is True
    
    def test_add_note_combatant_not_found(self):
        """Test adding note to non-existent combatant."""
        with pytest.raises(CombatantNotFoundError, match="Combatant 'Nonexistent' not found"):
            self.note_service.add_note("Nonexistent", "Some note")
    
    def test_add_note_no_encounter(self):
        """Test adding note when no encounter is loaded."""
        service = NoteService()
        
        with pytest.raises(EncounterNotLoadedError, match="add note"):
            service.add_note("Hero", "Some note")
    
    def test_remove_note_success(self):
        """Test successfully removing a note."""
        self.note_service.add_note("Hero", "Note 1")
        self.note_service.add_note("Hero", "Note 2")
        
        self.note_service.remove_note("Hero", 0)  # Remove first note
        
        notes = self.note_service.get_notes("Hero")
        assert len(notes) == 1
        assert notes[0] == "Note 2"
    
    def test_remove_note_invalid_index(self):
        """Test removing note with invalid index."""
        self.note_service.add_note("Hero", "Note 1")
        
        with pytest.raises(ValidationError, match="Invalid note index"):
            self.note_service.remove_note("Hero", 1)
    
    def test_edit_note_success(self):
        """Test successfully editing a note."""
        self.note_service.add_note("Hero", "Original note")
        self.note_service.edit_note("Hero", 0, "Edited note")
        
        notes = self.note_service.get_notes("Hero")
        assert len(notes) == 1
        assert notes[0] == "Edited note"
    
    def test_edit_note_invalid_index(self):
        """Test editing note with invalid index."""
        with pytest.raises(ValidationError, match="Invalid note index"):
            self.note_service.edit_note("Hero", 0, "New note")
    
    def test_get_notes_success(self):
        """Test getting notes for a combatant."""
        self.note_service.add_note("Hero", "Note 1")
        self.note_service.add_note("Hero", "Note 2")
        
        notes = self.note_service.get_notes("Hero")
        assert len(notes) == 2
        assert "Note 1" in notes
        assert "Note 2" in notes
        
        # Should return a copy, not the original list
        notes.append("Modified")
        original_notes = self.note_service.get_notes("Hero")
        assert len(original_notes) == 2
    
    def test_get_combatants_with_notes(self):
        """Test getting combatants that have notes."""
        self.note_service.add_note("Hero", "Hero note")
        
        combatants_with_notes = self.note_service.get_combatants_with_notes()
        assert len(combatants_with_notes) == 1
        assert combatants_with_notes[0].name == "Hero"
    
    def test_clear_all_notes(self):
        """Test clearing all notes for a combatant."""
        self.note_service.add_note("Hero", "Note 1")
        self.note_service.add_note("Hero", "Note 2")
        self.note_service.add_note("Hero", "Note 3")
        
        cleared_count = self.note_service.clear_all_notes("Hero")
        
        assert cleared_count == 3
        assert len(self.note_service.get_notes("Hero")) == 0
        assert self.combatant1.has_notes() is False
    
    def test_search_notes(self):
        """Test searching for notes containing specific terms."""
        self.note_service.add_note("Hero", "Blessed by cleric")
        self.note_service.add_note("Hero", "Has inspiration")
        self.note_service.add_note("Goblin", "Poisoned condition")
        
        # Search for "blessed"
        results = self.note_service.search_notes("blessed")
        assert len(results) == 1
        assert results[0] == ("Hero", 0, "Blessed by cleric")
        
        # Search for "condition"
        results = self.note_service.search_notes("condition")
        assert len(results) == 1
        assert results[0] == ("Goblin", 0, "Poisoned condition")
        
        # Search for non-existent term
        results = self.note_service.search_notes("nonexistent")
        assert len(results) == 0
    
    def test_get_note_statistics(self):
        """Test getting note statistics."""
        self.note_service.add_note("Hero", "Note 1")
        self.note_service.add_note("Hero", "Note 2")
        self.note_service.add_note("Goblin", "Note 3")
        
        stats = self.note_service.get_note_statistics()
        
        assert stats['total_notes'] == 3
        assert stats['total_combatants'] == 2
        assert stats['combatants_with_notes'] == 2
        assert stats['combatants_without_notes'] == 0
        assert stats['max_notes_per_combatant'] == 2
        assert stats['average_notes_per_combatant'] == 1.5
    
    def test_set_encounter(self):
        """Test setting a new encounter."""
        new_encounter = Encounter(name="New Encounter")
        new_combatant = Combatant(name="Wizard", max_hp=15, current_hp=15, initiative=18)
        new_encounter.add_combatant(new_combatant)
        
        self.note_service.set_encounter(new_encounter)
        self.note_service.add_note("Wizard", "Wizard note")
        
        notes = self.note_service.get_notes("Wizard")
        assert len(notes) == 1
        assert notes[0] == "Wizard note"


class TestDisplayManager:
    """Test cases for DisplayManager note-related functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.display = DisplayManager()
        self.encounter = Encounter(name="Test Encounter")
        
        self.combatant1 = Combatant(name="Hero", max_hp=20, current_hp=20, initiative=15)
        self.combatant2 = Combatant(name="Goblin", max_hp=10, current_hp=5, initiative=12)
        self.combatant3 = Combatant(name="Orc", max_hp=15, current_hp=0, initiative=10)
        
        # Add some notes
        self.combatant1.add_note("Blessed by cleric")
        self.combatant1.add_note("Has inspiration")
        self.combatant2.add_note("Poisoned")
        
        self.encounter.add_combatant(self.combatant1)
        self.encounter.add_combatant(self.combatant2)
        self.encounter.add_combatant(self.combatant3)
    
    def test_show_encounter_summary_with_notes(self):
        """Test encounter summary shows note indicators."""
        summary = self.display.show_encounter_summary(self.encounter)
        
        assert "Test Encounter" in summary
        assert "📝" in summary  # Note indicator should be present
        
        # Hero and Goblin should have note indicators, Orc should not
        lines = summary.split('\n')
        hero_line = next(line for line in lines if "Hero" in line)
        goblin_line = next(line for line in lines if "Goblin" in line)
        orc_line = next(line for line in lines if "Orc" in line)
        
        assert "📝" in hero_line
        assert "📝" in goblin_line
        assert "📝" not in orc_line
    
    def test_show_combatant_details_with_notes(self):
        """Test combatant details display includes notes."""
        details = self.display.show_combatant_details(self.combatant1)
        
        assert "=== Hero ===" in details
        assert "Notes:" in details
        assert "1. Blessed by cleric" in details
        assert "2. Has inspiration" in details
    
    def test_show_combatant_details_without_notes(self):
        """Test combatant details for combatant without notes."""
        details = self.display.show_combatant_details(self.combatant3)
        
        assert "=== Orc ===" in details
        assert "Notes: None" in details
    
    def test_show_notes_list_with_notes(self):
        """Test displaying notes list for combatant with notes."""
        notes_display = self.display.show_notes_list(self.combatant1)
        
        assert "Notes for Hero:" in notes_display
        assert "1. Blessed by cleric" in notes_display
        assert "2. Has inspiration" in notes_display
    
    def test_show_notes_list_without_notes(self):
        """Test displaying notes list for combatant without notes."""
        notes_display = self.display.show_notes_list(self.combatant3)
        
        assert "Orc has no notes." in notes_display
    
    def test_show_combatants_with_notes(self):
        """Test displaying all combatants that have notes."""
        display = self.display.show_combatants_with_notes(self.encounter)
        
        assert "Combatants with notes:" in display
        assert "• Hero (2 notes)" in display
        assert "• Goblin (1 note)" in display
        assert "Orc" not in display
    
    def test_show_combatants_with_notes_empty(self):
        """Test displaying combatants with notes when none have notes."""
        # Create encounter with no notes
        empty_encounter = Encounter(name="Empty")
        combatant = Combatant(name="NoNotes", max_hp=10, current_hp=10, initiative=10)
        empty_encounter.add_combatant(combatant)
        
        display = self.display.show_combatants_with_notes(empty_encounter)
        
        assert "No combatants have notes." in display
    
    def test_show_initiative_order_with_notes(self):
        """Test initiative order display includes note indicators."""
        order = self.display.show_initiative_order(self.encounter.combatants, current_turn=0)
        
        assert "Initiative Order:" in order
        assert "📝" in order  # Should have note indicators
        
        lines = order.split('\n')
        hero_line = next(line for line in lines if "Hero" in line)
        assert "📝" in hero_line
        assert ">>>" in hero_line  # Current turn marker
    
    def test_format_note_management_help(self):
        """Test note management help formatting."""
        help_text = self.display.format_note_management_help()
        
        assert "Note Management Commands:" in help_text
        assert "note add" in help_text
        assert "note list" in help_text
        assert "note edit" in help_text
        assert "note remove" in help_text
        assert "note show" in help_text
        assert "Examples:" in help_text


class TestNoteIntegration:
    """Integration tests for note management across components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.encounter = Encounter(name="Integration Test")
        self.note_service = NoteService(self.encounter)
        self.display = DisplayManager()
        
        # Create combatants
        self.hero = Combatant(name="Hero", max_hp=25, current_hp=20, initiative=18)
        self.villain = Combatant(name="Villain", max_hp=30, current_hp=30, initiative=15)
        
        self.encounter.add_combatant(self.hero)
        self.encounter.add_combatant(self.villain)
    
    def test_full_note_workflow(self):
        """Test complete note management workflow."""
        # Add notes
        self.note_service.add_note("Hero", "Blessed (+1 to saves)")
        self.note_service.add_note("Hero", "Has inspiration")
        self.note_service.add_note("Villain", "Concentrating on spell")
        
        # Verify notes were added
        hero_notes = self.note_service.get_notes("Hero")
        assert len(hero_notes) == 2
        
        # Edit a note
        self.note_service.edit_note("Hero", 0, "Blessed by cleric (+1 to all saves)")
        updated_notes = self.note_service.get_notes("Hero")
        assert updated_notes[0] == "Blessed by cleric (+1 to all saves)"
        
        # Display encounter summary
        summary = self.display.show_encounter_summary(self.encounter)
        assert "📝" in summary
        
        # Display combatant details
        hero_details = self.display.show_combatant_details(self.hero)
        assert "Blessed by cleric (+1 to all saves)" in hero_details
        assert "Has inspiration" in hero_details
        
        # Search notes
        search_results = self.note_service.search_notes("blessed")
        assert len(search_results) == 1
        assert search_results[0][0] == "Hero"
        
        # Remove a note
        self.note_service.remove_note("Hero", 1)  # Remove "Has inspiration"
        remaining_notes = self.note_service.get_notes("Hero")
        assert len(remaining_notes) == 1
        assert "Has inspiration" not in remaining_notes
        
        # Get statistics
        stats = self.note_service.get_note_statistics()
        assert stats['total_notes'] == 2  # 1 for Hero, 1 for Villain
        assert stats['combatants_with_notes'] == 2
    
    def test_note_persistence_requirements(self):
        """Test that notes meet persistence requirements."""
        # Add notes with various content types
        self.note_service.add_note("Hero", "Status: Blessed")
        self.note_service.add_note("Hero", "Spell: Shield (AC +5)")
        self.note_service.add_note("Hero", "Condition: Inspired")
        
        # Verify notes are stored correctly
        notes = self.note_service.get_notes("Hero")
        assert len(notes) == 3
        assert all(isinstance(note, str) for note in notes)
        
        # Verify encounter summary shows note indicators
        summary = self.display.show_encounter_summary(self.encounter)
        hero_line = next(line for line in summary.split('\n') if "Hero" in line)
        assert "📝" in hero_line
        
        # Verify detailed view shows all notes
        details = self.display.show_combatant_details(self.hero)
        for i, note in enumerate(notes, 1):
            assert f"{i}. {note}" in details