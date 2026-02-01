#!/bin/bash
# Script to create GitHub issues from CODE_REVIEW.md
# Run this from the repository root: ./create_issues.sh

set -e

echo "Creating GitHub issues for D&D Encounter Tracker..."
echo ""

# Issue 1: Security - Path traversal validation
echo "Creating issue 1/10: Security - Path traversal validation"
gh issue create \
  --title "Security: Add path traversal validation for filenames" \
  --label "security,bug,high-priority" \
  --body "## Summary
Filenames passed to \`DataManager\` are not validated for path traversal attacks. A malicious filename like \`../../../etc/passwd\` could potentially access files outside the data directory.

## Location
- \`dnd_encounter_tracker/data/persistence.py\`

## Details
From CODE_REVIEW.md (Functionality Issue #6):

The \`save_to_file()\`, \`load_from_file()\`, and other file operations accept filenames without validating that the resolved path stays within the intended data directory.

## Suggested Fix
\`\`\`python
def _validate_filename(self, filename: str) -> None:
    \"\"\"Ensure filename doesn't escape data directory.\"\"\"
    filepath = self.data_directory / filename
    # Resolve to absolute path and check it's within data_directory
    if not filepath.resolve().is_relative_to(self.data_directory.resolve()):
        raise ValidationError(\"filename\", filename, \"Invalid file path\")
\`\`\`

Call this validation method at the start of all file operations.

## Priority
**High** - Security vulnerability

## References
- CODE_REVIEW.md - Functionality Issues #6"

echo ""

# Issue 2: Bug - Backup filename parsing
echo "Creating issue 2/10: Bug - Backup filename parsing"
gh issue create \
  --title "Bug: Backup filename parsing incorrectly groups files with underscores" \
  --label "bug,high-priority" \
  --body "## Summary
The backup cleanup logic incorrectly parses filenames that contain underscores, potentially deleting wrong backup files.

## Location
- \`dnd_encounter_tracker/data/persistence.py:345-352\`

## Details
From CODE_REVIEW.md (Functionality Issue #2):

The backup grouping logic assumes filenames follow format \`name_YYYYMMDD_HHMMSS.backup\`. Encounters with underscores in names (e.g., \`goblin_cave_20240101_120000.backup\`) will be incorrectly grouped.

**Example:**
- \`goblin_cave_20240101_120000.backup\` would be parsed as base name \`goblin\` instead of \`goblin_cave\`

## Suggested Fix
\`\`\`python
# Use a regex that matches the timestamp pattern at the end
import re
match = re.match(r'^(.+)_(\d{8}_\d{6})\.backup$', backup_file.stem)
if match:
    base_name = match.group(1)
\`\`\`

## Priority
**High** - Could delete wrong backup files

## References
- CODE_REVIEW.md - Functionality Issues #2"

echo ""

# Issue 3: Bug - Interactive mode unsaved changes
echo "Creating issue 3/10: Bug - Interactive mode unsaved changes"
gh issue create \
  --title "Bug: Interactive mode doesn't track all modifying commands" \
  --label "bug,high-priority" \
  --body "## Summary
The interactive mode doesn't track all commands that modify encounter state, leading to potential data loss when users exit without saving.

## Location
- \`dnd_encounter_tracker/cli/interactive.py:151\`

## Details
From CODE_REVIEW.md (Functionality Issues #3 and #11):

### Issue 1: \`next\` command not tracked
The \`next\` command advances turns but isn't included in \`modifying_commands\`, so \`unsaved_changes\` won't be set.

**Current:**
\`\`\`python
modifying_commands = ['new', 'add', 'remove', 'hp', 'init', 'note']
\`\`\`

**Should include:** \`'next'\`

### Issue 2: Missing command parsers
The interactive command parser doesn't handle \`backup\` or \`cleanup\` commands, but they exist in the CLI.

## Suggested Fix
1. Add \`'next'\` to \`modifying_commands\`
2. Add parsing for \`backup\` and \`cleanup\` in \`_parse_interactive_command()\`
3. Consider resetting \`unsaved_changes\` flag on \`load\`

## Priority
**High** - Data loss risk

## References
- CODE_REVIEW.md - Functionality Issues #3, #11"

echo ""

# Issue 4: Bug - Tie-breaker and initiative edge cases
echo "Creating issue 4/10: Bug - Tie-breaker and initiative edge cases"
gh issue create \
  --title "Bug: Tie-breaker values not reset when initiative changes" \
  --label "bug" \
  --body "## Summary
When a combatant's initiative is changed, their tie-breaker value is not reset, which can cause unexpected sort order behavior.

## Location
- \`dnd_encounter_tracker/core/models.py:269-282\`

## Details
From CODE_REVIEW.md (Functionality Issues #4 and #5):

### Issue 1: Stale tie-breaker values
When reordering combatants with same initiative, tie-breaker values are set but never reset when initiative changes. A combatant could retain an old tie-breaker value affecting sort order unexpectedly.

### Issue 2: Race condition in file save
There's a small window between creating the backup and writing the temp file where a crash could leave the file system in an inconsistent state.

## Suggested Fix
Reset \`_tie_breaker\` to 0 when \`initiative\` changes:

\`\`\`python
def adjust_initiative(self, name: str, new_initiative: int) -> None:
    combatant = self.get_combatant(name)
    # ...
    combatant.initiative = new_initiative
    combatant._tie_breaker = 0  # Reset tie-breaker
    self.sort_by_initiative()
\`\`\`

## Priority
**Medium**

## References
- CODE_REVIEW.md - Functionality Issues #4, #5"

echo ""

# Issue 5: Refactor - DRY violations in display code
echo "Creating issue 5/10: Refactor - DRY violations in display code"
gh issue create \
  --title "Refactor: Extract duplicated HP and type color formatting" \
  --label "refactor,code-quality" \
  --body "## Summary
HP status color formatting and combatant type color mapping are duplicated in multiple places.

## Locations
- \`dnd_encounter_tracker/cli/display.py:44-56\` (HP formatting)
- \`dnd_encounter_tracker/cli/display.py:103-114\` (HP formatting)
- \`dnd_encounter_tracker/cli/display.py:204-216\` (HP formatting)
- \`dnd_encounter_tracker/cli/display.py:59-66\` (type colors)
- \`dnd_encounter_tracker/cli/display.py:90-96\` (type colors)
- \`dnd_encounter_tracker/cli/commands.py:269-275\` (type colors)

## Details
From CODE_REVIEW.md (Readability Issues #1, #2, #5):

### HP Formatting Duplication
The same HP color logic appears in \`show_encounter_summary()\`, \`show_combatant_details()\`, and \`show_initiative_order()\`.

### Type Color Duplication
The same type-to-color mapping dictionary is defined multiple times.

### Magic Numbers
HP threshold values (0.25, 0.5) are hardcoded.

## Suggested Fix
\`\`\`python
class DisplayManager:
    HP_CRITICAL_THRESHOLD = 0.25
    HP_WOUNDED_THRESHOLD = 0.5

    TYPE_COLORS = {
        'player': formatter.bright_blue,
        'monster': formatter.bright_red,
        'npc': formatter.bright_magenta,
        'unknown': formatter.dim
    }

    def _format_hp_display(self, combatant: Combatant) -> str:
        \"\"\"Format HP with color based on health status.\"\"\"
        hp_ratio = combatant.current_hp / combatant.max_hp if combatant.max_hp > 0 else 0

        if combatant.current_hp == 0:
            return formatter.bright_red(f\"{combatant.current_hp}/{combatant.max_hp}\")
        elif hp_ratio <= self.HP_CRITICAL_THRESHOLD:
            return formatter.red(f\"{combatant.current_hp}/{combatant.max_hp}\")
        elif hp_ratio <= self.HP_WOUNDED_THRESHOLD:
            return formatter.yellow(f\"{combatant.current_hp}/{combatant.max_hp}\")
        else:
            return formatter.green(f\"{combatant.current_hp}/{combatant.max_hp}\")
\`\`\`

## References
- CODE_REVIEW.md - Code Readability #1, #2, #5"

echo ""

# Issue 6: Refactor - Extract common patterns
echo "Creating issue 6/10: Refactor - Extract common patterns"
gh issue create \
  --title "Refactor: Extract repeated combatant lookup and error handling patterns" \
  --label "refactor,code-quality" \
  --body "## Summary
The pattern of looking up a combatant and raising \`CombatantNotFoundError\` with available names is repeated ~15 times across the codebase.

## Locations
- \`dnd_encounter_tracker/core/encounter_service.py:194-197\`
- \`dnd_encounter_tracker/core/encounter_service.py:244-247\`
- \`dnd_encounter_tracker/core/encounter_service.py:274-277\`
- \`dnd_encounter_tracker/core/encounter_service.py:301-304\`
- \`dnd_encounter_tracker/core/note_service.py:41-44\`
- \`dnd_encounter_tracker/core/note_service.py:62-65\`
- And more...

## Details
From CODE_REVIEW.md (Readability Issues #3, #4):

### Repeated Lookup Pattern
\`\`\`python
combatant = self.current_encounter.get_combatant(combatant_name)
if not combatant:
    available_names = [c.name for c in self.current_encounter.combatants]
    raise CombatantNotFoundError(combatant_name, available_names)
\`\`\`

### Inconsistent Error Messages
Error messages for \`EncounterNotLoadedError\` are inconsistent:
- Line 85: \`\"No encounter is currently loaded\"\`
- Line 116: \`\"add combatant\"\`
- Line 172: \`\"No encounter is currently loaded\"\`
- Line 192: \`\"update hit points\"\`

## Suggested Fix
\`\`\`python
def _get_combatant_or_raise(self, name: str) -> Combatant:
    \"\"\"Get combatant by name or raise CombatantNotFoundError.\"\"\"
    combatant = self.current_encounter.get_combatant(name)
    if not combatant:
        available_names = [c.name for c in self.current_encounter.combatants]
        raise CombatantNotFoundError(name, available_names)
    return combatant
\`\`\`

Use consistent action-based format for EncounterNotLoadedError:
\`\`\`python
raise EncounterNotLoadedError(\"save encounter\")
raise EncounterNotLoadedError(\"add combatant\")
\`\`\`

## References
- CODE_REVIEW.md - Code Readability #3, #4"

echo ""

# Issue 7: Refactor - Code cleanup
echo "Creating issue 7/10: Refactor - Code cleanup"
gh issue create \
  --title "Refactor: Minor code cleanup items" \
  --label "refactor,code-quality,good-first-issue" \
  --body "## Summary
Collection of minor code cleanup items that improve code quality.

## Items

### 1. Unused Import (Readability #7)
**File:** \`dnd_encounter_tracker/core/encounter_service.py:11\`

\`NoteIndexError\` is imported but never used.

### 2. Empty __init__ Method (Readability #8)
**File:** \`dnd_encounter_tracker/cli/display.py:11-13\`

The \`__init__\` method contains only \`pass\`. Either remove it or add documentation.

### 3. Incomplete Type Hint (Readability #9)
**File:** \`dnd_encounter_tracker/cli/interactive.py:172\`

**Current:** \`def _parse_interactive_command(self, args: List[str]) -> Optional:\`
**Should be:** \`def _parse_interactive_command(self, args: List[str]) -> Optional[Namespace]:\`

### 4. Exception Chaining (Readability #10)
**File:** \`dnd_encounter_tracker/cli/commands.py:161-167\`

Re-raises \`FileFormatError\` with string conversion, losing exception chaining.

**Fix:** Use \`raise ... from e\` for proper exception chaining.

### 5. Long Method (Readability #6)
**File:** \`dnd_encounter_tracker/cli/interactive.py:172-333\`

The \`_parse_interactive_command\` method is 161 lines. Consider using a command dispatch pattern.

### 6. os.system for clear screen (Functionality #9)
**File:** \`dnd_encounter_tracker/cli/interactive.py:364-365\`

Use ANSI escape codes instead:
\`\`\`python
def _clear_screen(self) -> None:
    print(\"\\033[2J\\033[H\", end=\"\")
\`\`\`

### 7. Silent exception swallowing (Functionality #10)
**File:** \`dnd_encounter_tracker/data/persistence.py:177-179\`

All exceptions are caught and an empty list is returned. Only catch expected exceptions.

## References
- CODE_REVIEW.md - Code Readability #6-10, Functionality #9-10"

echo ""

# Issue 8: Testing - Add missing test coverage
echo "Creating issue 8/10: Testing - Add missing test coverage"
gh issue create \
  --title "Testing: Add missing test coverage for NoteService, aliases, and CLI" \
  --label "testing,enhancement" \
  --body "## Summary
Several components lack dedicated test coverage.

## Missing Test Areas

### 1. NoteService (Testing #1)
**File:** \`dnd_encounter_tracker/core/note_service.py\`

The \`NoteService\` class has no dedicated test file. Create \`tests/test_note_service.py\` with tests for:
- \`search_notes()\` with various search patterns
- \`get_note_statistics()\` with edge cases
- \`clear_all_notes()\` behavior

### 2. CommandAliases and InputValidator (Testing #2)
**File:** \`dnd_encounter_tracker/cli/aliases.py\`

No dedicated unit tests exist. Create \`tests/test_aliases.py\` covering:
- Alias resolution
- Typo corrections
- Contextual shortcuts
- Name validation edge cases
- HP value validation with warnings

### 3. Display Edge Cases (Testing #3)
**File:** \`tests/test_display_manager.py\`

Add tests for:
- Combatants with very long names (50+ chars)
- Notes with special characters
- ANSI color code stripping for non-TTY output

### 4. CLI End-to-End Tests (Testing #4)
Add tests that invoke the actual CLI:
\`\`\`python
def test_cli_full_workflow():
    result = subprocess.run(
        ['python', '-m', 'dnd_encounter_tracker', 'new', 'Test'],
        capture_output=True
    )
    assert result.returncode == 0
\`\`\`

### 5. Command Handler Error Paths (Testing #5)
Some exception handlers in \`commands.py\` (e.g., \`_handle_init\` at line 405-406) are not explicitly tested.

## References
- CODE_REVIEW.md - Testing Improvements #1-5"

echo ""

# Issue 9: Testing - Improve test infrastructure
echo "Creating issue 9/10: Testing - Improve test infrastructure"
gh issue create \
  --title "Testing: Improve test infrastructure and isolation" \
  --label "testing,enhancement" \
  --body "## Summary
Test infrastructure improvements for better isolation and coverage.

## Items

### 1. Use tmp_path Consistently (Testing #6)
**File:** \`tests/test_data_persistence.py\`

Tests create files in \`encounters/\` directory which may conflict with user data.

**Fix:** Use pytest's \`tmp_path\` fixture consistently:
\`\`\`python
@pytest.fixture
def data_manager(tmp_path):
    return DataManager(str(tmp_path))
\`\`\`

### 2. Concurrent Access Tests (Testing #7)
\`DataManager\` uses atomic file operations but there are no tests verifying behavior under concurrent access.

Add tests simulating concurrent read/write operations.

### 3. Property-Based Testing (Testing #8)
Consider adding \`hypothesis\` for property-based testing:
\`\`\`python
from hypothesis import given, strategies as st

@given(st.integers(min_value=1, max_value=1000))
def test_hp_update_always_clamps(hp_value):
    combatant = Combatant(\"Test\", max_hp=100, current_hp=50, initiative=10)
    combatant.update_hp(str(hp_value))
    assert 0 <= combatant.current_hp <= combatant.max_hp
\`\`\`

## References
- CODE_REVIEW.md - Testing Improvements #6-8"

echo ""

# Issue 10: Enhancement - Input validation
echo "Creating issue 10/10: Enhancement - Input validation"
gh issue create \
  --title "Enhancement: Improve input validation for notes and names" \
  --label "enhancement" \
  --body "## Summary
Add validation for edge cases in user input that could cause issues.

## Items

### 1. Note Content Length (Functionality #8)
**File:** \`dnd_encounter_tracker/core/models.py:85-94\`

Notes can be arbitrarily long with no upper limit, potentially causing display issues or performance problems.

**Suggested Fix:**
\`\`\`python
MAX_NOTE_LENGTH = 500

def add_note(self, note: str) -> None:
    if len(note) > self.MAX_NOTE_LENGTH:
        raise ValidationError(\"note\", note[:50] + \"...\",
            f\"exceeds maximum length of {self.MAX_NOTE_LENGTH} characters\")
\`\`\`

### 2. Case Sensitivity Inconsistency (Functionality #5)
**Files:** Multiple

Combatant names are compared case-insensitively (\`name.lower()\`) but stored with original case. This can lead to confusing behavior:
- \`add Thorin ...\` then \`add THORIN ...\` fails with duplicate error
- But display shows \"Thorin\" not \"THORIN\"

**Suggested Fix:** Either normalize case on storage or document this behavior clearly.

### 3. Memory Usage with Large Encounters (Functionality #7)
**File:** \`dnd_encounter_tracker/data/persistence.py:252-278\`

\`list_encounters_with_metadata()\` loads every encounter fully into memory to get the name.

**Suggested Fix:** Parse just the \`name\` field without loading full combatant data.

## References
- CODE_REVIEW.md - Functionality Issues #5, #7, #8"

echo ""
echo "Done! Created 10 issues."
echo "View them at: gh issue list"
