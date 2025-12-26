#!/usr/bin/env zsh
# ============================================================================
# install.sh
# Installation script for enhanced ZSH modules
# ============================================================================

set -e

# Colors
C_RESET="\033[0m"
C_BOLD="\033[1m"
C_GREEN="\033[32m"
C_YELLOW="\033[33m"
C_CYAN="\033[36m"
C_RED="\033[31m"

echo -e "${C_BOLD}${C_CYAN}╔════════════════════════════════════════════════════════╗${C_RESET}"
echo -e "${C_BOLD}${C_CYAN}║   Enhanced ZSH Modules Installation                    ║${C_RESET}"
echo -e "${C_BOLD}${C_CYAN}╚════════════════════════════════════════════════════════╝${C_RESET}"
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MODULES_SOURCE="${SCRIPT_DIR}/modules"
MODULES_TARGET="${HOME}/.zsh/modules"

# Check if modules directory exists
if [[ ! -d "$MODULES_SOURCE" ]]; then
    echo -e "${C_RED}❌ Error: modules directory not found at $MODULES_SOURCE${C_RESET}"
    exit 1
fi

echo -e "${C_BOLD}Installation Details:${C_RESET}"
echo "  Source: $MODULES_SOURCE"
echo "  Target: $MODULES_TARGET"
echo ""

# Create target directory if it doesn't exist
if [[ ! -d "$MODULES_TARGET" ]]; then
    echo -e "${C_YELLOW}Creating modules directory...${C_RESET}"
    mkdir -p "$MODULES_TARGET"
fi

# Backup existing modules
if [[ -d "$MODULES_TARGET" ]] && [[ -n "$(ls -A $MODULES_TARGET)" ]]; then
    BACKUP_DIR="${HOME}/.zsh/modules_backup_$(date +%Y%m%d_%H%M%S)"
    echo -e "${C_YELLOW}📦 Backing up existing modules to: $BACKUP_DIR${C_RESET}"
    cp -r "$MODULES_TARGET" "$BACKUP_DIR"
fi

# Copy modules
echo -e "${C_CYAN}📁 Installing modules...${C_RESET}"
echo ""

for module in "$MODULES_SOURCE"/*.zsh; do
    if [[ -f "$module" ]]; then
        module_name=$(basename "$module")
        echo -e "  ${C_GREEN}✓${C_RESET} Installing $module_name"
        cp "$module" "$MODULES_TARGET/"
        chmod +x "$MODULES_TARGET/$module_name"
    fi
done

echo ""

# Check if .zshrc exists
if [[ ! -f "${HOME}/.zshrc" ]]; then
    echo -e "${C_YELLOW}⚠️  No .zshrc found. Creating one...${C_RESET}"
    touch "${HOME}/.zshrc"
fi

# Add module loading code to .zshrc if not already present
if ! grep -q "# Enhanced ZSH Modules" "${HOME}/.zshrc"; then
    echo -e "${C_CYAN}📝 Adding module loader to .zshrc...${C_RESET}"
    cat >> "${HOME}/.zshrc" << 'EOF'

# ============================================================================
# Enhanced ZSH Modules
# Auto-load all modules from ~/.zsh/modules
# ============================================================================

# Load all modules in numerical order
if [[ -d "${HOME}/.zsh/modules" ]]; then
    for module in ${HOME}/.zsh/modules/[0-9]*.zsh; do
        if [[ -f "$module" ]]; then
            source "$module"
        fi
    done
fi

EOF
    echo -e "${C_GREEN}✓ Module loader added to .zshrc${C_RESET}"
else
    echo -e "${C_GREEN}✓ Module loader already present in .zshrc${C_RESET}"
fi

echo ""
echo -e "${C_BOLD}${C_CYAN}╔════════════════════════════════════════════════════════╗${C_RESET}"
echo -e "${C_BOLD}${C_CYAN}║   Installation Complete!                               ║${C_RESET}"
echo -e "${C_BOLD}${C_CYAN}╚════════════════════════════════════════════════════════╝${C_RESET}"
echo ""

echo -e "${C_BOLD}📦 Installed Modules:${C_RESET}"
echo ""
echo -e "  ${C_GREEN}✓${C_RESET} 05-auto-suggestions.zsh    - Smart command suggestions"
echo -e "  ${C_GREEN}✓${C_RESET} 15-terminal-voice.zsh      - Voice integration in terminal"
echo -e "  ${C_GREEN}✓${C_RESET} 25-enhanced-dashboard.zsh  - Enhanced startup dashboard"
echo -e "  ${C_GREEN}✓${C_RESET} 35-kill-all-processes.zsh  - Kill commands for AI/LLM"
echo ""

echo -e "${C_BOLD}🎯 Features Enabled:${C_RESET}"
echo ""
echo "  1. Auto-Suggestions:"
echo "     • Press Alt+s to show suggestions"
echo "     • Press Alt+a to accept first suggestion"
echo ""
echo "  2. Voice Integration:"
echo "     • Press Ctrl+V for voice input"
echo "     • Commands: vl, vs, vc, vchat"
echo ""
echo "  3. Dashboard:"
echo "     • Auto-shows on terminal startup"
echo "     • Tracks file changes"
echo "     • Type 'dashboard' to show anytime"
echo ""
echo "  4. Kill Commands:"
echo "     • kill-all-ai    - Kill all AI processes"
echo "     • emergency-kill - Emergency stop"
echo "     • Type 'kill-help' for more"
echo ""

echo -e "${C_BOLD}⚠️  Next Steps:${C_RESET}"
echo ""
echo "  1. Install voice dependencies (optional):"
echo "     pip3 install --user SpeechRecognition pyaudio gtts playsound"
echo ""
echo "  2. Reload your shell:"
echo -e "     ${C_CYAN}source ~/.zshrc${C_RESET}"
echo ""
echo "     OR close and reopen your terminal"
echo ""

echo -e "${C_BOLD}📚 Quick Reference:${C_RESET}"
echo ""
echo "  Command Suggestions:"
echo "    Alt+s              - Show suggestions"
echo "    Alt+a              - Accept suggestion"
echo ""
echo "  Voice Commands:"
echo "    Ctrl+V             - Voice input"
echo "    vl                 - Voice listen"
echo "    vs <text>          - Voice speak"
echo "    vchat              - Voice chat with AI"
echo ""
echo "  Dashboard:"
echo "    dashboard          - Show dashboard"
echo ""
echo "  Kill Commands:"
echo "    kill-all-ai        - Kill all AI processes"
echo "    ka                 - Shortcut for kill-all-ai"
echo "    ekill              - Emergency kill"
echo "    ls-ai              - List AI processes"
echo ""

echo -e "${C_GREEN}✅ Installation successful!${C_RESET}"
echo ""
echo -e "${C_YELLOW}Run '${C_CYAN}source ~/.zshrc${C_YELLOW}' to activate now${C_RESET}"
echo ""
