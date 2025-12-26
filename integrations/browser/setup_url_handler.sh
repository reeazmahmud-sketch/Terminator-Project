#!/bin/bash
# ============================================================
# TERMINATOR URL Scheme Handler Setup
# ============================================================
# Creates a macOS app that handles terminator:// URLs
# Allows browser bookmarklets to launch TERMINATOR
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
APP_DIR="$HOME/Applications/TERMINATOR URL Handler.app"

echo "🔗 Setting up TERMINATOR URL Handler..."

# Create app bundle structure
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# Create Info.plist with URL scheme
cat > "$APP_DIR/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>terminator-handler</string>
    <key>CFBundleIdentifier</key>
    <string>com.terminator.urlhandler</string>
    <key>CFBundleName</key>
    <string>TERMINATOR URL Handler</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleURLTypes</key>
    <array>
        <dict>
            <key>CFBundleURLName</key>
            <string>TERMINATOR Query</string>
            <key>CFBundleURLSchemes</key>
            <array>
                <string>terminator</string>
            </array>
        </dict>
    </array>
    <key>LSBackgroundOnly</key>
    <true/>
</dict>
</plist>
PLIST

# Create the handler script
cat > "$APP_DIR/Contents/MacOS/terminator-handler" << 'HANDLER'
#!/bin/bash
# TERMINATOR URL Handler
# Handles URLs like: terminator://ask?q=query

URL="$1"

# Parse the URL
if [[ "$URL" =~ ^terminator://([^?]+)\?(.*)$ ]]; then
    COMMAND="${BASH_REMATCH[1]}"
    PARAMS="${BASH_REMATCH[2]}"

    # URL decode the query parameter
    QUERY=$(echo "$PARAMS" | sed 's/q=//' | python3 -c "import sys, urllib.parse; print(urllib.parse.unquote(sys.stdin.read()))")

    case "$COMMAND" in
        ask|query)
            osascript << EOF
tell application "Terminal"
    activate
    do script "echo '$QUERY' | python3 ~/Desktop/Terminator-Project/terminator_universal_cli.py"
end tell
EOF
            ;;
        explain)
            osascript << EOF
tell application "Terminal"
    activate
    do script "echo 'Explain this code:\n\n$QUERY' | python3 ~/Desktop/Terminator-Project/terminator_universal_cli.py"
end tell
EOF
            ;;
        review)
            osascript << EOF
tell application "Terminal"
    activate
    do script "echo 'Review this code for issues:\n\n$QUERY' | python3 ~/Desktop/Terminator-Project/terminator_universal_cli.py"
end tell
EOF
            ;;
        agents)
            osascript << EOF
tell application "Terminal"
    activate
    do script "echo '/agents' | python3 ~/Desktop/Terminator-Project/terminator_universal_cli.py"
end tell
EOF
            ;;
        *)
            osascript << EOF
tell application "Terminal"
    activate
    do script "python3 ~/Desktop/Terminator-Project/terminator_universal_cli.py"
end tell
EOF
            ;;
    esac
fi
HANDLER

chmod +x "$APP_DIR/Contents/MacOS/terminator-handler"

# Register the URL scheme
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$APP_DIR"

echo "✅ URL Handler installed!"
echo ""
echo "Test it by opening in browser:"
echo "  terminator://ask?q=Hello%20TERMINATOR"
echo ""
echo "Bookmarklet for selected text:"
echo "  javascript:(function(){var t=window.getSelection().toString();if(t)window.location='terminator://ask?q='+encodeURIComponent(t)})() "
