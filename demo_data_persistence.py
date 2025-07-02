#!/usr/bin/env python3
"""Demo script to show DataManager functionality."""

from dnd_encounter_tracker.core.models import Encounter, Combatant
from dnd_encounter_tracker.data.persistence import DataManager
import tempfile
import os

def main():
    """Demonstrate DataManager functionality."""
    print("=== D&D Encounter Tracker - Data Persistence Demo ===\n")
    
    # Create a temporary directory for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")
        
        # Initialize DataManager
        data_manager = DataManager(temp_dir)
        print("✓ DataManager initialized\n")
        
        # Create sample encounter
        print("Creating sample encounter...")
        thorin = Combatant(
            name="Thorin Oakenshield",
            max_hp=45,
            current_hp=32,
            initiative=18,
            notes=["Blessed by cleric", "Has inspiration"],
            combatant_type="player"
        )
        
        goblin1 = Combatant(
            name="Goblin Archer",
            max_hp=15,
            current_hp=8,
            initiative=12,
            notes=["Poisoned", "Hidden behind tree"],
            combatant_type="monster"
        )
        
        goblin2 = Combatant(
            name="Goblin Warrior",
            max_hp=18,
            current_hp=18,
            initiative=14,
            combatant_type="monster"
        )
        
        encounter = Encounter(
            name="Goblin Ambush",
            combatants=[thorin, goblin1, goblin2],
            current_turn=1,
            round_number=3
        )
        
        print(f"✓ Created encounter: {encounter.name}")
        print(f"  - {len(encounter.combatants)} combatants")
        print(f"  - Round {encounter.round_number}, Turn {encounter.current_turn}")
        print()
        
        # Save encounter
        print("Saving encounter to file...")
        filename = "goblin_ambush"
        data_manager.save_to_file(encounter, filename)
        print(f"✓ Saved encounter as '{filename}.json'")
        
        # Verify file exists
        if data_manager.encounter_exists(filename):
            print("✓ File existence confirmed")
        
        # List available encounters
        available = data_manager.get_available_encounters()
        print(f"✓ Available encounters: {available}")
        print()
        
        # Load encounter back
        print("Loading encounter from file...")
        loaded_encounter = data_manager.load_from_file(filename)
        print(f"✓ Loaded encounter: {loaded_encounter.name}")
        
        # Verify data integrity
        print("\nVerifying data integrity...")
        assert loaded_encounter.name == encounter.name
        assert len(loaded_encounter.combatants) == len(encounter.combatants)
        assert loaded_encounter.current_turn == encounter.current_turn
        assert loaded_encounter.round_number == encounter.round_number
        
        # Check combatant details
        loaded_thorin = loaded_encounter.get_combatant("Thorin Oakenshield")
        assert loaded_thorin is not None
        assert loaded_thorin.max_hp == thorin.max_hp
        assert loaded_thorin.current_hp == thorin.current_hp
        assert loaded_thorin.initiative == thorin.initiative
        assert loaded_thorin.notes == thorin.notes
        assert loaded_thorin.combatant_type == thorin.combatant_type
        
        print("✓ All data integrity checks passed")
        print()
        
        # Test file format validation
        print("Testing file format validation...")
        is_valid = data_manager.validate_file_format(filename)
        print(f"✓ File format validation: {'PASSED' if is_valid else 'FAILED'}")
        
        # Modify and save again (test backup creation)
        print("\nTesting backup creation...")
        loaded_encounter.name = "Modified Goblin Ambush"
        data_manager.save_to_file(loaded_encounter, filename)
        print("✓ Saved modified encounter (backup should be created)")
        
        # Check if backup exists
        backup_path = os.path.join(temp_dir, f"{filename}.json.backup")
        if os.path.exists(backup_path):
            print("✓ Backup file created successfully")
        
        # Test error handling
        print("\nTesting error handling...")
        try:
            data_manager.load_from_file("nonexistent_file")
        except Exception as e:
            print(f"✓ Properly handled missing file: {type(e).__name__}")
        
        try:
            data_manager.save_to_file(encounter, "")
        except Exception as e:
            print(f"✓ Properly handled empty filename: {type(e).__name__}")
        
        print("\n=== Demo completed successfully! ===")
        print("\nKey features demonstrated:")
        print("• JSON file save/load operations")
        print("• Automatic .json extension handling")
        print("• Backup file creation on overwrite")
        print("• File format validation and corruption detection")
        print("• Comprehensive error handling")
        print("• Data integrity preservation")
        print("• Encounter listing and file management")

if __name__ == "__main__":
    main()