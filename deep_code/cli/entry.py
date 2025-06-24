#!/usr/bin/env python3
import sys
import os
from pathlib import Path

def main():
    try:
        from deep_code.cli.main import app
        app()
    except ImportError:
        # Fallback to relative import if package structure changes
        from .main import app
        app()

if __name__ == "__main__":
    main()