# TERMINATOR Integration with Web Apps

Integrate TERMINATOR with Notion, NotebookLM, GitHub, Apple Notes (web), OneNote, and more.

## Method 1: URL Scheme Handler (Recommended)

### Setup

1. Create the URL scheme handler app:

```bash
# Run the setup script
./integrations/browser/setup_url_handler.sh
```

2. After setup, you can use URLs like:
```
terminator://ask?q=Your+question+here
terminator://explain?code=function+foo()
```

### Browser Bookmarklets

Create bookmarks with these JavaScript URLs:

**Ask TERMINATOR (with selected text):**
```javascript
javascript:(function(){var t=window.getSelection().toString();if(t){window.location='terminator://ask?q='+encodeURIComponent(t)}else{var q=prompt('Ask TERMINATOR:');if(q)window.location='terminator://ask?q='+encodeURIComponent(q)}})()
```

**Explain Selection:**
```javascript
javascript:(function(){var t=window.getSelection().toString();if(t)window.location='terminator://explain?code='+encodeURIComponent(t);else alert('Select text first')})()
```

**Summarize Page:**
```javascript
javascript:(function(){var t=document.body.innerText.substring(0,2000);window.location='terminator://ask?q='+encodeURIComponent('Summarize this:\n\n'+t)})()
```

## Method 2: Keyboard Maestro (Power Users)

If you have Keyboard Maestro:

1. Create new macro triggered by hotkey (e.g., ⌃⇧T)
2. Add action: "Execute Shell Script"
3. Script:
```bash
#!/bin/bash
TEXT=$(pbpaste)
osascript -e "tell application \"Terminal\"
    activate
    do script \"echo '$TEXT' | python3 ~/Desktop/Terminator-Project/terminator_universal_cli.py\"
end tell"
```

## Method 3: Alfred Workflow

### Install Alfred Workflow

1. Download Alfred (if not installed): https://www.alfredapp.com
2. Import the workflow from `integrations/alfred/`
3. Use keyword `term` followed by your query

### Alfred Commands

- `term [query]` - Ask TERMINATOR
- `term agents` - List agents
- `term health` - Health check

## App-Specific Guides

### Notion

1. Select text in Notion
2. Copy (Cmd+C)
3. Use keyboard shortcut or bookmarklet
4. TERMINATOR analyzes in Terminal

**Notion Tip:** Use TERMINATOR to:
- Summarize long notes
- Generate outlines
- Explain technical content

### GitHub

1. Select code in GitHub file view
2. Use bookmarklet "Explain Selection"
3. TERMINATOR explains the code

**GitHub Tip:** Works great for:
- Understanding unfamiliar repos
- Code review assistance
- Explaining pull request changes

### NotebookLM

1. Select text from your sources
2. Copy and use TERMINATOR
3. Get local AI analysis (no data sent to cloud)

**NotebookLM Tip:** TERMINATOR runs locally via Ollama - great for sensitive documents.

### Apple Notes (iCloud Web)

1. Select text in notes.icloud.com
2. Use bookmarklet
3. TERMINATOR processes locally

### Microsoft OneNote

1. Select text in OneNote (web or app)
2. Copy (Cmd+C)
3. Use keyboard shortcut (⌃⇧T if configured)

## Creating Custom Bookmarklets

Template for any web app:

```javascript
javascript:(function(){
    var selectedText = window.getSelection().toString();
    var query = selectedText || prompt('Ask TERMINATOR:');
    if (query) {
        // Option 1: URL scheme (requires handler)
        window.location = 'terminator://ask?q=' + encodeURIComponent(query);

        // Option 2: Copy to clipboard + alert
        // navigator.clipboard.writeText(query);
        // alert('Copied! Use Cmd+Shift+T to ask TERMINATOR');
    }
})()
```

## Browser Extension Alternative

For deeper integration, a browser extension could:
- Add right-click menu "Ask TERMINATOR"
- Add sidebar panel
- Keyboard shortcuts within browser

**Note:** Browser extensions require more setup. For most users, bookmarklets + keyboard shortcuts work well.

## Quick Reference

| App | Best Method |
|-----|-------------|
| Notion | Bookmarklet or Keyboard Shortcut |
| GitHub | Bookmarklet (Explain Selection) |
| NotebookLM | Copy + Keyboard Shortcut |
| Apple Notes | Services Menu |
| OneNote | Copy + Keyboard Shortcut |
| VS Code | Use VS Code Extension |
| Xcode | Services Menu or Shortcut |

## Privacy Note

TERMINATOR runs **locally** using Ollama. Your data never leaves your machine when using the default Ollama backend. This is ideal for:
- Sensitive documents
- Private notes
- Confidential code
