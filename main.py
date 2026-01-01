"""Monarx - macOS system monitor."""
import sys


def main():
    if sys.platform != "darwin":
        print(f"Unsupported platform: {sys.platform}. Monarx is macOS-only.")
        sys.exit(1)
        
    from mac import run
    run()


if __name__ == "__main__":
    main()
