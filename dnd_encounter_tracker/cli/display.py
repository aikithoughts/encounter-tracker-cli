"""Display manager for formatting encounter and combatant output."""

from typing import List, Optional
from ..core.models import Combatant, Encounter
from .colors import formatter


class DisplayManager:
    """Handles formatted output for encounters and combatants."""
    
    def __init__(self):
        """Initialize display manager."""
        pass
    
    def show_encounter_summary(self, encounter: Encounter) -> str:
        """Display a summary of the encounter with initiative order.
        
        Args:
            encounter: The encounter to display
            
        Returns:
            Formatted encounter summary string
        """
        if not encounter.has_combatants():
            return f"{formatter.header('Encounter:')} {encounter.name}\n{formatter.dim('No combatants in encounter.')}"
        
        lines = [
            f"{formatter.header('Encounter:')} {formatter.bold(encounter.name)}",
            f"{formatter.subheader('Round:')} {formatter.bold(str(encounter.round_number))}",
            "",
            formatter.subheader("Initiative Order:")
        ]
        
        for i, combatant in enumerate(encounter.combatants):
            # Mark current turn with colored arrow
            if i == encounter.current_turn:
                turn_marker = formatter.bright_yellow(">>> ")
            else:
                turn_marker = "    "
            
            # Show note indicator
            note_indicator = " 📝" if combatant.has_notes() else ""
            
            # Format HP display with colors
            hp_current = combatant.current_hp
            hp_max = combatant.max_hp
            hp_ratio = hp_current / hp_max if hp_max > 0 else 0
            
            if hp_current == 0:
                hp_display = formatter.bright_red(f"{hp_current}/{hp_max} (DEAD)")
            elif hp_ratio <= 0.25:
                hp_display = formatter.red(f"{hp_current}/{hp_max} (CRITICAL)")
            elif hp_ratio <= 0.5:
                hp_display = formatter.yellow(f"{hp_current}/{hp_max}")
            else:
                hp_display = formatter.green(f"{hp_current}/{hp_max}")
            
            # Color combatant type
            type_colors = {
                'player': formatter.bright_blue,
                'monster': formatter.bright_red,
                'npc': formatter.bright_magenta,
                'unknown': formatter.dim
            }
            type_formatter = type_colors.get(combatant.combatant_type.lower(), formatter.dim)
            type_display = type_formatter(combatant.combatant_type.title())
            
            # Format initiative with color
            init_display = formatter.cyan(f"{combatant.initiative:2d}")
            
            line = f"{turn_marker}{init_display} | {combatant.name:<20} | HP: {hp_display:<25} | {type_display}{note_indicator}"
            lines.append(line)
        
        return "\n".join(lines)
    
    def show_combatant_details(self, combatant: Combatant) -> str:
        """Display detailed information about a specific combatant.
        
        Args:
            combatant: The combatant to display
            
        Returns:
            Formatted combatant details string
        """
        lines = [
            formatter.header(f"=== {combatant.name} ==="),
        ]
        
        # Color combatant type
        type_colors = {
            'player': formatter.bright_blue,
            'monster': formatter.bright_red,
            'npc': formatter.bright_magenta,
            'unknown': formatter.dim
        }
        type_formatter = type_colors.get(combatant.combatant_type.lower(), formatter.dim)
        lines.append(f"{formatter.bold('Type:')} {type_formatter(combatant.combatant_type.title())}")
        
        # Format initiative
        lines.append(f"{formatter.bold('Initiative:')} {formatter.cyan(str(combatant.initiative))}")
        
        # Format HP with colors
        hp_current = combatant.current_hp
        hp_max = combatant.max_hp
        hp_ratio = hp_current / hp_max if hp_max > 0 else 0
        
        if hp_current == 0:
            hp_display = formatter.bright_red(f"{hp_current}/{hp_max}")
        elif hp_ratio <= 0.25:
            hp_display = formatter.red(f"{hp_current}/{hp_max}")
        elif hp_ratio <= 0.5:
            hp_display = formatter.yellow(f"{hp_current}/{hp_max}")
        else:
            hp_display = formatter.green(f"{hp_current}/{hp_max}")
        
        lines.append(f"{formatter.bold('Hit Points:')} {hp_display}")
        
        # Status with colors
        if combatant.current_hp == 0:
            status = formatter.bright_red("DEAD")
        elif combatant.current_hp <= combatant.max_hp * 0.25:
            status = formatter.red("CRITICAL")
        else:
            status = formatter.green("Alive")
        
        lines.append(f"{formatter.bold('Status:')} {status}")
        
        # Display notes
        lines.append("")
        if combatant.has_notes():
            lines.append(formatter.bold("Notes:"))
            for i, note in enumerate(combatant.notes):
                lines.append(f"  {formatter.cyan(f'{i + 1}.')} {note}")
        else:
            lines.append(f"{formatter.bold('Notes:')} {formatter.dim('None')}")
        
        return "\n".join(lines)
    
    def show_notes_list(self, combatant: Combatant) -> str:
        """Display just the notes for a combatant.
        
        Args:
            combatant: The combatant whose notes to display
            
        Returns:
            Formatted notes list string
        """
        if not combatant.has_notes():
            return f"{formatter.bold(combatant.name)} {formatter.dim('has no notes.')}"
        
        lines = [f"{formatter.bold('Notes for')} {formatter.header(combatant.name)}:"]
        for i, note in enumerate(combatant.notes):
            lines.append(f"  {formatter.cyan(f'{i + 1}.')} {note}")
        
        return "\n".join(lines)
    
    def show_combatants_with_notes(self, encounter: Encounter) -> str:
        """Display all combatants that have notes.
        
        Args:
            encounter: The encounter to check
            
        Returns:
            Formatted list of combatants with notes
        """
        combatants_with_notes = [c for c in encounter.combatants if c.has_notes()]
        
        if not combatants_with_notes:
            return formatter.dim("No combatants have notes.")
        
        lines = [formatter.bold("Combatants with notes:")]
        for combatant in combatants_with_notes:
            note_count = len(combatant.notes)
            count_text = f"({note_count} note{'s' if note_count != 1 else ''})"
            lines.append(f"  {formatter.cyan('•')} {formatter.bold(combatant.name)} {formatter.dim(count_text)}")
        
        return "\n".join(lines)
    
    def show_initiative_order(self, combatants: List[Combatant], current_turn: Optional[int] = None) -> str:
        """Display combatants in initiative order.
        
        Args:
            combatants: List of combatants to display
            current_turn: Index of current turn (optional)
            
        Returns:
            Formatted initiative order string
        """
        if not combatants:
            return formatter.dim("No combatants to display.")
        
        lines = [formatter.subheader("Initiative Order:")]
        
        for i, combatant in enumerate(combatants):
            # Mark current turn with colored arrow
            if current_turn is not None and i == current_turn:
                turn_marker = formatter.bright_yellow(">>> ")
            else:
                turn_marker = "    "
            
            # Show note indicator
            note_indicator = " 📝" if combatant.has_notes() else ""
            
            # Format HP display with colors
            hp_current = combatant.current_hp
            hp_max = combatant.max_hp
            hp_ratio = hp_current / hp_max if hp_max > 0 else 0
            
            if hp_current == 0:
                hp_display = formatter.bright_red(f"{hp_current}/{hp_max}")
            elif hp_ratio <= 0.25:
                hp_display = formatter.red(f"{hp_current}/{hp_max}")
            elif hp_ratio <= 0.5:
                hp_display = formatter.yellow(f"{hp_current}/{hp_max}")
            else:
                hp_display = formatter.green(f"{hp_current}/{hp_max}")
            
            # Format initiative with color
            init_display = formatter.cyan(f"{combatant.initiative:2d}")
            
            line = f"{turn_marker}{init_display} | {combatant.name:<20} | HP: {hp_display:<20}{note_indicator}"
            lines.append(line)
        
        return "\n".join(lines)
    
    def format_note_management_help(self) -> str:
        """Display help for note management commands.
        
        Returns:
            Formatted help text for note management
        """
        return """
Note Management Commands:

  note add <combatant> <note_text>     Add a note to a combatant
  note list <combatant>                List all notes for a combatant
  note edit <combatant> <index> <text> Edit a note by index (1-based)
  note remove <combatant> <index>      Remove a note by index (1-based)
  note show                            Show all combatants with notes

Examples:
  note add Thorin "Blessed by cleric"
  note list Thorin
  note edit Thorin 1 "Blessed by cleric (+1 to all saves)"
  note remove Thorin 2
  note show

Note: Indices are 1-based (first note is index 1).
        """.strip()