#!/usr/bin/env python3
"""
Integration test runner for D&D Encounter Tracker.

This script runs comprehensive integration tests including:
- End-to-end workflow tests
- Performance tests with large encounters
- Requirement compliance tests
- Sample data generation and validation

Usage:
    python run_integration_tests.py [options]

Options:
    --quick         Run only quick tests (skip performance tests)
    --performance   Run only performance tests
    --verbose       Verbose output
    --generate-samples  Generate sample encounter files
"""

import argparse
import sys
import os
import subprocess
import tempfile
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tests.fixtures.data_generators import DataGenerator


def run_pytest_command(test_pattern, verbose=False, additional_args=None):
    """Run pytest with specified pattern and options."""
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    cmd.append(test_pattern)
    
    if additional_args:
        cmd.extend(additional_args)
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode == 0


def generate_sample_encounters():
    """Generate sample encounter files for testing and demonstration."""
    print("Generating sample encounter files...")
    
    generator = DataGenerator()
    encounters = generator.create_sample_encounters()
    
    # Ensure sample_encounters directory exists
    sample_dir = Path("sample_encounters")
    sample_dir.mkdir(exist_ok=True)
    
    generated_files = []
    
    for name, encounter in encounters.items():
        filename = sample_dir / f"{name}.json"
        data = generator.create_encounter_json_data(encounter)
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        generated_files.append(filename)
        print(f"  Generated: {filename}")
    
    # Generate additional test scenarios
    test_scenarios = {
        "empty_encounter": generator.create_encounter(
            name="Empty Encounter",
            num_players=0,
            num_monsters=0,
            num_npcs=0
        ),
        "single_combatant": generator.create_encounter(
            name="Solo Adventure",
            num_players=1,
            num_monsters=0,
            num_npcs=0
        ),
        "large_battle": generator.create_large_encounter(50),
        "initiative_ties": create_initiative_tie_scenario(),
        "damaged_party": create_damaged_party_scenario(),
        "status_effects": create_status_effects_scenario()
    }
    
    for name, encounter in test_scenarios.items():
        filename = sample_dir / f"{name}.json"
        data = generator.create_encounter_json_data(encounter)
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        generated_files.append(filename)
        print(f"  Generated: {filename}")
    
    print(f"Generated {len(generated_files)} sample encounter files")
    return generated_files


def create_initiative_tie_scenario():
    """Create scenario with initiative ties for testing."""
    from dnd_encounter_tracker.core.models import Encounter, Combatant
    
    encounter = Encounter(name="Initiative Ties Test")
    
    # Create combatants with identical initiatives
    for i in range(4):
        combatant = Combatant(
            name=f"Tied Fighter {i+1}",
            max_hp=30,
            current_hp=30,
            initiative=15,  # All have same initiative
            combatant_type="player"
        )
        encounter.add_combatant(combatant)
    
    return encounter


def create_damaged_party_scenario():
    """Create scenario with damaged party members."""
    generator = DataGenerator()
    encounter = generator.create_encounter(
        name="Damaged Party",
        num_players=4,
        num_monsters=2,
        num_npcs=1
    )
    
    # Apply various damage levels
    for i, combatant in enumerate(encounter.combatants):
        if combatant.combatant_type == "player":
            # Damage players to different levels
            damage_percent = 0.3 + (i * 0.2)  # 30%, 50%, 70%, 90%
            damage = int(combatant.max_hp * damage_percent)
            combatant.current_hp = max(1, combatant.max_hp - damage)
    
    return encounter


def create_status_effects_scenario():
    """Create scenario with various status effects."""
    generator = DataGenerator()
    encounter = generator.create_encounter(
        name="Status Effects Showcase",
        num_players=3,
        num_monsters=3,
        num_npcs=2
    )
    
    status_effects = [
        "Blessed (+1d4 to attacks and saves)",
        "Poisoned (disadvantage on attacks)",
        "Concentrating on Bless",
        "Prone (disadvantage on attacks)",
        "Grappled (speed 0)",
        "Frightened (disadvantage on attacks)",
        "Invisible (advantage on attacks)",
        "Stunned (incapacitated)"
    ]
    
    # Add status effects to combatants
    for i, combatant in enumerate(encounter.combatants):
        if i < len(status_effects):
            combatant.add_note(status_effects[i])
    
    return encounter


