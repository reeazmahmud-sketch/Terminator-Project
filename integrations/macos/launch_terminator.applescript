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
