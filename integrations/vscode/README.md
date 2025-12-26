# TERMINATOR VS Code Extension

Integrate TERMINATOR AI into VS Code, Cursor, Windsurf, and compatible editors.

## Features

- **Launch TERMINATOR** (Cmd+Shift+T) - Open TERMINATOR in integrated terminal
- **Ask Question** (Cmd+Shift+A) - Ask TERMINATOR anything
- **Explain Code** - Right-click selected code for explanation
- **Review Code** - Right-click selected code for code review
- **List Agents** - Show all 38+ TERMINATOR agents
- **Health Check** - Run system diagnostics

## Installation

### Option 1: Install from Source (Recommended)

```bash
cd ~/Desktop/Terminator-Project/integrations/vscode
npm install
npm run compile
```

Then in VS Code:
1. Press Cmd+Shift+P
2. Type "Developer: Install Extension from Location..."
3. Select this folder

### Option 2: Package and Install

```bash
npm install -g @vscode/vsce
cd ~/Desktop/Terminator-Project/integrations/vscode
npm install
vsce package
```

This creates `terminator-ai-1.0.0.vsix`. Install it:
- VS Code: Extensions → ... → Install from VSIX
- Cursor: Same process

## Usage

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Cmd+Shift+T | Launch TERMINATOR terminal |
| Cmd+Shift+A | Ask TERMINATOR a question |

### Right-Click Menu

Select any code, then right-click:
- **TERMINATOR: Ask About Selection**
- **TERMINATOR: Explain This Code**
- **TERMINATOR: Review This Code**

### Command Palette

Press Cmd+Shift+P and type "TERMINATOR":
- TERMINATOR: Launch Terminal
- TERMINATOR: Ask Question
- TERMINATOR: List Agents
- TERMINATOR: Health Check

## Works With

- VS Code
- Cursor
- Windsurf
- VSCodium
- Any VS Code-compatible editor

## Requirements

- Python 3.8+
- Ollama running locally
- TERMINATOR installed at ~/Desktop/Terminator-Project
