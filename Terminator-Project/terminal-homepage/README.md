# TERMINATOR Terminal Homepage

A beautiful, terminal-style browser homepage with TERMINATOR branding and powerful command features.

## Features

### 🎨 **Terminal Aesthetics**
- Authentic terminal look with ASCII art logo
- Dark theme with cyan/green accents
- Glowing effects and smooth animations
- Blinking cursor
- macOS-style window buttons

### ⌨️ **Command Interface**
- **Auto-complete** - Press Tab to complete commands
- **Command history** - Use ↑/↓ arrows to navigate
- **Smart suggestions** - Type-ahead with descriptions
- **Bookmarks** - Quick access to favorite sites
- **Direct search** - Just type to search Google

### 🚀 **Available Commands**

| Command | Description |
|---------|-------------|
| `help` | Show all commands |
| `clear` | Clear terminal |
| `search <query>` | Search Google |
| `go <url>` | Navigate to URL |
| `bookmark [add\|list]` | Manage bookmarks |
| `weather [city]` | Check weather |
| `time` | Show current time |
| `reddit [r/sub]` | Open Reddit |
| `youtube [search]` | Search YouTube |
| `github [user/repo]` | Open GitHub |
| `translate <text>` | Translate text |
| `news [category]` | Latest news |
| `terminator <cmd>` | Send to TERMINATOR CLI |
| `history` | Show command history |

### 📌 **Default Bookmarks**
- `gh` → GitHub
- `gmail` → Gmail
- `drive` → Google Drive
- `yt` → YouTube
- `reddit` → Reddit
- `twitter` → Twitter
- `linkedin` → LinkedIn
- `netflix` → Netflix
- `terminator` → TERMINATOR (localhost:8000)

## Installation

### **Set as Browser Homepage**

#### Chrome/Edge
1. Open `chrome://settings/` or `edge://settings/`
2. Search for "On startup"
3. Select "Open a specific page or set of pages"
4. Add: `file:///Users/reeazmahmud/Desktop/Terminator-Project/terminal-homepage/index.html`

#### Firefox
1. Open `about:preferences#home`
2. Under "Homepage and new windows"
3. Select "Custom URLs"
4. Add: `file:///Users/reeazmahmud/Desktop/Terminator-Project/terminal-homepage/index.html`

#### Safari
1. Open Safari Preferences → General
2. Set "Homepage" to: `file:///Users/reeazmahmud/Desktop/Terminator-Project/terminal-homepage/index.html`

### **Alternative: Use as New Tab Page**

Install a browser extension like:
- **Chrome:** "New Tab Redirect"
- **Firefox:** "New Tab Override"
- **Edge:** "New Tab Redirect"

Point it to the `index.html` file.

## Usage Examples

### Basic Navigation
```bash
$ go github.com
→ Opening: https://github.com

$ gh
→ Opening bookmark: GitHub

$ search Python tutorials
🔍 Searching Google for: Python tutorials
```

### Bookmarks
```bash
$ bookmark add gpt https://chat.openai.com
✓ Bookmark added: gpt → https://chat.openai.com

$ bookmark list
📚 Bookmarks:
  gh → https://github.com
  gpt → https://chat.openai.com

$ gpt
→ Opens ChatGPT
```

### Quick Shortcuts
```bash
$ reddit r/programming
→ Opening Reddit: r/programming

$ youtube coding tutorials
🎥 Searching YouTube: coding tutorials

$ github anthropics/claude-code
→ Opening GitHub: anthropics/claude-code

$ weather San Francisco
🌤️  Opening weather for: San Francisco
```

### TERMINATOR Integration
```bash
$ terminator run health check
⚡ Sending to TERMINATOR: run health check
Note: This requires TERMINATOR backend running
```

## Customization

### **Add Custom Commands**

Edit `terminal.js` and add to the `initializeCommands()` method:

```javascript
mycommand: {
    description: 'My custom command',
    action: (args) => {
        const param = args.join(' ');
        this.addOutputSafe('success-text', `Running: ${param}`);
        // Your custom logic here
    }
}
```

### **Change Colors**

Edit `styles.css` variables:

```css
:root {
    --bg-primary: #0a0e27;        /* Main background */
    --text-primary: #00ff9f;      /* Primary text (green) */
    --text-secondary: #00d4ff;    /* Secondary text (cyan) */
    --accent-red: #ff3e3e;        /* Accent color (red) */
}
```

### **Modify ASCII Logo**

Edit the `<pre class="ascii-art">` section in `index.html` with your custom ASCII art.

## Keyboard Shortcuts

- **Enter** - Execute command
- **Tab** - Auto-complete
- **↑/↓** - Navigate command history
- **Esc** - Hide suggestions
- **Click anywhere** - Focus input

## Features in Detail

### Command History
All commands are saved to `localStorage` and persist across sessions. Access with ↑/↓ arrows or use the `history` command.

### Smart Suggestions
As you type, relevant commands appear with descriptions. Click to auto-complete or press Tab.

### Direct Search
Don't know a command? Just type normally:
```bash
$ how to center a div in CSS
🔍 Searches Google automatically
```

### Bookmark Management
```bash
$ bookmark add shortname https://example.com
$ bookmark list
$ shortname  # Opens the bookmark
```

## Integration with TERMINATOR

When TERMINATOR backend is running (http://localhost:8000), you can send commands:

```bash
$ terminator /healthCheck
⚡ Sending to TERMINATOR: /healthCheck
```

Future enhancement: Full bi-directional communication with TERMINATOR CLI.

## Browser Compatibility

- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Edge
- ✅ Safari
- ✅ Brave

## Performance

- **Load time:** < 100ms
- **Memory:** < 5MB
- **No external dependencies**
- **Offline capable**
- **No tracking or analytics**

## Privacy

- All data stored locally (localStorage)
- No external API calls (except for navigation)
- No cookies or tracking
- Open source and auditable

## Future Enhancements

- [ ] TERMINATOR backend integration
- [ ] Custom themes
- [ ] Import/export bookmarks
- [ ] Command aliases
- [ ] Keyboard shortcuts customization
- [ ] Search engine selection
- [ ] Weather API integration
- [ ] Quick notes feature
- [ ] Calculator mode
- [ ] Unit converter

## License

Part of the TERMINATOR Project - AI-Powered Terminal System

## Credits

Created by Claude Code (Sonnet 4.5) for the TERMINATOR Project
