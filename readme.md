# Monarx

A lightweight macOS menu bar application for monitoring CPU, Memory, and Swap usage with native notifications.

## Features

- Live system stats in menu bar
- Native macOS notifications when thresholds exceeded
- Configurable thresholds
- Minimal and clean interface

## Requirements

- macOS
- Python 3.7+

## Installation

```bash
cd ~/tools/Monarx
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
source .venv/bin/activate
python menu_bar_app.py
```

## Configuration

Edit `config.py`:

```python
CPU_LIMIT = 85      # Alert when CPU exceeds this %
MEM_LIMIT = 80      # Alert when Memory exceeds this %
SWAP_LIMIT = 20     # Alert when Swap exceeds this %
CHECK_EVERY = 5     # Refresh interval (seconds)
COOLDOWN = 120      # Time between repeated notifications
```

## Menu Bar Display

Shows: `C:XX M:XX S:XX`

- **C** = CPU %
- **M** = Memory %
- **S** = Swap %

## Dropdown Menu

- CPU, Memory, Swap with status indicators `[OK]`, `[WARN]`, `[HIGH]`
- Current threshold settings
- Refresh button
- Quit button

## Auto-Start on Login

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
        <string>/Users/&lt;username&gt;/tools/Monarx/.venv/bin/python</string>
        <string>/Users/&lt;username&gt;/tools/Monarx/menu_bar_app.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load: `launchctl load ~/Library/LaunchAgents/com.monarx.plist`

Unload: `launchctl unload ~/Library/LaunchAgents/com.monarx.plist`

## Project Structure

```
Monarx/
├── menu_bar_app.py    # Main application
├── config.py          # Configuration
├── requirements.txt   # Dependencies
└── README.md
```

## License

MIT
