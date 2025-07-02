"""Custom exceptions for the D&D Encounter Tracker."""

from typing import Optional, List, Any


class EncounterTrackerError(Exception):
    """Base exception for encounter tracker.
    
    All custom exceptions inherit from this base class to provide
    consistent error handling and user feedback.
    """
    
    def __init__(self, message: str, details: Optional[str] = None, 
                 suggestions: Optional[List[str]] = None):
        """Initialize the exception.
        
        Args:
            message: Primary error message
            details: Additional error details
            suggestions: List of suggested actions to resolve the error
        """
        super().__init__(message)
        self.message = message
        self.details = details
        self.suggestions = suggestions or []
    
    def get_user_message(self) -> str:
        """Get a formatted user-friendly error message.
        
        Returns:
            Formatted error message with details and suggestions
        """
        parts = [f"Error: {self.message}"]
        
        if self.details:
            parts.append(f"Details: {self.details}")
        
        if self.suggestions:
            parts.append("Suggestions:")
            for suggestion in self.suggestions:
                parts.append(f"  - {suggestion}")
        
        return "\n".join(parts)


class CombatantNotFoundError(EncounterTrackerError):
    """Raised when combatant doesn't exist."""
    
    def __init__(self, combatant_name: str, available_combatants: Optional[List[str]] = None):
        """Initialize combatant not found error.
        
        Args:
            combatant_name: Name of the combatant that wasn't found
            available_combatants: List of available combatant names
        """
        message = f"Combatant '{combatant_name}' not found"
        
        suggestions = []
        if available_combatants is not None:
            if len(available_combatants) == 0:
                suggestions.append("Add combatants to the encounter first using 'add' command")
            else:
                suggestions.append("Check the spelling of the combatant name")
                suggestions.append("Use 'show' to see all combatants in the encounter")
                
                # Suggest similar names if any
                similar_names = self._find_similar_names(combatant_name, available_combatants)
                if similar_names:
                    suggestions.append(f"Did you mean: {', '.join(similar_names)}?")
        
        super().__init__(message, suggestions=suggestions)
        self.combatant_name = combatant_name
        self.available_combatants = available_combatants or []
    
    def _find_similar_names(self, target: str, names: List[str]) -> List[str]:
        """Find names similar to the target name.
        
        Args:
            target: Target name to match against
            names: List of available names
            
        Returns:
            List of similar names
        """
        target_lower = target.lower()
        similar = []
        
        for name in names:
            name_lower = name.lower()
            # Check for partial matches or similar spellings
            if (target_lower in name_lower or 
                name_lower in target_lower or
                self._levenshtein_distance(target_lower, name_lower) <= 2):
                similar.append(name)
        
        return similar[:3]  # Return at most 3 suggestions
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]


class InvalidHPValueError(EncounterTrackerError):
    """Raised for invalid HP modifications."""
    
    def __init__(self, hp_value: str, reason: str, current_hp: Optional[int] = None, 
                 max_hp: Optional[int] = None):
        """Initialize invalid HP value error.
        
        Args:
            hp_value: The invalid HP value that was provided
            reason: Reason why the value is invalid
            current_hp: Current HP of the combatant
            max_hp: Maximum HP of the combatant
        """
        message = f"Invalid HP value '{hp_value}': {reason}"
        
        details = None
        if current_hp is not None and max_hp is not None:
            details = f"Current HP: {current_hp}/{max_hp}"
        
        suggestions = [
            "Use absolute values (e.g., '25') to set HP directly",
            "Use additions (e.g., '+8') to add HP",
            "Use subtractions (e.g., '-12') to subtract HP",
            "HP cannot go below 0 or above maximum HP"
        ]
        
        super().__init__(message, details, suggestions)
        self.hp_value = hp_value
        self.reason = reason
        self.current_hp = current_hp
        self.max_hp = max_hp


class FileFormatError(EncounterTrackerError):
    """Raised for invalid file formats or file operations."""
    
    def __init__(self, filename: str, operation: str, reason: str):
        """Initialize file format error.
        
        Args:
            filename: Name of the file that caused the error
            operation: Operation being performed (load, save, etc.)
            reason: Reason for the error
        """
        message = f"Failed to {operation} file '{filename}': {reason}"
        
        suggestions = []
        if operation == "load":
            suggestions.extend([
                "Check that the file exists and is readable",
                "Verify the file is a valid JSON encounter file",
                "Use 'list' to see available encounter files"
            ])
        elif operation == "save":
            suggestions.extend([
                "Check that you have write permissions to the directory",
                "Ensure the filename is valid",
                "Make sure there's enough disk space"
            ])
        
        super().__init__(message, suggestions=suggestions)
        self.filename = filename
        self.operation = operation
        self.reason = reason


