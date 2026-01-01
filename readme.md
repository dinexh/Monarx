# Monarx

A lightweight macOS menu bar application for monitoring CPU, Memory, and Swap usage with detailed memory breakdown and pressure alerts.

## Features

- Live system stats in the macOS menu bar
- Detailed memory breakdown (Wired, Active, Compressed, Cached)
- Native notifications when thresholds are exceeded
- Memory pressure and lag risk detection
- Top CPU and Memory process monitoring with kill capability
- Configurable thresholds
- Minimal and clean interface

## Installation

```bash
cd ~/tools/Monarx
python3 -m venv .venv
source .venv/bin/activate
pip install psutil rumps pyobjc
```

## Usage

```bash
python main.py
```

## Configuration

Edit `core/config.py`:

```python
CPU_LIMIT = 85      # Alert when CPU exceeds this %
MEM_LIMIT = 80      # Alert when Memory exceeds this %
SWAP_LIMIT = 20     # Alert when Swap exceeds this %
CHECK_EVERY = 5     # Refresh interval (seconds)
COOLDOWN = 120      # Time between repeated notifications
```

## Display

The menu bar shows: `C:XX% M:XX%` (with status indicators like `OK` or `STR` for stress).

- **C** = CPU %
- **M** = Memory %

## Project Structure

```
Monarx/
├── main.py          # Entry point
├── core/            # System monitoring logic
│   ├── config.py    # Configuration
│   └── logging.py   # Logging setup
├── mac/             # macOS implementation
└── web/             # Next.js web application (landing page)
```

## CI/CD

This repository uses GitHub Actions with separate workflows for the Python app and web app to ensure they don't interfere with each other:

- **Python App CI** (`.github/workflows/python-app.yml`): Runs on macOS, tests Python code, only triggers on changes outside `web/`
- **Web App CI** (`.github/workflows/web-app.yml`): Builds and tests the Next.js app, only triggers on changes inside `web/`
- **Combined CI** (`.github/workflows/ci.yml`): Smart workflow that detects which parts changed and runs appropriate tests

Changes to the `web/` directory will **not** trigger Python app tests, and changes to Python files will **not** trigger web app builds.

## Auto-Start

Create `~/Library/LaunchAgents/com.monarx.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.monarx</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/dineshkorukonda/tools/Monarx/.venv/bin/python</string>
        <string>/Users/dineshkorukonda/tools/Monarx/main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/dineshkorukonda/tools/Monarx</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/dineshkorukonda/tools/Monarx/monitor.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/dineshkorukonda/tools/Monarx/monitor.err</string>
</dict>
</plist>
```

Load and start the agent:

```bash
launchctl load ~/Library/LaunchAgents/com.monarx.plist
```

To stop it:

```bash
launchctl unload ~/Library/LaunchAgents/com.monarx.plist
```

## License

MIT
