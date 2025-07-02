"""Command aliases and shortcuts for improved user experience."""

from typing import Dict, List, Optional, Tuple
import re


class CommandAliases:
    """Manages command aliases and shortcuts."""
    
    def __init__(self):
        """Initialize command aliases."""
        self.aliases = {
            # Encounter management aliases
            'create': 'new',
            'l': 'load',
            'open': 'load',
            's': 'save',
            'write': 'save',
            'ls': 'list',
            'dir': 'list',
            
            # Combatant management aliases
            'a': 'add',
            'r': 'remove',
            'rm': 'remove',
            'del': 'remove',
            'delete': 'remove',
            'health': 'hp',
            'damage': 'hp',
            'heal': 'hp',
            'initiative': 'init',
            
            # Display aliases
            'display': 'show',
            'view': 'show',
            'status': 'show',
            'c': 'combatant',
            'char': 'combatant',
            'character': 'combatant',
            'next-turn': 'next',
            'advance': 'next',
            
            # Note aliases
            'notes': 'note',
            'comment': 'note',
            'comments': 'note',
            
            # Help aliases
            '?': 'help',
            'man': 'help',
            
            # Interactive aliases
            'int': 'interactive',
            'shell': 'interactive',
            'repl': 'interactive',
            
            # Exit aliases (for interactive mode)
            'q': 'quit',
            'exit': 'quit',
            'bye': 'quit',
        }
        
        # Common typos and corrections
        self.typo_corrections = {
            'ad': 'add',
            'aadd': 'add',
            'remov': 'remove',
            'removve': 'remove',
            'sav': 'save',
            'savve': 'save',
            'loa': 'load',
            'loaad': 'load',
            'sho': 'show',
            'shwo': 'show',
            'nex': 'next',
            'nextt': 'next',
            'hel': 'help',
            'halp': 'help',
            'hlep': 'help',
            'initt': 'init',
            'inititive': 'init',
            'combatan': 'combatant',
            'combattant': 'combatant',
            'lis': 'list',
            'lst': 'list',
            'stat': 'show',
            'stats': 'show',
            'not': 'note',
            'nots': 'note',
            'quit': 'exit',
            'qui': 'quit',
            'exti': 'exit',
        }
        
        # Contextual shortcuts
        self.contextual_shortcuts = {
            # HP shortcuts
            'hurt': ('hp', '-'),
            'damage': ('hp', '-'),
            'heal': ('hp', '+'),
            'restore': ('hp', '+'),
            'kill': ('hp', '0'),
            'dead': ('hp', '0'),
            'revive': ('hp', '1'),
            'ko': ('hp', '0'),
            'unconscious': ('hp', '0'),
            'stabilize': ('hp', '1'),
            
            # Initiative shortcuts
            'fast': ('init', '+5'),
            'slow': ('init', '-5'),
            'first': ('init', '30'),
            'last': ('init', '1'),
            'delay': ('init', '-10'),
            'ready': ('init', '+0'),  # Placeholder for ready actions
            
            # Combat state shortcuts
            'down': ('hp', '0'),
            'up': ('hp', '1'),
            'dying': ('hp', '0'),
            'stable': ('hp', '1'),
        }
    
    def resolve_alias(self, command: str) -> str:
        """Resolve a command alias to its full command.
        
        Args:
            command: Command or alias to resolve
            
        Returns:
            Resolved command name
        """
        command_lower = command.lower().strip()
        
        # Check direct aliases first
        if command_lower in self.aliases:
            return self.aliases[command_lower]
        
        # Check typo corrections
        if command_lower in self.typo_corrections:
            return self.typo_corrections[command_lower]
        
        # Return original command if no alias found
        return command
    
    def get_suggestions(self, invalid_command: str) -> List[str]:
        """Get command suggestions for an invalid command.
        
        Args:
            invalid_command: The invalid command entered
            
        Returns:
            List of suggested commands
        """
        invalid_lower = invalid_command.lower().strip()
        suggestions = []
        
        # Check if it's a typo correction
        if invalid_lower in self.typo_corrections:
            suggestions.append(self.typo_corrections[invalid_lower])
        
        # Find similar commands using simple string matching
        all_commands = set(self.aliases.values()) | set(self.aliases.keys())
        
        for command in all_commands:
            # Exact substring match
            if invalid_lower in command or command in invalid_lower:
                suggestions.append(command)
            # Similar length and characters
            elif self._similarity_score(invalid_lower, command) > 0.6:
                suggestions.append(command)
        
        # Remove duplicates and limit suggestions
        return list(set(suggestions))[:5]
    
    def _similarity_score(self, str1: str, str2: str) -> float:
        """Calculate similarity score between two strings.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score between 0 and 1
        """
        if not str1 or not str2:
            return 0.0
        
        # Simple character overlap scoring
        set1 = set(str1.lower())
        set2 = set(str2.lower())
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def expand_shorthand(self, args: List[str]) -> List[str]:
        """Expand shorthand notation in command arguments.
        
        Args:
            args: List of command arguments
            
        Returns:
            Expanded arguments list
        """
        if not args:
            return args
        
        expanded = []
        
        for arg in args:
            # HP shorthand expansion
            if re.match(r'^[+-]\d+$', arg):
                # This is a relative HP change, keep as-is
                expanded.append(arg)
            elif re.match(r'^\d+$', arg):
                # This is an absolute value, keep as-is
                expanded.append(arg)
            elif arg.lower() in ['dead', 'kill', 'ko']:
                expanded.append('0')
            elif arg.lower() in ['full', 'max', 'heal']:
                # This would need context to resolve properly
                expanded.append(arg)
            else:
                expanded.append(arg)
        
        return expanded
    
    def get_command_help(self, command: str) -> Optional[str]:
        """Get quick help for a command.
        
        Args:
            command: Command to get help for
            
        Returns:
            Quick help text or None if not available
        """
        help_text = {
            'new': 'Create a new encounter: new "Encounter Name"',
            'load': 'Load an encounter: load filename',
            'save': 'Save current encounter: save filename',
            'list': 'List saved encounters: list [--detailed]',
            'add': 'Add combatant: add Name HP Initiative [Type]',
            'remove': 'Remove combatant: remove Name',
            'hp': 'Update HP: hp Name <value|+value|-value>',
            'init': 'Set initiative: init Name Value',
            'show': 'Display encounter: show [--details]',
            'combatant': 'Show combatant details: combatant Name',
            'next': 'Advance to next turn: next',
            'note': 'Manage notes: note <add|list|edit|remove|show> ...',
            'help': 'Show help: help [topic]',
            'interactive': 'Start interactive mode: interactive',
        }
        
        resolved_command = self.resolve_alias(command)
        return help_text.get(resolved_command)
    
    def get_all_aliases(self) -> Dict[str, str]:
        """Get all available aliases.
        
        Returns:
            Dictionary of aliases and their resolved commands
        """
        return self.aliases.copy()


