"""
Intelligent Resume Analyzer
============================
Entry point for the application.

Run with:
    python3 main.py

Requirements: Python 3.8+ standard library only (tkinter must be available,
which is included with most standard Python installations).
"""

import sys
import os

# Ensure the project root is on sys.path so `modules` can be imported
# regardless of the current working directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.gui import launch_app


def main():
    try:
        launch_app()
    except Exception as e:  # noqa: broad-except (top-level safety net)
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
