# Apple Shortcuts Integration for TERMINATOR

## Quick Setup (2 minutes)

### Shortcut 1: Launch TERMINATOR (Recommended)

1. Open **Shortcuts** app
2. Click **+** to create new shortcut
3. Search for "Run Shell Script" and add it
4. Paste this script:
   ```bash
   open -a Terminal ~/Desktop/Terminator-Project
   sleep 1
   osascript -e 'tell application "Terminal" to do script "python3 terminator_universal_cli.py" in front window'
   ```
5. Name it "Launch TERMINATOR"
6. Click shortcut settings (i) → Add Keyboard Shortcut → **⌃⇧T** (Ctrl+Shift+T)

### Shortcut 2: Ask TERMINATOR (with selected text)

1. Create new shortcut
2. Add "Receive **Text** from **Quick Actions**"
3. Add "Run Shell Script":
   ```bash
   osascript -e "tell application \"Terminal\"
       activate
       do script \"echo '$1' | python3 ~/Desktop/Terminator-Project/terminator_universal_cli.py\"
   end tell"
   ```
4. Enable "Use as Quick Action" in settings
5. Name it "Ask TERMINATOR"

### Shortcut 3: TERMINATOR Menu Bar

1. Create new shortcut
2. Add "Ask for Input" with prompt "TERMINATOR Command:"
3. Add "Run Shell Script" with same script as #2
4. Enable "Pin in Menu Bar"

## Siri Integration

After creating shortcuts, you can say:
- "Hey Siri, Launch TERMINATOR"
- "Hey Siri, Ask TERMINATOR"

## Keyboard Shortcuts Summary

| Shortcut | Action |
|----------|--------|
| ⌃⇧T | Launch TERMINATOR |
| Right-click → Services | Ask TERMINATOR with selection |
| Menu bar icon | Quick command input |