class EncounterNotLoadedError(EncounterTrackerError):
    """Raised when no encounter is active."""
    
    def __init__(self, operation: str = "perform this operation"):
        """Initialize encounter not loaded error.
        
        Args:
            operation: The operation that requires an active encounter
        """
        message = f"No encounter is currently loaded to {operation}"
        
        suggestions = [
            "Create a new encounter with 'new <name>'",
            "Load an existing encounter with 'load <filename>'",
            "Use 'list' to see available encounters"
        ]
        
        super().__init__(message, suggestions=suggestions)
        self.operation = operation


class ValidationError(EncounterTrackerError):
    """Raised when data validation fails."""
    
    def __init__(self, field: str, value: Any, reason: str, 
                 valid_examples: Optional[List[str]] = None):
        """Initialize validation error.
        
        Args:
            field: Name of the field that failed validation
            value: The invalid value
            reason: Reason for validation failure
            valid_examples: Examples of valid values
        """
        message = f"Invalid {field}: {reason}"
        details = f"Provided value: {value}"
        
        suggestions = []
        if valid_examples:
            suggestions.append(f"Valid examples: {', '.join(valid_examples)}")
        
        super().__init__(message, details, suggestions)
        self.field = field
        self.value = value
        self.reason = reason
        self.valid_examples = valid_examples or []


class DuplicateCombatantError(EncounterTrackerError):
    """Raised when trying to add a combatant with a name that already exists."""
    
    def __init__(self, combatant_name: str):
        """Initialize duplicate combatant error.
        
        Args:
            combatant_name: Name of the duplicate combatant
        """
        message = f"A combatant named '{combatant_name}' already exists in this encounter"
        
        suggestions = [
            "Use a different name for the combatant",
            "Add a number or descriptor to make the name unique (e.g., 'Goblin 1', 'Goblin 2')",
            "Remove the existing combatant first if you want to replace it"
        ]
        
        super().__init__(message, suggestions=suggestions)
        self.combatant_name = combatant_name


class NoteIndexError(EncounterTrackerError):
    """Raised when an invalid note index is provided."""
    
    def __init__(self, index: int, note_count: int, combatant_name: str):
        """Initialize note index error.
        
        Args:
            index: The invalid index
            note_count: Total number of notes for the combatant
            combatant_name: Name of the combatant
        """
        if note_count == 0:
            message = f"'{combatant_name}' has no notes"
            suggestions = [
                f"Add a note first with 'note add {combatant_name} \"<note text>\"'"
            ]
        else:
            message = f"Invalid note index {index} for '{combatant_name}'"
            details = f"Valid indices: 1 to {note_count}"
            suggestions = [
                f"Use 'note list {combatant_name}' to see all notes with their indices"
            ]
        
        super().__init__(message, 
                        details if note_count > 0 else None, 
                        suggestions)
        self.index = index
        self.note_count = note_count
        self.combatant_name = combatant_name


class InitiativeError(EncounterTrackerError):
    """Raised for initiative-related errors."""
    
    def __init__(self, message: str, current_initiative: Optional[int] = None):
        """Initialize initiative error.
        
        Args:
            message: Error message
            current_initiative: Current initiative value if applicable
        """
        details = None
        if current_initiative is not None:
            details = f"Current initiative: {current_initiative}"
        
        suggestions = [
            "Initiative values should be integers",
            "Common initiative range is 1-30, but any integer is valid",
            "Use 'show' to see current initiative order"
        ]
        
        super().__init__(message, details, suggestions)
        self.current_initiative = current_initiative


class CommandError(EncounterTrackerError):
    """Raised for command-line interface errors."""
    
    def __init__(self, command: str, reason: str, usage_example: Optional[str] = None):
        """Initialize command error.
        
        Args:
            command: The command that failed
            reason: Reason for the failure
            usage_example: Example of correct usage
        """
        message = f"Command '{command}' failed: {reason}"
        
        suggestions = []
        if usage_example:
            suggestions.append(f"Usage: {usage_example}")
        suggestions.append("Use --help with any command for detailed usage information")
        
        super().__init__(message, suggestions=suggestions)
        self.command = command
        self.reason = reason
        self.usage_example = usage_example