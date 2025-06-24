#!/usr/bin/env python3
import sys
import os
from pathlib import Path

def main():
    # Get the installed package location and add src path
    current_file = Path(__file__).resolve()
    
    # Try to find the src directory relative to the installed package
    possible_src_paths = [
        current_file.parent.parent,  # If installed in development mode
        Path(sys.prefix) / "lib" / "python3.12" / "site-packages" / "src",  # If installed normally
        Path("/home/rick/Desktop/apps/Deep Code/ai-code/src"),  # Fallback to absolute path
    ]
    
    src_dir = None
    for path in possible_src_paths:
        if (path / "cli" / "main.py").exists():
            src_dir = path
            break
    
    if src_dir:
        sys.path.insert(0, str(src_dir))
    
    try:
        from cli.main import app
        app()
    except ImportError:
        # Fallback to absolute import
        sys.path.insert(0, "/home/rick/Desktop/apps/Deep Code/ai-code/src")
        from cli.main import app
        app()

if __name__ == "__main__":
    main()