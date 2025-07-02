"""Color and formatting utilities for CLI output."""

import os
import sys
from typing import Optional


class Colors:
    """ANSI color codes for terminal output."""
    
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    STRIKETHROUGH = '\033[9m'
    
    # Reset
    RESET = '\033[0m'
    
    @classmethod
    def is_supported(cls) -> bool:
        """Check if color output is supported.
        
        Returns:
            True if colors are supported, False otherwise
        """
        # Check if we're in a terminal that supports colors
        if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
            return False
        
        # Check environment variables
        if os.environ.get('NO_COLOR'):
            return False
        
        if os.environ.get('FORCE_COLOR'):
            return True
        
        # Check TERM environment variable
        term = os.environ.get('TERM', '').lower()
        if 'color' in term or term in ['xterm', 'xterm-256color', 'screen', 'tmux']:
            return True
        
        # Windows terminal detection
        if sys.platform == 'win32':
            try:
                import colorama
                colorama.init()
                return True
            except ImportError:
                # Try to enable ANSI support on Windows 10+
                try:
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                    return True
                except:
                    return False
        
        return False


class ColorFormatter:
    """Utility class for applying colors and formatting to text."""
    
    def __init__(self, use_colors: Optional[bool] = None):
        """Initialize color formatter.
        
        Args:
            use_colors: Whether to use colors (auto-detect if None)
        """
        self.use_colors = use_colors if use_colors is not None else Colors.is_supported()
    
    def format(self, text: str, color: str = '', style: str = '') -> str:
        """Apply color and style formatting to text.
        
        Args:
            text: Text to format
            color: Color code to apply
            style: Style code to apply
            
        Returns:
            Formatted text string
        """
        if not self.use_colors:
            return text
        
        return f"{style}{color}{text}{Colors.RESET}"
    
    def red(self, text: str, bold: bool = False) -> str:
        """Format text in red."""
        style = Colors.BOLD if bold else ''
        return self.format(text, Colors.RED, style)
    
    def green(self, text: str, bold: bool = False) -> str:
        """Format text in green."""
        style = Colors.BOLD if bold else ''
        return self.format(text, Colors.GREEN, style)
    
    def yellow(self, text: str, bold: bool = False) -> str:
        """Format text in yellow."""
        style = Colors.BOLD if bold else ''
        return self.format(text, Colors.YELLOW, style)
    
    def blue(self, text: str, bold: bool = False) -> str:
        """Format text in blue."""
        style = Colors.BOLD if bold else ''
        return self.format(text, Colors.BLUE, style)
    
    def magenta(self, text: str, bold: bool = False) -> str:
        """Format text in magenta."""
        style = Colors.BOLD if bold else ''
        return self.format(text, Colors.MAGENTA, style)
    
    def cyan(self, text: str, bold: bool = False) -> str:
        """Format text in cyan."""
        style = Colors.BOLD if bold else ''
        return self.format(text, Colors.CYAN, style)
    
    def white(self, text: str, bold: bool = False) -> str:
        """Format text in white."""
        style = Colors.BOLD if bold else ''
        return self.format(text, Colors.WHITE, style)
    
    def bright_red(self, text: str, bold: bool = False) -> str:
        """Format text in bright red."""
        style = Colors.BOLD if bold else ''
        return self.format(text, Colors.BRIGHT_RED, style)
    
    def bright_green(self, text: str, bold: bool = False) -> str:
        """Format text in bright green."""
        style = Colors.BOLD if bold else ''
        return self.format(text, Colors.BRIGHT_GREEN, style)
    
    def bright_yellow(self, text: str, bold: bool = False) -> str:
        """Format text in bright yellow."""
        style = Colors.BOLD if bold else ''
        return self.format(text, Colors.BRIGHT_YELLOW, style)
    
    def bright_blue(self, text: str, bold: bool = False) -> str:
        """Format text in bright blue."""
        style = Colors.BOLD if bold else ''
        return self.format(text, Colors.BRIGHT_BLUE, style)
    
    def bright_magenta(self, text: str, bold: bool = False) -> str:
        """Format text in bright magenta."""
        style = Colors.BOLD if bold else ''
        return self.format(text, Colors.BRIGHT_MAGENTA, style)
    
    def bright_cyan(self, text: str, bold: bool = False) -> str:
        """Format text in bright cyan."""
        style = Colors.BOLD if bold else ''
        return self.format(text, Colors.BRIGHT_CYAN, style)
    
    def bold(self, text: str) -> str:
        """Format text in bold."""
        return self.format(text, '', Colors.BOLD)
    
    def dim(self, text: str) -> str:
        """Format text dimmed."""
        return self.format(text, '', Colors.DIM)
    
    def underline(self, text: str) -> str:
        """Format text underlined."""
        return self.format(text, '', Colors.UNDERLINE)
    
    def success(self, text: str) -> str:
        """Format success message."""
        return self.bright_green(f"✓ {text}")
    
    def error(self, text: str) -> str:
        """Format error message."""
        return self.bright_red(f"✗ {text}")
    
    def warning(self, text: str) -> str:
        """Format warning message."""
        return self.bright_yellow(f"⚠ {text}")
    
    def info(self, text: str) -> str:
        """Format info message."""
        return self.bright_blue(f"ℹ {text}")
    
    def header(self, text: str) -> str:
        """Format header text."""
        return self.bold(self.bright_cyan(text))
    
    def subheader(self, text: str) -> str:
        """Format subheader text."""
        return self.bold(self.cyan(text))
    
    def critical(self, text: str) -> str:
        """Format critical status message."""
        return self.bright_red(f"💀 {text}")
    
    def combat_action(self, text: str) -> str:
        """Format combat action message."""
        return self.bright_yellow(f"⚔️ {text}")
    
    def spell_effect(self, text: str) -> str:
        """Format spell effect message."""
        return self.bright_magenta(f"✨ {text}")
    
    def turn_indicator(self, text: str) -> str:
        """Format turn indicator."""
        return self.bright_yellow(f">>> {text}")
    
    def hp_healthy(self, text: str) -> str:
        """Format healthy HP display."""
        return self.bright_green(text)
    
    def hp_wounded(self, text: str) -> str:
        """Format wounded HP display."""
        return self.yellow(text)
    
    def hp_critical(self, text: str) -> str:
        """Format critical HP display."""
        return self.bright_red(text)
    
    def hp_dead(self, text: str) -> str:
        """Format dead HP display."""
        return self.format(text, Colors.BRIGHT_RED, Colors.BOLD + Colors.BLINK)
    
    def note_indicator(self, text: str = "📝") -> str:
        """Format note indicator."""
        return self.cyan(text)
    
    def initiative_value(self, text: str) -> str:
        """Format initiative value."""
        return self.bright_cyan(text)
    
    def combatant_player(self, text: str) -> str:
        """Format player combatant name."""
        return self.bright_blue(text)
    
    def combatant_monster(self, text: str) -> str:
        """Format monster combatant name."""
        return self.bright_red(text)
    
    def combatant_npc(self, text: str) -> str:
        """Format NPC combatant name."""
        return self.bright_magenta(text)
    
    def prompt(self, text: str) -> str:
        """Format command prompt."""
        return self.bold(self.cyan(text))


# Global formatter instance
formatter = ColorFormatter()