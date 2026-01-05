#!/usr/bin/env zsh
# ============================================================================
# install-enhanced.sh
# Enhanced installation with backup and verification
# ============================================================================

set -e

# Colors
C_RESET="\033[0m"
C_BOLD="\033[1m"
C_GREEN="\033[32m"
C_YELLOW="\033[33m"
C_CYAN="\033[36m"
C_RED="\033[31m"
C_GRAY="\033[90m"

echo -e "${C_BOLD}${C_CYAN}╔════════════════════════════════════════════════════════╗${C_RESET}"
echo -e "${C_BOLD}${C_CYAN}║   Enhanced ZSH Modules Installation v2.0               ║${C_RESET}"
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

echo -e "${C_BOLD}Installation Configuration:${C_RESET}"
echo "  Source: $MODULES_SOURCE"
echo "  Target: $MODULES_TARGET"
echo "  Backup: ${HOME}/.zsh/modules_backup_$(date +%Y%m%d_%H%M%S)"
echo ""

# Ask for confirmation
echo -e "${C_YELLOW}This will:${C_RESET}"
echo "  1. Backup existing modules (if any)"
echo "  2. Install new/enhanced modules"
echo "  3. Update your ~/.zshrc"
echo "  4. Test the installation"
echo ""
echo -n "Continue? (y/N): "
read -r confirm

if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo -e "${C_YELLOW}Installation cancelled.${C_RESET}"
    exit 0
fi

echo ""

# Create target directory if it doesn't exist
if [[ ! -d "$MODULES_TARGET" ]]; then
    echo -e "${C_CYAN}📁 Creating modules directory...${C_RESET}"
    mkdir -p "$MODULES_TARGET"
fi

# Backup existing modules
if [[ -d "$MODULES_TARGET" ]] && [[ -n "$(ls -A $MODULES_TARGET 2>/dev/null)" ]]; then
    BACKUP_DIR="${HOME}/.zsh/modules_backup_$(date +%Y%m%d_%H%M%S)"
    echo -e "${C_YELLOW}📦 Backing up existing modules...${C_RESET}"
    cp -r "$MODULES_TARGET" "$BACKUP_DIR"
    echo -e "${C_GREEN}   ✓ Backup saved to: $BACKUP_DIR${C_RESET}"
fi

# Copy/update modules
echo -e "${C_CYAN}📁 Installing/updating modules...${C_RESET}"
echo ""

# List of modules to install
declare -A modules=(
    ["05-auto-suggestions-enhanced.zsh"]="Smart command suggestions (with auto-trigger)"
    ["15-terminal-voice.zsh"]="Voice integration"
    ["25-enhanced-dashboard-v2.zsh"]="Enhanced dashboard (with reload detection)"
    ["35-kill-all-processes.zsh"]="Kill commands for AI/LLM"
)

# Install new/enhanced modules
for module_file in "${(@k)modules}"; do
    local description="${modules[$module_file]}"
    local source_file="$MODULES_SOURCE/$module_file"
    
    if [[ -f "$source_file" ]]; then
        echo -e "  ${C_GREEN}✓${C_RESET} Installing: $module_file"
        echo -e "    ${C_GRAY}$description${C_RESET}"
        cp "$source_file" "$MODULES_TARGET/"
        chmod +x "$MODULES_TARGET/$module_file"
    else
        echo -e "  ${C_YELLOW}⚠${C_RESET} Skipping: $module_file (not found)"
    fi
done

