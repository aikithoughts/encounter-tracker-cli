#!/usr/bin/env python3
"""Demonstration of the notes management system."""

from dnd_encounter_tracker.core.models import Combatant, Encounter
from dnd_encounter_tracker.core.note_service import NoteService
from dnd_encounter_tracker.cli.display import DisplayManager


def main():
    """Demonstrate the notes management system."""
    print("=== D&D Encounter Tracker - Notes Management Demo ===\n")
    
    # Create an encounter with combatants
    encounter = Encounter(name="Goblin Ambush")
    
    hero = Combatant(name="Thorin", max_hp=45, current_hp=32, initiative=18, combatant_type="player")
    wizard = Combatant(name="Gandalf", max_hp=30, current_hp=30, initiative=15, combatant_type="player")
    goblin1 = Combatant(name="Goblin Chief", max_hp=15, current_hp=8, initiative=12, combatant_type="monster")
    goblin2 = Combatant(name="Goblin Archer", max_hp=10, current_hp=10, initiative=10, combatant_type="monster")
    
    encounter.add_combatant(hero)
    encounter.add_combatant(wizard)
    encounter.add_combatant(goblin1)
    encounter.add_combatant(goblin2)
    
    # Initialize services
    note_service = NoteService(encounter)
    display = DisplayManager()
    
    print("1. Initial encounter state:")
    print(display.show_encounter_summary(encounter))
    print()
    
    # Add some notes
    print("2. Adding notes to combatants...")
    note_service.add_note("Thorin", "Blessed by cleric (+1 to all saves)")
    note_service.add_note("Thorin", "Has inspiration die")
    note_service.add_note("Gandalf", "Concentrating on Shield spell")
    note_service.add_note("Goblin Chief", "Wounded and angry")
    
    print("Notes added successfully!")
    print()
    
    print("3. Encounter with note indicators:")
    print(display.show_encounter_summary(encounter))
    print()
    
    print("4. Detailed view of Thorin:")
    print(display.show_combatant_details(hero))
    print()
    
    print("5. All combatants with notes:")
    print(display.show_combatants_with_notes(encounter))
    print()
    
    print("6. Editing a note...")
    note_service.edit_note("Thorin", 0, "Blessed by cleric (+1 to all saves, advantage on death saves)")
    print("Note edited successfully!")
    print()
    
    print("7. Updated notes for Thorin:")
    print(display.show_notes_list(hero))
    print()
    
    print("8. Searching for notes containing 'blessed':")
    search_results = note_service.search_notes("blessed")
    for combatant_name, note_index, note_text in search_results:
        print(f"  {combatant_name}: {note_text}")
    print()
    
    print("9. Note statistics:")
    stats = note_service.get_note_statistics()
    print(f"  Total notes: {stats['total_notes']}")
    print(f"  Combatants with notes: {stats['combatants_with_notes']}/{stats['total_combatants']}")
    print(f"  Average notes per combatant: {stats['average_notes_per_combatant']:.1f}")
    print()
    
    print("10. Removing a note...")
    note_service.remove_note("Thorin", 1)  # Remove "Has inspiration die"
    print("Note removed successfully!")
    print()
    
    print("11. Final notes for Thorin:")
    print(display.show_notes_list(hero))
    print()
    
    print("=== Demo Complete ===")
    print("\nThe notes management system successfully implements all requirements:")
    print("✓ 4.1: Notes are stored with specific combatants")
    print("✓ 4.2: Notes are displayed when viewing combatants")
    print("✓ 4.3: Free-form text input is supported")
    print("✓ 4.4: Notes can be edited and removed")
    print("✓ 4.5: Encounter view indicates which combatants have notes (📝)")


if __name__ == "__main__":
    main()