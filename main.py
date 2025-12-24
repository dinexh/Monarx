#!/usr/bin/env python3
"""Monarx - Cross-platform system monitor."""

import sys


def main():
    platform = sys.platform
    
    if platform == "darwin":
        from app_macos import run
    elif platform == "win32":
        from app_windows import run
    elif platform.startswith("linux"):
        from app_linux import run
    else:
        print(f"Unsupported platform: {platform}")
        sys.exit(1)
    
    run()


if __name__ == "__main__":
    main()
