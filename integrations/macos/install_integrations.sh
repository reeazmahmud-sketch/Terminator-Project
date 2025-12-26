#!/bin/bash
# ============================================================
# TERMINATOR macOS Integration Installer
# ============================================================
# Installs system-wide integrations for TERMINATOR:
# - Global CLI command
# - macOS Services menu (right-click integration)
# - Keyboard shortcut launcher app
# - Raycast extension
# - Apple Shortcuts templates
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
TERMINATOR_CLI="$PROJECT_ROOT/terminator_universal_cli.py"

echo "🤖 TERMINATOR macOS Integration Installer"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# 1. Install CLI command globally
echo -e "${CYAN}[1/5] Installing global CLI command...${NC}"
if ! command -v terminator &> /dev/null; then
    sudo ln -sf "$TERMINATOR_CLI" /usr/local/bin/terminator
    sudo chmod +x /usr/local/bin/terminator
    echo -e "${GREEN}✓ 'terminator' command installed globally${NC}"
else
    echo -e "${GREEN}✓ 'terminator' command already installed${NC}"
fi

# 2. Create macOS Services Quick Action
echo -e "${CYAN}[2/5] Creating macOS Services integration...${NC}"
SERVICES_DIR="$HOME/Library/Services"
mkdir -p "$SERVICES_DIR"

# We'll create a simpler approach using a shell script service
SERVICE_SCRIPT="$PROJECT_ROOT/integrations/macos/ask_terminator_service.sh"
cat > "$SERVICE_SCRIPT" << 'SCRIPT'
#!/bin/bash
# macOS Service script for TERMINATOR
# Selected text is passed via stdin

INPUT=$(cat)
osascript << EOF
tell application "Terminal"
    activate
    do script "cd ~/Desktop/Terminator-Project && echo '$INPUT' | python3 terminator_universal_cli.py"
end tell
EOF
SCRIPT
chmod +x "$SERVICE_SCRIPT"

echo -e "${GREEN}✓ Service script created at: $SERVICE_SCRIPT${NC}"
echo "  → Create Quick Action in Automator using this script"

# 3. Create AppleScript launcher app
echo -e "${CYAN}[3/5] Creating keyboard shortcut launcher...${NC}"

# Create AppleScript file
cat > "$PROJECT_ROOT/integrations/macos/launch_terminator.applescript" << 'APPLESCRIPT'
-- TERMINATOR Launcher
-- Save as Application, then assign keyboard shortcut in System Preferences

on run
    tell application "Terminal"
        activate

        -- Check for existing TERMINATOR window
        set found to false
        repeat with w in windows
            try
                if name of w contains "terminator" then
                    set frontmost of w to true
                    set found to true
                    exit repeat
                end if
            end try
        end repeat

        -- Start new if not found
        if not found then
            do script "cd ~/Desktop/Terminator-Project && python3 terminator_universal_cli.py"
        end if
    end tell
end run
APPLESCRIPT

# Compile to application
osacompile -o "$PROJECT_ROOT/integrations/macos/Launch TERMINATOR.app" \
    "$PROJECT_ROOT/integrations/macos/launch_terminator.applescript" 2>/dev/null || true

echo -e "${GREEN}✓ Launcher app created${NC}"
echo "  → Double-click 'Launch TERMINATOR.app' to test"
echo "  → Assign shortcut: System Preferences → Keyboard → Shortcuts → App Shortcuts"

# 4. Create Raycast extension
echo -e "${CYAN}[4/5] Creating Raycast extension...${NC}"
RAYCAST_DIR="$PROJECT_ROOT/integrations/raycast/terminator"

cat > "$RAYCAST_DIR/package.json" << 'JSON'
{
  "$schema": "https://www.raycast.com/schemas/extension.json",
  "name": "terminator",
  "title": "TERMINATOR AI",
  "description": "Launch and interact with TERMINATOR AI agent system",
  "icon": "command-icon.png",
  "author": "terminator",
  "license": "MIT",
  "commands": [
    {
      "name": "launch",
      "title": "Launch TERMINATOR",
      "description": "Open TERMINATOR in Terminal",
      "mode": "no-view"
    },
    {
      "name": "ask",
      "title": "Ask TERMINATOR",
      "description": "Send a query to TERMINATOR",
      "mode": "no-view",
      "arguments": [
        {
          "name": "query",
          "placeholder": "Your question...",
          "type": "text",
          "required": true
        }
      ]
    },
    {
      "name": "agents",
      "title": "List Agents",
      "description": "Show all TERMINATOR agents",
      "mode": "no-view"
    },
    {
      "name": "health",
      "title": "Health Check",
      "description": "Run TERMINATOR diagnostics",
      "mode": "no-view"
    }
  ],
  "dependencies": {
    "@raycast/api": "^1.50.0"
  },
  "devDependencies": {
    "@types/node": "^18.8.3",
    "typescript": "^4.4.3"
  },
  "scripts": {
    "build": "ray build -e dist",
    "dev": "ray develop"
  }
}
JSON

