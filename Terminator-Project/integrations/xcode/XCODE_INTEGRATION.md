# TERMINATOR Xcode Integration

## Quick Integration Methods

### Method 1: Services Menu (Easiest)

After running `install_integrations.sh`, you can use TERMINATOR from Xcode:

1. Select code in Xcode
2. Right-click → Services → **Ask TERMINATOR**
3. TERMINATOR opens with your code

### Method 2: Keyboard Shortcut

1. System Preferences → Keyboard → Shortcuts → Services
2. Find "Ask TERMINATOR"
3. Assign shortcut (e.g., ⌃⇧T)
4. Use in Xcode with selected code

### Method 3: Xcode Behaviors

Create a custom behavior that launches TERMINATOR:

1. Xcode → Preferences → Behaviors
2. Click + to add custom behavior
3. Name: "Ask TERMINATOR"
4. Check "Run" and select the script below

Create this script at `~/Desktop/Terminator-Project/integrations/xcode/xcode_terminator.sh`:

```bash
#!/bin/bash
# Get selected text from Xcode via clipboard
osascript -e 'tell application "Xcode" to activate'
osascript -e 'tell application "System Events" to keystroke "c" using command down'
sleep 0.5

SELECTED=$(pbpaste)

osascript << EOF
tell application "Terminal"
    activate
    do script "echo 'Explain this Swift/Objective-C code:\n\n$SELECTED' | python3 ~/Desktop/Terminator-Project/terminator_universal_cli.py"
end tell
EOF
```

### Method 4: Xcode Source Editor Extension (Advanced)

For a native Xcode extension, you need to:

1. Create new Xcode project → macOS → Xcode Source Editor Extension
2. Implement the extension to call TERMINATOR
3. Sign and install

Template code for `SourceEditorCommand.swift`:

```swift
import Foundation
import XcodeKit

class AskTerminatorCommand: NSObject, XCSourceEditorCommand {

    func perform(with invocation: XCSourceEditorCommandInvocation,
                 completionHandler: @escaping (Error?) -> Void) {

        // Get selected text
        guard let selection = invocation.buffer.selections.firstObject as? XCSourceTextRange else {
            completionHandler(nil)
            return
        }

        let lines = invocation.buffer.lines
        var selectedText = ""

        for i in selection.start.line...selection.end.line {
            if let line = lines[i] as? String {
                selectedText += line
            }
        }

        // Launch Terminal with TERMINATOR
        let script = """
        tell application "Terminal"
            activate
            do script "echo '\(selectedText.replacingOccurrences(of: "'", with: "'\\''"))' | python3 ~/Desktop/Terminator-Project/terminator_universal_cli.py"
        end tell
        """

        var error: NSDictionary?
        if let scriptObject = NSAppleScript(source: script) {
            scriptObject.executeAndReturnError(&error)
        }

        completionHandler(nil)
    }
}
```

## Recommended Setup

For most users, **Method 1 (Services) + Method 2 (Keyboard Shortcut)** is the best approach:

1. Install integrations: `./integrations/macos/install_integrations.sh`
2. Assign keyboard shortcut in System Preferences
3. Select code in Xcode → Use shortcut or right-click

## Usage Examples

### Explain Swift Code
1. Select a function in Xcode
2. Trigger TERMINATOR (shortcut or Services)
3. TERMINATOR explains the code

### Debug Help
1. Select error-causing code
2. Ask TERMINATOR: "Why might this code cause [error]?"

### Code Review
1. Select code before commit
2. Ask TERMINATOR for review

## Tips

- TERMINATOR understands Swift, Objective-C, and C/C++
- Include error messages when debugging
- For large code blocks, copy to clipboard and use `/ask` command