def validate_sample_files():
    """Validate that generated sample files are correct."""
    print("Validating sample encounter files...")
    
    sample_dir = Path("sample_encounters")
    if not sample_dir.exists():
        print("No sample_encounters directory found")
        return False
    
    json_files = list(sample_dir.glob("*.json"))
    if not json_files:
        print("No JSON files found in sample_encounters directory")
        return False
    
    valid_count = 0
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Basic validation
            required_fields = ["name", "combatants", "current_turn", "round_number"]
            if all(field in data for field in required_fields):
                valid_count += 1
                print(f"  ✓ {json_file.name}")
            else:
                print(f"  ✗ {json_file.name} - missing required fields")
        
        except json.JSONDecodeError as e:
            print(f"  ✗ {json_file.name} - invalid JSON: {e}")
        except Exception as e:
            print(f"  ✗ {json_file.name} - error: {e}")
    
    print(f"Validated {valid_count}/{len(json_files)} sample files")
    return valid_count == len(json_files)


def run_integration_tests(quick=False, performance_only=False, verbose=False):
    """Run the integration test suite."""
    print("D&D Encounter Tracker - Integration Test Suite")
    print("=" * 50)
    
    if performance_only:
        print("Running performance tests only...")
        success = run_pytest_command(
            "tests/test_performance.py",
            verbose=verbose,
            additional_args=["-m", "not slow"]
        )
        return success
    
    test_suites = [
        ("Integration Workflows", "tests/test_integration_workflows.py"),
        ("Comprehensive Integration", "tests/test_comprehensive_integration.py"),
    ]
    
    if not quick:
        test_suites.append(("Performance Tests", "tests/test_performance.py"))
    
    all_passed = True
    
    for suite_name, test_path in test_suites:
        print(f"\n{suite_name}")
        print("-" * len(suite_name))
        
        if quick and "performance" in test_path.lower():
            # Skip slow performance tests in quick mode
            additional_args = ["-m", "not slow"]
        else:
            additional_args = None
        
        success = run_pytest_command(test_path, verbose=verbose, additional_args=additional_args)
        
        if success:
            print(f"✓ {suite_name} passed")
        else:
            print(f"✗ {suite_name} failed")
            all_passed = False
    
    return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run integration tests for D&D Encounter Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_integration_tests.py                    # Run all tests
  python run_integration_tests.py --quick            # Skip performance tests
  python run_integration_tests.py --performance      # Only performance tests
  python run_integration_tests.py --generate-samples # Generate sample files
  python run_integration_tests.py --verbose          # Verbose output
        """
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run only quick tests (skip slow performance tests)"
    )
    
    parser.add_argument(
        "--performance",
        action="store_true",
        help="Run only performance tests"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose test output"
    )
    
    parser.add_argument(
        "--generate-samples",
        action="store_true",
        help="Generate sample encounter files"
    )
    
    parser.add_argument(
        "--validate-samples",
        action="store_true",
        help="Validate existing sample files"
    )
    
    args = parser.parse_args()
    
    # Change to project directory
    os.chdir(project_root)
    
    success = True
    
    if args.generate_samples:
        generate_sample_encounters()
        if not args.validate_samples:
            return 0
    
    if args.validate_samples:
        if not validate_sample_files():
            success = False
    
    if not (args.generate_samples or args.validate_samples):
        # Run tests if not just generating/validating samples
        success = run_integration_tests(
            quick=args.quick,
            performance_only=args.performance,
            verbose=args.verbose
        )
    
    if success:
        print("\n✓ All operations completed successfully!")
        return 0
    else:
        print("\n✗ Some operations failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())