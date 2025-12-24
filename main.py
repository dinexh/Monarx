#!/usr/bin/env python3
"""Monarx - Cross-platform system monitor."""

import sys


def main():
    platform = sys.platform
    
    if platform == "darwin":
        from mac import run
    elif platform == "win32":
        from windows import run
    elif platform.startswith("linux"):
        from linux import run
    else:
        print(f"Unsupported platform: {platform}")
        sys.exit(1)
    
    run()


if __name__ == "__main__":
    main()
