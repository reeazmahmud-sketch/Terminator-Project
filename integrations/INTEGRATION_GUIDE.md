# TERMINATOR macOS Integration Guide

> Use TERMINATOR from anywhere on your Mac - VS Code, Xcode, Cursor, GitHub, Notion, and more.

## Quick Start (5 minutes)

```bash
# Install all integrations
cd ~/Desktop/Terminator-Project/integrations/macos
chmod +x install_integrations.sh
./install_integrations.sh
```

This installs:
- Global `terminator` command
- macOS Services menu integration
- Launch TERMINATOR.app
- Raycast extension
- Apple Shortcuts templates

## Integration Matrix

| App | Method | Shortcut |
|-----|--------|----------|
| **Terminal** | `terminator` command | - |
| **VS Code / Cursor** | Extension | Cmd+Shift+T |
| **Xcode** | Services Menu | Right-click |
| **GitHub** | Bookmarklet | - |
| **Notion** | Bookmarklet + Shortcut | - |
| **NotebookLM** | Copy + Shortcut | ⌃⇧T |
| **Apple Notes** | Services Menu | Right-click |
| **Raycast** | Extension | Raycast hotkey |
| **Spotlight** | Launch app | - |
| **Any App** | Keyboard Shortcut | ⌃⇧T (configurable) |

## Integration Details

### 1. Terminal / CLI
```bash
# From any terminal
terminator

# One-shot query
echo "explain async/await" | terminator

# Run command
echo "/agents" | terminator
```

### 2. VS Code / Cursor / Windsurf
```bash
cd ~/Desktop/Terminator-Project/integrations/vscode
npm install && npm run compile
```

Then: Cmd+Shift+P → "Developer: Install Extension from Location..."

**Features:**
- Cmd+Shift+T: Launch TERMINATOR
- Cmd+Shift+A: Ask question
- Right-click: Explain/Review code

### 3. Xcode
Best method: **Services Menu**

1. Select code in Xcode
2. Right-click → Services → Ask TERMINATOR
3. TERMINATOR opens with your code

See: `integrations/xcode/XCODE_INTEGRATION.md`

### 4. Raycast
```bash
# Import extension
# Raycast → Extensions → + → Import Extension
# Select: ~/Desktop/Terminator-Project/integrations/raycast/terminator
```

**Commands:**
- `Launch TERMINATOR` - Open in Terminal
- `Ask TERMINATOR [query]` - Direct query
- `List Agents` - Show all agents
- `Health Check` - Run diagnostics

### 5. Browser Apps (Notion, GitHub, NotebookLM, etc.)
```bash
# Install URL handler
chmod +x ~/Desktop/Terminator-Project/integrations/browser/setup_url_handler.sh
./setup_url_handler.sh
```

**Bookmarklets** (add to bookmarks bar):

**Ask TERMINATOR:**
```javascript
javascript:(function(){var t=window.getSelection().toString()||prompt('Ask:');if(t)window.location='terminator://ask?q='+encodeURIComponent(t)})()
```

**Explain Selection:**
```javascript
javascript:(function(){var t=window.getSelection().toString();if(t)window.location='terminator://explain?code='+encodeURIComponent(t)})()
```

### 6. Apple Shortcuts / Siri
1. Open Shortcuts app
2. Create shortcut with "Run Shell Script"
3. Script: `echo "$1" | python3 ~/Desktop/Terminator-Project/terminator_universal_cli.py`
4. Add keyboard shortcut or enable Siri

**Siri Commands:**
- "Hey Siri, Launch TERMINATOR"
- "Hey Siri, Ask TERMINATOR"

### 7. Global Keyboard Shortcut
1. System Preferences → Keyboard → Shortcuts → Services
2. Find "Ask TERMINATOR"
3. Click "Add Shortcut"
4. Press your preferred shortcut (e.g., ⌃⇧T)

## Directory Structure

```
integrations/
├── INTEGRATION_GUIDE.md          # This file
├── macos/
│   ├── install_integrations.sh   # Main installer
│   ├── Launch TERMINATOR.app     # Keyboard shortcut app
│   └── launch_terminator.applescript
├── vscode/
│   ├── package.json
│   ├── src/extension.ts
│   └── README.md
├── xcode/
│   └── XCODE_INTEGRATION.md
├── raycast/
│   └── terminator/
│       ├── package.json
│       └── src/*.tsx
├── browser/
│   ├── WEB_APPS_INTEGRATION.md
│   └── setup_url_handler.sh
└── shortcuts/
    └── SETUP_SHORTCUTS.md
```

## Troubleshooting

### "terminator" command not found
```bash
sudo ln -sf ~/Desktop/Terminator-Project/terminator_universal_cli.py /usr/local/bin/terminator
sudo chmod +x /usr/local/bin/terminator
```

### Services menu not showing
```bash
/System/Library/CoreServices/pbs -flush
# Then log out and back in
```

### VS Code extension not loading
```bash
cd ~/Desktop/Terminator-Project/integrations/vscode
rm -rf out node_modules
npm install
npm run compile
```

### Ollama not responding
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve
```

## Privacy & Security

TERMINATOR runs **100% locally** using Ollama by default:
- No data sent to cloud
- Works offline
- Safe for sensitive/confidential content

Optional cloud backends (Gemini, Claude) available for enhanced capabilities.

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│                 TERMINATOR Quick Access                  │
├─────────────────────────────────────────────────────────┤
│ Terminal        │ terminator                            │
│ VS Code         │ Cmd+Shift+T                           │
│ Any App         │ ⌃⇧T (configure in System Prefs)       │
│ Selected Text   │ Right-click → Services → Ask          │
│ Raycast         │ "term" keyword                        │
│ Browser         │ Use bookmarklet                       │
│ Siri            │ "Hey Siri, Launch TERMINATOR"         │
├─────────────────────────────────────────────────────────┤
│ /help           │ All commands                          │
│ /agents         │ List 38+ agents                       │
│ /tools          │ 8 tool categories                     │
│ /modules        │ 61 core modules                       │
│ /status         │ System health                         │
│ /healthCheck    │ Full diagnostics                      │
└─────────────────────────────────────────────────────────┘
```
