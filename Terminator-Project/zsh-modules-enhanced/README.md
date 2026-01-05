# Enhanced ZSH Modules

Complete terminal enhancement suite with auto-suggestions, voice integration, smart dashboard, and process management.

## 📦 What's Included

### 1. Auto-Suggestions Module (`05-auto-suggestions.zsh`)
**Smart command suggestions based on your usage patterns**

Features:
- Tracks command frequency and recency
- Shows suggestions when typing single letters (especially 's')
- Context-aware suggestions based on current directory
- Learns from your command history

Key Bindings:
- `Alt+s` - Show suggestions for current input
- `Alt+a` - Accept first suggestion

Commands:
- `suggestions` - Manually show suggestions
- `rebuild-suggestions` - Rebuild the suggestion cache

### 2. Terminal Voice Integration (`15-terminal-voice.zsh`)
**Full voice interaction in your terminal - no GUI needed**

Features:
- Speech-to-text input (Google Speech Recognition)
- Text-to-speech output (gTTS)
- Voice command mode
- Voice chat with AI (Ollama integration)
- Works in any terminal

Key Bindings:
- `Ctrl+V` - Voice input at cursor position

Commands:
- `vl` / `voice-listen` - Listen for voice input
- `vs <text>` / `voice-speak <text>` - Speak text aloud
- `vc` / `voice-command` - Enter voice command mode
- `vchat` / `voice-chat` - Chat with AI using voice
- `install-voice-deps` - Install required dependencies

Voice Command Mode:
```bash
$ vc
🎤 Voice Command Mode
Say a command, and I'll execute it.
Say 'exit' or 'quit' to stop.

🎤 Listening... (speak now)
📝 Heard: list files
➜ Executing: ls
[files listed]
```

Voice Chat Mode:
```bash
$ vchat
💬 Voice Chat Mode (with AI)
Speak your question, and AI will respond with voice.

🎤 Listening... (speak now)
📝 Heard: What is the weather like today?
🤔 Thinking...
💭 AI: I don't have access to real-time weather data...
🔊 Speaking: [AI response spoken aloud]
```

Dependencies:
```bash
pip3 install --user SpeechRecognition pyaudio gtts playsound

# On macOS, you may also need:
brew install portaudio
```

### 3. Enhanced Dashboard (`25-enhanced-dashboard.zsh`)
**Beautiful startup dashboard with system info and change tracking**

Features:
- Auto-displays on terminal startup
- Auto-displays after `source ~/.zshrc`
- Tracks changes to terminal configuration files
- Shows running AI/LLM processes
- Displays session statistics
- Quick command reference

What's Shown:
- System information (date, time, hostname, user)
- Recent configuration file changes
- Running AI/LLM/Agent processes
- Session statistics (commands run, session time)
- Voice module status
- Quick command reference

Commands:
- `dashboard` - Show dashboard manually

Configuration:
The dashboard monitors these files by default:
- `~/.zshrc`
- `~/.zsh/` directory
- `~/.zprofile`
- `~/.zshenv`

Dashboard will show when:
1. You open a new terminal
2. You run `source ~/.zshrc`
3. You type `dashboard`

### 4. Kill All Processes (`35-kill-all-processes.zsh`)
**Comprehensive process management for AI, LLM, and agents**

Features:
- Kill specific process types
- Kill all AI/LLM processes at once
- Emergency kill command
- List running AI processes
- No orphaned processes

Individual Kill Commands:
- `kill-ollama` - Kill Ollama processes
- `kill-python-agents` - Kill Python AI agents
- `kill-mcp` - Kill MCP servers
- `kill-llm-servers` - Kill LLM servers (LM Studio, LocalAI, etc.)
- `kill-voice` - Kill voice processes
- `kill-node-agents` - Kill Node.js AI agents
- `kill-gpu-processes` - Kill GPU AI processes

Bulk Kill Commands:
- `kill-all-ai` - Kill all AI processes (with confirmation)
- `kill-all-ai-force` - Kill all AI processes (no confirmation)
- `emergency-kill` - Immediate kill everything (use in emergencies)

Utility Commands:
- `list-ai-processes` / `ls-ai` - List all running AI processes
- `kill-help` - Show help for all kill commands

Short Aliases:
- `ka` → `kill-all-ai`
- `kaf` → `kill-all-ai-force`
- `ko` → `kill-ollama`
- `kp` → `kill-python-agents`
- `km` → `kill-mcp`
- `kl` → `kill-llm-servers`
- `kv` → `kill-voice`
- `ekill` → `emergency-kill`

