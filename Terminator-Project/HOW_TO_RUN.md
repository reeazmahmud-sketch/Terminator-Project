# 🚀 HOW TO RUN TERMINATOR

## For First-Time Users (Do Once)

### Step 1: Open Terminal
- Press `Cmd + Space` (Spotlight)
- Type "Terminal"
- Press Enter

### Step 2: Navigate to Project
Copy and paste this command:
```bash
cd /Users/reeazmahmud/Desktop/Terminator-Project
```
Press Enter

### Step 3: Install Dependencies (First Time Only!)
Copy and paste this command:
```bash
pip3 install -r requirements.txt
```
Press Enter and wait 1-2 minutes

✅ **Setup Complete!** You only do this once.

---

## Every Time You Want to Use TERMINATOR

### Option 1: Easy Menu (Recommended)
```bash
cd /Users/reeazmahmud/Desktop/Terminator-Project
./start_all.sh
```

You'll see:
```
Select interface to launch:
  [1] Web Terminal (React UI with Voice)
  [2] Terminal UI (CLI with Animations)
  [3] Simple CLI (Minimal)
  [4] All Interfaces (Background)

Choice [1-4]:
```

Type `1` and press Enter (for Web Terminal)

### Option 2: Direct Launch (Fast)

**Web Terminal (Best for most users):**
```bash
cd /Users/reeazmahmud/Desktop/Terminator-Project
./start_web_terminal.sh
```

**Terminal UI (For terminal lovers):**
```bash
cd /Users/reeazmahmud/Desktop/Terminator-Project
./start_terminal_ui.sh
```

**Simple CLI (Minimal):**
```bash
cd /Users/reeazmahmud/Desktop/Terminator-Project
./start_cli.sh
```

---

## After Starting

### If you chose Web Terminal:
1. Your browser will open automatically
2. Go to: http://localhost:8000
3. Start chatting!

### If you chose Terminal UI or CLI:
- It runs right in the terminal
- Just start typing your commands

---

## To Stop TERMINATOR

Press `Ctrl + C` in the terminal window

---

## Quick Copy-Paste Commands

### START (Copy all 2 lines together):
```bash
cd /Users/reeazmahmud/Desktop/Terminator-Project
./start_all.sh
```

### CHECK IF RUNNING:
```bash
curl http://localhost:8000/status
```

### STOP (if needed):
Press `Ctrl + C` in terminal

---

## Troubleshooting

### "Permission denied"
Run this once:
```bash
cd /Users/reeazmahmud/Desktop/Terminator-Project
chmod +x start_*.sh
```

### "Port 8000 already in use"
```bash
lsof -ti:8000 | xargs kill
```
Then try starting again

### "pip3: command not found"
Install Python first:
```bash
brew install python3
```

---

## Video Tutorial Coming Soon!

For now, just copy-paste the commands above. That's it! 🎉