class InputValidator:
    """Validates and suggests corrections for user input."""
    
    def __init__(self):
        """Initialize input validator."""
        self.valid_combatant_types = ['player', 'monster', 'npc', 'unknown']
        self.common_names = [
            # Common player names
            'thorin', 'legolas', 'gimli', 'aragorn', 'gandalf',
            'frodo', 'sam', 'merry', 'pippin', 'boromir',
            # Common monster names
            'goblin', 'orc', 'troll', 'dragon', 'skeleton',
            'zombie', 'spider', 'wolf', 'bear', 'bandit',
        ]
    
    def validate_combatant_name(self, name: str) -> Tuple[bool, Optional[str]]:
        """Validate a combatant name.
        
        Args:
            name: Name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Combatant name cannot be empty"
        
        if len(name.strip()) > 50:
            return False, "Combatant name too long (max 50 characters)"
        
        # Check for potentially problematic characters
        if any(char in name for char in ['|', '\n', '\t']):
            return False, "Combatant name contains invalid characters"
        
        return True, None
    
    def validate_hp_value(self, value: str, current_hp: Optional[int] = None, max_hp: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """Validate an HP value.
        
        Args:
            value: HP value to validate
            current_hp: Current HP for context
            max_hp: Maximum HP for context
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value or not value.strip():
            return False, "HP value cannot be empty"
        
        value = value.strip()
        
        # Check for valid HP formats
        if re.match(r'^[+-]?\d+$', value):
            try:
                num_value = int(value)
                
                # Additional validation with context
                if current_hp is not None and max_hp is not None:
                    if value.startswith(('+', '-')):
                        # Relative change
                        new_hp = current_hp + num_value
                        if new_hp < 0:
                            return True, f"Warning: This would set HP below 0 (will be clamped to 0)"
                        elif new_hp > max_hp:
                            return True, f"Warning: This would exceed max HP (will be clamped to {max_hp})"
                    else:
                        # Absolute value
                        if num_value > max_hp:
                            return True, f"Warning: This exceeds max HP of {max_hp}"
                        elif num_value == 0:
                            return True, "Warning: This will set the combatant to 0 HP (unconscious/dead)"
                
                # Warn about very large values
                if abs(num_value) > 500:
                    return True, f"Warning: Very large HP value ({num_value}). Double-check this is correct."
                
                return True, None
            except ValueError:
                return False, "HP value must be a number"
        
        # Check for common shortcuts and mistakes
        if value.lower() in ['dead', 'kill', 'ko', 'unconscious', 'down', 'dying']:
            return True, "Tip: Use '0' to set HP to zero"
        elif value.lower() in ['full', 'max']:
            if max_hp is not None:
                return True, f"Tip: Use '{max_hp}' to set to maximum HP"
            else:
                return False, "Use the actual maximum HP value"
        elif value.lower() in ['heal', 'restore']:
            return False, "Use +amount for healing (e.g., +8)"
        elif value.lower() in ['hurt', 'damage']:
            return False, "Use -amount for damage (e.g., -12)"
        
        return False, f"Invalid HP format. Use: number (25), +number (+8), or -number (-12)"
    
    def validate_initiative_value(self, value: str) -> Tuple[bool, Optional[str]]:
        """Validate an initiative value.
        
        Args:
            value: Initiative value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value or not value.strip():
            return False, "Initiative value cannot be empty"
        
        try:
            init_value = int(value.strip())
            
            if init_value < -10:
                return True, "Warning: Very low initiative (below -10)"
            elif init_value > 30:
                return True, "Warning: Very high initiative (above 30)"
            
            return True, None
        except ValueError:
            return False, "Initiative must be a whole number"
    
    def validate_combatant_type(self, combatant_type: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate a combatant type.
        
        Args:
            combatant_type: Type to validate
            
        Returns:
            Tuple of (is_valid, corrected_type, error_message)
        """
        if not combatant_type:
            return True, 'unknown', None
        
        type_lower = combatant_type.lower().strip()
        
        # Direct match
        if type_lower in self.valid_combatant_types:
            return True, type_lower, None
        
        # Common aliases
        type_aliases = {
            'pc': 'player',
            'char': 'player',
            'character': 'player',
            'hero': 'player',
            'mob': 'monster',
            'enemy': 'monster',
            'creature': 'monster',
            'beast': 'monster',
            'nonplayer': 'npc',
            'non-player': 'npc',
        }
        
        if type_lower in type_aliases:
            return True, type_aliases[type_lower], None
        
        # Suggest closest match
        suggestions = []
        for valid_type in self.valid_combatant_types:
            if type_lower in valid_type or valid_type in type_lower:
                suggestions.append(valid_type)
        
        if suggestions:
            return False, None, f"Invalid type '{combatant_type}'. Did you mean: {', '.join(suggestions)}?"
        
        return False, None, f"Invalid type '{combatant_type}'. Valid types: {', '.join(self.valid_combatant_types)}"
    
    def suggest_name_completion(self, partial_name: str, existing_names: List[str]) -> List[str]:
        """Suggest name completions based on partial input.
        
        Args:
            partial_name: Partial name entered
            existing_names: List of existing combatant names
            
        Returns:
            List of suggested completions
        """
        if not partial_name:
            return []
        
        partial_lower = partial_name.lower()
        suggestions = []
        
        # Check existing names first
        for name in existing_names:
            if name.lower().startswith(partial_lower):
                suggestions.append(name)
        
        # Check common names
        for name in self.common_names:
            if name.startswith(partial_lower) and name not in [s.lower() for s in suggestions]:
                suggestions.append(name.title())
        
        return suggestions[:5]  # Limit to 5 suggestions


# Global instances
aliases = CommandAliases()
validator = InputValidator()