## 🚀 Installation

### Automatic Installation

1. Clone or download this repository
2. Navigate to the directory:
   ```bash
   cd zsh-modules-enhanced
   ```
3. Run the installation script:
   ```bash
   ./install.sh
   ```
4. Reload your shell:
   ```bash
   source ~/.zshrc
   ```
   OR close and reopen your terminal

### Manual Installation

1. Copy modules to your ZSH modules directory:
   ```bash
   mkdir -p ~/.zsh/modules
   cp modules/*.zsh ~/.zsh/modules/
   chmod +x ~/.zsh/modules/*.zsh
   ```

2. Add this to your `~/.zshrc`:
   ```bash
   # Enhanced ZSH Modules
   if [[ -d "${HOME}/.zsh/modules" ]]; then
       for module in ${HOME}/.zsh/modules/[0-9]*.zsh; do
           if [[ -f "$module" ]]; then
               source "$module"
           fi
       done
   fi
   ```

3. Reload your shell:
   ```bash
   source ~/.zshrc
   ```

## 📚 Usage Examples

### Auto-Suggestions

```bash
# Type 's' and press Alt+s to see suggestions
$ s
💡 Suggestions:
  1) sudo apt update
  2) ssh user@server
  3) systemctl status nginx
  4) scp file.txt remote:/path
  5) screen -r

# Press Alt+a to accept the first suggestion
$ sudo apt update
```

### Voice Integration

```bash
# Voice input at cursor
$ echo "The weather is"
[Press Ctrl+V]
🎤 Listening... (speak now)
📝 Heard: sunny and warm
$ echo "The weather is sunny and warm"

# Voice command execution
$ vc
🎤 Voice Command Mode
[Speak: "list files"]
➜ Executing: ls
[files listed]

# Voice chat with AI
$ vchat
💬 Voice Chat Mode
[Speak: "What is Kubernetes?"]
🤔 Thinking...
💭 AI: Kubernetes is a container orchestration platform...
🔊 [Response spoken aloud]
```

### Dashboard

```bash
# Shows automatically on startup, or type:
$ dashboard

╔════════════════════════════════════════════════════════════╗
║               🖥️  TERMINAL DASHBOARD                       ║
╚════════════════════════════════════════════════════════════╝

📅 Date: Monday, November 18, 2024
⏰ Time: 14:23:45 PST

💻 System: Darwin on MacBook-Pro
👤 User: reeazmahmud
📁 PWD: ~/terminalai

⚠️  Recent Changes Detected:

  ✓ ~/.zshrc
    Modified: 2024-11-18 14:20:15

📝 Recent Configuration Changes:

  • ~/.zsh/modules/30-llm.zsh (Nov 18 13:45)
  • ~/.zshrc (Nov 18 14:20)

🤖 Running AI/LLM Processes:

  ● Ollama (2 processes)
  ● Python AI Agents (1 processes)

📊 Quick Stats:

  Commands run: 127
  Session time: 2h 15m
  Voice: Enabled ✓

⚡ Quick Commands:

  dashboard        - Show this dashboard
  kill-all-ai     - Kill all AI/LLM processes
  vl               - Voice listen
  vs <text>        - Voice speak
  vchat            - Voice chat with AI
  ollama-llama3   - Chat with Llama3
```

### Kill Commands

```bash
# List running AI processes
$ ls-ai
🔍 AI/LLM Processes:

▸ ollama:
  PID 1234: /usr/local/bin/ollama serve
  PID 1235: /usr/local/bin/ollama run llama3

▸ Python AI agents:
  PID 5678: python3 gui_mcp.py

# Kill all AI processes (with confirmation)
$ kill-all-ai
🛑 KILLING ALL AI/LLM/AGENT PROCESSES

⚠️  This will terminate ALL AI-related processes.
Are you sure? (y/N): y

🔫 Killing Ollama processes...
✓ Ollama processes killed

🔫 Killing Python AI agents...
✓ Killed 1 Python AI agent(s)

✅ All AI/LLM/Agent processes terminated

# Emergency kill (no confirmation)
$ ekill
🚨 EMERGENCY KILL - TERMINATING EVERYTHING NOW
✓ Emergency kill executed
```

## 🔧 Configuration

### Auto-Suggestions

Configuration variables in `05-auto-suggestions.zsh`:
```bash
COMMAND_HISTORY_DB="${HOME}/.zsh_command_history.db"
COMMAND_FREQ_CACHE="${HOME}/.zsh_command_freq_cache"
```

### Voice Integration

