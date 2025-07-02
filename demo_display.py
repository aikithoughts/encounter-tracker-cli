#!/usr/bin/env python3
"""Demo script to showcase the DisplayManager functionality."""

from dnd_encounter_tracker.cli.display import DisplayManager
from dnd_encounter_tracker.core.models import Combatant, Encounter


def main():
    """Demonstrate display functionality."""
    print("=== D&D Encounter Tracker Display Demo ===\n")
    
    # Create display manager
    display = DisplayManager()
    
    # Create an encounter
    encounter = Encounter(name="Goblin Ambush")
    
    # Create combatants with various states
    hero = Combatant(name="Thorin Oakenshield", max_hp=45, current_hp=32, initiative=18, combatant_type="player")
    wizard = Combatant(name="Gandalf", max_hp=25, current_hp=25, initiative=16, combatant_type="player")
    goblin1 = Combatant(name="Goblin Archer", max_hp=12, current_hp=3, initiative=14, combatant_type="monster")  # Critical HP
    goblin2 = Combatant(name="Goblin Warrior", max_hp=15, current_hp=8, initiative=12, combatant_type="monster")
    orc = Combatant(name="Orc Brute", max_hp=20, current_hp=0, initiative=10, combatant_type="monster")  # Dead
    
    # Add notes to some combatants
    hero.add_note("Blessed by cleric (+1 to all saves)")
    hero.add_note("Has inspiration die")
    wizard.add_note("Shield spell active (AC +5)")
    goblin1.add_note("Poisoned (disadvantage on attacks)")
    goblin2.add_note("Rage active (+2 damage)")
    
    # Add combatants to encounter
    encounter.add_combatant(hero)
    encounter.add_combatant(wizard)
    encounter.add_combatant(goblin1)
    encounter.add_combatant(goblin2)
    encounter.add_combatant(orc)
    
    # Set encounter state
    encounter.current_turn = 0  # Thorin's turn
    encounter.round_number = 3
    
    print("1. ENCOUNTER SUMMARY")
    print("=" * 50)
    summary = display.show_encounter_summary(encounter)
    print(summary)
    print()
    
    print("2. COMBATANT DETAILS")
    print("=" * 50)
    print("Hero Details:")
    hero_details = display.show_combatant_details(hero)
    print(hero_details)
    print()
    
    print("Critical Combatant Details:")
    goblin_details = display.show_combatant_details(goblin1)
    print(goblin_details)
    print()
    
    print("Dead Combatant Details:")
    orc_details = display.show_combatant_details(orc)
    print(orc_details)
    print()
    
    print("3. INITIATIVE ORDER (Standalone)")
    print("=" * 50)
    initiative_order = display.show_initiative_order(encounter.combatants, current_turn=1)
    print(initiative_order)
    print()
    
    print("4. NOTES MANAGEMENT")
    print("=" * 50)
    print("Combatants with notes:")
    notes_summary = display.show_combatants_with_notes(encounter)
    print(notes_summary)
    print()
    
    print("Notes for Thorin:")
    thorin_notes = display.show_notes_list(hero)
    print(thorin_notes)
    print()
    
    print("5. HELP DISPLAY")
    print("=" * 50)
    help_text = display.format_note_management_help()
    print(help_text)
    print()
    
    print("6. EDGE CASES")
    print("=" * 50)
    
    # Empty encounter
    empty_encounter = Encounter(name="Empty Battle")
    empty_summary = display.show_encounter_summary(empty_encounter)
    print("Empty encounter:")
    print(empty_summary)
    print()
    
    # Empty initiative order
    empty_order = display.show_initiative_order([])
    print("Empty initiative order:")
    print(empty_order)
    print()
    
    print("=== Demo Complete ===")


if __name__ == "__main__":
    main()