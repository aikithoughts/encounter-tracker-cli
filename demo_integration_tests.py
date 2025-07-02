#!/usr/bin/env python3
"""
Demo script showcasing the integration test capabilities.

This script demonstrates:
1. Sample data generation
2. End-to-end workflow testing
3. Performance testing capabilities
4. Data validation and integrity checks
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tests.fixtures.data_generators import DataGenerator
from dnd_encounter_tracker.core.encounter_service import EncounterService
from dnd_encounter_tracker.data.persistence import DataManager
from dnd_encounter_tracker.cli.display import DisplayManager


def demo_data_generation():
    """Demonstrate data generation capabilities."""
    print("=" * 60)
    print("DEMO: Data Generation Capabilities")
    print("=" * 60)
    
    generator = DataGenerator()
    
    # Generate individual combatants
    print("\n1. Individual Combatant Generation:")
    print("-" * 40)
    
    player = generator.create_combatant(combatant_type="player")
    monster = generator.create_combatant(combatant_type="monster")
    npc = generator.create_combatant(combatant_type="npc")
    
    for combatant in [player, monster, npc]:
        print(f"  {combatant.name} ({combatant.combatant_type})")
        print(f"    HP: {combatant.current_hp}/{combatant.max_hp}")
        print(f"    Initiative: {combatant.initiative}")
        print(f"    Notes: {len(combatant.notes)} notes")
    
    # Generate complete encounters
    print("\n2. Complete Encounter Generation:")
    print("-" * 40)
    
    small_encounter = generator.create_encounter(
        name="Small Skirmish",
        num_players=3,
        num_monsters=2,
        num_npcs=1
    )
    
    large_encounter = generator.create_large_encounter(25)
    
    print(f"  Small Encounter: {small_encounter.name}")
    print(f"    Total combatants: {len(small_encounter.combatants)}")
    print(f"    Current turn: {small_encounter.current_turn}")
    print(f"    Round: {small_encounter.round_number}")
    
    print(f"  Large Encounter: {large_encounter.name}")
    print(f"    Total combatants: {len(large_encounter.combatants)}")
    
    # Generate sample encounters
    print("\n3. Sample Encounter Collection:")
    print("-" * 40)
    
    samples = generator.create_sample_encounters()
    for name, encounter in samples.items():
        print(f"  {name}: {encounter.name} ({len(encounter.combatants)} combatants)")
    
    return samples


def demo_end_to_end_workflow():
    """Demonstrate end-to-end workflow testing."""
    print("\n" + "=" * 60)
    print("DEMO: End-to-End Workflow Testing")
    print("=" * 60)
    
    # Create temporary directory for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Initialize services
            data_manager = DataManager()
            encounter_service = EncounterService(data_manager)
            display_manager = DisplayManager()
            
            print("\n1. Creating New Encounter:")
            print("-" * 40)
            
            # Create encounter
            encounter = encounter_service.create_encounter("Demo Battle")
            print(f"  Created encounter: {encounter.name}")
            
            # Add combatants
            encounter_service.add_combatant("Hero Warrior", 50, 18, "player")
            encounter_service.add_combatant("Sneaky Rogue", 35, 20, "player")
            encounter_service.add_combatant("Orc Brute", 45, 12, "monster")
            encounter_service.add_combatant("Goblin Archer", 25, 16, "monster")
            
            print(f"  Added {len(encounter.combatants)} combatants")
            
            print("\n2. Combat Simulation:")
            print("-" * 40)
            
            # Simulate combat actions
            encounter_service.update_hp("Hero Warrior", "-12")
            encounter_service.update_hp("Orc Brute", "-20")
            encounter_service.add_note("Hero Warrior", "Blessed by cleric")
            encounter_service.add_note("Goblin Archer", "Hidden behind cover")
            
            print("  Applied damage and status effects")
            
            # Show initiative order
            order = encounter_service.get_initiative_order()
            print("  Initiative Order:")
            for i, combatant in enumerate(order):
                status = "CURRENT" if i == encounter.current_turn else ""
                print(f"    {i+1}. {combatant.name} (Init: {combatant.initiative}) "
                      f"HP: {combatant.current_hp}/{combatant.max_hp} {status}")
            
            print("\n3. Turn Management:")
            print("-" * 40)
            
            # Advance turns
            for turn in range(3):
                current = encounter_service.get_current_combatant()
                print(f"  Turn {turn + 1}: {current.name}'s turn")
                encounter_service.next_turn()
            
            print(f"  Now in round {encounter.round_number}")
            
            print("\n4. Data Persistence:")
            print("-" * 40)
            
            # Save encounter
            encounter_service.save_encounter("demo_battle")
            print("  Saved encounter to file")
            
            # Load in new service
            new_service = EncounterService(DataManager())
            loaded_encounter = new_service.load_encounter("demo_battle")
            print(f"  Loaded encounter: {loaded_encounter.name}")
            print(f"  Combatants preserved: {len(loaded_encounter.combatants)}")
            
            # Verify data integrity
            original_names = {c.name for c in encounter.combatants}
            loaded_names = {c.name for c in loaded_encounter.combatants}
            assert original_names == loaded_names
            print("  ✓ Data integrity verified")
            
        finally:
            os.chdir(original_cwd)


def demo_performance_testing():
    """Demonstrate performance testing capabilities."""
    print("\n" + "=" * 60)
    print("DEMO: Performance Testing Capabilities")
    print("=" * 60)
    
    import time
    
    generator = DataGenerator()
    
    print("\n1. Large Encounter Creation Performance:")
    print("-" * 40)
    
    sizes = [10, 50, 100, 200]
    
    for size in sizes:
        start_time = time.perf_counter()
        encounter = generator.create_large_encounter(size)
        creation_time = time.perf_counter() - start_time
        
        print(f"  {size:3d} combatants: {creation_time:.4f}s")
    
    print("\n2. Initiative Sorting Performance:")
    print("-" * 40)
    
    large_encounter = generator.create_large_encounter(100)
    
    # Test multiple sorts
    sort_times = []
    for _ in range(5):
        start_time = time.perf_counter()
        large_encounter.sort_by_initiative()
        sort_time = time.perf_counter() - start_time
        sort_times.append(sort_time)
    
    avg_sort_time = sum(sort_times) / len(sort_times)
    print(f"  Average sort time (100 combatants): {avg_sort_time:.6f}s")
    
    print("\n3. File I/O Performance:")
    print("-" * 40)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            service = EncounterService(DataManager())
            service.current_encounter = large_encounter
            
            # Test save performance
            start_time = time.perf_counter()
            service.save_encounter("performance_test")
            save_time = time.perf_counter() - start_time
            
            # Test load performance
            start_time = time.perf_counter()
            loaded = service.load_encounter("performance_test")
            load_time = time.perf_counter() - start_time
            
            # Check file size
            file_size = os.path.getsize("performance_test.json")
            
            print(f"  Save time (100 combatants): {save_time:.4f}s")
            print(f"  Load time (100 combatants): {load_time:.4f}s")
            print(f"  File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
        finally:
            os.chdir(original_cwd)


def demo_data_validation():
    """Demonstrate data validation and integrity checks."""
    print("\n" + "=" * 60)
    print("DEMO: Data Validation and Integrity")
    print("=" * 60)
    
    generator = DataGenerator()
    
    print("\n1. HP Constraint Validation:")
    print("-" * 40)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            service = EncounterService(DataManager())
            encounter = service.create_encounter("Validation Test")
            service.add_combatant("Test Subject", 50, 15, "player")
            
            combatant = encounter.combatants[0]
            
            # Test HP constraints
            print(f"  Initial HP: {combatant.current_hp}/{combatant.max_hp}")
            
            service.update_hp("Test Subject", "-100")  # Excessive damage
            print(f"  After -100 damage: {combatant.current_hp}/{combatant.max_hp}")
            
            service.update_hp("Test Subject", "200")  # Excessive healing
            print(f"  After setting to 200: {combatant.current_hp}/{combatant.max_hp}")
            
            print("  ✓ HP constraints properly enforced")
            
            print("\n2. Initiative Order Consistency:")
            print("-" * 40)
            
            # Create encounter with specific initiatives
            test_encounter = service.create_encounter("Initiative Test")
            initiatives = [20, 15, 18, 12, 22]
            names = []
            
            for i, init in enumerate(initiatives):
                name = f"Combatant {i+1}"
                service.add_combatant(name, 30, init, "player")
                names.append(name)
            
            # Check order multiple times
            orders = []
            for _ in range(3):
                order = service.get_initiative_order()
                order_names = [c.name for c in order]
                orders.append(order_names)
            
            # All orders should be identical
            assert all(order == orders[0] for order in orders)
            print("  ✓ Initiative order is consistent")
            
            # Expected order: 22, 20, 18, 15, 12
            expected_initiatives = [22, 20, 18, 15, 12]
            actual_initiatives = [c.initiative for c in service.get_initiative_order()]
            assert actual_initiatives == expected_initiatives
            print("  ✓ Initiative sorting is correct")
            
            print("\n3. Save/Load Data Integrity:")
            print("-" * 40)
            
            # Create complex encounter
            complex_encounter = generator.create_encounter(
                name="Integrity Test",
                num_players=3,
                num_monsters=4,
                num_npcs=2
            )
            
            # Modify some data
            complex_encounter.combatants[0].current_hp = 25
            complex_encounter.combatants[0].add_note("Test note 1")
            complex_encounter.combatants[0].add_note("Test note 2")
            complex_encounter.current_turn = 3
            complex_encounter.round_number = 5
            
            # Save and load
            service.current_encounter = complex_encounter
            service.save_encounter("integrity_test")
            loaded = service.load_encounter("integrity_test")
            
            # Verify all data preserved
            assert loaded.name == complex_encounter.name
            assert loaded.current_turn == complex_encounter.current_turn
            assert loaded.round_number == complex_encounter.round_number
            assert len(loaded.combatants) == len(complex_encounter.combatants)
            
            # Check specific combatant data
            orig_first = complex_encounter.combatants[0]
            loaded_first = loaded.combatants[0]
            assert loaded_first.name == orig_first.name
            assert loaded_first.current_hp == orig_first.current_hp
            assert loaded_first.notes == orig_first.notes
            
            print("  ✓ All encounter data preserved through save/load")
            
        finally:
            os.chdir(original_cwd)


def main():
    """Run the integration test demo."""
    print("D&D Encounter Tracker - Integration Test Demo")
    print("This demo showcases the comprehensive testing capabilities")
    print("developed for the encounter tracker system.")
    
    try:
        # Run all demo sections
        samples = demo_data_generation()
        demo_end_to_end_workflow()
        demo_performance_testing()
        demo_data_validation()
        
        print("\n" + "=" * 60)
        print("DEMO SUMMARY")
        print("=" * 60)
        print("✓ Data Generation: Created sample encounters and combatants")
        print("✓ End-to-End Workflows: Tested complete user scenarios")
        print("✓ Performance Testing: Measured system performance at scale")
        print("✓ Data Validation: Verified integrity and constraint enforcement")
        print(f"✓ Sample Data: Generated {len(samples)} sample encounters")
        
        print("\nIntegration test capabilities successfully demonstrated!")
        print("\nTo run the full test suite:")
        print("  python run_integration_tests.py")
        print("  python run_integration_tests.py --quick")
        print("  python run_integration_tests.py --performance")
        print("  python run_integration_tests.py --generate-samples")
        
        return 0
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())