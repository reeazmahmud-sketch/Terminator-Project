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