# Also copy original versions if they exist
for original in "$MODULES_SOURCE"/*.zsh; do
    if [[ -f "$original" ]]; then
        local basename=$(basename "$original")
        # Skip if we already copied the enhanced version
        if [[ ! "${(@k)modules[(I)$basename]}" ]]; then
            echo -e "  ${C_GREEN}✓${C_RESET} Installing: $basename"
            cp "$original" "$MODULES_TARGET/"
            chmod +x "$MODULES_TARGET/$basename"
        fi
    fi
done

echo ""

# Check if .zshrc exists
if [[ ! -f "${HOME}/.zshrc" ]]; then
    echo -e "${C_YELLOW}⚠️  No .zshrc found. Creating one...${C_RESET}"
    touch "${HOME}/.zshrc"
fi

# Add module loading code to .zshrc if not already present
if ! grep -q "# Enhanced ZSH Modules" "${HOME}/.zshrc" 2>/dev/null; then
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

# Verify installation
echo -e "${C_CYAN}🔍 Verifying installation...${C_RESET}"
echo ""

local errors=0

# Check if modules exist
for module_file in "${(@k)modules}"; do
    if [[ -f "$MODULES_TARGET/$module_file" ]]; then
        echo -e "  ${C_GREEN}✓${C_RESET} $module_file exists"
    else
        echo -e "  ${C_RED}✗${C_RESET} $module_file missing"
        ((errors++))
    fi
done

# Check if .zshrc has loader
if grep -q "Enhanced ZSH Modules" "${HOME}/.zshrc"; then
    echo -e "  ${C_GREEN}✓${C_RESET} .zshrc configured"
else
    echo -e "  ${C_RED}✗${C_RESET} .zshrc not configured"
    ((errors++))
fi

echo ""

if [[ $errors -eq 0 ]]; then
    echo -e "${C_BOLD}${C_GREEN}✅ Installation successful!${C_RESET}"
else
    echo -e "${C_BOLD}${C_YELLOW}⚠️  Installation completed with $errors error(s)${C_RESET}"
fi

echo ""
echo -e "${C_BOLD}${C_CYAN}╔════════════════════════════════════════════════════════╗${C_RESET}"
echo -e "${C_BOLD}${C_CYAN}║   📦 What's Installed                                  ║${C_RESET}"
echo -e "${C_BOLD}${C_CYAN}╚════════════════════════════════════════════════════════╝${C_RESET}"
echo ""

echo -e "${C_BOLD}1. Auto-Suggestions${C_RESET} (Enhanced)"
echo "   • Shows suggestions when you type single letters (s, g, c, etc.)"
echo "   • Press Alt+s to show suggestions manually"
echo "   • Press Alt+a to accept first suggestion"
echo ""

echo -e "${C_BOLD}2. Terminal Voice Integration${C_RESET}"
echo "   • Press Ctrl+V for voice input"
echo "   • Commands: vl (listen), vs (speak), vchat (AI chat)"
echo "   • Install deps: pip3 install SpeechRecognition pyaudio gtts playsound"
echo ""

echo -e "${C_BOLD}3. Enhanced Dashboard${C_RESET} (v2)"
echo "   • Auto-shows on new terminal"
echo "   • Auto-shows when you run 'source ~/.zshrc'"
echo "   • Tracks config file changes"
echo "   • Shows running AI processes"
echo ""

echo -e "${C_BOLD}4. Kill All Processes${C_RESET}"
echo "   • kill-all-ai (ka) - Kill all AI processes"
echo "   • emergency-kill (ekill) - Emergency stop"
echo "   • Type 'kill-help' for all commands"
echo ""

echo -e "${C_BOLD}${C_YELLOW}⚠️  Next Steps:${C_RESET}"
echo ""
echo "  ${C_CYAN}1.${C_RESET} Install voice dependencies (optional but recommended):"
echo "     pip3 install --user SpeechRecognition pyaudio gtts playsound"
echo ""
echo "     On macOS, you may also need:"
echo "     brew install portaudio"
echo ""
echo "  ${C_CYAN}2.${C_RESET} Reload your shell to activate:"
echo -e "     ${C_BOLD}${C_GREEN}source ~/.zshrc${C_RESET}"
echo ""
echo "     OR"
echo ""
echo "     Close and reopen your terminal"
echo ""
echo "  ${C_CYAN}3.${C_RESET} Test the features:"
echo "     • Type 's' and wait - should show suggestions"
echo "     • Press Alt+s - should show suggestions menu"
echo "     • Run 'dashboard' - should display full dashboard"
echo "     • Run 'vl' - should try voice listen (if deps installed)"
echo ""

echo -e "${C_BOLD}💡 Quick Reference:${C_RESET}"
echo ""
echo "  Dashboard:        dashboard, dashboard-compact"
echo "  Suggestions:      Alt+s (show), Alt+a (accept)"
echo "  Voice:            Ctrl+V (input), vl, vs, vchat"
echo "  Kill Commands:    ka, ko, kp, km, ekill, kill-help"
echo ""

echo -e "${C_GREEN}✨ Installation complete! Reload your shell to activate.${C_RESET}"
echo ""
