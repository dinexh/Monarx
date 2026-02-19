"""MacMonitor - macOS system monitor."""
import sys


def main():
    if sys.platform != "darwin":
        print(f"Unsupported platform: {sys.platform}. MacMonitor is macOS-only.")
        sys.exit(1)
        
    from mac import run
    run()


if __name__ == "__main__":
    main()
