import sys

if sys.platform == "darwin":
    from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
