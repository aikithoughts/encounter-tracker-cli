#!/usr/bin/env python3
"""Demo script showing turn management and combat flow functionality."""

from dnd_encounter_tracker.core.encounter_service import EncounterService
from dnd_encounter_tracker.data.persistence import DataManager
from dnd_encounter_tracker.cli.display import DisplayManager

def demo_turn_management():
    """Demonstrate turn management functionality."""
    print("=== D&D Encounter Tracker - Turn Management Demo ===\n")
    
    # Create service and display manager
    service = EncounterService(DataManager("demo_encounters"))
    display = DisplayManager()
    
    # Create a new encounter
    print("1. Creating encounter...")
    encounter = service.create_encounter("Goblin Ambush")
    print(f"Created encounter: {encounter.name}")
    
    # Add combatants
    print("\n2. Adding combatants...")
    service.add_combatant("Thorin", 45, 16, "player")
    service.add_combatant("Legolas", 35, 18, "player")  # Highest initiative
    service.add_combatant("Gimli", 50, 12, "player")
    service.add_combatant("Goblin Chief", 30, 15, "monster")
    service.add_combatant("Goblin Scout", 15, 14, "monster")
    
    print("Added 5 combatants")
    
    # Show initial state
    print("\n3. Initial encounter state:")
    encounter = service.get_current_encounter()
    print(display.show_encounter_summary(encounter))
    
    # Demonstrate turn advancement
    print("\n4. Advancing through turns...")
    for round_num in range(1, 3):  # Show 2 rounds
        print(f"\n--- Round {round_num} ---")
        
        # Reset to start of round if needed
        if round_num == 1:
            encounter.current_turn = 0
            encounter.round_number = 1
        
        for turn in range(len(encounter.combatants)):
            current = service.get_current_combatant()
            print(f"Turn {turn + 1}: {current.name}'s turn (Initiative: {current.initiative})")
            
            # Simulate some combat actions
            if current.name == "Legolas" and round_num == 1:
                service.update_hp("Goblin Scout", "-10")
                print(f"  → Legolas attacks Goblin Scout for 10 damage!")
            elif current.name == "Goblin Chief" and round_num == 1:
                service.update_hp("Thorin", "-8")
                service.add_note("Thorin", "Wounded by Goblin Chief")
                print(f"  → Goblin Chief attacks Thorin for 8 damage!")
            elif current.name == "Gimli" and round_num == 2:
                service.update_hp("Goblin Scout", "0")
                print(f"  → Gimli finishes off the Goblin Scout!")
            
            # Advance to next turn (except on last turn of last round)
            if not (round_num == 2 and turn == len(encounter.combatants) - 1):
                service.next_turn()
    
    # Show final state
    print(f"\n5. Final encounter state:")
    print(display.show_encounter_summary(encounter))
    
    # Demonstrate combatant removal and turn adjustment
    print("\n6. Removing defeated combatant...")
    print(f"Current turn before removal: {service.get_current_combatant().name}")
    service.remove_combatant("Goblin Scout")
    print(f"Removed Goblin Scout")
    print(f"Current turn after removal: {service.get_current_combatant().name}")
    
    # Show updated encounter
    print("\n7. Updated encounter:")
    encounter = service.get_current_encounter()
    print(display.show_encounter_summary(encounter))
    
    # Demonstrate save/load with turn state
    print("\n8. Saving encounter with turn state...")
    service.save_encounter("goblin_ambush")
    print("Encounter saved!")
    
    # Load encounter and verify turn state is preserved
    print("\n9. Loading encounter...")
    loaded_encounter = service.load_encounter("goblin_ambush")
    print(f"Loaded encounter: {loaded_encounter.name}")
    print(f"Round: {loaded_encounter.round_number}")
    print(f"Current turn: {service.get_current_combatant().name}")
    
    # Continue combat from saved state
    print("\n10. Continuing combat from saved state...")
    service.next_turn()
    print(f"Advanced to next turn: {service.get_current_combatant().name}")
    
    print("\n=== Turn Management Demo Complete ===")

if __name__ == "__main__":
    demo_turn_management()