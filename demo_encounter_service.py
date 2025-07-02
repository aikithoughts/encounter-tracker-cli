#!/usr/bin/env python3
"""Demonstration of the EncounterService functionality."""

from dnd_encounter_tracker.core.encounter_service import EncounterService
from dnd_encounter_tracker.data.persistence import DataManager


def main():
    """Demonstrate EncounterService functionality."""
    print("=== D&D Encounter Tracker - Service Layer Demo ===\n")
    
    # Initialize the service with a data manager
    data_manager = DataManager("demo_encounters")
    service = EncounterService(data_manager)
    
    # Create a new encounter
    print("1. Creating a new encounter...")
    encounter = service.create_encounter("Goblin Ambush")
    print(f"   Created encounter: {encounter.name}")
    
    # Add combatants
    print("\n2. Adding combatants...")
    service.add_combatant("Thorin", 45, 18, "player")
    service.add_combatant("Legolas", 35, 20, "player")
    service.add_combatant("Gimli", 50, 12, "player")
    service.add_combatant("Goblin 1", 7, 15, "monster")
    service.add_combatant("Goblin 2", 7, 13, "monster")
    
    print("   Added 5 combatants to the encounter")
    
    # Show initiative order
    print("\n3. Initiative order:")
    order = service.get_initiative_order()
    for i, combatant in enumerate(order, 1):
        print(f"   {i}. {combatant.name} (Initiative: {combatant.initiative}, HP: {combatant.current_hp}/{combatant.max_hp})")
    
    # Update some hit points
    print("\n4. Updating hit points...")
    service.update_hp("Thorin", "-12")  # Thorin takes 12 damage
    service.update_hp("Goblin 1", "-7")  # Goblin 1 dies
    service.update_hp("Legolas", "+5")   # Legolas gets healed (but capped at max)
    
    print("   Updated HP for Thorin (-12), Goblin 1 (-7), and Legolas (+5)")
    
    # Add some notes
    print("\n5. Adding notes...")
    service.add_note("Thorin", "Blessed by cleric (+1 AC)")
    service.add_note("Thorin", "Has inspiration")
    service.add_note("Goblin 2", "Hiding behind tree")
    
    print("   Added notes to combatants")
    
    # Show current state
    print("\n6. Current encounter state:")
    current = service.get_current_combatant()
    if current:
        print(f"   Current turn: {current.name}")
    
    summary = service.get_encounter_summary()
    print(f"   Round: {summary['round_number']}")
    print(f"   Combatants: {summary['combatant_count']}")
    
    # Show detailed combatant info
    print("\n7. Detailed combatant information:")
    for combatant in service.get_initiative_order():
        status = "ALIVE" if combatant.is_alive() else "DEAD"
        notes_info = f" (Notes: {len(combatant.notes)})" if combatant.has_notes() else ""
        print(f"   {combatant.name}: {combatant.current_hp}/{combatant.max_hp} HP, Init {combatant.initiative} [{status}]{notes_info}")
        
        if combatant.has_notes():
            for j, note in enumerate(combatant.notes):
                print(f"     - {note}")
    
    # Advance a few turns
    print("\n8. Advancing turns...")
    for i in range(3):
        current = service.next_turn()
        if current:
            print(f"   Turn {i+1}: {current.name}'s turn")
    
    # Save the encounter
    print("\n9. Saving encounter...")
    service.save_encounter("goblin_ambush")
    print("   Encounter saved to 'goblin_ambush.json'")
    
    # Show available encounters
    print("\n10. Available encounters:")
    encounters = service.get_available_encounters()
    for encounter_name in encounters:
        print(f"    - {encounter_name}")
    
    print("\n=== Demo Complete ===")
    print("The EncounterService provides a clean interface for:")
    print("- Creating and managing encounters")
    print("- Adding/removing combatants")
    print("- Managing hit points and initiative")
    print("- Adding notes and tracking combat state")
    print("- Saving/loading encounters with full persistence")
    print("- All with proper error handling and validation")


if __name__ == "__main__":
    main()