"""Entry point for running the D&D Encounter Tracker as a module."""

import sys
from .cli.main import main

if __name__ == '__main__':
    sys.exit(main())