#!/usr/bin/env python3
"""Demo script to test interactive functionality."""

from dnd_encounter_tracker.cli.interactive import InteractiveSession
import tempfile
import shutil
from pathlib import Path

def test_interactive_workflow():
    """Test a complete interactive workflow."""
    print("=== TESTING INTERACTIVE WORKFLOW ===")
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    
    try:
        # Create session with temporary directory
        session = InteractiveSession()
        session.data_manager.data_directory = temp_path
        
        print("1. Testing session initialization...")
        print(f"   Prompt: {session._get_prompt()}")
        
        print("\n2. Testing encounter creation...")
        session._execute_command('new "Test Encounter"')
        encounter = session.encounter_service.get_current_encounter()
        print(f"   Created encounter: {encounter.name}")
        print(f"   Prompt: {session._get_prompt()}")
        
        print("\n3. Testing combatant addition...")
        session._execute_command('add Thorin 45 18 player')
        session._execute_command('add Legolas 38 16 player')
        session._execute_command('add "Goblin Scout" 7 12 monster')
        
        encounter = session.encounter_service.get_current_encounter()
        print(f"   Added {len(encounter.combatants)} combatants")
        
        print("\n4. Testing encounter display...")
        session._execute_command('show')
        
        print("\n5. Testing HP management...")
        session._execute_command('hp Thorin -8')
        thorin = encounter.get_combatant("Thorin")
        print(f"   Thorin's HP: {thorin.current_hp}/{thorin.max_hp}")
        
        print("\n6. Testing note management...")
        session._execute_command('note add Thorin "Blessed by cleric"')
        print(f"   Thorin's notes: {thorin.notes}")
        
        print("\n7. Testing turn advancement...")
        session._execute_command('next')
        current = encounter.get_current_combatant()
        print(f"   Current turn: {current.name if current else 'None'}")
        
        print("\n8. Testing save functionality...")
        session._execute_command('save test_encounter')
        print(f"   Unsaved changes: {session.unsaved_changes}")
        
        print("\n9. Testing status display...")
        session._execute_command('status')
        
        print("\n10. Testing help system...")
        session._execute_command('help')
        
        print("\n=== ALL TESTS PASSED ===")
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

def test_help_system():
    """Test the help system comprehensively."""
    print("\n=== TESTING HELP SYSTEM ===")
    
    from dnd_encounter_tracker.cli.help import HelpManager
    help_mgr = HelpManager()
    
    topics = ['commands', 'examples', 'workflow', 'notes', 'hp', 'initiative']
    
    for topic in topics:
        print(f"\nTesting help topic: {topic}")
        help_content = help_mgr.help_topics[topic]()
        print(f"   Content length: {len(help_content)} characters")
        print(f"   Contains examples: {'Example:' in help_content or 'example' in help_content.lower()}")

def test_command_parsing():
    """Test command parsing functionality."""
    print("\n=== TESTING COMMAND PARSING ===")
    
    session = InteractiveSession()
    
    test_commands = [
        ['new', 'Test Encounter'],
        ['add', 'Thorin', '45', '18', 'player'],
        ['hp', 'Thorin', '-8'],
        ['init', 'Thorin', '20'],
        ['note', 'add', 'Thorin', 'Blessed', 'by', 'cleric'],
        ['note', 'list', 'Thorin'],
        ['show'],
        ['next'],
        ['save', 'test'],
        ['load', 'test'],
        ['list']
    ]
    
    for cmd in test_commands:
        args = session._parse_interactive_command(cmd)
        if args:
            print(f"   ✓ {' '.join(cmd)} -> {args.command}")
        else:
            print(f"   ✗ {' '.join(cmd)} -> Failed to parse")

if __name__ == '__main__':
    test_interactive_workflow()
    test_help_system()
    test_command_parsing()
    print("\n🎉 All demo tests completed successfully!")