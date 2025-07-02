#!/usr/bin/env python3
"""Demo script showcasing file management and encounter listing features."""

import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

from dnd_encounter_tracker.data.persistence import DataManager
from dnd_encounter_tracker.core.encounter_service import EncounterService
from dnd_encounter_tracker.core.models import Encounter, Combatant


def demo_file_management():
    """Demonstrate file management features."""
    print("=== D&D Encounter Tracker - File Management Demo ===\n")
    
    # Create temporary directory for demo
    temp_dir = tempfile.mkdtemp(prefix="dnd_demo_")
    print(f"Demo directory: {temp_dir}\n")
    
    try:
        # Initialize services
        data_manager = DataManager(temp_dir)
        encounter_service = EncounterService(data_manager)
        
        # 1. Create and save multiple encounters
        print("1. Creating and saving multiple encounters...")
        encounters_data = [
            ("goblin_ambush", "Goblin Ambush", [
                ("Thorin", 45, 18, "player"),
                ("Legolas", 35, 16, "player"),
                ("Goblin Scout", 7, 12, "monster"),
                ("Goblin Warrior", 11, 10, "monster")
            ]),
            ("dragon_lair", "Ancient Dragon's Lair", [
                ("Gandalf", 60, 20, "npc"),
                ("Ancient Red Dragon", 546, 24, "monster"),
                ("Kobold Minion", 5, 8, "monster")
            ]),
            ("tavern_brawl", "Tavern Brawl", [
                ("Drunk Patron", 8, 6, "npc"),
                ("Bartender", 15, 12, "npc"),
                ("Town Guard", 25, 14, "npc")
            ])
        ]
        
        for filename, name, combatants in encounters_data:
            encounter = encounter_service.create_encounter(name)
            
            for c_name, hp, init, c_type in combatants:
                encounter_service.add_combatant(c_name, hp, init, c_type)
            
            encounter_service.save_encounter(filename)
            print(f"  ✓ Saved '{name}' as {filename}.json")
        
        print()
        
        # 2. List encounters with basic view
        print("2. Listing encounters (basic view)...")
        encounters = encounter_service.get_available_encounters()
        for encounter in encounters:
            print(f"  - {encounter}")
        print()
        
        # 3. List encounters with detailed metadata
        print("3. Listing encounters with detailed metadata...")
        encounters_with_metadata = encounter_service.list_encounters_with_metadata()
        
        print("Available encounters (most recently modified first):")
        print("=" * 70)
        
        for encounter_info in encounters_with_metadata:
            filename = encounter_info["filename"]
            encounter_name = encounter_info["encounter_name"]
            metadata = encounter_info["metadata"]
            
            # Format dates for display
            try:
                created = datetime.fromisoformat(metadata["created"])
                modified = datetime.fromisoformat(metadata["last_modified"])
                created_str = created.strftime("%Y-%m-%d %H:%M")
                modified_str = modified.strftime("%Y-%m-%d %H:%M")
            except (ValueError, KeyError):
                created_str = metadata.get("created", "Unknown")[:16]
                modified_str = metadata.get("last_modified", "Unknown")[:16]
            
            # Format file size
            size_bytes = metadata.get("size_bytes", 0)
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f} KB"
            else:
                size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
            
            print(f"File: {filename}.json")
            print(f"Name: {encounter_name}")
            print(f"Created: {created_str}")
            print(f"Modified: {modified_str}")
            print(f"Size: {size_str}")
            print("-" * 40)
        
        print()
        
        # 4. Create backups
        print("4. Creating backups...")
        for filename in ["goblin_ambush", "dragon_lair"]:
            backup_path = encounter_service.backup_encounter(filename)
            print(f"  ✓ Created backup: {Path(backup_path).name}")
        print()
        
        # 5. Modify an encounter and save (creates automatic backup)
        print("5. Modifying encounter (automatic backup on overwrite)...")
        encounter_service.load_encounter("goblin_ambush")
        encounter_service.add_combatant("Orc Berserker", 19, 9, "monster")
        encounter_service.save_encounter("goblin_ambush")
        print("  ✓ Modified 'Goblin Ambush' - automatic backup created")
        print()
        
        # 6. Show all backup files
        print("6. Current backup files:")
        backup_files = list(Path(temp_dir).glob("*.backup"))
        for backup_file in sorted(backup_files):
            stat = backup_file.stat()
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime)
            print(f"  - {backup_file.name} ({size} bytes, {modified.strftime('%Y-%m-%d %H:%M')})")
        print()
        
        # 7. Cleanup old backups
        print("7. Cleaning up old backups (keeping 2 per encounter)...")
        deleted_files = encounter_service.cleanup_old_backups(max_backups=2)
        
        if deleted_files:
            print(f"  ✓ Cleaned up {len(deleted_files)} old backup files:")
            for deleted_file in deleted_files:
                print(f"    - {Path(deleted_file).name}")
        else:
            print("  ✓ No old backup files to clean up")
        print()
        
        # 8. Show remaining backup files
        print("8. Remaining backup files after cleanup:")
        backup_files = list(Path(temp_dir).glob("*.backup"))
        for backup_file in sorted(backup_files):
            stat = backup_file.stat()
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime)
            print(f"  - {backup_file.name} ({size} bytes, {modified.strftime('%Y-%m-%d %H:%M')})")
        
        if not backup_files:
            print("  (No backup files remaining)")
        print()
        
        # 9. Demonstrate metadata preservation
        print("9. Demonstrating metadata preservation...")
        
        # Get original metadata
        original_metadata = encounter_service.get_encounter_metadata("tavern_brawl")
        print(f"  Original created: {original_metadata['created'][:19]}")
        print(f"  Original modified: {original_metadata['last_modified'][:19]}")
        
        # Load, modify, and save
        encounter_service.load_encounter("tavern_brawl")
        encounter_service.add_combatant("Mysterious Stranger", 30, 15, "npc")
        encounter_service.save_encounter("tavern_brawl")
        
        # Get updated metadata
        updated_metadata = encounter_service.get_encounter_metadata("tavern_brawl")
        print(f"  Updated created: {updated_metadata['created'][:19]} (preserved)")
        print(f"  Updated modified: {updated_metadata['last_modified'][:19]} (updated)")
        print()
        
        print("=== File Management Demo Complete ===")
        print(f"Demo files created in: {temp_dir}")
        print("You can explore the files manually or run cleanup when done.")
        
    except Exception as e:
        print(f"Error during demo: {e}")
        raise
    
    finally:
        # Ask user if they want to clean up
        try:
            response = input("\nClean up demo files? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                shutil.rmtree(temp_dir, ignore_errors=True)
                print("Demo files cleaned up.")
            else:
                print(f"Demo files preserved in: {temp_dir}")
        except KeyboardInterrupt:
            print(f"\nDemo files preserved in: {temp_dir}")


if __name__ == "__main__":
    demo_file_management()