Configuration variables in `15-terminal-voice.zsh`:
```bash
VOICE_INPUT_LANG="en-US"      # Speech recognition language
VOICE_OUTPUT_LANG="en"        # Text-to-speech language
VOICE_PYTHON_CMD="python3"    # Python command to use
```

### Dashboard

Configuration variables in `25-enhanced-dashboard.zsh`:
```bash
DASHBOARD_AUTO_SHOW=true      # Auto-show on startup
DASHBOARD_WATCH_FILES=(       # Files to monitor
    "${HOME}/.zshrc"
    "${HOME}/.zsh"
    "${HOME}/.zprofile"
    "${HOME}/.zshenv"
)
```

To disable auto-show, add to your `~/.zshrc` before loading modules:
```bash
DASHBOARD_AUTO_SHOW=false
```

## 🐛 Troubleshooting

### Auto-Suggestions not working

1. Check if module loaded:
   ```bash
   grep "Auto-suggestions module loaded" ~/.zsh/modules/05-auto-suggestions.zsh
   ```

2. Rebuild cache:
   ```bash
   rebuild-suggestions
   ```

3. Check key bindings:
   ```bash
   bindkey | grep suggestions
   ```

### Voice features not working

1. Check if dependencies are installed:
   ```bash
   python3 -c "import speech_recognition, gtts"
   ```

2. Install dependencies:
   ```bash
   pip3 install --user SpeechRecognition pyaudio gtts playsound
   ```

3. On macOS, install portaudio:
   ```bash
   brew install portaudio
   ```

4. Test microphone access:
   ```bash
   vl
   ```

### Dashboard not showing

1. Check if module loaded:
   ```bash
   type dashboard
   ```

2. Manually show dashboard:
   ```bash
   dashboard
   ```

3. Check auto-show setting:
   ```bash
   echo $DASHBOARD_AUTO_SHOW
   ```

### Kill commands not working

1. Check if processes are running:
   ```bash
   ls-ai
   ```

2. Try force kill:
   ```bash
   kaf
   ```

3. Manual cleanup:
   ```bash
   pkill -9 ollama
   pkill -9 -f "ollama_cli\|gui_mcp"
   ```

## 🔄 Integration with Existing Setup

These modules are designed to work alongside your existing ZSH configuration:

- **Existing modules**: Numbered `00-80`, these are `05-35`, filling gaps
- **Existing aliases**: Won't conflict with standard aliases
- **Existing key bindings**: Uses `Alt` and `Ctrl` combinations that are typically free

If you have conflicts, you can:
1. Rename modules (change the number prefix)
2. Modify key bindings in the module files
3. Disable specific features by commenting out sections

## 📋 Requirements

### Required
- ZSH shell
- Unix-like operating system (macOS, Linux, WSL)

### Optional (for voice features)
- Python 3.6+
- pip3
- Microphone access
- Internet connection (for speech recognition)

### Optional (for AI chat)
- Ollama installed and running
- At least one model downloaded (e.g., llama3)

## 🎯 Quick Reference Card

Print this for easy reference:

```
╔═══════════════════════════════════════════════════════╗
║           ENHANCED ZSH MODULES - QUICK REF            ║
╠═══════════════════════════════════════════════════════╣
║ AUTO-SUGGESTIONS                                      ║
║   Alt+s              Show suggestions                 ║
║   Alt+a              Accept first suggestion          ║
║                                                       ║
║ VOICE                                                 ║
║   Ctrl+V             Voice input                      ║
║   vl                 Voice listen                     ║
║   vs <text>          Voice speak                      ║
║   vc                 Voice command mode               ║
║   vchat              Voice chat with AI               ║
║                                                       ║
║ DASHBOARD                                             ║
║   dashboard          Show dashboard                   ║
║                                                       ║
║ KILL COMMANDS                                         ║
║   ka / kill-all-ai   Kill all AI (confirm)           ║
║   kaf                Kill all AI (force)              ║
║   ekill              Emergency kill                   ║
║   ls-ai              List AI processes                ║
║   kill-help          Show kill commands help          ║
╚═══════════════════════════════════════════════════════╝
```

## 📝 License

MIT License - Feel free to use, modify, and distribute.

## 🤝 Contributing

Suggestions and improvements welcome! This is designed to be modular and extensible.

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review module files for configuration options
3. Check that all dependencies are installed

## 🎉 Enjoy!

Your terminal is now supercharged with:
- ✅ Smart command suggestions
- ✅ Full voice integration
- ✅ Beautiful startup dashboard
- ✅ Comprehensive process management

Happy computing! 🚀