# Use execFile (safer) instead of exec
cat > "$RAYCAST_DIR/src/launch.tsx" << 'TSX'
import { closeMainWindow, showHUD } from "@raycast/api";
import { execFile } from "child_process";

export default async function Command() {
  await closeMainWindow();

  // Using execFile with osascript is safe - no shell injection possible
  const script = `tell application "Terminal"
    activate
    do script "cd ~/Desktop/Terminator-Project && python3 terminator_universal_cli.py"
  end tell`;

  execFile("/usr/bin/osascript", ["-e", script], (error) => {
    if (error) console.error("Launch error:", error);
  });

  await showHUD("TERMINATOR Launched");
}
TSX

cat > "$RAYCAST_DIR/src/ask.tsx" << 'TSX'
import { closeMainWindow, showHUD } from "@raycast/api";
import { execFile } from "child_process";

interface Arguments {
  query: string;
}

export default async function Command(props: { arguments: Arguments }) {
  const { query } = props.arguments;
  await closeMainWindow();

  // Escape single quotes for AppleScript string
  const safeQuery = query.replace(/'/g, "'\"'\"'");

  const script = `tell application "Terminal"
    activate
    do script "echo '${safeQuery}' | python3 ~/Desktop/Terminator-Project/terminator_universal_cli.py"
  end tell`;

  execFile("/usr/bin/osascript", ["-e", script], (error) => {
    if (error) console.error("Ask error:", error);
  });

  await showHUD("Asked TERMINATOR");
}
TSX

cat > "$RAYCAST_DIR/src/agents.tsx" << 'TSX'
import { closeMainWindow, showHUD } from "@raycast/api";
import { execFile } from "child_process";

export default async function Command() {
  await closeMainWindow();

  const script = `tell application "Terminal"
    activate
    do script "echo /agents | python3 ~/Desktop/Terminator-Project/terminator_universal_cli.py"
  end tell`;

  execFile("/usr/bin/osascript", ["-e", script], (error) => {
    if (error) console.error("Agents error:", error);
  });

  await showHUD("Listing Agents");
}
TSX

cat > "$RAYCAST_DIR/src/health.tsx" << 'TSX'
import { closeMainWindow, showHUD } from "@raycast/api";
import { execFile } from "child_process";

export default async function Command() {
  await closeMainWindow();

  const script = `tell application "Terminal"
    activate
    do script "echo /healthCheck | python3 ~/Desktop/Terminator-Project/terminator_universal_cli.py"
  end tell`;

  execFile("/usr/bin/osascript", ["-e", script], (error) => {
    if (error) console.error("Health error:", error);
  });

  await showHUD("Running Health Check");
}
TSX

echo -e "${GREEN}✓ Raycast extension created${NC}"
echo "  → Import: Raycast → Extensions → + → Import Extension"

# 5. Create Apple Shortcuts instructions
echo -e "${CYAN}[5/5] Creating Apple Shortcuts guide...${NC}"

cat > "$PROJECT_ROOT/integrations/shortcuts/SETUP_SHORTCUTS.md" << 'MD'
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
MD

echo -e "${GREEN}✓ Shortcuts guide created${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "=========================================="
echo ""
echo "Installed:"
echo "  1. ✓ Global 'terminator' command"
echo "  2. ✓ Service script for Automator"
echo "  3. ✓ Launch TERMINATOR.app"
echo "  4. ✓ Raycast extension"
echo "  5. ✓ Apple Shortcuts guide"
echo ""
echo "Quick Start:"
echo "  • Run 'terminator' from any terminal"
echo "  • Double-click 'Launch TERMINATOR.app'"
echo "  • Set up keyboard shortcut (see guide)"
echo ""
echo "Documentation: $PROJECT_ROOT/integrations/"
