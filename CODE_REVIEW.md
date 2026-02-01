# Code Review: D&D Encounter Tracker CLI

This document contains suggestions for improving code readability, testing, and addressing potential functionality issues.

---

## Table of Contents
1. [Code Readability](#code-readability)
2. [Testing Improvements](#testing-improvements)
3. [Functionality Issues](#functionality-issues)
4. [Summary](#summary)

---

## Code Readability

### 1. Duplicate HP Formatting Logic

**Files:** `display.py:44-56`, `display.py:103-114`, `display.py:204-216`

**Issue:** HP status color formatting is duplicated in three places: `show_encounter_summary()`, `show_combatant_details()`, and `show_initiative_order()`.

**Suggestion:** Extract into a reusable helper method:

```python
def _format_hp_display(self, combatant: Combatant) -> str:
    """Format HP with color based on health status."""
    hp_ratio = combatant.current_hp / combatant.max_hp if combatant.max_hp > 0 else 0

    if combatant.current_hp == 0:
        return formatter.bright_red(f"{combatant.current_hp}/{combatant.max_hp}")
    elif hp_ratio <= 0.25:
        return formatter.red(f"{combatant.current_hp}/{combatant.max_hp}")
    elif hp_ratio <= 0.5:
        return formatter.yellow(f"{combatant.current_hp}/{combatant.max_hp}")
    else:
        return formatter.green(f"{combatant.current_hp}/{combatant.max_hp}")
```

---

### 2. Duplicate Combatant Type Color Mapping

**Files:** `display.py:59-66`, `display.py:90-96`, `commands.py:269-275`

**Issue:** The same type-to-color mapping dictionary is defined multiple times.

**Suggestion:** Define as a class constant in `DisplayManager`:

```python
class DisplayManager:
    TYPE_COLORS = {
        'player': formatter.bright_blue,
        'monster': formatter.bright_red,
        'npc': formatter.bright_magenta,
        'unknown': formatter.dim
    }
```

---

### 3. Repeated Combatant Lookup Pattern with Error Handling

**Files:** `encounter_service.py:194-197`, `encounter_service.py:244-247`, `encounter_service.py:274-277`, `encounter_service.py:301-304`, `note_service.py:41-44`, `note_service.py:62-65`, etc.

**Issue:** The pattern of looking up a combatant and raising `CombatantNotFoundError` with available names is repeated ~15 times.

**Suggestion:** Extract into a helper method:

```python
def _get_combatant_or_raise(self, name: str) -> Combatant:
    """Get combatant by name or raise CombatantNotFoundError."""
    combatant = self.current_encounter.get_combatant(name)
    if not combatant:
        available_names = [c.name for c in self.current_encounter.combatants]
        raise CombatantNotFoundError(name, available_names)
    return combatant
```

---

### 4. Inconsistent `EncounterNotLoadedError` Message Patterns

**File:** `encounter_service.py`

**Issue:** Error messages for `EncounterNotLoadedError` are inconsistent:
- Line 85: `"No encounter is currently loaded"`
- Line 116: `"add combatant"`
- Line 172: `"No encounter is currently loaded"`
- Line 192: `"update hit points"`

**Suggestion:** Use a consistent format, preferring the action-based format:
```python
raise EncounterNotLoadedError("save encounter")
raise EncounterNotLoadedError("add combatant")
```

---

### 5. Magic Numbers for HP Thresholds

**Files:** `display.py:51-56`, `display.py:109-114`, `display.py:121-124`

**Issue:** HP threshold values (0.25, 0.5) are hardcoded magic numbers.

**Suggestion:** Define as class constants:
```python
class DisplayManager:
    HP_CRITICAL_THRESHOLD = 0.25
    HP_WOUNDED_THRESHOLD = 0.5
```

---

### 6. Long Method in `_parse_interactive_command`

**File:** `interactive.py:172-333`

**Issue:** This method is 161 lines with deeply nested if/elif chains, making it hard to read and maintain.

**Suggestion:** Use a command dispatch pattern:
```python
def _parse_interactive_command(self, args: List[str]) -> Optional[Namespace]:
    if not args:
        return None

    command = args[0]
    parser = self._command_parsers.get(command)

    if parser:
        return parser(args[1:])

    print(f"Unknown command: {command}")
    return None
```

---

### 7. Unused Import: `NoteIndexError` in `encounter_service.py`

**File:** `encounter_service.py:11`

**Issue:** `NoteIndexError` is imported but never used in the file.

**Suggestion:** Remove the unused import.

---

### 8. Empty `__init__` Method

**File:** `display.py:11-13`

**Issue:** The `__init__` method contains only `pass`.

**Suggestion:** Either remove it entirely (Python provides a default) or add a docstring explaining future initialization needs.

---

### 9. Type Hint Inconsistency

**File:** `interactive.py:172`

**Issue:** Return type is `Optional` without a type parameter.

**Current:** `def _parse_interactive_command(self, args: List[str]) -> Optional:`

**Should be:** `def _parse_interactive_command(self, args: List[str]) -> Optional[Namespace]:`

---

### 10. Inconsistent Error Handling in `_handle_save`

**File:** `commands.py:161-167`

**Issue:** Re-raises `FileFormatError` with string conversion of the original exception, losing exception chaining.

**Suggestion:** Use `raise ... from e` for proper exception chaining:
```python
except FileFormatError as e:
    raise FileFormatError(
        filename=args.filename,
        operation="save",
        reason=str(e)
    ) from e
```

---

## Testing Improvements

### 1. Missing Test Coverage for `NoteService`

**Issue:** The `NoteService` class (`note_service.py`) appears to have no dedicated test file, though some note functionality is tested via `EncounterService`.

**Suggestion:** Create `tests/test_note_service.py` with tests for:
- `search_notes()` with various search patterns
- `get_note_statistics()` with edge cases
- `clear_all_notes()` behavior

---

### 2. No Tests for CLI `aliases.py`

**Issue:** The `CommandAliases` and `InputValidator` classes have no dedicated unit tests.

**Suggestion:** Create `tests/test_aliases.py` covering:
- Alias resolution
- Typo corrections
- Contextual shortcuts
- Name validation edge cases
- HP value validation with warnings

---

### 3. Missing Tests for Display Formatting

**File:** `tests/test_display_manager.py`

**Issue:** Tests verify output but don't test edge cases like:
- Combatants with very long names (50+ chars)
- Notes with special characters
- ANSI color code stripping for non-TTY output

**Suggestion:** Add tests for boundary conditions and special characters.

---

### 4. No Integration Test for Full CLI Command Flow

**Issue:** Integration tests exist but don't test the actual CLI argument parsing through `main.py`.

**Suggestion:** Add end-to-end tests that invoke the CLI:
```python
def test_cli_full_workflow():
    result = subprocess.run(
        ['python', '-m', 'dnd_encounter_tracker', 'new', 'Test'],
        capture_output=True
    )
    assert result.returncode == 0
```

---

### 5. Incomplete Error Path Testing in `commands.py`

**Issue:** Some exception handlers in `commands.py` (e.g., `_handle_init` at line 405-406) are not explicitly tested.

**Suggestion:** Add tests for all exception handling paths in command handlers.

---

### 6. Test Fixtures Should Use `tmp_path`

**File:** `tests/test_data_persistence.py`

**Issue:** Tests create files in `encounters/` directory which may conflict with user data.

**Suggestion:** Use pytest's `tmp_path` fixture consistently:
```python
@pytest.fixture
def data_manager(tmp_path):
    return DataManager(str(tmp_path))
```

---

### 7. Missing Concurrent Access Tests

**Issue:** `DataManager` uses atomic file operations but there are no tests verifying behavior under concurrent access.

**Suggestion:** Add tests simulating concurrent read/write operations.

---

### 8. No Property-Based Testing

**Suggestion:** Consider adding `hypothesis` for property-based testing:
```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=1, max_value=1000))
def test_hp_update_always_clamps(hp_value):
    combatant = Combatant("Test", max_hp=100, current_hp=50, initiative=10)
    combatant.update_hp(str(hp_value))
    assert 0 <= combatant.current_hp <= combatant.max_hp
```

---

## Functionality Issues

### 1. Potential Race Condition in File Save

**File:** `persistence.py:59-65`

**Issue:** There's a small window between creating the backup and writing the temp file where a crash could leave the file system in an inconsistent state.

**Current flow:**
1. Create backup
2. Write to temp file
3. Rename temp to final

**Suggestion:** Consider using a write-ahead log pattern or ensure backup creation happens after successful temp file write.

---

### 2. Backup Cleanup May Delete Wrong Files

**File:** `persistence.py:345-352`

**Issue:** The backup grouping logic assumes filenames follow format `name_YYYYMMDD_HHMMSS.backup`. Encounters with underscores in names (e.g., `goblin_cave_20240101_120000.backup`) will be incorrectly grouped.

**Example:**
- `goblin_cave_20240101_120000.backup` would be parsed as base name `goblin` instead of `goblin_cave`

**Suggestion:** Use a more robust pattern or store backup metadata separately:
```python
# Use a regex that matches the timestamp pattern at the end
match = re.match(r'^(.+)_(\d{8}_\d{6})\.backup$', backup_file.stem)
```

---

### 3. Interactive Mode Doesn't Track `next` as Modifying Command

**File:** `interactive.py:151`

**Issue:** The `next` command advances turns but isn't included in `modifying_commands`, so `unsaved_changes` won't be set.

**Current:** `modifying_commands = ['new', 'add', 'remove', 'hp', 'init', 'note']`

**Should include:** `'next'` (and possibly `'load'` should reset the flag)

---

### 4. Tie-Breaker Value Not Properly Reset

**File:** `models.py:317-318`

**Issue:** When reordering combatants with same initiative, tie-breaker values are set but never reset when initiative changes. A combatant could retain an old tie-breaker value affecting sort order unexpectedly.

**Suggestion:** Reset `_tie_breaker` to 0 when `initiative` changes:
```python
def adjust_initiative(self, name: str, new_initiative: int) -> None:
    combatant = self.get_combatant(name)
    # ...
    combatant.initiative = new_initiative
    combatant._tie_breaker = 0  # Reset tie-breaker
    self.sort_by_initiative()
```

---

### 5. Case Sensitivity Inconsistency in Combatant Names

**Files:** Multiple

**Issue:** Combatant names are compared case-insensitively (`name.lower()`) but stored with original case. This can lead to confusing behavior:
- `add Thorin ...` then `add THORIN ...` fails with duplicate error
- But display shows "Thorin" not "THORIN"

**Suggestion:** Either normalize case on storage or document this behavior clearly.

---

### 6. No Validation for File Path Traversal

**File:** `persistence.py`

**Issue:** Filenames are not validated for path traversal attacks. A malicious filename like `../../../etc/passwd` could potentially access files outside the data directory.

**Suggestion:** Add path validation:
```python
def _validate_filename(self, filename: str) -> None:
    """Ensure filename doesn't escape data directory."""
    filepath = self.data_directory / filename
    # Resolve to absolute path and check it's within data_directory
    if not filepath.resolve().is_relative_to(self.data_directory.resolve()):
        raise ValidationError("filename", filename, "Invalid file path")
```

---

### 7. Memory Leak Potential in Large Encounters

**File:** `persistence.py:252-278`

**Issue:** `list_encounters_with_metadata()` loads every encounter fully into memory to get the name. For directories with many large encounter files, this could be slow and memory-intensive.

**Suggestion:** Parse just the `name` field without loading full combatant data:
```python
def _get_encounter_name_fast(self, filepath: Path) -> str:
    with open(filepath, 'r') as f:
        # Only parse until we find the name field
        data = json.load(f)
        return data.get("name", filepath.stem)
```

---

### 8. Missing Validation for Note Content Length

**File:** `models.py:85-94`

**Issue:** Notes can be arbitrarily long with no upper limit, potentially causing display issues or performance problems.

**Suggestion:** Add a reasonable length limit:
```python
MAX_NOTE_LENGTH = 500

def add_note(self, note: str) -> None:
    if len(note) > self.MAX_NOTE_LENGTH:
        raise ValidationError("note", note[:50] + "...",
            f"exceeds maximum length of {self.MAX_NOTE_LENGTH} characters")
```

---

### 9. `_clear_screen` Uses Unescaped Shell Command

**File:** `interactive.py:364-365`

**Issue:** `os.system('cls' if os.name == 'nt' else 'clear')` is safe here but using `os.system` is generally discouraged.

**Suggestion:** Use ANSI escape codes instead:
```python
def _clear_screen(self) -> None:
    """Clear the terminal screen."""
    print("\033[2J\033[H", end="")
```

---

### 10. Exception Silently Swallowed in `get_available_encounters`

**File:** `persistence.py:177-179`

**Issue:** All exceptions are caught and an empty list is returned, hiding potential issues.

**Suggestion:** Log the exception or only catch expected exceptions:
```python
except (OSError, IOError) as e:
    # Log or handle gracefully
    return []
```

---

### 11. Incomplete `backup` and `cleanup` Command Parsing

**File:** `interactive.py`

**Issue:** The interactive command parser doesn't handle `backup` or `cleanup` commands, but they exist in the CLI.

**Suggestion:** Add parsing for these commands in `_parse_interactive_command()`.

---

## Summary

### High Priority
1. **Fix backup filename parsing** - Could delete wrong backups (Issue #2 in Functionality)
2. **Add path traversal validation** - Security concern (Issue #6 in Functionality)
3. **Track `next` as modifying command** - Data loss risk (Issue #3 in Functionality)

### Medium Priority
1. Refactor duplicate HP/type color formatting code
2. Add tests for `NoteService` and `aliases.py`
3. Fix type hint in `interactive.py`
4. Reset tie-breaker on initiative change

### Low Priority
1. Extract repeated combatant lookup pattern
2. Use constants for HP thresholds
3. Refactor long `_parse_interactive_command` method
4. Add property-based testing

---

*Review completed: 2026-02-01*
